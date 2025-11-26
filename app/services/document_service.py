from app import db
from app.models import Document, DocumentSignature, ResidentSignature, Condominium
from app.utils.signature_service import SignatureServiceFactory
from app.utils.validation import validate_file
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import io
from flask import current_app
from app.exceptions import ValidationError, BusinessError, ResourceNotFoundError
import structlog

logger = structlog.get_logger()

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'documents')

class DocumentService:
    @staticmethod
    def generate_document_code(condo, doc_type="OF"):
        prefix = condo.document_code_prefix
        if not prefix:
            source = condo.subdomain or condo.name or "DOCS"
            prefix = source[:4].upper()
        
        date_str = datetime.now().strftime('%Y%m%d')
        base_pattern = f"{doc_type}{date_str}{prefix}%"
        
        last_doc = Document.query\
            .filter(Document.document_code.like(base_pattern))\
            .order_by(Document.document_code.desc())\
            .first()
            
        if last_doc and last_doc.document_code:
            try:
                last_seq = int(last_doc.document_code[-4:])
                new_seq = last_seq + 1
            except:
                new_seq = 1
        else:
            new_seq = 1
            
        return f"{doc_type}{date_str}{prefix}{new_seq:04d}"

    @staticmethod
    def generate_unsigned_pdf(doc):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2.0, height - 50, doc.title)
        
        p.setFont("Helvetica", 10)
        if doc.document_code:
            p.drawRightString(width - 40, height - 30, f"Ref: {doc.document_code}")
        p.drawRightString(width - 40, height - 45, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}")

        p.setFont("Helvetica", 11)
        text = p.beginText(40, height - 100)
        for line in doc.content.replace('<p>', '').replace('</p>', '\n').split('\n'):
            text.textLine(line)
        
        p.drawText(text)
        p.save()
        
        buffer.seek(0)
        filename = f"{uuid.uuid4().hex}.pdf"
        path = os.path.join(UPLOAD_FOLDER, 'unsigned', filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'wb') as f:
            f.write(buffer.getvalue())
        
        doc.pdf_unsigned_path = os.path.join('static', 'uploads', 'documents', 'unsigned', filename)
        db.session.commit()
        return doc.pdf_unsigned_path

    @staticmethod
    def create_document(user, form_data, user_condo):
        title = form_data.get('title')
        content = form_data.get('content')
        
        if not title or not content:
            raise ValidationError("Título y contenido son obligatorios")

        doc_type = form_data.get('document_type', 'OF')
        requires_sig = 'requires_signature' in form_data
        collect_sigs = 'collect_signatures' in form_data

        condo_id = user_condo.id if user_condo else None
        if not condo_id and user.role != 'MASTER':
            raise BusinessError("Usuario sin condominio asignado.")

        new_code = None
        if user_condo:
            new_code = DocumentService.generate_document_code(user_condo, doc_type=doc_type)

        doc = Document(
            title=title,
            content=content,
            created_by_id=user.id,
            condominium_id=condo_id,
            document_code=new_code,
            document_type=doc_type,
            requires_signature=requires_sig,
            collect_signatures_from_residents=collect_sigs
        )
        
        if collect_sigs:
            doc.generate_public_link()

        try:
            db.session.add(doc)
            db.session.commit()
            logger.info("Documento creado", doc_id=doc.id, user_id=user.id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error DB al crear documento", error=str(e), user_id=user.id)
            raise BusinessError("Error al guardar el documento")
        
        DocumentService.generate_unsigned_pdf(doc)
        return doc

    @staticmethod
    def update_document(doc, form_data):
        doc.title = form_data['title']
        doc.content = form_data['content']
        doc.requires_signature = 'requires_signature' in form_data
        doc.collect_signatures_from_residents = 'collect_signatures' in form_data
        
        if doc.collect_signatures_from_residents and not doc.public_signature_link:
            doc.generate_public_link()

        try:
            db.session.commit()
            logger.info("Documento actualizado", doc_id=doc.id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error DB al actualizar documento", error=str(e), doc_id=doc.id)
            raise BusinessError("Error al actualizar el documento")

        DocumentService.generate_unsigned_pdf(doc)
        return doc

    @staticmethod
    def upload_physical_signature(doc, user, file, ip_address):
        if not file or file.filename == '':
            raise ValidationError("No se seleccionó ningún archivo.")
        
        try:
            validate_file(file, allowed_extensions=['pdf'], allowed_mimetypes=['application/pdf'])
        except ValueError as e:
            raise ValidationError(str(e))

        filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
        path = os.path.join(UPLOAD_FOLDER, 'signed', filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file.save(path)

        doc.pdf_signed_path = os.path.join('static', 'uploads', 'documents', 'signed', filename)
        doc.signature_type = 'physical'
        doc.status = 'signed'
        
        sig = DocumentSignature(document_id=doc.id, user_id=user.id, signature_type='physical', ip_address=ip_address)
        
        try:
            db.session.add(sig)
            db.session.commit()
            logger.info("Firma física subida", doc_id=doc.id, user_id=user.id)
        except Exception as e:
             db.session.rollback()
             logger.error("Error DB al subir firma física", error=str(e), doc_id=doc.id)
             raise BusinessError("Error al guardar la firma")
             
        return doc

    @staticmethod
    def request_electronic_signature(doc, user, user_condo):
        service = SignatureServiceFactory.get_provider(user_condo)
        if not service:
            raise BusinessError("El servicio de firma electrónica no está configurado.")
        
        if not doc.pdf_unsigned_path or not os.path.exists(os.path.join('app', doc.pdf_unsigned_path)):
            DocumentService.generate_unsigned_pdf(doc)
        
        pdf_abs_path = os.path.join('app', doc.pdf_unsigned_path)
        
        try:
            result = service.create_flow(pdf_abs_path, user, doc.title)
        except Exception as e:
            logger.error("Error proveedor firma", error=str(e), doc_id=doc.id)
            raise BusinessError(f"Error al conectar con el proveedor de firma: {str(e)}")
        
        flow_id = result.get('id') or result.get('_id') or result.get('flowId')
        if not flow_id and 'data' in result:
            flow_id = result['data'].get('id')

        if not flow_id:
            logger.error(f"Respuesta inesperada del proveedor de firma: {result}")
            raise BusinessError("Respuesta irreconocible del proveedor.")

        doc.external_flow_id = str(flow_id)
        db.session.commit()
        return doc

    @staticmethod
    def check_signature_status(doc, user_condo, ip_address):
        if not doc.external_flow_id:
            raise BusinessError("No hay flujo activo")
            
        service = SignatureServiceFactory.get_provider(user_condo)
        if not service:
             raise BusinessError("Servicio de firma no configurado")

        try:
            details = service.get_flow_details(doc.external_flow_id)
        except Exception as e:
             logger.error("Error obteniendo detalles flujo", error=str(e), flow_id=doc.external_flow_id)
             raise BusinessError("Error al consultar estado de firma")
        
        signed_file_path = None
        if 'files' in details:
            for file in details['files']:
                if file.get('status') == 'signed' or file.get('signedPath'):
                     signed_file_path = file.get('signedPath') or file.get('path')
                     break
        
        if not signed_file_path and (details.get('status') == 'completed' or details.get('state') == 'completed'):
             if 'files' in details and len(details['files']) > 0:
                 signed_file_path = details['files'][0].get('path')

        if signed_file_path:
            try:
                file_content = service.download_file(signed_file_path)
            except Exception as e:
                 logger.error("Error descargando archivo firmado", error=str(e), path=signed_file_path)
                 raise BusinessError("Error al descargar el documento firmado")
            
            filename = f"{uuid.uuid4().hex}_{secure_filename(doc.title)}.pdf"
            local_path = os.path.join(UPLOAD_FOLDER, 'signed', filename)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                f.write(file_content)
                
            doc.pdf_signed_path = os.path.join('static', 'uploads', 'documents', 'signed', filename)
            doc.signature_type = 'uanataca'
            doc.status = 'signed'
            
            sig = DocumentSignature(document_id=doc.id, user_id=doc.created_by_id, signature_type='uanataca', ip_address=ip_address)
            db.session.add(sig)
            db.session.commit()
            logger.info("Documento firmado electrónicamente completado", doc_id=doc.id)
            return True
            
        return False

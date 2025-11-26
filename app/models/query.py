from flask_sqlalchemy.query import Query
from flask import g

class TenantQuery(Query):
    """
    Query personalizado que intercepta las consultas para aplicar automáticamente
    el filtro por 'condominium_id' si el modelo lo tiene y hay un tenant activo.
    """

    def _get_tenant_id(self):
        """Obtiene el ID del condominio actual desde g.condominium"""
        if hasattr(g, 'condominium') and g.condominium:
            return g.condominium.id
        return None

    def _has_tenant_column(self):
        """Verifica si el modelo principal de la query tiene 'condominium_id'"""
        try:
            if self._mapper_zero():
                return hasattr(self._mapper_zero().class_, 'condominium_id')
        except Exception:
            pass
        return False

    def _apply_filter(self):
        """Aplica el filtro de tenant si corresponde"""
        tenant_id = self._get_tenant_id()
        
        # Si hay tenant y el modelo tiene la columna
        if tenant_id and self._has_tenant_column():
            return self.filter_by(condominium_id=tenant_id)
            
        return self

    # --- Sobrescribir métodos de ejecución ---

    def all(self):
        return Query.all(self._apply_filter())

    def first(self):
        return Query.first(self._apply_filter())

    def one(self):
        return Query.one(self._apply_filter())

    def one_or_none(self):
        return Query.one_or_none(self._apply_filter())
    
    def count(self):
        return Query.count(self._apply_filter())

    def get(self, ident):
        # get() carga por Primary Key. 
        # Estrategia: Cargar y luego validar (Post-Load Validation)
        obj = Query.get(self, ident)
        
        tenant_id = self._get_tenant_id()
        if obj and tenant_id and self._has_tenant_column():
            # Si el objeto no pertenece al tenant actual, devolver None (como si no existiera)
            if getattr(obj, 'condominium_id') != tenant_id:
                return None
                
        return obj

    def paginate(self, **kwargs):
        # Delegar al método paginate de la clase padre pero con el filtro aplicado
        return Query.paginate(self._apply_filter(), **kwargs)


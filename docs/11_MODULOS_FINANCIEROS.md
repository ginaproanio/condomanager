# 11. Estrategia de Módulos Financieros y Monetización

Este documento detalla la arquitectura modular para la gestión financiera del condominio (recibir y gastar dinero) y las estrategias de monetización de la plataforma (generar nuevos ingresos).

---

## PARTE A: Gestión Financiera del Condominio

### 1. Visión de Separación de Poderes
Desacoplamos el "Dinero que entra" del "Dinero que se registra contablemente" y de la "Facturación Legal".

| Módulo | Código | Propósito | Estado |
| :--- | :--- | :--- | :--- |
| **Gestión de Recaudación (Cobranza)** | `collections` | Recibir dinero (PayPhone, Transferencias) y registrar quién pagó. | **ACTIVO** |
| **Contabilidad Condominial** | `accounting` | Registrar asientos, balances, reportes financieros formales. | *PRÓXIMAMENTE* |
| **Caja Chica** | `petty_cash` | Gestión ágil de gastos menores operativos. | **ACTIVO** |
| **Facturación Electrónica (SRI)** | `invoicing` | Emisión de facturas legales válidas para el SRI. | *PLANIFICADO* |

---

### 2. Detalle de Módulos Financieros

#### 2.1 Módulo de Gestión de Recaudación (Cobranza) - `collections`
Este es el módulo **base**.

*   **Funcionalidad Actual:** Pagos completos o parciales vía PayPhone o Transferencia.
*   **Diferimiento (Cuotas):** PayPhone *ya ofrece* al pagador diferir su pago con su tarjeta de crédito al momento de pagar. **NO es el condominio quien financia**, es el banco del emisor de la tarjeta.

#### 2.2 Módulo de Contabilidad Condominial - `accounting`
Para la gestión formal de los libros.

#### 2.3 Módulo de Caja Chica - `petty_cash`
Para la operación diaria de gastos menores. Permite registrar ingresos y egresos de efectivo con comprobantes.

#### 2.4 Facturación Electrónica - `invoicing`
Para legalizar tributariamente los ingresos.

---

## PARTE B: Nuevos Modelos de Negocio (Monetización)

Estos módulos transforman a CondoManager de un "Gasto" para el condominio a un "Generador de Valor".

### 3. Club de Compras (B2B Procurement)
Centralizar el poder de compra de múltiples condominios para obtener precios de mayorista.

*   **Concepto:** "Amazon para Condominios".
*   **Funcionamiento:**
    1.  Se habilita una tienda interna para el Administrador.
    2.  Catálogo: Suministros de limpieza, cloro, focos, uniformes, papelería.
    3.  CondoManager consolida pedidos y negocia con fabricantes.
*   **Monetización:** Margen de intermediación (markup) o rebates por volumen de los proveedores.
*   **Implementación:** Módulo `procurement`.

### 4. Publicidad Hiper-Local (AdServer)
Vender espacios publicitarios digitales a negocios locales que quieren llegar a los residentes.

*   **Concepto:** Publicidad segmentada geográficamente.
*   **Funcionamiento:**
    1.  Negocios (Pizzerías, Farmacias, Gimnasios cercanos) compran "Campañas".
    2.  Formato: Banner en el Dashboard del Residente o Notificación Push ("Promo Viernes").
    3.  Segmentación: "Mostrar solo a residentes de Cumbayá".
*   **Monetización:**
    *   **CPM:** Costo por cada 1,000 impresiones (visualizaciones).
    *   **CPC:** Costo por cada clic en el anuncio.
*   **Implementación:** Módulo `ad_network`.

### 5. Módulo de Recargas y Pagos de Servicios
Permite a los condóminos pagar servicios básicos y realizar recargas desde la plataforma.

*   **Proveedores Integrables:**
    *   **Red Facilito:** Amplia red de recaudación en Ecuador.
    *   **Nuvei, PlacetoPay, Kushki:** Pasarelas robustas con servicios de valor agregado.
    *   **PayPhone:** Ya integrado, ofrece opciones de pago de servicios.
    *   **Ya Ganaste, PonleMás, RAPIACTIVO:** Especializados en recargas digitales.
*   **Beneficio:** Comodidad para el usuario y posible comisión por transacción para la plataforma.

### 6. Módulo de Validación de Datos (KYC)
Para asegurar la veracidad de la información de los residentes y propietarios.

*   **Herramientas:**
    *   **ZampiSoft API Consult:** https://apiconsult.zampisoft.com/ (Ecuador).
    *   **WebServices EC:** http://webservices.ec/.
*   **Uso:** Validar cédulas, RUCs y antecedentes al registrar nuevos usuarios o inquilinos.

---

## 4. Roadmap de Implementación

1.  **Fase 1 (Actual):** Recaudación Sólida + Marketplace Inmobiliario (Sindicación) + Redes Sociales (Perfil).
2.  **Fase 2 (Q2 2025):** Publicidad Hiper-Local (AdServer). Es el "Low Hanging Fruit" (fácil de implementar, alta rentabilidad).
3.  **Fase 3 (Q3 2025):** Club de Compras y Pagos de Servicios. Requiere logística y acuerdos comerciales.

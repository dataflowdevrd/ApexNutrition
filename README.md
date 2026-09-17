# ApexNutrition
Creacion de sistema de inventario, facturacion, integracion a dgii y conectado a n8n


# Apex Nutrition — Enterprise Management System

Sistema integral de gestión empresarial, facturación fiscal, control de inventario farmacéutico y trazabilidad logística para **Apex Nutrition**, la primera marca registrada de creatina en gomitas de República Dominicana.

---

## 📌 Visión del Proyecto

El sistema está diseñado bajo estándares industriales para soportar el ciclo de vida completo de la empresa:
* **Cumplimiento Sanitario (DIGEMAPS):** Trazabilidad obligatoria por lotes de producción, control de fechas de caducidad y retención de muestras.
* **Cumplimiento Fiscal (DGII):** Emisión de Comprobantes Fiscales (NCF/e-CF) para ventas directas (B2C) y canales corporativos en gimnasios y farmacias (B2B).
* **Automatización Omnicanal (n8n):** Integración nativa para la captura de pedidos y estados de pago en tiempo real desde múltiples canales de venta.
* **Logística Automatizada:** Cálculo dinámico de costos de delivery según distancias de entrega.

---

## 🏛️ Arquitectura de Software: Hexagonal (Ports & Adapters)

El núcleo de la aplicación sigue una **Arquitectura Hexagonal**, desacoplando las reglas de negocio puras de los frameworks y servicios externos:

```text
       ┌─────────────────────────────────────────────────────────┐
       │                 CAPA EXTERNA (DRIVERS)                  │
       │     FastAPI (REST API)     │     Streamlit (Dashboard)  │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │               PUERTOS / INTERFACES (PORTS)              │
       │         ProductRepository  │   OrderProcessor           │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                NÚCLEO DEL DOMINIO (CORE)                │
       │    Entidades (Producto, Lote, Venta, Delivery)          │
       │    Lógica de Negocio y Reglas de Validación             │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │               ADAPTADORES DE SALIDA (DRIVEN)            │
       │   Supabase (PostgreSQL 3FN) │ Webhooks Omnicanal (n8n)  │
       └─────────────────────────────────────────────────────────┘

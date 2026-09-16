import uuid
from typing import Tuple
from .models import VentaCreate, TipoNCF

class BillingService:
    ITBIS_RATE = 0.18  # Tasa oficial 18%

    @staticmethod
    def generar_secuencia_ncf(tipo: TipoNCF, secuencia_actual: int) -> str:
        """Formatea el comprobante de acuerdo a la DGII (Letra + Tipo + 8 dígitos)."""
        return f"{tipo.value}{secuencia_actual:08d}"

    @classmethod
    def calcular_totales(cls, venta_data: VentaCreate) -> Tuple[float, float, float]:
        """Calcula Subtotal, ITBIS y Monto Total."""
        subtotal = sum(item.cantidad * item.precio_unitario for item in venta_data.items)
        itbis = round(subtotal * cls.ITBIS_RATE, 2) if venta_data.aplica_itbis else 0.0
        total = round(subtotal + itbis, 2)
        return round(subtotal, 2), itbis, total

class DeliveryService:
    TARIFA_BASE_DOP = 150.00    # Tarifa inicial para los primeros 3 km
    COSTO_POR_KM_EXTRA = 35.00  # Costo por kilómetro adicional
    KM_BASE = 3.0

    @classmethod
    def calcular_tarifa_envio(cls, distancia_km: float) -> float:
        """Calcula el costo de entrega en base a la distancia en km."""
        if distancia_km <= cls.KM_BASE:
            return cls.TARIFA_BASE_DOP
        km_adicionales = distancia_km - cls.KM_BASE
        costo_total = cls.TARIFA_BASE_DOP + (km_adicionales * cls.COSTO_POR_KM_EXTRA)
        return round(costo_total, 2)
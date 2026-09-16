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
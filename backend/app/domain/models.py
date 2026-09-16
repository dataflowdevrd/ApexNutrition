from datetime import datetime, date
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

# --- ENUMERACIONES DEL NEGOCIO ---
class EstadoLote(str, Enum):
    ACTIVO = "ACTIVO"
    PROXIMO_A_VENCER = "PROXIMO_A_VENCER"
    VENCIDO = "VENCIDO"
    AGOTADO = "AGOTADO"

class EstadoDelivery(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_RUTA = "EN_RUTA"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


# --- MODELOS DE DOMINIO ---

class Producto(BaseModel):
    """Representa el producto físico (ej. Gomitas de Creatina Monohidratada)."""
    id: Optional[str] = None
    nombre: str = "Gomitas de Creatina Monohidratada"
    marca: str = "Apex Nutrition"
    registro_sanitario: Optional[str] = None  # Registro DIGEMAPS
    precio_unitario: float = Field(gt=0, description="Precio de venta al público en DOP")
    costo_produccion: float = Field(gt=0, description="Costo unitario de producción en DOP")
    creatina_por_porcion_g: float = Field(default=5.0, description="Gramos de creatina por porción")
    creado_en: datetime = Field(default_factory=datetime.utcnow)


class Lote(BaseModel):
    """Control e inventario por lote de producción (Requisito DIGEMAPS y control de vencimiento)."""
    id: Optional[str] = None
    producto_id: str
    numero_lote: str  # Ej: LOTE-2026-001
    cantidad_inicial: int = Field(gt=0)
    cantidad_actual: int = Field(ge=0)
    fecha_fabricacion: date
    fecha_vencimiento: date
    estado: EstadoLote = EstadoLote.ACTIVO

    def esta_vencido(self, fecha_referencia: Optional[date] = None) -> bool:
        hoy = fecha_referencia or date.today()
        return hoy >= self.fecha_vencimiento


class Delivery(BaseModel):
    """Lógica y costos de logística de envío."""
    id: Optional[str] = None
    cliente_nombre: str
    direccion: str
    distancia_km: float = Field(gt=0)
    tarifa_base_km: float = Field(default=30.0, description="Costo en DOP por kilómetro")
    costo_envio: float = 0.0
    estado: EstadoDelivery = EstadoDelivery.PENDIENTE
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    def calcular_costo(self) -> float:
        """Calcula el costo total del delivery según la distancia."""
        self.costo_envio = round(self.distancia_km * self.tarifa_base_km, 2)
        return self.costo_envio
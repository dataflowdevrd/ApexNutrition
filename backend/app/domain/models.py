from datetime import datetime, date
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict

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


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    marca: Optional[str] = None
    registro_sanitario: Optional[str] = None
    precio_unitario: Optional[float] = Field(default=None, gt=0)
    costo_produccion: Optional[float] = Field(default=None, gt=0)
    creatina_por_porcion_g: Optional[float] = Field(default=None, gt=0)


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


class LoteUpdate(BaseModel):
    numero_lote: Optional[str] = None
    cantidad_inicial: Optional[int] = Field(default=None, gt=0)
    cantidad_actual: Optional[int] = Field(default=None, ge=0)
    fecha_fabricacion: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[EstadoLote] = None


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
    
class TipoNCF(str, Enum):
    CREDITO_FISCAL = "B01"  # Para ventas B2B (Gimnasios, Tiendas, Farmacias)
    CONSUMO_FINAL = "B02"   # Para ventas directas B2C

class MetodoPago(str, Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    TARJETA = "TARJETA"

class ItemVentaCreate(BaseModel):
    lote_id: str
    cantidad: int = Field(gt=0)
    precio_unitario: float = Field(gt=0)

class VentaCreate(BaseModel):
    cliente_id: Optional[str] = None
    tipo_ncf: TipoNCF = TipoNCF.CONSUMO_FINAL
    metodo_pago: MetodoPago = MetodoPago.TRANSFERENCIA
    items: List[ItemVentaCreate] = Field(..., min_length=1)
    aplica_itbis: bool = True  # 18% según corresponda

class VentaResponse(BaseModel):
    id: str
    codigo_factura: str
    ncf: str
    subtotal: float
    itbis: float
    total: float
    estado: str
    creado_en: datetime
    
class DeliveryCreate(BaseModel):
    venta_id: str
    direccion_destino: str
    sector: Optional[str] = None
    distancia_km: Optional[float] = Field(default=None, gt=0, description="Distancia estimada; se calcula con Google Maps si se envían coordenadas")
    contacto_receptor: Optional[str] = None
    telefono_receptor: Optional[str] = None
    notas_entrega: Optional[str] = None
    destino_lat: Optional[float] = None
    destino_lng: Optional[float] = None


class DeliveryQuoteRequest(BaseModel):
    destino_lat: float
    destino_lng: float
    origen_lat: Optional[float] = None
    origen_lng: Optional[float] = None


class DeliveryQuoteResponse(BaseModel):
    distancia_km: float
    duracion_minutos: Optional[int] = None
    costo_envio_dop: float
    proveedor: str

class DeliveryResponse(BaseModel):
    id: str
    venta_id: str
    direccion_destino: str
    sector: Optional[str] = None
    distancia_km: float
    costo_envio_dop: float
    estado: EstadoDelivery
    creado_en: datetime
    destino_lat: Optional[float] = None
    destino_lng: Optional[float] = None
    


class OrigenCanal(str, Enum):
    WHATSAPP = "WHATSAPP"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    WEB_FORM = "WEB_FORM"

class EventoOmnicanalCreate(BaseModel):
    canal: OrigenCanal
    payload: Dict[str, Any]
    identificador_externo: Optional[str] = None
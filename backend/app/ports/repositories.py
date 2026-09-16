from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.models import Lote, LoteUpdate, Producto, ProductoUpdate
from ..domain.models import VentaCreate, VentaResponse
from ..domain.models import DeliveryCreate, DeliveryResponse

class ProductRepositoryPort(ABC):
    @abstractmethod
    def create_product(self, product: Producto) -> Producto:
        pass

    @abstractmethod
    def list_products(self) -> List[Producto]:
        pass

    @abstractmethod
    def update_product(self, product_id: str, product: ProductoUpdate) -> Producto:
        pass

    @abstractmethod
    def delete_product(self, product_id: str) -> None:
        pass

class LotRepositoryPort(ABC):
    @abstractmethod
    def create_lot(self, lot: Lote) -> Lote:
        pass

    @abstractmethod
    def list_lots_by_product(self, product_id: str) -> List[Lote]:
        pass

    @abstractmethod
    def update_lot(self, lot_id: str, lot: LoteUpdate) -> Lote:
        pass

    @abstractmethod
    def delete_lot(self, lot_id: str) -> None:
        pass
    


class SaleRepositoryPort(ABC):
    @abstractmethod
    def create_sale(self, venta: VentaCreate, subtotal: float, itbis: float, total: float, ncf: str) -> dict:
        pass
    


class DeliveryRepositoryPort(ABC):
    @abstractmethod
    def create_delivery(self, delivery: DeliveryCreate, costo_envio: float) -> dict:
        pass

    @abstractmethod
    def get_delivery_by_sale(self, venta_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def update_delivery_status(self, delivery_id: str, status: str) -> dict:
        pass
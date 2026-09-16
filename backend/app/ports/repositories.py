from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.models import Producto, Lote

class ProductRepositoryPort(ABC):
    @abstractmethod
    def create_product(self, product: Producto) -> Producto:
        pass

    @abstractmethod
    def list_products(self) -> List[Producto]:
        pass

class LotRepositoryPort(ABC):
    @abstractmethod
    def create_lot(self, lot: Lote) -> Lote:
        pass

    @abstractmethod
    def list_lots_by_product(self, product_id: str) -> List[Lote]:
        pass
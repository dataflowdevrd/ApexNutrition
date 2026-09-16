from typing import List
from ..ports.repositories import ProductRepositoryPort, LotRepositoryPort
from ..domain.models import Producto, Lote
from .database import supabase

class SupabaseProductRepository(ProductRepositoryPort):
    def create_product(self, product: Producto) -> Producto:
        data = {
            "nombre": product.nombre,
            "marca": product.marca,
            "registro_sanitario": product.registro_sanitario,
            "precio_base_dop": product.precio_unitario,
            "costo_produccion_dop": product.costo_produccion,
            "gramos_creatina_porcion": product.creatina_por_porcion_g,
            "sku": "APX-CRT-001"
        }
        res = supabase.table("productos").insert(data).execute()
        created = res.data[0]
        product.id = created["id"]
        return product

    def list_products(self) -> List[Producto]:
        res = supabase.table("productos").select("*").execute()
        return [
            Producto(
                id=item["id"],
                nombre=item["nombre"],
                marca=item["marca"],
                registro_sanitario=item["registro_sanitario"],
                precio_unitario=item["precio_base_dop"],
                costo_produccion=item["costo_produccion_dop"],
                creatina_por_porcion_g=item["gramos_creatina_porcion"]
            )
            for item in res.data
        ]

class SupabaseLotRepository(LotRepositoryPort):
    def create_lot(self, lot: Lote) -> Lote:
        data = {
            "producto_id": lot.producto_id,
            "numero_lote": lot.numero_lote,
            "cantidad_inicial": lot.cantidad_inicial,
            "cantidad_actual": lot.cantidad_actual,
            "fecha_fabricacion": str(lot.fecha_fabricacion),
            "fecha_vencimiento": str(lot.fecha_vencimiento),
            "estado": lot.estado.value
        }
        res = supabase.table("lotes").insert(data).execute()
        created = res.data[0]
        lot.id = created["id"]
        return lot

    def list_lots_by_product(self, product_id: str) -> List[Lote]:
        res = supabase.table("lotes").select("*").eq("producto_id", product_id).execute()
        return [
            Lote(
                id=item["id"],
                producto_id=item["producto_id"],
                numero_lote=item["numero_lote"],
                cantidad_inicial=item["cantidad_inicial"],
                cantidad_actual=item["cantidad_actual"],
                fecha_fabricacion=item["fecha_fabricacion"],
                fecha_vencimiento=item["fecha_vencimiento"],
                estado=item["estado"]
            )
            for item in res.data
        ]
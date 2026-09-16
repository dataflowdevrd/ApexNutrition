from typing import List
from ..ports.repositories import ProductRepositoryPort, LotRepositoryPort
from ..domain.models import Lote, LoteUpdate, Producto, ProductoUpdate
from .database import supabase
import random
from ..ports.repositories import SaleRepositoryPort
import uuid

class SupabaseProductRepository(ProductRepositoryPort):
    def create_product(self, product: Producto) -> Producto:
        sku_generado = f"APX-CRT-{uuid.uuid4().hex[:6].upper()}"
        data = {
            "sku": sku_generado,
            "nombre": product.nombre,
            "marca": product.marca,
            "registro_sanitario": product.registro_sanitario,
            "precio_base_dop": product.precio_unitario,
            "costo_produccion_dop": product.costo_produccion,
            "gramos_creatina_porcion": product.creatina_por_porcion_g,
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

    def update_product(self, product_id: str, product: ProductoUpdate) -> Producto:
        data = {
            "nombre": product.nombre,
            "marca": product.marca,
            "registro_sanitario": product.registro_sanitario,
            "precio_base_dop": product.precio_unitario,
            "costo_produccion_dop": product.costo_produccion,
            "gramos_creatina_porcion": product.creatina_porcion_g,
        }
        data = {key: value for key, value in data.items() if value is not None}
        if not data:
            raise ValueError("Debe proporcionar al menos un campo para actualizar")
        res = supabase.table("productos").update(data).eq("id", product_id).execute()
        if not res.data:
            raise LookupError("Producto no encontrado")
        item = res.data[0]
        return Producto(
            id=item["id"], nombre=item["nombre"], marca=item["marca"],
            registro_sanitario=item.get("registro_sanitario"),
            precio_unitario=item["precio_base_dop"],
            costo_produccion=item["costo_produccion_dop"],
            creatina_por_porcion_g=item["gramos_creatina_porcion"],
        )

    def delete_product(self, product_id: str) -> None:
        res = supabase.table("productos").delete().eq("id", product_id).execute()
        if not res.data:
            raise LookupError("Producto no encontrado")

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

    def update_lot(self, lot_id: str, lot: LoteUpdate) -> Lote:
        data = lot.model_dump(exclude_unset=True, exclude_none=True, mode="json")
        if "estado" in data:
            data["estado"] = data["estado"].value
        if not data:
            raise ValueError("Debe proporcionar al menos un campo para actualizar")
        res = supabase.table("lotes").update(data).eq("id", lot_id).execute()
        if not res.data:
            raise LookupError("Lote no encontrado")
        item = res.data[0]
        return Lote(**item)

    def delete_lot(self, lot_id: str) -> None:
        res = supabase.table("lotes").delete().eq("id", lot_id).execute()
        if not res.data:
            raise LookupError("Lote no encontrado")


class SupabaseSaleRepository(SaleRepositoryPort):
    def create_sale(self, venta, subtotal: float, itbis: float, total: float, ncf: str) -> dict:
        codigo_factura = f"FAC-{random.randint(10000, 99999)}"
        items = [item.model_dump() for item in venta.items]
        response = supabase.rpc("registrar_venta_transaccional", {
            "p_cliente_id": venta.cliente_id,
            "p_codigo_factura": codigo_factura,
            "p_tipo_ncf": venta.tipo_ncf.value,
            "p_ncf": ncf,
            "p_metodo_pago": venta.metodo_pago.value,
            "p_subtotal": subtotal,
            "p_itbis": itbis,
            "p_total": total,
            "p_items": items,
        }).execute()
        if not response.data:
            raise RuntimeError("Supabase no devolvió la venta creada")
        return response.data if isinstance(response.data, dict) else response.data[0]

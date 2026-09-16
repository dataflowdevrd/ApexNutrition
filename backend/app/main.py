from fastapi import FastAPI, HTTPException
from typing import List
import random
from .domain.models import Lote, LoteUpdate, Producto, ProductoUpdate
from .adapters.supa_base_repository import SupabaseProductRepository, SupabaseLotRepository
from .domain.models import VentaCreate, VentaResponse
from .domain.services import BillingService
from .adapters.supa_base_repository import SupabaseSaleRepository

app = FastAPI(
    title="Apex Nutrition API",
    description="Motor de facturación, inventario y logística para gomitas de creatina en RD.",
    version="1.0.0"
)

product_repo = SupabaseProductRepository()
lot_repo = SupabaseLotRepository()

@app.get("/")
def read_root():
    return {"status": "ok", "app": "Apex Nutrition API"}

@app.post("/productos", response_model=Producto, status_code=201)
def crear_producto(producto: Producto):
    try:
        return product_repo.create_product(producto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/productos", response_model=List[Producto])
def listar_productos():
    return product_repo.list_products()

@app.put("/productos/{producto_id}", response_model=Producto)
@app.patch("/productos/{producto_id}", response_model=Producto)
def actualizar_producto(producto_id: str, producto: ProductoUpdate):
    try:
        return product_repo.update_product(producto_id, producto)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/productos/{producto_id}", status_code=204)
def eliminar_producto(producto_id: str):
    try:
        product_repo.delete_product(producto_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/lotes", response_model=Lote, status_code=201)
def crear_lote(lote: Lote):
    try:
        return lot_repo.create_lot(lote)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/productos/{producto_id}/lotes", response_model=List[Lote])
def listar_lotes(producto_id: str):
    return lot_repo.list_lots_by_product(producto_id)

@app.put("/lotes/{lote_id}", response_model=Lote)
@app.patch("/lotes/{lote_id}", response_model=Lote)
def actualizar_lote(lote_id: str, lote: LoteUpdate):
    try:
        return lot_repo.update_lot(lote_id, lote)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/lotes/{lote_id}", status_code=204)
def eliminar_lote(lote_id: str):
    try:
        lot_repo.delete_lot(lote_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


sale_repo = SupabaseSaleRepository()

@app.post("/ventas", response_model=VentaResponse, status_code=201)
def registrar_venta(venta: VentaCreate):
    try:
        # Calcular montos
        subtotal, itbis, total = BillingService.calcular_totales(venta)
        
        # Generar NCF consecutivo simulado
        # En producción esto lee el último correlativo autorizado por la DGII
        consecutivo_simulado = random.randint(1, 9999)
        ncf = BillingService.generar_secuencia_ncf(venta.tipo_ncf, consecutivo_simulado)
        
        # Persistir venta y descontar stock automáticamente
        resultado = sale_repo.create_sale(venta, subtotal, itbis, total, ncf)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
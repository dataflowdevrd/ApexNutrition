from fastapi import FastAPI, HTTPException
from typing import List
from .domain.models import Producto, Lote
from .adapters.supa_base_repository import SupabaseProductRepository, SupabaseLotRepository

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

@app.post("/lotes", response_model=Lote, status_code=201)
def crear_lote(lote: Lote):
    try:
        return lot_repo.create_lot(lote)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/productos/{producto_id}/lotes", response_model=List[Lote])
def listar_lotes(producto_id: str):
    return lot_repo.list_lots_by_product(producto_id)
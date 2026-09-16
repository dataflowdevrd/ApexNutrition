from fastapi import FastAPI
from .adapters.database import supabase

app = FastAPI(title="Apex Nutrition API")

@app.get("/")
def read_root():
    return {"message": "API de Apex Nutrition funcionando correctamente"}

@app.get("/test-db")
def test_database():
    try:
        # Consultar la tabla productos para verificar conexión
        response = supabase.table("productos").select("*").execute()
        return {
            "status": "Conexión exitosa a Supabase",
            "data": response.data
        }
    except Exception as e:
        return {"status": "Error de conexión", "details": str(e)}
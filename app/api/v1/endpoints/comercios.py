"""
Endpoints relacionados con comercios
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/")
async def listar_comercios():
    """Lista todos los comercios (placeholder)"""
    return {"message": "Endpoint de comercios - En desarrollo"}


@router.get("/{comercio_id}")
async def obtener_comercio(comercio_id: int):
    """Obtiene un comercio por ID (placeholder)"""
    return {"message": f"Obtener comercio {comercio_id} - En desarrollo"}


@router.post("/")
async def crear_comercio():
    """Crea un nuevo comercio (placeholder)"""
    return {"message": "Crear comercio - En desarrollo"}


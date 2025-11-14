"""
Endpoints relacionados con usuarios
"""
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()


@router.get("/")
async def listar_usuarios():
    """Lista todos los usuarios (placeholder)"""
    return {"message": "Endpoint de usuarios - En desarrollo"}


@router.get("/{usuario_id}")
async def obtener_usuario(usuario_id: int):
    """Obtiene un usuario por ID (placeholder)"""
    return {"message": f"Obtener usuario {usuario_id} - En desarrollo"}


@router.post("/")
async def crear_usuario():
    """Crea un nuevo usuario (placeholder)"""
    return {"message": "Crear usuario - En desarrollo"}


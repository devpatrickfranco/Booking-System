from typing import List, Optional # Importe Optional para a busca de nome

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

import crud, schemas 

router = APIRouter(
    prefix="/salas", # Geralmente usamos o plural no prefixo RESTful
    tags=["Salas"] # Capitalize tags
)

@router.get("/", response_model=List[schemas.Sala]) # Adicione response_model para FastAPI documentar
def get_all_salas(
    nome: Optional[str] = None, # Adicione o parâmetro nome para busca
    db: Session = Depends(get_db)
):
    """
    Retorna todas as salas cadastradas no sistema.
    Pode filtrar por nome (busca parcial e case-insensitive).
    """
    try:
        return crud.get_all_salas(db=db, nome=nome) # Passe o nome para o CRUD
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")

@router.get("/{sala_id}", response_model=schemas.Sala, status_code=status.HTTP_200_OK)
def get_sala_by_id(
    sala_id: int, # Isso captura o '1' da URL /salas/1
    db: Session = Depends(get_db)
):
    """
    Busca uma sala pelo ID.
    Retorna 404 Not Found se a sala não for encontrada.
    """
    sala = crud.get_sala_by_id(db=db, sala_id=sala_id)
    if not sala:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada.")
    
    return sala

@router.post("/", response_model=schemas.Sala, status_code=status.HTTP_201_CREATED)
def create_sala(
    sala: schemas.SalaCreate, # Use SalaCreate para a entrada
    db: Session = Depends(get_db)
):
    """
    Cria uma nova sala no sistema.
    """
    try:
        return crud.create_sala(db=db, sala=sala) # Mantenha a ordem dos parâmetros ou nomeie-os
    except crud.DuplicateEntryError as e: # Capture a exceção específica de duplicidade
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except Exception as e: # Captura outros erros inesperados
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")

@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sala(
    sala_id: int, # Isso captura o '1' da URL /salas/1
    db: Session = Depends(get_db)
):
    """
    Deleta uma sala pelo ID.
    Retorna 204 No Content se a sala for deletada com sucesso.
    """
    try:
        deleted = crud.delete_sala(db=db, sala_id=sala_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada.")
        
        # Como o status é 204, não precisamos retornar nada. FastAPI lida com isso.
        return 
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")
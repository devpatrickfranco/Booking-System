from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload # Importe joinedload aqui se não estiver em outro lugar

from database import get_db
import crud, schemas # Assumindo que crud.py e schemas.py estão no mesmo nível da pasta

router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"]
)

# --- ROTAS GET ---

# 1. Rota mais específica: Busca por intervalo (com caminho literal fixo)
@router.get("/intervalo", response_model=List[schemas.Reserva], status_code=status.HTTP_200_OK)
def get_reservas_by_intervalo(
    data_inicio: datetime, # Parâmetro de consulta (query parameter)
    data_final: datetime,  # Parâmetro de consulta (query parameter)
    db: Session = Depends(get_db)):
    """
    Retorna todas as reservas que se sobrepõem a um período de datas específico.
    Exemplo de uso: /reservas/intervalo?data_inicio=2025-06-26T15:00:00&data_final=2025-06-26T17:00:00
    """
    try:
        reservas = crud.get_resrevas_by_period(
            db=db,
            start_date=data_inicio,
            end_date=data_final
        )
        return reservas
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")

# 2. Rota para buscar uma reserva por ID (parâmetro de caminho)
@router.get("/{reserva_id}", response_model=schemas.Reserva, status_code=status.HTTP_200_OK)
def get_reserva_by_id_endpoint(reserva_id: int, db: Session = Depends(get_db)):
    """
    Busca uma reserva pelo ID.
    Retorna 404 Not Found se a reserva não for encontrada.
    Exemplo de uso: /reservas/123
    """
    reserva = crud.get_reserva_by_id(db=db, reserva_id=reserva_id)
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva não encontrada.")
    
    return reserva

# 3. Rota mais genérica: Busca todas as reservas (sem parâmetros de caminho)
@router.get("/", response_model=List[schemas.Reserva])
def get_all_reservas_endpoint(db: Session = Depends(get_db)):
    """
    Retorna todas as reservas cadastradas no sistema.
    """
    try:
        # Assumindo que você terá uma função crud.get_all_reservas em crud.py
        # ou, para simplicidade, um query direto:
        return crud.get_all_reservas(db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")

# --- OUTRAS ROTAS ---

@router.post("/", response_model=schemas.Reserva, status_code=status.HTTP_201_CREATED)
def create_reserva_endpoint(reserva: schemas.ReservaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova reserva.
    """
    try:
        return crud.create_reserva(db=db, reserva=reserva)
    except crud.ReservationConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")
    
@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reserva_endpoint(reserva_id: int, db: Session = Depends(get_db)):
    """
    Deleta uma reserva pelo ID.
    Retorna 204 No Content se a reserva foi deletada com sucesso.
    Retorna 404 Not Found se a reserva não for encontrada.
    """
    deleted = crud.delete_reserva(db=db, reserva_id=reserva_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva não encontrada.")
    
    return
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc as sa_exc

from datetime import datetime

import models, schemas

class DuplicateEntryError(Exception):
    def __init__(self, message="Já existe um item com este identificador único."):
        self.message = message
        super().__init__(self.message)


def get_all_users(db: Session) -> List[models.Usuario]:
    """
    Retorna todos os usuários cadastrados no sistema.
    """
    return db.query(models.Usuario).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.Usuario]:
    """
    Busca um usuário pelo ID.
    Retorna None se o usuário não for encontrado.
    """
    return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()

def create_user(db: Session, user: schemas.UsuarioCreate) -> models.Usuario:
    db_usuario = models.Usuario(**user.model_dump())
    db.add(db_usuario)
    try:
        db.commit()
        db.refresh(db_usuario)
    except sa_exc.IntegrityError:
        db.rollback()
        raise DuplicateEntryError("Email já cadastrado.")
    return db_usuario

def delete_user(db: Session, user_id: int) -> bool:
    """
    Deleta um usuário do banco de dados.
    Retorna True se o usuário foi deletado, False se não foi encontrado.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not usuario:
        return False  # Usuário não encontrado

    db.delete(usuario)
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise  # Relança a exceção para ser tratada pelo router


# ===== salas =====

def get_all_salas(db: Session, nome: Optional[str] = None) -> List[models.Sala]:
    query = db.query(models.Sala).options(joinedload(models.Sala.reservas))
    if nome:
        query = query.filter(models.Sala.nome.ilike(f"%{nome}%"))
    return query.all()

def get_sala_by_id(db: Session, sala_id: int) -> Optional[models.Sala]:
    """
    Busca uma sala pelo ID.
    Retorna None se a sala não for encontrada.
    """
    return db.query(models.Sala).filter(models.Sala.id == sala_id).first()

def create_sala(db: Session, sala: schemas.SalaCreate) -> models.Sala:
    normalized_nome = sala.nome.strip().lower()

    existing_sala = db.query(models.Sala).filter(models.Sala.nome == normalized_nome).first()
    if existing_sala:
        raise DuplicateEntryError(f"Já existe uma sala com o nome '{sala.nome}'.")

    db_sala = models.Sala(**sala.model_dump())
    db_sala.nome = normalized_nome

    db.add(db_sala)
    try:
        db.commit()
        db.refresh(db_sala)
    except sa_exc.IntegrityError as e:
        db.rollback()
        # Fallback para o caso de concorrência ou outra violação UNIQUE
        if "UNIQUE constraint failed" in str(e) and "salas.nome" in str(e):
             raise DuplicateEntryError(f"Já existe uma sala com o nome '{sala.nome}'.")
        raise
    return db_sala

def delete_sala(db: Session, sala_id: int) -> bool:
    """
    Deleta uma sala do banco de dados.
    Retorna True se a sala foi deletada, False se não foi encontrada.
    """
    sala = db.query(models.Sala).filter(models.Sala.id == sala_id).first()
    if not sala:
        return False # Sala não encontrada

    # Opcional: Lidar com dependências (e.g., reservas).
    # Dependendo da sua configuração ForeignKey (ON DELETE CASCADE),
    # as reservas podem ser deletadas automaticamente.
    # Caso contrário, você precisaria deletá-las explicitamente aqui.
    # Ex: db.query(models.Reserva).filter(models.Reserva.id_sala == sala_id).delete()

    db.delete(sala)
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise # Relança a exceção para ser tratada pelo router

# ===== reservas =====

def get_all_reservas(db: Session, sala_id: Optional[int] = None, user_id: Optional[int] = None) -> List[models.Reserva]:
    query = db.query(models.Reserva).options(joinedload(models.Reserva.sala), joinedload(models.Reserva.usuario))
    if sala_id:
        query = query.filter(models.Reserva.id_sala == sala_id)
    if user_id:
        query = query.filter(models.Reserva.id_usuario == user_id)
    
    return query.all()

def get_reserva_by_id(db: Session, reserva_id: int) -> Optional[models.Reserva]:
    """
    Busca uma reserva pelo ID.
    Retorna None se a reserva não for encontrada.
    """

    return db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()

def get_resrevas_by_period(db: Session, start_date: datetime, end_date: datetime) -> List[models.Reserva]:
    """
    Retorna todas as reservas que se sobrepõem ao período fornecido.
    """
    query = db.query(models.Reserva)

    query = query.filter(
        models.Reserva.data_inicio < end_date,
        models.Reserva.data_final > start_date
    )
    query = query.options(
        joinedload(models.Reserva.sala),
        joinedload(models.Reserva.usuario)
    )

    return query.all()
    
def create_reserva(db: Session, reserva: schemas.ReservaCreate) -> models.Reserva:
    # Verifica se a sala existe
    sala = db.query(models.Sala).filter(models.Sala.id == reserva.id_sala).first()
    if not sala:
        raise ValueError(f"Sala com ID {reserva.id_sala} não encontrada.")

    # Verifica se o usuário existe
    usuario = db.query(models.Usuario).filter(models.Usuario.id == reserva.id_usuario).first()
    if not usuario:
        raise ValueError(f"Usuário com ID {reserva.id_usuario} não encontrado.")

    # Verifica se a quantidade de participantes não excede a capacidade da sala
    capacidade_sala = sala.capacidade
    if reserva.participantes > capacidade_sala:
        raise ValueError(f"A quantidade de participantes ({reserva.participantes}) excede a capacidade da sala ({capacidade_sala}).")

    
    db_reserva = models.Reserva(**reserva.model_dump())
    db.add(db_reserva)
    try:
        db.commit()
        db.refresh(db_reserva)
    except sa_exc.IntegrityError as e:
        db.rollback()
        raise DuplicateEntryError("Já existe uma reserva com esses dados.")
    
    return db_reserva

def delete_reserva(db: Session, reserva_id: int) -> bool:
    """
    Deleta uma reserva do banco de dados.
    Retorna True se a reserva foi deletada, False se não foi encontrada.
    """
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        return False  # Reserva não encontrada

    db.delete(reserva)
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise  # Relança a exceção para ser tratada pelo router
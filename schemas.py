from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Schemas para Usuario ---
class UsuarioBase(BaseModel):
    nome: str
    email: str

class UsuarioCreate(UsuarioBase):
    # Este schema é usado para criar um novo usuário.
    # Não inclui 'id', pois ele é gerado pelo banco de dados.
    pass

class Usuario(UsuarioBase):
    # Este schema é usado para retornar um usuário existente.
    # Inclui 'id' e as relações (salas), que são carregadas do DB.
    id: int
    salas: List["Sala"] = [] # Forward reference para evitar circularidade

    class Config:
        from_attributes = True

# --- Schemas para Sala ---
class SalaBase(BaseModel):
    nome: str
    capacidade: int
    localizacao: str

class SalaCreate(SalaBase):
    # Este schema é usado para criar uma nova sala.
    pass

class Sala(SalaBase):
    # Este schema é usado para retornar uma sala existente.
    # Inclui 'id' e as relações (usuarios, reservas).
    id: int
    usuarios: List[Usuario] = []
    reservas: List["Reserva"] = [] # Forward reference para evitar circularidade

    class Config:
        from_attributes = True

# --- Schemas para Reserva ---
class ReservaBase(BaseModel):
    id_sala: int
    id_usuario: int
    data_inicio: datetime
    data_final: datetime

class ReservaCreate(ReservaBase):
    # Este schema é usado para criar uma nova reserva.
    # Adicionei 'participantes' aqui se ele for um campo de entrada na criação.
    participantes: int = 0 # Valor padrão, ajuste se for obrigatório

class Reserva(ReservaBase):
    # Este schema é usado para retornar uma reserva existente.
    id: int
    sala: SalaBase # Inclui o objeto Sala completo
    usuario: UsuarioBase # Inclui o objeto Usuario completo
    participantes: int # O campo 'participantes' deve vir do banco de dados

    class Config:
        from_attributes = True

# --- Ajuste de Forward References (IMPORTANTE para evitar erros) ---
# Isso resolve dependências circulares entre os modelos
Usuario.model_rebuild()
Sala.model_rebuild()
Reserva.model_rebuild()
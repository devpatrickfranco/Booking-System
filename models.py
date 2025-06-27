from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

sala_usuario = Table(
    'sala_usuario',
    Base.metadata,
    Column('sala_id', Integer, ForeignKey('salas.id')),
    Column('usuario_id', Integer, ForeignKey('usuarios.id'))
)

class Sala(Base):
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, unique=True)
    capacidade = Column(Integer, index=True)
    localizacao = Column(String, index=True)

    usuarios = relationship("Usuario", secondary=sala_usuario, back_populates="salas")
    reservas = relationship("Reserva", back_populates="sala")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, index=True, unique=True)

    salas = relationship("Sala", secondary=sala_usuario, back_populates="usuarios")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    id_sala = Column(Integer, ForeignKey('salas.id'), unique=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id'))
    data_inicio = Column(DateTime, index=True)
    data_final = Column(DateTime, index=True)
    participantes = Column(Integer, default=0)

    sala = relationship("Sala", back_populates="reservas")
    usuario = relationship("Usuario")
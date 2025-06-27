from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers.usuarios import usuarios
from routers.salas import salas
from routers.reservas import reservas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração de origem
origins = [ 
    "http://localhost:5173",
]

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite todas as origens, ajuste conforme necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(salas.router)
app.include_router(reservas.router)

@app.get("/")
async def root():
    return {"message": "API com CORS habilitado"}
from typing import List, Optional # Keep Optional for potential future filters

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

import crud, schemas, models# No need to import 'models' directly in the router

router = APIRouter(
    prefix="/usuarios", # Plural is common for RESTful endpoints
    tags=["Usuários"] # Capitalized tag for consistency
)

@router.get("/", response_model=List[schemas.Usuario]) # Specify the response model
def get_all_users(db: Session = Depends(get_db)):
    """
    Returns all registered users in the system.
    """
    try:
        # Assuming you'll add a get_all_users function in crud.py
        # You can add filters here if needed, similar to get_all_salas
        return db.query(models.Usuario).all() # Simple retrieval if no specific CRUD function yet
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")

@router.get("/{user_id}", response_model=schemas.Usuario, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):

    """"
        Retrieves a user by ID.
        return user
    """

    try:
        return crud.get_user_by_id(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Internal server error: {e}")

@router.post("/", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: schemas.UsuarioCreate, db: Session = Depends(get_db)): # Use UsuarioCreate for input
    """
    Creates a new user in the system.
    """
    try:
        return crud.create_user(db=db, user=user)
    except crud.DuplicateEntryError as e: # Catch the specific custom exception
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message) # Use 409 Conflict
    except Exception as e: # Catch any other unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deletes a user by ID.
    Returns 204 No Content on success.
    """
    try:
        user = crud.get_user_by_id(db=db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
        crud.delete_user(db=db, user_id=user_id) # Assuming you have this function in crud.py
        return None # FastAPI will return 204 No Content automatically
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
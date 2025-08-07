from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from db import models
from schemas.user import UserCreate, UserOut, UserLogin, Token
from core.security import hash_password as get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si ya existe un usuario con ese email
        existing_email = db.query(models.User).filter(
            models.User.email == user.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado."
            )

        # Verificar si ya existe un usuario con ese username
        existing_username = db.query(models.User).filter(
            models.User.username == user.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está registrado."
            )

        # Buscar rol en tabla de roles (por nombre: 'user' o 'admin')
        role_name = user.role.value if user.role else "user"
        role = db.query(models.Role).filter(
            models.Role.name == role_name).first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido. Debe ser 'admin' o 'user'."
            )

        # Crear el nuevo usuario
        new_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password),
            role_id=role.id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserOut(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            role_name=role.name
        )

    except Exception as e:
        print(f"Error en register: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al registrar usuario"
        )


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos."
        )

    if not db_user.role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El usuario no tiene un rol asignado."
        )

    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role.name}
    )

    return {"access_token": access_token, "token_type": "bearer"}

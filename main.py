import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, get_db, Base
import models
import auth

# Cria a pasta raiz física do banco primeiro (OBRIGATÓRIO PARA GIT LIMPO)
import os
UPLOADS_DIR = "uploads/books"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Depois que a pasta existe, Inicia o Banco de Dados gerando o arquivo dentro dela automaticamente
Base.metadata.create_all(bind=engine)

# Seeder de Administração: Se o banco estiver zerado, cria o primeiro usuário automaticamente
def init_admin():
    from database import SessionLocal
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            default_email = os.getenv("ADMIN_EMAIL", "admin@oasis.com")
            default_password = os.getenv("ADMIN_PASSWORD", "admin123")
            hashed_pw = auth.get_password_hash(default_password)
            db.add(models.User(email=default_email, hashed_password=hashed_pw))
            db.commit()
            print(f"Admin inicial criado com {default_email}")
    except Exception as e:
        print(f"Erro ao injetar Admin: {e}")
    finally:
        db.close()
init_admin()

app = FastAPI(title="Biblioteca API Digital")

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/api/register")
# def register_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == form.username).first()
#     if user:
#         raise HTTPException(status_code=400, detail="Este e-mail já existe.")
    
#     hashed_password = auth.get_password_hash(form.password)
#     new_user = models.User(email=form.username, hashed_password=hashed_password)
#     db.add(new_user)
#     db.commit()
#     return {"message": "Conta criada com sucesso!"}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos.")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/books")
def get_books(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Book).filter(models.Book.user_id == user.id).all()

@app.post("/api/books/upload")
async def upload_book(
    title: str = Form(""),
    author: str = Form(""),
    shelf: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    ext = file.filename.split(".")[-1]
    import uuid
    safe_filename = f"{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    new_book = models.Book(
        title=title or file.filename,
        author=author or "Desconhecido",
        shelf=shelf,
        type=ext,
        file_path=f"/api/files/{safe_filename}",
        user_id=user.id
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

from fastapi.responses import FileResponse
@app.get("/api/files/{filename}")
def get_file(filename: str, user: models.User = Depends(auth.get_current_user)):
    if not filename.startswith(f"{user.id}_"):
         raise HTTPException(status_code=403, detail="Não autorizado.")
    
    file_path = os.path.join(UPLOADS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Arquivo físico não existe mais na VPS.")


# Magia de Fábrica (Servir o React como se fosse views)
dist_dir = "dist"
if os.path.isdir(dist_dir):
    app.mount("/assets", StaticFiles(directory=f"{dist_dir}/assets"), name="assets")
    app.mount("/pwa-192x192.png", StaticFiles(directory=dist_dir), name="pwa192")
    app.mount("/pwa-512x512.png", StaticFiles(directory=dist_dir), name="pwa512")
    app.mount("/vite.svg", StaticFiles(directory=dist_dir), name="vite")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        index_file = os.path.join(dist_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"msg": "Por favor, rode 'npm run build' primeiro no app_build"}

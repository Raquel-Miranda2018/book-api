from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import health, books, categories, stats, auth, scraping, ml
from app.utils.middleware import LoggingMiddleware
from app.database import Base, engine
from app.models.book import Book
from app.models.user import User
from app.models.api_log import APILog

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Book Recommendation API - Tech Challenge Phase 1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(books.router, prefix="/api/v1", tags=["Books"])
app.include_router(categories.router, prefix="/api/v1", tags=["Categories"])
app.include_router(stats.router, prefix="/api/v1", tags=["Statistics"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(scraping.router, prefix="/api/v1", tags=["Admin"])
app.include_router(ml.router, prefix="/api/v1", tags=["ML Pipeline"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Book Recommendation API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    from app.database import SessionLocal
    from app.utils.security import get_password_hash

    # Garante que todas as tabelas existam
    Base.metadata.create_all(bind=engine)

    # Cria o admin se não existir
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if not admin:
            admin_user = User(
                username=settings.ADMIN_USERNAME,
                email=f"{settings.ADMIN_USERNAME}@example.com",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                is_active=True,
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ Admin '{settings.ADMIN_USERNAME}' criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
    finally:
        db.close()

    print(f"🚀 API {settings.APP_NAME} v{settings.APP_VERSION} Online")
    
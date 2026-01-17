import sys
import os
import pandas as pd
from sqlalchemy import func

# Adiciona o diretório raiz ao sys.path para permitir imports do módulo 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine, SessionLocal
# IMPORTANTE: Importar os modelos para que o SQLAlchemy os reconheça
from app.models.book import Book
from app.models.user import User
from app.models.api_log import APILog

def migrate_data():
    """Migrate data from CSV to SQLite database"""
    print("🚀 Starting database migration...")
    
    # 1. Criar as tabelas se elas não existirem
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Verificar se o CSV existe
    csv_path = os.path.join("data", "books.csv")
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        return

    # 3. Ler o CSV
    print(f"📥 Reading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Successfully read {len(df)} books from CSV")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # 4. Inserir no Banco
    db = SessionLocal()
    try:
        # Limpar dados antigos para evitar duplicatas
        print("🧹 Cleaning existing data...")
        db.query(Book).delete()
        
        print("📚 Inserting books into database...")
        books_to_insert = []
        for _, row in df.iterrows():
            book = Book(
                id=int(row['id']),
                title=str(row['title']),
                price=float(row['price']),
                rating=int(row['rating']),
                availability=int(row['availability']),
                category=str(row['category']),
                image_url=str(row['image_url'])
            )
            books_to_insert.append(book)
        
        db.bulk_save_objects(books_to_insert)
        db.commit()
        print(f"✅ Successfully inserted {len(books_to_insert)} books!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

def print_summary():
    """Print database summary"""
    db = SessionLocal()
    try:
        total_books = db.query(func.count(Book.id)).scalar() or 0
        total_categories = db.query(func.count(func.distinct(Book.category))).scalar() or 0
        avg_price = db.query(func.avg(Book.price)).scalar()

        print("\n" + "=" * 50)
        print("📊 DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total Books: {total_books}")
        print(f"Total Categories: {total_categories}")
        if avg_price:
            print(f"Average Price: £{avg_price:.2f}")
        print(f"Database: {engine.url}")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()
    print_summary()
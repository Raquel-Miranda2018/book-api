from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI(
    title="Books API",
    description="API REST para consulta de livros extraídos do site Books to Scrape",
    version="1.0.0"
)

# Carregar dados
df = pd.read_csv("data/books.csv")


# =========================
# HEALTH CHECK
# =========================
@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "total_books": len(df)
    }


# =========================
# LISTAR LIVROS
# =========================
@app.get("/api/v1/books")
def get_books():
    return df.to_dict(orient="records")


# =========================
# LIVRO POR ID
# =========================
@app.get("/api/v1/books/{book_id}")
def get_book_by_id(book_id: int):
    book = df[df["id"] == book_id]

    if book.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    return book.to_dict(orient="records")[0]


# =========================
# BUSCA POR TÍTULO E/OU CATEGORIA
# =========================
@app.get("/api/v1/books/search")
def search_books(title: str | None = None, category: str | None = None):
    result = df

    if title:
        result = result[result["title"].str.contains(title, case=False, na=False)]

    if category:
        result = result[result["category"].str.lower() == category.lower()]

    return result.to_dict(orient="records")


# =========================
# LISTAR CATEGORIAS
# =========================
@app.get("/api/v1/categories")
def get_categories():
    categories = sorted(df["category"].unique())
    return categories

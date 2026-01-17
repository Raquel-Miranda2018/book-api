import streamlit as st
import requests

API_BASE = "https://book-api-raquel.onrender.com/api/v1"

st.set_page_config(page_title="Book Recommendation App", layout="wide")
st.title("📚 Book Recommendation App")

@st.cache_data(ttl=60)
def fetch_categories():
    r = requests.get(f"{API_BASE}/categories", timeout=20)
    r.raise_for_status()
    data = r.json()

    # Caso 1: ["Fiction", "Poetry"]
    if data and isinstance(data[0], str):
        return data

    # Caso 2: [{"category": "...", "count": ...}]
    if data and isinstance(data[0], dict) and "category" in data[0]:
        return [c["category"] for c in data]

    return []

def fetch_books(title: str | None = None, category: str | None = None):
    try:
        # Se tiver filtro, usa /books/search
        if (title and title.strip()) or (category and category != "Todas"):
            params = {}
            if title and title.strip():
                params["title"] = title.strip()
            if category and category != "Todas":
                params["category"] = category
            r = requests.get(f"{API_BASE}/books/search", params=params, timeout=20)
        else:
            r = requests.get(f"{API_BASE}/books", timeout=20)

        r.raise_for_status()
        data = r.json()

        # Seu /books e /books/search retornam LISTA de dicts
        if isinstance(data, list):
            return data

        # Se vier erro tipo {"detail": "..."}
        if isinstance(data, dict) and "detail" in data:
            st.error(data["detail"])
            return []

        st.error("Resposta inesperada da API.")
        return []

    except requests.exceptions.RequestException as e:
        st.error(f"Erro chamando a API: {e}")
        return []

# Sidebar
st.sidebar.header("Filtros")
title_q = st.sidebar.text_input("Pesquisar por título", value="")
try:
    cats = fetch_categories()
except Exception:
    cats = []
category = st.sidebar.selectbox("Categoria", ["Todas"] + cats)

books = fetch_books(title=title_q, category=category)

st.caption(f"Resultados: {len(books)}")

if not books:
    st.info("Nenhum livro encontrado.")
else:
    # lista em cards
    for book in books:
        if not isinstance(book, dict):
            continue

        with st.container(border=True):
            st.subheader(book.get("title", "Sem título"))
            cols = st.columns(3)
            cols[0].write(f"**Categoria:** {book.get('category', '-')}")
            cols[1].write(f"**Preço:** {book.get('price', '-')}")
            cols[2].write(f"**Rating:** {book.get('rating', '-')}")
            st.write(book.get("description", ""))
            # se tiver id, dá pra buscar detalhes depois
            if "id" in book:
                st.caption(f"ID: {book['id']}")

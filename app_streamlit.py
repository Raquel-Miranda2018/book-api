import streamlit as st
import requests

API_BASE = "https://book-api-raquel.onrender.com/api/v1"

st.set_page_config(page_title="Book Recommendation App", layout="wide")
st.title("📚 Book Recommendation App")

PAGE_SIZE = 20

@st.cache_data(ttl=60)
def fetch_categories():
    r = requests.get(f"{API_BASE}/categories", timeout=20)
    r.raise_for_status()
    data = r.json()

    if data and isinstance(data[0], str):
        return data

    if data and isinstance(data[0], dict) and "category" in data[0]:
        return [c["category"] for c in data]

    return []

def fetch_books(title: str | None = None, category: str | None = None, page: int = 1, page_size: int = 20):
    title_ok = bool(title and title.strip())
    category_ok = bool(category and category != "Todas")

    try:
        if title_ok or category_ok:
            params = {"page": page, "page_size": page_size}
            if title_ok:
                params["title"] = title.strip()
            if category_ok:
                params["category"] = category

            r = requests.get(f"{API_BASE}/books/search", params=params, timeout=20)
        else:
            r = requests.get(f"{API_BASE}/books", params={"page": page, "page_size": page_size}, timeout=20)

        if r.status_code >= 400:
            st.error(f"API retornou {r.status_code}")
            try:
                st.json(r.json())
            except Exception:
                st.code(r.text)
            return [], 1, 0

        data = r.json()

        # Formato paginado: {"books":[...], "total":..., "page":..., "page_size":..., "total_pages":...}
        if isinstance(data, dict) and "books" in data:
            books = data.get("books", [])
            total_pages = int(data.get("total_pages", 1) or 1)
            total = int(data.get("total", len(books)) or len(books))
            return books, total_pages, total

        # Formato lista direta (fallback)
        if isinstance(data, list):
            return data, 1, len(data)

        st.error("Resposta inesperada da API.")
        st.json(data)
        return [], 1, 0

    except requests.exceptions.RequestException as e:
        st.error(f"Erro chamando a API: {e}")
        return [], 1, 0

# --------- Estado da página ---------
if "page" not in st.session_state:
    st.session_state.page = 1

def reset_page():
    st.session_state.page = 1

# --------- Sidebar (com reset de página ao mudar filtros) ---------
st.sidebar.header("Filtros")

title_q = st.sidebar.text_input("Pesquisar por título", value="", on_change=reset_page, key="title_q")

try:
    cats = fetch_categories()
except Exception:
    cats = []

category = st.sidebar.selectbox("Categoria", ["Todas"] + cats, on_change=reset_page, key="category")

# --------- Busca ---------
books, total_pages, total_items = fetch_books(
    title=st.session_state.title_q,
    category=st.session_state.category,
    page=st.session_state.page,
    page_size=PAGE_SIZE
)

st.caption(f"Total: {total_items} | Página {st.session_state.page}/{total_pages} | Mostrando: {len(books)}")

# --------- Controles de paginação ---------
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ Anterior", disabled=st.session_state.page <= 1):
        st.session_state.page -= 1
        st.rerun()

with col3:
    if st.button("Próxima ➡️", disabled=st.session_state.page >= total_pages):
        st.session_state.page += 1
        st.rerun()

# --------- Lista ---------
if not books:
    st.info("Nenhum livro encontrado.")
else:
    for book in books:
        if not isinstance(book, dict):
            continue

        with st.container(border=True):
            st.subheader(book.get("title", "Sem título"))

            cols = st.columns(4)
            cols[0].write(f"**Categoria:** {book.get('category', '-')}")
            cols[1].write(f"**Preço:** {book.get('price', '-')}")
            cols[2].write(f"**Rating:** {book.get('rating', '-')}")
            cols[3].write(f"**Disponível:** {book.get('availability', '-')}")
            
            # Se quiser mostrar imagem:
            if book.get("image_url"):
                st.image(book["image_url"], width=160)

            st.write(book.get("description", ""))

            if "id" in book:
                st.caption(f"ID: {book['id']}")
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from api_test import montar_dados_google, enriquecer_metadados_com_google

# ==========================================
# CONFIGURAÇÃO DA API DO GEMINI
# ==========================================
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# PASSO 1: NLU — Gemini gera a query otimizada
# ==========================================
@st.cache_data(ttl=3600)
def llm_processamento_nlu(prompt_usuario):
    prompt = f"""
    O usuário de uma loja de livros digitou o seguinte pedido: "{prompt_usuario}"
    Transforme esse pedido em uma expressão de busca otimizada para a API do Google Books.
    
    REGRAS CRÍTICAS:
    1. Se pedir GÊNERO LITERÁRIO (ex: ação, romance, terror), use 'subject:' seguido do gênero em inglês.
    2. Exemplo: "livro de romance" -> subject:"romance"
    3. Retorne APENAS a string, sem aspas, sem explicações.
    """
    resposta = client.models.generate_content(
        model='gemini-3.1-flash-lite-preview', 
        contents=prompt
    )
    return resposta.text.strip()

# ==========================================
# PASSO 2+3: Busca, seleciona e enriquece 
# ==========================================
@st.cache_data(ttl=3600)
def buscar_e_enriquecer(query_otimizada: str) -> dict:
    API_KEY = st.secrets["BOOKS_API_KEY"]
    url = f"https://www.googleapis.com/books/v1/volumes?q={query_otimizada}&maxResults=30&key={API_KEY}"
    isbns_selecionados = {"relevante": None, "avaliado": None, "recente": None}

    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()

        if "items" not in dados:
            return {k: None for k in isbns_selecionados}

        livros_validos = []
        for item in dados["items"]:
            info = item.get("volumeInfo", {})

            isbn = None
            for ident in info.get("industryIdentifiers", []):
                if ident.get("type") == "ISBN_13":
                    isbn = ident.get("identifier")

            if not isbn:
                continue

            data_bruta = str(info.get("publishedDate", "0000")).strip().upper()
            if not data_bruta or data_bruta in ["NULL", "NONE", "N/A", ""]:
                data_limpa = "0000"
            else:
                data_limpa = str(info.get("publishedDate")).strip()

            livros_validos.append({
                "isbn": isbn,
                "nota": info.get("averageRating", 0),
                "data": data_limpa,
                # Envia o 'item' inteiro para puxar ofertas comerciais
                "dados_google": montar_dados_google(item)
            })

        if not livros_validos:
            return {k: None for k in isbns_selecionados}

        isbns_usados = set()

        # 1. PRIORIDADE MÁXIMA: Mais Recente
        livros_com_data = [l for l in livros_validos if l["data"] != "0000"]
        if livros_com_data:
            isbns_selecionados["recente"] = sorted(livros_com_data, key=lambda x: x["data"], reverse=True)[0]["isbn"]
        else:
            isbns_selecionados["recente"] = livros_validos[0]["isbn"]
        isbns_usados.add(isbns_selecionados["recente"])

        # 2. PRIORIDADE MÉDIA: Mais Bem Avaliado
        livros_com_nota = [l for l in livros_validos if l["nota"] > 0 and l["isbn"] not in isbns_usados]
        if livros_com_nota:
            isbns_selecionados["avaliado"] = sorted(livros_com_nota, key=lambda x: x["nota"], reverse=True)[0]["isbn"]
        else:
            restantes = [l for l in livros_validos if l["isbn"] not in isbns_usados]
            isbns_selecionados["avaliado"] = restantes[0]["isbn"] if restantes else isbns_selecionados["recente"]
        isbns_usados.add(isbns_selecionados["avaliado"])

        # 3. PRIORIDADE FINAL: Mais Relevante
        restantes_relevantes = [l for l in livros_validos if l["isbn"] not in isbns_usados]
        if restantes_relevantes:
            isbns_selecionados["relevante"] = restantes_relevantes[0]["isbn"]
        else:
            isbns_selecionados["relevante"] = isbns_selecionados["recente"]
        isbns_usados.add(isbns_selecionados["relevante"])

    except Exception as e:
        st.error(f"Erro na busca do catálogo: {e}")
        return {k: None for k in isbns_selecionados}

    dados_por_isbn: dict[str, dict] = {l["isbn"]: l["dados_google"] for l in livros_validos}

    # Salva a data correta do Google Books para restauração
    datas_por_isbn: dict[str, str] = {l["isbn"]: l["data"] for l in livros_validos}

    isbn_para_categorias: dict[str, list[str]] = {}
    for categoria, isbn in isbns_selecionados.items():
        if isbn:
            isbn_para_categorias.setdefault(isbn, []).append(categoria)
    isbns_unicos = list(isbn_para_categorias.keys())

    dados_enriquecidos: dict[str, dict | None] = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futuros = {executor.submit(enriquecer_metadados_com_google, isbn, dados_por_isbn[isbn]): isbn for isbn in isbns_unicos}
        for futuro in as_completed(futuros):
            isbn = futuros[futuro]
            try:
                resultado = futuro.result()
                if resultado and "erro" not in resultado:
                    # Injeta a data do Google Books de volta (evita 'null' da Open Library)
                    data_correta = datas_por_isbn.get(isbn, "0000")
                    if data_correta != "0000":
                        resultado["datePublished"] = data_correta
                    dados_enriquecidos[isbn] = resultado
                else:
                    dados_enriquecidos[isbn] = None
            except Exception as e:
                dados_enriquecidos[isbn] = None
                st.warning(f"Erro ao enriquecer ISBN {isbn}: {e}")

    return {categoria: dados_enriquecidos.get(isbn) for categoria, isbn in isbns_selecionados.items()}

# ==========================================
# PASSO 4: Gemini escreve a recomendação personalizada
# ==========================================
@st.cache_data(ttl=3600)
def llm_enriquecimento_semantico(prompt_usuario: str, dados_json_ld: dict, categoria_texto: str) -> str:
    titulo = dados_json_ld.get("name", "o livro")
    sinopse = dados_json_ld.get("description", "Sem sinopse.")
    dados_avaliacao = dados_json_ld.get("aggregateRating") or {}

    prompt = f"""
    O usuário procurou por: "{prompt_usuario}".
    Você está recomendando o livro "{titulo}" porque ele foi classificado como o "{categoria_texto}" da busca.

    Sinopse: {sinopse}
    Avaliação Média: {dados_avaliacao.get('ratingValue', 'N/A')}
    Ano de Publicação: {dados_json_ld.get('datePublished', 'N/A')}

    Escreva de forma empática (máximo 4 linhas) justificando esta recomendação.
    Mencione POR QUE ele está nessa categoria (ex: se for o mais bem avaliado, elogie a nota;
    se for lançamento, mencione que é novidade).
    """
    resposta = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    return resposta.text

# ==========================================
# INTERFACE VISUAL — Card de livro
# ==========================================
def exibir_cartao_livro(json_ld: dict | None, prompt_usuario: str, categoria_texto: str):
    if not json_ld:
        st.warning(f"Não encontramos dados suficientes para a categoria: {categoria_texto}")
        return

    motivo = llm_enriquecimento_semantico(prompt_usuario, json_ld, categoria_texto)
    st.success(motivo)

    col1, col2 = st.columns([1, 2])

    with col1:
        if json_ld.get("image"):
            st.image(json_ld["image"], width="stretch")
        else:
            st.info("Capa indisponível")

    with col2:
        st.subheader(json_ld.get("name", "Título desconhecido"))

        # Extração a partir do formato semântico Person
        autores_schema = json_ld.get("author", [])
        nomes_autores = [a.get("name") for a in autores_schema if isinstance(a, dict) and a.get("@type") == "Person"]
        st.write(f"**Autor(es):** {', '.join(nomes_autores) if nomes_autores else 'Autor desconhecido'}")

        # Extração a partir do formato semântico Organization
        editoras_schema = json_ld.get("publisher", [])
        nomes_editoras = [e.get("name") for e in editoras_schema if isinstance(e, dict) and e.get("@type") == "Organization"]
        st.write(f"**Editora:** {', '.join(nomes_editoras) if nomes_editoras else 'N/A'}")

        st.write(f"**Publicação:** {json_ld.get('datePublished', 'N/A')}")

        if json_ld.get("numberOfPages"):
            st.write(f"**Páginas:** {json_ld['numberOfPages']}")

        dados_avaliacao = json_ld.get("aggregateRating") or {}
        st.write(f"⭐ **Nota:** {dados_avaliacao.get('ratingValue', 'N/A')}")

        # Exibe as informações de preço (Offer) se disponíveis
        ofertas = json_ld.get("offers")
        if ofertas:
            st.write(f"🏷️ **Preço Oficial:** {ofertas.get('price')} {ofertas.get('priceCurrency')}")

        generos = json_ld.get("genre") or []
        if generos:
            st.write(f"**Gênero:** {', '.join(generos)}")

    if json_ld.get("description"):
        with st.expander("Ler Sinopse Completa", expanded=False):
            st.write(json_ld["description"])

    author_links = json_ld.get("authorLinks") or []
    links_validos = [a for a in author_links if a.get("url")]
    if links_validos:
        with st.expander("Links de Autoridade dos Autores"):
            for autor in links_validos:
                st.markdown(f"- [{autor.get('nome')}]({autor.get('url')})")

    with st.expander("Visualizar Schema.org (JSON-LD)"):
        st.json(json_ld)

# ==========================================
# FLUXO PRINCIPAL DO STREAMLIT
# ==========================================
st.set_page_config(page_title="BookAdvisor AI", layout="centered")
st.title("📚 BookAdvisor AI")
st.markdown("**Sistema Inteligente de Recomendação e Enriquecimento Semântico**")
st.divider()

prompt_usuario = st.text_input(
    "Converse com o Agente:",
    placeholder="Ex: Quero um livro de ação"
)
buscar_btn = st.button("🔍 Buscar")

if buscar_btn and prompt_usuario:
    st.write("---")

    with st.status("Processando intenção e varrendo a base global...", expanded=True) as status:
        query_otimizada = llm_processamento_nlu(prompt_usuario)
        st.write(f"✔️ Termo de busca NLU: `{query_otimizada}`")

        st.write("🗄️ Buscando catálogo e enriquecendo com Open Library em paralelo...")
        dicionario_livros = buscar_e_enriquecer(query_otimizada)

        status.update(
            label="✅ Análise e enriquecimento concluídos!",
            state="complete",
            expanded=False
        )

    aba1, aba2, aba3 = st.tabs(["🎯 Mais Relevante", "⭐ Melhor Avaliado", "🆕 Mais Recente"])

    with aba1:
        st.subheader("O Melhor Match")
        exibir_cartao_livro(dicionario_livros["relevante"], prompt_usuario, "Mais Relevante (Melhor Match)")

    with aba2:
        # Tratamento UI para livros recentes ou subgêneros sem avaliação
        dados_avaliado = dicionario_livros.get("avaliado") or {}
        nota = dados_avaliado.get("aggregateRating")

        if nota:
            st.subheader("O Favorito dos Leitores")
        else:
            st.subheader("Destaque do Gênero (Ainda sem avaliações)")
            
        exibir_cartao_livro(dicionario_livros["avaliado"], prompt_usuario, "Mais Bem Avaliado")

    with aba3:
        st.subheader("Novidade do Mercado")
        exibir_cartao_livro(dicionario_livros["recente"], prompt_usuario, "Mais Recente (Lançamento)")

elif buscar_btn and not prompt_usuario:
    st.warning("Por favor, digite o que você está procurando antes de buscar.")

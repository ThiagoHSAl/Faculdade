import requests
import json
import time

def get_com_retry(url, tentativas=3):
    """
    Tenta fazer a requisição múltiplas vezes com atraso exponencial (Backoff).
    Isso evita bloqueios temporários (Rate Limit) das APIs.
    """
    for i in range(tentativas):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if i < tentativas - 1:
                time.sleep(2 ** i)
    return None

def montar_dados_google(item: dict) -> dict:
    """
    Monta o dict padronizado do Google Books a partir de um item completo
    (incluindo informações de venda e oferta).
    """
    volume_info = item.get("volumeInfo", {})
    sale_info = item.get("saleInfo", {})
    
    return {
        "titulo": volume_info.get("title", "Título não encontrado"),
        "autores": volume_info.get("authors", []),
        "sinopse": volume_info.get("description", "Sinopse indisponível"),
        "genero": volume_info.get("categories", []),
        "avaliacao_media": volume_info.get("averageRating", None),
        "url_capa": volume_info.get("imageLinks", {}).get("thumbnail", ""),
        "preco": sale_info.get("retailPrice", {}).get("amount"),
        "moeda": sale_info.get("retailPrice", {}).get("currencyCode"),
        "venda": sale_info.get("saleability")
    }

def buscar_open_library(isbn: str) -> dict | None:
    """Busca metadados e links de autoridade na Open Library API."""
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    dados = get_com_retry(url)

    if dados:
        chave = f"ISBN:{isbn}"
        if chave in dados:
            livro_info = dados[chave]
            autores_dados = livro_info.get("authors", [])
            links_autores = [{"nome": a.get("name"), "url": a.get("url")} for a in autores_dados]

            return {
                "numero_paginas": livro_info.get("number_of_pages", None),
                "data_publicacao": livro_info.get("publish_date", "Data desconhecida"),
                "editora": [e.get("name") for e in livro_info.get("publishers", [])],
                "links_autoridade_autores": links_autores
            }
    return None

def enriquecer_metadados_com_google(isbn: str, dados_google: dict) -> dict:
    """
    Mescla os dados e aplica as classes semânticas estritas do Schema.org.
    """
    dados_open_lib = buscar_open_library(isbn) or {}
    
    # Mapeamento de Person (Autores)
    autores_lista = dados_google.get("autores") or [a.get("nome") for a in dados_open_lib.get("links_autoridade_autores", [])]
    autores_schema = [{"@type": "Person", "name": autor} for autor in autores_lista]

    # Mapeamento de Organization (Editora)
    editoras_lista = dados_open_lib.get("editora") or ["Não informada"]
    editoras_schema = [{"@type": "Organization", "name": ed} for ed in editoras_lista]

    # Mapeamento de Offer (Oferta/Preço)
    oferta_schema = None
    if dados_google.get("preco"):
        oferta_schema = {
            "@type": "Offer",
            "price": dados_google.get("preco"),
            "priceCurrency": dados_google.get("moeda"),
            "availability": "https://schema.org/InStock" if dados_google.get("venda") == "FOR_SALE" else "https://schema.org/OutOfStock"
        }

    return {
        "@context": "https://schema.org/",
        "@type": "Book",
        "isbn": isbn,
        "name": dados_google.get("titulo"),
        "author": autores_schema,
        "description": dados_google.get("sinopse"),
        "genre": dados_google.get("genero"),
        "publisher": editoras_schema,
        "datePublished": dados_open_lib.get("data_publicacao"),
        "numberOfPages": dados_open_lib.get("numero_paginas"),
        "image": dados_google.get("url_capa"),
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": dados_google.get("avaliacao_media")} if dados_google.get("avaliacao_media") else None,
        "offers": oferta_schema,
        "award": "Prêmios não disponíveis na API base",
        "authorLinks": dados_open_lib.get("links_autoridade_autores")
    }

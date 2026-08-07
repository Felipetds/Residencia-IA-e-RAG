import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json
from pathlib import Path

PASTA_JSON = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula2\arquivos_json")

artigos = ['bioetica_e_ia', 'escrita_academica_ia', 'twitter_algoritmo']

def buscar_arquivos():
    pasta = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula2\arquivos_md")
    caminhos = [str(pdf) for pdf in pasta.glob("*.md")]
    print(caminhos)
    return caminhos

def consulta(nome_artigo_md, nome_artigo_json, caminho):

    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Usa o modelo definido no .env ou um valor padrão
    modelo = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    class Artigo(BaseModel):
        titulo: str

    with open(caminho, "r", encoding="utf-8") as f:
        markdown = f.read()

    response = client.chat.completions.create(
        model=modelo,
        messages=[
            {
            "role": "user",
            "content": f"""
            Este é o conteúdo de um artigo em Markdown.
            {markdown}"""
            }
        ],
    response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "article_metadata",
        "schema": {
            "type": "object",
            "properties": {
                "titulo": {
                    "type": "string",
                    "description": "Título do trabalho"
                },
                "autores": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Lista de autores do trabalho"
                },
                "ano_publicacao": {
                    "type": "integer",
                    "description": "Ano de publicação do trabalho"
                },
                "palavras_chave": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Lista de palavras-chave do artigo"
                },
                "resumo": {
                    "type": "string",
                    "description": "Resumo do artigo"
                },
                "referencias": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Lista de referências bibliográficas"
                }
            },
            "required": [
                "titulo",
                "autores",
                "ano_publicacao",
                "palavras_chave",
                "resumo",
                "referencias"
            ],
            "additionalProperties": False
        }
    }
}
    )

    conteudo = response.choices[0].message.content
    dados = json.loads(conteudo)

    caminho_json = PASTA_JSON / nome_artigo_json

    with open(caminho_json, "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print("Arquivo JSON criado com sucesso!")

caminhos = buscar_arquivos()

for i in range(len(artigos)):

    nome = artigos[i]
    nome_artigo_md = str(nome + '.md')
    nome_artigo_json = str(nome + '.json')

    caminho = caminhos[i]

    consulta(nome_artigo_md, nome_artigo_json, caminho)


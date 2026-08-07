import os
from docling.document_converter import DocumentConverter
from pathlib import Path

PASTA_MD = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula2\arquivos_md")

def buscar_arquivos():
    pasta = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula2\arquivos_pdf")
    caminhos = [str(pdf) for pdf in pasta.glob("*.pdf")]
    print(caminhos)
    return caminhos

arquivos = ['bioetica_e_ia', 'escrita_academica_ia', 'twitter_algoritmo']

def conversor(nome_artigo_pdf, nome_artigo_md, caminho):

    os.environ["TORCH_COMPILE_DISABLE"] = "1"

    source = f"{caminho}"

    converter = DocumentConverter()
    doc = converter.convert(source).document

    markdown = doc.export_to_markdown()

    caminho_md = PASTA_MD / nome_artigo_md

    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write(markdown)

    print("Arquivo salvo em:", os.path.abspath(nome_artigo_pdf))

caminhos = buscar_arquivos()

for i in range(len(arquivos)):

    nome = arquivos[i]
    nome_artigo_pdf = str(nome + '.pdf')
    nome_artigo_md = str(nome + '.md')

    caminho = caminhos[i]

    conversor(nome_artigo_pdf, nome_artigo_md, caminho)
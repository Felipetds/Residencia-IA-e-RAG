import os
from docling.document_converter import DocumentConverter
from pathlib import Path

PASTA_MD = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula4\arquivos_md")

def buscar_arquivos():
    pasta = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Arquivos_10-08-2026")
    caminhos = [str(pdf) for pdf in pasta.glob("*.pdf")]
    print(caminhos)
    return caminhos

def buscar_nomes_arquivos():
    pasta = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Arquivos_10-08-2026")
    nomes = [pdf.name for pdf in pasta.glob("*.pdf")]
    print(nomes)
    return nomes

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
nomes_arquivos = buscar_nomes_arquivos()

for i in range(len(caminhos)):

    caminho = caminhos[i]
    nome = nomes_arquivos[i]

    nome_artigo_pdf = str(nome + ".pdf")
    nome_artigo_md = str(nome + ".md")

    conversor(nome_artigo_pdf, nome_artigo_md, caminho)
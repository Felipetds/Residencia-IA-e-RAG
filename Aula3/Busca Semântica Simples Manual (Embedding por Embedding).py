from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
import math


caminho = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula2\arquivos_md\bioetica_e_ia.md")

def consultar_linha(caminho):
  linhas = caminho.read_text(encoding="utf-8").splitlines()
  # Filtra apenas linhas que possuem algum caractere visível
  linhas_sem_vazias = [linha for linha in linhas if linha.strip()]
  return linhas_sem_vazias

def gerar_embeddings(termos):

  load_dotenv()
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

  embeddings = []

  response = client.embeddings.create(model="text-embedding-3-small", input=[str(t) for t in termos])

  embeddings = [item.embedding[:10] for item in response.data]

  return np.array(embeddings)

def gerar_embedding_ancora(ancora):

  load_dotenv()
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

  embedding_ancora = []

  response = client.embeddings.create(model="text-embedding-3-small",input="O que é “Autonomia e opacidade algorítmica”?")

  embedding_ancora = np.array(response.data[0].embedding[:10])

  return embedding_ancora

def gerar_resultados(termos ,embedding_ancora_170, embeddings):
  resultados = []
  for texto, ancora, vec in zip(termos, embedding_ancora_170, embeddings):

    resultados.append({
        "Texto": texto,
        "Dist. Euclidiana": round(math.dist(ancora, vec), 4),
        "Similaridade Cosseno": round(float(cosine_similarity(ancora.reshape(1, -1), vec.reshape(1, -1))[0][0]), 4),
        "Distância Cosseno": round(float(cosine_distances(ancora.reshape(1, -1), vec.reshape(1, -1))[0][0]), 4)
    })

  df_resultados = pd.DataFrame(resultados)
  return df_resultados



linhas_sem_vazias = consultar_linha(caminho)
termos = np.array(linhas_sem_vazias)
embeddings = gerar_embeddings(termos)
embedding_ancora = gerar_embedding_ancora("O que é “Autonomia e opacidade algorítmica”?")
embedding_ancora_170 = np.tile(embedding_ancora, (170, 1))

tabela = gerar_resultados(termos ,embedding_ancora_170, embeddings)

tabela_ordenada = tabela.sort_values(by="Similaridade Cosseno", ascending=False)
print(tabela_ordenada.head())

tabela_ordenada = tabela.sort_values(by="Similaridade Cosseno", ascending=False)
tabela_ordenada_top_3 = tabela_ordenada.head(3)
tabela_md = tabela_ordenada.to_markdown("resultados_busca_semantica_bioetica_e_ia-ordenado.md", index=False)
tabela_md = tabela_ordenada_top_3.to_markdown("resultados_busca_semantica_bioetica_e_ia-ordenado_top_3.md", index=False)

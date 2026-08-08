from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
import math

def buscar_arquivos():
    
    pasta = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula2\arquivos_md")
    caminhos = list(pasta.glob("*.md"))
    print(f"Arquivos encontrados: {caminhos}")
    return caminhos

def consultar_linha(caminho_path):
    
    linhas = caminho_path.read_text(encoding="utf-8").splitlines()
    linhas_sem_vazias = [linha for linha in linhas if linha.strip()]
    return linhas_sem_vazias

def gerar_embeddings(termos):
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(model="text-embedding-3-small", input=[str(t) for t in termos])
    embeddings = [item.embedding[:10] for item in response.data]
    return np.array(embeddings)

def gerar_embedding_ancora(ancora_texto):
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(model="text-embedding-3-small", input=ancora_texto)
    embedding_ancora = np.array(response.data[0].embedding[:10])
    return embedding_ancora

def gerar_resultados(termos, embedding_ancora_repetido, embeddings):
    
    resultados = []
    for texto, ancora, vec in zip(termos, embedding_ancora_repetido, embeddings):
        resultados.append({
            'Texto': texto,
            'Dist. Euclidiana': round(math.dist(ancora, vec), 4),
            'Similaridade Cosseno': round(float(cosine_similarity(ancora.reshape(1, -1), vec.reshape(1, -1))[0][0]), 4),
            'Distância Cosseno': round(float(cosine_distances(ancora.reshape(1, -1), vec.reshape(1, -1))[0][0]), 4)
        })
    return pd.DataFrame(resultados)

def busca_semantica(pasta_destino, caminhos_arquivos, texto_ancora, embedding_ancora):
      
  # Loop passando o arquivo individualmente
  for arquivo in caminhos_arquivos:
      linhas_sem_vazias = consultar_linha(arquivo)
      
      # Não permite receber um arquivo Markdown em branco
      if not linhas_sem_vazias:
          continue
          
      termos = np.array(linhas_sem_vazias)
      embeddings = gerar_embeddings(termos)
      
      # Recebe o tamanho real do arquivo atual
      embedding_ancora_dinamico = np.tile(embedding_ancora, (len(termos), 1))
      
      tabela = gerar_resultados(termos, embedding_ancora_dinamico, embeddings)
      tabela_ordenada = tabela.sort_values(by='Similaridade Cosseno', ascending=False)
      
      print(f"\n--- Top resultados para o arquivo: {arquivo.name} ---")
      print(tabela_ordenada.head())
      
      tabela_ordenada_top_3 = tabela_ordenada.head(3)
      # Salva os arquivos Markdown usando o nome original do arquivo analisado para não sobrescrever dados
      nome_base = arquivo.stem

      caminho_completo_ordenado = pasta_destino / f"resultados_{nome_base}_ordenado.md"
      caminho_completo_top_3 = pasta_destino / f"resultados_{nome_base}_top_3.md"
      tabela_ordenada.to_markdown(caminho_completo_ordenado, index=False)
      tabela_ordenada_top_3.to_markdown(caminho_completo_top_3, index=False)

# Fluxo principal de execução
pasta_destino = Path(r"C:\Users\Felipe\Desktop\Ecoa - PUC\Residencia-LLM-e-RAG\Aula3\Resultados")
caminhos_arquivos = buscar_arquivos()
texto_ancora = "O que é Autonomia e opacidade algorítmica?"
embedding_ancora = gerar_embedding_ancora(texto_ancora)

busca_semantica(pasta_destino, caminhos_arquivos, texto_ancora, embedding_ancora)
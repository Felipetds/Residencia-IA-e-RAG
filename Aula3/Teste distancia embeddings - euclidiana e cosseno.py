import os
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
import numpy as np
import math

termos = ['gato','felino','cachorro','carro','caminhão','moto','banana','maçã','goiaba']

def gerar_(termos):

    load_dotenv()

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
        )

    embeddings = []

    for termo in termos:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=termo
        )

        embedding = response.data[0].embedding

        # guarda apenas os 10 primeiros valores
        embeddings.append(embedding[:10])
    return embeddings

def euclidiana(embed_1, embed_2):
    distancia_eucli = math.dist(embed_1, embed_2)
    return distancia_eucli

def cosseno_similaridade(embed_1, embed_2):
    embed_1 = np.array(embed_1)
    embed_2 = np.array(embed_2)
    similaridade_coss = cosine_similarity(embed_1.reshape(1, -1), embed_2.reshape(1, -1))
    return similaridade_coss

def cosseno_distancia(embed_1, embed_2):
    embed_1 = np.array(embed_1)
    embed_2 = np.array(embed_2)
    distancia_coss = cosine_distances(embed_1.reshape(1, -1), embed_2.reshape(1, -1))
    return distancia_coss


embeddings = gerar_(termos)
print(f"Distancia euclidiana entre gato e felino {euclidiana(embeddings[0], embeddings[1])}")
print(f"Similaridade cosseno entre gato e felino {cosseno_similaridade(embeddings[0], embeddings[1])}")
print(f"Distancia cosseno entre gato e felino {cosseno_distancia(embeddings[0], embeddings[1])}")

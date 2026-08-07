import os
from dotenv import load_dotenv
from openai import OpenAI

termos = ['gato','felino','cachorro','carro','caminhão','moto','banana','maçã','goiaba']

embeddings = []

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def coleta(palavra):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=palavra
    )

    embedding = response.data[0].embedding

    print(f"Palavra: {palavra}")
    print(f"Dimensão: {len(embedding)}")
    print(f"Primeiros valores: {embedding[:10]}")
    print()

    return embedding


for termo in termos:
    embedding = coleta(termo)
    embeddings.append(embedding)



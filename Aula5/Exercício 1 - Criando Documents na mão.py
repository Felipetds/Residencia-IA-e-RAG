from langchain_core.documents import Document

documentos = [
    Document(
        page_content="Embeddings são representações vetoriais densas de texto.",
        metadata={
            "fonte": "Embeddings.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "embeddings",
            "autor": "Nome do autor"
        }
    ),
    Document(
        page_content="Chunking divide documentos em partes menores.",
        metadata={
            "fonte": "Chunk.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "Chunk",
            "autor": "Nome do autor"
        }
    ),
    Document(
        page_content="O RAG recupera informações relevantes antes de gerar respostas.",
        metadata={
            "fonte": "RAG.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "RAG",
            "autor": "Nome do autor"
        }
    ),
    Document(
        page_content="O RAG combina recuperação de informações e geração de texto.",
        metadata={
            "fonte": "RAG.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "RAG",
            "autor": "Nome do autor"
        }
    ),
    Document(
        page_content="Chunks muito grandes podem dificultar a recuperação.",
        metadata={
            "fonte": "Chunk.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "Chunk",
            "autor": "Nome do autor"
        }
    ),
    Document(
        page_content="Embeddings permitem comparar a similaridade entre textos.",
        metadata={
            "fonte": "Embeddings.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "embeddings",
            "autor": "Nome do autor"
        }
    )               
]  

for i in range(len(documentos)):
  print(documentos[i].page_content)
  print(documentos[i].metadata)
  print("\n")

'''
Embeddings são representações vetoriais densas de texto.
{'fonte': 'Embeddings.md', 'pagina': 1, 'tipo': 'teoria', 'tema': 'embeddings', 'autor': 'Nome do autor'}


Chunking divide documentos em partes menores.
{'fonte': 'Chunk.md', 'pagina': 1, 'tipo': 'teoria', 'tema': 'Chunk', 'autor': 'Nome do autor'}


O RAG recupera informações relevantes antes de gerar respostas.
{'fonte': 'RAG.md', 'pagina': 1, 'tipo': 'teoria', 'tema': 'RAG', 'autor': 'Nome do autor'}


O RAG combina recuperação de informações e geração de texto.
{'fonte': 'RAG.md', 'pagina': 1, 'tipo': 'teoria', 'tema': 'RAG', 'autor': 'Nome do autor'}


Chunks muito grandes podem dificultar a recuperação.
{'fonte': 'Chunk.md', 'pagina': 1, 'tipo': 'teoria', 'tema': 'Chunk', 'autor': 'Nome do autor'}


Embeddings permitem comparar a similaridade entre textos.
{'fonte': 'Embeddings.md', 'pagina': 1, 'tipo': 'teoria', 'tema': 'embeddings', 'autor': 'Nome do autor'}
'''

len(documentos)
'''
resposta: 6
'''

'''
- Que tipos de dado são aceitos dentro de `metadata`? Teste colocar uma lista ou um dicionário aninhado e relate o que acontece.
O campo metadata é do tipo "dict" ou dicionário . O "dict" é uma estrutura de dados mutável que armazena informações em pares de chave e valor e pode 
armazenar diferentes tipos de dados, como strings, números inteiros, números decimais, booleanos, listas e até dicionários aninhados.

- O que acontece se você criar um `Document` sem passar `metadata`?
O Document é criado normalmente e o LangChain utiliza um dicionário vazio ({}) como valor padrão.
'''


### schema de metadados

| CAMPO | DESCRIÇÃO |
| --- | --- |
| fonte | nome do arquivo .md de origem |
| documento_id | identificador do documento |
| chunk_index | posição do chunk dentro do documento |
| estrategia | qual das 10 estratégias da Aula 04 gerou este chunk |
| chunk_size | configuração usada |
| chunk_overlap | configuração usada |
| n_caracteres | tamanho real do chunk |
| tipo_conteudo | classificação do conteúdo, como texto, tabela, código ou lista |
| n_tokens | quantidade de tokens do chunk |
| percentual_documento | percentual do documento representado pelo chunk |


### Justificativa

tipo_conteudo: Permite identificar qual tipo de conteúdo está presente no chunk, como texto, tabela, código ou lista. Esse campo é importante para avaliar se as estratégias de chunking preservam adequadamente diferentes estruturas do documento e também pode ser utilizado posteriormente para filtrar ou priorizar determinados tipos de conteúdo em um sistema RAG.

n_tokens:	Registra a quantidade de tokens presentes no chunk. Essa informação é relevante para aplicações com modelos de linguagem, pois os limites de contexto e os custos de processamento são baseados em tokens. Também permite comparar o tamanho real dos chunks de forma mais adequada ao funcionamento dos LLMs.

percentual_documento:	Indica quanto do conteúdo total do documento é representado pelo chunk. Esse campo permite analisar a proporção que cada chunk ocupa no documento e comparar documentos de tamanhos diferentes. Também pode ajudar a identificar chunks muito pequenos ou muito grandes em relação ao documento de origem.

### Exemplo
'''
{
  "text": "valores  fundamentais  como  beneficência,  não maleficência, confidencialidade e respeito à auto -nomia do doente - pilares da bioética ainda hoje 4 . Tais valores foram reforçados no século XX por documentos como o Código de Nüremberg e  a Declaração de Helsinki , que consolidaram as bases para a ética em pesquisa e prática médica 3 .",
  "metadata": {
    "fonte": "bioetica_e_ia.md",
    "documento_id": "doc_001",
    "chunk_index": 5323,
    "estrategia": "fixed with overlap",
    "chunk_size": 500,
    "chunk_overlap": 50,
    "n_caracteres": 338,
    "tipo_conteudo": "texto",
    "n_tokens": 85,
    "percentual_documento": 0.6599886747505516
  }
}
'''
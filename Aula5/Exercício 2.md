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

## Respostas
### Qual campo você incluiria se precisasse citar a fonte na resposta final do RAG, informando ao usuário exatamente de onde veio a informação?
Eu incluiria o campo pagina, que armazenaria o número da página do documento original em que o conteúdo do chunk está localizado. Esse campo, em conjunto com fonte e documento_id, permitiria ao sistema RAG informar ao usuário com maior precisão de onde a informação utilizada na resposta foi retirada.

### Por que chunk_index é útil? Pense no caso em que o trecho recuperado está cortado no meio de uma explicação.
Ele indica a posição do chunk dentro do documento e permite identificar os chunks anteriores e posteriores. Isso é ajuda a recuperar um trecho que está cortado no meio de uma explicação, e o sistema utiliza o índice para recuperar os chunks vizinhos e complementar o contexto antes de gerar a resposta.
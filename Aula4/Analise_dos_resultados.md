### Qual estratégia gerou mais chunks?
A estratégia que gerou mais chunks foi a fixed com chunk_size = 200 e chunk_overlap = 0.
Somando os resultados dos 12 documentos, foram 9.745 chunks. Por exemplo, gpt3_language_models gerou 2.030 chunks nessa configuração.

### Qual gerou menos chunks?
A estratégia markdown foi a que gerou menos chunks no conjunto dos experimentos. Somando os 12 documentos, foram 664 chunks. Por exemplo, bioetica_e_ia gerou apenas 22 chunks.

### Como o tamanho dos chunks variou?
Nas estratégias fixed, o aumento de chunk_size produziu chunks progressivamente maiores:

A media de tamanho dos menores chunks foi: 
chunk_size = 200 e overlap = 0: 1.58 caracteres.
chunk_size = 500 e overlap = 0: 6.42 caracteres.
chunk_size = 500 e overlap = 50: 12.50 caracteres.
chunk_size = 500 e overlap = 200: 13.60 caracteres.
chunk_size = 1000 e overlap = 0: 27.92 caracteres.
chunk_size = 2000 e overlap = 0: 347.25 caracteres.

A media de tamanho dos maiores chunks foi: 
chunk_size = 200 e overlap = 0: 199.58 caracteres.
chunk_size = 500 e overlap = 0: 499.17 caracteres.
chunk_size = 500 e overlap = 50: 499.17 caracteres.
chunk_size = 500 e overlap = 200: 499.25 caracteres.
chunk_size = 1000 e overlap = 0: 998.17 caracteres.
chunk_size = 2000 e overlap = 0: 1989.33 caracteres.

### Qual estratégia preservou melhor a estrutura dos documentos?
A estratégia que aparentou preservar melhor a estrutura dos documentos foi a "MarkdownHeaderTextSplitter". Isso ocorre porque ela utiliza a estrutura do Markdown como referência para a divisão. Os resultados mostram uma quantidade muito menor de chunks, sem produzir os chunks extremamente grandes observados em outros casos.

### Como tabelas foram tratadas?


### Como imagens foram tratadas?


### Quais informações foram perdidas durante a conversão PDF → Markdown?


### O chunking por caracteres fragmentou conceitos ou estruturas importantes?
Sim, há indícios de que ocorreram fragmentações de conceitos e estruturas. Isso fica evidente pela existência de chunks muito pequenos. Por exemplo, em diversos documentos o menor chunk possui apenas 1 caractere. Em "Attention Is All You Need", o menor chunk na configuração de 200 caracteres foi de apenas 1 caractere.

Esse comportamento pode separar:

- frases;
- explicações;
- conceitos;
- listas;
- títulos e seus conteúdos.

O overlap ajuda a reduzir a perda de contexto entre chunks, mas não elimina completamente o problema.

### O chunking por parágrafo produziu chunks muito grandes?
Sim. Esse foi um dos principais problemas observados. A estratégia paragrafo_recursivo produziu chunks com tamanho médio em torno de x caracteres.

Exemplos:

- bioetica_e_ia: média de x caracteres;
- bert_pretraining: média de x caracteres;
- escrita_academica_ia: média de x caracteres.

### O chunking por sentença conseguiu preservar melhor o contexto?


### O Recursive Splitter apresentou vantagens?


### O Markdown Splitter conseguiu preservar a estrutura semântica?


### Qual estratégia parece mais adequada para um sistema de RAG?


### Quais estratégias devem ser descartadas?


### Quais estratégias você acha que devem ser utilizadas nos próximos experimentos?
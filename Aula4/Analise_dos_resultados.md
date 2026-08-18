### Qual estratégia gerou mais chunks?
A estratégia que gerou mais chunks foi a fixed com chunk_size = 200 e chunk_overlap = 0.
Somando os resultados dos 12 documentos, foram 9.745 chunks. Por exemplo, gpt3_language_models gerou 2.030 chunks nessa configuração.

### Qual gerou menos chunks?
A estratégia markdown foi a que gerou menos chunks no conjunto dos experimentos. Somando os 12 documentos, foram 664 chunks. Por exemplo, bioetica_e_ia gerou apenas 22 chunks.

### Como o tamanho dos chunks variou?
Nas estratégias fixed, o aumento de chunk_size produziu chunks progressivamente maiores:

A media de tamanho dos menores chunks foi: 
- chunk_size = 200 e overlap = 0: 1.58 caracteres.
- chunk_size = 500 e overlap = 0: 6.42 caracteres.
- chunk_size = 500 e overlap = 50: 12.50 caracteres.
- chunk_size = 500 e overlap = 200: 13.60 caracteres.
- chunk_size = 1000 e overlap = 0: 27.92 caracteres.
- chunk_size = 2000 e overlap = 0: 347.25 caracteres.

A media de tamanho dos maiores chunks foi: 
- chunk_size = 200 e overlap = 0: 199.58 caracteres.
- chunk_size = 500 e overlap = 0: 499.17 caracteres.
- chunk_size = 500 e overlap = 50: 499.17 caracteres.
- chunk_size = 500 e overlap = 200: 499.25 caracteres.
- chunk_size = 1000 e overlap = 0: 998.17 caracteres.
- chunk_size = 2000 e overlap = 0: 1989.33 caracteres.

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
Sim, em comparação com o chunking puramente baseado em caracteres. A estratégia sentencas_agrupadas utiliza as sentenças como unidade de construção, evitando cortar uma frase arbitrariamente no meio.

### O Recursive Splitter apresentou vantagens?


### O Markdown Splitter conseguiu preservar a estrutura semântica?
Sim, e foi uma das estratégias que apresentou os resultados mais interessantes. Como os documentos foram convertidos para Markdown, essa estratégia consegue utilizar elementos estruturais do documento, em vez de simplesmente considerar a quantidade de caracteres.

Um resultado interessante é que ela gerou poucos chunks sem produzir necessariamente os chunks gigantes do método "paragrafo_recursivo".

Por exemplo, bioetica_e_ia produziu:

- Markdown: 22 chunks;
- sentença: 135 chunks;
- parágrafo recursivo: 76 chunks.

### Qual estratégia parece mais adequada para um sistema de RAG?
Com base nos resultados desses experimentos, eu priorizaria:

- markdown;
- fixed with overlap: chunk_size = X e overlap = X.

O Markdown parece especialmente interessante porque preserva melhor a estrutura semântica dos documentos com base nos arquivos que foram utilizados para teste.

O fixed with overlap é interessante quando se deseja uma estratégia mais simples e controlável, utilizando o overlap para diminuir a perda de contexto entre partes consecutivas. Os resultados mostram que aumentar o overlap aumenta tanto o número de chunks quanto o número de tokens processados.

É importante observar que o fato de termos utilizado documentos bem estruturados e padronizados, como artigos cientificos, facilita a extração dos textos quando geramos os arquivos ".md".

Caso seja necessario a utilização de outros tipos de arquivos, provavelmente os resultados serão alterados.

### Quais estratégias devem ser descartadas?


### Quais estratégias você acha que devem ser utilizadas nos próximos experimentos? 
Eu recomendaria concentrar os próximos testes em três estratégias:

- markdown;
- fixed with overlap:	chunk_size = "X" + overlap "X".

Os experimentos mostraram que não basta buscar a maior ou menor quantidade de chunks. Para um RAG, o mais importante é encontrar um equilíbrio entre tamanho, quantidade, preservação do contexto e estrutura semântica.

Por isso, ainda não é possivel definir um tamanho exato para o chunk_size e para o overlap. Mas acredito que possa ser interessante algo como chunk_size = 500 + overlap 100.
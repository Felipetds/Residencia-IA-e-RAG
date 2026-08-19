# Projeto e Arquitetura de uma Aplicação RAG - Assistente para dúvidas sobre produtos de um e-commerce
Catálogo, especificações, avaliações

## Parte 1 - Identificação dos problemas

## 1.1 Descrição do problema

### Qual é o problema que você deseja resolver?
Desenvolver um assistente virtual capaz de responder perguntas dos clientes sobre os produtos disponíveis em um e-commerce, utilizando RAG para recuperar informações relevantes de uma base de conhecimento antes de gerar a resposta.

### Quem utilizaria a aplicação? 
Cliente que tiverem interesse em algum produto mas possam ter alguma duvida em relação a marca, aplicação ou qualquer outro tema relacionado.

### Que tipo de informação o usuário gostaria de consultar?
Especificações técnicas de produtos, média de preço entre modelos concorrentes, diferença entre modelos entre outras.

### De onde vêm essas informações?
De bases de conhecimento, manuais de usuários entre outros.

### Por que utilizar um LLM sozinho não seria suficiente?
Um LLM sozinho não seria suficiente porque ele gera respostas com base nos conhecimentos adquiridos durante seu treinamento e não possui, necessariamente, acesso às informações atualizadas e específicas do catálogo do e-commerce. O modelo pode não conhecer esse produto específico ou pode fornecer uma informação incorreta. Pode acontecer também de informações como preço, estoque, especificações e disponibilidade mudar constantemente.
O uso de RAG permite consultar uma base de conhecimento atualizada antes da geração da resposta. Dessa forma, o modelo recebe informações relevantes sobre o produto e utiliza esse contexto para formular a resposta.

### Como o usuário vai utilizar o sistema? (API, aplicativo, interface web?)
Aplicativo ou interface web.

### Exemplos de perguntas realizadas pelos usuários:
- "Qual tipo de processador esse notebook utiliza?"
- "Qual tipo de tela esse notebook possui?"
- "Qual a diferença entre o produto X da marca A e da marca B?"

## 1.3

### Existe alguma pergunta, dentro do seu próprio cenário, que RAG responderia mal e um banco de dados relacional responderia bem? Qual, e por quê?
Sim. Um exemplo seria: "Qual é o preço atual do Notebook Dell Inspiron 15?". Nesse caso, O preço é uma informação estruturada e dinâmica, que pode ser alterada frequentemente. Um banco de dados relacional consegue consultar diretamente o valor mais recente.
RAG é mais adequado para informações textuais, semânticas e documentais, enquanto bancos relacionais são melhores para informações estruturadas, exatas e dinâmicas, como preço, estoque e pedidos. O cenário ideal para o e-commerce seria combinar as duas abordagens.

### O que aconteceria se a pergunta do usuário exigisse contar, somar ou ordenar informação espalhada por muitos documentos?
Nesse caso, poderia apresentar resultados imprecisos, pois sua função principal é recuperar os documentos ou chunks mais relevantes para uma pergunta, e não realizar operações matemáticas ou agregações sobre grandes conjuntos de dados.

Exemplo: "Quantos produtos da categoria notebook possuem mais de 16 GB de RAM?"

Essa informação pode estar espalhada por centenas de documentos. O modelo poderia recuperar apenas os Top 10 chunks mais relevantes, deixando produtos de fora. Consequentemente, o modelo poderia chegar a uma contagem incorreta.

## Parte 2 - Organização dos documentos

### Quais tipos de arquivo existirão? (PDF, DOCX, HTML, Markdown, páginas web, planilhas, imagens, áudios, vídeos, outros)

### Qual o volume aproximado? (dezenas, centenas, milhares de documentos?)

### Qual o tamanho típico de cada documento? (Paginas, kbs)

### Com que frequência novos documentos entram? Documentos antigos são atualizados ou substituídos?

### Organização de pastas:

```text
```

Exemplo:
```text
setor
  ↓
tipo de produtos
        ↓
busca semântica
        ↓
documentos mais relevantes
```

### Existe documento que não deve entrar na base?

Serão adicionados somente arquivos que possuam informações relevantes dos produtos como manuais, informações sobre garatias e descrições de especificações técnicas.

### Como lidar com versões do mesmo documento?

Para evitar conflitos relacionados a datas, versões ou outros casos, cada documento deve possuir metadados de versão, validade e identificação do produto.

## Parte 3 - Pipeline de ingestão

### 3.1 Extração

A extração de texto dos documentos seria realizada utilizando a biblioteca Docling em Python, que permite converter diferentes formatos de documentos para uma representação estruturada, preservando informações como texto, tabelas e estrutura do documento.
Para PDFs que possuem uma camada de texto, o Docling realizará a extração diretamente do conteúdo textual, evitando a necessidade de OCR. Durante essa etapa, é importante preservar informações estruturais do documento.

As tabelas não serão descartadas, pois podem conter informações relevantes. A preservação dessas informações também é importante para perguntas que posteriormente possam exigir contagem, soma ou ordenação de informações.

As imagens serão analisadas de acordo com sua relevância para o documento. Imagens que contenham informações relevantes, como gráficos, documentos, comprovantes ou outros casos, não deverão ser simplesmente descartadas. Quando necessário, essas informações poderão ser processadas por OCR ou por modelos capazes de interpretar conteúdo visual. Imagens sem valor informacional serão descartadas para evitar o armazenamento de conteúdo desnecessário.

### 3.2 Limpeza e normalização

A limpeza não terá como objetivo deixar o documento "limpo", mas sim melhorar a qualidade do conteúdo utilizado pelo RAG sem comprometer a informação necessária para a recuperação e a rastreabilidade das informações.

O principal ponto é remover informações duplicadas.

Exemplo: Manual de uma ferramenta. 

Geralmente existe as mesmas intruções em idiomas diferentes, nesses casos deve ser mantida somente as instruções em português. Caso não possua, devera ser mantido em inglês. 

### 3.3 Frequência de ingestão

Sempre que um novo produto for adicionado ao catálogo da empresa.
Documentos antigos também serão avaliados periodicamente e poderão ser substituídos, desativados ou removidos, principalmente quando estiverem desatualizados e houver risco de contribuírem para respostas incorretas.
Quando um documento for adicionado ou atualizado, não será necessário reprocessar toda a base. O ideal é realizar um processamento incremental, reprocessando somente o documento que sofreu alteração. Isso evita processamento desnecessário e reduz o custo e o tempo de atualização da base.

## Parte 4 - Metadados

### 4.1 Metadados do documento

### 4.2 Metadados do chunk

```text
{
  "documento_id": "doc_0001",
  "chunk_index": 15,
  "pagina_inicio": 6,
  "pagina_fim": 6,
  "tipo_conteudo": "texto",
  "n_caracteres": 368,
  "n_tokens": 106
}
```

Os metadados do chunk serão utilizados para identificar onde o trecho está localizado no documento e quais são suas características.

- documento_id: Relaciona o chunk ao documento de origem.
- chunk_index: Identifica a posição do chunk dentro do documento e facilita sua rastreabilidade.
- pagina_inicio: Permite localizar o início do conteúdo no documento original e citar a fonte.
- pagina_fim: Permite identificar até onde o conteúdo do chunk se estende.
- tipo_conteudo: Permite diferenciar texto, tabela, lista, código ou outros tipos de conteúdo.
- n_caracteres: Permite analisar o tamanho dos chunks e avaliar a estratégia de chunking.
- n_tokens: Permite controlar o tamanho dos chunks em relação ao limite de contexto do modelo e analisar o custo de processamento.

```text
Documento
│
├── Metadados do documento
│   ├── documento_id
│   ├── fonte
│   ├── setor
│   ├── tipo_documento
│   ├── marca
│   └── tipo_de_equipamento
│
├── Chunk 0
│   └── Metadados do chunk
│       ├── chunk_index
│       ├── pagina_inicio
│       ├── pagina_fim
│       ├── tipo_conteudo
│       ├── n_caracteres
│       └── n_tokens
│
└── ...
```

## Parte 5 - Chunking / Splitting

O metodo escolhido foi o "MarkdownHeaderTextSplitter", ele vai dividir o documento pela estrutura dos títulos com o "separators=["\n\n", "\n", " ", ""]". 

Não utilizaria o overlap por entender que o metodo já preserva suficientemente o contexto.

- Limite Máximo de Contexto (Tokens por String): O limite é de 8.191 tokens por string/texto individual enviado.
- Limite de Lote (Batching Limits): A soma de todos os tokens de todas as strings contidas no mesmo lote (batch) não pode ultrapassar 300.000 tokens por requisição.


## Parte 6 - Embeddings

| ITEM | RESPOSTAS |
| --- | --- |
| Modelo escolhido | text-embedding-3-small |
| Dimensão do embedding | 1536 (padrão, mas aceita redução flexível via código) |
| Suporta português? | Sim, com excelente desempenho em benchmarks locais |
| É multilíngue? | Sim, possui suporte nativo a dezenas de idiomas com melhorias significativas sobre o modelo anterior |
| Tamanho máximo de entrada | 8.191 tokens por requisição |
| É open source? | Não, trata-se de um modelo proprietário |
| Pode ser executado localmente? | Não, a execução depende exclusivamente dos servidores em nuvem da OpenAI |
| Possui API? | Sim, integrada via endpoint oficial de Embeddings da OpenAI |
| Custo aproximado | $0.02 por milhão (1M) de tokens de entrada |
| Fonte da informação | https://help.openai.com/pt-br/articles/6824809-embeddings-faq |

### Considerou algum modelo alternativo e descartou? Qual, e por quê?
Considerei o uso de algum modelo que seja gratuito para tonar o projeto mais acessivel. 

### Se o cenário envolve documentos sigilosos, isso muda sua escolha entre modelo local e API? Como?
Não, inicialmente o sistema não possuiria dados sigilosos.

### O tamanho máximo de entrada do modelo tem relação com a sua decisão de chunking da Parte 5? Explique.
Sim, essa limitação é uma das formas de controlar o custo da aplicação. O modelo text-embedding-3-small da OpenAI possui limitações estritas de entrada que afetam a quantidade de texto enviada por chamada.

- Limite Máximo de Contexto (Tokens por String): O limite é de 8.191 tokens por string/texto individual enviado.
- Limite de Lote (Batching Limits): A soma de todos os tokens de todas as strings contidas no mesmo lote (batch) não pode ultrapassar 300.000 tokens por requisição.

## Arquitetura final

| ETAPA | DECISAO | JUSTIFICATIVA |
| --- | --- | --- |
| Extração | Docling para converter documentos padronizados em Markdown. | Preserva a estrutura e facilita a leitura de arquivos |
| Limpeza | Limpeza mínima ou nula | Interferencia minima para evitar perda de informações importantes |
| Chunking | Divisão inicial por seção | Preserva o contexto e não gera chunks extremamente grandes |
| Metadados | Dados de identificação, localização e tamanho dos documentos e dos chunks | Essas informações garantem localização para referências |
| Embeddings | Modelo text-embedding-3-small (Pode ser uma alternativa local) | Excelente custo-benefício e facil de acompanhar as métricas de utilização/custo |

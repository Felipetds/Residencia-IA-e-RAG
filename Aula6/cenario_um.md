# Projeto e Arquitetura de uma Aplicação RAG - Advocacia (busca por jurisprudencias)

Definição:
Jurisprudência é o conjunto de decisões e interpretações dadas pelos tribunais sobre um mesmo tema jurídico ao longo do tempo. Ela serve como um guia para orientar novos julgamentos em casos parecidos, trazendo mais segurança e ordem para a Justiça.

## Parte 1 - Identificação dos problemas

## 1.1 Descrição do problema

### Qual é o problema que você deseja resolver?
Confiabilidade de que as informações retornadas pelo modelo são reais e rastreaveis (O modelo deve retornar susgestões de decisões que se assemelhem com a petição inicial que está sendo escrita).

### Quem utilizaria a aplicação? 
Advogados em geral.

### Que tipo de informação o usuário gostaria de consultar?
Sentenças: Ato que encerra a fase principal do processo ou a execução, julgando se o pedido é aceito ou negado.
Decisões Interlocutórias: Resposta dada pelo juiz a uma questão específica durante o andamento do processo.

### De onde vêm essas informações?
Arquivos do proprio avogado e base de conhecimento (Documentos validados de outros casos).

### Por que utilizar um LLM sozinho não seria suficiente?
Alto risco de alucinações: Erros de conceitos, jurisprudências que foram alteradas com o passar do tempo e inventar informações genéricas ou falsas. 

### Como o usuário vai utilizar o sistema? (API, aplicativo, interface web?)
Aplicativo ou interface web.

### Exemplos de perguntas realizadas pelos usuários:
"Estou preparando uma petição inicial sobre falha na prestação de serviço (X) contratado, O contrato possui valor (Y) e prazo de duração (Z). Encontre casos semelhantes na base de dados e mostre quais foram as decisões dos juízes."

"Pedido de indenização por cobrança indevida no valor (X) realizada por empresa do setor (Y). Existem sentenças na nossa base em que o pedido de indenização por foi julgado procedente em casos parecidos com este? Quais foram os valores fixados?"

"Analise esta petição inicial e me indique casos semelhantes da nossa base que tenham fatos e argumentos jurídicos semelhantes, informando de qual processo e documento cada decisão foi retirada."

## 1.3

### Existe alguma pergunta, dentro do seu próprio cenário, que RAG responderia mal e um banco de dados relacional responderia bem? Qual, e por quê?
Um banco de dados relacional conseguiria desempenhar melhor em consultas simples como em utilização de filtros, exemplo: temas, datas e se a sentença foi favoravel ou não. O principal fator é o custo de tokens por consulta.

### O que aconteceria se a pergunta do usuário exigisse contar, somar ou ordenar informação espalhada por muitos documentos?
Nesses caso o ideal é utilizar o modelo apenas para retornar as informações impondo um limite na consulta. Exemplo: Quantas decisões da base reconheceram dano moral em casos (X) e qual foi o maior valor de indenização?
O ideal é realizar a busca focando nos aspectos principais da pergunta, "reconheceram dano moral em casos (X)" e "valor de indenização". Retornar os 10 principais documentos, relizar a extração das informações, realizar a ordenação e os calculos dentro do proprio sistema e não pelo modelo.
Essas informações como "valor de indenização" podem ser adicionadas aos metadados dos chunks para facilitar as consultas.

## Parte 2 - Organização dos documentos

### Quais tipos de arquivo existirão? (PDF, DOCX, HTML, Markdown, páginas web, planilhas, imagens, áudios, vídeos, outros)
Provavelmente seriam apenas PDFs por se tratar de documentos oficiais. "A principal extensão usada para envio e protocolo de documentos jurídicos nos tribunais brasileiros é o .pdf, exigido pela maioria absoluta dos sistemas de processo eletrônico (como PJe, e-SAJ e PROJUDI)."

### Qual o volume aproximado? (dezenas, centenas, milhares de documentos?)
Provavelmente algo em torno de centenas inicialmente.

### Qual o tamanho típico de cada documento? (Paginas, kbs)
 tamanho pode variar entre 10 a 50 páginas para cada documento aproximadamente podendo pesar de 0,3 MB a 4 MB em arquivos que possuem apenas texto e 10 MB a 50 MB em arquivos que possuem texto com gráficos, tabelas e imagens.

### Com que frequência novos documentos entram? Documentos antigos são atualizados ou substituídos?
Inicialmente seriam adicionados novos documentos a cada 3 meses, podendo ser em menos tempo em casos especiais. Documentos antigos seriam subistituidos ou removidos com o tempo para evitar respostas desatualizadas.

### Organização de pastas:
Os documentos seriam divididos de acordo com os temas principais.

```text
documentos/
├── direito_civil/
│   ├── peticoes/
│   ├── sentencas/
│   └── decisoes_interlocutorias/
│
├── direito_consumidor/
│   ├── peticoes/
│   ├── sentencas/
│   └── decisoes_interlocutorias/
│
├── direito_trabalhista/
│   ├── peticoes/
│   ├── sentencas/
│   └── decisoes_interlocutorias/
│
├── direito_previdenciario/
│   ├── peticoes/
│   ├── sentencas/
│   └── decisoes_interlocutorias/
│
├── direito_penal/
│   ├── peticoes/
│   ├── sentencas/
│   └── decisoes_interlocutorias/
│
└── direito_ambiental/
    ├── peticoes/
    ├── sentencas/
    └── decisoes_interlocutorias/
```

A organização dos documentos foi definida considerando a forma como o usuário pode realizar buscas de informações jurídicas e os filtros que podem ser utilizados. A primeira divisão é feita pela área de atuação, pois esse é um dos principais critérios utilizados pelo usuário para delimitar uma pesquisa. Por exemplo, uma busca sobre cobrança indevida tende a estar relacionada ao Direito do Consumidor, enquanto uma busca sobre aposentadoria pertence ao Direito Previdenciário.

O próximo nível de organização é o tipo de documento. Essa divisão é importante porque o usuário pode querer, por exemplo, encontrar sentenças semelhantes a uma determinada petição, sem necessariamente recuperar outras petições. Além disso, essas categorias podem posteriormente ser utilizadas como metadados e filtros no processo de recuperação.

Exemplo:
```text
área do Direito
        ↓
tipo de documento
        ↓
busca semântica
        ↓
documentos mais relevantes
```

### Existe documento que não deve entrar na base?
Nem todo documento disponível deve ser inserido automaticamente na base de conhecimento, Alguns exemplos são:

- Documentos contendo dados pessoais desnecessários;
- Informações protegidas por sigilo profissional;
- Documentos de processos que não podem ser compartilhados;
- Documentos com informações financeiras ou pessoais sensíveis;
- Arquivos incompletos ou corrompidos;
- Documentos obsoletos;
- Versões preliminares ou documentos que ainda não foram validados.

### Como lidar com versões do mesmo documento?
Para evitar conflitos relacionados a datas, versões ou outros casos, cada documento deve possuir metadados de versão e validade.

## Parte 3 - Pipeline de ingestão

### 3.1 Extração
A extração de texto dos documentos seria realizada utilizando a biblioteca Docling em Python, que permite converter diferentes formatos de documentos para uma representação estruturada, preservando informações como texto, tabelas e estrutura do documento.
Para PDFs que possuem uma camada de texto, o Docling realizará a extração diretamente do conteúdo textual, evitando a necessidade de OCR. Durante essa etapa, é importante preservar informações estruturais do documento, como:

- títulos;
- parágrafos;
- listas;
- tabelas;
- páginas;
- ordem do conteúdo.

Essas informações serão utilizadas posteriormente na geração dos chunks e dos metadados para auxiliar o modelo a reponder às perguntas com mais eficiência e para referenciar as respostas.

Para PDFs digitalizados, nos quais o conteúdo está armazenado como imagem e não existe uma camada de texto, será utilizado o recurso de OCR - Optical Character Recognition, ou Reconhecimento Óptico de Caracteres. Como o OCR pode apresentar erros, especialmente em nomes, números de processos, valores e termos jurídicos, o documento original deverá ser mantido para possibilitar a conferência das informações extraídas.

As tabelas não serão descartadas, pois podem conter informações relevantes para a análise jurídica, como valores, datas, cálculos e comparações. A preservação dessas informações também é importante para perguntas que posteriormente possam exigir contagem, soma ou ordenação de informações.

As imagens serão analisadas de acordo com sua relevância para o documento. Imagens que contenham informações relevantes, como gráficos, documentos, comprovantes ou outras evidências, não deverão ser simplesmente descartadas. Quando necessário, essas informações poderão ser processadas por OCR ou por modelos capazes de interpretar conteúdo visual. Imagens sem valor informacional serão descartadas para evitar o armazenamento de conteúdo desnecessário.

### 3.2 Limpeza e normalização
Após a extração dos documentos utilizando o Docling, será realizada uma etapa de limpeza e normalização para remover informações desnecessárias e corrigir problemas de formatação que possam prejudicar a geração dos chunks e a recuperação dos documentos. Serão removidos ou tratados elementos que aparecem repetidamente e não contribuem diretamente para o conteúdo jurídico.
As referências, citações legais, números de processos, nomes de tribunais e outras informações jurídicas não serão removidas, pois podem ser importantes para a rastreabilidade das respostas.
A limpeza não terá como objetivo deixar o documento "limpo", mas sim melhorar a qualidade do conteúdo utilizado pelo RAG sem comprometer a informação necessária para a recuperação e a rastreabilidade das informações jurídicas.

### 3.3 Frequência de ingestão
Inicialmente, a ingestão de novos documentos será realizada de forma agendada, aproximadamente a cada três meses. Esse período poderá ser reduzido em situações especiais, como a publicação de decisões relevantes ou alterações importantes na legislação que exijam uma atualização mais rápida da base.
Documentos antigos também serão avaliados periodicamente e poderão ser substituídos, desativados ou removidos, principalmente quando estiverem desatualizados e houver risco de contribuírem para respostas incorretas.
Quando um documento for adicionado ou atualizado, não será necessário reprocessar toda a base. O ideal é realizar um processamento incremental, reprocessando somente o documento que sofreu alteração. Isso evita processamento desnecessário e reduz o custo e o tempo de atualização da base.

## Parte 4 - Metadados

### 4.1 Metadados do documento
```text
{
  "documento_id": "doc_0000001",
  "fonte": "sentenca_0000001.pdf",
  "area_direito": "direito_consumidor",
  "tipo_documento": "sentenca",
  "tribunal": "TJRJ",
  "numero_processo": "0000000-00.0000.0.00.0000",
  "data_documento": "18-08-2026",
  "versao": "1.0",
  "status": "vigente",
  "data_inicio_validade": "18-08-2026",
  "data_fim_validade": null
}
```

- documento_id: Identifica unicamente o documento e permite criar uma relação entre os seus chunks.
- fonte: Permite identificar o arquivo original e apresentar a fonte ao usuário.
- area_direito: Permite filtrar a busca por área.
- tipo_documento: Permite diferenciar petições, sentenças e decisões interlocutórias.
- tribunal: Permite restringir a busca a determinado tribunal e auxilia na identificação da fonte.
- numero_processo: Permite rastrear a decisão até o processo original e apresentar essa informação ao usuário.
- data_documento: Permite realizar filtros temporais e contextualizar a decisão.
- versao: Permite diferenciar versões de um mesmo documento.
- status: Indica se o documento está vigente, obsoleto ou pendente de validação.
- data_inicio_validade: Permite determinar a partir de quando aquela versão é válida.
- data_fim_validade: Permite determinar até quando aquela versão foi válida.

### 4.2 Metadados do chunk
```text
{
  "documento_id": "doc_0000001",
  "chunk_index": 15,
  "pagina_inicio": 8,
  "pagina_fim": 10,
  "tipo_conteudo": "texto",
  "n_caracteres": 1842,
  "n_tokens": 420
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
│   ├── area_direito
│   ├── tipo_documento
│   ├── tribunal
│   ├── numero_processo
│   ├── data_documento
│   ├── versao
│   ├── status
│   ├── data_inicio_validade
│   └── data_fim_validade
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

Os principais filtros serão aplicados sobre os metadados do documento: area_direito, tipo_documento, tribunal, data_documento, status, data_inicio_validade e data_fim_validade.

Exemplo: "Encontre sentenças do Direito do Consumidor do TJRJ sobre negativação indevida."

O sistema poderia aplicar:
```text
{
  "area_direito": "direito_consumidor",
  "tipo_documento": "sentenca",
  "tribunal": "TJRJ"
}
```

Para apresentar a fonte ao usuário, serão combinados metadados dos dois níveis para permitir ao usuario voltar ao documento original e conferir o trecho utilizado.

Exemplo:
- Tribunal: TJRJ
- Processo: 0000000-00.0000.0.00.0000
- Documento: sentença_0000001.pdf
- Data: 18-08-2026
- Página: 8–10

Os metadados terão diferentes origens, parte vem do proprio LLM e parte vem do sistema.
- Exemplo LLM: tribunal, processo e tipo_conteudo.
- Exemplo sistema: area_direito, tipo_documento e documento_id.

```text
Estrutura de pastas
        ↓
area_direito / tipo_documento

Docling
        ↓
fonte / páginas / estrutura

LLM com saída estruturada
        ↓
tribunal / processo / data

Pipeline
        ↓
documento_id / versão / status

Chunking
        ↓
chunk_index / tamanho / tipo_conteudo
```

## Parte 5 - Chunking / Splitting

O metodo escolhido foi de divisão em duas etapas, o "MarkdownHeaderTextSplitter" vai dividir o documento pela estrutura dos títulos com o "separators=["\n\n", "\n", " ", ""]". Em seguida, o resultado passa pelo "RecursiveCharacterTextSplitter" para limitar o tamanho maximo dos chunks e adaptar aos valores aceitos pela API.

Não utilizaria o overlap por entender que esses metodos já preservam suficientemente o contexto.

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
Outras opções de modelos para serem utilizados localmente caso exista alguma necessidade de proteger os dados.

- Multilingual-E5 (intfloat/multilingual-e5-small ou large): Suporte a mais de 100 idiomas, incluindo português, com ótima precisão para buscas semânticas e RAG.
- BGE (BAAI/bge-m3): Modelo multilíngue de alta performance, muito robusto para recuperação de textos densos e esparsos.
- Nomic Embed (nomic-ai/nomic-embed-text): Muito leve, excelente para rodar rapidamente apenas com CPU ou em dispositivos com restrição de hardware.
- Qwen3-Embedding (Qwen/Qwen3-Embedding-0.6B): Modelo muito poderoso de código aberto que lida bem com densidade vetorial e recuperação em vários idiomas.

### Se o cenário envolve documentos sigilosos, isso muda sua escolha entre modelo local e API? Como?
Sim, é extremamente importante preservar os dados sensiveis. O foco passa a ser executar localmente para que nenhum dado ou documento seja enviado para APIs externas garantindo a privacidade e conformidade com leis como a LGPD.

### O tamanho máximo de entrada do modelo tem relação com a sua decisão de chunking da Parte 5? Explique.
Sim, essa limitação é uma das formas de controlar o custo da aplicação. O modelo text-embedding-3-small da OpenAI possui limitações estritas de entrada que afetam a quantidade de texto enviada por chamada.

- Limite Máximo de Contexto (Tokens por String): O limite é de 8.191 tokens por string/texto individual enviado.
- Limite de Lote (Batching Limits): A soma de todos os tokens de todas as strings contidas no mesmo lote (batch) não pode ultrapassar 300.000 tokens por requisição.

## Arquitetura final

| ETAPA | DECISAO | JUSTIFICATIVA |
| --- | --- | --- |
| Extração | Docling para converter documentos padronizados em Markdown. | Preserva a estrutura e facilita a leitura de arquivos |
| Limpeza | Limpeza mínima ou nula para documentos gerados nativamente pela aplicação. | Interferencia minima para evitar perda de informações importantes |
| Chunking | Divisão inicial por seção e divisão sevundaria para garantir o tamanho dentro do limite da API | Preserva o contexto e garante a adequação de tamanho ao input do modelo |
| Metadados | Dados de identificação, localização, tempo e tamanho dos documentos e dos chunks | Essas informações garantem controle de versão e localização para referências |
| Embeddings | Modelo text-embedding-3-small (Pode ser uma alternativa local) | Excelente custo-benefício e facil de acompanhar as métricas de utilização/custo |
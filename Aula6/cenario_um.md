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

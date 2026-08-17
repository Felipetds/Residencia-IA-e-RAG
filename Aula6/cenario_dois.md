# Projeto e Arquitetura de uma Aplicação RAG - Assistente para dúvidas sobre produtos
Catálogo, especificações, avaliações

## Parte 1 - Identificação dos problemas

## 1.1 Descrição do problema

### Qual é o problema que você deseja resolver?

### Quem utilizaria a aplicação? 

### Que tipo de informação o usuário gostaria de consultar?

### De onde vêm essas informações?

### Por que utilizar um LLM sozinho não seria suficiente?

### Como o usuário vai utilizar o sistema? (API, aplicativo, interface web?)

### Exemplos de perguntas realizadas pelos usuários:

## 1.3

### Existe alguma pergunta, dentro do seu próprio cenário, que RAG responderia mal e um banco de dados relacional responderia bem? Qual, e por quê?

### O que aconteceria se a pergunta do usuário exigisse contar, somar ou ordenar informação espalhada por muitos documentos?

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
área do Direito
        ↓
tipo de documento
        ↓
busca semântica
        ↓
documentos mais relevantes
```

### Existe documento que não deve entrar na base?

### Como lidar com versões do mesmo documento?

## Parte 3 - Pipeline de ingestão

### 3.1 Extração


### 3.2 Limpeza e normalização

### 3.3 Frequência de ingestão

## Parte 4 - Metadados

### 4.1 Metadados do documento

### 4.2 Metadados do chunk

## Parte 5 - Chunking / Splitting

## Parte 6 - Embeddings

## Arquitetura final

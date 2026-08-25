# Acompanhamento - Mini Desafio RAG VendeFácil

**Integrante 1:** Marcos Felix Da Silva - [@MarcosFelixmdr](https://github.com/MarcosFelixmdr)
**Integrante 2:** Irene da Costa - [@Irene-costa](https://github.com/Irene-costa)
**Integrante 3:** Felipe Teixeira da Silva - [@Felipetds](https://github.com/Felipetds)

**Repositório:** `https://github.com/MarcosFelixmdr/rag-vendefacil--grupo05--Felix-Silva-Costa`

---

## Como preencher

- Um bloco por encontro, em **ordem cronológica** - o encontro mais recente vai no **fim** do arquivo.
- O relato individual é escrito **pelo próprio integrante**, em primeira pessoa. Não escreva pelo colega.
- Escrever entre **17:30 e 17:40**. `commit` + `push` até as **18:00**, mesmo que o dia não tenha fechado.
- Mensagem de commit: `acompanhamento: AAAA-MM-DD`

**Um relato útil responde:** o que eu implementei, qual decisão técnica eu tomei e por quê, onde travei, e como (ou se) resolvi.

<details>
<summary>Exemplo de relato individual bom × ruim</summary>

❌ *"Trabalhei na parte de ingestão junto com meu colega. Avançamos bastante e conseguimos carregar os arquivos."*

✅ *"Implementei os loaders de CSV e JSONL em `src/ingest.py`. Decidi serializar cada linha do `customers.csv` como frase em linguagem natural em vez de manter o formato separado por vírgula, porque nos primeiros testes de similaridade os chunks CSV crus não recuperavam nada - o embedding não separa campo de valor. Travei ~40 min no `tickets.jsonl`: o `state` estava indo para o texto do chunk mas não para os metadados, então o filtro voltava vazio. Resolvi movendo a extração para antes da criação do `Document`. Usei o Claude para gerar o esqueleto do parser de JSONL; ajustei o schema de metadados na mão."*

</details>

---

## Encontro 1 - 2026-08-24

**Etapa:** 1 - Ingestão heterogênea, metadados e indexação vetorial

### Relato individual - [Marcos Felix Da Silva]
Adiconei meus dados no arquivo, todos fizeram o mesmo depois ficamos discutindo modelos de IA para serem usados para a etapa 1. Ainda não decidimos e vamos pesquisar por fora e definir os modelos mais eficientes e economicos para essa tarefa.

### Relato individual - [Irene da Costa]
Clonei o repositório, adicionei meus dados do GitHub, usei o gemini para estruturar a divisão de papéis do trio e gerar o template do ACOMPANHAMENTO.md de acordo com as regras do guia do aluno.

### Relato individual - [Felipe Silva]
Fiz a configuração do vs code e do github, clonei o repositório, conversamos sobre os modelos que serão usados no projeto. Sugestões para gerar embeddings: "text-embedding-3-small".
Outros modelos foram sugeridos para o llm que vai ser responsável pelas respostas, vamos pesquisar os custos e limitações.

### Resumo do dia (escrito em conjunto)

**Entregamos hoje:**
- Fizemos 0.1 ao 0.3 e discutimos os requisitos do projetos: modelos de IA para as respostas, modelos para os embeddings e estratégias de chunking.  

**Ficou pendente:**
- Definir os modelos que serão utilizados, carregar e processar arquivos, aplicar as estratégias de chunking, anexar um schema de metadados padronizado a cada chunk e vetorizar e indexar em FAISS.

**Bloqueios em aberto:**
- Não tivemos nenhum bloqueio até o momento.

**Próximo passo (início do encontro 2):**
- Iniciar a etapa 1 e finalizar os requisitos do projeto.

**Uso de assistentes de IA:**
- Comparação entre os modelos sugeridos e pesquisa.

---

## Encontro 2 - AAAA-MM-DD

**Etapa:** 2 - Busca híbrida e filtragem por metadados

### Relato individual - [Nome do Integrante 1]

### Relato individual - [Nome do Integrante 2]

### Resumo do dia (escrito em conjunto)

**Entregamos hoje:**
-

**Ficou pendente:**
-

**Bloqueios em aberto:**
-

**Próximo passo (início do encontro 3):**
-

**Uso de assistentes de IA:**
-

---

## Encontro 3 - AAAA-MM-DD

**Etapa:** 3 - Síntese estruturada, evidência e guardrails de LGPD

### Relato individual - [Nome do Integrante 1]

### Relato individual - [Nome do Integrante 2]

### Resumo do dia (escrito em conjunto)

**Entregamos hoje:**
-

**Ficou pendente:**
-

**Bloqueios em aberto:**
-

**Próximo passo (início do encontro 4):**
-

**Uso de assistentes de IA:**
-

---

## Encontro 4 - AAAA-MM-DD

**Etapa:** 4 - Avaliação (RAG Triad), interface e relatório

### Relato individual - [Nome do Integrante 1]

### Relato individual - [Nome do Integrante 2]

### Resumo do dia (escrito em conjunto)

**Entregamos hoje:**
-

**Ficou pendente:**
-

**Bloqueios em aberto:**
-

**Preparação para o Demo Day:**
-

**Uso de assistentes de IA:**
-

---

*TIC em Trilhas · PUC-Rio · Instituto ECOA · MCTI Futuro · Softex*

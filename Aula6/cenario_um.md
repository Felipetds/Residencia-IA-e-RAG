# Projeto e Arquitetura de uma Aplicação RAG - Advocacia (busca por jurisprudencias)

Definição:
Jurisprudência é o conjunto de decisões e interpretações dadas pelos tribunais sobre um mesmo tema jurídico ao longo do tempo. Ela serve como um guia para orientar novos julgamentos em casos parecidos, trazendo mais segurança e ordem para a Justiça.

## 1.1 Descrição do problema

### Qual é o problema que você deseja resolver?
- Confiabilidade de que as informações retornadas pelo modelo são reais e rastreaveis (O modelo deve retornar susgestões de decisões que se assemelhem com a petição inicial que está sendo escrita).

### Quem utilizaria a aplicação? 
- Advogados em geral.

### Que tipo de informação o usuário gostaria de consultar?
- Sentenças: Ato que encerra a fase principal do processo ou a execução, julgando se o pedido é aceito ou negado.
- Decisões Interlocutórias: Resposta dada pelo juiz a uma questão específica durante o andamento do processo.

### De onde vêm essas informações?
- Arquivos do proprio avogado e base de conhecimento (Documentos validados de outros casos).

### Por que utilizar um LLM sozinho não seria suficiente?
- Alto risco de alucinações: Erros de conceitos, jurisprudências que foram alteradas com o passar do tempo e inventar informações genéricas ou falsas. 

### Como o usuário vai utilizar o sistema? (API, aplicativo, interface web?)
- Aplicativo ou interface web.

### Exemplos de perguntas realizadas pelos usuários:
- "Estou preparando uma petição inicial sobre falha na prestação de serviço (X) contratado, O contrato possui valor (Y) e prazo de duração (Z). Encontre casos semelhantes na base de dados e mostre quais foram as decisões dos juízes."

- "Pedido de indenização por cobrança indevida no valor (X) realizada por empresa do setor (Y). Existem sentenças na nossa base em que o pedido de indenização por foi julgado procedente em casos parecidos com este? Quais foram os valores fixados?"

- "Analise esta petição inicial e me indique casos semelhantes da nossa base que tenham fatos e argumentos jurídicos semelhantes, informando de qual processo e documento cada decisão foi retirada."
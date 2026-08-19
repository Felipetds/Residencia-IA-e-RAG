# Comparação entre os dois cenários

### Em que pontos as decisões foram diferentes? Por quê?
As principais diferenças estão relacionadas à natureza das informações e ao nível de confiabilidade e rastreabilidade exigido em cada aplicação.

No cenário de e-commerce, o sistema é voltado para clientes que desejam consultar especificações, características e diferenças entre produtos. Além disso, informações estruturadas e dinâmicas, como preço e estoque, foram identificadas como mais adequadas para consulta em banco de dados relacional.

No cenário de advocacia, o objetivo é a confiabilidade e a rastreabilidade da informação, pois o sistema deve encontrar decisões semelhantes e permitir que o advogado identifique de qual processo e documento aquela informação foi retirada. Isso fez com que os metadados fossem mais específicos, incluindo tribunal, numero_processo, data_documento, versao, status e período de validade.

Também houve diferença no chunking:
- No e-commerce, foi escolhida uma divisão baseada inicialmente na estrutura dos títulos/seções. 
- Na advocacia, foi adotada uma estratégia em duas etapas: primeiro a divisão pela estrutura dos títulos e depois uma divisão adicional para limitar o tamanho dos chunks. Essa decisão faz sentido porque os documentos jurídicos podem possuir seções extensas e precisam manter simultaneamente contexto e tamanho controlado.

Outra diferença importante está na privacidade. No e-commerce, foi considerado que inicialmente não haveria dados sigilosos. Na advocacia, a existência de informações sensíveis levou à consideração de modelos de embeddings locais para evitar o envio de documentos a APIs externas.

### Em que pontos foram iguais? Isso é sinal de boa prática geral ou de você ter repetido a decisão sem pensar?
Os dois projetos adotaram várias decisões semelhantes:
- documentos predominantemente em PDF convertidos para Markdown;
- utilização do Docling para extração;
- preservação da estrutura dos documentos;
- limpeza mínima para evitar perda de informação;
- preservação de tabelas e imagens quando relevantes;
- processamento incremental de documentos atualizados;
- utilização de metadados no nível do documento e do chunk;
- preservação do contexto durante o chunking;
- uso inicial do text-embedding-3-small.

Os projetos mostram que essas práticas gerais precisam ser adaptadas ao cenário. Isso aparece principalmente nos metadados: enquanto o e-commerce utiliza informações como nome_produto, categoria, marca e modelo, a advocacia utiliza area_direito, tribunal, numero_processo, versao e validade. Portanto, a arquitetura geral pode ser semelhante, mas os dados utilizados para recuperação e filtragem precisam refletir as necessidades específicas de cada domínio.

### Se você tivesse que construir apenas um dos dois, qual escolheria, e por quê?
Eu escolheria inicialmente o projeto de e-commerce, o principal motivo é que ele apresenta um cenário mais simples para desenvolver e validar uma primeira aplicação RAG.

Os documentos possuem informações relativamente objetivas, como características, especificações e manuais de produtos, e inicialmente não existem as mesmas preocupações com dados sigilosos existentes no cenário jurídico.
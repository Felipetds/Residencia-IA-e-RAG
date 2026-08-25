### Análise inicial para estruturação da base de dados:

Existem dados apropriados para consulta determinística/SQL e conteúdo apropriado para recuperação semântica/vetorial.

- SQL: dados estruturados em que a pergunta envolve filtro, comparação, contagem, soma, média, agrupamento ou ordenação.
- FAISS: documentos cujo objetivo é localizar informação por significado, contexto, procedimento, explicação ou relato.

## Structured

| Arquivo | Destino |
| --- | --- |
| customers.csv | SQL |
| employees.csv | SQL |
| products.json | SQL |
| sales.csv | SQL |
| stores.json | SQL |

## Semi-structured

| Arquivo | Destino |
| --- | --- |
| system_logs.csv | SQL |
| tickets.jsonl | SQL + FAISS |

## Unstructured

### E-mails

| Arquivo | Destino |
| --- | --- |
| customer_001_sincronizacao.txt | FAISS |
| customer_002_reembolso_cancelamento.txt | FAISS |
| customer_003_duvida_tef_firewall.txt | FAISS |
| customer_004_solicitacao_recurso_pix.txt | FAISS |
| customer_005_integracao_whatsapp.txt | FAISS |
| customer_006_duvida_inventario_cego.txt | FAISS |
| customer_007_solicitacao_segunda_via_fatura.txt | FAISS |
| customer_008_duvida_nfe_aliquota_icms.txt | FAISS |
| customer_009_problema_balanca_toledo.txt | FAISS |
| customer_010_solicitacao_treinamento_caixa.txt | FAISS |
| customer_011_erro_frete_correios_ecommerce.txt | FAISS |
| customer_012_duvida_plano_enterprise_migracao.txt | FAISS |
| customer_013_solicitacao_extrato_taxas_tef.txt | FAISS |
| customer_014_problema_cupom_nao_imprime.txt | FAISS |
| customer_015_duvida_relatorio_dre.txt | FAISS |
| customer_016_suporte_aplicativo_coletor.txt | FAISS |
| customer_017_cancelamento_plano_basic.txt | FAISS |
| customer_018_pedido_suporte_247_whatsapp.txt | FAISS |
| customer_019_problema_cupom_sat_sp.txt | FAISS |
| customer_020_integracao_shopee_mercado_livre.txt | FAISS |
| customer_021_solicitacao_novos_pinpads.txt | FAISS |
| customer_022_duvida_curva_abc_produtos.txt | FAISS |
| customer_023_erro_importacao_xml_fornecedor.txt | FAISS |
| customer_024_solicitacao_lgpd_exclusao_dados.txt | FAISS |
| customer_025_problema_gaveta_dinheiro.txt | FAISS |
| customer_026_elogio_atendimento_suporte.txt | FAISS |
| customer_027_envio_credenciais_acesso_admin.txt | FAISS* |
| customer_028_envio_senha_certificado_digital.txt | FAISS* |
| internal_001_alerta_seguranca_lgpd.txt | FAISS |
| internal_002_release_notes_v3_4.txt | FAISS |
| internal_003_manutencao_programada_servidores.txt | FAISS |
| internal_004_alinhamento_vendas_enterprise_q2.txt | FAISS |
| internal_005_treinamento_equipe_suporte_tef.txt | FAISS |
| internal_006_pesquisa_clima_organizacional.txt | FAISS |
| internal_007_auditoria_lgpd_logs_producao.txt | FAISS |
| internal_008_atualizacao_tabela_precos_2026.txt | FAISS |
| internal_009_beta_whatsapp_commerce_status.txt | FAISS |
| internal_010_politica_viagens_eventos_tech.txt | FAISS |
| internal_011_relatorio_churn_q1_pos_mortem.txt | FAISS |
| internal_012_homologacao_novas_maquininhas.txt | FAISS |
| internal_013_compartilhamento_chave_api_producao.txt | FAISS* |
| internal_014_envio_credenciais_banco_dados_prod.txt | FAISS* |
| internal_015_senha_root_servidores_tef.txt | FAISS* |

> **FAISS\***: sanitizar senhas, credenciais, chaves de API e outros segredos antes da vetorização.

### Reuniões / atas - Estratégia: MarkdownHeaderTextSplitter.

| Arquivo | Destino |
| --- | --- |
| 2026-01-architecture_review_db.md | FAISS |
| 2026-01-infrastructure_cost_optimization.md | FAISS |
| 2026-01-onboarding_process_review.md | FAISS |
| 2026-01-product_roadmap.md | FAISS |
| 2026-02-customer_success_retention_plan.md | FAISS |
| 2026-02-engineering_outage_retrospective.md | FAISS |
| 2026-02-inventory_collector_app_roadmap.md | FAISS |
| 2026-02-pdv_offline_contingency_test.md | FAISS |
| 2026-02-security_committee_lgpd.md | FAISS |
| 2026-02-support_operations_sync.md | FAISS |
| 2026-03-fiscal_sefaz_state_integrations.md | FAISS |
| 2026-03-hr_performance_review_q1.md | FAISS |
| 2026-03-incident_prevention_game_day.md | FAISS |
| 2026-03-omnichannel_checkout_analytics.md | FAISS |
| 2026-03-pay_features_brainstorm.md | FAISS |
| 2026-03-q1_results_exec_review.md | FAISS |
| 2026-03-sales_enterprise_feedback.md | FAISS |
| 2026-03-ux_ui_pdv_redesign.md | FAISS |

### Políticas - Estratégia: MarkdownHeaderTextSplitter.

| Arquivo | Destino |
| --- | --- |
| atendimento_sla.md | FAISS |
| beneficios_e_viagens.md | FAISS |
| codigo_de_conduta.md | FAISS |
| home_office.md | FAISS |
| reembolso.md | FAISS |
| reembolso.pdf | Não indexar se for duplicata do .md |
| seguranca_lgpd.md | FAISS |
| seguranca_lgpd.pdf | Não indexar se for duplicata do .md |

### Documentação - Estratégia: MarkdownHeaderTextSplitter.

| Arquivo | Destino |
| --- | --- |
| indicadores_vendas.md | FAISS |
| relatorios_financeiros.md | FAISS |
| frete_e_logistica.md | FAISS |
| integracao_catalogo.md | FAISS |
| importacao_nfe_xml.md | FAISS |
| inventario.md | FAISS |
| sincronizacao_estoque.md | FAISS |
| pix_dinamico_webhooks.md | FAISS |
| tef_e_maquininhas.md | FAISS |
| hardware_e_perifericos.md | FAISS |
| manual_pdv.md | FAISS |
| troca_e_devolucao.md | FAISS |

---------------------------------------------------------------------------------------------------------------

### Metadados

| Categoria | Arquivo / grupo | Destino principal | Metadados para RAG? |
|---|---|---|---|
| **Structured** | `customers.csv` | SQL | Não |
| **Structured** | `employees.csv` | SQL | Não |
| **Structured** | `products.json` | SQL | Não* |
| **Structured** | `sales.csv` | SQL | Não |
| **Structured** | `stores.json` | SQL | Não |
| **Semi-structured** | `system_logs.csv` | SQL | Não* |
| **Semi-structured** | `tickets.jsonl` | SQL + Vetorial | Sim |
| **Unstructured** | `emails/customer_*.txt` | Vetorial | Sim |
| **Unstructured** | `emails/internal_*.txt` | Vetorial | Sim |
| **Unstructured** | `meetings/*.md` | Vetorial | Sim |
| **Unstructured** | `policies/*.md` | Vetorial | Sim |
| **Unstructured** | `policies/*.pdf` | Vetorial | Sim |
| **Unstructured** | `documentation/analytics/*` | Vetorial | Sim |
| **Unstructured** | `documentation/ecommerce/*` | Vetorial | Sim |
| **Unstructured** | `documentation/estoque/*` | Vetorial | Sim |
| **Unstructured** | `documentation/pay/*` | Vetorial | Sim |
| **Unstructured** | `documentation/pdv/*` | Vetorial | Sim |

---------------------------------------------------------------------------------------------------------------

### Metadados

- Tickets — tickets.jsonl

Documento

```text
{
  "documento": {
    "documento_id": "ticket_001",
    "fonte": "tickets.jsonl",
    "caminho": "semi_structured/tickets.jsonl",
    "categoria": "semi_structured",
    "tipo_documento": "ticket",
    "dominio": "suporte",
    "formato": "jsonl",
    "ticket_id": "TKT-001",
    "cliente_id": "CUST-001",
    "data_documento": "2026-08-20",
    "status": "fechado",
    "prioridade": "alta",
    "assunto": "Problema de sincronização"
  },
```

Chunk

```text
  "chunk": {
    "chunk_id": "ticket_001_chunk_000",
    "documento_id": "ticket_001",
    "chunk_index": 0,
    "estrategia": "recursive",
    "chunk_size": 500,
    "chunk_overlap": 100,
    "n_caracteres": 432,
    "n_tokens": 108,
    "tipo_conteudo": "texto"
  }
}
```

- E-mails — emails/*.txt

Documento
```text
{
  "documento": {
    "documento_id": "email_001",
    "fonte": "customer_001_sincronizacao.txt",
    "caminho": "unstructured/emails/customer_001_sincronizacao.txt",
    "categoria": "unstructured",
    "tipo_documento": "email",
    "tipo_email": "customer",
    "dominio": "suporte",
    "formato": "txt",
    "remetente": "cliente",
    "destinatario": "suporte",
    "assunto": "Problema de sincronização",
    "data_documento": "2026-08-15",
    "cliente_id": "CUST-001"
  },
```
Chunk
```text
  "chunk": {
    "chunk_id": "email_001_chunk_000",
    "documento_id": "email_001",
    "chunk_index": 0,
    "estrategia": "recursive",
    "chunk_size": 500,
    "chunk_overlap": 100,
    "n_caracteres": 465,
    "n_tokens": 117,
    "tipo_conteudo": "texto"
  }
}

```
- Reuniões — meetings/*.md

Documento
```text
{
  "documento": {
    "documento_id": "meeting_001",
    "fonte": "reuniao_pdv.md",
    "caminho": "unstructured/meetings/reuniao_pdv.md",
    "categoria": "unstructured",
    "tipo_documento": "meeting",
    "dominio": "pdv",
    "formato": "md",
    "titulo": "Reunião sobre melhorias no PDV",
    "data_documento": "2026-08-10",
    "participantes": [
      "Produto",
      "Desenvolvimento",
      "Suporte"
    ]
  },
```

Chunk

```text
  "chunk": {
    "chunk_id": "meeting_001_chunk_000",
    "documento_id": "meeting_001",
    "chunk_index": 0,
    "secao": "Problemas identificados",
    "subsecao": null,
    "estrategia": "markdown_recursive",
    "chunk_size": 500,
    "chunk_overlap": 100,
    "n_caracteres": 487,
    "n_tokens": 121,
    "tipo_conteudo": "texto"
  }
}
```

4. Políticas — policies/*.md e policies/*.pdf

Documento
```text
{
  "documento": {
    "documento_id": "policy_001",
    "fonte": "politica_reembolso.pdf",
    "caminho": "unstructured/policies/politica_reembolso.pdf",
    "categoria": "unstructured",
    "tipo_documento": "policy",
    "dominio": "financeiro",
    "formato": "pdf",
    "titulo": "Política de Reembolso",
    "versao": "2.0",
    "data_documento": "2026-01-01",
    "data_vigencia": "2026-01-01",
    "status": "ativa",
    "area_responsavel": "Financeiro"
  },
```

Chunk
```text
  "chunk": {
    "chunk_id": "policy_001_chunk_003",
    "documento_id": "policy_001",
    "chunk_index": 3,
    "secao": "Reembolso",
    "subsecao": "Prazo",
    "pagina_inicio": 4,
    "pagina_fim": 4,
    "estrategia": "markdown_recursive",
    "chunk_size": 500,
    "chunk_overlap": 100,
    "n_caracteres": 451,
    "n_tokens": 113,
    "tipo_conteudo": "texto"
  }
}
```

5. Documentação — documentation/*

Documento
```text
{
  "documento": {
    "documento_id": "documentation_001",
    "fonte": "integracao_pix.md",
    "caminho": "unstructured/documentation/pay/integracao_pix.md",
    "categoria": "unstructured",
    "tipo_documento": "documentation",
    "dominio": "pay",
    "formato": "md",
    "titulo": "Integração PIX",
    "versao": "1.2",
    "data_documento": "2026-07-10"
  },
```

Chunk
```text
  "chunk": {
    "chunk_id": "documentation_001_chunk_005",
    "documento_id": "documentation_001",
    "chunk_index": 5,
    "secao": "Integração",
    "subsecao": "Autenticação",
    "estrategia": "markdown_recursive",
    "chunk_size": 500,
    "chunk_overlap": 100,
    "n_caracteres": 476,
    "n_tokens": 119,
    "tipo_conteudo": "texto"
  }
}
```
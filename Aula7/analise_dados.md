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

### Reuniões / atas

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

### Políticas

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

### Documentação

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
# Revisão de entrega e próximos gates

Revisão de 13/11/2026. Implementação e evidência de execução real em HML são distintas de aceite humano do conteúdo e de exposição externa. Relatório completo significa conclusão do fluxo técnico com suas limitações explícitas; não significa que indicadores populacionais ausentes foram calculados.

## Matriz do desafio

| Requisito | Evidência / situação |
|---|---|
| Base Open DATASUS SRAG | CSV histórico de 2019 fixado por hash; carga idempotente e 33 territórios confirmados em HML. Sem bases complementares, conforme decisão do usuário. |
| Taxa de aumento de casos | Crescimento dos últimos sete dias contra os sete anteriores; fonte, período e denominador explícitos. |
| Taxa de mortalidade | Letalidade entre desfechos conhecidos, com definição explícita. Mortalidade populacional não calculável no CSV exclusivo. Não declarar equivalência. |
| Taxa de ocupação de UTI | Ocupação operacional não calculável sem capacidade de leitos. Proporção de internação em UTI entre casos apresentada separadamente. |
| Taxa de vacinação da população | Cobertura populacional não calculável sem população-alvo e base de vacinação. Proporção de vacinação contra gripe entre casos apresentada separadamente. |
| Gráfico diário de trinta dias | Série real até 28/12/2019, por início dos sintomas; lacunas, zeros e supressões diferenciados. |
| Gráfico mensal de doze meses | Série histórica com mês final parcial identificado. |
| Agente consulta o banco | Três chamadas de ferramentas reais aceitas pela Groq; consultas SQL parametrizadas e reader sem escrita. |
| Notícias em tempo de geração | Até cinco títulos/resumos recentes, com fonte, URL e data; sem leitura integral. Separados do cenário histórico. |
| Relatório automatizado | HTML/JSON com números e gráficos determinísticos, narrativa validada e auditoria. Execução completa confirmada pelo operador em 12/11/2026. |
| Governança e transparência | Snapshot, carga, versões, fontes, eventos, hashes, tokens e rejeições. Sem log de raciocínio ou rascunhos rejeitados. |
| Guardrails | Ferramentas fechadas, escopo fixado, validação de saída e modo parcial. Rejeição e reparo observados na execução real. Não provam correção semântica de toda frase. |
| Dados sensíveis | Banco contém agregações, sem registros individuais; segredo fora do Git/frontend. Supressão primária não elimina inferência entre agregados sobrepostos: acesso restrito. |
| Clean Code e verificação | Módulos de ingestão, repositório, API, provedor, agente e relatório separados. Sessenta testes Python locais e testes de navegador documentados. |
| Repositório GitHub público | Código, documentação e exemplos sem chaves/CSVs. Relatórios de execução permanecem privados em HML. |
| Diagrama conceitual em PDF | Entregue em output/pdf/arquitetura-conceitual-srag.pdf, com duas páginas. Gerador versionado. |
| Acesso de homologação | Domínio escolhido: poc-srag.estacaolab.com.br. DNS, Caddy, autenticação e inspeção visual ainda pendentes de validação. |

## Inspeção humana do resultado existente

Usar o relatório 62a21130022b4e8296737c20a2de4972, sem gerar outro para revisão:

1. Abrir dashboard e relatório em acesso restrito. Conferir identidade, período e carga.
2. Verificar os dois gráficos, lacunas e mês parcial; conferir visualização em desktop e celular.
3. Ler a narrativa: consistência com os dados, limites dos indicadores, distinção entre notícias atuais e histórico, ausência de atribuição causal indevida.
4. Abrir as referências e conferir correspondência com títulos/fontes do relatório; a existência de um link não valida toda a interpretação do LLM.
5. Conferir mudanças de filtros no painel e a indicação de que relatório depende da seleção usada na geração. Trocar filtros não deve consumir quota automaticamente.
6. Registrar aceite ou problemas observados em aidlc-docs/progress.md. A inspeção ainda não foi executada no ambiente real pelo agente local.

## Acesso externo restrito

Consultar hml-caddy.md antes de alterar o proxy compartilhado. O nome escolhido não prova que o DNS aponta para a VM. Não expor 8766 ou PostgreSQL ao público. Manter o alias da API na rede Docker e autenticação para todo o site, inclusive endpoints de relatórios. Não liberar dados publicamente com base somente na supressão primária.

## Entrega final

PDF disponível e integração real aceita. Ainda faltam revisão humana/visual, apontamento DNS e proxy autenticado. Backup/retenção do volume e rollback precisam ser validados antes de produção. A entrega deve declarar honestamente os indicadores originais não calculáveis, sem substituí-los silenciosamente por proxies.

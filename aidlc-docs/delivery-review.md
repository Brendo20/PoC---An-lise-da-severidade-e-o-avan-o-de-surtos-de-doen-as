# Revisão de entrega e próximos gates

Revisão de 13/11/2026. Implementação e evidência de execução real em HML são distintas de aceite humano do conteúdo e de exposição externa. Relatório completo significa conclusão do fluxo técnico com suas limitações explícitas; não significa que indicadores populacionais ausentes foram calculados.

**Gate semântico concluído em 13/11:** o relatório antigo foi reprovado na leitura final; v7 implantada com histórico por regras e igualdade em schema/validação. Novo relatório d55a99bf5d54456e9c89442fcc25e9e6 completo, histórico conferido e narrativa legada retirada. Revisão pública em 360/1100px e leitura de consistência concluídas sem encontrar as extrapolações anteriores. Arquivos originais preservados.

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
| Dados sensíveis | Banco contém agregações, sem registros individuais; segredo fora do Git/frontend. Acesso público autorizado pelo usuário; supressão primária não elimina inferência entre agregados sobrepostos. |
| Clean Code e verificação | Módulos separados, 63 testes Python locais e testes de navegador documentados. Regressões semânticas adicionadas após a leitura do relatório real. |
| Repositório GitHub público | Código, documentação e exemplos sem chaves/CSVs. Arquivos do volume internos; relatórios acessíveis por endpoints públicos. |
| Diagrama conceitual em PDF | Entregue em output/pdf/arquitetura-conceitual-srag.pdf, com duas páginas. Gerador versionado. |
| Acesso de homologação | poc-srag.estacaolab.com.br com HTTPS público e HTTP 200 confirmados. Sem senha por decisão do usuário. Revisão visual de acesso, filtros e gráficos passou em 360/1100px. |

## Inspeção humana do resultado existente

O relatório 62a21130022b4e8296737c20a2de4972 foi reprovado e sua narrativa foi retirada. O aceite final usa d55a99bf5d54456e9c89442fcc25e9e6, após implantação da v7. Roteiro aplicado na revisão:

1. Abrir dashboard e relatório pelo domínio público. Conferir identidade, período e carga.
2. Verificar os dois gráficos, lacunas e mês parcial; conferir visualização em desktop e celular.
3. Ler a narrativa: consistência com os dados, limites dos indicadores, distinção entre notícias atuais e histórico, ausência de atribuição causal indevida.
4. Abrir as referências e conferir correspondência com títulos/fontes do relatório; a existência de um link não valida toda a interpretação do LLM.
5. Conferir mudanças de filtros no painel e a indicação de que relatório depende da seleção usada na geração. Trocar filtros não deve consumir quota automaticamente.
6. Registrar aceite ou problemas observados em aidlc-docs/progress.md. Primeira revisão encontrou a falha; a revisão posterior do resultado v7 confirmou a correção histórica no exemplo final.

## Acesso externo público

Consultar hml-caddy.md antes de alterar o proxy compartilhado. O nome escolhido não prova que o DNS aponta para a VM. Não expor 8766 ou PostgreSQL ao público. Manter o alias da API na rede Docker e autenticação para todo o site, inclusive endpoints de relatórios. Não liberar dados publicamente com base somente na supressão primária.

Atualização: DNS e HTTPS confirmados, sem autenticação por decisão posterior do usuário. O parágrafo acima registra a recomendação inicial. Não presumir que autorização de publicação resolve todos os riscos de privacidade. Não reconstruir o proxy para atualizar a aplicação.

## Entrega final

PDF e texto de envio disponíveis; DNS/HTTPS públicos aceitos; v7 implantada e revisada. Material pronto para envio, sem promessa de atendimento numérico aos indicadores não calculáveis. Backup/retenção do volume, controle de acesso e rollback exigem trabalho adicional antes de produção. A entrega deve declarar os limites sem substituir indicadores silenciosamente por proxies.

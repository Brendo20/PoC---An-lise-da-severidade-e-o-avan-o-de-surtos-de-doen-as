# Requisitos e decisões de escopo

Estado atualizado em 13/11/2026: o usuário escolheu exclusivamente o CSV SRAG 2019 e apresentação explícita dos indicadores não calculáveis. Integração real PostgreSQL/Groq/notícias/relatório aceita em HML em 12/11/2026; PDF conceitual entregue. Matriz atual em delivery-review.md. Limites das métricas originais não foram apagados por esse aceite técnico.

## Objetivo
Entregar repositório público reproduzível, dashboard, relatório gerado por agente com consulta de métricas e notícias, dois gráficos e PDF de arquitetura. Prioridades: precisão, governança, guardrails, minimização de dados e clean code.

## Escopo temporal
Base principal: arquivo histórico de 2019 indicado no desafio. Referência validada: 28/12/2019, máximo observado de DT_SIN_PRI. Datas de download, carga, geração do relatório e referência analítica são informações distintas.

Gráfico diário: 30 datas corridas até a referência, inclusive. Gráfico mensal: 12 meses de calendário até o mês da referência; mês final parcial deve ser identificado. Dias sem casos são zero somente dentro de uma janela com cobertura conhecida; falta de cobertura não equivale a zero.

Notícias atuais ficam em seção explicitamente contemporânea, sem atribuir causalidade aos dados de 2019. A análise histórica é descritiva e usa os dados do recorte; não afirmar causas históricas não estabelecidas. Sem notícias válidas, exibir indisponibilidade, sem inventar explicações.

## Contrato de métricas no escopo aprovado
1. Crescimento: (casos nos últimos 7 dias / casos nos 7 anteriores - 1) × 100, por início dos sintomas e mesmos filtros. Denominador zero produz indisponível.
2. Letalidade observada entre desfechos conhecidos: EVOLUCAO=2 / EVOLUCAO em {1,2,3} × 100. Exibir denominador e percentual de desfechos ausentes/ignorados. Não chamar de mortalidade populacional; não declarar equivalência com esse requisito.
3. Ocupação UTI: indisponível até obter leitos ocupados e disponíveis compatíveis com território e período. Indicador auxiliar separado: UTI=1 / UTI em {1,2} × 100, explicitamente proporção de internação em UTI.
4. Cobertura vacinal populacional: não calculável no CSV exclusivo. Indicador auxiliar separado: VACINA=1 / VACINA em {1,2} × 100, vacinação contra gripe na última campanha, confirmada na investigação do dicionário. Não mede cobertura ou eficácia.

Não considerar requisitos de ocupação, mortalidade populacional ou vacinação populacional atendidos por indicadores substitutos. O usuário recusou fontes complementares nesta PoC; entregar as limitações explicitamente, sem ampliar a coleta nem ocultar a divergência de definição.

## Unidades de trabalho
- U1: qualidade, minimização e diagnóstico do CSV.
- U2: agregação, contrato de métricas, séries e dashboard (U2-U4-real-data.md e stage-1-dashboard.md).
- U3: persistência e ferramentas PostgreSQL (U3-database-tools.md).
- U4: API de leitura e interface integrada (U4-postgres-api.md).
- U5: agente, notícias, relatório e auditoria (U5-agent-reports.md).
- Entrega: PDF, revisão, acesso restrito de HML e matriz do desafio (delivery-review.md). Produção ainda não implantada.

## Critérios de aceite
- Métricas e gráficos conciliam com consultas determinísticas em dados conhecidos.
- Números do relatório correspondem aos resultados das ferramentas.
- Indicadores exibem fórmula, período, território, denominador, fonte e limitações.
- Ausências, códigos ignorados, denominadores zero e períodos incompletos são tratados explicitamente.
- Agente não recebe identificadores ou registros individuais e não executa SQL arbitrário.
- Notícias têm URL, data de publicação quando disponível e horário de consulta; conteúdo externo não pode alterar instruções ou acionar ferramentas.
- Execução registra carga, filtros, versões, ferramentas, erros, duração e validações; sem raciocínio interno ou segredos.
- Falhas externas produzem resposta controlada, sem valores inventados.
- Repositório contém instruções de execução, testes relevantes, .env.example sem segredos e PDF conceitual da arquitetura.
- Deploy é validado em HML, com backup, health checks e rollback antes de PROD.

## Próximas decisões
Decisão de 11/11/2026: uso exclusivo de SRAG 2019 e apresentação explícita dos indicadores não calculáveis. Não integrar bases mais recentes/complementares sem nova solicitação. Inventário e integração real de HML confirmados pelo operador; não presumir implantação em produção. Próximos gates: revisão humana/visual e acesso restrito via DNS/Caddy, com subdomínio poc-srag.estacaolab.com.br informado em 13/11/2026.

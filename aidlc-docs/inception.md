# Inception — proposta inicial

## Objetivo
Entregar repositório público reproduzível, dashboard, relatório gerado por agente com consulta de métricas e notícias, dois gráficos e PDF de arquitetura. Prioridades: precisão, governança, guardrails, minimização de dados e clean code.

## Escopo temporal
Base principal: arquivo histórico de 2019 indicado no desafio. Data de referência proposta: 28/12/2019, máximo observado de DT_SIN_PRI, sujeito à validação. Datas de download, carga, geração do relatório e referência analítica são informações distintas.

Gráfico diário: 30 datas corridas até a referência, inclusive. Gráfico mensal: 12 meses de calendário até o mês da referência; mês final parcial deve ser identificado. Dias sem casos são zero somente dentro de uma janela com cobertura conhecida; falta de cobertura não equivale a zero.

Notícias atuais serão uma seção explicitamente contemporânea, sem atribuir causalidade aos dados de 2019. Para explicar o período histórico, buscar fontes históricas compatíveis e citadas. Sem notícias válidas, exibir indisponibilidade, sem inventar explicações.

## Contrato proposto de métricas
1. Crescimento: (casos nos últimos 7 dias / casos nos 7 anteriores - 1) × 100, por início dos sintomas e mesmos filtros. Denominador zero produz indisponível.
2. Letalidade observada entre desfechos conhecidos: EVOLUCAO=2 / EVOLUCAO em {1,2,3} × 100. Óbitos por outras causas são separados. Exibir denominador e percentual de desfechos ausentes/ignorados. Não chamar de mortalidade populacional. Essa definição é proposta, não substituição aprovada do requisito.
3. Ocupação UTI: indisponível até obter leitos ocupados e disponíveis compatíveis com território e período. Indicador auxiliar separado: UTI=1 / UTI em {1,2} × 100, explicitamente proporção de internação em UTI.
4. Cobertura vacinal populacional: indisponível até obter fonte complementar, vacina, esquema, período e população-alvo. Indicador auxiliar separado: VACINA=1 / VACINA em {1,2} × 100, após confirmar definição da vacina e compatibilidade histórica no dicionário.

Não considerar requisitos de ocupação, mortalidade populacional ou vacinação populacional atendidos por indicadores substitutos. Fontes complementares e tratamento da ambiguidade do enunciado são pendências obrigatórias antes do aceite final.

## Unidades de trabalho
- U1: ingestão reproduzível e qualidade, incluindo hashes e manifestos.
- U2: contrato das métricas, fontes complementares, SQL parametrizado e séries.
- U3: orquestrador, ferramentas tipadas, notícias, validação e auditoria.
- U4: interface, filtros, gráficos, relatórios e transparência da carga.
- U5: implantação HML/PROD, documentação, PDF, avaliação e entrega GitHub.

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
Decisão posterior em 11/11/2026: usuário confirmou uso exclusivo de SRAG 2019 e apresentação explícita dos indicadores não calculáveis. Não pesquisar ou integrar bases mais recentes ou fontes complementares sem nova solicitação. Próximos passos: persistência PostgreSQL, agente, notícias atuais separadas do cenário histórico, relatório com dois gráficos e implantação validada. Inspeção de capacidade real da VM permanece pendente. Nenhuma aprovação de deploy ou conclusão da PoC é presumida.

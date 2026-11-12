# Registro AI-DLC

## 12/11/2026 — U5 construída; gate de integração real pendente
- Entrada: API em HML validada com 33 territórios, 48.866 casos e carga efetiva; Groq autenticada e modelo disponível após inclusão de User-Agent. Usuário autorizou continuar.
- Construção: agente com três ferramentas fechadas, snapshot/territórios fixados, cliente Groq sem SDK, busca RSS, narrativa estruturada, relatório HTML/JSON com dois gráficos e volume de auditoria. Registro da escolha arquitetural em ADR-004.
- Guardrails: sem SQL/URLs definidos pelo modelo; números determinísticos; validação de schema, tendências/referências e restrições de narrativa; limites de rodadas, contexto, simultaneidade e intervalo; modo parcial preserva dados em falha de quota. Não há prova semântica completa do texto.
- Interface: geração explícita, seleção principal/comparação aplicada, resultados antigos ocultados e respostas em andamento descartadas quando o recorte muda. Prévia estática não usa chave nem habilita agente.
- Validação local: 50 testes Python passaram. Browser com dublês passou geração, comparação, snapshot, dois gráficos, parcial, troca de filtro em andamento e 320px sem overflow; regressão de 47 cenários de filtros, tooltips, API e smoke passou, sem erros JavaScript. HTML do relatório e painel inspecionados visualmente. Sintaxe JavaScript e Compose com conexão fictícia validados. Evidências locais ignoradas pelo Git.
- Consulta real aos feeds retornou cinco notícias recentes, sem erro de fonte. Groq e PostgreSQL não foram chamados nos testes locais do agente. A primeira geração real será validada pelo operador via check_agent_hml.py após rebuild ARM64.
- Pendências: aceite da geração real em HML, diagrama conceitual em PDF e revisão final de entrega. Caddy e acesso externo não foram alterados.

## 12/11/2026 — API de leitura e frontend integrado preparados
- Entrada: operador confirmou carga idempotente e permissões reader SELECT=true, INSERT/UPDATE/DELETE=false. Métricas do banco real correspondem ao CSV. Usuário autorizou avançar.
- Implementados FastAPI/Uvicorn, consulta única de dashboard por snapshot, endpoints de métricas/séries e healthchecks. SQL parametrizado, leitura com timeout e erros sanitizados.
- Frontend servido pela API consulta /api/dashboard e mostra loaded_at efetivo; falha não aciona fallback para arquivo local. Prévia estática permanece em modo local explícito.
- Dockerfile.api e Compose HML: apenas conexão reader, 256 MiB, 0,5 CPU, sem root, filesystem somente leitura, logs limitados, healthcheck; porta vinculada a 127.0.0.1:8766 e rede portais-net existente. Nenhuma configuração do Caddy alterada.
- Validação local: 32 testes Python, sintaxe JavaScript e Compose com DSN fictício passaram. Testes HTTP com repositório controlado, sem acesso ao banco da VM.
- Navegador em modo API com fixture em memória: data de carga, bloqueio de snapshot local, falha sem fallback, 47 cenários de filtros, tooltips e smoke test passaram. Zero erros JavaScript. Prévia visual inspecionada; servidor de fixture encerrado.
- Evidências locais ignoradas pelo Git: reports/frontend-api.json, reports/frontend-filters.json, reports/frontend-tooltips.json e reports/frontend-smoke.json. Não constituem teste de API contra PostgreSQL real.
- Próximo gate: operador executar build ARM64 e validar serviço HTTP com PostgreSQL em HML. Agente LLM e notícias continuam pendentes.

## 12/11/2026 — Migração HML confirmada pelo operador
- Operador confirmou .env com modo 600 e ignorado pelo Git, migração 001 aplicada no banco exclusivo e zero snapshots.
- Preparado Dockerfile.tools com contexto de build em allowlist, downloader com hash fixado e runbook de carga inicial.
- Próximo passo operacional: build ARM64, download verificado, agregação e carga/consulta no PostgreSQL. Nenhuma execução dessas etapas na VM foi presumida.

## 12/11/2026 — Preparação da primeira versão Git
- Usuário forneceu o repositório GitHub de destino: Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as.
- Consulta remota confirmou ausência de branches; diretório local ainda não tinha Git.
- Revisão de versionamento: fontes, testes, documentação e assets geográficos/gráficos; CSVs, snapshots, relatórios de execução, credenciais e capturas locais excluídos.
- Adicionada validação GitHub Actions com testes sintéticos Python e verificação de sintaxe JavaScript, sem dataset real ou credenciais.
- Preparação de commit inicial; envio e validação remota serão verificados separadamente. Nenhuma alteração na VM Oracle.

## 11/11/2026 — Legibilidade e tooltips dos gráficos
- Título alterado para o texto solicitado: PoC - Análise da severidade e o avanço de surtos de doenças.
- Títulos dos quatro cards em negrito.
- Crescimento sem casos no período anterior agora mostra "Sem casos", com explicação de que a base de comparação é zero. Valores suprimidos mostram "Suprimido", sem confundir ausência de divulgação com zero.
- Gráficos diário/mensal apresentam tooltip por período com os territórios selecionados; mostram contagens, zeros, supressões e mês parcial. Interação por mouse, toque e teclado, com setas/Home/End e Escape; tabelas continuam disponíveis.
- Teste frontend-tooltips passou, incluindo comparação, supressão, rótulos, cabeçalho, negrito e tooltip em 320px sem overflow. Os 47 cenários globais de filtros e o smoke test também passaram, sem erros JavaScript.
- Prévia visual inspecionada. Nenhuma fórmula, dado de origem ou infraestrutura foi alterado.

## 11/11/2026 — Etapa 1 do dashboard concluída
- Solicitação: aplicar achados da investigação e garantir que mapas/menus filtrem todo o dashboard.
- Cards adicionados: internação em UTI entre casos com informação e vacinação contra gripe entre casos com informação. Nomes, fórmulas, denominadores e incompletude explícitos; sem equivalência com ocupação operacional/cobertura populacional.
- Centralizadas transições dos filtros e renderização; auditoria por território agora acompanha as seleções. Totais fixos da origem identificados como tais.
- Mapa com destino explícito principal/comparação. Sem comparação consigo mesmo; adicionar/remover, troca de nível e reset coerentes.
- Ferramenta de métricas preparada para PostgreSQL passou a incluir os dois indicadores observáveis, mantendo separados os indicadores literais não calculáveis.
- Validação: 19 testes Python, sintaxe JavaScript e dois testes de navegador passaram. Teste novo cobriu 47 seleções sincronizadas, todas as 27 UFs e cinco regiões, superfícies do dashboard e larguras 320/360/768/1100px. Zero erros JavaScript. Smoke test confirmou ausência de requisições externas.
- Prévias desktop e mobile inspecionadas; encerramento documentado em aidlc-docs/units/stage-1-dashboard.md.
- Nenhuma alteração na VM ou banco; agente, notícias e relatório final continuam na próxima etapa.

## 11/11/2026 — Reinvestigação de UTI e vacinação
- Usuário pediu nova investigação aprofundada, questionando a impossibilidade de responder aos indicadores.
- Auditados todos os campos do CSV, categorias, cruzamento com hospitalização, datas de UTI, vacinação geral/materna/pediátrica e definições do dicionário/ficha.
- Conclusão: medidas observáveis existem (internação em UTI e vacinação entre casos); não equivalem às taxas literais de ocupação operacional e cobertura populacional. A interface não deve sugerir que não há informação útil nessas áreas.
- Criados src/srag/investigate.py e aidlc-docs/uti-vaccination-investigation.md, com fórmulas, contagens nos dois recortes e limitações.
- Não alterados nomes, fórmulas ou indicadores da interface nesta investigação; proposta de apresentação adicional depende da revisão do resultado com o usuário.

## 11/11/2026 — Escopo exclusivo de 2019 e persistência PostgreSQL
- O usuário confirmou que a base da PoC é 2019 e escolheu explicitamente: "Usar exclusivamente o CSV e explicitar os indicadores não calculáveis".
- Pesquisa de bases recentes foi encerrada; nenhuma base nova foi incorporada.
- Relatório deve incluir os quatro indicadores solicitados, com valor não calculável e justificativa quando a base não suportar o cálculo. Letalidade é indicador adicional corretamente nomeado, não mortalidade populacional.
- Interface ajustada para refletir a decisão, sem prometer fontes complementares.
- Criados sql/001_aggregate_store.sql, camada srag.database, extra opcional psycopg e .env.example sem credenciais.
- Repositório armazena somente agregações versionadas; snapshots imutáveis por conteúdo, carga transacional, promoção atômica e data efetiva de carga do banco. Ferramentas têm SQL fixo, parâmetros, allowlist e transações de leitura com timeout.
- Detectado serviço PostgreSQL 17 local em execução, sem conexão do projeto configurada. Não houve migração, criação de banco, acesso aos dados existentes ou alteração na Oracle.
- Validação: 19 testes Python passaram; sete testes novos da camada de banco usam conexão controlada e não substituem integração PostgreSQL.
- Pendências imediatas: configurar conexões exclusivas, testar migração e carga reais, integrar notícias e LLM, gerar relatório com os dois gráficos e auditoria. A documentação OpenAI foi consultada para planejar a integração, mas nenhuma chamada de LLM foi realizada.

## 10/11/2026 — Design aprovado e frontend com dados reais
- Entrada do usuário: aprovação visual ("ficou excelente") e autorização para continuar.
- Gate: direção visual aprovada; contrato epidemiológico e fontes complementares continuam com pendências.
- Construção: src/srag/aggregate.py gera agregações por Brasil, UF de residência e região; frontend estático em frontend/ usa snapshot e malha locais. Protótipo ilustrativo preservado.
- Manifesto inclui hash da origem, parâmetros, versões, data de geração e status explícito de ausência de carga SQL. Identidade do snapshot inclui cobertura e regras de supressão.
- Validação: 12 testes Python passaram. Sintaxe JavaScript validada. Conciliação independente do CSV confirmou Brasil 48.866 casos no recorte, SP 12.312, MG 4.021 e séries nacionais diária/mensal.
- Brasil: 5.414 óbitos por SRAG entre 44.615 desfechos conhecidos (12,1349%); 4.251 sem desfecho conhecido (8,6993%). Crescimento: 360 casos nos últimos 7 dias versus 408 nos anteriores, -11,7647%.
- 37 registros sem UF reconhecida na base foram preservados no total nacional. O Brasil pode divergir da soma dos territórios com localização conhecida.
- Navegador Edge: mapa com 27 UFs, SP × MG, Norte × Sudeste, clique, reset, resumo atualizado, supressão e erro HTTP de snapshot. Zero erros JavaScript e zero requisições externas em runtime.
- Responsividade: 320/360/768/1100px sem overflow horizontal. Prévias desktop e mobile inspecionadas visualmente.
- Evidências locais: reports/frontend-smoke.json, reports/snapshot-real-v1.json, frontend/preview-desktop.png e frontend/preview-mobile.png; ignoradas pelo Git.
- Implementação disponível para validação local. Nenhum deploy, carga PostgreSQL, agente LLM ou busca de notícias foi realizado.
- Próxima unidade: persistência e ferramentas de consulta no PostgreSQL, após inventário de acesso/ambiente. Revisão de privacidade e fontes complementares continuam necessárias antes da publicação.

## 10/11/2026 — Design de experiência v0.1
- Usuário pediu interface clean e escaneável, mapa interativo e comparação entre estados e regiões.
- Criado protótipo navegável em design/srag-wireframe.html, sem backend ou deploy.
- Geometria oficial IBGE: 27 UFs; orientação dos anéis ajustada à projeção esférica d3 após teste identificar sobreposição indevida.
- Dados de demonstração explicitamente identificados; não usar como análise epidemiológica.
- Validação em Edge headless: SP × MG, Norte × Sudeste (7 e 4 UFs), clique no mapa, remoção de comparação, prévia do relatório e largura de 360px sem overflow; zero erros JavaScript.
- Prévia desktop e mobile inspecionada visualmente. Ajustado contraste do botão principal no hover.
- Naquele momento, aprovação visual pendente; aprovação posterior e integração real registradas acima. Municípios continuam pendentes.
- Teste reproduzível: design/verify.cjs, com Playwright instalado e canal msedge disponível.

## 10/11/2026 — Inception e Construction de U1
- Intenção: continuar o projeto seguindo AI-DLC, conforme solicitação do usuário.
- Evidência: CSV histórico exigido, documentação fornecida e diagnóstico integral inicial.
- Decisão: avançar no profiler reproduzível sem presumir conclusão da Inception global.
- Artefatos: contrato de métricas v0.1, desenho U1, código e testes de qualidade.
- Pendências: fontes complementares históricas, revisão de cobertura e capacidade real de HML/PROD.
- Nenhuma alteração em VM, banco ou publicação foi realizada.

## Validação de U1 — 10/11/2026
- Seis testes automatizados passaram, cobrindo qualidade, privacidade e reprodutibilidade.
- Primeira execução real revelou timestamps ISO com Z, não cobertos inicialmente. Parser e teste foram corrigidos; nova execução passou.
- CSV real: 48.941 registros, 194 colunas e zero linhas estruturalmente malformadas. Contagens de categorias conciliadas com o total de registros.
- SHA-256: f6de547c1234e2de4d65f830606849a006346e50b32106bd635714665100134a.
- Referência candidata: 28/12/2019; 1 internação futura, 1 internação antes dos sintomas, 24 entradas UTI antes dos sintomas, 178 casos UTI sem entrada válida e 7.639 sem saída válida.
- Evidência local: reports/data-profile-2019.json (ignorada pelo Git). Resumo agregado e hash permanecem versionáveis neste documento.
- U1 parcialmente construída; ingestão PostgreSQL e seus testes de integração continuam pendentes. Inception global aberta para fontes e ambiguidades das métricas.

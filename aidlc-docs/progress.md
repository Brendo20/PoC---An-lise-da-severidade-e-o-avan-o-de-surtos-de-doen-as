# Registro AI-DLC

## 13/11/2026 - Preparação de envio e falha semântica encontrada na revisão final
- Operador confirmou Caddy 2.11.7, DNS correto e HTTPS 200 em 163.176.51.25. Publicação sem senha foi solicitada explicitamente; documentação/modelo atualizados para acesso público, mantendo portas internas e limites existentes. Nenhuma autenticação reintroduzida.
- Revisão local do site real via navegador somente leitura passou: 360/1100px, 48.866 casos, SP x MG, dois gráficos, três caminhos privados com 404 e zero erros JavaScript. Nenhuma geração LLM disparada. Evidências locais ignoradas pelo Git.
- Leitura do relatório antigo encontrou afirmações não demonstradas: estabilidade de percentuais e impacto vacinal. O aceite técnico anterior não validou essas frases. Gate semântico reaberto, com limitação comunicada ao usuário antes do envio.
- Implementada v7-grounded-history: histórico por regras, enum no schema, igualdade local e evento de conferência. Notícias continuam com comentário LLM atribuído aos títulos/resumos. Relatórios legados incompatíveis têm análise retirada na projeção pública; arquivos originais preservados para auditoria.
- 63 testes Python passaram, incluindo regressões da extrapolação, schema, tendências e imutabilidade de legado. PDF atualizado e renderizado com acesso público e estado real de revisão. Pacote e texto de envio em SUBMISSION.md, marcados para uso após aceite v7 em HML. Nenhum envio ao avaliador realizado.
- Próximo gate: rebuild somente da API, geração real v7, leitura do novo resultado e conferência da retirada da narrativa antiga. Não declarar entrega final pronta antes desse gate.

## 13/11/2026 — PDF conceitual entregue e acesso externo preparado
- Usuário autorizou continuar. Gerado output/pdf/arquitetura-conceitual-srag.pdf, duas páginas: orquestrador, ferramentas, LLM, PostgreSQL, notícias, fluxo de carga, auditoria, guardrails e limites. Fonte reproduzível build_architecture_pdf.py; sem novas dependências de runtime da API.
- PDF renderizado com Poppler e inspecionado visualmente; layout de setas ajustado para não atravessar blocos. Extração confirmou duas páginas com texto selecionável. Imagens intermediárias em tmp/pdfs, fora do Git.
- README vincula PDF e matriz do desafio em delivery-review.md. Inception atualizado para refletir o escopo exclusivo do CSV e a sequência real das unidades; histórico de decisões permanece neste registro. Indicadores não calculáveis continuam explícitos, sem alegação de atendimento por proxies.
- Usuário escolheu poc-srag.estacaolab.com.br e informou IP público HML 163.176.51.25. Consulta DNS retornou 216.198.79.65 e 64.29.17.1; apontamento divergente, ajuste de DNS ainda não confirmado.
- Preparados runbook e modelo de site Caddy com autenticação por hash, todos os caminhos protegidos e proxy pelo alias interno. Não aplicados na VM; versão, mounts, DNS, certificado e acesso autenticado ainda pendentes de preflight. Nenhum segredo versionado e nenhum host existente alterado.
- Próximo gate: usuário executar preflight e corrigir DNS; inspecionar dashboard e relatório existente em acesso restrito, sem gerar nova chamada LLM só para revisão.

## 12/11/2026 — Aceite de integração real U5 confirmado em HML
- Evidência do operador: rebuild ARM64 e container saudável; check_agent_hml.py retornou complete, narrativa_validada=true, três rodadas de ferramentas, cinco notícias, avisos vazios e erros_provedor vazios. Relatório 62a21130022b4e8296737c20a2de4972, modelo openai/gpt-oss-20b, prompt srag-2019-v5-targeted-repair.
- Snapshot srag-ec77679e6022ca66-2019-12-28-v1.0.0 e carga 2026-11-12T12:45:32.573171+00:00. O script verifica métricas iguais ao dashboard, séries de trinta dias/doze meses e dois gráficos SVG. Nenhuma chamada real à VM foi feita pelo ambiente local; resultado fornecido pelo operador.
- Auditoria com dezoito eventos. Primeira tentativa rejeitada por narrative_numbers em current_commentary; reparo único aprovado. Guardrail operou antes da publicação da narrativa. Não representa ausência de variação futura, quotas ou garantia semântica integral.
- Gate de integração real de U5 atendido para essa execução. Relatório HTML/JSON e auditoria permanecem no volume privado. Próximos gates: inspeção humana e visual em HML, diagrama conceitual PDF, revisão final de entrega e acesso externo restrito antes de qualquer rota pública.

## 12/11/2026 — Experimento de pattern rejeitado; diagnóstico de trechos
- Operador executou sondagem sobre relatório existente, sem rebuild. Groq retornou HTTP 400/json_validate_failed; não prova suporte ou aderência ao pattern. Nenhum relatório foi promovido. Retirado pattern do schema implantável e mantida versão v5 do prompt, que é a imagem em execução confirmada.
- Sondagem recebeu --inspect-numbers: uma chamada de redação sem pattern, com até cinco trechos numéricos limitados por comentário. Não expõe chave ou campo de raciocínio, não repete ferramentas nem grava rascunho. Necessário distinguir nomes/datas/referências de afirmações quantitativas antes de mudar a política; nenhum trecho ainda observado.
- 60 testes Python passaram, incluindo limites dos trechos e ocultação de credenciais. Gate de narrativa continua aberto. Próxima execução é somente diagnóstico, sem rebuild.

## 12/11/2026 — Rejeição localizada em números do comentário atual
- Operador confirmou v5, três ferramentas concluídas e nenhum erro de provedor. As duas tentativas de redação foram rejeitadas por narrative_numbers em current_commentary no relatório 07c95c16a460495f80819ad8a9c18acd. Não é possível determinar o número ou trecho exato, pois o rascunho não foi persistido.
- v6 adiciona pattern sem algarismos/percentuais/marcação apenas aos dois campos de comentário, mantendo validação local e referências em campo separado. Não remove texto numerado após geração nem aceita uma saída reprovada.
- Preparada sondagem por stdin com uma única chamada de redação e evidências salvas, sem rebuild ou repetição das ferramentas. Não altera o relatório original. Compatibilidade/aderência real do schema e geração completa continuam pendentes.
- 58 testes Python passaram, incluindo padrão de comentários e preservação de IDs/regras de tendências. Regex local não comprova suporte ou aderência do provedor; sondagem real é necessária antes do deploy desta revisão.

## 12/11/2026 — Resposta real recebida; rejeição textual exige diagnóstico específico
- Operador confirmou v4 com três ferramentas concluídas e nenhuma falha HTTP; relatório parcial bdf99fa78e234811999902f412a262e7 ficou sem narrativa. Diagnóstico apenas de redação com evidências salvas retornou unverified_narrative_claim.
- O código anterior agrupava números, marcação, credenciais, termos de eficácia e causalidade. Não permite determinar retroativamente a categoria específica. Separados códigos e campo do comentário; mantidos os mesmos padrões de bloqueio, inclusive em negações.
- Prompt explicita restrições de linguagem; reparo único recebe JSON rejeitado e orientação específica em memória. Rascunho não é salvo em relatório/auditoria. Diagnóstico HML passa a imprimir rejeicoes_narrativa. Nenhuma validação foi desligada para aceitar a resposta.
- 57 testes Python passaram, incluindo categorias, negativos ainda bloqueados, correção direcionada, orçamento de tentativas, descarte de rascunhos rejeitados e sanitização de erros desconhecidos. Gate de geração real com narrativa continua pendente na VM.

## 12/11/2026 — Três ferramentas aceitas em HML; quota bloqueou redação
- Operador confirmou prompt v3 e três rodadas de ferramentas concluídas na Groq. Relatório parcial 8d9858acbed44c3182153e7d6d8ee2f8 preservou carga, métricas, séries e cinco notícias. Na etapa llm_unavailable, HTTP 429/rate_limit_exceeded impediu narrativa. Gate de ferramentas reais validado; gate de narrativa permanece aberto.
- Não é possível concluir qual janela de quota foi atingida a partir do registro anterior. Reduzido contexto das coletas independentes e orçamento máximo de saída de 1.800 para 512 por chamada de ferramenta. Redação recebe métricas e notícias compactas; gráficos e séries completos continuam no relatório.
- Diagnóstico passa a preservar Retry-After numérico válido em segundos. Sem retries automáticos, troca de conta ou promessa de quota gratuita disponível. Consultar limites da organização no Console da Groq quando necessário.
- 54 testes Python passaram, cobrindo tamanho de contexto por fase, evidências preservadas, orçamento de ferramentas e Retry-After sanitizado. Nova geração real com narrativa ainda pendente após atualização e disponibilidade de quota.

## 12/11/2026 — HTTP 400/tool_use_failed confirmado; revisão das fases
- Operador confirmou rebuild saudável e nova falha tool_use_failed na primeira rodada com paralelismo desativado. Correção anterior não resolveu a integração; nenhuma narrativa foi aceita. Dados e cinco notícias preservados no relatório parcial.
- Separados prompts de coleta e redação. O orquestrador prescreve a sequência obrigatória de três ferramentas e oferece uma por requisição, com tool_choice nomeado; valida nome oferecido e argumentos vazios antes de executar. Isso substitui seleção livre da ordem pelo modelo e foi registrado na arquitetura.
- Redação inicia conversa nova com métricas, séries e notícias coletadas, sem histórico de function calls ou comando para usar ferramentas. Limites, supressões e validações de narrativa permanecem aplicados. Sem retentativa automática ou desligamento da validação de ferramentas.
- Validação local: 53 testes Python passaram, incluindo três etapas e isolamento do contexto final, tool_choice explícito e rejeição de configuração ambígua. Diagnóstico HML passa a informar versão do prompt e rodadas concluídas. Sucesso real da Groq ainda não confirmado; não atribuir o erro a uma causa textual específica sem evidência.

## 12/11/2026 — Correção de compatibilidade Groq após falha em HML
- Evidência do operador: duas gerações completas tentadas resultaram em relatório parcial, cinco notícias e 12 eventos, sem narrativa. Diagnóstico isolado da primeira chamada teve sucesso com uma ferramenta; não comprova estabilidade do fluxo inteiro.
- Revisão da documentação oficial identificou incompatibilidade: GPT-OSS não suporta ferramentas paralelas, mas o cliente habilitava parallel_tool_calls=true e o prompt incentivava mesma rodada. Corrigido para false e uma chamada por rodada; ferramentas continuam sendo escolhidas pelo modelo com escopo validado.
- HTTP genérico deixou de ocultar status. Auditoria preserva status e código do provedor em allowlist, descartando mensagem bruta/failed_generation. O teste HML passa a imprimir esses campos. Janela de espera cliente ampliada para três minutos para acomodar as rodadas sequenciais.
- Validação local: 52 testes Python passaram, incluindo parâmetro de paralelismo, três rodadas sequenciais com escopo pendente e diagnóstico sanitizado. Não houve inferência real Groq local. Correção deve ser reconstruída e validada na VM; causa exata do HTTP anterior não foi recuperada retroativamente.

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

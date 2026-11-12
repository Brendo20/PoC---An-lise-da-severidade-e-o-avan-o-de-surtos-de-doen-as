# Observatório SRAG — PoC Indicium

Repositório: [Brendo20 — PoC de análise de surtos](https://github.com/Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as).

Projeto de relatórios epidemiológicos com ferramentas determinísticas e agente de IA, desenvolvido com AI-DLC.

Status: dashboard, carga PostgreSQL e API confirmados em HML pelo operador. Agente Groq com ferramentas de banco, notícias e relatório implementado e validado localmente com dublês. Busca real de notícias validada; primeira geração real na Groq e build atualizado na VM ainda pendentes.

## Documentação
- [Requisitos e critérios de aceite](aidlc-docs/inception.md)
- [Diagnóstico inicial dos dados](aidlc-docs/data-assessment.md)
- [Decisões de arquitetura](aidlc-docs/architecture-decisions.md)

Os CSVs originais e segredos não devem ser publicados no Git. O acesso público será a agregações e relatórios, sem consultas a registros individuais.

## Validação automática

GitHub Actions executa os testes Python com dados sintéticos e confere a sintaxe JavaScript em pushes e pull requests. Os testes de navegador usam o snapshot local e são executados separadamente, conforme as instruções abaixo. Nenhum segredo ou CSV é necessário para a validação automática.

## Diagnóstico reproduzível (Python 3.11+)

O profiler usa apenas a biblioteca padrão. A suíte completa inclui testes HTTP e requer os extras de API e teste. Na raiz do projeto, em PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m pip install -e ".[api,test]"
python -m unittest discover -s tests -v
python -m srag.profile "CAMINHO/INFLUD19-23-03-2026.csv" --as-of 2026-11-10 --source-url "https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/d96d6348-083a-4184-a39a-794b5e8ec337" --output reports/data-profile-2019.json
```

O comando não altera o CSV e recusa sobrescrever evidência anterior. O JSON contém somente estatísticas agregadas; não constitui uma carga no banco. A data de corte é explícita para permitir reprodução.

- [Contrato de métricas](aidlc-docs/metric-contract.md)
- [Desenho e pendências de U1](aidlc-docs/units/U1-data-quality.md)
- [Registro AI-DLC](aidlc-docs/progress.md)

## Proposta de interface

[Requisitos e decisões de experiência](aidlc-docs/frontend-design.md). O protótipo aprovado em `design/srag-wireframe.html` é preservado como referência ilustrativa. A implementação com dados reais fica em `frontend/`.

## Executar o frontend com dados reais

Na raiz do projeto, com Python 3.11+, em PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m srag.aggregate "CAMINHO/INFLUD19-23-03-2026.csv" --reference 2019-12-28 --coverage-start 2018-12-30 --coverage-end 2019-12-28 --output frontend/data/snapshot.json
python -m http.server 8765 --bind 127.0.0.1 --directory frontend
```

Abra http://127.0.0.1:8765/ no navegador. Para encerrar, pressione Ctrl+C no terminal. Não abra `index.html` diretamente: o carregamento dos dados depende de HTTP.

O gerador recusa sobrescrever uma saída existente. Para uma nova execução, gere uma saída com outro nome e mantenha o manifesto anterior antes de promover a nova cópia para `frontend/data/snapshot.json`. A data de geração do snapshot não é uma carga PostgreSQL. Não existe rotina agendada nesta etapa.

Mapa, indicadores e gráficos usam arquivos locais, sem CDN ou dependência de rede em tempo de execução. D3 7.9.0 e licença estão em `frontend/vendor/`, com hashes de origem. A malha simplificada do IBGE permanece versionada, sem inferência de compatibilidade municipal histórica.

### Escopo e limitações

- Brasil, UFs e regiões, por início dos sintomas e UF de residência. Casos sem UF reconhecida são preservados no total nacional.
- Crescimento de 7 dias, letalidade entre desfechos conhecidos, proporção de internação em UTI e vacinação contra gripe entre casos com informação conhecida; séries reais de 30 dias e 12 meses, com mês final parcial sinalizado.
- UTI e vacinação mostram numerador, denominador e percentual desconhecido. Não equivalem a ocupação operacional ou cobertura populacional, não calculáveis no escopo exclusivo do CSV.
- Mapas e menus usam um estado único de filtros. Seleção principal/comparação atualiza cards, comparativos, gráficos, tabelas, legendas, resumo e qualidade do recorte. Os botões do mapa indicam qual território será alterado. A janela temporal é fixa e comum aos territórios; não há filtro de período nesta etapa.
- A prévia estática apresenta resumo determinístico. No serviço API, um botão separado aciona o agente e gera relatório com números, dois gráficos e notícias, sem chamadas automáticas ao trocar filtros.
- Contagens pequenas são suprimidas; proteção complementar contra inferência ainda pendente. **Snapshot restrito ao desenvolvimento local, ignorado pelo Git e não liberado para publicação.**
- Sem recortes municipais ou autenticação de aplicação; acesso restrito a HML. Carga PostgreSQL e API existentes confirmadas pelo operador.

### Validação do frontend

Com Playwright e Microsoft Edge instalados, mantenha o servidor local em execução e rode:

```powershell
node tests/frontend-smoke.cjs
node tests/frontend-filters.cjs
node tests/frontend-tooltips.cjs
```

Se Playwright não estiver no caminho padrão, configure `SRAG_PLAYWRIGHT_MODULE` para o pacote instalado. `SRAG_PREVIEW_URL` permite informar outra URL local. O teste verifica números reais conhecidos, mapa e comparações, supressão, erro de carregamento e responsividade. Evidências em `reports/` e prévias em `frontend/preview-*.png` são ignoradas pelo Git.

Desenho desta unidade: [U2/U4 — dados reais e frontend](aidlc-docs/units/U2-U4-real-data.md).

Critérios e evidências da etapa 1: [indicadores e filtros sincronizados](aidlc-docs/units/stage-1-dashboard.md).

## Escopo confirmado em 11/11/2026

Usar exclusivamente SRAG 2019. O relatório final deve apresentar crescimento e letalidade com definições corretas e explicitar que mortalidade populacional, ocupação real de UTI e vacinação populacional não são calculáveis com o CSV. Notícias serão consultadas no momento da geração e separadas da análise histórica. Essa decisão não transforma os indicadores indisponíveis em requisitos numericamente atendidos.

## PostgreSQL — preparação

O projeto inclui `sql/001_aggregate_store.sql` e `src/srag/database.py`. O desenho está em [U3 — banco e ferramentas](aidlc-docs/units/U3-database-tools.md). São armazenadas agregações, sem registros individuais de pacientes.

No banco exclusivo da PoC, configure duas conexões no ambiente: `SRAG_LOADER_DATABASE_URL` (migração/carga) e `SRAG_DATABASE_URL` (login somente leitura). `.env.example` lista os nomes, mas não carrega variáveis automaticamente. Não envie credenciais no chat ou versione arquivos `.env`.

```powershell
python -m pip install -e ".[postgres]"
$env:PYTHONPATH = "src"
python -m srag.database migrate
python -m srag.database load frontend/data/snapshot.json
python -m srag.database status
```

A migração cria o schema `srag` apenas no banco apontado pela conexão. Os GRANTs de leitura estão comentados no SQL e devem ser aplicados ao login exclusivo correto pelo administrador. A carga usa transação, preserva snapshots anteriores e só promove uma carga completa; repetição de conteúdo idêntico mantém a data de carga original. Conteúdo diferente com mesmo identificador é rejeitado.

**Estado confirmado em HML pelo operador:** migração 001, carga ativa e repetição idempotente validadas; reader com SELECT=true e INSERT/UPDATE/DELETE=false. Snapshot `srag-ec77679e6022ca66-2019-12-28-v1.0.0`, carga em 12/11/2026 às 12:45:32 UTC (09:45:32 em Brasília).

## API e dashboard integrado

O serviço FastAPI disponibiliza frontend e dados na mesma origem. `/api/dashboard` consulta os 33 territórios em uma única instrução SQL, mantendo a mesma carga em toda a tela. Os filtros continuam locais e instantâneos sobre esse resultado. A API não recebe a conexão loader nem permite SQL livre.

| Endpoint | Finalidade |
|---|---|
| `/health/live` | Processo em execução |
| `/health/ready` | Carga ativa acessível no PostgreSQL |
| `/api/dashboard` | Metadados, carga efetiva, métricas e séries dos territórios |
| `/api/metrics?territory=SP` | Indicadores do território com snapshot e data de carga |
| `/api/series?territory=Norte` | Séries do território com snapshot e data de carga |

Instalação de desenvolvimento: `python -m pip install -e ".[api,test]"`. Configure `SRAG_DATABASE_URL` no ambiente e execute `python -m uvicorn srag.api:app --host 127.0.0.1 --port 8766`. O arquivo `.env` não é carregado automaticamente pelo comando Python; Compose interpola a conexão reader e a configuração Groq.

### HML Oracle

Na raiz do checkout da VM, com `.env` protegido e carga já validada:

```bash
git pull --ff-only
docker compose -f compose.hml.yml config --quiet
docker compose -f compose.hml.yml up -d --build api
docker compose -f compose.hml.yml ps
curl --fail --silent --show-error http://127.0.0.1:8766/health/ready
```

Não execute `docker compose config` sem `--quiet` para compartilhar saída: a configuração expandida contém segredos. O build exclui `.env`, CSVs e snapshots. A aplicação usa o PostgreSQL existente e um volume privado para relatórios/auditoria. Porta apenas em loopback, rede `portais-net`, 256 MiB e 0,5 CPU, sem root e filesystem somente leitura, exceto volume e tmpfs. Não altera Caddy. Após o build, confirme healthcheck e os números reais na VM antes de considerar implantação concluída.

O serviço está interno, sem autenticação de aplicação nesta etapa. Não adicionar rota pública no Caddy antes de definir domínio e controle de acesso de HML. O snapshot continua sem liberação para divulgação pública.

### Origem e falhas

Quando servido pela API, o HTML seleciona `/api/dashboard` e a interface mostra a data efetiva da carga. Falhas da API não recorrem ao snapshot do disco. A API bloqueia `/data/snapshot.json`, `.env`, SQL e código-fonte. A prévia estática anterior continua disponível por `http.server`, claramente em modo local, sem sugerir consulta ao banco.

### Testes da integração HTTP

Os testes Python usam `FastAPI TestClient` e repositório controlado. Para teste visual sem banco, `python tests/serve_api_fixture.py` serve uma fixture em memória em 127.0.0.1:8767. Ela não comprova conectividade com PostgreSQL. Nesse servidor, configure `SRAG_PREVIEW_URL=http://127.0.0.1:8767/` e execute os testes frontend existentes e `node tests/frontend-api.cjs`.

Desenho e critérios: [U4 — API PostgreSQL](aidlc-docs/units/U4-postgres-api.md). Build ARM64 e teste HTTP contra o banco real dependem da execução pelo operador em HML.

## Agente, notícias e relatório — U5

O orquestrador executa function calling real com `openai/gpt-oss-20b`, servido pela Groq. As três ferramentas fechadas consultam métricas, séries e notícias; o modelo não recebe SQL livre, URLs para buscar ou dados individuais. O backend fixa o snapshot e até dois territórios compatíveis antes da execução. A saída final usa JSON Schema em chamada separada, conforme [tool calling da Groq](https://console.groq.com/docs/tool-use/local-tool-calling) e [structured outputs](https://console.groq.com/docs/structured-outputs).

Cada rodada solicita uma única ferramenta, com `parallel_tool_calls=false`: o GPT-OSS não suporta chamadas paralelas na [matriz de capacidades da Groq](https://console.groq.com/docs/tool-use/overview). Até três rodadas consultam as ferramentas obrigatórias. Falhas HTTP preservam o status e apenas códigos de erro permitidos na auditoria; mensagem bruta e `failed_generation` são descartados para não registrar raciocínio ou conteúdo sensível. O teste HML imprime esse diagnóstico sanitizado.

A sequência obrigatória é definida pelo orquestrador: métricas, séries e notícias. Cada requisição oferece apenas a ferramenta da etapa e usa `tool_choice` com seu nome explícito, modalidade [documentada pela Groq](https://console.groq.com/docs/tool-use/local-tool-calling). A chamada retornada pelo LLM precisa corresponder à função oferecida e aos argumentos vazios; nenhuma ferramenta é executada em nome do modelo sem essa validação. O fallback controlado em falha fica identificado como parcial. A redação usa conversa nova com as evidências, sem histórico de chamadas ou instruções de coleta. Esse fluxo prescrito prioriza requisitos obrigatórios e auditabilidade; o modelo não escolhe livremente a ordem das etapas.

Consumo: as etapas de coleta independentes não reenviam resultados de etapas anteriores e usam orçamento máximo de 512 tokens de saída cada; a redação mantém 1.800. O texto recebe métricas e evidências compactas de notícias. As séries completas ficam no relatório e nos gráficos determinísticos, sem serem reenviadas ao LLM. Isso reduz contexto e orçamento solicitado, mas não garante disponibilidade de quota. HTTP 429 conserva `Retry-After` numérico válido na auditoria, sem retentativas automáticas. A [Groq aplica limites de requisições e tokens por janela](https://console.groq.com/docs/rate-limits); verificar os limites reais da organização no Console antes de repetir tentativas.

Números e gráficos são renderizados pelo backend. A validação confere estrutura, referências, tendências de crescimento e restrições da narrativa; isso **não prova a correção semântica de toda frase do LLM**. Texto inválido admite uma tentativa de correção; falha ou quota gera relatório parcial explícito, preservando indicadores. Máximo de três rodadas de ferramentas e duas tentativas de narrativa; timeout de 25 segundos por chamada e sem retentativas automáticas de quota.

Os feeds públicos fixos do Ministério da Saúde e da Agência Fiocruz são consultados primeiro, com Google News RSS como descoberta complementar. São selecionadas até cinco matérias dos últimos trinta dias, por título/resumo, com fonte, publicação e horário de consulta. Não há leitura integral nem garantia de cobertura específica da UF. Notícias atuais e análise histórica ficam separadas, sem atribuição causal entre épocas. A busca depende da disponibilidade e do conteúdo dos feeds.

Configuração privada no `.env` (não versionar nem compartilhar): `GROQ_API_KEY` e `GROQ_MODEL=openai/gpt-oss-20b`. Nenhuma chave vai para o frontend. O plano e as quotas disponíveis dependem da conta Groq; a aplicação limita uma geração simultânea, intervalo de um minuto e cache de relatório completo por cinco minutos. Cache e bloqueio são locais a um processo; manter **um worker e uma réplica** nesta PoC. Reinício remove cache/intervalo em memória, sem apagar arquivos persistidos.

| Endpoint | Uso |
|---|---|
| `GET /api/agent/status` | Configuração habilitada, sem testar credencial nem consumir tokens |
| `POST /api/reports` | JSON `{"territories":["Brasil"],"snapshot_id":"id-do-dashboard"}` |
| `GET /api/reports/{id}` | Relatório JSON, fontes e eventos de auditoria |
| `GET /api/reports/{id}/html` | Relatório independente, imprimível, com os dois gráficos |

O volume Docker `srag-reports` guarda `report.json`, `report.html` e `audit.jsonl` por execução. Auditoria registra ferramentas, hash dos resultados, duração, uso de tokens, rejeições e decisões de validação. Não guarda raciocínio interno, prompts completos ou segredos. Arquivos ficam no diretório privado do usuário do container; endpoints ainda dependem do controle de acesso externo de HML. Não executar `down -v`: apaga volumes. Retenção, backup e autenticação precisam ser definidos antes de produção.

Com a chave já protegida no `.env`, atualizar e validar **na VM**, na raiz do repositório:

```bash
git pull --ff-only
docker compose -f compose.hml.yml config --quiet
docker compose -f compose.hml.yml up -d --build --wait --wait-timeout 120 api
docker compose -f compose.hml.yml exec -T api python - < check_agent_hml.py
```

O último comando realiza uma geração real e consome a quota disponível; imprime somente diagnóstico sanitizado. Aceite: `status=complete`, narrativa validada, notícias presentes e conferência das métricas/duas séries com o dashboard. Relatório parcial não encerra o gate da integração LLM. Não é necessário recarregar a base ou recriar o banco.

Testes locais: suíte Python e `tests/frontend-agent.cjs` usam dublês de Groq/banco/notícias. O servidor `tests/serve_api_fixture.py` habilita essa simulação explicitamente. Executar o teste de navegador não atesta acesso real aos provedores. Desenho e critérios AI-DLC: [U5 — agente e relatórios](aidlc-docs/units/U5-agent-reports.md).

Pendências da entrega: teste real do agente em HML, diagrama conceitual em PDF, revisão final do README e evidências de aceite. Ocupação operacional de UTI, cobertura vacinal e mortalidade populacionais permanecem não calculáveis pelo CSV exclusivo; proxies estão identificados e não substituem essas definições.

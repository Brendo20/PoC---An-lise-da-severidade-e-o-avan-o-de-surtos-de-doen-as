# Observatório SRAG — PoC Indicium

Repositório: [Brendo20 — PoC de análise de surtos](https://github.com/Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as).

Projeto de relatórios epidemiológicos com ferramentas determinísticas e agente de IA, desenvolvido com AI-DLC.

Status: dashboard validado; carga PostgreSQL e leitura restrita confirmadas em HML pelo operador. API e frontend integrado preparados para validação em HML. Agente LLM e notícias ainda não integrados.

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
- Resumo determinístico, sem LLM ou notícias nesta etapa. Não representa o agente final solicitado no desafio.
- Contagens pequenas são suprimidas; proteção complementar contra inferência ainda pendente. **Snapshot restrito ao desenvolvimento local, ignorado pelo Git e não liberado para publicação.**
- Sem recortes municipais, autenticação, carga PostgreSQL ou deploy nesta etapa.

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

Instalação de desenvolvimento: `python -m pip install -e ".[api,test]"`. Configure `SRAG_DATABASE_URL` no ambiente e execute `python -m uvicorn srag.api:app --host 127.0.0.1 --port 8766`. O arquivo `.env` não é carregado automaticamente pelo comando Python; Compose o utiliza para interpolar somente a conexão reader.

### HML Oracle

Na raiz do checkout da VM, com `.env` protegido e carga já validada:

```bash
git pull --ff-only
docker compose -f compose.hml.yml config --quiet
docker compose -f compose.hml.yml up -d --build api
docker compose -f compose.hml.yml ps
curl --fail --silent --show-error http://127.0.0.1:8766/health/ready
```

Não execute `docker compose config` sem `--quiet` para compartilhar saída: a configuração expandida contém a conexão. O build exclui `.env`, CSVs e snapshots. Não são necessários mounts de dados no serviço; ele usa o PostgreSQL já existente. Porta apenas em loopback, rede `portais-net`, 256 MiB e 0,5 CPU, sem root e filesystem somente leitura. Não altera Caddy. Após o build, confirme healthcheck e os números reais na VM antes de considerar implantação concluída.

O serviço está interno, sem autenticação de aplicação nesta etapa. Não adicionar rota pública no Caddy antes de definir domínio e controle de acesso de HML. O snapshot continua sem liberação para divulgação pública.

### Origem e falhas

Quando servido pela API, o HTML seleciona `/api/dashboard` e a interface mostra a data efetiva da carga. Falhas da API não recorrem ao snapshot do disco. A API bloqueia `/data/snapshot.json`, `.env`, SQL e código-fonte. A prévia estática anterior continua disponível por `http.server`, claramente em modo local, sem sugerir consulta ao banco.

### Testes da integração HTTP

Os testes Python usam `FastAPI TestClient` e repositório controlado. Para teste visual sem banco, `python tests/serve_api_fixture.py` serve uma fixture em memória em 127.0.0.1:8767. Ela não comprova conectividade com PostgreSQL. Nesse servidor, configure `SRAG_PREVIEW_URL=http://127.0.0.1:8767/` e execute os testes frontend existentes e `node tests/frontend-api.cjs`.

Desenho e critérios: [U4 — API PostgreSQL](aidlc-docs/units/U4-postgres-api.md). Build ARM64 e teste HTTP contra o banco real dependem da execução pelo operador em HML.

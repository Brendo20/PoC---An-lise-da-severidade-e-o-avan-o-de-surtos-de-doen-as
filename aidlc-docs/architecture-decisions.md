# Decisões de arquitetura

## ADR-001 — Hospedagem Oracle (proposta)
Contexto: infraestrutura informada com HML e PROD ARM64, cada uma com 1 OCPU e 6 GB de RAM; Caddy, PostgreSQL 16 e rede portais-net compartilhados com portais existentes. Estas informações vieram do documento fornecido e não foram verificadas no servidor.

Proposta: reutilizar Caddy e PostgreSQL; criar banco e credenciais exclusivos, aplicação FastAPI, worker Python/LangGraph e frontend preferencialmente estático. LLM por API. PostgreSQL não público. Não adicionar Payload CMS ao projeto SRAG.

Banco exclusivo fornece isolamento lógico; recursos e domínio de falha da instância permanecem compartilhados. A rede compartilhada também não constitui isolamento entre projetos. Definir privilégios, limites de conexões e recursos após inventário.

HML antes de PROD. Builds compatíveis com ARM64, preferencialmente fora de PROD. Worker com uma tarefa simultânea inicialmente. Jobs podem ser persistidos no PostgreSQL com aquisição atômica, lease, recuperação de falhas e idempotência; detalhes na Construction.

## ADR-002 — Cálculos determinísticos (proposta)
SQL parametrizado e ferramentas tipadas calculam métricas e séries; LLM redige a partir de agregações e evidências. Validar saída estruturada e correspondência numérica. Sem SQL livre, acesso individual ou banco vetorial inicialmente.

## ADR-003 — Histórico e atualidade (proposta)
Preservar a base exigida de 2019. Separar data de carga e referência analítica. Notícias atuais não explicam diretamente o cenário histórico. Fontes históricas e contemporâneas terão seções e finalidade explícitas.

## Pendências operacionais
Inventário somente leitura de containers, memória, CPU, disco, redes, configuração do proxy e estratégia de backup. Nenhum acesso à VM ou alteração de infraestrutura foi realizado. IPs, comandos de acesso e credenciais do documento de infraestrutura não serão copiados para o repositório público.

## ADR-004 — Agente limitado e persistência de relatórios (12/11/2026)

Decisão da Construction: implementar orquestrador Python com function calling Groq e três ferramentas fechadas, sem adicionar LangGraph nesta unidade. O fluxo tem escopo fixado, limites pequenos e validação explícita; não exige grafo durável ou banco vetorial. Isso substitui a preferência inicial por worker LangGraph; bibliotecas citadas nos pré-requisitos não são exigência de arquitetura do enunciado. A escolha reduz dependências na VM de um CPU e mantém eventos verificáveis por etapa. Migração para framework de grafo será reconsiderada se houver tarefas assíncronas duráveis, retomada ou múltiplos agentes.

Narrativa estruturada é solicitada depois das ferramentas, pois a combinação de saída estruturada estrita e ferramentas não é suportada nesse modo da Groq. Tabelas/gráficos independem do texto gerado. Leitura SQL permanece parametrizada, restrita e fixada por snapshot; nenhum comando SQL pode ser criado pelo modelo. Notícias não confiáveis não definem ferramentas nem destinos de rede.

JSON, HTML e auditoria JSONL ficam em volume privado, sem aumentar privilégios do reader PostgreSQL. Execução síncrona, uma geração simultânea e um worker atendem à PoC; não oferecem fila durável, cancelamento ou escala horizontal. Publicação externa exige autenticação, revisão de privacidade, backup e retenção do volume.

Atualização operacional: inventário, carga idempotente, reader restrito e API real foram confirmados pelo operador em HML. Credencial Groq validada por listagem de modelos; isso não equivale a inferência LLM. Primeira geração real da U5 ainda pendente.

### Revisão por evidência HML — coleta prescrita e redação isolada

Gerações reais retornaram HTTP 400/tool_use_failed na primeira chamada, inclusive após desabilitar paralelismo. Uma tentativa isolada teve sucesso; não houve relatório completo aceito. Revisado para oferecer uma função obrigatória por etapa com tool_choice nomeado, em ordem fixada pelo orquestrador. Há function calling real e validação do retorno; deixa de haver escolha livre de ordem pelo modelo. Prompt de coleta separado do de redação. A redação parte de evidências explícitas em conversa nova, evitando carregar instruções de coleta para uma requisição sem ferramentas. Não adicionar retries automáticos ou desabilitar validação da Groq. Aceite pendente de nova geração na VM.

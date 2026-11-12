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

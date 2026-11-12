# U3 — Persistência e ferramentas de consulta

## Decisão do usuário — 11/11/2026
Base exclusiva: SRAG 2019. Não acrescentar fontes de dados complementares. Explicitar indicadores não calculáveis: ocupação real de UTI e cobertura vacinal populacional. Manter letalidade com nome correto, sem declarar que equivale a mortalidade populacional. Notícias devem ser consultadas no momento da execução e separadas do contexto de 2019.

## Desenho
O PostgreSQL recebe agregações calculadas e validadas, em vez de armazenar campos individuais desnecessários. Cada snapshot mantém origem, hash de conteúdo, referência analítica e loaded_at efetivo do banco. Tabela de territórios guarda métricas e séries. Ponteiro de carga ativa só muda após transação bem-sucedida. Relatórios fixam snapshot_id no início; troca da carga ativa não mistura períodos ou dados em uma execução.

Ferramentas consultar_metricas e consultar_series retornam agregações por território de allowlist. SQL é fixo e parametrizado, transações de consulta são somente leitura e com timeout. O login de consulta deve ter apenas SELECT e USAGE; o agente não recebe DSN, senha, SQL livre nem campos individuais.

Migração 001 cria somente schema srag e tabelas no banco configurado. Não altera banco ou proxy dos portais. Pode ser aplicada em PostgreSQL 16/17, mas a execução real ainda depende da conexão exclusiva ser configurada. Instalação local detectada: serviço PostgreSQL 17 em execução, sem DSN do projeto disponível. Nenhum login ou senha foi procurado ou presumido.

## Validação
Testes unitários com conexão controlada verificam allowlist, parâmetros SQL e leitura. Não substituem teste de integração em PostgreSQL. Migração, permissões, rollback e carga idempotente precisam ser executados no banco exclusivo antes de declarar a unidade completa.

## Próximas etapas
Configurar conexão e executar migração/carga em desenvolvimento; conectar orquestrador e busca de notícias; adicionar LLM e validação de saída; gerar relatório com métricas e dois gráficos; testar fluxo real com auditoria e falhas. PDF conceitual e deploy HML/PROD permanecem pendentes.

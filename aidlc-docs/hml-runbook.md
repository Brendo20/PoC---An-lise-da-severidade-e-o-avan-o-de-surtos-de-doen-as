# HML — carga inicial de 2019

## Estado confirmado pelo operador em 12/11/2026
Repositório clonado em /srv/portais/projetos/indicium-srag. VM ARM64 com 1 CPU e 6 GB de RAM, Caddy/PostgreSQL 16/rede portais-net já existentes. Banco exclusivo indicium_srag_hml e logins loader/reader criados. Migração 001 aplicada às 12:36:18 UTC. Zero snapshots. .env com permissão 600 e ignorado pelo Git. Estas são evidências fornecidas pelo operador, não uma sessão SSH do agente.

## Container de ferramentas
Dockerfile.tools usa Python 3.12, instala o extra PostgreSQL e contém apenas código/SQL. .dockerignore usa allowlist para não enviar dados, snapshots, Git ou .env ao build. A imagem base suporta ARM64; build ainda requer execução/validação na VM. Não cria serviços persistentes, PostgreSQL ou proxy adicionais.

As tarefas de download e agregação rodam com o UID/GID do operador e diretórios montados. A carga roda sem capabilities, filesystem raiz somente leitura, /tmp limitado, 256 MiB e 0,5 CPU. Conexões são lidas do .env pelo Docker, sem senhas em argumentos. Para carga, usar apenas a rede portais-net. O container só permanece ativo durante cada comando.

## Sequência operacional
1. git pull --ff-only.
2. Build da imagem indicium-srag-tools:hml pelo Dockerfile.tools.
3. Criar data/raw e frontend/data, ambos fora do Git.
4. Executar srag.download para obter o CSV de 2019 e verificar o hash fixado no código.
5. Executar srag.aggregate com referência 2019-12-28 e cobertura declarada 2018-12-30 a 2019-12-28.
6. Executar srag.database load com a conexão loader e snapshot montado somente leitura.
7. Executar srag.database status com a conexão reader. Confirmar loaded_at real e id da carga.

Cada etapa depende do sucesso da anterior. O gerador não sobrescreve snapshot existente. O downloader reutiliza somente arquivo com hash exato e preserva destinos divergentes. Se a URL histórica mudar ou deixar de responder, transferir o CSV local já auditado e repetir a verificação, sem trocar automaticamente a base.

## Critérios de aceite
Hash do CSV igual ao arquivo auditado; 48.941 registros lidos, 48.866 no recorte; uma carga completa com 33 territórios; consulta reader funcionando e sem permissão de escrita. Repetir a mesma carga deve retornar already_loaded sem mudar loaded_at. Nenhuma alteração em Caddy antes da configuração do subdomínio e controle de acesso de HML.

## Limites
Este procedimento carrega agregações, não dados individuais. O snapshot original mantém database_load=not_loaded; a fonte de verdade para a carga SQL é o banco, consultado por status. A interface estática ainda não é integrada ao banco. Base e snapshot são restritos a HML, sem liberação pública automática.

## Resultado da carga confirmado pelo operador
Snapshot srag-ec77679e6022ca66-2019-12-28-v1.0.0 carregado em 12/11/2026 às 12:45:32.573171 UTC. Repetição retornou already_loaded sem alterar loaded_at. Reader confirmou SELECT=true e INSERT/UPDATE/DELETE=false; métricas Brasil conciliadas: 48.866 casos, crescimento -11,7647%, letalidade 12,1349%, UTI entre casos 36,9304%, vacinação entre casos 32,0824%.

## API preparada
compose.hml.yml e Dockerfile.api acrescentam um único serviço que serve interface e consultas PostgreSQL por loopback 127.0.0.1:8766, com alias interno indicium-srag-hml-api. Usa apenas SRAG_DATABASE_URL, sem mounts de dados ou conexão loader. Build e healthcheck na VM ainda devem ser confirmados. Consulte o README para comandos. A implementação integrada substitui o arquivo estático por /api/dashboard quando o frontend é servido por esse serviço.

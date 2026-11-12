# U4 — API e dashboard conectados ao PostgreSQL

## Gate de entrada — 12/11/2026
Operador confirmou carga ativa em HML, idempotência e login reader com SELECT=true e INSERT/UPDATE/DELETE=false. Métricas nacionais conferem com o CSV. O usuário autorizou avançar para API e integração.

## Desenho
FastAPI + Uvicorn, um worker e concorrência limitada. Consulta única retorna metadata e 33 territórios de um mesmo snapshot ativo, em transação somente leitura com timeout. Assim os filtros existentes continuam instantâneos e coerentes sobre uma versão do banco. Metadados apresentam loaded_at real, separado de data de geração e referência de 2019.

Endpoints: /health/live, /health/ready, /api/dashboard, /api/metrics e /api/series. Território em allowlist e SQL parametrizado. Rotas não permitem escrita. Nenhuma credencial é retornada; erros de armazenamento são sanitizados.

Frontend e API compartilham origem. O HTML servido pela API configura a fonte de dados como API; a prévia estática permanece explicitamente local. Falha de API não pode acionar fallback silencioso para snapshot antigo. O serviço não serve .env, código, diretórios, snapshots do disco ou CSVs.

## Operação
Compose HML utiliza apenas SRAG_DATABASE_URL, sem a conexão loader ou chave LLM. Variável lida do .env pelo Compose e não copiada na imagem. Reutiliza portais-net, sem banco/proxy adicional. Porta de diagnóstico vinculada somente a 127.0.0.1:8766; sem alteração em Caddy ou exposição pública. Limite de memória/CPU, filesystem read-only, usuário sem root, capabilities removidas, logs com rotação e healthcheck.

## Critérios de aceite
- Uma consulta do dashboard conserva snapshot_id, loaded_at e todos os territórios.
- Reader permanece único acesso DB da API; nenhuma rota executa SQL livre.
- HTTP 400 para território desconhecido; 503 sanitizado para indisponibilidade; healthcheck distingue processo vivo de carga acessível.
- Frontend exibe data de carga efetiva e usa /api/dashboard em modo integrado, sem requisitar snapshot local.
- Filtros, mapas, tooltips, comparações e responsividade preservados nos testes.
- Recursos sensíveis e arquivo de snapshot inacessíveis pelo servidor.

Validação local usa repositório controlado em memória para testar HTTP e contrato; não será declarada como integração real com a VM. A validação PostgreSQL da API depende dos comandos que o operador executará em HML.

## Evidências de construção
32 testes Python passaram; Compose validado com conexão fictícia, sem daemon ou banco reais. Navegador em modo API validou data de carga, nenhuma requisição de snapshot do disco, erro sem fallback, 47 cenários sincronizados de filtros, tooltips e smoke test. Prévia visual inspecionada. Arquivos de evidência em reports/ são locais e ignorados pelo Git. Build da imagem ARM64 e integração HTTP real com PostgreSQL permanecem pendentes de HML.

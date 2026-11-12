# U1 — Diagnóstico reproduzível e desenho da ingestão

## Gate e escopo
O usuário autorizou a continuidade seguindo AI-DLC em 10/11/2026. A unidade de diagnóstico pode avançar sem resolver as fontes complementares; a Inception global permanece aberta nessas decisões. Nenhuma autorização de publicação ou alteração em PROD é inferida.

## Desenho funcional
Entrada: CSV original local, URL de origem e data de corte explícita. Saída: JSON agregado com SHA-256 do arquivo, versão do profiler, data de execução, volume, esquema, qualidade e referência temporal candidata. A data do download não é inferida do nome do arquivo. Nenhuma carga no PostgreSQL é alegada.

Leitura em streaming, biblioteca padrão Python, sem dependências de produção. Identificadores são comparados como hashes em memória; não são exportados. Memória cresce com identificadores únicos, não com todas as linhas. Dados malformados estruturalmente são contados e ignorados nas estatísticas de campos; erros sintáticos de CSV interrompem a análise. Categorias inválidas são contadas sem exportar seus textos.

## Regras de qualidade
Datas ISO, timestamps ISO (preservando a data expressa na origem) e DD/MM/AAAA; inválidas e futuras são sinalizadas. Códigos com .0 são normalizados apenas quando representam inteiro. Ausência e ignorado permanecem distintos. Verificar ordem de início dos sintomas, notificação, internação, UTI e evolução. Uma anomalia não autoriza excluir todo o registro da futura carga.

A referência máxima válida não futura ainda requer revisão: não prova cobertura completa. Não produzir gráficos com zeros artificiais antes de verificar a cobertura.

## Validação
Testes sintéticos cobrem códigos, datas inválidas, datas futuras, ordem cronológica, identificadores repetidos, privacidade do resultado, hash estável, esquema ausente, arquivo vazio e linhas malformadas. Executar também sobre o arquivo real e conciliar contagens com o diagnóstico inicial.

## Continuação da unidade
Ainda pendentes: esquema SQL, migrações, armazenamento raw restrito, carga em staging, reconciliação, promoção transacional da carga ativa, idempotência e integração PostgreSQL. Não considerar U1 completa somente pelo profiler.

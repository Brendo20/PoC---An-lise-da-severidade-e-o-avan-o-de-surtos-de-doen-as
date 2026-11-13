# Acesso restrito pelo Caddy - preparação

Domínio informado pelo usuário em 13/11/2026: poc-srag.estacaolab.com.br. A escolha autoriza preparar esse host na homologação. Ainda não foram alterados DNS, Caddyfile ou container do proxy.

Consulta DNS local em 13/11/2026 retornou registros A 216.198.79.65 e 64.29.17.1; não foi estabelecido que correspondem ao IPv4 público da VM HML. Confirmar o IP público da instância e ajustar somente esse subdomínio no provedor DNS, preservando os demais portais. Se houver CDN/proxy intermediário, verificar a rota efetiva; não inferir o destino pelo nome do host.

IP público HML informado posteriormente pelo usuário: 163.176.51.25. O apontamento observado diverge desse destino. Para acesso direto ao Caddy, criar/ajustar o registro A específico de poc-srag para 163.176.51.25. Não alterar o domínio raiz, outros subdomínios ou wildcard usado pelos portais. Conferir registros A/CNAME conflitantes somente desse host e eventual AAAA sem destino IPv6 HML confirmado. A edição do DNS e sua propagação ainda não foram confirmadas; esta documentação não altera a zona.

## Preflight somente leitura na VM

```bash
docker exec portais-caddy caddy version

docker inspect portais-caddy \
  --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'

docker exec portais-caddy wget -qO- \
  http://indicium-srag-hml-api:8000/health/ready

getent ahostsv4 poc-srag.estacaolab.com.br
```

Esses comandos não alteram serviços nem chamam a Groq. A consulta readiness deve retornar o snapshot já validado. Conferir os mounts antes de escolher o caminho de edição; o caminho presumido /srv/portais/infra/proxy/Caddyfile precisa corresponder ao arquivo usado pelo proxy. Se wget não existir no container, usar uma alternativa disponível; não instalar pacotes no proxy compartilhado para esse teste.

## Configuração preparada

Modelo revisável em hml-caddy.caddy.example. Acrescenta apenas o host da PoC, autentica todos os caminhos e usa o alias indicium-srag-hml-api:8000 na rede portais-net. Não encaminha o cabeçalho de credencial Basic ao backend. Não contém senha/hash real e não é uma configuração pronta para aplicar. Não deve substituir os demais hosts do proxy.

A diretiva basic_auth exige Caddy 2.8 ou posterior; versões anteriores usam outro nome. A autenticação usa hash, não senha em texto simples. Fontes oficiais: [basic_auth](https://caddyserver.com/docs/caddyfile/directives/basic_auth) e [CLI](https://caddyserver.com/docs/command-line).

Após preflight e DNS confirmados, a aplicação deve seguir esta ordem:

1. Fazer cópia de segurança privada do Caddyfile efetivamente montado e anotar seu caminho para rollback.
2. Gerar hash bcrypt com caddy hash-password em modo interativo na VM. Não passar senha em argumento, não enviar senha ou hash no chat e não versionar o hash real.
3. Editar somente o bloco adicional da PoC, substituindo o token pelo hash. Preservar todos os hosts anteriores e a forma de montagem do arquivo.
4. Executar caddy validate com adapter caddyfile sobre o arquivo montado antes de recarregar. Adaptação sintática isolada não substitui validação.
5. Recarregar a configuração com caddy reload, sem reiniciar os serviços dos portais. Se a validação falhar, corrigir/restaurar antes do reload.
6. Conferir HTTPS, autenticação ausente/incorreta com HTTP 401 e acesso autorizado com HTTP 200. Não usar curl -k como prova de certificado válido.
7. Inspecionar dashboard e relatório já salvo. Não gerar novo relatório só para conferir o proxy.
8. Verificar que hosts anteriores continuam respondendo e registrar os resultados reais. Em problema, restaurar a cópia, validar e recarregar.

Essas são instruções de preparação; preflight, edição, certificado e testes externos ainda não foram executados nem aprovados por evidência. Não é necessário rebuild da aplicação para adicionar o site no Caddy. A porta da API permanece vinculada a 127.0.0.1:8766; não abrir 8766 ou 5432 no firewall.

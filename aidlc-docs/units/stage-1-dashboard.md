# Etapa 1 — Indicadores revisados e filtros sincronizados

Status: concluída em 11/11/2026 no escopo do dashboard local, após autorização do usuário para aplicar os achados e garantir o efeito global dos filtros. Não equivale a conclusão da PoC ou liberação para publicação.

## Requisitos e resultado
| Critério | Implementação | Validação |
|---|---|---|
| Mostrar dados disponíveis de UTI e vacinação | Cards, resumo comparativo e síntese determinística com proporções entre casos com resposta conhecida | Brasil: 36,93% e 32,08%, conciliados com snapshot e investigação do CSV |
| Nomes corretos e transparência | Sem equivalência a ocupação ou cobertura populacional; fórmulas, denominadores e desconhecidos explícitos | Cards e metodologia revisados |
| Filtro por menu | Estado único de filtros para nível, principal e comparação | Todas as 27 UFs e cinco regiões testadas |
| Filtro por mapa | Escolha explícita do destino principal/comparação; regiões selecionam os estados membros | Cliques reais em ambos os destinos, estados e regiões |
| Consistência global | Mesma seleção em indicadores, comparações, mapa, séries, tabelas, legendas, resumo e qualidade | 47 cenários sincronizados no navegador |
| Remoção e reset | Sem comparação de território consigo mesmo; reset remove comparação de todas as seções | Testes de menu, mapa, adicionar/remover e reset |
| Ausências e supressão | Valores suprimidos não viram zero e justificativas acompanham o recorte | Casos reais e smoke test |
| Responsividade | Refluxo desktop/mobile | 320, 360, 768 e 1100px, sem overflow horizontal; prévias inspecionadas |

## Ajustes de implementação
`updateFilters` centraliza transições e dispara uma renderização completa. A auditoria do recorte passou a ser atualizada a cada seleção, corrigindo sua independência anterior dos filtros. Informações fixas de origem agora são identificadas como totais do arquivo, para não parecerem totais filtrados.

O destino do mapa fica explícito por botões. Mudar de nível reinicia o recorte para Brasil; escolher como principal o território antes comparado limpa a comparação; clicar no principal quando o mapa está em modo comparação é rejeitado com mensagem. Essas regras mantêm menus e mapa coerentes.

A janela temporal continua fixa em 2019 e comum aos territórios. Não foi criado um filtro de data sem dados/contrato correspondentes. Municípios permanecem fora desta etapa.

## Evidências
- 19 testes Python passaram, sem regressões na agregação ou persistência preparada.
- `tests/frontend-filters.cjs`: 47 verificações globais, 27 UFs e cinco regiões; zero erros JavaScript.
- `tests/frontend-smoke.cjs`: comparações, valores nacionais, supressão, falha de carregamento e runtime sem requisições externas passaram.
- `reports/frontend-filters.json` e `reports/frontend-smoke.json` (evidências locais ignoradas pelo Git).
- `frontend/preview-desktop.png` e `frontend/preview-mobile.png` (prévias locais ignoradas pelo Git).

## Limites e próxima etapa
Snapshot restrito ao uso local; revisão contra inferência e supressão complementar antes da publicação. Agente, notícias, relatório final e conexão real PostgreSQL não foram implementados como parte desta etapa. A próxima unidade é a validação de migração e carga no banco exclusivo, seguida da integração do agente.

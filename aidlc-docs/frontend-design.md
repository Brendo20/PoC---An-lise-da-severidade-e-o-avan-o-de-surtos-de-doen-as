# Experiência do frontend — v0.1

Status: direção visual aprovada pelo usuário ("ficou excelente"), seguida de autorização para continuar. Integração funcional em construção; não equivale a aceite de produção.

## Requisitos confirmados pelo usuário
Design clean e escaneável; mapa SVG interativo; seleção territorial; comparação entre estados e regiões, incluindo Norte × Sudeste; detalhamento municipal progressivo.

## Primeira proposta
Página única com cabeçalho de contexto histórico, filtros territoriais, indicadores, mapa por UF, resumo comparativo, séries diária/mensal e relatório com evidências. Comparação inicial entre dois territórios do mesmo nível. Seleção por listas como alternativa ao mapa. Selecionar Brasil remove a comparação; mudar nível reinicia o recorte. Mapa é categórico de seleção, sem escala de severidade inferida.

Municípios ficam explicitamente fora desta primeira interação, até validar geocódigos, geometria e privacidade. Nenhuma hierarquia municipal é inferida de uma malha contemporânea.

## Dados do protótipo
Números e curvas são exclusivamente ilustrativos e identificados na tela. Não são resultados epidemiológicos, não foram conciliados com o CSV e não são enviados para agentes. Indicadores dependentes de fontes complementares ficam indisponíveis. Referência histórica candidata: 28/12/2019; não há carga no banco.

## Geometria
Malha oficial simplificada do IBGE baixada em 10/11/2026: 27 features, código codarea ligado aos códigos de UF. Fonte:
https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&qualidade=minima&intrarregiao=UF

Arquivo: design/assets/brazil-states.geojson. Projeção Mercator via d3-geo 3.1.1. Sem desenho manual dos contornos; geometria incorporada ao protótipo, sem chamadas de dados durante uso.

## Critérios de aceite do design
- Brasil, UF e região selecionáveis; comparação e remoção coerentes.
- Filtros atualizam mapa, resumo, legendas, curvas e título do relatório.
- Cores consistentes e segunda série tracejada; comparação legível sem depender apenas de cor.
- Não comparar regiões com UFs nesta etapa.
- Seleção alternativa por controles nativos de teclado; mapa é complemento de ponteiro.
- Refluxo em telas estreitas e estados de indisponibilidade explícitos.
- Nenhuma interpretação causal de dados ilustrativos.

## Pendências antes da implementação
Revisão visual do usuário, tipografia e cores finais, modo de comparação absoluta/normalizada quando houver denominadores, estados reais de erro/carregamento/supressão, avaliação de acessibilidade e privacidade de recortes municipais, integração API e remoção dos dados de demonstração.

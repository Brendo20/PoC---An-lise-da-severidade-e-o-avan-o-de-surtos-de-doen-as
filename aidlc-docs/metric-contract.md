# Contrato das métricas — v0.2

Status: definições de trabalho implementadas parcialmente; decisão de escopo do usuário registrada em 11/11/2026: usar exclusivamente o CSV de 2019 e explicitar indicadores não calculáveis. Fontes complementares não fazem parte do escopo autorizado.

As fórmulas de crescimento e letalidade foram implementadas para validação local e conciliadas com o CSV. Mortalidade populacional, ocupação real e cobertura vacinal populacional não podem ser calculadas exclusivamente com esta base. O usuário autorizou explicitamente apresentar essas limitações, sem substituir silenciosamente os indicadores.

## Filtros e datas
Casos por DT_SIN_PRI. Brasil inicialmente; filtro por UF de residência SG_UF quando implementado. Casos sem UF não devem desaparecer do total nacional. Um registro de notificação não equivale necessariamente a uma pessoa única. Nenhuma deduplicação por atributos clínicos sem regra documentada.

Referência candidata: 28/12/2019. Janela diária: 29/11 a 28/12/2019, inclusive. Janela mensal: janeiro a dezembro de 2019; dezembro parcial até dia 28. Os 75 registros com início dos sintomas em dezembro de 2018 são preservados, fora da janela de calendário de 2019.

## Indicadores
| ID | Indicador | Numerador | Denominador | Limitação |
|---|---|---|---|---|
| M01 | Crescimento em 7 dias | Casos em D-6 até D | Casos em D-13 até D-7 | (N/D - 1) × 100; base zero: indisponível |
| M02 | Letalidade entre desfechos conhecidos | EVOLUCAO=2 | EVOLUCAO em 1,2,3 | Mesmo recorte por início dos sintomas; desfechos observados na extração, não reconstruídos como conhecidos na data histórica |
| M03 | Ocupação de UTI | Leitos ocupados no território e data | Leitos disponíveis no mesmo escopo | Não calculável no escopo exclusivo do CSV |
| M04 | Cobertura vacinal populacional | Pessoas da população-alvo com esquema definido | População-alvo correspondente | Não calculável no escopo exclusivo do CSV |
| A01 | Proporção de internação em UTI | UTI=1 | UTI em 1,2 | Não equivale a ocupação; reportar ignorados/ausentes |
| A02 | Vacinação contra gripe entre casos com informação | VACINA=1 | VACINA em 1,2 | Última campanha conforme dicionário p.13; não representa população |

Percentuais multiplicam a razão por 100. Toda taxa inclui contagens, unidade, fórmula e proporção de informação desconhecida. Denominador zero produz valor nulo e motivo explícito. Arredondar apenas na apresentação. Óbitos por outras causas são separados.

## Política de atendimento ao desafio
M02 não substitui silenciosamente mortalidade populacional; A01/A02 não atendem M03/M04. Preservar nomes corretos e disponibilizar justificativas. Não combinar numeradores de 2019 com denominadores atuais. Conforme decisão de 11/11/2026, incluir no relatório os quatro requisitos, com valor não calculável e justificativa quando necessário, além da letalidade disponível. Isso documenta a limitação; não significa atendimento numérico integral aos indicadores originalmente pedidos.

## Evidências e privacidade
Ferramentas retornam somente agregações, versão de fórmula e identificador da carga. Supressão pública de grupos pequenos será aplicada antes do envio ao LLM, incluindo análise de inferência por diferenças de totais. Limite de supressão e filtros permitidos serão definidos antes da interface pública.

Na construção local v0.2, contagens de 1 a 4 recebem valor nulo e status suprimido. Taxas com numerador, complemento ou categoria desconhecida nessa faixa não são exportadas. Lacunas não são convertidas em zero. Há risco residual por agregações temporais e geográficas sobrepostas: snapshot não liberado para publicação até avaliar supressão complementar e inferência por diferenças.

## Apresentação revisada em 11/11/2026
O usuário autorizou concluir a etapa 1 com os achados de UTI e vacinação. Os cards principais e o resumo agora incluem A01/A02 com nomes observáveis, denominadores conhecidos e proporção desconhecida. A01 considera UTI em {1,2} entre todos os casos notificados do recorte, sem filtro adicional HOSPITAL=1. A02 descreve vacinação declarada contra gripe, sem inferir proteção anterior ao episódio ou eficácia. Os textos metodológicos preservam a indisponibilidade literal de M03/M04. Nenhuma fórmula ou dado original foi alterado.

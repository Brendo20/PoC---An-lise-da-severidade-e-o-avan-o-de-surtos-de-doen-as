# Investigação aprofundada — UTI e vacinação

Data: 11/11/2026. Escopo solicitado: revisar novamente o CSV e testar o que os campos realmente permitem responder, mantendo exclusivamente a base de 2019.

## Resultado
Há indicadores relevantes de UTI e vacinação calculáveis com os registros. A ausência de dados populacionais e de capacidade de leitos impede as definições literais de ocupação operacional de UTI e cobertura vacinal da população geral. Não é correto concluir que nada pode ser informado nessas áreas.

Os indicadores auxiliares já existentes no agregador devem ser considerados na apresentação final, com nomes, denominadores e limitações próprios. Esta investigação não autoriza renomeá-los como os indicadores literais nem alterar silenciosamente o contrato aprovado.

## Origem e reprodução
INFLUD19-23-03-2026.csv; SHA-256 f6de547c1234e2de4d65f830606849a006346e50b32106bd635714665100134a. Leitura integral de 48.941 registros e 194 colunas. Auditoria reproduzível:

```powershell
$env:PYTHONPATH = "src"
python -m srag.investigate "CAMINHO/INFLUD19-23-03-2026.csv"
```

O comando somente lê o arquivo e imprime agregações. Não publica dados nem altera a interface. Datas vazias e ignorados não são tratados como respostas negativas.

## Dois recortes para evitar mistura de denominadores
Arquivo completo: 48.941 registros, incluindo 75 com início dos sintomas em dezembro de 2018. Dashboard atual: 01/01/2019 a 28/12/2019, com 48.866 registros. Valores da tabela abaixo são do recorte do dashboard, não do arquivo completo.

| Medida | Numerador | Denominador | Resultado |
|---|---:|---:|---:|
| Internação em UTI entre casos com UTI conhecida | 17.344 | 46.964 | 36,93% |
| Internação em UTI entre hospitalizados com UTI conhecida | 17.279 | 46.790 | 36,93% |
| Vacinação contra gripe entre casos com resposta conhecida | 9.994 | 31.151 | 32,08% |
| Vacinação confirmada entre todos os casos | 9.994 | 48.866 | 20,45% |

No arquivo completo, os números correspondentes são UTI 17.369/47.038 (36,93%) e vacinação 10.011/31.202 (32,08%).

## UTI: semântica e datas
O dicionário, página 16, define UTI como a resposta à pergunta se o paciente foi internado em UTI. DT_ENTUTI e DT_SAIDUTI são datas de entrada e saída. Não há quantidade de leitos operacionais, capacidade total por hospital/data nem censo de pacientes de outras causas.

O total de pacientes distintos no período não é denominador de ocupação. O máximo observado de internações simultâneas também não identifica a capacidade: um hospital pode ter leitos ociosos, bloqueados ou ocupados por outras doenças ausentes da base. Não inferir capacidade contando hospitais ou tomando o pico como 100%.

Qualidade no arquivo completo, entre 17.369 registros com UTI=1:
- 178 sem entrada; 7.639 sem saída.
- 9.715 com ambas as datas (55,93%); 9.701 têm saída não anterior à entrada e entrada não anterior aos sintomas.
- 413 intervalos coerentes têm entrada e saída no mesmo dia; convenções de pacientes-dia exigem decisão explícita.
- Dois intervalos coerentes excedem 365 dias, exigindo análise de plausibilidade.
- 65 respostas UTI=1 não têm HOSPITAL=1; filtrar hospitalizados muda a população analisada.

É possível construir uma série exploratória de internações simultâneas documentadas, mediante convenção explícita do intervalo e tratamento de datas. Ela é parcial e não deve ser apresentada como taxa operacional de ocupação ou censo completo. Não imputar saídas ausentes para fabricar a taxa.

No recorte do dashboard, 1.902 registros (3,89%) têm UTI vazia/ignorada. O percentual entre respostas conhecidas deve vir acompanhado dessa incompletude.

## Vacinação: pergunta disponível e viés de seleção
O dicionário, página 13, define VACINA como vacinação contra gripe na última campanha. VACINA=1/2/9 significa sim/não/ignorado. DT_UT_DOSE informa a data da vacinação. A página 14 descreve vacinação materna em menores de seis meses e datas de doses pediátricas; estes campos não acrescentam pessoas da população geral ao denominador.

No recorte do dashboard: 9.994 sim; 21.157 não; 8.410 ignorados; 9.305 vazios. São 17.715 respostas desconhecidas (36,25%). Excluir os desconhecidos dá 32,08%; dividir os sim por todos os registros dá 20,45%, que é proporção com vacinação documentada, não estimativa equivalente da vacinação entre respostas conhecidas. Não chamar os desconhecidos de não vacinados.

A população observada são casos notificados, selecionados por adoecimento grave, hospitalização ou óbito. Não é uma amostra representativa da população geral. Mesmo que não existissem ausências, a proporção vacinada entre esses casos não estimaria cobertura populacional nem eficácia vacinal.

No arquivo completo, entre 10.011 respostas sim:
- 8.023 têm DT_UT_DOSE e 1.988 não têm data.
- 246 datas de dose são posteriores ao início dos sintomas; não presumir que representem proteção anterior ao episódio.
- 1.567 datas de dose são de outro ano; isso requer contexto de campanha, não exclusão automática.
- 510 registros têm alguma data nos campos pediátricos de dose única/primeira/segunda dose. Esses campos não permitem inferir a vacinação de toda a população ou substituir automaticamente VACINA.

## Interpretação para a certificação
Há ambiguidade no enunciado: ele pede indicadores populacionais/operacionais fornecendo uma base de casos. É plausível que espere aproximações calculadas pelos campos disponíveis, mas isso não está comprovado. A entrega mais defensável é apresentar os indicadores solicitados, explicar a impossibilidade literal e oferecer as medidas observáveis com nomes corretos, fórmulas e qualidade.

Proposta para o relatório: seção UTI com proporção de internação e cobertura do campo; seção vacinação com proporção contra gripe entre casos com informação e percentual desconhecido; nota metodológica esclarecendo que não equivalem a ocupação operacional ou cobertura populacional. As métricas literais permanecem não calculáveis sem denominadores externos, que o usuário decidiu não incluir.

## Referências semânticas
- Dicionário local 2019–2025: páginas 13, 14 e 16.
- Ficha fornecida: página 1 confirma os campos individuais; sua data interna é 25/05/2023, apesar do nome do arquivo conter 2025. Não tratá-la como ficha original de 2019.
- Ministério da Saúde, manual de implantação do NIR: taxa de ocupação requer pacientes-dia e leitos-dia operacionais: https://bvsms.saude.gov.br/bvs/publicacoes/manual_implantacao_implementacao_nir_nucelo_interno_regulacao_hospitais_gerais_especializado.pdf
- Ministério da Saúde, regras de cobertura vacinal: numerador padronizado e população-alvo compatível: https://www.gov.br/saude/pt-br/composicao/svsa/pni/regras-para-registros-vacinais/regras-para-registros-vacinais/

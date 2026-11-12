# Diagnóstico inicial — 10/11/2026

## Fonte e escopo
Arquivo analisado: INFLUD19-23-03-2026.csv, disponibilizado pelo recurso explicitamente indicado no desafio:
https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/d96d6348-083a-4184-a39a-794b5e8ec337

Análise integral por leitura CSV em streaming, sem expor linhas individuais. Separador ponto e vírgula; leitura UTF-8-SIG. Ainda não há pipeline persistido nem certificação completa da qualidade.

## Resultados observados
- 48.941 linhas e 194 colunas, diferente da estimativa do enunciado.
- Nenhuma repetição de identificador não vazio NU_NOTIFIC; isso não comprova ausência de duplicidade clínica.
- DT_SIN_PRI: 30/12/2018 a 28/12/2019; 75 registros em 2018 e 48.866 em 2019; nenhuma ausência ou falha de parsing ISO.
- DT_NOTIFIC: 30/12/2018 a 20/08/2023. Datas tardias exigem análise, sem exclusão automática.
- DT_INTERNA: 1.317 ausências; máximo 10/07/2109, inconsistente com o contexto temporal.
- DT_ENTUTI: 31.750 ausências; DT_SAIDUTI: 39.211 ausências. Ausências precisam ser avaliadas condicionalmente à internação em UTI.
- UTI: 17.369 sim, 29.669 não, 338 ignorados e 1.565 vazios.
- EVOLUCAO: 39.255 cura, 5.423 óbito, 7 óbito por outras causas, 1.387 ignorados e 2.869 vazios.
- VACINA: 10.011 sim, 21.191 não, 8.432 ignorados e 9.307 vazios.
- VACINA_COV: 53 sim em uma base histórica de 2019. Campo não será usado para inferir vacinação contemporânea aos casos; investigar proveniência e compatibilidade histórica.
- Códigos como EVOLUCAO e CLASSI_FIN aparecem como textos com sufixo .0; normalização deve preservar semântica e distinguir ausência de zero.

## Documentação consultada
Dicionário 2019–2025, 28 páginas: páginas 2 (início dos sintomas), 10 (vacina COVID), 16 (internação e UTI), 24 (classificação e evolução). Ficha de 2025 recebida, com 2 páginas; compatibilidade histórica ainda deve ser revisada.

## Tratamento proposto
Preservar arquivo original; gerar hash, identificador da carga e relatório de qualidade. Selecionar apenas campos necessários. Sinalizar datas inválidas e inconsistências cronológicas por campo, sem descartar todo o registro automaticamente. Não imputar sim/não em respostas ignoradas. Não imputar saída de UTI para reconstruir ocupação.

Dados individuais, identificadores, datas de nascimento e campos de texto livre não serão enviados ao LLM ou publicados. Consultas agregadas devem aplicar supressão configurável de grupos pequenos.

Pendente: hash do arquivo, auditoria cronológica completa, consistência entre campos, perfil territorial e definição final do recorte.

# U2/U4 — Agregações determinísticas e frontend local

## Entrada e decisão
Em 10/11/2026, o usuário aprovou o visual e autorizou continuar. Preservar o design, o mapa e a comparação entre estados/regiões. A aprovação visual não implica aceite das métricas incompletas ou autorização para modificar PROD.

## Escopo desta construção
Gerar snapshot local a partir do CSV original, com referência, cobertura declarada e hash. Usar UF de residência; registros sem UF reconhecida entram no Brasil e são contabilizados separadamente. Calcular crescimento, letalidade entre desfechos conhecidos e séries reais de 30 dias/12 meses. Exportar somente agregações; nenhuma linha individual ou identificador.

Frontend estático servido localmente, desacoplado do PostgreSQL. Esta é uma etapa de validação da interface e dos cálculos; banco, agente LLM, notícias e implantação continuam pendentes. Resumo determinístico deve ser identificado como tal.

## Regras
- Datas das janelas inclusivas e referência comum para todos os territórios.
- Cobertura é parâmetro declarado, não deduzida do máximo para transformar ausência de dados em zero. Janela fora da cobertura recebe indisponível.
- Métricas anuais usam a mesma janela dos 12 meses, por início dos sintomas.
- Linhas estruturais inválidas, datas inválidas e registros fora de cobertura são contados.
- Zero permanece zero; ausência de cobertura e supressão são valores nulos com motivos diferentes.
- Supressão primária para contagens positivas menores que 5. Métricas com categorias pequenas ficam indisponíveis, sem exportar seus numeradores. Isso não é garantia formal contra inferência entre agregados sobrepostos.
- Snapshot é restrito ao desenvolvimento local e ignorado pelo Git. Publicação exige avaliação de supressão complementar e inferência temporal/geográfica antes de liberar dados. Sem recortes municipais nesta etapa.
- Ocupação de UTI e cobertura vacinal populacional continuam indisponíveis. Não substituí-las por proxies silenciosos.

## Critérios de verificação
Testes sintéticos de limites das janelas, zeros, supressão, desconhecidos, UF ausente, taxas e denominador zero. Conciliação independente com o CSV real. Navegador: mapa, troca de nível, comparação, erro de carga, resumo determinístico, série com lacunas e responsividade. Preservar o protótipo aprovado como referência.

## Resultado desta etapa
Construção local validada em 10/11/2026: 12 testes Python, conciliação independente do CSV e smoke test em Edge passaram. Evidências no registro AI-DLC. Não considerar U2/U4 integralmente concluídas: integração PostgreSQL/API, estados assíncronos do agente e avaliação de liberação pública ainda pendentes.

# Preparação do envio - desafio Artificial Intelligence Engineer

## Situação da entrega

**Material pronto para envio em 13/11/2026.** A v7 foi implantada e validada em HML: relatório completo, histórico conferido, narrativa legada retirada, sem avisos ou erros. O novo relatório também foi revisado publicamente em desktop/celular, sem novas chamadas ao modelo. Limitações do CSV e da demonstração permanecem explícitas.

## Links para o avaliador

- Repositório público: https://github.com/Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as
- Demonstração HTTPS, sem senha: https://poc-srag.estacaolab.com.br/
- Relatório final validado: https://poc-srag.estacaolab.com.br/api/reports/d55a99bf5d54456e9c89442fcc25e9e6/html
- PDF conceitual: https://github.com/Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as/blob/main/output/pdf/arquitetura-conceitual-srag.pdf
- README: instruções, contrato de indicadores, arquitetura e execução.
- Matriz do desafio: aidlc-docs/delivery-review.md.
- Registro AI-DLC e evidências: aidlc-docs/progress.md.

O exemplo final é d55a99bf5d54456e9c89442fcc25e9e6, prompt srag-2019-v7-grounded-history. O relatório antigo 62a21130022b4e8296737c20a2de4972 teve sua narrativa retirada da projeção pública, confirmado pelo teste HML. Seus arquivos originais permanecem preservados para auditoria.

## Roteiro de avaliação

1. Abrir a demonstração e conferir referência histórica, última carga e indicadores.
2. Comparar UFs ou regiões pelo mapa e pelos menus. Conferir atualização de cards, séries, qualidade e resumo.
3. Conferir gráficos de trinta dias/doze meses, tooltips e distinção entre zero, desconhecido e suprimido.
4. Gerar um relatório somente se houver quota disponível. Falhas de quota ou validação são explícitas; não significam ausência de dados.
5. Ler definições, limitações, referências e auditoria do relatório novo. O histórico vem de regras verificáveis; o LLM comenta títulos/resumos atuais em seção separada.
6. Consultar PDF, testes e decisões AI-DLC no repositório.

## Texto para o envio

Assunto: Entrega do desafio - Artificial Intelligence Engineer - PoC SRAG

Olá,

Compartilho minha solução para o desafio de Artificial Intelligence Engineer:

Repositório: https://github.com/Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as

Demonstração: https://poc-srag.estacaolab.com.br/

Relatório de exemplo: https://poc-srag.estacaolab.com.br/api/reports/d55a99bf5d54456e9c89442fcc25e9e6/html

A PoC utiliza o CSV histórico de SRAG de 2019 do Open DATASUS, com processamento em Python, agregações no PostgreSQL, dashboard interativo e orquestrador com ferramentas de métricas, séries e notícias. Os relatórios incluem dois gráficos, proveniência, limitações e auditoria. O desenvolvimento segue AI-DLC, com decisões e evidências documentadas.

O README apresenta instruções de reprodução, testes, arquitetura e o link para o diagrama conceitual em PDF. Também registra uma limitação do escopo exclusivo do CSV: ocupação operacional de UTI, cobertura vacinal populacional e mortalidade populacional não podem ser calculadas diretamente. Os indicadores auxiliares entre casos estão identificados com suas definições e denominadores, sem serem apresentados como equivalentes aos indicadores populacionais.

Obrigado.

## Aceite final registrado

- Operador confirmou v7 completa: três ferramentas, cinco notícias, dezesseis eventos e nenhuma rejeição ou erro do provedor.
- Histórico conferido pelas regras; leitura do novo texto não encontrou as extrapolações do relatório anterior.
- Narrativa legada retirada sem apagar evidências originais.
- Revisão pública somente leitura passou em 360/1100px, com dois gráficos, comparação SP x MG e zero erros JavaScript. Caminhos de dados locais, .env e código retornaram 404.
- PDF e links de exemplo atualizados para o resultado final. Repositório e demonstração são públicos; quotas e risco residual de inferência documentados.

Este documento prepara a mensagem; nenhum envio ao avaliador foi realizado.

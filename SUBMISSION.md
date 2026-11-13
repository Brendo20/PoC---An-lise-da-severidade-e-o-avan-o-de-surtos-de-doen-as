# Preparação do envio - desafio Artificial Intelligence Engineer

## Situação da entrega

Material preparado em 13/11/2026. **Aguardar o aceite da correção semântica v7 em HML antes de enviar.** A leitura final encontrou inferências indevidas no relatório antigo, embora ele tivesse passado no validador anterior. Correção, regressões e tratamento de relatórios legados estão no código; a implantação ainda não foi confirmada.

## Links para o avaliador

- Repositório público: https://github.com/Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as
- Demonstração HTTPS, sem senha: https://poc-srag.estacaolab.com.br/
- PDF conceitual: https://github.com/Brendo20/PoC---An-lise-da-severidade-e-o-avan-o-de-surtos-de-doen-as/blob/main/output/pdf/arquitetura-conceitual-srag.pdf
- README: instruções, contrato de indicadores, arquitetura e execução.
- Matriz do desafio: aidlc-docs/delivery-review.md.
- Registro AI-DLC e evidências: aidlc-docs/progress.md.

Não usar o relatório antigo 62a21130022b4e8296737c20a2de4972 como exemplo final. Após o rebuild, sua narrativa será retirada da projeção pública por incompatibilidade com a regra semântica atual. Os arquivos originais permanecem preservados na VM.

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

A PoC utiliza o CSV histórico de SRAG de 2019 do Open DATASUS, com processamento em Python, agregações no PostgreSQL, dashboard interativo e orquestrador com ferramentas de métricas, séries e notícias. Os relatórios incluem dois gráficos, proveniência, limitações e auditoria. O desenvolvimento segue AI-DLC, com decisões e evidências documentadas.

O README apresenta instruções de reprodução, testes, arquitetura e o link para o diagrama conceitual em PDF. Também registra uma limitação do escopo exclusivo do CSV: ocupação operacional de UTI, cobertura vacinal populacional e mortalidade populacional não podem ser calculadas diretamente. Os indicadores auxiliares entre casos estão identificados com suas definições e denominadores, sem serem apresentados como equivalentes aos indicadores populacionais.

Obrigado.

## Último gate antes de encaminhar

- Implantar a revisão v7 e executar check_agent_hml.py; confirmar complete e narrativa validada.
- Ler a narrativa do novo relatório e confirmar ausência de inferências de proteção vacinal ou estabilidade não medidas.
- Confirmar que o relatório legado aparece parcial/com narrativa retirada, sem apagar seus arquivos originais.
- Atualizar o registro AI-DLC com o novo report_id e, se desejado, acrescentar o link do relatório novo a esta entrega.
- Conferir que o último commit está no GitHub e que os três links acima abrem para o avaliador.

Este documento prepara a mensagem; nenhum envio ao avaliador foi realizado.

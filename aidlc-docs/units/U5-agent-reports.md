# U5 — Agente Groq, notícias e relatório

## Entrada
Usuário autorizou avançar após validar GROQ_API_KEY e openai/gpt-oss-20b na VM. Autenticação funcionou com User-Agent explícito. Manter a chave exclusivamente na VM. API e PostgreSQL já validados em HML pelo operador.

## Desenho funcional e limites
Agente com loop limitado de function calling: consultar_metricas, consultar_series e buscar_noticias, sem argumentos livres. Territórios e snapshot são fixados pelo backend a partir da seleção validada. Nenhuma ferramenta aceita SQL ou URL arbitrários. No máximo três rodadas de ferramentas, seguidas da análise estruturada sem ferramentas; até uma tentativa de correção da saída. Não registrar raciocínio interno.

Correção após teste real em HML: uma ferramenta por rodada, `parallel_tool_calls=false`, conforme capacidade documentada do GPT-OSS. O prompt não solicita paralelismo. Auditoria registra HTTP e código do provedor em allowlist, sem mensagem bruta ou `failed_generation`. Aceite continua dependente da nova execução completa na VM.

Após persistir HTTP 400/tool_use_failed com paralelismo desativado, desenho revisado para workflow prescrito: uma ferramenta oferecida por rodada, selecionada explicitamente por nome em tool_choice. Ordem obrigatória métricas, séries e notícias; retorno deve corresponder à ferramenta oferecida, mesmo se outras estiverem pendentes. Coleta usa prompt curto específico. Redação usa prompt próprio e conversa nova com as evidências. Isso substitui a escolha de ordem pelo modelo. Não afirmar causa textual exata da geração rejeitada, pois failed_generation não foi retido. Novo aceite real continua pendente.

Após três rodadas reais bem-sucedidas, a redação retornou 429/rate_limit_exceeded. Coletas passaram a usar contextos independentes, sem acumular resultados anteriores, e orçamento de saída de 512 tokens por etapa. A redação mantém métricas e notícias compactas; séries completas preservadas no relatório/gráficos, sem necessidade de enviá-las ao LLM. Retry-After numérico válido é registrado para orientar espera; sem reenvio automático. Não confundir testes locais com disponibilidade real de quota ou aceite da narrativa.

Métricas e gráficos são construídos deterministicamente com os resultados do banco. O modelo produz apenas comentários qualitativos, sem algarismos, percentuais, URLs ou markup; tendências de crescimento devem concordar com os dados. Referências devem existir no retorno da ferramenta. Saída inválida não é publicada: o relatório fica parcial, com dados verificados e motivo explícito. Esta validação não prova ausência de toda inferência textual equivocada.

Notícias: feeds fixos do Ministério da Saúde e Fiocruz; descoberta adicional por Google News RSS. Janela recente de trinta dias, data válida, relevância SRAG/InfoGripe, tamanho e quantidade limitados. URLs de artigos não são buscadas pelo servidor; quando agregadas via Google News, o link é identificado como de descoberta. Notícias atuais ficam em seção separada, sem explicar causalmente casos de 2019. Falha ou ausência de notícias é declarada, não preenchida por invenção. A leitura é de títulos/resumos, sem alegar leitura integral das matérias.

## Governança
Uma geração simultânea e intervalo mínimo entre chamadas novas; cache de cinco minutos por seleção/carga/modelo. Eventos e hashes de resultados em JSONL por execução; métricas, séries, fontes e saída validada preservadas no relatório. Auditoria e relatórios em volume persistente privado. Não conter DSNs, chave, registros individuais ou raciocínio interno. IDs gerados pelo servidor e caminhos em allowlist.

POST /api/reports recebe seleção e snapshot esperados. Se a carga ativa divergir, HTTP 409 pede atualização da tela antes de gastar quota. Geração só por ação explícita; trocar filtro invalida a apresentação da resposta anterior. GET de HTML contém indicadores, limitações, os dois gráficos, tabelas acessíveis, notícias e proveniência, sem JavaScript.

## Aceite e validação
Testar provider sem chamada externa real, cabeçalhos/erro sanitizado/limites; parse RSS/RDF/Atom e conteúdo malicioso; tool calls desconhecidas/argumentos e limite; tendências e saída inválida; escape HTML; snapshot fixado; persistência de auditoria; falhas e cache; integração da interface e alteração de filtro durante geração. Testar feeds públicos reais separadamente. Execução real do LLM depende da VM e não será inferida a partir de testes com mocks.

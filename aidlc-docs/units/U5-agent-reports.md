# U5 — Agente Groq, notícias e relatório

## Entrada
Usuário autorizou avançar após validar GROQ_API_KEY e openai/gpt-oss-20b na VM. Autenticação funcionou com User-Agent explícito. Manter a chave exclusivamente na VM. API e PostgreSQL já validados em HML pelo operador.

## Desenho funcional e limites
Agente com loop limitado de function calling: consultar_metricas, consultar_series e buscar_noticias, sem argumentos livres. Territórios e snapshot são fixados pelo backend a partir da seleção validada. Nenhuma ferramenta aceita SQL ou URL arbitrários. No máximo três rodadas de ferramentas, seguidas da análise estruturada sem ferramentas; até uma tentativa de correção da saída. Não registrar raciocínio interno.

Correção após teste real em HML: uma ferramenta por rodada, `parallel_tool_calls=false`, conforme capacidade documentada do GPT-OSS. O prompt não solicita paralelismo. Auditoria registra HTTP e código do provedor em allowlist, sem mensagem bruta ou `failed_generation`. Aceite continua dependente da nova execução completa na VM.

Após persistir HTTP 400/tool_use_failed com paralelismo desativado, desenho revisado para workflow prescrito: uma ferramenta oferecida por rodada, selecionada explicitamente por nome em tool_choice. Ordem obrigatória métricas, séries e notícias; retorno deve corresponder à ferramenta oferecida, mesmo se outras estiverem pendentes. Coleta usa prompt curto específico. Redação usa prompt próprio e conversa nova com as evidências. Isso substitui a escolha de ordem pelo modelo. Não afirmar causa textual exata da geração rejeitada, pois failed_generation não foi retido. Novo aceite real continua pendente.

Após três rodadas reais bem-sucedidas, a redação retornou 429/rate_limit_exceeded. Coletas passaram a usar contextos independentes, sem acumular resultados anteriores, e orçamento de saída de 512 tokens por etapa. A redação mantém métricas e notícias compactas; séries completas preservadas no relatório/gráficos, sem necessidade de enviá-las ao LLM. Retry-After numérico válido é registrado para orientar espera; sem reenvio automático. Não confundir testes locais com disponibilidade real de quota ou aceite da narrativa.

Após resposta real sem erro de provedor, diagnóstico isolado retornou unverified_narrative_claim. Esse código antigo agrupava cinco categorias e não permite identificar qual ocorreu. Revisão v5 separa números, marcação/URL, padrão de credencial, termos de eficácia e termos causais, com campo de comentário. Mesmo padrão de bloqueio anterior, incluindo frases negativas. Prompt explicita restrições lexicais; reparo recebe categoria/campo e JSON anterior apenas em memória. Auditoria não registra rascunho, trecho ou raciocínio. Aceite real da narrativa permanece aberto até execução validada.

v5 confirmou narrative_numbers em current_commentary nas duas tentativas. v6 acrescenta pattern regular simples aos dois campos no schema estrito; números e IDs permanecem permitidos em campos próprios. Não substituir referências, apagar números depois da geração ou aceitar texto reprovado. Sondagem independente check_narrative_schema_hml.py reutiliza um relatório salvo e testa uma única redação antes do rebuild; não promove relatório nem repete ferramentas. Compatibilidade real do pattern com o provedor é gate explícito, sem alegar prova pelos testes locais.

Resultado da sondagem: HTTP 400/json_validate_failed. Pattern retirado do schema implantável; v6 não foi aceita nem implantada. Diagnóstico --inspect-numbers usa schema sem pattern e mostra apenas trechos numéricos limitados com ocultação de credenciais, sem salvar rascunho. Motivo exato de cada número precisa de evidência antes de rever a política textual. Serviço em execução permanece na v5.

Métricas e gráficos são construídos deterministicamente com os resultados do banco. O modelo produz apenas comentários qualitativos, sem algarismos, percentuais, URLs ou markup; tendências de crescimento devem concordar com os dados. Referências devem existir no retorno da ferramenta. Saída inválida não é publicada: o relatório fica parcial, com dados verificados e motivo explícito. Esta validação não prova ausência de toda inferência textual equivocada.

Notícias: feeds fixos do Ministério da Saúde e Fiocruz; descoberta adicional por Google News RSS. Janela recente de trinta dias, data válida, relevância SRAG/InfoGripe, tamanho e quantidade limitados. URLs de artigos não são buscadas pelo servidor; quando agregadas via Google News, o link é identificado como de descoberta. Notícias atuais ficam em seção separada, sem explicar causalmente casos de 2019. Falha ou ausência de notícias é declarada, não preenchida por invenção. A leitura é de títulos/resumos, sem alegar leitura integral das matérias.

## Governança
Uma geração simultânea e intervalo mínimo entre chamadas novas; cache de cinco minutos por seleção/carga/modelo. Eventos e hashes de resultados em JSONL por execução; métricas, séries, fontes e saída validada preservadas no relatório. Auditoria e relatórios em volume persistente privado. Não conter DSNs, chave, registros individuais ou raciocínio interno. IDs gerados pelo servidor e caminhos em allowlist.

POST /api/reports recebe seleção e snapshot esperados. Se a carga ativa divergir, HTTP 409 pede atualização da tela antes de gastar quota. Geração só por ação explícita; trocar filtro invalida a apresentação da resposta anterior. GET de HTML contém indicadores, limitações, os dois gráficos, tabelas acessíveis, notícias e proveniência, sem JavaScript.

## Aceite e validação
Testar provider sem chamada externa real, cabeçalhos/erro sanitizado/limites; parse RSS/RDF/Atom e conteúdo malicioso; tool calls desconhecidas/argumentos e limite; tendências e saída inválida; escape HTML; snapshot fixado; persistência de auditoria; falhas e cache; integração da interface e alteração de filtro durante geração. Testar feeds públicos reais separadamente. Execução real do LLM depende da VM e não será inferida a partir de testes com mocks.

### Resultado real confirmado pelo operador

Em 12/11/2026, check_agent_hml.py na VM retornou complete para o relatório 62a21130022b4e8296737c20a2de4972. Três rodadas de ferramentas, cinco notícias, narrativa validada, nenhum aviso ou erro de provedor. Prompt v5-targeted-repair, snapshot srag-ec77679e6022ca66-2019-12-28-v1.0.0 e carga 2026-11-12T12:45:32.573171+00:00. Primeira redação rejeitada por números em current_commentary; segunda aceita. Dezoito eventos de auditoria.

Gate de integração real atendido nessa execução: o teste confere métricas, séries e dois gráficos. Pendem leitura humana da narrativa e validação visual do relatório no ambiente real. Não equivale a autorização de divulgação pública dos dados ou a garantia de que todas as gerações futuras serão completas. Evidência comunicada pelo operador, distinta dos sessenta testes Python locais.

### Gate semântico reaberto em 13/11/2026

Revisão pública confirmou acesso, filtros e gráficos, mas encontrou no comentário histórico do relatório antigo estabilidade de indicadores e impacto da vacinação que não são demonstrados pelo recorte. Guardrails anteriores de schema, números, palavras e tendências eram insuficientes para essa afirmação livre. Não considerar a narrativa antiga semanticamente aprovada.

v7 calcula historical_commentary a partir da direção do crescimento realmente disponível e de explicações fixas dos denominadores/limites. O campo usa enum com o texto permitido e o validador exige igualdade exata. Esse trecho histórico é explicitamente determinístico; o LLM comenta notícias atuais em campo separado. Não atribuir autoria livre desse trecho ao modelo. Relatórios antigos incompatíveis são projetados como parciais, com narrativa retirada no JSON/HTML público e arquivo original preservado. Três regressões semânticas adicionadas; novo aceite em HML pendente.

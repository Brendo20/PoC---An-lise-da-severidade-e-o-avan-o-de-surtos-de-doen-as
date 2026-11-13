"""Gera o diagrama conceitual versionado. Requer reportlab, sem credenciais ou dados reais.

Executar: python build_architecture_pdf.py
Saída: output/pdf/arquitetura-conceitual-srag.pdf
"""
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'output/pdf/arquitetura-conceitual-srag.pdf'
FONT_DIR = Path(reportlab.__file__).resolve().parent / 'fonts'
pdfmetrics.registerFont(TTFont('Vera', str(FONT_DIR / 'Vera.ttf')))
pdfmetrics.registerFont(TTFont('Vera-Bold', str(FONT_DIR / 'VeraBd.ttf')))
W, H = landscape(A4)
INK, MUTED, BLUE = '#172D45', '#536780', '#235DB5'
LINE, BG, PURPLE, ORANGE = '#D8E1ED', '#F5F8FC', '#7050A0', '#8D631D'


def paragraph(c, text, x, y_top, width, size=9, color=INK, bold=False, max_height=None):
    style = ParagraphStyle('body', fontName='Vera-Bold' if bold else 'Vera', fontSize=size,
                           leading=size * 1.45, textColor=colors.HexColor(color), alignment=TA_LEFT)
    p = Paragraph(text, style)
    _, height = p.wrap(width, H)
    if max_height is not None and height > max_height:
        raise ValueError(f'Text does not fit: {text[:70]} ({height:.1f} > {max_height})')
    p.drawOn(c, x, y_top - height)
    return height


def box(c, x, y, width, height, title, body, accent=BLUE, fill='#FFFFFF', dashed=False):
    c.setFillColor(colors.HexColor(fill))
    c.setStrokeColor(colors.HexColor(accent))
    c.setLineWidth(.85)
    c.setDash(4, 3) if dashed else c.setDash()
    c.roundRect(x, y, width, height, 8, fill=1, stroke=1)
    c.setDash()
    title_height = paragraph(c, escape(title), x + 11, y + height - 10, width - 22,
                             size=10, bold=True, color=accent)
    paragraph(c, body, x + 11, y + height - 16 - title_height, width - 22,
              size=8, max_height=height - title_height - 20)


def arrow(c, points, color=BLUE, dashed=False):
    c.setStrokeColor(colors.HexColor(color))
    c.setFillColor(colors.HexColor(color))
    c.setLineWidth(1.15)
    c.setDash(4, 3) if dashed else c.setDash()
    p = c.beginPath(); p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    c.drawPath(p)
    c.setDash()
    (ax, ay), (bx, by) = points[-2:]
    import math
    angle = math.atan2(by - ay, bx - ax)
    p = c.beginPath(); p.moveTo(bx, by)
    for offset in (-.45, .45):
        p.lineTo(bx - 6 * math.cos(angle + offset), by - 6 * math.sin(angle + offset))
    p.close(); c.drawPath(p, fill=1, stroke=0)


def header(c, page, title, subtitle):
    c.setFillColor(colors.HexColor(BG)); c.rect(0, 0, W, H, fill=1, stroke=0)
    paragraph(c, 'INDICIUM / PoC SRAG', 32, H - 23, 600, 8.5, BLUE, True)
    paragraph(c, title, 32, H - 44, W - 64, 20, bold=True)
    paragraph(c, subtitle, 32, H - 76, W - 64, 8.5, MUTED)
    c.setStrokeColor(colors.HexColor(LINE)); c.line(32, 27, W - 32, 27)
    paragraph(c, 'AI-DLC | Arquitetura implementada e evidência de HML | Revisão: 13/11/2026', 32, 20, W - 120, 7, MUTED)
    paragraph(c, f'{page} / 2', W - 65, 20, 40, 7, MUTED)


def architecture(c):
    header(c, 1, 'Arquitetura conceitual da solução',
           'Agente principal, ferramentas, LLM, banco de dados e notícias. Setas representam chamadas; resultados retornam ao solicitante.')
    # Contorno apenas do container da aplicação; não engloba serviços externos.
    c.setStrokeColor(colors.HexColor(LINE)); c.setFillColor(colors.HexColor('#EDF3FC'))
    c.roundRect(205, 145, 385, 357, 12, fill=1, stroke=1)
    paragraph(c, 'CONTAINER API / VM ORACLE HML', 220, 162, 350, 7, MUTED, True)

    box(c, 32, 440, 145, 60, 'Profissional de saúde', 'Dashboard no navegador<br/>Filtros: Brasil, UF ou região')
    box(c, 225, 435, 155, 65, 'API FastAPI', 'Serve interface e endpoints<br/>Fixa seleção e snapshot')
    box(c, 225, 325, 155, 78, 'Agente principal', 'Orquestrador Python<br/>Workflow obrigatório<br/>Uma ferramenta por etapa')
    box(c, 415, 360, 155, 65, 'Tool: métricas', 'consultar_metricas<br/>Agregados por território')
    box(c, 415, 275, 155, 65, 'Tool: séries', 'consultar_series<br/>30 dias e 12 meses')
    box(c, 415, 190, 155, 65, 'Tool: notícias', 'buscar_noticias<br/>Até cinco títulos/resumos')
    box(c, 225, 190, 155, 70, 'Relatório validado', 'Histórico por regras<br/>Notícias: comentário do LLM<br/>HTML / JSON + dois gráficos')

    box(c, 640, 425, 169, 75, 'LLM externo / Groq', 'openai/gpt-oss-20b<br/>Function calling + redação<br/>Chave somente no backend', PURPLE, '#F6F1FC')
    box(c, 640, 295, 169, 97, 'PostgreSQL 16 / VM', 'Banco exclusivo da PoC<br/>Snapshot e loaded_at<br/>Reader: somente SELECT<br/>Consultas parametrizadas', BLUE)
    box(c, 640, 173, 169, 101, 'Fontes externas / HTTPS', 'Ministério da Saúde<br/>Agência Fiocruz<br/>Google News RSS (descoberta)<br/>URLs de feeds fixas', ORANGE, '#FCF7EE')
    box(c, 32, 190, 145, 88, 'Volume privado / VM', 'report.html e report.json<br/>audit.jsonl por execução<br/>Fora do repositório<br/>Sem dados individuais')
    box(c, 32, 330, 145, 76, 'HTTPS / Caddy', 'poc-srag.estacaolab.com.br<br/>HTTPS público, sem senha<br/>Caddy 2.11.7', BLUE, '#FFFFFF')

    arrow(c, [(177, 468), (225, 468)])
    paragraph(c, 'HTTP', 183, 484, 38, 7, MUTED)
    arrow(c, [(302, 435), (302, 403)])
    arrow(c, [(380, 390), (390, 390), (390, 430), (610, 430), (610, 467), (640, 467)], PURPLE)
    paragraph(c, 'HTTPS: coleta e narrativa', 420, 450, 190, 7.2, PURPLE)
    arrow(c, [(380, 365), (400, 365), (400, 392), (415, 392)])
    arrow(c, [(400, 365), (400, 307), (415, 307)])
    arrow(c, [(400, 307), (400, 222), (415, 222)])
    arrow(c, [(570, 392), (615, 392), (615, 365), (640, 365)])
    arrow(c, [(570, 307), (615, 307), (615, 325), (640, 325)])
    arrow(c, [(570, 222), (640, 222)], ORANGE)
    arrow(c, [(302, 325), (302, 260)])
    paragraph(c, 'Valida e renderiza', 310, 291, 91, 7.1, MUTED)
    arrow(c, [(225, 225), (177, 225)])
    paragraph(c, 'Grava', 181, 241, 40, 7, MUTED)
    paragraph(c, 'O LLM não executa SQL nem escolhe URLs. Respostas das tools são validadas antes do uso. '
              'A redação recebe métricas e notícias; gráficos usam as séries completas do banco.',
              32, 116, W - 64, 9, max_height=45)
    paragraph(c, 'Azul: serviços e dados da PoC. Roxo: inferência externa. Ocre: notícias externas. '
              'Acesso público via Caddy; banco e arquivos do volume permanecem na VM. API publica os relatórios por endpoint.',
              32, 69, W - 64, 8, MUTED, max_height=30)
    c.showPage()


def governance(c):
    header(c, 2, 'Dados, governança e critérios de aceite',
           'A carga histórica e as notícias atuais têm referências temporais distintas. Nenhuma notícia atual explica causalmente os casos de 2019.')
    steps = [
        ('1. Fonte histórica', 'Open DATASUS<br/>CSV de SRAG de 2019<br/>Dicionário e ficha'),
        ('2. Download auditado', 'Hash SHA-256 fixado<br/>Arquivo preservado<br/>Sem troca automática de base'),
        ('3. Agregação Python', 'Qualidade e categorias<br/>Brasil / UF / região<br/>Supressão de contagens 1 a 4'),
        ('4. Carga PostgreSQL', 'Loader exclusivo<br/>Migração e carga idempotente<br/>Snapshot + data da carga'),
        ('5. Consulta e relatório', 'Reader sem escrita<br/>Snapshot fixado na geração<br/>Tools + LLM + validação'),
    ]
    for i, (title, body) in enumerate(steps):
        x = 32 + i * 159
        box(c, x, 401, 140, 97, title, body)
        if i < 4:
            arrow(c, [(x + 140, 450), (x + 159, 450)])

    box(c, 32, 184, 248, 191, 'Auditoria e transparência',
        'Eventos por execução em JSONL.<br/><br/>'
        'Ferramenta solicitada, duração, hash do resultado, uso de tokens e decisões de validação.<br/><br/>'
        'Modelo, prompt, snapshot, referência histórica, carga e fontes preservados no relatório.<br/><br/>'
        'Não registrar chaves, DSNs, raciocínio interno ou rascunhos rejeitados.')
    box(c, 296, 184, 248, 191, 'Guardrails e operação',
        'Tools fechadas; SQL parametrizado. Histórico por regras com validação de igualdade. LLM comenta notícias.<br/><br/>'
        'Três etapas de coleta e uma redação; no máximo um reparo. Validação de texto, tendências e referências.<br/><br/>'
        'Uma geração simultânea, intervalo de um minuto e cache completo de cinco minutos.<br/><br/>'
        'Quota ou saída inválida: relatório parcial explícito. Um worker e uma réplica.')
    box(c, 560, 184, 248, 191, 'Escopo e limites dos indicadores',
        'Crescimento de casos e letalidade têm definições e denominadores explícitos.<br/><br/>'
        'Internação em UTI entre casos não mede ocupação operacional de leitos.<br/><br/>'
        'Vacinação entre casos não mede cobertura populacional nem eficácia.<br/><br/>'
        'Notícias: títulos/resumos recentes, sem leitura integral. Acesso sem autenticação; supressão primária não elimina risco de inferência.')
    box(c, 32, 49, 776, 113, 'Aceite final v7 / HML em 13/11/2026',
        'Relatório: d55a99bf5d54456e9c89442fcc25e9e6. Status complete; três tools; cinco notícias; dezesseis eventos.<br/>'
        'Histórico conferido; narrativa legada retirada; nenhum aviso, rejeição ou erro do provedor.<br/>'
        'O teste confere métricas iguais ao dashboard, séries de 30 dias e 12 meses e dois gráficos SVG no HTML.<br/>'
        'Revisão pública do novo resultado em desktop/celular aprovada; histórico por regras sem as inferências anteriores.<br/>'
        'Evidência informada pelo operador. Não equivale a garantia semântica integral, alta disponibilidade ou revisão completa de privacidade.<br/>'
        'Fontes de arquitetura: código em src/srag/, compose.hml.yml e decisões AI-DLC versionadas no repositório.',
        fill='#EDF5EF', accent='#366D4E')
    c.showPage()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(W, H), invariant=1)
    c.setTitle('Arquitetura conceitual - PoC SRAG Indicium')
    c.setAuthor('PoC SRAG - documentação técnica')
    c.setSubject('Orquestrador, ferramentas, Groq, PostgreSQL, notícias, auditoria e limites')
    architecture(c); governance(c); c.save()
    print(OUTPUT)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Erzeugt die Handbücher für die Pflege der Website (Spanisch und Englisch) als druckfertige PDFs.

Aufruf (auf dem Mac, mit reportlab aus vendor/py):
    PYTHONPATH=vendor/py python3 scripts/make_manual.py
Ergebnis: manual/Manual-pagina-web-ES.pdf, manual/Website-handbook-EN.pdf und README.md
(die README auf GitHub ist das spanische Handbuch, aus denselben Inhalten erzeugt)
Bildschirmfotos: manual/img/{es,en}-*.jpg
"""
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle, XPreformatted)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manual"
FOREST, CLAY, SAND, LINE, MUTED, INK = (colors.HexColor(c) for c in
                                        ("#173a2a", "#b8562e", "#f5efe3", "#e0d6c2", "#5a635c", "#1d231f"))
CODEBG = colors.HexColor("#f7f4ec")
W, H = A4
M = 20 * mm
REPO = "github.com/Kampuntin-Maikiuants/Kampuntin-Maikiuants.github.io"
# Beispiel für einen Erfahrungsbericht (Voluntariado)
EXAMPLE_TESTIMONIAL = """    - quote: >-
        Llegué para ayudar en el vivero y me fui habiendo aprendido muchísimo más.
      name: "Ana"
      meta: "Voluntariado · Alemania · 2026"
      photo: "/assets/img/fotos/testimonio-ana.jpg"
      text: |-
        Primer párrafo del relato.

        Segundo párrafo del relato."""
# DNS-Einträge für eine eigene Domain (GitHub Pages)
DNS = [["A", "@", "185.199.108.153"], ["A", "@", "185.199.109.153"], ["A", "@", "185.199.110.153"],
       ["A", "@", "185.199.111.153"], ["CNAME", "www", "kampuntin-maikiuants.github.io"]]
SITE = "kampuntin-maikiuants.github.io"

# ---------- Stile ----------
ST = {
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10.3, leading=14.6, textColor=INK, spaceAfter=6),
    "h1": ParagraphStyle("h1", fontName="Times-Bold", fontSize=23, leading=27, textColor=FOREST, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Times-Bold", fontSize=14.5, leading=18, textColor=FOREST, spaceBefore=12,
                         spaceAfter=5),
    "step": ParagraphStyle("step", fontName="Helvetica", fontSize=10.3, leading=14.4, textColor=INK),
    "num": ParagraphStyle("num", fontName="Helvetica-Bold", fontSize=10.5, leading=12, textColor=colors.white,
                          alignment=1),
    "note": ParagraphStyle("note", fontName="Helvetica", fontSize=9.8, leading=13.8, textColor=INK),
    "caption": ParagraphStyle("caption", fontName="Helvetica-Oblique", fontSize=8.8, leading=11.5, textColor=MUTED,
                              spaceBefore=3, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=9.4, leading=12.6, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=9.4, leading=12.6, textColor=FOREST),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=8.3, leading=11, textColor=INK),
    "toc0": ParagraphStyle("toc0", fontName="Helvetica-Bold", fontSize=10.5, leading=14, spaceBefore=4,
                           textColor=FOREST),
    "toc1": ParagraphStyle("toc1", fontName="Helvetica", fontSize=9.2, leading=11.8, leftIndent=14, textColor=INK),
}


def md(text):
    """Mini-Auszeichnung: **fett**, `code`, Sonderzeichen maskieren."""
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r'<font name="Courier" size="9" color="#93401f">\1</font>', t)
    return t


class Doc(BaseDocTemplate):
    def __init__(self, path, title, footer, **kw):
        super().__init__(str(path), pagesize=A4, leftMargin=M, rightMargin=M, topMargin=22 * mm,
                         bottomMargin=20 * mm, title=title, author="Kampuntin Maikiuants", **kw)
        self.footer = footer
        frame = Frame(M, 20 * mm, W - 2 * M, H - 42 * mm, id="f")
        self.addPageTemplates([PageTemplate("cover", [frame], onPage=self.cover_page),
                               PageTemplate("page", [frame], onPage=self.normal_page)])

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and getattr(f, "toc_level", None) is not None:
            self.notify("TOCEntry", (f.toc_level, f.getPlainText(), self.page))

    def cover_page(self, c, doc):
        c.saveState()
        c.setFillColor(FOREST)
        c.rect(0, H - 95 * mm, W, 95 * mm, fill=1, stroke=0)
        c.drawImage(str(ROOT / "assets/img/logo-256.png"), M, H - 48 * mm, 26 * mm, 26 * mm, mask="auto")
        c.setFillColor(colors.white)
        c.setFont("Times-Bold", 30)
        c.drawString(M, H - 66 * mm, doc.cover_title)
        c.setFont("Helvetica", 12.5)
        c.setFillColor(colors.HexColor("#f0c7a4"))
        c.drawString(M, H - 76 * mm, doc.cover_sub)
        c.setFillColor(colors.HexColor("#c9d3c7"))
        c.setFont("Helvetica", 10)
        c.drawString(M, H - 85 * mm, SITE)
        c.restoreState()

    def normal_page(self, c, doc):
        c.saveState()
        c.setStrokeColor(LINE)
        c.setLineWidth(.6)
        c.line(M, 14 * mm, W - M, 14 * mm)
        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        c.drawString(M, 9.5 * mm, self.footer)
        c.drawRightString(W - M, 9.5 * mm, str(doc.page))
        c.restoreState()


class Builder:
    def __init__(self, lang):
        self.lang = lang
        self.story = []
        self.fw = W - 2 * M

    def h1(self, text):
        self.story.append(PageBreak())
        p = Paragraph(md(text), ST["h1"])
        p.toc_level = 0
        self.story.append(p)

    def h2(self, text):
        p = Paragraph(md(text), ST["h2"])
        p.toc_level = 1
        p.keepWithNext = True
        self.story.append(p)

    def p(self, text):
        self.story.append(Paragraph(md(text), ST["body"]))

    def bullets(self, items):
        rows = [[Paragraph('<font color="#b8562e">•</font>', ST["step"]), Paragraph(md(i), ST["step"])]
                for i in items]
        t = Table(rows, colWidths=[6 * mm, self.fw - 6 * mm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
        self.story += [t, Spacer(1, 5)]

    def steps(self, items):
        rows = []
        for n, item in enumerate(items, 1):
            body = [Paragraph(md(item), ST["step"])] if isinstance(item, str) else item
            rows.append([Paragraph(str(n), ST["num"]), body])
        t = Table(rows, colWidths=[8 * mm, self.fw - 8 * mm])
        style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (1, 0), (1, -1), 8),
                 ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 3),
                 ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (0, -1), 0)]
        for r in range(len(rows)):
            style += [("BACKGROUND", (0, r), (0, r), CLAY), ("TOPPADDING", (0, r), (0, r), 2.5),
                      ("BOTTOMPADDING", (0, r), (0, r), 2.5), ("VALIGN", (0, r), (0, r), "TOP")]
        t.setStyle(TableStyle(style))
        self.story += [t, Spacer(1, 4)]

    def box(self, text, kind="tip"):
        label = {"tip": {"es": "Consejo", "en": "Tip"}, "warn": {"es": "Importante", "en": "Important"}}[kind][self.lang]
        bar = CLAY if kind == "warn" else colors.HexColor("#3d7a52")
        t = Table([[Paragraph(f'<b>{label}:</b> {md(text)}', ST["note"])]], colWidths=[self.fw])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SAND), ("LINEBEFORE", (0, 0), (0, -1), 3, bar),
                               ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                               ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        self.story += [Spacer(1, 3), t, Spacer(1, 8)]

    def code(self, text, title=None):
        txt = wrap_code(text.rstrip("\n")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cell = [XPreformatted(txt, ST["code"])]
        if title:
            cell.insert(0, Paragraph(f'<font name="Helvetica-Bold" size="8" color="#5a635c">{md(title)}</font>',
                                     ST["code"]))
        t = Table([[cell]], colWidths=[self.fw])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CODEBG), ("BOX", (0, 0), (-1, -1), .6, LINE),
                               ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                               ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
        self.story += [Spacer(1, 2), t, Spacer(1, 8)]

    def table(self, header, rows, widths):
        data = [[Paragraph(md(h), ST["cellb"]) for h in header]]
        data += [[Paragraph(md(c), ST["cell"]) for c in r] for r in rows]
        t = Table(data, colWidths=[w * self.fw for w in widths], repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), SAND), ("LINEBELOW", (0, 0), (-1, -1), .5, LINE),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 5)]))
        self.story += [t, Spacer(1, 9)]

    def img(self, name, caption, width=1.0):
        path = OUT / "img" / f"{self.lang}-{name}.jpg"
        from PIL import Image as PILImage
        iw, ih = PILImage.open(path).size
        w = self.fw * width
        im = Image(str(path), width=w, height=w * ih / iw)
        t = Table([[im]], colWidths=[w])
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .7, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        self.story.append(KeepTogether([t, Paragraph(md(caption), ST["caption"])]))


class MdBuilder:
    """Gleiche Schnittstelle wie Builder, schreibt aber Markdown (für die README auf GitHub)."""
    LABEL = {"tip": {"es": "Consejo", "en": "Tip"}, "warn": {"es": "Importante", "en": "Important"}}

    def __init__(self, lang):
        self.lang, self.lines, self.chapters = lang, [], []

    def h1(self, text):
        self.chapters.append(text)
        self.lines += ["", f"## {text}", ""]

    def h2(self, text):
        self.lines += ["", f"### {text}", ""]

    def p(self, text):
        self.lines += [text, ""]

    def bullets(self, items):
        self.lines += [f"- {i}" for i in items] + [""]

    def steps(self, items):
        self.lines += [f"{n}. {i}" for n, i in enumerate(items, 1)] + [""]

    def box(self, text, kind="tip"):
        self.lines += [f"> **{self.LABEL[kind][self.lang]}:** {text}", ""]

    def code(self, text, title=None):
        if title:
            path, _, rest = title.partition(" ")
            self.lines.append(f"`{path}` {rest}".rstrip())
        self.lines += ["```yaml", text.rstrip("\n"), "```", ""]

    def table(self, header, rows, widths):
        cell = lambda c: c.replace("|", "\\|")
        self.lines.append("| " + " | ".join(cell(h) for h in header) + " |")
        self.lines.append("|" + "---|" * len(header))
        self.lines += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
        self.lines.append("")

    def img(self, name, caption, width=1.0):
        self.lines += [f"![{caption}](manual/img/{self.lang}-{name}.jpg)", f"_{caption}_", ""]


def slug(text):
    """Anker wie bei GitHub: klein, Satzzeichen weg, Leerzeichen zu Bindestrichen."""
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def build_md(lang, filename, T):
    b = MdBuilder(lang)
    T["content"](b)
    head = [f"# {T['title']}", "", T["cover_lead"], "", T["readme_links"], "", f"**{T['toc_title']}**", ""]
    head += [f"- [{c}](#{slug(c)})" for c in b.chapters]
    (ROOT / filename).write_text("\n".join(head + b.lines).rstrip() + "\n", encoding="utf-8")
    print("geschrieben:", ROOT / filename)


def wrap_code(text, width=90):
    """Lange Code-Zeilen an Leerzeichen umbrechen; Folgezeilen etwas tiefer einrücken."""
    out = []
    for line in text.splitlines():
        indent = " " * (len(line) - len(line.lstrip()) + 4)
        while len(line) > width:
            cut = line.rfind(" ", 0, width)
            if cut <= len(indent):
                break
            out.append(line[:cut])
            line = indent + line[cut + 1:]
        out.append(line)
    return "\n".join(out)


def block(path, start_pat, stop_pat=None, max_lines=40):
    """Ausschnitt aus einer Datei (für Beispiele im Handbuch)."""
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    i = next(k for k, l in enumerate(lines) if re.match(start_pat, l))
    out = [lines[i]]
    for l in lines[i + 1:i + max_lines]:
        if stop_pat and re.match(stop_pat, l):
            break
        if l.lstrip().startswith("#"):
            continue
        out.append(re.sub(r"\s{2,}#.*$", "", l))
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def build(lang, filename, T):
    b = Builder(lang)
    doc = Doc(OUT / filename, T["title"], T["footer"])
    doc.cover_title, doc.cover_sub = T["cover_title"], T["cover_sub"]
    toc = TableOfContents()
    toc.levelStyles = [ST["toc0"], ST["toc1"]]
    toc.dotsMinLevel = 0
    toc.tableStyle = TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 1)])
    s = b.story
    s += [NextPageTemplate("page"), Spacer(1, 82 * mm)]
    s.append(Paragraph(md(T["cover_lead"]), ParagraphStyle("lead", parent=ST["body"], fontSize=12.5, leading=18)))
    s.append(Spacer(1, 6 * mm))
    s.append(Paragraph(md(T["cover_meta"]), ST["caption"]))
    s.append(PageBreak())
    s.append(Paragraph(T["toc_title"], ST["h1"]))
    s.append(toc)
    T["content"](b)
    doc.multiBuild(b.story)
    print("geschrieben:", OUT / filename)


# =====================================================================================
# Inhalte – Spanisch
# =====================================================================================
def es(b):
    b.h1("1. Antes de empezar")
    b.p("La página web de Kampuntin no necesita un servidor propio. Todos los textos, fotos y fechas están "
        "guardados en **GitHub**, un servicio gratuito. Cada vez que alguien guarda un cambio allí, la página se "
        "actualiza sola en uno a tres minutos.")
    b.h2("1.1 Las dos herramientas")
    b.table(["Herramienta", "Para qué", "Dirección"], [
        ["**GitHub**", "Todos los archivos de la página: textos, fotos, álbumes y ajustes.", REPO],
        ["**Pages CMS**", "Un formulario sencillo para las fechas de los tours y las plazas libres. "
                          "Funciona también desde el celular.", "app.pagescms.org"],
    ], [.17, .43, .40])
    b.h2("1.2 Crear tu acceso (una sola vez)")
    b.steps([
        "Crea una cuenta gratuita en **github.com** (botón «Sign up»). Usa un correo que revises con frecuencia.",
        "Envía tu nombre de usuario de GitHub a la persona que administra la página (hoy: Jesko Dorner).",
        "Esa persona te invita en GitHub: en el repositorio «Settings» › «Collaborators» › «Add people».",
        "Recibirás un correo de GitHub. Haz clic en «Accept invitation». Desde ese momento puedes editar.",
    ])
    b.box("GitHub está en inglés. En este manual los nombres de los botones aparecen entre comillas, tal como los "
          "ves en la pantalla, por ejemplo «Add file» o «Commit changes».")
    b.h2("1.3 Cómo se edita un archivo en GitHub")
    b.steps([
        f"Abre **{REPO}** e inicia sesión («Sign in»).",
        "Haz clic en las carpetas hasta llegar al archivo, por ejemplo `_data` › `es` › `home.yml`.",
        "Arriba a la derecha del archivo haz clic en el lápiz («Edit this file»).",
        "Cambia el texto.",
        "Haz clic en el botón verde «Commit changes…». En la ventana escribe en una línea qué cambiaste "
        "(por ejemplo «Nuevo precio del viaje Arutam») y confirma con «Commit changes».",
        "Espera uno a tres minutos y recarga la página web. Listo.",
    ])
    b.h2("1.4 ¿Ya está publicado?")
    b.p("En GitHub, la pestaña «Actions» muestra cada actualización de la página:")
    b.bullets(["**Círculo amarillo:** la página se está actualizando.",
               "**Marca verde:** listo, el cambio está en línea.",
               "**Cruz roja:** algo salió mal. La página sigue mostrando la versión anterior. Ver capítulo 7."])
    b.box("Si no ves el cambio, recarga la página con fuerza: en la computadora Ctrl + F5 (en Mac: Cmd + Shift + R).")
    b.h2("1.5 Tres idiomas")
    b.p("La página existe en español, inglés y francés. Casi todos los textos están en tres archivos con el mismo "
        "nombre en las carpetas `_data/es`, `_data/en` y `_data/fr`. **Cambia siempre los tres.** Si no sabes "
        "traducir, cambia el español y pide ayuda para los otros idiomas, o usa un traductor como DeepL.")
    b.h2("1.6 Reglas de oro para los archivos .yml")
    b.p("Los textos están en archivos con la terminación `.yml`. Son fáciles de leer, pero hay que respetar algunas "
        "reglas:")
    b.bullets([
        "No borres los espacios al principio de las líneas. La sangría indica qué pertenece a qué.",
        "Usa espacios, nunca la tecla Tab.",
        "Si un texto contiene dos puntos seguidos de un espacio, ponlo entre comillas: "
        "`\"Viaje Arutam: 22 días\"`.",
        "Para agregar algo nuevo, copia un bloque que ya existe, pégalo justo debajo y cambia los textos.",
        "Las líneas que empiezan con `#` son notas para quien edita. No aparecen en la página.",
    ])

    b.h1("2. Tours: fechas, plazas y aviso en la página de inicio")
    b.h2("2.1 Cómo funciona")
    b.p("Hay dos viajes: el **Viaje espiritual** (11 días) y el **Viaje Arutam** (22 días). Los viajes son de Raíces, que "
        "organiza el viaje y las reservas; en Maikiuants, Kampuntin se encarga de la organización y el acompañamiento. El nombre, la duración, el precio y la "
        "descripción de cada viaje se guardan una sola vez. Las fechas se guardan aparte, y cada fecha dice a qué "
        "viaje pertenece.")
    b.img("viajes", "La sección «Dos viajes» en la página de tours. Abajo se pueden abrir los programas.")
    b.bullets([
        "**Fechas y plazas:** archivo `_data/tour_dates.yml`. Lo más fácil es usar Pages CMS (2.2).",
        "**Nombre, duración, precio y texto de cada viaje:** `_data/es/tours.yml` (y `en`, `fr`), bajo `trips` (2.5).",
        "**El aviso en la página de inicio** toma la próxima fecha automáticamente (2.4).",
    ])
    b.h2("2.2 Agregar una fecha nueva (con Pages CMS)")
    b.steps([
        "Abre **app.pagescms.org** e inicia sesión con «Sign in with GitHub».",
        "Elige el repositorio **Kampuntin-Maikiuants.github.io**.",
        "En el menú de la izquierda haz clic en **Fechas de tours**.",
        "Debajo de la última fecha, haz clic en el botón para agregar una entrada nueva (signo +).",
        "Llena los campos (ver la tabla).",
        "Haz clic en «Save». En uno a tres minutos la fecha aparece en la página de tours y, si es la próxima, "
        "también en el aviso de la página de inicio.",
    ])
    b.table(["Campo", "Qué escribir"], [
        ["Inicio", "Primer día del viaje (exacto o aproximado)."],
        ["Fin", "Último día del viaje."],
        ["Viaje", "Viaje espiritual (11 días) o Viaje Arutam (22 días)."],
        ["Texto en vez de la fecha", "Solo si la fecha aún no es exacta, por ejemplo «Abril / mayo 2027». "
                                     "En español, inglés y francés."],
        ["Nota pequeña", "Opcional, una línea debajo de la fecha, por ejemplo «Fecha exacta por confirmar»."],
        ["Plazas libres", "Cuántas plazas quedan. **0** = Completo. Vacío = se usa el Estado."],
        ["Estado", "Plazas a consultar · Plazas libres · Últimas plazas · Completo "
                   "(solo si «Plazas libres» está vacío)."],
    ], [.3, .7])
    b.img("fechas", "Así se ven los precios y las próximas fechas en la página de tours.")
    b.box("Las fechas pasadas desaparecen solas: cuando llega el día de inicio, la fecha ya no se muestra (la "
          "página se actualiza cada 6 horas). No hace falta borrarlas, pero puedes hacerlo para mantener la "
          "lista ordenada.")
    b.h2("2.3 Actualizar las plazas libres")
    b.steps([
        "Abre Pages CMS › **Fechas de tours**.",
        "En la fecha del viaje escribe en **Plazas libres** cuántas quedan (por ejemplo 12, y después de cada "
        "reserva un número menos).",
        "Haz clic en «Save». Con 3 plazas o menos el número se muestra en naranja; con **0** aparece «Completo».",
    ])
    b.p("Una fecha completa ya no aparece en el aviso de la página de inicio. El aviso muestra entonces la "
        "siguiente fecha con plazas.")
    b.h2("2.4 El aviso (pop-up) en la página de inicio")
    b.img("popup", "El aviso aparece abajo a la derecha, unos segundos después de abrir la página de inicio.")
    b.p("El aviso muestra siempre la próxima fecha que todavía no pasó y que no está completa, con el nombre del "
        "viaje, la duración y el precio. **No hay que cambiar nada para que se actualice.**")
    b.p("**Encender o apagar el aviso:**")
    b.steps([
        "En GitHub abre el archivo `_config.yml` (está en la carpeta principal) y haz clic en el lápiz.",
        "Busca la línea `tour_popup: true`.",
        "Escribe `false` para apagarlo o `true` para encenderlo y guarda con «Commit changes».",
    ])
    b.p("**Cambiar el texto o la foto del aviso:** en `_data/es/home.yml` (y `en`, `fr`), al final, en el bloque "
        "`tour_popup`. La foto (`image`) es una ruta a un archivo de la página.")
    b.code(block("_data/es/home.yml", r"^tour_popup:", r"^\S"), "_data/es/home.yml")
    b.h2("2.5 Cambiar el precio, la duración o la descripción de un viaje")
    b.steps([
        "En GitHub abre `_data/es/tours.yml` y haz clic en el lápiz.",
        "Busca `trips:`. Debajo están `espiritual` y `arutam`.",
        "Cambia `amount` (precio), `days` (duración), `when` (temporada) o `text` (descripción corta).",
        "Haz lo mismo en `_data/en/tours.yml` y `_data/fr/tours.yml`.",
        "Guarda con «Commit changes».",
    ])
    b.code(block("_data/es/tours.yml", r"^  espiritual:", r"^  arutam:"), "_data/es/tours.yml (fragmento)")
    b.p("El programa detallado (llegada, actividades y regreso) está en el mismo archivo: en `spiritual` para el "
        "viaje espiritual y en `experience` para el viaje Arutam.")
    b.box("Un viaje completamente nuevo (un tercer tipo de viaje) necesita un pequeño cambio técnico en la página. "
          "Para eso, contacta a la persona que administra la página.", "warn")

    b.h1("3. Galería: álbumes y fotos")
    b.h2("3.1 Cómo funciona")
    b.p("Cada álbum es una **carpeta** dentro de `assets/galeria`. Todas las fotos de la carpeta aparecen en el "
        "álbum. La primera foto (o la que elijas) es la portada. Los álbumes se ordenan por el nombre de la "
        "carpeta, de mayor a menor: por eso cada carpeta empieza con un número. Los tres primeros álbumes "
        "aparecen también abajo en la página de tours.")
    b.img("galeria", "La galería: cada tarjeta es un álbum. Un clic abre todas las fotos.")
    b.p("Las carpetas actuales van de `01` a `11`. Un álbum nuevo recibe el número siguiente (`12`, `13`, …) "
        "para aparecer primero.")
    b.h2("3.2 Preparar las fotos")
    b.bullets([
        "Formato **JPG**.",
        "Unos **1600 píxeles de ancho** y menos de **500 KB** por foto. Las fotos grandes hacen lenta la página.",
        "Para achicar fotos gratis: **squoosh.app** en el navegador, o una app para reducir fotos en el celular.",
        "Nombres sencillos, sin espacios ni acentos: `001.jpg`, `002.jpg`, … El orden de los números es el orden "
        "en el álbum.",
        "Pide permiso a las personas que aparecen en las fotos.",
    ])
    b.h2("3.3 Crear un álbum nuevo")
    b.steps([
        "En GitHub abre la carpeta `assets` › `galeria`.",
        "Haz clic en «Add file» › «Create new file».",
        "En el campo del nombre escribe el nombre de la carpeta, una barra `/` y `_LEEME.txt`, por ejemplo: "
        "`12-fiesta-de-la-chonta-2027/_LEEME.txt`. Al escribir la barra, GitHub crea la carpeta.",
        "En el contenido escribe una línea, por ejemplo «Álbum Fiesta de la Chonta 2027». Haz clic en "
        "«Commit changes…» y luego en «Commit changes».",
    ])
    b.h2("3.4 Subir las fotos")
    b.steps([
        "Abre la carpeta nueva (o un álbum que ya existe).",
        "Haz clic en «Add file» › «Upload files».",
        "Arrastra las fotos a la ventana o haz clic en «choose your files». Puedes subir varias a la vez.",
        "Abajo haz clic en «Commit changes» y espera a que termine la subida.",
        "En uno a tres minutos el álbum aparece en la galería.",
    ])
    b.box("El archivo `_LEEME.txt` no aparece en la página. Puedes dejarlo o borrarlo.")
    b.h2("3.5 Título bonito y portada")
    b.p("Sin más datos, el álbum usa el nombre de la carpeta como título. Para un título en tres idiomas y una "
        "portada elegida, abre `_data/albums.yml`, copia un bloque arriba de la lista y cámbialo:")
    b.code('- folder: 12-fiesta-de-la-chonta-2027\n'
           '  title: { es: "Fiesta de la Chonta 2027", en: "Chonta festival 2027", fr: "Fête de la Chonta 2027" }\n'
           '  cover: "004.jpg"', "_data/albums.yml (ejemplo)")
    b.bullets(["`folder`: el nombre exacto de la carpeta.", "`title`: el título en los tres idiomas.",
               "`cover`: el nombre de la foto de portada. Vacío (`\"\"`) = la primera foto."])
    b.h2("3.6 Borrar una foto o un álbum")
    b.steps([
        "Abre la foto en GitHub.",
        "Arriba a la derecha haz clic en los tres puntos «…» › «Delete file».",
        "Confirma con «Commit changes». Un álbum desaparece cuando ya no tiene fotos.",
    ])

    b.h1("4. Novedades: Facebook e Instagram")
    b.h2("4.1 Qué se ve en la página Novedades")
    b.img("novedades", "Arriba aparecen las cuentas de Facebook e Instagram como tarjetas.")
    b.p("La página muestra las cuentas de Facebook e Instagram como tarjetas. Si la importación automática está "
        "configurada (4.3), debajo aparecen también las publicaciones más recientes con texto y fotos. Las tres "
        "últimas aparecen además en la página de inicio.")
    b.p("El muro de Facebook no se puede mostrar directamente: Facebook solo lo muestra a personas que tienen la "
        "sesión iniciada en Facebook, y las demás verían un cuadro vacío. Por eso la página **importa** las "
        "publicaciones.")
    b.h2("4.2 Cambiar o agregar una cuenta")
    b.steps([
        "En GitHub abre `_config.yml` y haz clic en el lápiz.",
        "Busca `social:`.",
        "Cambia el nombre (`name`) o el enlace (`url`). Para otra cuenta de Facebook copia un bloque "
        "`- name: … url: …` y pégalo debajo.",
        "Guarda con «Commit changes». La tarjeta aparece en Novedades y en el pie de página.",
    ])
    b.code(block("_config.yml", r"^social:", r"^  wwoof:"), "_config.yml (fragmento)")
    b.h2("4.3 Mostrar las publicaciones automáticamente")
    b.p("Se configura una sola vez y toma unos 20 minutos. Después, la página busca publicaciones nuevas cada "
        "6 horas, sola.")
    b.box("Requisitos: tienen que ser **páginas de Facebook** (no perfiles personales) y quien lo configura tiene "
          "que ser administrador de esas páginas. Para Instagram, la cuenta tiene que ser profesional (empresa o "
          "creador) y estar vinculada a una de las páginas de Facebook.", "warn")
    b.steps([
        "Entra en **developers.facebook.com** con la cuenta de Facebook que administra las páginas. "
        "«My Apps» › «Create App», tipo «Business», nombre por ejemplo «Kampuntin Website».",
        "Abre «Tools» › «Graph API Explorer» y elige arriba la app nueva. En «Permissions» agrega "
        "`pages_show_list` y `pages_read_engagement`, y para Instagram también `instagram_basic` y "
        "`business_management`. Luego «Generate Access Token» y confirma.",
        "Abre «Tools» › «Access Token Debugger», pega el token, haz clic en «Debug» y abajo en "
        "«Extend Access Token». Copia el token largo.",
        "Vuelve al Graph API Explorer, pega el token largo y ejecuta la consulta `me/accounts`. La respuesta "
        "tiene un `access_token` para cada página. Estos tokens de página no vencen.",
        "En GitHub, en el repositorio: «Settings» › «Secrets and variables» › «Actions» › «New repository "
        "secret». Nombre: `FB_PAGE_TOKENS`. Valor: los tokens de página, uno por línea. Guarda con «Add secret».",
        "Pestaña «Actions» › «Website bauen & Social Media importieren» › «Run workflow». En uno a tres minutos "
        "aparecen las publicaciones.",
    ])
    b.h2("4.4 ¿Funciona la importación?")
    b.p("En «Actions» abre la última ejecución. Arriba, en «Annotations», hay un mensaje corto (en alemán):")
    b.bullets(["Amarillo «Kein Secret FB_PAGE_TOKENS gesetzt»: falta el paso 5.",
               "Rojo «Token Nr. 1: …»: el token es incorrecto o venció. Al lado está el mensaje de Facebook.",
               "Azul «… Beiträge geladen»: todo bien."])
    b.box("Si alguien cambia la contraseña de Facebook o quita los permisos de la app, los tokens dejan de "
          "funcionar: repite los pasos 2 a 5. Si en el repositorio no pasa nada durante 60 días, GitHub pausa la "
          "actualización automática: en «Actions» haz clic en «Enable workflow».")
    b.h2("4.5 Mostrar una publicación de Instagram a mano")
    b.steps([
        "Abre la publicación en Instagram y copia el enlace, por ejemplo `https://www.instagram.com/p/ABC123/`.",
        "En GitHub abre `_data/instagram_embeds.yml` y agrega una línea: `- https://www.instagram.com/p/ABC123/`",
        "Guarda con «Commit changes». La publicación aparece en Novedades. Se carga recién al hacer clic, para "
        "proteger la privacidad de las visitas.",
    ])

    b.h1("5. Equipo, textos y otras cosas útiles")
    b.h2("5.1 Agregar o cambiar una persona del equipo")
    b.img("equipo", "Las tarjetas del equipo en la página «Equipo».")
    b.steps([
        "Prepara una foto **cuadrada** (unos 600 × 600 píxeles, JPG) con la cara en el centro.",
        "Súbela a `assets` › `img` › `equipo` con «Add file» › «Upload files», con un nombre sencillo, por "
        "ejemplo `eddy.jpg`.",
        "Abre `_data/team.yml`, copia el bloque de una persona, pégalo y cámbialo (ver el ejemplo).",
        "Guarda con «Commit changes».",
    ])
    b.code('- name: "Eddy Ankuash"\n'
           '  group: kampuntin\n'
           '  photo: "/assets/img/equipo/eddy.jpg"\n'
           '  role: { es: "Secretario de Kampuntin", en: "Secretary of Kampuntin", fr: "Secrétaire de Kampuntin" }\n'
           '  bio:\n'
           '    es: "Texto corto en español."\n'
           '    en: "Short text in English."\n'
           '    fr: "Texte court en français."', "_data/team.yml (ejemplo)")
    b.bullets(["Opcional: `contact: true` muestra el enlace «Escríbenos» (solo para las personas de contacto).",
               "Opcional: `social:` agrega enlaces a Instagram o Facebook.",
               "Opcional: `shuar_name:` muestra el nombre shuar debajo del nombre."])
    b.box("Para cambiar una foto, sube la nueva con otro nombre (por ejemplo `eddy-2.jpg`) y cambia la línea "
          "`photo`. Así los navegadores muestran enseguida la foto nueva. Publica fotos y textos de personas solo "
          "con su permiso.")
    b.h2("5.2 ¿Dónde está cada texto?")
    b.table(["Página", "Archivo (en `_data/es`, `_data/en` y `_data/fr`)"], [
        ["Inicio", "`home.yml`"], ["Tours", "`tours.yml`"], ["Voluntariado", "`volunteering.yml`"],
        ["Ciencia", "`science.yml`"], ["Novedades", "`updates.yml`"], ["Galería (textos)", "`gallery.yml`"],
        ["Equipo (textos generales)", "`people.yml`"], ["Contacto", "`contact.yml`"], ["Aviso legal", "`legal.yml`"],
        ["Menú, botones y pie de página", "`ui.yml`"],
    ], [.38, .62])
    b.table(["Contenido compartido por los tres idiomas", "Archivo"], [
        ["Personas del equipo", "`_data/team.yml`"], ["Fechas de los tours", "`_data/tour_dates.yml`"],
        ["Álbumes (títulos y portadas)", "`_data/albums.yml`"], ["Videos", "`_data/videos.yml`"],
        ["Especies amenazadas", "`_data/species.yml`"],
        ["Correo, WhatsApp, personas de contacto, redes sociales, aviso encendido o apagado", "`_config.yml`"],
    ], [.62, .38])
    b.h2("5.3 Personas de contacto y WhatsApp")
    b.p("Las personas de la página de contacto y del pie de página están en `_config.yml`, bajo `contact:` › "
        "`people:`. Cada persona tiene nombre, función en tres idiomas, número de WhatsApp (solo cifras, con "
        "código de país, sin + ni espacios) y el teléfono tal como se muestra.")
    b.code(block("_config.yml", r"^    - name: Julien", r"^    - name: (?!Julien)", 6), "_config.yml (fragmento)")
    b.h2("5.4 Videos")
    b.p("**Videos cortos** (MP4, menos de 50 MB): súbelos a `assets/video` y agrégalos en `_data/videos.yml` "
        "(copia un bloque con `file`, `poster`, `title` y `text`). **Videos largos:** súbelos a YouTube y escribe "
        "solo el código del video en `youtube:`, por ejemplo `AbCdEf12345` de `https://youtu.be/AbCdEf12345`.")

    b.h2("5.5 Experiencias de voluntarios (testimonios)")
    b.img("testimonios", "Las experiencias en la página de voluntariado. Un clic en «Leer la experiencia completa» abre el relato.")
    b.p("En la página de voluntariado hay tarjetas con experiencias de personas que ya estuvieron en Maikiuants. Cada "
        "tarjeta tiene una cita corta que siempre se ve, el nombre, una línea pequeña (por ejemplo «Voluntaria · "
        "Alemania · 2026») y, si quieres, el relato completo para abrir y una foto pequeña.")
    b.steps([
        "Pide a la persona una cita corta (una a tres frases), cómo quiere aparecer (nombre, país, año), si quiere "
        "también un relato más largo y una foto. **Pide su permiso para publicarlo.**",
        "Opcional, la foto: cuadrada, con la cara en el centro, unos 300 × 300 píxeles. Súbela a `assets` › `img` › "
        "`fotos` con «Add file» › «Upload files», por ejemplo como `testimonio-ana.jpg`.",
        "En GitHub abre `_data/es/volunteering.yml` y haz clic en el lápiz. Busca `testimonials:` y debajo `items:`.",
        "Copia un bloque completo, desde `- quote:` hasta antes del siguiente `- quote:`, y pégalo arriba de la "
        "lista (la primera tarjeta es la más nueva). Cambia los textos (ver el ejemplo).",
        "Haz lo mismo en `_data/en/volunteering.yml` y `_data/fr/volunteering.yml`, con el texto traducido.",
        "Guarda con «Commit changes».",
    ])
    b.code(EXAMPLE_TESTIMONIAL, "_data/es/volunteering.yml (ejemplo de un bloque)")
    b.bullets([
        "`quote`: la cita corta. Deja `>-` tal cual y escribe el texto en la línea de abajo, con la misma sangría.",
        "`name` y `meta`: el nombre y la línea pequeña debajo.",
        "`photo`: la ruta de la foto, o vacío (`\"\"`) si no hay foto.",
        "`text`: el relato completo (opcional). Deja `|-` tal cual; una línea vacía separa los párrafos. Si no hay "
        "relato, borra las líneas de `text`; entonces no aparece el botón «Leer la experiencia completa».",
    ])
    b.box("Para quitar una experiencia, borra su bloque completo. Por ahora las experiencias aparecen solo en la "
          "página de voluntariado; para tenerlas también en la página de tours, pide ayuda a quien administra la "
          "página.")

    b.h1("6. Una dirección propia (dominio)")
    b.p("Hoy la página está en **kampuntin-maikiuants.github.io**. Con un dominio propio, por ejemplo "
        "**www.kampuntin.org**, la dirección es más corta y fácil de recordar. La página sigue gratis en GitHub; "
        "solo el dominio cuesta dinero.")
    b.h2("6.1 Elegir y comprar el dominio")
    b.steps([
        "Elige un nombre y una terminación, por ejemplo `kampuntin.org`, `kampuntin.com` o `kampuntin.ec`. En la "
        "página del proveedor puedes comprobar si todavía está libre.",
        "Cómpralo en un proveedor de dominios (registrador), por ejemplo Namecheap, Porkbun o Cloudflare. Para la "
        "terminación .ec también hay proveedores en Ecuador. Precio aproximado: 10 a 20 USD por año para .org o "
        ".com; otras terminaciones pueden costar más.",
        "Registra el dominio a nombre de Kampuntin, con un correo de la organización, y activa la renovación "
        "automática. Si el dominio vence, la página deja de verse con esa dirección.",
    ])
    b.box("Guarda bien los datos de acceso del proveedor y compártelos con una segunda persona de confianza. Sin "
          "acceso al proveedor no se puede renovar ni cambiar el dominio.", "warn")
    b.h2("6.2 Conectar el dominio con la página (DNS)")
    b.p("En la cuenta del proveedor, abre la configuración de DNS del dominio (se llama «DNS», «DNS records» o "
        "«Zona DNS») y crea estas entradas:")
    b.table(["Tipo", "Nombre (host)", "Valor"], DNS, [.18, .27, .55])
    b.p("Borra las otras entradas A o CNAME para `@` y `www` que el proveedor haya creado (por ejemplo para una "
        "página de espera).")
    b.box("Opcional, para conexiones IPv6: cuatro entradas AAAA para `@` con los valores `2606:50c0:8000::153`, "
          "`2606:50c0:8001::153`, `2606:50c0:8002::153` y `2606:50c0:8003::153`.")
    b.h2("6.3 Activar el dominio en GitHub")
    b.steps([
        "En GitHub, en el repositorio: «Settings» › «Pages».",
        "En «Custom domain» escribe tu dominio con www, por ejemplo `www.kampuntin.org`, y haz clic en «Save».",
        "GitHub comprueba el DNS. Puede tardar desde unos minutos hasta 48 horas. Cuando aparece «DNS check "
        "successful», marca «Enforce HTTPS». Si la casilla todavía está gris, espera unas horas y vuelve a intentarlo.",
        "Listo: la página se abre en la dirección nueva. La dirección antigua kampuntin-maikiuants.github.io lleva "
        "automáticamente a la nueva.",
    ])
    b.box("Recomendado: verifica el dominio en GitHub para que nadie más pueda usarlo con GitHub Pages. En la "
          "configuración de la organización Kampuntin-Maikiuants: «Settings» › «Pages» › «Add a domain», y sigue "
          "las instrucciones (es otra entrada DNS, de tipo TXT).")
    b.h2("6.4 Después del cambio")
    b.bullets([
        "Cambia la dirección en los perfiles de Facebook e Instagram, en WWOOF, en los volantes y en los códigos QR.",
        "Si las vistas previas en WhatsApp o Facebook todavía muestran la dirección antigua, escribe la dirección "
        "nueva en `_config.yml`, en la línea `url:` (quita el `#` del principio), por ejemplo "
        "`url: \"https://www.kampuntin.org\"`.",
        "Un correo con el dominio (por ejemplo info@kampuntin.org) se puede agregar después con un servicio de "
        "correo. Muchos proveedores de dominios ofrecen reenvío de correo gratis.",
    ])

    b.h1("7. Si algo sale mal")
    b.table(["Problema", "Qué hacer"], [
        ["La página no cambia", "Espera tres minutos y recarga con Ctrl + F5. Mira la pestaña «Actions»: "
                                "¿amarillo (trabajando), verde (listo) o rojo (error)?"],
        ["Cruz roja en «Actions»", "Casi siempre es un error en un archivo `.yml`: un espacio de más o de menos, "
                                   "o faltan comillas. Abre la ejecución roja: el mensaje dice el archivo y la "
                                   "línea. Corrige y guarda de nuevo. Mientras tanto la página sigue mostrando la "
                                   "última versión buena."],
        ["Borré algo por error", "Nada se pierde. En GitHub abre el archivo › «History», abre la versión anterior, "
                                 "copia el texto y pégalo de nuevo con el lápiz."],
        ["Una foto no aparece", "Revisa que el nombre en el archivo sea exactamente igual al de la foto, con "
                                "mayúsculas y la terminación (`.jpg` no es lo mismo que `.JPG`)."],
        ["Las publicaciones de Facebook ya no se actualizan", "Ver 4.4."],
    ], [.3, .7])
    b.p("**Ayuda:** Jesko Dorner · jesko.dorner@gmail.com")
    b.h2("Hoja resumen")
    b.table(["Tarea", "Dónde", "Herramienta"], [
        ["Fecha de tour nueva, plazas", "Fechas de tours", "Pages CMS"],
        ["Precio o texto de un viaje", "`_data/es|en|fr/tours.yml` › `trips`", "GitHub"],
        ["Aviso encendido o apagado", "`_config.yml` › `tour_popup`", "GitHub"],
        ["Texto o foto del aviso", "`_data/es|en|fr/home.yml` › `tour_popup`", "GitHub"],
        ["Álbum nuevo, subir fotos", "`assets/galeria/NN-nombre/`", "GitHub"],
        ["Título o portada de un álbum", "`_data/albums.yml`", "GitHub"],
        ["Cuentas de Facebook e Instagram", "`_config.yml` › `social`", "GitHub"],
        ["Publicaciones automáticas", "Secret `FB_PAGE_TOKENS`", "GitHub y Facebook"],
        ["Publicación de Instagram a mano", "`_data/instagram_embeds.yml`", "GitHub"],
        ["Persona del equipo", "`_data/team.yml` y `assets/img/equipo`", "GitHub"],
        ["Personas de contacto", "`_config.yml` › `contact`", "GitHub"],
        ["Videos", "`_data/videos.yml` y `assets/video`", "GitHub"],
        ["Experiencia de voluntario", "`_data/es|en|fr/volunteering.yml` › `testimonials`", "GitHub"],
        ["Dominio propio", "Proveedor de dominios (DNS) y «Settings» › «Pages»", "Proveedor y GitHub"],
    ], [.36, .44, .20])


# =====================================================================================
# Content – English
# =====================================================================================
def en(b):
    b.h1("1. Before you start")
    b.p("The Kampuntin website does not need its own server. All texts, photos and dates are stored on "
        "**GitHub**, a free service. Whenever someone saves a change there, the website updates itself within one "
        "to three minutes.")
    b.h2("1.1 The two tools")
    b.table(["Tool", "What for", "Address"], [
        ["**GitHub**", "All website files: texts, photos, albums and settings.", REPO],
        ["**Pages CMS**", "A simple form for tour dates and available places. Also works on a phone.",
         "app.pagescms.org"],
    ], [.17, .43, .40])
    b.h2("1.2 Getting access (once)")
    b.steps([
        "Create a free account on **github.com** («Sign up»). Use an email address you check regularly.",
        "Send your GitHub username to the person who manages the website (currently Jesko Dorner).",
        "That person invites you on GitHub: in the repository «Settings» › «Collaborators» › «Add people».",
        "You will receive an email from GitHub. Click «Accept invitation». From then on you can edit.",
    ])
    b.box("Button names appear in quotation marks exactly as you see them on screen, for example «Add file» or "
          "«Commit changes».")
    b.h2("1.3 How to edit a file on GitHub")
    b.steps([
        f"Open **{REPO}** and sign in («Sign in»).",
        "Click through the folders to the file, for example `_data` › `en` › `home.yml`.",
        "At the top right of the file, click the pencil («Edit this file»).",
        "Change the text.",
        "Click the green «Commit changes…» button. In the window, describe your change in one line (for example "
        "«New price for the Arutam journey») and confirm with «Commit changes».",
        "Wait one to three minutes and reload the website. Done.",
    ])
    b.h2("1.4 Is it online yet?")
    b.p("On GitHub, the «Actions» tab shows every website update:")
    b.bullets(["**Yellow circle:** the website is being updated.",
               "**Green tick:** done, the change is online.",
               "**Red cross:** something went wrong. The website still shows the previous version. See chapter 7."])
    b.box("If you don't see the change, force a reload: on a computer press Ctrl + F5 (on a Mac: Cmd + Shift + R).")
    b.h2("1.5 Three languages")
    b.p("The website exists in Spanish, English and French. Almost all texts are in three files with the same name "
        "in the folders `_data/es`, `_data/en` and `_data/fr`. **Always change all three.** If you can't "
        "translate, change the Spanish text and ask for help with the other languages, or use a translator such as "
        "DeepL.")
    b.h2("1.6 Golden rules for .yml files")
    b.p("The texts are in files ending in `.yml`. They are easy to read, but a few rules apply:")
    b.bullets([
        "Don't delete the spaces at the start of lines. The indentation shows what belongs to what.",
        "Use spaces, never the Tab key.",
        "If a text contains a colon followed by a space, put it in quotation marks: `\"Arutam journey: 22 days\"`.",
        "To add something new, copy an existing block, paste it right below and change the texts.",
        "Lines starting with `#` are notes for editors. They don't appear on the website.",
    ])

    b.h1("2. Tours: dates, places and the homepage notice")
    b.h2("2.1 How it works")
    b.p("There are two journeys: the **spiritual journey** (11 days) and the **Arutam journey** (22 days). "
        "The journeys are run by Raíces, which organises the journey and the bookings; in Maikiuants, Kampuntin takes care of the "
        "organisation and support. The name, duration, "
        "price and description of each journey are stored once. The dates are stored separately, and each date "
        "says which journey it belongs to.")
    b.img("viajes", "The «Two journeys» section on the tours page. The programmes can be opened below.")
    b.bullets([
        "**Dates and places:** file `_data/tour_dates.yml`. The easiest way is Pages CMS (2.2).",
        "**Name, duration, price and text of each journey:** `_data/en/tours.yml` (and `es`, `fr`), under "
        "`trips` (2.5).",
        "**The homepage notice** picks the next date automatically (2.4).",
    ])
    b.h2("2.2 Adding a new date (with Pages CMS)")
    b.steps([
        "Open **app.pagescms.org** and sign in with «Sign in with GitHub».",
        "Choose the repository **Kampuntin-Maikiuants.github.io**.",
        "In the menu on the left, click **Fechas de tours** (tour dates).",
        "Below the last date, click the button to add a new entry (plus sign).",
        "Fill in the fields (see table). The form labels are in Spanish.",
        "Click «Save». Within one to three minutes the date appears on the tours page and, if it is the next one, "
        "in the homepage notice.",
    ])
    b.table(["Field (Spanish label)", "What to enter"], [
        ["Inicio (start)", "First day of the journey (exact or approximate)."],
        ["Fin (end)", "Last day of the journey."],
        ["Viaje (journey)", "Viaje espiritual (11 días) or Viaje Arutam (22 días)."],
        ["Texto en vez de la fecha (text instead of the date)",
         "Only if the date is not fixed yet, for example «April / May 2027». In Spanish, English and French."],
        ["Nota pequeña (small note)", "Optional, a line below the date, for example «Exact date to be confirmed»."],
        ["Plazas libres (free places)", "How many places are left. **0** = full. Empty = the status below is used."],
        ["Estado (status)", "Plazas a consultar (on request) · Plazas libres (available) · Últimas plazas (last "
                            "places) · Completo (full). Only if «Plazas libres» is empty."],
    ], [.36, .64])
    b.img("fechas", "This is how prices and upcoming dates look on the tours page.")
    b.box("Past dates disappear by themselves: once the start date has passed, the date is no longer shown (the "
          "website updates every 6 hours). You don't need to delete them, but you can, to keep the list tidy.")
    b.h2("2.3 Updating free places")
    b.steps([
        "Open Pages CMS › **Fechas de tours**.",
        "For the date of the journey, enter in **Plazas libres** how many places are left (for example 12, and one "
        "less after each booking).",
        "Click «Save». With 3 places or fewer the number turns orange; with **0** it shows «Full».",
    ])
    b.p("A full date no longer appears in the homepage notice. The notice then shows the next date with places.")
    b.h2("2.4 The homepage notice (pop-up)")
    b.img("popup", "The notice appears at the bottom right a few seconds after opening the homepage.")
    b.p("The notice always shows the next date that has not passed and is not full, with the name of the journey, "
        "the duration and the price. **You don't need to change anything to keep it up to date.**")
    b.p("**Switching the notice on or off:**")
    b.steps([
        "On GitHub, open the file `_config.yml` (in the main folder) and click the pencil.",
        "Find the line `tour_popup: true`.",
        "Write `false` to switch it off or `true` to switch it on, and save with «Commit changes».",
    ])
    b.p("**Changing the text or photo of the notice:** in `_data/en/home.yml` (and `es`, `fr`), at the end, in the "
        "`tour_popup` block. The photo (`image`) is a path to a file on the website.")
    b.code(block("_data/en/home.yml", r"^tour_popup:", r"^\S"), "_data/en/home.yml")
    b.h2("2.5 Changing the price, duration or description of a journey")
    b.steps([
        "On GitHub, open `_data/en/tours.yml` and click the pencil.",
        "Find `trips:`. Below it are `espiritual` and `arutam`.",
        "Change `amount` (price), `days` (duration), `when` (season) or `text` (short description).",
        "Do the same in `_data/es/tours.yml` and `_data/fr/tours.yml`.",
        "Save with «Commit changes».",
    ])
    b.code(block("_data/en/tours.yml", r"^  espiritual:", r"^  arutam:"), "_data/en/tours.yml (excerpt)")
    b.p("The detailed programme (arrival, activities and return) is in the same file: in `spiritual` for the "
        "spiritual journey and in `experience` for the Arutam journey.")
    b.box("A completely new journey (a third kind of journey) needs a small technical change to the website. For "
          "that, contact the person who manages the website.", "warn")

    b.h1("3. Gallery: albums and photos")
    b.h2("3.1 How it works")
    b.p("Each album is a **folder** inside `assets/galeria`. All photos in the folder appear in the album. The "
        "first photo (or the one you choose) is the cover. Albums are sorted by folder name, from highest to "
        "lowest: that is why each folder starts with a number. The first three albums also appear at the bottom "
        "of the tours page.")
    b.img("galeria", "The gallery: each card is an album. One click opens all photos.")
    b.p("The current folders go from `01` to `11`. A new album gets the next number (`12`, `13`, …) so it appears "
        "first.")
    b.h2("3.2 Preparing photos")
    b.bullets([
        "Format **JPG**.",
        "About **1600 pixels wide** and under **500 KB** per photo. Large photos make the website slow.",
        "To shrink photos for free: **squoosh.app** in the browser, or a photo resizing app on your phone.",
        "Simple names without spaces or accents: `001.jpg`, `002.jpg`, … The order of the numbers is the order in "
        "the album.",
        "Ask the people in the photos for permission.",
    ])
    b.h2("3.3 Creating a new album")
    b.steps([
        "On GitHub, open the folder `assets` › `galeria`.",
        "Click «Add file» › «Create new file».",
        "In the name field, type the folder name, a slash `/` and `_LEEME.txt`, for example: "
        "`12-chonta-festival-2027/_LEEME.txt`. When you type the slash, GitHub creates the folder.",
        "In the content, write one line, for example «Album Chonta festival 2027». Click «Commit changes…» and "
        "then «Commit changes».",
    ])
    b.h2("3.4 Uploading photos")
    b.steps([
        "Open the new folder (or an existing album).",
        "Click «Add file» › «Upload files».",
        "Drag the photos into the window or click «choose your files». You can upload several at once.",
        "At the bottom, click «Commit changes» and wait until the upload has finished.",
        "Within one to three minutes the album appears in the gallery.",
    ])
    b.box("The file `_LEEME.txt` does not appear on the website. You can keep it or delete it.")
    b.h2("3.5 A nice title and cover")
    b.p("Without further information, the album uses the folder name as its title. For a title in three languages "
        "and a chosen cover, open `_data/albums.yml`, copy a block at the top of the list and change it:")
    b.code('- folder: 12-chonta-festival-2027\n'
           '  title: { es: "Fiesta de la Chonta 2027", en: "Chonta festival 2027", fr: "Fête de la Chonta 2027" }\n'
           '  cover: "004.jpg"', "_data/albums.yml (example)")
    b.bullets(["`folder`: the exact folder name.", "`title`: the title in the three languages.",
               "`cover`: the file name of the cover photo. Empty (`\"\"`) = the first photo."])
    b.h2("3.6 Deleting a photo or an album")
    b.steps([
        "Open the photo on GitHub.",
        "At the top right, click the three dots «…» › «Delete file».",
        "Confirm with «Commit changes». An album disappears when it has no photos left.",
    ])

    b.h1("4. Updates: Facebook and Instagram")
    b.h2("4.1 What the Updates page shows")
    b.img("novedades", "At the top, the Facebook and Instagram accounts appear as cards.")
    b.p("The page shows the Facebook and Instagram accounts as cards. If the automatic import is set up (4.3), the "
        "latest posts with text and photos appear below. The three newest also appear on the homepage.")
    b.p("The Facebook timeline cannot be shown directly: Facebook only shows it to people who are logged in to "
        "Facebook, everyone else would see an empty box. That is why the website **imports** the posts.")
    b.h2("4.2 Changing or adding an account")
    b.steps([
        "On GitHub, open `_config.yml` and click the pencil.",
        "Find `social:`.",
        "Change the name (`name`) or the link (`url`). For another Facebook account, copy a block "
        "`- name: … url: …` and paste it below.",
        "Save with «Commit changes». The card appears on the Updates page and in the footer.",
    ])
    b.code(block("_config.yml", r"^social:", r"^  wwoof:"), "_config.yml (excerpt)")
    b.h2("4.3 Showing posts automatically")
    b.p("This is set up once and takes about 20 minutes. After that, the website checks for new posts every "
        "6 hours by itself.")
    b.box("Requirements: they must be **Facebook Pages** (not personal profiles), and the person setting it up must "
          "be an admin of those pages. For Instagram, the account must be a professional account (business or "
          "creator) linked to one of the Facebook Pages.", "warn")
    b.steps([
        "Go to **developers.facebook.com** with the Facebook account that manages the pages. «My Apps» › "
        "«Create App», type «Business», name for example «Kampuntin Website».",
        "Open «Tools» › «Graph API Explorer» and select the new app at the top. Under «Permissions» add "
        "`pages_show_list` and `pages_read_engagement`, and for Instagram also `instagram_basic` and "
        "`business_management`. Then «Generate Access Token» and confirm.",
        "Open «Tools» › «Access Token Debugger», paste the token, click «Debug» and at the bottom "
        "«Extend Access Token». Copy the long token.",
        "Go back to the Graph API Explorer, paste the long token and run the query `me/accounts`. The answer "
        "contains an `access_token` for each page. These page tokens don't expire.",
        "On GitHub, in the repository: «Settings» › «Secrets and variables» › «Actions» › «New repository "
        "secret». Name: `FB_PAGE_TOKENS`. Value: the page tokens, one per line. Save with «Add secret».",
        "«Actions» tab › «Website bauen & Social Media importieren» › «Run workflow». Within one to three "
        "minutes the posts appear.",
    ])
    b.h2("4.4 Is the import working?")
    b.p("In «Actions», open the latest run. At the top, under «Annotations», there is a short message (in German):")
    b.bullets(["Yellow «Kein Secret FB_PAGE_TOKENS gesetzt»: step 5 is missing.",
               "Red «Token Nr. 1: …»: the token is wrong or has expired. Facebook's message is shown next to it.",
               "Blue «… Beiträge geladen»: everything is fine."])
    b.box("If someone changes the Facebook password or removes the app's permissions, the tokens stop working: "
          "repeat steps 2 to 5. If nothing happens in the repository for 60 days, GitHub pauses the automatic "
          "update: in «Actions», click «Enable workflow».")
    b.h2("4.5 Showing an Instagram post manually")
    b.steps([
        "Open the post on Instagram and copy the link, for example `https://www.instagram.com/p/ABC123/`.",
        "On GitHub, open `_data/instagram_embeds.yml` and add a line: `- https://www.instagram.com/p/ABC123/`",
        "Save with «Commit changes». The post appears on the Updates page. It only loads after a click, to "
        "protect visitors' privacy.",
    ])

    b.h1("5. Team, texts and other useful things")
    b.h2("5.1 Adding or changing a team member")
    b.img("equipo", "The team cards on the «People» page.")
    b.steps([
        "Prepare a **square** photo (about 600 × 600 pixels, JPG) with the face in the centre.",
        "Upload it to `assets` › `img` › `equipo` with «Add file» › «Upload files», with a simple name, for "
        "example `eddy.jpg`.",
        "Open `_data/team.yml`, copy a person's block, paste it and change it (see example).",
        "Save with «Commit changes».",
    ])
    b.code('- name: "Eddy Ankuash"\n'
           '  group: kampuntin\n'
           '  photo: "/assets/img/equipo/eddy.jpg"\n'
           '  role: { es: "Secretario de Kampuntin", en: "Secretary of Kampuntin", fr: "Secrétaire de Kampuntin" }\n'
           '  bio:\n'
           '    es: "Texto corto en español."\n'
           '    en: "Short text in English."\n'
           '    fr: "Texte court en français."', "_data/team.yml (example)")
    b.bullets(["Optional: `contact: true` shows the «Contact us» link (only for contact persons).",
               "Optional: `social:` adds links to Instagram or Facebook.",
               "Optional: `shuar_name:` shows the Shuar name below the name."])
    b.box("To change a photo, upload the new one under a different name (for example `eddy-2.jpg`) and change the "
          "`photo` line. That way browsers show the new photo right away. Only publish photos and texts about "
          "people with their permission.")
    b.h2("5.2 Where is each text?")
    b.table(["Page", "File (in `_data/es`, `_data/en` and `_data/fr`)"], [
        ["Home", "`home.yml`"], ["Tours", "`tours.yml`"], ["Volunteering", "`volunteering.yml`"],
        ["Science", "`science.yml`"], ["Updates", "`updates.yml`"], ["Gallery (texts)", "`gallery.yml`"],
        ["People (general texts)", "`people.yml`"], ["Contact", "`contact.yml`"], ["Legal notice", "`legal.yml`"],
        ["Menu, buttons and footer", "`ui.yml`"],
    ], [.38, .62])
    b.table(["Content shared by all three languages", "File"], [
        ["Team members", "`_data/team.yml`"], ["Tour dates", "`_data/tour_dates.yml`"],
        ["Albums (titles and covers)", "`_data/albums.yml`"], ["Videos", "`_data/videos.yml`"],
        ["Threatened species", "`_data/species.yml`"],
        ["Email, WhatsApp, contact persons, social media, notice on or off", "`_config.yml`"],
    ], [.62, .38])
    b.h2("5.3 Contact persons and WhatsApp")
    b.p("The people on the contact page and in the footer are in `_config.yml`, under `contact:` › `people:`. "
        "Each person has a name, a role in three languages, a WhatsApp number (digits only, with country code, "
        "without + or spaces) and the phone number as displayed.")
    b.code(block("_config.yml", r"^    - name: Julien", r"^    - name: (?!Julien)", 6), "_config.yml (excerpt)")
    b.h2("5.4 Videos")
    b.p("**Short videos** (MP4, under 50 MB): upload them to `assets/video` and add them in `_data/videos.yml` "
        "(copy a block with `file`, `poster`, `title` and `text`). **Long videos:** upload them to YouTube and "
        "enter only the video code under `youtube:`, for example `AbCdEf12345` from `https://youtu.be/AbCdEf12345`.")

    b.h2("5.5 Volunteer stories (testimonials)")
    b.img("testimonios", "The stories on the volunteering page. A click on «Read the full story» opens the whole text.")
    b.p("The volunteering page has cards with stories from people who have already been to Maikiuants. Each card has "
        "a short quote that is always visible, the name, a small line (for example «Volunteer · Germany · 2026») "
        "and, if you like, the full story to open and a small photo.")
    b.steps([
        "Ask the person for a short quote (one to three sentences), how they want to appear (name, country, year), "
        "whether they want to add a longer story and a photo. **Ask for their permission to publish it.**",
        "Optional, the photo: square, face in the centre, about 300 × 300 pixels. Upload it to `assets` › `img` › "
        "`fotos` with «Add file» › «Upload files», for example as `testimonio-ana.jpg`.",
        "On GitHub, open `_data/en/volunteering.yml` and click the pencil. Find `testimonials:` and below it `items:`.",
        "Copy a complete block, from `- quote:` to just before the next `- quote:`, and paste it at the top of the "
        "list (the first card is the newest). Change the texts (see example).",
        "Do the same in `_data/es/volunteering.yml` and `_data/fr/volunteering.yml`, with the translated text.",
        "Save with «Commit changes».",
    ])
    b.code(EXAMPLE_TESTIMONIAL, "_data/es/volunteering.yml (example of one block)")
    b.bullets([
        "`quote`: the short quote. Leave `>-` as it is and write the text on the line below, with the same indentation.",
        "`name` and `meta`: the name and the small line below it.",
        "`photo`: the path to the photo, or empty (`\"\"`) if there is no photo.",
        "`text`: the full story (optional). Leave `|-` as it is; an empty line separates paragraphs. If there is no "
        "story, delete the `text` lines; then the «Read the full story» button does not appear.",
    ])
    b.box("To remove a story, delete its whole block. For now the stories only appear on the volunteering page; to "
          "have them on the tours page as well, ask the person who manages the website for help.")

    b.h1("6. Your own address (domain)")
    b.p("Today the website is at **kampuntin-maikiuants.github.io**. With your own domain, for example "
        "**www.kampuntin.org**, the address is shorter and easier to remember. The website stays free on GitHub; "
        "only the domain costs money.")
    b.h2("6.1 Choosing and buying the domain")
    b.steps([
        "Choose a name and an ending, for example `kampuntin.org`, `kampuntin.com` or `kampuntin.ec`. The "
        "provider's website shows whether it is still available.",
        "Buy it from a domain provider (registrar), for example Namecheap, Porkbun or Cloudflare. For the .ec "
        "ending there are also providers in Ecuador. Approximate price: 10 to 20 USD per year for .org or .com; "
        "other endings can cost more.",
        "Register the domain in Kampuntin's name, with an email address of the organisation, and switch on "
        "automatic renewal. If the domain expires, the website can no longer be reached at that address.",
    ])
    b.box("Keep the provider login safe and share it with a second trusted person. Without access to the provider "
          "the domain cannot be renewed or changed.", "warn")
    b.h2("6.2 Connecting the domain to the website (DNS)")
    b.p("In your provider account, open the domain's DNS settings (called «DNS», «DNS records» or «DNS zone») and "
        "create these entries:")
    b.table(["Type", "Name (host)", "Value"], DNS, [.18, .27, .55])
    b.p("Delete any other A or CNAME entries for `@` and `www` that the provider created (for example for a "
        "parking page).")
    b.box("Optional, for IPv6 connections: four AAAA entries for `@` with the values `2606:50c0:8000::153`, "
          "`2606:50c0:8001::153`, `2606:50c0:8002::153` and `2606:50c0:8003::153`.")
    b.h2("6.3 Activating the domain on GitHub")
    b.steps([
        "On GitHub, in the repository: «Settings» › «Pages».",
        "Under «Custom domain», enter your domain with www, for example `www.kampuntin.org`, and click «Save».",
        "GitHub checks the DNS. This can take from a few minutes up to 48 hours. When «DNS check successful» "
        "appears, tick «Enforce HTTPS». If the box is still greyed out, wait a few hours and try again.",
        "Done: the website opens at the new address. The old address kampuntin-maikiuants.github.io redirects to "
        "the new one automatically.",
    ])
    b.box("Recommended: verify the domain on GitHub so nobody else can use it with GitHub Pages. In the settings "
          "of the organisation Kampuntin-Maikiuants: «Settings» › «Pages» › «Add a domain», and follow the "
          "instructions (it is another DNS entry, of type TXT).")
    b.h2("6.4 After the change")
    b.bullets([
        "Update the address on the Facebook and Instagram profiles, on WWOOF, on flyers and in QR codes.",
        "If link previews on WhatsApp or Facebook still show the old address, enter the new address in "
        "`_config.yml` on the `url:` line (remove the `#` at the start), for example "
        "`url: \"https://www.kampuntin.org\"`.",
        "An email address with the domain (for example info@kampuntin.org) can be added later with an email "
        "service. Many domain providers offer free email forwarding.",
    ])

    b.h1("7. If something goes wrong")
    b.table(["Problem", "What to do"], [
        ["The website doesn't change", "Wait three minutes and reload with Ctrl + F5. Check the «Actions» tab: "
                                       "yellow (working), green (done) or red (error)?"],
        ["Red cross in «Actions»", "Almost always an error in a `.yml` file: one space too many or too few, or "
                                   "missing quotation marks. Open the red run: the message names the file and the "
                                   "line. Fix it and save again. Meanwhile the website keeps showing the last good "
                                   "version."],
        ["I deleted something by mistake", "Nothing is lost. On GitHub open the file › «History», open the previous "
                                           "version, copy the text and paste it back with the pencil."],
        ["A photo doesn't appear", "Check that the name in the file is exactly the same as the photo's, including "
                                   "capital letters and the extension (`.jpg` is not the same as `.JPG`)."],
        ["Facebook posts are no longer updated", "See 4.4."],
    ], [.3, .7])
    b.p("**Help:** Jesko Dorner · jesko.dorner@gmail.com")
    b.h2("Quick reference")
    b.table(["Task", "Where", "Tool"], [
        ["New tour date, free places", "Fechas de tours", "Pages CMS"],
        ["Price or text of a journey", "`_data/es|en|fr/tours.yml` › `trips`", "GitHub"],
        ["Notice on or off", "`_config.yml` › `tour_popup`", "GitHub"],
        ["Text or photo of the notice", "`_data/es|en|fr/home.yml` › `tour_popup`", "GitHub"],
        ["New album, uploading photos", "`assets/galeria/NN-name/`", "GitHub"],
        ["Album title or cover", "`_data/albums.yml`", "GitHub"],
        ["Facebook and Instagram accounts", "`_config.yml` › `social`", "GitHub"],
        ["Automatic posts", "Secret `FB_PAGE_TOKENS`", "GitHub and Facebook"],
        ["Instagram post manually", "`_data/instagram_embeds.yml`", "GitHub"],
        ["Team member", "`_data/team.yml` and `assets/img/equipo`", "GitHub"],
        ["Contact persons", "`_config.yml` › `contact`", "GitHub"],
        ["Videos", "`_data/videos.yml` and `assets/video`", "GitHub"],
        ["Volunteer story", "`_data/es|en|fr/volunteering.yml` › `testimonials`", "GitHub"],
        ["Own domain", "Domain provider (DNS) and «Settings» › «Pages»", "Provider and GitHub"],
    ], [.36, .44, .20])


TEXTS = {
    "es": dict(title="Manual de la página web – Kampuntin Maikiuants", cover_title="Manual de la página web",
               cover_sub="Kampuntin Maikiuants", footer="Manual de la página web · Kampuntin Maikiuants",
               cover_lead="Cómo actualizar tours, galerías y novedades, paso a paso. Para personas sin "
                          "conocimientos técnicos.",
               cover_meta="Versión: octubre de 2026 · Página web: " + SITE, toc_title="Contenido", content=es,
               readme_links="Página web: https://" + SITE + " · Este manual también como PDF para imprimir: "
                            "[español](manual/Manual-pagina-web-ES.pdf) · [English](manual/Website-handbook-EN.pdf) · "
                            "Notas técnicas para quien administra la página (en alemán): "
                            "[manual/Technik-DE.md](manual/Technik-DE.md)"),
    "en": dict(title="Website handbook – Kampuntin Maikiuants", cover_title="Website handbook",
               cover_sub="Kampuntin Maikiuants", footer="Website handbook · Kampuntin Maikiuants",
               cover_lead="How to update tours, galleries and news, step by step. For people without technical "
                          "knowledge.",
               cover_meta="Version: October 2026 · Website: " + SITE, toc_title="Contents", content=en),
}

if __name__ == "__main__":
    build("es", "Manual-pagina-web-ES.pdf", TEXTS["es"])
    build("en", "Website-handbook-EN.pdf", TEXTS["en"])
    build_md("es", "README.md", TEXTS["es"])

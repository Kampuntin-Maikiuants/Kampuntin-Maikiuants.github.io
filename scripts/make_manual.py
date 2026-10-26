#!/usr/bin/env python3
"""Erzeugt die Handbücher für die Pflege der Website (Spanisch und Englisch) als druckfertige PDFs.

Aufruf (auf dem Mac, mit reportlab aus vendor/py):
    PYTHONPATH=vendor/py python3 scripts/make_manual.py
Ergebnis: manual/Manual-pagina-web-ES.pdf und manual/Website-handbook-EN.pdf
Das Handbuch enthält Zugangsdaten und liegt deshalb nur lokal (manual/ steht in .gitignore).
Zugangsdaten: manual/accesos.json (Liste mit servicio, para{es,en}, web, usuario, contrasena).
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
DNS = [["A", "@", "185.199.108.153", "Proxied"], ["A", "@", "185.199.109.153", "Proxied"],
       ["A", "@", "185.199.110.153", "Proxied"], ["A", "@", "185.199.111.153", "Proxied"],
       ["CNAME", "www", "kampuntin-maikiuants.github.io", "Proxied"]]
SITE = "www.kampuntin.org"
# Zugangsdaten nur lokal (nie ins Skript schreiben – das Skript liegt auf GitHub)
import json as _json
_acc = Path(__file__).resolve().parent.parent / "manual" / "accesos.json"
ACCESOS = _json.loads(_acc.read_text(encoding="utf-8")) if _acc.exists() else []

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
        ["**Pages CMS**", "Formularios sencillos para lo que se cambia seguido: fechas y plazas, fotos y álbumes, "
                          "equipo, experiencias de voluntarios, viajes y el aviso. Funciona también desde el "
                          "celular (ver 1.8).", "app.pagescms.org"],
        ["**GitHub**", "Todos los archivos de la página. Se usa para lo demás: contactos, redes sociales, videos y "
                       "los textos de las páginas.", REPO],
    ], [.17, .43, .40])
    b.box("Regla sencilla: lo que está en Pages CMS, cámbialo en Pages CMS. Lo demás, en GitHub.")
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
               "**Cruz roja:** algo salió mal. La página sigue mostrando la versión anterior. Ver capítulo 8."])
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
        "`\"Viaje Arutam: 10 días\"`.",
        "Para agregar algo nuevo, copia un bloque que ya existe, pégalo justo debajo y cambia los textos.",
        "Las líneas que empiezan con `#` son notas para quien edita. No aparecen en la página.",
    ])

    b.h2("1.7 Datos de acceso")
    if ACCESOS:
        for a in ACCESOS:
            b.p("**" + a["servicio"] + "** – " + a["para"]["es"])
            b.bullets(["Página: " + a["web"], "Usuario: `" + a["usuario"] + "`", "Contraseña: `" + a["contrasena"] + "`"])
    else:
        b.p("Los datos de acceso están en el archivo local `manual/accesos.json`.")
    b.box("Este manual contiene contraseñas. No lo subas a GitHub ni a otras páginas y compártelo solo con personas "
          "de confianza. Si alguien deja el equipo, cambia las contraseñas.", "warn")

    b.h2("1.8 Pages CMS: el editor sencillo")
    b.steps([
        "Abre **app.pagescms.org** e inicia sesión con «Sign in with GitHub» (con tu cuenta de GitHub, ver 1.2).",
        "Elige el repositorio **Kampuntin-Maikiuants.github.io**.",
        "En el menú de la izquierda eliges qué quieres cambiar (ver la tabla).",
        "Cambia lo que quieras y haz clic en «Save». Igual que con GitHub, la página se actualiza en uno a tres "
        "minutos (ver 1.4).",
    ])
    b.table(["En el menú", "Qué cambias ahí", "Ver"], [
        ["Fechas de tours", "Fechas de los viajes y plazas libres", "2.2"],
        ["Aviso (pop-up)", "Texto, botón y foto del aviso", "2.4"],
        ["Viajes", "Nombre, duración, temporada y texto de los dos viajes", "2.5"],
        ["Galería (álbumes de fotos)", "Crear álbumes, subir y borrar fotos", "3.3–3.6"],
        ["Álbumes de fotos", "Título y portada de cada álbum", "3.5"],
        ["Equipo", "Personas del equipo: foto, función, textos y enlaces", "5.1"],
        ["Experiencias de voluntarios", "Las experiencias en la página de voluntariado", "5.5"],
        ["Fotos del equipo · Otras fotos", "Ver, subir o borrar esas fotos", "5.1, 5.5"],
    ], [.32, .52, .16])
    b.box("Los textos en tres idiomas tienen un formulario por idioma (Español, English, Français): cambia siempre "
          "los tres (ver 1.5). En las listas puedes cambiar el orden arrastrando los puntitos a la izquierda de cada "
          "entrada.")

    b.h1("2. Tours: fechas, plazas y aviso en la página de inicio")
    b.h2("2.1 Cómo funciona")
    b.p("Hay dos viajes: el **Viaje espiritual** (8 días) y el **Viaje Arutam** (10 días). Los dos empiezan y terminan "
        "en Limón Indanza. El nombre, la duración y la descripción de cada viaje se guardan una sola vez. Las fechas se guardan aparte, y cada fecha dice a qué "
        "viaje pertenece.")
    b.img("viajes", "La sección «Dos viajes» en la página de tours. Abajo se pueden abrir los programas.")
    b.bullets([
        "**Fechas y plazas:** Pages CMS › Fechas de tours (2.2).",
        "**Nombre, duración y texto de cada viaje:** Pages CMS › Viajes (2.5).",
        "**El aviso en la página de inicio** toma la próxima fecha automáticamente (2.4).",
    ])
    b.h2("2.2 Agregar una fecha nueva (con Pages CMS)")
    b.steps([
        "Abre **app.pagescms.org** e inicia sesión con «Sign in with GitHub».",
        "Elige el repositorio **Kampuntin-Maikiuants.github.io**.",
        "En el menú de la izquierda haz clic en **Fechas de tours**.",
        "Debajo de la última fecha, haz clic en «Add an item».",
        "Llena los campos (ver la tabla).",
        "Haz clic en «Save». En uno a tres minutos la fecha aparece en la página de tours y, si es la próxima, "
        "también en el aviso de la página de inicio.",
    ])
    b.table(["Campo", "Qué escribir"], [
        ["Inicio", "Primer día del viaje (exacto o aproximado)."],
        ["Fin", "Último día del viaje."],
        ["Viaje", "Viaje espiritual (8 días) o Viaje Arutam (10 días)."],
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
        "viaje y la duración. **No hay que cambiar nada para que se actualice.**")
    b.p("**Cambiar el texto, el botón o la foto:**")
    b.steps([
        "Pages CMS › **Aviso (pop-up)** › **Español**.",
        "Cambia «Texto», «Texto del botón» o «Foto del aviso». Una foto nueva la puedes subir directamente en el "
        "campo de la foto.",
        "Haz clic en «Save». Repite en **English** y **Français**.",
    ])
    b.p("**Encender o apagar el aviso** (en GitHub):")
    b.steps([
        "En GitHub abre el archivo `_config.yml` (está en la carpeta principal) y haz clic en el lápiz.",
        "Busca la línea `tour_popup: true`.",
        "Escribe `false` para apagarlo o `true` para encenderlo y guarda con «Commit changes».",
    ])
    b.h2("2.5 Cambiar el nombre, la duración o la descripción de un viaje")
    b.steps([
        "Pages CMS › **Viajes** › **Español**.",
        "En «Viaje espiritual» o «Viaje Arutam» cambia el nombre, la duración (por ejemplo «8 días»), la temporada "
        "(por ejemplo «Abril – mayo 2027») o la descripción corta.",
        "Haz clic en «Save». Repite en **English** y **Français**.",
    ])
    b.box("Hoy la página no muestra precios: en su lugar dice «Precio a consultar». Para mostrar un precio, en GitHub "
          "abre `_data/es/tours.yml` (y `en`, `fr`) y agrega debajo de `days` una línea como `amount: \"1.200 USD\"`. "
          "Para volver a «Precio a consultar», borra esa línea.")
    b.p("El programa detallado de cada viaje (llegada, actividades y regreso) se cambia en GitHub, en "
        "`_data/es/tours.yml` (y `en`, `fr`): en `spiritual` para el viaje espiritual y en `experience` para el "
        "viaje Arutam.")
    b.box("Un viaje completamente nuevo (un tercer tipo de viaje) necesita un pequeño cambio técnico en la página. "
          "Para eso, contacta a la persona que administra la página.", "warn")

    b.h1("3. Galería: álbumes y fotos")
    b.h2("3.1 Cómo funciona")
    b.p("Cada álbum es una **carpeta** en la «Galería» de Pages CMS (en GitHub: `assets/galeria`). Todas las fotos de "
        "la carpeta aparecen en el álbum. La primera foto (o la que elijas) es la portada. El orden de los álbumes en "
        "la página es el orden de la lista «Álbumes de fotos» (3.5). Un álbum nuevo que todavía no está en esa lista "
        "aparece primero. Los tres primeros álbumes aparecen también abajo en la página de tours.")
    b.img("galeria", "La galería: cada tarjeta es un álbum. Un clic abre todas las fotos.")
    b.p("Las carpetas antiguas tienen un número delante (`01` a `11`). Para álbumes nuevos ya no hace falta.")
    b.h2("3.2 Preparar las fotos")
    b.bullets([
        "Formato **JPG** (también sirven PNG y WebP).",
        "Unos **1600 píxeles de ancho** y menos de **500 KB** por foto. Las fotos grandes hacen lenta la página y "
        "a veces no se pueden subir.",
        "Para achicar fotos gratis: **squoosh.app** en el navegador, o una app para reducir fotos en el celular.",
        "Fotos del iPhone: tienen que ser JPG, no HEIC. En el iPhone: Ajustes › Cámara › Formatos › «Más compatible».",
        "Nombres sencillos, sin espacios ni acentos: `001.jpg`, `002.jpg`, … El orden de los números es el orden "
        "en el álbum.",
        "Pide permiso a las personas que aparecen en las fotos.",
    ])
    b.h2("3.3 Crear un álbum nuevo")
    b.steps([
        "Abre Pages CMS › **Galería (álbumes de fotos)**. Ves las carpetas de los álbumes.",
        "Haz clic en el botón para crear una carpeta (el ícono de carpeta con +).",
        "Escribe el nombre de la carpeta, sin espacios ni acentos, por ejemplo `fiesta-de-la-chonta-2027`, y "
        "confirma.",
    ])
    b.h2("3.4 Subir las fotos")
    b.steps([
        "En la «Galería», abre la carpeta del álbum con un clic.",
        "**En la computadora:** arrastra las fotos a la ventana; puedes arrastrar varias a la vez. **En el "
        "celular:** toca «Upload» y elige una foto; repite para cada foto.",
        "Cada foto se guarda sola. Espera a que terminen todas.",
        "En uno a tres minutos el álbum aparece en la galería.",
    ])
    b.box("Si una foto no se sube, seguramente es demasiado grande: achícala antes (3.2).", "warn")
    b.box("Para muchas fotos a la vez también sirve GitHub: abre `assets` › `galeria` › la carpeta del álbum › "
          "«Add file» › «Upload files», arrastra las fotos y haz clic en «Commit changes».")
    b.h2("3.5 Título y portada")
    b.p("Sin más datos, el álbum usa el nombre de la carpeta como título. Para un título en tres idiomas y una "
        "portada elegida:")
    b.steps([
        "Pages CMS › **Álbumes de fotos**.",
        "Haz clic en «Add an item».",
        "Llena **Carpeta del álbum** (el nombre exacto de la carpeta, por ejemplo `fiesta-de-la-chonta-2027`), "
        "**Título** en los tres idiomas y **Portada** (el nombre de una foto, por ejemplo `004.jpg`; vacío = la "
        "primera foto).",
        "Haz clic en «Save».",
    ])
    b.p("El orden de esta lista es el orden en la galería. La entrada nueva aparece al final: arrástrala arriba "
        "para que el álbum salga primero.")
    b.h2("3.6 Borrar una foto o un álbum")
    b.steps([
        "Pages CMS › **Galería (álbumes de fotos)** › abre la carpeta del álbum.",
        "En la foto, abre el menú (los tres puntos) y elige «Delete». Confirma.",
        "Un álbum desaparece de la página cuando ya no tiene fotos. Si tenía título en «Álbumes de fotos», borra "
        "también esa entrada.",
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
        "Abre Pages CMS › **Equipo**.",
        "Para una persona nueva, haz clic en «Add an item». Para cambiar a alguien, abre su "
        "entrada.",
        "Llena los campos (ver la tabla). En «Foto» puedes subir la foto directamente.",
        "Haz clic en «Save».",
    ])
    b.table(["Campo", "Qué escribir"], [
        ["Nombre", "Nombre y apellido."],
        ["Nombre shuar", "Opcional. Aparece debajo del nombre."],
        ["Grupo", "«Kampuntin: equipo en Maikiuants»."],
        ["Foto", "La foto cuadrada. Sin foto aparece la inicial del nombre."],
        ["Mostrar el enlace «Escríbenos»", "Solo para las personas de contacto."],
        ["Función", "Por ejemplo «Secretario de Kampuntin», en los tres idiomas."],
        ["Texto corto · Texto largo", "La descripción en los tres idiomas. Si hay texto largo, se muestra ese."],
        ["Enlaces", "Opcional: el texto («Instagram», «Facebook») y el enlace al perfil."],
    ], [.34, .66])
    b.p("El orden de la lista es el orden en la página: para mover a alguien, arrastra su entrada.")
    b.box("Para cambiar una foto, sube la nueva con otro nombre (por ejemplo `eddy-2.jpg`) y elígela en «Foto». Así "
          "los navegadores muestran enseguida la foto nueva. Publica fotos y textos de personas solo con su permiso.")
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
        "tarjeta tiene una cita corta que siempre se ve, el nombre, una línea pequeña (por ejemplo «Voluntariado · "
        "octubre de 2026») y, si quieres, el relato completo para abrir y una foto pequeña.")
    b.steps([
        "Pide a la persona una cita corta (una a tres frases), cómo quiere aparecer, si quiere también un relato más "
        "largo y una foto. **Pide su permiso para publicarlo.**",
        "Abre Pages CMS › **Experiencias de voluntarios** › **Español**.",
        "En «Experiencias» haz clic en «Add an item» y arrastra la entrada nueva arriba de la lista: "
        "la primera tarjeta es la más nueva.",
        "Llena **Cita corta**, **Nombre**, **Línea pequeña**, opcional **Foto** (cuadrada, unos 300 × 300 píxeles) "
        "y opcional **Relato completo** (una línea vacía separa los párrafos).",
        "Haz clic en «Save». Repite en **English** y **Français** con el texto traducido.",
    ])
    b.box("Sin relato completo no aparece el botón «Leer la experiencia completa». Para quitar una experiencia, "
          "bórrala de la lista en los tres idiomas.")

    b.h2("5.6 El pie de página")
    b.p("El pie de página aparece abajo en todas las páginas. Cada parte se cambia en un lugar distinto:")
    b.table(["Parte", "Dónde se cambia"], [
        ["Recuadro «¿Te gustaría conocer Maikiuants?» (título, texto y botón)", "`_data/es/ui.yml` › `cta`"],
        ["Frase debajo del logo y títulos de las columnas", "`_data/es/ui.yml` › `footer`"],
        ["Nombre oficial de la organización", "`_config.yml` › `org_name`"],
        ["Columna «Explorar» (orden de las páginas)", "`_data/navigation.yml`"],
        ["Columna «Contacto»: correo general y personas", "`_config.yml` › `contact` (ver 5.3)"],
        ["Columna «Síguenos»: Instagram, Facebook, WWOOF y otros enlaces", "`_config.yml` › `social`"],
    ], [.55, .45])
    b.p("Los textos de `ui.yml` existen en los tres idiomas: cámbialos también en `_data/en/ui.yml` y "
        "`_data/fr/ui.yml`.")
    b.p("**Agregar, cambiar o quitar una red social** (en `_config.yml`, bajo `social:`):")
    b.bullets([
        "**Instagram:** `handle` es el nombre de la cuenta sin @, `url` es el enlace. Para quitar Instagram, deja "
        "el enlace vacío: `url: \"\"`.",
        "**Facebook:** cada página son dos líneas, `- name:` y `url:`. Para agregar una página, copia las dos "
        "líneas y pégalas debajo. Para quitar una, borra sus dos líneas.",
        "**WWOOF:** para quitarlo, escribe `wwoof: \"\"`. Así también desaparece el botón de WWOOF en la página "
        "de voluntariado.",
        "**Otros enlaces** (por ejemplo una segunda cuenta de Instagram o YouTube): cambia `links: []` por una "
        "lista como la del ejemplo. Cada enlace son dos líneas: el texto que se ve (`name`) y el enlace (`url`).",
    ])
    b.code('  links:\n    - name: "Instagram · Freddy"\n      url: "https://www.instagram.com/nekas_chicham/"\n'
           '    - name: "YouTube"\n      url: "https://www.youtube.com/@..."', "Ejemplo: otros enlaces en _config.yml")
    b.box("Instagram y Facebook también aparecen como tarjetas en la página Novedades (ver 4.2). Lo que cambias en "
          "`social` se ve en los dos lugares. Los «otros enlaces» solo aparecen en el pie de página.")

    b.h1("6. La dirección: www.kampuntin.org")
    b.p("La página está en **www.kampuntin.org**. Los dominios **kampuntin.org** y **kampuntin.com** están registrados "
        "en **Cloudflare** (acceso en 1.7). Todas estas direcciones llevan automáticamente a https://www.kampuntin.org: "
        "kampuntin.org, kampuntin.com, www.kampuntin.com y la dirección antigua kampuntin-maikiuants.github.io. La "
        "página sigue gratis en GitHub; solo los dominios cuestan dinero.")
    b.h2("6.1 Renovar los dominios")
    b.steps([
        "Inicia sesión en **cloudflare.com** (datos en 1.7).",
        "En el menú de la izquierda: «Domain Registration» › «Manage Domains». Ahí ves los dos dominios y la fecha "
        "de vencimiento.",
        "Revisa que la renovación automática («Auto-renew») esté activada en los dos y que la forma de pago guardada "
        "siga siendo válida. Cloudflare cobra la renovación una vez al año.",
    ])
    b.box("Si un dominio vence, la página deja de verse con esa dirección. Comparte el acceso a Cloudflare con una "
          "segunda persona de confianza.", "warn")
    b.h2("6.2 Cómo está configurado")
    b.p("Normalmente no hay que cambiar nada. Si algo deja de funcionar, compara con esta lista.")
    b.p("**kampuntin.org** en Cloudflare › «DNS» › «Records»:")
    b.table(["Type", "Name", "Content", "Proxy status"], DNS, [.14, .16, .45, .25])
    b.bullets([
        "«SSL/TLS» › «Overview»: modo **Full** (o «Automatic», que usa Full). **No** elijas «Full (Strict)»: la página "
        "mostraría un error.",
        "«SSL/TLS» › «Edge Certificates»: «Always Use HTTPS» activado. Así todos llegan a la versión segura (https).",
    ])
    b.p("**En GitHub:**")
    b.bullets([
        "«Settings» › «Pages» › «Custom domain»: `www.kampuntin.org`.",
        "En el repositorio hay un archivo `CNAME` con el texto `www.kampuntin.org`. No lo borres.",
        "En `_config.yml` está la línea `url: \"https://www.kampuntin.org\"`. Con ella, los enlaces para Google y la "
        "vista previa al compartir usan la dirección correcta.",
    ])
    b.box("Recomendado, si aún no está hecho: verifica el dominio en GitHub para que nadie más pueda usarlo con GitHub "
          "Pages. En la configuración de la organización Kampuntin-Maikiuants: «Settings» › «Pages» › «Add a domain». "
          "GitHub te da una entrada TXT; créala en Cloudflare (kampuntin.org › «DNS» › «Records» › «Add record») y "
          "vuelve a GitHub para confirmar.")
    b.h2("6.3 kampuntin.com: la redirección")
    b.p("kampuntin.com no tiene página propia: Cloudflare lleva a todos los visitantes a www.kampuntin.org. Así está "
        "configurado en Cloudflare › **kampuntin.com**:")
    b.bullets([
        "«DNS» › «Records»: `A` · `@` · `192.0.2.1` y `CNAME` · `www` · `kampuntin.com`, los dos en **Proxied** (nube "
        "naranja). La dirección 192.0.2.1 es solo un marcador.",
        "«Rules» › «Redirect Rules»: una regla para «All incoming requests» con «Type» = «Static», «URL» = "
        "`https://www.kampuntin.org` y «Status code» = 301.",
    ])
    b.h2("6.4 Si la página no se abre")
    b.bullets([
        "Revisa en Cloudflare que los dominios no hayan vencido (6.1).",
        "Compara los ajustes con 6.2. Un error frecuente es el modo «Full (Strict)»: cámbialo a «Full».",
        "En GitHub, «Settings» › «Pages»: «Custom domain» debe seguir en `www.kampuntin.org`. Si está vacío, escríbelo "
        "de nuevo y haz clic en «Save».",
        "Si solo falla kampuntin.com, revisa la regla de 6.3.",
    ])
    b.h2("6.5 Un correo con el dominio (opcional)")
    b.p("Con el reenvío gratuito de Cloudflare se puede crear una dirección como info@kampuntin.org que llega a un "
        "correo existente, por ejemplo ocstkampuntin@gmail.com: Cloudflare › kampuntin.org › «Email» › «Email Routing», "
        "y seguir los pasos.")

    b.h1("7. Aparecer en Google")
    b.p("Google muestra la página solo si sabe que existe. Con la **Google Search Console** le avisas a Google, y "
        "además ves con qué búsquedas llega la gente y si hay problemas. Es gratis y se configura una sola vez.")
    b.h2("7.1 Registrar kampuntin.org en la Google Search Console")
    b.steps([
        "Abre **search.google.com/search-console** e inicia sesión con la cuenta de Google de Kampuntin "
        "(ocstkampuntin@gmail.com), así el acceso queda en la organización.",
        "Haz clic en «Agregar propiedad». Elige la opción de la izquierda, «Dominio», y escribe `kampuntin.org`.",
        "Google reconoce que el dominio está en Cloudflare y ofrece hacer la verificación allí. Acepta, inicia sesión en "
        "Cloudflare (datos en 1.7) y autoriza. Google crea solo la entrada necesaria.",
        "Si no aparece esa opción: copia el valor TXT que muestra Google. En Cloudflare abre kampuntin.org › «DNS» › "
        "«Records» › «Add record»: «Type» `TXT`, «Name» `@`, en «Content» pega el valor y guarda. Vuelve a Google y "
        "haz clic en «Verificar».",
    ])
    b.box("No borres después la entrada TXT de Google en Cloudflare. Google la revisa de vez en cuando; sin ella se "
          "pierde el acceso a la Search Console.", "warn")
    b.h2("7.2 Enviar el mapa del sitio y pedir la indexación")
    b.steps([
        "En el menú de la izquierda, «Sitemaps»: escribe `https://www.kampuntin.org/sitemap.xml` y haz clic en "
        "«Enviar». El mapa del sitio se crea solo y contiene todas las páginas en los tres idiomas.",
        "En la barra de arriba («Inspeccionar cualquier URL») escribe `https://www.kampuntin.org/` y haz clic en "
        "«Solicitar indexación». Haz lo mismo con las páginas más importantes, por ejemplo "
        "`https://www.kampuntin.org/tours/`, `/en/` y `/fr/`.",
        "Ahora hay que esperar: normalmente la página aparece en Google después de unos días o hasta dos semanas. "
        "Para comprobarlo, busca en Google `site:kampuntin.org`.",
    ])
    b.box("Para dar acceso a otra persona: «Configuración» › «Usuarios y permisos» › «Agregar usuario».")
    b.h2("7.3 Enlaces desde otras páginas")
    b.p("Google confía más en una página cuando otras páginas la enlazan. Por eso conviene poner **www.kampuntin.org** "
        "en todas partes:")
    b.bullets([
        "En las páginas de Facebook Kampuntin y Maikiuants (campo «Sitio web») y en la biografía de Instagram.",
        "En el perfil de WWOOF y en las páginas de organizaciones amigas.",
        "En los volantes y en la firma de los correos.",
        "En GitHub, en la organización Kampuntin-Maikiuants: «Settings» › «Profile», con una descripción (por ejemplo "
        "«Página web de Kampuntin») y la URL `https://www.kampuntin.org`.",
        "Opcional: un perfil en Google Maps («Perfil de Empresa en Google») para Kampuntin en Maikiuants, con la "
        "dirección de la página. Así aparece también un mapa cuando alguien busca «Kampuntin».",
    ])
    b.h2("7.4 Bing, DuckDuckGo y otros buscadores")
    b.p("En **bing.com/webmasters** se puede importar la página desde la Google Search Console con un clic. Así la "
        "página llega también a Bing, DuckDuckGo, Ecosia y Yahoo.")
    b.box("En algunos buscadores aparece también la página de GitHub de Kampuntin-Maikiuants (el código de la página). "
          "Es normal y no es un problema: ahí solo está lo que ya se ve en la página web, sin contraseñas. Cuando "
          "www.kampuntin.org esté registrada, aparecerá más arriba.")

    b.h1("8. Si algo sale mal")
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
        ["La página no se abre en www.kampuntin.org", "Ver 6.4."],
    ], [.3, .7])
    b.p("**Ayuda:** Jesko Dorner · jesko.dorner@gmail.com")
    b.h2("Hoja resumen")
    b.table(["Tarea", "Dónde", "Herramienta"], [
        ["Fecha de tour nueva, plazas", "Fechas de tours", "Pages CMS"],
        ["Nombre, duración o texto de un viaje", "Viajes", "Pages CMS"],
        ["Texto o foto del aviso", "Aviso (pop-up)", "Pages CMS"],
        ["Álbum nuevo, subir o borrar fotos", "Galería (álbumes de fotos)", "Pages CMS"],
        ["Título o portada de un álbum", "Álbumes de fotos", "Pages CMS"],
        ["Persona del equipo", "Equipo", "Pages CMS"],
        ["Experiencia de voluntario", "Experiencias de voluntarios", "Pages CMS"],
        ["Precio o programa detallado de un viaje", "`_data/es|en|fr/tours.yml`", "GitHub"],
        ["Aviso encendido o apagado", "`_config.yml` › `tour_popup`", "GitHub"],
        ["Cuentas de Facebook e Instagram", "`_config.yml` › `social`", "GitHub"],
        ["Publicaciones automáticas", "Secret `FB_PAGE_TOKENS`", "GitHub y Facebook"],
        ["Publicación de Instagram a mano", "`_data/instagram_embeds.yml`", "GitHub"],
        ["Personas de contacto", "`_config.yml` › `contact`", "GitHub"],
        ["Pie de página: redes y textos", "`_config.yml` › `social`; `_data/es|en|fr/ui.yml` › `footer`", "GitHub"],
        ["Videos", "`_data/videos.yml` y `assets/video`", "GitHub"],
        ["Dominios, renovación y DNS", "Cloudflare (acceso en 1.7, ajustes en 6)", "Cloudflare y GitHub"],
        ["Aparecer en Google", "Search Console, propiedad «Dominio» kampuntin.org (ver 7)", "Google y Cloudflare"],
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
        ["**Pages CMS**", "Simple forms for things that change often: dates and places, photos and albums, team, "
                          "volunteer stories, journeys and the notice. Also works on a phone (see 1.8).",
         "app.pagescms.org"],
        ["**GitHub**", "All website files. Used for everything else: contacts, social networks, videos and the "
                       "page texts.", REPO],
    ], [.17, .43, .40])
    b.box("Simple rule: if something is in Pages CMS, change it in Pages CMS. Everything else on GitHub.")
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
               "**Red cross:** something went wrong. The website still shows the previous version. See chapter 8."])
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
        "If a text contains a colon followed by a space, put it in quotation marks: `\"Arutam journey: 10 days\"`.",
        "To add something new, copy an existing block, paste it right below and change the texts.",
        "Lines starting with `#` are notes for editors. They don't appear on the website.",
    ])

    b.h2("1.7 Access details")
    if ACCESOS:
        for a in ACCESOS:
            b.p("**" + a["servicio"] + "** – " + a["para"]["en"])
            b.bullets(["Website: " + a["web"], "Username: `" + a["usuario"] + "`", "Password: `" + a["contrasena"] + "`"])
    else:
        b.p("The access details are in the local file `manual/accesos.json`.")
    b.box("This handbook contains passwords. Do not upload it to GitHub or other websites, and only share it with "
          "people you trust. If someone leaves the team, change the passwords.", "warn")

    b.h2("1.8 Pages CMS: the simple editor")
    b.steps([
        "Open **app.pagescms.org** and sign in with «Sign in with GitHub» (with your GitHub account, see 1.2).",
        "Choose the repository **Kampuntin-Maikiuants.github.io**.",
        "In the menu on the left, choose what you want to change (see the table). The menu names are in Spanish.",
        "Make your changes and click «Save». As with GitHub, the website updates within one to three minutes "
        "(see 1.4).",
    ])
    b.table(["In the menu", "What you change there", "See"], [
        ["Fechas de tours", "Journey dates and free places", "2.2"],
        ["Aviso (pop-up)", "Text, button and photo of the notice", "2.4"],
        ["Viajes", "Name, duration, season and text of the two journeys", "2.5"],
        ["Galería (álbumes de fotos)", "Create albums, upload and delete photos", "3.3–3.6"],
        ["Álbumes de fotos", "Title and cover of each album", "3.5"],
        ["Equipo", "Team members: photo, role, texts and links", "5.1"],
        ["Experiencias de voluntarios", "The stories on the volunteering page", "5.5"],
        ["Fotos del equipo · Otras fotos", "View, upload or delete those photos", "5.1, 5.5"],
    ], [.32, .52, .16])
    b.box("Texts in three languages have one form per language (Español, English, Français): always change all "
          "three (see 1.5). In lists, you can change the order by dragging the dots on the left of each entry.")

    b.h1("2. Tours: dates, places and the homepage notice")
    b.h2("2.1 How it works")
    b.p("There are two journeys: the **spiritual journey** (8 days) and the **Arutam journey** (10 days). "
        "Both start and end in Limón Indanza. The name, duration and description of each journey are stored once. The dates are stored separately, and each date "
        "says which journey it belongs to.")
    b.img("viajes", "The «Two journeys» section on the tours page. The programmes can be opened below.")
    b.bullets([
        "**Dates and places:** Pages CMS › Fechas de tours (2.2).",
        "**Name, duration and text of each journey:** Pages CMS › Viajes (2.5).",
        "**The homepage notice** picks the next date automatically (2.4).",
    ])
    b.h2("2.2 Adding a new date (with Pages CMS)")
    b.steps([
        "Open **app.pagescms.org** and sign in with «Sign in with GitHub».",
        "Choose the repository **Kampuntin-Maikiuants.github.io**.",
        "In the menu on the left, click **Fechas de tours** (tour dates).",
        "Below the last date, click «Add an item».",
        "Fill in the fields (see table). The form labels are in Spanish.",
        "Click «Save». Within one to three minutes the date appears on the tours page and, if it is the next one, "
        "in the homepage notice.",
    ])
    b.table(["Field (Spanish label)", "What to enter"], [
        ["Inicio (start)", "First day of the journey (exact or approximate)."],
        ["Fin (end)", "Last day of the journey."],
        ["Viaje (journey)", "Viaje espiritual (8 días) or Viaje Arutam (10 días)."],
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
    b.p("The notice always shows the next date that has not passed and is not full, with the name and duration of "
        "the journey. **Nothing needs to be changed for it to update.**")
    b.p("**Changing the text, button or photo:**")
    b.steps([
        "Pages CMS › **Aviso (pop-up)** › **English**.",
        "Change «Texto», «Texto del botón» or «Foto del aviso». You can upload a new photo directly in the photo "
        "field.",
        "Click «Save». Repeat in **Español** and **Français**.",
    ])
    b.p("**Switching the notice on or off** (on GitHub):")
    b.steps([
        "On GitHub, open the file `_config.yml` (in the main folder) and click the pencil.",
        "Find the line `tour_popup: true`.",
        "Write `false` to switch it off or `true` to switch it on, and save with «Commit changes».",
    ])
    b.h2("2.5 Changing the name, duration or description of a journey")
    b.steps([
        "Pages CMS › **Viajes** › **English**.",
        "Under «Viaje espiritual» or «Viaje Arutam», change the name, the duration (for example «8 days»), the "
        "season (for example «April – May 2027») or the short description.",
        "Click «Save». Repeat in **Español** and **Français**.",
    ])
    b.box("At the moment the website shows no prices: instead it says «Price on request». To show a price, open "
          "`_data/en/tours.yml` (and `es`, `fr`) on GitHub and add a line such as `amount: \"1,200 USD\"` below "
          "`days`. To go back to «Price on request», delete that line.")
    b.p("The detailed programme of each journey (arrival, activities and return) is changed on GitHub, in "
        "`_data/en/tours.yml` (and `es`, `fr`): in `spiritual` for the spiritual journey and in `experience` for the "
        "Arutam journey.")
    b.box("A completely new journey (a third kind of journey) needs a small technical change to the website. For "
          "that, contact the person who manages the website.", "warn")

    b.h1("3. Gallery: albums and photos")
    b.h2("3.1 How it works")
    b.p("Each album is a **folder** in the «Galería» of Pages CMS (on GitHub: `assets/galeria`). All photos in the "
        "folder appear in the album. The first photo (or the one you choose) is the cover. The order of the albums on "
        "the website is the order of the «Álbumes de fotos» list (3.5). A new album that is not yet in that list "
        "appears first. The first three albums also appear at the bottom of the tours page.")
    b.img("galeria", "The gallery: each card is an album. One click opens all photos.")
    b.p("The older folders have a number in front (`01` to `11`). New albums no longer need one.")
    b.h2("3.2 Preparing photos")
    b.bullets([
        "Format **JPG** (PNG and WebP also work).",
        "About **1600 pixels wide** and under **500 KB** per photo. Large photos make the website slow and "
        "sometimes cannot be uploaded.",
        "To shrink photos for free: **squoosh.app** in the browser, or a photo-resizing app on your phone.",
        "iPhone photos must be JPG, not HEIC. On the iPhone: Settings › Camera › Formats › «Most Compatible».",
        "Simple names without spaces or accents: `001.jpg`, `002.jpg`, … The order of the numbers is the order in "
        "the album.",
        "Ask the people in the photos for permission.",
    ])
    b.h2("3.3 Creating a new album")
    b.steps([
        "Open Pages CMS › **Galería (álbumes de fotos)**. You see the album folders.",
        "Click the button to create a folder (the folder icon with +).",
        "Enter the folder name without spaces or accents, for example `chonta-festival-2027`, and confirm.",
    ])
    b.h2("3.4 Uploading photos")
    b.steps([
        "In the «Galería», open the album folder with one click.",
        "**On a computer:** drag the photos into the window; you can drag several at once. **On a phone:** tap "
        "«Upload» and choose a photo; repeat for each photo.",
        "Each photo is saved by itself. Wait until all are done.",
        "Within one to three minutes the album appears in the gallery.",
    ])
    b.box("If a photo does not upload, it is probably too large: shrink it first (3.2).", "warn")
    b.box("For many photos at once, GitHub also works: open `assets` › `galeria` › the album folder › «Add file» › "
          "«Upload files», drag the photos in and click «Commit changes».")
    b.h2("3.5 Title and cover")
    b.p("Without further details, the album uses the folder name as its title. For a title in three languages and a "
        "chosen cover:")
    b.steps([
        "Pages CMS › **Álbumes de fotos**.",
        "Click «Add an item».",
        "Fill in **Carpeta del álbum** (the exact folder name, for example `chonta-festival-2027`), **Título** in "
        "the three languages and **Portada** (the name of a photo, for example `004.jpg`; empty = the first photo).",
        "Click «Save».",
    ])
    b.p("The order of this list is the order in the gallery. A new entry appears at the end: drag it to the top so "
        "that the album appears first.")
    b.h2("3.6 Deleting a photo or an album")
    b.steps([
        "Pages CMS › **Galería (álbumes de fotos)** › open the album folder.",
        "On the photo, open the menu (the three dots) and choose «Delete». Confirm.",
        "An album disappears from the website when it has no photos left. If it had a title in «Álbumes de fotos», "
        "delete that entry too.",
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
        "Open Pages CMS › **Equipo**.",
        "For a new person, click «Add an item». To change someone, open their entry.",
        "Fill in the fields (see the table). In «Foto» you can upload the photo directly.",
        "Click «Save».",
    ])
    b.table(["Field", "What to enter"], [
        ["Nombre", "First and last name."],
        ["Nombre shuar", "Optional. Shown below the name."],
        ["Grupo", "«Kampuntin: equipo en Maikiuants»."],
        ["Foto", "The square photo. Without a photo, the first letter of the name is shown."],
        ["Mostrar el enlace «Escríbenos»", "Only for contact persons."],
        ["Función", "The role, for example «Secretary of Kampuntin», in the three languages."],
        ["Texto corto · Texto largo", "The description in the three languages. If there is a long text, it is shown."],
        ["Enlaces", "Optional: the text («Instagram», «Facebook») and the link to the profile."],
    ], [.34, .66])
    b.p("The order of the list is the order on the website: to move someone, drag their entry.")
    b.box("To change a photo, upload the new one with a different name (for example `eddy-2.jpg`) and choose it in "
          "«Foto». This way browsers show the new photo straight away. Only publish photos and texts of people with "
          "their permission.")
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
        "a short quote that is always visible, the name, a small line (for example «Volunteering · October 2026») "
        "and, if you like, the full story to open and a small photo.")
    b.steps([
        "Ask the person for a short quote (one to three sentences), how they want to appear, whether they also want a "
        "longer story and a photo. **Ask for their permission to publish it.**",
        "Open Pages CMS › **Experiencias de voluntarios** › **English**.",
        "Under «Experiencias», click «Add an item» and drag the new entry to the top of the list: the first "
        "card is the newest.",
        "Fill in **Cita corta** (quote), **Nombre** (name), **Línea pequeña** (small line), optionally **Foto** "
        "(square, about 300 × 300 pixels) and optionally **Relato completo** (full story; an empty line separates "
        "paragraphs).",
        "Click «Save». Repeat in **Español** and **Français** with the translated text.",
    ])
    b.box("Without a full story, the «Read the full story» button does not appear. To remove a story, delete it from "
          "the list in all three languages.")

    b.h2("5.6 The footer")
    b.p("The footer appears at the bottom of every page. Each part is changed in a different place:")
    b.table(["Part", "Where to change it"], [
        ["Box «Would you like to visit Maikiuants?» (title, text and button)", "`_data/en/ui.yml` › `cta`"],
        ["Sentence below the logo and column headings", "`_data/en/ui.yml` › `footer`"],
        ["Official name of the organisation", "`_config.yml` › `org_name`"],
        ["«Explore» column (order of the pages)", "`_data/navigation.yml`"],
        ["«Contact» column: general email and contact persons", "`_config.yml` › `contact` (see 5.3)"],
        ["«Follow us» column: Instagram, Facebook, WWOOF and other links", "`_config.yml` › `social`"],
    ], [.55, .45])
    b.p("The texts in `ui.yml` exist in all three languages: change them in `_data/es/ui.yml` and "
        "`_data/fr/ui.yml` too.")
    b.p("**Adding, changing or removing a social network** (in `_config.yml`, under `social:`):")
    b.bullets([
        "**Instagram:** `handle` is the account name without @, `url` is the link. To remove Instagram, leave the "
        "link empty: `url: \"\"`.",
        "**Facebook:** each page is two lines, `- name:` and `url:`. To add a page, copy the two lines and paste "
        "them below. To remove one, delete its two lines.",
        "**WWOOF:** to remove it, write `wwoof: \"\"`. This also removes the WWOOF button on the volunteering page.",
        "**Other links** (for example a second Instagram account or YouTube): replace `links: []` with a list like "
        "the one in the example. Each link is two lines: the text shown (`name`) and the link (`url`).",
    ])
    b.code('  links:\n    - name: "Instagram · Freddy"\n      url: "https://www.instagram.com/nekas_chicham/"\n'
           '    - name: "YouTube"\n      url: "https://www.youtube.com/@..."', "Example: other links in _config.yml")
    b.box("Instagram and Facebook also appear as cards on the Updates page (see 4.2). What you change in `social` "
          "shows up in both places. «Other links» only appear in the footer.")

    b.h1("6. The address: www.kampuntin.org")
    b.p("The website is at **www.kampuntin.org**. The domains **kampuntin.org** and **kampuntin.com** are registered "
        "with **Cloudflare** (access in 1.7). All these addresses lead automatically to https://www.kampuntin.org: "
        "kampuntin.org, kampuntin.com, www.kampuntin.com and the old address kampuntin-maikiuants.github.io. The "
        "website stays free on GitHub; only the domains cost money.")
    b.h2("6.1 Renewing the domains")
    b.steps([
        "Sign in at **cloudflare.com** (details in 1.7).",
        "In the menu on the left: «Domain Registration» › «Manage Domains». There you see both domains and their "
        "expiry date.",
        "Check that «Auto-renew» is switched on for both and that the saved payment method is still valid. Cloudflare "
        "charges the renewal once a year.",
    ])
    b.box("If a domain expires, the website can no longer be reached at that address. Share the Cloudflare access "
          "with a second trusted person.", "warn")
    b.h2("6.2 How it is set up")
    b.p("Normally nothing needs to be changed. If something stops working, compare with this list.")
    b.p("**kampuntin.org** in Cloudflare › «DNS» › «Records»:")
    b.table(["Type", "Name", "Content", "Proxy status"], DNS, [.14, .16, .45, .25])
    b.bullets([
        "«SSL/TLS» › «Overview»: mode **Full** (or «Automatic», which uses Full). Do **not** choose «Full (Strict)»: "
        "the website would show an error.",
        "«SSL/TLS» › «Edge Certificates»: «Always Use HTTPS» switched on. This sends everyone to the secure version "
        "(https).",
    ])
    b.p("**On GitHub:**")
    b.bullets([
        "«Settings» › «Pages» › «Custom domain»: `www.kampuntin.org`.",
        "The repository contains a file `CNAME` with the text `www.kampuntin.org`. Do not delete it.",
        "`_config.yml` contains the line `url: \"https://www.kampuntin.org\"`. It makes the links for Google and the "
        "link preview use the correct address.",
    ])
    b.box("Recommended, if not done yet: verify the domain on GitHub so nobody else can use it with GitHub Pages. In "
          "the settings of the Kampuntin-Maikiuants organisation: «Settings» › «Pages» › «Add a domain». GitHub gives "
          "you a TXT record; create it in Cloudflare (kampuntin.org › «DNS» › «Records» › «Add record») and go back "
          "to GitHub to confirm.")
    b.h2("6.3 kampuntin.com: the redirect")
    b.p("kampuntin.com has no website of its own: Cloudflare sends all visitors to www.kampuntin.org. This is how it "
        "is set up in Cloudflare › **kampuntin.com**:")
    b.bullets([
        "«DNS» › «Records»: `A` · `@` · `192.0.2.1` and `CNAME` · `www` · `kampuntin.com`, both **Proxied** (orange "
        "cloud). The address 192.0.2.1 is only a placeholder.",
        "«Rules» › «Redirect Rules»: one rule for «All incoming requests» with «Type» = «Static», «URL» = "
        "`https://www.kampuntin.org` and «Status code» = 301.",
    ])
    b.h2("6.4 If the website does not open")
    b.bullets([
        "Check in Cloudflare that the domains have not expired (6.1).",
        "Compare the settings with 6.2. A common mistake is the «Full (Strict)» mode: change it to «Full».",
        "On GitHub, «Settings» › «Pages»: «Custom domain» must still be `www.kampuntin.org`. If it is empty, enter it "
        "again and click «Save».",
        "If only kampuntin.com fails, check the rule in 6.3.",
    ])
    b.h2("6.5 An email address with the domain (optional)")
    b.p("With Cloudflare's free email forwarding you can create an address such as info@kampuntin.org that arrives in "
        "an existing inbox, for example ocstkampuntin@gmail.com: Cloudflare › kampuntin.org › «Email» › «Email "
        "Routing», then follow the steps.")

    b.h1("7. Getting found on Google")
    b.p("Google only shows the website if it knows that it exists. With the **Google Search Console** you tell Google "
        "about it, and you can also see which searches bring people to the website and whether there are problems. "
        "It is free and only needs to be set up once.")
    b.h2("7.1 Registering kampuntin.org in Google Search Console")
    b.steps([
        "Open **search.google.com/search-console** and sign in with Kampuntin's Google account "
        "(ocstkampuntin@gmail.com), so that access stays with the organisation.",
        "Click «Add property». Choose the option on the left, «Domain», and enter `kampuntin.org`.",
        "Google recognises that the domain is with Cloudflare and offers to do the verification there. Accept, sign in "
        "to Cloudflare (details in 1.7) and allow it. Google creates the required record by itself.",
        "If that option does not appear: copy the TXT value Google shows. In Cloudflare, open kampuntin.org › «DNS» › "
        "«Records» › «Add record»: «Type» `TXT`, «Name» `@`, paste the value into «Content» and save. Go back to Google "
        "and click «Verify».",
    ])
    b.box("Do not delete Google's TXT record in Cloudflare later. Google checks it from time to time; without it, "
          "access to Search Console is lost.", "warn")
    b.h2("7.2 Submitting the sitemap and requesting indexing")
    b.steps([
        "In the menu on the left, «Sitemaps»: enter `https://www.kampuntin.org/sitemap.xml` and click «Submit». The "
        "sitemap is created automatically and contains all pages in all three languages.",
        "In the bar at the top («Inspect any URL»), enter `https://www.kampuntin.org/` and click «Request indexing». "
        "Do the same for the most important pages, for example `https://www.kampuntin.org/tours/`, `/en/` and `/fr/`.",
        "Now you have to wait: the website usually appears on Google after a few days to two weeks. To check, search "
        "Google for `site:kampuntin.org`.",
    ])
    b.box("To give another person access: «Settings» › «Users and permissions» › «Add user».")
    b.h2("7.3 Links from other websites")
    b.p("Google trusts a website more when other websites link to it. So it is worth putting **www.kampuntin.org** "
        "everywhere:")
    b.bullets([
        "On the Kampuntin and Maikiuants Facebook pages («Website» field) and in the Instagram bio.",
        "On the WWOOF profile and on the websites of partner organisations.",
        "On flyers and in email signatures.",
        "On GitHub, in the Kampuntin-Maikiuants organisation: «Settings» › «Profile», with a description (for example "
        "«Kampuntin website») and the URL `https://www.kampuntin.org`.",
        "Optional: a Google Maps profile («Google Business Profile») for Kampuntin in Maikiuants, with the address of "
        "the website. Then a map also appears when someone searches for «Kampuntin».",
    ])
    b.h2("7.4 Bing, DuckDuckGo and other search engines")
    b.p("At **bing.com/webmasters** you can import the website from Google Search Console with one click. This way the "
        "website also reaches Bing, DuckDuckGo, Ecosia and Yahoo.")
    b.box("Some search engines also show the GitHub page of Kampuntin-Maikiuants (the website's code). This is normal "
          "and not a problem: it only contains what is already visible on the website, no passwords. Once "
          "www.kampuntin.org is registered, it will appear higher up.")

    b.h1("8. If something goes wrong")
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
        ["The website does not open at www.kampuntin.org", "See 6.4."],
    ], [.3, .7])
    b.p("**Help:** Jesko Dorner · jesko.dorner@gmail.com")
    b.h2("Quick reference")
    b.table(["Task", "Where", "Tool"], [
        ["New tour date, free places", "Fechas de tours", "Pages CMS"],
        ["Name, duration or text of a journey", "Viajes", "Pages CMS"],
        ["Text or photo of the notice", "Aviso (pop-up)", "Pages CMS"],
        ["New album, upload or delete photos", "Galería (álbumes de fotos)", "Pages CMS"],
        ["Album title or cover", "Álbumes de fotos", "Pages CMS"],
        ["Team member", "Equipo", "Pages CMS"],
        ["Volunteer story", "Experiencias de voluntarios", "Pages CMS"],
        ["Price or detailed programme of a journey", "`_data/es|en|fr/tours.yml`", "GitHub"],
        ["Notice on or off", "`_config.yml` › `tour_popup`", "GitHub"],
        ["Facebook and Instagram accounts", "`_config.yml` › `social`", "GitHub"],
        ["Automatic posts", "Secret `FB_PAGE_TOKENS`", "GitHub and Facebook"],
        ["Instagram post manually", "`_data/instagram_embeds.yml`", "GitHub"],
        ["Contact persons", "`_config.yml` › `contact`", "GitHub"],
        ["Footer: social networks and texts", "`_config.yml` › `social`; `_data/es|en|fr/ui.yml` › `footer`", "GitHub"],
        ["Videos", "`_data/videos.yml` and `assets/video`", "GitHub"],
        ["Domains, renewal and DNS", "Cloudflare (access in 1.7, settings in 6)", "Cloudflare and GitHub"],
        ["Getting found on Google", "Search Console, «Domain» property kampuntin.org (see 7)", "Google and Cloudflare"],
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

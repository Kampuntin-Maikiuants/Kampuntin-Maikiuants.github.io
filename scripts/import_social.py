#!/usr/bin/env python3
"""
Holt die neuesten Beiträge der Facebook-Seiten (und eines verknüpften Instagram-Kontos)
über die offizielle Graph API und legt sie als Website-Inhalte ab:

  _data/social_posts.json   – Text, Datum, Link, Bildpfade
  assets/img/social/         – heruntergeladene Fotos

Benötigt die Umgebungsvariable FB_PAGE_TOKENS: ein oder mehrere Seiten-Zugriffstoken
(eins pro Zeile oder durch Komma getrennt). Ohne Token passiert nichts.
Nur Python-Standardbibliothek – läuft direkt auf GitHub Actions.
"""
import json, os, re, sys, urllib.parse, urllib.request

API = "https://graph.facebook.com/" + os.environ.get("GRAPH_API_VERSION", "v26.0")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data", "social_posts.json")
IMG_DIR = os.path.join(ROOT, "assets", "img", "social")
IMG_URL = "/assets/img/social/"
PER_SOURCE = int(os.environ.get("POSTS_PER_SOURCE", "12"))
MAX_TOTAL = int(os.environ.get("MAX_POSTS", "24"))
MAX_IMAGES = 6


def get(path, token, **params):
    params["access_token"] = token
    url = path if path.startswith("http") else f"{API}/{path}"
    url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def download(url, name):
    os.makedirs(IMG_DIR, exist_ok=True)
    dst = os.path.join(IMG_DIR, name)
    if not os.path.exists(dst):
        with urllib.request.urlopen(url, timeout=60) as r, open(dst, "wb") as f:
            f.write(r.read())
    return IMG_URL + name


def safe(s):
    return re.sub(r"[^A-Za-z0-9_-]", "_", s)


def facebook_posts(page, token):
    fields = ("id,message,created_time,permalink_url,full_picture,"
              "attachments{media_type,media,subattachments{media_type,media}}")
    data = get(f"{page['id']}/posts", token, fields=fields, limit=PER_SOURCE).get("data", [])
    posts = []
    for p in data:
        urls = []
        for att in (p.get("attachments") or {}).get("data", []):
            subs = (att.get("subattachments") or {}).get("data", [])
            for a in (subs or [att]):
                src = ((a.get("media") or {}).get("image") or {}).get("src")
                if src and a.get("media_type") in (None, "photo", "album", "share", "link"):
                    urls.append(src)
        if not urls and p.get("full_picture"):
            urls.append(p["full_picture"])
        text = (p.get("message") or "").strip()
        if not text and not urls:
            continue
        pid = safe(p["id"])
        images = [download(u, f"fb-{pid}-{i}.jpg") for i, u in enumerate(urls[:MAX_IMAGES])]
        posts.append({"id": "fb-" + pid, "source": "facebook", "account": page["name"],
                      "url": p.get("permalink_url") or page.get("link", ""),
                      "date": p["created_time"], "text": text, "images": images})
    return posts


def instagram_posts(ig, token):
    fields = ("id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,"
              "children{media_type,media_url,thumbnail_url}")
    data = get(f"{ig['id']}/media", token, fields=fields, limit=PER_SOURCE).get("data", [])
    posts = []
    for m in data:
        items = (m.get("children") or {}).get("data") or [m]
        urls = [(c.get("thumbnail_url") if c.get("media_type") == "VIDEO" else c.get("media_url")) for c in items]
        urls = [u for u in urls if u]
        pid = safe(m["id"])
        images = [download(u, f"ig-{pid}-{i}.jpg") for i, u in enumerate(urls[:MAX_IMAGES])]
        posts.append({"id": "ig-" + pid, "source": "instagram", "account": "@" + ig.get("username", ""),
                      "url": m.get("permalink", ""), "date": m["timestamp"],
                      "text": (m.get("caption") or "").strip(), "images": images})
    return posts


def main():
    tokens = [t.strip() for t in re.split(r"[\n,]", os.environ.get("FB_PAGE_TOKENS", "")) if t.strip()]
    if not tokens:
        # ::warning:: erscheint auf GitHub direkt in der Übersicht des Durchlaufs
        print("::warning title=Facebook-Import::Kein Secret FB_PAGE_TOKENS gesetzt – Import übersprungen. "
              "Einrichtung: Handbuch (PDF), Kapitel 4.3.")
        return 0
    try:
        old = json.load(open(DATA, encoding="utf-8"))
    except (OSError, ValueError):
        old = []
    fresh, done_accounts, errors = [], set(), 0
    for token in tokens:
        try:
            page = get("me", token, fields="id,name,link,instagram_business_account{id,username}")
            fresh += facebook_posts(page, token)
            done_accounts.add(page["name"])
            print(f"Facebook „{page['name']}“: ok")
            ig = page.get("instagram_business_account")
            if ig:
                fresh += instagram_posts(ig, token)
                done_accounts.add("@" + ig.get("username", ""))
                print(f"Instagram @{ig.get('username')}: ok")
        except Exception as e:  # ein Konto mit Problem soll die anderen nicht blockieren
            errors += 1
            detail = ""
            if hasattr(e, "read"):  # Fehlermeldung von Facebook mitlesen
                try:
                    detail = json.load(e).get("error", {}).get("message", "")
                except Exception:
                    pass
            print(f"::error title=Facebook-Import::Token Nr. {tokens.index(token) + 1}: {e} {detail}")
    # Beiträge von Konten, die diesmal nicht geladen werden konnten, behalten
    kept = [p for p in old if p.get("account") not in done_accounts]
    posts = {p["id"]: p for p in kept + fresh}.values()
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)[:MAX_TOTAL]
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    # Bilder entfernen, die zu keinem Beitrag mehr gehören
    used = {os.path.basename(i) for p in posts for i in p["images"]}
    if os.path.isdir(IMG_DIR):
        for name in os.listdir(IMG_DIR):
            if name.startswith(("fb-", "ig-")) and name not in used:
                os.remove(os.path.join(IMG_DIR, name))
    print(f"::notice title=Facebook-Import::{len(fresh)} Beiträge geladen, {len(posts)} gespeichert "
          f"({', '.join(sorted(done_accounts)) or 'keine Konten'}).")
    return 1 if errors and not fresh else 0


if __name__ == "__main__":
    sys.exit(main())

"""Download Google Fonts subsets covering exactly the characters used in index.html.

Writes fonts/*.woff2 and fonts/fonts.css so rendering needs no network access.
"""
import html
import pathlib
import re
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "fonts"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
FAMILIES = {
    "Noto Sans SC": "400;500;700",
    "Noto Serif SC": "500;700",
    "JetBrains Mono": "500",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.read()


def main():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    body = re.sub(r"<style>.*?</style>", "", src, flags=re.S)
    chars = set(html.unescape(body)) | set(" 0123456789/·.$\"")
    text = "".join(sorted(c for c in chars if c.isprintable()))

    OUT.mkdir(exist_ok=True)
    css_out = []
    for fam, weights in FAMILIES.items():
        q = urllib.parse.urlencode({"family": f"{fam}:wght@{weights}", "text": text, "display": "block"})
        css = get("https://fonts.googleapis.com/css2?" + q).decode()
        for i, block in enumerate(re.findall(r"@font-face\s*{[^}]*}", css)):
            url = re.search(r"url\((https://[^)]+)\)", block).group(1)
            weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
            name = f"{fam.replace(' ', '')}-{weight}.woff2"
            (OUT / name).write_bytes(get(url))
            css_out.append(re.sub(r"url\([^)]+\)", f"url({name})", block))
            print("saved", name)
    (OUT / "fonts.css").write_text("\n".join(css_out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

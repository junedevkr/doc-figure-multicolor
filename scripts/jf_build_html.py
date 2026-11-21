#!/usr/bin/env python3
"""spec JSON → 자기완결 HTML (크롬·파이썬 패키지 없이, 표준 라이브러리만)

  python3 scripts/jf_build_html.py 그림_01.json [그림_02.json ...]

템플릿 마커(프리셋 CSS·spec·아이콘)를 치환하고 june-figure 페이지 틀(기본 16:9)과 글꼴을 입힌다.
결과는 spec 옆에 같은 이름의 .html. 여러 장을 한 파일로 넘겨 보려면 jf_build_deck.py.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import jf_page

FORMS = ["cycle", "funnel", "venn", "quadrant", "pyramid", "concentric", "hub", "fishbone",
         "staircase", "before-after", "waterfall", "iceberg", "swimlane", "logic-tree"]

def walk(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("icon", "dept_icon") and isinstance(v, str):
                out.add(v)
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)

def load_spec(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    if not spec.get("template"):
        sys.exit("spec에 template 필드가 필요합니다: %s" % spec_path)
    if spec["template"] in FORMS:   # 도식 형태 25종은 forms 템플릿 하나가 그린다
        spec = dict(spec, form=spec["template"], template="forms")
    return spec

def preset_css(spec):
    return open(os.path.join(ROOT, "presets", spec.get("preset", "jf-method") + ".css"), encoding="utf-8").read()

def build_string(spec, embed=False):
    spec = jf_page.prepare_spec(spec)
    tpl = jf_page.prepare_template(open(os.path.join(ROOT, "templates", spec["template"] + ".html"), encoding="utf-8").read())
    allicons = json.load(open(os.path.join(ROOT, "templates", "icons", "tabler-outline.json"), encoding="utf-8"))
    used = set(); walk(spec, used)
    miss = used - set(allicons)
    if miss:
        sys.exit("없는 아이콘: %s" % ", ".join(sorted(miss)))
    data = json.dumps(spec, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("/*__STYLE_TOKENS__*/", preset_css(spec), 1)
    html = html.replace("/*__FIGURE_DATA__*/ null", data, 1).replace("/*__FIGURE_DATA__*/", data, 1)
    html = html.replace("/*__ICON_SET__*/ {}", json.dumps({k: allicons[k] for k in used}, ensure_ascii=False), 1)
    html = html.replace("/*__ICONS__*/ {}", "{}", 1)
    return jf_page.apply(html, spec, embed=embed)

def build(spec_path):
    spec = load_spec(spec_path)
    out = os.path.splitext(spec_path)[0] + ".html"
    open(out, "w", encoding="utf-8").write(build_string(spec))
    m = jf_page.mode(spec)
    print("✓ %s  preset=%s  page=%s" % (out, spec.get("preset"), ("%s %dx%d" % ((m,) + jf_page.size(spec))) if m else "none"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        build(p)

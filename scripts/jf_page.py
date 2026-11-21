#!/usr/bin/env python3
"""doc-figure-multicolor 페이지 틀 (표준 라이브러리만)

기본값: 16:9 페이지(1920×1080 기준). 비율을 유지한 채 화면 폭에 맞춰 통째로 확대·축소한다(안쪽 재배치 없음).
- 모든 페이지가 같은 안쪽 여백(page_pad, 기본 64px)과 같은 내용 폭(1792px)을 쓴다
- 그림은 페이지 위쪽 여백에 붙여 놓아 페이지마다 제목 위치가 같다
- board는 페이지 높이의 88~100%를 채우도록 본문 배치 기준(print_cm)을 조정해 다시 그린다(넘치면 글자를 줄이고, 비면 키움, 폭은 그대로).
  가장 큰 본문 글자는 print_cm 16(문서 삽입 기본) 수준까지 — spec "page_min_cm"으로 조정.
  그래도 88%에 못 미치면 남는 높이를 본문 행 사이 간격으로 나눈다(최대 120px)
- 바깥 배경(내용 계열 주색을 섞은 회색)과 페이지 바탕(--bg)을 다른 색으로 둔다
- 글꼴은 spec "font": "gothic"(기본, 프리젠테이션) | "myeongjo"(명조, Noto Serif KR). 글꼴을 내려받은 뒤 도식을 그린다
- 인쇄(PDF)하면 바깥 배경 없이 페이지만 1920×1080 한 장으로 나온다
- 그린 뒤 글자와 실제 바탕의 대비를 재서 일반 글자 4.5, 큰 굵은 글자 3.0에 못 미치면 글자색을 자동으로 진하게(짙은 바탕이면 밝게) 맞춘다

spec 필드
  "page": "16:9"(기본) | "4:3" | "none"(보고서·논문 본문 삽입용 원본 그림)
  "page_pad": 페이지 안쪽 여백 px (기본 64)

여러 장을 한 HTML로 넘겨 보려면 scripts/jf_build_deck.py를 쓴다.
"""
import json, os, re

PAGE_W = 1920
MARGIN = 40            # 단독 HTML의 바깥 배경 여백
DEFAULT_PAD = 64
PAGE_PRINT_CM = 26     # 페이지 모드 board 배치 폭 기준(문서 삽입 기본 16cm보다 넓게)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_CSS = os.path.join(ROOT, "references", "jf-font.css")
FONT_STACK = '"Presentation", "PresentationVariable", "Pretendard", "Apple SD Gothic Neo", "NanumSquare", "NanumGothic", "Malgun Gothic", sans-serif'

def mode(spec):
    v = spec.get("page", "16:9")
    return None if v in (None, False, "none", "off") else str(v)

def size(spec):
    rw, rh = (float(x) for x in mode(spec).split(":"))
    return PAGE_W, int(round(PAGE_W * rh / rw))

def pad(spec):
    return int(spec.get("page_pad", DEFAULT_PAD))

def window(spec):
    """PNG 렌더용 창 크기 (페이지 + 바깥 배경 여백)"""
    w, h = size(spec)
    return w + 2 * MARGIN, h + 2 * MARGIN

def prepare_template(tpl):
    """다시 그릴 수 있도록 전역 선언을 var로 바꾸고, 다시 그릴 때 덮어쓸 값을 받는 자리를 둔다"""
    # 템플릿마다 띄어쓰기가 달라도(const FIGURE = …) 다시 그릴 수 있게 var로 바꾼다
    tpl = re.sub(r"\bconst\s+FIGURE\s*=\s*/\*__FIGURE_DATA__\*/\s*null",
                 "var FIGURE=/*__FIGURE_DATA__*/ null;if(window.__JF_OVERRIDE__&&FIGURE)Object.assign(FIGURE,window.__JF_OVERRIDE__)", tpl, count=1)
    return re.sub(r"\b(?:const|let)\s+(ICONS|ICON_SET)\s*=", r"var \1=", tpl)

def prepare_spec(spec):
    """페이지 모드에서 board 폭을 페이지 안쪽 폭에 맞춘다(화살표를 그리기 전에 정해야 한다)"""
    if mode(spec) and spec.get("template") == "board":
        spec = dict(spec, width=PAGE_W - 2 * pad(spec))   # 페이지마다 내용 폭을 같게 — spec의 width는 페이지 모드에서 쓰지 않음
        if not spec.get("print_cm"):
            spec = dict(spec, print_cm=PAGE_PRINT_CM)
    return spec

def concept(spec):
    """프리셋 머리 주석의 '@concept: pop|soft'로 컬러 컨셉을 정한다"""
    path = os.path.join(ROOT, "presets", str(spec.get("preset", "")) + ".css")
    if not os.path.exists(path):
        return None
    mo = re.search(r"@concept:\s*([a-z]+)", open(path, encoding="utf-8").read(2000))
    return mo.group(1) if mo else None

FONT_LIST = os.path.join(ROOT, "references", "jf-fonts.json")
FALLBACK = {"gothic": '"Pretendard", "Apple SD Gothic Neo", "NanumSquare", "NanumGothic", "Malgun Gothic", sans-serif',
            "myeongjo": '"AppleMyungjo", "Nanum Myeongjo", "NanumMyeongjo", "Batang", serif'}

def _load_fonts():
    d = json.load(open(FONT_LIST, encoding="utf-8"))
    fonts, defaults = {}, {}
    for f in d["fonts"]:
        stack = '"%s", %s' % (f["family"], FALLBACK[f["kind"]])
        if f["key"] == "presentation":
            stack = FONT_STACK
        fonts[f["key"]] = dict(f, css=os.path.join(ROOT, "references", "fonts", f["file"]), stack=stack)
        defaults.setdefault(f["kind"], f["key"])
    return fonts, defaults

FONTS, FONT_DEFAULT = _load_fonts()
SERIF_STACK = FONTS[FONT_DEFAULT["myeongjo"]]["stack"]

def font_kind(spec):
    """spec "font": 글꼴 키(jf-fonts.json) | "gothic"·"고딕"(기본 고딕) | "myeongjo"·"명조"(기본 명조) — 글꼴 키를 돌려준다"""
    v = str(spec.get("font", "gothic")).strip()
    low = v.lower()
    if low in FONTS:
        return low
    for k, f in FONTS.items():
        if v == f["label"]:
            return k
    if low in ("myeongjo", "명조", "serif", "mincho"):
        return FONT_DEFAULT["myeongjo"]
    return FONT_DEFAULT["gothic"]

def font_css(key="presentation"):
    key = key if key in FONTS else font_kind({"font": key})
    f = FONTS[key]
    css = open(f["css"], encoding="utf-8").read()
    if key != "presentation":   # 프리셋의 글꼴 토큰을 덮어쓴다(@import는 맨 앞에 와야 함)
        css += "\n:root.jf-font-%s { --font: %s; --font-title: %s; --board-font: %s; }\n" % (key, f["stack"], f["stack"], f["stack"])
    return css

PAGE_CSS = r"""
html.jf-page, html.jf-page body { background: color-mix(in srgb, var(--tone-main, #555) 12%, #D4D2CE) !important; }
html.jf-page body { margin: 0; padding: __M__px; }
html.jf-page { scrollbar-gutter: stable; }
#jf-fit { position: relative; margin: 0 auto; }
#jf-fit > #jf-page { position: absolute; left: 0; top: 0; transform-origin: 0 0; }
html.jf-page.jf-embed, html.jf-page.jf-embed body { background: var(--bg, #fff) !important; overflow: hidden; }
html.jf-page.jf-embed body { padding: 0; }
#jf-page { position: relative; overflow: hidden; background: var(--bg, #fff); flex: none;
  box-shadow: 0 8px 28px rgba(0,0,0,.16), 0 0 0 1px rgba(0,0,0,.06); }
html.jf-embed #jf-page { box-shadow: none; }
#jf-page > #figure { position: absolute; left: 0; top: 0; transform-origin: 0 0; background: transparent; }
/* 제목 크기는 페이지마다 같게 — 본문 배치 기준(print_cm)이 페이지별로 달라져도 머리는 고정 px */
html.jf-page #figure .hd { margin-bottom: 26px; }
html.jf-page #figure .hd .kicker { font-size: calc(24px / var(--jf-s, 1)) !important; color: var(--ink-soft) !important; font-weight: 600; margin-bottom: 6px; }
html.jf-page #figure .hd h1 { font-size: calc(42px / var(--jf-s, 1)) !important; line-height: 1.25 !important; letter-spacing: -0.5px; }
html.jf-page #figure .hd .sub { font-size: calc(24px / var(--jf-s, 1)) !important; }
html.jf-page #figure .hd .tag { font-size: calc(20px / var(--jf-s, 1)) !important; }
/* 글자 값이 든 표(matrix에 문자열 값) — 점 칸용 작은 칸 대신 폭을 채우는 표로 */
html.jf-page #figure .mtx:has(td.v) { width: 100%; border-spacing: 6px; padding: 10px; }
html.jf-page #figure .mtx:has(td.v) th { font-size: calc(var(--B) * 0.9); color: var(--ink-soft); padding: 4px 8px; }
html.jf-page #figure .mtx:has(td.v) th.rh { width: 20%; text-align: left; font-size: calc(var(--B) * 0.92); color: var(--ink); }
html.jf-page #figure .mtx:has(td.v) td { width: auto; height: calc(var(--B) * 2); font-size: calc(var(--B) * 0.92); border-radius: 8px; }
html.jf-page #figure .mtx td.v { background: var(--tt, var(--tone-main-tint)); color: var(--ink); border-color: transparent; }
/* 세로 색 막대 대신 제목 위 짧은 가로 표식 (forms의 제목 표식도 같은 크기) */
html.jf-page #figure::before { width: 48px !important; height: 6px !important; }
html.jf-page #figure .hd.headline { padding-left: 0 !important; padding-top: 20px; padding-bottom: 18px; }
html.jf-page #figure .hd.headline::before { left: 0 !important; top: 0 !important; bottom: auto !important; width: 48px !important; height: 6px !important; background: var(--tone-main) !important; }
/* ===== 평면 모양(jf-flat): 쨍한 컨셉·출처 팔레트 컨셉 공통 — 테두리 없는 색 면, 큰 둥근 모서리, 검은 제목 ===== */
html.jf-flat #figure .hd h1 { color: var(--ink) !important; font-weight: 800; }
html.jf-flat #figure .hd.headline { border-bottom: 0 !important; }
html.jf-flat #figure .hd.headline::before { width: 64px !important; height: 8px !important; border-radius: 4px; }
html.jf-flat #figure .group { border: 0 !important; border-radius: 26px !important; background: var(--tt, var(--tone-main-tint)) !important; }
html.jf-flat #figure .group > .gh { background: transparent !important; color: var(--tc, var(--tone-main)) !important; text-align: left; padding: 20px 24px 2px !important; font-size: calc(var(--B) * 1.1) !important; }
html.jf-flat #figure .group > .gb { padding: 14px 20px 20px !important; }
html.jf-flat #figure .card { border: 0 !important; border-radius: 18px !important; }
html.jf-flat #figure .group .card:not(.f-solid):not(.focus) { --card-bg: #fff; }
html.jf-flat #figure .card .chd { border-radius: 0; }
html.jf-flat #figure .band { border: 0 !important; border-radius: 18px !important; }
html.jf-flat #figure .band .bl { background: rgba(0,0,0,.16); }
html.jf-flat #figure .band.soft .bl { background: var(--tc, var(--tone-main)); }
html.jf-flat #figure .tline { border: 0 !important; border-radius: 20px !important; }
html.jf-flat #figure .tline .tl-bar, html.jf-flat #figure .tline .tl-bar > div { height: 14px; }
html.jf-flat #figure .chips .chip { border: 0 !important; }
html.jf-flat #figure .pill { border-radius: 999px; }
html.jf-flat #figure .steps .st { font-weight: 800; }

/* ===== 쨍한 컨셉(jf-pop): 짙은 바깥 배경 + 핑크 표식 ===== */
html.jf-page.jf-pop, html.jf-page.jf-pop body { background: #17171D !important; }
html.jf-page.jf-pop.jf-embed, html.jf-page.jf-pop.jf-embed body { background: var(--bg, #fff) !important; }
html.jf-pop #jf-page { box-shadow: 0 18px 50px rgba(0,0,0,.45); }
html.jf-pop #figure .hd.headline::before { background: var(--tone-sub) !important; }
html.jf-pop #figure::before { background: var(--tone-sub) !important; }

/* ===== 짙은 바탕 컨셉(jf-deep): 주색을 바깥 배경으로, 표식은 강조색 ===== */
html.jf-page.jf-deep, html.jf-page.jf-deep body { background: var(--tone-main) !important; }
html.jf-page.jf-deep.jf-embed, html.jf-page.jf-deep.jf-embed body { background: var(--bg, #fff) !important; }
html.jf-deep #jf-page { box-shadow: 0 18px 50px rgba(0,0,0,.35); }
html.jf-deep #figure .hd.headline::before, html.jf-deep #figure::before { background: var(--tone-wait) !important; }
html.jf-deep #figure .card .ct, html.jf-deep #figure .group > .gh { color: var(--ink) !important; }

/* ===== 파스텔 출처 팔레트(jf-soft): 원본 색 면 위 글자를 짙은 색으로, 화살표는 짙은 회갈색 ===== */
html.jf-page.jf-soft, html.jf-page.jf-soft body { background: var(--tone-main-tint) !important; }
html.jf-page.jf-soft.jf-embed, html.jf-page.jf-soft.jf-embed body { background: var(--bg, #fff) !important; }
html.jf-soft #jf-page { box-shadow: 0 14px 40px rgba(60,30,30,.14); }
html.jf-soft #figure .hd.headline::before, html.jf-soft #figure::before { background: var(--tone-sub) !important; }
html.jf-soft #figure .group > .gh, html.jf-soft #figure .card .chd, html.jf-soft #figure .band, html.jf-soft #figure .band .bl,
html.jf-soft #figure .band .bt .s, html.jf-soft #figure .pill, html.jf-soft #figure .steps .st, html.jf-soft #figure .steps .st .s,
html.jf-soft #figure .chips .clabel, html.jf-soft #figure .card.f-solid, html.jf-soft #figure .card.f-solid .ct,
html.jf-soft #figure .card.f-solid .cs, html.jf-soft #figure .card.f-solid li, html.jf-soft #figure .card .ct,
html.jf-soft #figure .card .cv, html.jf-soft #figure .card .kpi .to, html.jf-soft #figure .card .kpi .ar,
html.jf-soft #figure .tline .tl-labels > div, html.jf-soft #figure .diamond .dt, html.jf-soft #figure .card .numc,
html.jf-soft #figure .card .num-in, html.jf-soft #figure ul.items.b-num li::before { color: var(--ink) !important; opacity: 1 !important; }
html.jf-soft #figure .card.f-solid .kpi .from, html.jf-soft #figure .card.f-solid .kpi .at { color: var(--ink-soft) !important; opacity: 1 !important; }
html.jf-soft #figure .band .bl { background: rgba(255,255,255,.42) !important; }
html.jf-soft #figure .card.f-solid li::before, html.jf-soft #figure ul.items li::before { background: var(--ink-soft) !important; }
html.jf-soft #figure .card .ic svg, html.jf-soft #figure .chips .chip svg, html.jf-soft #figure .band .bl svg { stroke: var(--ink-soft) !important; }
html.jf-soft #figure .card.f-solid .ic { background: rgba(255,255,255,.5); }
html.jf-soft #figure .diamond svg.dshape path { stroke: var(--ink-soft) !important; }
html.jf-soft #figure svg#links .lk { stroke: var(--ink-soft) !important; }
html.jf-soft #figure svg#links marker path, html.jf-soft #figure svg#links marker polygon { fill: var(--ink-soft) !important; }
html.jf-soft #figure .tline .tl-bar .knot { border-color: var(--ink-soft) !important; }

/* ===== 그려지는 애니메이션(덱에서 페이지를 열 때) ===== */
/* transform 대신 translate — 템플릿이 이름표 가운데 정렬에 쓰는 transform을 덮어쓰지 않는다 */
@keyframes jfUp { from { opacity: 0; translate: 0 16px; } to { opacity: 1; translate: 0 0; } }
@keyframes jfWipe { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
@keyframes jfDraw { to { stroke-dashoffset: 0; } }
@keyframes jfFade { from { opacity: 0; } to { opacity: 1; } }
html.jf-hit #figure, html.jf-hit #figure * { pointer-events: auto !important; }
html.jf-center #figure::before, html.jf-center #figure > .hd { transform: translate(var(--jf-hdx, 0px), var(--jf-hdy, 0px)); }
@page { size: __W__px __H__px; margin: 0; }
@media print {
  [data-jf-anim] { animation: none !important; opacity: 1 !important; clip-path: none !important; stroke-dashoffset: 0 !important; }
  html.jf-page, html.jf-page body { background: var(--bg, #fff) !important; }
  html.jf-page body { padding: 0; }
  #jf-page { box-shadow: none; transform: none !important; }
  #jf-fit { width: auto !important; height: auto !important; }
  #jf-fit > #jf-page { position: relative; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""

LOADER = r"""
<script id="jf-loader">
(function(){
  var C = __CFG__;
  var olds = Array.prototype.slice.call(document.querySelectorAll('script[type="text/jf-deferred"]'));
  var texts = olds.map(function(s){ return s.textContent; });
  olds.forEach(function(s){ s.remove(); });
  var fig = document.getElementById('figure');
  var snap = fig ? fig.innerHTML : '', style0 = fig ? (fig.getAttribute('style') || '') : '';
  function exec(){ texts.forEach(function(t){ var s = document.createElement('script'); s.text = t; document.body.appendChild(s); }); try { hugNotes(); } catch (e) {} }
  // 그림판(stage) 왼쪽 끝에 붙던 단위·출처·범례·설명을 실제 그림의 왼쪽(오른쪽 맞춤이면 오른쪽) 끝에 맞춘다
  // — 그림이 그림판 가운데에 좁게 그려지면(기울기 등) 메모만 왼쪽에 떨어져 본문 둘레가 넓어지고 그림이 가운데에 오지 않는다
  function hugNotes(){
    if (!C.page || !fig || isBoard()) return;
    var st = fig.querySelector('.vz-stage, .fm-stage'); if (!st) return;
    var sr = st.getBoundingClientRect(), u = sr.width / st.offsetWidth || 1, b = paintBox(st);
    if (!b) return;
    var offL = (b.L - sr.left) / u, offR = (sr.right - b.R) / u, w = (b.R - b.L) / u;
    if (offL < 24 && offR < 24) return;
    Array.prototype.slice.call(fig.children).forEach(function(e){
      if (!/\b(unit|src|caption|lg|concl)\b/.test(e.className || '')) return;
      var al = getComputedStyle(e).textAlign;
      e.style.maxWidth = w.toFixed(1) + 'px'; e.style.boxSizing = 'border-box';
      if (al === 'right' || al === 'end') { e.style.marginLeft = 'auto'; e.style.marginRight = offR.toFixed(1) + 'px'; }
      else if (al === 'center') { e.style.marginLeft = offL.toFixed(1) + 'px'; }
      else e.style.marginLeft = offL.toFixed(1) + 'px';
    });
  }
  // 페이지 배율(s)을 그리기 전에 정한다 — 제목 크기 보정(42px ÷ s)을 그린 뒤에 바꾸면 템플릿이 이미 그은 선·표 줄과 어긋나므로,
  // 배율이 바뀌면 처음부터 다시 그린다
  function isBoard(){ return typeof FIGURE !== 'undefined' && FIGURE && FIGURE.template === 'board'; }
  // 본문 상자 — 제목(.hd)을 뺀 나머지에서 실제로 칠해진 것(글자·색 칠한 상자·테두리·그림 도형)만 모아 그 둘레를 잰다(그림 좌표 단위)
  function contentBox(){
    var fr = fig.getBoundingClientRect(), u = fr.width / fig.offsetWidth || 1, b = paintBox(fig, fig.querySelector('.hd'));
    if (!b) return null;
    return {l: (b.L - fr.left) / u, t: (b.T - fr.top) / u, w: (b.R - b.L) / u, h: (b.B - b.T) / u};
  }
  function paintBox(scope, hd){
    var L = 1e9, T = 1e9, R = -1e9, B = -1e9;
    function add(r){ if (!r || (r.width < 0.5 && r.height < 0.5)) return;   /* 가로·세로 직선은 한쪽 두께가 0이어도 센다 */ L = Math.min(L, r.left); T = Math.min(T, r.top); R = Math.max(R, r.right); B = Math.max(B, r.bottom); }
    var all = scope.querySelectorAll('*'), rg = document.createRange();
    for (var i = 0; i < all.length; i++) {
      var e = all[i];
      if (hd && (e === hd || hd.contains(e))) continue;
      if (e.closest('defs, marker, clipPath, mask, pattern, linearGradient, radialGradient')) continue;
      var cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue;
      if (e instanceof SVGElement) {
        if (/^(path|rect|circle|ellipse|line|polyline|polygon|text|image|use)$/i.test(e.tagName) && !(cs.fill === 'none' && cs.stroke === 'none')) add(e.getBoundingClientRect());
        continue;
      }
      for (var c = e.firstChild; c; c = c.nextSibling) if (c.nodeType === 3 && c.nodeValue.trim()) { rg.selectNodeContents(c); add(rg.getBoundingClientRect()); }
      var bg = rgba(cs.backgroundColor);
      if ((bg && bg[3] > 0.02) || cs.backgroundImage !== 'none' || parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderBottomWidth) + parseFloat(cs.borderRightWidth) > 0 || /^(IMG|CANVAS|VIDEO)$/.test(e.tagName)) add(e.getBoundingClientRect());
    }
    if (L > R) return null;
    return {L: L, T: T, R: R, B: B};
  }
  // 제목 묶음(h1 윗변 ~ .hd 아랫변)의 높이(그림 좌표 단위)
  function headFig(){
    var hd = fig.querySelector('.hd'), h1 = fig.querySelector('.hd h1'); if (!hd || !h1) return 0;
    var u = fig.getBoundingClientRect().width / fig.offsetWidth || 1;
    return (hd.getBoundingClientRect().bottom - h1.getBoundingClientRect().top) / u;
  }
  var GAP = 44;   // 제목 묶음과 본문 사이(페이지 px)
  function layoutOf(){
    var TX = C.TX || 104, TY = C.TY || 114, cb = contentBox(), hf = headFig();
    if (!cb) return null;
    var availW = C.W - 2 * TX, availH = C.H - C.PAD - (C.footRoom || 0) - TY - GAP;
    var s = Math.min(availW / cb.w, availH / (cb.h + hf), 1.3);
    return {s: s, cb: cb, hf: hf, TX: TX, TY: TY, availW: availW};
  }
  function scaleOf(){
    if (!isBoard()) { var lo = layoutOf(); if (lo) return lo.s; }
    var inner = C.W - 2 * C.PAD; return Math.min(inner / fig.offsetWidth, (C.H - 2 * C.PAD) / fig.offsetHeight, 1.3);
  }
  function setS(v){ document.documentElement.style.setProperty('--jf-s', v.toFixed(4)); }
  function settleScale(){
    for (var k = 0; k < 3; k++) {
      var s = scaleOf(), cur = parseFloat(document.documentElement.style.getPropertyValue('--jf-s')) || 1;
      if (Math.abs(s - cur) < 0.004) return;
      setS(s);
      var keep = window.__JF_OVERRIDE__;
      fig.innerHTML = snap; fig.setAttribute('style', style0); window.__JF_OVERRIDE__ = keep; exec();
    }
  }
  function fitBoard(){
      // 페이지 높이의 88~100%를 채우도록 본문 배치 기준(print_cm)을 조정 — 넘치면 줄이고, 비면 키운다(폭은 그대로)
      var avail = C.H - 2 * C.PAD - (C.footRoom || 0), pc = FIGURE.print_cm || 16, n = 0, best = null;
      function fits(h){ return h <= avail; }
      while (n < 8) {
        var h = fig.offsetHeight;
        if (fits(h) && (!best || h > best.h)) best = {pc: pc, h: h};
        if (fits(h) && h >= avail * 0.88) break;
        var target = avail * 0.95, next = pc * Math.pow(h / target, 0.9);
        next = Math.max(C.minPc || 13, Math.min(C.maxPc || 60, next));
        if (Math.abs(next - pc) < 0.05) break;
        pc = next; window.__JF_OVERRIDE__ = {print_cm: +pc.toFixed(2)};
        fig.innerHTML = snap; fig.setAttribute('style', style0); exec(); n++;
      }
      if (!fits(fig.offsetHeight) && best && best.pc !== pc) {
        pc = best.pc; window.__JF_OVERRIDE__ = {print_cm: +pc.toFixed(2)};
        fig.innerHTML = snap; fig.setAttribute('style', style0); exec();
      }
      // 글자를 최대로 키워도 82%에 못 미치면 남는 높이를 본문 행 사이 간격으로 고르게 나눈다
      var nb = (FIGURE.body || []).length, h2 = fig.offsetHeight;
      if (fits(h2) && h2 < avail * 0.88 && nb > 1) {
        var g0 = FIGURE.gap || 18, g = Math.min(120, g0 + (avail * 0.94 - h2) / (nb - 1));
        window.__JF_OVERRIDE__ = {print_cm: +pc.toFixed(2), gap: Math.round(g)};
        fig.innerHTML = snap; fig.setAttribute('style', style0); exec();
        if (!fits(fig.offsetHeight)) { window.__JF_OVERRIDE__ = {print_cm: +pc.toFixed(2)}; fig.innerHTML = snap; fig.setAttribute('style', style0); exec(); }
      }
  }
  function place(){
    var W = C.W, H = C.H, P = C.PAD, inner = W - 2 * P;
    var page = document.getElementById('jf-page'), fresh = !page;
    if (fresh) {
      page = document.createElement('div'); page.id = 'jf-page';
      page.style.width = W + 'px'; page.style.height = H + 'px';
      fig.parentNode.insertBefore(page, fig); page.appendChild(fig);
    }
    var fw = fig.offsetWidth, fh = fig.offsetHeight;
    var s = Math.min(inner / fw, (H - 2 * P) / fh, 1.3);
    var lo = isBoard() ? null : layoutOf(), h1 = fig.querySelector('.hd h1');
    fig.style.setProperty('--jf-hdx', '0px'); fig.style.setProperty('--jf-hdy', '0px');
    if (lo) {
      // 판형이 아닌 도식: 제목 아래 16:9 영역의 가운데에 본문을 놓는다(4:3처럼 왼쪽에 붙고 오른쪽이 비지 않게)
      document.documentElement.classList.add('jf-center');
      s = lo.s;
      var top0 = lo.TY + lo.hf * s + GAP, availH = H - P - (C.footRoom || 0) - top0;
      fig.style.transform = 'scale(' + s.toFixed(4) + ')';
      fig.style.left = (lo.TX + (lo.availW - lo.cb.w * s) / 2 - lo.cb.l * s).toFixed(1) + 'px';
      fig.style.top = (top0 + Math.max(0, (availH - lo.cb.h * s) / 2) - lo.cb.t * s).toFixed(1) + 'px';
      // 제목(과 그 위 짧은 표식)만 따로 옮겨 모든 페이지에서 같은 자리(TX, TY)에 — transform은 자리를 차지하지 않아 본문 선·표와 어긋나지 않는다
      if (h1) {
        var pr0 = page.getBoundingClientRect(), hr0 = h1.getBoundingClientRect(), k0 = pr0.width / W || 1;
        fig.style.setProperty('--jf-hdx', ((lo.TX - (hr0.left - pr0.left) / k0) / s).toFixed(2) + 'px');
        fig.style.setProperty('--jf-hdy', ((lo.TY - (hr0.top - pr0.top) / k0) / s).toFixed(2) + 'px');
      }
      h1 = null;
    } else {
    fig.style.transform = 'scale(' + s.toFixed(4) + ')';
    fig.style.left = P + 'px';   // 왼쪽 위 여백에 붙인다 — 페이지마다 제목 위치·왼쪽 여백이 같게
    fig.style.top = P + 'px';
    }
    // 템플릿마다 안쪽 여백이 달라도 제목 글자의 왼쪽 위가 모든 페이지에서 같은 자리(TX, TY)에 오도록 그림 전체를 옮긴다
    if (h1) {
      var pr = page.getBoundingClientRect(), hr = h1.getBoundingClientRect(), k = pr.width / W || 1;
      var TX = C.TX || 104, TY = C.TY || 114;
      var dx = TX - (hr.left - pr.left) / k, dy = TY - (hr.top - pr.top) / k;
      if (Math.abs(dx) < 80 && Math.abs(dy) < 80) { fig.style.left = (P + dx).toFixed(1) + 'px'; fig.style.top = (P + dy).toFixed(1) + 'px'; }
    }
    window.__JF_PAGE__ = {width: W, height: H, pad: P, scale: +s.toFixed(4), fig: [fw, fh], print_cm: (window.__JF_OVERRIDE__ || {}).print_cm || (typeof FIGURE !== 'undefined' && FIGURE && FIGURE.print_cm) || null};
    // 단독 HTML: 16:9를 유지한 채 화면 폭에 맞춰 페이지를 통째로 확대·축소(덱 안에서는 덱이 맡음)
    if (!C.embed && fresh) {
      var wrap = document.createElement('div'); wrap.id = 'jf-fit';
      page.parentNode.insertBefore(wrap, page); wrap.appendChild(page);
      var refit = function(){
        var k = Math.max(0.2, (document.documentElement.clientWidth - 2 * C.M) / W);
        wrap.style.width = Math.round(W * k) + 'px'; wrap.style.height = Math.round(H * k) + 'px';
        page.style.transform = 'scale(' + k + ')';
      };
      refit(); window.addEventListener('resize', refit);
    }
  }
  // 글자와 실제 바탕의 대비를 재서 모자라면 글자색을 진하게(밝은 바탕) 또는 밝게(짙은 바탕) — 알약·꼬리표·색 글씨 포함
  function rgba(c){ var m = String(c).match(/rgba?\(([^)]+)\)/); if (!m) return null; var p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function over(top, base){ var a = top[3]; return [top[0]*a + base[0]*(1-a), top[1]*a + base[1]*(1-a), top[2]*a + base[2]*(1-a), 1]; }
  function lumi(c){ var f = function(v){ v /= 255; return v <= 0.04045 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }; return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2]); }
  function ratio(a, b){ var x = lumi(a), y = lumi(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05); }
  function bgOf(el){
    var chain = [], e = el;
    while (e && e.nodeType === 1) { var b = rgba(getComputedStyle(e).backgroundColor); if (b && b[3] > 0) { chain.push(b); if (b[3] >= 1) break; } e = e.parentElement; }
    var base = [255,255,255,1];
    for (var i = chain.length - 1; i >= 0; i--) base = over(chain[i], base);
    return base;
  }
  // 글자 바로 밑에 실제로 칠해진 색 — 템플릿이 상자를 SVG 도형으로 그리고 글자를 그 위에 얹는 경우가 많아
  // 조상 요소의 배경만 보면 흰 바탕으로 잘못 읽는다(흰 글자를 회색으로 바꾸던 원인). 글자 가운데 점 아래를 차례로 훑는다
  function bgAt(el, isSvg){
    var r = el.getBoundingClientRect();
    var x = r.left + r.width / 2, y = r.top + r.height / 2;
    if (!r.width || x < 0 || y < 0 || x >= window.innerWidth || y >= window.innerHeight) return bgOf(isSvg ? (el.closest('svg') || el).parentElement || el : el);
    var stack = document.elementsFromPoint(x, y), chain = [];
    if (!stack.length) return bgOf(isSvg ? (el.closest('svg') || el).parentElement || el : el);
    for (var i = 0; i < stack.length; i++) {
      var e = stack[i];
      if (e !== el && el.contains(e)) continue;          // 글자 요소 안쪽 조각은 건너뛰고
      if (e === el && isSvg) continue;                    // SVG 글자의 fill은 글자색이므로 건너뛴다(HTML 글자 요소 자신의 배경은 센다)
      var cs = getComputedStyle(e), col = null, op = parseFloat(cs.opacity) || 1;
      if (e instanceof SVGElement) {
        if (!/^(rect|path|polygon|polyline|circle|ellipse)$/i.test(e.tagName)) continue;
        if (cs.fill === 'none') continue;
        col = rgba(cs.fill); if (!col) return null;
        col[3] *= (parseFloat(cs.fillOpacity) || (cs.fillOpacity === '0' ? 0 : 1)) * op;
      } else {
        col = rgba(cs.backgroundColor);
        if ((!col || col[3] === 0) && cs.backgroundImage && cs.backgroundImage !== 'none') return null;
        if (col) col[3] *= op;
      }
      if (col && col[3] > 0.01) { chain.push(col); if (col[3] >= 0.99) break; }
    }
    var base = [255,255,255,1];
    for (var j = chain.length - 1; j >= 0; j--) base = over(chain[j], base);
    return base;
  }
  function fixContrast(root){
    document.documentElement.classList.add('jf-hit');
    try { fixContrast0(root); } finally { document.documentElement.classList.remove('jf-hit'); }
  }
  function fixContrast0(root){
    var n = 0, all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i], own = false;
      for (var c = el.firstChild; c; c = c.nextSibling) if (c.nodeType === 3 && c.nodeValue.trim()) { own = true; break; }
      if (!own) continue;
      var cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
      var isSvg = el instanceof SVGElement;
      var fg = rgba(isSvg ? cs.fill : cs.color); if (!fg) continue;
      var bg = bgAt(el, isSvg);
      if (!bg) continue;   // 바탕을 알 수 없으면(그라데이션 등) 손대지 않는다
      fg = over(fg, bg);
      var fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
      var need = (fs >= 24 || (fs >= 18.5 && bold)) ? 3.0 : 4.5;
      if (ratio(fg, bg) >= need) continue;
      var dark = lumi(bg) > 0.18, t = 0, out = fg;
      // 반올림으로 기준선 바로 밑에 걸리지 않게 조금 여유(+0.15)
      while (ratio(out, bg) < need + 0.15 && t < 1) { t += 0.08; var k = dark ? 0 : 255; out = [fg[0] + (k-fg[0])*t, fg[1] + (k-fg[1])*t, fg[2] + (k-fg[2])*t, 1]; }
      var v = 'rgb(' + out.slice(0,3).map(Math.round).join(',') + ')';
      if (isSvg) el.style.setProperty('fill', v, 'important'); else el.style.setProperty('color', v, 'important');
      n++;
    }
    window.__JF_CONTRAST__ = n;
  }
  // 그려지는 애니메이션: 상자는 위에서 아래·왼쪽에서 오른쪽 순서로 떠오르고, 그림(SVG)은 왼쪽부터 펼쳐지며, 화살표는 선이 그어진다
  function clearAnim(root){ root.querySelectorAll('[data-jf-anim]').forEach(function(e){ e.style.animation = ''; e.style.strokeDasharray = ''; e.style.strokeDashoffset = ''; e.removeAttribute('data-jf-anim'); }); }
  window.__JF_ANIM__ = function(on){
    var fig = document.getElementById('figure'); if (!fig) return;
    clearAnim(fig); if (!on) return;
    void fig.offsetWidth;
    var sel = '.hd, .band, .group, .card, .steps, .chips, .tline, .diamond, .mtx, .pill, .kv, .lb, .row > .ico';
    var els = Array.prototype.slice.call(fig.querySelectorAll(sel)).filter(function(e){ return !e.closest('svg'); });
    var svgs = Array.prototype.slice.call(fig.querySelectorAll('svg')).filter(function(sv){ return sv.id !== 'links' && !sv.closest('.card .ic, .ico, .chip, .bl, .jn') && sv.getBoundingClientRect().width > 120; });
    var items = els.map(function(e){ var r = e.getBoundingClientRect(); return {e: e, t: Math.round(r.top / 60), l: r.left, k: 'up'}; })
      .concat(svgs.map(function(e){ var r = e.getBoundingClientRect(); return {e: e, t: Math.round(r.top / 60), l: r.left, k: 'wipe'}; }));
    items.sort(function(a, b){ return a.t - b.t || a.l - b.l; });
    var step = Math.min(90, 1500 / Math.max(1, items.length)), last = 0;
    items.forEach(function(it, i){
      var d = Math.round(i * step); last = d;
      it.e.setAttribute('data-jf-anim', '1');
      it.e.style.animation = it.k === 'up' ? ('jfUp .55s cubic-bezier(.2,.7,.2,1) ' + d + 'ms both') : ('jfWipe .9s cubic-bezier(.4,0,.2,1) ' + d + 'ms both');
    });
    fig.querySelectorAll('svg#links path.lk').forEach(function(p, i){
      var len = 0; try { len = p.getTotalLength(); } catch (e) {}
      if (!len) return;
      p.setAttribute('data-jf-anim', '1');
      p.style.strokeDasharray = len; p.style.strokeDashoffset = len;
      p.style.animation = 'jfDraw .7s ease-out ' + (last * 0.6 + 250 + i * 60) + 'ms forwards';
    });
    fig.querySelectorAll('.lklabel').forEach(function(l){ l.setAttribute('data-jf-anim', '1'); l.style.animation = 'jfFade .4s ease ' + (last * 0.6 + 600) + 'ms both'; });
  };
  // 같은 내용에서 색·글꼴만 바꾸기 — 페이지를 다시 불러오지 않고 CSS를 갈아 끼운 뒤 그 자리에서 다시 그린다
  function swapBlock(begin, end, text){
    var st = Array.prototype.slice.call(document.querySelectorAll('style')).filter(function(x){ return x.textContent.indexOf(begin) >= 0; })[0];
    if (!st) return;
    var t = st.textContent, a = t.indexOf(begin), b = t.indexOf(end);
    if (a >= 0 && b > a) st.textContent = t.slice(0, a + begin.length) + text + t.slice(b);
  }
  function render(){
    if (fig) { fig.innerHTML = snap; fig.setAttribute('style', style0); }
    if (C.page && typeof FIGURE !== 'undefined' && FIGURE) { var fw0 = FIGURE.template === 'board' ? (C.W - 2 * C.PAD) : (FIGURE.width || 1500); setS(Math.min((C.W - 2 * C.PAD) / fw0, 1.3)); }
    window.__JF_OVERRIDE__ = null;
    exec();
    if (C.page && fig && typeof FIGURE !== 'undefined' && FIGURE && FIGURE.template === 'board') fitBoard();
    if (C.page && fig) settleScale();
    if (C.page && fig) place();
    if (fig) fixContrast(fig);
  }
  window.__JF_RETHEME__ = function(o){
    if (o.css != null) swapBlock('/*JF-PRESET-BEGIN*/', '/*JF-PRESET-END*/', o.css);
    if (o.fontcss != null) swapBlock('/*JF-FONT-BEGIN*/', '/*JF-FONT-END*/', o.fontcss);
    var cl = document.documentElement.classList;
    ['jf-flat', 'jf-pop', 'jf-soft', 'jf-deep'].forEach(function(k){ cl.remove(k); });
    Array.prototype.slice.call(cl).forEach(function(k){ if (k.indexOf('jf-font-') === 0) cl.remove(k); });
    C.concept = o.concept || null; C.font = o.font || C.font; C.fontFamily = o.fam || C.fontFamily;
    if (C.concept) { cl.add('jf-flat'); cl.add('jf-' + C.concept); }
    if (C.font && C.font !== 'presentation') cl.add('jf-font-' + C.font);
    window.__JF_DONE__ = false;
    var go = function(){ render(); window.__JF_DONE__ = true; if (o.done) o.done(window); };
    var fl = ['400', '700', '800'].map(function(w){ return document.fonts.load(w + ' 24px "' + C.fontFamily + '"', '가나다ABC123'); });
    Promise.all(fl).then(go, go);
  };
  var done = false;
  function run(){
    if (done) return; done = true;
    if (C.page) { document.documentElement.classList.add('jf-page'); if (C.embed) document.documentElement.classList.add('jf-embed'); if (C.concept) { document.documentElement.classList.add('jf-flat'); document.documentElement.classList.add('jf-' + C.concept); } }
    if (C.page && typeof FIGURE !== 'undefined' && FIGURE) { var fw0 = FIGURE.template === 'board' ? (C.W - 2 * C.PAD) : (FIGURE.width || 1500); setS(Math.min((C.W - 2 * C.PAD) / fw0, 1.3)); }
    exec();
    if (C.page && fig && typeof FIGURE !== 'undefined' && FIGURE && FIGURE.template === 'board') fitBoard();
    if (C.page && fig) settleScale();
    if (C.page && fig) place();
    if (fig) fixContrast(fig);
    window.__JF_DONE__ = true;
    if (C.animate) window.__JF_ANIM__(true);
    try { if (window.parent && window.parent !== window && window.parent.__JF_FRAME_READY__) window.parent.__JF_FRAME_READY__(window); } catch (e) {}
  }
  if (C.font && C.font !== 'presentation') document.documentElement.classList.add('jf-font-' + C.font);
  var fam = C.fontFamily || 'Presentation';
  var loads = ['400', '500', '600', '700', '800'].map(function(w){ return document.fonts.load(w + ' 24px "' + fam + '"', '가나다ABC123'); });
  Promise.all(loads).then(run, run);
  setTimeout(run, 3000);
})();
</script>
"""

def apply(html, spec, embed=False, placeholders=False):
    """글꼴은 항상, 페이지 틀은 page 모드일 때. 인라인 스크립트는 글꼴을 내려받은 뒤 실행.
    placeholders=True면 글꼴 CSS·설정 자리를 표식으로 남긴다(덱 색상·글꼴 선택 상자가 채움)"""
    if "jf-loader" in html:
        return html
    m = mode(spec)
    page_css = ""
    if m:
        w, h = size(spec)
        page_css = PAGE_CSS.replace("__M__", str(MARGIN)).replace("__W__", str(w)).replace("__H__", str(h))
    fk = font_kind(spec)
    css = '<style id="jf-font">\n' + ("/*JF-FONT-BEGIN*//*__JF_FONTCSS__*//*JF-FONT-END*/" if placeholders else font_css(fk)) + page_css + '</style>\n'
    i = html.find("</head>")
    html = html[:i] + css + html[i:] if i >= 0 else css + html
    b = html.find("<body")
    head, body = html[:b], html[b:]
    body = re.sub(r"<script(?![^>]*\bsrc=)([^>]*)>", lambda mo: '<script type="text/jf-deferred"%s>' % mo.group(1), body)
    if m:
        w, h = size(spec)
        cfg = {"page": True, "W": w, "H": h, "PAD": pad(spec), "embed": bool(embed), "concept": concept(spec), "M": MARGIN,
               "font": fk, "fontFamily": FONTS[fk]["family"],
               "minPc": float(spec.get("page_min_cm", 16)), "maxPc": 60, "animate": bool(spec.get("animate", False)) and not embed}
    else:
        cfg = {"page": False, "font": fk, "fontFamily": FONTS[fk]["family"]}
    loader = LOADER.replace("__CFG__", "__JF_CFG__" if placeholders else json.dumps(cfg))
    i = body.rfind("</body>")
    body = body[:i] + loader + body[i:] if i >= 0 else body + loader
    return head + body

def base_cfg(spec, embed=True):
    """선택 상자용 — 프리셋·글꼴과 무관한 페이지 설정"""
    w, h = size(spec)
    return {"page": True, "W": w, "H": h, "PAD": pad(spec), "embed": bool(embed), "M": MARGIN,
            "minPc": float(spec.get("page_min_cm", 16)), "maxPc": 60, "animate": False}

def backdrop(tokens_css, preset=""):
    """덱 바깥 배경 — 프리셋 주색 12% + 따뜻한 회색 (CSS color-mix와 같은 값). 쨍한 컨셉은 짙은 배경"""
    c = concept({"preset": preset})
    if c == "pop":
        return "#17171D"
    if c == "deep":
        mo = re.search(r"--tone-main:\s*(#[0-9A-Fa-f]{6})", tokens_css)
        if mo:
            return mo.group(1)
    if c == "soft":
        mo = re.search(r"--tone-main-tint:\s*(#[0-9A-Fa-f]{6})", tokens_css)
        if mo:
            return mo.group(1)
    mo = re.search(r"--tone-main:\s*(#[0-9A-Fa-f]{6})", tokens_css)
    main = mo.group(1) if mo else "#555555"
    a = [int(main[i:i + 2], 16) for i in (1, 3, 5)]
    b = [0xD4, 0xD2, 0xCE]
    return "#%02X%02X%02X" % tuple(round(x * 0.12 + y * 0.88) for x, y in zip(a, b))

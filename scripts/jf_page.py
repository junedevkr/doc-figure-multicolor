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
    tpl = tpl.replace("const FIGURE=/*__FIGURE_DATA__*/ null",
                      "var FIGURE=/*__FIGURE_DATA__*/ null;if(window.__JF_OVERRIDE__&&FIGURE)Object.assign(FIGURE,window.__JF_OVERRIDE__)", 1)
    return re.sub(r"\bconst (ICONS|ICON_SET)\s*=", r"var \1=", tpl)

def prepare_spec(spec):
    """페이지 모드에서 board 폭을 페이지 안쪽 폭에 맞춘다(화살표를 그리기 전에 정해야 한다)"""
    if mode(spec) and spec.get("template") == "board":
        if not spec.get("width"):
            spec = dict(spec, width=PAGE_W - 2 * pad(spec))
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
html.jf-page #figure .hd .kicker { font-size: 24px !important; color: var(--ink-soft) !important; font-weight: 600; margin-bottom: 6px; }
html.jf-page #figure .hd h1 { font-size: 42px !important; line-height: 1.25 !important; letter-spacing: -0.5px; }
html.jf-page #figure .hd .sub { font-size: 24px !important; }
html.jf-page #figure .hd .tag { font-size: 20px !important; }
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

@page { size: __W__px __H__px; margin: 0; }
@media print {
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
  function exec(){ texts.forEach(function(t){ var s = document.createElement('script'); s.text = t; document.body.appendChild(s); }); }
  function place(){
    var W = C.W, H = C.H, P = C.PAD, inner = W - 2 * P;
    var page = document.createElement('div'); page.id = 'jf-page';
    page.style.width = W + 'px'; page.style.height = H + 'px';
    fig.parentNode.insertBefore(page, fig); page.appendChild(fig);
    var fw = fig.offsetWidth, fh = fig.offsetHeight;
    var s = Math.min(inner / fw, (H - 2 * P) / fh, 1.3);
    // 축소·확대 배율이 1이 아니면 제목 글자를 거꾸로 보정해 화면에서는 늘 42px·24px로 보이게
    for (var it = 0; it < 2 && Math.abs(s - 1) > 0.005; it++) {
      fig.querySelectorAll('.hd h1').forEach(function(e){ e.style.setProperty('font-size', (42 / s).toFixed(2) + 'px', 'important'); });
      fig.querySelectorAll('.hd .kicker, .hd .sub').forEach(function(e){ e.style.setProperty('font-size', (24 / s).toFixed(2) + 'px', 'important'); });
      fw = fig.offsetWidth; fh = fig.offsetHeight;
      s = Math.min(inner / fw, (H - 2 * P) / fh, 1.3);
    }
    fig.style.transform = 'scale(' + s.toFixed(4) + ')';
    fig.style.left = Math.round(P + (inner - fw * s) / 2) + 'px';
    fig.style.top = P + 'px';
    window.__JF_PAGE__ = {width: W, height: H, pad: P, scale: +s.toFixed(4), fig: [fw, fh], print_cm: (window.__JF_OVERRIDE__ || {}).print_cm || (typeof FIGURE !== 'undefined' && FIGURE && FIGURE.print_cm) || null};
    // 단독 HTML: 16:9를 유지한 채 화면 폭에 맞춰 페이지를 통째로 확대·축소(덱 안에서는 덱이 맡음)
    if (!C.embed) {
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
  function fixContrast(root){
    var n = 0, all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i], own = false;
      for (var c = el.firstChild; c; c = c.nextSibling) if (c.nodeType === 3 && c.nodeValue.trim()) { own = true; break; }
      if (!own) continue;
      var cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
      var isSvg = el instanceof SVGElement;
      var fg = rgba(isSvg ? cs.fill : cs.color); if (!fg) continue;
      var bg = bgOf(isSvg ? (el.closest('svg') || el).parentElement || el : el);
      fg = over(fg, bg);
      var fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
      var need = (fs >= 24 || (fs >= 18.5 && bold)) ? 3.0 : 4.5;
      if (ratio(fg, bg) >= need) continue;
      var dark = lumi(bg) > 0.18, t = 0, out = fg;
      while (ratio(out, bg) < need && t < 1) { t += 0.08; var k = dark ? 0 : 255; out = [fg[0] + (k-fg[0])*t, fg[1] + (k-fg[1])*t, fg[2] + (k-fg[2])*t, 1]; }
      var v = 'rgb(' + out.slice(0,3).map(Math.round).join(',') + ')';
      if (isSvg) el.style.setProperty('fill', v, 'important'); else el.style.setProperty('color', v, 'important');
      n++;
    }
    window.__JF_CONTRAST__ = n;
  }
  var done = false;
  function run(){
    if (done) return; done = true;
    if (C.page) { document.documentElement.classList.add('jf-page'); if (C.embed) document.documentElement.classList.add('jf-embed'); if (C.concept) { document.documentElement.classList.add('jf-flat'); document.documentElement.classList.add('jf-' + C.concept); } }
    exec();
    if (C.page && fig && typeof FIGURE !== 'undefined' && FIGURE && FIGURE.template === 'board') {
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
    if (C.page && fig) place();
    if (fig) fixContrast(fig);
    window.__JF_DONE__ = true;
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
    css = '<style id="jf-font">\n' + ("/*__JF_FONTCSS__*/" if placeholders else font_css(fk)) + page_css + '</style>\n'
    i = html.find("</head>")
    html = html[:i] + css + html[i:] if i >= 0 else css + html
    b = html.find("<body")
    head, body = html[:b], html[b:]
    body = re.sub(r"<script(?![^>]*\bsrc=)([^>]*)>", lambda mo: '<script type="text/jf-deferred"%s>' % mo.group(1), body)
    if m:
        w, h = size(spec)
        cfg = {"page": True, "W": w, "H": h, "PAD": pad(spec), "embed": bool(embed), "concept": concept(spec), "M": MARGIN,
               "font": fk, "fontFamily": FONTS[fk]["family"],
               "minPc": float(spec.get("page_min_cm", 16)), "maxPc": 60}
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
            "minPc": float(spec.get("page_min_cm", 16)), "maxPc": 60}

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

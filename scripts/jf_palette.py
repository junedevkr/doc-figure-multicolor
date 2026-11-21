#!/usr/bin/env python3
"""doc-figure-multicolor 색 체계 도구 (표준 라이브러리만)

  python3 scripts/jf_palette.py build               # references/jf-palettes.json → presets/jf-*.css
  python3 scripts/jf_palette.py check               # 대비(WCAG)·구별(ΔE) 검사
  python3 scripts/jf_palette.py pick  -f 초록.txt   # 내용으로 팔레트 판별 (또는 --text "...")
  python3 scripts/jf_palette.py pick  -f 초록.txt --mono warm   # 흑백톤으로
  python3 scripts/jf_palette.py theme jf-policy     # PT 테마 색 JSON
  python3 scripts/jf_palette.py preview -o 미리보기.html

프리셋은 presets/house.css를 틀로 삼아 토큰 '값'만 바꾼다. 토큰 이름 집합은 원본과 같다.
"""
import argparse, colorsys, glob, html, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = os.path.join(ROOT, "presets")
PAL = os.path.join(ROOT, "references", "jf-palettes.json")
BASE = os.path.join(PRESETS, "house.css")
ORIGINAL = ["house", "house-report", "gov-navy", "gov-navy-doc", "gov-navy-w1200", "accent-plan",
            "forest-green", "academic-serif", "modern-charcoal", "line-minimal", "teal-lab",
            "report-classic", "report-classic-doc", "exhibit", "mono-formal", "design-report"]

# ---------- 색 계산 ----------
def h2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def rgb2h(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v * 255))) for v in (r, g, b))

def hls(h):
    return colorsys.rgb_to_hls(*h2rgb(h))

def mk(hue, l, s):
    return rgb2h(*colorsys.hls_to_rgb(hue, max(0, min(1, l)), max(0, min(1, s))))

def tint(h, l, smul=1.0, smax=None):
    hu, _, s = hls(h); s = s * smul
    if smax is not None: s = min(s, smax)
    return mk(hu, l, s)

def lum(h):
    def c(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(v) for v in h2rgb(h)); return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + 0.05) / (lb + 0.05)

def lab(h):
    def c(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(v) for v in h2rgb(h))
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722)
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)

def de(a, b):
    return math.dist(lab(a), lab(b))

def darken_for_white(h, target=4.5):
    """흰 글자가 target 대비를 넘을 때까지 명도를 낮춘다"""
    hu, l, s = hls(h)
    while contrast(mk(hu, l, s), "#FFFFFF") < target and l > 0.05:
        l -= 0.01
    return mk(hu, l, s)

# ---------- 토큰 만들기 ----------
def color_tokens(c, shape, min_contrast=4.5, tint_sat=0.7):
    m = {k: darken_for_white(v, min_contrast) for k, v in c.items()}
    main, sub = m["main"], m["sub"]
    hu = hls(main)[0]
    gray = lambda l, s=0.07: mk(hu, l, s)
    t = {
        "navy-deep": main, "navy-mid": sub, "navy-marker": m["wait"],
        "bar-fill": tint(main, 0.95, 0.6), "bar-fill-2": tint(main, 0.90, 0.55), "bar-border": sub,
        "grid-line": gray(0.87, 0.12), "ink": gray(0.15, 0.22), "ink-soft": gray(0.40, 0.10),
        "bg": "#FFFFFF", "chip-track": tint(main, 0.90, 0.55),
        "heat-1": tint(main, 0.94, 0.5), "heat-2": tint(main, 0.72, 0.45), "heat-3": tint(main, 0.22, 1.0),
        "heat-1-ink": gray(0.15, 0.22), "heat-2-ink": gray(0.10, 0.25), "heat-3-ink": "#FFFFFF",
        "neutral-fill": gray(0.955, 0.08), "neutral-line": gray(0.79, 0.08), "neutral-ink": gray(0.34, 0.08),
        "accent": m["stop"], "accent-soft": tint(m["stop"], 0.95, 0.6),
        "track-1": main, "track-2": tint(main, 0.48, 0.35), "track-3": gray(0.70, 0.06),
        "neutral-head": gray(0.38, 0.08), "line-soft": tint(main, 0.85, 0.4),
        "fill-faint": tint(main, 0.975, 0.5), "line-track": gray(0.80, 0.07),
        "board-line": tint(main, 0.84, 0.3), "board-panel": tint(main, 0.97, 0.45),
        "board-chip": tint(main, 0.93, 0.4), "board-step-mid": tint(main, 0.83, 0.45),
        "title-tag-color": m["main"],
    }
    for k in ("main", "sub", "go", "wait", "stop", "mute"):
        t["tone-%s" % k] = m[k]
        t["tone-%s-tint" % k] = tint(m[k], 0.945, tint_sat)
        t["tone-%s-line" % k] = tint(m[k], 0.74, 0.45)
    return t

JF_FONT = '"Presentation", "PresentationVariable", "Pretendard", "Apple SD Gothic Neo", "NanumSquare", "NanumGothic", "Malgun Gothic", sans-serif'

def identity_tokens(shape):
    """doc-figure-multicolor 공통 생김새 — 원본 프리셋과 갈리는 지점"""
    rb, rbar = shape.get("radius_box", 8), shape.get("radius_bar", 6)
    return {
        "radius-box": "%dpx" % rb, "radius-bar": "%dpx" % rbar, "radius-badge": "30%",
        "board-radius": "%dpx" % rb, "badge-shape": "30%", "radius-pill": "%dpx" % max(4, rb),
        "title-align": "left", "title-deco": "none", "title-under": "0 solid transparent",
        "title-under-gap": "0px", "fig-display": "flex", "title-tag": "block",
        "ornament": "none", "word-break": "keep-all", "accent-line": "solid",
        "strong-ring": "inset 0 0 0 0 transparent",
        "font": JF_FONT, "font-title": JF_FONT, "board-font": JF_FONT,
    }

def mono_tokens(kind, spot=None):
    if kind == "ink":
        g = lambda v: "#%02X%02X%02X" % (v, v, v)
        bg, card, fill = "#FFFFFF", "#FFFFFF", None
    else:  # gray — 중립 회색 단계(그레이스케일)
        g = lambda v: "#%02X%02X%02X" % (v, v, v)
        bg, card = "#FFFFFF", "#FFFFFF"
    t = {
        "navy-deep": g(38), "navy-mid": g(84), "navy-marker": g(48),
        "bar-fill": g(236), "bar-fill-2": g(222), "bar-border": g(110), "grid-line": g(206),
        "ink": g(26), "ink-soft": g(88), "bg": bg, "chip-track": g(222),
        "heat-1": g(236), "heat-2": g(166), "heat-3": g(40),
        "heat-1-ink": g(26), "heat-2-ink": g(18), "heat-3-ink": "#FFFFFF",
        "neutral-fill": g(244), "neutral-line": g(196), "neutral-ink": g(74),
        "accent": g(0), "accent-soft": g(220), "track-1": g(40), "track-2": g(110), "track-3": g(170),
        "neutral-head": g(88), "line-soft": g(198), "fill-faint": g(247), "line-track": g(200),
        "board-line": g(200), "board-panel": g(246) if kind == "ink" else g(243),
        "board-chip": g(238), "board-step-mid": g(214), "card-fill": card,
        "title-tag-color": g(38),
    }
    steps = (("main", 26), ("sub", 26), ("go", 26), ("wait", 26), ("stop", 0), ("mute", 26)) if kind == "ink" else \
            (("main", 38), ("sub", 84), ("go", 62), ("wait", 96), ("stop", 0), ("mute", 112))
    for k, v in steps:   # 흑백: 검정 한 가지 + 흰 바탕 / 그레이스케일: 회색 단계
        t["tone-%s" % k] = g(v); t["tone-%s-tint" % k] = g(244 if kind == "ink" else 240); t["tone-%s-line" % k] = g(170 if kind == "ink" else 190)
    if kind == "ink":
        shape = {"radius_box": 0, "radius_bar": 0}
        t.update({"strong-fill": "#FFFFFF", "strong-ink": g(26), "strong-ink-soft": g(88),
                  "strong-ring": "inset 0 0 0 2px #1A1A1A"})
    else:
        shape = {"radius_box": 6, "radius_bar": 4}
    idt = identity_tokens(shape)
    if kind == "ink":
        idt.pop("strong-ring")
    t = {**idt, **t}
    if spot:
        s = darken_for_white(spot)
        t.update({"focus-fill": s, "focus-ink": "#FFFFFF", "focus-ink-soft": tint(s, 0.88, 0.5),
                  "focus-ring": "inset 0 0 0 0 transparent", "title-tag-color": s})
    return t

def write_preset(name, tokens, header):
    src = open(BASE, encoding="utf-8").read()
    body = src[src.index(":root"):]
    for k, v in tokens.items():
        pat = re.compile(r"(?<![\w-])(--%s\s*:\s*)([^;]+)(;)" % re.escape(k))
        if not pat.search(body):
            sys.exit("토큰 없음: --%s" % k)
        body = pat.sub(lambda mo: mo.group(1) + v + mo.group(3), body, count=1)
    head = "/* =========================================================================\n   doc-figure-multicolor 프리셋 — %s\n%s\n\n   * 프리셋 규율: 토큰 '값'만 바꾸고 '이름'은 더하거나 빼지 않는다.\n   * @image-style: %s\n   ========================================================================= */\n" % (
        name, "\n".join("   " + x for x in header["lines"]), header["image"])
    with open(os.path.join(PRESETS, name + ".css"), "w", encoding="utf-8") as f:
        f.write(head + body)

def load():
    return json.load(open(PAL, encoding="utf-8"))

SRC = os.path.join(ROOT, "references", "jf-source-palettes.json")

def chart_presets():
    """컬러차트 순서(P-01~P-28)대로 [(팔레트 번호, 프리셋 이름, 컨셉 이름)] — 손으로 다듬은 컨셉이 있으면 그것, 없으면 jf-pNN"""
    P = load(); src = json.load(open(SRC, encoding="utf-8"))
    tuned = {d.get("palette_id"): "jf-" + k for k, d in P.get("concepts", {}).items() if d.get("palette_id")}
    return [(q["id"], tuned.get(q["id"], "jf-p%s" % q["id"][2:]), q["name"]) for q in src["palettes"]]

def build_auto_palettes(P):
    """컬러차트 팔레트 중 손으로 다듬은 컨셉이 없는 것을 원본 색 그대로 프리셋으로 만든다.
    원본 색은 바꾸지 않고, 모자란 역할 색은 원본 색과 같은 색상(hue)에서 명도·채도만 조절한다.
    색 면 위 글자 대비는 페이지가 그린 뒤 자동으로 맞춘다."""
    src = json.load(open(SRC, encoding="utf-8")); made = []
    tuned = {d.get("palette_id") for d in P.get("concepts", {}).values()}
    for q in src["palettes"]:
        if q["id"] in tuned:
            continue
        cols = [c.upper() if c.startswith("#") else "#" + c.upper() for c in q["colors"]]
        blacks = [c for c in cols if lum(c) < 0.02]
        cand = [c for c in cols if 0.02 <= lum(c) <= 0.85] or cols
        main = max(cand, key=lambda c: (1 - lum(c)) * 0.6 + hls(c)[2] * 0.4)
        rest = [c for c in cand if c != main]
        hm, lm, sm = hls(main)
        sub = rest[0] if rest else mk(hm, min(0.8, lm + 0.25), sm * 0.8)
        hs, ls, ss = hls(sub)
        wait = rest[1] if len(rest) > 1 else mk(hs, min(0.85, ls + 0.18), ss)
        c = {"main": main, "sub": sub, "wait": wait,
             "go": darken_for_white(mk(hs, 0.40, min(ss, 0.55))), "stop": darken_for_white(mk(hm, max(0.22, lm - 0.12), sm)), "mute": mk(hm, 0.76, 0.12)}
        ink = blacks[0] if blacks else "#1E1E22"
        tints = {k: tint(v, 0.94, 0.9) for k, v in c.items()}
        on = lambda bg: max(("#FFFFFF", ink, "#000000"), key=lambda fg: contrast(fg, bg))
        css = "deep" if lum(main) < 0.12 else "soft"
        tok = {**identity_tokens({"radius_box": 14, "radius_bar": 10}), **color_tokens(c, {}, 1.0, 1.0)}
        for k, v in tints.items():
            tok["tone-%s-tint" % k] = v; tok["tone-%s-line" % k] = v
        tok.update({"ink": ink, "ink-soft": "#55565E", "navy-deep": main, "navy-mid": sub, "navy-marker": wait,
                    "title-ink": ink, "title-tag-color": wait, "strong-fill": main, "strong-ink": on(main),
                    "focus-fill": main, "focus-ink": on(main), "heat-1": tints["sub"], "heat-2": sub, "heat-3": main,
                    "heat-1-ink": ink, "heat-2-ink": on(sub), "heat-3-ink": on(main), "accent": c["stop"],
                    "accent-soft": tints["stop"], "board-panel": tint(main, 0.975, 0.6), "board-chip": tints["sub"],
                    "board-line": tint(main, 0.88, 0.4), "board-link-w": "3px"})
        name = "jf-p%s" % q["id"][2:]
        write_preset(name, tok, {
            "lines": ["컬러차트 %s %s — 원본 색 %s 그대로, 모자란 역할 색은 같은 색상에서 명도·채도만 조절" % (q["id"], q["name"], " · ".join(cols)),
                      "@concept: %s" % css],
            "image": "a clean presentation diagram using exactly these palette colors: %s, borderless blocks, rounded corners" % ", ".join(cols)})
        made.append(name)
    return made

def build(_a):
    P = load(); made = []
    for fam, d in P["families"].items():
        c = d["colors"]
        tok = {**identity_tokens(d["shape"]), **color_tokens(c, d["shape"])}
        write_preset("jf-" + fam, tok, {
            "lines": ["내용 계열: %s (%s)" % (d["label"], fam),
                      "색은 뜻으로: main 핵심 개념, sub 하위 개념, go 결과·산출, wait 조건·주의, stop 문제·위험, mute 기존·선행연구",
                      "공통 생김새: 제목 왼쪽 + 짧은 색 표식, 둥근 사각 번호(30%), 각진 칩"],
            "image": "a clean Korean academic presentation diagram, %s family: main %s, secondary %s, outputs %s, caution %s, risk %s, pale tinted cards, %dpx corners, short color tag above a left-aligned title, no shadows, Freesentation-like Korean presentation sans-serif" % (
                fam, c["main"], c["sub"], c["go"], c["wait"], c["stop"], d["shape"]["radius_box"])})
        made.append("jf-" + fam)
    for name, d in P.get("concepts", {}).items():
        c = d["colors"]; mc = 1.0 if d.get("exact") else d.get("min_contrast", 4.5)
        tok = {**identity_tokens(d["shape"]), **color_tokens(c, d["shape"], mc, 1.0)}
        if not d.get("exact"):
            tok["board-line"] = tint(c["main"], 0.90, 0.5)
        for k, v in d.get("tints", {}).items():
            tok["tone-%s-tint" % k] = v
        for k in ("main", "sub", "go", "wait", "stop", "mute"):
            tok["tone-%s-line" % k] = tok["tone-%s-tint" % k]   # 테두리를 바탕과 같게 — 선 없는 색 면
        tok.update(d.get("tokens", {}))
        write_preset("jf-" + name, tok, {
            "lines": ["컬러 컨셉: %s" % d["label"], d["note"], "@concept: %s" % d.get("css", "pop")],
            "image": "a vivid modern presentation diagram: electric indigo %s, hot pink %s, emerald %s, orange %s, red %s, borderless colored blocks, %dpx rounded corners, bold black title with a short pink tag, white slide on a dark backdrop" % (
                c["main"], c["sub"], c["go"], c["wait"], c["stop"], d["shape"]["radius_box"])})
        made.append("jf-" + name)
    made += build_auto_palettes(P)
    write_preset("jf-mono-ink", mono_tokens("ink"), {
        "lines": ["흑백: 검정 한 가지와 흰 바탕만, 직각, 강조 상자는 외곽선. 흑백 인쇄·제출용"],
        "image": "a strict black-and-white academic diagram, pure grayscale, square corners, outlined emphasis boxes, left-aligned title with a short black tag, no shadows"})
    write_preset("jf-mono-gray", mono_tokens("gray"), {
        "lines": ["그레이스케일: 중립 회색 단계(진한 회색 머리띠·옅은 회색 바탕), 모서리 6px"],
        "image": "a neutral grayscale academic diagram, charcoal and mid-gray headers on light gray panels, 6px corners, left-aligned title with a short charcoal tag, no shadows"})
    made += ["jf-mono-ink", "jf-mono-gray"]
    print("만든 프리셋 %d벌: %s" % (len(made), ", ".join(made)))

# ---------- 검사 ----------
def tokens_of(name):
    s = open(os.path.join(PRESETS, name + ".css"), encoding="utf-8").read()
    s = s[s.index(":root"):]
    return dict(re.findall(r"(?<![\w-])--([\w-]+)\s*:\s*([^;]+);", s))

def min_contrast_of(name):
    """흰 글자가 얹히는 색 면의 최소 대비 — 쨍한 컨셉은 굵은 큰 글자 기준(3.0)"""
    for cname, d in load().get("concepts", {}).items():
        if name == "jf-" + cname:
            return d.get("min_contrast", 4.5)
    return 4.5

def preset_concept(name):
    path = os.path.join(PRESETS, name + ".css")
    if not os.path.exists(path):
        return None
    mo = re.search(r"@concept:\s*([a-z]+)", open(path, encoding="utf-8").read(3000))
    return mo.group(1) if mo else None

def on_tone_ink(name):
    """파스텔 컨셉(css soft)은 색 면 위 글자가 짙은 색"""
    for cname, d in load().get("concepts", {}).items():
        if name == "jf-" + cname:
            return d.get("css") == "soft"
    return False

def is_exact(name):
    if re.fullmatch(r"jf-p\d\d", name):
        return True
    for cname, d in load().get("concepts", {}).items():
        if name == "jf-" + cname:
            return bool(d.get("exact"))
    return False

def check(_a):
    base = set(tokens_of("house")); bad = 0
    jf = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(PRESETS, "jf-*.css")))
    for n in jf:
        t = tokens_of(n)
        if set(t) != base:
            print("✗ %s 토큰 집합 불일치: %s" % (n, set(t) ^ base)); bad += 1
        pairs = [("본문", "ink", "bg"), ("부제", "ink-soft", "bg"), ("히트맵3", "heat-3-ink", "heat-3")]
        pairs += [("tone-%s" % k, None, "tone-%s" % k) for k in ("main", "sub", "go", "wait", "stop", "mute")]
        for lab_, fg, bgk in pairs:
            fgv = "#FFFFFF" if fg is None else t[fg]
            bgv = t[bgk]
            if not bgv.startswith("#") or not fgv.startswith("#"):
                continue
            r = contrast(fgv, bgv)
            need = min_contrast_of(n) if fg is None else 4.5
            if fg is None and on_tone_ink(n):
                fgv = t["ink"]; need = 4.5; r = contrast(fgv, bgv)
            elif fg is None and is_exact(n):   # 원본 고정 색: 흰 글자·짙은 글자 중 나은 쪽(페이지가 자동으로 고름)
                r = max(contrast("#FFFFFF", bgv), contrast(t["ink"], bgv), contrast("#000000", bgv)); need = 4.5
            if r < need:
                print("✗ %s %s 대비 %.2f (<%.1f)" % (n, lab_, r, need)); bad += 1
    P = load(); mains = {"jf-" + f: d["colors"]["main"] for f, d in P["families"].items()}
    mains.update({"jf-" + f: (d["colors"]["main"] if d.get("exact") else darken_for_white(d["colors"]["main"], d.get("min_contrast", 4.5))) for f, d in P.get("concepts", {}).items()})
    orig = {}
    for o in ORIGINAL:
        p = os.path.join(PRESETS, o + ".css")
        if os.path.exists(p):
            t = tokens_of(o); orig[o] = t["navy-deep"]
    print("\n[구별] 내 주색 ↔ 원본 프리셋 주색 ΔE(CIE76, 20 이상 권장)")
    for n, c in mains.items():
        near = min(orig.items(), key=lambda kv: de(c, kv[1]))
        d = de(c, near[1]); flag = "✓" if d >= 20 else ("·" if is_exact(n) else "✗")
        if d < 20 and not is_exact(n): bad += 1   # 원본 색 고정 컨셉은 사용자가 고른 색이라 참고로만
        print("  %s %-12s %s  가장 가까운 원본 %-15s %s  ΔE %.1f" % (flag, n, c, near[0], near[1], d))
    print("\n[구별] 내 주색끼리 최소 ΔE")
    names = list(mains)
    worst = min(((a, b, de(mains[a], mains[b])) for i, a in enumerate(names) for b in names[i + 1:]), key=lambda x: x[2])
    print("  %s %s ↔ %s  ΔE %.1f" % ("✓" if worst[2] >= 20 else "✗", *worst))
    if worst[2] < 20: bad += 1
    print("\n%s 검사 %d벌, 문제 %d건" % ("✓" if not bad else "✗", len(jf), bad))
    return 1 if bad else 0

# ---------- 판별 ----------
def pick(a):
    text = a.text or ""
    if a.file:
        text += "\n" + open(a.file, encoding="utf-8", errors="ignore").read()
    if not text.strip():
        sys.exit("--text 또는 -f 로 제목·초록·키워드를 넣으세요")
    low = text.lower(); P = load(); score = {}
    for fam, d in P["families"].items():
        hits = {}
        for k in d["keywords"]:
            kl = k.lower()
            if re.fullmatch(r"[a-z &\-]+", kl):
                n = len(re.findall(r"\b%s\w*" % re.escape(kl), low))
            else:
                n = low.count(kl)
            if n: hits[k] = n
        score[fam] = (sum(hits.values()), hits)
    rank = sorted(score.items(), key=lambda kv: -kv[1][0])
    top, (s, hits) = rank[0]
    if s == 0:
        top = "method"
    preset = "jf-" + top
    if a.mono:
        preset = {"ink": "jf-mono-ink", "gray": "jf-mono-gray"}[a.mono]
    out = {"preset": preset, "family": top, "label": P["families"][top]["label"],
           "reason": sorted(hits, key=lambda k: -hits[k])[:8] if s else ["키워드 없음 → 기본(방법론·분석)"],
           "ranking": [{"family": f, "score": v[0]} for f, v in rank],
           "runner_up": rank[1][0] if len(rank) > 1 and rank[1][1][0] else None}
    print(json.dumps(out, ensure_ascii=False, indent=1))

# ---------- PT 테마 ----------
def theme(a):
    t = tokens_of(a.preset)
    keys = {"title": "navy-deep", "accent": "focus-fill", "text": "ink", "text_soft": "ink-soft",
            "background": "bg", "panel": "board-panel", "line": "board-line", "tag": "title-tag-color"}
    out = {k: t.get(v) for k, v in keys.items()}
    if not str(out["accent"]).startswith("#"):
        out["accent"] = t["navy-deep"]
    out["tones"] = {k: {"strong": t["tone-%s" % k], "tint": t["tone-%s-tint" % k], "line": t["tone-%s-line" % k]}
                    for k in ("main", "sub", "go", "wait", "stop", "mute")}
    out["preset"] = a.preset
    print(json.dumps(out, ensure_ascii=False, indent=1))

# ---------- 미리보기 ----------
def preview(a):
    jf = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(PRESETS, "jf-*.css")))
    P = load(); fams = list(P["families"])
    order = ["jf-" + f for f in fams] + ["jf-mono-ink", "jf-mono-gray"]
    order = [n for n in order if n in jf]
    labels = {"jf-" + f: d["label"] for f, d in P["families"].items()}
    labels.update({"jf-mono-ink": "흑백", "jf-mono-gray": "그레이스케일"})
    tone_names = [("main", "핵심 개념"), ("sub", "하위 개념"), ("go", "결과·산출"), ("wait", "조건·주의"), ("stop", "문제·위험"), ("mute", "선행연구·배경")]
    cards = []
    for n in order:
        t = tokens_of(n); e = html.escape
        focus = t["focus-fill"] if t["focus-fill"].startswith("#") else t["navy-deep"]
        strong_bg = t["strong-fill"] if t["strong-fill"].startswith("#") else t["navy-deep"]
        strong_ink = t["strong-ink"] if t["strong-ink"].startswith("#") else "#FFFFFF"
        ring = "2px solid %s" % strong_ink if "2px" in t["strong-ring"] else "0"
        chips = "".join('<div class="tone" style="background:%s;border:1px solid %s"><b style="background:%s"></b><span style="color:%s">%s</span><code style="color:%s">%s</code></div>'
                        % (t["tone-%s-tint" % k], t["tone-%s-line" % k], t["tone-%s" % k], t["ink"], lbl, t["ink-soft"], t["tone-%s" % k]) for k, lbl in tone_names)
        cards.append('''<section class="card" style="background:%s;border-radius:%s">
<i class="tag" style="background:%s"></i><h2 style="color:%s">%s</h2><p class="nm" style="color:%s">%s</p>
<div class="flow"><div class="box" style="background:%s;color:%s;border-radius:%s;border:%s">개념</div><span style="color:%s">→</span>
<div class="box" style="background:%s;color:%s;border:1px solid %s;border-radius:%s">연구과정</div><span style="color:%s">→</span>
<div class="box" style="background:%s;color:#fff;border-radius:%s">결론</div></div>
<div class="tones">%s</div></section>''' % (
            t["bg"], t["radius-box"], t["title-tag-color"], t["navy-deep"], e(labels.get(n, n)), t["ink-soft"], n,
            strong_bg, strong_ink, t["radius-box"], ring, t["ink-soft"],
            t["tone-sub-tint"], t["ink"], t["tone-sub-line"], t["radius-box"], t["ink-soft"],
            focus, t["radius-box"], chips))
    doc = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>doc-figure-multicolor 팔레트</title><style>%s
:root{--page:#F3F2EF;--ink:#1C1B1A}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--page:#1E1E1E;--ink:#EDEDED}}
:root[data-theme="dark"]{--page:#1E1E1E;--ink:#EDEDED}
body{margin:0;padding:24px 16px;background:var(--page);color:var(--ink);font-family:Presentation,PresentationVariable,Pretendard,"Apple SD Gothic Neo",sans-serif}
h1{font-size:22px;margin:0 0 4px}.sub{margin:0 0 20px;opacity:.75;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.card{padding:18px 18px 14px;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.tag{display:block;width:34px;height:5px;margin-bottom:8px}.card h2{font-size:18px;margin:0}.nm{margin:2px 0 12px;font-size:12px;font-family:ui-monospace,monospace}
.flow{display:flex;align-items:center;gap:6px;margin-bottom:12px}.box{flex:1;text-align:center;padding:9px 4px;font-weight:700;font-size:13px}
.tones{display:grid;grid-template-columns:1fr 1fr;gap:6px}.tone{display:flex;align-items:center;gap:6px;padding:5px 6px;border-radius:4px;font-size:12px}
.tone b{width:14px;height:14px;border-radius:3px;flex:none}.tone span{flex:1}.tone code{font-size:10px}
</style></head><body><h1>doc-figure-multicolor 팔레트</h1><p class="sub">내용 계열 7가지 · 흑백 · 그레이스케일. 색 칩은 도식 안에서 맡는 뜻</p><div class="grid">%s</div></body></html>''' % (open(os.path.join(ROOT, "references", "jf-font.css"), encoding="utf-8").read(), "\n".join(cards))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print("미리보기: %s (%d벌)" % (a.out, len(order)))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("build").set_defaults(fn=build)
    sp.add_parser("check").set_defaults(fn=check)
    p = sp.add_parser("pick"); p.add_argument("-f", "--file"); p.add_argument("--text")
    p.add_argument("--mono", choices=["ink", "gray"]); p.set_defaults(fn=pick)
    p = sp.add_parser("theme"); p.add_argument("preset"); p.set_defaults(fn=theme)
    p = sp.add_parser("preview"); p.add_argument("-o", "--out", default=os.path.join(ROOT, "examples", "preview", "jf-palettes.html")); p.set_defaults(fn=preview)
    a = ap.parse_args(); sys.exit(a.fn(a) or 0)

if __name__ == "__main__":
    main()

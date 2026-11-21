#!/usr/bin/env python3
"""출처 팔레트 컬러차트 (표준 라이브러리만)

  python3 scripts/jf_color_chart.py -o 컬러차트.html

references/jf-source-palettes.json의 팔레트(공개된 프레젠테이션 팔레트 값 그대로)를
색 칩 + 16:9 미니 슬라이드 미리보기로 보여 준다. 카드를 눌러 고르면 아래 막대에 번호가 모인다.
"""
import argparse, colorsys, html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from jf_palette import contrast, lum, h2rgb

def norm(h):
    h = h.strip().upper()
    return h if h.startswith("#") else "#" + h

def roles(p):
    cols = [norm(c) for c in p["colors"]]
    light = max(cols, key=lum)
    bg = light if lum(light) > 0.78 else "#FFFFFF"
    dark = min(cols, key=lum)
    ink = dark if lum(dark) < 0.015 else "#1E1E22"   # 거의 검정일 때만 글자색으로, 짙은 남색 등은 강조색으로 남김
    acc = [c for c in cols if c not in (bg, ink) and lum(c) <= 0.78]
    if not acc:
        acc = [c for c in cols if c != bg] or cols
    if p.get("theme12"):   # 12색 테마가 있는 팔레트: 강조색(5번째)·보조(8번째)·강조 짙음(6번째)을 앞으로
        t = [norm(c) for c in p["theme12"]]
        extra = [t[4], t[7], t[0], t[5]]
        acc = list(dict.fromkeys(extra + acc))
    while len(acc) < 3:
        acc.append(acc[len(acc) % max(1, len(acc))])
    return bg, ink, acc

def on(c):
    return "#FFFFFF" if contrast(c, "#FFFFFF") >= 3.0 else "#1E1E22"

def tint(c, k=0.86):
    r, g, b = h2rgb(c)
    return "#%02X%02X%02X" % tuple(round((x + (1 - x) * k) * 255) for x in (r, g, b))

def card(p):
    bg, ink, acc = roles(p)
    a0, a1, a2 = acc[0], acc[1], acc[2]
    sw = "".join('<span class="sw" style="background:%s"><i style="color:%s">%s</i></span>' % (norm(c), on(norm(c)), norm(c)) for c in p["colors"])
    bars = "".join('<b style="height:%d%%;background:%s"></b>' % (h, c) for h, c in ((48, a1), (72, a0), (60, a2), (88, a0)))
    return '''<article class="pal" data-id="%(id)s" tabindex="0" role="button" aria-pressed="false">
  <div class="mini" style="background:%(bg)s;color:%(ink)s">
    <i class="tag" style="background:%(a0)s"></i>
    <div class="mt">4 분석 결과 &gt; 4-1 집단별 변화</div>
    <div class="mrow">
      <div class="mc"><div class="mh" style="background:%(a0)s;color:%(o0)s">4-1 축산농민</div><div class="mb" style="background:%(t0)s">경제적 불확실성</div></div>
      <div class="mc"><div class="mh" style="background:%(a1)s;color:%(o1)s">4-2 전문가</div><div class="mb" style="background:%(t1)s">과학적 불확실성</div></div>
      <div class="mc"><div class="mh" style="background:%(a2)s;color:%(o2)s">4-3 공무원</div><div class="mb" style="background:%(t2)s">정책적 불확실성</div></div>
      <div class="bars">%(bars)s</div>
    </div>
    <div class="mband" style="background:%(a0)s;color:%(o0)s">5 불확실성의 거버넌스</div>
  </div>
  <div class="meta">
    <div class="id">%(id)s <span class="chk">선택됨</span></div>
    <div class="nm">%(name)s</div>
    <div class="sws">%(sw)s</div>
  </div>
</article>''' % dict(id=p["id"], bg=bg, ink=ink, a0=a0, a1=a1, a2=a2, o0=on(a0), o1=on(a1), o2=on(a2),
                     t0=tint(a0), t1=tint(a1), t2=tint(a2), bars=bars, name=html.escape(p["name"]), sw=sw)

PAGE = r"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<title>doc-figure-multicolor 컬러차트</title>
<style>
__FONT__
* { box-sizing: border-box; }
html { background: #EFEEEA; scrollbar-gutter: stable; }
body { margin: 0; color: #1E1E22; font-family: "Presentation", "Pretendard", "Apple SD Gothic Neo", sans-serif; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1600px; margin: 0 auto; padding: 48px 40px 140px; }
h1 { font-size: 40px; margin: 0 0 8px; font-weight: 800; }
.lead { font-size: 19px; color: #55565E; margin: 0 0 22px; line-height: 1.5; }
.lead a { color: inherit; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 22px; }
.pal { background: #fff; border-radius: 16px; overflow: hidden; cursor: pointer; outline: 3px solid transparent; transition: outline-color .15s, transform .15s; }
.pal:hover { transform: translateY(-2px); }
.pal:focus-visible { outline-color: #8A8A92; }
.pal.sel { outline-color: #1E1E22; }
.mini { aspect-ratio: 16 / 9; padding: 16px 16px 12px; display: flex; flex-direction: column; gap: 8px; position: relative; border-bottom: 1px solid #EEE; }
.mini .tag { display: block; width: 26px; height: 4px; border-radius: 2px; }
.mini .mt { font-size: 15px; font-weight: 800; }
.mrow { display: flex; gap: 6px; flex: 1; }
.mc { flex: 1; display: flex; flex-direction: column; border-radius: 7px; overflow: hidden; }
.mh { font-size: 10px; font-weight: 800; padding: 5px 4px; text-align: center; }
.mb { flex: 1; font-size: 10px; font-weight: 700; padding: 6px 4px; text-align: center; color: #1E1E22; }
.bars { width: 46px; display: flex; align-items: flex-end; gap: 3px; padding-bottom: 2px; }
.bars b { flex: 1; border-radius: 2px 2px 0 0; }
.mband { font-size: 11px; font-weight: 800; text-align: center; padding: 6px; border-radius: 7px; }
.meta { padding: 12px 14px 14px; }
.id { font-size: 15px; font-weight: 800; letter-spacing: .5px; display: flex; justify-content: space-between; align-items: center; }
.chk { display: none; font-size: 13px; background: #1E1E22; color: #fff; border-radius: 999px; padding: 2px 10px; }
.pal.sel .chk { display: inline-block; }
.nm { font-size: 17px; font-weight: 700; margin-top: 2px; }
.sws { display: flex; margin-top: 10px; border-radius: 8px; overflow: hidden; }
.sw { flex: 1; height: 46px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 5px; }
.sw i { font-style: normal; font-size: 11px; font-weight: 600; font-family: ui-monospace, Menlo, monospace; }
.bar { position: fixed; left: 0; right: 0; bottom: 0; background: #1E1E22; color: #fff; }
.bar .in { max-width: 1600px; margin: 0 auto; padding: 18px 40px; display: flex; align-items: center; gap: 18px; font-size: 19px; }
.bar .ids { flex: 1; font-weight: 700; letter-spacing: .5px; min-height: 1em; }
.bar .ids:empty::before { content: "카드를 눌러 마음에 드는 팔레트를 고르세요 (여러 개 가능)"; font-weight: 500; opacity: .6; }
.bar button { font: inherit; font-size: 17px; font-weight: 700; border: 0; border-radius: 999px; padding: 10px 20px; cursor: pointer; }
.bar .copy { background: #fff; color: #1E1E22; }
.bar .clear { background: transparent; color: #fff; outline: 1px solid rgba(255,255,255,.4); }
</style></head>
<body>
<div class="wrap">
  <h1>doc-figure-multicolor 컬러차트</h1>
  <p class="lead">공개된 프레젠테이션 팔레트 __N__개를 색상 코드 그대로 같은 미니 슬라이드에 입혀 비교합니다. 미리보기의 색 배치(제목·머리띠·띠)는 비교용 규칙이고, 고른 팔레트로 프리셋을 만들 때 다시 맞춥니다.</p>
  <div class="grid" id="grid">__CARDS__</div>
</div>
<div class="bar"><div class="in">
  <span>고른 팔레트</span><div class="ids" id="ids"></div>
  <button class="copy" id="copy" type="button">번호 복사</button><button class="clear" id="clear" type="button">모두 해제</button>
</div></div>
<script>
(function(){
  var cards = Array.prototype.slice.call(document.querySelectorAll('.pal')), sel = [];
  try { sel = JSON.parse(localStorage.getItem('jf-chart-sel') || '[]'); } catch (e) {}
  function sync(){
    cards.forEach(function(c){ var on = sel.indexOf(c.dataset.id) >= 0; c.classList.toggle('sel', on); c.setAttribute('aria-pressed', on); });
    document.getElementById('ids').textContent = sel.join(', ');
    try { localStorage.setItem('jf-chart-sel', JSON.stringify(sel)); } catch (e) {}
  }
  function toggle(c){ var i = sel.indexOf(c.dataset.id); if (i >= 0) sel.splice(i, 1); else sel.push(c.dataset.id); sync(); }
  cards.forEach(function(c){
    c.addEventListener('click', function(e){ if (e.target.closest('a')) return; toggle(c); });
    c.addEventListener('keydown', function(e){ if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(c); } });
  });
  document.getElementById('clear').onclick = function(){ sel = []; sync(); };
  document.getElementById('copy').onclick = function(){
    var t = sel.join(', '); if (!t) return;
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function(){ document.getElementById('copy').textContent = '복사됨'; setTimeout(function(){ document.getElementById('copy').textContent = '번호 복사'; }, 1400); }, function(){});
  };
  sync();
})();
</script>
</body></html>
"""

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    d = json.load(open(os.path.join(ROOT, "references", "jf-source-palettes.json"), encoding="utf-8"))
    cards = "\n".join(card(p) for p in d["palettes"])
    out = PAGE
    for k, v in (("__FONT__", open(os.path.join(ROOT, "references", "jf-font.css"), encoding="utf-8").read()), ("__CARDS__", cards),
                 ("__N__", str(len(d["palettes"])))):
        out = out.replace(k, v)
    open(a.out, "w", encoding="utf-8").write(out)
    print("✓ %s  팔레트 %d개" % (a.out, len(d["palettes"])))

if __name__ == "__main__":
    main()

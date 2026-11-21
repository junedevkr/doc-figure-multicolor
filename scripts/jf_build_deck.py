#!/usr/bin/env python3
"""여러 장의 spec → 하나의 HTML 덱 (표준 라이브러리만)

  python3 scripts/jf_build_deck.py 그림_01.json 그림_02.json -o 페이지모음.html [--title "제목"] [--no-number]

- 모든 페이지가 같은 16:9 무대(1920×1080)에 놓인다. 무대·페이지의 폭과 여백은 페이지를 넘겨도 바뀌지 않는다
- 아래쪽 화살표 버튼과 페이지 번호(1 / N), 키보드 ← → · PageUp/PageDown · Home/End · Space, 주소 #2 로 바로 가기
- 전체화면 발표: 버튼이나 F 키. 화면 크기에 맞춰 16:9 무대를 통째로 확대·축소(배치는 그대로)하고 남는 곳은 검은 여백.
  전체화면에서는 화살표·체크박스·종료 버튼을 두지 않는다. 화면 클릭(왼쪽 1/4은 이전)·← →·Space로 넘기고 Esc로 나간다
- --footer "논문 제목": 페이지마다 하단 왼쪽에 작게 이탤릭으로 (spec의 "footer"가 있으면 그 페이지는 그것)
- 페이지 번호: 'PT 하단에 페이지 번호' 선택(N 키)으로 슬라이드 오른쪽 아래 번호를 보이거나 숨긴다. PDF에도 그대로 적용
- PDF(인쇄): 화살표·버튼·배경은 숨기고 페이지마다 1920×1080 한 장
- 16:9 비율을 유지한 채 화면 폭에 맞춰 무대를 통째로 확대·축소한다(안쪽 배치·줄바꿈은 그대로, 다시 배치하지 않음)
- 바깥 배경이 짙으면(쨍한 컨셉 등) 화살표·페이지 번호·버튼·글자를 밝은색으로
"""
import argparse, html as H, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import jf_page, jf_build_html as B

ICON = {
    "prev": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5 8 12l7 7"/></svg>',
    "next": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m9 5 7 7-7 7"/></svg>',
    "full": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
    "exit": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5"/></svg>',
    "pdf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V3h12v6M6 18H4a1 1 0 0 1-1-1v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6a1 1 0 0 1-1 1h-2"/><path d="M6 14h12v7H6z"/></svg>',
}

SHELL = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<style>
__FONT__
:root { --backdrop: __BACKDROP__; --ink: #1E1E22; --stage-w: __W__px; --stage-h: __H__px; }
* { box-sizing: border-box; }
html { background: var(--backdrop); scrollbar-gutter: stable; }
body { margin: 0; background: var(--backdrop); color: var(--ink);
  font-family: __FONT_STACK__; -webkit-font-smoothing: antialiased; }
/* 16:9를 유지한 채 화면 폭에 맞춰 무대를 통째로 확대·축소 (안쪽 배치는 그대로) */
.deck { padding: 32px 40px 24px; }
#show { position: relative; width: var(--stage-w); height: var(--stage-h); margin: 0 auto; }
.stage { position: absolute; left: 0; top: 0; width: var(--stage-w); height: var(--stage-h); background: #fff; overflow: hidden;
  transform-origin: 0 0; box-shadow: 0 10px 32px rgba(0,0,0,.18), 0 0 0 1px rgba(0,0,0,.06); }
.sheet { position: absolute; left: 0; top: 0; width: var(--stage-w); height: var(--stage-h); background: #fff;
  visibility: hidden; pointer-events: none; }
.sheet.on { visibility: visible; pointer-events: auto; }
.sheet iframe { display: block; width: var(--stage-w); height: var(--stage-h); border: 0; }
.sheet .pno { display: none; position: absolute; right: 64px; bottom: 22px; font-size: 20px; font-weight: 600;
  color: #6B6B70; font-variant-numeric: tabular-nums; letter-spacing: .5px; pointer-events: none; }
body.show-pno .sheet .pno { display: block; }
.sheet .foot { position: absolute; left: 64px; bottom: 22px; max-width: 1400px; font-size: 18px; font-style: italic; font-weight: 500;
  color: #6B6B70; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; pointer-events: none; }
.tap { position: absolute; inset: 0; display: none; cursor: pointer; }

.nav { width: var(--stage-w); height: 76px; margin: 20px auto 0; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; }
.nav .ttl { font-size: 20px; font-weight: 600; opacity: .72; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 24px; }
.ctl { display: flex; align-items: center; gap: 22px; }
.rbtn { width: 56px; height: 56px; border-radius: 50%; border: 0; background: #fff; color: var(--ink); cursor: pointer;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,.14); flex: none; }
.rbtn:hover { background: #F4F4F6; }
button:focus-visible, .opt input:focus-visible { outline: 3px solid #1E1E22; outline-offset: 3px; }
.rbtn:disabled { opacity: .35; cursor: default; box-shadow: none; }
.rbtn svg { width: 26px; height: 26px; }
.count { width: 132px; text-align: center; font-size: 26px; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: .5px; }
.count .tot { opacity: .55; font-weight: 600; }
.nav .right { justify-self: end; display: flex; align-items: center; gap: 18px; }
.opt { display: flex; align-items: center; gap: 10px; font-size: 18px; cursor: pointer; user-select: none; white-space: nowrap; }
.opt input { width: 20px; height: 20px; margin: 0; accent-color: #1E1E22; cursor: pointer; }
.pill { height: 44px; border-radius: 22px; padding: 0 18px; border: 0; background: #fff; color: var(--ink); cursor: pointer;
  font: inherit; font-size: 18px; font-weight: 600; display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.14); white-space: nowrap; }
.pill:hover { background: #F4F4F6; }
.pill svg { width: 20px; height: 20px; }

/* 전체화면 발표 — 16:9 무대를 통째로 확대·축소, 남는 곳은 검은 여백 */
#show:fullscreen, #show.present { width: 100vw; height: 100vh; background: #000; }
#show.present { position: fixed; left: 0; top: 0; z-index: 100; }
body.presenting { overflow: hidden; }
#show:fullscreen .stage, #show.present .stage { box-shadow: none; }
#show:fullscreen .tap, #show.present .tap { display: block; }
#show:fullscreen:not(.ui), #show.present:not(.ui) { cursor: none; }

/* 짙은 바깥 배경일 때 조작 막대를 밝게 */
body.dark { --ink: #F2F2F5; }
body.dark .nav .ttl { opacity: .8; }
body.dark .rbtn, body.dark .pill { background: rgba(255,255,255,.12); color: #F2F2F5; box-shadow: inset 0 0 0 1px rgba(255,255,255,.28); }
body.dark .rbtn:hover, body.dark .pill:hover { background: rgba(255,255,255,.22); }
body.dark .rbtn:disabled { opacity: .3; box-shadow: inset 0 0 0 1px rgba(255,255,255,.18); }
body.dark .count .tot { opacity: .65; }
body.dark .opt input { accent-color: #F2F2F5; }
body.dark button:focus-visible, body.dark .opt input:focus-visible { outline-color: #F2F2F5; }

@page { size: __W__px __H__px; margin: 0; }
@media print {
  html, body { background: #fff !important; width: auto; min-width: 0; }
  .deck { width: auto; margin: 0; padding: 0; }
  #show { width: auto !important; height: auto !important; margin: 0; }
  .stage { position: static; width: auto; height: auto; box-shadow: none; overflow: visible; background: none; transform: none !important; }
  .sheet { position: relative; visibility: visible; break-after: page; page-break-after: always; overflow: hidden; }
  .sheet:last-child { break-after: auto; page-break-after: auto; }
  .nav, .tap { display: none !important; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>
</head>
<body>
<div class="deck">
  <div id="show">
    <div class="stage" id="stage" aria-live="polite"></div>
    <div class="tap" id="tap" aria-hidden="true"></div>
  </div>
  <nav class="nav" aria-label="페이지 이동">
    <div class="ttl">__TITLE__</div>
    <div class="ctl">
      <button class="rbtn" data-act="prev" type="button" aria-label="이전 페이지">__I_PREV__</button>
      <div class="count"><span data-cur>1</span> <span class="tot">/ <span data-tot>1</span></span></div>
      <button class="rbtn" data-act="next" type="button" aria-label="다음 페이지">__I_NEXT__</button>
    </div>
    <div class="right">
      <label class="opt" title="슬라이드 오른쪽 아래에 페이지 번호 (N 키). PDF에도 그대로 적용"><input type="checkbox" data-pno> PT 하단에 페이지 번호</label>
      <button class="pill" data-act="full" type="button" aria-label="전체화면 발표 (F 키)">__I_FULL__전체화면</button>
      <button class="pill" data-act="print" type="button" aria-label="PDF로 저장">__I_PDF__PDF</button>
    </div>
  </nav>
</div>
<script>
(function(){
  var PAGES = __PAGES__, TITLES = __TITLES__, FOOTS = __FOOTS__, PNO_DEFAULT = __PNO__, FOOT = __FOOT__;
  var W = __W__, H = __H__;
  var show = document.getElementById('show'), stage = document.getElementById('stage'), sheets = [], cur = 0;
  function all(sel){ return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  PAGES.forEach(function(src, i){
    var sh = document.createElement('section'); sh.className = 'sheet';
    var f = document.createElement('iframe');
    f.title = (i + 1) + '쪽 · ' + TITLES[i]; f.setAttribute('scrolling', 'no'); f.srcdoc = src;
    var no = document.createElement('div'); no.className = 'pno'; no.textContent = (i + 1) + ' / ' + PAGES.length;
    sh.appendChild(f); sh.appendChild(no);
    var fo = FOOTS[i] || FOOT; if (fo) { var ft = document.createElement('div'); ft.className = 'foot'; ft.textContent = fo; sh.appendChild(ft); } stage.appendChild(sh); sheets.push(sh);
  });
  all('[data-tot]').forEach(function(e){ e.textContent = PAGES.length; });

  function go(n, push){
    n = Math.max(0, Math.min(PAGES.length - 1, n));
    sheets.forEach(function(s, i){ s.classList.toggle('on', i === n); });
    cur = n;
    all('[data-cur]').forEach(function(e){ e.textContent = n + 1; });
    all('[data-act="prev"]').forEach(function(b){ b.disabled = n === 0; });
    all('[data-act="next"]').forEach(function(b){ b.disabled = n === PAGES.length - 1; });
    if (push !== false) history.replaceState(null, '', '#' + (n + 1));
  }

  // 페이지 번호 표시 (화면·전체화면·PDF 공통)
  var pnoBoxes = all('[data-pno]');
  function setPno(on){
    document.body.classList.toggle('show-pno', on);
    pnoBoxes.forEach(function(b){ b.checked = on; });
    try { localStorage.setItem('jf-deck-pno', on ? '1' : '0'); } catch (e) {}
  }
  var saved = null; try { saved = localStorage.getItem('jf-deck-pno'); } catch (e) {}
  setPno(saved === null ? PNO_DEFAULT : saved === '1');
  pnoBoxes.forEach(function(b){ b.addEventListener('change', function(){ setPno(b.checked); }); });

  // 전체화면 — 무대를 화면에 맞춰 통째로 확대·축소
  var nav = document.querySelector('.nav');
  function presenting(){ return document.fullscreenElement === show || show.classList.contains('present'); }
  function fit(){
    if (presenting()) {
      var vw = window.innerWidth, vh = window.innerHeight, s = Math.min(vw / W, vh / H);
      stage.style.transform = 'scale(' + s + ')';
      stage.style.left = Math.round((vw - W * s) / 2) + 'px';
      stage.style.top = Math.round((vh - H * s) / 2) + 'px';
    } else {
      var avail = document.documentElement.clientWidth - 80, s2 = Math.max(0.2, avail / W);
      show.style.width = Math.round(W * s2) + 'px'; show.style.height = Math.round(H * s2) + 'px';
      stage.style.transform = 'scale(' + s2 + ')'; stage.style.left = '0px'; stage.style.top = '0px';
      nav.style.width = Math.round(W * s2) + 'px';
    }
  }
  // 브라우저 전체화면을 쓰고, 막힌 환경(앱 안 미리보기 등)에서는 창 전체를 채우는 발표 모드로
  function setPresent(on){ show.classList.toggle('present', on); document.body.classList.toggle('presenting', on); if (!on) { show.style.width = ''; show.style.height = ''; } fit(); poke(); }
  function toggleFull(){
    if (document.fullscreenElement) { document.exitFullscreen(); return; }
    if (show.classList.contains('present')) { setPresent(false); return; }
    var req = show.requestFullscreen || show.webkitRequestFullscreen;
    if (!req) { setPresent(true); return; }
    try {
      var p = req.call(show);
      if (p && p.catch) p.catch(function(){ setPresent(true); });
    } catch (e) { setPresent(true); return; }
    setTimeout(function(){ if (!document.fullscreenElement && !show.classList.contains('present')) setPresent(true); }, 700);
  }
  document.addEventListener('fullscreenchange', function(){ fit(); poke(); });
  window.addEventListener('resize', fit);
  var hideT = null;
  function poke(){ show.classList.add('ui'); clearTimeout(hideT); hideT = setTimeout(function(){ show.classList.remove('ui'); }, 2200); }
  show.addEventListener('mousemove', poke);
  document.getElementById('tap').addEventListener('click', function(e){
    if (e.clientX < window.innerWidth * 0.25) go(cur - 1); else go(cur + 1);
  });

  all('[data-act]').forEach(function(b){
    b.addEventListener('click', function(){
      var a = b.getAttribute('data-act');
      if (a === 'prev') go(cur - 1);
      else if (a === 'next') go(cur + 1);
      else if (a === 'full') toggleFull();
      else if (a === 'print') window.print();
    });
  });
  function key(e){
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target && e.target.tagName;
    var k = e.key;
    if (k === 'ArrowRight' || k === 'PageDown' || (k === ' ' && !e.shiftKey && t !== 'BUTTON' && t !== 'INPUT')) { go(cur + 1); e.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'PageUp' || (k === ' ' && e.shiftKey)) { go(cur - 1); e.preventDefault(); }
    else if (k === 'Home') { go(0); e.preventDefault(); }
    else if (k === 'End') { go(PAGES.length - 1); e.preventDefault(); }
    else if (k === 'f' || k === 'F') { toggleFull(); e.preventDefault(); }
    else if (k === 'Escape' && show.classList.contains('present')) { setPresent(false); e.preventDefault(); }
    else if (k === 'n' || k === 'N') { setPno(!document.body.classList.contains('show-pno')); e.preventDefault(); }
  }
  document.addEventListener('keydown', key);
  sheets.forEach(function(sh){
    var f = sh.querySelector('iframe');
    f.addEventListener('load', function(){
      try { var d = f.contentWindow.document; d.addEventListener('keydown', key); d.addEventListener('mousemove', poke); } catch (e) {}
    });
  });
  if (__DARK__) document.body.classList.add('dark');
  window.addEventListener('beforeprint', function(){ stage.style.transform = ''; });
  window.addEventListener('afterprint', fit);
  fit();
  var h = parseInt((location.hash || '').slice(1), 10);
  go(isNaN(h) ? 0 : h - 1, false);
})();
</script>
</body>
</html>
"""

def is_dark(hexcolor):
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.35

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--no-number", action="store_true", help="처음 열 때 페이지 번호를 숨긴 상태로")
    ap.add_argument("--footer", default="", help="페이지 하단 왼쪽에 작게 이탤릭으로 넣을 논문 제목")
    ap.add_argument("--preset", default="", help="모든 페이지의 프리셋을 이것으로 (예: jf-pop)")
    a = ap.parse_args()
    specs = [B.load_spec(p) for p in a.specs]
    if a.preset:
        specs = [dict(s, preset=a.preset) for s in specs]
    sizes = {jf_page.size(dict(s, page=jf_page.mode(s) or "16:9")) for s in specs}
    if len(sizes) != 1:
        sys.exit("페이지 비율이 서로 다름: %s — 한 덱은 한 비율로" % sizes)
    w, h = sizes.pop()
    pages, titles, foots = [], [], []
    for s in specs:
        s = dict(s, page=jf_page.mode(s) or "16:9")
        pages.append(B.build_string(s, embed=True))
        titles.append(s.get("title") or s.get("kicker") or "")
        foots.append(s.get("footer", ""))
    title = a.title or titles[0]
    out = SHELL
    for k, v in (("__FONT__", jf_page.font_css()), ("__BACKDROP__", jf_page.backdrop(B.preset_css(specs[0]), specs[0].get("preset", ""))),
                 ("__W__", str(w)), ("__H__", str(h)), ("__FONT_STACK__", jf_page.FONT_STACK),
                 ("__I_PREV__", ICON["prev"]), ("__I_NEXT__", ICON["next"]), ("__I_FULL__", ICON["full"]),
                 ("__I_EXIT__", ICON["exit"]), ("__I_PDF__", ICON["pdf"]),
                 ("__PNO__", "false" if a.no_number else "true"),
                 ("__DARK__", "true" if is_dark(jf_page.backdrop(B.preset_css(specs[0]), specs[0].get("preset", ""))) else "false"),
                 ("__FOOT__", json.dumps(a.footer, ensure_ascii=False).replace("</", "<\\/")),
                 ("__TITLES__", json.dumps(titles, ensure_ascii=False).replace("</", "<\\/")),
                 ("__FOOTS__", json.dumps(foots, ensure_ascii=False).replace("</", "<\\/")),
                 ("__TITLE__", H.escape(title))):
        out = out.replace(k, v)
    out = out.replace("__PAGES__", "[" + ",".join(json.dumps(p, ensure_ascii=False).replace("</", "<\\/") for p in pages) + "]")
    open(a.out, "w", encoding="utf-8").write(out)
    print("✓ %s  %d쪽  %dx%d" % (a.out, len(pages), w, h))

if __name__ == "__main__":
    main()

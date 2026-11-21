#!/usr/bin/env python3
"""여러 장의 spec → 하나의 HTML 덱 (표준 라이브러리만)

  python3 scripts/jf_build_deck.py 그림_01.json 그림_02.json -o 페이지모음.html [--title "제목"] [--no-number]

- 모든 페이지가 같은 16:9 무대(1920×1080)에 놓인다. 무대·페이지의 폭과 여백은 페이지를 넘겨도 바뀌지 않는다
- 아래쪽 화살표 버튼과 페이지 번호(1 / N), 키보드 ← → · PageUp/PageDown · Home/End · Space, 주소 #2 로 바로 가기
- 전체화면 발표: 버튼이나 F 키. 화면 크기에 맞춰 16:9 무대를 통째로 확대·축소(배치는 그대로)하고 남는 곳은 검은 여백.
  전체화면에서는 화살표·체크박스·종료 버튼을 두지 않는다. 화면 클릭(왼쪽 1/4은 이전)·← →·Space로 넘기고 Esc로 나간다
- --switcher: 아래쪽에 색상(컬러차트 28종·내용 계열·흑백)·글꼴(고딕·명조) 선택 상자. 내용은 그대로 두고 고르는 즉시 모든 페이지를 다시 그린다
- --font <글꼴 키>|gothic|myeongjo: 모든 페이지 글꼴(references/jf-fonts.json, 기본 고딕=프리젠테이션, 기본 명조=Noto Serif KR)
- --footer "논문 제목": 페이지마다 하단 왼쪽에 작게 이탤릭으로 (spec의 "page_footer"가 있으면 그 페이지는 그것, 문자열 "footer"도 같은 뜻)
- 애니메이션: 페이지를 열 때 상자가 차례로 떠오르고 그림이 펼쳐지며 화살표가 그어진다. '애니메이션' 체크(A 키)로 끔. PDF에는 영향 없음
- 페이지 번호: '페이지 번호' 체크(N 키)으로 슬라이드 오른쪽 아래 번호를 보이거나 숨긴다. PDF에도 그대로 적용
- 그라데이션: 체크(D 키)하면 상자·도형·그래프에 위가 밝은 그라데이션(원본 doc-figure v2.4의 --gloss 토큰 방식). 화면·PDF 공통, spec "gloss": true로 켠 채 시작
- 페이지 이동: 가운데 번호를 누르면 위로 열리는 드롭다운 목록(번호·제목). 전체 보기 아이콘이나 G 키 → 모든 페이지 미리보기 칸(지금 색·글꼴 그대로).
  숫자를 치고 Enter로도 바로 이동(전체화면에서도)
- 클릭 강조(C 키, 켤 때만): 슬라이드를 누르면 글자는 형광펜이 아래 55%를 칠하며 지나가고, 상자는 테두리가 조여 들며 강조, 그래프·도형 조각은 밝게 빛난다.
  다시 누르면 지우고 E 키로 이 페이지 강조·잉크를 모두 지움. 켜 두면 전체화면에서 화면 클릭 넘기기는 멈춘다(키로 넘김)
- 드래그 금지: 체크하면 슬라이드 글자를 끌어 선택하지 못함
- 조작 막대: 왼쪽 페이지 이동(이전·번호 목록·다음·전체 보기) · 가운데 발표 도구(펜·형광펜·레이저·클릭 강조·지우기) · 오른쪽 '보기' 메뉴(색상·글꼴·애니메이션·그라데이션·페이지 번호·드래그 금지)·발표자 노트·전체화면·PDF
- 단축키 표시: 버튼 오른쪽 위에 겹친 키캡 배지(G P H L C E S F, 보기 메뉴 안 A D N). 좌우 이동 버튼에는 표시하지 않음. 한글 입력 상태에서도 같은 자리 키로 동작(물리 키로 판별) 전체화면에서는 막대 없이 키로만, 도구를 바꾸면 잠깐 이름을 띄움
- PDF 버튼: 인쇄 대화상자 없이 지금 화면 그대로(고른 색·글꼴, 페이지 번호 표시 여부, 하단 글귀, 펜·형광펜 잉크) PDF 파일을
  바로 내려받는다. 페이지마다 1920×1080(1440×810pt) 한 장, 2배 해상도 그림. 라이브러리(html-to-image·jsPDF)는 누를 때 받아 오며,
  받을 수 없으면 인쇄로 대신한다. Ctrl/Cmd+P 인쇄도 그대로 쓸 수 있다(화살표·버튼·배경 숨김)
- 16:9 비율을 유지한 채 화면 폭에 맞춰 무대를 통째로 확대·축소한다(안쪽 배치·줄바꿈은 그대로, 다시 배치하지 않음)
- 발표 도구: 펜(P)·형광펜(H)·레이저 포인터(L), 이 페이지 잉크 지우기(E)·한 획 되돌리기(Z), 도구 끄기는 같은 키나 Esc.
  잉크는 페이지마다 따로 남고 전체화면에서도 그대로(키로만 바꿈). 도구를 켜면 화면 클릭으로 넘기기는 멈춘다. PDF에는 잉크를 넣지 않는다
- 발표자 노트: 버튼이나 S 키로 별도 창(팝업)을 연다 — 지금·다음 슬라이드 미리보기, spec의 "notes"(문자열 또는 줄 목록),
  경과 시간·시계, 이전·다음 버튼, 노트 글자 크기. 덱과 노트 창 어느 쪽에서 넘겨도 같이 움직인다. 팝업이 막히면 화면 오른쪽 아래 상자로
- 바깥 배경이 짙으면(짙은 주색 컨셉 등) 화살표·페이지 번호·버튼·글자를 밝은색으로
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
    "pen": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20l1.2-4.6L16.5 4.1a2 2 0 0 1 2.8 0l.6.6a2 2 0 0 1 0 2.8L8.6 18.8 4 20z"/><path d="M14.5 6.1l3.4 3.4"/></svg>',
    "hl": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M9 14l-3 3v3h3l3-3"/><path d="M9 14l7.5-7.5a2.1 2.1 0 0 1 3 3L12 17"/><path d="M4 21h16" stroke-width="3"/></svg>',
    "laser": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"><circle cx="12" cy="12" r="3.2" fill="currentColor"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/></svg>',
    "erase": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 20H20"/><path d="M5.6 16.6a2 2 0 0 1 0-2.8l8.5-8.5a2 2 0 0 1 2.8 0l2.8 2.8a2 2 0 0 1 0 2.8L12 18.6 8.5 20l-2.9-3.4z"/><path d="M9.5 10l5.5 5.5"/></svg>',
    "view": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"><path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/></svg>',
    "fx": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M9 9l11 4-5 2-2 5-4-11z"/><path d="M5 3.5l1 2.5M2.5 7l2.5 1M10 2.5l-.5 2.6"/></svg>',
    "grid": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linejoin="round"><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/></svg>',
    "notes": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3.5" width="16" height="17" rx="2"/><path d="M8 8.5h8M8 12h8M8 15.5h5"/></svg>',
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
.sheet .pno { display: none; position: absolute; right: __PNO_R__px; bottom: __PNO_B__px; font-size: __PNO_S__px; font-weight: 600;
  color: #6B6B70; font-variant-numeric: tabular-nums; letter-spacing: .5px; pointer-events: none; }
body.show-pno .sheet .pno { display: block; }
.sheet .foot { position: absolute; left: __FOOT_X__px; bottom: __FOOT_B__px; max-width: 1400px; font-size: __FOOT_S__px; font-style: italic; font-weight: 500;
  color: #6B6B70; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; pointer-events: none; }
.tap { position: absolute; inset: 0; display: none; cursor: pointer; }

.nav { width: var(--stage-w); min-height: 52px; margin: 16px auto 0; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px 18px; }
.nav .ttl { font-size: 15px; font-weight: 600; opacity: .72; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 24px; }
.ctl { display: flex; align-items: center; gap: 12px; }
.rbtn { width: 36px; height: 36px; border-radius: 50%; border: 0; background: #fff; color: var(--ink); cursor: pointer;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,.14); flex: none; }
.rbtn:hover { background: #F4F4F6; }
button:focus-visible, .opt input:focus-visible { outline: 3px solid #1E1E22; outline-offset: 3px; }
.rbtn:disabled { opacity: .35; cursor: default; box-shadow: none; }
.rbtn svg { width: 18px; height: 18px; }
.count { width: 76px; text-align: center; font-size: 17px; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: .5px; }
.count .tot { opacity: .55; font-weight: 600; }
.nav .right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; justify-content: flex-end; }
.sw { display: flex; align-items: center; gap: 6px; font-size: 13px; white-space: nowrap; }
.sw select { font: inherit; font-size: 13px; font-weight: 600; height: 30px; border-radius: 8px; border: 1px solid #D6D6DC; padding: 0 8px; background: #fff; color: #1E1E22; cursor: pointer; flex: 1; min-width: 0; }
/* 보기 메뉴 — 색상·글꼴·표시 선택을 한곳에 */
.menuwrap { position: relative; }
#setmenu { position: absolute; bottom: calc(100% + 10px); right: 0; width: min(330px, calc(100vw - 40px)); z-index: 30; display: none;
  background: #fff; color: #1E1E22; border-radius: 12px; padding: 10px 12px; box-shadow: 0 12px 36px rgba(0,0,0,.28); }
#setmenu.on { display: block; }
.mrow { display: flex; align-items: center; gap: 10px; padding: 6px 2px; font-size: 13px; }
.mrow .ml { flex: none; min-width: 34px; }
.mrow.opt .ml { flex: 1; }
.msep { height: 1px; background: #E4E4EA; margin: 6px 0; }
#setmenu .opt input { accent-color: #1E1E22; }
body.dark #setmenu { background: #26262C; color: #F2F2F5; box-shadow: 0 12px 36px rgba(0,0,0,.5), inset 0 0 0 1px rgba(255,255,255,.12); }
body.dark #setmenu .sw select { background: #33333A; color: #F2F2F5; border-color: rgba(255,255,255,.2); }
body.dark #setmenu .sw select option, body.dark #setmenu .sw select optgroup { color: #1E1E22; background: #fff; }
body.dark #setmenu .msep { background: rgba(255,255,255,.14); }
body.dark #setmenu .opt input { accent-color: #F2F2F5; }
.opt { display: flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; user-select: none; white-space: nowrap; }
.opt input { width: 15px; height: 15px; margin: 0; accent-color: #1E1E22; cursor: pointer; }
.pill { height: 30px; border-radius: 15px; padding: 0 12px; border: 0; background: #fff; color: var(--ink); cursor: pointer;
  font: inherit; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 8px rgba(0,0,0,.14); white-space: nowrap; }
.pill:hover { background: #F4F4F6; }
.pill svg { width: 15px; height: 15px; }

/* 발표 도구 — 펜·형광펜·레이저. 잉크는 무대 안 캔버스(1920×1080)에 그려 무대와 함께 확대·축소되고 페이지마다 따로 남는다 */
.ink { position: absolute; left: 0; top: 0; width: var(--stage-w); height: var(--stage-h); pointer-events: none; z-index: 5; }
#ink-hl { mix-blend-mode: multiply; }
#show.tool-on #ink-pen { pointer-events: auto; cursor: crosshair; }
#show.tool-laser #ink-pen { cursor: none; }
#show.tool-on .tap, #show.fx-on .tap { display: none !important; }
.laser { position: absolute; width: 22px; height: 22px; margin: -11px 0 0 -11px; border-radius: 50%; z-index: 6; pointer-events: none; display: none;
  background: radial-gradient(circle, #fff 0 18%, #FF2B2B 32%, rgba(255,43,43,.55) 55%, rgba(255,43,43,0) 72%); }
.tools { display: flex; align-items: center; gap: 4px; }
.tbtn { width: 30px; height: 30px; border-radius: 50%; border: 0; background: #fff; color: var(--ink); cursor: pointer; padding: 0;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,.14); flex: none; }
.tbtn svg { width: 16px; height: 16px; }
.tbtn:hover { background: #F4F4F6; }
.tbtn.on { background: #1E1E22; color: #fff; }
body.dark .tbtn { background: rgba(255,255,255,.12); color: #F2F2F5; box-shadow: inset 0 0 0 1px rgba(255,255,255,.28); }
body.dark .tbtn:hover { background: rgba(255,255,255,.22); }
body.dark .tbtn.on { background: #F2F2F5; color: #1E1E22; }
.pill.on { background: #1E1E22; color: #fff; }
body.dark .pill.on { background: #F2F2F5; color: #1E1E22; }
/* 단축키 작은 표시 — 보통 화면에서만(전체화면은 막대가 없음) */
.tbtn, .rbtn, .pill { position: relative; }
.k { display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; min-width: 17px; height: 17px; padding: 0 4px; flex: none; line-height: 1;
  border: 1px solid currentColor; border-bottom-width: 2px; border-radius: 4px; font: 700 10px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
  text-transform: uppercase; letter-spacing: 0; opacity: .6; white-space: nowrap; }
/* 단축키 배지: 버튼 오른쪽 위에 겹쳐 — 버튼 사이 간격 안에 들어가 옆 버튼과 겹치지 않음 */
.hk .k { position: absolute; top: -7px; right: -7px; min-width: 15px; height: 15px; padding: 0 3px; font-size: 9px; opacity: 1;
  background: var(--backdrop); color: var(--ink); border-color: currentColor; pointer-events: none; z-index: 1; }
.k.inl { margin-left: auto; opacity: .7; }
.tools { gap: 12px !important; }
.ctl { gap: 14px !important; }
.count { cursor: pointer; border: 0; background: none; color: inherit; font: inherit; font-size: 17px; font-weight: 700; padding: 0 4px; border-radius: 8px; }
.count:hover { background: rgba(127,127,127,.15); }
.count::after { content: "▾"; font-size: 11px; margin-left: 4px; opacity: .6; }
/* 페이지 이동 — 번호를 누르면 위로 열리는 목록 */
.pgwrap { position: relative; }
#pgmenu { position: absolute; bottom: calc(100% + 10px); left: -8px; width: min(360px, calc(100vw - 40px)); max-height: min(60vh, 440px); overflow: auto; z-index: 30;
  display: none; background: #fff; color: #1E1E22; border-radius: 12px; padding: 6px; box-shadow: 0 12px 36px rgba(0,0,0,.28); }
#pgmenu.on { display: block; }
#pgmenu button { display: flex; gap: 10px; align-items: baseline; width: 100%; text-align: left; border: 0; background: none; color: inherit; cursor: pointer;
  font: inherit; font-size: 14px; padding: 7px 10px; border-radius: 8px; }
#pgmenu button b { min-width: 26px; text-align: right; font-variant-numeric: tabular-nums; opacity: .6; }
#pgmenu button:hover { background: #F0F0F3; }
#pgmenu button.cur { background: #1E1E22; color: #fff; }
#pgmenu button.cur b { opacity: .8; }
/* 페이지 고르기 — 무대 위에 번호·제목 칸, 전체화면에서도 G 키 */
#picker { position: absolute; inset: 0; z-index: 50; display: none; background: rgba(14,14,18,.96); overflow: auto; padding: 28px 32px; }
#picker.on { display: block; }
#picker .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; }
#picker .th { position: relative; width: 100%; aspect-ratio: 16 / 9; background: #fff; border-radius: 6px; overflow: hidden; margin-bottom: 7px; }
#picker .th iframe { position: absolute; left: 0; top: 0; width: var(--stage-w); height: var(--stage-h); border: 0; transform-origin: 0 0; pointer-events: none; }
#picker button { text-align: left; border: 0; border-radius: 10px; padding: 10px 12px; background: rgba(255,255,255,.1); color: #F2F2F5; cursor: pointer;
  font: inherit; font-size: 13px; line-height: 1.35; min-height: 58px; box-shadow: inset 0 0 0 1px rgba(255,255,255,.18); }
#picker button b { font-size: 15px; margin-right: 6px; font-variant-numeric: tabular-nums; }
#picker button:hover, #picker button.cur { background: rgba(255,255,255,.24); box-shadow: inset 0 0 0 2px #F2F2F5; }
#picker .ph { color: #F2F2F5; font-size: 14px; font-weight: 700; margin: 0 0 12px; opacity: .85; }
/* 전체화면에서 도구·페이지 이동을 잠깐 알려 주는 표시 */
#toast { position: absolute; left: 50%; bottom: 28px; transform: translateX(-50%); z-index: 60; padding: 8px 16px; border-radius: 18px;
  background: rgba(14,14,18,.82); color: #F2F2F5; font-size: 15px; font-weight: 700; pointer-events: none; opacity: 0; transition: opacity .25s; white-space: nowrap; }
#toast.on { opacity: 1; }

/* 팝업이 막혔을 때만 쓰는 화면 안 발표자 노트 */
#notes-in { position: fixed; right: 16px; bottom: 16px; width: min(520px, calc(100vw - 32px)); max-height: 50vh; overflow: auto; z-index: 200; display: none;
  background: #1E1E22; color: #F2F2F5; border-radius: 12px; padding: 16px 18px; box-shadow: 0 12px 40px rgba(0,0,0,.4); font-size: 17px; line-height: 1.6; white-space: pre-wrap; }

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
body.dark #pgmenu { background: #26262C; color: #F2F2F5; box-shadow: 0 12px 36px rgba(0,0,0,.5), inset 0 0 0 1px rgba(255,255,255,.12); }
body.dark #pgmenu button:hover { background: rgba(255,255,255,.1); }
body.dark #pgmenu button.cur { background: #F2F2F5; color: #1E1E22; }
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
  .nav, .tap, .ink, .laser, #notes-in, #picker, #toast { display: none !important; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>
</head>
<body>
<div class="deck">
  <div id="show">
    <div class="stage" id="stage" aria-live="polite"><canvas class="ink" id="ink-hl" width="__W__" height="__H__"></canvas><canvas class="ink" id="ink-pen" width="__W__" height="__H__"></canvas><div class="laser" id="laser"></div></div>
    <div class="tap" id="tap" aria-hidden="true"></div>
    <div id="picker" role="dialog" aria-label="페이지 고르기"><p class="ph">전체 보기 — 눌러서 이동 (숫자 입력 후 Enter도 됨, G·Esc 닫기)</p><div class="grid"></div></div>
    <div id="toast" aria-live="polite"></div>
  </div>
  <nav class="nav" aria-label="발표 조작">
    <div class="ctl" role="group" aria-label="페이지 이동">
      <button class="rbtn" data-act="prev" type="button" aria-label="이전 페이지">__I_PREV__</button>
      <div class="pgwrap"><button class="count" data-act="menu" type="button" aria-haspopup="listbox" aria-label="페이지 이동 목록" title="눌러서 페이지 이동 (숫자 입력 후 Enter도 됨)"><span data-cur>1</span> <span class="tot">/ <span data-tot>1</span></span></button><div id="pgmenu" role="listbox" aria-label="페이지 이동"></div></div>
      <button class="rbtn" data-act="next" type="button" aria-label="다음 페이지">__I_NEXT__</button>
      <button class="rbtn hk" data-act="pick" type="button" aria-label="전체 보기 (G 키)" title="모든 페이지 미리보기 (G 키)">__I_GRID__<span class="k">G</span></button>
    </div>
    <div class="tools" role="group" aria-label="발표 도구">
      <button class="tbtn hk" data-tool="pen" type="button" title="펜 (P 키)" aria-label="펜 (P 키)" aria-pressed="false">__I_PEN__<span class="k">P</span></button>
      <button class="tbtn hk" data-tool="hl" type="button" title="형광펜 (H 키)" aria-label="형광펜 (H 키)" aria-pressed="false">__I_HL__<span class="k">H</span></button>
      <button class="tbtn hk" data-tool="laser" type="button" title="레이저 포인터 (L 키)" aria-label="레이저 포인터 (L 키)" aria-pressed="false">__I_LASER__<span class="k">L</span></button>
      <button class="tbtn hk" data-act="fx" type="button" title="클릭 강조: 글자는 형광펜, 상자는 테두리, 화살표는 다시 그리며 강조, 그림 조각은 빛나기. 다시 누르면 지움 (C 키)" aria-label="클릭 강조 (C 키)" aria-pressed="false">__I_FX__<span class="k">C</span></button>
      <button class="tbtn hk" data-act="erase" type="button" title="이 페이지 잉크·강조 지우기 (E 키, 한 획 되돌리기는 Z 키)" aria-label="이 페이지 잉크·강조 지우기 (E 키)">__I_ERASE__<span class="k">E</span></button>
    </div>
    <div class="right">
      <div class="menuwrap"><button class="pill" data-act="settings" type="button" aria-haspopup="dialog" aria-label="보기 설정: 색상·글꼴·애니메이션·그라데이션·페이지 번호·드래그 금지">__I_VIEW__보기 ▾</button>
        <div id="setmenu" role="dialog" aria-label="보기 설정">
          __SWITCH_UI__
          <label class="mrow opt" title="페이지를 열 때 그려지듯 나타남"><input type="checkbox" data-anim><span class="ml">애니메이션</span><span class="k inl">A</span></label>
          <label class="mrow opt" title="상자·도형·그래프에 위가 밝은 그라데이션. PDF에도 그대로"><input type="checkbox" data-grad><span class="ml">그라데이션</span><span class="k inl">D</span></label>
          <label class="mrow opt" title="슬라이드 오른쪽 아래에 페이지 번호. PDF에도 그대로"><input type="checkbox" data-pno><span class="ml">페이지 번호</span><span class="k inl">N</span></label>
          <label class="mrow opt" title="슬라이드 글자를 끌어 선택하지 못하게"><input type="checkbox" data-nosel><span class="ml">드래그 금지</span></label>
        </div>
      </div>
      <button class="pill hk" data-act="notes" type="button" aria-label="발표자 노트 창 열기 (S 키)">__I_NOTES__발표자 노트<span class="k">S</span></button>
      <button class="pill hk" data-act="full" type="button" aria-label="전체화면 발표 (F 키)">__I_FULL__전체화면<span class="k">F</span></button>
      <button class="pill" data-act="pdf" type="button" aria-label="화면 그대로 PDF 파일로 바로 저장" title="지금 화면 그대로(색·글꼴·페이지 번호·잉크) PDF 파일을 바로 내려받음">__I_PDF__<span data-pdf-label>PDF</span></button>
    </div>
  </nav>
</div>
<div id="notes-in" role="dialog" aria-label="발표자 노트"></div>
<script>
(function(){
  var PAGES = __PAGES__, TITLES = __TITLES__, FOOTS = __FOOTS__, NOTES = __NOTES__, PNO_DEFAULT = __PNO__, FOOT = __FOOT__;
  var SW = __SWITCH__, curP = null, curF = null;
  function fill(i, p, f){
    var pg = SW.pages[i], t = SW.tpls[pg.t];
    var cfg = Object.assign({}, SW.cfg, {concept: SW.concept[p] || null, font: f, fontFamily: SW.fam[f]});
    return t.split('/*__JF_PRESET__*/').join(SW.css[p]).split('/*__JF_FONTCSS__*/').join(SW.fontcss[f]).split('__JF_CFG__').join(JSON.stringify(cfg))
            .split('/*__JF_DATA__*/').join(pg.d).split('/*__JF_ICONS__*/').join(pg.i);
  }
  if (SW) {
    try { var sv = JSON.parse(localStorage.getItem('jf-deck-switch') || 'null'); if (sv && SW.css[sv.p] && SW.fontcss[sv.f]) { SW.preset = sv.p; SW.font = sv.f; } } catch (e) {}
    curP = SW.preset; curF = SW.font;
    PAGES = SW.pages.map(function(_, i){ return fill(i, curP, curF); });
  }
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

  // 그려지는 애니메이션 — 페이지를 열 때마다 다시 그림, 체크를 풀면 끔
  var animBox = document.querySelector('[data-anim]'), animOn = true;
  try { var sa = localStorage.getItem('jf-deck-anim'); if (sa !== null) animOn = sa === '1'; } catch (e) {}
  function frameWin(i){ var f = sheets[i] && sheets[i].querySelector('iframe'); return f && f.contentWindow; }
  function animate(i){ var w = frameWin(i); if (w && w.__JF_DONE__ && w.__JF_ANIM__) w.__JF_ANIM__(animOn); }
  window.__JF_FRAME_READY__ = function(w){
    frameOpts(w);
    var i = sheets.findIndex(function(sh){ return sh.querySelector('iframe').contentWindow === w; });
    if (i >= 0 && gradOn && !w.__JF_GLOSS_ON__ && w.__JF_GLOSS__) { w.__JF_GLOSS__(true, function(win){ if (i === cur) animate(cur); }); return; }
    if (frameWin(cur) === w) animate(cur);
  };
  function setAnim(on){
    animOn = on; if (animBox) animBox.checked = on;
    try { localStorage.setItem('jf-deck-anim', on ? '1' : '0'); } catch (e) {}
    animate(cur);
  }
  // ── 발표 도구: 펜·형광펜·레이저 ──────────────────────────────
  var cvPen = document.getElementById('ink-pen'), cvHl = document.getElementById('ink-hl'), laser = document.getElementById('laser');
  var gPen = cvPen.getContext('2d'), gHl = cvHl.getContext('2d');
  var INK = PAGES.map(function(){ return []; }), tool = null, stroke = null;
  var STYLE = {pen: {c: '#E5243B', w: 5, a: 1}, hl: {c: '#FFE14D', w: 30, a: 0.9}};
  function paint(g, st){
    var p = st.pts, S = STYLE[st.k]; if (!p.length) return;
    g.save(); g.globalAlpha = S.a; g.strokeStyle = S.c; g.fillStyle = S.c; g.lineWidth = S.w; g.lineCap = 'round'; g.lineJoin = 'round';
    if (p.length === 1) { g.beginPath(); g.arc(p[0][0], p[0][1], S.w / 2, 0, 7); g.fill(); g.restore(); return; }
    g.beginPath(); g.moveTo(p[0][0], p[0][1]);
    for (var i = 1; i < p.length - 1; i++) { var mx = (p[i][0] + p[i + 1][0]) / 2, my = (p[i][1] + p[i + 1][1]) / 2; g.quadraticCurveTo(p[i][0], p[i][1], mx, my); }
    g.lineTo(p[p.length - 1][0], p[p.length - 1][1]); g.stroke(); g.restore();
  }
  function redraw(){
    gPen.clearRect(0, 0, W, H); gHl.clearRect(0, 0, W, H);
    (INK[cur] || []).concat(stroke ? [stroke] : []).forEach(function(st){ paint(st.k === 'hl' ? gHl : gPen, st); });
  }
  function at(e){ var r = cvPen.getBoundingClientRect(); return [(e.clientX - r.left) / r.width * W, (e.clientY - r.top) / r.height * H]; }
  var toastEl = document.getElementById('toast'), toastT = null;
  function toast(msg){ if (!presenting()) return; toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(function(){ toastEl.classList.remove('on'); }, 1100); }
  var TOOL_NAME = {pen: '펜', hl: '형광펜', laser: '레이저 포인터'};
  function setTool(t){
    tool = (t && t !== tool) ? t : null;
    toast(tool ? TOOL_NAME[tool] + ' (같은 키·Esc로 끔)' : '도구 끔');
    show.classList.toggle('tool-on', !!tool); show.classList.toggle('tool-laser', tool === 'laser');
    all('[data-tool]').forEach(function(b){ var on = b.getAttribute('data-tool') === tool; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    if (tool !== 'laser') laser.style.display = 'none';
  }
  cvPen.addEventListener('pointerdown', function(e){
    if (!tool || tool === 'laser' || e.button !== 0) return;
    cvPen.setPointerCapture(e.pointerId); stroke = {k: tool, pts: [at(e)]}; redraw(); e.preventDefault();
  });
  cvPen.addEventListener('pointermove', function(e){
    if (tool === 'laser') { var q = at(e); laser.style.left = q[0] + 'px'; laser.style.top = q[1] + 'px'; laser.style.display = 'block'; return; }
    if (!stroke) return; var p = at(e), l = stroke.pts[stroke.pts.length - 1];
    if (Math.abs(p[0] - l[0]) + Math.abs(p[1] - l[1]) > 1.5) { stroke.pts.push(p); redraw(); }
  });
  function endStroke(){ if (stroke) { INK[cur].push(stroke); stroke = null; redraw(); } }
  cvPen.addEventListener('pointerup', endStroke); cvPen.addEventListener('pointercancel', endStroke);
  cvPen.addEventListener('pointerleave', function(){ if (tool === 'laser') laser.style.display = 'none'; });
  function erase(){ INK[cur] = []; stroke = null; redraw(); var fw = frameWin(cur); if (fw && fw.__JF_FX_CLEAR__) fw.__JF_FX_CLEAR__(); toast('이 페이지 잉크·강조 지움'); }
  function undo(){ INK[cur].pop(); redraw(); toast('한 획 되돌림'); }

  // ── 발표자 노트: 별도 창(팝업) — 현재·다음 슬라이드 미리보기, 노트, 경과 시간, 이동 버튼 ──────
  var nw = null, t0 = null, notesIn = document.getElementById('notes-in');
  function pageSrc(i){ return SW ? fill(i, curP, curF) : PAGES[i]; }
  // 노트 창도 덱과 같은 글꼴 — 덱 문서의 @font-face·@import 규칙만 옮겨 담는다
  var FONT_RULES = (function(){ var out = []; try { Array.prototype.forEach.call(document.styleSheets, function(ss){ Array.prototype.forEach.call(ss.cssRules || [], function(r){ if (r.type === 3 || r.type === 5) out.push(r.cssText); }); }); } catch (e) {} return out.join('\n'); })();
  var NOTES_DOC = '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>발표자 노트</title><style>' + FONT_RULES
    + '*{box-sizing:border-box}body{margin:0;background:#16161A;color:#F2F2F5;font-family:' + getComputedStyle(document.body).fontFamily + ';height:100vh;display:grid;grid-template-rows:auto 1fr auto}'
    + 'header{display:flex;align-items:center;gap:18px;padding:12px 18px;background:#0E0E11;font-variant-numeric:tabular-nums}'
    + '.pg{font-size:22px;font-weight:800}.pg span{opacity:.55;font-weight:600}.tm{font-size:22px;font-weight:700;margin-left:auto}.clk{font-size:16px;opacity:.6}'
    + 'button{font:inherit;font-size:14px;font-weight:700;height:34px;padding:0 14px;border-radius:17px;border:0;background:rgba(255,255,255,.12);color:#F2F2F5;cursor:pointer;box-shadow:inset 0 0 0 1px rgba(255,255,255,.25)}button:hover{background:rgba(255,255,255,.22)}'
    + 'main{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:18px;padding:16px 18px;min-height:0}'
    + '.col{display:flex;flex-direction:column;gap:10px;min-height:0}.lab{font-size:13px;font-weight:700;opacity:.6;letter-spacing:.5px}'
    + '.pv{position:relative;width:100%;aspect-ratio:16/9;background:#fff;border-radius:6px;overflow:hidden;flex:none}.pv iframe{position:absolute;left:0;top:0;width:' + W + 'px;height:' + H + 'px;border:0;transform-origin:0 0;pointer-events:none}'
    + '.nx{opacity:.85}.ttl{font-size:15px;font-weight:700;opacity:.85}'
    + '#nt{font-size:24px;line-height:1.65;white-space:pre-wrap;overflow:auto;min-height:0;padding-right:6px}#nt.empty{opacity:.45;font-size:18px}'
    + 'footer{display:flex;gap:8px;padding:10px 18px;background:#0E0E11;align-items:center}footer .sp{flex:1}.zoom{opacity:.7;font-size:13px}'
    + '</style></head><body><header><div class="pg"><b id="cu">1</b> <span>/ <span id="to">1</span></span></div><div class="ttl" id="tt"></div><div class="tm" id="tm">00:00</div><div class="clk" id="ck"></div></header>'
    + '<main><div class="col"><div class="lab">지금 슬라이드</div><div class="pv" id="pv1"><iframe id="f1" scrolling="no"></iframe></div><div class="lab">다음</div><div class="pv nx" id="pv2" style="width:62%"><iframe id="f2" scrolling="no"></iframe></div><div class="ttl" id="nt2"></div></div>'
    + '<div class="col"><div class="lab">발표자 노트</div><div id="nt"></div></div></main>'
    + '<footer><button id="bp">◀ 이전</button><button id="bn">다음 ▶</button><span class="sp"></span><span class="zoom">노트 글자</span><button id="zm">−</button><button id="zp">+</button><button id="rs">시간 초기화</button></footer></body></html>';
  function fitPv(d){ ['pv1', 'pv2'].forEach(function(id){ var b = d.getElementById(id), f = b && b.querySelector('iframe'); if (f) f.style.transform = 'scale(' + (b.clientWidth / W) + ')'; }); }
  function notesSync(){
    var txt = (NOTES[cur] || '').trim();
    if (notesIn.style.display === 'block') notesIn.textContent = (cur + 1) + ' / ' + PAGES.length + '  ' + (TITLES[cur] || '') + '\n\n' + (txt || '(노트 없음)');
    if (!nw || nw.closed) return;
    var d = nw.document;
    d.getElementById('cu').textContent = cur + 1; d.getElementById('to').textContent = PAGES.length;
    d.getElementById('tt').textContent = TITLES[cur] || '';
    var nt = d.getElementById('nt'); nt.textContent = txt || '이 페이지에는 노트가 없습니다. spec의 "notes"에 적으면 여기 나옵니다'; nt.classList.toggle('empty', !txt);
    var f1 = d.getElementById('f1'), f2 = d.getElementById('f2');
    if (f1.__i !== cur) { f1.__i = cur; f1.srcdoc = pageSrc(cur); }
    var nx = cur + 1 < PAGES.length ? cur + 1 : -1;
    if (f2.__i !== nx) { f2.__i = nx; f2.srcdoc = nx >= 0 ? pageSrc(nx) : '<body style="margin:0;background:#2A2A30"></body>'; }
    d.getElementById('nt2').textContent = nx >= 0 ? TITLES[nx] || '' : '마지막 페이지';
    fitPv(d);
  }
  function openNotes(){
    if (nw && !nw.closed) { nw.focus(); return; }
    nw = window.open('', 'jf-notes', 'width=1100,height=720');
    if (!nw) {   // 팝업이 막히면 화면 오른쪽 아래에 노트 상자
      var on = notesIn.style.display !== 'block'; notesIn.style.display = on ? 'block' : 'none';
      all('[data-act="notes"]').forEach(function(b){ b.classList.toggle('on', on); }); notesSync(); return;
    }
    nw.document.open(); nw.document.write(NOTES_DOC); nw.document.close();
    var d = nw.document, fs = 24; t0 = Date.now();
    d.getElementById('bp').onclick = function(){ go(cur - 1); }; d.getElementById('bn').onclick = function(){ go(cur + 1); };
    d.getElementById('rs').onclick = function(){ t0 = Date.now(); };
    d.getElementById('zp').onclick = function(){ fs = Math.min(48, fs + 2); d.getElementById('nt').style.fontSize = fs + 'px'; };
    d.getElementById('zm').onclick = function(){ fs = Math.max(14, fs - 2); d.getElementById('nt').style.fontSize = fs + 'px'; };
    d.addEventListener('keydown', key);
    nw.addEventListener('resize', function(){ fitPv(d); });
    var tick = function(){ if (!nw || nw.closed) return; var s = Math.floor((Date.now() - t0) / 1000);
      d.getElementById('tm').textContent = String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
      d.getElementById('ck').textContent = new Date().toLocaleTimeString('ko-KR', {hour: '2-digit', minute: '2-digit'}); };
    tick(); nw.__jfT = nw.setInterval(tick, 1000);
    all('[data-act="notes"]').forEach(function(b){ b.classList.add('on'); });
    var watch = setInterval(function(){ if (!nw || nw.closed) { clearInterval(watch); all('[data-act="notes"]').forEach(function(b){ b.classList.remove('on'); }); } }, 800);
    notesSync();
  }
  window.addEventListener('beforeunload', function(){ try { if (nw && !nw.closed) nw.close(); } catch (e) {} });

  // ── 페이지 고르기: 번호(가운데 숫자)나 G 키로 칸 목록, 숫자 입력 후 Enter로 바로 이동 ──────
  var picker = document.getElementById('picker'), pgrid = picker.querySelector('.grid');
  // 번호 → 드롭다운 목록
  var pgmenu = document.getElementById('pgmenu');
  function openMenu(on){
    if (on === undefined) on = !pgmenu.classList.contains('on');
    if (on) {
      pgmenu.innerHTML = '';
      PAGES.forEach(function(_, i){ var b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'option'); if (i === cur) { b.className = 'cur'; b.setAttribute('aria-selected', 'true'); }
        var nb = document.createElement('b'); nb.textContent = i + 1; b.appendChild(nb); var tt = document.createElement('span'); tt.textContent = TITLES[i] || ''; b.appendChild(tt);
        b.addEventListener('click', function(ev){ ev.stopPropagation(); openMenu(false); go(i); }); pgmenu.appendChild(b); });
    }
    pgmenu.classList.toggle('on', on);
    if (on) { var c = pgmenu.querySelector('.cur'); if (c) { c.scrollIntoView({block: 'center'}); c.focus(); } }
  }
  document.addEventListener('click', function(ev){ if (pgmenu.classList.contains('on') && !ev.target.closest('.pgwrap')) openMenu(false); });
  var setmenu = document.getElementById('setmenu');
  function openSettings(on){ if (on === undefined) on = !setmenu.classList.contains('on'); setmenu.classList.toggle('on', on); if (on) openMenu(false); }
  document.addEventListener('click', function(ev){ if (setmenu.classList.contains('on') && !ev.target.closest('.menuwrap')) openSettings(false); });
  // 전체 보기 → 미리보기 칸(보이는 칸만 그때그때 그림, 색·글꼴·그라데이션도 지금 화면 그대로)
  var thumbKey = '', thumbIO = null;
  function fitThumbs(){ pgrid.querySelectorAll('.th').forEach(function(th){ var f = th.querySelector('iframe'); if (f) f.style.transform = 'scale(' + (th.clientWidth / W) + ')'; }); }
  function openPicker(on){
    if (on === undefined) on = !picker.classList.contains('on');
    var key = (SW ? curP + '|' + curF : '') + '|' + gradOn;
    if (on && (key !== thumbKey || !pgrid.children.length)) {
      thumbKey = key; pgrid.innerHTML = ''; if (thumbIO) thumbIO.disconnect();
      thumbIO = new IntersectionObserver(function(es){ es.forEach(function(en){
        if (!en.isIntersecting || en.target.querySelector('iframe')) return;
        var i = +en.target.getAttribute('data-i'), f = document.createElement('iframe'); f.setAttribute('scrolling', 'no'); f.tabIndex = -1;
        f.addEventListener('load', function(){ var tw = f.contentWindow, tries = 0;
          (function g(){ if (tw.__JF_DONE__) { if (gradOn && tw.__JF_GLOSS__) tw.__JF_GLOSS__(true); } else if (tries++ < 60) setTimeout(g, 150); })(); });
        f.srcdoc = pageSrc(i); en.target.appendChild(f); f.style.transform = 'scale(' + (en.target.clientWidth / W) + ')';
      }); }, {root: picker, rootMargin: '200px'});
      PAGES.forEach(function(_, i){ var b = document.createElement('button'); b.type = 'button';
        var th = document.createElement('div'); th.className = 'th'; th.setAttribute('data-i', i); b.appendChild(th);
        var nb = document.createElement('b'); nb.textContent = i + 1; b.appendChild(nb); b.appendChild(document.createTextNode(TITLES[i] || ''));
        b.addEventListener('click', function(){ openPicker(false); go(i); }); pgrid.appendChild(b); thumbIO.observe(th); });
    }
    pgrid.querySelectorAll('button').forEach(function(b, i){ b.classList.toggle('cur', i === cur); });
    picker.classList.toggle('on', on);
    if (on) { openMenu(false); fitThumbs(); var c = pgrid.querySelector('.cur'); if (c) { c.scrollIntoView({block: 'center'}); c.focus(); } }
  }
  window.addEventListener('resize', function(){ if (picker.classList.contains('on')) fitThumbs(); });
  var numBuf = '', numT = null;
  function typeNum(d){ numBuf = (numBuf + d).slice(-4); clearTimeout(numT); numT = setTimeout(function(){ numBuf = ''; }, 1600); toastAny('→ ' + numBuf + ' 쪽 (Enter)'); }
  function toastAny(msg){ toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(function(){ toastEl.classList.remove('on'); }, 1300); }

  // ── 클릭 강조·드래그 금지: 페이지(iframe) 안에서 처리. 켜 두면 새로 그려진 페이지에도 바로 적용 ──────
  var fxBtns = all('[data-act="fx"]'), noselBox = document.querySelector('[data-nosel]'), fxOn = false, noselOn = false;
  try { fxOn = localStorage.getItem('jf-deck-fx') === '1'; noselOn = localStorage.getItem('jf-deck-nosel') === '1'; } catch (e) {}
  function frameOpts(w){ if (!w) return; try { if (w.__JF_FX__) w.__JF_FX__(fxOn); if (w.__JF_NOSELECT__) w.__JF_NOSELECT__(noselOn); } catch (e) {} }
  function setFx(on){ fxOn = on; fxBtns.forEach(function(b){ b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); }); show.classList.toggle('fx-on', on);
    try { localStorage.setItem('jf-deck-fx', on ? '1' : '0'); } catch (e) {} sheets.forEach(function(_, i){ frameOpts(frameWin(i)); }); toast(on ? '클릭 강조 켬 (다시 누르면 지움, E 모두 지움)' : '클릭 강조 끔'); }
  function setNosel(on){ noselOn = on; if (noselBox) noselBox.checked = on; document.body.classList.toggle('nosel', on);
    try { localStorage.setItem('jf-deck-nosel', on ? '1' : '0'); } catch (e) {} sheets.forEach(function(_, i){ frameOpts(frameWin(i)); }); }

  // ── 그라데이션: 원본 doc-figure v2.4의 --gloss 토큰 방식. 켜면 모든 페이지를 그 자리에서 다시 그린다 ──────
  var gradBox = document.querySelector('[data-grad]'), gradOn = false;
  try { gradOn = localStorage.getItem('jf-deck-grad') === '1'; } catch (e) {}
  function applyGrad(i){ var w = frameWin(i); if (w && w.__JF_DONE__ && w.__JF_GLOSS__ && !!w.__JF_GLOSS_ON__ !== gradOn) w.__JF_GLOSS__(gradOn, function(win){ if (i === cur && animOn && win.__JF_ANIM__) win.__JF_ANIM__(true); }); }
  function setGrad(on){
    gradOn = on; if (gradBox) gradBox.checked = on;
    try { localStorage.setItem('jf-deck-grad', on ? '1' : '0'); } catch (e) {}
    applyGrad(cur); sheets.forEach(function(_, i){ if (i !== cur) setTimeout(function(){ applyGrad(i); }, 30 * i); });
    toast(on ? '그라데이션 켬' : '그라데이션 끔');
  }

  // ── PDF: 인쇄 대화상자 없이 지금 화면 그대로 파일로 바로 저장 ──────────────
  //   각 페이지를 보이는 그대로 그림으로 떠서(html-to-image, 페이지 안에서 실행해 웹폰트까지 담음)
  //   하단 글귀·페이지 번호·잉크를 얹고, jsPDF로 1920×1080(1440×810pt) 한 장씩 묶어 내려받는다
  var PDF_LIB = {cap: 'https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js',
                 pdf: 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'};
  var capSrc = null, busy = false;
  function addScript(doc, text){ var sc = doc.createElement('script'); sc.text = text; (doc.head || doc.documentElement).appendChild(sc); }
  function getText(u){ return fetch(u).then(function(r){ if (!r.ok) throw new Error(u); return r.text(); }); }
  function wait(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function overlay(g, i){
    var sh = sheets[i], sr = sh.getBoundingClientRect(), k = sr.width / W || 1;
    sh.querySelectorAll('.foot, .pno').forEach(function(el){
      var cs = getComputedStyle(el); if (cs.display === 'none' || !el.textContent) return;
      var r = el.getBoundingClientRect();
      g.save(); g.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily; g.fillStyle = cs.color; g.textBaseline = 'middle';
      g.textAlign = el.classList.contains('pno') ? 'right' : 'left';
      var y = (r.top + r.height / 2 - sr.top) / k, x = el.classList.contains('pno') ? (r.right - sr.left) / k : (r.left - sr.left) / k;
      g.fillText(el.textContent, x, y); g.restore();
    });
    (INK[i] || []).forEach(function(st){ g.save(); if (st.k === 'hl') g.globalCompositeOperation = 'multiply'; paint(g, st); g.restore(); });
  }
  function savePdf(btn){
    if (busy) return; busy = true;
    var lab = btn.querySelector('[data-pdf-label]'), old = lab.textContent;
    var setLab = function(t){ lab.textContent = t; };
    setLab('준비 중');
    var libs = [capSrc ? Promise.resolve(capSrc) : getText(PDF_LIB.cap),
                window.jspdf ? Promise.resolve() : getText(PDF_LIB.pdf).then(function(t){ addScript(document, t); })];
    Promise.all(libs).then(async function(res){
      capSrc = res[0];
      var doc = new window.jspdf.jsPDF({orientation: 'landscape', unit: 'px', format: [W, H], hotfixes: ['px_scaling'], compress: true});
      for (var i = 0; i < PAGES.length; i++) {
        setLab((i + 1) + ' / ' + PAGES.length);
        var w = frameWin(i), t0 = Date.now();
        while (!(w && w.__JF_DONE__) && Date.now() - t0 < 15000) { await wait(150); w = frameWin(i); }
        if (w.__JF_ANIM__) w.__JF_ANIM__(false);   // 떠오르는 중간 모습이 찍히지 않게
        if (!w.htmlToImage) addScript(w.document, capSrc);
        var node = w.document.getElementById('jf-page') || w.document.body;
        var cv = await w.htmlToImage.toCanvas(node, {width: W, height: H, pixelRatio: 2, backgroundColor: '#ffffff'});
        var g = cv.getContext('2d'); g.setTransform(cv.width / W, 0, 0, cv.height / H, 0, 0);
        overlay(g, i);
        if (i > 0) doc.addPage([W, H], 'landscape');
        doc.addImage(cv.toDataURL('image/jpeg', 0.92), 'JPEG', 0, 0, W, H, undefined, 'FAST');
      }
      var name = (document.title || 'slides').replace(/[\\/:*?"<>|]+/g, ' ').trim() || 'slides';
      doc.save(name + '.pdf');
      setLab('저장됨'); setTimeout(function(){ setLab(old); }, 1800);
    }).catch(function(e){
      // 라이브러리를 못 받으면(오프라인 등) 인쇄로 대신 — 대상에서 'PDF로 저장'을 고르면 같은 1920×1080 한 장씩
      console.error(e); setLab(old); window.print();
    }).then(function(){ busy = false; animate(cur); });
  }

  function go(n, push){
    n = Math.max(0, Math.min(PAGES.length - 1, n));
    sheets.forEach(function(s, i){ s.classList.toggle('on', i === n); });
    var changed = cur !== n;
    cur = n;
    if (changed || push === false) animate(n);
    all('[data-cur]').forEach(function(e){ e.textContent = n + 1; });
    all('[data-act="prev"]').forEach(function(b){ b.disabled = n === 0; });
    all('[data-act="next"]').forEach(function(b){ b.disabled = n === PAGES.length - 1; });
    if (push !== false) history.replaceState(null, '', '#' + (n + 1));
    redraw(); notesSync();
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

  all('[data-tool]').forEach(function(b){ b.addEventListener('click', function(){ setTool(b.getAttribute('data-tool')); }); });
  all('[data-act]').forEach(function(b){
    b.addEventListener('click', function(){
      var a = b.getAttribute('data-act');
      if (a === 'prev') go(cur - 1);
      else if (a === 'next') go(cur + 1);
      else if (a === 'full') toggleFull();
      else if (a === 'pdf') savePdf(b);
      else if (a === 'pick') openPicker();
      else if (a === 'menu') openMenu();
      else if (a === 'settings') openSettings();
      else if (a === 'fx') setFx(!fxOn);
      else if (a === 'erase') erase();
      else if (a === 'notes') openNotes();
    });
  });
  function key(e){
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target && e.target.tagName;
    var k = e.key, c = e.code || '';
    // 한글 입력 상태에서도 같은 자리의 키로 동작하도록 물리 키(KeyP·Digit3)로 읽는다
    var L = c.indexOf('Key') === 0 ? c.slice(3).toLowerCase() : (/^[a-zA-Z]$/.test(k) ? k.toLowerCase() : '');
    var D = c.indexOf('Digit') === 0 ? c.slice(5) : (/^Numpad[0-9]$/.test(c) ? c.slice(6) : (/^[0-9]$/.test(k) ? k : ''));
    if (t === 'SELECT' || (t === 'INPUT' && e.target.type !== 'checkbox')) return;
    if (setmenu.classList.contains('on') && k === 'Escape') { openSettings(false); e.preventDefault(); return; }
    if (pgmenu.classList.contains('on') && k === 'Escape') { openMenu(false); e.preventDefault(); return; }
    if (picker.classList.contains('on') && (k === 'Escape' || L === 'g')) { openPicker(false); e.preventDefault(); return; }
    if (D) { typeNum(D); e.preventDefault(); return; }
    if (k === 'Enter' && numBuf) { var nn = parseInt(numBuf, 10); numBuf = ''; openPicker(false); go(nn - 1); toastAny(nn + ' 쪽'); e.preventDefault(); return; }
    if (picker.classList.contains('on')) return;
    if (k === 'ArrowRight' || k === 'PageDown' || (k === ' ' && !e.shiftKey && t !== 'BUTTON' && t !== 'INPUT')) { go(cur + 1); e.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'PageUp' || (k === ' ' && e.shiftKey)) { go(cur - 1); e.preventDefault(); }
    else if (k === 'Home') { go(0); e.preventDefault(); }
    else if (k === 'End') { go(PAGES.length - 1); e.preventDefault(); }
    else if (L === 'f') { toggleFull(); e.preventDefault(); }
    else if (k === 'Escape' && tool) { setTool(null); e.preventDefault(); }
    else if (k === 'Escape' && show.classList.contains('present')) { setPresent(false); e.preventDefault(); }
    else if (L === 'p') { setTool('pen'); e.preventDefault(); }
    else if (L === 'h') { setTool('hl'); e.preventDefault(); }
    else if (L === 'l') { setTool('laser'); e.preventDefault(); }
    else if (L === 'e') { erase(); e.preventDefault(); }
    else if (L === 'z') { undo(); e.preventDefault(); }
    else if (L === 's') { openNotes(); e.preventDefault(); }
    else if (L === 'g') { openPicker(true); e.preventDefault(); }
    else if (L === 'd') { setGrad(!gradOn); e.preventDefault(); }
    else if (L === 'c') { setFx(!fxOn); e.preventDefault(); }
    else if (L === 'n') { setPno(!document.body.classList.contains('show-pno')); e.preventDefault(); }
    else if (L === 'a') { setAnim(!animOn); e.preventDefault(); }
  }
  document.addEventListener('keydown', key);
  sheets.forEach(function(sh){
    var f = sh.querySelector('iframe');
    f.addEventListener('load', function(){
      try { var d = f.contentWindow.document; d.addEventListener('keydown', key); d.addEventListener('mousemove', poke); } catch (e) {}
      frameOpts(f.contentWindow);
    });
  });
  if (__DARK__) document.body.classList.add('dark');
  // 색상·글꼴 선택 상자 — 내용은 같고 프리셋 CSS·글꼴만 바꿔 모든 페이지를 다시 그린다
  function theme(p, f){
    curP = p; curF = f;
    // 같은 내용 그대로 — 각 페이지에서 CSS(프리셋·글꼴)만 갈아 끼워 다시 그린다. 그 기능이 없을 때만 다시 불러옴
    sheets.forEach(function(sh, i){
      var w = sh.querySelector('iframe').contentWindow;
      if (w && w.__JF_RETHEME__) {
        w.__JF_RETHEME__({css: SW.css[p], fontcss: SW.fontcss[f], concept: SW.concept[p] || null, font: f, fam: SW.fam[f],
                          done: function(win){ if (i === cur && animOn && win.__JF_ANIM__) win.__JF_ANIM__(true); }});
      } else {
        sh.querySelector('iframe').srcdoc = fill(i, p, f);
      }
    });
    document.documentElement.style.setProperty('--backdrop', SW.backdrop[p]);
    document.body.classList.toggle('dark', !!SW.dark[p]);
    try { localStorage.setItem('jf-deck-switch', JSON.stringify({p: p, f: f})); } catch (e) {}
  }
  if (SW) {
    var selP = document.getElementById('sw-preset'), selF = document.getElementById('sw-font');
    selP.value = curP; selF.value = curF;
    selP.addEventListener('change', function(){ theme(selP.value, curF); });
    selF.addEventListener('change', function(){ theme(curP, selF.value); });
    document.documentElement.style.setProperty('--backdrop', SW.backdrop[curP]);
    document.body.classList.toggle('dark', !!SW.dark[curP]);
    nav.classList.add('has-sw');
  }
  nav.classList.add('has-sw');   // 버튼이 많아 좁은 화면에서는 두 줄로 접는다(제목은 숨김)
  window.addEventListener('beforeprint', function(){ stage.style.transform = ''; });
  window.addEventListener('afterprint', fit);
  fit();
  if (animBox) { animBox.checked = animOn; animBox.addEventListener('change', function(){ setAnim(animBox.checked); }); }
  if (gradBox) { gradBox.checked = gradOn; gradBox.addEventListener('change', function(){ setGrad(gradBox.checked); }); }
  fxBtns.forEach(function(b){ b.classList.toggle('on', fxOn); b.setAttribute('aria-pressed', fxOn ? 'true' : 'false'); }); show.classList.toggle('fx-on', fxOn);
  if (noselBox) { noselBox.checked = noselOn; noselBox.addEventListener('change', function(){ setNosel(noselBox.checked); }); }
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

def font_opts():
    out = []
    for kind, name in (("gothic", "고딕"), ("myeongjo", "명조")):
        items = [(k, f["label"]) for k, f in jf_page.FONTS.items() if f["kind"] == kind]
        if items:
            out.append('<optgroup label="%s">' % name + "".join('<option value="%s">%s</option>' % (k, H.escape(l)) for k, l in items) + "</optgroup>")
    return "".join(out)

def switch_data(specs, fk):
    """선택 상자용 데이터: 프리셋 표식이 든 페이지 틀, 프리셋 CSS, 컨셉, 바깥 배경, 글꼴 CSS"""
    import glob, re
    pal = json.load(open(os.path.join(ROOT, "references", "jf-palettes.json"), encoding="utf-8"))
    import jf_palette
    chart = [(pre, "%s %s" % (pid, name)) for pid, pre, name in jf_palette.chart_presets()]
    in_chart = {pre for pre, _ in chart}
    groups = [("컬러차트", chart),
              ("그 밖의 컨셉", [("jf-" + k, d["label"]) for k, d in pal.get("concepts", {}).items() if "jf-" + k not in in_chart]),
              ("내용 계열", [("jf-" + k, d["label"]) for k, d in pal["families"].items()]),
              ("흑백", [("jf-mono-ink", "흑백"), ("jf-mono-gray", "그레이스케일")])]
    have = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "presets", "jf-*.css"))}
    css, concept, bd, dark = {}, {}, {}, {}
    opts = []
    for g, items in groups:
        items = [(k, l) for k, l in items if k in have]
        if not items:
            continue
        opts.append('<optgroup label="%s">' % H.escape(g) + "".join('<option value="%s">%s</option>' % (k, H.escape(l)) for k, l in items) + "</optgroup>")
        for k, _ in items:
            c = open(os.path.join(ROOT, "presets", k + ".css"), encoding="utf-8").read()
            css[k] = c; concept[k] = jf_page.concept({"preset": k})
            bd[k] = jf_page.backdrop(c, k); dark[k] = is_dark(bd[k])
    first = specs[0].get("preset", "jf-timeless")
    tpls, pages = [], []
    for sp in specs:
        t, dd, ic = B.build_parts(dict(sp, page=jf_page.mode(sp) or "16:9"))
        if t not in tpls:
            tpls.append(t)
        pages.append({"t": tpls.index(t), "d": dd, "i": ic})
    data = {"tpls": tpls, "pages": pages,
            "css": css, "concept": concept, "backdrop": bd, "dark": dark,
            "fontcss": {k: jf_page.font_css(k) for k in jf_page.FONTS}, "fam": {k: v["family"] for k, v in jf_page.FONTS.items()},
            "cfg": jf_page.base_cfg(dict(specs[0], page=jf_page.mode(specs[0]) or "16:9")),
            "preset": first if first in css else sorted(css)[0], "font": fk}
    ui = ('<label class="mrow sw"><span class="ml">색상</span><select id="sw-preset" aria-label="색상 프리셋">%s</select></label>'
          '<label class="mrow sw"><span class="ml">글꼴</span><select id="sw-font" aria-label="글꼴">%s</select></label><div class="msep"></div>') % ("".join(opts), font_opts())
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/"), ui

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--no-number", action="store_true", help="처음 열 때 페이지 번호를 숨긴 상태로")
    ap.add_argument("--footer", default="", help="페이지 하단 왼쪽에 작게 이탤릭으로 넣을 논문 제목")
    ap.add_argument("--preset", default="", help="모든 페이지의 프리셋을 이것으로 (예: jf-timeless)")
    ap.add_argument("--font", default="", help="모든 페이지 글꼴: gothic(고딕, 기본) | myeongjo(명조)")
    ap.add_argument("--switcher", action="store_true", help="아래쪽에 색상·글꼴 선택 상자를 넣어 프리셋을 바꿔 보게 한다")
    a = ap.parse_args()
    specs = [B.load_spec(p) for p in a.specs]
    if a.preset:
        specs = [dict(s, preset=a.preset) for s in specs]
    if a.font:
        specs = [dict(s, font=a.font) for s in specs]
    # 페이지 하단 글귀는 "page_footer" — 문자열 "footer"도 받되 템플릿에는 넘기지 않는다(간트 등은 footer를 하단 상자 사양으로 쓴다)
    specs = [dict({k: v for k, v in s.items() if k != "footer"}, page_footer=s.get("page_footer") or s["footer"]) if isinstance(s.get("footer"), str) else s for s in specs]
    fk = jf_page.font_kind(specs[0])
    sizes = {jf_page.size(dict(s, page=jf_page.mode(s) or "16:9")) for s in specs}
    if len(sizes) != 1:
        sys.exit("페이지 비율이 서로 다름: %s — 한 덱은 한 비율로" % sizes)
    w, h = sizes.pop()
    pages, titles, foots, notes = [], [], [], []
    for s in specs:
        s = dict(s, page=jf_page.mode(s) or "16:9")
        pages.append(B.build_string(s, embed=True))
        titles.append(s.get("title") or s.get("kicker") or "")
        foots.append(s.get("page_footer", ""))
        nt = s.get("notes", "")   # 발표자 노트: 문자열 또는 줄 목록
        notes.append("\n".join("· " + str(x) for x in nt) if isinstance(nt, list) else str(nt or ""))
    title = a.title or titles[0]
    sw_data, sw_ui = "null", ""
    if a.switcher:
        sw_data, sw_ui = switch_data(specs, fk)
    out = SHELL
    E = jf_page.ELEM   # 하단 글귀·페이지 번호도 요소 기준(references/jf-elements.json)에서
    for k, v in (("__PNO_R__", str(E["page_number"]["right"])), ("__PNO_B__", str(E["page_number"]["bottom"])), ("__PNO_S__", str(E["page_number"]["size"])),
                 ("__FOOT_X__", str(E["footer"]["x"])), ("__FOOT_B__", str(E["footer"]["bottom"])), ("__FOOT_S__", str(E["footer"]["size"])),
                 ("__FONT__", jf_page.font_css(fk)), ("__BACKDROP__", jf_page.backdrop(B.preset_css(specs[0]), specs[0].get("preset", ""))),
                 ("__W__", str(w)), ("__H__", str(h)), ("__FONT_STACK__", jf_page.FONTS[fk]["stack"]),
                 ("__I_PREV__", ICON["prev"]), ("__I_NEXT__", ICON["next"]), ("__I_FULL__", ICON["full"]),
                 ("__I_EXIT__", ICON["exit"]), ("__I_PDF__", ICON["pdf"]),
                 ("__I_GRID__", ICON["grid"]), ("__I_VIEW__", ICON["view"]), ("__I_FX__", ICON["fx"]), ("__I_PEN__", ICON["pen"]), ("__I_HL__", ICON["hl"]), ("__I_LASER__", ICON["laser"]), ("__I_ERASE__", ICON["erase"]), ("__I_NOTES__", ICON["notes"]),
                 ("__NOTES__", json.dumps(notes, ensure_ascii=False).replace("</", "<\\/")),
                 ("__PNO__", "false" if a.no_number else "true"),
                 ("__DARK__", "true" if is_dark(jf_page.backdrop(B.preset_css(specs[0]), specs[0].get("preset", ""))) else "false"),
                 ("__FOOT__", json.dumps(a.footer, ensure_ascii=False).replace("</", "<\\/")),
                 ("__TITLES__", json.dumps(titles, ensure_ascii=False).replace("</", "<\\/")),
                 ("__FOOTS__", json.dumps(foots, ensure_ascii=False).replace("</", "<\\/")),
                 ("__TITLE__", H.escape(title))):
        out = out.replace(k, v)
    out = out.replace("__SWITCH_UI__", sw_ui).replace("__SWITCH__", sw_data)
    out = out.replace("__PAGES__", "[]" if a.switcher else "[" + ",".join(json.dumps(p, ensure_ascii=False).replace("</", "<\\/") for p in pages) + "]")
    open(a.out, "w", encoding="utf-8").write(out)
    print("✓ %s  %d쪽  %dx%d" % (a.out, len(pages), w, h))

if __name__ == "__main__":
    main()

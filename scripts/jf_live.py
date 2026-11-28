#!/usr/bin/env python3
"""화면에서 바로 고치기 — 덱을 띄워 두고, 화면에서 남긴 수정 지시를 큐로 받아 spec을 고친 뒤 다시 그린다 (표준 라이브러리만)

lecture-deck-kit(박주이)의 '화면에서 고치기' 흐름을 이 스킬의 spec → 덱 구조에 맞게 다시 만든 것.
페이지마다 spec 파일 이름이 고정 ID라서, 장을 넣거나 빼도 이미 남긴 지시가 엉뚱한 장을 가리키지 않는다.

  python3 scripts/jf_live.py serve  --root <폴더> --specs a.json b.json ... [--preset jf-timeless] [--font ...] [--port 4611]
  python3 scripts/jf_live.py watch  --root <폴더>        # 새 지시를 한 줄씩 출력(Monitor로 깨우기용)
  python3 scripts/jf_live.py pending --root <폴더>       # 아직 처리하지 않은 지시 + cursor_after (편집 전 스냅샷)
  python3 scripts/jf_live.py done   --root <폴더> --cursor N --note "무엇을 고쳤나" [--needs-input id,id]
  python3 scripts/jf_live.py status --root <폴더>
  python3 scripts/jf_live.py revert --root <폴더>        # 가장 최근 스냅샷으로 되돌림

- 상태의 진실은 feedback/queue.jsonl(추가만)과 feedback/cursor(처리한 줄 수) 두 파일뿐이다. 미처리 = 줄 수 − 커서.
  알림이 사라지거나 두 번 와도, 고치는 도중 새 지시가 와도 빠지거나 겹치지 않는다
- done은 마지막에 한 번: 덱을 다시 만들고(build.json의 같은 옵션) 게시 토큰을 올려 화면이 보던 페이지 그대로 새로 고쳐진다
- 편집 도구는 화면에 띄울 때만 붙는다. 저장되는 deck.html에는 들어가지 않는다
"""
import argparse, datetime, http.server, json, os, shutil, socketserver, subprocess, sys, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "jf_build_deck.py")


def fb(root, *p):
    return os.path.join(root, "feedback", *p)


def read_lines(root):
    q = fb(root, "queue.jsonl")
    if not os.path.exists(q):
        return []
    out = []
    for line in open(q, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                out.append({"broken": line})
    return out


def cursor(root):
    try:
        return int(open(fb(root, "cursor"), encoding="utf-8").read().strip() or 0)
    except (OSError, ValueError):
        return 0


def token(root):
    try:
        return open(fb(root, "published"), encoding="utf-8").read().strip()
    except OSError:
        return "0"


def bump(root):
    t = str(int(time.time() * 1000))
    open(fb(root, "published"), "w", encoding="utf-8").write(t)
    return t


def build(root):
    cfg = json.load(open(fb(root, "build.json"), encoding="utf-8"))
    r = subprocess.run([sys.executable, "-I", BUILD] + cfg["args"], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("덱 다시 만들기 실패:\n" + r.stdout + r.stderr)
    return r.stdout.strip()


# ── 화면에 붙는 편집 도구(서버가 보낼 때만 주입) ─────────────────────────
OVERLAY = r"""
(function(){
  if (window.__JF_LIVE__) return; window.__JF_LIVE__ = true;
  var D = window.__JF_DECK__; if (!D) return;
  var css = document.createElement('style'); css.textContent = [
    '#jfl-bar{position:fixed;top:12px;right:12px;z-index:400;display:flex;gap:6px;align-items:center;font:600 13px/1 system-ui,sans-serif}',
    '#jfl-bar button{height:32px;border:0;border-radius:16px;padding:0 12px;cursor:pointer;font:inherit;background:#1E1E22;color:#fff;box-shadow:0 4px 14px rgba(0,0,0,.25)}',
    '#jfl-bar .st{background:rgba(30,30,34,.85);color:#fff;border-radius:16px;padding:9px 12px}',
    '#jfl-pin{position:fixed;z-index:401;display:none;width:32px;height:32px;border-radius:50%;border:0;background:#FFB000;color:#1E1E22;font-size:16px;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.3)}',
    '#jfl-box{position:fixed;z-index:402;right:12px;top:52px;width:min(380px,calc(100vw - 24px));display:none;background:#fff;color:#1E1E22;border-radius:14px;padding:14px;box-shadow:0 16px 48px rgba(0,0,0,.35);font:14px/1.45 system-ui,sans-serif}',
    '#jfl-box .q{background:#FFF4CC;border-radius:8px;padding:6px 9px;margin:6px 0 8px;font-size:13px;max-height:84px;overflow:auto;white-space:pre-wrap}',
    '#jfl-box .pg{font-size:12px;opacity:.7}',
    '#jfl-box textarea{width:100%;box-sizing:border-box;min-height:74px;border:1px solid #D6D6DC;border-radius:8px;padding:8px;font:inherit;resize:vertical}',
    '#jfl-box .chips{display:flex;flex-wrap:wrap;gap:5px;margin:8px 0}',
    '#jfl-box .chips button{border:1px solid #D6D6DC;background:#fff;border-radius:14px;padding:4px 9px;font:12px system-ui,sans-serif;cursor:pointer}',
    '#jfl-box .chips button.on{background:#1E1E22;color:#fff;border-color:#1E1E22}',
    '#jfl-box .row{display:flex;gap:6px;justify-content:space-between;align-items:center;margin-top:6px}',
    '#jfl-box .row button{height:32px;border:0;border-radius:8px;padding:0 12px;cursor:pointer;font:600 13px system-ui,sans-serif}',
    '#jfl-box .send{background:#1E1E22;color:#fff}', '#jfl-box .ghost{background:#F0F0F3;color:#1E1E22}'
  ].join('\n'); document.head.appendChild(css);
  var bar = document.createElement('div'); bar.id = 'jfl-bar';
  bar.innerHTML = '<span class="st" id="jfl-st">화면에서 고치기 · 대기 0</span><button type="button" id="jfl-page">이 장 고치기</button><button type="button" id="jfl-deck">덱 전체</button>';
  document.body.appendChild(bar);
  var pin = document.createElement('button'); pin.id = 'jfl-pin'; pin.type = 'button'; pin.title = '고른 글자에 수정 지시 남기기'; pin.textContent = '💬'; document.body.appendChild(pin);
  var box = document.createElement('div'); box.id = 'jfl-box';
  box.innerHTML = '<div class="pg" id="jfl-pg"></div><div class="q" id="jfl-q"></div>'
    + '<textarea id="jfl-t" placeholder="어떻게 고칠지 적어 주세요 (예: 더 짧게, 표로 바꿔, 숫자 확인)"></textarea>'
    + '<div class="chips" id="jfl-chips"></div>'
    + '<div class="row"><span class="pg">Ctrl/Cmd+Enter 보내기 · Esc 닫기</span><span><button type="button" class="ghost" id="jfl-x">닫기</button> <button type="button" class="send" id="jfl-go">보내기</button></span></div>';
  document.body.appendChild(box);
  var CHIPS = ['더 간결하게', '둘로 쪼개기', '도식 형태 바꾸기', '근거·출처 보강', '용어 원문과 맞추기', '글자 크게'];
  var chipsEl = box.querySelector('#jfl-chips');
  CHIPS.forEach(function(c){ var b = document.createElement('button'); b.type = 'button'; b.textContent = c; b.onclick = function(){ b.classList.toggle('on'); }; chipsEl.appendChild(b); });
  var draft = null;
  function openBox(d){
    draft = d;
    box.querySelector('#jfl-pg').textContent = d.scope === 'deck' ? '덱 전체' : ((d.index + 1) + '쪽 · ' + (d.title || '') + ' · id ' + d.page);
    var q = box.querySelector('#jfl-q'); q.style.display = d.selected ? 'block' : 'none'; q.textContent = d.selected || '';
    box.querySelector('#jfl-t').value = ''; chipsEl.querySelectorAll('button').forEach(function(b){ b.classList.remove('on'); });
    box.style.display = 'block'; pin.style.display = 'none'; setTimeout(function(){ box.querySelector('#jfl-t').focus(); }, 30);
  }
  function closeBox(){ box.style.display = 'none'; draft = null; }
  function pageInfo(){ var i = D.cur(); return {index: i, page: D.ids[i], title: D.titles[i]}; }
  box.querySelector('#jfl-x').onclick = closeBox;
  box.querySelector('#jfl-go').onclick = send;
  box.querySelector('#jfl-t').addEventListener('keydown', function(e){
    e.stopPropagation();
    if (e.key === 'Escape') closeBox();
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) send();
  });
  function send(){
    if (!draft) return;
    var chips = Array.prototype.slice.call(chipsEl.querySelectorAll('button.on')).map(function(b){ return b.textContent; });
    var body = Object.assign({}, draft, {instruction: box.querySelector('#jfl-t').value.trim(), chips: chips});
    if (!body.instruction && !chips.length) { box.querySelector('#jfl-t').focus(); return; }
    fetch('/__feedback', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)})
      .then(function(r){ return r.json(); }).then(function(){ closeBox(); poll(); }).catch(function(){ alert('보내지 못했습니다 — 서버가 꺼졌는지 확인'); });
  }
  bar.querySelector('#jfl-page').onclick = function(){ var p = pageInfo(); openBox(Object.assign(p, {scope: 'page', selected: ''})); };
  bar.querySelector('#jfl-deck').onclick = function(){ var p = pageInfo(); openBox(Object.assign(p, {scope: 'deck', selected: ''})); };
  // 슬라이드 안에서 글자를 고르면 💬 — 페이지(iframe)마다 붙인다
  function hook(f, i){
    var d; try { d = f.contentDocument; } catch (e) { return; }
    if (!d || d.__jfl) return; d.__jfl = true;
    try { if (f.contentWindow.__JF_NOSELECT__) f.contentWindow.__JF_NOSELECT__(false); } catch (e) {}
    d.addEventListener('mouseup', function(){ setTimeout(function(){
      var sel = d.getSelection(), txt = sel ? String(sel).trim() : '';
      if (!txt || txt.length < 2) { pin.style.display = 'none'; return; }
      var r = sel.getRangeAt(0).getBoundingClientRect(), fr = f.getBoundingClientRect(), k = fr.width / f.offsetWidth || 1;
      var n = sel.anchorNode, full = n && n.nodeValue ? n.nodeValue : '', at = full.indexOf(txt);
      var before = at >= 0 ? full.slice(Math.max(0, at - 30), at) : '', after = at >= 0 ? full.slice(at + txt.length, at + txt.length + 30) : '';
      pin.style.left = Math.min(window.innerWidth - 40, fr.left + r.right * k + 6) + 'px';
      pin.style.top = Math.max(8, fr.top + r.top * k - 36) + 'px'; pin.style.display = 'block';
      pin.onclick = function(){ var p = pageInfo(); openBox(Object.assign(p, {scope: 'text', selected: txt.slice(0, 400), before: before, after: after})); };
    }, 10); });
  }
  setInterval(function(){ document.querySelectorAll('.sheet iframe').forEach(hook); }, 800);
  // 게시 토큰이 바뀌면(고쳐서 다시 만들어짐) 보던 페이지 그대로 새로 고침
  var tok = null;
  function poll(){
    fetch('/__status', {cache: 'no-store'}).then(function(r){ return r.json(); }).then(function(s){
      document.getElementById('jfl-st').textContent = '화면에서 고치기 · 대기 ' + s.pending + (s.pending ? ' (반영 중)' : '');
      if (tok === null) tok = s.published; else if (s.published !== tok) location.reload();
    }).catch(function(){ document.getElementById('jfl-st').textContent = '서버 연결 끊김'; });
  }
  poll(); setInterval(poll, 1500);
})();
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    root = "."
    deck = "deck.html"

    def __init__(self, *a, **k):
        super().__init__(*a, directory=self.root, **k)

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/__status":
            return self._json({"published": token(self.root), "pending": max(0, len(read_lines(self.root)) - cursor(self.root))})
        if path == "/__jf_live.js":
            b = OVERLAY.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            return self.wfile.write(b)
        if path in ("/", "/" + self.deck):
            html = open(os.path.join(self.root, self.deck), encoding="utf-8").read()
            i = html.rfind("</body>")
            inj = '<script src="/__jf_live.js"></script>'
            html = html[:i] + inj + html[i:] if i >= 0 else html + inj
            b = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            return self.wfile.write(b)
        return super().do_GET()

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/__feedback":
            return self._json({"error": "not found"}, 404)
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > 65536:
            return self._json({"error": "size"}, 413)
        try:
            d = json.loads(self.rfile.read(n).decode("utf-8"))
        except ValueError:
            return self._json({"error": "json"}, 400)
        keep = ("page", "index", "title", "scope", "selected", "before", "after", "instruction", "chips")
        rec = {k: d.get(k) for k in keep if d.get(k) not in (None, "", [])}
        rec["n"] = len(read_lines(self.root)) + 1
        rec["ts"] = datetime.datetime.now().isoformat(timespec="seconds")
        with open(fb(self.root, "queue.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return self._json({"ok": True, "n": rec["n"]})


def cmd_serve(a):
    root = os.path.abspath(a.root)
    os.makedirs(fb(root, "versions"), exist_ok=True)
    deck = a.deck
    args = [os.path.abspath(p) for p in a.specs] + ["-o", os.path.join(root, deck)]
    for opt in ("preset", "font", "title", "footer"):
        v = getattr(a, opt)
        if v:
            args += ["--" + opt, v]
    if a.switcher:
        args.append("--switcher")
    json.dump({"args": args, "deck": deck, "specs": [os.path.abspath(p) for p in a.specs]},
              open(fb(root, "build.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for name, init in (("queue.jsonl", ""), ("cursor", "0")):
        if not os.path.exists(fb(root, name)):
            open(fb(root, name), "w", encoding="utf-8").write(init)
    print(build(root))
    bump(root)
    Handler.root, Handler.deck = root, deck
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", a.port), Handler) as srv:
        print("화면에서 고치기: http://127.0.0.1:%d/%s  (Ctrl+C로 끝)" % (a.port, deck), flush=True)
        srv.serve_forever()


def cmd_watch(a):
    root = os.path.abspath(a.root)
    q = fb(root, "queue.jsonl")
    seen = len(read_lines(root))
    while True:
        lines = read_lines(root)
        for r in lines[seen:]:
            where = "덱 전체" if r.get("scope") == "deck" else "%s쪽 %s" % ((r.get("index") or 0) + 1, r.get("page", ""))
            sel = ('"%s"' % r["selected"][:40]) if r.get("selected") else "(장 전체)"
            msg = r.get("instruction") or " / ".join(r.get("chips") or [])
            print("[화면에서 고치기] #%s %s | 선택: %s | 지시: %s" % (r.get("n"), where, sel, msg), flush=True)
        seen = max(seen, len(lines))
        if not os.path.exists(q):
            break
        time.sleep(1)


def snapshot(root, note):
    cfg = json.load(open(fb(root, "build.json"), encoding="utf-8"))
    d = fb(root, "versions", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(d, exist_ok=True)
    files = cfg["specs"] + [os.path.join(root, cfg["deck"])]
    man = []
    for i, p in enumerate(files):
        if os.path.exists(p):
            dst = os.path.join(d, "%03d_%s" % (i, os.path.basename(p)))
            shutil.copy2(p, dst)
            man.append({"src": p, "copy": os.path.basename(dst)})
    json.dump({"note": note, "files": man}, open(os.path.join(d, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def cmd_pending(a):
    root = os.path.abspath(a.root)
    lines, c = read_lines(root), cursor(root)
    items = lines[c:]
    snap = snapshot(root, "pending 직전") if items else None
    print(json.dumps({"pending": len(items), "cursor_after": len(lines), "items": items, "snapshot": snap}, ensure_ascii=False, indent=1))


def cmd_done(a):
    root = os.path.abspath(a.root)
    total = len(read_lines(root))
    if a.cursor < cursor(root) or a.cursor > total:
        sys.exit("cursor 값이 맞지 않음 (현재 %d, 줄 수 %d) — pending이 알려준 cursor_after를 그대로 넣는다" % (cursor(root), total))
    out = "" if a.no_build else build(root)
    open(fb(root, "cursor"), "w", encoding="utf-8").write(str(a.cursor))
    t = bump(root)
    with open(fb(root, "log.md"), "a", encoding="utf-8") as f:
        f.write("- %s 처리 ~#%d: %s%s\n" % (datetime.datetime.now().isoformat(timespec="seconds"), a.cursor, a.note or "",
                                       (" · 되물음: " + a.needs_input) if a.needs_input else ""))
    left = len(read_lines(root)) - a.cursor
    print(json.dumps({"ok": True, "built": out, "published": t, "left": left}, ensure_ascii=False))


def cmd_status(a):
    root = os.path.abspath(a.root)
    lines, c = read_lines(root), cursor(root)
    print(json.dumps({"lines": len(lines), "cursor": c, "pending": max(0, len(lines) - c), "published": token(root)}, ensure_ascii=False))


def cmd_revert(a):
    root = os.path.abspath(a.root)
    vs = sorted(os.listdir(fb(root, "versions"))) if os.path.isdir(fb(root, "versions")) else []
    if not vs:
        sys.exit("되돌릴 스냅샷이 없음")
    d = fb(root, "versions", vs[-1])
    man = json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8"))
    for f in man["files"]:
        shutil.copy2(os.path.join(d, f["copy"]), f["src"])
    t = bump(root)
    print(json.dumps({"ok": True, "restored": vs[-1], "files": len(man["files"]), "published": t}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("serve"); p.add_argument("--root", required=True); p.add_argument("--specs", nargs="+", required=True)
    p.add_argument("--deck", default="deck.html"); p.add_argument("--port", type=int, default=4611)
    for opt in ("preset", "font", "title", "footer"):
        p.add_argument("--" + opt, default="")
    p.add_argument("--switcher", action="store_true"); p.set_defaults(fn=cmd_serve)
    p = sub.add_parser("watch"); p.add_argument("--root", required=True); p.set_defaults(fn=cmd_watch)
    p = sub.add_parser("pending"); p.add_argument("--root", required=True); p.set_defaults(fn=cmd_pending)
    p = sub.add_parser("done"); p.add_argument("--root", required=True); p.add_argument("--cursor", type=int, required=True)
    p.add_argument("--note", default=""); p.add_argument("--needs-input", default=""); p.add_argument("--no-build", action="store_true")
    p.set_defaults(fn=cmd_done)
    p = sub.add_parser("status"); p.add_argument("--root", required=True); p.set_defaults(fn=cmd_status)
    p = sub.add_parser("revert"); p.add_argument("--root", required=True); p.set_defaults(fn=cmd_revert)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

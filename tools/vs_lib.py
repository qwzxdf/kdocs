"""Visual Studio（実験的なインスタンス）を UI Automation で操作して、docs/vs/img 用の実寸 PNG を撮る道具。

ユーザーが普段使う Visual Studio には触れない。`devenv /RootSuffix Exp` で起動した実験的なインスタンスだけを相手にする。
"""
import re, time, subprocess
from pathlib import Path
from pywinauto import Desktop
from pywinauto.keyboard import send_keys
from PIL import ImageGrab, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'vs' / 'img'
RAW = ROOT / 'tools' / 'vs_raw'        # 枠を付ける前の原画（枠を直すだけなら撮り直さない）
DEVENV = r'C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\devenv.exe'
D = Desktop(backend='uia')
RED = (235, 40, 40)


def launch(target, wait=60):
    """実験的なインスタンスで、ソリューションかフォルダーを開く。"""
    subprocess.Popen(['powershell', '-NoProfile', '-Command',
                      f"Start-Process '{DEVENV}' -ArgumentList '/RootSuffix','Exp','{target}'"])
    for _ in range(wait * 2):
        time.sleep(0.5)
        v = VS.find()
        if v:
            time.sleep(8)
            return v
    raise RuntimeError('起動しない')


def kill():
    subprocess.run(['taskkill', '/F', '/FI', 'WINDOWTITLE eq *実験的なインスタンス*'], capture_output=True)
    subprocess.run(['powershell', '-NoProfile', '-Command',
                    "Get-CimInstance Win32_Process -Filter \"Name='devenv.exe'\" | "
                    "Where-Object { $_.CommandLine -match 'RootSuffix' } | "
                    "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"], capture_output=True)
    time.sleep(3)


class _Step:
    failed = []

    def __init__(self, label): self.label = label

    def __enter__(self): print('▶', self.label); return self

    def __exit__(self, et, ev, tb):
        if et:
            print('  ✗ 失敗:', self.label, repr(ev)[:150]); _Step.failed.append(self.label)
            return True


class VS:
    def __init__(self, hwnd, pid):
        self.hwnd, self.pid = hwnd, pid

    @staticmethod
    def find():
        for w in D.windows():
            try:
                if w.is_visible() and '実験的なインスタンス' in w.window_text():
                    return VS(w.handle, w.process_id())
            except Exception:
                pass
        return None

    # ---- 部品 ----
    def main(self): return D.window(handle=self.hwnd).wrapper_object()

    def front(self):
        try: self.main().set_focus()
        except Exception: pass
        time.sleep(0.2)

    def step(self, label): return _Step(label)

    def rect(self, c):
        r = c.rectangle(); return (r.left, r.top, r.right, r.bottom)

    def descendants(self, scope=None, **kw): return (scope or self.main()).descendants(**kw)

    def find_one(self, name, ctype=None, scope=None, regex=False, visible=True, nth=0):
        out = []
        for c in self.descendants(scope, control_type=ctype) if ctype else self.descendants(scope):
            try:
                t = c.window_text()
                ok = re.search(name, t) if regex else t == name
                if ok and (not visible or (c.is_visible() and c.rectangle().width() > 0)):
                    out.append(c)
            except Exception:
                pass
        if len(out) <= nth: raise KeyError(f'{name} が見つからない')
        return out[nth]

    def click(self, c, wait=0.6):
        self.front(); c.click_input(); time.sleep(wait)

    def key(self, keys, wait=0.8):
        self.front(); send_keys(keys, pause=0.05); time.sleep(wait)

    def esc(self, n=3):
        for _ in range(n):
            send_keys('{ESC}'); time.sleep(0.3)

    # ---- メニュー ----
    def menu(self, *path, wait=0.7):
        """メニューを順に開く（例: menu('ファイル','新規作成')）。開いたままにする。"""
        self.front()
        c = self.find_one(path[0], 'MenuItem')
        c.click_input(); time.sleep(wait)
        for p in path[1:]:
            c = [x for x in self.descendants(control_type='MenuItem')
                 if x.window_text() == p and x.is_visible() and x.rectangle().top > 30][-1]
            c.click_input(); time.sleep(wait)

    def popup_box(self, pad=4):
        """開いているメニューの外接長方形。"""
        rs = []
        for x in self.descendants(control_type='MenuItem'):
            try:
                r = x.rectangle()
                if x.is_visible() and r.top > 30 and r.width() > 40: rs.append((r.left, r.top, r.right, r.bottom))
            except Exception:
                pass
        if not rs: raise RuntimeError('メニューが開いていない')
        return (min(r[0] for r in rs) - pad, min(r[1] for r in rs) - pad, max(r[2] for r in rs) + pad, max(r[3] for r in rs) + pad)

    # ---- ダイアログ ----
    def top_windows(self):
        """この Visual Studio のウィンドウ（メイン以外）を Win32 で列挙する（UIA の列挙には出ないダイアログがある）。"""
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        out = []
        cb = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

        def f(h, _):
            if u.IsWindowVisible(h):
                p = wintypes.DWORD(); u.GetWindowThreadProcessId(h, ctypes.byref(p))
                if p.value == self.pid and h != self.hwnd:
                    b = ctypes.create_unicode_buffer(200); u.GetWindowTextW(h, b, 200)
                    out.append((h, b.value))
            return True
        u.EnumWindows(cb(f), 0)
        return out

    def dialog(self, title_re, timeout=10):
        for _ in range(int(timeout * 4)):
            for h, t in self.top_windows():
                if re.search(title_re, t):
                    return D.window(handle=h).wrapper_object()
            time.sleep(0.25)
        raise KeyError(title_re)

    def tree_select(self, dlg, *path):
        """プロパティ ページの左のツリーで項目を選ぶ。"""
        tree = dlg.descendants(control_type='Tree')[0]
        it = tree.get_item(list(path))
        it.select(); time.sleep(0.7)
        return it

    # ---- 撮影 ----
    def grab(self, box, front=True):
        if front: self.front()
        return ImageGrab.grab(bbox=box, all_screens=True).convert('RGB')

    def save(self, name, img, marks=()):
        """原画を vs_raw に、枠つきを docs/vs/img に PNG で保存する。marks は (x0,y0,x1,y1) の列（画像の座標）。"""
        RAW.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
        img.save(RAW / f'{name}.png', optimize=True)
        out = mark(img, marks) if marks else img
        out.save(OUT / f'{name}.png', optimize=True)
        print(f'  {name}.png', out.size, (OUT / f"{name}.png").stat().st_size // 1024, 'KB', f'marks={len(marks)}')

    def shot_window(self, name, w, marks=(), pad=0):
        r = w.rectangle()
        box = (r.left - pad, r.top - pad, r.right + pad, r.bottom + pad)
        self.save(name, self.grab(box), marks)

    def shot_menu(self, name, marks=()):
        self.save(name, self.grab(self.popup_box()), marks)

    def shot_main(self, name, crop=None, marks=()):
        """メイン ウィンドウ全体（枠の影を除く）。crop は (x0,y0,x1,y1) をウィンドウ左上からの座標で。"""
        r = self.main().rectangle()
        x0, y0 = max(r.left, 0) + 8 * (r.left < 0), max(r.top, 0) + 8 * (r.top < 0)
        x1, y1 = min(r.right, 1920) - 8 * (r.right > 1920), min(r.bottom, 1040) - 8 * (r.bottom > 1040)
        img = self.grab((x0, y0, x1, y1))
        if crop: img = img.crop(crop)
        self.save(name, img, marks)

    def recover(self):
        """開いたままのメニューとダイアログを閉じる。"""
        self.esc(3)
        for h, title in self.top_windows():
            try:
                w = D.window(handle=h).wrapper_object()
                for b in w.descendants(control_type='Button'):
                    if b.window_text() in ('キャンセル', '閉じる'):
                        b.click_input(); break
                else:
                    w.close()
            except Exception:
                pass
        self.esc(2)


def mark(img, boxes):
    """赤い枠と、右下の丸数字（Git のページと同じ見た目）。"""
    im = img.copy(); d = ImageDraw.Draw(im)
    try: fnt = ImageFont.truetype('meiryob.ttc', 16)
    except Exception: fnt = None
    for n, (x0, y0, x1, y1) in enumerate(boxes, 1):
        d.rectangle((x0, y0, x1, y1), outline=RED, width=3)
        d.ellipse((x1 - 11, y1 - 11, x1 + 11, y1 + 11), fill=RED)
        d.text((x1 - 5 - (4 if n > 9 else 0), y1 - 10), str(n), fill='white', font=fnt)
    return im

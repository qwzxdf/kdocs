"""SourceTree を UI Automation（pywinauto）で動かす部品と、実寸のスクリーンショット。

Git の解説ページ（docs/git/）の画像を、座標を使わずに、決まった手順で撮り直すための道具。
使い方と注意は tools/README_sourcetree.md を読むこと。
"""
import ctypes
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image, ImageGrab
from pywinauto import Application, mouse

ctypes.windll.shcore.SetProcessDpiAwareness(2)
user32 = ctypes.windll.user32
dwm = ctypes.windll.dwmapi

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'git' / 'img'
ST_EXE = Path.home() / 'AppData' / 'Local' / 'SourceTree' / 'SourceTree.exe'


def git(repo, *args, check=True):
    """git をそのまま呼ぶ（SourceTree の外で状態を作るとき用）。"""
    r = subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                       text=True, encoding='utf-8')
    if check and r.returncode != 0:
        raise RuntimeError(f'git {args}: {r.stderr}')
    return r.stdout


def write(path, text):
    """ファイルを UTF-8（LF）で書く。エディターで保存したことの代わり。"""
    Path(path).write_text(text, encoding='utf-8', newline='\n')


def _frame(hwnd):
    """影を含まない、見た目どおりの枠（DWMWA_EXTENDED_FRAME_BOUNDS = 9）。"""
    r = wintypes.RECT()
    if dwm.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(r), ctypes.sizeof(r)) != 0:
        user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom


class _Step:
    failed = []

    def __init__(self, s, label):
        self.s, self.label = s, label

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is None:
            return False
        if et in (KeyboardInterrupt, SystemExit):
            return False
        _Step.failed.append(self.label)
        print(f'!! 失敗: {self.label}: {et.__name__}: {str(ev)[:120]}')
        self.s.recover()
        return True


class ST:
    def __init__(self):
        self.app = Application(backend='uia').connect(path='SourceTree.exe')

    # ---- ウィンドウ ----
    def _spec(self, w):
        return self.app.window(handle=w.handle)

    def main(self):
        for w in self.app.windows():
            if w.window_text() == 'Sourcetree':
                return self._spec(w)
        return self._spec(self.app.top_window())

    def dialogs(self):
        m = self.main().handle
        return [self._spec(w) for w in self.app.windows()
                if w.handle != m and w.is_visible()]

    def dialog(self, timeout=6):
        """いま開いているダイアログを返す。出るまで待つ。"""
        end = time.time() + timeout
        while time.time() < end:
            d = self.dialogs()
            if d:
                return d[0]
            time.sleep(0.2)
        raise TimeoutError('ダイアログが出ない')

    def place(self):
        """本体を、いつも同じ位置と大きさ（1200 × 800）に置く。"""
        h = self.main().handle
        user32.ShowWindow(h, 9)
        user32.MoveWindow(h, 40, 40, 1200, 800, True)
        self.front()

    def front(self):
        # SwitchToThisWindow は前面に出す権利が無くても通り、Alt キーも押さずに済む
        user32.SwitchToThisWindow(self.main().handle, True)
        time.sleep(0.3)

    # ---- 操作 ----
    def find(self, scope=None, **kw):
        scope = scope or (self.dialogs() or [self.main()])[0]
        return scope.child_window(**kw)

    def click(self, scope=None, wait=0.6, **kw):
        """auto_id か title で部品を探して押す。Invoke が使えなければ実際にクリックする。"""
        c = self.find(scope, **kw).wrapper_object()
        self.front()
        c.click_input()      # Invoke は、効かないボタンがある（ブランチの作成など）ので、実際にクリックする
        time.sleep(wait)

    def toolbar(self, name, wait=0.8):
        self.click(self.main(), auto_id=name, wait=wait)

    def sidebar(self, text):
        """左のサイドバーの項目（ブランチ名など）を探して返す。"""
        for c in self.main().descendants(control_type='Text'):
            if c.window_text() == text:
                return c
        raise KeyError(text)

    def type_into(self, ctrl, text):
        ctrl.set_focus()
        ctrl.type_keys('^a{DEL}', pause=0.02)
        ctrl.type_keys(text.replace(' ', '{SPACE}'), pause=0.02)
        time.sleep(0.3)

    def key(self, keys, wait=0.6):
        self.main().type_keys(keys)
        time.sleep(wait)

    def open_repo(self, path):
        """SourceTree.exe -f でリポジトリのタブを開く。"""
        subprocess.Popen([str(ST_EXE), '-f', str(path)], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        time.sleep(3)

    def refresh(self):
        """外で git を動かしたあと、画面に反映させる（F5）。"""
        self.front()
        self.main().type_keys('{F5}')
        time.sleep(1.2)

    def dump(self, scope=None):
        """見えている操作部品を一覧にする。新しい画面の ID を調べるときに使う。"""
        scope = scope or (self.dialogs() or [self.main()])[0]
        for c in scope.descendants():
            i = c.element_info
            if i.control_type in ('Edit', 'Button', 'ComboBox', 'CheckBox', 'ListItem',
                                  'TabItem', 'MenuItem', 'RadioButton', 'Text'):
                try:
                    if not c.is_visible():
                        continue
                except Exception:
                    continue
                print(i.control_type, repr((i.name or '')[:40]), i.automation_id[:40])

    def menu_box(self, pad=6):
        """開いている右クリック メニュー（サブメニューも）の外接四角形。"""
        rs = [c.rectangle() for c in self.main().wrapper_object().descendants(control_type='MenuItem')
              if c.rectangle().width() > 60 and c.rectangle().top > 75 and c.is_visible()]
        if not rs:
            raise RuntimeError('メニューが開いていない')
        return (min(r.left for r in rs) - pad, min(r.top for r in rs) - pad,
                max(r.right for r in rs) + pad, max(r.bottom for r in rs) + pad)

    def overlay(self):
        """重なって描かれているダイアログの本体（無ければ None）。"""
        found = [c for c in self.main().wrapper_object().descendants()
                 if c.element_info.class_name.endswith('Dialog')]
        return found[-1] if found else None

    def overlay_box(self, pad=14):
        """本体の上に重なって描かれるダイアログ（クラス名が …Dialog）の、見える範囲。
        枠いっぱいに広がる容器ではなく、中の部品の外接四角形から求める。"""
        found = [c for c in self.main().wrapper_object().descendants()
                 if c.element_info.class_name.endswith('Dialog')]
        if not found:
            return None
        rs = [c.rectangle() for c in found[-1].descendants() if c.rectangle().width() > 0]
        return (min(r.left for r in rs) - pad, min(r.top for r in rs) - 6,
                max(r.right for r in rs) + pad, max(r.bottom for r in rs) + pad)

    # ---- 失敗からの復帰 ----
    def recover(self):
        """開きっぱなしのメニュー・ダイアログ・重なり表示を閉じて、本体を前面に戻す。"""
        for _ in range(3):
            try:
                for d in self.dialogs():          # 別ウィンドウ（マージで競合など）
                    try:
                        d.wrapper_object().close()
                    except Exception:
                        d.type_keys('{ESC}')
                self.front()
                # 本体の中に出るメッセージ（マージで競合 など）の「閉じる」「OK」
                for b in self.main().wrapper_object().descendants(control_type='Button'):
                    if b.element_info.automation_id.startswith('CommandButton') and b.is_visible():
                        b.click_input()
                        time.sleep(0.5)
                        break
                # 小さな確認ウィンドウ（破棄しますか？ など）は、本体の子として見える
                for b in self.main().wrapper_object().descendants(control_type='Button'):
                    if b.window_text() == 'キャンセル' and b.is_visible() and b.rectangle().top < 250:
                        b.click_input()
                        time.sleep(0.5)
                        break
                self.main().type_keys('{ESC}{ESC}')
                time.sleep(0.3)
                ov = self.overlay()
                if ov is None:
                    return
                for name in ('キャンセル', '閉じる', 'OK'):
                    b = ov.descendants(title=name, control_type='Button')
                    if b:
                        b[0].click_input()
                        time.sleep(0.5)
                        break
            except Exception:
                time.sleep(0.5)

    def step(self, label):
        """with s.step('名前'): … 失敗しても止まらず、復帰して次へ進む。"""
        return _Step(self, label)

    # ---- スクリーンショット ----
    def shot(self, name, mode='main', pad=0):
        """実寸の PNG を docs/git/img/<name>.png に保存する。
        main: 本体 / top: 手前のダイアログ / union: すべてのウィンドウを含む範囲。"""
        self.front()
        wins = [w for w in self.app.windows() if w.is_visible()]
        boxes = [(_frame(w.handle), w) for w in wins]
        if mode == 'top':
            d = self.dialogs()
            box = _frame(d[0].handle) if d else self.overlay_box() or boxes[0][0]
        elif mode == 'menu':
            box = self.menu_box()
        elif mode == 'union':
            bs = [b for b, _ in boxes]
            box = (min(b[0] for b in bs), min(b[1] for b in bs),
                   max(b[2] for b in bs), max(b[3] for b in bs))
        else:
            box = _frame(self.main().handle)
        box = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
        img = ImageGrab.grab(bbox=box, all_screens=True).convert('RGB')
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / f'{name}.png'
        img.quantize(colors=256, dither=Image.Dither.NONE).save(path, optimize=True)
        print(f'{name}.png', img.size, path.stat().st_size // 1024, 'KB')
        return path


if __name__ == '__main__':
    # python tools/st_lib.py dump  … いま見えている部品の一覧
    # python tools/st_lib.py shot 名前 [main|top|union]
    s = ST()
    cmd = sys.argv[1]
    if cmd == 'dump':
        s.dump()
    elif cmd == 'shot':
        s.shot(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'main')
    elif cmd == 'place':
        s.place()

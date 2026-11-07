"""docs/vs/img の画像を、まとめて撮る。使い方: python tools/vs_shoot.py props menus debug errors cmake

撮る画像の一覧は tools/vs_shots.md。段階（stage）ごとに、対象の Visual Studio（実験的なインスタンス）を起動して撮る。
枠は、あとから tools/vs_mark.py で原画（tools/vs_raw）に付ける。撮り直さなくてよい。
"""
import sys, time, ctypes
from vs_lib import *

GAME = r'C:\vsshots\Game\Game.sln'


def resize(dlg, w, h):
    r = dlg.rectangle()
    ctypes.windll.user32.MoveWindow(dlg.handle, r.left - (w - r.width()) // 2 if r.left > 400 else r.left, r.top, w, h, True)
    time.sleep(0.5)


def open_props(v):
    v.front()
    tree = [c for c in v.descendants(control_type='TreeItem') if c.window_text() == 'Game'][0]
    tree.click_input(); time.sleep(0.4)
    v.key('%{ENTER}', wait=3)
    return v.dialog('プロパティ ページ')


PROPS = [
    ('props-general', ('構成プロパティ', '全般')),
    ('props-debug', ('構成プロパティ', 'デバッグ')),
    ('props-vcdirs', ('構成プロパティ', 'VC++ ディレクトリ')),
    ('props-cpp-general', ('構成プロパティ', 'C/C++', '全般')),
    ('props-language', ('構成プロパティ', 'C/C++', '言語')),
    ('props-preprocessor', ('構成プロパティ', 'C/C++', 'プリプロセッサ')),
    ('props-cmdline', ('構成プロパティ', 'C/C++', 'コマンド ライン')),
    ('props-linker-general', ('構成プロパティ', 'リンカー', '全般')),
    ('props-linker-input', ('構成プロパティ', 'リンカー', '入力')),
    ('props-linker-system', ('構成プロパティ', 'リンカー', 'システム')),
]


def stage_props(v):
    v.recover()
    dlg = open_props(v)
    resize(dlg, 1100, 700)
    for name, path in PROPS:
        with v.step(name):
            v.tree_select(dlg, *path)
            v.shot_window(name, dlg)
    with v.step('props-cpp-general-asan'):
        v.tree_select(dlg, '構成プロパティ', 'C/C++', '全般')
        send_keys('{END}'); time.sleep(0.5)
        v.shot_window('props-cpp-general-asan', dlg)
    with v.step('props-config-dropdown'):
        cb = dlg.descendants(control_type='ComboBox')[0]
        cb.click_input(); time.sleep(0.8)
        r = dlg.rectangle()
        v.save('props-config-dropdown', v.grab((r.left, r.top, r.right, r.top + 260)))
        send_keys('{ESC}'); time.sleep(0.4)
    v.recover()



MENUS = [
    ('file-new-menu', ('ファイル', '新規作成')),
    ('file-open-menu', ('ファイル', '開く')),
    ('tools-menu', ('ツール',)),
    ('project-menu', ('プロジェクト',)),
    ('build-menu', ('ビルド',)),
    ('debug-menu', ('デバッグ',)),
    ('extensions-menu', ('拡張機能',)),
    ('view-other-windows', ('表示', 'その他のウィンドウ')),
]


def stage_menus(v):
    for name, path in MENUS:
        with v.step(name):
            v.recover()
            v.menu(*path)
            v.shot_menu(name)
            v.esc(3)
    v.recover()


def big_dialog(v, timeout=10):
    """幅 300 以上のダイアログ（WPF 製は、題名が「Microsoft Visual Studio」や空になる）。"""
    for _ in range(int(timeout * 4)):
        for h, t in v.top_windows():
            w = D.window(handle=h).wrapper_object()
            if w.rectangle().width() > 300: return w
        time.sleep(0.25)
    raise KeyError('ダイアログがない')


def select_project(v):
    tree = [c for c in v.descendants(control_type='TreeItem') if c.window_text() == 'Game'][0]
    tree.click_input(); time.sleep(0.4)


def stage_dialogs(v):
    v.recover()
    with v.step('new-project'):
        v.key('^+n', wait=4)
        w = big_dialog(v)
        c = [c for c in w.descendants(control_type='ComboBox') if c.window_text() == '言語フィルター'][0]
        c.select('C++'); time.sleep(1.5)
        v.shot_window('new-project', w)
        v.recover()
    with v.step('add-new-item'):
        select_project(v)
        v.key('^+a', wait=3)
        w = big_dialog(v)
        v.shot_window('add-new-item', w)
        for b in w.descendants(control_type='Button'):
            if 'すべてのテンプレート' in b.window_text():
                b.click_input(); time.sleep(1.5); v.shot_window('add-new-item', w); break
        v.recover()
    with v.step('options-all'):
        v.menu('ツール', 'オプション...'); time.sleep(3)
        v.shot_main('options-all')
        v.recover()
    with v.step('property-manager'):
        v.menu('表示', 'その他のウィンドウ', 'プロパティ マネージャー'); time.sleep(2)
        v.shot_main('property-manager')
        v.recover()


def grid_dropdown(v, dlg, name, box_h=330, pick=None):
    """プロパティ グリッドの選んだ行の「▼」を押して、開いたところを撮る。pick=(x,y) なら、その位置（ダイアログ左上から）をクリックする。"""
    r = dlg.rectangle(); dlg.set_focus()
    e = dlg.descendants(control_type='Edit')[0]; e.click_input(); time.sleep(0.5)
    cell = [b for b in dlg.descendants(control_type='Button') if b.window_text() == '開く' and b.rectangle().left - r.left > 1000][0]
    cell.click_input(); time.sleep(1.2)
    v.save(name, v.grab((r.left, r.top, r.right, r.top + box_h), front=False))
    if pick:
        from pywinauto import mouse
        mouse.click(coords=(r.left + pick[0], r.top + pick[1])); time.sleep(1.5)


def stage_includes(v):
    v.recover()
    dlg = open_props(v); resize(dlg, 1100, 700); r = dlg.rectangle()
    with v.step('props-cpp-standard'):
        v.tree_select(dlg, '構成プロパティ', 'C/C++', '言語')
        dlg.set_focus()
        from pywinauto import mouse
        mouse.click(coords=(r.left + 800, r.top + 222)); time.sleep(0.6)   # 「C++ 言語標準」の行
        cell = [b for b in dlg.descendants(control_type='Button') if b.window_text() == '開く' and b.rectangle().left - r.left > 1000][0]
        cell.click_input(); time.sleep(1.2)
        v.save('props-cpp-standard', v.grab((r.left, r.top + 180, r.right, r.top + 480), front=False))
        send_keys('{ESC}'); time.sleep(0.5)
    with v.step('include-edit'):
        v.tree_select(dlg, '構成プロパティ', 'C/C++', '全般')
        grid_dropdown(v, dlg, 'include-edit-menu', pick=(620, 110))
        d = v.dialog('追加のインクルード')
        v.shot_window('include-edit-dialog', d)
        for b in d.descendants(control_type='Button'):
            if b.window_text().startswith('マクロ'):
                b.click_input(); time.sleep(1.5); break
        v.shot_window('include-macros', v.dialog('追加のインクルード'))
    v.recover()


def open_main_cpp(v):
    v.key('^%l', wait=1.5)
    game = [c for c in v.descendants(control_type='TreeItem') if c.window_text() == 'Game'][0]
    try: game.expand()
    except Exception: pass
    time.sleep(0.8)
    f = [c for c in v.descendants(control_type='TreeItem') if c.window_text() == 'main.cpp'][0]
    f.double_click_input(); time.sleep(2)


def editor_zoom(v, percent=194):
    """エディターの倍率（左下の「100 %」）を変える。画像で文字が読めるように大きくする。"""
    z = [c for c in v.descendants(control_type='Edit') if re.search(r'^\d+ ?%$', c.window_text())]
    if z:
        z[0].click_input(); send_keys('^a' + str(percent) + '{ENTER}'); time.sleep(1)


def stage_debug(v):
    v.recover()
    with v.step('open main.cpp + breakpoint'):
        open_main_cpp(v)
        editor_zoom(v)
        from pywinauto import mouse
        mouse.click(coords=(700, 700)); time.sleep(0.4)
        send_keys('^+{F9}'); time.sleep(1.0)            # 前に置いたブレークポイントを全部消す
        if v.top_windows(): send_keys('{ENTER}'); time.sleep(0.6)   # 確認が出たら「はい」
        mouse.click(coords=(700, 700)); send_keys('^{HOME}'); send_keys('{DOWN 12}'); time.sleep(0.4)   # 13 行目へ
        send_keys('{F9}'); time.sleep(0.6)
    with v.step('start debugging'):
        send_keys('{F5}'); time.sleep(25)
    with v.step('debug-break'):
        v.shot_main('debug-break')
        v.shot_main('debug-toolbar', crop=(0, 30, 1100, 70))
    with v.step('debug-step'):
        send_keys('{F10}'); time.sleep(1); send_keys('{F10}'); time.sleep(1.5)
        v.shot_main('debug-step')
    with v.step('stop'):
        send_keys('+{F5}'); time.sleep(4)
    with v.step('first-toolbar'):
        v.shot_main('first-toolbar', crop=(0, 36, 810, 70))
    with v.step('output-window'):
        v.menu('表示', '出力'); time.sleep(1.5)
        v.shot_main('output-window', crop=(0, 760, 1560, 1000))
    with v.step('profiler-start'):
        v.key('%{F2}', wait=6)
        v.shot_main('profiler-start')
    v.recover()


def stage_errors(v):
    """C1083 と LNK2019 のエラー一覧。ソリューションごとに起動し直す。"""
    for name, sol in (('error-list-c1083', r'C:/vsshots\ErrC1083\ErrC1083.sln'), ('error-list-lnk2019', r'C:/vsshots\ErrLnk\ErrLnk.sln')):
        with v.step(name):
            kill(); v = launch(sol)
            open_main_cpp_generic(v)
            v.key('^+b', wait=30)
            v.key(r'^\e', wait=2)           # エラー一覧（Ctrl+\, E）
            v.shot_main(name)
    return v


def open_main_cpp_generic(v):
    v.key('^%l', wait=1.5)
    proj = [c for c in v.descendants(control_type='TreeItem') if c.window_text().startswith('Err')][0]
    try: proj.expand()
    except Exception: pass
    time.sleep(0.8)
    f = [c for c in v.descendants(control_type='TreeItem') if c.window_text() == 'main.cpp'][0]
    f.double_click_input(); time.sleep(3)


def stage_misc(v):
    v.recover()
    with v.step('options-text-editor'):
        v.menu('ツール', 'オプション...'); time.sleep(5)
        box = [c for c in v.descendants(control_type='TreeItem') if c.window_text() == 'テキスト エディター'][0]
        box.click_input(); time.sleep(1)
        try: box.expand()
        except Exception: pass
        time.sleep(1)
        sub = [c for c in v.descendants(control_type='TreeItem') if c.window_text() == '全般' and 30 < c.rectangle().left < 120 and c.rectangle().top > box.rectangle().top]
        if sub: sub[0].click_input(); time.sleep(1.5)
        v.shot_main('options-text-editor')
        from pywinauto import mouse
        mouse.click(coords=(900, 600)); send_keys('^{F4}'); time.sleep(1)
    with v.step('extensions-tabs'):
        v.menu('拡張機能', '拡張機能の管理...'); time.sleep(6)
        v.shot_main('extensions-tabs', crop=(0, 60, 900, 220))
        from pywinauto import mouse
        mouse.click(coords=(900, 600)); send_keys('^{F4}'); time.sleep(1)
    v.recover()


def stage_extra(v):
    """ツールセットのドロップダウンと、構成マネージャー。"""
    v.recover()
    dlg = open_props(v); resize(dlg, 1100, 700); r = dlg.rectangle()
    from pywinauto import mouse
    with v.step('props-toolset-dropdown'):
        v.tree_select(dlg, '構成プロパティ', '全般')
        dlg.set_focus()
        mouse.click(coords=(r.left + 800, r.top + 203)); time.sleep(0.6)
        cell = [b for b in dlg.descendants(control_type='Button') if b.window_text() == '開く' and b.rectangle().left - r.left > 1000][0]
        cell.click_input(); time.sleep(1.2)
        v.save('props-toolset-dropdown', v.grab((r.left, r.top + 150, r.right, r.top + 420), front=False))
        send_keys('{ESC}'); time.sleep(0.5)
    with v.step('config-manager'):
        b = [b for b in dlg.descendants(control_type='Button') if b.window_text().startswith('構成マネージャー')][0]
        b.click_input(); time.sleep(2)
        d = big_dialog_other(v, dlg)
        v.shot_window('config-manager', d)
    v.recover()

def big_dialog_other(v, dlg):
    for h, t in v.top_windows():
        if h != dlg.handle:
            w = D.window(handle=h).wrapper_object()
            if w.rectangle().width() > 300: return w
    raise KeyError('構成マネージャーがない')



def stage_cmake(v):
    kill(); v = launch(r'C:/vsshots\CMakeGame', wait=90); time.sleep(40)
    with v.step('cmake-folder'):
        v.shot_main('cmake-folder')
    with v.step('cmake-preset-dropdown'):
        cbs = [c for c in v.descendants(control_type='ComboBox') if 'x64' in c.window_text() or 'Debug' in c.window_text()]
        print('combos', [(c.window_text(), c.rectangle().left) for c in cbs])
        cbs[0].click_input(); time.sleep(1)
        v.shot_main('cmake-preset-dropdown', crop=(0, 25, 900, 200))
        v.esc(2)
    with v.step('cmake-build-menu'):
        v.recover(); v.menu('ビルド'); v.shot_menu('cmake-build-menu'); v.esc(2)
    with v.step('cmake-build-output'):
        v.key('^+b', wait=25)
        v.shot_main('cmake-build-output', crop=(0, 760, 1560, 1000))
    return v


STAGES = {'errors': stage_errors, 'misc': stage_misc, 'extra': stage_extra, 'cmake': stage_cmake, 'debug': stage_debug, 'includes': stage_includes, 'props': stage_props, 'menus': stage_menus, 'dialogs': stage_dialogs}

if __name__ == '__main__':
    v = VS.find()
    if not v: v = launch(GAME)
    for s in sys.argv[1:]:
        print('=== stage', s)
        r = STAGES[s](v)
        if r: v = r
    print('失敗した所:', __import__('vs_lib')._Step.failed)

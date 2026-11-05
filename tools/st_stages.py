"""st_shoot.py の続きの段階（マージ・コンフリクト・戻す・スタッシュ・タグ・メニュー類）。"""
import time

from st_lib import git, write


def texts(s, name):
    """本体の中の、見出しや項目の文字（Text）を、名前で探す。"""
    return [c for c in s.main().wrapper_object().descendants(control_type='Text')
            if c.window_text() == name]


def sidebar_item(s, name):
    """左のサイドバーの項目（いちばん左にあるもの）。"""
    return min(texts(s, name), key=lambda c: c.rectangle().left)


def menu_item(s, title_part):
    for c in s.main().wrapper_object().descendants(control_type='MenuItem'):
        if title_part in c.window_text():
            return c
    raise KeyError(title_part)


def history(s):
    s.click(s.main(), auto_id='SidebarHistoryItem', wait=1)


def close_overlays(s):
    while s.overlay():
        s.click(title='キャンセル', control_type='Button')
    s.main().type_keys('{ESC}')


def st_conflict(s, R):
    """別の人が main に push → フェッチ → main に移ってプル → マージで衝突 → 直す → コミット。"""
    me, fr = R / 'MyGame', R / 'Friend'
    close_overlays(s)
    git(fr, 'pull', '-q')
    write(fr / 'Player.cpp', '// プレイヤーの移動\nint speed = 6;\nint hp = 200;\n')
    git(fr, 'commit', '-qam', 'プレイヤーの HP を 200 に')
    git(fr, 'push', '-q')
    s.toolbar('ToolbarFetch')
    s.shot('st-fetch-dialog', 'top')
    s.click(title='OK', control_type='Button', wait=3)
    history(s)
    s.shot('st-history-fetched')
    sidebar_item(s, 'main').double_click_input()          # main に切り替える
    time.sleep(2)
    s.toolbar('ToolbarPull')
    s.click(title='プル', control_type='Button', wait=3)
    s.toolbar('ToolbarMerge')
    texts(s, 'feature/boss')[0].click_input()             # マージする枝を選ぶ
    time.sleep(0.5)
    s.shot('st-merge-dialog', 'top')
    s.click(title='OK', control_type='Button', wait=3)
    s.dialog()
    s.shot('st-conflict-dialog', 'top')
    s.recover()
    s.click(s.main(), auto_id='SidebarFileStatusItem', wait=1)
    s.shot('st-conflict-status')
    with s.step('競合のメニュー'):
        rows = s.main().wrapper_object().descendants(title='Player.cpp_Player.cpp', control_type='ListItem')
        rows[-1].right_click_input()
        time.sleep(0.8)
        menu_item(s, '競合').click_input()
        time.sleep(0.6)
        s.shot('st-conflict-menu', 'menu')
    s.recover()
    write(me / 'Player.cpp', '// プレイヤーの移動\nint speed = 6;\nint hp = 200;\n')   # 手で直した結果
    s.refresh()
    s.click(s.main(), auto_id='StageAll', wait=1)
    s.click(s.main(), auto_id='FileStatus_CommitButton', wait=2)
    history(s)
    s.shot('st-history-conflict-done')


def st_undo(s, R):
    """コミットの右クリック メニューと、リセットの画面。"""
    history(s)
    texts(s, 'プレイヤーの速度を 6 に変更')[0].right_click_input()
    time.sleep(0.6)
    s.shot('st-commit-menu', 'menu')
    menu_item(s, 'このコミットまでリセット').click_input()
    time.sleep(1)
    s.shot('st-reset-dialog', 'top')
    combo = [c for c in s.overlay().descendants(control_type='ComboBox')][-1]
    combo.click_input()
    time.sleep(0.6)
    s.shot('st-reset-modes', 'top', pad=40)
    s.main().type_keys('{ESC}')
    close_overlays(s)


def st_stash(s, R):
    """スタッシュに退避して、適用する。"""
    me = R / 'MyGame'
    write(me / 'Enemy.cpp', '// 敵の移動\nint enemySpeed = 5;\n')
    s.refresh()
    s.toolbar('ToolbarStash')
    s.shot('st-stash-dialog', 'top')
    box = s.overlay().descendants(control_type='Edit')[0]
    s.type_into(box, '敵の速度を試し中')
    s.shot('st-stash-dialog-named', 'top')
    s.click(title='OK', control_type='Button', wait=2)
    sidebar_item(s, 'スタッシュ').double_click_input()
    time.sleep(0.8)
    item = [c for c in s.main().wrapper_object().descendants(control_type='Text')
            if '敵の速度を試し中' in c.window_text()][0]
    item.right_click_input()
    time.sleep(0.6)
    s.shot('st-stash-menu', 'menu')
    menu_item(s, '適用').click_input()
    time.sleep(1)
    s.shot('st-stash-apply', 'top')
    s.click(title='OK', control_type='Button', wait=2)


def st_tag(s, R):
    """タグをつけて、リモートへ送る。"""
    s.toolbar('ToolbarTag')
    box = s.overlay().descendants(control_type='Edit')[0]
    s.type_into(box, 'v0.1')
    s.click(title='プッシュするタグ:', control_type='CheckBox')
    s.shot('st-tag-dialog', 'top')
    s.click(title='タグを追加', control_type='Button', wait=3)
    history(s)
    s.shot('st-history-tag')


def st_misc(s, R):
    """破棄・無視の確認、メニュー類、設定。1 つ失敗しても次へ進む。"""
    me = R / 'MyGame'
    git(me, 'checkout', '--', '.', check=False)
    write(me / 'Enemy.cpp', '// 敵の移動\nint enemySpeed = 9;\n')
    write(me / 'Memo.txt', 'メモ\n')
    s.recover()
    s.refresh()
    s.click(s.main(), auto_id='SidebarFileStatusItem', wait=1)

    def row(name):
        return s.main().wrapper_object().descendants(title=name + '_' + name, control_type='ListItem')[-1]

    with s.step('ファイルのメニューと破棄'):
        row('Enemy.cpp').right_click_input()
        time.sleep(1)
        s.shot('st-file-menu', 'menu')
        menu_item(s, 'ファイルの変更を破棄').click_input()
        time.sleep(1)
        s.shot('st-discard-confirm', 'top')
    s.recover()
    with s.step('無視'):
        row('Memo.txt').right_click_input()
        time.sleep(1)
        menu_item(s, '無視...').click_input()
        time.sleep(1.2)
        s.shot('st-ignore-dialog', 'top')
    s.recover()
    git(me, 'checkout', '--', '.', check=False)
    (me / 'Memo.txt').unlink(missing_ok=True)
    with s.step('検索'):
        s.click(s.main(), auto_id='SidebarSearchItem', wait=1)
        s.shot('st-search')
        history(s)
    with s.step('リポジトリ メニュー'):
        s.click(s.main(), auto_id='MenuRepository', wait=1)
        s.shot('st-repo-menu', 'menu')
    s.recover()
    with s.step('操作 メニュー'):
        s.click(s.main(), auto_id='MenuActions', wait=1)
        s.shot('st-actions-menu', 'menu')
    s.recover()
    with s.step('設定'):
        s.toolbar('ToolbarSettings')
        s.shot('st-remote-settings', 'top')
    s.recover()

"""docs/git/ の SourceTree 画像を、決まった手順で撮り直す。

使い方:
  python tools/st_shoot.py setup <ルート>      練習用のリポジトリ 3 つを作る（ルートは、まだ無いフォルダー）
  python tools/st_shoot.py run <ルート> [段階…]  撮影（段階を省くと全部）

練習用リポジトリ（ルート直下）:
  remote.git … 共有場所の役（bare）  MyGame … 自分  Friend … 別の人
段階は st_shoot.py の STAGES を見る。途中から撮り直せる。
"""
import sys
import time
from pathlib import Path

from st_lib import ST, git, write


def setup(root):
    root = Path(root)
    root.mkdir()
    git(root, 'init', '-q', '--bare', '-b', 'main', 'remote.git')
    for name, user in (('MyGame', ('Taro', 'taro@example.com')),
                       ('Friend', ('Hanako', 'hanako@example.com'))):
        git(root, 'clone', '-q', 'remote.git', name, check=False)
        git(root / name, 'config', 'user.name', user[0])
        git(root / name, 'config', 'user.email', user[1])
    me = root / 'MyGame'
    w = lambda n, t: (me / n).write_text(t, encoding='utf-8', newline='\n')
    w('Player.cpp', '// プレイヤーの移動\nint speed = 5;\nint hp = 100;\n')
    w('Enemy.cpp', '// 敵の移動\nint enemySpeed = 3;\n')
    w('.gitignore', '*.obj\n*.pdb\n.vs/\nx64/\n')
    git(me, 'add', '.')
    git(me, 'commit', '-qm', 'プレイヤーと敵の最初のコード')
    git(me, 'push', '-q', '-u', 'origin', 'main')
    w('Bullet.cpp', '// 弾\n')
    git(me, 'add', '.')
    git(me, 'commit', '-qm', '弾を追加')
    git(me, 'push', '-q')
    git(root / 'Friend', 'pull', '-q')
    print('作った:', root)


# ---------------------------------------------------------------- 段階

def st_tabs(s, R):
    """画面の見方・追加・クローン。"""
    s.place()
    s.click(s.main(), auto_id='SidebarHistoryItem')
    s.shot('st-history')
    s.toolbar('DefaultAddButton')
    s.main().child_window(auto_id='CloneRepoTab').wrapper_object().select()
    time.sleep(0.8)
    s.shot('st-clone')
    s.main().child_window(auto_id='AddRepoTab').wrapper_object().select()
    time.sleep(0.8)
    s.shot('st-add-repo')
    s.click(s.main(), auto_id='CloseButton')  # 新しいタブを閉じる


def st_commit(s, R):
    """変更 → ステージ → コミット。"""
    me = R / 'MyGame'
    write(me / 'Player.cpp', '// プレイヤーの移動\nint speed = 6;\nint hp = 100;\n')
    write(me / 'Boss.cpp', '// ボス\nint bossHp = 500;\n')
    write(me / 'test.obj', 'x')            # .gitignore で無視されるので出てこない
    s.click(s.main(), auto_id='SidebarFileStatusItem', wait=1)
    s.refresh()
    s.shot('st-status-unstaged')
    s.main().child_window(title='Player.cpp_Player.cpp', control_type='ListItem').click_input()
    s.click(s.main(), auto_id='StageSelected')
    time.sleep(0.5)
    s.main().child_window(title='Player.cpp_Player.cpp', control_type='ListItem').click_input()
    s.shot('st-status-staged')
    box = s.main().child_window(auto_id='CommitTextBox').wrapper_object()
    s.type_into(box, 'プレイヤーの速度を 6 に変更')
    s.shot('st-commit-message')
    s.click(s.main(), auto_id='FileStatus_CommitButton', wait=1.5)


def st_push(s, R):
    """別の人が先に push → プッシュが拒否される → プルして合体 → プッシュ。"""
    fr = R / 'Friend'
    write(fr / 'Enemy.cpp', '// 敵の移動\nint enemySpeed = 4;\n')
    git(fr, 'commit', '-qam', '敵の速度を 4 に変更')
    git(fr, 'push', '-q')
    s.toolbar('ToolbarPush')
    s.shot('st-push-dialog', 'top')
    s.click(title='プッシュ', control_type='Button', wait=3)
    s.shot('st-push-rejected', 'top')
    s.click(title='閉じる', control_type='Button')
    s.click(title='キャンセル', control_type='Button')   # 失敗すると、プッシュの画面がもう一度出る
    s.toolbar('ToolbarPull')
    s.shot('st-pull-dialog', 'top')
    s.click(title='プル', control_type='Button', wait=3)
    s.click(s.main(), auto_id='SidebarHistoryItem', wait=1)
    s.shot('st-history-merge')
    s.toolbar('ToolbarPush')
    s.click(title='プッシュ', control_type='Button', wait=3)


def st_branch(s, R):
    """ブランチを作る。サイドバーの右クリック メニュー。"""
    me = R / 'MyGame'
    s.click(title='キャンセル', control_type='Button') if s.overlay() else None
    s.toolbar('ToolbarBranch')
    box = s.main().child_window(auto_id='BranchNameField').wrapper_object()
    s.type_into(box, 'feature/boss')
    s.shot('st-branch-dialog', 'top')
    s.click(title='ブランチを作成', control_type='Button', wait=1.5)
    s.click(s.main(), auto_id='SidebarHistoryItem', wait=1)
    s.shot('st-branch-created')
    # 変更をコミットしておく（あとのマージで使う）
    git(me, 'add', 'Boss.cpp')
    git(me, 'commit', '-qm', 'ボスを追加')
    write(me / 'Player.cpp', '// プレイヤーの移動\nint speed = 6;\nint hp = 150;\n')
    git(me, 'commit', '-qam', 'プレイヤーの HP を 150 に')
    s.refresh()


STAGES = {'tabs': st_tabs, 'commit': st_commit, 'push': st_push, 'branch': st_branch}
from st_stages import st_conflict, st_undo, st_stash, st_tag, st_misc  # noqa: E402
STAGES.update(conflict=st_conflict, undo=st_undo, stash=st_stash, tag=st_tag, misc=st_misc)


def close_tabs(s):
    """開いているリポジトリのタブを、全部閉じる。"""
    for _ in range(6):
        try:
            s.click(s.main(), auto_id='CloseButton', wait=0.8)
        except Exception:
            break
        if not s.main().child_window(auto_id='ToolbarCommit').exists(timeout=0.5):
            break


def run(root, names):
    R = Path(root)
    s = ST()
    if not names or names[0] == 'tabs':
        close_tabs(s)
        s.open_repo(R / 'MyGame')
    for n in names or STAGES:
        print('==', n)
        with s.step('段階 ' + n):
            STAGES[n](s, R)
    from st_lib import _Step
    print('失敗した所:', _Step.failed or 'なし')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'setup':
        setup(sys.argv[2])
    elif cmd == 'run':
        run(sys.argv[2], sys.argv[3:])

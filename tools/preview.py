"""指定したページだけをビルドして、すぐに見られるプレビューを起動する。

全ページ（約 2400）のビルドは 90 秒かかるが、数ページなら数秒で済む。
除外したページへのリンクは切れる（警告は出るが、プレビューには影響しない）。

使い方:
    python tools/preview.py docs/graphics/shadows/cascaded.md
    python tools/preview.py docs/graphics/shadows          # フォルダー内のすべて
    python tools/preview.py docs/stl/containers/vector.md docs/stl/containers/map.md

保存すると、自動で再ビルドしてブラウザーが更新される。止めるときは Ctrl+C。
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8124   # 通常のプレビュー（serve.bat、8123）と同時に起動できる


def changed_pages():
    """未コミットの変更と、直前のコミットで触った docs の .md（削除は除く）。"""
    out = set()
    for cmd in (['git', 'diff', '--name-only', '--diff-filter=d', 'HEAD'],
                ['git', 'diff', '--name-only', '--diff-filter=d', 'HEAD~1', 'HEAD'],
                ['git', 'ls-files', '--others', '--exclude-standard']):
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        out.update(l for l in r.stdout.splitlines() if l.startswith('docs/') and l.endswith('.md'))
    return sorted(p for p in out if os.path.exists(os.path.join(ROOT, p)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    args = [a for a in sys.argv[1:] if a != '--no-open']
    no_open = len(args) != len(sys.argv) - 1
    if '--changed' in args:
        args = changed_pages()
        if not args:
            print('変更したページがありません')
            return 1
        print('対象: %d ページ' % len(args))
    keep = []
    for arg in args:
        p = os.path.relpath(os.path.abspath(arg), os.path.join(ROOT, 'docs')).replace('\\', '/')
        if p.startswith('..'):
            print('docs の外です: ' + arg)
            return 1
        keep.append(p.rstrip('/'))
    # 全ての .md を除外し、指定したものだけ戻す（.md 以外の画像・JS・CSS は残る）
    lines = ['_template.md', '**/*.md', '!/index.md']
    for p in keep:
        full = os.path.join(ROOT, 'docs', p)
        lines.append('!/' + p + ('/**/*.md' if os.path.isdir(full) else ''))
        if os.path.isdir(full):
            lines.append('!/' + p + '/*.md')
    cfg = os.path.join(ROOT, 'mkdocs.preview.yml')
    with open(cfg, 'w', encoding='utf-8', newline='\n') as f:
        f.write('INHERIT: mkdocs.yml\n')
        f.write('site_dir: site-preview\n')
        # 除外したページを .pages が指していても、エラーにしない
        f.write('plugins:\n  - awesome-pages:\n      strict: false\n  - tags\n')
        f.write('exclude_docs: |\n')
        for l in lines:
            f.write('  ' + l + '\n')
    url = 'http://127.0.0.1:%d/kdocs/%s' % (PORT, keep[0][:-3] + '/' if keep[0].endswith('.md') else keep[0] + '/')
    print('プレビュー: ' + url)
    exe = os.path.join(ROOT, '.venv', 'Scripts', 'mkdocs.exe')
    return 0 if os.environ.get('GEN_ONLY') else subprocess.call([exe, 'serve', '-f', cfg, '-a', '127.0.0.1:%d' % PORT] + ([] if no_open else ['--open']), cwd=ROOT)


if __name__ == '__main__':
    sys.exit(main())

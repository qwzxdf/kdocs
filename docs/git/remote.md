---
title: リモートと push・pull・fetch
tags:
  - Git
---

# リモートと push・pull・fetch

ここまでの話は、全部、自分のパソコンの中で完結していました。チームで作る、バックアップを取る、別のパソコンでも作業する。こうした場面では、GitHub などの共有場所（リモート）と記録をやり取りします。

やり取りのコマンドは `clone`、`push`、`fetch`、`pull` の 4 つです。名前は似ていますが、それぞれ役割が違います。`fetch` と `pull` の違いが分かれば、「リモートの変更が、いつ手元に来るのか」が自分で説明できるようになります。

!!! tip "ポイント"
    - `push` するまで、他人には何も見えない。`fetch` / `pull` するまで、他人の変更は手元に来ない
    - `fetch` は持ってくるだけ。`pull` は、持ってきて合体する
    - 作業を始める前に `pull`、終わったら `push` の習慣にすると、事故が減る
    - push が `rejected` で失敗したら、`--force` で押し切らず、先に `pull` で取り込む

!!! info "このページを読む前に"
    - [Git の考え方](concepts.md#remote)（ローカルとリモート）
    - [ブランチ](branch.md)
    - [GitHub を使う](github.md)（リモートの置き場所と認証）

## リモートを登録する {#add}

リモートは、名前と URL の組で登録します。ふつうの名前は <strong>`origin`</strong> です。

```bash
git remote add origin https://github.com/ユーザー名/MyGame.git
git remote -v                     # 登録されているリモートを見る
```

```text title="実行結果"
origin	https://github.com/ユーザー名/MyGame.git (fetch)
origin	https://github.com/ユーザー名/MyGame.git (push)
```

`origin` は、ただの名前です。後で複数のリモートを持つこともできますが、最初は 1 つで十分です。(`clone` したときは、自動で `origin` が登録されます。)

## clone：リモートから持ってくる {#clone}

すでにあるプロジェクトを手元に持ってくるには、`git clone` を使います。

```bash
git clone https://github.com/ユーザー名/MyGame.git
git clone https://github.com/ユーザー名/MyGame.git MyGame2   # フォルダー名を指定
```

履歴を丸ごと取ってきて、フォルダーを作り、`origin` を登録し、`main` を作業フォルダーに展開します。

履歴が長いリポジトリや、巨大なファイルが入っているリポジトリでは、時間がかかります。最新の状態だけでよければ、浅く取ることができます。

```bash
git clone --depth 1 https://github.com/ユーザー名/MyGame.git   # 最新のコミットだけ
```

浅い clone は速いのですが、履歴が無いので、過去を調べる、枝を切って戻る、といった操作は制限されます。サイトのライブラリを取るだけ、ビルドして動かすだけ、というときに向いています。

## push：自分の記録を送る {#push}

`git push` は、ローカルのコミットをリモートへ送ります。

```bash
git push -u origin main           # 最初の 1 回
git push                          # 2 回目以降
```

`-u` は「今後、この枝は `origin/main` と組にする」という指定です。最初の 1 回だけ付ければ、次からは `git push` だけで済みます。`push.autoSetupRemote` を設定していれば（[最初の設定](install.md#useful)）、`-u` を忘れても大丈夫です。

<strong>push するまでは、他人には何も見えません。</strong>ローカルでコミットを積んで、満足したら push します。逆に、push は「共有する」行為なので、中途半端な状態は送らないようにしてください。

新しい枝を作って push するときは、その枝の名前で送ります。

```bash
git switch -c feature/enemy
# …コミット…
git push -u origin feature/enemy
```

## fetch：持ってくるだけ {#fetch}

`git fetch` は、リモートの新しいコミットを、手元に<strong>持ってくるだけ</strong>です。作業フォルダーや、いまの枝には触れません。

```bash
git fetch                         # origin の変更を持ってくる
git fetch --all                   # 全部のリモート
git fetch --prune                 # リモートで消された枝の記録も、手元から消す
```

持ってきたコミットは、`origin/main` のような、リモートの様子を記録した名札に入ります。これは「最後に fetch した時点の、リモートの `main`」を指す、読み取り専用の札です。自分の `main` とは別物です。

```bash
git log --oneline main..origin/main   # 手元の main にまだ無い、リモートのコミット
git diff main origin/main             # 差を見る
```

`fetch` してから眺めると、<strong>他人が何をしたかを確かめてから</strong>、取り込むかどうか決められます。作業フォルダーを壊さないので、いつ打っても安全です。

## pull：持ってきて、合体する {#pull}

`git pull` は、`fetch` と `merge` を続けて実行します。

```bash
git pull                          # = git fetch + git merge origin/main
```

リモートの新しいコミットを取り込んで、いまの枝に合体します。作業を始める前に必ず 1 回実行する習慣を付けると、他の人の変更を知らずに作業を進めてしまう事故が減ります。

pull の最中にコンフリクトが起きることがあります。対処はマージのときと同じです。[コンフリクト](conflict.md) を見てください。

`pull.rebase` を設定していない状態で `git pull` すると、Git が方針を決めるよう警告することがあります。最初は、`git config --global pull.rebase false`（マージを使う）にしておけば迷いません。

### fetch と pull の使い分け {#fetch-vs-pull}

`pull` は便利ですが、勝手に合体してしまいます。次の場面では `fetch` のほうが向いています。

- 作業の途中で、変更が溜まっていて、いま合体したくない
- 他人が何を push したか、先に眺めたい
- コンフリクトが起きそうで、心の準備がしたい

それ以外の、毎日の始めには `pull` で構いません。

## push が拒否されたとき {#rejected}

次のようなエラーが出ることがあります。

```text title="push が拒否されたとき"
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally.
```

リモートに、自分がまだ持っていないコミットがある、という意味です。他の人が先に push しています。

対処は、<strong>先に取り込んでから、もう一度 push</strong> です。

```bash
git pull                          # 他の人のコミットを取り込む
git push                          # もう一度送る
```

慌てて `git push --force` を使うと、他の人のコミットがリモートから消えます。共有している枝（特に `main`）では使いません。詳しくは [事故と対処](accidents.md#force) にあります。

## 枝の追跡と状態 {#tracking}

`git status` の最初に、リモートとの関係が出ます。

```text title="git status の最初の部分"
On branch main
Your branch is ahead of 'origin/main' by 2 commits.
  (use "git push" to publish your local commits)
```

| 表示 | 意味 | 次にすること |
| --- | --- | --- |
| `ahead of ... by N commits` | 手元に、まだ push していないコミットが N 個ある | `git push` |
| `behind ... by N commits` | リモートに、まだ取り込んでいないコミットが N 個ある | `git pull` |
| `have diverged` | 両方に別のコミットがある | `git pull`（マージが必要） |
| `up to date` | 同じ | なにもしない |

この表示は、<strong>最後に fetch した時点の情報</strong>で出ます。最新を知りたいなら、先に `git fetch` します。

## リモートの枝を消す・使う {#remote-branch}

リモートにある枝は、別の枝として手元にも取れます。

```bash
git switch feature/ui             # リモートにだけある枝に移る（自動で追跡する枝を作る）
git push origin --delete feature/enemy   # リモートの枝を消す
```

PR が終わった枝は、リモートからも消しておくと、枝の一覧がすっきりします。GitHub の PR 画面には、マージ後に枝を消すボタンがあります。

## ゲームの制作で効く習慣 {#game}

- 一日の始めに `git pull`、終わりに `git push`。作業の区切りごとに送ると、パソコンが壊れても失うのは 1 日分以内で済む
- 大きなアセットを push するときは、時間がかかる。[Git LFS](git-lfs.md) を使っているか確かめる
- 作業中の枝も push しておくと、バックアップになる。他人に見せたくなければ、非公開のリポジトリを使う

## よくあるミス {#mistakes}

??? failure "コミットしたのに、他の人に見えない"
    `push` していません。ローカルのコミットは、push するまで共有されません。`git status` の `ahead` で確かめられます。

??? failure "`git pull` で、予期しないマージコミットができた"
    手元とリモートの両方が進んでいたためです。`git pull` が `fetch` + `merge` だと知っていれば、驚きません。履歴をきれいにしたければ `pull --rebase` を使えますが、[rebase](rebase.md) の注意を読んでからにしてください。

??? failure "`git push --force` で、他の人のコミットを消した"
    `--force` は、リモートの履歴を自分のもので上書きします。共有している枝には使いません。どうしても必要なら、安全側の `--force-with-lease` を使い、事前に相手へ伝えます。

## これだけ覚える {#summary}

- 一日の流れは `pull` → 作業 → `commit` → `push`
- `fetch` は持ってくるだけ、`pull` は持ってきて合体する
- push が拒否されたら、先に `pull`
- `--force` は共有の枝に使わない

## 関連ページ {#related}

- [GitHub を使う](github.md)
- [ブランチ](branch.md)
- [事故と対処](accidents.md)

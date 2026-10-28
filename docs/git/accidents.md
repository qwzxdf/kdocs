---
title: 事故と対処（detached HEAD・force push・巨大ファイル）
tags:
  - Git
---

# 事故と対処（detached HEAD・force push・巨大ファイル）

Git を使っていると、一度は「やってしまった」という場面に出会います。大半の事故は、落ち着いて手順を踏めば直せます。Git はコミットした内容をなかなか手放さないので、「消えたように見える」だけで、実は残っていることも多いのです。

このページは、初心者がよく遭遇する事故を、症状から引けるように並べました。画面ツール（Visual Studio、SourceTree、GitHub Desktop）でも、起きることは同じです。

!!! tip "ポイント"
    - 事故が起きたら、まず操作を止めて、`git status` と `git log` で状況を見る
    - コミットしてあれば、`git reflog` でほぼ取り戻せる。コミットしていない変更は戻らない
    - 共有している枝への `force push` は、他人のコミットを消す。避ける
    - パスワードや API キーを push したら、まずそのキーを無効にする。履歴を消すのは、その後

!!! info "このページを読む前に"
    - [取り消す・戻す](undo.md)（restore・reset・revert・reflog）
    - [リモートと push・pull・fetch](remote.md)

## detached HEAD になった {#detached}

症状は、`git status` や画面の枝名の位置に、枝の名前ではなくコミットの ID が出ることです。

```text title="git status の表示"
HEAD detached at 596e68a
nothing to commit, working tree clean
```

履歴のコミットや、タグを指定して移ると、どの枝にもいない状態になります。眺めるだけなら問題ありません。ただし、<strong>この状態でコミットすると、枝に戻ったときにそのコミットを見失います</strong>。

その場で枝を作れば、コミットに名前が付いて残ります。

```bash
git switch -c fix/old-bug         # 新しい枝を作って、いまの場所を名付ける
```

何もコミットしていなければ、元の枝に戻るだけです。

```bash
git switch main
```

すでに枝に戻ってコミットを見失ったら、`git reflog` で ID を探して、`git switch -c 枝名 <ID>` で救えます。

## force push で他人のコミットを消した {#force}

push が拒否されたとき、次のように「強制してしまえ」と思いがちです。

```bash
git push --force                  # 使わない
```

`--force` は、リモートの履歴を、自分の手元の履歴で<strong>上書き</strong>します。リモートにだけあった他人のコミットは、リモートから消えます。画面ツールで「強制プッシュしますか」と聞かれたときも、同じ操作です。

push が拒否されるのは、リモートに自分が持っていないコミットがあるという合図です。正しい直し方は、取り込んでから push することです。

```bash
git pull                          # 他の人のコミットを取り込む
git push
```

共有している枝（特に `main`）では、`--force` を使いません。履歴を書き換えたあと（`rebase`、`amend`）に、自分だけが使っている枝を push し直すときだけ、安全側の版を使います。

```bash
git push --force-with-lease       # 自分が最後に見たあと、他人が push していたら失敗する
```

`--force-with-lease` は、強制のうちで、他人の push を踏みつぶさないための確認が付いた版です。それでも、チームで共有している枝には、使わないでください。

すでに force push してしまったら、消えたコミットを持っている人（push した本人や、最後に pull した人）の手元に残っています。その人に `git push` してもらえば、元に戻せます。GitHub では、Pull Request の履歴や、リモートの reflog が残ることもあります。まず、起きたことをチームに伝えてください。

## 巨大ファイルをコミットした {#bigfile}

100 MB を超えるファイルは、GitHub が受け付けません。push が失敗します。しかも、コミットした時点で、履歴に入っています。ファイルを消して別のコミットを作っても、履歴の中には残るので、push は失敗し続けます。

```text title="push 失敗時のメッセージの例"
remote: error: File Assets/bgm.wav is 134.20 MB; this exceeds GitHub's file size limit of 100.00 MB
```

<strong>まだ push していない</strong>、かつ、そのコミットが直前の 1 つなら、コミットを取り消してやり直せます。

```bash
git reset --soft HEAD~1           # 直前のコミットを取り消す（変更はステージに残る）
git restore --staged Assets/bgm.wav   # 大きなファイルをステージから外す
# .gitignore に追加するか、Git LFS の対象にする
git commit -m "..."               # やり直す
```

コミットが複数前にあるなら、`HEAD~3` のように、巨大ファイルを含む最初のコミットの手前まで戻します。

すでに push 済み（または、複数のコミットに混ざっている）場合は、履歴からの削除が必要です。専用のツール（`git filter-repo` など）を使い、履歴を書き換えてから force push します。共有している履歴を書き換える難しい操作なので、チームの全員に伝え、全員が作り直した履歴を取り込み直す必要があります。個人のリポジトリで、作り直しても困らないなら、<strong>リポジトリを新しく作り直す</strong>のが現実的です。

大きなファイルを今後も扱うなら、[Git LFS](git-lfs.md) を使います。track してから add するのが決まりです。

## パスワードや API キーをコミットした {#secret}

APIキー、パスワード、トークンをコミットして push してしまったとき、最初にすることは<strong>履歴の削除ではありません</strong>。

1. <strong>そのキーを無効にして、作り直す</strong>。GitHub の Public リポジトリは、push の数分後には、自動で漁るボットに見つかります。ファイルを消しても、履歴から読めます
2. 作り直したキーを、コードに書かず、環境変数や、`.gitignore` に入れた設定ファイルから読む
3. 必要なら、履歴からも削除する（`git filter-repo` など）

キーを無効にすれば、漏れた古いキーは使えなくなるので、被害を止められます。履歴の書き換えは、その後の整理です。

防ぐには、秘密を含むファイルを最初から `.gitignore` に入れておき、設定の例（`config.sample.json`）だけをコミットします。[.gitignore](gitignore.md) を見てください。

## 違う枝にコミットした {#wrong-branch}

`main` で作業するつもりが、`feature` にコミットしていた、あるいは逆の事故です。

push 前なら、直せます。

```bash
git switch correct-branch         # 正しい枝へ移る
git cherry-pick a3f9c21           # 間違えた枝のコミットを持ってくる
git switch wrong-branch
git reset --hard HEAD~1           # 間違えた枝のコミットを取り消す
```

先に正しい枝にコミットを持ってきてから、元を消すのが順序です。逆にすると、ID を見失います。見失ったら `git reflog` で探せます。

## コンフリクトで混乱した {#conflict-panic}

マージ中のコンフリクトで頭が混乱したら、無理に直さず、始める前に戻ります。

```bash
git merge --abort                 # マージ前に戻る
git rebase --abort                # rebase 前に戻る
```

これは、マージやリベースを始める前の状態に、きれいに戻す安全な逃げ道です。直し方は [コンフリクト](conflict.md) にあります。

## 変更を消してしまった {#lost}

状況によって、戻せるかが変わります。

| 状況 | 戻せるか |
| --- | --- |
| コミット済みのものを `reset --hard` した | `git reflog` で戻せる |
| 枝を `-D` で消した | `git reflog` で ID を探して、枝を作り直せる |
| `stash` を drop / clear した | 一時的に残っていることがある（`git fsck --lost-found`）が、期待しない |
| コミットしていない変更を `restore` / `reset --hard` した | Git では戻せない。エディターの履歴機能を探す |

最後の行が重要です。<strong>コミットしていない変更は、Git にも残りません。</strong>危ない操作の前にはコミットする、という習慣が、一番の保険です。

Visual Studio には「ローカル履歴」の機能があり、保存したファイルの過去の内容を、拡張機能で残せる場合があります。Windows の「以前のバージョン」も、有効にしていれば使えます。

## 事故を避けるための習慣 {#habits}

- 危ない操作（`reset --hard`、`restore`、`clean`、`--force`）の前に、`git status` で状況を見る
- 大きな操作の前には、いったんコミットする。うまくいかなければ、そこへ戻れる
- 共有している枝の履歴は書き換えない（`amend`、`rebase`、`reset` は push 前の枝だけ）
- `git add .` のあとは、`git status` で何が入ったか確かめる
- 画面ツールでも、押す前に枝の名前を見る

## これだけ覚える {#summary}

- 慌てずに `git status` と `git log` を見る
- コミットがあれば、`reflog` で取り戻せる
- 共有している枝に `--force` は使わない
- 秘密を push したら、まずキーを無効にする
- 巨大ファイルは push 前なら `reset --soft`、後なら履歴の書き換えが必要

## 関連ページ {#related}

- [取り消す・戻す](undo.md)
- [Git LFS](git-lfs.md)
- [.gitignore](gitignore.md)

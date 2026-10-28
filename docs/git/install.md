---
title: インストールと最初の設定
tags:
  - Git
---

# インストールと最初の設定

Git は、入れただけでは使い始められません。コミットには「誰が作ったか」が必ず付くので、名前とメールアドレスを先に教える必要があります。さらに Windows では、改行コードの扱いを決めておかないと、あとで「全行が変更されたことになる」という困った差分に悩まされます。

このページは、インストールから、最初に 1 回だけ行う設定までを順に説明します。設定は一度済ませれば、新しいリポジトリでも使い回せます。

!!! tip "ポイント"
    - Visual Studio のインストーラーにも Git は入っている。ただし、コマンドを使うなら Git for Windows を別に入れておくと分かりやすい
    - 最初の 1 回は、`user.name` と `user.email` を必ず設定する。これが無いとコミットできない
    - 設定は 3 段階（システム、ユーザー、リポジトリ）。ふつうはユーザー全体（`--global`）に書く
    - GitHub に載せるなら、認証の方法（Git Credential Manager か SSH）も決めておく

!!! info "このページを読む前に"
    - [Git の考え方](concepts.md)（用語と 3 つの場所）

## インストール {#install}

Windows には、Git for Windows を使います。公式サイト（git-scm.com）からインストーラーを入れる方法のほかに、`winget` でも入ります。

```bash
winget install --id Git.Git -e
```

インストーラーは質問が多いのですが、ほとんど既定のままで構いません。次の項目だけは意味を知っておいてください。

<strong>既定のエディター</strong>は、`git commit` でメッセージを書くときに開くエディターです。既定では Vim が選ばれていて、Vim の操作を知らないと閉じ方が分からなくなります。Visual Studio Code や Notepad++ など、使い慣れたものを選んでください。あとから `git config --global core.editor` で変えられます。

<strong>改行コードの扱い</strong>は、「Checkout Windows-style, commit Unix-style」（`core.autocrlf=true`）が既定です。後述のとおり、本格的に使うなら `.gitattributes` に任せるほうが確実です。

<strong>既定のブランチ名</strong>は、`main` を選びます。古い資料では `master` が出てきますが、いまの GitHub は `main` が標準です。

<strong>PATH の設定</strong>は、「Git from the command line and also from 3rd-party software」を選びます。これで、PowerShell やコマンド プロンプト、Visual Studio から `git` が呼べます。

インストールしたら、新しいターミナルを開いて、次のコマンドで確認します。

```bash
git --version
```

```text title="実行結果（バージョンは環境によって違う）"
git version 2.55.0.windows.5
```

バージョンが表示されれば成功です。

## 名前とメールアドレス {#user}

最初に、コミットに付く作者の情報を設定します。

```bash
git config --global user.name "Taro Yamada"
git config --global user.email "taro@example.com"
```

`--global` は「このパソコンのこのユーザー全体に有効」という意味です。これを付けないと、いまいるリポジトリだけに設定されます。

メールアドレスは、GitHub に登録したものと同じにしてください。違うアドレスでコミットすると、GitHub 上で「誰のコミットか」が結び付かず、自分の貢献として数えられません。メールアドレスを公開したくないときは、GitHub の設定で用意されている noreply アドレス（`12345678+name@users.noreply.github.com` の形）を使えます。

設定は、次のコマンドでまとめて確認できます。

```bash
git config --global --list
```

## 設定の 3 段階 {#levels}

設定は、どこに書くかで効く範囲が変わります。範囲が狭いほうが優先されます。

| 範囲 | オプション | 保存先 |
| --- | --- | --- |
| システム全体 | `--system` | Git のインストール先の `etc/gitconfig` |
| ユーザー全体 | `--global` | `C:\Users\<名前>\.gitconfig` |
| そのリポジトリだけ | （なし） | リポジトリ内の `.git/config` |

ふつうは `--global` に書きます。「このリポジトリだけ、会社のメールアドレスを使いたい」のような場合に、リポジトリの中で `--global` を付けずに設定します。

## 入れておくと便利な設定 {#useful}

次の設定は、必須ではありませんが、入れておくと事故が減ります。

```bash
git config --global init.defaultBranch main
git config --global core.editor "code --wait"
git config --global pull.rebase false
git config --global fetch.prune true
git config --global push.autoSetupRemote true
```

`init.defaultBranch` は、`git init` で作るリポジトリの最初の枝の名前です。`core.editor` に `code --wait` を指定すると、メッセージの入力に Visual Studio Code が使えます。`--wait` は、エディターを閉じるまで Git を待たせるために必要です。

`pull.rebase false` は、`git pull` を「取り込み → マージ」として動かす設定です。Git は、設定が無いと pull のたびに警告を出すので、決めておくと静かになります。`fetch.prune true` は、リモートで消された枝の記録を、手元からも自動で消します。`push.autoSetupRemote true` は、新しい枝を最初に push するとき、`-u` を付け忘れても自動で上流を設定してくれます。

## 改行コードの問題 {#eol}

Windows の改行は CRLF、Linux と macOS は LF です。チームに両方の人がいると、同じファイルの全行が「変更された」と表示される事故が起きます。

一番確実なのは、リポジトリに `.gitattributes` を置いて、改行の扱いをファイルごとに決めてしまうことです。

```text title=".gitattributes"
* text=auto
*.cpp text eol=lf
*.h   text eol=lf
*.sln text eol=crlf
*.bat text eol=crlf
```

`* text=auto` は、テキストファイルかどうかを Git が判断して、リポジトリ内では LF にそろえる指定です。ただし、Visual Studio のソリューション（`.sln`）やバッチ ファイル（`.bat`）は CRLF のほうが安全なので、個別に指定しています。詳しくは [.editorconfig](../vs/editorconfig.md) と [文字コードを UTF-8 にしよう](../vs/utf8.md) を参照してください。

## GitHub との認証 {#auth}

GitHub のリポジトリに push するとき、パスワードの入力を求められます。いまの GitHub は、パスワードでの認証を受け付けず、次のどちらかを使います。

<strong>Git Credential Manager</strong> は、Git for Windows に同梱されています。初めて push や clone をするとブラウザーが開き、GitHub にサインインすると、認証情報が Windows の資格情報マネージャーに保存されます。次からは入力が要りません。<strong>学生の最初の 1 本としては、これが一番楽です。</strong>

<strong>SSH 鍵</strong>は、パスワードの代わりに、鍵のペアで認証する方法です。パソコンで鍵を作って、公開鍵を GitHub に登録します。

```bash
ssh-keygen -t ed25519 -C "taro@example.com"
```

作られた `~/.ssh/id_ed25519.pub` の中身を、GitHub の「Settings → SSH and GPG keys」に貼り付けます。以後は、リポジトリの URL を `https://...` ではなく `git@github.com:ユーザー名/MyGame.git` の形にして使います。秘密鍵（`id_ed25519`、`.pub` が付かないほう）は、誰にも渡さないでください。

どちらを選んでも、中身の Git の使い方は変わりません。認証の詳しい話は [GitHub を使う](github.md#auth) にもあります。

## よくあるミス {#mistakes}

??? failure "`Please tell me who you are` と出てコミットできない"
    `user.name` と `user.email` が未設定です。上の手順で設定してから、もう一度コミットします。

??? failure "メッセージ入力で Vim が開いて、閉じ方が分からない"
    Vim の画面なら、`Esc` を押して `:wq` と打って Enter でメッセージを保存して閉じます。保存せずに閉じるなら `:q!` です。あとで `core.editor` を使い慣れたエディターにしてください。

??? failure "メールアドレスが GitHub のものと違い、貢献として数えられない"
    すでにあるコミットのアドレスは、あとからは簡単に直せません。これからのコミットのために、`user.email` を直してください。

## これだけ覚える {#summary}

- 最初に `user.name` と `user.email` を設定する
- 設定はふつう `--global` に書く
- 改行の扱いは `.gitattributes` に任せる
- GitHub への認証は、Git Credential Manager が楽

## 関連ページ {#related}

- [Git の考え方](concepts.md)
- [記録する（add と commit）](commit.md)
- [GitHub を使う](github.md)

---
title: .gitignore（記録しないファイルを決める）
tags:
  - Git
---

# .gitignore（記録しないファイルを決める）

ゲームのプロジェクトをビルドすると、`x64/` や `.vs/` のような、ビルドが作ったファイルが大量にできます。これらを Git に入れると、数百 MB になることもありますし、他の人の環境では意味がありません。しかも、ビルドのたびに中身が変わるので、`git status` が毎回、大量の変更で埋まります。

「ここは管理しない」と決める仕組みが `.gitignore` です。最初のコミットの前に置くのがコツで、あとから入れると、すでに記録されたファイルには効かないという落とし穴があります。

!!! tip "ポイント"
    - `.gitignore` は、リポジトリ直下に置く普通のテキストファイル。これ自体はコミットして共有する
    - 入れるのは、ビルドの出力、個人の設定、一時ファイル、パスワードを含むファイル
    - すでにコミットしたファイルには効かない。`git rm --cached` で追跡だけを外す
    - 最初のコミットの前に置く

!!! info "このページを読む前に"
    - [記録する（status・add・commit）](commit.md)

## 基本の書き方 {#basic}

`.gitignore` の各行は、管理しないファイルやフォルダーを指す、パターンです。

```gitignore
# Visual Studio
.vs/
*.user
*.suo

# ビルドの出力
x64/
Debug/
Release/
out/
build/

# vcpkg
vcpkg_installed/
```

`#` で始まる行はコメントです。空行は無視されます。

| パターン | 意味 |
| --- | --- |
| `x64/` | 末尾が `/` なら、その名前のフォルダー（どの階層にあっても） |
| `*.user` | `*` は任意の文字列。拡張子が `.user` のファイル全部 |
| `/build` | 先頭が `/` なら、`.gitignore` と同じ階層の `build` だけ |
| `docs/*.tmp` | 特定のフォルダーの中だけ |
| `<strong>/temp` | どの階層の `temp` にも一致（`</strong>` は階層をまたぐ） |
| `!important.user` | `!` で始めると、除外から外す（例外にする） |

`/` で始まるかどうかで、範囲が変わります。`build/` と書くと、どの階層の `build` フォルダーも対象で、`/build/` と書くとリポジトリ直下の `build` だけです。プロジェクトの中に `third_party/lib/build/` のような別物があるときは、意図に合わせて選んでください。

## ゲームの制作で入れるもの {#game}

C++ と Visual Studio のプロジェクトでは、おおむね次の分類で考えます。

| 分類 | 例 | 理由 |
| --- | --- | --- |
| IDE の個人設定 | `.vs/`、`*.user`、`*.suo` | 人ごとに違う。他人の環境で意味がない |
| ビルドの出力 | `x64/`、`Debug/`、`Release/`、`out/`、`*.obj`、`*.pdb`、`*.exe` | 作り直せる。サイズが大きい |
| パッケージの置き場 | `vcpkg_installed/`、`packages/` | インストールで作れる。大きい |
| 一時ファイル | `*.tmp`、`*.log`、`*.bak` | 再現できる。差分が邪魔になる |
| 秘密情報 | `.env`、`secrets.json`、`*.pem` | 漏れると被害が出る |

入れてはいけないものを逆に除外しすぎる事故にも注意してください。たとえば `*.exe` を除外していて、配布用の外部ツールを置きたい場合、そのファイルだけ `!tools/foo.exe` のように例外にします。`.sln`、`.vcxproj`、`.vcxproj.filters`、ソース、リソース、`.editorconfig`、`.gitattributes` は、管理に<strong>入れます</strong>。

## テンプレートを使う {#template}

一から書くのは大変なので、GitHub が配っているテンプレートを元にするのが手早い方法です。GitHub でリポジトリを作るときの「Add .gitignore」で「VisualStudio」を選ぶか、`github/gitignore` リポジトリの `VisualStudio.gitignore` をコピーします。

Visual Studio でプロジェクトを作るとき、「Git リポジトリを作成」を選ぶと、C++ 用の `.gitignore` が自動で置かれます。

テンプレートは広く作ってあるので、自分のプロジェクト特有の出力先（`bin/`、`Saved/`、`Intermediate/` など）は、足してください。

## すでに記録したファイルを外す {#untrack}

!!! warning ".gitignore は、すでに記録したファイルには効かない"
    すでにコミットしてしまったファイルは、あとから `.gitignore` に書いても追跡され続けます。

追跡だけを外すには、`git rm --cached` を使います。

```bash
git rm --cached x64/Debug/MyGame.exe        # 追跡だけを外す（ファイルは残る）
git rm -r --cached x64/                     # フォルダーごと
git commit -m "ビルドの出力を管理から外す"
```

`--cached` が大事です。これを付けないと、ファイルそのものが削除されます。付けていれば、作業フォルダーには残ったまま、Git の管理からだけ外れます。

ただし、過去のコミットには、ファイルが残っています。履歴にサイズの大きいファイルが入ってしまった場合は、リポジトリを軽くしたければ履歴の書き換えが必要です。難しい操作なので、[事故と対処](accidents.md#bigfile) を見てください。

## 無視されているか確かめる {#check}

あるファイルが、どのルールで無視されているかを調べられます。

```bash
git check-ignore -v x64/Debug/MyGame.exe
```

```text title="実行結果の形"
.gitignore:5:x64/	x64/Debug/MyGame.exe
```

左が「どのファイルの何行目のルールか」、右が対象のファイルです。意図せず無視されているファイルがあるときは、これで原因が分かります。無視されたファイルを強制的に追加したいときは、`git add -f` を使います（例外のルールを書くほうが安全です）。

## 自分だけの無視と全員の無視 {#personal}

リポジトリの `.gitignore` は、全員に効きます。自分のエディターの一時ファイルのように、自分のパソコンだけで無視したいものは、次の 2 か所に書くと、チームに影響しません。

- `.git/info/exclude`：そのリポジトリだけ、自分だけ
- グローバルの無視ファイル：`git config --global core.excludesFile ~/.gitignore_global` で指定した、全リポジトリに効くファイル

プロジェクトに必要な無視は `.gitignore`、個人の事情は自分用のファイルに、と分けると、`.gitignore` がきれいに保たれます。

## よくあるミス {#mistakes}

??? failure "`.gitignore` に書いたのに、まだ表示される"
    すでに記録されたファイルには効きません。`git rm --cached` で追跡を外します。

??? failure "ビルド生成物を入れてしまい、リポジトリが重くなった"
    `x64/` や `.vs/` を `.gitignore` に書く前にコミットすると、数百 MB が履歴に残ります。履歴から完全に消すのは難しいので、最初のコミットの前に `.gitignore` を置いてください。

??? failure "`.gitignore` に `*.exe` と書いたら、必要な外部ツールまで無視された"
    例外を `!tools/foo.exe` のように書くか、そのフォルダーの `.gitignore` に分けます。`git check-ignore -v` で原因のルールを調べられます。

## これだけ覚える {#summary}

- 最初のコミットの前に `.gitignore` を置く
- ビルドの出力、個人の設定、秘密情報を入れる。ソースと `.sln` は入れる
- すでに記録したものは `git rm --cached`
- 迷ったら、GitHub の VisualStudio テンプレートを元にする

## 関連ページ {#related}

- [記録する（status・add・commit）](commit.md)
- [事故と対処](accidents.md)
- [外部ライブラリの入れ方](../vs/libraries.md)（`vcpkg_installed/` を入れない理由とつながる）

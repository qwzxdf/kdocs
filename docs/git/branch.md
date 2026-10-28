---
title: ブランチ（枝を分けて作業する）
tags:
  - Git
---

# ブランチ（枝を分けて作業する）

新しい機能を作っている途中で、別の不具合を直したくなることがあります。同じ場所で両方を進めると、どちらも中途半端な状態で混ざります。しかも、片方がうまくいかなかったとき、もう片方だけを残すのが難しくなります。

そこで、<strong>機能ごとに枝を分けて</strong>作業します。ブランチを切ると、作業フォルダーがその枝の状態に切り替わり、ほかの枝の作業とは完全に独立します。終わったら、`main` に合体します。

!!! tip "ポイント"
    - ブランチは、コミットを指す名札。作るのも消すのも一瞬で、容量もほとんど増えない
    - 枝を移ると、作業フォルダーのファイルがその枝の状態に入れ替わる
    - 切り替える前に、変更はコミットか stash しておく
    - 枝の名前は `feature/enemy`、`fix/crash-on-load` のように種類と中身を付ける

!!! info "このページを読む前に"
    - [Git の考え方](concepts.md#branch)（ブランチは名札）
    - [記録する（status・add・commit）](commit.md)

## 枝を見る {#list}

いまある枝は、`git branch` で一覧できます。

```bash
git branch                        # ローカルの枝
git branch -a                     # リモートの枝も含めて全部
git branch -vv                    # 各枝の先頭のコミットと、組になるリモートの枝も表示
```

`*` が付いているのが、いま自分がいる枝です。`main` しかない新しいリポジトリでは、`* main` の 1 行だけが出ます。

## 枝を作って移る：switch {#switch}

枝を作って、そこへ移るには `git switch -c` を使います。

```bash
git switch -c feature/enemy       # いまの場所から枝を作って、そこに移る
git switch main                   # 既にある枝に移る
git switch -                      # 直前にいた枝に戻る
```

`-c` は「作る（create）」の意味です。付けないと、すでにある枝への移動だけです。枝は、いまの場所（HEAD）から作られるので、`main` で作れば `main` から分かれます。

枝を移ると、作業フォルダーのファイルが、その枝の状態に切り替わります。`feature/enemy` で追加したファイルは、`main` に戻ると見えなくなり、`feature/enemy` に戻ると現れます。「消えた」と慌てなくて大丈夫で、コミット済みなら無くなっていません。

古い資料では、`git checkout -b 枝名` や `git checkout 枝名` が書かれています。`git switch` は、枝の移動だけを担当するように分けられた新しいコマンドで、同じことをより安全にできます。

## 変更を持ったまま移れるか {#carry}

作業中の変更があるまま枝を移ろうとすると、Git が止めることがあります。

```text title="止められたときのメッセージ"
error: Your local changes to the following files would be overwritten by checkout:
	Player.cpp
Please commit your changes or stash them before you switch branches.
```

移り先の枝で、そのファイルが違う内容になっていると、変更が上書きされてしまうからです。選択肢は 2 つです。

- いまの変更を<strong>コミット</strong>してから移る
- コミットするほどではなければ、<strong>stash</strong> で一時的に退避する（[stash](stash.md) で説明）

どちらでもないなら、変更が衝突しない場合に限って、そのまま移れます。無理に移ろうとして変更を捨てる（`--force`）は、使わないでください。

## 枝を合体する・消す {#merge-delete}

作業が終わったら、`main` に合体します。

```bash
git switch main                   # 取り込む側（main）に移る
git merge feature/enemy           # 枝の変更を、いまの枝（main）に合体する
git branch -d feature/enemy       # 役目を終えた枝を消す
```

`git merge` は、<strong>いまいる枝</strong>に指定した枝の変更を取り込みます。つまり、`main` に取り込みたければ、先に `main` に移ってから実行します。順序を逆にすると、取り込む向きが逆になります。マージの詳しい動きは [マージ](merge.md) で説明します。

`-d` は、マージ済みの枝だけを消します。まだマージしていない枝を消そうとすると、Git が止めます。本当に捨ててよい場合だけ、`-D` で強制的に消せます。

```bash
git branch -D experiment          # マージしていなくても消す（その枝のコミットは見えなくなる）
```

枝を消しても、そのコミットが全部消えるわけではありません。マージ済みなら、中身は `main` の履歴に入っています。マージ前に `-D` で消したコミットも、[reflog](undo.md#reflog) で探せます。

## 枝の名前を付ける {#naming}

枝の名前は、一覧で読めることが大切です。よく使われる形は、`種類/内容` です。

| 接頭辞 | 使いどころ | 例 |
| --- | --- | --- |
| `feature/` | 新しい機能 | `feature/enemy-ai` |
| `fix/` | 不具合の修正 | `fix/crash-on-load` |
| `refactor/` | 動きを変えない整理 | `refactor/scene-manager` |
| `experiment/` | 試しの作業（捨てるかもしれない） | `experiment/new-shadow` |

チームで決まりがあれば、それに従ってください。名前に使える文字は、英数字、`-`、`_`、`/` が安全です。空白や日本語は、コマンドで扱いにくくなります。

## 枝の名前を変える {#rename}

付けた名前を直したいときは、`-m`（move）を使います。

```bash
git branch -m feature/enemy feature/enemy-ai   # 名前を変える
git branch -m new-name                         # いまの枝の名前を変える
```

すでにリモートへ push した枝は、リモート側にも古い名前が残ります。共有していない枝の名前変更にとどめるか、新しい名前で push し直して古い枝を消してください。

## ブランチを使う流れ {#flow}

一人で作るときの典型的な一日を、通して書くと次のようになります。

```bash
git switch main
git pull                          # 最新にしてから
git switch -c feature/title-menu  # 枝を切る
# …直す、add、commit を繰り返す…
git switch main
git merge feature/title-menu      # 終わったら main に戻して合体
git push
git branch -d feature/title-menu
```

チームで PR を使う場合は、`merge` の部分を GitHub 上のプルリクエストに置き換えます。[チーム開発の進め方](team.md) を参照してください。

## ゲームの制作で効く使い方 {#game}

- 大きな機能は、<strong>動く状態を保てる単位</strong>で枝を切る。数日を超える枝は、`main` とのずれが大きくなり、合体が重くなる
- 「この描画の実装方式を試したい」といった実験は、`experiment/` の枝で気軽にやる。失敗したら `-D` で捨てればよい
- 締め切り前の安定版は、枝ではなく [タグ](tag.md) で印を付けておく

## よくあるミス {#mistakes}

??? failure "枝を移ったら、作業したファイルが消えた"
    コミットしないまま移ると、変更が持ち越されるか、止められるかのどちらかです。消えたのではなく、別の枝の状態になっています。元の枝に戻れば現れます。

??? failure "`main` で作業を始めてしまった"
    コミット前なら、そのまま `git switch -c feature/xxx` で枝を作れば、変更ごと新しい枝に移れます。コミット後でも、`main` の戻し方を調べる前に、まず枝を作って、コミットが名札で指されるようにします。

??? failure "マージ前の枝を `-D` で消した"
    [reflog](undo.md#reflog) で、その枝の先頭だったコミットの ID を探し、`git switch -c 枝名 <ID>` で復活できます。

## これだけ覚える {#summary}

- 枝は `git switch -c 名前` で作り、`git switch 名前` で移る
- 移る前に、変更はコミットか stash する
- 合体は、取り込む側の枝に移ってから `git merge`
- 終わった枝は、`git branch -d` で消す

## 関連ページ {#related}

- [マージ](merge.md)
- [コンフリクト](conflict.md)
- [stash](stash.md)
- [チーム開発の進め方](team.md)

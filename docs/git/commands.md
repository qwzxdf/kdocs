---
title: コマンド早見表
tags:
  - Git
---

# コマンド早見表

使い方は覚えたけれど、コマンドの綴りが出てこない。そういうときに、1 ページで引けるようにまとめました。各コマンドの意味は、リンク先のページで説明しています。

!!! info "このページを読む前に"
    - 個々の使い方は、各リンク先のページを先に読んでください。ここは引くためのページです

## 設定と準備 {#setup}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| 名前を設定 | `git config --global user.name "名前"` | [最初の設定](install.md#user) |
| メールアドレスを設定 | `git config --global user.email "a@b.c"` | [最初の設定](install.md#user) |
| 設定を一覧 | `git config --global --list` | [最初の設定](install.md#levels) |
| リポジトリを作る | `git init` | [記録する](commit.md#init) |
| リモートから持ってくる | `git clone <URL>` | [リモート](remote.md#clone) |

## 記録する {#record}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| 状態を見る | `git status` / `git status -s` | [記録する](commit.md#status) |
| ステージに入れる | `git add <ファイル>` / `git add .` | [記録する](commit.md#add) |
| 変更を一部ずつ入れる | `git add -p` | [記録する](commit.md#add) |
| 差分を見る（未ステージ） | `git diff` | [記録する](commit.md#diff) |
| 差分を見る（ステージ済み） | `git diff --staged` | [記録する](commit.md#diff) |
| コミットする | `git commit -m "メッセージ"` | [記録する](commit.md#commit) |
| 管理中のファイルを全部コミット | `git commit -a -m "メッセージ"` | [記録する](commit.md#commit) |

## 履歴を見る {#history}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| 履歴の一覧 | `git log --oneline` | [履歴を読む](log.md#log) |
| 枝の図つき・全部の枝 | `git log --oneline --graph --all` | [履歴を読む](log.md#log) |
| ファイルの履歴 | `git log --oneline -- <ファイル>` | [履歴を読む](log.md#log) |
| 1 つのコミットの中身 | `git show <ID>` | [履歴を読む](log.md#show) |
| 2 点を比べる | `git diff <ID> <ID>` | [履歴を読む](log.md#diff) |
| 行ごとの作者 | `git blame <ファイル>` | [履歴を読む](log.md#blame) |
| バグの出始めを探す | `git bisect start` | [履歴を読む](log.md#bisect) |

## 取り消す・戻す {#undo}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| 未ステージの変更を捨てる | `git restore <ファイル>` | [取り消す](undo.md#restore) |
| ステージから外す | `git restore --staged <ファイル>` | [取り消す](undo.md#unstage) |
| 過去の版のファイルを取り出す | `git restore --source=<ID> <ファイル>` | [取り消す](undo.md#source) |
| 直前のコミットを直す | `git commit --amend` | [取り消す](undo.md#amend) |
| コミットだけ取り消す（変更は残す） | `git reset --soft HEAD~1` | [取り消す](undo.md#reset) |
| コミットも変更も捨てる | `git reset --hard HEAD~1` | [取り消す](undo.md#reset) |
| 共有済みのコミットを打ち消す | `git revert <ID>` | [取り消す](undo.md#revert) |
| 消えたコミットを探す | `git reflog` | [取り消す](undo.md#reflog) |

## ブランチとマージ {#branch}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| 枝の一覧 | `git branch` / `git branch -a` | [ブランチ](branch.md#list) |
| 枝を作って移る | `git switch -c <名前>` | [ブランチ](branch.md#switch) |
| 枝に移る | `git switch <名前>` | [ブランチ](branch.md#switch) |
| 枝を合体する | `git merge <枝>` | [マージ](merge.md) |
| 合体を取りやめる | `git merge --abort` | [マージ](merge.md#abort) |
| 枝を消す | `git branch -d <名前>` | [ブランチ](branch.md#merge-delete) |
| 枝の名前を変える | `git branch -m <旧> <新>` | [ブランチ](branch.md#rename) |
| 枝を付け替える | `git rebase <枝>` | [rebase](rebase.md) |
| コミットを 1 つ持ってくる | `git cherry-pick <ID>` | [rebase](rebase.md#cherry-pick) |

## 共有する {#remote}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| リモートを登録 | `git remote add origin <URL>` | [リモート](remote.md#add) |
| 最初の push | `git push -u origin main` | [リモート](remote.md#push) |
| push | `git push` | [リモート](remote.md#push) |
| 持ってくるだけ | `git fetch` | [リモート](remote.md#fetch) |
| 持ってきて合体 | `git pull` | [リモート](remote.md#pull) |
| リモートの枝を消す | `git push origin --delete <枝>` | [リモート](remote.md#remote-branch) |

## 一時退避とタグ {#stash-tag}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| 変更をしまう | `git stash` / `git stash -u` | [stash](stash.md) |
| しまった変更を戻す | `git stash pop` | [stash](stash.md#basic) |
| stash の一覧 | `git stash list` | [stash](stash.md#list) |
| タグを付ける | `git tag -a v1.0.0 -m "メッセージ"` | [タグ](tag.md#create) |
| タグを送る | `git push origin v1.0.0` | [タグ](tag.md#push) |

## ファイルとその他 {#misc}

| やりたいこと | コマンド | 詳しく |
| --- | --- | --- |
| 追跡だけ外す | `git rm --cached <ファイル>` | [.gitignore](gitignore.md#untrack) |
| 無視ルールを調べる | `git check-ignore -v <ファイル>` | [.gitignore](gitignore.md#check) |
| ファイルを移動・改名 | `git mv <旧> <新>` | — |
| サブモジュールを取る | `git submodule update --init --recursive` | [サブモジュール](submodule.md#clone) |
| 衝突の目印の残りを探す | `git diff --check` | [コンフリクト](conflict.md#leftover) |

## 迷ったときの確認 {#check}

何をすればいいか迷ったら、まず次の 3 つで状況を見ます。

```bash
git status                        # どのファイルがどの状態か
git log --oneline --graph --all   # 履歴と、いまの位置
git diff                          # 何を直したか
```

ほとんどの事故は、この 3 つで状況を把握すれば、落ち着いて対処できます。

## 関連ページ {#related}

- [Git の考え方](concepts.md)
- [事故と対処](accidents.md)

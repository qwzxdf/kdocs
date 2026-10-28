---
title: GitHub を使う（リポジトリ・認証・プルリクエスト）
tags:
  - Git
---

# GitHub を使う（リポジトリ・認証・プルリクエスト）

Git と GitHub は、よく混同されます。Git は履歴を管理する道具で、パソコンの中で動きます。GitHub は、その Git のリポジトリを置いて、共有するためのサービスです。GitHub が無くても Git は使えますが、チームで作る、バックアップを取る、成果物を公開する、といった用途では GitHub が事実上の標準になっています。

このページは、アカウントを作ってからリポジトリを載せるまで、認証の方法、プルリクエスト、Issue といった GitHub 側の機能を順に説明します。

!!! tip "ポイント"
    - Git は道具、GitHub は置き場所。同じ役割のサービスに GitLab や Bitbucket もあり、Git の使い方は同じ
    - 学校の課題などで人に見せたくない作品は、Private（非公開）リポジトリにする
    - 認証は Git Credential Manager が楽。SSH 鍵も使える
    - 変更は、プルリクエストで `main` に入れる。レビューと自動チェックの入り口になる

!!! info "このページを読む前に"
    - [リモートと push・pull・fetch](remote.md)
    - [インストールと最初の設定](install.md)

## アカウントとリポジトリ {#account}

github.com でアカウントを作ります。メールアドレスは、[Git の設定](install.md#user) に書いたものと同じにしてください。

リポジトリは、「New repository」から作ります。入力する項目は、次のとおりです。

| 項目 | 説明 |
| --- | --- |
| Repository name | 名前。英数字とハイフンが無難 |
| Public / Private | 誰でも見られるか、自分と招待した人だけか |
| Add a README | 説明を書くファイル。作っておくと、トップページに表示される |
| Add .gitignore | 管理しないファイルの一覧。テンプレートから「C++」または「VisualStudio」を選ぶ |
| Choose a license | 公開するときの利用条件。公開しないなら不要 |

GitHub 側に README や `.gitignore` を作る場合、手元のプロジェクトを載せるときは先に `clone` から始めるのが簡単です。

```bash
git clone https://github.com/ユーザー名/MyGame.git
# このフォルダーにプロジェクトのファイルを入れて、add / commit / push
```

手元にすでにプロジェクトがあって、あとから GitHub に載せるなら、GitHub 側で<strong>空のリポジトリ</strong>（README などを追加しない）を作ります。

```bash
cd MyGame
git remote add origin https://github.com/ユーザー名/MyGame.git
git push -u origin main
```

## Public と Private {#visibility}

Public のリポジトリは、世界中の誰でも見られます。ソースコード、履歴、そして<strong>過去にコミットしたパスワードや API キー</strong>まで見えます。

学校や授業の課題を公開すると、規則違反になることがあります。ポートフォリオのために公開するなら、授業の指示や著作権（他人のアセットを含んでいないか）を確かめてからにしてください。迷ったら Private にして、あとから Public に変えられます。

## 認証 {#auth}

GitHub に push や clone をするとき、本人確認が必要です。いまの GitHub は、アカウントのパスワードは受け付けません。次の 3 つのうち、どれかを使います。

<strong>Git Credential Manager（GCM）</strong>は、Git for Windows に同梱されている仕組みです。最初に push すると、ブラウザーが開き、GitHub にサインインして許可すると、Windows に認証情報が保存されます。次から入力は要りません。ふつうの学生は、これで十分です。

<strong>SSH 鍵</strong>は、鍵のペアで認証します。[最初の設定](install.md#auth) で作った公開鍵を、GitHub の「Settings → SSH and GPG keys → New SSH key」に貼ります。以後は、URL を `git@github.com:ユーザー名/MyGame.git` の形で使います。

<strong>Personal Access Token（PAT）</strong>は、パスワードの代わりに使える長い文字列です。GitHub の「Settings → Developer settings → Personal access tokens」で作ります。CI やスクリプトから使うときのもので、手作業の Git には GCM のほうが楽です。トークンは作ったときにしか見えません。コードやリポジトリに書き込まず、どこにも貼らないでください。

認証で失敗したときの典型的な原因は、古い認証情報が残っていることです。Windows の「資格情報マネージャー」を開き、`git:https://github.com` の項目を消すと、次の操作で入力し直せます。

## プルリクエスト {#pr}

プルリクエスト（PR）は、「この枝の変更を `main` に入れてください」というお願いです。GitHub 上で差分を見て、コメントを付けて、承認してから合体します。チームでなくても、一人で作るときに使うと、変更を一度見直す機会になります。

流れは、次のとおりです。

1. 枝を切って、作業して、push する（`git push -u origin feature/enemy`）
2. GitHub のリポジトリを開くと、「Compare & pull request」ボタンが出る。押す
3. タイトルと説明を書いて、「Create pull request」
4. レビューを受ける。直す指摘があれば、同じ枝に push する（PR に自動で反映される）
5. 承認されたら「Merge pull request」で合体。終わった枝は消す

PR の説明に書くことは、何を変えたか、なぜ変えたか、どう確認したかの 3 つです。詳しくは [チーム開発の進め方](team.md#pr) にあります。

マージのボタンには、3 種類の方式があります。

| 方式 | 履歴の形 | 向いている場面 |
| --- | --- | --- |
| Create a merge commit | マージコミットが 1 つ付く。枝の履歴がそのまま残る | 履歴の経緯を残したい |
| Squash and merge | 枝の全コミットを 1 つにまとめて入れる | 枝の途中のコミットが雑でも、`main` をきれいにしたい |
| Rebase and merge | 枝のコミットを、一直線に積み直す | 履歴を一直線にしたい |

チームで 1 つに決めておくと、`main` の履歴が読みやすくなります。迷ったら Squash and merge が扱いやすいです。

## Issue {#issue}

Issue は、バグ報告、やることの管理、相談を書き込む掲示板です。ゲーム開発では、「ボスの当たり判定がずれる」「タイトル画面の BGM を入れる」のような作業を 1 件ずつ立てて、担当を決めると、チームの状況が見渡せます。

コミットメッセージや PR の説明に `Fixes #12` と書くと、PR を合体したときに、Issue 12 番が自動で閉じます。作業と記録が結び付くので、便利です。

## README を書く {#readme}

リポジトリのトップに表示される `README.md` は、そのプロジェクトの顔です。最低限、次を書いておくと、他の人（や半年後の自分）が助かります。

- 何のプロジェクトか（ゲームの概要、スクリーンショット）
- ビルドの手順（必要な Visual Studio のバージョン、ライブラリの入れ方）
- 遊び方・操作方法
- 使っているライブラリや素材のクレジット

## ゲームの制作で効く使い方 {#game}

- 完成した作品の公開には、GitHub の「Releases」が使える。ビルド済みの実行ファイルを zip にして添付すると、ソースをビルドしなくても遊んでもらえる。バージョンの印は [タグ](tag.md) で付ける
- 自動ビルドは [GitHub Actions](../vs/github-actions.md)。PR のたびにビルドが通るかを確認できる
- 大きなアセットは [Git LFS](git-lfs.md)。GitHub は、1 ファイル 100 MB を超えると push を拒否する

## よくあるミス {#mistakes}

??? failure "パスワードや API キーを、コミットして push してしまった"
    Public のリポジトリなら、すぐに悪用されます。ファイルを消しても履歴に残ります。<strong>まず、そのキーを無効にして作り直してください。</strong>履歴からの削除はあとで行います。[事故と対処](accidents.md#secret) を見てください。

??? failure "push しようとすると、認証で失敗し続ける"
    古い認証情報が残っています。Windows の資格情報マネージャーで、`git:https://github.com` を削除してから、やり直します。

??? failure "Public にしたら、課題が見えていた"
    課題のリポジトリは、公開してよいと指示があるまで Private にします。ほかの人に見せたいときは、「Settings → Collaborators」で個別に招待できます。

## これだけ覚える {#summary}

- GitHub は Git の置き場所。授業の作品は、公開してよいか確かめてから Public にする
- 認証は Git Credential Manager が楽
- 変更はプルリクエストで `main` に入れる
- パスワードや API キーは、絶対にコミットしない

## 関連ページ {#related}

- [リモートと push・pull・fetch](remote.md)
- [チーム開発の進め方](team.md)
- [GitHub Actions で自動ビルド](../vs/github-actions.md)

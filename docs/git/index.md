# Git

ゲームを作っていると「昨日まで動いていたのに、いま動かない」が必ず起きます。複数人で作れば同じファイルを同時に直して、片方が消えることもあります。<strong>Git</strong> はファイルの変更を履歴として残し、好きな時点に戻せる道具です。別々に直した内容をあとから合体する仕組みも持っています。

このカテゴリは、Git の考え方から、毎日の操作、チームでの使い方、事故の直し方までを順にまとめています。<strong>操作は、SourceTree の画面で説明します</strong>（コマンドを打つ必要はありません）。コマンドを使うのは、プッシュの拒否や、消えたコミットの救出のような、画面だけでは直せないトラブルの場面だけです。

## 読む順番

初めて Git を使うなら次の順番がおすすめです。

1. [Git の考え方](concepts.md)で、3 つの場所とブランチの意味をつかむ
2. [SourceTree のインストールと最初の設定](install.md)を済ませ、[SourceTree の画面](sourcetree.md)で部品の名前を覚える
3. [記録する](commit.md)、[履歴を読む](log.md)、[取り消す・戻す](undo.md)で一人で使う基本を覚える
4. [ブランチ](branch.md)、[マージ](merge.md)、[コンフリクト](conflict.md)で枝を使えるようにする
5. [リモート](remote.md)と [GitHub](github.md)で、共有する
6. [チーム開発の進め方](team.md)と [事故の対処](accidents.md)を読む。Visual Studio や GitHub Desktop で使いたい人は、別の道具のページ（[Visual Studio](vs-git.md)、[GitHub Desktop](github-desktop.md)）も読める

## ページ一覧

### 基本

| ページ | 内容 |
| --- | --- |
| [Git の考え方](concepts.md) | スナップショットと 3 つの場所、ブランチは名札、ローカルとリモート |
| [SourceTree のインストールと最初の設定](install.md) | SourceTree、名前とメール、改行の設定、GitHub との認証 |
| [記録する（ステージとコミット）](commit.md) | 2 段階の記録、差分の見方、コミットメッセージとコミットの大きさ |
| [履歴を読む](log.md) | 履歴の一覧、2 点の比較、行ごとの作者、バグの出始めを探す二分探索 |
| [取り消す・戻す](undo.md) | 破棄・Amend・リセット・打ち消しの使い分けと、消えたコミットを探す reflog |

### 枝と共有

| ページ | 内容 |
| --- | --- |
| [ブランチ](branch.md) | 枝を切る移る消す名前の付け方 |
| [マージ](merge.md) | fast-forward とマージコミット、合体の取り消し、プルとの関係 |
| [コンフリクト](conflict.md) | 目印の読み方と直し方、衝突しやすいファイル、避け方 |
| [リモートとプッシュ・プル](remote.md) | クローン、プッシュ、フェッチとプルの違い、プッシュが拒否されたとき |
| [GitHub を使う](github.md) | アカウントとリポジトリ、Public と Private、認証、プルリクエスト、Issue |
| [.gitignore](gitignore.md) | 記録しないファイルの決め方とすでに記録したものを外す方法 |

### 発展

| ページ | 内容 |
| --- | --- |
| [スタッシュ](stash.md) | 作業を一時的に退避する |
| [リベース](rebase.md) | 履歴を一直線にする、コミットを整える、チェリーピック。やってはいけない場面 |
| [タグ](tag.md) | バージョンに動かない印を付ける。GitHub のリリース |
| [サブモジュール](submodule.md) | 他のリポジトリを中に入れる。clone と更新の手順 |

### 道具

| ページ | 内容 |
| --- | --- |
| [SourceTree の画面](sourcetree.md) | 画面の部品の名前と、リポジトリの開き方 |
| [Visual Studio から Git を使う](vs-git.md) | 別の道具。「Git の変更」ウィンドウ、枝の切り替え、マージ エディター |
| [GitHub Desktop](github-desktop.md) | 別の道具。機能を絞った画面ツール |

### チームとゲーム制作

| ページ | 内容 |
| --- | --- |
| [チーム開発の進め方](team.md) | ブランチ運用、プルリクエスト、レビュー、clang-format |
| [Git LFS とゲームのリポジトリ](git-lfs.md) | 大きなバイナリの預け方、track、容量、フォルダー構成 |
| [事故の対処](accidents.md) | 分離 HEAD、強制プッシュ、巨大ファイル、秘密情報のプッシュ（コマンドを使う） |
| [コマンド早見表](commands.md) | トラブルのときに使うコマンドを、目的から引く |

## 関連ページ

- [Visual Studio](../vs/index.md)（設定、ビルド、デバッグ）
- [GitHub Actions で自動ビルド](../vs/github-actions.md)
- [.editorconfig](../vs/editorconfig.md)

# Git

ゲームを作っていると「昨日まで動いていたのに、いま動かない」が必ず起きます。複数人で作れば同じファイルを同時に直して、片方が消えることもあります。<strong>Git</strong> はファイルの変更を履歴として残し、好きな時点に戻せる道具です。別々に直した内容をあとから合体する仕組みも持っています。

このカテゴリは Git の考え方から、毎日の操作、チームでの使い方、事故の直し方までを順にまとめています。コマンドを打つ方法と画面のツール（Visual Studio、SourceTree、GitHub Desktop）の使い方の両方を扱います。中身は同じ Git なのでコマンドの意味が分かれば、どのツールでも画面の表示が読めます。

## 読む順番

初めて Git を使うなら次の順番がおすすめです。

1. [Git の考え方](concepts.md)で、3 つの場所とブランチの意味をつかむ
2. [インストールと最初の設定](install.md)を済ませる
3. [記録する](commit.md)、[履歴を読む](log.md)、[取り消す・戻す](undo.md)で一人で使う基本を覚える
4. [ブランチ](branch.md)、[マージ](merge.md)、[コンフリクト](conflict.md)で枝を使えるようにする
5. [リモート](remote.md)と [GitHub](github.md)で、共有する
6. 使うツールのページ（[Visual Studio](vs-git.md)、[SourceTree](sourcetree.md)、[GitHub Desktop](github-desktop.md)）を読む

## ページ一覧

### 基本

| ページ | 内容 |
| --- | --- |
| [Git の考え方](concepts.md) | スナップショットと 3 つの場所、ブランチは名札、ローカルとリモート |
| [インストールと最初の設定](install.md) | Git for Windows、名前とメール、改行の設定、GitHub との認証 |
| [記録する（status・add・commit）](commit.md) | 2 段階の記録、diff の見方、コミットメッセージとコミットの大きさ |
| [履歴を読む（log・show・blame）](log.md) | 履歴の一覧、2 点の比較、行ごとの作者、バグの出始めを探す bisect |
| [取り消す・戻す](undo.md) | restore・amend・reset・revert の使い分けと、消えたコミットを探す reflog |

### 枝と共有

| ページ | 内容 |
| --- | --- |
| [ブランチ](branch.md) | 枝を切る移る消す名前の付け方 |
| [マージ](merge.md) | fast-forward とマージコミット、合体の取り消し pull との関係 |
| [コンフリクト](conflict.md) | 目印の読み方と直し方、衝突しやすいファイル、避け方 |
| [リモートと push・pull・fetch](remote.md) | clone、push、fetch と pull の違い push が拒否されたとき |
| [GitHub を使う](github.md) | アカウントとリポジトリ、Public と Private、認証、プルリクエスト、Issue |
| [.gitignore](gitignore.md) | 記録しないファイルの決め方とすでに記録したものを外す方法 |

### 発展

| ページ | 内容 |
| --- | --- |
| [stash](stash.md) | 作業を一時的に退避する |
| [rebase と cherry-pick](rebase.md) | 履歴を一直線にする、コミットを整える。やってはいけない場面 |
| [タグ](tag.md) | バージョンに動かない印を付ける。GitHub のリリース |
| [サブモジュール](submodule.md) | 他のリポジトリを中に入れる。clone と更新の手順 |

### ツール

| ページ | 内容 |
| --- | --- |
| [Visual Studio から Git を使う](vs-git.md) | 「Git の変更」ウィンドウ、枝の切り替えマージ エディター |
| [SourceTree](sourcetree.md) | 高機能な画面ツール。履歴の図の上での操作、対話式リベース |
| [GitHub Desktop](github-desktop.md) | 機能を絞った画面ツール。迷わず clone から PR まで |

### チームとゲーム制作

| ページ | 内容 |
| --- | --- |
| [チーム開発の進め方](team.md) | ブランチ運用、プルリクエスト、レビュー、clang-format |
| [Git LFS とゲームのリポジトリ](git-lfs.md) | 大きなバイナリの預け方、track、容量、フォルダー構成 |
| [事故と対処](accidents.md) | detached HEAD、force push、巨大ファイル、秘密情報の push |
| [コマンド早見表](commands.md) | 目的からコマンドを引く |

## 関連ページ

- [Visual Studio](../vs/index.md)（設定、ビルド、デバッグ）
- [GitHub Actions で自動ビルド](../vs/github-actions.md)
- [.editorconfig](../vs/editorconfig.md)

---
title: サブモジュール（他のリポジトリを中に入れる）
tags:
  - Git
---

# サブモジュール（他のリポジトリを中に入れる）

ゲームを作っていると、他の人が作ったライブラリ（ImGui、Jolt Physics など）を、プロジェクトの中に置きたくなります。ソースをそのままコピーして `third_party/` に入れる方法は簡単ですが、ライブラリが更新されたときに、どこまでが自分の改変で、どこからが元のコードか分からなくなります。

<strong>サブモジュール</strong>は、「他のリポジトリの、このコミットを使う」という指定を、自分のリポジトリに記録する仕組みです。ライブラリの中身は自分の履歴には入らず、参照だけが入ります。

!!! tip "ポイント"
    - サブモジュールは、他のリポジトリの特定のコミットへの参照。中身は別のリポジトリのまま
    - `git clone` だけでは中身が空。`--recurse-submodules` を付けるか、あとで `git submodule update --init`
    - 更新は自動ではない。親側で「どのコミットを使うか」を、明示的に更新する
    - 扱いが難しい面もある。vcpkg などのパッケージ管理で足りるなら、そちらが楽

!!! info "このページを読む前に"
    - [リモートと push・pull・fetch](remote.md)
    - [外部ライブラリの入れ方](../vs/libraries.md)（vcpkg との使い分け）

## 追加する {#add}

```bash
git submodule add https://github.com/ocornut/imgui.git third_party/imgui
git commit -m "ImGui をサブモジュールとして追加"
```

`git submodule add` は、指定した URL のリポジトリを、`third_party/imgui` に取ってきます。同時に、次の 2 つが自動で作られます。

- `.gitmodules`：サブモジュールの URL と、置く場所を書いた設定ファイル
- 親リポジトリの中の、サブモジュールの位置に「特定のコミットへの参照」

どちらも親リポジトリでコミットします。サブモジュールの中身（ImGui のファイル）は、親のコミットには入りません。入るのは、「ImGui のこのコミットを使う」という記録だけです。

## clone する側の手順 {#clone}

サブモジュールを持つリポジトリを clone しても、サブモジュールのフォルダーは<strong>空</strong>で作られます。

```bash
git clone --recurse-submodules https://github.com/ユーザー名/MyGame.git
```

最初から `--recurse-submodules` を付けると、中身も一緒に取ってきます。付け忘れたときは、あとから取れます。

```bash
git submodule update --init --recursive
```

`--init` は、サブモジュールを初期化して取得します。`--recursive` は、サブモジュールがさらにサブモジュールを持つ場合まで辿ります。

「ビルドしようとしたら、ヘッダーが見つからない」のは、たいていこの手順の忘れです。

## 更新する {#update}

親が記録しているのは「特定のコミット」なので、ライブラリの新しい版が出ても、自動では追いつきません。更新は、2 段階です。

まず、サブモジュールの中で、使いたいコミットに移ります。

```bash
cd third_party/imgui
git fetch
git switch --detach v1.91.0       # タグやコミットを選ぶ
cd ../..
```

次に、親リポジトリで、「使うコミットが変わった」ことをコミットします。

```bash
git add third_party/imgui
git commit -m "ImGui を v1.91.0 に更新"
```

サブモジュールの中は、ふつう detached HEAD の状態です。これは正常で、「特定のコミットを使っている」ことを意味します。

他の人が親リポジトリを `pull` したあと、手元のサブモジュールを新しい記録に合わせるには、次を実行します。

```bash
git pull
git submodule update --init --recursive
```

`git pull` だけでは、サブモジュールの中身は更新されません。親が記録を更新したことを知っても、中身はそのままです。`submodule update` で追いつかせます。

## 状態を見る {#status}

```bash
git submodule status              # 各サブモジュールの、いま使っているコミット
git status                        # サブモジュールの状態も出る
```

`git status` に、サブモジュールが「modified content」「new commits」と出ることがあります。サブモジュール内でファイルを直した、あるいは、使っているコミットを動かした、という意味です。意図しない変更なら、サブモジュールの中で元に戻します。

## 削除する {#remove}

サブモジュールの削除は、フォルダーを消すだけでは足りません。

```bash
git submodule deinit -f third_party/imgui
git rm -f third_party/imgui
rm -rf .git/modules/third_party/imgui
git commit -m "ImGui のサブモジュールを削除"
```

`deinit` で登録を解き、`git rm` で記録と `.gitmodules` の項目を消し、`.git/modules` に残った実体も消します。

## 使いどころと、避けるべき場面 {#when}

サブモジュールは、次のような場面に向いています。

- ライブラリを改変して使う（自分のフォークを指す）
- 特定のバージョンに固定したい。他のリポジトリの履歴と一緒に追跡したい
- ビルドを再現するために、ソースごと入れたい

扱いが難しい場面もあります。

- 親とサブモジュールの両方を更新する作業は、手順が増えて、忘れやすい
- clone した直後に中身が空になるので、メンバーに説明が要る
- 画面ツールによっては、サブモジュールの扱いが弱い

単にライブラリを使うだけなら、[vcpkg](../vs/libraries.md) などのパッケージ管理のほうが楽です。ライブラリのバージョンを指定でき、ビルドまで自動になります。比較は [パッケージ管理の比較](../vs/package-managers.md) にあります。

## よくあるミス {#mistakes}

??? failure "clone したら `third_party/imgui` が空だった"
    `git submodule update --init --recursive` を実行します。次の clone からは、`--recurse-submodules` を付けます。

??? failure "サブモジュールを更新したのに、他の人の手元に反映されない"
    親リポジトリで `git add` して `commit` と `push` をしていません。サブモジュールの中の変更だけでは、親は更新されません。

??? failure "サブモジュールの中でコミットしたが、消えた"
    サブモジュールは detached HEAD なので、そのまま作業すると、コミットを見失います。サブモジュールの中で枝を作ってから作業して、そのリポジトリへ push します。

## これだけ覚える {#summary}

- `git submodule add URL 場所` で追加。`.gitmodules` もコミットする
- clone には `--recurse-submodules`、後からなら `git submodule update --init --recursive`
- 更新は 2 段階。サブモジュールを動かして、親でコミットする
- 単純にライブラリを使うだけなら、vcpkg が楽

## 関連ページ {#related}

- [外部ライブラリの入れ方](../vs/libraries.md)
- [パッケージ管理の比較](../vs/package-managers.md)
- [リモートと push・pull・fetch](remote.md)

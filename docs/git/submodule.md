---
title: サブモジュール（他のリポジトリを中に入れる）
tags:
  - Git
---

# サブモジュール（他のリポジトリを中に入れる）

ゲームを作っていると他の人が作ったライブラリ（ImGui、Jolt Physics など）をプロジェクトの中に置きたくなります。ソースをそのままコピーして `third_party/` に入れる方法は簡単ですが、ライブラリが更新されたときにどこまでが自分の改変で、どこからが元のコードか分からなくなります。

<strong>サブモジュール</strong>は「他のリポジトリのこのコミットを使う」という指定を自分のリポジトリに記録する仕組みです。ライブラリの中身は自分の履歴には入らず参照だけが入ります。

!!! tip "ポイント"
    - サブモジュールは他のリポジトリの特定のコミットへの参照。中身は別のリポジトリのまま
    - `git clone` だけでは中身が空。`--recurse-submodules` を付けるかあとで `git submodule update --init`
    - 更新は自動ではない。親側で「どのコミットを使うか」を明示的に更新する
    - 扱いが難しい面もある。vcpkg などのパッケージ管理で足りるならそちらが楽

!!! info "このページを読む前に"
    - [リモートとプッシュ・プル](remote.md)
    - [外部ライブラリの入れ方](../vs/libraries.md)（vcpkg との使い分け）

!!! note "SourceTree での操作"
    SourceTree のメニュー「リポジトリ」に、「サブモジュールを追加...」があります。追加・更新の意味は、このページのコマンドと同じです。サブモジュールは、使いこなすのが難しい機能なので、慣れるまでは、コマンドで状態を確かめながら進めてください。

## 追加する {#add}

```bash
git submodule add https://github.com/ocornut/imgui.git third_party/imgui
git commit -m "ImGui をサブモジュールとして追加"
```

`git submodule add` は指定した URL のリポジトリを `third_party/imgui` に取ってきます。同時に次の 2 つが自動で作られます。

- `.gitmodules`：サブモジュールの URL と置く場所を書いた設定ファイル
- 親リポジトリの中のサブモジュールの位置に「特定のコミットへの参照」

どちらも親リポジトリでコミットします。サブモジュールの中身（ImGui のファイル）は、親のコミットには入りません。入るのは「ImGui のこのコミットを使う」という記録だけです。

## clone する側の手順 {#clone}

サブモジュールを持つリポジトリを clone しても、サブモジュールのフォルダーは<strong>空</strong>で作られます。

```bash
git clone --recurse-submodules https://github.com/ユーザー名/MyGame.git
```

最初から `--recurse-submodules` を付けると中身も一緒に取ってきます。付け忘れたときはあとから取れます。

```bash
git submodule update --init --recursive
```

`--init` はサブモジュールを初期化して取得します。`--recursive` はサブモジュールがさらにサブモジュールを持つ場合まで辿ります。

「ビルドしようとしたらヘッダーが見つからない」のは、たいていこの手順の忘れです。

## 更新する {#update}

親が記録しているのは「特定のコミット」なので、ライブラリの新しい版が出ても、自動では追いつきません。更新は 2 段階です。

まず、サブモジュールの中で使いたいコミットに移ります。

```bash
cd third_party/imgui
git fetch
git switch --detach v1.91.0       # タグやコミットを選ぶ
cd ../..
```

次に、親リポジトリで「使うコミットが変わった」ことをコミットします。

```bash
git add third_party/imgui
git commit -m "ImGui を v1.91.0 に更新"
```

サブモジュールの中はふつう detached HEAD の状態です。これは正常で「特定のコミットを使っている」ことを意味します。

他の人が親リポジトリを `pull` したあと手元のサブモジュールを新しい記録に合わせるには、次を実行します。

```bash
git pull
git submodule update --init --recursive
```

`git pull` だけではサブモジュールの中身は更新されません。親が記録を更新したことを知っても、中身はそのままです。`submodule update` で追いつかせます。

## 状態を見る {#status}

```bash
git submodule status              # 各サブモジュールの、いま使っているコミット
git status                        # サブモジュールの状態も出る
```

`git status` にサブモジュールが「modified content」「new commits」と出ることがあります。サブモジュール内でファイルを直したあるいは、使っているコミットを動かしたという意味です。意図しない変更ならサブモジュールの中で元に戻します。

## 削除する {#remove}

サブモジュールの削除はフォルダーを消すだけでは足りません。

```bash
git submodule deinit -f third_party/imgui
git rm -f third_party/imgui
rm -rf .git/modules/third_party/imgui
git commit -m "ImGui のサブモジュールを削除"
```

`deinit` で登録を解き `git rm` で記録と `.gitmodules` の項目を消し、`.git/modules` に残った実体も消します。

## 使いどころと避けるべき場面 {#when}

サブモジュールは次のような場面に向いています。

- ライブラリを改変して使う（自分のフォークを指す）
- 特定のバージョンに固定したい。他のリポジトリの履歴と一緒に追跡したい
- ビルドを再現するためにソースごと入れたい

扱いが難しい場面もあります。

- 親とサブモジュールの両方を更新する作業は、手順が増えて忘れやすい
- clone した直後に中身が空になるので、メンバーに説明が要る
- 画面ツールによってはサブモジュールの扱いが弱い

単にライブラリを使うだけなら[vcpkg](../vs/libraries.md) などのパッケージ管理のほうが楽です。ライブラリのバージョンを指定できビルドまで自動になります。比較は [パッケージ管理の比較](../vs/package-managers.md) にあります。

## よくあるミス {#mistakes}

??? failure "clone したら `third_party/imgui` が空だった"
    `git submodule update --init --recursive` を実行します。次の clone からは `--recurse-submodules` を付けます。

??? failure "サブモジュールを更新したのに、他の人の手元に反映されない"
    親リポジトリで `git add` して `commit` と `push` をしていません。サブモジュールの中の変更だけでは親は更新されません。

??? failure "サブモジュールの中でコミットしたが、消えた"
    サブモジュールは detached HEAD なので、そのまま作業するとコミットを見失います。サブモジュールの中で枝を作ってから作業して、そのリポジトリへ push します。

## これだけ覚える {#summary}

- `git submodule add URL 場所` で追加。`.gitmodules` もコミットする
- clone には `--recurse-submodules`、後からなら `git submodule update --init --recursive`
- 更新は 2 段階。サブモジュールを動かして親でコミットする
- 単純にライブラリを使うだけなら vcpkg が楽

## 関連ページ {#related}

- [外部ライブラリの入れ方](../vs/libraries.md)
- [パッケージ管理の比較](../vs/package-managers.md)
- [リモートとプッシュ・プル](remote.md)

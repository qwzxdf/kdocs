---
title: std::filesystem
tags:
  - 入出力
---

# std::filesystem

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem` は、**ファイルやフォルダそのものを扱うライブラリ**です。パスの組み立て、ファイルがあるかの確認、フォルダの作成・削除、フォルダの中身の一覧、コピーや名前の変更などができます。ファイルの中身を読み書きするのは [`std::fstream`](fstream.md) の役目で、filesystem は「ファイルの外側」を扱います。Windows でも Mac / Linux でも同じコードで動くのが大きな利点です。

!!! tip "結論"
    - パスは文字列ではなく **`std::filesystem::path`** で持ち、`/` でつなげる（`dir / "save.dat"`）。
    - よく使うのは `exists`、`create_directories`、`directory_iterator`、`remove`、`rename`。
    - 長いので `namespace fs = std::filesystem;` と別名を付けるのが定番。
    - 失敗すると**例外**を投げる関数が多い。例外を使わないなら `std::error_code` を渡す版を使う。

!!! info "このページを読む前に"
    [ファイル入出力](../../basics/file-io.md) に、ファイルの読み書きとあわせた使い方の入門があります。

## 主な型

| 型 | 重要度 | 何を表す |
| --- | --- | --- |
| [`path`](#path) | <span class="rank rank-must">必須</span> | パス（ファイル・フォルダの場所） |
| [`directory_entry`](#directory_entry) | <span class="rank rank-often">よく使う</span> | フォルダの中の 1 項目（パス + 種類・大きさなどの情報） |
| [`directory_iterator`](#directory_iterator) | <span class="rank rank-often">よく使う</span> | フォルダの中身を回す |
| [`recursive_directory_iterator`](#recursive_directory_iterator) | <span class="rank rank-sometimes">たまに</span> | サブフォルダも含めて回す |
| [`filesystem_error`](#filesystem_error) | <span class="rank rank-sometimes">たまに</span> | 失敗したときの例外 |
| [`file_time_type`](#last_write_time) | <span class="rank rank-rare">知ってるだけ</span> | 更新日時 |
| [`space_info`](#space) | <span class="rank rank-rare">知ってるだけ</span> | ディスクの空き容量 |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`exists`](#exists) | <span class="rank rank-must">必須</span> | ファイル・フォルダがあるか |
| [`create_directories`](#create_directories) | <span class="rank rank-must">必須</span> | フォルダを作る（途中のフォルダも全部） |
| [`directory_iterator`](#directory_iterator) | <span class="rank rank-often">よく使う</span> | フォルダの中身を回す |
| [`remove`](#remove) | <span class="rank rank-often">よく使う</span> | ファイル・空のフォルダを消す |
| [`rename`](#rename) | <span class="rank rank-often">よく使う</span> | 名前の変更・移動 |
| [`is_regular_file`](#is_regular_file) | <span class="rank rank-often">よく使う</span> | 普通のファイルか |
| [`is_directory`](#is_directory) | <span class="rank rank-often">よく使う</span> | フォルダか |
| [`file_size`](#file_size) | <span class="rank rank-often">よく使う</span> | ファイルの大きさ（バイト） |
| [`copy_file`](#copy_file) | <span class="rank rank-sometimes">たまに</span> | ファイルをコピー |
| [`remove_all`](#remove_all) | <span class="rank rank-sometimes">たまに</span> | フォルダを中身ごと消す |
| [`current_path`](#current_path) | <span class="rank rank-sometimes">たまに</span> | 今の作業フォルダ |
| [`last_write_time`](#last_write_time) | <span class="rank rank-sometimes">たまに</span> | 最終更新日時 |
| [`recursive_directory_iterator`](#recursive_directory_iterator) | <span class="rank rank-sometimes">たまに</span> | サブフォルダも含めて回す |
| [`absolute`](#absolute) | <span class="rank rank-sometimes">たまに</span> | 絶対パスにする |
| [`relative`](#relative) | <span class="rank rank-sometimes">たまに</span> | 相対パスにする |
| [`create_directory`](#create_directory) | <span class="rank rank-rare">知ってるだけ</span> | フォルダを 1 つだけ作る |
| [`copy`](#copy) | <span class="rank rank-rare">知ってるだけ</span> | ファイル・フォルダをコピー |
| [`temp_directory_path`](#temp_directory_path) | <span class="rank rank-rare">知ってるだけ</span> | 一時フォルダの場所 |
| [`canonical`](#canonical) | <span class="rank rank-rare">知ってるだけ</span> | `..` などを解決した正式なパス |
| [`equivalent`](#equivalent) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのパスが同じファイルか |
| [`space`](#space) | <span class="rank rank-rare">知ってるだけ</span> | ディスクの容量・空き |
| [`resize_file`](#resize_file) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの大きさを変える |
| [`status`](#status) | <span class="rank rank-rare">知ってるだけ</span> | 種類・権限などの情報 |
| [`permissions`](#permissions) | <span class="rank rank-rare">知ってるだけ</span> | 権限を変える |

## よくある使い方

### 1. セーブ用のフォルダを用意して保存する

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path save_dir = "saves";
  fs::create_directories(save_dir);  // 無ければ作る（あれば何もしない）

  fs::path file = save_dir / "slot1.dat";  // saves/slot1.dat
  std::ofstream(file) << "level=3";

  std::println("保存した: {} ({} バイト)", file.generic_string(), fs::file_size(file));
}
```

```text title="実行結果"
保存した: saves/slot1.dat (7 バイト)
```

### 2. フォルダの中の画像を全部探す

```cpp
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <print>
#include <string>
#include <vector>

namespace fs = std::filesystem;

int main() {
  fs::create_directories("assets");
  for (const char* name : {"player.png", "enemy.png", "bgm.ogg"}) {
    std::ofstream(fs::path("assets") / name);
  }

  std::vector<std::string> images;
  for (const fs::directory_entry& entry : fs::directory_iterator("assets")) {
    if (entry.is_regular_file() && entry.path().extension() == ".png") {
      images.push_back(entry.path().filename().string());
    }
  }
  std::ranges::sort(images);  // 回す順番は決まっていないので並べる
  std::println("{}", images);
}
```

```text title="実行結果"
["enemy.png", "player.png"]
```

### 3. パスを分解する

```cpp
#include <filesystem>
#include <print>

int main() {
  std::filesystem::path p = "assets/textures/player.png";
  std::println("ファイル名: {}", p.filename().string());
  std::println("拡張子なし: {}", p.stem().string());
  std::println("拡張子: {}", p.extension().string());
  std::println("親フォルダ: {}", p.parent_path().string());
}
```

```text title="実行結果"
ファイル名: player.png
拡張子なし: player
拡張子: .png
親フォルダ: assets/textures
```

## 型と関数の詳しい説明

### path {#path}

```cpp
class path;
```

パスを表す型です。文字列から作れて、`/` でつなげられます。区切り文字（`/` と `\`）の違いを吸収してくれます。

| メンバ | 重要度 | 何をする | `"assets/img/player.png"` の例 |
| --- | --- | --- | --- |
| `operator/` | <span class="rank rank-must">必須</span> | パスをつなげる | `fs::path("assets") / "img"` |
| `filename()` | <span class="rank rank-must">必須</span> | ファイル名 | `player.png` |
| `extension()` | <span class="rank rank-must">必須</span> | 拡張子（`.` 付き） | `.png` |
| `stem()` | <span class="rank rank-often">よく使う</span> | 拡張子なしのファイル名 | `player` |
| `parent_path()` | <span class="rank rank-often">よく使う</span> | 親フォルダ | `assets/img` |
| `string()` | <span class="rank rank-often">よく使う</span> | `std::string` に変換（OS の区切り文字） | Windows なら `\` になることも |
| `generic_string()` | <span class="rank rank-often">よく使う</span> | `/` 区切りの `std::string` | `assets/img/player.png` |
| `replace_extension(".jpg")` | <span class="rank rank-sometimes">たまに</span> | 拡張子を変える | `assets/img/player.jpg` |
| `has_extension()` など `has_*` | <span class="rank rank-sometimes">たまに</span> | その部分があるか | `true` |
| `is_absolute()` / `is_relative()` | <span class="rank rank-sometimes">たまに</span> | 絶対パスか | `false` / `true` |
| `operator+=` | <span class="rank rank-sometimes">たまに</span> | 区切りを入れずに後ろに足す | `p += ".tmp"` |
| `lexically_normal()` | <span class="rank rank-rare">知ってるだけ</span> | `a/./b/../c` を `a/c` に整える | |
| `begin()` / `end()` | <span class="rank rank-rare">知ってるだけ</span> | 区切りごとに回す | `assets`, `img`, `player.png` |
| `u8string()` | <span class="rank rank-rare">知ってるだけ</span> | UTF-8 の文字列（`std::u8string`） | |
| `native()` | <span class="rank rank-rare">知ってるだけ</span> | OS 固有の文字列（Windows は `std::wstring`） | |

```cpp
#include <filesystem>
#include <print>

int main() {
  std::filesystem::path p = "saves";
  p /= "slot1";               // saves/slot1
  p += ".dat";                // saves/slot1.dat（区切りなしで足す）
  auto backup = p;
  backup.replace_extension(".bak");
  std::println("{} {}", p.generic_string(), backup.generic_string());
  std::println("{}", std::filesystem::path("a/./b/../c").lexically_normal().generic_string());
}
```

```text title="実行結果"
saves/slot1.dat saves/slot1.bak
a/c
```

!!! warning "Windows で日本語のパス"
    Windows では、日本語を含むパスを `string()` で取り出すと文字化けや例外になることがあります。表示用には `generic_u8string()` や、Visual Studio の `/utf-8` オプションを使います。ファイルを開くときは `path` をそのまま `std::ifstream` に渡せば問題ありません。

### exists {#exists}

```cpp
bool exists(const path& p);
bool exists(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `ec` | `std::error_code&` | 失敗したときにエラーが入る（例外を投げない版） |

- 戻り値: ファイルかフォルダがあれば `true`

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  if (!fs::exists("config.json")) {
    std::println("設定ファイルが無いのでデフォルトを使う");
  }
}
```

```text title="実行結果"
設定ファイルが無いのでデフォルトを使う
```

### create_directories {#create_directories}

```cpp
bool create_directories(const path& p);
bool create_directories(const path& p, std::error_code& ec);
```

- `p` までのフォルダを、途中のものも含めて全部作ります
- 戻り値: 新しく作ったら `true`、すでにあったら `false`（エラーではない）

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::create_directories("logs/2026/10"));
  std::println("{}", fs::create_directories("logs/2026/10"));  // 2 回目は作らない
}
```

```text title="実行結果"
true
false
```

### directory_iterator {#directory_iterator}

```cpp
class directory_iterator;
explicit directory_iterator(const path& p);
directory_iterator(const path& p, directory_options options);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 中身を見たいフォルダ |
| `options` | `directory_options` | 権限の無いフォルダを飛ばす、など（[フラグ](#フラグオプション)） |

- 範囲 for で回すと、`directory_entry` が 1 つずつ出てきます
- **順番は決まっていない**（名前順にしたいなら集めてから sort）
- `.` と `..` は出てこない

### recursive_directory_iterator {#recursive_directory_iterator}

```cpp
class recursive_directory_iterator;
```

- サブフォルダの中まで全部たどります。`depth()` で今の深さ、`disable_recursion_pending()` で「このフォルダには入らない」ができます

```cpp
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <print>
#include <string>
#include <vector>

namespace fs = std::filesystem;

int main() {
  fs::create_directories("data/stages");
  std::ofstream("data/items.json");
  std::ofstream("data/stages/1.json");

  std::vector<std::string> files;
  for (const auto& entry : fs::recursive_directory_iterator("data")) {
    if (entry.is_regular_file()) {
      files.push_back(entry.path().generic_string());
    }
  }
  std::ranges::sort(files);
  std::println("{}", files);
}
```

```text title="実行結果"
["data/items.json", "data/stages/1.json"]
```

### directory_entry {#directory_entry}

```cpp
class directory_entry;
```

| メンバ | 何をする |
| --- | --- |
| `path()` | パス |
| `is_regular_file()` / `is_directory()` | 種類 |
| `file_size()` | 大きさ |
| `last_write_time()` | 更新日時 |
| `exists()` | まだあるか |

- フォルダを回したときに取れる情報をまとめて持っているので、`fs::file_size(entry.path())` より `entry.file_size()` のほうが速いことがあります

### remove {#remove}

```cpp
bool remove(const path& p);
bool remove(const path& p, std::error_code& ec) noexcept;
```

- ファイルか**空の**フォルダを消します。戻り値は消したら `true`、無かったら `false`
- 中身のあるフォルダは消せない（例外）。[`remove_all`](#remove_all) を使う

### rename {#rename}

```cpp
void rename(const path& old_p, const path& new_p);
void rename(const path& old_p, const path& new_p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `old_p` | `const path&` | 元のパス |
| `new_p` | `const path&` | 新しいパス（別のフォルダなら移動になる） |

- `new_p` にファイルがあると**上書き**されます（壊れない保存に使える。[ファイル入出力](../../basics/file-io.md#壊れない保存一時ファイル--rename)）

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("slot.tmp") << "new data";
  fs::rename("slot.tmp", "slot.dat");  // 書き終わってから置き換える
  std::println("{} {}", fs::exists("slot.tmp"), fs::exists("slot.dat"));
  fs::remove("slot.dat");
  std::println("{}", fs::exists("slot.dat"));
}
```

```text title="実行結果"
false true
false
```

### is_regular_file {#is_regular_file}

```cpp
bool is_regular_file(const path& p);
```

- 普通のファイルなら `true`（フォルダやリンクは `false`）

### is_directory {#is_directory}

```cpp
bool is_directory(const path& p);
```

- フォルダなら `true`

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("music");
  std::ofstream("readme.txt");
  std::println("{} {}", fs::is_directory("music"), fs::is_regular_file("music"));
  std::println("{} {}", fs::is_directory("readme.txt"), fs::is_regular_file("readme.txt"));
}
```

```text title="実行結果"
true false
false true
```

### file_size {#file_size}

```cpp
std::uintmax_t file_size(const path& p);
```

- ファイルの大きさ（バイト）。フォルダや存在しないファイルだと例外

### copy_file {#copy_file}

```cpp
bool copy_file(const path& from, const path& to);
bool copy_file(const path& from, const path& to, copy_options options);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `from` | `const path&` | コピー元 |
| `to` | `const path&` | コピー先 |
| `options` | `copy_options` | すでにあるときどうするか（[フラグ](#フラグオプション)） |

- 何も指定しないと、`to` がすでにあるとき**例外**になります

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("save.dat") << "data";
  fs::copy_file("save.dat", "save_backup.dat", fs::copy_options::overwrite_existing);
  std::println("{}", fs::file_size("save_backup.dat"));
}
```

```text title="実行結果"
4
```

### remove_all {#remove_all}

```cpp
std::uintmax_t remove_all(const path& p);
```

- フォルダを**中身ごと**消します。戻り値は消したファイル・フォルダの数

!!! warning
    パスを間違えると大事なフォルダを消してしまいます。空のパスや `"/"`、`".."` を渡さないよう、使う前に確認します。

### current_path {#current_path}

```cpp
path current_path();
void current_path(const path& p);
```

- 今の作業フォルダを取得・変更します。相対パスはここから探されます

!!! note "実際は"
    Visual Studio からデバッグ実行すると作業フォルダが exe の場所と違うことがあり、「ファイルが見つからない」原因になります。表示して確かめると早いです。

### last_write_time {#last_write_time}

```cpp
file_time_type last_write_time(const path& p);
```

- 最終更新日時。前回と比べて変わっていたら読み込み直す（ホットリロード）のに使えます

```cpp
#include <chrono>
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("shader.txt") << "v1";
  auto before = fs::last_write_time("shader.txt");
  fs::last_write_time("shader.txt", before + std::chrono::seconds(5));  // 書き換えたとする
  std::println("更新された？ {}", fs::last_write_time("shader.txt") != before);
}
```

```text title="実行結果"
更新された？ true
```

### absolute {#absolute}

```cpp
path absolute(const path& p);
```

- 作業フォルダを先頭に付けた絶対パスにします（ファイルが無くてもいい）

### relative {#relative}

```cpp
path relative(const path& p, const path& base = current_path());
```

- `base` から見た `p` の相対パスを返します。エディタでアセットのパスを保存するときに使えます

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::path asset = fs::current_path() / "assets" / "player.png";
  std::println("{}", fs::relative(asset).generic_string());
  std::println("{}", fs::absolute("x.txt").is_absolute());
}
```

```text title="実行結果"
assets/player.png
true
```

### create_directory {#create_directory}

```cpp
bool create_directory(const path& p);
```

- フォルダを 1 つだけ作ります。親フォルダが無いと失敗するので、普通は `create_directories` を使います

### copy {#copy}

```cpp
void copy(const path& from, const path& to, copy_options options = copy_options::none);
```

- ファイルでもフォルダでもコピーします。フォルダの中身まで全部なら `copy_options::recursive`

### temp_directory_path {#temp_directory_path}

```cpp
path temp_directory_path();
```

- OS の一時フォルダの場所を返します

### canonical {#canonical}

```cpp
path canonical(const path& p);
```

- `..` やシンボリックリンクを解決した正式な絶対パス。**ファイルが無いと例外**

### equivalent {#equivalent}

```cpp
bool equivalent(const path& p1, const path& p2);
```

- 2 つのパスが同じファイルを指しているか

### space {#space}

```cpp
space_info space(const path& p);
```

- `capacity`（全体）、`free`（空き）、`available`（使える空き）をバイトで返します。セーブ前に容量を確かめるのに使えます

### resize_file {#resize_file}

```cpp
void resize_file(const path& p, std::uintmax_t new_size);
```

- ファイルの大きさを変えます（足りない分は 0 で埋まる）

### status {#status}

```cpp
file_status status(const path& p);
```

- 種類（`type()`）と権限（`permissions()`）をまとめて取得します

### permissions {#permissions}

```cpp
void permissions(const path& p, perms prms, perm_options opts = perm_options::replace);
```

- 読み書き・実行の権限を変えます。ゲームではほぼ使いません

### filesystem_error {#filesystem_error}

```cpp
class filesystem_error : public std::system_error;
```

- 例外を投げる版の関数が失敗したときに投げられます。`path1()` / `path2()` で関係したパス、`what()` で説明が取れます

```cpp
#include <filesystem>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  try {
    std::println("{}", fs::file_size("no_such_file.dat"));
  } catch (const fs::filesystem_error& e) {
    std::println("失敗: {}", e.path1().string());
  }

  std::error_code ec;  // 例外を使わない版
  auto size = fs::file_size("no_such_file.dat", ec);
  std::println("エラーあり？ {} / size は -1 相当？ {}", static_cast<bool>(ec),
               size == static_cast<std::uintmax_t>(-1));
}
```

```text title="実行結果"
失敗: no_such_file.dat
エラーあり？ true / size は -1 相当？ true
```

## フラグ・オプション

### copy_options

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `none` | <span class="rank rank-often">よく使う</span> | 何もしない（すでにあるとエラー） |
| `overwrite_existing` | <span class="rank rank-often">よく使う</span> | すでにあれば上書き |
| `recursive` | <span class="rank rank-sometimes">たまに</span> | フォルダの中身も全部コピー |
| `skip_existing` | <span class="rank rank-sometimes">たまに</span> | すでにあれば何もしない |
| `update_existing` | <span class="rank rank-sometimes">たまに</span> | コピー元のほうが新しければ上書き |
| `directories_only` | <span class="rank rank-rare">知ってるだけ</span> | フォルダの構造だけコピー |
| `copy_symlinks` / `skip_symlinks` | <span class="rank rank-rare">知ってるだけ</span> | シンボリックリンクの扱い |
| `create_symlinks` / `create_hard_links` | <span class="rank rank-rare">知ってるだけ</span> | コピーの代わりにリンクを作る |

`|` で組み合わせられます（`recursive | overwrite_existing`）。

### directory_options

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `none` | <span class="rank rank-often">よく使う</span> | デフォルト |
| `skip_permission_denied` | <span class="rank rank-sometimes">たまに</span> | 権限の無いフォルダを飛ばす（エラーにしない） |
| `follow_directory_symlink` | <span class="rank rank-rare">知ってるだけ</span> | リンク先のフォルダにも入る |

### file_type（`status(p).type()` の値）

| 値 | 意味 |
| --- | --- |
| `regular` | 普通のファイル |
| `directory` | フォルダ |
| `not_found` | 存在しない |
| `symlink` | シンボリックリンク |
| `block` / `character` / `fifo` / `socket` / `unknown` | 特殊なファイル（ゲームでは見ない） |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    // OS ごとに違う関数
    CreateDirectoryA("saves", nullptr);   // Windows
    mkdir("saves", 0755);                 // Linux / Mac
    std::string path = dir + "\\" + name; // 区切り文字を手で書く
    ```

=== "今の書き方（C++17）"

    ```cpp
    std::filesystem::create_directories("saves");
    std::filesystem::path path = dir / name;
    ```

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| セーブフォルダの作成 | `create_directories` |
| セーブスロットの一覧 | `directory_iterator` + 拡張子で絞り込み |
| アセットの一括読み込み | `recursive_directory_iterator` |
| 壊れない保存 | 一時ファイルに書いて `rename` |
| ホットリロード | `last_write_time` |
| ログの整理 | 古いファイルを `remove` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 失敗する操作（存在しないファイルの `file_size` など） | `filesystem_error` 例外（`error_code` 版ならエラーが入る） |
| 回している最中にそのフォルダの中身を変える | どの項目が出てくるか決まっていない |

## よくあるミス

??? failure "区切り文字を文字列で足す"
    `dir.string() + "/" + name` より `dir / name` のほうが、OS の違いや二重の `/` を気にしなくて済みます。

??? failure "directory_iterator の順番に頼る"
    名前順に出てくるとは限りません（OS やファイルシステムによる）。並べたいなら集めてから `sort` します。

??? failure "例外を考えずに使う"
    ファイルが無いだけで例外が飛んでゲームが落ちることがあります。`exists` で確かめるか、`std::error_code` 版を使います。

## 理解度チェック

!!! question "Q1. `fs::path(\"save/slot2.dat\")` の `stem()` と `extension()` は？"
    <div class="spoiler" markdown>

    **答え:** `slot2` と `.dat`。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::fstream`](fstream.md) | ファイルの中身を読み書きする |
| OS の API（`CreateFile` など） | OS ごとに違う。filesystem で足りないときだけ |

## コンパイラ対応

C++17 の機能です。主要なコンパイラすべてで使えます（古い GCC 8 では `-lstdc++fs` のリンクが必要でした）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] パスは `fs::path`、つなげるのは `/`
    - [x] `exists`・`create_directories`・`directory_iterator`・`remove`・`rename`
    - [x] 失敗すると例外。使わないなら `std::error_code` 版

## 関連ページ

- [ファイル入出力](../../basics/file-io.md)
- [cpprefjp: <filesystem>](https://cpprefjp.github.io/reference/filesystem.html)
- [cppreference: Filesystem library](https://en.cppreference.com/w/cpp/filesystem)

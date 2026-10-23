---
title: std::filesystem
summary: "ファイルやフォルダの存在確認・一覧・コピー・削除。パスの扱い。"
order: 64
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

セーブ用のフォルダを作る、フォルダの中の画像を全部探す、ファイルの拡張子を調べる。ファイルの中身ではなく、ファイルやフォルダそのものを扱う処理は、ゲームの起動時やツール側で頻繁に必要になります。文字列でパスをつないで OS ごとの関数を呼ぶ書き方は、移植性がなく、間違えやすくなります。`std::filesystem` は、パスの組み立て、存在確認、フォルダの作成と削除、一覧、コピーや名前の変更を、OS に依存せずに行うライブラリです。

!!! tip "ポイント"
    - パスは文字列ではなく **`std::filesystem::path`** で持ち、`/` でつなげる（`dir / "save.dat"`）。
    - よく使うのは `exists`、`create_directories`、`directory_iterator`、`remove`、`rename`。
    - 長いので `namespace fs = std::filesystem;` と別名を付けるのが定番。
    - 失敗すると**例外**を投げる関数が多い。例外を使わないなら `std::error_code` を渡す版を使う。

!!! info "このページを読む前に"
    [ファイル入出力](../../basics/file-io.md) に、ファイルの読み書きとあわせた使い方の入門があります。

## 主な型

| 型 | 重要度 | 何を表す |
| --- | --- | --- |
| [`path`](filesystem/path.md) | <span class="rank rank-must">必須</span> | パス（ファイル・フォルダの場所） |
| [`directory_entry`](filesystem/directory_entry.md) | <span class="rank rank-often">よく使う</span> | フォルダの中の 1 項目（パス + 種類・大きさなどの情報） |
| [`directory_iterator`](filesystem/directory_iterator.md) | <span class="rank rank-often">よく使う</span> | フォルダの中身を回す |
| [`recursive_directory_iterator`](filesystem/recursive_directory_iterator.md) | <span class="rank rank-sometimes">たまに</span> | サブフォルダも含めて回す |
| [`filesystem_error`](filesystem/filesystem_error.md) | <span class="rank rank-sometimes">たまに</span> | 失敗したときの例外 |
| [`file_time_type`](filesystem/last_write_time.md) | <span class="rank rank-rare">知ってるだけ</span> | 更新日時 |
| [`space_info`](filesystem/space.md) | <span class="rank rank-rare">知ってるだけ</span> | ディスクの空き容量 |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`exists`](filesystem/exists.md) | <span class="rank rank-must">必須</span> | ファイル・フォルダがあるか |
| [`create_directories`](filesystem/create_directories.md) | <span class="rank rank-must">必須</span> | フォルダを作る（途中のフォルダも全部） |
| [`directory_iterator`](filesystem/directory_iterator.md) | <span class="rank rank-often">よく使う</span> | フォルダの中身を回す |
| [`remove`](filesystem/remove.md) | <span class="rank rank-often">よく使う</span> | ファイル・空のフォルダを消す |
| [`rename`](filesystem/rename.md) | <span class="rank rank-often">よく使う</span> | 名前の変更・移動 |
| [`is_regular_file`](filesystem/is_regular_file.md) | <span class="rank rank-often">よく使う</span> | 普通のファイルか |
| [`is_directory`](filesystem/is_directory.md) | <span class="rank rank-often">よく使う</span> | フォルダか |
| [`file_size`](filesystem/file_size.md) | <span class="rank rank-often">よく使う</span> | ファイルの大きさ（バイト） |
| [`copy_file`](filesystem/copy_file.md) | <span class="rank rank-sometimes">たまに</span> | ファイルをコピー |
| [`remove_all`](filesystem/remove_all.md) | <span class="rank rank-sometimes">たまに</span> | フォルダを中身ごと消す |
| [`current_path`](filesystem/current_path.md) | <span class="rank rank-sometimes">たまに</span> | 今の作業フォルダ |
| [`last_write_time`](filesystem/last_write_time.md) | <span class="rank rank-sometimes">たまに</span> | 最終更新日時 |
| [`recursive_directory_iterator`](filesystem/recursive_directory_iterator.md) | <span class="rank rank-sometimes">たまに</span> | サブフォルダも含めて回す |
| [`absolute`](filesystem/absolute.md) | <span class="rank rank-sometimes">たまに</span> | 絶対パスにする |
| [`relative`](filesystem/relative.md) | <span class="rank rank-sometimes">たまに</span> | 相対パスにする |
| [`create_directory`](filesystem/create_directory.md) | <span class="rank rank-rare">知ってるだけ</span> | フォルダを 1 つだけ作る |
| [`copy`](filesystem/copy.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイル・フォルダをコピー |
| [`temp_directory_path`](filesystem/temp_directory_path.md) | <span class="rank rank-rare">知ってるだけ</span> | 一時フォルダの場所 |
| [`canonical`](filesystem/canonical.md) | <span class="rank rank-rare">知ってるだけ</span> | `..` などを解決した正式なパス |
| [`equivalent`](filesystem/equivalent.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのパスが同じファイルか |
| [`space`](filesystem/space.md) | <span class="rank rank-rare">知ってるだけ</span> | ディスクの容量・空き |
| [`resize_file`](filesystem/resize_file.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの大きさを変える |
| [`status`](filesystem/status.md) | <span class="rank rank-rare">知ってるだけ</span> | 種類・権限などの情報 |
| [`permissions`](filesystem/permissions.md) | <span class="rank rank-rare">知ってるだけ</span> | 権限を変える |

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

## フラグ・オプション

### copy_options

[`copy_options`](filesystem/copy_options.md)（`copy` の動作の指定）を参照してください。

### directory_options

[`directory_options`](filesystem/directory_options.md)（フォルダの走査の動作の指定）を参照してください。

### file_type

[`file_type`](filesystem/file_type.md)（`status(p).type()` の値）を参照してください。

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

セーブデータの保存先の準備が基本です。`create_directories` で保存先フォルダを作り、`exists` で既存のセーブを調べ、`rename` で一時ファイルから本番のファイルへ置き換えます。

アセットの探索にも使います。`recursive_directory_iterator` でフォルダの中を再帰的にたどり、拡張子が `.png` のファイルを集めます。ホットリロード（ファイルの更新を検知して読み直す）では、`last_write_time` で更新時刻を比べます。

パスの扱いは `std::filesystem::path` を使い、`/` でつなげます。文字列に直すのは、外部のライブラリに渡すときだけです。多くの関数は失敗すると例外を投げますが、`std::error_code` を渡す版を使えば、例外なしで結果を受け取れます。

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

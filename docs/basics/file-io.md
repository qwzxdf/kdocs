---
title: ファイル入出力
tags:
  - 基礎
---

# ファイル入出力

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <fstream>` / `#include <filesystem>`
</div>

ゲームでは、セーブデータ、設定、ステージデータなどをファイルに読み書きします。C++ では、**`std::ofstream` で書き込み、`std::ifstream` で読み込み**ます。ファイルの存在確認やフォルダの作成、パスの組み立ては **`std::filesystem`**（C++17）で行います。テキスト（人が読める文字）で保存するか、バイナリ（メモリの中身そのまま）で保存するかで書き方が変わります。

!!! tip "ポイント"
    - テキストの書き込みは `std::ofstream out("save.txt"); out << ...;`、読み込みは `std::ifstream` + `std::getline`。
    - バイナリは `std::ios::binary` を付けて、`write` / `read` で読み書きする。
    - **開けたかどうか必ず確認する**（`if (!file)`）。
    - パスは `std::filesystem::path` で組み立てる（`dir / "save.dat"`）。
    - 本格的なセーブデータは [シリアライズ](../engine/serialization/index.md) の仕組み（JSON ライブラリなど）を使う。

!!! info "このページを読む前に"
    - [basics/index.md](index.md)（このセクション全体の地図と、読む順番）

## 基本

### テキストを書いて読む

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <string>

int main() {
  const std::filesystem::path path = "config.txt";

  {
    std::ofstream out(path);  // 書き込み用に開く（既にあれば上書き）
    out << "volume=80\n";
    out << "fullscreen=1\n";
  }  // スコープを抜けると自動で閉じる

  std::ifstream in(path);
  if (!in) {
    std::println("開けなかった");
    return 1;
  }
  std::string line;
  while (std::getline(in, line)) {  // 1 行ずつ読む
    std::println("読んだ: {}", line);
  }
}
```

```text title="実行結果"
読んだ: volume=80
読んだ: fullscreen=1
```

### バイナリで書いて読む

```cpp
#include <cstdint>
#include <fstream>
#include <print>

struct SaveHeader {
  std::uint32_t version;
  std::int32_t stage;
  std::int32_t score;
};

int main() {
  SaveHeader save = {1, 3, 12800};
  {
    std::ofstream out("save.dat", std::ios::binary);
    out.write(reinterpret_cast<const char*>(&save), sizeof(save));
  }

  SaveHeader loaded{};
  std::ifstream in("save.dat", std::ios::binary);
  in.read(reinterpret_cast<char*>(&loaded), sizeof(loaded));
  std::println("v{} stage {} score {}", loaded.version, loaded.stage, loaded.score);
}
```

```text title="実行結果"
v1 stage 3 score 12800
```

!!! warning "構造体をそのまま書くのは小さいデータまで"
    この方法は手軽ですが、`std::string` や `std::vector`、ポインタを含む構造体には使えません（中身ではなくアドレスが保存される）。また、コンパイラや CPU が変わると読めなくなることがあります。[シリアライズ](../engine/serialization/index.md) を参照してください。

## 詳しく

### 開くときのモード（フラグ）

| フラグ | 重要度 | 意味 |
| --- | --- | --- |
| `std::ios::in` | <span class="rank rank-must">必須</span> | 読み込み（ifstream のデフォルト） |
| `std::ios::out` | <span class="rank rank-must">必須</span> | 書き込み（ofstream のデフォルト）。既存の中身は消える |
| `std::ios::binary` | <span class="rank rank-must">必須</span> | バイナリモード（改行コードの変換をしない） |
| `std::ios::app` | <span class="rank rank-often">よく使う</span> | 末尾に追記する（ログファイル） |
| `std::ios::trunc` | <span class="rank rank-sometimes">たまに</span> | 開くときに中身を空にする（out のデフォルトの動き） |
| `std::ios::ate` | <span class="rank rank-rare">知ってるだけ</span> | 開いた直後に末尾へ移動する |

組み合わせは `|` でつなぎます（`std::ios::out | std::ios::binary`）。

```cpp
#include <fstream>
#include <print>
#include <string>

int main() {
  std::ofstream("log.txt") << "起動\n";                        // 新規作成
  std::ofstream("log.txt", std::ios::app) << "ステージ 1\n";   // 追記
  std::ofstream("log.txt", std::ios::app) << "クリア\n";

  std::ifstream in("log.txt");
  std::string line;
  while (std::getline(in, line)) {
    std::println("{}", line);
  }
}
```

```text title="実行結果"
起動
ステージ 1
クリア
```

### ファイル全体を一度に読む

```cpp
#include <fstream>
#include <print>
#include <sstream>
#include <string>

std::string ReadAll(const char* path) {
  std::ifstream in(path, std::ios::binary);
  std::ostringstream ss;
  ss << in.rdbuf();  // 全部を文字列ストリームに流し込む
  return ss.str();
}

int main() {
  std::ofstream("stage.txt") << "##..\n#..#\n";
  std::string text = ReadAll("stage.txt");
  std::println("{} バイト読んだ", text.size());
}
```

```text title="実行結果"
10 バイト読んだ
```

### std::filesystem <span class="ver ver-17">C++17</span> {#stdfilesystem data-toc-label="std::filesystem"}

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| `std::filesystem::path` | <span class="rank rank-must">必須</span> | パスの型。`/` でつなげる |
| `exists(p)` | <span class="rank rank-must">必須</span> | ファイル・フォルダがあるか |
| `create_directories(p)` | <span class="rank rank-often">よく使う</span> | フォルダを作る（途中のフォルダも全部） |
| `directory_iterator(p)` | <span class="rank rank-often">よく使う</span> | フォルダの中身を回す |
| `remove(p)` | <span class="rank rank-often">よく使う</span> | ファイルを消す |
| `file_size(p)` | <span class="rank rank-sometimes">たまに</span> | ファイルの大きさ |
| `p.extension()` / `p.stem()` / `p.filename()` | <span class="rank rank-sometimes">たまに</span> | 拡張子 / 拡張子なしの名前 / ファイル名 |
| `rename(from, to)` | <span class="rank rank-sometimes">たまに</span> | 名前を変える（安全な保存に使う） |
| `copy_file(from, to)` | <span class="rank rank-sometimes">たまに</span> | コピー |
| `recursive_directory_iterator(p)` | <span class="rank rank-sometimes">たまに</span> | サブフォルダも含めて回す |
| `last_write_time(p)` | <span class="rank rank-rare">知ってるだけ</span> | 最終更新日時（ホットリロード） |
| `current_path()` | <span class="rank rank-rare">知ってるだけ</span> | 今の作業フォルダ |

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path dir = "saves";
  fs::create_directories(dir);

  fs::path file = dir / "slot1.dat";  // saves/slot1.dat
  std::ofstream(file) << "data";

  std::println("あるか: {} / 名前: {} / 拡張子: {} / {} バイト", fs::exists(file),
               file.stem().string(), file.extension().string(), fs::file_size(file));

  for (const auto& entry : fs::directory_iterator(dir)) {
    std::println("見つけた: {}", entry.path().filename().string());
  }
}
```

```text title="実行結果"
あるか: true / 名前: slot1 / 拡張子: .dat / 4 バイト
見つけた: slot1.dat
```

### 壊れない保存（一時ファイル → rename）

保存の途中でゲームが落ちると、セーブデータが半分だけ書かれた状態で壊れます。**一時ファイルに書き終えてから名前を変える**と、古いデータか新しいデータのどちらかが必ず残ります。

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

bool SafeSave(const fs::path& path, const std::string& data) {
  fs::path tmp = path;
  tmp += ".tmp";
  {
    std::ofstream out(tmp, std::ios::binary);
    if (!out.write(data.data(), static_cast<std::streamsize>(data.size()))) {
      return false;
    }
  }
  fs::rename(tmp, path);  // 置き換えは一瞬で終わる
  return true;
}

int main() {
  std::println("{}", SafeSave("slot.dat", "score=100"));
}
```

```text title="実行結果"
true
```

## ゲームでの例

| 場面 | 方法 |
| --- | --- |
| 設定ファイル | テキスト（`key=value`）か JSON |
| セーブデータ | バイナリ + バージョン番号、または JSON（[シリアライズ](../engine/serialization/index.md)） |
| ステージデータ | テキスト（文字でマップを書く）や JSON、専用のバイナリ |
| ログ | `std::ios::app` で追記 |
| アセット一覧 | `directory_iterator` でフォルダの中身を回す |

## よくあるミス

??? failure "開けたか確認しない"
    パスが間違っていても、`std::ifstream` は例外を投げずに「失敗した状態」になるだけです。そのまま読むと空の値が入ります。`if (!in)` で確認します。

??? failure "作業フォルダの違いでファイルが見つからない"
    Visual Studio から実行すると、作業フォルダがプロジェクトのフォルダになり、exe と同じ場所にあるファイルが見つからないことがあります。`std::filesystem::current_path()` を表示して確かめます。

??? failure "バイナリなのに std::ios::binary を付け忘れる"
    Windows では、テキストモードだと `\n` が `\r\n` に変換され、バイナリデータが壊れます。

??? failure "std::string を含む構造体を write する"
    string の中身はヒープにあるので、`write` で保存されるのはポインタの値だけです。読み込むと壊れた string になります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書くのは `std::ofstream`、読むのは `std::ifstream`
    - [x] 開けたか `if (!file)` で確認
    - [x] バイナリは `std::ios::binary`、追記は `std::ios::app`
    - [x] パスは `std::filesystem::path` と `/`

## 関連ページ

- [シリアライズ](../engine/serialization/index.md)
- [cpprefjp: std::filesystem](https://cpprefjp.github.io/reference/filesystem.html)
- [cppreference: std::basic_fstream](https://en.cppreference.com/w/cpp/io/basic_fstream)

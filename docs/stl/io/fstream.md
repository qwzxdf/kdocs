---
title: std::ifstream / std::ofstream
tags:
  - 入出力
---

# std::ifstream / std::ofstream

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <fstream>`
</div>

`std::ifstream` は**ファイルを読む**ため、`std::ofstream` は**ファイルに書く**ための型です（読み書き両方なら `std::fstream`）。`std::cout` と同じ `<<` / `>>` で書けて、`std::getline` で 1 行ずつ読めます。バイナリデータは `write` / `read` で扱います。開くときのモード（フラグ）で、上書きか追記か、テキストかバイナリかを選びます。

!!! tip "ポイント"
    - 書くなら `std::ofstream out(path);`、読むなら `std::ifstream in(path);`。
    - **開けたか必ず `if (!in)` で確かめる**（失敗しても例外は出ない）。
    - 1 行ずつ読むのは `while (std::getline(in, line))`。
    - バイナリは `std::ios::binary` を付けて `write` / `read`。追記は `std::ios::app`。
    - スコープを抜けると自動で閉じる。`close()` は普通は書かなくていい。

!!! info "このページを読む前に"
    [ファイル入出力](../../basics/file-io.md) に入門があります。パスの扱いは [`std::filesystem`](filesystem.md) を見てください。

## 主な型

| 型 | 重要度 | 何をする |
| --- | --- | --- |
| `std::ifstream` | <span class="rank rank-must">必須</span> | 読み込み専用 |
| `std::ofstream` | <span class="rank rank-must">必須</span> | 書き込み専用 |
| `std::fstream` | <span class="rank rank-rare">知ってるだけ</span> | 読み書き両方 |

## 関数一覧

| 関数 | 重要度 | 対象 | 何をする |
| --- | --- | --- | --- |
| [コンストラクタ（開く）](#open) | <span class="rank rank-must">必須</span> | 両方 | パスとモードを指定して開く |
| [`operator bool`](#bool) | <span class="rank rank-must">必須</span> | 両方 | 開けていて、エラーが無いか |
| [`operator!`](#not) | <span class="rank rank-must">必須</span> | 両方 | 開けなかった・エラーが起きたか |
| [`operator<<`](#shift-out) | <span class="rank rank-must">必須</span> | ofstream | テキストを書く |
| [`std::getline`](#getline) | <span class="rank rank-must">必須</span> | ifstream | 1 行読む |
| [`operator>>`](#shift-in) | <span class="rank rank-often">よく使う</span> | ifstream | 空白区切りで値を読む |
| [`write`](#write) | <span class="rank rank-often">よく使う</span> | ofstream | バイナリで書く |
| [`read`](#read) | <span class="rank rank-often">よく使う</span> | ifstream | バイナリで読む |
| [`is_open`](#is_open) | <span class="rank rank-sometimes">たまに</span> | 両方 | 開いているか |
| [`close`](#close) | <span class="rank rank-sometimes">たまに</span> | 両方 | 閉じる |
| [`gcount`](#gcount) | <span class="rank rank-sometimes">たまに</span> | ifstream | 直前の `read` で読めたバイト数 |
| [`eof`](#eof) | <span class="rank rank-sometimes">たまに</span> | ifstream | 終わりまで読んだか |
| [`seekg`](#seekg) | <span class="rank rank-sometimes">たまに</span> | ifstream | 読む位置を移動 |
| [`tellg`](#tellg) | <span class="rank rank-sometimes">たまに</span> | ifstream | 今の読む位置 |
| [`rdbuf`](#rdbuf) | <span class="rank rank-sometimes">たまに</span> | 両方 | 中身を丸ごと流し込む |
| [`flush`](#flush) | <span class="rank rank-rare">知ってるだけ</span> | ofstream | たまった中身をすぐ書き出す |
| [`seekp`](#seekp) | <span class="rank rank-rare">知ってるだけ</span> | ofstream | 書く位置を移動 |
| [`tellp`](#tellp) | <span class="rank rank-rare">知ってるだけ</span> | ofstream | 今の書く位置 |
| [`clear`](#clear) | <span class="rank rank-rare">知ってるだけ</span> | 両方 | エラー状態を消す |
| [`open`](#open-member) | <span class="rank rank-rare">知ってるだけ</span> | 両方 | あとから開く |

## よくある使い方

### 1. 設定を書いて読む

```cpp
#include <fstream>
#include <print>
#include <string>

int main() {
  {
    std::ofstream out("config.ini");
    out << "volume=" << 80 << '\n';
    out << "name=Alice\n";
  }  // ここで閉じられて書き出される

  std::ifstream in("config.ini");
  if (!in) {
    std::println("開けなかった");
    return 1;
  }
  std::string line;
  while (std::getline(in, line)) {
    auto eq = line.find('=');
    std::println("[{}] = [{}]", line.substr(0, eq), line.substr(eq + 1));
  }
}
```

```text title="実行結果"
[volume] = [80]
[name] = [Alice]
```

### 2. 空白区切りの数値を読む

```cpp
#include <fstream>
#include <print>
#include <vector>

int main() {
  std::ofstream("stage.txt") << "3 4\n1 0 0 1\n0 1 1 0\n1 1 1 1\n";

  std::ifstream in("stage.txt");
  int height = 0;
  int width = 0;
  in >> height >> width;  // 空白・改行を飛ばして数値を読む
  std::vector<int> tiles(height * width);
  for (int& t : tiles) {
    in >> t;
  }
  std::println("{}x{} {}", height, width, tiles);
}
```

```text title="実行結果"
3x4 [1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1]
```

### 3. バイナリで書いて読む

```cpp
#include <cstdint>
#include <fstream>
#include <print>
#include <vector>

int main() {
  std::vector<std::int32_t> scores = {980, 870, 860};
  {
    std::ofstream out("scores.bin", std::ios::binary);
    auto count = static_cast<std::uint32_t>(scores.size());
    out.write(reinterpret_cast<const char*>(&count), sizeof(count));
    out.write(reinterpret_cast<const char*>(scores.data()), scores.size() * sizeof(std::int32_t));
  }

  std::ifstream in("scores.bin", std::ios::binary);
  std::uint32_t count = 0;
  in.read(reinterpret_cast<char*>(&count), sizeof(count));
  std::vector<std::int32_t> loaded(count);
  in.read(reinterpret_cast<char*>(loaded.data()), count * sizeof(std::int32_t));
  std::println("{}", loaded);
}
```

```text title="実行結果"
[980, 870, 860]
```

## 関数の詳しい説明

### コンストラクタ（開く） {#open}

```cpp
explicit ifstream(const std::filesystem::path& p, std::ios::openmode mode = std::ios::in);
explicit ofstream(const std::filesystem::path& p, std::ios::openmode mode = std::ios::out);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | パス（文字列や `fs::path`） | 開くファイル |
| `mode` | `std::ios::openmode` | 開き方（[フラグ](#フラグオプション)） |

- ofstream は、ファイルが無ければ作り、あれば**中身を消して**開きます（`app` を付けると追記）
- 開けなくても例外は出ません。必ず確かめます

### operator bool {#bool}

```cpp
explicit operator bool() const;
```

- 開けていて、エラーが起きていなければ `true`。読み込みで最後まで行ったときは `false` になります
- `while (in >> x)`、`while (std::getline(in, line))` の形で使います

### operator! {#not}

```cpp
bool operator!() const;
```

- 開けなかった・エラーが起きたなら `true`。`if (!in)` の形で使います

```cpp
#include <fstream>
#include <print>

int main() {
  std::ifstream in("no_such_file.txt");
  if (!in) {
    std::println("開けなかった");
  }
}
```

```text title="実行結果"
開けなかった
```

### operator<< {#shift-out}

```cpp
ostream& operator<<(int value);  // 数値・文字列・文字などの型ごとにある
```

- 値を文字にして書きます。つなげて書けます。数値の書き方は [iostream の書式フラグ](iostream.md#フラグオプション書式フラグとマニピュレータ) で変えられます

!!! note "実際は"
    数値と文字列を混ぜて書くなら、`out << std::format("HP {}/{}
", hp, max_hp);` のほうが読みやすいです。C++23 では `std::println(out, ...)` で ofstream にも直接書けます（`<ostream>`）。

### std::getline {#getline}

```cpp
std::istream& getline(std::istream& in, std::string& str, char delim = '\n');
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `in` | `std::istream&` | 読み込み元 |
| `str` | `std::string&` | 読んだ行が入る（改行は含まない） |
| `delim` | `char` | 区切り文字（省略すると改行） |

- 戻り値の `in` は、読めなくなると `false` 扱いになるので `while` に書けます
- Windows で作ったファイルを読むと、行の最後に `'\r'` が残ることがあります

### operator>> {#shift-in}

```cpp
istream& operator>>(int& value);  // 型ごとにある
```

- 空白・タブ・改行を飛ばしてから、次の値を読みます。読めなかったら失敗状態になります
- 文字列（`std::string`）に読むと、空白までの 1 単語になります

!!! warning "`>>` と `getline` を混ぜるとき"
    `in >> n;` のあとに `std::getline(in, line);` すると、数値の後ろに残った改行だけを読んで空行になります。間に `in >> std::ws;`（空白を読み飛ばす）を入れます。

### write {#write}

```cpp
ostream& write(const char* s, std::streamsize count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const char*` | 書くデータの先頭（`reinterpret_cast<const char*>(&value)`） |
| `count` | `std::streamsize` | バイト数 |

- メモリの中身をそのまま書きます。`std::ios::binary` で開いておきます

### read {#read}

```cpp
istream& read(char* s, std::streamsize count);
```

- `count` バイト読み込みます。足りなければ失敗状態になり、`gcount()` で実際に読めた数が分かります

### is_open {#is_open}

```cpp
bool is_open() const;
```

- ファイルを開いているか。`if (!in)` とほぼ同じですが、こちらはエラー状態を見ません

### close {#close}

```cpp
void close();
```

- 閉じます。デストラクタで自動的に閉じるので、普通は書きません。同じ変数で別のファイルを開き直すときに使います

### gcount {#gcount}

```cpp
std::streamsize gcount() const;
```

- 直前の `read` / `getline` で読めた文字（バイト）数

### eof {#eof}

```cpp
bool eof() const;
```

- 終わりを越えて読もうとしたら `true`

!!! warning "while (!in.eof()) は使わない"
    最後の行を読んだ直後はまだ `eof()` が `false` なので、もう 1 回ループして空の値を処理してしまいます。`while (std::getline(in, line))` の形で書きます。

### seekg {#seekg}

```cpp
istream& seekg(std::streamoff off, std::ios::seekdir dir);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `off` | `std::streamoff` | 移動量 |
| `dir` | `std::ios::seekdir` | 基準（`beg` 先頭 / `cur` 今の位置 / `end` 末尾） |

### tellg {#tellg}

```cpp
pos_type tellg();
```

- 今の読む位置。`seekg(0, std::ios::end)` してから `tellg()` するとファイルの大きさが分かります

```cpp
#include <fstream>
#include <print>
#include <string_view>

int main() {
  std::ofstream("data.bin", std::ios::binary) << "ABCDEFGH";
  std::ifstream in("data.bin", std::ios::binary);
  in.seekg(0, std::ios::end);
  auto size = static_cast<long long>(in.tellg());
  in.seekg(2, std::ios::beg);  // 3 バイト目へ
  char buf[3] = {};
  in.read(buf, 3);
  std::println("大きさ {} / 読んだ {} バイト: {}", size, in.gcount(), std::string_view(buf, 3));
}
```

```text title="実行結果"
大きさ 8 / 読んだ 3 バイト: CDE
```

### rdbuf {#rdbuf}

```cpp
std::filebuf* rdbuf() const;
```

- 中のバッファを返します。`out << in.rdbuf();` でファイルの中身を丸ごと流し込めます（コピーや全部読み込みに使う）

```cpp
#include <fstream>
#include <print>
#include <sstream>

int main() {
  std::ofstream("story.txt") << "むかしむかし\nあるところに\n";
  std::ifstream in("story.txt");
  std::stringstream ss;
  ss << in.rdbuf();  // 全部読み込む
  std::println("{} バイト", ss.str().size());
}
```

```text title="実行結果"
38 バイト
```

### flush {#flush}

```cpp
ostream& flush();
```

- まだ書き出されていない中身をすぐにファイルへ書きます。ログを書いた直後に落ちても残るようにしたいときに使います（`std::endl` も flush します）

### seekp {#seekp}

```cpp
ostream& seekp(std::streamoff off, std::ios::seekdir dir);
```

- 書く位置を移動します。ヘッダの「データ数」をあとから書き直すときなどに使います

### tellp {#tellp}

```cpp
pos_type tellp();
```

- 今の書く位置（ここまでに書いたバイト数）

### clear {#clear}

```cpp
void clear(iostate state = goodbit);
```

- エラー状態（`failbit` や `eofbit`）を消します。最後まで読んだあとに `seekg` で戻って読み直すときに必要です

### open {#open-member}

```cpp
void open(const std::filesystem::path& p, std::ios::openmode mode = /* in / out */);
```

- コンストラクタで開かなかったとき、あとから開きます

## フラグ・オプション

### openmode（開き方）

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `std::ios::in` | <span class="rank rank-must">必須</span> | 読み込み（ifstream のデフォルト） |
| `std::ios::out` | <span class="rank rank-must">必須</span> | 書き込み（ofstream のデフォルト。中身は消える） |
| `std::ios::binary` | <span class="rank rank-must">必須</span> | バイナリ。改行コードを変換しない |
| `std::ios::app` | <span class="rank rank-often">よく使う</span> | 必ず末尾に追記する |
| `std::ios::trunc` | <span class="rank rank-sometimes">たまに</span> | 開くときに中身を消す |
| `std::ios::ate` | <span class="rank rank-rare">知ってるだけ</span> | 開いた直後に末尾へ移動（その後は好きな場所に書ける） |
| `std::ios::noreplace` | <span class="rank rank-rare">知ってるだけ</span> | すでにファイルがあれば開くのに失敗する <span class="ver ver-23">C++23</span> |

### seekdir（移動の基準）

| 値 | 意味 |
| --- | --- |
| `std::ios::beg` | 先頭から |
| `std::ios::cur` | 今の位置から |
| `std::ios::end` | 末尾から |

### iostate（状態）

| 値 | 意味 | 調べる関数 |
| --- | --- | --- |
| `goodbit` | 問題なし | `good()` |
| `eofbit` | 終わりまで読んだ | `eof()` |
| `failbit` | 読み取り・変換に失敗した（数字の所に文字があった、など） | `fail()` |
| `badbit` | 読み書きそのものができない深刻なエラー | `bad()` |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    FILE* fp = fopen("save.dat", "rb");
    if (fp) {
      fread(&data, sizeof(data), 1, fp);
      fclose(fp);  // 忘れるとファイルが開きっぱなし
    }
    ```

=== "今の書き方"

    ```cpp
    std::ifstream in("save.dat", std::ios::binary);
    if (in) {
      in.read(reinterpret_cast<char*>(&data), sizeof(data));
    }  // 自動で閉じる
    ```

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| 設定・ステージのテキスト | `getline` / `>>` |
| ログ | `std::ios::app` で追記、`flush` |
| セーブデータ | `binary` + `write` / `read`（[シリアライズ](../../engine/serialization/index.md)） |
| ファイル全体の読み込み | `rdbuf` |

## よくあるミス

??? failure "開けたか確かめない"
    パスが違っても例外は出ず、読み込んだ値が全部 0 や空になります。

??? failure "バイナリなのに binary を付けない"
    Windows ではデータの中の `\n`（0x0A）が `\r\n` に変換され、壊れます。

??? failure "while (!in.eof())"
    最後の要素を 2 回処理してしまいます。`while (std::getline(in, line))` か `while (in >> x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stringstream`](sstream.md) | ファイルではなく文字列に対して同じ操作をする |
| [`std::filesystem`](filesystem.md) | ファイルそのもの（存在、コピー、削除）を扱う |
| `FILE*`（`fopen`） | C の関数。閉じ忘れに注意 |

## コンパイラ対応

C++98 からある機能です。`fs::path` で開けるのは C++17、`noreplace` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読むのは ifstream、書くのは ofstream
    - [x] 開けたか確認
    - [x] 行は `while (std::getline(in, line))`
    - [x] バイナリは `std::ios::binary`、追記は `std::ios::app`

## 関連ページ

- [ファイル入出力](../../basics/file-io.md)
- [cpprefjp: basic_fstream](https://cpprefjp.github.io/reference/fstream/basic_fstream.html)
- [cppreference: std::basic_fstream](https://en.cppreference.com/w/cpp/io/basic_fstream)

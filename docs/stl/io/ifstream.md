---
title: std::ifstream
summary: "ファイルを読むための型（テキスト・バイナリ）。"
order: 65
tags:
  - 入出力・文字列
---

# std::ifstream

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <fstream>`
</div>

`std::ifstream` は、**ファイルを読む**ための型です。`std::cin` と同じ `>>` や `std::getline` で読めます。バイナリは `read` で読みます。スコープを抜けると、自動でファイルを閉じます。書くほうは [`std::ofstream`](ofstream.md) です。

!!! tip "ポイント"
    - `std::ifstream in(path);` で開く。**開けたかを必ず `if (!in)` で確かめる**（失敗しても例外は出ない）。
    - 1 行ずつ読むのは `while (std::getline(in, line))`。
    - バイナリは `std::ios::binary` を付けて `read`。
    - 閉じ忘れの心配はない（デストラクターで閉じる）。

!!! info "このページを読む前に"
    [ファイル入出力](../../basics/file-io.md) に入門があります。パスの扱いは [`std::filesystem`](filesystem.md) を見てください。

## 関数の詳しい説明

### コンストラクタ（開く） {#open}

```cpp
explicit ifstream(const std::filesystem::path& p, std::ios::openmode mode = std::ios::in);
explicit ofstream(const std::filesystem::path& p, std::ios::openmode mode = std::ios::out);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | パス（文字列や `fs::path`） | 開くファイル |
| `mode` | `std::ios::openmode` | 開き方（[フラグ](#flags)） |

- ofstream は、ファイルが無ければ作り、あれば**中身を消して**開きます（`app` を付けると追記）
- 開けなくても例外は出ません。必ず確かめます

### operator bool {#bool}

```cpp
explicit operator bool() const;
```

- 開けていて、エラーが起きていなければ `true`。読み込みで最後まで行ったときは `false` になります
- `while (in >> x)`、`while (std::getline(in, line))` の形で使います

### operator>> {#shift-in}

```cpp
istream& operator>>(int& value);  // 型ごとにある
```

- 空白・タブ・改行を飛ばしてから、次の値を読みます。読めなかったら失敗状態になります
- 文字列（`std::string`）に読むと、空白までの 1 単語になります

!!! warning "`>>` と `getline` を混ぜるとき"
    `in >> n;` のあとに `std::getline(in, line);` すると、数値の後ろに残った改行だけを読んで空行になります。間に `in >> std::ws;`（空白を読み飛ばす）を入れます。

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

## フラグ・オプション {#flags}

`std::ios::openmode` は、ファイルの開き方を決めるビットマスクです。`|` で組み合わせます。`ifstream` の既定は `in` です。

### std::ios::in

読み込みで開きます。ファイルが無いと開けません。

### std::ios::out

書き込みで開きます。`ifstream` に付けると読み書きになりますが、普通は `fstream` を使います。

### std::ios::binary

バイナリ モードです。付けないテキスト モードでは、Windows が `
` と `
` を相互に変換します。画像やセーブ データなど、バイト列をそのまま読むときは必ず付けます。

### std::ios::ate

開いた直後に、読み書き位置をファイルの終わりへ動かします（at end）。ファイルの大きさを `tellg()` で調べるときに使います。

### std::ios::app

書くたびに、必ず終わりへ追記します。`ifstream` で読むときは使いません。

### std::ios::trunc

開いたときに、中身を消します。

### std::ios::noreplace <span class="ver ver-23">C++23</span>

`out` と一緒に使うと、ファイルがすでにあるときに開くのを失敗させます。上書き事故を避けたいときの指定です。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイル・セーブデータの読み込み | `std::ifstream in("save.dat"); std::getline(in, line)` |
| バイナリのアセットを読む | `in.read(buffer, size)` |

## よくあるミス

??? failure "開けたか確認しない"
    存在しないファイルを開いても例外は出ません。`if (!in)` で確かめないと、空のデータを読み続けます。

??? failure "while (!in.eof()) で読む"
    最後の1行で余分にループします。`while (std::getline(in, line))` か `while (in >> x)` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ofstream`](ofstream.md) | 書く |
| [`std::fstream`](fstream.md) | 読み書き両方 |
| [`std::filesystem`](filesystem.md) | パス・存在確認 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルを読む型
    - [x] 開けたかを必ず確認
    - [x] 1 行は `getline`

## 関連ページ

- [cpprefjp: std::ifstream](https://cpprefjp.github.io/reference/fstream/basic_ifstream.html)
- [cppreference: std::basic_ifstream](https://en.cppreference.com/w/cpp/io/basic_ifstream)

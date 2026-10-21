---
title: std::ofstream
summary: "ファイルに書くための型（テキスト・バイナリ）。"
order: 66
tags:
  - 入出力・文字列
---

# std::ofstream

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <fstream>`
</div>

`std::ofstream` は、**ファイルに書く**ための型です。`std::cout` と同じ `<<` で書けます。バイナリは `write` で書きます。開くと中身は消えます（`std::ios::app` を付けると追記）。読むほうは [`std::ifstream`](ifstream.md) です。

!!! tip "ポイント"
    - `std::ofstream out(path);` で開く（既存の中身は消える）。
    - 追記は `std::ios::app`、バイナリは `std::ios::binary`。
    - **開けたかを必ず `if (!out)` で確かめる**。
    - スコープを抜けると、たまった中身を書き出して閉じる。

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

### operator<< {#shift-out}

```cpp
ostream& operator<<(int value);  // 数値・文字列・文字などの型ごとにある
```

- 値を文字にして書きます。つなげて書けます。数値の書き方は [iostream の書式フラグ](cout.md#shift-out) で変えられます

!!! note "実際は"
    数値と文字列を混ぜて書くなら、`out << std::format("HP {}/{}\n", hp, max_hp);` のほうが読みやすいです。C++23 では `std::println(out, ...)` で ofstream にも直接書けます（`<ostream>`）。

### write {#write}

```cpp
ostream& write(const char* s, std::streamsize count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const char*` | 書くデータの先頭（`reinterpret_cast<const char*>(&value)`） |
| `count` | `std::streamsize` | バイト数 |

- メモリの中身をそのまま書きます。`std::ios::binary` で開いておきます

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

## フラグ・オプション {#flags}

`std::ios::openmode` は、ファイルの開き方を決めるビットマスクです。`|` で組み合わせます。`ofstream` の既定は `out` で、`out` 単独は中身を消して開きます（`trunc` が付いたのと同じ）。

### std::ios::out

書き込みで開きます。ファイルが無ければ作ります。`app` や `in` が付かない `out` は、すでにある中身を消します。

### std::ios::app

書くたびに、必ず終わりへ追記します。ログ ファイルはこれです。`out | app` と書くのが普通です。

### std::ios::trunc

開いたときに中身を消します。`out` だけのときの動作を明示したいときに付けます。

### std::ios::ate

開いた直後に、書き込み位置をファイルの終わりへ動かします。`app` と違って、`seekp` で途中へ戻せます。中身を消さずに書き足したいときは、`out | ate` ではなく `out | in | ate` にします（`out` だけだと中身が消えます）。

### std::ios::binary

バイナリ モードです。付けないテキスト モードでは、Windows が `
` を `
` に変換して書きます。セーブ データなどのバイト列は必ず付けます。

### std::ios::noreplace <span class="ver ver-23">C++23</span>

ファイルがすでにあるときは、開くのを失敗させます。上書き事故を避けたいときの指定です。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの書き出し | `std::ofstream out("save.dat", std::ios::binary);` |
| ログファイルへの追記 | `std::ofstream log("log.txt", std::ios::app);` |

## よくあるミス

??? failure "書き込みが終わる前にプログラムが落ちる"
    バッファにたまった中身は、閉じる（または `flush`）まで書き出されません。大事なデータは書いたら `flush()` するか、スコープを抜けて閉じます。

??? failure "出力先のフォルダが無い"
    `ofstream` はフォルダを作りません。先に `std::filesystem::create_directories` で用意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ifstream`](ifstream.md) | 読む |
| [`std::fstream`](fstream.md) | 読み書き両方 |
| [`std::filesystem`](filesystem.md) | フォルダを作る |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルに書く型
    - [x] 既存の中身は消える（追記は `app`）
    - [x] 開けたかを確認

## 関連ページ

- [cpprefjp: std::ofstream](https://cpprefjp.github.io/reference/fstream/basic_ofstream.html)
- [cppreference: std::basic_ofstream](https://en.cppreference.com/w/cpp/io/basic_ofstream)

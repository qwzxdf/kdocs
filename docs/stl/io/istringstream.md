---
title: std::istringstream
summary: "文字列から、値を読み出す（読む専用）。"
order: 81
tags:
  - 入出力・文字列
---

# std::istringstream

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <sstream>`
</div>

設定の 1 行 `"hp 100 mp 50"` を単語や数値に分けたい。`find` と `substr` を繰り返すと、読みにくくなります。`std::istringstream` は、文字列を入力ストリームとして読む型です。`std::cin` や `ifstream` と同じ `>>` や `getline` で読めます。コマンドを単語に分ける、1 行の中の値を取り出す、といった処理に向いています。

!!! tip "ポイント"
    - `std::istringstream in("12 abc 3.5");` で作って、`in >> n >> word >> x;`。
    - 読みに失敗すると `failbit` が立つ。`if (in >> n)` で確かめる。
    - 文字列の分割だけなら [`views::split`](../algorithms/views/split.md) も使える。

!!! info "このページを読む前に"
    [`std::stringstream`](stringstream.md) の仲間です。ファイルの読み書きは [`std::ifstream`](ifstream.md) を見てください。

## 関数の詳しい説明

### std::istringstream {#istringstream}

```cpp
class istringstream {
 public:
  explicit istringstream(const std::string& str);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 読みたい文字列 |

- 戻り値: （クラス）。`>>` や `std::getline` で読める
- 計算量: O(読む量)

```cpp
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream in("12 sword 3.5");

  int id = 0;
  std::string name;
  double rate = 0.0;
  in >> id >> name >> rate;
  std::println("{} {} {}", id, name, rate);
}
```

```text title="実行結果"
12 sword 3.5
```

### str {#str}

```cpp
std::string str() const;
void str(const std::string& s);
```

- 計算量: O(長さ)

中の文字列のコピーを返します。引数つきの版は、中の文字列を置き換え、読み書きの位置を先頭に戻します。

### rdbuf {#rdbuf}

```cpp
std::stringbuf* rdbuf() const;
```

- 計算量: 定数

中のバッファ（`stringbuf`）へのポインタ。

### swap {#swap}

```cpp
void swap(istringstream& other);
```

- 計算量: 定数

中身（バッファとストリームの状態）を入れ替えます。

### view <span class="ver ver-20">C++20</span> {#view data-toc-label="view"}

```cpp
std::string_view view() const noexcept;
```

- 計算量: 定数

中の文字列をコピーせずに `string_view` で見ます。ストリームに書き込むと無効になります。

## ゲームでの使いどころ

コマンドの解析に使います。`std::istringstream in(line); std::string cmd; int arg; in >> cmd >> arg;` と書けば、「move 10」のような入力を分解できます。

読み込み処理のテストにも便利です。ファイルを用意せず、文字列を渡すだけで、`std::istream` を受け取る関数を試せます。

単純な区切りでの分割なら、`views::split` のほうが軽く書けます。`istringstream` は、型の違う値が並んでいる文字列を型ごとに読み分けるときに向いています。

## よくあるミス

??? failure "型が合わず読めない"
    数字のところに文字があると、`failbit` が立って以降が読めません。

??? failure "読みに失敗しても気づかない"
    型が合わないと `failbit` が立ち、以降の読み込みも失敗します。`if (in >> n)` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stringstream`](stringstream.md) | 読み書き両方 |
| [`std::from_chars`](from_chars.md) | 数値への変換だけなら、こちらが速い |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列から読む
    - [x] `>>` と `getline`
    - [x] 失敗は `failbit`

## 関連ページ

- [cpprefjp: std::istringstream](https://cpprefjp.github.io/reference/sstream/basic_istringstream.html)
- [cppreference: std::basic_istringstream](https://en.cppreference.com/w/cpp/io/basic_istringstream)

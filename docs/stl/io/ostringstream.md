---
title: std::ostringstream
summary: "値をつなげて、文字列を組み立てる（書く専用）。"
order: 82
tags:
  - 入出力・文字列
---

# std::ostringstream

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <sstream>`
</div>

`std::ostringstream` は、**`<<` で値をつなげて、1 つの文字列を組み立てる**型です。`str()` で組み立てた文字列を取り出せます。新しいコードでは [`std::format`](../utilities/format.md) のほうが簡単ですが、古いコードでよく出てきます。

!!! tip "ポイント"
    - `std::ostringstream os; os << "HP " << hp; os.str()`。
    - 再利用するときは `os.str("")` で空にする。
    - 桁や幅は [`setw`](setw.md) などで指定する。

!!! info "このページを読む前に"
    [`std::stringstream`](stringstream.md) の仲間です。ファイルの読み書きは [`std::ifstream`](ifstream.md) を見てください。

## 関数の詳しい説明

### std::ostringstream {#ostringstream}

```cpp
class ostringstream {
 public:
  explicit ostringstream(std::ios::openmode mode = std::ios::out);
  std::string str() const;
};
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `mode` | `openmode` | 開き方 | `out` |

- 戻り値: （クラス）。`str()` で組み立てた文字列を取り出す
- 計算量: O(書く量)

```cpp
#include <print>
#include <sstream>

int main() {
  std::ostringstream os;
  os << "HP " << 45 << '/' << 120;
  std::println("[{}]", os.str());
}
```

```text title="実行結果"
[HP 45/120]
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
void swap(ostringstream& other);
```

- 計算量: 定数

中身（バッファとストリームの状態）を入れ替えます。

### view <span class="ver ver-20">C++20</span> {#view data-toc-label="view"}

```cpp
std::string_view view() const noexcept;
```

- 計算量: 定数

中の文字列を、コピーせずに `string_view` で見ます。ストリームに書き込むと無効になります。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログ 1 行の組み立て（古い書き方） | `os << a << b;` |

## よくあるミス

??? failure "毎フレーム作り直して遅い"
    作るたびにメモリを確保します。使い回して `str("")` で空にするか、`std::format` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](../utilities/format.md) | 書式つきで組み立てる（推奨） |
| [`std::stringstream`](stringstream.md) | 読み書き両方 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値をつなげて文字列にする
    - [x] `str()` で取り出す
    - [x] 新しいコードは `format`

## 関連ページ

- [cpprefjp: std::ostringstream](https://cpprefjp.github.io/reference/sstream/basic_ostringstream.html)
- [cppreference: std::basic_ostringstream](https://en.cppreference.com/w/cpp/io/basic_ostringstream)

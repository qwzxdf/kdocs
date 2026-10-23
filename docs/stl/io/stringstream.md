---
title: std::stringstream
summary: "文字列を、ストリームとして読み書きする（分解・組み立て）。"
order: 80
tags:
  - 入出力・文字列
---

# std::stringstream

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <sstream>`
</div>

文字列を組み立てたり、文字列から値を取り出したりしたい。`std::stringstream` は、文字列をストリームとして読み書きできる型です。`<<` で値をつなげて文字列を作り、`>>` や `getline` で文字列から値を取り出せます。読むだけの `istringstream`、書くだけの `ostringstream` もあります。

!!! tip "ポイント"
    - ファイルを使わずに、読み込み処理をテストできる（文字列を渡すだけ）。
    - 文字列の組み立ては [`std::format`](../utilities/format.md) のほうが短くて速い。
    - 中身を空にするのは `str("")`。`clear()` はエラー状態を消すだけ。

!!! info "このページを読む前に"
    [`std::ifstream`](ifstream.md) や [`std::cout`](cout.md) など、ストリームの基本を先に読んでください。

## 関数の詳しい説明

### コンストラクタ {#constructor}

```cpp
explicit istringstream(const std::string& str);
explicit ostringstream(std::ios::openmode mode = std::ios::out);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 読むための中身 |
| `mode` | `openmode` | `std::ios::ate` を付けると、最初の中身の後ろに追記する |

### str {#str}

```cpp
std::string str() const;
void str(const std::string& s);
```

- 引数なしで、中の文字列のコピーを返します。引数ありで、中身を入れ替えます

### operator>> {#shift-in}

```cpp
std::istream& operator>>(int& value);  // 型ごとにある
```

- 空白を飛ばして次の値を読みます。読めなければ失敗状態になります

### operator<< {#shift-out}

```cpp
std::ostream& operator<<(int value);  // 型ごとにある
```

- 値を文字にして後ろに書き足します

```cpp
#include <print>
#include <sstream>

int main() {
  std::ostringstream os;
  os << "HP " << 45 << '/' << 120;
  std::println("[{}]", os.str());
  os.str("");  // 中身を空にして使い回す
  os << "reset";
  std::println("[{}]", os.str());
}
```

```text title="実行結果"
[HP 45/120]
[reset]
```

### std::getline {#getline}

```cpp
std::istream& getline(std::istream& in, std::string& str, char delim = '\n');
```

- `delim` の手前までを読みます。区切り文字を `','` にすると CSV の列を分けられます

### view {#view}

<span class="ver ver-20">C++20</span>

```cpp
std::string_view view() const noexcept;
```

- 中の文字列をコピーせずに見ます。ストリームを変更すると無効になります

### clear {#clear}

```cpp
void clear(std::ios::iostate state = std::ios::goodbit);
```

- エラー状態を消します。**中身は消えません**（中身を空にするのは `str("")`）

```cpp
#include <print>
#include <sstream>
#include <string_view>

int main() {
  std::istringstream in("abc");
  int n = 0;
  in >> n;
  std::println("失敗？ {}", in.fail());
  in.clear();
  std::println("失敗？ {} / 中身 {}", in.fail(), in.view());
}
```

```text title="実行結果"
失敗？ true
失敗？ false / 中身 abc
```

### rdbuf {#rdbuf}

```cpp
std::stringbuf* rdbuf() const;
```

- 計算量: 定数

中のバッファ（`stringbuf`）へのポインタ。

### swap {#swap}

```cpp
void swap(stringstream& other);
```

- 計算量: 定数

中身（バッファとストリームの状態）を入れ替えます。

## ゲームでの使いどころ

読み込み処理のテストで使います。ファイルを用意せず、文字列を `stringstream` に入れて、`std::istream&` を受け取る関数に渡せます。

文字列の組み立ては、`std::format` のほうが短く、速くなります。`stringstream` は、読み書きの両方が要るときや、ストリームの機能（マニピュレーター）を使いたいときに残ります。

中身を空にするのは `str("")` です。`clear()` は、エラー状態を消すだけです。ストリームは作成が重めなので、毎フレームのように大量に作るのは避けます。

## よくあるミス

??? failure "clear で中身が消えると思う"
    `clear()` はエラー状態を消すだけです。中身を空にするには `str("")` です。

??? failure "`clear()` で中身が消えると思う"
    `clear()` は、エラー状態をリセットするだけです。中身を空にするには `str("")` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::istringstream`](istringstream.md) | 読む専用 |
| [`std::ostringstream`](ostringstream.md) | 書く専用 |
| [`std::format`](../utilities/format.md) | 組み立てなら、こちらが簡単 |

## コンパイラ対応

C++98 から使えます。`view()` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列をストリームとして読み書きする
    - [x] 分解は `>>` と `getline`
    - [x] 組み立ては `format` が簡単

## 関連ページ

- [cpprefjp: std::stringstream](https://cpprefjp.github.io/reference/sstream/basic_stringstream.html)
- [cppreference: std::basic_stringstream](https://en.cppreference.com/w/cpp/io/basic_stringstream)

---
title: std::istreambuf_iterator
summary: "ストリームバッファから、1 文字ずつ生で読むイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::istreambuf_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

ファイルの内容を、まるごと `std::string` に読み込みたい。`istream_iterator<char>` は空白を飛ばしてしまいます。`std::istreambuf_iterator` は、<strong>ストリームのバッファから 1 文字ずつ、空白も含めてそのまま読む</strong>入力イテレーターです。

!!! tip "ポイント"
    - `std::istreambuf_iterator<char>(stream)` で作る
    - 空白や改行も含めて、1 文字ずつ読む
    - 引数なしで作ると、終端を表す
    - `std::string` のコンストラクターに範囲として渡せる

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::istreambuf_iterator {#istreambuf_iterator}

<span class="ver ver-98">C++98</span>

```cpp
template <class CharT>
class istreambuf_iterator {
 public:
  istreambuf_iterator();
  istreambuf_iterator(std::basic_istream<CharT>& stream) noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | 入力ストリーム | 読み取り元 |

`istream_iterator<char>` は、`>>` を使うので空白を読み飛ばします。`istreambuf_iterator` は、バッファを直接読むので、空白も改行もそのままです。ファイル全体を読む定番の書き方に使われます。

速度が必要な大きなファイルには、`std::ifstream::read` で一気に読むほうが速いです。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream input("a b\nc");
  const std::string text((std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>());
  std::println("文字数 = {}", text.size());   // 空白と改行も数える
}
```

```text title="実行結果"
文字数 = 5
```

## ゲームでの使いどころ

テキスト ファイルを、まるごと文字列に読み込みます。

```cpp
std::ifstream file("config.txt");
std::string text((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
```

## よくあるミス

??? failure "`istream_iterator<char>` で読んで空白が消える"
    `istreambuf_iterator` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ostreambuf_iterator`](ostreambuf_iterator.md) | 出力版 |
| [`istream_iterator`](istream_iterator.md) | 空白区切りで読む |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `istreambuf_iterator` は空白も含めて 1 文字ずつ読む
    - [x] ファイル全体を文字列に読む書き方に使う
    - [x] 大きなファイルは `read` が速い

## 関連ページ

- [cpprefjp: std::istreambuf_iterator](https://cpprefjp.github.io/reference/iterator/istreambuf_iterator.html)
- [cppreference: std::istreambuf_iterator](https://en.cppreference.com/w/cpp/iterator/istreambuf_iterator)

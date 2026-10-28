---
title: std::ostreambuf_iterator
summary: "ストリームバッファへ、1 文字ずつ生で書くイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::ostreambuf_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

文字を 1 文字ずつ、バッファに直接書き出したい。`std::ostreambuf_iterator` は、<strong>書式処理を通さず、ストリームのバッファに文字を書き込む</strong>出力イテレーターです。`std::copy` で文字列をそのまま流し込めます。

!!! tip "ポイント"
    - `std::ostreambuf_iterator<char>(stream)` で作る
    - 代入すると、1 文字ずつバッファに書かれる
    - 書式（幅、基数）の影響を受けない
    - `std::copy` の出力先に使える

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ostreambuf_iterator {#ostreambuf_iterator}

<span class="ver ver-98">C++98</span>

```cpp
template <class CharT>
class ostreambuf_iterator {
 public:
  ostreambuf_iterator(std::basic_ostream<CharT>& stream) noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | 出力ストリーム | 書き込み先 |

`*it = ch` は、バッファに 1 文字を書き込みます。`<<` を経由しないので、書式の設定が反映されず、その分は速く、予測しやすいです。書き込みに失敗したかは、`failed()` で調べられます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <sstream>
#include <string>

int main() {
  const std::string text = "abc";
  std::ostringstream out;
  std::copy(text.begin(), text.end(), std::ostreambuf_iterator<char>(out));
  std::println("{}", out.str());
}
```

```text title="実行結果"
abc
```

## ゲームでの使いどころ

文字列を、ストリームに流し込みます。通常は `stream << text` で足ります。

## よくあるミス

??? failure "書式の設定が効くと思う"
    書式を経由しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`istreambuf_iterator`](istreambuf_iterator.md) | 入力版 |
| [`ostream_iterator`](ostream_iterator.md) | 値を書式つきで書く |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ostreambuf_iterator` は 1 文字ずつバッファに書く
    - [x] 書式の設定の影響を受けない
    - [x] 通常は `<<` で足りる

## 関連ページ

- [cpprefjp: std::ostreambuf_iterator](https://cpprefjp.github.io/reference/iterator/ostreambuf_iterator.html)
- [cppreference: std::ostreambuf_iterator](https://en.cppreference.com/w/cpp/iterator/ostreambuf_iterator)

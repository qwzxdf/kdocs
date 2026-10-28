---
title: std::format_to
summary: "文字列を、既にある場所に書き込む。確保を減らしたいときに。"
order: 49
tags:
  - ユーティリティ
---

# std::format_to

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

毎フレーム文字列を作ると、`std::format` は新しい `std::string` を作るので、メモリの確保が毎回起きます。作った文字列をすでにあるバッファに書き込めれば、確保を減らせます。`std::format_to` は、`std::format` と同じ書式で、結果を新しい文字列ではなく、すでにある場所（バッファや出力イテレーター）に書き込む関数です。最大の文字数を決める `format_to_n` や、文字数だけを先に知る `formatted_size` も仲間です。

!!! tip "ポイント"
    - `std::format_to(std::back_inserter(str), "{}", x)` で、既存の `string` に追記する。
    - 決まった大きさの配列に書くなら `format_to_n`（あふれない）。
    - 先に必要な文字数を知りたいなら `formatted_size`。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) などは不要です。書式の指定は [std::format](format.md) のページにまとめてあります。

## 関数の詳しい説明

### std::format_to {#format_to}

```cpp
template <class OutputIt, class... Args>
OutputIt format_to(OutputIt out, std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き込み先（`std::back_inserter(str)` など） |

- 戻り値: 書き終わった次の位置
- 既にある文字列やバッファに書き足すので、毎回新しい文字列を作らずに済みます

```cpp
#include <format>
#include <iterator>
#include <print>
#include <string>

int main() {
  std::string log;
  log.reserve(64);
  for (int frame = 1; frame <= 3; ++frame) {
    std::format_to(std::back_inserter(log), "[{}]", frame);
  }
  std::println("{}", log);
}
```

```text title="実行結果"
[1][2][3]
```

## ゲームでの使いどころ

毎フレームの文字列の組み立てで、確保を減らすのに使います。`std::string buf;` を使い回し、`buf.clear(); std::format_to(std::back_inserter(buf), "FPS: {}", fps);` と書けば、バッファの容量が再利用されます。

決まった大きさの配列に書き込むなら、`format_to_n` を使います。あふれた分は捨てられ、安全です。固定長の `char buf[64]` に、HUD の文字列を作る、といった用途です。

先に必要な文字数を知りたいときは、`formatted_size` で数えられます。

## よくあるミス

??? failure "format_to でバッファがあふれる"
    `format_to` は大きさを確認しません。固定長の配列には `format_to_n` を使い、終端の `\0` も自分で付けます。

??? failure "固定長の配列に `format_to` で書いて、あふれる"
    `format_to` は書き込み先の大きさを検査しません。固定長の配列には `format_to_n` を使い、大きさを渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](format.md) | 新しい文字列を作る |
| [`std::print`](print.md) | 出力する |

## コンパイラ対応

C++20 の機能です。GCC 13 / Clang 17 / MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 既にある場所に書き込む
    - [x] 固定長なら `format_to_n`
    - [x] 文字数だけなら `formatted_size`

## 関連ページ

- [cpprefjp: std::format_to](https://cpprefjp.github.io/reference/format/format_to.html)
- [cppreference: std::format_to](https://en.cppreference.com/w/cpp/utility/format/format_to)

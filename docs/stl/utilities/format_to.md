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

`std::format_to` は、`std::format` と同じ書式で、**結果を新しい `std::string` ではなく、すでにある場所（バッファや出力イテレータ）に書き込む**関数です。メモリの確保を減らしたいときに使います。最大の文字数を決める `format_to_n`、文字数だけを調べる `formatted_size` も同じ仲間です。

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

| 場面 | 書き方 |
| --- | --- |
| 毎フレーム使うバッファに、HUD の文字列を書き込む | `std::format_to(buf, "HP {}/{}", hp, max_hp)` |
| 固定長のログバッファ | `std::format_to_n(buf, sizeof(buf) - 1, ...)` |

## よくあるミス

??? failure "format_to でバッファがあふれる"
    `format_to` は大きさを確認しません。固定長の配列には `format_to_n` を使い、終端の `\0` も自分で付けます。

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

---
title: std::format_to_n
summary: "最大 n 文字だけ、出力先に書式化して書き込む。"
order: 900
tags:
  - ユーティリティ
---

# std::format_to_n

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

固定長のバッファ（`char buf[64]`）に整形したいとき、`std::format_to` は、長さを確認せずに書き込むので、あふれる危険があります。`std::format_to_n(out, n, fmt, args...)` は、書き込む長さを最大 `n` 文字に制限します。戻り値で、「本来の長さ」が分かるので、足りたかどうかが確認できます。

!!! tip "ポイント"
    - 最大 `n` 文字まで書き込む。終端の `\0` は付かない
    - 戻り値の `size` が、本来の長さ。`n` を超えていたら、切り詰められた
    - 戻り値の `out` が、書き終えた位置
    - 終端が要るなら、自分で `\0` を書く

!!! info "このページを読む前に"
    [`std::format_to`](format_to.md) と [`std::formatted_size`](formatted_size.md) を先に読んでください。

## 関数の詳しい説明

### std::format_to_n {#format_to_n}

<span class="ver ver-20">C++20</span>

```cpp
template <class OutputIt, class... Args>
std::format_to_n_result<OutputIt>
format_to_n(OutputIt out, std::iter_difference_t<OutputIt> n,
            std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き込み先 |
| `n` | 整数 | 書き込む最大の文字数 |
| `fmt` | `std::format_string` | 書式文字列 |
| `args` | 任意 | 書式の引数 |

戻り値は `format_to_n_result` で、`out`（書き終えた位置）と `size`（整形結果の全体の長さ）を持ちます。`size` が `n` より大きければ、切り詰められています。

`n` 文字を超える部分は、書き込まれません。終端の `\0` も付かないので、`char` の配列に書くときは、`n` を配列の大きさ - 1 にして、終端を自分で書きます。

```cpp
char buf[16];
auto r = std::format_to_n(buf, sizeof(buf) - 1, "{}", value);
*r.out = '\0';
```

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string_view>

int main() {
  char buf[8];
  const auto r = std::format_to_n(buf, sizeof(buf) - 1, "{}", 123456789);
  *r.out = '\0';  // 終端を付ける

  std::println("全体の長さ: {}", r.size);
  std::println("書き込んだ文字: {}", std::string_view(buf));
  std::println("切り詰められた: {}", r.size > sizeof(buf) - 1);
}
```

```text title="実行結果"
全体の長さ: 9
書き込んだ文字: 1234567
切り詰められた: true
```

9 文字の結果が、7 文字に切り詰められています。

## ゲームでの使いどころ

固定長のバッファに、HUD の文字列を作るときに使います。あふれても、メモリを壊さずに、切り詰めで済みます。

## よくあるミス

??? failure "終端を付け忘れる"
    `format_to_n` は終端を書きません。文字列として使う前に、`\0` を足します。

??? failure "n を配列の大きさそのものにして、終端が書けない"
    `sizeof(buf) - 1` を渡して、最後の 1 文字分を終端用に残します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_to`](format_to.md) | 長さを制限しない |
| [`formatted_size`](formatted_size.md) | 全体の長さだけを求める |
| `std::snprintf` | C の同様の関数 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::format_to_n](https://cpprefjp.github.io/reference/format/format_to_n.html)
- [cppreference: std::format_to_n](https://en.cppreference.com/w/cpp/utility/format/format_to_n)

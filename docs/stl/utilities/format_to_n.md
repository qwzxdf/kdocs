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

固定長の `char` 配列に書式化したいとき、`format_to` は、配列の大きさを超えて書き込む危険があります。`format_to_n` は、書き込む文字数の上限を指定でき、はみ出しません。戻り値の `size` は、上限がなければ何文字になったかを教えてくれるので、切り捨てが起きたかが分かります。

!!! tip "ポイント"
    - 上限を超える分は書き込まれない。
    - 終端の `'\0'` は自分で付ける。
    - `result.size` が「本来の長さ」。`size > n` なら切り捨てられた。

!!! info "このページを読む前に"
    [`std::format`](format.md) と [`std::format_to`](format_to.md) を先に読んでください。

## 関数の詳しい説明

### std::format_to_n {#format_to_n}

```cpp
template <class OutputIt, class... Args>
format_to_n_result<OutputIt> format_to_n(OutputIt out, std::iter_difference_t<OutputIt> n, std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き込み先 |
| `n` | 整数 | 書き込む最大の文字数 |
| `fmt` | 書式文字列 | コンパイル時の定数 |
| `args...` | 値 | `{}` に入れる値 |

- 戻り値: `out`（書き終えた位置）と `size`（本来の文字数）をもつ構造体
- 計算量: O(書く文字数)


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  char buf[8] = {};
  auto result = std::format_to_n(buf, sizeof(buf) - 1, "Score:{}", 123456);
  std::println("[{}] 本来は {} 文字", buf, result.size);
}
```

```text title="実行結果"
[Score:1] 本来は 12 文字
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定長のバッファにはみ出さず書式化する | `std::format_to_n(buf, sizeof buf - 1, "Score:{}", s);` |

## よくあるミス

??? failure "終端文字を付け忘れる"
    `format_to_n` は終端を書きません。`*result.out = '\0';` で自分で付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_to`](format_to.md) | 上限なし |
| [`formatted_size`](formatted_size.md) | 長さだけ求める |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大 n 文字だけ書き込む
    - [x] 終端は自分で付ける
    - [x] size で切り捨てを検出

## 関連ページ

- [cpprefjp: std::format_to_n](https://cpprefjp.github.io/reference/format/format_to_n.html)
- [cppreference: std::format_to_n](https://en.cppreference.com/w/cpp/utility/format/format_to_n)

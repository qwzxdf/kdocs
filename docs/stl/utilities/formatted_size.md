---
title: std::formatted_size
summary: "書式化した結果が何文字になるかだけを返す（文字列は作らない）。"
order: 900
tags:
  - ユーティリティ
---

# std::formatted_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

書式化した文字列を、固定長のバッファに入れるとき、先に必要な大きさが分かれば、ちょうどの大きさで確保できます。`formatted_size` は、実際に文字列を作らずに、何文字になるかだけを返します。

!!! tip "ポイント"
    - 文字列は作らない（メモリ確保もしない）。
    - 戻り値は終端の `'\0'` を含まない文字数。
    - 確保してから `format_to` で書き込む、という使い方をする。

!!! info "このページを読む前に"
    [`std::format`](format.md) と [`std::format_to`](format_to.md) を先に読んでください。

## 関数の詳しい説明

### std::formatted_size {#formatted_size}

```cpp
template <class... Args>
std::size_t formatted_size(std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | 書式文字列 | コンパイル時の定数 |
| `args...` | 値 | `{}` に入れる値 |

- 戻り値: 書式化した結果の文字数
- 計算量: O(書く文字数)


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  std::println("{}", std::formatted_size("HP {}/{}", 45, 120));
}
```

```text title="実行結果"
9
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 書式化結果の大きさを先に求める | `std::string s(std::formatted_size("{}-{}", a, b), '\0');` |

## よくあるミス

??? failure "終端文字ぶんを足し忘れる"
    戻り値は終端を含みません。C の文字列にするなら 1 足します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_to_n`](format_to_n.md) | 上限つきで書き込む |
| [`format`](format.md) | 文字列を作る |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式化結果の文字数だけ返す
    - [x] 文字列は作らない
    - [x] 終端は含まない

## 関連ページ

- [cpprefjp: std::formatted_size](https://cpprefjp.github.io/reference/format/formatted_size.html)
- [cppreference: std::formatted_size](https://en.cppreference.com/w/cpp/utility/format/formatted_size)

---
title: std::to_chars_result
summary: "to_chars の結果（書き込み終えた位置とエラー）を表す構造体。"
order: 900
tags:
  - 入出力・文字列
---

# std::to_chars_result

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <charconv>`
</div>

`std::to_chars` は、例外を使わずに、結果を構造体で返します。`ptr` が書き込みを終えた位置、`ec` がエラーコードです。`ec` が `std::errc{}`（0）なら成功です。バッファが足りないと、`ec` が `value_too_large` になります。

!!! tip "ポイント"
    - `ptr`: 書き込みを終えた位置（失敗したら `last`）。
    - `ec`: エラーコード（成功なら 0）。
    - 構造化束縛で受けると読みやすい。

!!! info "このページを読む前に"
    [`std::to_chars`](to_chars.md) と [`std::from_chars`](from_chars.md) を先に読んでください。

## 関数の詳しい説明

### std::to_chars_result {#to_chars_result}

```cpp
struct to_chars_result {
  char* ptr;
  std::errc ec;
};
```

- 戻り値: `ptr` と `ec`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <charconv>
#include <print>
#include <string_view>

int main() {
  char buf[8];
  auto r = std::to_chars(buf, buf + 8, 123);
  std::println("{} {}", std::string_view(buf, r.ptr - buf), r.ec == std::errc{});
}
```

```text title="実行結果"
123 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 数値を速く文字列にする |

## よくあるミス

??? failure "バッファが足りないのを無視する"
    `ec` を確かめないと、途切れた文字列を使ってしまいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`from_chars_result`](from_chars_result.md) | 読み込み側 |
| [`to_chars`](to_chars.md) | 数値を文字列にする |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] to_chars の結果（書き込み終えた位置とエラー）を表す構造体
    - [x] `ptr`: 書き込みを終えた位置（失敗したら `last`）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::to_chars_result](https://cpprefjp.github.io/reference/charconv/to_chars_result.html)
- [cppreference: std::to_chars_result](https://en.cppreference.com/w/cpp/utility/to_chars_result)

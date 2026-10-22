---
title: std::from_chars_result
summary: "from_chars の結果（読み終えた位置とエラー）を表す構造体。"
order: 900
tags:
  - 入出力・文字列
---

# std::from_chars_result

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <charconv>`
</div>

`std::from_chars` は、例外を使わずに、結果を構造体で返します。`ptr` が読み終えた位置、`ec` がエラーコードです。`ec` が `std::errc{}`（0）なら成功、`invalid_argument` なら数字がない、`result_out_of_range` なら範囲外です。

!!! tip "ポイント"
    - `ptr`: 読み終えた位置（失敗したら `first`）。
    - `ec`: エラーコード（成功なら 0）。
    - 構造化束縛で受けると読みやすい。

!!! info "このページを読む前に"
    [`std::to_chars`](to_chars.md) と [`std::from_chars`](from_chars.md) を先に読んでください。

## 関数の詳しい説明

### std::from_chars_result {#from_chars_result}

```cpp
struct from_chars_result {
  const char* ptr;
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
  std::string_view s = "42";
  int v = 0;
  auto r = std::from_chars(s.data(), s.data() + s.size(), v);
  std::println("{} {}", v, r.ec == std::errc{});
}
```

```text title="実行結果"
42 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 文字列を速く数値にする |

## よくあるミス

??? failure "`ec` を確かめない"
    失敗すると `v` は変わりません。確かめずに使うと、古い値を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_chars_result`](to_chars_result.md) | 書き出し側 |
| [`from_chars`](from_chars.md) | 文字列を数値にする |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] from_chars の結果（読み終えた位置とエラー）を表す構造体
    - [x] `ptr`: 読み終えた位置（失敗したら `first`）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::from_chars_result](https://cpprefjp.github.io/reference/charconv/from_chars_result.html)
- [cppreference: std::from_chars_result](https://en.cppreference.com/w/cpp/utility/from_chars_result)

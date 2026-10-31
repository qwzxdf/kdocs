---
title: std::stold
summary: "文字列を long double に変換する（失敗すると例外）。"
order: 900
tags:
  - コンテナ
---

# std::stold

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stold(str)` は、文字列を `long double` に変換します。`stod` の精度が高い版です。MSVC では `long double` が `double` と同じ 64 ビットなので、結果は `stod` と同じです。

!!! tip "ポイント"
    - `long double` に変換する
    - MSVC では `double` と同じ精度
    - GCC / Clang（x86）では 80 ビットの拡張精度
    - 規則は `stod` と同じ

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stold {#stold}

<span class="ver ver-11">C++11</span>

```cpp
long double stold(const std::string& str, std::size_t* pos = nullptr);
```

`long double` の精度と範囲は、環境で違います。ゲームでは、`float` や `double` で足りるので、`long double` を使う機会はほとんどありません。

文字列の読み取りの規則（空白、符号、指数、`inf`、`nan`、ロケールの影響）は `stod` と同じです。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  const long double v = std::stold("2.5");
  std::println("{}", static_cast<double>(v));
  std::println("{}", sizeof(long double) >= sizeof(double));
}
```

```text title="実行結果"
2.5
true
```

## ゲームでの使いどころ

ほとんど使いません。高い精度が必要な計算の入力で使います。

## よくあるミス

??? failure "MSVC で精度が上がると思う"
    `double` と同じです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stod`](stod.md) | `double` |
| [`stol`](stol.md) | 整数 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::stold](https://cpprefjp.github.io/reference/string/stold.html)
- [cppreference: std::stold](https://en.cppreference.com/w/cpp/string/basic_string/stol)

---
title: std::stod
summary: "文字列を double に変換する（失敗すると例外）。"
order: 63
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stod

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stod` は、**文字列を `double` に変換する**関数です。[`stof`](stof.md) の `double` 版で、使い方は同じです。

!!! tip "ポイント"
    - 失敗は例外。
    - ロケールの影響を受ける。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stod {#stod}

```cpp
double stod(const std::string& str, std::size_t* pos = nullptr);
```

- `stof` の double 版です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  double v = std::stod("3.25");
  std::println("{}", v);
}
```

```text title="実行結果"
3.25
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 精度が必要な数値の読み込み | `double v = std::stod(text);` |

## よくあるミス

??? failure "例外を受けない"
    `try` / `catch` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stof`](stof.md) | float |
| [`std::from_chars`](../io/from_chars.md) | 例外なし |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → double
    - [x] 失敗は例外
    - [x] stof の double 版

## 関連ページ

- [cpprefjp: std::stod](https://cpprefjp.github.io/reference/string/stod.html)
- [cppreference: std::stod](https://en.cppreference.com/w/cpp/string/basic_string/stod)

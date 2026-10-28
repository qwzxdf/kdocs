---
title: std::chars_format
summary: "to_chars / from_chars で浮動小数点の書式（固定・指数・16 進）を選ぶ列挙型。"
order: 900
tags:
  - 入出力・文字列
---

# std::chars_format

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <charconv>`
</div>

小数を文字列にするとき、`3.5`（固定）にするか、`3.5e+00`（指数）にするかを選べます。`std::to_chars` の第 4 引数に `chars_format` を渡します。`from_chars` の読み込みでも、どの形式を受け付けるかを指定できます。

!!! tip "ポイント"
    - `fixed`: 固定小数点（`3.5`）。
    - `scientific`: 指数表記（`3.5e+00`）。
    - `general`: どちらか短いほう。`hex`: 16 進数。

!!! info "このページを読む前に"
    [`std::to_chars`](to_chars.md) と [`std::from_chars`](from_chars.md) を先に読んでください。

## 関数の詳しい説明

### std::chars_format {#chars_format}

```cpp
enum class chars_format {
  scientific = 1,
  fixed = 2,
  hex = 4,
  general = fixed | scientific
};
```

- 戻り値: なし（列挙型）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <charconv>
#include <print>
#include <string_view>

int main() {
  char buf[16];
  auto r = std::to_chars(buf, buf + 16, 3.5, std::chars_format::fixed);
  std::println("{}", std::string_view(buf, r.ptr - buf));
  r = std::to_chars(buf, buf + 16, 3.5, std::chars_format::scientific);
  std::println("{}", std::string_view(buf, r.ptr - buf));
}
```

```text title="実行結果"
3.5
3.5e+00
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 小数を決まった形式で出力する |

## よくあるミス

??? failure "形式を省略して往復を期待する"
    形式を省略すると、最短で往復できる表現が選ばれます。固定にしたいなら指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_chars`](to_chars.md) | 小数を文字列にする |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] to_chars / from_chars で浮動小数点の書式（固定・指数・16 進）を選ぶ列挙型
    - [x] `fixed`: 固定小数点（`3.5`）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::chars_format](https://cpprefjp.github.io/reference/charconv/chars_format.html)
- [cppreference: std::chars_format](https://en.cppreference.com/w/cpp/utility/chars_format)

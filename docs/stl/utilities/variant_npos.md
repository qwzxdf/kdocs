---
title: std::variant_npos
summary: "variant が値を持たない状態を表す、index() の値。"
order: 900
tags:
  - ユーティリティ
---

# std::variant_npos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`variant` の代入中に例外が起きると、中身が壊れた「値なし」の状態（valueless）になることがあります。そのとき `v.index()` が返す特別な値が `std::variant_npos` です。

!!! tip "ポイント"
    - `size_t` の最大値（`-1`）。
    - `v.valueless_by_exception()` でも同じ状態を調べられる。
    - 普通は気にしなくてよい。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::variant_npos {#variant_npos}

```cpp
inline constexpr size_t variant_npos = -1;
```

- 戻り値: なし（定数）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <variant>

int main() {
  std::variant<int, double> v;
  std::println("{}", v.index() == std::variant_npos);
  std::println("{}", std::variant_npos == static_cast<std::size_t>(-1));
}
```

```text title="実行結果"
false
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 例外安全のテストで状態を確認する | `v.index() == std::variant_npos` |

## よくあるミス

??? failure "通常の variant で期待する"
    例外が出ない限り、`index()` はこの値になりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::variant`](variant.md) | variant の本体 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値なしの状態の index()
    - [x] size_t の最大値
    - [x] valueless_by_exception でも調べられる

## 関連ページ

- [cpprefjp: std::variant_npos](https://cpprefjp.github.io/reference/variant/variant_npos.html)
- [cppreference: std::variant_npos](https://en.cppreference.com/w/cpp/utility/variant/variant_npos)

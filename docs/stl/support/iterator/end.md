---
title: std::end
summary: "コンテナや配列の終わり（最後の次）を指すイテレータを返す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::end

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <iterator>`
</div>

`c.end()` はコンテナ専用で、C の配列には書けません。`std::end(c)` は、コンテナなら `c.end()`、配列なら先頭 + 要素数を返します。配列でもコンテナでも、同じ書き方で終端を取れるので、ジェネリックなコードで使います。

!!! tip "ポイント"
    - コンテナでも C の配列でも同じ書き方で使える。
    - `std::begin` とセットで使う。
    - C++20 では `std::ranges::end` も使える。

!!! info "このページを読む前に"
    [`std::begin`](begin.md) を先に読んでください。

## 関数の詳しい説明

### std::end {#end}

```cpp
template <class C>
constexpr auto end(C& c) -> decltype(c.end());
template <class T, std::size_t N>
constexpr T* end(T (&array)[N]) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ | 対象のコンテナ |
| `array` | 配列 | 対象の配列 |

- 戻り値: 終わりを指すイテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  int a[] = {1, 2, 3};
  std::println("{}", std::end(a) - std::begin(a));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列とコンテナの両方を受け取る関数で走査する | `for (auto it = std::begin(c); it != std::end(c); ++it)` |

## よくあるミス

??? failure "ポインタに使う"
    配列の要素数が分からないポインタ（`int*`）には使えません。配列の型（`int[3]`）のときだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`begin`](begin.md) | 先頭を返す |
| [`ranges::end`](../ranges/begin.md) | C++20 の版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 終端のイテレータを返す
    - [x] 配列にも使える
    - [x] begin とセット

## 関連ページ

- [cpprefjp: std::end](https://cpprefjp.github.io/reference/iterator/end.html)
- [cppreference: std::end](https://en.cppreference.com/w/cpp/iterator/end)

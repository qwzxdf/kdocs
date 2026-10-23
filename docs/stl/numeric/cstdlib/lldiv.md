---
title: std::lldiv
summary: "long long の割り算で、商と余りをいっしょに返す。"
order: 900
tags:
  - 数値
---

# std::lldiv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`std::div` の、型違いの仲間です。`std::lldiv` は、`long long`の割り算の商と余りを、1 回の呼び出しで返します。

!!! tip "ポイント"
    - `std::lldiv(7, 2)` は商 3、余り 1
    - 結果は `lldiv_t` 構造体（`quot` と `rem`）
    - 0 方向への切り捨てで、余りの符号は割られる数に従う
    - `y` が 0 のときは未定義動作

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lldiv {#lldiv}

```cpp
lldiv_t lldiv(long long x, long long y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `long long` | 割られる数 |
| `y` | `long long` | 割る数。0 は不可 |

戻り値の `lldiv_t` は、`quot`（商）と `rem`（余り）を持つ構造体で、`x == quot * y + rem` が成り立ちます。商は 0 方向に切り捨てられるので、`lldiv(-7, 2)` は商 −3、余り −1 です。

`y` が 0 のとき、または商が表せない場合（最小値 ÷ −1）は、未定義動作です。

`/` と `%` を並べて書けば、コンパイラが 1 つの命令にまとめるため、`lldiv` が速いとは限りません。型の幅だけが `std::div` と違います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  const auto a = std::lldiv(7, 2);
  std::println("7 / 2  -> 商 {}, 余り {}", a.quot, a.rem);
  const auto b = std::lldiv(-7, 2);
  std::println("-7 / 2 -> 商 {}, 余り {}", b.quot, b.rem);
}
```

```text title="実行結果"
7 / 2  -> 商 3, 余り 1
-7 / 2 -> 商 -3, 余り -1
```

## ゲームでの使いどころ

大きな値の商と余りを、1 回で受け取りたいときに使います。

```cpp
const auto t = std::lldiv(total_ms, 1000);   // 秒とミリ秒に分ける
```

負の数で「常に 0 以上の余り」が欲しい場合は、別に補正が要ります。

## よくあるミス

??? failure "負の数の余りが 0 以上だと思う"
    符号は割られる数に従います。

??? failure "0 で割る"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`div`](div.md) | `int` 版 |
| [`remainder`](../cmath/remainder.md) | 浮動小数点数の余り |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `lldiv` は商と余りを `lldiv_t` で返す
    - [x] 0 方向への切り捨てで、余りの符号は `x` に従う
    - [x] `y` が 0 は未定義動作

## 関連ページ

- [cpprefjp: std::lldiv](https://cpprefjp.github.io/reference/cstdlib/lldiv.html)
- [cppreference: std::lldiv](https://en.cppreference.com/w/cpp/c/lldiv)

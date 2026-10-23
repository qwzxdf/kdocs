---
title: std::div
summary: "整数の割り算で、商と余りを同時に求める。"
order: 1
group: <cstdlib> の関数
tags:
  - 数値
---

# std::div

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::div(a, b)` は、**整数の割り算の商（`quot`）と余り（`rem`）を一度に求める**関数です。構造体で両方が返ります。

!!! tip "ポイント"
    - 商と余りを別々に計算するより、まとめて求められる。
    - 負の数のとき、商は 0 に向かって切り捨て（C++11 以降）。

!!! info "このページを読む前に"
    - [stl/index.md](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::div {#div}

```cpp
std::div_t div(int numerator, int denominator);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `numerator` | `int` | 割られる数 |
| `denominator` | `int` | 割る数（0 でないこと） |

- 戻り値: `quot`（商）と `rem`（余り）を持つ構造体
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <print>

int main() {
  auto r = std::div(7, 2);
  std::println("{} {}", r.quot, r.rem);
}
```

```text title="実行結果"
3 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 秒を「分と秒」に分ける | `auto [m, s] = std::div(sec, 60);` |

## よくあるミス

??? failure "0 で割る"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| `operator%` | 余りだけ |
| [`fmod`](../cmath/fmod.md) | 小数の余り |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 商と余りを同時に
    - [x] `quot` と `rem`
    - [x] 0 で割らない

## 関連ページ

- [cpprefjp: std::div](https://cpprefjp.github.io/reference/cstdlib/div.html)
- [cppreference: std::div](https://en.cppreference.com/w/cpp/numeric/math/div)

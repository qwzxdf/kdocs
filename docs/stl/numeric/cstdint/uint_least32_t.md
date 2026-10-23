---
title: std::uint_least32_t
summary: "32 ビット以上で、最も小さい符号なし整数。"
order: 900
tags:
  - 数値
---

# std::uint_least32_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` や `long` の大きさは環境で違います。`std::uint_least32_t` は、32 ビット以上で、最も小さい符号なし整数を表す型です。

!!! tip "ポイント"
    - 32 ビット以上で、最も小さい符号なし整数。
    - `<cstdint>` で定義される。
    - 大きさにこだわらない移植性のある書き方に使う。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::uint_least32_t {#uint_least32_t}

```cpp
using uint_least32_t = /* 符号なし整数型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::uint_least32_t) >= 4);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル・通信・ビットフラグ | `std::uint_least32_t` |

## よくあるミス

??? failure "符号なしの引き算で負になると思う"
    符号なしの型は、引いて 0 を下回ると、大きな値にぐるっと回ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<cstdint>`](../cstdint.md) | 整数型の一覧 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 32 ビット以上で、最も小さい符号なし整数
    - [x] 大きさを意識するときに使う
    - [x] 普通の計算は int で足りる

## 関連ページ

- [cpprefjp: std::uint_least32_t](https://cpprefjp.github.io/reference/cstdint/uint_least32_t.html)
- [cppreference: std::uint_least32_t](https://en.cppreference.com/w/cpp/types/integer)

---
title: std::uint8_t
summary: "ちょうど 8 ビットの符号なし整数。"
order: 900
tags:
  - 数値
---

# std::uint8_t

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` や `long` の大きさは環境で違います。`std::uint8_t` は、ちょうど 8 ビットの符号なし整数を表す型です。0〜255 の値（色の各成分、バイト列）に使います。中身は `unsigned char` なので、`std::cout << x` では**文字**として出ます（`std::println` なら数値）。実装が対応していなくても定義される必要がない型（`optional` な型）なので、極端に特殊な環境では使えないことがあります。

!!! tip "ポイント"
    - ちょうど 8 ビットの符号なし整数。
    - `<cstdint>` で定義される。
    - 普通の計算には `int` でよく、ファイル・通信・ビット操作で大きさを固定したいときに使う。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::uint8_t {#uint8_t}

```cpp
using uint8_t = /* 符号なし整数型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstdint>
#include <iostream>
#include <print>

int main() {
  std::uint8_t level = 65;
  std::cout << level << ' ' << static_cast<int>(level) << '\n';  // 1 つ目は 'A'
  std::println("{}", level);  // println は数値で出す
}
```

```text title="実行結果"
A 65
65
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル・通信・ビットフラグ | `std::uint8_t` |

## よくあるミス

??? failure "符号なしの引き算で負になると思う"
    符号なしの型は、引いて 0 を下回ると、非常に大きな値にぐるっと回ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<cstdint>`](../cstdint.md) | 整数型の一覧 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ちょうど 8 ビットの符号なし整数
    - [x] 大きさを意識するときに使う
    - [x] 普通の計算は int で足りる

## 関連ページ

- [cpprefjp: std::uint8_t](https://cpprefjp.github.io/reference/cstdint/uint8_t.html)
- [cppreference: std::uint8_t](https://en.cppreference.com/w/cpp/types/integer)

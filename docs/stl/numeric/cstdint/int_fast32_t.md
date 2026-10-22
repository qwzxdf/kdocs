---
title: std::int_fast32_t
summary: "32 ビット以上で、その環境で最も速く扱える符号付き整数。"
order: 900
tags:
  - 数値
---

# std::int_fast32_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` や `long` の大きさは環境で違います。`std::int_fast32_t` は、32 ビット以上で、その環境で最も速く扱える符号付き整数を表す型です。

!!! tip "ポイント"
    - 32 ビット以上で、その環境で最も速く扱える符号付き整数。
    - `<cstdint>` で定義される。
    - 大きさにこだわらない移植性のある書き方に使う。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::int_fast32_t {#int_fast32_t}

```cpp
using int_fast32_t = /* 符号付き整数型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::int_fast32_t) >= 4);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル・通信・ビットフラグ | `std::int_fast32_t` |

## よくあるミス

??? failure "符号なしの引き算で負になると思う"
    オーバーフローは未定義動作です。範囲を超える計算に注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<cstdint>`](../cstdint.md) | 整数型の一覧 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 32 ビット以上で、その環境で最も速く扱える符号付き整数
    - [x] 大きさを意識するときに使う
    - [x] 普通の計算は int で足りる

## 関連ページ

- [cpprefjp: std::int_fast32_t](https://cpprefjp.github.io/reference/cstdint/int_fast32_t.html)
- [cppreference: std::int_fast32_t](https://en.cppreference.com/w/cpp/types/integer)

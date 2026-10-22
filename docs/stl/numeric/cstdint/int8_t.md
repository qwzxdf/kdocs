---
title: std::int8_t
summary: "ちょうど 8 ビットの符号付き整数。"
order: 900
tags:
  - 数値
---

# std::int8_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` や `long` の大きさは環境で違います。`std::int8_t` は、ちょうど 8 ビットの符号付き整数を表す型です。-128〜127 の小さな値に使います。`uint8_t` と同じく、`cout` では文字として出ます。実装が対応していなくても定義される必要がない型（`optional` な型）なので、極端に特殊な環境では使えないことがあります。

!!! tip "ポイント"
    - ちょうど 8 ビットの符号付き整数。
    - `<cstdint>` で定義される。
    - 普通の計算には `int` でよく、ファイル・通信・ビット操作で大きさを固定したいときに使う。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::int8_t {#int8_t}

```cpp
using int8_t = /* 符号付き整数型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::int8_t) == 1);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル・通信・ビットフラグ | `std::int8_t` |

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
    - [x] ちょうど 8 ビットの符号付き整数
    - [x] 大きさを意識するときに使う
    - [x] 普通の計算は int で足りる

## 関連ページ

- [cpprefjp: std::int8_t](https://cpprefjp.github.io/reference/cstdint/int8_t.html)
- [cppreference: std::int8_t](https://en.cppreference.com/w/cpp/types/integer)

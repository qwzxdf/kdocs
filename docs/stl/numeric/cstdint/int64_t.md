---
title: std::int64_t
summary: "ちょうど 64 ビットの符号付き整数。"
order: 900
tags:
  - 数値
---

# std::int64_t

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` や `long` の大きさは環境で違います。`std::int64_t` は、ちょうど 64 ビットの符号付き整数を表す型です。21 億を超える数（所持金、ミリ秒のタイムスタンプ）に使います。実装が対応していなくても定義される必要がない型（`optional` な型）なので、極端に特殊な環境では使えないことがあります。

!!! tip "ポイント"
    - ちょうど 64 ビットの符号付き整数。
    - `<cstdint>` で定義される。
    - 普通の計算には `int` でよく、ファイル・通信・ビット操作で大きさを固定したいときに使う。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::int64_t {#int64_t}

```cpp
using int64_t = /* 符号付き整数型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::int64_t) == 8);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル・通信・ビットフラグ | `std::int64_t` |

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
    - [x] ちょうど 64 ビットの符号付き整数
    - [x] 大きさを意識するときに使う
    - [x] 普通の計算は int で足りる

## 関連ページ

- [cpprefjp: std::int64_t](https://cpprefjp.github.io/reference/cstdint/int64_t.html)
- [cppreference: std::int64_t](https://en.cppreference.com/w/cpp/types/integer)

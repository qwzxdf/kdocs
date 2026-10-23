---
title: std::uint64_t
summary: "ちょうど 64 ビットの符号なし整数。"
order: 900
tags:
  - 数値
---

# std::uint64_t

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` や `long` の大きさは環境で違います。`std::uint64_t` は、ちょうど 64 ビットの符号なし整数を表す型です。ハッシュ値や、世代付きのハンドルを 1 つの数に詰めるのに使います。実装が対応していなくても定義される必要がない型（`optional` な型）なので、極端に特殊な環境では使えないことがあります。

!!! tip "ポイント"
    - ちょうど 64 ビットの符号なし整数。
    - `<cstdint>` で定義される。
    - 普通の計算には `int` でよく、ファイル・通信・ビット操作で大きさを固定したいときに使う。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::uint64_t {#uint64_t}

```cpp
using uint64_t = /* 符号なし整数型 */;
```

- 戻り値: なし（型）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  std::println("{}", sizeof(std::uint64_t) == 8);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイル・通信・ビットフラグ | `std::uint64_t` |

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
    - [x] ちょうど 64 ビットの符号なし整数
    - [x] 大きさを意識するときに使う
    - [x] 普通の計算は int で足りる

## 関連ページ

- [cpprefjp: std::uint64_t](https://cpprefjp.github.io/reference/cstdint/uint64_t.html)
- [cppreference: std::uint64_t](https://en.cppreference.com/w/cpp/types/integer)

---
title: std::bit_xor
summary: "`a ^ b`（ビットごとの XOR）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_xor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

「違うビットだけ」を取り出したいとき、`^` を渡します。チェックサムの簡易計算や、2 つのフラグ集合の差分の取り出しに使います。

!!! tip "ポイント"
    - `std::bit_xor<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数にラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_xor {#bit_xor}

```cpp
template <class T = void>
struct bit_xor {
  constexpr auto operator()(const T& a, const T& b) const;  // a ^ b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a ^ b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::bit_xor<>{}(12, 10));
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つのフラグ集合の差分 | `std::bit_xor<>{}(old_flags, new_flags)` |

## よくあるミス

??? failure "累乗と取り違える"
    C++ の `^` は排他的論理和で、累乗ではありません。累乗は [`pow`](../../numeric/cmath/pow.md) です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_and`](bit_and.md) | `&` |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a ^ b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::bit_xor<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::bit_xor](https://cpprefjp.github.io/reference/functional/bit_xor.html)
- [cppreference: std::bit_xor](https://en.cppreference.com/w/cpp/utility/functional/bit_xor)

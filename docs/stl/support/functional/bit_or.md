---
title: std::bit_or
summary: "`a | b`（ビットごとの OR）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_or

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

複数のフラグを 1 つにまとめたいとき、`|` を畳み込みに渡します。

!!! tip "ポイント"
    - `std::bit_or<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数にラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_or {#bit_or}

```cpp
template <class T = void>
struct bit_or {
  constexpr auto operator()(const T& a, const T& b) const;  // a | b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a | b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::bit_or<>{}(12, 10));
}
```

```text title="実行結果"
14
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フラグ値を全部合成 | `std::ranges::fold_left(flags, 0u, std::bit_or<>{});` |

## よくあるミス

??? failure "論理 OR と取り違える"
    `bit_or` はビット単位、`logical_or` は真偽です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_and`](bit_and.md) | `&` |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a | b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::bit_or<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::bit_or](https://cpprefjp.github.io/reference/functional/bit_or.html)
- [cppreference: std::bit_or](https://en.cppreference.com/w/cpp/utility/functional/bit_or)

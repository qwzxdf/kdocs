---
title: std::bit_and
summary: "`a & b`（ビットごとの AND）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_and

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

フラグの共通部分を求めたいとき、`&` を畳み込みに渡せます。複数のフラグ値のうち「全部に立っているビット」を求めるときなどです。

!!! tip "ポイント"
    - `std::bit_and<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数に、ラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_and {#bit_and}

```cpp
template <class T = void>
struct bit_and {
  constexpr auto operator()(const T& a, const T& b) const;  // a & b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a & b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::bit_and<>{}(12, 10));
}
```

```text title="実行結果"
8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 複数のマスクの共通部分 | `std::ranges::fold_left(masks, ~0u, std::bit_and<>{});` |

## よくあるミス

??? failure "論理 AND と取り違える"
    `bit_and` はビット単位、`logical_and` は真偽です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_or`](bit_or.md) | `|` |
| [`bit_xor`](bit_xor.md) | `^` |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a & b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::bit_and<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::bit_and](https://cpprefjp.github.io/reference/functional/bit_and.html)
- [cppreference: std::bit_and](https://en.cppreference.com/w/cpp/utility/functional/bit_and)

---
title: std::minus
summary: "`a - b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::minus

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`-` をアルゴリズムに渡したいとき、ラムダ `[](int a, int b){ return a - b; }` を書くのは冗長です。`std::minus<>{}` なら 1 語で済みます。差を取る `adjacent_difference` や、`fold_left` の演算に使います。

!!! tip "ポイント"
    - `std::minus<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数に、ラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::minus {#minus}

```cpp
template <class T = void>
struct minus {
  constexpr auto operator()(const T& a, const T& b) const;  // a - b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a - b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::minus<>{}(10, 3));
}
```

```text title="実行結果"
7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 隣り合う値の差 | `std::adjacent_difference(v.begin(), v.end(), out.begin(), std::minus<>{});` |

## よくあるミス

??? failure "引数の順序を逆に考える"
    `minus(a, b)` は `a - b` です。`fold_right` では引数の順が逆になることがあるので、結果を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`plus`](plus.md) | 足し算 |
| [`negate`](negate.md) | 符号を反転 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a - b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::minus<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::minus](https://cpprefjp.github.io/reference/functional/minus.html)
- [cppreference: std::minus](https://en.cppreference.com/w/cpp/utility/functional/minus)

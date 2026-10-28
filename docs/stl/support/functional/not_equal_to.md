---
title: std::not_equal_to
summary: "`a != b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::not_equal_to

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

「違うものを数える」「違う場所を探す」といった処理で `!=` を渡したいとき、`std::not_equal_to<>{}` が使えます。`mismatch` や `adjacent_find` の述語にもなります。

!!! tip "ポイント"
    - `std::not_equal_to<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数にラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::not_equal_to {#not_equal_to}

```cpp
template <class T = void>
struct not_equal_to {
  constexpr auto operator()(const T& a, const T& b) const;  // a != b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a != b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::not_equal_to<>{}(3, 4));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つの配列で最初に違う位置を探す | `std::mismatch(a.begin(), a.end(), b.begin(), b.end())`（既定は `==` の否定）。述語を渡すなら `std::equal_to<>{}` |

## よくあるミス

??? failure "`equal_to` と取り違える"
    述語の向きを間違えると、探しているものと逆の結果になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`equal_to`](equal_to.md) | `==` |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a != b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::not_equal_to<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::not_equal_to](https://cpprefjp.github.io/reference/functional/not_equal_to.html)
- [cppreference: std::not_equal_to](https://en.cppreference.com/w/cpp/utility/functional/not_equal_to)

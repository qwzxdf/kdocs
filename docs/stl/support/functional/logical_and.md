---
title: std::logical_and
summary: "`a && b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::logical_and

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

「全部が真か」を 1 つの値にまとめたいとき、`&&` を畳み込みの演算として渡せます。ただし関数オブジェクトでは**短絡評価されません**。

!!! tip "ポイント"
    - `std::logical_and<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数に、ラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logical_and {#logical_and}

```cpp
template <class T = void>
struct logical_and {
  constexpr auto operator()(const T& a, const T& b) const;  // a && b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a && b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::logical_and<>{}(true, false));
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フラグ配列の論理積 | `std::ranges::fold_left(flags, true, std::logical_and<>{});` |

## よくあるミス

??? failure "短絡評価を期待する"
    `a && b` は a が偽なら b を評価しませんが、`logical_and` は両方を引数として評価してから呼ばれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logical_or`](logical_or.md) | `||` |
| [`all_of`](../../algorithms/all_of.md) | 全部が真か調べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a && b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::logical_and<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::logical_and](https://cpprefjp.github.io/reference/functional/logical_and.html)
- [cppreference: std::logical_and](https://en.cppreference.com/w/cpp/utility/functional/logical_and)

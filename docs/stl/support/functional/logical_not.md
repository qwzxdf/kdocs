---
title: std::logical_not
summary: "`!a` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::logical_not

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

述語の結果を反転したいとき、`std::not_fn` を使うほか、単純な `!` なら `std::logical_not<>{}` を渡せます。

!!! tip "ポイント"
    - `std::logical_not<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数に、ラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logical_not {#logical_not}

```cpp
template <class T = void>
struct logical_not {
  constexpr auto operator()(const T& a) const;  // !a
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |

- 戻り値: `!a` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::logical_not<>{}(true));
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フラグを全部反転 | `std::transform(f.begin(), f.end(), f.begin(), std::logical_not<>{});` |

## よくあるミス

??? failure "関数の結果を反転したい"
    述語の反転は [`not_fn`](not_fn.md) のほうが向いています。`logical_not` は値の `!` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`not_fn`](not_fn.md) | 述語の結果を反転する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] !a を関数オブジェクトにしたもの
    - [x] 型を省略した `std::logical_not<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::logical_not](https://cpprefjp.github.io/reference/functional/logical_not.html)
- [cppreference: std::logical_not](https://en.cppreference.com/w/cpp/utility/functional/logical_not)

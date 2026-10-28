---
title: std::logical_or
summary: "`a || b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::logical_or

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

「どれか 1 つでも真か」を畳み込みで調べたいときに使います。`any_of` のほうが短絡評価されるので、実際には `any_of` が向いています。

!!! tip "ポイント"
    - `std::logical_or<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数にラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logical_or {#logical_or}

```cpp
template <class T = void>
struct logical_or {
  constexpr auto operator()(const T& a, const T& b) const;  // a || b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a || b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::logical_or<>{}(true, false));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フラグ配列の論理和 | `std::ranges::fold_left(flags, false, std::logical_or<>{});` |

## よくあるミス

??? failure "短絡評価を期待する"
    関数オブジェクトでは両方の引数が先に評価されます。途中で止めたいなら `any_of` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logical_and`](logical_and.md) | `&&` |
| [`any_of`](../../algorithms/any_of.md) | どれかが真か調べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a || b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::logical_or<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::logical_or](https://cpprefjp.github.io/reference/functional/logical_or.html)
- [cppreference: std::logical_or](https://en.cppreference.com/w/cpp/utility/functional/logical_or)

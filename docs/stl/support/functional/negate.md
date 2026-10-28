---
title: std::negate
summary: "`-a`（符号の反転）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::negate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

全要素の符号を反転したいとき、`transform` に `std::negate<>{}` を渡すと、ラムダなしで書けます。

!!! tip "ポイント"
    - `std::negate<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数にラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::negate {#negate}

```cpp
template <class T = void>
struct negate {
  constexpr auto operator()(const T& a) const;  // -a
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |

- 戻り値: `-a` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::negate<>{}(5));
}
```

```text title="実行結果"
-5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 速度ベクトルの成分を反転 | `std::transform(v.begin(), v.end(), v.begin(), std::negate<>{});` |

## よくあるミス

??? failure "符号なしの型に使う"
    `unsigned` に `negate` を使うと、大きな値にぐるっと回ります。符号つきの型で使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`minus`](minus.md) | 引き算 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] -a を関数オブジェクトにしたもの
    - [x] 型を省略した `std::negate<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::negate](https://cpprefjp.github.io/reference/functional/negate.html)
- [cppreference: std::negate](https://en.cppreference.com/w/cpp/utility/functional/negate)

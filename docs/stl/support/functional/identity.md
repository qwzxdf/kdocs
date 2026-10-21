---
title: std::identity
summary: "受け取った値をそのまま返す関数オブジェクト。"
order: 6
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::identity

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <functional>`
</div>

`std::identity` は、**受け取った値をそのまま返す**関数オブジェクトです。ranges のアルゴリズムの `proj`（プロジェクション）の既定値として使われています。「何もしない射影」が要るときに、自分で渡せます。

!!! tip "ポイント"
    - ranges の `proj` を省略したときの既定値。
    - 自作のアルゴリズムの既定値に使える。
    - C++20 の機能。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::identity {#identity}

<span class="ver ver-20">C++20</span>

```cpp
struct identity {
  template <class T>
  constexpr T&& operator()(T&& t) const noexcept;
};
```

- 受け取ったものをそのまま返します。ranges のアルゴリズムの「プロジェクション無し」のデフォルトです

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::identity{}(5));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作の ranges 風アルゴリズムの proj の既定値 | `Proj proj = std::identity{}` |

## よくあるミス

??? failure "ラムダと混同する"
    `[](auto&& x) -> auto&& { return x; }` と同じ役割の部品です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sort`](../../algorithms/sort.md) | proj を取るアルゴリズム |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値をそのまま返す
    - [x] proj の既定値
    - [x] C++20

## 関連ページ

- [cpprefjp: std::identity](https://cpprefjp.github.io/reference/functional/identity.html)
- [cppreference: std::identity](https://en.cppreference.com/w/cpp/utility/functional/identity)

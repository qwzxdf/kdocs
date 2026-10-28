---
title: std::ranges::elements_of
summary: "ジェネレーターの中で、別のレンジを丸ごと `co_yield` する（C++23）。"
order: 100
tags:
  - 型・言語サポート
---

# std::ranges::elements_of

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <generator>`
</div>

`std::generator` の中で、別のレンジの要素を全部返したいとき、`for (auto x : r) co_yield x;` と書くと、1 要素ごとに中断と再開が走ります。`co_yield std::ranges::elements_of(r)` と書くと、レンジをまるごと委譲でき、入れ子の再帰ジェネレーターで特に効率的です。

!!! tip "ポイント"
    - `co_yield elements_of(r)` で、レンジを丸ごと返す。
    - 再帰ジェネレーターに向く。
    - `generator` と共に C++23 で入った。

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### elements_of {#elements_of}

```cpp
template <ranges::range R, class Allocator = allocator<byte>>
elements_of(R&&, Allocator = {}) -> elements_of<R&&, Allocator>;
```

| 引数 | 意味 |
| --- | --- |
| `r` | 返したいレンジ |

- `elements_of` オブジェクトを返します。`co_yield` のオペランドとして使います

## 実際に動かしてみる

```cpp
#include <generator>
#include <iostream>
#include <ranges>
#include <vector>

std::generator<int> Concat() {
  std::vector<int> a = {1, 2};
  co_yield std::ranges::elements_of(a);   // a の要素を丸ごと返す
  co_yield 3;
}

int main() {
  for (int v : Concat()) {
    std::cout << v << " ";
  }
  std::cout << "\n";
}
```

```text title="実行結果"
1 2 3 
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ツリーの再帰走査 | `co_yield std::ranges::elements_of(Walk(child))` |

## よくあるミス

??? failure "通常の `co_yield` にレンジを渡す"
    `co_yield r` は、レンジそのものを 1 つの値として返そうとします。`elements_of` で包みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::generator`](../generator.md) | コルーチンのジェネレーター |

## コンパイラ対応

C++23 の機能です（`<generator>` が必要）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レンジを丸ごと `co_yield` する。
    - [x] 再帰ジェネレーターでも速い。
    - [x] `generator` と対で使う。

## 関連ページ

- [cpprefjp: elements_of](https://cpprefjp.github.io/reference/generator/elements_of.html)
- [cppreference: elements_of](https://en.cppreference.com/w/cpp/ranges/elements_of)

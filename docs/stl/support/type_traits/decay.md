---
title: std::decay
summary: "関数に値渡しされたときの型（参照・const を外し、配列・関数はポインターに）にする。"
order: 16
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::decay

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::decay_t<T>` は、**値渡しで関数に渡したときに、実際に受け取る型**を返します。参照と `const` が外れ、配列はポインター、関数は関数ポインターになります。`std::thread` や `std::make_pair` が、引数の型を決めるのに使っています。

!!! tip "ポイント"
    - `decay_t<const int&>` は `int`。
    - `decay_t<int[3]>` は `int*`。
    - C++20 以降、配列や関数を変換しない `remove_cvref` もある。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::decay_t {#decay}

- 値渡しで受け取ったときと同じ変換（参照・const を外し、配列・関数をポインタに）をした型

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<std::decay_t<const int&>, int>, std::is_same_v<std::decay_t<int[3]>, int*>);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 値で保存する型を決める（テンプレート） | `std::decay_t<T> stored;` |

## よくあるミス

??? failure "remove_cvref と取り違える"
    配列がポインターに変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | 配列・関数はそのまま |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値渡しされた型に直す
    - [x] 配列はポインターになる
    - [x] thread / make_pair が使う

## 関連ページ

- [cpprefjp: std::decay](https://cpprefjp.github.io/reference/type_traits/decay.html)
- [cppreference: std::decay](https://en.cppreference.com/w/cpp/types/decay)

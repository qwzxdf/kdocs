---
title: std::equivalence_relation
summary: "同値関係（反射・対称・推移）となる二項関係を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::equivalence_relation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

並べ替えや検索のアルゴリズムは、2 つの値を比べる関数を受け取ります。`std::equivalence_relation` は、<strong>同値関係を表す述語</strong>であることを要求するコンセプトです。

!!! tip "ポイント"
    - `std::equivalence_relation<R, T, U>`: `R` が `T` と `U` を比べる述語か
    - `std::less<>` や `std::equal_to<>` のような、比較の関数オブジェクトが満たす
    - 構文上の条件は `relation` と同じ。意味上の約束は検査されない
    - 標準のアルゴリズムの引数の制約として使われる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::equivalence_relation {#equivalence_relation}

<span class="ver ver-20">C++20</span>

```cpp
template <class R, class T, class U>
concept equivalence_relation = relation<R, T, U>;   // 意味上の要求を加えたもの
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | 比べる述語の型 |
| `T` | 型 | 1 つ目の値の型 |
| `U` | 型 | 2 つ目の値の型 |

`relation` の条件に加えて、「同値関係」（反射的、対称的、推移的）という意味上の約束を要求します。`std::equal_to<>` が代表です。約束は、コンパイラには検査されません。

カスタムの比較関数（ラムダ）を渡すときも、この条件に合うかが、呼び出しの場所で検査されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <functional>
#include <print>

struct Player {
  int hp;
};

int main() {
  std::println("std::equal_to<>, int, int  -> {}", std::equivalence_relation<std::equal_to<>, int, int>);
  std::println("std::equal_to<>, int, Player -> {}", std::equivalence_relation<std::equal_to<>, int, Player>);
}
```

```text title="実行結果"
std::equal_to<>, int, int  -> true
std::equal_to<>, int, Player -> false
```

## ゲームでの使いどころ

自作のアルゴリズムで、比較の関数を受け取る引数を制限します。

```cpp
template <class It, class Cmp>
  requires std::equivalence_relation<Cmp, std::iter_value_t<It>, std::iter_value_t<It>>
void MySort(It first, It last, Cmp cmp);
```

## よくあるミス

??? failure "意味上の約束を破る比較関数を渡す"
    コンパイラは検査しません。`<=` のような、順序が壊れる関数を渡さないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`predicate`](predicate.md) | 1 つの引数の述語 |
| [`invocable`](invocable.md) | 呼べるか |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::equivalence_relation` は同値関係を表す述語
    - [x] `std::less<>` / `std::equal_to<>` が満たす
    - [x] 意味上の約束はコンパイラに検査されない

## 関連ページ

- [cpprefjp: std::equivalence_relation](https://cpprefjp.github.io/reference/concepts/equivalence_relation.html)
- [cppreference: std::equivalence_relation](https://en.cppreference.com/w/cpp/concepts/equivalence_relation)

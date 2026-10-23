---
title: std::same_as
summary: "2 つの型が同じであることを要求するコンセプト。"
order: 1
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::same_as

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

「引数は `int` でなければならない」というテンプレートを書きたいとき、`template <class T>` だけでは、どんな型でも受け付けてしまいます。`std::same_as<T, U>` は、T と U がまったく同じ型であることを要求するコンセプトです。`template <std::same_as<int> T>` と書けば、`int` 以外はコンパイルの時点で弾かれます。型特性の `is_same_v` と違って、関数テンプレートの引数に直接書けます。

!!! tip "ポイント"
    - `template <std::same_as<int> T>` や、`std::same_as<int> auto x` と書ける。
    - `const` や参照も区別する。

!!! info "このページを読む前に"
    テンプレートの基本（型を引数にする関数やクラス）が分かると読みやすいです。

## 関数の詳しい説明

### std::same_as {#same_as}

```cpp
template <class T>
concept same_as = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

int main() {
  std::println("{} {}", std::same_as<int, int>, std::same_as<int, long>);
}
```

```text title="実行結果"
true false
```

## しくみ

`std::same_as<T, U>` は、`is_same_v<T, U>` と `is_same_v<U, T>` の両方が真のとき満たされます。型の同一性の判定なので、`const int` と `int`、`int&` と `int` は別の型として扱われます。

引数の型をそろえる用途では、`template <class T> void F(T a, std::same_as<T> auto b)` のように書けます。`a` と `b` が同じ型でなければならない、という制約になります。

戻り値の型を要求する `requires` 式と組み合わせると、「この式の結果が `int` であること」を表せます。`{ x.Size() } -> std::same_as<int>;` と書くと、`Size()` の戻り値が `int` である型だけを通すコンセプトが作れます。

## ゲームでの使いどころ

型を限定した関数テンプレートに使います。たとえば `template <std::same_as<float> T> void SetVolume(T v)` なら、`double` が渡されたときにコンパイルエラーにでき、意図しない型の変換を防げます。

コンセプトの組み立て部品としても使います。自作の `Drawable` コンセプトで、`{ obj.Draw() } -> std::same_as<void>;` と書けば、「`Draw()` が `void` を返す型」を表現できます。

ECS のコンポーネントを型で探すテンプレートで、「この型は、コンポーネントの一覧のどれかと同じか」を `std::same_as` で判断する場面でも使われます。

## よくあるミス

??? failure "`const` や参照を無視して比べてしまう"
    `std::same_as<const int&, int>` は偽です。引数が参照で来る場合は、`std::same_as<std::remove_cvref_t<T>, int>` のように、外してから比べます。

??? failure "コンセプトの引数の順序を取り違える"
    `template <std::same_as<int> T>` では、`std::same_as<T, int>` の意味になります。第 1 引数が自動的に `T` になる点を覚えておきます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。C++17 では、`static_assert(std::is_same_v<T, int>)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::is_same`](../type_traits/is_same.md) | 型特性版。`bool` の値として使え、`if constexpr` に向く |
| [`std::integral`](integral.md) | 整数型であることを要求する |
| `std::convertible_to` | 変換できることを要求する。型が同じでなくてよい |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 特定の型だけを許すなら `template <std::same_as<int> T>`。
    - [x] `const` や参照は区別される。
    - [x] 型特性の `is_same_v` のコンセプト版。

## 関連ページ

- [cpprefjp: std::same_as](https://cpprefjp.github.io/reference/concepts/same_as.html)
- [cppreference: std::same_as](https://en.cppreference.com/w/cpp/concepts/same_as)

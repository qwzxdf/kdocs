---
title: std::remove_cv
summary: "`const` と `volatile` を取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_cv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型から `const` と `volatile` を両方外して、中身の型だけを取り出したい。`std::remove_cv` は、<strong>最上位の `const` と `volatile` を外した型</strong>を返します。

!!! tip "ポイント"
    - `std::remove_cv_t<const int>` は `int`
    - 参照は外さない（`const int&` はそのまま）
    - 参照も外すなら `remove_cvref`（C++20）
    - テンプレートの引数 `T` の素の型を取り出すときに使う

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_cv_t {#remove_cv}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using remove_cv_t = typename remove_cv<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`const volatile int` も、`const int` も、`volatile int` も `int` になります。ポインタが指す先の修飾は外れません。

参照まで外したいときは、`std::remove_cvref`（C++20）を使います。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_cv<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_cv_t<T>` のほうが短く書けます。

参照が付いている型には効きません。`const int&` は、参照であって、`const` が付いた型ではないからです。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_cv_t<const int> は int : {}", std::is_same_v<std::remove_cv_t<const int>, int>);
  std::println("std::remove_cv_t<const volatile int> は int : {}", std::is_same_v<std::remove_cv_t<const volatile int>, int>);
  std::println("std::remove_cv_t<const int&> は const int& : {}", std::is_same_v<std::remove_cv_t<const int&>, const int&>);
}
```

```text title="実行結果"
std::remove_cv_t<const int> は int : true
std::remove_cv_t<const volatile int> は int : true
std::remove_cv_t<const int&> は const int& : true
```

## ゲームでの使いどころ

型を加工するテンプレートで使います。ゲームのコードで直接書く機会は多くありませんが、汎用のテンプレート（コンテナ、イベントシステム、ECS）の内部ではよく登場します。

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | 参照も外す |
| [`remove_const`](remove_const.md) | `const` だけ外す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_cv_t<const int>` は `int`
    - [x] 参照は外さない（`const int&` はそのまま）
    - [x] 参照も外すなら `remove_cvref`（C++20）

## 関連ページ

- [cpprefjp: std::remove_cv](https://cpprefjp.github.io/reference/type_traits/remove_cv.html)
- [cppreference: std::remove_cv](https://en.cppreference.com/w/cpp/types/remove_cv)

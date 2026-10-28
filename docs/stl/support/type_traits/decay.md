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

関数に値渡しされるとき、配列はポインタに関数は関数ポインタに参照と `const` は外れて変換されます。この「値渡しで何になるか」の規則を型だけで再現したいときに使うのが `std::decay` です。

!!! tip "ポイント"
    - `std::decay_t<const int&>` は `int`
    - 配列はポインタに関数は関数ポインタになる
    - 参照と `const` と `volatile` も外れる
    - 配列や関数のポインタ化が不要なら `remove_cvref`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::decay_t {#decay}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using decay_t = typename decay<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`std::decay<T>` は、次の規則で型を変換します。参照を外す。`const` と `volatile` を外す。配列型は要素へのポインタにする。関数型は関数ポインタにする。それ以外の型はそのままです。

関数テンプレートに引数を値渡しするとき、`T` が推論される型と同じです。コンテナに保存する型を決めるときなど（`std::make_tuple` が内部で使う）に登場します。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::decay<T>::type` と書いても同じ型ですが、C++14 以降の `std::decay_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::decay_t<const int&> は int : {}", std::is_same_v<std::decay_t<const int&>, int>);
  std::println("std::decay_t<int[3]> は int* : {}", std::is_same_v<std::decay_t<int[3]>, int*>);
  std::println("std::decay_t<void(int)> は void(*)(int) : {}", std::is_same_v<std::decay_t<void(int)>, void(*)(int)>);
}
```

```text title="実行結果"
std::decay_t<const int&> は int : true
std::decay_t<int[3]> は int* : true
std::decay_t<void(int)> は void(*)(int) : true
```

## ゲームでの使いどころ

値渡しされたときの型を型だけで求めます。

```cpp
template <class T>
void Store(T&& value) {
  std::decay_t<T> copy = std::forward<T>(value);   // 値として保持する型
}
```

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | 配列や関数は変えない |
| [`remove_reference`](remove_reference.md) | 参照だけ外す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::decay_t<const int&>` は `int`
    - [x] 配列はポインタに関数は関数ポインタになる
    - [x] 参照と `const` と `volatile` も外れる

## 関連ページ

- [cpprefjp: std::decay](https://cpprefjp.github.io/reference/type_traits/decay.html)
- [cppreference: std::decay](https://en.cppreference.com/w/cpp/types/decay)

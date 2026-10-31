---
title: std::in_place_type
summary: "variant / any / optional に、型を指定してその場で作らせる目印。"
order: 900
tags:
  - ユーティリティ
---

# std::in_place_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <utility>`
</div>

`std::variant<int, std::string>` や `std::any` に、「この型の値を、これから渡す引数で直接作ってください」と伝えたいとき、型を指定する印が必要です。`std::in_place_type<T>` は、その印で、型 `T` を選びます。

!!! tip "ポイント"
    - `variant` / `any` のコンストラクターで、型を選んで、引数から直接作る
    - `T` が `variant` に 1 回だけ現れる必要がある
    - 同じ型が複数あるときは、番号を使う `in_place_index`
    - C++17

!!! info "このページを読む前に"
    [`std::in_place`](in_place.md) を先に読んでください。

## 関数の詳しい説明

### std::in_place_type {#in_place_type}

<span class="ver ver-17">C++17</span>

```cpp
template <class T> struct in_place_type_t { explicit in_place_type_t() = default; };
template <class T> inline constexpr std::in_place_type_t<T> in_place_type{};
```

使い方は、コンストラクターの第 1 引数に渡します。

```cpp
std::variant<int, std::string> v(std::in_place_type<std::string>, 3, 'x');
std::any a(std::in_place_type<std::string>, "abc");
```

`variant` の場合、`T` は選択肢のなかにちょうど 1 回だけ現れる型でなければなりません。2 回現れる（`variant<int, int>`）か、現れないと、コンパイル エラーです。

`variant::emplace<T>(引数...)` でも、同じ作り方ができます。すでにある `variant` の中身を、別の型で作り直すときは、`emplace` を使います。

## 実際に動かしてみる

```cpp
#include <any>
#include <print>
#include <string>
#include <variant>

int main() {
  // 型を指定して、引数から直接作る
  std::variant<int, std::string> v(std::in_place_type<std::string>, 3, 'x');
  std::println("番号 {} 値 {}", v.index(), std::get<std::string>(v));

  std::any a(std::in_place_type<std::string>, 2, 'y');
  std::println("{}", std::any_cast<std::string>(a));

  // 作り直しは emplace
  v.emplace<int>(7);
  std::println("番号 {} 値 {}", v.index(), std::get<int>(v));
}
```

```text title="実行結果"
番号 1 値 xxx
yy
番号 0 値 7
```

## ゲームでの使いどころ

メッセージの `variant` に、特定のメッセージ型を直接作って入れるときに使います。

## よくあるミス

??? failure "同じ型が 2 回ある variant で使う"
    型で選べないので、コンパイルできません。`in_place_index` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`in_place`](in_place.md) | `optional` 用の印 |
| [`in_place_index`](in_place_index.md) | 番号で選ぶ |
| `variant::emplace` | 既存の `variant` の中身を作り直す |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::in_place_type](https://cpprefjp.github.io/reference/utility/in_place_type_t.html)
- [cppreference: std::in_place_type](https://en.cppreference.com/w/cpp/utility/in_place)

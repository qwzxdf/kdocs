---
title: std::any_cast
summary: "any に入っている値を、型を指定して取り出す。"
order: 60
tags:
  - ユーティリティ
---

# std::any_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <any>`
</div>

`std::any` は、どんな型の値でも入れられますが、中身を取り出すには、入れた型を正確に指定します。`std::any_cast<T>` は、`any` から `T` の値を取り出す関数で、違う型を指定すると、例外か `nullptr` で失敗を知らせます。

!!! tip "ポイント"
    - `std::any_cast<T>(a)` は値を返し、型が違うと `std::bad_any_cast` を投げる
    - `std::any_cast<T>(&a)` は、ポインタを返し、型が違うと `nullptr`
    - 入れた型と**完全に同じ**型でなければ失敗する。`int` で入れて `long` では取れない
    - 参照で受けると、中身を書き換えられる

!!! info "このページを読む前に"
    [`std::any`](any.md) と [`std::make_any`](make_any.md) を先に読んでください。

## 関数の詳しい説明

### std::any_cast {#any_cast}

<span class="ver ver-17">C++17</span>

```cpp
template <class T> T any_cast(const std::any& operand);
template <class T> T any_cast(std::any& operand);
template <class T> T any_cast(std::any&& operand);
template <class T> const T* any_cast(const std::any* operand) noexcept;
template <class T>       T* any_cast(std::any* operand) noexcept;
```

### 値を取り出す形 {#value}

`any_cast<int>(a)` は、`a` が `int` を持っていれば、その値のコピーを返します。違う型を持つ、または空なら、`std::bad_any_cast` を投げます。`any_cast<int&>(a)` のように参照で受ければ、コピーせず、書き換えられます。

### ポインタで確かめる形 {#pointer}

`any_cast<int>(&a)` は、`a` が `int` を持っていれば、その中身へのポインタを返し、そうでなければ `nullptr` を返します。例外を使わずに調べられるので、型が複数ありうる場面では、こちらが向いています。

```cpp
if (auto* p = std::any_cast<int>(&a)) {
  // *p を使う
}
```

### 型の一致 {#exact}

入れた型と、まったく同じ型でなければ、取り出せません。`int` で入れたものを、`long` や `double` では取り出せません。文字列リテラルを入れると `const char*` が入るので、`std::string` では取り出せません。

## 実際に動かしてみる

```cpp
#include <any>
#include <print>
#include <string>

int main() {
  std::any a = 42;

  // 値を取り出す
  std::println("{}", std::any_cast<int>(a));

  // 違う型を指定すると例外
  try {
    std::any_cast<std::string>(a);
  } catch (const std::bad_any_cast&) {
    std::println("型が違う: bad_any_cast");
  }

  // ポインタ版は nullptr で失敗を知らせる
  std::println("string のポインタ: {}", std::any_cast<std::string>(&a) == nullptr);
  if (int* p = std::any_cast<int>(&a)) {
    *p = 99;  // 中身を書き換えられる
  }
  std::println("{}", std::any_cast<int>(a));

  // 文字列リテラルは const char*
  std::any s = "abc";
  std::println("const char*: {}", std::any_cast<const char*>(&s) != nullptr);
}
```

```text title="実行結果"
42
型が違う: bad_any_cast
string のポインタ: true
99
const char*: true
```

## ゲームでの使いどころ

イベントの引数を `std::any` で運ぶ設計で、受け取り側が型を指定して取り出します。型が決まっているなら、`variant` に置き換えると、取り出しの失敗がコンパイル時に分かります。

## よくあるミス

??? failure "int で入れて long で取り出そうとする"
    完全に同じ型でないと取り出せません。`bad_any_cast` が投げられます。

??? failure "文字列リテラルを string で取り出す"
    `const char*` で入っています。`std::string` で取り出そうとすると、失敗します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::bad_any_cast`](bad_any_cast.md) | 失敗したときの例外 |
| [`std::make_any`](make_any.md) | 値を直接作って入れる |
| [`std::get`](get.md) | `variant` から取り出す |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::any_cast](https://cpprefjp.github.io/reference/any/any_cast.html)
- [cppreference: std::any_cast](https://en.cppreference.com/w/cpp/utility/any/any_cast)

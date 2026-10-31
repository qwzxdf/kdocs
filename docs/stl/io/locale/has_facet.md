---
title: std::has_facet
summary: "ロケールが、指定したファセット（部品）を持っているかを調べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::has_facet

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`use_facet` は、ファセットがロケールに入っていないと、例外（`std::bad_cast`）を投げます。取り出す前に、その部品があるかを確かめたい。そのための関数が `has_facet` です。標準のファセット（`numpunct` や `ctype` など）は、どのロケールにも入っているので、主に自作のファセットを使うときに役立ちます。

!!! tip "ポイント"
    - 持っていれば `true`。持っていなければ `false`（例外は投げない）
    - 標準のファセットは、どのロケールにも入っている
    - 自作のファセットは、ロケールに差し込んだものだけ `true`
    - 取り出す前に確認するときに使う。確実にあるとき（標準のファセット）は不要

!!! info "このページを読む前に"
    [`std::locale::facet`](facet.md) と [`std::use_facet`](use_facet.md) を先に読んでください。

## 関数の詳しい説明

### std::has_facet {#has_facet}

```cpp
template <class Facet>
bool has_facet(const std::locale& loc) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Facet` | テンプレート引数 | 調べるファセットの型 |
| `loc` | `const std::locale&` | 対象のロケール |

`loc` が型 `Facet` のファセットを持っていれば `true` を返します。判定は、`Facet::id` が一致する部品が、ロケールの中にあるかで行われます。

標準のファセットは、`std::locale::classic()` を含め、どのロケールにも入っています。そのため `has_facet<std::numpunct<char>>(loc)` は常に `true` です。調べる意味があるのは、`std::codecvt_utf8` のような、特定のロケールにだけ入るもの（実装による）と、自作のファセットです。

`Facet` は、`static std::locale::id id;` を持つ型でなければなりません。持たない型を渡すと、コンパイル エラーです。

## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

struct MyFacet : std::locale::facet {
  static std::locale::id id;
};
std::locale::id MyFacet::id;

int main() {
  const std::locale base = std::locale::classic();
  std::println("標準の ctype: {}", std::has_facet<std::ctype<char>>(base));
  std::println("自作は未登録: {}", std::has_facet<MyFacet>(base));

  const std::locale with_my(base, new MyFacet);
  std::println("登録後: {}", std::has_facet<MyFacet>(with_my));
}
```

```text title="実行結果"
標準の ctype: true
自作は未登録: false
登録後: true
```

`MyFacet` を差し込んだ `with_my` だけが `true` です。元の `base` は変わっていません。

## ゲームでの使いどころ

自作のファセット（独自の書式や翻訳）を、ロケールに入れておいて、使う側が確認してから取り出す、という設計のときに使います。ゲームで直接書く機会は多くありません。

## よくあるミス

??? failure "has_facet で確認せずに use_facet して例外が飛ぶ"
    入っていないファセットを `use_facet` すると、`std::bad_cast` が飛びます。入っているか分からないときは、先に `has_facet` で確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`use_facet`](use_facet.md) | ファセットを取り出す。なければ例外 |
| [`std::locale::facet`](facet.md) | ファセットの基底クラス |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `has_facet<型>(loc)` は、ロケールがその部品を持つかを返す
    - [x] 標準のファセットは常にある。確認が要るのは自作のもの
    - [x] 取り出す前の確認に使う

## 関連ページ

- [cpprefjp: has_facet](https://cpprefjp.github.io/reference/locale/has_facet.html)
- [cppreference: std::has_facet](https://en.cppreference.com/w/cpp/locale/has_facet)

---
title: std::use_facet
summary: "ロケールから、ファセット（部品）を取り出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::use_facet

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

ロケールが持つ小さな部品を、直接使いたい。数値の小数点の文字を調べる、文字を大文字にする、日付を整形する。`use_facet` は、ロケールから指定した型のファセットへの参照を取り出します。取り出したファセットの関数を呼ぶと、そのロケールの規則に従った結果が返ります。

!!! tip "ポイント"
    - `std::use_facet<型>(loc)` で、ファセットへの const 参照が返る
    - 持っていないファセットを指定すると `std::bad_cast` を投げる
    - 参照は、元のロケールが生きている間だけ有効。ロケールを一時オブジェクトで作って、参照だけ持ち出さない
    - 標準のファセットは常にあるので、そのまま呼んでよい

!!! info "このページを読む前に"
    [`std::locale::facet`](facet.md) と [`std::has_facet`](has_facet.md) を先に読んでください。

## 関数の詳しい説明

### std::use_facet {#use_facet}

```cpp
template <class Facet>
const Facet& use_facet(const std::locale& loc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Facet` | テンプレート引数 | 取り出したいファセットの型 |
| `loc` | `const std::locale&` | 対象のロケール |

戻り値は、`loc` が持つ `Facet` の const 参照です。この参照は、`loc` か、そのコピーが生きている間だけ有効です。ロケールが破棄されると、ぶら下がった参照になります。

```cpp
const auto& np = std::use_facet<std::numpunct<char>>(std::locale("ja_JP.UTF-8"));
// ここで一時オブジェクトの locale は破棄されている。np は使えない
```

上の書き方は危険です。ロケールを変数に保存してから、取り出します。

`Facet` を持っていないロケールに対しては、`std::bad_cast` を投げます。標準のファセットなら必ずありますが、自作のファセットは、ロケールに入れていないと投げます。確実でないなら、`has_facet` で先に調べます。

取り出したファセットは、`const` なので、中のデータは変えられません。関数は `std::ctype<char>::toupper` のように呼びます。ファセットの関数は、スレッドから同時に呼んでも安全です。

## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  const std::locale loc = std::locale::classic();  // 変数に保存して寿命を保つ

  const auto& np = std::use_facet<std::numpunct<char>>(loc);
  std::println("小数点: {}", np.decimal_point());

  const auto& ct = std::use_facet<std::ctype<char>>(loc);
  std::println("大文字: {}", ct.toupper('g'));
}
```

```text title="実行結果"
小数点: .
大文字: G
```

## ゲームでの使いどころ

ロケールの規則（大文字小文字、小数点）に従った処理を、ストリームを通さずに直接使いたいときに使います。英語の大文字小文字の変換なら `std::toupper` で足りるので、ゲームで `use_facet` を直接書く場面は少なめです。

## よくあるミス

??? failure "一時オブジェクトのロケールから参照を取る"
    `use_facet<X>(std::locale("..."))` の参照は、文が終わると無効になります。ロケールを変数に置いてから、取り出します。

??? failure "自作のファセットを入れずに use_facet する"
    `std::bad_cast` が飛びます。`has_facet` で確認するか、ロケールに先に入れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`has_facet`](has_facet.md) | 持っているかを調べる。例外は投げない |
| [`std::locale::facet`](facet.md) | ファセットの基底クラス |
| [`std::ctype`](ctype.md) | 文字の分類・変換のファセット |
| [`std::numpunct`](numpunct.md) | 数値の書式のファセット |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `use_facet<型>(loc)` は、ロケールのファセットを取り出す
    - [x] ないと `std::bad_cast`。参照はロケールが生きている間だけ有効
    - [x] ロケールを変数に保存してから取り出す

## 関連ページ

- [cpprefjp: use_facet](https://cpprefjp.github.io/reference/locale/use_facet.html)
- [cppreference: std::use_facet](https://en.cppreference.com/w/cpp/locale/use_facet)

---
title: std::visit
summary: "variant の中身の型に応じて、処理を呼び分ける。"
order: 55
tags:
  - ユーティリティ
---

# std::visit

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

ゲームの敵の動きを種類ごとに切り替えたい。`variant<Slime, Goblin, Dragon>` に敵を入れて、種類ごとの処理を書くとき、`if` と `get_if` を並べる方法では、種類を増やしたときに書き忘れても気づけません。`std::visit` は、`variant` に入っている値の型に合わせて、対応する処理を呼び出す関数です。すべての型に対応する処理がなければ、コンパイルエラーになります。

!!! tip "ポイント"
    - すべての型に対応する処理が**足りないと、コンパイルエラー**になる。型を増やしたとき、書き忘れに気づける。
    - `overloaded`（ラムダを束ねる小さなヘルパー）と組み合わせると読みやすい。
    - 複数の variant を同時に渡して、組み合わせで分岐もできる。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) の基本と、[ラムダ式](../../basics/lambda.md)を先に読んでください。

## 関数の詳しい説明

### std::visit {#visit}

```cpp
template <class Visitor, class... Variants>
constexpr decltype(auto) visit(Visitor&& vis, Variants&&... vars);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `vis` | 関数オブジェクト | **すべての候補の型**を受け取れる関数（ラムダの `auto` 引数か、overloaded） |
| `vars` | variant | 対象の variant（複数渡すと全組み合わせ） |

- 戻り値: `vis` の戻り値（すべての型で同じ型を返す必要がある）

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  std::variant<int, std::string> v = 42;
  // auto 引数のラムダなら全部の型を受け取れる
  std::visit([](const auto& x) { std::println("中身: {}", x); }, v);
  v = "text";
  std::visit([](const auto& x) { std::println("中身: {}", x); }, v);
}
```

```text title="実行結果"
中身: 42
中身: text
```

## ゲームでの使いどころ

敵の種類ごとの動きや、イベントの種類ごとの処理に使います。ラムダを束ねる `overloaded` というヘルパーを使うと、型ごとの処理を一か所に並べて書けます。

```cpp
std::visit(overloaded{
    [](const Slime& s) { /* スライムの動き */ },
    [](const Goblin& g) { /* ゴブリンの動き */ },
}, enemy);
```

型を増やすと、対応する処理がないものでコンパイルエラーになります。仮想関数と違い、型の種類をひとまとめに扱うので、後から処理を足したいときに便利です。

複数の `variant` を同時に渡して、組み合わせで分岐することもできます。2 つのオブジェクトの当たり判定を型の組み合わせごとに書く場面で使われます。

## よくあるミス

??? failure "対応する型を書き忘れて、コンパイルエラーの長いメッセージに悩む"
    型が足りないと、巨大なエラーメッセージが出ます。ほとんどの場合は、「どれかの型の処理が足りない」だけです。最後に `[](const auto&) {}` を置くと、残りを無視できますが、書き忘れに気づけなくなるので、意図的なときだけにします。

??? failure "戻り値の型がそろわない"
    すべての処理が同じ型を返す必要があります。`int` を返すものと `void` のものを混ぜると、コンパイルエラーです。

??? failure "値が入っていない `variant` に呼ぶ"
    例外で値が壊れた状態（`valueless_by_exception`）の `variant` に `visit` すると、`bad_variant_access` を投げます。通常は起きませんが、コンストラクターが例外を投げる型を入れるときは注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::get_if`](get_if.md) | 特定の型かだけを調べる |
| [`std::holds_alternative`](holds_alternative.md) | 今の型を調べる |
| virtual 関数 | 型ごとの処理をクラスに持たせる方法 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型ごとの処理を `overloaded` で並べて、`visit` に渡す。
    - [x] 型の処理が足りないと、コンパイルエラーで気づける。
    - [x] すべての処理が同じ型を返す。

## 関連ページ

- [cpprefjp: std::visit](https://cpprefjp.github.io/reference/variant/visit.html)
- [cppreference: std::visit](https://en.cppreference.com/w/cpp/utility/variant/visit)

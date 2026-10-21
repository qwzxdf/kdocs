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

`std::visit` は、**`std::variant` に入っている値の型に合わせて、対応する処理を呼び出す**関数です。「敵の種類ごとに動きを変える」「イベントの種類ごとに処理する」といった、型ごとの switch を書くときに使います。処理は、型ごとのオーバーロード（`overloaded` ヘルパー）で書くのが定番です。

!!! tip "ポイント"
    - すべての型に対応する処理が**足りないと、コンパイルエラー**になる。型を増やしたとき、書き忘れに気づける。
    - `overloaded`（ラムダを束ねる小さなヘルパー）と組み合わせると読みやすい。
    - 複数の variant を同時に渡して、組み合わせで分岐もできる。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

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

| 場面 | 書き方 |
| --- | --- |
| イベントの種類ごとの処理（入力、衝突、タイマー） | `std::visit(overloaded{...}, event)` |
| 状態ごとのデータを持つステートマシン | `std::visit(...)` |

## よくあるミス

??? failure "一部の型を書き忘れる"
    ラムダが足りないと、コンパイルエラーです。`[](auto&&) {}` を最後に付けると「その他」を受けられますが、型の追加を見逃しやすくなります。

??? failure "戻り値の型がそろわない"
    すべての処理の戻り値は同じ型でなければなりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::get_if`](get_if.md) | 特定の型かだけを調べる |
| [`std::holds_alternative`](holds_alternative.md) | 今の型を調べる |
| virtual 関数 | 型ごとの処理を、クラスに持たせる方法 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型ごとに処理を呼び分ける
    - [x] 書き忘れはコンパイルエラー
    - [x] `overloaded` と一緒に使う

## 関連ページ

- [cpprefjp: std::visit](https://cpprefjp.github.io/reference/variant/visit.html)
- [cppreference: std::visit](https://en.cppreference.com/w/cpp/utility/variant/visit)

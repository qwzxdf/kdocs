---
title: std::variant_npos
summary: "variant が値を持たない状態を表す、index() の値。"
order: 900
tags:
  - ユーティリティ
---

# std::variant_npos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::variant` の `index()` は、いま入っている型の番号を返します。ところが、まれに「どの型も入っていない」状態があります。型を入れ替える途中で例外が飛んだ場合です。そのとき `index()` が返すのが、`std::variant_npos` です。`size_t` の最大値で、有効な番号と区別できます。

!!! tip "ポイント"
    - `index() == std::variant_npos` なら、値を持たない状態（valueless）
    - 値は `static_cast<std::size_t>(-1)`
    - `valueless_by_exception()` で同じ判定ができる
    - 普通のコードでは起きない。例外を投げる型を入れるときだけ

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::variant_npos {#variant_npos}

<span class="ver ver-17">C++17</span>

```cpp
inline constexpr std::size_t variant_npos = -1;
```

`variant` は、型を入れ替える（`emplace` や代入）とき、古い値を破棄してから、新しい値を作ります。この途中で、新しい値の作成が例外を投げると、古い値はすでにないので、どの型も入っていない状態になります。それが valueless by exception です。

この状態の `variant` では、`index()` が `variant_npos` を返し、`valueless_by_exception()` が `true` を返します。`std::visit` を呼ぶと、`std::bad_variant_access` が投げられます。

`std::get<I>(v)` も、`bad_variant_access` を投げます。この状態から復帰するには、新しい値を代入（`emplace`）します。

例外を投げない型（`noexcept` なムーブを持つ型）だけを入れる `variant` なら、この状態は起きません。ゲームでは、ムーブで例外を投げる型は珍しいので、この状態を気にする場面はほとんどありません。

## 実際に動かしてみる

```cpp
#include <print>
#include <variant>

// ムーブで例外を投げる型
struct Thrower {
  Thrower() = default;
  Thrower(Thrower&&) { throw 1; }
};

int main() {
  std::variant<int, Thrower> v = 5;
  std::println("最初の番号: {}", v.index());

  try {
    v.emplace<Thrower>(Thrower{});  // 作る途中で例外が飛ぶ
  } catch (int) {
    std::println("例外が飛んだ");
  }

  std::println("valueless: {}", v.valueless_by_exception());
  std::println("index が variant_npos: {}", v.index() == std::variant_npos);

  v = 7;  // 値を入れ直せば復帰する
  std::println("復帰後の番号: {}", v.index());
}
```

```text title="実行結果"
最初の番号: 0
例外が飛んだ
valueless: true
index が variant_npos: true
復帰後の番号: 0
```

## ゲームでの使いどころ

`std::visit` の前に毎回調べる必要はありません。ムーブで例外を投げる型を `variant` に入れてしまう設計を、避けるのが先です。

## よくあるミス

??? failure "index() を switch で使い、npos を忘れる"
    `variant_npos` の分岐がないと、想定外の番号が来ます。例外を投げる型を入れるなら、考慮します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::variant`](variant.md) | 本体 |
| `valueless_by_exception()` | 同じ状態を調べるメンバー関数 |
| [`std::monostate`](monostate.md) | 空の状態を明示的に持たせる型 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::variant_npos](https://cpprefjp.github.io/reference/variant/variant_npos.html)
- [cppreference: std::variant_npos](https://en.cppreference.com/w/cpp/utility/variant/variant_npos)

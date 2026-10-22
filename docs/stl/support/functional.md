---
title: <functional>（関数オブジェクト・invoke・hash など）
summary: "比較（`greater`）・参照渡し（`ref`）・引数の固定（`bind_front`）などの、関数の道具。"
order: 83
tags:
  - 型・言語サポート
---

# &lt;functional&gt;（関数オブジェクト・invoke・hash など）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <functional>`
</div>

`<functional>` は、**関数を扱うための道具**をまとめたヘッダです。関数を入れておく [`std::function`](../utilities/function.md) のほかに、足し算や比較を表す**関数オブジェクト**（`std::plus`、`std::greater` など）、何でも呼び出せる `std::invoke`、引数を一部固定する `std::bind_front`、参照を値のように渡す `std::ref`、ハッシュ値を作る `std::hash` などがあります。

!!! tip "ポイント"
    - 並べ替えの比較には `std::greater{}`、合計には `std::plus{}` を渡す。
    - 自作の型を unordered_map のキーにするなら `std::hash` を使ってハッシュを作る。
    - スレッドや bind に**参照で**渡したいときは `std::ref(x)`。
    - 引数の一部を固定した関数を作るなら、`std::bind` ではなくラムダか `std::bind_front`。

## 関数一覧

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::function`](../utilities/function.md) | <span class="rank rank-often">よく使う</span> | 関数を変数に入れる（別ページ） |
| [`std::greater`](functional/greater.md) | <span class="rank rank-often">よく使う</span> | `a > b` を表す関数オブジェクト |
| [`std::less`](functional/less.md) | <span class="rank rank-often">よく使う</span> | `a < b` を表す関数オブジェクト |
| [`std::hash`](../utilities/hash.md) | <span class="rank rank-sometimes">たまに</span> | ハッシュ値を作る |
| [`std::ref`](functional/ref.md) | <span class="rank rank-sometimes">たまに</span> | 参照を値のように渡す |
| [`std::plus`](functional/plus.md) | <span class="rank rank-sometimes">たまに</span> | `a + b` を表す関数オブジェクト |
| [`std::invoke`](functional/invoke.md) | <span class="rank rank-sometimes">たまに</span> | 関数・メンバ関数・メンバ変数を同じ書き方で呼ぶ <span class="ver ver-17">C++17</span> |
| [`std::bind_front`](functional/bind_front.md) | <span class="rank rank-sometimes">たまに</span> | 前の引数を固定した関数を作る <span class="ver ver-20">C++20</span> |
| [`std::cref`](functional/ref.md) | <span class="rank rank-rare">知ってるだけ</span> | const 参照を値のように渡す |
| [`std::equal_to`](functional/equal_to.md) | <span class="rank rank-rare">知ってるだけ</span> | `a == b` を表す関数オブジェクト |
| [`std::multiplies`](functional/multiplies.md) | <span class="rank rank-rare">知ってるだけ</span> | `a * b` を表す関数オブジェクト |
| [`std::identity`](functional/identity.md) | <span class="rank rank-rare">知ってるだけ</span> | 受け取ったものをそのまま返す <span class="ver ver-20">C++20</span> |
| [`std::bind_back`](functional/bind_back.md) | <span class="rank rank-rare">知ってるだけ</span> | 後ろの引数を固定 <span class="ver ver-23">C++23</span> |
| [`std::not_fn`](functional/not_fn.md) | <span class="rank rank-rare">知ってるだけ</span> | 条件の結果を反転した関数を作る <span class="ver ver-17">C++17</span> |
| [`std::bind`](functional/bind.md) | <span class="rank rank-rare">知ってるだけ</span> | 古い引数の固定（使わない） |
| [`std::mem_fn`](functional/mem_fn.md) | <span class="rank rank-rare">知ってるだけ</span> | メンバ関数を普通の関数のように呼べるようにする |
| [`std::minus`](functional/minus.md) | <span class="rank rank-rare">知ってるだけ</span> | `a - b` を表す関数オブジェクト。 |
| [`std::divides`](functional/divides.md) | <span class="rank rank-rare">知ってるだけ</span> | `a / b` を表す関数オブジェクト。 |
| [`std::modulus`](functional/modulus.md) | <span class="rank rank-rare">知ってるだけ</span> | `a % b`（余り）を表す関数オブジェクト。 |
| [`std::negate`](functional/negate.md) | <span class="rank rank-rare">知ってるだけ</span> | `-a`（符号の反転）を表す関数オブジェクト。 |
| [`std::not_equal_to`](functional/not_equal_to.md) | <span class="rank rank-rare">知ってるだけ</span> | `a != b` を表す関数オブジェクト。 |
| [`std::greater_equal`](functional/greater_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | `a >= b` を表す関数オブジェクト。 |
| [`std::less_equal`](functional/less_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | `a <= b` を表す関数オブジェクト。 |
| [`std::logical_and`](functional/logical_and.md) | <span class="rank rank-rare">知ってるだけ</span> | `a && b` を表す関数オブジェクト。 |
| [`std::logical_or`](functional/logical_or.md) | <span class="rank rank-rare">知ってるだけ</span> | `a || b` を表す関数オブジェクト。 |
| [`std::logical_not`](functional/logical_not.md) | <span class="rank rank-rare">知ってるだけ</span> | `!a` を表す関数オブジェクト。 |
| [`std::bit_and`](functional/bit_and.md) | <span class="rank rank-rare">知ってるだけ</span> | `a & b`（ビットごとの AND）を表す関数オブジェクト。 |
| [`std::bit_or`](functional/bit_or.md) | <span class="rank rank-rare">知ってるだけ</span> | `a \| b`（ビットごとの OR）を表す関数オブジェクト。 |
| [`std::bit_xor`](functional/bit_xor.md) | <span class="rank rank-rare">知ってるだけ</span> | `a ^ b`（ビットごとの XOR）を表す関数オブジェクト。 |
| [`std::bit_not`](functional/bit_not.md) | <span class="rank rank-rare">知ってるだけ</span> | `~a`（ビット反転）を表す関数オブジェクト。 |
| [`std::invoke_r`](functional/invoke_r.md) | <span class="rank rank-rare">知ってるだけ</span> | 呼び出しの結果を、指定した戻り値の型に変換して返す。 <span class="ver ver-23">C++23</span> |
| [`std::unwrap_reference`](functional/unwrap_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | reference_wrapper を、ふつうの参照の型に戻す型変換。 <span class="ver ver-20">C++20</span> |
| [`std::unwrap_ref_decay`](functional/unwrap_ref_decay.md) | <span class="rank rank-rare">知ってるだけ</span> | decay してから、reference_wrapper を参照に戻す型変換。 <span class="ver ver-20">C++20</span> |
| [`std::placeholders`](functional/placeholders.md) | <span class="rank rank-rare">知ってるだけ</span> | bind の引数の位置を表す _1, _2, … の名前空間。 |
| [`std::is_bind_expression`](functional/is_bind_expression.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が bind の式かどうかを調べる型特性。 <span class="ver ver-17">C++17</span> |
| [`std::is_placeholder`](functional/is_placeholder.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がプレースホルダー（_1 など）か、何番かを調べる型特性。 <span class="ver ver-17">C++17</span> |
| [`std::copyable_function`](functional/copyable_function.md) | <span class="rank rank-rare">知ってるだけ</span> | コピーできる、const や noexcept も指定できる関数のラッパー。 <span class="ver ver-26">C++26</span> |
| [`std::function_ref`](functional/function_ref.md) | <span class="rank rank-rare">知ってるだけ</span> | 呼び出せるものを借りて参照するだけの、軽い関数ラッパー。 <span class="ver ver-26">C++26</span> |
| [`std::default_searcher`](functional/default_searcher.md) | <span class="rank rank-rare">知ってるだけ</span> | `std::search` に渡せる、素朴な部分列検索のオブジェクト。 <span class="ver ver-17">C++17</span> |
| [`std::boyer_moore_searcher`](functional/boyer_moore_searcher.md) | <span class="rank rank-rare">知ってるだけ</span> | 長い列の中から部分列を速く探す検索のオブジェクト（ボイヤー・ムーア法）。 <span class="ver ver-17">C++17</span> |
| [`std::boyer_moore_horspool_searcher`](functional/boyer_moore_horspool_searcher.md) | <span class="rank rank-rare">知ってるだけ</span> | ボイヤー・ムーア・ホースプール法で部分列を探す検索のオブジェクト。 <span class="ver ver-17">C++17</span> |

## よくある使い方

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {70, 100, 40};
  std::ranges::sort(scores, std::greater{});  // 大きい順

  auto damage = [](int base, int bonus) { return base + bonus; };
  auto sword = std::bind_front(damage, 50);   // base を 50 に固定
  std::println("{} / {} {}", scores, sword(5), sword(20));
}
```

```text title="実行結果"
[100, 70, 40] / 55 70
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 道具 |
| --- | --- |
| 大きい順に並べる | `std::greater{}` |
| 自作の座標を unordered_map のキーに | `std::hash` で組み合わせる |
| メンバ関数をコールバックに | `std::bind_front(&Class::Func, this)` |
| スレッドに参照を渡す | `std::ref` |

## よくあるミス

??? failure "std::bind で読めないコードになる"
    `std::bind(&F, _2, 10, _1)` は何をしているか分かりにくいです。ラムダで書きます。

??? failure "ハッシュの組み合わせを x ^ y にする"
    `(1, 2)` と `(2, 1)`、`(3, 3)` と `(0, 0)` が同じハッシュになり、衝突が増えます。上の例のようにずらして混ぜます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 比較は std::greater{} / std::less{}
    - [x] 自作の型のハッシュは std::hash を組み合わせる
    - [x] 参照を渡すなら std::ref
    - [x] 引数の固定はラムダか bind_front

## 関連ページ

- [std::function](../utilities/function.md)
- [cppreference: Function objects](https://en.cppreference.com/w/cpp/utility/functional)

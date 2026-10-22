---
title: std::ranges::any_of
summary: "条件を満たす要素が、1 つでもあるかを調べる。"
order: 23
tags:
  - アルゴリズム
---

# std::ranges::any_of

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

生きている敵が 1 体でもいるか、プレイヤーが何かに当たったか。「条件を満たすものが 1 つでもあるか」を調べるには、フラグ変数を用意して `for` で回し、見つかったら `break` する、という数行のコードを書くことになります。`std::ranges::any_of` は、その判定を 1 行で書ける関数です。最初の `true` が見つかった時点で調べるのをやめます。

!!! tip "ポイント"
    - 「生きている敵がいるか」「何かに当たったか」のような、**どれか 1 つ**を調べるときに使う。
    - 答えが決まった時点（1 つ目の `true`）で止まるので、無駄に全部を見ない。
    - **空の範囲**では必ず `false`。

!!! info "このページを読む前に"
    [`ranges` とビュー](../../basics/ranges.md)と[ラムダ式](../../basics/lambda.md)が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::any_of {#any_of}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr bool any_of(R&& r, Pred pred, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 調べる範囲 | 省略不可 |
| `pred` | 関数・ラムダ | 要素を受け取って `bool` を返す | 省略不可 |
| `proj` | プロジェクション | `pred` に渡す前の変換 | そのまま |

- 戻り値: `pred` が `true` になる要素が 1 つでもあれば `true`。空なら `false`
- 計算量: O(n)。`true` が見つかった時点で止まる

<div class="anim" data-label="std::ranges::any_of(v, is_even)">
1 3 4 5 # 偶数が 1 つでもあるか
*1 3 4 5 # 1 は偶数ではない
1 *3 4 5 # 3 も違う
1 3 *4 5 # 4 は偶数。ここで true を返して終わる
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> damage = {0, 0, 15, 0};
  bool hit = std::ranges::any_of(damage, [](int d) { return d > 0; });
  std::println("ダメージを受けた？ {}", hit);
}
```

```text title="実行結果"
ダメージを受けた？ true
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `pred` | <span class="rank rank-sometimes">たまに</span> | `&Type::bool_member` | bool のメンバがそのまま条件になる |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバを取り出してから `pred` に渡す |

```cpp
#include <algorithm>
#include <print>
#include <vector>

struct Collider {
  bool overlapping;
};

int main() {
  std::vector<Collider> colliders = {{false}, {true}, {false}};
  // メンバポインタを pred に直接渡せる
  std::println("何かに当たっている？ {}", std::ranges::any_of(colliders, &Collider::overlapping));
}
```

```text title="実行結果"
何かに当たっている？ true
```

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    bool any_alive = false;
    for (const auto& e : enemies) {
      if (e.hp > 0) {
        any_alive = true;
        break;
      }
    }
    ```

=== "今の書き方（C++20）"

    ```cpp
    bool any_alive = std::ranges::any_of(enemies, [](const Enemy& e) { return e.hp > 0; });
    ```

## ゲームでの使いどころ

戦闘が続くかの判定に使います。`std::ranges::any_of(enemies, &Enemy::alive)` が `false` になったら、勝利の処理へ進みます。

当たり判定にも向いています。弾が敵のどれか 1 体に当たったか、プレイヤーがトラップのどれかに触れたか、を調べます。どれに当たったかも必要なら、位置を返す `find_if` を使います。

入力の判定では、`any_of(keys, IsPressed)` で「いずれかのキーが押されているか」を調べます。「どのキーか」が必要なら、やはり `find_if` です。

## よくあるミス

??? failure "`any_of` の結果から要素を取り出そうとする"
    `any_of` は `bool` を返すだけで、見つかった要素は教えてくれません。要素も必要なら、`find_if` で位置を取り、`end()` と比べます。

??? failure "空の範囲での結果を取り違える"
    空の範囲では必ず `false` です。「敵がいない」と「敵が全員倒れている」を区別しないと、バグになります。意図を明確にするために、`empty()` と組み合わせて書きます。

??? failure "条件で毎回重い計算をする"
    条件のラムダ式の中で、要素ごとに距離計算などの重い処理をすると、要素が多いときに遅くなります。あらかじめ計算した値をメンバーに持っておき、比較だけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`all_of`](all_of.md) | 全部が満たすか |
| [`none_of`](none_of.md) | 1 つも満たさないか。`any_of` の否定 |
| [`find_if`](find.md) | 最初に見つかった要素の位置が必要なとき |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「1 つでもあるか」は `any_of` 1 行。
    - [x] 空の範囲では `false`。
    - [x] 見つけた要素が必要なら `find_if`。

## 関連ページ

- [cpprefjp: std::ranges::any_of](https://cpprefjp.github.io/reference/algorithm/ranges_any_of.html)
- [cppreference: std::ranges::any_of](https://en.cppreference.com/w/cpp/algorithm/ranges/all_any_none_of)

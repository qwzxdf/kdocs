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

`std::ranges::any_of` は、**範囲の中に、条件を満たす要素が 1 つでもあるかどうかを `bool` で答える**関数です。for ループとフラグ変数で書いていた判定が 1 行になり、読む人にも意図が伝わります。

!!! tip "ポイント"
    - 「生きている敵がいるか」「何かに当たったか」のような、**どれか 1 つ**を調べるときに使う。
    - 答えが決まった時点（1 つ目の `true`）で止まるので、無駄に全部を見ない。
    - **空の範囲**では必ず `false`。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) で条件を書きます。

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

| 場面 | 書き方 |
| --- | --- |
| 何かに当たったか | `any_of(colliders, 重なっている)` |
| まだ敵が残っているか | `any_of(enemies, 生きている)` |
| 入力があったか | `any_of(keys, 押されている)` |

## よくあるミス

??? failure "空の範囲だと false になる"
    空の範囲では必ず `false` です。「1 つもない」ことを調べたいなら [`none_of`](none_of.md) のほうが意図が伝わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::all_of`](all_of.md) | 全部が条件を満たすか |
| [`std::ranges::none_of`](none_of.md) | 1 つも満たさないか（`!any_of` と同じ） |
| [`std::ranges::find_if`](find.md) | 最初に見つかった位置を返す。「どれ？」まで知りたいとき |
| [`std::ranges::count_if`](count.md) | 何個あるかを返す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 つでも条件を満たす要素があれば `true`
    - [x] 答えが決まった時点で止まる
    - [x] 空の範囲は `false`

## 関連ページ

- [cpprefjp: std::ranges::any_of](https://cpprefjp.github.io/reference/algorithm/ranges_any_of.html)
- [cppreference: std::ranges::any_of](https://en.cppreference.com/w/cpp/algorithm/ranges/all_any_none_of)

---
title: std::ranges::any_of / all_of / none_of
tags:
  - アルゴリズム
---

# std::ranges::any_of / all_of / none_of

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`any_of`、`all_of`、`none_of` は、**範囲の要素が条件を満たすかどうかを `bool` で答える**関数です。「どれか 1 つでも」「全部」「1 つも〜ない」の 3 種類があります。for ループとフラグ変数で書いていた判定が 1 行で書けて、読む人にも意図が伝わりやすくなります。

!!! tip "ポイント"
    - 「生きている敵がいるか」は `any_of`、「全員準備完了か」は `all_of`、「1 人も死んでいないか」は `none_of`。
    - 答えが決まった時点で止まるので、無駄に全部見ない。
    - **空の範囲**では `any_of` は `false`、`all_of` と `none_of` は `true` になる。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) で条件を書きます。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::any_of`](#any_of) | <span class="rank rank-often">よく使う</span> | 条件を満たすものが**1 つでも**あるか | O(n) |
| [`std::ranges::all_of`](#all_of) | <span class="rank rank-often">よく使う</span> | **全部**が条件を満たすか | O(n) |
| [`std::ranges::none_of`](#none_of) | <span class="rank rank-sometimes">たまに</span> | 条件を満たすものが**1 つも無い**か | O(n) |

## よくある使い方

### ステージクリア判定

```cpp
#include <algorithm>
#include <print>
#include <vector>

struct Enemy {
  int hp;
  bool is_boss;
};

int main() {
  std::vector<Enemy> enemies = {{0, false}, {12, false}, {0, true}};

  bool any_alive = std::ranges::any_of(enemies, [](const Enemy& e) { return e.hp > 0; });
  bool boss_dead = std::ranges::none_of(
      enemies, [](const Enemy& e) { return e.is_boss && e.hp > 0; });

  std::println("まだ敵がいる？ {} / ボスは倒した？ {}", any_alive, boss_dead);
}
```

```text title="実行結果"
まだ敵がいる？ true / ボスは倒した？ true
```

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

### std::ranges::all_of {#all_of}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr bool all_of(R&& r, Pred pred, Proj proj = {});
```

- 戻り値: 全要素で `pred` が `true` なら `true`。**空なら `true`**
- 計算量: O(n)。`false` が見つかった時点で止まる

<div class="anim" data-label="std::ranges::all_of(v, is_even)">
2 4 5 6 # すべて偶数か
*2 4 5 6 # 2 は偶数
2 *4 5 6 # 4 も偶数
2 4 *5 6 # 5 は偶数ではない。ここで false を返して終わる
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

struct Player {
  bool ready;
};

int main() {
  std::vector<Player> players = {{true}, {true}, {false}};
  std::println("全員準備 OK？ {}", std::ranges::all_of(players, &Player::ready));
}
```

```text title="実行結果"
全員準備 OK？ false
```

`pred` にメンバポインタ `&Player::ready` を直接渡すと、「そのメンバが `true` か」で判定できます。

### std::ranges::none_of {#none_of}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr bool none_of(R&& r, Pred pred, Proj proj = {});
```

- 戻り値: `pred` が `true` になる要素が 1 つも無ければ `true`。**空なら `true`**
- `!any_of(...)` と同じ意味です

<div class="anim" data-label="std::ranges::none_of(v, is_even)">
1 3 4 5 # 偶数が 1 つもないか
*1 3 4 5 # 1 は偶数ではない
1 *3 4 5 # 3 も違う
1 3 *4 5 # 4 は偶数。ここで false を返して終わる
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> hp = {30, 12, 50};
  bool no_one_dead = std::ranges::none_of(hp, [](int h) { return h <= 0; });
  std::println("誰も倒れていない？ {}", no_one_dead);
}
```

```text title="実行結果"
誰も倒れていない？ true
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `pred` | <span class="rank rank-sometimes">たまに</span> | `&Type::bool_member` | bool のメンバがそのまま条件になる |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバを取り出してから `pred` に渡す |

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

| 場面 | 関数 |
| --- | --- |
| ステージクリア（敵が全滅したか） | `none_of(enemies, 生きている)` |
| 全員そろったか | `all_of(players, &Player::ready)` |
| 何かに当たったか | `any_of(colliders, 重なっている)` |
| ロードが終わったか | `all_of(assets, 読み込み済み)` |

## よくあるミス

??? failure "空の範囲で all_of が true になる"
    敵が 0 体のとき、`all_of(enemies, 倒れている)` は `true` です。「敵が 1 体もいない」と「全員倒した」を区別したいなら、`!enemies.empty() &&` を付けます。

## 理解度チェック

!!! question "Q1. 空の vector に対する any_of / all_of / none_of の結果は？"
    <div class="spoiler" markdown>

    **答え:** `any_of` は `false`、`all_of` と `none_of` は `true`。「満たさないものが 1 つも無い」ので all は true になります。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find_if`](find.md) | 最初に見つかった位置を返す |
| [`std::ranges::count_if`](count_if.md) | 何個あるかを返す |
| [`std::ranges::contains`](find.md#contains) | 値が含まれているか <span class="ver ver-23">C++23</span> |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 つでも → `any_of`、全部 → `all_of`、1 つも無い → `none_of`
    - [x] 答えが決まった時点で止まる
    - [x] 空なら all_of / none_of は true

## 関連ページ

- [cpprefjp: std::ranges::all_of](https://cpprefjp.github.io/reference/algorithm/ranges_all_of.html)
- [cppreference: std::ranges::all_of, any_of, none_of](https://en.cppreference.com/w/cpp/algorithm/ranges/all_any_none_of)

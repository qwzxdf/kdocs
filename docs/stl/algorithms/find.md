---
title: std::ranges::find
summary: "条件に合う最初の要素を探す。見つからなければ `end()` が返る。"
order: 22
tags:
  - アルゴリズム
---

# std::ranges::find

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::find` は、**範囲の中から値を先頭から順に探す**関数です。`find_if` は「条件に合う最初の要素」を探します。見つかればその位置（イテレータ）を、見つからなければ範囲の終わり（`end()`）を返します。「あるかどうか」だけを知りたいなら、C++23 の [`std::ranges::contains`](contains.md) が使えます。

!!! tip "ポイント"
    - <strong>条件で探すなら `find_if`、値で探すなら `find`。</strong> 結果は必ず `end()` と比べる。
    - あるかどうかだけなら C++23 の [`std::ranges::contains`](contains.md) が一番短い。最後の要素を探すなら [`find_last`](find_last.md)。
    - 構造体のメンバで探すならプロジェクション: `std::ranges::find(enemies, 42, &Enemy::id)`。
    - 先頭から順に見るので O(n)。何度も探すなら `unordered_map` などを検討する。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md)、[ラムダ式](../../basics/lambda.md) が分かると読みやすいです。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::find_if`](#find_if) | <span class="rank rank-must">必須</span> | 条件に合う最初の要素を探す | O(n) |
| [`std::ranges::find`](#find) | <span class="rank rank-must">必須</span> | 値と等しい最初の要素を探す | O(n) |
| [`std::ranges::find_if_not`](#find_if_not) | <span class="rank rank-sometimes">たまに</span> | 条件に合わない最初の要素を探す | O(n) |

## よくある使い方

### 1. ID で探す

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Enemy {
  int id;
  std::string name;
};

int main() {
  std::vector<Enemy> enemies = {{7, "スライム"}, {42, "ゴブリン"}, {9, "コウモリ"}};

  // id が 42 のものを探す（プロジェクションでメンバを指定）
  auto it = std::ranges::find(enemies, 42, &Enemy::id);
  if (it != enemies.end()) {
    std::println("見つかった: {}", it->name);
  }
}
```

```text title="実行結果"
見つかった: ゴブリン
```

### 2. 条件で探す

```cpp
#include <algorithm>
#include <cmath>
#include <print>
#include <vector>

struct Enemy {
  float x;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {{10.0f, 0}, {35.0f, 20}, {50.0f, 80}};
  float player_x = 30.0f;

  // 近くにいる（距離 10 以内）生きている敵
  auto it = std::ranges::find_if(enemies, [&](const Enemy& e) {
    return e.hp > 0 && std::abs(e.x - player_x) <= 10.0f;
  });

  if (it != enemies.end()) {
    std::println("x = {} の敵をターゲット", it->x);
  }
}
```

```text title="実行結果"
x = 35 の敵をターゲット
```

### 3. 見つけた位置から添字を出す

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> stage_ids = {101, 102, 205, 301};
  auto it = std::ranges::find(stage_ids, 205);
  if (it != stage_ids.end()) {
    auto index = it - stage_ids.begin();  // イテレータ同士の引き算で添字になる
    std::println("{} 番目", index);
  }
}
```

```text title="実行結果"
2 番目
```

## 関数の詳しい説明

### std::ranges::find_if {#find_if}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr borrowed_iterator_t<R> find_if(R&& r, Pred pred, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 探す範囲（vector、array、map など何でも） | 省略不可 |
| `pred` | 関数・ラムダ | 要素を受け取り、**探しているものなら `true`** | 省略不可 |
| `proj` | プロジェクション | `pred` に渡す前に要素を変換する | そのまま |

- 戻り値: 最初に `pred` が `true` になった要素のイテレータ。無ければ `end()`
- 計算量: O(n)。見つかった時点で止まる

!!! note "実際は"
    「条件に合う最初の 1 つ」を探すときの基本です。全部欲しいなら `std::views::filter` を使います。

<div class="anim" data-label="std::ranges::find_if(v, is_big)">
1 5 12 3 # 10 以上で最初のもの
*1 5 12 3 # 違う
1 *5 12 3 # 違う
1 5 *12 3 # 見つかる
</div>

### std::ranges::find {#find}

```cpp
template <input_range R, class T, class Proj = identity>
constexpr borrowed_iterator_t<R> find(R&& r, const T& value, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 探す範囲 | 省略不可 |
| `value` | `const T&` | 探す値。要素（またはプロジェクションの結果）と `==` で比べる | 省略不可 |
| `proj` | プロジェクション | 比べる前に要素を変換する（`&Enemy::id` など） | そのまま |

- 戻り値: 最初に見つかった要素のイテレータ。無ければ `end()`
- 計算量: O(n)

<div class="anim" data-label="std::ranges::find(v, 30)">
10 20 30 40 # v
*10 20 30 40 # 先頭から順に比べる
10 *20 30 40 # 違う
10 20 *30 40 # 見つかる。その位置を返す
</div>

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> party = {"勇者", "魔法使い", "僧侶"};
  auto it = std::ranges::find(party, "魔法使い");
  std::println("いる？ {}", it != party.end());
}
```

```text title="実行結果"
いる？ true
```

### std::ranges::find_if_not {#find_if_not}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr borrowed_iterator_t<R> find_if_not(R&& r, Pred pred, Proj proj = {});
```

- 戻り値: `pred` が **`false`** になった最初の要素のイテレータ

<div class="anim" data-label="std::ranges::find_if_not(v, is_even)">
2 4 5 6 # 偶数でない最初のもの
*2 4 5 6 # 偶数
2 *4 5 6 # 偶数
2 4 *5 6 # 見つかる
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<bool> loaded = {true, true, false, true};
  auto it = std::ranges::find_if_not(loaded, [](bool b) { return b; });
  std::println("{} 番目がまだ読み込まれていない", it - loaded.begin());
}
```

```text title="実行結果"
2 番目がまだ読み込まれていない
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `proj` | <span class="rank rank-often">よく使う</span> | `&Type::member` | メンバで比べる |
| `proj` | <span class="rank rank-sometimes">たまに</span> | ラムダ式 | 計算した値で比べる |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    auto it = std::find_if(enemies.begin(), enemies.end(),
                           [](const Enemy& e) { return e.id == 42; });
    bool has = std::find(v.begin(), v.end(), 5) != v.end();
    ```

=== "今の書き方（C++23）"

    ```cpp
    auto it = std::ranges::find(enemies, 42, &Enemy::id);
    bool has = std::ranges::contains(v, 5);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ID でオブジェクトを探す | `find(objects, id, &Object::id)` |
| 条件に合う最初の 1 体 | 近くにいる敵、空いているスロット |
| 持っているか | `contains(inventory, item_id)` |

## パフォーマンス

- 先頭から順に見るので、要素が多いと遅くなります。毎フレーム何百回も探すなら、`std::unordered_map<Id, 添字>` を別に持つと O(1) になります。
- 要素が少ない（数十個まで）なら、ハッシュ表より vector の `find` のほうが速いことも多いです。
- ソート済みなら [`std::ranges::lower_bound`](binary_search.md) で O(log n) で探せます。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 見つからなかった（`end()`）のに `*it` / `it->` で読む | 未定義動作 |

## よくあるミス

??? failure "end() と比べずに使う"
    ```cpp
    auto it = std::ranges::find(enemies, 99, &Enemy::id);
    it->hp -= 10;  // 見つからなかったら未定義動作

    if (it != enemies.end()) {
      it->hp -= 10;  // OK
    }
    ```

??? failure "map で std::ranges::find を使う"
    map に対して `std::ranges::find` を使うと O(n) で全部見てしまいます。map / set / unordered_map はメンバ関数の `m.find(key)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::any_of`](any_of.md) | 条件に合うものがあるかを bool で返す |
| [`std::ranges::count_if`](count.md) | 条件に合う数を数える |
| [`std::ranges::lower_bound`](binary_search.md) | ソート済み範囲を二分探索 |
| `std::views::filter` | 条件に合うものを全部取り出す |
| `m.find(key)`（map などのメンバ） | キーで O(log n) / O(1) で探す |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::ranges::find` / `find_if` <span class="ver ver-20">C++20</span> | ○ | ○ | ○ |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件なら `find_if`、値なら `find`
    - [x] 結果は必ず `end()` と比べる
    - [x] あるかだけなら `std::ranges::contains`
    - [x] map などはメンバの `find` を使う

## 関連ページ

- [cpprefjp: std::ranges::find](https://cpprefjp.github.io/reference/algorithm/ranges_find.html)
- [cppreference: std::ranges::find](https://en.cppreference.com/w/cpp/algorithm/ranges/find)

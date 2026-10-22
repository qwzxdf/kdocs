---
title: std::ranges::all_of
summary: "範囲の要素が全部、条件を満たすかを調べる。"
order: 24
tags:
  - アルゴリズム
---

# std::ranges::all_of

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

パーティ全員が準備完了か、アセットを全部読み込んだか。「全部が条件を満たすか」を調べるには、`for` で回して、1 つでも満たさなければ `false` を返す、というコードを毎回書くことになります。`std::ranges::all_of` は、その判定を 1 行で書ける関数です。条件を満たさない要素が見つかった時点で調べるのをやめるので、無駄がありません。

!!! tip "ポイント"
    - 「全員」「全部」を確かめたいときに使う。
    - 条件を満たさない要素が 1 つ見つかった時点で止まる。
    - **空の範囲では `true`** になる。「0 個の中では全員が条件を満たす」と考えるため。

!!! info "このページを読む前に"
    [`ranges` とビュー](../../basics/ranges.md)と[ラムダ式](../../basics/lambda.md)が分かると読みやすいです。

## 関数の詳しい説明

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

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `pred` | <span class="rank rank-sometimes">たまに</span> | `&Type::bool_member` | bool のメンバがそのまま条件になる |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバを取り出してから `pred` に渡す |

```cpp
#include <algorithm>
#include <print>
#include <vector>

struct Asset {
  int loaded_bytes;
  int total_bytes;
};

int main() {
  std::vector<Asset> assets = {{100, 100}, {80, 100}};
  // 読み込んだ量が全体に達しているかを、すべてのアセットで調べる
  bool done = std::ranges::all_of(assets, [](const Asset& a) { return a.loaded_bytes == a.total_bytes; });
  std::println("ロード完了？ {}", done);
}
```

```text title="実行結果"
ロード完了？ false
```

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    bool all_ready = true;
    for (const auto& p : players) {
      if (!p.ready) {
        all_ready = false;
        break;
      }
    }
    ```

=== "今の書き方（C++20）"

    ```cpp
    bool all_ready = std::ranges::all_of(players, &Player::ready);
    ```

## ゲームでの使いどころ

状態がそろったことを待つ場面で使います。`std::ranges::all_of(party, &Member::ready)` が `true` になったら戦闘を開始する、読み込みが全部終わったらタイトル画面へ進む、といった形です。

ステージのクリア条件にも向いています。すべての敵が倒れたか、すべてのスイッチが押されたか、を 1 行で判定できます。

空の範囲では `true` が返る点には注意が必要です。敵が 0 体のとき、「全員が倒れている」は真になります。敵がいない状況を別に扱いたいなら、`empty()` を先に確かめます。

## よくあるミス

??? failure "空の範囲で `true` になって、早すぎる判定になる"
    敵のリストが空のとき、`all_of(enemies, &Enemy::dead)` は `true` です。ステージの開始直前に、まだ敵を配置していないと、いきなりクリア判定になります。`!enemies.empty() && all_of(...)` のように、空でないことも確かめます。

??? failure "`none_of` で書くべき条件を、否定した `all_of` で書く"
    `all_of(v, [](auto& x) { return !x.alive; })` は読みにくいので、`none_of(v, &X::alive)` と書きます。「全員が〜でない」は、`none_of` と同じ意味です。

??? failure "条件に副作用を入れる"
    条件のラムダ式の中でカウンターを増やすと、途中で止まるため、全要素には実行されません。副作用のある処理は、条件の中に入れません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`any_of`](any_of.md) | 1 つでも満たすものがあるか。全員ではなく、誰か 1 人を調べる |
| [`none_of`](none_of.md) | 1 つも満たさないか。`all_of` の否定の形 |
| [`count_if`](count.md) | 満たす数を数える。数が必要なときはこちら |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「全部が条件を満たすか」は `all_of` 1 行で書ける。
    - [x] 空の範囲では `true`。空を別に扱いたいときは、先に `empty()` を調べる。
    - [x] 条件を満たさない要素が見つかった時点で止まる。

## 関連ページ

- [cpprefjp: std::ranges::all_of](https://cpprefjp.github.io/reference/algorithm/ranges_all_of.html)
- [cppreference: std::ranges::all_of](https://en.cppreference.com/w/cpp/algorithm/ranges/all_any_none_of)

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

`std::ranges::all_of` は、**範囲のすべての要素が条件を満たすかどうかを `bool` で答える**関数です。「全員準備完了か」「全部のアセットを読み込んだか」を 1 行で書けます。

!!! tip "ポイント"
    - 「全員」「全部」を確かめたいときに使う。
    - 条件を満たさない要素が 1 つ見つかった時点で止まる。
    - **空の範囲では `true`** になる。「0 個の中では全員が条件を満たす」と考えるため。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) で条件を書きます。

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

| 場面 | 書き方 |
| --- | --- |
| 全員そろったか | `all_of(players, &Player::ready)` |
| ロードが終わったか | `all_of(assets, 読み込み済み)` |
| 全部のスイッチが入ったか | `all_of(switches, オンになっている)` |

## よくあるミス

??? failure "空の範囲で true になる"
    敵が 0 体のとき、`all_of(enemies, 倒れている)` は `true` です。「敵が 1 体もいない」と「全員倒した」を区別したいなら、`!enemies.empty() &&` を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::any_of`](any_of.md) | 1 つでも条件を満たすか |
| [`std::ranges::none_of`](none_of.md) | 1 つも満たさないか |
| [`std::ranges::equal`](equal.md) | 2 つの範囲が同じ中身か |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全部が条件を満たせば `true`
    - [x] 1 つでも満たさないものが見つかった時点で止まる
    - [x] **空の範囲は `true`**（ここでハマる）

## 関連ページ

- [cpprefjp: std::ranges::all_of](https://cpprefjp.github.io/reference/algorithm/ranges_all_of.html)
- [cppreference: std::ranges::all_of](https://en.cppreference.com/w/cpp/algorithm/ranges/all_any_none_of)

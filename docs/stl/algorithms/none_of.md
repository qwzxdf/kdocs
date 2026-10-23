---
title: std::ranges::none_of
summary: "範囲の要素が 1 つも条件を満たさないかを調べる。"
order: 25
tags:
  - アルゴリズム
---

# std::ranges::none_of

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

敵が全滅したか、警告が 1 つも出ていないか。「1 つも〜ない」ことを確かめたいとき、`!any_of(...)` と書くと、二重の否定で読みにくくなります。`std::ranges::none_of` は、範囲の中に条件を満たす要素が 1 つも無いかを、`bool` で答えます。`any_of` の否定と同じ意味ですが、意図がそのまま読めます。

!!! tip "ポイント"
    - `none_of(r, p)` は `!any_of(r, p)` と同じ意味。「1 つも〜ない」と読めるほうを選ぶ。
    - 条件を満たす要素が 1 つ見つかった時点で止まる。
    - 空の範囲では `true`。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) で条件を書きます。

## 関数の詳しい説明

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

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    bool no_one_dead = true;
    for (int h : hp) {
      if (h <= 0) {
        no_one_dead = false;
        break;
      }
    }
    ```

=== "今の書き方（C++20）"

    ```cpp
    bool no_one_dead = std::ranges::none_of(hp, [](int h) { return h <= 0; });
    ```

## ゲームでの使いどころ

クリアや全滅の判定に使います。`none_of(enemies, &Enemy::alive)` が `true` なら、敵が全滅しています。エラーの有無の確認にも向いています。

空の範囲では `true` になります。敵が最初から 0 体のステージで、いきなり勝利判定になる場合があるので、`empty()` も確かめます。

条件を満たす要素が 1 つ見つかった時点で止まるので、無駄に全部を見ません。

## よくあるミス

??? failure "二重否定で読みにくくなる"
    `none_of(v, [](auto x) { return !ok(x); })` は「ダメなものが 1 つもない」で、`all_of(v, ok)` と同じです。条件を肯定形で書けるなら `all_of` のほうが読みやすいです。

??? failure "空の範囲で `true` になって、早すぎる判定になる"
    敵のリストが空のとき、`none_of` は `true` です。まだ敵を配置していない時点で、勝利判定が走ることがあります。`empty()` と組み合わせます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::any_of`](any_of.md) | 1 つでも条件を満たすか（`none_of` はその否定） |
| [`std::ranges::all_of`](all_of.md) | 全部が条件を満たすか |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 つも条件を満たさなければ `true`（`!any_of` と同じ）
    - [x] 1 つ目の `true` が見つかった時点で止まる
    - [x] 空の範囲は `true`

## 関連ページ

- [cpprefjp: std::ranges::none_of](https://cpprefjp.github.io/reference/algorithm/ranges_none_of.html)
- [cppreference: std::ranges::none_of](https://en.cppreference.com/w/cpp/algorithm/ranges/all_any_none_of)

---
title: std::ranges::max_element
summary: "範囲の中で、最大の要素の「位置（イテレータ）」を返す。"
order: 29
tags:
  - アルゴリズム
---

# std::ranges::max_element

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`max_element` は、**範囲の中で最大の要素の「位置」（イテレータ）を返す**関数です。[`min_element`](min_element.md) の反対で、「一番ヘイトの高い相手」「一番スコアの高い行動」を探すときに使います。

!!! tip "ポイント"
    - 値だけ欲しいなら [`std::ranges::max`](max.md)。見つけて何かするなら `max_element`。
    - メンバで比べるならプロジェクション: `std::ranges::max_element(party, {}, &Member::aggro)`。
    - 空の範囲だと `end()`。**同じ値が複数あれば、最初の**ものを返す。

## 関数の詳しい説明

### std::ranges::max_element {#max_element}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> max_element(R&& r, Comp comp = {}, Proj proj = {});
```

- 戻り値: 最大の要素のイテレータ。同じ値が複数なら**最初の**もの。空なら `end()`

<div class="anim" data-label="std::ranges::max_element(v)">
4 2 7 1 5 # v
*4 2 7 1 5 # 最大の候補は 4
4 2 *7 1 5 # 7 が大きいので候補が変わる
4 2 *7 1 5 # 最後まで見て、7 の位置を返す
</div>

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Member {
  std::string name;
  int aggro;
};

int main() {
  std::vector<Member> party = {{"戦士", 80}, {"魔法使い", 95}, {"僧侶", 40}};
  auto target = std::ranges::max_element(party, {}, &Member::aggro);
  std::println("敵は {} を狙う", target->name);
}
```

```text title="実行結果"
敵は 魔法使い を狙う
```


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `proj` | <span class="rank rank-must">必須</span> | `&Type::member` | メンバで比べる |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` | 大小を逆にする |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ヘイトが一番高い相手 | `max_element(party, {}, &Member::aggro)` |
| AI の最善手 | `max_element(actions, {}, &Action::score)` |
| いちばん HP が高い敵 | `max_element(enemies, {}, &Enemy::hp)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲の結果（`end()`）を `*` / `->` で読む | 未定義動作 |

## よくあるミス

??? failure "「最後の」最大を期待する"
    同じ値が複数あるとき、`max_element` は**最初**のものを返します。最後のものが欲しいときは、逆順の範囲（`std::views::reverse`）に使うか、[`minmax_element`](minmax_element.md) を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::max`](max.md) | 値のコピーを返す |
| [`std::ranges::min_element`](min_element.md) | 最小の位置を返す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大の「位置」が欲しいなら `max_element`
    - [x] メンバで比べるなら `{}, &T::member`
    - [x] 空なら `end()`。必ず確認する

## 関連ページ

- [cpprefjp: std::ranges::max_element](https://cpprefjp.github.io/reference/algorithm/ranges_max_element.html)
- [cppreference: std::ranges::max_element](https://en.cppreference.com/w/cpp/algorithm/ranges/max_element)

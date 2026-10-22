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

パーティの中でいちばんヘイトが高い相手を狙う、スコアの最も高い行動を選ぶ。最大値そのものではなく、「どの要素が最大か」を知りたい場面は多くあります。`std::ranges::max(v)` は値のコピーを返すだけで、どの要素かは分かりません。`max_element` は、最大の要素の位置（イテレーター）を返すので、見つけた要素を書き換えたり、添え字を求めたりできます。

!!! tip "ポイント"
    - 値だけ欲しいなら [`std::ranges::max`](max.md)。見つけて何かするなら `max_element`。
    - メンバで比べるならプロジェクション: `std::ranges::max_element(party, {}, &Member::aggro)`。
    - 空の範囲だと `end()`。**同じ値が複数あれば、最初の**ものを返す。

!!! info "このページを読む前に"
    [`std::ranges::max`](max.md) は最大の値を返します。位置が欲しいときは、このページの `max_element` を使います。

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

AI が行動を選ぶ場面で使います。候補の行動をスコア付きで `vector` に入れておき、`std::ranges::max_element(actions, {}, &Action::score)` で最も高いものを選びます。

ターゲットの選択では、ヘイトが最大の相手、体力が最も多い敵、最もレベルの高い仲間などを探します。

添え字が必要なら、`it - v.begin()` で求められます。空の範囲では `end()` が返るので、使う前に必ず `end()` と比べます。同じ値が複数あるときは、最初のものが返ります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲の結果（`end()`）を `*` / `->` で読む | 未定義動作 |

## よくあるミス

??? failure "空の範囲で、`end()` を逆参照する"
    空の `vector` に `max_element` を呼ぶと `end()` が返ります。そのまま `*it` で参照すると未定義動作です。`if (it != v.end())` と確かめてから使います。

??? failure "同じ値が複数あるときの結果を勘違いする"
    最大の値が複数あるとき、`max_element` は最初のものを返します。最後のものが欲しいなら、逆順の範囲で探すか、比較を工夫します。

??? failure "`max` と取り違えて値のコピーを期待する"
    `max_element` の戻り値はイテレーターで、値ではありません。値が欲しいなら `*it` ですが、値だけが欲しいときは `ranges::max` のほうが簡単です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`min_element`](min_element.md) | 最小の要素の位置 |
| [`std::ranges::max`](max.md) | 最大の値のコピー |
| [`sort`](sort.md) | 全体を並べる。最大 1 つだけなら `max_element` で十分で、速い |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大の要素の位置が欲しいなら `max_element`、値だけなら `ranges::max`。
    - [x] 空の範囲では `end()`。使う前に比べる。
    - [x] 同じ値が複数あれば、最初のもの。

## 関連ページ

- [cpprefjp: std::ranges::max_element](https://cpprefjp.github.io/reference/algorithm/ranges_max_element.html)
- [cppreference: std::ranges::max_element](https://en.cppreference.com/w/cpp/algorithm/ranges/max_element)

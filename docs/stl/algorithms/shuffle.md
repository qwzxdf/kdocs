---
title: std::ranges::shuffle
summary: "要素をランダムな順に並べ替える（カードの山のシャッフル）。"
order: 32
tags:
  - アルゴリズム
---

# std::ranges::shuffle

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

カードの山をシャッフルする、ステージの出現順をランダムにする。要素をランダムな順に並べ替えるには、`rand()` で添え字を作って `swap` する書き方では、偏りが出がちです。`std::ranges::shuffle` は、範囲の要素をランダムな順に並べ替えるアルゴリズムです。乱数エンジンを引数で渡す形で、偏りの少ない方法（Fisher-Yates 法）が使われます。

!!! tip "ポイント"
    - 乱数エンジン（`std::mt19937` など）を**引数で渡す**。毎回 `std::random_device` で作らず、1 つ作って使い回す。
    - 古い `std::random_shuffle` は C++17 で削除された。使わない。
    - 再現できる結果が欲しいとき（テスト、リプレイ）は、シードを固定したエンジンを渡す。

!!! info "このページを読む前に"
    [乱数](../utilities/random.md) の基本が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::shuffle {#shuffle}

```cpp
template <random_access_range R, class Gen>
borrowed_iterator_t<R> shuffle(R&& r, Gen&& gen);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | ランダムアクセスできる範囲 | 並べ替える範囲（vector、array、deque など） |
| `gen` | 乱数エンジン | `std::mt19937` など。**参照で渡され、状態が進む** |

- 戻り値: 範囲の終わり（ほぼ使わない）
- 計算量: O(n)
- どの並び順も同じ確率で出る

<div class="anim" data-label="std::ranges::shuffle(v, rng)">
1 2 3 4 5 # v
>3 >5 >1 >4 >2 # 乱数でランダムに並べ替える
</div>

```cpp
#include <algorithm>
#include <print>
#include <random>
#include <string>
#include <vector>

int main() {
  std::random_device seed;   // 本番では毎回違う種を使う
  std::mt19937 rng(seed());

  std::vector<std::string> quiz = {"Q1", "Q2", "Q3"};
  std::ranges::shuffle(quiz, rng);
  std::println("問題数: {}", quiz.size());
}
```

```text title="実行結果"
問題数: 3
```


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `g` | <span class="rank rank-must">必須</span> | `std::mt19937` など | 乱数エンジン（URBG） |

## ゲームでの使いどころ

カードゲームの山札のシャッフルが代表例です。`std::ranges::shuffle(deck, rng)` で、山札が混ざります。

ステージの出現順や、敵の配置の順番を毎回変えたいときにも使います。ランダムな順に並べたうえで、先頭から順に使えば、重複なしで選べます。

リプレイやテストで同じ結果が欲しいときは、乱数エンジンの種を固定します。エンジンは毎回作り直さず、1 つ作って使い回します。古い `std::random_shuffle` は C++17 で削除されたので、使いません。

## よくあるミス

??? failure "毎回 random_device からエンジンを作る"
    `std::random_device` は重い（OS に問い合わせる）ことがあります。ゲーム中にシャッフルのたびに作らず、1 つのエンジンを使い回します。

??? failure "同じシードで、毎回同じ並びになる"
    固定のシード（`std::mt19937 rng{42}`）なら、実行のたびに同じ並びです。テストには便利ですが、本番では `std::random_device{}()` などで初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sample`](sample.md) | ランダムに N 個だけ選ぶ |
| [`<random>`](../utilities/random.md) | 乱数エンジンと分布 |
| [`std::ranges::sort`](sort.md) | 決まった順に並べる |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 乱数エンジンを渡して並べ替える
    - [x] エンジンは使い回す
    - [x] `random_shuffle` は使わない

## 関連ページ

- [cpprefjp: std::ranges::shuffle](https://cpprefjp.github.io/reference/algorithm/ranges_shuffle.html)
- [cppreference: std::ranges::shuffle](https://en.cppreference.com/w/cpp/algorithm/ranges/shuffle)

---
title: std::ranges::stable_sort
tags:
  - アルゴリズム
---

# std::ranges::stable_sort

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::stable_sort` は、**同じ値どうしの元の順番を保ったまま並べ替える**関数です（安定ソート）。使い方は [`std::ranges::sort`](sort.md) とまったく同じですが、`sort` は同じ値の順番がバラバラになることがあるのに対し、`stable_sort` は「先に入っていたほうが前」のままになります。

!!! tip "結論"
    - **同点のときの順番に意味があるなら `stable_sort`。** ランキングで「同点なら先に達成した人が上」など。
    - 「先にレア度で並べ、次に種類で並べ直す」のように、**2 回並べて複数の条件を作る**ときにも使える。
    - `sort` より少し遅く、追加のメモリを使うことがある。順番が関係ないなら `sort`。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::stable_sort`](#stable_sort) | <span class="rank rank-sometimes">たまに</span> | 同じ値の順番を保って並べ替える | O(n log n)（メモリが無いと O(n log² n)） |

## よくある使い方

### 同点のときは先に達成した人を上にする

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <string>
#include <vector>

struct Record {
  std::string name;
  int score;
};

int main() {
  // 達成した順に並んでいる
  std::vector<Record> records = {
      {"Alice", 500}, {"Bob", 800}, {"Carol", 500}, {"Dave", 800}};

  std::ranges::stable_sort(records, std::greater{}, &Record::score);
  for (const auto& r : records) {
    std::println("{} {}", r.score, r.name);
  }
}
```

```text title="実行結果"
800 Bob
800 Dave
500 Alice
500 Carol
```

`sort` だと、Bob と Dave の順番（Alice と Carol の順番）が入れ替わることがあります。

## 関数の詳しい説明

### std::ranges::stable_sort {#stable_sort}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
borrowed_iterator_t<R> stable_sort(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | ランダムアクセスできる範囲 | 並べ替える範囲 | 省略不可 |
| `comp` | 比較関数 | 「a を b より前に置くなら true」 | `<`（小さい順） |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 範囲の終わり（ほぼ使わない）
- 計算量: 追加のメモリが取れれば O(n log n)、取れなければ O(n log² n)

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Item {
  std::string name;
  int type;
  int rarity;
};

int main() {
  std::vector<Item> bag = {
      {"剣A", 1, 3}, {"薬", 2, 1}, {"剣B", 1, 5}, {"盾", 3, 5}};

  // 2 回並べる: 先に「2 番目の条件（レア度の高い順）」、次に「1 番目の条件（種類順）」
  std::ranges::stable_sort(bag, std::greater{}, &Item::rarity);
  std::ranges::stable_sort(bag, {}, &Item::type);

  for (const auto& i : bag) {
    std::println("種類 {} レア {} {}", i.type, i.rarity, i.name);
  }
}
```

```text title="実行結果"
種類 1 レア 5 剣B
種類 1 レア 3 剣A
種類 2 レア 1 薬
種類 3 レア 5 盾
```

!!! note "実際は"
    UI で「列をクリックして並べ替え」をするとき、前の並び順を活かしたまま新しい列で並べたいなら stable_sort が向いています。

## フラグ・オプション

`comp` / `proj` は [`std::ranges::sort` のフラグ・オプション](sort.md#フラグオプション) と同じです。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ランキング | 同点なら先に達成した人が上 |
| 描画順 | 同じ z のスプライトは追加した順に描く（ちらつき防止） |
| インベントリ | 種類順 → 同じ種類の中ではレア度順 |

## パフォーマンス

- 追加の作業用メモリを確保することがあります。毎フレーム大量に並べるなら `sort` + 比較条件の追加（例: ID も比べる）で代用するほうが速いこともあります。

## よくあるミス

??? failure "2 回並べる順番を逆にする"
    「A で並べて、同じ A の中では B の順」にしたいなら、**先に B、後で A** で stable_sort します（後で並べたほうが優先される）。

## 理解度チェック

!!! question "Q1. 描画順を z で並べたら、同じ z のスプライトが毎フレームちらつく。なぜ？"
    <div class="spoiler" markdown>

    **答え:** `sort` は同じ値の順番を保証しないので、毎フレーム描く順が入れ替わるからです。`stable_sort` にするか、比較に ID などを加えて順番が必ず決まるようにします。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sort`](sort.md) | 同じ値の順番は保たない。少し速い |
| [`std::ranges::partial_sort`](partial_sort.md) | 先頭 N 個だけ |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ値の順番を保つなら `stable_sort`
    - [x] 複数の条件は「後の条件から」2 回並べる

## 関連ページ

- [cpprefjp: std::ranges::stable_sort](https://cpprefjp.github.io/reference/algorithm/ranges_stable_sort.html)
- [cppreference: std::ranges::stable_sort](https://en.cppreference.com/w/cpp/algorithm/ranges/stable_sort)

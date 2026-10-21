---
title: std::ranges::sample
summary: "範囲からランダムに N 個を選んで取り出す。"
order: 33
tags:
  - アルゴリズム
---

# std::ranges::sample

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::sample` は、**範囲からランダムに N 個を選んで、別の場所へ書き出す**アルゴリズムです。同じ要素が 2 回選ばれることはありません（非復元抽出）。ガチャの抽選候補、ランダムなクエストの選出などに使います。

!!! tip "ポイント"
    - 選ばれた要素の**元の順序は保たれる**（forward 範囲のとき）。順番も変えたいなら `shuffle` を組み合わせる。
    - 要素数が N 未満なら、全部が選ばれる。
    - 乱数エンジンを引数で渡す。

!!! info "このページを読む前に"
    [乱数](../utilities/random.md) の基本が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::sample {#sample}

```cpp
template <input_range R, weakly_incrementable O, class Gen>
O sample(R&& r, O out, range_difference_t<R> n, Gen&& gen);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 選ぶ元 |
| `out` | 出力イテレータ | 選んだものを書き込む先（`std::back_inserter(v)` など） |
| `n` | 整数 | 何個選ぶか（元より多ければ全部） |
| `gen` | 乱数エンジン | 乱数のもと |

- **重複なし**で選ばれる。元の順番は保たれる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <random>
#include <vector>

int main() {
  std::mt19937 rng(1);
  std::vector<int> spawn_points = {0, 1, 2, 3, 4, 5};
  std::vector<int> chosen;
  std::ranges::sample(spawn_points, std::back_inserter(chosen), 3, rng);
  std::println("{} 個選んだ", chosen.size());
}
```

```text title="実行結果"
3 個選んだ
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ランダムなクエストを 3 つ選ぶ | `sample(quests, back_inserter(picked), 3, rng)` |
| ドロップ候補から数個を選ぶ | `sample(table, out, n, rng)` |

## よくあるミス

??? failure "同じ要素が重複して選ばれると思う"
    `sample` は重複しません（非復元抽出）。重複ありで引きたいなら、`uniform_int_distribution` で添字を引くのを繰り返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::shuffle`](shuffle.md) | 全体の順序をランダムにする |
| [`std::uniform_int_distribution`](../utilities/random/uniform_int_distribution.md) | 重複ありで添字を引く |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ランダムに N 個を重複なしで選ぶ
    - [x] 選ばれた要素の順序は保たれる
    - [x] エンジンは引数で渡す

## 関連ページ

- [cpprefjp: std::ranges::sample](https://cpprefjp.github.io/reference/algorithm/ranges_sample.html)
- [cppreference: std::ranges::sample](https://en.cppreference.com/w/cpp/algorithm/ranges/sample)

---
title: std::ranges::shuffle / sample
tags:
  - アルゴリズム
  - 乱数
---

# std::ranges::shuffle / sample

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>` / `#include <random>`
</div>

`std::ranges::shuffle` は、**範囲の要素をランダムな順番に並べ替える**関数です。`std::ranges::sample` は、範囲から**ランダムに n 個を選んで**別の場所にコピーします。どちらも乱数を作る「乱数エンジン」（`std::mt19937` など）を引数に渡して使います。

!!! tip "ポイント"
    - トランプを混ぜる、出題順をランダムにする、敵の出現順をばらすなどに使う。
    - 乱数エンジンは `std::mt19937` を**1 つ作って使い回す**（毎回作り直さない）。
    - 古い `std::random_shuffle` は削除されたので使わない。

!!! info "このページを読む前に"
    乱数エンジンについては [`<random>`](../utilities/random.md) を見てください。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::shuffle`](#shuffle) | <span class="rank rank-sometimes">たまに</span> | 全体をランダムに並べ替える | O(n) |
| [`std::ranges::sample`](#sample) | <span class="rank rank-rare">知ってるだけ</span> | ランダムに n 個選んでコピー | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <random>
#include <vector>

int main() {
  std::mt19937 rng(12345);  // 種を固定すると毎回同じ結果になる（デバッグ用）

  std::vector<int> deck = {1, 2, 3, 4, 5, 6, 7, 8};
  std::ranges::shuffle(deck, rng);

  // 結果は実装によって違うが、要素の数と中身は変わらない
  std::ranges::sort(deck);
  std::println("並べ直すと {}", deck);
}
```

```text title="実行結果"
並べ直すと [1, 2, 3, 4, 5, 6, 7, 8]
```

混ぜた直後の並び順は、同じ種でも**コンパイラ（標準ライブラリ）によって違う**ことがあります。

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

## フラグ・オプション

`gen` に渡す乱数エンジンは [`<random>`](../utilities/random.md) を参照してください。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::random_shuffle(v.begin(), v.end());  // C++17 で削除された
    ```

=== "今の書き方（C++20）"

    ```cpp
    std::mt19937 rng(std::random_device{}());
    std::ranges::shuffle(v, rng);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| カードゲーム | 山札を混ぜる |
| ランダムな順番 | クイズの出題順、BGM のシャッフル再生 |
| 出現位置 | 出現ポイントからランダムに 3 か所 |
| テトリス系 | 7 種類を袋に入れて混ぜ、順に出す（7-bag） |

## よくあるミス

??? failure "毎回エンジンを作り直す"
    ```cpp
    void Shuffle(std::vector<int>& v) {
      std::mt19937 rng(0);  // 毎回同じ種 → 毎回同じ並び
      std::ranges::shuffle(v, rng);
    }
    ```

    エンジンはゲーム全体で 1 つ（またはシステムごとに 1 つ）作って、参照で渡します。

??? failure "リプレイで再現できない"
    `std::random_device` で種を作ると毎回違う結果になります。リプレイや同期が必要なら、種を保存しておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<random>`](../utilities/random.md) の分布 | 1 個だけランダムに選ぶなら `uniform_int_distribution` で添字を作る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ranges::shuffle(v, rng)` で混ぜる
    - [x] `rng` は 1 つ作って使い回す
    - [x] 同じ種でもコンパイラが違うと結果が違うことがある

## 関連ページ

- [cpprefjp: std::ranges::shuffle](https://cpprefjp.github.io/reference/algorithm/ranges_shuffle.html)
- [cppreference: std::ranges::shuffle](https://en.cppreference.com/w/cpp/algorithm/ranges/shuffle)

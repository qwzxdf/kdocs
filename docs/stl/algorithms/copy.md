---
title: std::ranges::copy
summary: "範囲の要素を、別の場所にコピーする（条件つき・個数指定もある）。"
order: 40
tags:
  - アルゴリズム
---

# std::ranges::copy

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::copy` は、**範囲の要素を別の場所へコピーする**アルゴリズムです。条件に合うものだけをコピーする `copy_if`、先頭から n 個だけコピーする `copy_n` も、同じ仲間です。ループで 1 つずつ書く代わりに使います。

!!! tip "ポイント"
    - コピー先には**十分な大きさ**が要る。足りないなら `std::back_inserter(dst)` を渡して、末尾に足していく。
    - 条件に合うものだけ取り出すなら `copy_if`。取り出した結果を `vector` にしたいだけなら、[`views::filter`](views/filter.md) と [`ranges::to`](ranges_to.md) のほうが短い。
    - コピー元とコピー先が**重なっている**とき、後ろへずらすなら [`copy_backward`](copy_backward.md)。
    - 要素をコピーせず「移す」なら [`move`](move.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::copy {#copy}

```cpp
template <input_range R, weakly_incrementable O>
constexpr copy_result<borrowed_iterator_t<R>, O> copy(R&& r, O result);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | コピー元 |
| `result` | 出力イテレータ | 書き込み先の先頭。**足りる大きさがあるか、`std::back_inserter` にする** |

- 戻り値: `.in`（読み終わった位置）と `.out`（書き終わった次の位置）を持つ構造体

<div class="anim" data-label="std::ranges::copy(src, dst.begin())">
1 2 3 | _ _ _ # src と dst
1 2 3 | +1 _ _ # 1 つずつコピーする
1 2 3 | +1 +2 +3 # 全部コピーされる
</div>

```cpp
#include <algorithm>
#include <array>
#include <print>
#include <vector>

int main() {
  std::array<int, 3> src = {1, 2, 3};
  std::vector<int> dst(5, 0);
  std::ranges::copy(src, dst.begin() + 1);  // 添字 1 から上書き
  std::println("{}", dst);
}
```

```text title="実行結果"
[0, 1, 2, 3, 0]
```

### std::ranges::copy_if {#copy_if}

```cpp
template <input_range R, weakly_incrementable O, class Proj = identity, class Pred>
constexpr copy_if_result<borrowed_iterator_t<R>, O> copy_if(R&& r, O result, Pred pred, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | コピー元 |
| `result` | 出力イテレータ | 書き込み先 |
| `pred` | 関数 | **コピーするなら `true`** |
| `proj` | プロジェクション | `pred` に渡す前の変換 |

<div class="anim" data-label="std::ranges::copy_if(src, out, is_even)">
1 2 3 4 5 6 | _ _ _ # src と dst
1 *2 3 *4 5 *6 | _ _ _ # 条件に合うものだけ
1 2 3 4 5 6 | +2 +4 +6 # 順番を保ったまま詰めてコピーされる
</div>

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

struct Enemy {
  int id;
  bool visible;
};

int main() {
  std::vector<Enemy> enemies = {{1, true}, {2, false}, {3, true}};
  std::vector<Enemy> to_draw;
  std::ranges::copy_if(enemies, std::back_inserter(to_draw), &Enemy::visible);
  std::println("描画するのは {} 体", to_draw.size());
}
```

```text title="実行結果"
描画するのは 2 体
```

### std::ranges::copy_n {#copy_n}

```cpp
template <input_iterator I, weakly_incrementable O>
constexpr copy_n_result<I, O> copy_n(I first, std::iter_difference_t<I> n, O result);
```

- `first` から `n` 個を `result` にコピーします


### copy_n の使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {1, 2, 3, 4, 5};
  std::vector<int> dst(3);

  // 先頭から 3 個だけコピーする
  std::ranges::copy_n(src.begin(), 3, dst.begin());
  std::println("{} {} {}", dst[0], dst[1], dst[2]);
}
```

```text title="実行結果"
1 2 3
```

## フラグ・オプション

| 関数 | 重要度 | 意味 |
| --- | --- | --- |
| `copy` | <span class="rank rank-sometimes">たまに</span> | 全部コピーする |
| `copy_if` | <span class="rank rank-sometimes">たまに</span> | 条件に合うものだけコピーする |
| `copy_n` | <span class="rank rank-rare">知ってるだけ</span> | 先頭から n 個だけコピーする |
| `copy_backward` | <span class="rank rank-rare">知ってるだけ</span> | 後ろから順にコピーする（[別のページ](copy_backward.md)） |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列から別の配列へ受け渡す | `copy(src, dst.begin())` |
| 条件に合う敵だけ別の vector に集める | `copy_if(enemies, back_inserter(alive), 生きている)` |
| バッファの先頭 n 個だけ送る | `copy_n(buf.begin(), n, out)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| コピー先の大きさが足りない | 範囲外への書き込み（未定義動作） |
| コピー元とコピー先が重なっている（`copy`） | 未定義動作。重なっていて後ろへずらすなら `copy_backward` |

## よくあるミス

??? failure "空の vector にコピーする"
    ```cpp
    std::vector<int> dst;
    std::ranges::copy(src, dst.begin());           // NG: dst は空なので範囲外に書き込む
    std::ranges::copy(src, std::back_inserter(dst)); // OK: 末尾に足していく
    ```

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::move`](move.md) | コピーせずに移す |
| [`std::ranges::copy_backward`](copy_backward.md) | 重なった範囲を後ろへずらす |
| `std::vector` のコピーコンストラクタ・`assign` | コンテナ全体を丸ごとコピーするなら、こちらが簡単 |
| [`std::ranges::to`](ranges_to.md) | 範囲から新しいコンテナを作る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲を別の場所へコピーする
    - [x] コピー先は十分な大きさに、または `back_inserter`
    - [x] 条件つきは `copy_if`

## 関連ページ

- [cpprefjp: std::ranges::copy](https://cpprefjp.github.io/reference/algorithm/ranges_copy.html)
- [cppreference: std::ranges::copy](https://en.cppreference.com/w/cpp/algorithm/ranges/copy)

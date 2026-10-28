---
title: <iterator>（next / distance / back_inserter など）
summary: "イテレータを進める・距離を測る・挿入するなどの道具（`next`、`distance`、`back_inserter`）。"
order: 82
tags:
  - 型・言語サポート
---

# &lt;iterator&gt;（next / distance / back_inserter など）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <iterator>`
</div>

`<iterator>` は、**イテレータを動かしたり、2 つのイテレータの距離を測ったり、アルゴリズムの書き込み先を作ったりする道具**をまとめたヘッダです。`std::next` や `std::distance` は、vector だけでなく list や map のイテレータにも使えます。`std::back_inserter` は、空の vector にアルゴリズムの結果を書き込むときの定番です。

!!! tip "ポイント"
    - n 個先・前は `std::next(it, n)` / `std::prev(it, n)`（どのコンテナでも使える）。
    - 2 つの位置の距離は `std::distance(a, b)`（vector なら `b - a` でもいい）。
    - 空の vector に書き込むなら `std::back_inserter(v)`。
    - 配列の大きさは `std::size(a)`、符号付きなら `std::ssize(a)`。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) を先に読んでください。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::back_inserter`](iterator/back_inserter.md) | <span class="rank rank-often">よく使う</span> | `push_back` で追加しながら書き込むイテレータ |
| [`std::next`](iterator/next.md) | <span class="rank rank-often">よく使う</span> | n 個先のイテレータを返す |
| [`std::prev`](iterator/prev.md) | <span class="rank rank-often">よく使う</span> | n 個前のイテレータを返す |
| [`std::size`](iterator/size.md) | <span class="rank rank-often">よく使う</span> | 配列・コンテナの要素数 <span class="ver ver-17">C++17</span> |
| [`std::ssize`](iterator/ssize.md) | <span class="rank rank-often">よく使う</span> | 要素数（符号付き） <span class="ver ver-20">C++20</span> |
| [`std::distance`](iterator/distance.md) | <span class="rank rank-sometimes">たまに</span> | 2 つのイテレータの距離 |
| [`std::advance`](iterator/advance.md) | <span class="rank rank-sometimes">たまに</span> | イテレータそのものを n 個進める |
| [`std::inserter`](iterator/inserter.md) | <span class="rank rank-sometimes">たまに</span> | `insert` で追加しながら書き込む（set / map 用） |
| [`std::begin`](iterator/begin.md) | <span class="rank rank-sometimes">たまに</span> | 配列でもコンテナでも先頭を返す |
| [`std::end`](iterator/begin.md) | <span class="rank rank-sometimes">たまに</span> | 配列でもコンテナでも終わりを返す |
| [`std::data`](iterator/data.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭のポインタ |
| [`std::empty`](iterator/empty.md) | <span class="rank rank-rare">知ってるだけ</span> | 空か |
| [`std::front_inserter`](iterator/front_inserter.md) | <span class="rank rank-rare">知ってるだけ</span> | `push_front` で追加しながら書き込む |
| [`std::make_move_iterator`](iterator/move_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 読むたびにムーブするイテレータ |
| [`std::reverse_iterator`](iterator/reverse_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 逆向きに進むイテレータ |
| [`std::istream_iterator`](iterator/istream_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームから値を読むイテレータ |
| [`std::iterator_traits`](iterator/iterator_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータの性質（要素の型、種類など）を取り出す。 |
| [`std::input_iterator_tag`](iterator/input_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力イテレータ（1 回だけ読み進められる）を表すタグの型。 |
| [`std::output_iterator_tag`](iterator/output_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力イテレータ（書き込みながら進められる）を表すタグの型。 |
| [`std::forward_iterator_tag`](iterator/forward_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 前方イテレータ（何度でも読み返せる（一方向））を表すタグの型。 |
| [`std::bidirectional_iterator_tag`](iterator/bidirectional_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 双方向イテレータ（前後どちらにも進める）を表すタグの型。 |
| [`std::random_access_iterator_tag`](iterator/random_access_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | ランダムアクセスイテレータ（添字で好きな位置へ飛べる）を表すタグの型。 |
| [`std::contiguous_iterator_tag`](iterator/contiguous_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 連続イテレータ（メモリ上で連続した要素を指す）を表すタグの型。 <span class="ver ver-20">C++20</span> |
| [`std::crbegin`](iterator/crbegin.md) | <span class="rank rank-rare">知ってるだけ</span> | const の逆順イテレータで、末尾の要素を指す。 <span class="ver ver-14">C++14</span> |
| [`std::crend`](iterator/crend.md) | <span class="rank rank-rare">知ってるだけ</span> | const の逆順イテレータで、先頭の手前を指す。 <span class="ver ver-14">C++14</span> |
| [`std::make_reverse_iterator`](iterator/make_reverse_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータから reverse_iterator を作る。 |
| [`std::move_sentinel`](iterator/move_sentinel.md) | <span class="rank rank-rare">知ってるだけ</span> | move_iterator と組み合わせる、ムーブ用の終端。 <span class="ver ver-20">C++20</span> |
| [`std::back_insert_iterator`](iterator/back_insert_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、コンテナの末尾へ push_back するイテレータ。 |
| [`std::front_insert_iterator`](iterator/front_insert_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、コンテナの先頭へ push_front するイテレータ。 |
| [`std::insert_iterator`](iterator/insert_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、コンテナの指定位置へ insert するイテレータ。 |
| [`std::istreambuf_iterator`](iterator/istreambuf_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームバッファから、1 文字ずつ生で読むイテレータ。 |
| [`std::ostreambuf_iterator`](iterator/ostreambuf_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームバッファへ 1 文字ずつ生で書くイテレータ。 |
| [`std::counted_iterator`](iterator/counted_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 残りの個数を数えながら進むイテレータ。 <span class="ver ver-20">C++20</span> |
| [`std::default_sentinel`](iterator/default_sentinel.md) | <span class="rank rank-rare">知ってるだけ</span> | counted_iterator などの終端を表す目印の定数。 <span class="ver ver-20">C++20</span> |
| [`std::unreachable_sentinel`](iterator/unreachable_sentinel.md) | <span class="rank rank-rare">知ってるだけ</span> | 「終わりには絶対に届かない」と約束する終端。 <span class="ver ver-20">C++20</span> |
| [`std::common_iterator`](iterator/common_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータと sentinel（終端）を 1 つの型にまとめる。 <span class="ver ver-20">C++20</span> |
| [`std::basic_const_iterator`](iterator/basic_const_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を const として見せるイテレータのアダプタ。 <span class="ver ver-23">C++23</span> |
| [`std::make_const_iterator`](iterator/make_const_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータを要素が const として見えるイテレータに変換する。 <span class="ver ver-23">C++23</span> |
| [`std::projected`](iterator/projected.md) | <span class="rank rank-rare">知ってるだけ</span> | プロジェクション（変換）を通した値をアルゴリズムに見せるための型。 <span class="ver ver-20">C++20</span> |
| [`std::iter_value_t`](iterator/iter_value_t.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータが指す値の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
| [`std::iter_reference_t`](iterator/iter_reference_t.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータの `*it` の型（参照）を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
| [`std::iter_difference_t`](iterator/iter_difference_t.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータの差の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
| [`std::iter_move`](iterator/iter_move.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータが指す要素を右辺値として取り出す。 <span class="ver ver-20">C++20</span> |
| [`std::cbegin`](iterator/cbegin.md) | <span class="rank rank-sometimes">たまに</span> | コンテナや配列の先頭を指す、const のイテレータを返す。 <span class="ver ver-14">C++14</span> |
| [`std::cend`](iterator/cend.md) | <span class="rank rank-rare">知ってるだけ</span> | コンテナや配列の終端を指す、const のイテレータを返す。 <span class="ver ver-14">C++14</span> |
| [`std::rbegin`](iterator/rbegin.md) | <span class="rank rank-sometimes">たまに</span> | コンテナや配列の逆順の先頭（最後の要素）を指すイテレータを返す。 <span class="ver ver-14">C++14</span> |
| [`std::rend`](iterator/rend.md) | <span class="rank rank-rare">知ってるだけ</span> | コンテナや配列の逆順の終端（先頭の手前）を指すイテレータを返す。 <span class="ver ver-14">C++14</span> |

## よくある使い方

```cpp
#include <algorithm>
#include <iterator>
#include <list>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {40, 90, 75, 60};

  std::vector<int> high;
  std::ranges::copy_if(scores, std::back_inserter(high), [](int s) { return s >= 70; });

  std::list<int> queue = {1, 2, 3, 4};
  auto third = std::next(queue.begin(), 2);  // list でも使える（it + 2 は書けない）

  int raw[] = {5, 6, 7};
  std::println("{} / {} / {}", high, *third, std::size(raw));
}
```

```text title="実行結果"
[90, 75] / 3 / 3
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| 条件に合うものを別の vector に集める | `back_inserter` |
| map の n 番目 | `std::next(m.begin(), n)` |
| 見つかった位置の添字 | `std::distance(v.begin(), it)` |
| C の配列の要素数 | `std::size` |

## よくあるミス

??? failure "空の vector の begin() に書き込む"
    `std::ranges::copy(src, dst.begin())` は dst が空だと範囲外です。`std::back_inserter(dst)` を使います。

??? failure "std::next で範囲外まで進む"
    `std::next(it, 5)` は、end を越えるかどうかを確かめません。越えると未定義動作です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] n 個先は std::next、距離は std::distance
    - [x] 空の vector への出力は back_inserter
    - [x] 配列の大きさは std::size / std::ssize

## 関連ページ

- [イテレータ](../../basics/iterator.md)
- [cppreference: Iterator library](https://en.cppreference.com/w/cpp/iterator)

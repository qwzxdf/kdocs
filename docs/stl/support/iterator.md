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

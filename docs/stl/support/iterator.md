---
title: <iterator>（next / distance / back_inserter など）
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
| [`std::back_inserter`](#back_inserter) | <span class="rank rank-often">よく使う</span> | `push_back` で追加しながら書き込むイテレータ |
| [`std::next`](#next) | <span class="rank rank-often">よく使う</span> | n 個先のイテレータを返す |
| [`std::prev`](#prev) | <span class="rank rank-often">よく使う</span> | n 個前のイテレータを返す |
| [`std::size`](#size) | <span class="rank rank-often">よく使う</span> | 配列・コンテナの要素数 <span class="ver ver-17">C++17</span> |
| [`std::ssize`](#ssize) | <span class="rank rank-often">よく使う</span> | 要素数（符号付き） <span class="ver ver-20">C++20</span> |
| [`std::distance`](#distance) | <span class="rank rank-sometimes">たまに</span> | 2 つのイテレータの距離 |
| [`std::advance`](#advance) | <span class="rank rank-sometimes">たまに</span> | イテレータそのものを n 個進める |
| [`std::inserter`](#inserter) | <span class="rank rank-sometimes">たまに</span> | `insert` で追加しながら書き込む（set / map 用） |
| [`std::begin`](#begin) | <span class="rank rank-sometimes">たまに</span> | 配列でもコンテナでも先頭を返す |
| [`std::end`](#end) | <span class="rank rank-sometimes">たまに</span> | 配列でもコンテナでも終わりを返す |
| [`std::data`](#data) | <span class="rank rank-rare">知ってるだけ</span> | 先頭のポインタ |
| [`std::empty`](#empty) | <span class="rank rank-rare">知ってるだけ</span> | 空か |
| [`std::front_inserter`](#front_inserter) | <span class="rank rank-rare">知ってるだけ</span> | `push_front` で追加しながら書き込む |
| [`std::make_move_iterator`](#make_move_iterator) | <span class="rank rank-rare">知ってるだけ</span> | 読むたびにムーブするイテレータ |
| [`std::reverse_iterator`](#reverse_iterator) | <span class="rank rank-rare">知ってるだけ</span> | 逆向きに進むイテレータ |
| [`std::istream_iterator`](#istream_iterator) | <span class="rank rank-rare">知ってるだけ</span> | ストリームから値を読むイテレータ |

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

## 関数の詳しい説明

### std::back_inserter {#back_inserter}

```cpp
template <class Container>
std::back_insert_iterator<Container> back_inserter(Container& c);
```

- このイテレータに書き込む（`*it = x`）と、`c.push_back(x)` が呼ばれます。アルゴリズムの出力先に使います

<div class="anim" data-label="std::back_inserter(v)">
1 2 # v
1 2 +3 # 代入するたびに push_back される
1 2 3 +4 # 出力先の大きさを気にしなくてよい
</div>

### std::next {#next}

```cpp
template <class InputIt>
InputIt next(InputIt it, std::iter_difference_t<InputIt> n = 1);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | イテレータ | 元の位置（変わらない） |
| `n` | 整数 | 何個先か（省略すると 1） |

- n 個先のイテレータを**新しく返します**。list など `+ n` できないイテレータにも使えます（その場合 O(n)）

<div class="anim" data-label="std::next(it, 2)">
*a b c d # it は a を指す
a b *c d # 2 つ先を返す。it 自体は動かない
</div>

### std::prev {#prev}

```cpp
template <class BidirIt>
BidirIt prev(BidirIt it, std::iter_difference_t<BidirIt> n = 1);
```

- n 個前のイテレータを返します。`std::prev(v.end())` で最後の要素

<div class="anim" data-label="std::prev(it, 2)">
a b c *d # it は d を指す
a *b c d # 2 つ前を返す。it 自体は動かない
</div>

### std::size {#size}

<span class="ver ver-17">C++17</span>

```cpp
template <class C>
constexpr auto size(const C& c) -> decltype(c.size());
template <class T, std::size_t N>
constexpr std::size_t size(const T (&array)[N]) noexcept;
```

- C の配列でもコンテナでも要素数を返します。`sizeof(a) / sizeof(a[0])` の代わり

### std::ssize {#ssize}

<span class="ver ver-20">C++20</span>

```cpp
template <class C>
constexpr auto ssize(const C& c);  // 符号付き
```

- 符号付き（`std::ptrdiff_t`）の要素数。`int` と比べたり、後ろから回したりするときに警告が出ません

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  for (auto i = std::ssize(v) - 1; i >= 0; --i) {  // 符号付きなので -1 で止まる
    std::print("{} ", v[i]);
  }
  std::println("/ 最後 {}", *std::prev(v.end()));
}
```

```text title="実行結果"
3 2 1 / 最後 3
```

### std::distance {#distance}

```cpp
template <class InputIt>
std::iter_difference_t<InputIt> distance(InputIt first, InputIt last);
```

- `first` から `last` まで何個あるか。vector なら O(1)、list なら O(n)。見つかった位置の添字を出すのにも使えます

<div class="anim" data-label="std::distance(first, last)">
*a b c *d # first は a、last は d
*a *b *c d # 間の個数（3）を数える
</div>

### std::advance {#advance}

```cpp
template <class InputIt, class Distance>
void advance(InputIt& it, Distance n);
```

- `it` **そのもの**を n 個進めます（戻り値なし）。新しいイテレータが欲しいなら `std::next`

<div class="anim" data-label="std::advance(it, 2)">
*a b c d # it は a を指す
a b *c d # 2 つ進む（it が書き換わる）
</div>

```cpp
#include <algorithm>
#include <iterator>
#include <map>
#include <print>

int main() {
  std::map<int, char> m = {{10, 'a'}, {20, 'b'}, {30, 'c'}};
  auto it = m.begin();
  std::advance(it, 2);  // it 自体が動く
  std::println("{} / 距離 {}", it->first, std::distance(m.begin(), it));
}
```

```text title="実行結果"
30 / 距離 2
```

### std::inserter {#inserter}

```cpp
template <class Container>
std::insert_iterator<Container> inserter(Container& c, typename Container::iterator pos);
```

- 書き込むと `c.insert(pos, x)` が呼ばれます。set や map に結果を入れるのに使います

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <set>
#include <vector>

int main() {
  std::vector<int> drops = {3, 1, 3, 2};
  std::set<int> kinds;
  std::ranges::copy(drops, std::inserter(kinds, kinds.end()));
  std::println("{}", kinds);
}
```

```text title="実行結果"
{1, 2, 3}
```

### std::begin {#begin}

```cpp
template <class C>
constexpr auto begin(C& c) -> decltype(c.begin());
template <class T, std::size_t N>
constexpr T* begin(T (&array)[N]) noexcept;
```

- C の配列でもコンテナでも先頭を返します。テンプレートで「何でも受け取る」関数を書くときに使います

### std::end {#end}

```cpp
template <class C>
constexpr auto end(C& c) -> decltype(c.end());
```

- 同じく終わりを返します

### std::data {#data}

```cpp
template <class C>
constexpr auto data(C& c) -> decltype(c.data());
```

- 先頭のポインタ。C の配列にも使えます

### std::empty {#empty}

```cpp
template <class C>
constexpr auto empty(const C& c) -> decltype(c.empty());
```

- 空か。C の配列は常に false

```cpp
#include <iterator>
#include <print>

int main() {
  int a[] = {4, 5, 6};
  int sum = 0;
  for (auto it = std::begin(a); it != std::end(a); ++it) {
    sum += *it;
  }
  std::println("{} {} {}", sum, *std::data(a), std::empty(a));
}
```

```text title="実行結果"
15 4 false
```

### std::front_inserter {#front_inserter}

```cpp
template <class Container>
std::front_insert_iterator<Container> front_inserter(Container& c);
```

- 書き込むと `c.push_front(x)` が呼ばれます（deque、list 用）。逆順に入ります

### std::make_move_iterator {#make_move_iterator}

```cpp
template <class Iter>
std::move_iterator<Iter> make_move_iterator(Iter i);
```

- 読むたびに要素を**ムーブ**するイテレータ。別の vector へ中身をムーブで移すときに使います

```cpp
#include <algorithm>
#include <deque>
#include <iterator>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> from = {"sword", "shield"};
  std::vector<std::string> to(std::make_move_iterator(from.begin()),
                              std::make_move_iterator(from.end()));
  std::deque<int> d;
  std::ranges::copy(std::vector<int>{1, 2, 3}, std::front_inserter(d));
  std::println("{} / {}", to, d);
}
```

```text title="実行結果"
["sword", "shield"] / [3, 2, 1]
```

### std::reverse_iterator {#reverse_iterator}

```cpp
template <class Iter>
class reverse_iterator;
```

- `++` すると前に進むイテレータ。`rbegin()` / `rend()` が返すのはこれです。`.base()` で普通のイテレータに戻せます

### std::istream_iterator {#istream_iterator}

```cpp
template <class T>
class istream_iterator;
```

- ストリームから `>>` で値を読むイテレータ。ファイルの数値を全部 vector に読むのに使えます

```cpp
#include <iterator>
#include <print>
#include <sstream>
#include <vector>

int main() {
  std::istringstream in("10 20 30");
  std::vector<int> values(std::istream_iterator<int>(in), std::istream_iterator<int>{});
  std::vector<int> v = {1, 2, 3};
  auto r = v.rbegin();
  std::println("{} / {} {}", values, *r, *std::prev(r.base()));
}
```

```text title="実行結果"
[10, 20, 30] / 3 3
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

## 理解度チェック

!!! question "Q1. `std::advance(it, 2)` と `auto it2 = std::next(it, 2)` の違いは？"
    <div class="spoiler" markdown>

    **答え:** advance は `it` 自体を動かし、何も返しません。next は `it` を変えずに、2 つ先の新しいイテレータを返します。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] n 個先は std::next、距離は std::distance
    - [x] 空の vector への出力は back_inserter
    - [x] 配列の大きさは std::size / std::ssize

## 関連ページ

- [イテレータ](../../basics/iterator.md)
- [cppreference: Iterator library](https://en.cppreference.com/w/cpp/iterator)

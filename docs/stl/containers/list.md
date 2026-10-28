---
title: std::list
summary: "連結リスト。途中の挿入・削除は速いが全体が遅く、ほとんど使わない。"
order: 16
tags:
  - コンテナ
---

# std::list

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-1">× 重い</span>
<span class="ver ver-11">C++98〜</span>
`#include <list>`
</div>

`std::list` は、<strong>要素どうしを前後のポインタでつないだ「双方向連結リスト」</strong>です。要素はメモリ上のバラバラな場所に置かれ、それぞれが「前の要素」と「次の要素」の場所を覚えています。途中の要素を消したり、途中に入れたりするのが O(1) でできるのが特徴です。

!!! tip "ポイント"
    - <strong>ほぼ使わない。</strong> 教科書では「途中の挿入・削除が速い」と習うが、実際のゲームでは**ほとんどの場合 vector のほうが速い**。
    - 理由: 要素がメモリ上でバラバラなので、回すたびにキャッシュミスが起きる。
    - 使っていいのは「要素のアドレスが絶対に動いてほしくない」「`splice` で別のリストへ付け替えたい」ときくらい。

!!! info "このページを読む前に"
    [キャッシュ効率](../../basics/cache.md) を読むと、なぜ list が遅いのかが分かります。

<div class="mem">
<div class="mem-step"><span class="mem-label">vector</span><span class="mem-cells"><span>A</span><span>B</span><span>C</span><span>D</span></span><span class="mem-note">隣り合って並ぶ。まとめて読める</span></div>
<div class="mem-step"><span class="mem-label">list</span><span class="mem-cells"><span>A</span><span class="free">　</span><span class="free">　</span><span>C</span><span class="free">　</span><span>B</span><span class="free">　</span><span class="free">　</span><span>D</span></span><span class="mem-note">バラバラに置かれ、ポインタでつながる。1 個ずつ飛び回って読む</span></div>
</div>

## 宣言

```cpp
template <class T, class Allocator = std::allocator<T>>
class list;
```

## 関数一覧

vector と同じ名前の関数は同じ意味です。

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`push_back`](#push_back) | <span class="rank rank-often">よく使う</span> | 末尾に追加（毎回メモリ確保） | O(1) |
| [`push_front`](#push_front) | <span class="rank rank-often">よく使う</span> | 先頭に追加 | O(1) |
| [`pop_back`](#pop_back) | <span class="rank rank-often">よく使う</span> | 末尾を削除 | O(1) |
| [`pop_front`](#pop_front) | <span class="rank rank-often">よく使う</span> | 先頭を削除 | O(1) |
| [`front`](#front) | <span class="rank rank-often">よく使う</span> | 先頭の要素 | O(1) |
| [`back`](#back) | <span class="rank rank-often">よく使う</span> | 末尾の要素 | O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`begin`](#begin) | <span class="rank rank-often">よく使う</span> | 先頭のイテレータ | O(1) |
| [`end`](#end) | <span class="rank rank-often">よく使う</span> | 最後の次のイテレータ | O(1) |
| [`erase`](#erase) | <span class="rank rank-sometimes">たまに</span> | 位置を指定して削除 | O(1) |
| [`insert`](#insert) | <span class="rank rank-sometimes">たまに</span> | 位置を指定して挿入 | O(1) |
| [`remove_if`](#remove_if) | <span class="rank rank-sometimes">たまに</span> | 条件で削除（メンバ関数） | O(n) |
| [`remove`](#remove) | <span class="rank rank-sometimes">たまに</span> | 値で削除（メンバ関数） | O(n) |
| [`splice`](#splice) | <span class="rank rank-sometimes">たまに</span> | 別のリストから要素を付け替える | O(1) |
| [`sort`](#sort) | <span class="rank rank-sometimes">たまに</span> | 並べ替え（`std::sort` は使えない） | O(n log n) |
| [`clear`](#clear) | <span class="rank rank-sometimes">たまに</span> | 全削除 | O(n) |
| [`emplace_back`](#emplace_back) | <span class="rank rank-rare">知ってるだけ</span> | 末尾にその場で構築 | O(1) |
| [`emplace_front`](#emplace_front) | <span class="rank rank-rare">知ってるだけ</span> | 先頭にその場で構築 | O(1) |
| [`unique`](#unique) | <span class="rank rank-rare">知ってるだけ</span> | 連続する重複を消す | O(n) |
| [`reverse`](#reverse) | <span class="rank rank-rare">知ってるだけ</span> | 逆順にする | O(n) |
| [`merge`](#merge) | <span class="rank rank-rare">知ってるだけ</span> | ソート済みリストを合流 | O(n + m) |

`operator[]` は**ありません**。n 番目に行くには先頭から n 回たどる必要があります。

## よくある使い方

```cpp
#include <list>
#include <print>

int main() {
  std::list<int> l = {1, 2, 3, 4, 5};

  // 偶数を消す
  l.remove_if([](int x) { return x % 2 == 0; });

  l.push_front(0);
  std::println("{}", l);
}
```

```text title="実行結果"
[0, 1, 3, 5]
```

## 関数の詳しい説明

### push_back {#push_back}

```cpp
void push_back(const T& value);
void push_back(T&& value);
```

- 末尾に追加します。**毎回ノード 1 個ぶんのメモリ確保**が起きます

<div class="anim" data-label="l.push_back(40)">
10 20 30 # l
10 20 30 +40 # 新しいノードを後ろにつなぐ
</div>

### push_front {#push_front}

```cpp
void push_front(const T& value);
void push_front(T&& value);
```

- 先頭に追加します

<div class="anim" data-label="l.push_front(5)">
10 20 30 # l
+5 10 20 30 # 新しいノードを前につなぐ
</div>

### pop_back {#pop_back}

```cpp
void pop_back();
```

- 末尾を消します。空のとき未定義動作

<div class="anim" data-label="l.pop_back()">
10 20 30 40 # l
10 20 30 x40 # 後ろのノードを消す
10 20 30 # 完了
</div>

### pop_front {#pop_front}

```cpp
void pop_front();
```

- 先頭を消します。空のとき未定義動作

<div class="anim" data-label="l.pop_front()">
10 20 30 40 # l
x10 20 30 40 # 前のノードを消す
20 30 40 # 完了
</div>

### front {#front}

```cpp
reference front();
```

- 先頭の要素。空のとき未定義動作

### back {#back}

```cpp
reference back();
```

- 末尾の要素。空のとき未定義動作

```cpp
#include <list>
#include <print>

int main() {
  std::list<int> l;
  l.push_back(2);
  l.push_front(1);
  l.push_back(3);
  std::println("{} / 先頭 {} / 末尾 {}", l, l.front(), l.back());
  l.pop_front();
  l.pop_back();
  std::println("{}", l);
}
```

```text title="実行結果"
[1, 2, 3] / 先頭 1 / 末尾 3
[2]
```

### size {#size}

```cpp
size_type size() const noexcept;
```

- 要素数。C++11 から O(1) です

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 空なら `true`

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 先頭のイテレータ。`++` と `--` はできますが、`+ 3` のように飛ぶことはできません

### end {#end}

```cpp
iterator end() noexcept;
```

- 最後の次のイテレータ

```cpp
#include <iterator>
#include <list>
#include <print>

int main() {
  std::list<int> l = {10, 20, 30};
  auto it = l.begin();
  std::advance(it, 2);  // 2 回たどる（it + 2 とは書けない）
  std::println("{} / size {}", *it, l.size());
}
```

```text title="実行結果"
30 / size 3
```

### erase {#erase}

```cpp
iterator erase(const_iterator pos);
iterator erase(const_iterator first, const_iterator last);
```

- 指定した位置を消して、次の要素のイテレータを返します。O(1)
- **消した要素以外のイテレータ・参照は壊れません**（list の数少ない強み）

<div class="anim" data-label="l.erase(it)">
10 20 30 40 # it は 20 を指している
10 x20 30 40 # ノードを外して破棄
10 30 40 # ほかは動かない
</div>

### insert {#insert}

```cpp
iterator insert(const_iterator pos, const T& value);
```

- `pos` の前に挿入します。O(1)。他の要素は動きません

<div class="anim" data-label="l.insert(it, 99)">
10 20 30 40 # it は 20 を指している
10 +99 20 30 40 # つなぎ替えるだけ。ほかは動かない
</div>

```cpp
#include <list>
#include <print>

int main() {
  std::list<int> l = {1, 2, 4};
  auto it = std::next(l.begin(), 2);  // 4 を指す
  l.insert(it, 3);
  l.erase(l.begin());
  std::println("{} / it はまだ 4: {}", l, *it);
}
```

```text title="実行結果"
[2, 3, 4] / it はまだ 4: 4
```

### remove_if {#remove_if}

```cpp
template <class Pred>
size_type remove_if(Pred pred);
```

- 条件に合う要素を全部消します。戻り値は消した数（C++20〜）
- `std::erase_if(l, pred)` でも同じです

<div class="anim" data-label="l.remove_if(is_odd)">
1 2 3 4 5 # l
x1 2 x3 4 x5 # 条件に合うノードを消す
2 4 # 完了
</div>

### remove {#remove}

```cpp
size_type remove(const T& value);
```

- `value` と等しい要素を全部消します

<div class="anim" data-label="l.remove(2)">
1 2 3 2 # l
1 x2 3 x2 # 値が 2 のノードを消す
1 3 # 完了
</div>

```cpp
#include <list>
#include <print>

int main() {
  std::list<int> l = {1, 2, 3, 2, 5, 6};
  l.remove(2);
  l.remove_if([](int x) { return x % 2 == 0; });
  std::println("{}", l);
}
```

```text title="実行結果"
[1, 3, 5]
```

### splice {#splice}

```cpp
void splice(const_iterator pos, list& other);
void splice(const_iterator pos, list& other, const_iterator it);
void splice(const_iterator pos, list& other, const_iterator first, const_iterator last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `const_iterator` | この位置の前に入れる |
| `other` | `list&` | 移す元のリスト（自分自身でもいい） |
| `it` | `const_iterator` | 移す要素 1 個 |
| `first`, `last` | `const_iterator` | 移す範囲 |

- ポインタをつなぎ替えるだけで、要素はコピーもムーブもされません。O(1)

<div class="anim" data-label="a.splice(pos, b)">
1 2 3 | 8 9 # a と b
1 >8 >9 2 3 | _ # b のノードを a に移す。コピーなし
</div>

```cpp
#include <list>
#include <print>
#include <string>

int main() {
  // 最近使った順（先頭が一番新しい）
  std::list<std::string> recent = {"sword", "shield", "potion"};
  auto it = std::next(recent.begin(), 2);  // potion
  recent.splice(recent.begin(), recent, it);  // potion を先頭へ移動
  std::println("{}", recent);
}
```

```text title="実行結果"
["potion", "sword", "shield"]
```

!!! note "実際は"
    LRU キャッシュ（最近使ったものを先頭に移す）が list の数少ない出番です。

### sort {#sort}

```cpp
void sort();
template <class Compare>
void sort(Compare comp);
```

- 並べ替えます。list のイテレータは飛べないので、`std::ranges::sort` は使えず、このメンバ関数を使います

<div class="anim" data-label="l.sort()">
3 1 4 2 # l
>1 >2 >3 >4 # ノードをつなぎ替えて並べ替える
</div>

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全削除します。ノードを 1 個ずつ解放するので O(n)

<div class="anim" data-label="l.clear()">
10 20 30 # l
x10 x20 x30 # 全ノードを破棄
_ # 空
</div>

### emplace_back {#emplace_back}

```cpp
template <class... Args>
reference emplace_back(Args&&... args);
```

- 末尾にその場で構築します

<div class="anim" data-label="l.emplace_back(40)">
10 20 30 # l
10 20 30 +40 # ノードの中でその場で作る
</div>

### emplace_front {#emplace_front}

```cpp
template <class... Args>
reference emplace_front(Args&&... args);
```

- 先頭にその場で構築します

<div class="anim" data-label="l.emplace_front(5)">
10 20 30 # l
+5 10 20 30 # ノードの中でその場で作る
</div>

### unique {#unique}

```cpp
size_type unique();
```

- **連続している**重複を 1 個にまとめます。全体の重複を消すなら先に `sort` します

<div class="anim" data-label="l.unique()">
1 1 2 2 2 3 # 連続した同じ値
1 x1 2 x2 x2 3 # 連続する重複を消す
1 2 3 # 完了
</div>

### reverse {#reverse}

```cpp
void reverse() noexcept;
```

- 順番を逆にします

<div class="anim" data-label="l.reverse()">
1 2 3 4 # l
>4 >3 >2 >1 # つなぎ替えで逆順になる。要素のコピーはなし
</div>

### merge {#merge}

```cpp
void merge(list& other);
```

- ソート済みの `other` をソート済みの自分に合流させます。`other` は空になります

<div class="anim" data-label="a.merge(b)">
1 4 7 | 2 5 8 # どちらも整列済み
1 >2 4 >5 7 >8 | _ # b のノードが a に移る
1 2 4 5 7 8 | _ # a が整列したまま 1 本になる
</div>

```cpp
#include <list>
#include <print>

int main() {
  std::list<int> a = {3, 1, 3, 2};
  a.sort();
  a.unique();
  std::list<int> b = {0, 4};
  a.merge(b);
  a.reverse();
  std::println("{} / b {}", a, b);
}
```

```text title="実行結果"
[4, 3, 2, 1, 0] / b []
```

### assign {#assign}

```cpp
void assign(size_type n, const T& value);
template <class InputIt>
void assign(InputIt first, InputIt last);
void assign(std::initializer_list<T> il);
```

- 計算量: O(要素数)

中身を全部捨てて、新しい要素で置き換えます。

### assign_range <span class="ver ver-23">C++23</span> {#assign_range data-toc-label="assign_range"}

```cpp
template <ranges::input_range R>
void assign_range(R&& rg);
```

- 計算量: O(要素数)

範囲の要素で、中身を置き換えます。

### insert_range <span class="ver ver-23">C++23</span> {#insert_range data-toc-label="insert_range"}

```cpp
template <ranges::input_range R>
iterator insert_range(const_iterator pos, R&& rg);
```

- 計算量: O(挿入数 + 移動する要素数)

範囲の要素を `pos` の位置に挿入します。

### append_range <span class="ver ver-23">C++23</span> {#append_range data-toc-label="append_range"}

```cpp
template <ranges::input_range R>
void append_range(R&& rg);
```

- 計算量: O(追加数)

範囲の要素を末尾に追加します。`insert(end(), ...)` より意図が伝わります。

### prepend_range <span class="ver ver-23">C++23</span> {#prepend_range data-toc-label="prepend_range"}

```cpp
template <ranges::input_range R>
void prepend_range(R&& rg);
```

- 計算量: O(追加数)

範囲の要素を先頭に追加します。

### resize {#resize}

```cpp
void resize(size_type n);
void resize(size_type n, const T& value);
```

- 計算量: O(差)

要素数を `n` にします。増えるぶんは、既定値（または `value`）で埋め、減るぶんは末尾から削除します。

### operator= {#op_assign}

```cpp
list& operator=(const list& other);
list& operator=(list&& other) noexcept;
```

- 計算量: コピーは O(要素数)、ムーブは定数

コピー代入とムーブ代入。ムーブ代入は、中身の所有権を移すだけで、要素をコピーしません。

### operator== {#op_eq}

```cpp
bool operator==(const list& a, const list& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
auto operator<=>(const list& a, const list& b);
```

- 計算量: O(要素数)

要素を先頭から順に比べる、辞書順の三方比較。`<`・`>`・`<=`・`>=` も使えるようになります。

### cbegin {#cbegin}

```cpp
const_iterator cbegin() const noexcept;
```

- 計算量: 定数

先頭の要素を指す const イテレータ。要素を書き換えられないので、読むだけの走査で使います。

### cend {#cend}

```cpp
const_iterator cend() const noexcept;
```

- 計算量: 定数

終端（最後の要素の次）を指す const イテレータ。

### rbegin {#rbegin}

```cpp
reverse_iterator rbegin() noexcept;
```

- 計算量: 定数

逆順の先頭（最後の要素）を指すイテレータ。後ろから前へ走査するときに使います。

### crbegin {#crbegin}

```cpp
const_reverse_iterator crbegin() const noexcept;
```

- 計算量: 定数

逆順の先頭（最後の要素）を指す const イテレータ。

### rend {#rend}

```cpp
reverse_iterator rend() noexcept;
```

- 計算量: 定数

逆順の終端（先頭の手前）を指すイテレータ。

### crend {#crend}

```cpp
const_reverse_iterator crend() const noexcept;
```

- 計算量: 定数

逆順の終端（先頭の手前）を指す const イテレータ。

### max_size {#max_size}

```cpp
size_type max_size() const noexcept;
```

- 計算量: 定数

理論上、入れられる最大の要素数。実装の上限で、実際にそれだけ確保できるとは限りません。

### get_allocator {#get_allocator}

```cpp
allocator_type get_allocator() const noexcept;
```

- 計算量: 定数

使っているアロケータのコピー。

### swap {#swap}

```cpp
void swap(list& other) noexcept;
```

- 計算量: 定数

中身を `other` と入れ替えます。要素のコピーやムーブはせず、内部のポインタを入れ替えるだけなので速いです。

### emplace {#emplace}

```cpp
template <class... Args>
iterator emplace(Args&&... args);
```

- 計算量: O(log n)（順序つき）、平均 O(1)（unordered）

引数から、その場で要素を作って挿入します。コピーやムーブを避けられます。

## ゲームでの使いどころ

ほぼありません。代わりに以下を使います。

| やりたいこと | 代わり |
| --- | --- |
| 途中の要素を消したい | vector + `std::erase_if`、順番が要らないなら swap して pop_back |
| 要素のアドレスを固定したい | `std::vector<std::unique_ptr<T>>`、またはオブジェクトプール |
| 両端から出し入れしたい | [`std::deque`](deque.md) |

## パフォーマンス

- 要素 1 個ごとにヒープ確保が起きます（追加が遅い）。
- 要素 1 個ごとに前後のポインタ 16 バイトが余分にかかります。
- 回すたびにメモリの別の場所へ飛ぶので、キャッシュミスで**vector の何倍も遅く**なります。

## よくあるミス

??? failure "「途中の削除が O(1) だから速いはず」と思って使う"
    削除自体は O(1) でも、<strong>消す要素を探すのに O(n)</strong> かかり、その探索が vector より遅いので、トータルでは vector に負けることがほとんどです。

??? failure "std::sort に渡す"
    list のイテレータはランダムアクセスできないので、`std::sort(l.begin(), l.end())` はコンパイルエラーです。`l.sort()` を使います。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::vector`](vector.md) | 連続メモリ。ほぼ全部速い | ほとんどの場合 |
| [`std::deque`](deque.md) | 両端に強い | 両端から出し入れ |
| [`std::forward_list`](forward_list.md) | 片方向。もっと小さい | さらに使わない |

## コンパイラ対応

C++98 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 連結リスト。途中の挿入・削除が O(1)
    - [x] でも回すのが遅いので、ほぼ vector のほうが速い
    - [x] 迷ったら使わない

## 関連ページ

- [cpprefjp: std::list](https://cpprefjp.github.io/reference/list/list.html)
- [cppreference: std::list](https://en.cppreference.com/w/cpp/container/list)

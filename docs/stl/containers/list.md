---
title: std::list
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

`std::list` は、**要素どうしを前後のポインタでつないだ「双方向連結リスト」**です。要素はメモリ上のバラバラな場所に置かれ、それぞれが「前の要素」と「次の要素」の場所を覚えています。途中の要素を消したり、途中に入れたりするのが O(1) でできるのが特徴です。

!!! tip "結論"
    - **ほぼ使わない。** 教科書では「途中の挿入・削除が速い」と習うが、実際のゲームでは**ほとんどの場合 vector のほうが速い**。
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

### push_front {#push_front}

```cpp
void push_front(const T& value);
void push_front(T&& value);
```

- 先頭に追加します

### pop_back {#pop_back}

```cpp
void pop_back();
```

- 末尾を消します。空のとき未定義動作

### pop_front {#pop_front}

```cpp
void pop_front();
```

- 先頭を消します。空のとき未定義動作

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

### insert {#insert}

```cpp
iterator insert(const_iterator pos, const T& value);
```

- `pos` の前に挿入します。O(1)。他の要素は動きません

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

### remove {#remove}

```cpp
size_type remove(const T& value);
```

- `value` と等しい要素を全部消します

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

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全削除します。ノードを 1 個ずつ解放するので O(n)

### emplace_back {#emplace_back}

```cpp
template <class... Args>
reference emplace_back(Args&&... args);
```

- 末尾にその場で構築します

### emplace_front {#emplace_front}

```cpp
template <class... Args>
reference emplace_front(Args&&... args);
```

- 先頭にその場で構築します

### unique {#unique}

```cpp
size_type unique();
```

- **連続している**重複を 1 個にまとめます。全体の重複を消すなら先に `sort` します

### reverse {#reverse}

```cpp
void reverse() noexcept;
```

- 順番を逆にします

### merge {#merge}

```cpp
void merge(list& other);
```

- ソート済みの `other` を、ソート済みの自分に合流させます。`other` は空になります

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
    削除自体は O(1) でも、**消す要素を探すのに O(n)** かかり、その探索が vector より遅いので、トータルでは vector に負けることがほとんどです。

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

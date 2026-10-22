---
title: std::deque
summary: "先頭にも末尾にも素早く追加できる配列。ブロックに分かれて並ぶ。"
order: 8
tags:
  - コンテナ
---

# std::deque

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <deque>`
</div>

`std::deque`（デック）は、**先頭にも末尾にもすばやく追加・削除できる配列**です。vector は末尾にしか速く足せませんが、deque は先頭への追加も O(1) です。中身は小さなブロックをいくつも並べた構造になっていて、vector ほどきれいに 1 本には並んでいません。

!!! tip "ポイント"
    - <strong>先頭からも末尾からも出し入れするときだけ使う。</strong> それ以外は [`std::vector`](vector.md)。
    - 使い方は vector とほぼ同じ。追加で `push_front` / `pop_front` がある。
    - 「先に入れたものから取り出す」だけなら [`std::queue`](queue.md)（中身は deque）でもいい。
    - 追加しても**要素への参照は壊れない**（両端に追加するとき）。

!!! info "このページを読む前に"
    [`std::vector`](vector.md) を先に読んでおくと、差分だけで済みます。

## 宣言

```cpp
template <class T, class Allocator = std::allocator<T>>
class deque;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 必ず |
| `Allocator` | メモリの確保方法 | しない |

<div class="mem">
<div class="mem-step"><span class="mem-label">ブロック 1</span><span class="mem-cells"><span class="free">　</span><span class="free">　</span><span>A</span><span>B</span></span></div>
<div class="mem-step"><span class="mem-label">ブロック 2</span><span class="mem-cells"><span>C</span><span>D</span><span>E</span><span>F</span></span></div>
<div class="mem-step"><span class="mem-label">ブロック 3</span><span class="mem-cells"><span>G</span><span class="free">　</span><span class="free">　</span><span class="free">　</span></span><span class="mem-note">前にも後ろにも空きがあるので、両端への追加が速い</span></div>
</div>

## 関数一覧

vector と同じ名前の関数は同じ意味です。

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`push_back`](#push_back) | <span class="rank rank-must">必須</span> | 末尾に追加 | O(1) |
| [`push_front`](#push_front) | <span class="rank rank-must">必須</span> | **先頭に追加** | O(1) |
| [`pop_back`](#pop_back) | <span class="rank rank-must">必須</span> | 末尾を削除 | O(1) |
| [`pop_front`](#pop_front) | <span class="rank rank-must">必須</span> | **先頭を削除** | O(1) |
| [`front`](#front) | <span class="rank rank-must">必須</span> | 先頭の要素 | O(1) |
| [`back`](#back) | <span class="rank rank-must">必須</span> | 末尾の要素 | O(1) |
| [`size`](#size) | <span class="rank rank-must">必須</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-must">必須</span> | 空か | O(1) |
| [`emplace_back`](#emplace_back) | <span class="rank rank-often">よく使う</span> | 末尾にその場で構築 | O(1) |
| [`emplace_front`](#emplace_front) | <span class="rank rank-often">よく使う</span> | 先頭にその場で構築 | O(1) |
| [`operator[]`](#operator) | <span class="rank rank-often">よく使う</span> | i 番目（vector より少し遅い） | O(1) |
| [`begin`](#begin) | <span class="rank rank-often">よく使う</span> | 先頭のイテレータ | O(1) |
| [`end`](#end) | <span class="rank rank-often">よく使う</span> | 最後の次のイテレータ | O(1) |
| [`clear`](#clear) | <span class="rank rank-often">よく使う</span> | 全削除 | O(n) |
| [`std::erase_if`](#erase_if) | <span class="rank rank-sometimes">たまに</span> | 条件で削除 <span class="ver ver-20">C++20</span> | O(n) |
| [`at`](#at) | <span class="rank rank-sometimes">たまに</span> | 範囲チェック付きアクセス | O(1) |
| [`insert`](#insert) | <span class="rank rank-sometimes">たまに</span> | 途中に挿入 | O(n) |
| [`erase`](#erase) | <span class="rank rank-sometimes">たまに</span> | 途中を削除 | O(n) |
| [`resize`](#resize) | <span class="rank rank-rare">知ってるだけ</span> | 要素数を変える | O(n) |
| [`append_range`](#append_range) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を末尾に追加 <span class="ver ver-23">C++23</span> | O(m) |
| [`prepend_range`](#prepend_range) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を先頭に追加 <span class="ver ver-23">C++23</span> | O(m) |
| [`shrink_to_fit`](#shrink_to_fit) | <span class="rank rank-rare">知ってるだけ</span> | 余ったメモリを返す | O(n) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | O(1) |

`reserve`、`capacity`、`data` は**ありません**。中身が 1 本に並んでいないので、ポインタで C の API に渡すこともできません。

## よくある使い方

### 1. 両端から出し入れする

```cpp
#include <deque>
#include <print>

int main() {
  std::deque<int> d = {2, 3};
  d.push_front(1);  // 先頭に追加
  d.push_back(4);   // 末尾に追加
  std::println("{}", d);

  d.pop_front();
  d.pop_back();
  std::println("{}", d);
}
```

```text title="実行結果"
[1, 2, 3, 4]
[2, 3]
```

### 2. 直近 N 件の履歴

新しいものを末尾に足し、古いものを先頭から捨てます。入力履歴、ログ、FPS の平均などに使えます。

```cpp
#include <deque>
#include <print>

int main() {
  constexpr std::size_t kMaxHistory = 3;
  std::deque<float> frame_times;

  for (float t : {16.0f, 17.0f, 33.0f, 16.0f, 15.0f}) {
    frame_times.push_back(t);
    if (frame_times.size() > kMaxHistory) {
      frame_times.pop_front();  // 一番古いものを捨てる
    }
  }
  std::println("直近: {}", frame_times);
}
```

```text title="実行結果"
直近: [33, 16, 15]
```

## 関数の詳しい説明

### push_back {#push_back}

```cpp
void push_back(const T& value);
void push_back(T&& value);
```

- 末尾に追加します。O(1)（ブロックが足りなければ新しいブロックを確保）
- 追加しても既存の要素の**参照・ポインタは壊れない**（イテレータは壊れる）

<div class="anim" data-label="d.push_back(40)">
10 20 30 # d
10 20 30 +40 # 後ろに追加。ほかは動かない
</div>

### push_front {#push_front}

```cpp
void push_front(const T& value);
void push_front(T&& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` / `T&&` | 先頭に追加する値 |

- 先頭に追加します。O(1)。**vector に無い deque だけの機能**です

<div class="anim" data-label="d.push_front(5)">
10 20 30 # d
+5 10 20 30 # 前に追加。ほかは動かない（vector と違う）
</div>

```cpp
#include <deque>
#include <print>

int main() {
  std::deque<int> d = {2, 3};
  d.push_front(1);
  d.push_back(4);
  std::println("{}", d);
}
```

```text title="実行結果"
[1, 2, 3, 4]
```

### pop_back {#pop_back}

```cpp
void pop_back();
```

- 末尾を消します。戻り値なし。**空のとき未定義動作**

<div class="anim" data-label="d.pop_back()">
10 20 30 40 # d
10 20 30 x40 # 後ろを消す
10 20 30 # 完了
</div>

### pop_front {#pop_front}

```cpp
void pop_front();
```

- 先頭を消します。戻り値なし。**空のとき未定義動作**

<div class="anim" data-label="d.pop_front()">
10 20 30 40 # d
x10 20 30 40 # 前を消す
20 30 40 # ほかは動かない
</div>

```cpp
#include <deque>
#include <print>

int main() {
  std::deque<int> d = {1, 2, 3, 4};
  d.pop_front();
  d.pop_back();
  std::println("{}", d);
}
```

```text title="実行結果"
[2, 3]
```

### front {#front}

```cpp
reference front();
```

- 先頭の要素の参照。空のとき未定義動作

### back {#back}

```cpp
reference back();
```

- 末尾の要素の参照。空のとき未定義動作

```cpp
#include <deque>
#include <print>
#include <string>

int main() {
  std::deque<std::string> inputs = {"↓", "↘", "→"};
  std::println("最初 {} / 最後 {}", inputs.front(), inputs.back());
}
```

```text title="実行結果"
最初 ↓ / 最後 →
```

### size {#size}

```cpp
size_type size() const noexcept;
```

- 要素数。O(1)

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 空なら `true`。`pop_front` / `front` の前に確認します

### emplace_back {#emplace_back}

```cpp
template <class... Args>
reference emplace_back(Args&&... args);
```

- 末尾にその場で構築します。追加した要素の参照が返ります

<div class="anim" data-label="d.emplace_back(40)">
10 20 30 # d
10 20 30 +40 # 後ろにその場で作る
</div>

### emplace_front {#emplace_front}

```cpp
template <class... Args>
reference emplace_front(Args&&... args);
```

- 先頭にその場で構築します

<div class="anim" data-label="d.emplace_front(5)">
10 20 30 # d
+5 10 20 30 # 前にその場で作る
</div>

```cpp
#include <deque>
#include <print>
#include <string>

int main() {
  std::deque<std::string> d;
  d.emplace_back(2, 'b');
  d.emplace_front(3, 'a');
  std::println("{}", d);
}
```

```text title="実行結果"
["aaa", "bb"]
```

### operator[] {#operator}

```cpp
reference operator[](size_type pos);
```

- `pos` 番目の要素。範囲外は未定義動作
- O(1) ですが、「何番目のブロックの何番目か」を計算するので vector よりわずかに遅いです

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 先頭のイテレータ。範囲 for で使われます

### end {#end}

```cpp
iterator end() noexcept;
```

- 最後の次のイテレータ

```cpp
#include <deque>
#include <print>

int main() {
  std::deque<int> d = {10, 20, 30};
  int total = 0;
  for (int x : d) {
    total += x;
  }
  std::println("合計 {} / 2 番目 {}", total, d[1]);
}
```

```text title="実行結果"
合計 60 / 2 番目 20
```

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全要素を削除します

<div class="anim" data-label="d.clear()">
10 20 30 40 # d
x10 x20 x30 x40 # すべて破棄
_ _ _ _ # size 0
</div>

### std::erase_if <span class="ver ver-20">C++20</span> {#erase_if data-toc-label="std::erase_if"}

```cpp
template <class T, class Alloc, class Pred>
size_type erase_if(std::deque<T, Alloc>& c, Pred pred);
```

- 条件に合う要素をすべて消します（[vector の erase_if](vector.md#erase_if) と同じ）

### at {#at}

```cpp
reference at(size_type pos);
```

- 範囲外なら `std::out_of_range`

### insert {#insert}

```cpp
iterator insert(const_iterator pos, const T& value);
```

- `pos` の前に挿入します。O(n)（両端に近いほうをずらす）
- 途中に挿入すると、**参照・ポインタも全部壊れます**

<div class="anim" data-label="d.insert(d.begin() + 1, 99)">
10 20 30 40 # d
10 _ >20 >30 40 # 近い側（後ろ）をずらす
10 +99 20 30 40 # 99 を入れる。端に近いほど軽い
</div>

### erase {#erase}

```cpp
iterator erase(const_iterator pos);
iterator erase(const_iterator first, const_iterator last);
```

- 指定した位置を消します。O(n)

<div class="anim" data-label="d.erase(d.begin() + 1)">
10 20 30 40 # d
10 x20 30 40 # 消す
10 >30 >40 # 近い側を詰める
</div>

### resize {#resize}

```cpp
void resize(size_type count);
void resize(size_type count, const T& value);
```

- 要素数を `count` にします（[vector の resize](vector.md#resize) と同じ）

<div class="anim" data-label="d.resize(5)">
10 20 30 # d
10 20 30 +0 +0 # 足りない分を 0 で作る
</div>

### append_range <span class="ver ver-23">C++23</span> {#append_range data-toc-label="append_range"}

```cpp
template <container-compatible-range<T> R>
void append_range(R&& rg);
```

- 範囲をまとめて末尾に追加します

### prepend_range <span class="ver ver-23">C++23</span> {#prepend_range data-toc-label="prepend_range"}

```cpp
template <container-compatible-range<T> R>
void prepend_range(R&& rg);
```

- 範囲をまとめて先頭に追加します。**順番はそのまま**先頭に入ります（逆順にはならない）

```cpp
#include <deque>
#include <print>
#include <vector>

int main() {
  std::deque<int> d = {4, 5};
  d.prepend_range(std::vector<int>{1, 2, 3});
  d.append_range(std::vector<int>{6, 7});
  std::println("{}", d);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5, 6, 7]
```

### shrink_to_fit {#shrink_to_fit}

```cpp
void shrink_to_fit();
```

- 使っていないブロックのメモリを返すようにお願いします

### swap {#swap}

```cpp
void swap(deque& other) noexcept;
```

- 中身を交換します。O(1)

## フラグ・オプション

フラグはありません。

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |
| 両端への追加・削除 | O(1) |
| `[]` | O(1) |
| 途中への追加・削除 | O(n) |

## 古い書き方と今の書き方

特に変わっていません。vector の先頭に `insert(v.begin(), x)` していた古いコードは、deque の `push_front` に置き換えられます。

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

範囲の要素を、`pos` の位置に挿入します。

### operator= {#op_assign}

```cpp
deque& operator=(const deque& other);
deque& operator=(deque&& other) noexcept;
```

- 計算量: コピーは O(要素数)、ムーブは定数

コピー代入とムーブ代入。ムーブ代入は、中身の所有権を移すだけで、要素をコピーしません。

### operator== {#op_eq}

```cpp
bool operator==(const deque& a, const deque& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
auto operator<=>(const deque& a, const deque& b);
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

### emplace {#emplace}

```cpp
template <class... Args>
iterator emplace(Args&&... args);
```

- 計算量: O(log n)（順序つき）、平均 O(1)（unordered）

引数から、その場で要素を作って挿入します。コピーやムーブを避けられます。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 直近 N 件の履歴 | 入力バッファ（格闘ゲームのコマンド判定）、FPS 平均、ログ |
| 幅優先探索 | 経路探索・塗りつぶしの「次に調べるマス」 |
| アンドゥ・リドゥ | 上限を超えたら古い履歴を先頭から捨てる |

## パフォーマンス

- `[]` は「何番目のブロックの何番目か」を計算するので、vector よりわずかに遅いです。
- 回すのも vector より遅いですが、list よりはずっと速いです。
- 決まった大きさのリングバッファで足りるなら、`std::array` + 添字で自作したほうが速いです。

### イテレータ・参照が壊れる条件

| 操作 | イテレータ | 参照・ポインタ |
| --- | --- | --- |
| 両端に追加 | **全部壊れる** | 壊れない |
| 両端から削除 | 消した要素だけ | 消した要素だけ |
| 途中に追加・削除 | 全部 | 全部 |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空で `front` / `back` / `pop_front` / `pop_back` | 未定義動作 |
| 範囲外の `[]` | 未定義動作 |

## よくあるミス

??? failure "vector の代わりに何となく使う"
    deque は vector より回すのが遅く、`data()` もありません。先頭への追加が無いなら vector を使います。

??? failure "&d[0] を C の API に渡す"
    deque の中身は連続していないので、`&d[0]` から先を配列として読むと範囲外になります。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::vector`](vector.md) | 末尾だけ速い。中身が連続 | 先頭への追加が無い（ほとんどの場合） |
| [`std::queue`](queue.md) | deque を「先入れ先出し」専用にしたもの | 末尾に入れて先頭から出すだけ |
| [`std::list`](list.md) | 途中の挿入も O(1) だが遅い | ほぼ使わない |

## コンパイラ対応

C++98 からある機能です。`append_range` / `prepend_range` は C++23 で、GCC 15 / Clang 17 / MSVC 17.4 以降が目安です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭にも末尾にも O(1) で出し入れできる
    - [x] 使い方は vector とほぼ同じ。`push_front` / `pop_front` が増えただけ
    - [x] 先頭を使わないなら vector のほうが速い

## 関連ページ

- [cpprefjp: std::deque](https://cpprefjp.github.io/reference/deque/deque.html)
- [cppreference: std::deque](https://en.cppreference.com/w/cpp/container/deque)

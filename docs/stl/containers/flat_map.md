---
title: std::flat_map
summary: "`vector` で作った `map`。検索は速く回すのも速いが挿入・削除は遅い。"
order: 13
tags:
  - コンテナ
---

# std::flat_map

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-23">C++23</span>
`#include <flat_map>`
</div>

`std::flat_map` は、**中身がソート済みの vector になっている map** です。使い方は [`std::map`](map.md) とほぼ同じですが、中では「キーの vector」と「値の vector」を 2 本持っていて、検索は二分探索で行います。メモリが 1 本に並んでいるので、**検索と全要素のループが map より速い**一方、途中への追加・削除は vector と同じく O(n) で遅くなります。

!!! tip "ポイント"
    - <strong>最初に作って、あとは検索するだけの表に使う。</strong> アイテム表、パラメータ表、ローカライズの文字列表など。
    - 使い方は `std::map` と同じ（`[]`, `find`, `contains`, `lower_bound`）。
    - 頻繁に追加・削除するなら `std::map` か `std::unordered_map`。
    - **MSVC は VS 2026 の新しめの版から**対応している（[コンパイラ対応](#コンパイラ対応)）。

!!! info "このページを読む前に"
    [`std::map`](map.md) と [`std::vector`](vector.md) を知っていれば、差分だけで理解できます。

## 宣言

```cpp
template <class Key, class T, class Compare = std::less<Key>,
          class KeyContainer = std::vector<Key>,
          class MappedContainer = std::vector<T>>
class flat_map;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `Key` / `T` | キー / 値の型 | 必ず |
| `Compare` | 並び順 | map と同じ |
| `KeyContainer` / `MappedContainer` | キー・値を入れる入れ物 | しない（`std::vector` のまま） |

<div class="mem">
<div class="mem-step"><span class="mem-label">keys</span><span class="mem-cells"><span>10</span><span>20</span><span>30</span><span>40</span></span><span class="mem-note">ソート済み。二分探索で引く</span></div>
<div class="mem-step"><span class="mem-label">values</span><span class="mem-cells"><span>a</span><span>b</span><span>c</span><span>d</span></span><span class="mem-note">同じ添字が対応する</span></div>
</div>

## 関数一覧

map と同じ関数は同じ意味です。

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`find`](#find) | <span class="rank rank-must">必須</span> | 探す | O(log n) |
| [`contains`](#contains) | <span class="rank rank-must">必須</span> | あるか | O(log n) |
| [`operator[]`](#operator) | <span class="rank rank-must">必須</span> | 読み書き（無ければ**途中に挿入**） | O(log n)、挿入は O(n) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | 最小のキーのイテレータ（範囲 for はキーの順） | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 終わりのイテレータ | O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`at`](#at) | <span class="rank rank-often">よく使う</span> | 読み書き。無ければ例外 | O(log n) |
| [`lower_bound`](#lower_bound) | <span class="rank rank-often">よく使う</span> | 以上の最初 | O(log n) |
| [`upper_bound`](#upper_bound) | <span class="rank rank-often">よく使う</span> | より大きい最初 | O(log n) |
| [`keys`](#keys) | <span class="rank rank-often">よく使う</span> | キーだけの vector を見る | O(1) |
| [`values`](#values) | <span class="rank rank-often">よく使う</span> | 値だけの vector を見る | O(1) |
| [`insert`](#insert) | <span class="rank rank-sometimes">たまに</span> | 追加（後ろをずらす） | O(n) |
| [`try_emplace`](#try_emplace) | <span class="rank rank-sometimes">たまに</span> | 無いときだけ追加 | O(n) |
| [`erase`](#erase) | <span class="rank rank-sometimes">たまに</span> | 削除（後ろを詰める） | O(n) |
| [`clear`](#clear) | <span class="rank rank-sometimes">たまに</span> | 全削除 | O(n) |
| [`extract`](#extract) | <span class="rank rank-rare">知ってるだけ</span> | 中の vector を丸ごと取り出す | O(1) |
| [`replace`](#replace) | <span class="rank rank-rare">知ってるだけ</span> | 中の vector を丸ごと入れ替える | O(1) |
| [`std::erase_if`](#erase_if) | <span class="rank rank-rare">知ってるだけ</span> | 条件で削除 | O(n) |

## よくある使い方

### 1. 作ってから引くだけの表

```cpp
#include <flat_map>
#include <print>
#include <string>

int main() {
  // 読み込み時に一度だけ作る
  std::flat_map<int, std::string> item_names = {
      {300, "エリクサー"}, {100, "ポーション"}, {200, "エーテル"}};

  // あとは引くだけ
  if (auto it = item_names.find(200); it != item_names.end()) {
    std::println("200: {}", it->second);
  }

  for (const auto& [id, name] : item_names) {
    std::println("{} {}", id, name);
  }
}
```

```text title="実行結果"
200: エーテル
100 ポーション
200 エーテル
300 エリクサー
```

### 2. ソート済みのデータからまとめて作る

すでにソート済み・重複なしと分かっているなら `std::sorted_unique` を渡すと、並べ直しの手間が省けます。

```cpp
#include <flat_map>
#include <print>
#include <utility>
#include <vector>

int main() {
  std::vector<int> levels = {1, 2, 3, 4};
  std::vector<int> exp = {0, 100, 300, 700};

  // vector 2 本をそのまま渡して作る（ムーブすればコピーも起きない）
  std::flat_map<int, int> table(std::sorted_unique, std::move(levels),
                                std::move(exp));
  std::println("Lv.3 の必要経験値: {}", table[3]);
}
```

```text title="実行結果"
Lv.3 の必要経験値: 300
```

## 関数の詳しい説明

### find {#find}

```cpp
iterator find(const Key& key);
```

- 見つかった要素のイテレータ。無ければ `end()`
- 計算量: O(log n)（二分探索。キーが 1 本に並んでいるので map より速い）

<div class="anim" data-label="m.find(5)">
1 3 5 7 9 # 整列した配列
1 3 *5 7 9 # 二分探索で探す
</div>

### contains {#contains}

```cpp
bool contains(const Key& key) const;
```

- キーがあれば `true`

<div class="anim" data-label="m.contains(5)">
1 3 5 7 9 # 整列した配列
1 3 *5 7 9 # 二分探索で調べる
</div>

```cpp
#include <flat_map>
#include <print>
#include <string>

int main() {
  std::flat_map<int, std::string> names = {{100, "ポーション"}, {200, "エーテル"}};
  if (auto it = names.find(200); it != names.end()) {
    std::println("{}", it->second);
  }
  std::println("{}", names.contains(300));
}
```

```text title="実行結果"
エーテル
false
```

### operator[] {#operator}

```cpp
T& operator[](const Key& key);
```

- 値の参照。キーが無ければデフォルト値で**途中に挿入**します（後ろの要素をずらすので O(n)）

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 最小のキーの要素。範囲 for はキーの小さい順に回ります。中身が連続しているので map より速く回せます

### end {#end}

```cpp
iterator end() noexcept;
```

- 終わりのイテレータ

### size {#size}

```cpp
size_type size() const noexcept;
```

- 要素数

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 空なら `true`

### at {#at}

```cpp
T& at(const Key& key);
```

- 無ければ `std::out_of_range`。マスターデータのように「必ずあるはず」の表から読むときに向いています

### lower_bound {#lower_bound}

```cpp
iterator lower_bound(const Key& key);
```

- キーが `key` 以上の最初の要素（[map の lower_bound](map.md#lower_bound) と同じ）

<div class="anim" data-label="m.lower_bound(4)">
1 3 5 7 # 整列した配列
1 3 *5 7 # 4 以上で最初の要素
</div>

### upper_bound {#upper_bound}

```cpp
iterator upper_bound(const Key& key);
```

- キーが `key` より大きい最初の要素

<div class="anim" data-label="m.upper_bound(5)">
1 3 5 7 # 整列した配列
1 3 5 *7 # 5 より大きい最初の要素
</div>

```cpp
#include <flat_map>
#include <iterator>
#include <print>

int main() {
  std::flat_map<int, int> level_table = {{0, 1}, {100, 2}, {300, 3}};
  std::println("{}", std::prev(level_table.upper_bound(150))->second);
  std::println("{}", level_table.lower_bound(100)->second);
}
```

```text title="実行結果"
2
2
```

### keys {#keys}

```cpp
const key_container_type& keys() const noexcept;
```

- キーだけが入った vector の **const 参照**

### values {#values}

```cpp
const mapped_container_type& values() const noexcept;
```

- 値だけが入った vector の const 参照。同じ添字のキーと対応しています

```cpp
#include <flat_map>
#include <print>
#include <string>

int main() {
  std::flat_map<std::string, int> stats = {{"hp", 100}, {"atk", 20}, {"def", 15}};
  std::println("キー: {}", stats.keys());
  std::println("値:   {}", stats.values());
}
```

```text title="実行結果"
キー: ["atk", "def", "hp"]
値:   [20, 15, 100]
```

!!! note "実際は"
    値だけをまとめて `std::span` で別の関数に渡す、といった使い方ができます。map ではできない flat_map ならではの機能です。

### insert {#insert}

```cpp
std::pair<iterator, bool> insert(const value_type& value);
template <class InputIt>
void insert(InputIt first, InputIt last);
```

- 1 個版は後ろをずらして挿入するので O(n)。範囲版は「末尾にまとめて足して最後に並べ直す」ので、たくさん入れるならこちらが速い

<div class="anim" data-label="m.insert({4, &quot;D&quot;})">
1 3 5 # 整列した配列で持つ
1 3 _ >5 # 後ろをずらす（vector と同じ）
1 3 +4 5 # すき間に入れる
</div>

### try_emplace {#try_emplace}

```cpp
template <class... Args>
std::pair<iterator, bool> try_emplace(const Key& key, Args&&... args);
```

- 無いときだけ追加します。O(n)

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
```

- 削除します。後ろを詰めるので O(n)

<div class="anim" data-label="m.erase(3)">
1 3 5 7 # 整列した配列
1 x3 5 7 # 消す
1 >5 >7 _ # 後ろを詰める
</div>

```cpp
#include <flat_map>
#include <print>

int main() {
  std::flat_map<int, char> m;
  m.insert({3, 'c'});
  m.try_emplace(1, 'a');
  m.try_emplace(1, 'z');  // 既にあるので無視
  m.insert({2, 'b'});
  m.erase(3);
  std::println("{}", m);
}
```

```text title="実行結果"
{1: 'a', 2: 'b'}
```

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全削除します

<div class="anim" data-label="m.clear()">
1 3 5 # 整列した配列
x1 x3 x5 # すべて破棄
_ _ _ # 空
</div>

### extract {#extract}

```cpp
containers extract() &&;
```

- 中の vector 2 本（`keys` と `values`）を取り出します。flat_map は空になります

### replace {#replace}

```cpp
void replace(key_container_type&& keys, mapped_container_type&& values);
```

- vector 2 本を丸ごと入れ替えます。**ソート済み・重複なしである必要があります**（違うと未定義動作）

```cpp
#include <flat_map>
#include <print>
#include <utility>

int main() {
  std::flat_map<int, int> m = {{1, 10}, {2, 20}};
  auto [keys, values] = std::move(m).extract();
  for (int& v : values) {
    v *= 2;  // まとめて編集
  }
  m.replace(std::move(keys), std::move(values));
  std::println("{}", m);
}
```

```text title="実行結果"
{1: 20, 2: 40}
```

### std::erase_if {#erase_if}

```cpp
template <class K, class T, class C, class KC, class MC, class Pred>
size_type erase_if(std::flat_map<K, T, C, KC, MC>& c, Pred pred);
```

- 条件に合う要素をまとめて消します。O(n)

## フラグ・オプション

| 値 | 重要度 | 意味 | 使う場面 |
| --- | --- | --- | --- |
| `std::sorted_unique` | <span class="rank rank-sometimes">たまに</span> | 「渡すデータはソート済みで重複なし」という目印 | 事前に整えたデータから作るとき。**嘘をつくと未定義動作** |
| `std::sorted_equivalent` | <span class="rank rank-rare">知ってるだけ</span> | 「ソート済み（重複あり）」という目印 | `flat_multimap` 用 |

## 計算量まとめ

| 操作 | flat_map | map |
| --- | --- | --- |
| 検索 | O(log n)（速い） | O(log n) |
| 全要素を回す | O(n)（とても速い） | O(n) |
| 途中に追加・削除 | <strong>O(n)</strong> | O(log n) |

### emplace {#emplace}

```cpp
template <class... Args>
iterator emplace(Args&&... args);
```

- 計算量: O(log n)（順序つき）、平均 O(1)（unordered）

引数から、その場で要素を作って挿入します。コピーやムーブを避けられます。

### emplace_hint {#emplace_hint}

```cpp
template <class... Args>
iterator emplace_hint(const_iterator hint, Args&&... args);
```

- 計算量: ヒントが正しければ償却定数

挿入される位置のヒント（直前の位置）を渡して、その場で要素を作ります。ヒントが合っていれば、償却定数で挿入できます。

### insert_or_assign {#insert_or_assign}

```cpp
template <class M>
pair<iterator, bool> insert_or_assign(const key_type& k, M&& obj);
```

- 計算量: O(n)

キーがなければ挿入し、あれば値を上書きします。`operator[]` と違い、値の型に既定構築が要りません。挿入は、ソート済みの配列の途中への挿入なので、後ろの要素が動きます。

### count {#count}

```cpp
size_type count(const key_type& key) const;
```

- 計算量: O(log n + 個数)、平均 O(個数)（unordered）

指定したキーの要素の数を返します。重複を許すコンテナで意味があります。

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const key_type& key);
```

- 計算量: O(log n)、平均 O(個数)（unordered）

指定したキーに等しい要素の範囲（`[first, last)`）を返します。

### key_comp {#key_comp}

```cpp
key_compare key_comp() const;
```

- 計算量: 定数

キーの比較に使っている関数オブジェクトのコピー。

### value_comp {#value_comp}

```cpp
value_compare value_comp() const;
```

- 計算量: 定数

要素（キーと値のペア）の比較に使っている関数オブジェクトのコピー。

### swap {#swap}

```cpp
void swap(flat_map& other) noexcept;
```

- 計算量: 定数

中身を `other` と入れ替えます。要素のコピーやムーブはせず、内部のポインタを入れ替えるだけなので速いです。

### rbegin {#rbegin}

```cpp
reverse_iterator rbegin() noexcept;
```

- 計算量: 定数

逆順の先頭（最後の要素）を指すイテレータ。後ろから前へ走査するときに使います。

### rend {#rend}

```cpp
reverse_iterator rend() noexcept;
```

- 計算量: 定数

逆順の終端（先頭の手前）を指すイテレータ。

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

### max_size {#max_size}

```cpp
size_type max_size() const noexcept;
```

- 計算量: 定数

理論上、入れられる最大の要素数。実装の上限で、実際にそれだけ確保できるとは限りません。

### operator== {#op_eq}

```cpp
bool operator==(const flat_map& a, const flat_map& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| マスターデータ | アイテム表、敵パラメータ表（起動時に読み込んで以後変更しない） |
| ローカライズ | 文字列 ID → 翻訳テキスト |
| 小さめの表 | 要素数が数十〜数百で、追加より検索が多いもの |

## パフォーマンス

- キーが 1 本の vector に並んでいるので、二分探索のキャッシュ効率が良く、map よりかなり速く引けます。
- 1 個ずつ `insert` して作ると、毎回後ろをずらすので O(n²) になります。**まとめて作る**か、vector に溜めてからコンストラクタに渡します。
- 追加・削除で再確保が起きると、イテレータ・参照・ポインタは**すべて壊れます**（vector と同じ）。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `std::sorted_unique` を付けて、ソートされていないデータを渡す | 未定義動作 |
| 追加・削除のあとで古いイテレータ・参照を使う | 未定義動作 |

## よくあるミス

??? failure "ループで 1 個ずつ insert して遅くなる"
    ```cpp
    std::flat_map<int, Item> items;
    for (const auto& item : loaded) {
      items.insert({item.id, item});  // 毎回途中に挿入。O(n²)
    }
    ```

    一度 `std::vector<std::pair<int, Item>>` に溜めて、`std::flat_map` のコンストラクタに範囲で渡すと、最後に 1 回ソートするだけで済みます。

??? failure "map と同じつもりで参照を持ち続ける"
    map の要素への参照は追加しても壊れませんが、flat_map は vector なので壊れます。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::map`](map.md) | 木構造。追加・削除が O(log n) | 頻繁に追加・削除する |
| [`std::unordered_map`](unordered_map.md) | ハッシュ表。順番なし | 順番が要らない |
| [`std::flat_set`](flat_set.md) | キーだけ版 | 集合 |
| vector + sort + `lower_bound` | 同じことを手で書く | flat_map が使えない環境 |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::flat_map` / `flat_multimap` <span class="ver ver-23">C++23</span> | VS 2026 18.6 で使用可（18.2 以前は未対応） | 15〜 | 20〜 |

!!! info
    古い MSVC で使えない場合は、「ソート済みの `std::vector<std::pair<Key, T>>` + `std::ranges::lower_bound`」で同じことができます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ソート済み vector の map。検索と回すのが速い
    - [x] 追加・削除は O(n)。作ってから変更しない表に使う
    - [x] 1 個ずつ insert せず、まとめて作る

## 関連ページ

- [cpprefjp: std::flat_map](https://cpprefjp.github.io/reference/flat_map/flat_map.html)
- [cppreference: std::flat_map](https://en.cppreference.com/w/cpp/container/flat_map)

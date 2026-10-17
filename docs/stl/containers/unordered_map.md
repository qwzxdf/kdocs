---
title: std::unordered_map
tags:
  - コンテナ
---

# std::unordered_map

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <unordered_map>`
</div>

`std::unordered_map` は、<strong>キーから値をすばやく引ける表（ハッシュ表）</strong>です。「名前 → テクスチャ」「ID → 敵データ」のように、何かをキーにして対応する値を探したいときに使います。中ではキーから「ハッシュ値」という数値を計算して置き場所を決めるので、要素数が増えても検索はほぼ一定時間で終わります。並び順はバラバラです。

!!! tip "ポイント"
    - <strong>キーで検索したいならまずこれ。</strong> 順番が必要なときだけ [`std::map`](map.md)。
    - 入れるのは `m[key] = value;`、探すのは `find` か `contains`。
    - <strong>`m[key]` は「無ければ作る」</strong>。存在確認に `[]` を使わない。
    - 回す順番はバラバラ。表示順が大事なら別に並べる。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md)、[イテレータ](../../basics/iterator.md)、[計算量](../../basics/big-o.md) が分かると読みやすいです。`std::pair` も出てくるので [pair / tuple](../utilities/pair_tuple.md) もどうぞ。

## 宣言

```cpp
template <class Key, class T, class Hash = std::hash<Key>,
          class KeyEqual = std::equal_to<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class unordered_map;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `Key` | キーの型 | 必ず |
| `T` | 値の型 | 必ず |
| `Hash` | キーからハッシュ値を作る関数 | **自作の型をキーにするときだけ** |
| `KeyEqual` | キーが等しいかの判定 | ほぼしない |
| `Allocator` | メモリの確保方法 | しない |

中身は `std::pair<const Key, T>` の集まりです。範囲 for で回すと、`first` がキー、`second` が値として出てきます。

### 作り方

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |
| `std::unordered_map<std::string, int> m;` | <span class="rank rank-must">必須</span> | 空 |
| `std::unordered_map<std::string, int> m = {{"hp", 100}, {"mp", 30}};` | <span class="rank rank-must">必須</span> | 2 要素 |
| `std::unordered_map<std::string, int> m(other);` | <span class="rank rank-sometimes">たまに</span> | コピー |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator[]`](#operator) | <span class="rank rank-must">必須</span> | 読み書き。**無ければ作る** | 平均 O(1) |
| [`find`](#find) | <span class="rank rank-must">必須</span> | 探す。見つからなければ `end()` | 平均 O(1) |
| [`contains`](#contains) | <span class="rank rank-must">必須</span> | あるかどうか <span class="ver ver-20">C++20</span> | 平均 O(1) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | 先頭のイテレータ（範囲 for で使われる） | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 終わりのイテレータ。「見つからない」の印 | O(1) |
| [`erase`](#erase) | <span class="rank rank-often">よく使う</span> | キーや位置を指定して削除 | 平均 O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`try_emplace`](#try_emplace) | <span class="rank rank-often">よく使う</span> | 無いときだけ追加 <span class="ver ver-17">C++17</span> | 平均 O(1) |
| [`insert_or_assign`](#insert_or_assign) | <span class="rank rank-sometimes">たまに</span> | あれば上書き、無ければ追加 <span class="ver ver-17">C++17</span> | 平均 O(1) |
| [`at`](#at) | <span class="rank rank-sometimes">たまに</span> | 読み書き。無ければ例外 | 平均 O(1) |
| [`clear`](#clear) | <span class="rank rank-sometimes">たまに</span> | 全削除 | O(n) |
| [`reserve`](#reserve) | <span class="rank rank-sometimes">たまに</span> | n 個入れても再ハッシュしないよう準備 | O(n) |
| [`std::erase_if`](#erase_if) | <span class="rank rank-sometimes">たまに</span> | 条件で削除 <span class="ver ver-20">C++20</span> | O(n) |
| [`insert`](#insert) | <span class="rank rank-sometimes">たまに</span> | 追加（既にあれば何もしない） | 平均 O(1) |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で構築して追加 | 平均 O(1) |
| [`count`](#count) | <span class="rank rank-rare">知ってるだけ</span> | 0 か 1 を返す。`contains` で十分 | 平均 O(1) |
| [`extract`](#extract) | <span class="rank rank-rare">知ってるだけ</span> | 要素をノードとして取り外す <span class="ver ver-17">C++17</span> | 平均 O(1) |
| [`merge`](#merge) | <span class="rank rank-rare">知ってるだけ</span> | 別の map の要素を移す <span class="ver ver-17">C++17</span> | 平均 O(m) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | O(1) |
| [`equal_range`](#equal_range) | <span class="rank rank-rare">知ってるだけ</span> | キーに一致する範囲（multimap 用） | 平均 O(1) |
| [`bucket_count`](#bucket_count) | <span class="rank rank-rare">知ってるだけ</span> | バケットの数 | O(1) |
| [`load_factor`](#load_factor) | <span class="rank rank-rare">知ってるだけ</span> | 1 バケットあたりの平均要素数 | O(1) |
| [`max_load_factor`](#max_load_factor) | <span class="rank rank-rare">知ってるだけ</span> | 再ハッシュのしきい値の取得・設定 | O(1) |
| [`rehash`](#rehash) | <span class="rank rank-rare">知ってるだけ</span> | バケット数を指定して作り直す | O(n) |
| [`bucket`](#bucket) | <span class="rank rank-rare">知ってるだけ</span> | キーが入るバケットの番号 | O(1) |
| [`hash_function`](#hash_function) | <span class="rank rank-rare">知ってるだけ</span> | 使っているハッシュ関数を取得 | O(1) |

## よくある使い方

### 1. 入れて、探して、回す

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, int> prices;

  // 入れる（上書きも同じ書き方）
  prices["potion"] = 50;
  prices["ether"] = 120;
  prices["potion"] = 60;

  // 探す
  if (auto it = prices.find("ether"); it != prices.end()) {
    std::println("ether は {} G", it->second);
  }

  // あるかどうかだけ
  std::println("elixir はある？ {}", prices.contains("elixir"));

  // 全部回す（順番はバラバラ）
  for (const auto& [name, price] : prices) {
    std::println("{}: {}", name, price);
  }
}
```

```text title="実行結果（例。最後の 2 行の順番は実装によって変わる）"
ether は 120 G
elixir はある？ false
ether: 120
potion: 60
```

`const auto& [name, price]` は「構造化束縛」という書き方で、`pair` の `first` と `second` に名前を付けて取り出しています。

### 2. 数を数える

`[]` は「無ければ 0（値の型のデフォルト値）で作る」ので、カウンタにそのまま使えます。

```cpp
#include <print>
#include <string>
#include <unordered_map>
#include <vector>

int main() {
  std::vector<std::string> drops = {"slime", "bat", "slime", "slime", "bat"};

  std::unordered_map<std::string, int> counts;
  for (const auto& name : drops) {
    ++counts[name];  // 初めての名前なら 0 から始まる
  }

  std::println("slime: {} / bat: {}", counts["slime"], counts["bat"]);
}
```

```text title="実行結果"
slime: 3 / bat: 2
```

### 3. リソースをキャッシュする

同じテクスチャを何度も読み込まないように、名前をキーにして覚えておく定番の使い方です。

```cpp
#include <memory>
#include <print>
#include <string>
#include <unordered_map>

struct Texture {
  std::string path;
};

class TextureCache {
 public:
  const Texture& Get(const std::string& path) {
    // 無いときだけ作る。あればそれを返す
    auto [it, inserted] = cache_.try_emplace(path, nullptr);
    if (inserted) {
      std::println("読み込み: {}", path);
      it->second = std::make_unique<Texture>(path);
    }
    return *it->second;
  }

 private:
  std::unordered_map<std::string, std::unique_ptr<Texture>> cache_;
};

int main() {
  TextureCache cache;
  cache.Get("player.png");
  cache.Get("enemy.png");
  cache.Get("player.png");  // 2 回目は読み込まない
}
```

```text title="実行結果"
読み込み: player.png
読み込み: enemy.png
```

### 4. 自作の型をキーにする

`int` や `std::string` はそのままキーにできますが、自作の構造体をキーにするには「ハッシュの作り方」と `==` が必要です。

```cpp
#include <cstddef>
#include <functional>
#include <print>
#include <string>
#include <unordered_map>

struct GridPos {
  int x;
  int y;
  bool operator==(const GridPos&) const = default;
};

// GridPos からハッシュ値を作る関数オブジェクト
struct GridPosHash {
  std::size_t operator()(const GridPos& p) const {
    std::size_t h1 = std::hash<int>{}(p.x);
    std::size_t h2 = std::hash<int>{}(p.y);
    return h1 ^ (h2 << 1);
  }
};

int main() {
  std::unordered_map<GridPos, std::string, GridPosHash> objects;
  objects[{3, 4}] = "宝箱";
  objects[{0, 1}] = "看板";

  std::println("(3, 4) には {}", objects[{3, 4}]);
}
```

```text title="実行結果"
(3, 4) には 宝箱
```

## 関数の詳しい説明

### operator[] {#operator}

```cpp
T& operator[](const Key& key);
T& operator[](Key&& key);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` / `Key&&` | キー |

- 戻り値: 値の参照。**キーが無ければ値をデフォルト構築して追加し、その参照を返す**
- 計算量: 平均 O(1)、最悪 O(n)

<div class="anim" data-label="m[&quot;C&quot;]">
_ A _ B _ _ # バケット
_ A _ B +C _ # なければ作られる
</div>

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, int> stock;
  stock["potion"] = 3;   // 追加
  stock["potion"] += 2;  // 上書き
  std::println("potion: {}", stock["potion"]);

  // 読んだだけで "ether" が 0 で追加される
  int ether = stock["ether"];
  std::println("ether: {} / size: {}", ether, stock.size());
}
```

```text title="実行結果"
potion: 5
ether: 0 / size: 2
```

!!! warning "読むだけのつもりでも要素が増える"
    存在確認には `contains` か `find` を使います。また `const` な map には `[]` が使えません（追加する可能性があるため）。

### find {#find}

```cpp
iterator find(const Key& key);
const_iterator find(const Key& key) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 探すキー |

- 戻り値: 見つかった要素のイテレータ。**見つからなければ `end()`**
- 計算量: 平均 O(1)、最悪 O(n)

<div class="anim" data-label="m.find(&quot;B&quot;)">
_ A _ B _ _ # バケット
_ A _ *B _ _ # ハッシュで箱を決めて探す。順番は関係ない
</div>

```cpp
#include <print>
#include <string>
#include <unordered_map>

struct Enemy {
  int hp;
};

int main() {
  std::unordered_map<int, Enemy> enemies = {{1, {30}}, {2, {50}}};

  if (auto it = enemies.find(2); it != enemies.end()) {
    it->second.hp -= 20;  // it->first がキー、it->second が値
    std::println("敵 {} の HP: {}", it->first, it->second.hp);
  }
  if (enemies.find(9) == enemies.end()) {
    std::println("敵 9 はいない");
  }
}
```

```text title="実行結果"
敵 2 の HP: 30
敵 9 はいない
```

!!! note "実際は"
    「あったら使う」は `find` が基本です。`contains` で確認してから `[]` で取ると、**検索が 2 回**走ります。

### contains <span class="ver ver-20">C++20</span> {#contains data-toc-label="contains"}

```cpp
bool contains(const Key& key) const;
```

- 戻り値: キーがあれば `true`
- 計算量: 平均 O(1)

<div class="anim" data-label="m.contains(&quot;B&quot;)">
_ A _ B _ _ # バケット
_ A _ *B _ _ # あれば true
</div>

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, bool> flags = {{"met_king", true}};
  std::println("{} {}", flags.contains("met_king"), flags.contains("beat_boss"));
}
```

```text title="実行結果"
true false
```

!!! note "実際は"
    「あるかどうか」だけ知りたいときに使います。値も使うなら `find` にします。

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 戻り値: 最初の要素のイテレータ（**どの要素が最初かは決まっていない**）
- 計算量: O(1)

範囲 for はこの `begin` から `end` まで回します。要素は `std::pair<const Key, T>` なので、構造化束縛で取り出すのが定番です。

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, int> prices = {{"potion", 50}};
  for (auto& [name, price] : prices) {
    price *= 2;  // 値は書き換えられる。キーは const
    std::println("{}: {}", name, price);
  }
}
```

```text title="実行結果"
potion: 100
```

### end {#end}

```cpp
iterator end() noexcept;
```

- 戻り値: 最後の要素の次を指すイテレータ。`find` が「見つからない」ときに返す
- 計算量: O(1)
- `end()` を `->` や `*` で読むと未定義動作

!!! note "実際は"
    `it != m.end()` の比較にしか使いません。

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
iterator erase(const_iterator first, const_iterator last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 消したいキー |
| `pos` | `const_iterator` | 消したい要素の位置 |
| `first`, `last` | `const_iterator` | 消す範囲 |

- 戻り値: キー版は消した数（0 か 1）。位置版は次の要素のイテレータ
- 消した要素以外のイテレータ・参照は**壊れない**

<div class="anim" data-label="m.erase(&quot;B&quot;)">
_ A _ B C _ # バケット
_ A _ xB C _ # 消す
_ A _ _ C _ # ほかは動かない
</div>

```cpp
#include <print>
#include <unordered_map>

int main() {
  std::unordered_map<int, int> hp = {{1, 30}, {2, 0}, {3, 50}};
  std::size_t n = hp.erase(2);
  std::println("消した数: {} / 残り: {}", n, hp.size());
  std::println("もう一度: {}", hp.erase(2));
}
```

```text title="実行結果"
消した数: 1 / 残り: 2
もう一度: 0
```

### size {#size}

```cpp
size_type size() const noexcept;
```

- 戻り値: 要素数
- 計算量: O(1)

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 戻り値: 要素が 0 個なら `true`
- 計算量: O(1)

```cpp
#include <print>
#include <unordered_map>

int main() {
  std::unordered_map<int, int> m;
  std::println("{} {}", m.empty(), m.size());
  m[1] = 10;
  std::println("{} {}", m.empty(), m.size());
}
```

```text title="実行結果"
true 0
false 1
```

### try_emplace <span class="ver ver-17">C++17</span> {#try_emplace data-toc-label="try_emplace"}

```cpp
template <class... Args>
std::pair<iterator, bool> try_emplace(const Key& key, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | キー |
| `args` | 何個でも | 値のコンストラクタ引数。**キーが無いときだけ使われる** |

- 戻り値: `pair<イテレータ, 追加したか>`
- 計算量: 平均 O(1)

<div class="anim" data-label="m.try_emplace(&quot;A&quot;, 9)">
_ A _ B _ _ # すでにキー A がある
_ *A _ B _ _ # あるので何もしない
</div>

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, int> scores;
  auto [it1, added1] = scores.try_emplace("Alice", 100);
  auto [it2, added2] = scores.try_emplace("Alice", 999);  // 既にあるので無視
  std::println("{} {} {}", added1, added2, scores["Alice"]);
}
```

```text title="実行結果"
true false 100
```

!!! note "実際は"
    [よくある使い方 3](#3-リソースをキャッシュする) のように「無ければ作る、あれば何もしない」を 1 回の検索で書けます。

### insert_or_assign <span class="ver ver-17">C++17</span> {#insert_or_assign data-toc-label="insert_or_assign"}

```cpp
template <class M>
std::pair<iterator, bool> insert_or_assign(const Key& key, M&& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | キー |
| `value` | 値 | 入れる値 |

- 戻り値: `pair<イテレータ, 新しく追加したか>`（上書きなら `false`）

<div class="anim" data-label="m.insert_or_assign(&quot;A&quot;, 9)">
_ A _ B _ _ # すでにキー A がある
_ +A _ B _ _ # あれば値を上書き、なければ追加
</div>

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, int> best;
  auto [it1, added1] = best.insert_or_assign("stage1", 300);
  auto [it2, added2] = best.insert_or_assign("stage1", 450);
  std::println("{} {} {}", added1, added2, best["stage1"]);
}
```

```text title="実行結果"
true false 450
```

!!! note "実際は"
    `m[key] = value` とほぼ同じですが、値の型にデフォルトコンストラクタが無くても使え、「新規か上書きか」も分かります。

### at {#at}

```cpp
T& at(const Key& key);
const T& at(const Key& key) const;
```

- 戻り値: 値の参照
- 例外: キーが無ければ `std::out_of_range`

<div class="anim" data-label="m.at(&quot;B&quot;)">
_ A _ B _ _ # バケット
_ A _ *B _ _ # あれば値、なければ例外
</div>

```cpp
#include <print>
#include <string>
#include <unordered_map>

void PrintGravity(const std::unordered_map<std::string, float>& config) {
  // const な map には [] が使えないので at
  std::println("gravity = {}", config.at("gravity"));
}

int main() {
  PrintGravity({{"gravity", 9.8f}});
}
```

```text title="実行結果"
gravity = 9.8
```

!!! note "実際は"
    `const` な map から読むとき、「絶対にあるはず」のキー（設定値など）に使います。

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全要素を削除します
- 計算量: O(n)（要素ごとにメモリを解放する）

<div class="anim" data-label="m.clear()">
_ A _ B C _ # バケット
_ xA _ xB xC _ # すべて破棄
_ _ _ _ _ _ # 箱の数は残る
</div>

### reserve {#reserve}

```cpp
void reserve(size_type count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | `size_type` | この個数まで再ハッシュ（作り直し）が起きないようにする |

- 計算量: O(n)

<div class="anim" data-label="m.reserve(8)">
_ A _ B C _ # バケット 6 個
_ _ _ _ _ _ _ _ # 先に箱を増やす
_ >A _ >B _ >C _ _ # 要素は配置し直される（1 回だけ）
</div>

```cpp
#include <print>
#include <unordered_map>

int main() {
  std::unordered_map<int, int> m;
  m.reserve(1000);
  std::println("1000 個入れても再ハッシュしない: {}",
               m.bucket_count() * m.max_load_factor() >= 1000);
}
```

```text title="実行結果"
1000 個入れても再ハッシュしない: true
```

!!! note "実際は"
    要素が増えると、ある時点で表全体を作り直す「再ハッシュ」が起きます。個数が分かっているなら先に `reserve` しておきます。

### std::erase_if <span class="ver ver-20">C++20</span> {#erase_if data-toc-label="std::erase_if"}

```cpp
template <class K, class T, class H, class P, class A, class Pred>
size_type erase_if(std::unordered_map<K, T, H, P, A>& c, Pred pred);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `unordered_map&` | 対象 |
| `pred` | 関数・ラムダ | `pair<const Key, T>` を受け取り、`true` なら消す |

- 戻り値: 消した数
- 計算量: O(n)

```cpp
#include <print>
#include <unordered_map>

int main() {
  std::unordered_map<int, int> hp = {{1, 30}, {2, 0}, {3, -5}};
  std::size_t n =
      std::erase_if(hp, [](const auto& pair) { return pair.second <= 0; });
  std::println("{} 体消えた / 残り {}", n, hp.size());
}
```

```text title="実行結果"
2 体消えた / 残り 1
```

### insert {#insert}

```cpp
std::pair<iterator, bool> insert(const value_type& value);
void insert(std::initializer_list<value_type> ilist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `pair<const Key, T>` | 入れるキーと値 |
| `ilist` | `{...}` | まとめて入れる |

- 戻り値: `pair<イテレータ, 追加したか>`。**既にキーがあれば何もしない**（上書きしない）

<div class="anim" data-label="m.insert({&quot;C&quot;, 3})">
_ A _ B _ _ # 箱（バケット）が並んでいる
_ A _ B +C _ # ハッシュで決まった箱に入る
</div>

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, int> m;
  m.insert({"potion", 50});
  m.insert({"potion", 999});  // 上書きされない
  m.insert({{"ether", 120}, {"elixir", 500}});
  std::println("{} {}", m["potion"], m.size());
}
```

```text title="実行結果"
50 3
```

### emplace {#emplace}

```cpp
template <class... Args>
std::pair<iterator, bool> emplace(Args&&... args);
```

- `pair<const Key, T>` のコンストラクタ引数を渡して、その場で作ります
- 既にキーがあると、**作ったものを捨てる**（無駄に構築される）ことがあります

!!! note "実際は"
    `try_emplace` のほうが無駄が無く分かりやすいので、そちらを使います。

### count {#count}

```cpp
size_type count(const Key& key) const;
```

- 戻り値: キーの数（unordered_map では 0 か 1）

!!! note "実際は"
    C++20 より前は `count(key) > 0` で存在確認していました。今は `contains` を使います。

### extract <span class="ver ver-17">C++17</span> {#extract data-toc-label="extract"}

```cpp
node_type extract(const Key& key);
node_type extract(const_iterator pos);
```

- 要素を map から取り外して「ノード」として受け取ります。キーの書き換えや別の map への移動ができます（メモリの確保し直しが起きない）

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_map<std::string, int> m = {{"old_name", 1}};
  auto node = m.extract("old_name");
  node.key() = "new_name";  // キーを書き換える
  m.insert(std::move(node));
  std::println("{}", m.contains("new_name"));
}
```

```text title="実行結果"
true
```

### merge <span class="ver ver-17">C++17</span> {#merge data-toc-label="merge"}

```cpp
void merge(unordered_map& source);
```

- `source` の要素をこちらへ移します。**同じキーが既にある要素は `source` に残ります**

```cpp
#include <print>
#include <unordered_map>

int main() {
  std::unordered_map<int, char> a = {{1, 'a'}};
  std::unordered_map<int, char> b = {{1, 'x'}, {2, 'b'}};
  a.merge(b);
  std::println("a: {} 個 / b: {} 個", a.size(), b.size());
}
```

```text title="実行結果"
a: 2 個 / b: 1 個
```

### swap {#swap}

```cpp
void swap(unordered_map& other) noexcept;
```

- 中身を交換します。O(1)

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& key);
```

- キーに一致する要素の範囲を返します。unordered_map ではキーは 1 個しか無いので、`unordered_multimap` 用の関数です

### bucket_count {#bucket_count}

```cpp
size_type bucket_count() const noexcept;
```

- 今のバケット（置き場所）の数

### load_factor {#load_factor}

```cpp
float load_factor() const noexcept;
```

- 平均して 1 バケットに何個入っているか（`size() / bucket_count()`）

### max_load_factor {#max_load_factor}

```cpp
float max_load_factor() const noexcept;
void max_load_factor(float ml);
```

- `load_factor` がこの値を超えると再ハッシュが起きます。デフォルトは `1.0`。小さくすると速くなるがメモリを食う

### rehash {#rehash}

```cpp
void rehash(size_type count);
```

- バケット数を `count` 以上にして作り直します。`reserve(n)` は `rehash(n / max_load_factor())` と同じです

### bucket {#bucket}

```cpp
size_type bucket(const Key& key) const;
```

- キーが入るバケットの番号。ハッシュの偏りを調べるデバッグ用です

```cpp
#include <print>
#include <unordered_map>

int main() {
  std::unordered_map<int, int> m;
  for (int i = 0; i < 10; ++i) {
    m[i] = i;
  }
  std::println("要素 {} / 負荷率は上限以下？ {} / 上限 {}", m.size(),
               m.load_factor() <= m.max_load_factor(), m.max_load_factor());
}
```

```text title="実行結果"
要素 10 / 負荷率は上限以下？ true / 上限 1
```

!!! note "実際は"
    バケット関係の関数は、速度を詰める段階になるまで触る必要はありません。

### hash_function {#hash_function}

```cpp
hasher hash_function() const;
```

- この map が使っているハッシュ関数のコピーを返します。ほぼ使いません

## フラグ・オプション

フラグはありません。カスタマイズするのはテンプレート引数の `Hash` と `KeyEqual` です。

| 指定 | 重要度 | 意味 | 使う場面 |
| --- | --- | --- | --- |
| `Hash` | <span class="rank rank-sometimes">たまに</span> | キーからハッシュ値を作る | 自作の型をキーにする（[よくある使い方 4](#4-自作の型をキーにする)） |
| `KeyEqual` | <span class="rank rank-rare">知ってるだけ</span> | キーが等しいかの判定 | 大文字小文字を区別しない比較など |

## 計算量まとめ

| 操作 | 平均 | 最悪 |
| --- | --- | --- |
| `[]`, `find`, `contains`, `erase`, 追加 | O(1) | O(n) |
| 全要素を回す | O(n) | O(n) |
| `clear` | O(n) | O(n) |

最悪 O(n) になるのは、ハッシュ値がたくさんぶつかったとき（ハッシュ関数が悪いとき）です。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    if (m.count("potion") > 0) {
    }

    for (auto it = m.begin(); it != m.end(); ++it) {
      std::cout << it->first << ": " << it->second << "\n";
    }

    // 無ければ追加
    if (m.find(key) == m.end()) {
      m.insert(std::make_pair(key, Value(1, 2)));
    }

    // 条件で削除
    for (auto it = m.begin(); it != m.end();) {
      if (it->second <= 0) {
        it = m.erase(it);
      } else {
        ++it;
      }
    }
    ```

=== "今の書き方（C++23）"

    ```cpp
    if (m.contains("potion")) {
    }

    for (const auto& [name, value] : m) {
      std::println("{}: {}", name, value);
    }

    m.try_emplace(key, 1, 2);

    std::erase_if(m, [](const auto& p) { return p.second <= 0; });
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| リソース管理 | `unordered_map<std::string, Texture>`（名前 → テクスチャ） |
| ID で引く | `unordered_map<EntityId, Enemy>` |
| 設定・パラメータ | `unordered_map<std::string, float>`（`"gravity"` → `9.8`） |
| マップ上の物 | `unordered_map<GridPos, Item>`（広いマップにまばらに置く） |
| 入力の割り当て | `unordered_map<KeyCode, Action>` |

!!! note "毎フレーム全部回すなら vector"
    「全敵を毎フレーム更新する」ような処理は vector のほうが圧倒的に速いです。ID で引く用途と回す用途が両方あるなら、vector に本体を持ち、`unordered_map<Id, 添字>` で引けるようにする形がよく使われます。

## パフォーマンス

- 各要素は**別々にヒープ確保**される（ノードベース）ので、全要素を回すのは vector より遅いです。
- キーが `std::string` だと、検索のたびに文字列全体のハッシュを計算します。頻繁に引くなら数値 ID をキーにします。
- 要素数が少ない（数十個まで）なら、vector に入れて線形探索したほうが速いこともあります。
- 再ハッシュが起きると全要素の置き場所を作り直します。個数が分かっていれば `reserve` します。

### イテレータ・参照が壊れる条件

| 操作 | 壊れるもの |
| --- | --- |
| 追加で再ハッシュが起きた | **イテレータは全部**。参照・ポインタは壊れない |
| 追加（再ハッシュなし） | 壊れない |
| `erase` | 消した要素だけ |
| `clear` | 全部 |

vector と違って、**要素への参照やポインタは追加しても壊れません**。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `end()` を `->` で使う | 未定義動作 |
| 回している最中に追加して、そのイテレータを使い続ける | 未定義動作（再ハッシュで壊れる） |
| `at` で無いキー | `std::out_of_range` 例外 |
| キーを `const_cast` で書き換える | 未定義動作（置き場所がずれる） |

## よくあるミス

??? failure "[] で存在確認して要素が増える"
    ```cpp
    if (inventory["key"] > 0) {  // "key" が無いと 0 で追加される
    }

    // OK
    if (auto it = inventory.find("key"); it != inventory.end() && it->second > 0) {
    }
    ```

??? failure "回しながら erase する"
    ```cpp
    // NG: erase した it を ++ している
    for (auto it = m.begin(); it != m.end(); ++it) {
      if (it->second <= 0) {
        m.erase(it);
      }
    }

    // OK
    std::erase_if(m, [](const auto& p) { return p.second <= 0; });
    ```

??? failure "順番が保たれると思い込む"
    unordered_map を回して出てくる順番は、入れた順でもキーの順でもありません。ランキング表示などに使うなら、`std::map` を使うか、vector にコピーしてから `sort` します。

??? failure "自作の型をそのままキーにしてコンパイルエラー"
    `std::hash<GridPos>` が無いので、長いエラーが出ます。[よくある使い方 4](#4-自作の型をキーにする) のようにハッシュ関数と `==` を用意します。

??? failure "const な map で [] を使う"
    ```cpp
    void Print(const std::unordered_map<std::string, int>& m) {
      std::println("{}", m["hp"]);  // コンパイルエラー
      std::println("{}", m.at("hp"));  // OK（無ければ例外）
    }
    ```

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::map`](map.md) | キーの順に並ぶ。検索は O(log n) | 順番に回したい、範囲で探したい |
| [`std::unordered_set`](unordered_set.md) | キーだけで値が無い | 「あるかどうか」だけ知りたい |
| [`std::flat_map`](flat_map.md) | 中身がソート済み vector。回すのが速い <span class="ver ver-23">C++23</span> | 最初に作ってあとは引くだけの表 |
| [`std::vector`](vector.md) | 線形探索 | 要素が少ない、毎フレーム全部回す |
| [`std::multimap`](multimap.md) / `unordered_multimap` | 同じキーを複数持てる | ほぼ使わない |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `try_emplace` / `insert_or_assign` <span class="ver ver-17">C++17</span> | ○ | ○ | ○ |
| `contains` / `std::erase_if` <span class="ver ver-20">C++20</span> | ○ | ○ | ○ |

## これだけ覚える

!!! abstract "まとめ"
    - [x] キーで探すなら `std::unordered_map`
    - [x] 探すのは `find`（見つからなければ `end()`）、あるかだけなら `contains`
    - [x] `m[key]` は無ければ作る。存在確認に使わない
    - [x] 順番はバラバラ。毎フレーム全部回すなら vector のほうが速い

## 関連ページ

- [cpprefjp: std::unordered_map](https://cpprefjp.github.io/reference/unordered_map/unordered_map.html)
- [cppreference: std::unordered_map](https://en.cppreference.com/w/cpp/container/unordered_map)

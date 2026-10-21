---
title: std::map
summary: "キーの順に並ぶ「キー → 値」の表。範囲で探したいとき・順番に回したいときに。"
order: 5
tags:
  - コンテナ
---

# std::map

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <map>`
</div>

`std::map` は、**キーの順番に並んだ表**です。[`std::unordered_map`](unordered_map.md) と同じく「キー → 値」を持ちますが、中身が常にキーの小さい順に並んでいます。中は「赤黒木」という二分探索木で、検索・追加・削除はすべて O(log n) です。

!!! tip "ポイント"
    - <strong>キーの順番に回したいとき、範囲で探したいときに使う。</strong> それ以外は `unordered_map` で十分。
    - 関数の使い方は `unordered_map` とほぼ同じ（`[]`, `find`, `contains`, `erase`）。
    - map だけの強みは `lower_bound` / `upper_bound`（「この値以上で一番小さいキー」が探せる）。
    - 並び順を逆にしたいなら `std::map<int, T, std::greater<>>`。

!!! info "このページを読む前に"
    先に [`std::unordered_map`](unordered_map.md) を読んでおくと、このページは差分だけで済みます。[イテレータ](../../basics/iterator.md)、[計算量](../../basics/big-o.md) も関係します。

## 宣言

```cpp
template <class Key, class T, class Compare = std::less<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class map;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `Key` | キーの型。`<` で比較できる必要がある | 必ず |
| `T` | 値の型 | 必ず |
| `Compare` | 並べる順番を決める比較関数 | **逆順にしたいとき、`std::less<>` にしたいとき** |
| `Allocator` | メモリの確保方法 | しない |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator[]`](#operator) | <span class="rank rank-must">必須</span> | 読み書き。**無ければ作る** | O(log n) |
| [`find`](#find) | <span class="rank rank-must">必須</span> | 探す。見つからなければ `end()` | O(log n) |
| [`contains`](#contains) | <span class="rank rank-must">必須</span> | あるかどうか <span class="ver ver-20">C++20</span> | O(log n) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | **一番小さいキー**のイテレータ | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 終わりのイテレータ | O(1) |
| [`erase`](#erase) | <span class="rank rank-often">よく使う</span> | 削除 | O(log n) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`lower_bound`](#lower_bound) | <span class="rank rank-often">よく使う</span> | キーが**以上**の最初の要素 | O(log n) |
| [`upper_bound`](#upper_bound) | <span class="rank rank-often">よく使う</span> | キーが**より大きい**最初の要素 | O(log n) |
| [`rbegin`](#rbegin) | <span class="rank rank-often">よく使う</span> | **一番大きいキー**のイテレータ | O(1) |
| [`try_emplace`](#try_emplace) | <span class="rank rank-sometimes">たまに</span> | 無いときだけ追加 <span class="ver ver-17">C++17</span> | O(log n) |
| [`insert_or_assign`](#insert_or_assign) | <span class="rank rank-sometimes">たまに</span> | あれば上書き、無ければ追加 <span class="ver ver-17">C++17</span> | O(log n) |
| [`at`](#at) | <span class="rank rank-sometimes">たまに</span> | 無ければ例外 | O(log n) |
| [`std::erase_if`](#erase_if) | <span class="rank rank-sometimes">たまに</span> | 条件で削除 <span class="ver ver-20">C++20</span> | O(n) |
| [`clear`](#clear) | <span class="rank rank-sometimes">たまに</span> | 全削除 | O(n) |
| [`rend`](#rend) | <span class="rank rank-sometimes">たまに</span> | 逆順の終わり | O(1) |
| [`equal_range`](#equal_range) | <span class="rank rank-rare">知ってるだけ</span> | `lower_bound` と `upper_bound` の組 | O(log n) |
| [`insert`](#insert) | <span class="rank rank-rare">知ってるだけ</span> | 追加（既にあれば何もしない） | O(log n) |
| [`emplace`](#emplace) | <span class="rank rank-rare">知ってるだけ</span> | その場で構築して追加 | O(log n) |
| [`emplace_hint`](#emplace_hint) | <span class="rank rank-rare">知ってるだけ</span> | 位置のヒント付きで追加 | 償却 O(1)〜O(log n) |
| [`count`](#count) | <span class="rank rank-rare">知ってるだけ</span> | `contains` で十分 | O(log n) |
| [`extract`](#extract) | <span class="rank rank-rare">知ってるだけ</span> | ノードとして取り外す <span class="ver ver-17">C++17</span> | O(log n) |
| [`merge`](#merge) | <span class="rank rank-rare">知ってるだけ</span> | 別の map から移す <span class="ver ver-17">C++17</span> | O(m log n) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | O(1) |
| [`key_comp`](#key_comp) | <span class="rank rank-rare">知ってるだけ</span> | 比較関数を取得 | O(1) |

`reserve` と `bucket_count` などのハッシュ関係の関数はありません。

## よくある使い方

### 1. キーの順に表示する

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<int, std::string> stages;
  stages[3] = "砂漠";
  stages[1] = "草原";
  stages[2] = "森";

  // 入れた順ではなく、キーの小さい順に出てくる
  for (const auto& [number, name] : stages) {
    std::println("Stage {}: {}", number, name);
  }
}
```

```text title="実行結果"
Stage 1: 草原
Stage 2: 森
Stage 3: 砂漠
```

### 2. しきい値の表を引く

「経験値がいくつ以上ならレベルいくつ」のような表は、`upper_bound` で一発で引けます。

```cpp
#include <iterator>
#include <map>
#include <print>

int main() {
  // 必要経験値 → レベル
  std::map<int, int> level_table = {{0, 1}, {100, 2}, {300, 3}, {700, 4}};

  for (int exp : {0, 99, 100, 450, 9999}) {
    // exp より大きい最初のキーを探して、その 1 つ前が今のレベル
    auto it = std::prev(level_table.upper_bound(exp));
    std::println("経験値 {} → Lv.{}", exp, it->second);
  }
}
```

```text title="実行結果"
経験値 0 → Lv.1
経験値 99 → Lv.1
経験値 100 → Lv.2
経験値 450 → Lv.3
経験値 9999 → Lv.4
```

### 3. 大きい順に並べる

```cpp
#include <functional>
#include <map>
#include <print>
#include <string>

int main() {
  // std::greater<> を指定すると大きい順になる
  std::map<int, std::string, std::greater<>> ranking;
  ranking[1200] = "Bob";
  ranking[3400] = "Alice";
  ranking[800] = "Carol";

  int rank = 1;
  for (const auto& [score, name] : ranking) {
    std::println("{}位 {} ({})", rank++, name, score);
  }
}
```

```text title="実行結果"
1位 Alice (3400)
2位 Bob (1200)
3位 Carol (800)
```

!!! warning "同点があると上書きされる"
    map はキーが重複できないので、同じスコアの人が 2 人いると片方が消えます。ランキングには `std::multimap` か、`vector` に入れて `sort` するほうが向いています。

### 4. タイムラインを持つ

時刻をキーにして「次に起きるイベント」を取り出す使い方です。

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<float, std::string> events = {
      {1.0f, "敵出現"}, {2.5f, "ボス登場"}, {0.5f, "BGM 開始"}};

  float now = 0.8f;
  // now 以上で最初のイベント
  if (auto it = events.lower_bound(now); it != events.end()) {
    std::println("次は {} 秒: {}", it->first, it->second);
  }
}
```

```text title="実行結果"
次は 1 秒: 敵出現
```

## 関数の詳しい説明

使い方の多くは [`std::unordered_map`](unordered_map.md) と同じです。違うのは<strong>計算量が O(log n)</strong> であることと、**キーの順に並んでいる**ことです。

### operator[] {#operator}

```cpp
T& operator[](const Key& key);
T& operator[](Key&& key);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` / `Key&&` | キー |

- 戻り値: 値の参照。**キーが無ければデフォルト値で追加する**
- 計算量: O(log n)

<div class="anim" data-label="m[4]">
1 3 5 # キー
1 3 +4 5 # なければ作られる（値は 0 や空）
</div>

```cpp
#include <map>
#include <print>

int main() {
  std::map<int, int> kills;  // ステージ番号 → 倒した数
  ++kills[3];
  ++kills[1];
  ++kills[3];
  std::println("{}", kills);
}
```

```text title="実行結果"
{1: 1, 3: 2}
```

!!! warning
    unordered_map と同じく、読むだけのつもりでも要素が追加されます。存在確認には `contains` / `find` を使います。

### find {#find}

```cpp
iterator find(const Key& key);
const_iterator find(const Key& key) const;
```

- 戻り値: 見つかった要素のイテレータ。見つからなければ `end()`
- 計算量: O(log n)

<div class="anim" data-label="m.find(3)">
1 3 5 7 # キー
1 *3 5 7 # 見つかれば、その要素を指す
</div>

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<std::string, int> prices = {{"potion", 50}, {"ether", 120}};
  if (auto it = prices.find("ether"); it != prices.end()) {
    std::println("{} は {} G", it->first, it->second);
  }
}
```

```text title="実行結果"
ether は 120 G
```

### contains <span class="ver ver-20">C++20</span> {#contains data-toc-label="contains"}

```cpp
bool contains(const Key& key) const;
```

- 戻り値: キーがあれば `true`
- 計算量: O(log n)

<div class="anim" data-label="m.contains(3)">
1 3 5 7 # キー
1 *3 5 7 # あれば true
</div>

```cpp
#include <map>
#include <print>

int main() {
  std::map<int, bool> cleared = {{1, true}, {2, true}};
  std::println("{} {}", cleared.contains(2), cleared.contains(5));
}
```

```text title="実行結果"
true false
```

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 戻り値: **一番小さいキー**の要素のイテレータ。空なら `end()`
- 計算量: O(1)

範囲 for は `begin` から順に回るので、**キーの小さい順**に出てきます。

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<int, std::string> stages = {{3, "砂漠"}, {1, "草原"}, {2, "森"}};
  std::println("最初のステージ: {}", stages.begin()->second);
  for (const auto& [number, name] : stages) {
    std::println("Stage {}: {}", number, name);
  }
}
```

```text title="実行結果"
最初のステージ: 草原
Stage 1: 草原
Stage 2: 森
Stage 3: 砂漠
```

### end {#end}

```cpp
iterator end() noexcept;
```

- 戻り値: 最後の要素の次。`find` や `lower_bound` が「見つからない」ときに返す
- `end()` を読むと未定義動作

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
iterator erase(const_iterator first, const_iterator last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 消すキー |
| `pos` | `const_iterator` | 消す位置 |
| `first`, `last` | `const_iterator` | 消す範囲 |

- 戻り値: キー版は消した数、位置版は次の要素のイテレータ
- 計算量: O(log n)。範囲版は O(log n + 消す数)

<div class="anim" data-label="m.erase(3)">
1 3 5 # キー
1 x3 5 # 消す
1 5 # 完了
</div>

```cpp
#include <map>
#include <print>

int main() {
  std::map<int, char> m = {{10, 'a'}, {20, 'b'}, {30, 'c'}, {40, 'd'}};
  m.erase(20);
  // 25 以上を全部消す（範囲で消せるのは map ならでは）
  m.erase(m.lower_bound(25), m.end());
  std::println("{}", m);
}
```

```text title="実行結果"
{10: 'a'}
```

### size {#size}

```cpp
size_type size() const noexcept;
```

- 戻り値: 要素数。O(1)

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 戻り値: 空なら `true`。O(1)

### lower_bound {#lower_bound}

```cpp
iterator lower_bound(const Key& key);
const_iterator lower_bound(const Key& key) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 基準になるキー |

- 戻り値: キーが `key` **以上**の最初の要素。無ければ `end()`
- 計算量: O(log n)

<div class="mem">
<div class="mem-step"><span class="mem-label">キー</span><span class="mem-cells"><span>10</span><span>20</span><span class="move">30</span><span>40</span><span>50</span></span></div>
<div class="mem-step"><span class="mem-label">lower_bound(30)</span><span class="mem-note">→ 30（30 以上の最初）</span></div>
<div class="mem-step"><span class="mem-label">lower_bound(35)</span><span class="mem-note">→ 40（35 以上の最初）</span></div>
</div>

<div class="anim" data-label="m.lower_bound(4)">
1 3 5 7 # キー
1 3 *5 7 # 4 以上で最初の要素
</div>

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<float, std::string> events = {
      {1.0f, "敵出現"}, {2.5f, "ボス登場"}, {0.5f, "BGM 開始"}};

  float now = 0.8f;
  if (auto it = events.lower_bound(now); it != events.end()) {
    std::println("次は {} 秒: {}", it->first, it->second);
  }
}
```

```text title="実行結果"
次は 1 秒: 敵出現
```

### upper_bound {#upper_bound}

```cpp
iterator upper_bound(const Key& key);
const_iterator upper_bound(const Key& key) const;
```

- 戻り値: キーが `key` **より大きい**最初の要素。無ければ `end()`
- 計算量: O(log n)

<div class="mem">
<div class="mem-step"><span class="mem-label">キー</span><span class="mem-cells"><span>10</span><span>20</span><span>30</span><span class="new">40</span><span>50</span></span></div>
<div class="mem-step"><span class="mem-label">upper_bound(30)</span><span class="mem-note">→ 40（30 より大きい最初。30 自身は含まない）</span></div>
</div>

<div class="anim" data-label="m.upper_bound(5)">
1 3 5 7 # キー
1 3 5 *7 # 5 より大きい最初の要素
</div>

```cpp
#include <iterator>
#include <map>
#include <print>

int main() {
  // 必要経験値 → レベル
  std::map<int, int> level_table = {{0, 1}, {100, 2}, {300, 3}, {700, 4}};

  for (int exp : {0, 99, 100, 450, 9999}) {
    // exp より大きい最初のキーの、1 つ前が今のレベル
    auto it = std::prev(level_table.upper_bound(exp));
    std::println("経験値 {} → Lv.{}", exp, it->second);
  }
}
```

```text title="実行結果"
経験値 0 → Lv.1
経験値 99 → Lv.1
経験値 100 → Lv.2
経験値 450 → Lv.3
経験値 9999 → Lv.4
```

!!! note "実際は"
    「しきい値の表を引く」は `upper_bound` + `std::prev` が定番です。exp がどのキーより小さいと `begin()` の前に行ってしまうので、キー 0 を必ず入れておくなどの工夫をします。

### rbegin {#rbegin}

```cpp
reverse_iterator rbegin() noexcept;
```

- 戻り値: **一番大きいキー**の要素を指す逆向きのイテレータ
- 計算量: O(1)

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<int, std::string> scores = {{1200, "Bob"}, {3400, "Alice"}};
  std::println("最高点: {} ({})", scores.rbegin()->first, scores.rbegin()->second);
}
```

```text title="実行結果"
最高点: 3400 (Alice)
```

### try_emplace <span class="ver ver-17">C++17</span> {#try_emplace data-toc-label="try_emplace"}

```cpp
template <class... Args>
std::pair<iterator, bool> try_emplace(const Key& key, Args&&... args);
```

- キーが無いときだけ、`args` で値を作って追加します。戻り値は `pair<イテレータ, 追加したか>`
- 使い方は [unordered_map の try_emplace](unordered_map.md#try_emplace) と同じです

<div class="anim" data-label="m.try_emplace(3, &quot;X&quot;)">
1 3 5 # すでにキー 3 がある
1 *3 5 # あるので何もしない（値は上書きされない）
</div>

### insert_or_assign <span class="ver ver-17">C++17</span> {#insert_or_assign data-toc-label="insert_or_assign"}

```cpp
template <class M>
std::pair<iterator, bool> insert_or_assign(const Key& key, M&& value);
```

- あれば上書き、無ければ追加します。戻り値の `second` は新規なら `true`
- 使い方は [unordered_map の insert_or_assign](unordered_map.md#insert_or_assign) と同じです

<div class="anim" data-label="m.insert_or_assign(3, &quot;X&quot;)">
1 3 5 # すでにキー 3 がある
1 +3 5 # あれば値を上書き、なければ追加
</div>

### at {#at}

```cpp
T& at(const Key& key);
const T& at(const Key& key) const;
```

- キーが無ければ `std::out_of_range`。`const` な map から読むときに使います

<div class="anim" data-label="m.at(3)">
1 3 5 # キー
1 *3 5 # あれば値、なければ例外
</div>

### std::erase_if <span class="ver ver-20">C++20</span> {#erase_if data-toc-label="std::erase_if"}

```cpp
template <class K, class T, class C, class A, class Pred>
size_type erase_if(std::map<K, T, C, A>& c, Pred pred);
```

- `pred` に `pair<const Key, T>` が渡され、`true` なら消します。戻り値は消した数

```cpp
#include <map>
#include <print>

int main() {
  std::map<int, int> hp = {{1, 30}, {2, 0}, {3, 50}};
  std::erase_if(hp, [](const auto& p) { return p.second <= 0; });
  std::println("{}", hp);
}
```

```text title="実行結果"
{1: 30, 3: 50}
```

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全要素を削除します。O(n)

<div class="anim" data-label="m.clear()">
1 3 5 # キー
x1 x3 x5 # すべて破棄
_ _ _ # 空
</div>

### rend {#rend}

```cpp
reverse_iterator rend() noexcept;
```

- 戻り値: 逆順の終わり（一番小さいキーの 1 つ前）

```cpp
#include <functional>
#include <map>
#include <print>

int main() {
  std::map<int, char> m = {{1, 'a'}, {2, 'b'}, {3, 'c'}};
  for (auto it = m.rbegin(); it != m.rend(); ++it) {
    std::print("{} ", it->first);
  }
  std::println("");
}
```

```text title="実行結果"
3 2 1 
```

!!! note "実際は"
    いつも大きい順で回すなら、最初から `std::map<int, char, std::greater<>>` にしておくほうが分かりやすいです。

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& key);
```

- 戻り値: `{lower_bound(key), upper_bound(key)}`。普通の map では要素 0 個か 1 個の範囲になります
- 本領を発揮するのは [`std::multimap`](multimap.md#equal_range) です

<div class="anim" data-label="m.equal_range(3)">
1 3 5 # キー
1 *3 5 # [下限, 上限) の組。map では 0 〜 1 個
</div>

### insert {#insert}

```cpp
std::pair<iterator, bool> insert(const value_type& value);
void insert(std::initializer_list<value_type> ilist);
```

- 既にキーがあれば何もしません（上書きしない）。使い方は [unordered_map の insert](unordered_map.md#insert) と同じです

<div class="anim" data-label="m.insert({4, &quot;D&quot;})">
1 3 5 # キーは常に整列
1 3 +4 5 # 順番どおりの場所に入る
</div>

### emplace {#emplace}

```cpp
template <class... Args>
std::pair<iterator, bool> emplace(Args&&... args);
```

- その場で `pair` を作って追加します。`try_emplace` のほうが無駄が無いので、そちらを使います

### emplace_hint {#emplace_hint}

```cpp
template <class... Args>
iterator emplace_hint(const_iterator hint, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `hint` | `const_iterator` | 「たぶんこの位置の直前に入る」というヒント |
| `args` | 何個でも | `pair` のコンストラクタ引数 |

- ヒントが正しければ償却 O(1) で追加できます

```cpp
#include <map>
#include <print>

int main() {
  std::map<int, int> m;
  // ソート済みのデータを順に入れるなら、毎回 end() をヒントにすると速い
  for (int i = 0; i < 5; ++i) {
    m.emplace_hint(m.end(), i, i * i);
  }
  std::println("{}", m);
}
```

```text title="実行結果"
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

### count {#count}

```cpp
size_type count(const Key& key) const;
```

- 0 か 1 を返します。今は `contains` を使います

<div class="anim" data-label="m.count(3)">
1 3 5 7 # キー
1 *3 5 7 # 0 か 1（キーは重複しない）
</div>

### extract <span class="ver ver-17">C++17</span> {#extract data-toc-label="extract"}

```cpp
node_type extract(const Key& key);
```

- 要素をノードとして取り外します。キーを書き換えて入れ直す、別の map へ移す、といった使い方ができます（[unordered_map の extract](unordered_map.md#extract) と同じ）

### merge <span class="ver ver-17">C++17</span> {#merge data-toc-label="merge"}

```cpp
void merge(map& source);
```

- `source` の要素をこちらへ移します。同じキーがあるものは `source` に残ります

### swap {#swap}

```cpp
void swap(map& other) noexcept;
```

- 中身を交換します。O(1)

### key_comp {#key_comp}

```cpp
key_compare key_comp() const;
```

- この map が使っている比較関数のコピーを返します。テンプレートを書くとき以外は使いません

## フラグ・オプション

`Compare` に何を指定するかで並び順が変わります。

| 指定 | 重要度 | 意味 | 使う場面 |
| --- | --- | --- | --- |
| `std::less<Key>`（省略時） | <span class="rank rank-must">必須</span> | 小さい順 | 普通はこれ |
| `std::greater<>` | <span class="rank rank-often">よく使う</span> | 大きい順 | ランキング、新しい順 |
| `std::less<>` | <span class="rank rank-sometimes">たまに</span> | 小さい順。**型の違うキーでも検索できる**（透過比較） | `map<std::string, T>` を `string_view` や `"..."` で検索するとき、一時 string を作らずに済む |
| 自作の比較関数 | <span class="rank rank-rare">知ってるだけ</span> | 好きな順 | 構造体をキーにする（ただし `<=>` を定義するほうが簡単） |

```cpp
// std::less<> にすると find("potion") で一時的な std::string が作られない
std::map<std::string, int, std::less<>> prices;
prices.find(std::string_view("potion"));
```

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |
| `[]`, `find`, `contains`, `erase`, 追加 | O(log n) |
| `lower_bound`, `upper_bound` | O(log n) |
| 最小・最大（`begin`, `rbegin`） | O(1) |
| 全要素を回す | O(n) |

## 古い書き方と今の書き方

unordered_map と同じです（`count` → `contains`、イテレータのループ → 構造化束縛、手書きの削除ループ → `std::erase_if`）。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 順番が意味を持つ表 | ステージ番号 → データ、レベル → 必要経験値 |
| しきい値の検索 | 経験値からレベル、距離から LOD、HP 割合から表情 |
| タイムライン | 時刻 → イベント（カットシーン、リズムゲームのノーツ） |
| デバッグ表示 | 名前順に並べて表示したい統計 |

## パフォーマンス

- 要素は木の「ノード」としてバラバラにヒープ確保されます。回すのも検索も、要素が多いと **unordered_map や vector より遅い**です。
- 一方で、**最悪計算量が O(log n) で安定**しています（unordered_map の最悪 O(n) のような落とし穴が無い）。
- 作ったあとは検索しかしないなら [`std::flat_map`](flat_map.md) のほうが速いです。

### イテレータ・参照が壊れる条件

| 操作 | 壊れるもの |
| --- | --- |
| 追加 | 壊れない |
| `erase` | 消した要素だけ |
| `clear` | 全部 |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `end()` や空の map の `begin()` を `->` で使う | 未定義動作 |
| `std::prev(m.begin())` | 未定義動作 |
| 比較関数が「a < b かつ b < a」になりうる | 未定義動作（木が壊れる） |
| `at` で無いキー | `std::out_of_range` 例外 |

## よくあるミス

??? failure "upper_bound の結果を確認せずに prev する"
    ```cpp
    // level_table が空、または exp がどのキーよりも小さいと begin() の前に行ってしまう
    auto it = std::prev(level_table.upper_bound(exp));

    // OK
    auto it2 = level_table.upper_bound(exp);
    if (it2 != level_table.begin()) {
      --it2;
    }
    ```

??? failure "順番が要らないのに map を使う"
    「とりあえず map」で書くと、unordered_map より遅いことが多いです。順番が要らないなら unordered_map を選びます。

??? failure "浮動小数点をキーにして find が当たらない"
    `0.1f + 0.2f` と `0.3f` は等しくないことがあります。`find` ではなく `lower_bound` で「以上の最初」を探す形にします。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::unordered_map`](unordered_map.md) | 順番なし。平均 O(1) | 順番が要らない（ほとんどの場合） |
| [`std::flat_map`](flat_map.md) | ソート済み vector。検索と回すのが速い、追加は遅い <span class="ver ver-23">C++23</span> | 作ってから変更しない表 |
| [`std::set`](set.md) | キーだけ | 順番付きの「集合」 |
| [`std::multimap`](multimap.md) | 同じキーを複数持てる | 同点ありのランキング、同時刻のイベント |

## コンパイラ対応

C++98 からある機能です。`contains` / `std::erase_if`（C++20）も主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] キーの順に並ぶ表。使い方は unordered_map とほぼ同じ
    - [x] 順番が要らないなら unordered_map のほうが速い
    - [x] `lower_bound`（以上）/ `upper_bound`（より大きい）でしきい値検索ができる
    - [x] 逆順は `std::greater<>`

## 関連ページ

- [cpprefjp: std::map](https://cpprefjp.github.io/reference/map/map.html)
- [cppreference: std::map](https://en.cppreference.com/w/cpp/container/map)

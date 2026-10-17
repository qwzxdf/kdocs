---
title: std::unordered_set
tags:
  - コンテナ
---

# std::unordered_set

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <unordered_set>`
</div>

`std::unordered_set` は、<strong>重複しない値の集まり（集合）</strong>です。「この値が入っているか」をすばやく調べられます。[`std::unordered_map`](unordered_map.md) から「値」を取り除いて、キーだけにしたものだと考えると分かりやすいです。同じ値を 2 回入れても 1 個しか残りません。

!!! tip "ポイント"
    - <strong>「あるかどうか」だけ知りたいときに使う。</strong> 取得済みアイテム、訪問済みマス、当たり済みの敵など。
    - 入れるのは `insert`、調べるのは `contains`、消すのは `erase`。この 3 つで足りる。
    - 順番はバラバラ。順番が必要なら [`std::set`](set.md)。
    - 要素が数十個までなら、vector に入れて探すほうが速いこともある。

!!! info "このページを読む前に"
    [`std::unordered_map`](unordered_map.md) と仕組みは同じです。先に読んでおくと楽です。

## 宣言

```cpp
template <class Key, class Hash = std::hash<Key>,
          class KeyEqual = std::equal_to<Key>,
          class Allocator = std::allocator<Key>>
class unordered_set;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `Key` | 入れる値の型 | 必ず |
| `Hash` | ハッシュ関数 | 自作の型を入れるときだけ |
| `KeyEqual` / `Allocator` | 等しさの判定 / メモリ確保 | しない |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`insert`](#insert) | <span class="rank rank-must">必須</span> | 追加（既にあれば何もしない） | 平均 O(1) |
| [`contains`](#contains) | <span class="rank rank-must">必須</span> | 入っているか <span class="ver ver-20">C++20</span> | 平均 O(1) |
| [`erase`](#erase) | <span class="rank rank-must">必須</span> | 削除 | 平均 O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`clear`](#clear) | <span class="rank rank-often">よく使う</span> | 全削除 | O(n) |
| [`begin`](#begin) | <span class="rank rank-often">よく使う</span> | 先頭のイテレータ（範囲 for で使われる） | O(1) |
| [`end`](#end) | <span class="rank rank-often">よく使う</span> | 終わりのイテレータ | O(1) |
| [`find`](#find) | <span class="rank rank-sometimes">たまに</span> | 探してイテレータを返す | 平均 O(1) |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で構築して追加 | 平均 O(1) |
| [`reserve`](#reserve) | <span class="rank rank-sometimes">たまに</span> | 再ハッシュを防ぐ | O(n) |
| [`std::erase_if`](#erase_if) | <span class="rank rank-sometimes">たまに</span> | 条件で削除 <span class="ver ver-20">C++20</span> | O(n) |
| [`count`](#count) | <span class="rank rank-rare">知ってるだけ</span> | 0 か 1。`contains` で十分 | 平均 O(1) |
| [`extract`](#extract) | <span class="rank rank-rare">知ってるだけ</span> | ノードとして取り外す <span class="ver ver-17">C++17</span> | 平均 O(1) |
| [`merge`](#merge) | <span class="rank rank-rare">知ってるだけ</span> | 別の set から移す <span class="ver ver-17">C++17</span> | 平均 O(m) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | O(1) |
| [`bucket_count`](#bucket_count) | <span class="rank rank-rare">知ってるだけ</span> | バケットの数（[unordered_map 参照](unordered_map.md#bucket_count)） | O(1) |

## よくある使い方

### 1. 取得済みかどうかを覚える

```cpp
#include <print>
#include <string>
#include <unordered_set>

int main() {
  std::unordered_set<std::string> obtained;

  obtained.insert("sword");
  obtained.insert("key");
  obtained.insert("sword");  // 2 回目は無視される

  std::println("数: {}", obtained.size());
  std::println("key を持っている？ {}", obtained.contains("key"));
  std::println("map を持っている？ {}", obtained.contains("map"));

  obtained.erase("key");  // 使ったので消す
  std::println("key を持っている？ {}", obtained.contains("key"));
}
```

```text title="実行結果"
数: 2
key を持っている？ true
map を持っている？ false
key を持っている？ false
```

### 2. 1 フレームに 1 回だけ当たるようにする

攻撃判定が何フレームも続くとき、同じ敵に何度もダメージが入らないようにする定番の使い方です。

```cpp
#include <print>
#include <unordered_set>
#include <vector>

int main() {
  std::unordered_set<int> hit_enemies;  // この攻撃で当たった敵の ID

  // 3 フレームにわたって、毎回 ID 1 と 2 の敵に当たり判定が出たとする
  std::vector<std::vector<int>> frames = {{1}, {1, 2}, {2}};
  for (const auto& overlaps : frames) {
    for (int id : overlaps) {
      // insert の戻り値の second が true なら「初めて入った」
      if (hit_enemies.insert(id).second) {
        std::println("敵 {} にダメージ", id);
      }
    }
  }
}
```

```text title="実行結果"
敵 1 にダメージ
敵 2 にダメージ
```

### 3. 重複を取り除く

```cpp
#include <print>
#include <unordered_set>
#include <vector>

int main() {
  std::vector<int> drops = {3, 1, 3, 2, 1, 3};
  std::unordered_set<int> unique(drops.begin(), drops.end());
  std::println("種類: {}", unique.size());
}
```

```text title="実行結果"
種類: 3
```

## 関数の詳しい説明

### insert {#insert}

```cpp
std::pair<iterator, bool> insert(const value_type& value);
std::pair<iterator, bool> insert(value_type&& value);
void insert(InputIt first, InputIt last);
void insert(std::initializer_list<value_type> ilist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` / `Key&&` | 入れる値 |
| `first`, `last` / `ilist` | 範囲 / `{...}` | まとめて入れる |

- 戻り値: 1 個版は `pair<イテレータ, 新しく入ったか>`
- 計算量: 平均 O(1)

<div class="anim" data-label="s.insert(&quot;C&quot;)">
_ A _ B _ _ # バケット
_ A _ B +C _ # ハッシュで決まった箱に入る
</div>

```cpp
#include <print>
#include <unordered_set>

int main() {
  std::unordered_set<int> visited;
  std::println("{}", visited.insert(5).second);  // 初めて
  std::println("{}", visited.insert(5).second);  // 2 回目
  visited.insert({1, 2, 3});
  std::println("{}", visited.size());
}
```

```text title="実行結果"
true
false
4
```

!!! note "実際は"
    `.second` で「初めて入ったか」が分かるので、`contains` で確認してから `insert` する必要はありません。

### contains <span class="ver ver-20">C++20</span> {#contains data-toc-label="contains"}

```cpp
bool contains(const Key& key) const;
```

- 戻り値: 入っていれば `true`
- 計算量: 平均 O(1)

<div class="anim" data-label="s.contains(&quot;B&quot;)">
_ A _ B _ _ # バケット
_ A _ *B _ _ # あれば true
</div>

```cpp
#include <print>
#include <string>
#include <unordered_set>

int main() {
  std::unordered_set<std::string> tags = {"enemy", "flying"};
  std::println("{} {}", tags.contains("flying"), tags.contains("boss"));
}
```

```text title="実行結果"
true false
```

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
```

- 戻り値: キー版は消した数（0 か 1）。位置版は次の要素のイテレータ
- 計算量: 平均 O(1)

<div class="anim" data-label="s.erase(&quot;B&quot;)">
_ A _ B C _ # バケット
_ A _ xB C _ # 消す
</div>

```cpp
#include <print>
#include <unordered_set>

int main() {
  std::unordered_set<int> pressed = {32, 87};
  std::println("{}", pressed.erase(87));
  std::println("{}", pressed.erase(87));
}
```

```text title="実行結果"
1
0
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

- 空なら `true`。O(1)

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全要素を削除します。O(n)

<div class="anim" data-label="s.clear()">
_ A _ B C _ # バケット
_ xA _ xB xC _ # すべて破棄
_ _ _ _ _ _ # 空
</div>

```cpp
#include <print>
#include <unordered_set>

int main() {
  std::unordered_set<int> hit = {1, 2, 3};
  std::println("{} {}", hit.size(), hit.empty());
  hit.clear();  // 次の攻撃に備えてリセット
  std::println("{} {}", hit.size(), hit.empty());
}
```

```text title="実行結果"
3 false
0 true
```

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 先頭のイテレータ。範囲 for で使われます。**順番はバラバラ**です
- 要素は `const` なので、回しながら書き換えることはできません

### end {#end}

```cpp
iterator end() noexcept;
```

- 終わりのイテレータ。`find` が「見つからない」ときに返します

### find {#find}

```cpp
iterator find(const Key& key);
```

- 戻り値: 見つかった要素のイテレータ。無ければ `end()`

!!! note "実際は"
    set の要素は「キーそのもの」なので、イテレータを取っても `contains` 以上にできることはあまりありません。`erase(it)` で消すときくらいです。

<div class="anim" data-label="s.find(&quot;B&quot;)">
_ A _ B _ _ # バケット
_ A _ *B _ _ # 箱を決めて探す
</div>

### emplace {#emplace}

```cpp
template <class... Args>
std::pair<iterator, bool> emplace(Args&&... args);
```

- 要素のコンストラクタ引数を渡して、その場で作って追加します

<div class="anim" data-label="s.emplace(&quot;C&quot;)">
_ A _ B _ _ # バケット
_ A _ B +C _ # その場で作る。重複なら何もしない
</div>

```cpp
#include <print>
#include <string>
#include <unordered_set>

int main() {
  std::unordered_set<std::string> s;
  s.emplace(3, 'x');  // std::string(3, 'x')
  std::println("{}", s.contains("xxx"));
}
```

```text title="実行結果"
true
```

### reserve {#reserve}

```cpp
void reserve(size_type count);
```

- `count` 個入れても再ハッシュが起きないように準備します（[unordered_map の reserve](unordered_map.md#reserve) と同じ）

### std::erase_if <span class="ver ver-20">C++20</span> {#erase_if data-toc-label="std::erase_if"}

```cpp
template <class K, class H, class P, class A, class Pred>
size_type erase_if(std::unordered_set<K, H, P, A>& c, Pred pred);
```

- 要素を受け取り、`true` を返したものを消します。戻り値は消した数

```cpp
#include <print>
#include <unordered_set>

int main() {
  std::unordered_set<int> ids = {1, 2, 3, 4, 5, 6};
  std::erase_if(ids, [](int id) { return id % 2 == 0; });
  std::println("{}", ids.size());
}
```

```text title="実行結果"
3
```

### count {#count}

```cpp
size_type count(const Key& key) const;
```

- 0 か 1 を返します。今は `contains` を使います

### extract <span class="ver ver-17">C++17</span> {#extract data-toc-label="extract"}

```cpp
node_type extract(const Key& key);
```

- 要素をノードとして取り外します。`node.value()` で値を書き換えて入れ直せます

### merge <span class="ver ver-17">C++17</span> {#merge data-toc-label="merge"}

```cpp
void merge(unordered_set& source);
```

- `source` の要素をこちらへ移します。重複するものは `source` に残ります

```cpp
#include <print>
#include <unordered_set>

int main() {
  std::unordered_set<int> a = {1, 2};
  std::unordered_set<int> b = {2, 3};
  a.merge(b);
  std::println("a: {} 個 / b: {} 個", a.size(), b.size());
}
```

```text title="実行結果"
a: 3 個 / b: 1 個
```

### swap {#swap}

```cpp
void swap(unordered_set& other) noexcept;
```

- 中身を交換します。O(1)

### bucket_count {#bucket_count}

```cpp
size_type bucket_count() const noexcept;
```

- バケットの数です。`load_factor`、`max_load_factor`、`rehash`、`bucket` も unordered_map と同じようにあります（[unordered_map 参照](unordered_map.md#bucket_count)）

## フラグ・オプション

フラグはありません。自作の型を入れるときは `Hash` を指定します（[unordered_map のよくある使い方 4](unordered_map.md#4-自作の型をキーにする) と同じ）。

## 計算量まとめ

| 操作 | 平均 | 最悪 |
| --- | --- | --- |
| `insert`, `contains`, `erase` | O(1) | O(n) |
| 全要素を回す | O(n) | O(n) |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    if (s.find(id) != s.end()) {
    }
    if (s.count(id) > 0) {
    }
    ```

=== "今の書き方"

    ```cpp
    if (s.contains(id)) {
    }
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 取得済み・達成済み | アイテム、実績、開いた宝箱、見たイベント |
| 多段ヒット防止 | 1 回の攻撃で当たった敵 ID |
| 探索 | 経路探索・塗りつぶしで訪問済みのマス |
| 押されているキー | `unordered_set<KeyCode>` |
| タグ | エンティティが持つタグの集まり |

## パフォーマンス

- unordered_map と同じく、要素は別々にヒープ確保されます。
- 値が小さい整数（0〜数千）なら、`std::vector<bool>` や `std::bitset` で「添字 = 値」にしたほうがずっと速いです。
- 要素が数十個までなら、vector に入れて `std::ranges::find` で探すほうが速いことがあります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 要素を `const_cast` で書き換える | 未定義動作（置き場所がずれる） |
| 回しながら `insert` してそのイテレータを使い続ける | 未定義動作 |

## よくあるミス

??? failure "要素を書き換えようとする"
    ```cpp
    for (auto& name : names) {
      name += "!";  // コンパイルエラー: 要素は const
    }
    ```

    値を変えたいなら、消してから入れ直します。

??? failure "順番が保たれると思い込む"
    unordered_set を回すと順番はバラバラです。表示順が大事なら `std::set` か vector を使います。

## 理解度チェック

!!! question "Q1. 何が出力される？"
    ```cpp
    std::unordered_set<int> s = {1, 2, 2, 3, 3, 3};
    std::println("{}", s.size());
    ```

    <div class="spoiler" markdown>

    **答え:** `3`。重複は 1 個にまとまります。

    </div>

!!! question "Q2. 敵 ID が 0〜99 の整数だけ。当たった敵を覚えるのに一番速いのは？"
    <div class="spoiler" markdown>

    **答え:** `std::bitset<100>` か `std::array<bool, 100>`。ID をそのまま添字にできるので、ハッシュ計算もメモリ確保も要りません。

    </div>

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::set`](set.md) | 小さい順に並ぶ。O(log n) | 順番に回したい |
| [`std::unordered_map`](unordered_map.md) | 値も持てる | キーに対応するデータがある |
| [`std::bitset`](bitset.md) | 0〜N-1 の整数専用。とても速い | 値の範囲が小さい整数 |
| [`std::flat_set`](flat_set.md) | ソート済み vector <span class="ver ver-23">C++23</span> | 作ってから変更しない |

## コンパイラ対応

C++11 からある機能です。`contains` / `std::erase_if`（C++20）も主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「あるかどうか」だけ知りたいなら `std::unordered_set`
    - [x] `insert` / `contains` / `erase` の 3 つで足りる
    - [x] `insert(x).second` で「初めて入ったか」が分かる
    - [x] 小さい整数なら bitset のほうが速い

## 関連ページ

- [cpprefjp: std::unordered_set](https://cpprefjp.github.io/reference/unordered_set/unordered_set.html)
- [cppreference: std::unordered_set](https://en.cppreference.com/w/cpp/container/unordered_set)

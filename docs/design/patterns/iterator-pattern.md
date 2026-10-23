---
title: イテレータ（パターン）
tags:
  - 設計
---

# イテレータ（パターン）

**イテレータ**（Iterator）パターンは、「中身の作り（配列か、リストか、木か）を知らなくても、要素を 1 つずつ順番に取り出せるようにする」設計です。C++ では、これが言語に組み込まれています。`std::vector` も `std::map` も `std::list` も、同じ `begin()` / `end()` と範囲 for で回せるのは、イテレータという共通の窓口があるからです。このページでは、標準のイテレータの考え方を、自作のコンテナ・データ構造に使う設計として説明します（イテレータの基本は [イテレータ（基礎）](../../basics/iterator.md)）。

!!! tip "ポイント"
    - 自作のコンテナでも、**`begin()` と `end()` を持たせる**と、範囲 for と標準アルゴリズムが使えるようになる。
    - **中身を公開せず、「回し方」だけを公開する**のがイテレータの役目（カプセル化）。
    - 簡単に済ませるなら、`std::generator`（C++23）や、ranges のビューで「回すもの」を作る。
    - コンテナを作り替えても（`vector` → `list`）、回す側のコードは変えなくてよい。
    - 回している最中に、コンテナの中身を変えない（イテレータが無効になる）。

## 悪い例：中身を公開して、回し方を教える

```cpp
class Inventory {
 public:
  std::vector<Item> items;       // 中身が丸見え
};

// 使う側が、vector であることを前提にしている
for (std::size_t i = 0; i < inventory.items.size(); ++i) {
  Use(inventory.items[i]);
}
```

| 問題 | 説明 |
| --- | --- |
| **中身（`vector`）に依存する** | `map` や `list` に変えると、使う側が全部壊れる |
| 回し方がバラバラ | 添字、イテレータ、範囲 for…とコードごとに違う |
| 条件付きの回し方が、使う側に漏れる | 「使えるアイテムだけ回す」を、毎回 `if` で書く |

## 良い例 1：begin / end を公開する（範囲 for に対応）

```cpp
class Inventory {
 public:
  using iterator = std::vector<Item>::iterator;
  using const_iterator = std::vector<Item>::const_iterator;

  iterator begin() { return items_.begin(); }
  iterator end() { return items_.end(); }
  const_iterator begin() const { return items_.begin(); }
  const_iterator end() const { return items_.end(); }

 private:
  std::vector<Item> items_;     // 中身は、隠したまま
};

for (const Item& item : inventory) {     // 範囲 for が使える
  Use(item);
}
auto it = std::ranges::find_if(inventory, IsUsable);   // 標準アルゴリズムも使える
```

中身を `std::list` に変えても、`using iterator = std::list<Item>::iterator;` を直すだけで、**使う側は変わりません**。

<div class="anim" data-label="イテレータ：中身の作りに関係なく、1 つずつ進む">
*A B C D # begin()：先頭を指す
A *B C D # ++it
A B *C D # ++it
A B C *D # ++it
A B C D # end()：最後の次。ここで終わり（要素はない）
</div>

## 良い例 2：イテレータを自作する

**木**やグリッドのように、標準のコンテナではない構造を回すときは、イテレータを自作します。

```cpp
// 2 次元のマップを、行方向に 1 マスずつ回すイテレータ
class Grid {
 public:
  class Iterator {
   public:
    using iterator_category = std::forward_iterator_tag;
    using value_type = Tile;
    using difference_type = std::ptrdiff_t;
    using pointer = Tile*;
    using reference = Tile&;

    Iterator(Tile* p) : p_(p) {}
    Tile& operator*() const { return *p_; }          // 今の要素
    Tile* operator->() const { return p_; }
    Iterator& operator++() { ++p_; return *this; }    // 次へ
    Iterator operator++(int) { Iterator tmp = *this; ++p_; return tmp; }
    bool operator==(const Iterator&) const = default; // 比べる

   private:
    Tile* p_;
  };

  Iterator begin() { return Iterator(tiles_.data()); }
  Iterator end() { return Iterator(tiles_.data() + tiles_.size()); }

 private:
  std::vector<Tile> tiles_;
};
```

必要な部品は、**`*`（今の要素）、`++`（次へ）、`==`（比べる）、`begin()` / `end()`** です。これだけで、範囲 for と多くのアルゴリズムが使えます。

## 良い例 3：回し方を「部品」にする

「使えるアイテムだけ」「画面内の敵だけ」のような**条件付きの回し方**は、ビュー（ranges）やジェネレーターで作ります。

### ranges のビュー（C++20）

```cpp
// 使えるアイテムだけを回すビューを、返す
auto Inventory::Usable() const {
  return items_ | std::views::filter([](const Item& i) { return i.IsUsable(); });
}

for (const Item& item : inventory.Usable()) {    // 呼ぶ側は、条件を知らなくてよい
  Show(item);
}
```

### std::generator（C++23）

```cpp
#include <generator>

// 木を、深さ優先で 1 つずつ返す（再帰をそのまま書ける）
std::generator<const Node&> Walk(const Node& node) {
  co_yield node;
  for (const Node& child : node.children) {
    co_yield std::ranges::elements_of(Walk(child));   // 子をたどる
  }
}

for (const Node& n : Walk(root)) {
  Process(n);
}
```

イテレータを自作するより、ずっと短く書けます（[std::generator](../../stl/support/generator.md)、[ranges とビュー](../../basics/ranges.md)）。

## 回しているときの注意

| 注意 | 説明 |
| --- | --- |
| **回している最中に、コンテナを変更しない** | `push_back` や `erase` で、イテレータが無効になる（[イテレータの無効化](../../basics/iterator.md)） |
| 消したいなら、`erase_if` か、「消す印」 | ループの中で `erase` しない。[`std::erase_if`](../../stl/algorithms/erase_if.md) を使う |
| `const` のコンテナには、`const_iterator` | 読むだけの回し方を用意する |
| 範囲 for の `auto` は、コピーに注意 | `for (auto x : items)` は 1 つずつコピーする。`const auto&` にする |

## 他のコレクションの回し方

| 回し方 | 説明 | 向いている場面 |
| --- | --- | --- |
| **範囲 for** | 一番シンプル | 全部を順に |
| イテレータ（`begin` / `end`） | 標準アルゴリズムに渡せる | `std::find`、`std::sort` |
| コールバック（`ForEach(func)`） | 中身を見せず、関数を受け取って呼ぶ | 内部の構造を完全に隠したい |
| ビュー・ジェネレーター | 条件付き・加工付きの回し方 | フィルター、変換 |
| 添字ループ | 位置が必要なとき | 隣の要素を使う、逆順 |

```cpp
// コールバック方式：回し方は、持ち主が決める（ロックを取るなどができる）
void Inventory::ForEach(const std::function<void(const Item&)>& func) const {
  std::lock_guard lock(mutex_);
  for (const Item& item : items_) {
    func(item);
  }
}
```

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| インベントリ・パーティ | `begin()` / `end()` で、範囲 for と標準アルゴリズムに対応 |
| タイルマップ・グリッド | 行ごと、マスごと、近傍（上下左右）のイテレータ・ビュー |
| 木構造（シーン グラフ、ビヘイビア ツリー） | `std::generator` や、深さ優先のイテレータ |
| ECS のクエリ | 「Position と Velocity を持つエンティティ」をたどるイテレータ（[ECS](ecs.md)） |
| 画面内の敵だけ | ranges の `filter` ビュー |

## よくあるミス

??? failure "回しながら、そのコンテナに追加・削除する"
    `for (auto& e : enemies) { enemies.push_back(...); }` は、イテレータが無効になって、未定義動作です。追加は、あとでまとめて行います（「追加する予定」のリストに積む）。

??? failure "イテレータを、無効になったあとも持つ"
    `push_back` のあと、前に取った `it` を使うと壊れます。必要なら、添字（番号）や ID で覚えます。

??? failure "自作イテレータに、必要な型名（`using`）がない"
    標準アルゴリズムが、`iterator_category` や `value_type` などの型名を探します。ないと、コンパイル エラーになります。上の例のように書きます（C++20 では、concepts の条件を満たせばよい）。

??? failure "`begin()` と `end()` が、`const` 版を持たない"
    `const Inventory&` から回そうとすると、コンパイルエラーになります。`const` 版も用意します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータ ＝ 中身の作りを隠して、1 つずつ順に取り出す窓口
    - [x] 自作のコンテナにも `begin()` / `end()`（`const` 版も）を付けると、範囲 for とアルゴリズムが使える
    - [x] 条件付きの回し方は、ranges のビューや `std::generator` で作る
    - [x] 回している最中に、そのコンテナを変更しない
    - [x] 中身（`vector`）を public にせず、回し方だけ公開する

## 関連ページ

- [イテレータ（基礎）](../../basics/iterator.md)
- [範囲 for（基礎）](../../basics/range-for.md)
- [ranges とビュー](../../basics/ranges.md)
- [std::generator](../../stl/support/generator.md)
- [ECS](ecs.md)

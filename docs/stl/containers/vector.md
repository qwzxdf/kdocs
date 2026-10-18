---
title: std::vector
tags:
  - コンテナ
---

# std::vector

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++98〜</span>
`#include <vector>`
</div>

`std::vector` は、**あとから要素を増やしたり減らしたりできる配列**です。中身はメモリ上にすき間なく並んでいるので、C の配列と同じ速さで読み書きできます。入りきらなくなったら自動で大きい場所に引っ越してくれるので、最初に個数を決めなくても使えます。

!!! tip "ポイント"
    - <strong>迷ったらこれを使う。</strong> ゲームで使うコンテナの大半は vector で足ります。
    - 9 割は `push_back` / `emplace_back` で足して、範囲 for で回して、`std::erase_if` で消す。この 3 つで足ります。
    - 個数が分かっているなら最初に `reserve`。
    - **要素を追加すると、持っていたポインタ・参照・イテレータが壊れることがある**。ここだけは必ず覚えておく。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md)（`<int>` の意味）、[参照](../../basics/reference.md)、[範囲 for](../../basics/range-for.md)、[ラムダ式](../../basics/lambda.md) が分かると読みやすいです。

## 宣言

```cpp
template <class T, class Allocator = std::allocator<T>>
class vector;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 必ず |
| `Allocator` | メモリの確保方法（[アロケータの解説](../memory/allocator.md)） | **しない**。自作アロケータや [`std::pmr`](../memory/pmr.md) を使うときだけ |

### コンストラクタ

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |
| `std::vector<int> v;` | <span class="rank rank-must">必須</span> | 空 |
| `std::vector<int> v = {1, 2, 3};` | <span class="rank rank-must">必須</span> | `1, 2, 3` |
| `std::vector<int> v(n);` | <span class="rank rank-often">よく使う</span> | `0` が n 個（`T` のデフォルト値） |
| `std::vector<int> v(n, value);` | <span class="rank rank-often">よく使う</span> | `value` が n 個 |
| `std::vector<int> v(first, last);` | <span class="rank rank-sometimes">たまに</span> | イテレータ範囲のコピー |
| `std::vector<int> v(std::from_range, r);` | <span class="rank rank-sometimes">たまに</span> | range `r` のコピー <span class="ver ver-23">C++23</span> |
| `std::vector<int> v(other);` | <span class="rank rank-sometimes">たまに</span> | `other` のコピー |
| `std::vector<int> v(std::move(other));` | <span class="rank rank-sometimes">たまに</span> | `other` の中身を移す（`other` は空になる） |

!!! warning "`()` と `{}` で意味が変わる"
    **個数を指定するときは `()`、中身を書くときは `{}`** と覚えておきます。

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> a(5);     // 0 が 5 個
  std::vector<int> b{5};     // 5 が 1 個
  std::vector<int> c(5, 1);  // 1 が 5 個
  std::vector<int> d{5, 1};  // 5 と 1 の 2 個

  std::println("a = {}", a);
  std::println("b = {}", b);
  std::println("c = {}", c);
  std::println("d = {}", d);
}
```

```text title="実行結果"
a = [0, 0, 0, 0, 0]
b = [5]
c = [1, 1, 1, 1, 1]
d = [5, 1]
```

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`push_back`](#push_back) | <span class="rank rank-must">必須</span> | 末尾に追加 | 償却 O(1) |
| [`size`](#size) | <span class="rank rank-must">必須</span> | 要素数 | O(1) |
| [`operator[]`](#operator) | <span class="rank rank-must">必須</span> | i 番目にアクセス（範囲チェックなし） | O(1) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | 先頭のイテレータ | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 最後の次のイテレータ | O(1) |
| [`emplace_back`](#emplace_back) | <span class="rank rank-must">必須</span> | 末尾にその場で構築して追加 | 償却 O(1) |
| [`std::erase_if`](#erase_if) | <span class="rank rank-must">必須</span> | 条件に合う要素をすべて削除 | O(n) |
| [`empty`](#empty) | <span class="rank rank-must">必須</span> | 空かどうか | O(1) |
| [`clear`](#clear) | <span class="rank rank-must">必須</span> | 全削除 | O(n) |
| [`reserve`](#reserve) | <span class="rank rank-often">よく使う</span> | 容量を先に確保 | O(n) |
| [`back`](#back) | <span class="rank rank-often">よく使う</span> | 末尾の要素 | O(1) |
| [`front`](#front) | <span class="rank rank-often">よく使う</span> | 先頭の要素 | O(1) |
| [`pop_back`](#pop_back) | <span class="rank rank-often">よく使う</span> | 末尾を削除 | O(1) |
| [`resize`](#resize) | <span class="rank rank-often">よく使う</span> | 要素数を変える | O(n) |
| [`erase`](#erase) | <span class="rank rank-often">よく使う</span> | 位置を指定して削除 | O(n) |
| [`insert`](#insert) | <span class="rank rank-sometimes">たまに</span> | 位置を指定して挿入 | O(n) |
| [`at`](#at) | <span class="rank rank-sometimes">たまに</span> | i 番目にアクセス（範囲チェックあり） | O(1) |
| [`data`](#data) | <span class="rank rank-sometimes">たまに</span> | 先頭のポインタ（グラフィック API に渡す） | O(1) |
| [`append_range`](#append_range) | <span class="rank rank-sometimes">たまに</span> | 範囲をまとめて末尾に追加 <span class="ver ver-23">C++23</span> | O(m) |
| [`std::erase`](#std-erase) | <span class="rank rank-sometimes">たまに</span> | 指定した値をすべて削除 | O(n) |
| [`assign`](#assign) | <span class="rank rank-sometimes">たまに</span> | 中身を丸ごと入れ替え | O(n) |
| [`capacity`](#capacity) | <span class="rank rank-sometimes">たまに</span> | 確保済みの容量 | O(1) |
| [`swap`](#swap) | <span class="rank rank-sometimes">たまに</span> | 2 つの vector の中身を交換 | O(1) |
| [`emplace`](#emplace) | <span class="rank rank-rare">知ってるだけ</span> | 位置を指定してその場で構築 | O(n) |
| [`insert_range`](#insert_range) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を位置指定で挿入 <span class="ver ver-23">C++23</span> | O(n + m) |
| [`assign_range`](#assign_range) | <span class="rank rank-rare">知ってるだけ</span> | 範囲で中身を入れ替え <span class="ver ver-23">C++23</span> | O(n + m) |
| [`shrink_to_fit`](#shrink_to_fit) | <span class="rank rank-rare">知ってるだけ</span> | 余った容量を返す（お願いするだけ） | O(n) |
| [`rbegin`](#rbegin) | <span class="rank rank-rare">知ってるだけ</span> | 逆順の先頭イテレータ | O(1) |
| [`rend`](#rend) | <span class="rank rank-rare">知ってるだけ</span> | 逆順の終わりイテレータ | O(1) |
| [`cbegin`](#cbegin) | <span class="rank rank-rare">知ってるだけ</span> | const の先頭イテレータ | O(1) |
| [`cend`](#cend) | <span class="rank rank-rare">知ってるだけ</span> | const の終わりイテレータ | O(1) |
| [`max_size`](#max_size) | <span class="rank rank-rare">知ってるだけ</span> | 理論上の最大要素数 | O(1) |
| [`get_allocator`](#get_allocator) | <span class="rank rank-rare">知ってるだけ</span> | アロケータを取得 | O(1) |

## よくある使い方

上の関数を実際にどう組み合わせるかの例です。

### 1. 作って、足して、回す

```cpp
#include <print>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  std::vector<Enemy> enemies;

  // 要素を作って末尾に追加する。コンストラクタ引数を直接渡せる
  enemies.emplace_back("スライム", 10);
  enemies.push_back({"ゴブリン", 25});

  // 書き換えるなら auto&
  for (auto& enemy : enemies) {
    enemy.hp -= 5;
  }

  // 読むだけなら const auto&
  for (const auto& enemy : enemies) {
    std::println("{}: HP {}", enemy.name, enemy.hp);
  }
}
```

```text title="実行結果"
スライム: HP 5
ゴブリン: HP 20
```

### 2. 条件に合うものをまとめて消す

```cpp
#include <print>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {
      {"スライム", 0}, {"ゴブリン", 25}, {"コウモリ", -3}, {"ドラゴン", 300}};

  // HP が 0 以下の敵を全部消す。消した数が返る
  std::size_t removed =
      std::erase_if(enemies, [](const Enemy& e) { return e.hp <= 0; });

  std::println("{} 体消えた", removed);
  for (const auto& enemy : enemies) {
    std::println("{}: HP {}", enemy.name, enemy.hp);
  }
}
```

```text title="実行結果"
2 体消えた
ゴブリン: HP 25
ドラゴン: HP 300
```

ループの中で 1 個ずつ `erase` するより、**これ 1 行のほうが安全で速い**です。

### 3. 最初から個数が決まっている

```cpp
#include <print>
#include <vector>

struct Bullet {
  float x;
  float y;
};

int main() {
  // 100 個分の場所だけ先に確保する（size は 0 のまま）
  std::vector<Bullet> bullets;
  bullets.reserve(100);

  // 10 個を 0 で埋めて作る（size は 10）
  std::vector<int> scores(10, 0);

  // 中身を直接書いて作る
  std::vector<int> stage_ids = {1, 2, 3, 5, 8};

  std::println("bullets: size {} / capacity {}", bullets.size(),
               bullets.capacity());
  std::println("scores: size {}", scores.size());
  std::println("stage_ids: {}", stage_ids);
}
```

```text title="実行結果"
bullets: size 0 / capacity 100
scores: size 10
stage_ids: [1, 2, 3, 5, 8]
```

### 4. 関数に渡す

```cpp
#include <print>
#include <span>
#include <string>
#include <vector>

struct Sprite {
  std::string name;
};

struct Enemy {
  int hp;
};

// 読むだけ: const 参照で受ける（コピーされない）
void PrintNames(const std::vector<Sprite>& sprites) {
  for (const auto& sprite : sprites) {
    std::println("{}", sprite.name);
  }
}

// 中身を書き換える: 参照で受ける
void DamageAll(std::vector<Enemy>& enemies, int damage) {
  for (auto& enemy : enemies) {
    enemy.hp -= damage;
  }
}

// vector 以外の配列も受けたい: std::span で受ける（C++20）
int Sum(std::span<const int> values) {
  int total = 0;
  for (int value : values) {
    total += value;
  }
  return total;
}

int main() {
  std::vector<Sprite> sprites = {{"player"}, {"enemy"}};
  PrintNames(sprites);

  std::vector<Enemy> enemies = {{30}, {50}};
  DamageAll(enemies, 10);
  std::println("{} {}", enemies[0].hp, enemies[1].hp);

  std::vector<int> scores = {10, 20, 30};
  int bonus[] = {1, 2, 3};
  std::println("{} {}", Sum(scores), Sum(bonus));
}
```

```text title="実行結果"
player
enemy
20 40
60 6
```

## 関数の詳しい説明

### push_back {#push_back}

```cpp
void push_back(const T& value);
void push_back(T&& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` / `T&&` | 追加する値。左辺値ならコピー、右辺値（`std::move` や一時オブジェクト）ならムーブされる |

- 戻り値: なし
- 計算量: 償却 O(1)。容量が足りないときだけ再確保が起きて O(n)
- 例外: メモリ確保に失敗すると `std::bad_alloc`

<div class="anim" data-label="v.push_back(40)  ※空きがあるとき">
10 20 30 _ _ # v = {10, 20, 30}　size 3 / capacity 5
10 20 30 +40 _ # 空いている場所に 40 を置く
10 20 30 40 _ # size 4 / capacity 5。空きがあるので引っ越しは起きない
</div>

<div class="anim" data-label="v.push_back(50)  ※満杯のとき（引っ越し）">
10 20 30 40 # size 4 / capacity 4。もう空きがない
10 20 30 40 | _ _ _ _ # ① 2 倍の大きさの新しい場所を確保する
x10 x20 x30 x40 | >10 >20 >30 >40 _ _ _ _ # ② 要素を全部ムーブする
x10 x20 x30 x40 | 10 20 30 40 +50 _ _ _ # ③ 新しい場所に 50 を追加する
| 10 20 30 40 50 _ _ _ # ④ 古い場所を解放。元を指していたイテレータ・参照は壊れる
</div>

```cpp
#include <print>
#include <string>
#include <utility>
#include <vector>

int main() {
  std::vector<std::string> names;
  std::string player = "Alice";

  names.push_back(player);  // コピー。player はそのまま残る
  std::println("player = {}", player);

  names.push_back(std::move(player));  // ムーブ。player の中身は移される
  names.push_back("Bob");              // 一時オブジェクトなのでムーブ

  std::println("{}", names);
}
```

```text title="実行結果"
player = Alice
["Alice", "Alice", "Bob"]
```

!!! note "実際は"
    すでにある値を入れるなら `push_back`、その場で作るなら `emplace_back` と使い分ければ十分です。迷ったら `push_back` で問題ありません。

### size {#size}

```cpp
size_type size() const noexcept;
```

- 戻り値: 要素数。型は `std::size_t`（**符号なし**）
- 計算量: O(1)

```cpp
#include <cstddef>
#include <print>
#include <vector>

int main() {
  std::vector<int> hp = {30, 50, 80};
  std::println("size = {}", hp.size());

  for (std::size_t i = 0; i < hp.size(); ++i) {
    std::println("hp[{}] = {}", i, hp[i]);
  }

  // 符号付きで欲しいときは std::ssize（C++20）。後ろから回すときに便利
  for (std::ptrdiff_t i = std::ssize(hp) - 1; i >= 0; --i) {
    std::println("後ろから {}", hp[i]);
  }
}
```

```text title="実行結果"
size = 3
hp[0] = 30
hp[1] = 50
hp[2] = 80
後ろから 80
後ろから 50
後ろから 30
```

!!! warning "符号なしの落とし穴"
    `hp.size() - 1` は空のとき **-1 ではなく巨大な数** になります。[よくあるミス](#よくあるミス) を参照してください。

### operator[] {#operator}

```cpp
reference operator[](size_type pos);
const_reference operator[](size_type pos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 0 始まりの位置 |

- 戻り値: `pos` 番目の要素の参照
- 計算量: O(1)
- 例外: なし。**範囲外は未定義動作**（チェックしない）

<div class="anim" data-label="v[2]">
10 20 30 40 # 添字は 0 から数える
10 20 *30 40 # v[2] は 30。範囲のチェックはしない（範囲外は未定義動作）
</div>

```cpp
std::vector<int> map_tiles(16 * 9, 0);
map_tiles[3] = 1;
int tile = map_tiles[3];
```

!!! note "実際は"
    範囲チェック付きの [`at`](#at) より `[]` を使うのが普通です。範囲外は Debug ビルドならたいていアサートで止まってくれます。

### begin {#begin}

```cpp
iterator begin() noexcept;
const_iterator begin() const noexcept;
```

- 戻り値: 先頭の要素を指すイテレータ。空なら `end()` と同じ
- 計算量: O(1)

<div class="mem">
<div class="mem-step"><span class="mem-label">v = {10, 20, 30}</span><span class="mem-cells"><span class="move">10</span><span>20</span><span>30</span><span class="free">　</span></span></div>
<div class="mem-step"><span class="mem-label"></span><span class="mem-note">↑ begin() は先頭の 10 を指す</span></div>
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};
  auto it = v.begin();
  std::println("{}", *it);  // イテレータが指す要素は * で取り出す

  ++it;  // 次の要素へ進む
  std::println("{}", *it);

  *v.begin() = 99;  // 書き換えもできる
  std::println("{}", v);
}
```

```text title="実行結果"
10
20
[99, 20, 30]
```

!!! note "実際は"
    C++20 以降、`begin()` を自分で書く場面はかなり減りました。範囲 for と `std::ranges::` のアルゴリズムが中で使ってくれます。今でも書くのは「先頭から n 番目の位置」を指定するとき（`v.begin() + n`）くらいです。

### end {#end}

```cpp
iterator end() noexcept;
const_iterator end() const noexcept;
```

- 戻り値: **最後の要素の次**を指すイテレータ。ここには要素が無い
- 計算量: O(1)

<div class="mem">
<div class="mem-step"><span class="mem-label">v = {10, 20, 30}</span><span class="mem-cells"><span>10</span><span>20</span><span>30</span><span class="gone">　</span></span></div>
<div class="mem-step"><span class="mem-label"></span><span class="mem-note">end() は最後の 30 の<strong>次</strong>を指す。中身は無いので * で読むと未定義動作</span></div>
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};

  // 「見つからなかった」は end() で表される
  auto it = std::ranges::find(v, 50);
  std::println("見つかった？ {}", it != v.end());

  // 最後の要素は end() の 1 つ前
  std::println("最後: {}", *(v.end() - 1));
}
```

```text title="実行結果"
見つかった？ false
最後: 30
```

!!! note "実際は"
    `end()` は主に「見つからなかった」の判定に使います。最後の要素が欲しいなら [`back()`](#back) のほうが分かりやすいです。

### emplace_back {#emplace_back}

```cpp
template <class... Args>
reference emplace_back(Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 何個でも | `T` のコンストラクタにそのまま渡す引数 |

- 戻り値: 追加した要素の参照（C++17〜）
- 計算量: 償却 O(1)
- 例外: `push_back` と同じ

<div class="anim" data-label="v.emplace_back(30)">
10 20 _ _ # v = {10, 20}
10 20 +30 _ # 空いている場所で、その場で 30 を作る（コピー・ムーブなし）
</div>

```cpp
#include <print>
#include <vector>

struct Particle {
  Particle(float x, float y, float life) : x(x), y(y), life(life) {}
  float x;
  float y;
  float life;
};

int main() {
  std::vector<Particle> particles;

  // Particle のコンストラクタ引数を直接渡す
  particles.emplace_back(100.0f, 200.0f, 1.5f);

  // 追加した要素の参照が返るので、そのまま触れる
  Particle& p = particles.emplace_back(0.0f, 0.0f, 3.0f);
  p.life *= 2.0f;

  for (const auto& particle : particles) {
    std::println("({}, {}) life {}", particle.x, particle.y, particle.life);
  }
}
```

```text title="実行結果"
(100, 200) life 1.5
(0, 0) life 6
```

!!! note "実際は"
    `push_back({...})` と速さはほとんど変わりません。「コンストラクタ引数を並べて書けて楽」くらいの理由で使えば OK です。

    ただし `emplace_back` は `explicit` コンストラクタも呼べてしまうので、`std::vector<std::unique_ptr<T>>` に生ポインタを渡すようなミスがコンパイルを通ります。

### std::erase_if <span class="ver ver-20">C++20</span> {#erase_if data-toc-label="std::erase_if"}

```cpp
template <class T, class Alloc, class Pred>
size_type erase_if(std::vector<T, Alloc>& c, Pred pred);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `std::vector&` | 対象の vector |
| `pred` | 関数・ラムダ | 要素を 1 つ受け取り、`true` を返したら消す |

- 戻り値: 消した要素の数
- 計算量: O(n)
- 残った要素の順番はそのまま保たれる

<div class="mem">
<div class="mem-step"><span class="mem-label">前</span><span class="mem-cells"><span>A</span><span class="gone">×</span><span>C</span><span class="gone">×</span><span>E</span></span><span class="mem-note">× が消したい要素</span></div>
<div class="mem-step"><span class="mem-label">後</span><span class="mem-cells"><span>A</span><span class="move">C</span><span class="move">E</span><span class="free">　</span><span class="free">　</span></span><span class="mem-note">残すものを前に詰めて、後ろを切り捨てる。1 回なめるだけで終わる</span></div>
</div>

```cpp
#include <print>
#include <vector>

struct Bullet {
  float y;
};

int main() {
  std::vector<Bullet> bullets = {{120.0f}, {-5.0f}, {30.0f}, {-1.0f}};

  // 画面外に出た弾を消して、消した数を使う
  std::size_t removed =
      std::erase_if(bullets, [](const Bullet& b) { return b.y < 0.0f; });
  std::println("消えた弾: {} / 残り: {}", removed, bullets.size());
}
```

```text title="実行結果"
消えた弾: 2 / 残り: 2
```

!!! note "実際は"
    <strong>vector から要素を消すときの第一候補です。</strong> メンバ関数ではなく `std::` の関数なので注意してください（`enemies.erase_if(...)` ではありません）。

### empty {#empty}

```cpp
[[nodiscard]] bool empty() const noexcept;
```

- 戻り値: 要素が 0 個なら `true`
- 計算量: O(1)

```cpp
if (!enemies.empty()) {
  Enemy& boss = enemies.back();
}
```

!!! warning "`clear` と間違えない"
    `enemies.empty();` は **空にする関数ではありません**。空かどうかを調べるだけです。`[[nodiscard]]` が付いているので、戻り値を使わないと警告が出ます。

### clear {#clear}

```cpp
void clear() noexcept;
```

- 戻り値: なし
- 計算量: O(n)（各要素のデストラクタを呼ぶため）
- **容量（`capacity`）はそのまま**。メモリは返されない

<div class="anim" data-label="v.clear()">
10 20 30 40 _ # size 4 / capacity 5
x10 x20 x30 x40 _ # ① すべての要素を破棄する
_ _ _ _ _ # size 0。capacity は 5 のまま（メモリは返さない）
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> enemies = {1, 2, 3, 4, 5};
  enemies.clear();
  std::println("size {} / capacity {}", enemies.size(), enemies.capacity());
}
```

```text title="実行結果"
size 0 / capacity 5
```

!!! note "実際は"
    容量が残るのはむしろ好都合です。次のステージで同じくらい敵を追加しても再確保が起きません。毎フレーム `clear` して詰め直す使い方は速いです。

### reserve {#reserve}

```cpp
void reserve(size_type new_cap);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `new_cap` | `size_type` | 最低限確保したい要素数 |

- 戻り値: なし
- 計算量: 再確保が起きれば O(n)、`new_cap <= capacity()` なら何もしない
- 例外: `new_cap > max_size()` なら `std::length_error`
- **`size` は変わらない**。場所を取るだけ

<div class="anim" data-label="v.reserve(5)">
10 20 30 # size 3 / capacity 3
10 20 30 _ _ # capacity だけが 5 に増える。size と中身は変わらない
</div>

```cpp
#include <cstddef>
#include <print>
#include <vector>

int main() {
  // reserve なしで 20 個足すと、何回も引っ越しが起きる
  std::vector<int> a;
  std::size_t last = a.capacity();
  for (int i = 0; i < 20; ++i) {
    a.push_back(i);
    if (a.capacity() != last) {
      last = a.capacity();
      std::println("再確保: capacity {}", last);
    }
  }

  // reserve しておけば引っ越しは起きない
  std::vector<int> b;
  b.reserve(20);
  std::println("reserve 後: size {} / capacity {}", b.size(), b.capacity());
}
```

```text title="実行結果（GCC / Clang）"
再確保: capacity 1
再確保: capacity 2
再確保: capacity 4
再確保: capacity 8
再確保: capacity 16
再確保: capacity 32
reserve 後: size 0 / capacity 20
```

MSVC は 1.5 倍ずつ増えるので `1, 2, 3, 4, 6, 9, 13, 19, 28` になります。どちらにしても**20 個足すだけで 6〜9 回引っ越している**のがポイントです。

!!! note "実際は"
    最大数がだいたい分かっているなら、ゲーム開始時やステージ読み込み時に `reserve` しておくのが定番です。再確保が減るうえ、**ポインタが壊れるタイミングも減ります**。

### back {#back}

```cpp
reference back();
const_reference back() const;
```

- 戻り値: 最後の要素の参照
- 計算量: O(1)
- **空のときに呼ぶと未定義動作**

<div class="anim" data-label="v.back()">
10 20 30 # v = {10, 20, 30}
10 20 *30 # back() は最後の要素（30）への参照
</div>

```cpp
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> history = {"移動", "攻撃"};
  history.push_back("防御");

  // 直前に追加したものを見る
  if (!history.empty()) {
    std::println("最後の行動: {}", history.back());
  }
}
```

```text title="実行結果"
最後の行動: 防御
```

!!! note "実際は"
    「直前に追加したもの」「スタックの一番上」を見るのに使います。`v[v.size() - 1]` と書くより安全で読みやすいです。

### front {#front}

```cpp
reference front();
const_reference front() const;
```

- 戻り値: 最初の要素の参照
- 計算量: O(1)
- **空のときに呼ぶと未定義動作**

<div class="anim" data-label="v.front()">
10 20 30 # v = {10, 20, 30}
*10 20 30 # front() は先頭の要素（10）への参照
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {70, 100, 40};
  std::ranges::sort(scores);
  std::println("最低点: {}", scores.front());
}
```

```text title="実行結果"
最低点: 40
```

!!! note "実際は"
    `v[0]` と同じです。並べ替えたあとの「一番小さいもの」を取るときなどに、意図がはっきりするので使います。

### pop_back {#pop_back}

```cpp
void pop_back();
```

- 戻り値: **なし**（取り出した値は返ってこない）
- 計算量: O(1)
- **空のときに呼ぶと未定義動作**

<div class="anim" data-label="v.pop_back()">
10 20 30 40 _ # v = {10, 20, 30, 40}
10 20 30 x40 _ # 最後の要素を破棄する
10 20 30 _ _ # size 3。capacity は 5 のまま（メモリは返さない）
</div>

```cpp
#include <print>
#include <string>
#include <utility>
#include <vector>

int main() {
  std::vector<std::string> history = {"移動", "攻撃", "防御"};

  // 値が欲しいなら先に back() で取ってから消す
  std::string last = std::move(history.back());
  history.pop_back();

  std::println("取り消し: {}", last);
  std::println("残り: {}", history);
}
```

```text title="実行結果"
取り消し: 防御
残り: ["移動", "攻撃"]
```

### resize {#resize}

```cpp
void resize(size_type count);
void resize(size_type count, const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | `size_type` | 新しい要素数 |
| `value` | `const T&` | 増えた分を埋める値（省略するとデフォルト値） |

- 戻り値: なし
- 計算量: O(|count - size()|)、再確保が起きれば O(n)
- 増やすと末尾に追加、減らすと末尾から削除

<div class="anim" data-label="v.resize(5) → v.resize(2)">
10 20 30 # size 3
10 20 30 +0 +0 # resize(5)：足りない分を 0 で作る
10 20 x30 x0 x0 # resize(2)：はみ出す分を破棄する
10 20 _ _ _ # size 2。capacity は減らない
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};

  v.resize(5);  // 増えた分は 0
  std::println("{}", v);

  v.resize(7, 9);  // 増えた分は 9
  std::println("{}", v);

  v.resize(2);  // 先頭 2 個だけ残る
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3, 0, 0]
[1, 2, 3, 0, 0, 9, 9]
[1, 2]
```

!!! note "`reserve` との違い"
    | | `size` | 中身に `[]` でアクセスできる？ |
    | --- | --- | --- |
    | `reserve(10)` | 変わらない | **できない**（未定義動作） |
    | `resize(10)` | 10 になる | できる |

### erase {#erase}

```cpp
iterator erase(const_iterator pos);
iterator erase(const_iterator first, const_iterator last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `const_iterator` | 消す要素の位置 |
| `first`, `last` | `const_iterator` | 消す範囲 `[first, last)` |

- 戻り値: 消した要素の **次** を指すイテレータ
- 計算量: O(n)（後ろの要素を前に詰めるため）
- 消した位置より後ろのイテレータ・参照は無効になる

<div class="anim" data-label="v.erase(v.begin() + 1)">
10 20 30 40 # v = {10, 20, 30, 40}
10 x20 30 40 # ① 消す要素を破棄する
10 >30 >40 _ # ② 後ろを 1 つずつ前へ詰める。要素が多いほど重い
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30, 40, 50, 60};

  // 2 番目（添字 1）を消す
  v.erase(v.begin() + 1);
  std::println("{}", v);

  // 先頭から 2 個消す
  v.erase(v.begin(), v.begin() + 2);
  std::println("{}", v);
}
```

```text title="実行結果"
[10, 30, 40, 50, 60]
[40, 50, 60]
```

!!! note "実際は"
    条件で消すなら [`std::erase_if`](#erase_if) を使い、`erase` は「何番目を消す」が決まっているときだけ使います。順番がどうでもいいなら [swap して pop_back](#ゲームでの使いどころ) のほうが速いです。

### insert {#insert}

```cpp
iterator insert(const_iterator pos, const T& value);
iterator insert(const_iterator pos, T&& value);
iterator insert(const_iterator pos, size_type count, const T& value);
iterator insert(const_iterator pos, InputIt first, InputIt last);
iterator insert(const_iterator pos, std::initializer_list<T> ilist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `const_iterator` | この位置の **前** に挿入する |
| `value` | `const T&` / `T&&` | 挿入する値 |
| `count` | `size_type` | 同じ値を何個入れるか |
| `first`, `last` | イテレータ | 挿入する範囲 |
| `ilist` | `{...}` | 挿入する値のリスト |

- 戻り値: 挿入した最初の要素を指すイテレータ
- 計算量: O(n)（後ろをずらすため）。末尾近くなら軽い
- 再確保が起きると全部、起きなくても `pos` 以降のイテレータ・参照が無効になる

<div class="anim" data-label="v.insert(v.begin() + 1, 99)">
10 20 30 40 _ # v = {10, 20, 30, 40}
10 _ >20 >30 >40 # ① 挿入位置より後ろを 1 つずつ後ろへずらす
10 +99 20 30 40 # ② あいた場所に 99 を入れる。後ろが多いほど重い
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> ranking = {80, 60};

  // 先頭に追加
  ranking.insert(ranking.begin(), 100);
  std::println("{}", ranking);

  // 添字 2 の前にまとめて追加
  ranking.insert(ranking.begin() + 2, {75, 70});
  std::println("{}", ranking);

  // 末尾に 0 を 2 個追加
  ranking.insert(ranking.end(), 2, 0);
  std::println("{}", ranking);
}
```

```text title="実行結果"
[100, 80, 60]
[100, 80, 75, 70, 60]
[100, 80, 75, 70, 60, 0, 0]
```

!!! note "実際は"
    先頭や途中への挿入が頻繁なら、vector の使い方を見直すサインです。ソート済みを保ちたいなら「末尾に足して最後に `sort`」でたいてい足ります。

### at {#at}

```cpp
reference at(size_type pos);
const_reference at(size_type pos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `size_type` | 0 始まりの位置 |

- 戻り値: `pos` 番目の要素の参照
- 計算量: O(1)
- 例外: 範囲外なら `std::out_of_range`

<div class="anim" data-label="v.at(10)">
10 20 30 40 # size 4
10 20 30 40 # 添字 10 は範囲外 → std::out_of_range を投げる
</div>

```cpp
try {
  const Item& item = inventory.at(slot);
} catch (const std::out_of_range& e) {
  // 範囲外
}
```

!!! note "実際は"
    ゲームでは例外を使わない（無効にしている）プロジェクトが多いので、あまり使いません。外部データ（セーブデータなど）由来の添字で、どうしても安全にしたいときくらいです。普通は `if (slot < inventory.size())` で確認してから `[]` を使います。

### data {#data}

```cpp
T* data() noexcept;
const T* data() const noexcept;
```

- 戻り値: 先頭要素へのポインタ。空のときは参照してはいけない
- 計算量: O(1)

```cpp
// 頂点データをそのまま GPU に送る（DirectX / OpenGL などの API はポインタとバイト数を要求する）
std::vector<Vertex> vertices = BuildMesh();
UploadVertexBuffer(vertices.data(), vertices.size() * sizeof(Vertex));
```

!!! note "実際は"
    vector の中身は**メモリ上で必ず連続している**ので、C の配列を受け取る API にそのまま渡せます。これが vector の大きな強みです。

### append_range <span class="ver ver-23">C++23</span> {#append_range data-toc-label="append_range"}

```cpp
template <container-compatible-range<T> R>
void append_range(R&& rg);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `rg` | range | 末尾に追加する範囲（vector、配列、`std::views` など） |

- 戻り値: なし
- 計算量: O(m)（m は追加する数）
- 必要な分を 1 回で確保するので、`push_back` を繰り返すより速い

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> enemy_hp = {1, 2};
  std::vector<int> wave2 = {10, 60, 80, 30};

  // 別の vector を末尾に全部つなげる
  enemy_hp.append_range(wave2);
  std::println("{}", enemy_hp);

  // views と組み合わせて、条件に合うものだけ追加する
  enemy_hp.append_range(wave2 | std::views::filter([](int hp) {
                          return hp > 50;
                        }));
  std::println("{}", enemy_hp);
}
```

```text title="実行結果"
[1, 2, 10, 60, 80, 30]
[1, 2, 10, 60, 80, 30, 60, 80]
```

!!! note "実際は"
    「vector をつなげる」はこれで書くのが一番短いです。古いコードの `v.insert(v.end(), other.begin(), other.end())` と同じ意味です。

### std::erase <span class="ver ver-20">C++20</span> {#std-erase data-toc-label="std::erase"}

```cpp
template <class T, class Alloc, class U = T>
size_type erase(std::vector<T, Alloc>& c, const U& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `std::vector&` | 対象の vector |
| `value` | `const U&` | この値と `==` で等しい要素をすべて消す |

- 戻り値: 消した要素の数
- 計算量: O(n)

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {0, 10, 0, 20, 0};
  std::size_t removed = std::erase(scores, 0);
  std::println("{} 個消した: {}", removed, scores);
}
```

```text title="実行結果"
3 個消した: [10, 20]
```

!!! note "実際は"
    メンバ関数の [`erase`](#erase)（位置で消す）とは別物です。「値で消す」なら `std::erase`、「条件で消す」なら [`std::erase_if`](#erase_if) です。

### assign {#assign}

```cpp
void assign(size_type count, const T& value);
void assign(InputIt first, InputIt last);
void assign(std::initializer_list<T> ilist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count`, `value` | | `value` を `count` 個にする |
| `first`, `last` | イテレータ | 範囲のコピーにする |
| `ilist` | `{...}` | 書いた値にする |

- 計算量: O(n)

<div class="anim" data-label="v.assign(3, 7)">
1 2 3 4 # v = {1, 2, 3, 4}
x1 x2 x3 x4 # ① 今ある中身を破棄する
+7 +7 +7 _ # ② 7 を 3 個で作り直す。capacity は足りていれば再利用
</div>

```cpp
tiles.assign(16 * 9, 0);  // 全部 0 で初期化し直す
```

!!! note "実際は"
    `tiles = std::vector<int>(16 * 9, 0);` と書いても同じです。容量を使い回したいときに `assign` を使う程度です。

### capacity {#capacity}

```cpp
size_type capacity() const noexcept;
```

- 戻り値: 再確保せずに入る要素数。常に `size() <= capacity()`
- 計算量: O(1)

<div class="mem">
<div class="mem-step"><span class="mem-label">v = {10, 20, 30}<br>v.reserve(6)</span><span class="mem-cells"><span>10</span><span>20</span><span>30</span><span class="free">　</span><span class="free">　</span><span class="free">　</span></span><span class="mem-note">size = 3 / capacity = 6</span></div>
<div class="mem-legend"><span><span class="mem-cells"><span>　</span></span>使っている（size）</span><span><span class="mem-cells"><span class="free">　</span></span>確保済みだが空き（capacity − size）</span></div>
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};
  v.reserve(6);
  std::println("size {} / capacity {}", v.size(), v.capacity());
}
```

```text title="実行結果"
size 3 / capacity 6
```

!!! note "実際は"
    デバッグ表示で「再確保が起きているか」を確認するくらいにしか使いません。容量の増え方は [`reserve`](#reserve) の実行例を見てください。

### swap {#swap}

```cpp
void swap(vector& other) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `other` | `vector&` | 中身を交換する相手 |

- 計算量: O(1)（中のポインタを交換するだけ。要素はコピーされない）

<div class="anim" data-label="a.swap(b)">
1 2 3 | 7 8 # a = {1, 2, 3}　b = {7, 8}
1 2 3 | 7 8 # 要素はコピーしない。中身の場所（ポインタ）だけ入れ替える
7 8 | 1 2 3 # a = {7, 8}　b = {1, 2, 3}。O(1)
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> current = {1, 2, 3};
  std::vector<int> previous = {9};

  // ダブルバッファ: 今フレームの結果と前フレームを入れ替える
  current.swap(previous);
  std::println("current = {} / previous = {}", current, previous);
}
```

```text title="実行結果"
current = [9] / previous = [1, 2, 3]
```

!!! note "実際は"
    「今フレーム用」と「次フレーム用」の 2 本を持って毎フレーム入れ替える、ダブルバッファの形でよく使います。`std::swap(a, b)` と書いても同じです。

### emplace {#emplace}

```cpp
template <class... Args>
iterator emplace(const_iterator pos, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `const_iterator` | この位置の **前** に作る |
| `args` | 何個でも | `T` のコンストラクタにそのまま渡す引数 |

- 戻り値: 作った要素を指すイテレータ
- 計算量: O(n)（後ろをずらすため）

```cpp
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> names = {"Alice", "Carol"};
  // std::string(3, 'B') を添字 1 の位置に直接作る
  names.emplace(names.begin() + 1, 3, 'B');
  std::println("{}", names);
}
```

```text title="実行結果"
["Alice", "BBB", "Carol"]
```

!!! note "実際は"
    `insert` の「その場で作る」版です。`insert` 自体をあまり使わないので、こちらはさらに使いません。

### insert_range <span class="ver ver-23">C++23</span> {#insert_range data-toc-label="insert_range"}

```cpp
template <container-compatible-range<T> R>
iterator insert_range(const_iterator pos, R&& rg);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `const_iterator` | この位置の前に挿入する |
| `rg` | range | 挿入する範囲 |

- 戻り値: 挿入した最初の要素を指すイテレータ
- 計算量: O(n + m)

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 5};
  std::vector<int> middle = {2, 3, 4};
  v.insert_range(v.begin() + 1, middle);
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5]
```

!!! note "実際は"
    途中への挿入なので重いです。ほぼ使いません。

### assign_range <span class="ver ver-23">C++23</span> {#assign_range data-toc-label="assign_range"}

```cpp
template <container-compatible-range<T> R>
void assign_range(R&& rg);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `rg` | range | 新しい中身 |

- 計算量: O(n + m)
- 今の中身は全部消えて、`rg` のコピーになる。容量は使い回される

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {9, 9, 9, 9};
  v.assign_range(std::views::iota(1, 4));
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3]
```

!!! note "実際は"
    `v = other | std::ranges::to<std::vector>();` と書いても結果は同じです。容量を使い回したいときだけ意味があります。

### shrink_to_fit {#shrink_to_fit}

```cpp
void shrink_to_fit();
```

- 余った容量を返すように**お願いする**（実装は無視してもよい）
- 計算量: O(n)（実際に縮むなら、新しい領域を確保して全要素をムーブする）

<div class="anim" data-label="v.shrink_to_fit()">
10 20 30 _ _ _ # size 3 / capacity 6
10 20 30 # 余った capacity を返す（実装によっては引っ越しが起きる）
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v;
  v.reserve(100);
  v.push_back(1);
  std::println("{} / {}", v.size(), v.capacity());

  v.shrink_to_fit();
  std::println("{} / {}", v.size(), v.capacity());
}
```

```text title="実行結果"
1 / 100
1 / 1
```

!!! note "実際は"
    ゲーム中に呼ぶと再確保が起きるので、ほぼ使いません。「ロード画面で一時的に巨大になった vector のメモリを返したい」ときくらいです。

### rbegin {#rbegin}

```cpp
reverse_iterator rbegin() noexcept;
const_reverse_iterator rbegin() const noexcept;
```

- 戻り値: **最後の要素**を指す逆向きのイテレータ。`++` すると前の要素に進む
- 計算量: O(1)

### rend {#rend}

```cpp
reverse_iterator rend() noexcept;
const_reverse_iterator rend() const noexcept;
```

- 戻り値: **最初の要素の 1 つ前**を指す逆向きのイテレータ（中身は無い）
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};

  // rbegin から rend まで進むと、後ろから順に回れる
  for (auto it = v.rbegin(); it != v.rend(); ++it) {
    std::println("{}", *it);
  }

  // 今はこちらのほうが読みやすい
  for (int x : v | std::views::reverse) {
    std::println("reverse: {}", x);
  }
}
```

```text title="実行結果"
3
2
1
reverse: 3
reverse: 2
reverse: 1
```

!!! note "実際は"
    後ろから回すなら `std::views::reverse` で足ります。`rbegin` / `rend` を直接書くことはまずありません。

### cbegin {#cbegin}

```cpp
const_iterator cbegin() const noexcept;
```

- 戻り値: 先頭を指す **const** イテレータ（指している要素を書き換えられない）
- 計算量: O(1)

### cend {#cend}

```cpp
const_iterator cend() const noexcept;
```

- 戻り値: 最後の次を指す **const** イテレータ
- 計算量: O(1)

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  for (auto it = v.cbegin(); it != v.cend(); ++it) {
    std::println("{}", *it);
    // *it = 5;  とするとコンパイルエラー
  }
}
```

```text title="実行結果"
1
2
3
```

!!! note "実際は"
    `const auto&` の範囲 for で同じことができるので、ほぼ使いません。`crbegin` / `crend`（const の逆順）もあります。

### max_size {#max_size}

```cpp
size_type max_size() const noexcept;
```

- 戻り値: 理論上入れられる最大の要素数（実際のメモリ量とは関係ない）
- 計算量: O(1)

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v;
  std::println("{}", v.max_size());
}
```

```text title="実行結果（64 ビットの GCC の例）"
2305843009213693951
```

!!! note "実際は"
    使いません。これより先にメモリが足りなくなります。

### get_allocator {#get_allocator}

```cpp
allocator_type get_allocator() const noexcept;
```

- 戻り値: この vector が使っているアロケータのコピー
- 計算量: O(1)

!!! note "実際は"
    自作のアロケータを使っているときに、同じアロケータで別のコンテナを作るためのものです。普通は使いません。

## フラグ・オプション

vector 自体にはフラグはありません。C++23 で増えた **タグ** だけ覚えておきます。

| 値 | 重要度 | 意味 | 使う場面 |
| --- | --- | --- | --- |
| `std::from_range` | <span class="rank rank-sometimes">たまに</span> | 「この引数は range として扱って」という目印 <span class="ver ver-23">C++23</span> | views から vector を作るとき |

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> hp = {30, 0, 50, -10, 80};
  auto alive = hp | std::views::filter([](int h) { return h > 0; });

  // どちらも同じ結果。ranges::to のほうがよく見る
  std::vector<int> a(std::from_range, alive);
  auto b = alive | std::ranges::to<std::vector>();

  std::println("a = {}", a);
  std::println("b = {}", b);
}
```

```text title="実行結果"
a = [30, 50, 80]
b = [30, 50, 80]
```

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |
| `[]`, `at`, `front`, `back` | O(1) |
| 末尾に追加（`push_back`, `emplace_back`） | 償却 O(1) |
| 末尾を削除（`pop_back`） | O(1) |
| 条件で削除（`std::erase_if`） | O(n) |
| 値を探す（`std::ranges::find`） | O(n) |
| 途中・先頭に追加・削除（`insert`, `erase`） | O(n) |

## 古い書き方と今の書き方

ネットの古い記事でよく見る書き方との比較です。

=== "古い書き方"

    ```cpp
    // remove-erase イディオム
    enemies.erase(
        std::remove_if(enemies.begin(), enemies.end(),
                       [](const Enemy& e) { return e.hp <= 0; }),
        enemies.end());

    // 別の vector を末尾につなげる
    enemies.insert(enemies.end(), wave2.begin(), wave2.end());

    // 条件に合うものだけ集める
    std::vector<Enemy> alive;
    for (const auto& e : enemies) {
      if (e.hp > 0) {
        alive.push_back(e);
      }
    }

    // ソート
    std::sort(scores.begin(), scores.end());
    ```

=== "今の書き方（C++23）"

    ```cpp
    // C++20
    std::erase_if(enemies, [](const Enemy& e) { return e.hp <= 0; });

    // C++23
    enemies.append_range(wave2);

    // C++23
    auto alive = enemies
               | std::views::filter([](const Enemy& e) { return e.hp > 0; })
               | std::ranges::to<std::vector>();

    // C++20
    std::ranges::sort(scores);
    ```

## ゲームでの使いどころ

### 敵・弾・パーティクルのリスト

一番よくある使い方です。毎フレーム更新して、死んだものは `std::erase_if` でまとめて消します。

```cpp
void UpdateBullets(std::vector<Bullet>& bullets, float delta_time) {
  for (auto& bullet : bullets) {
    bullet.y -= bullet.speed * delta_time;
  }
  std::erase_if(bullets, [](const Bullet& b) { return b.y < 0.0f; });
}
```

### 順番がどうでもいいなら「swap して pop_back」

`erase` は後ろを全部詰めるので O(n) ですが、<strong>最後の要素で上書きして末尾を消せば O(1)</strong> です。描画順などを気にしないリストで使えます。

<div class="mem">
<div class="mem-step"><span class="mem-label">B を消したい</span><span class="mem-cells"><span>A</span><span class="gone">B</span><span>C</span><span>D</span><span class="move">E</span></span><span class="mem-note">最後の E を B の場所に入れる</span></div>
<div class="mem-step"><span class="mem-label">後</span><span class="mem-cells"><span>A</span><span class="move">E</span><span>C</span><span>D</span><span class="free">　</span></span><span class="mem-note">動いたのは 1 個だけ。そのかわり順番は変わる</span></div>
</div>

```cpp
#include <cstddef>
#include <print>
#include <string>
#include <utility>
#include <vector>

void RemoveUnordered(std::vector<std::string>& v, std::size_t index) {
  if (index != v.size() - 1) {
    v[index] = std::move(v.back());
  }
  v.pop_back();
}

int main() {
  std::vector<std::string> enemies = {"A", "B", "C", "D", "E"};
  RemoveUnordered(enemies, 1);
  std::println("{}", enemies);
}
```

```text title="実行結果"
["A", "E", "C", "D"]
```

### 2 次元のマップは 1 本の vector で持つ

`std::vector<std::vector<int>>` は行ごとにメモリがバラバラになって遅く、扱いも面倒です。**1 本の vector に `y * width + x` でアクセス**するのが定番です。

<div class="mem">
<div class="mem-step"><span class="mem-label">幅 4 × 高さ 3 のマップ</span><span class="mem-cells"><span>0,0</span><span>1,0</span><span>2,0</span><span>3,0</span><span class="move">0,1</span><span class="move">1,1</span><span class="move">2,1</span><span class="move">3,1</span><span>0,2</span><span>1,2</span><span>2,2</span><span>3,2</span></span></div>
<div class="mem-step"><span class="mem-label"></span><span class="mem-note">(x, y) = (2, 1) は 1 × 4 + 2 = 添字 6。行が横一列に並んでいるだけ</span></div>
</div>

```cpp
#include <print>
#include <vector>

class TileMap {
 public:
  TileMap(int width, int height)
      : width_(width), height_(height), tiles_(width * height, 0) {}

  int& At(int x, int y) { return tiles_[y * width_ + x]; }
  int height() const { return height_; }

 private:
  int width_;
  int height_;
  std::vector<int> tiles_;
};

int main() {
  TileMap map(4, 3);
  map.At(2, 1) = 7;

  for (int y = 0; y < map.height(); ++y) {
    std::println("{} {} {} {}", map.At(0, y), map.At(1, y), map.At(2, y),
                 map.At(3, y));
  }
}
```

```text title="実行結果"
0 0 0 0
0 0 7 0
0 0 0 0
```

C++23 なら `std::mdspan` で `tiles[y, x]` と書くこともできます（コンパイラ対応に注意）。

### ポリモーフィズムは unique_ptr で持つ

```cpp
// 基底クラスで持つと派生クラスの部分が切り落とされる（スライシング）
std::vector<GameObject> objects;  // NG

// ポインタで持つ
std::vector<std::unique_ptr<GameObject>> objects;
objects.push_back(std::make_unique<Player>());
objects.push_back(std::make_unique<Enemy>());
```

## パフォーマンス

- **連続したメモリ**に並ぶので、全要素を回す処理はどのコンテナよりも速いです（キャッシュ効率が良い）。要素数が数百〜数千なら、検索でも `map` や `list` より vector の線形探索のほうが速いことがよくあります。
- 容量が足りなくなると<strong>今より大きい領域を確保して全要素をムーブ（またはコピー）</strong> します。GCC / Clang は 2 倍、MSVC は 1.5 倍ずつ増えます。`reserve` で避けられます。
- 再確保のときにムーブを使ってもらうには、**ムーブコンストラクタに `noexcept` が必要**です。付いていないとコピーされます（自分で書かずに `= default` にしておけば自動で付きます）。
- MSVC の Debug ビルドはイテレータのチェックがあるので**とても遅い**です。速度は Release で測ってください。

### 再確保（引っ越し）のしくみ {#realloc}

<div class="mem">
<div class="mem-step"><span class="mem-label">capacity 4 で満杯</span><span class="mem-cells"><span>10</span><span>20</span><span>30</span><span>40</span></span><span class="mem-note">ここで push_back(50) すると…</span></div>
<div class="mem-step"><span class="mem-label">① 新しい場所を確保</span><span class="mem-cells"><span class="move">10</span><span class="move">20</span><span class="move">30</span><span class="move">40</span><span class="new">50</span><span class="free">　</span><span class="free">　</span><span class="free">　</span></span><span class="mem-note">2 倍の領域に全部ムーブして、50 を追加</span></div>
<div class="mem-step"><span class="mem-label">② 古い場所を解放</span><span class="mem-cells"><span class="gone">10</span><span class="gone">20</span><span class="gone">30</span><span class="gone">40</span></span><span class="mem-note">ここを指していたポインタ・参照・イテレータは<strong>全部壊れる</strong></span></div>
<div class="mem-legend"><span><span class="mem-cells"><span class="move">　</span></span>引っ越した要素</span><span><span class="mem-cells"><span class="new">　</span></span>追加した要素</span><span><span class="mem-cells"><span class="gone">　</span></span>解放された場所</span><span><span class="mem-cells"><span class="free">　</span></span>空き</span></div>
</div>

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  const int* before = v.data();
  v.push_back(5);  // capacity 4 で満杯なので再確保が起きる
  std::println("引っ越した？ {}", before != v.data());

  v.reserve(100);
  const int* after_reserve = v.data();
  for (int i = 0; i < 50; ++i) {
    v.push_back(i);  // 100 個までは再確保が起きない
  }
  std::println("引っ越した？ {}", after_reserve != v.data());
}
```

```text title="実行結果"
引っ越した？ true
引っ越した？ false
```

### イテレータ・参照が壊れる条件

| 操作 | 壊れるもの |
| --- | --- |
| `push_back` / `emplace_back` / `insert` で再確保が起きた | **全部** |
| `insert` / `emplace`（再確保なし） | 挿入位置より後ろ |
| `erase` | 削除位置より後ろ |
| `pop_back` | 末尾の要素と `end()` |
| `reserve`（容量が増えた） | **全部** |
| `resize`（容量が増えた） | **全部** |
| `clear` | **全部** |
| `swap` | 壊れない（相手の vector を指すようになる） |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `v[v.size()]` など範囲外アクセス | 未定義動作 |
| 空の vector で `back()` / `front()` / `pop_back()` | 未定義動作 |
| `reserve` しただけの場所に `[]` で書き込む | 未定義動作 |
| 壊れたイテレータ・参照・ポインタを使う | 未定義動作 |
| `at()` で範囲外 | `std::out_of_range` 例外 |
| `reserve(n)` で `n > max_size()` | `std::length_error` 例外 |
| メモリ不足 | `std::bad_alloc` 例外 |

## よくあるミス

??? failure "ループ中に erase して要素を飛ばす・落ちる"
    ```cpp
    // NG: erase した後の it は壊れている
    for (auto it = enemies.begin(); it != enemies.end(); ++it) {
      if (it->hp <= 0) {
        enemies.erase(it);
      }
    }

    // NG: 消した次の要素を飛ばす
    for (std::size_t i = 0; i < enemies.size(); ++i) {
      if (enemies[i].hp <= 0) {
        enemies.erase(enemies.begin() + i);
      }
    }

    // OK
    std::erase_if(enemies, [](const Enemy& e) { return e.hp <= 0; });
    ```

??? failure "要素への参照を持ったまま追加する"
    ```cpp
    Enemy& target = enemies[0];
    enemies.push_back(Enemy{});  // 再確保で target が壊れる可能性がある
    target.hp -= 10;             // 未定義動作
    ```

    プレイヤーが「狙っている敵」をポインタで覚えておく、などで起きます。添字で覚える、`reserve` で再確保を起こさない、ID で管理する、のどれかで避けます。[再確保のしくみ](#realloc) を参照してください。

??? failure "`size() - 1` が巨大な数になる"
    ```cpp
    std::vector<int> v;
    // v.size() - 1 は 0 - 1 なので、符号なしで 18446744073709551615 になる
    for (std::size_t i = 0; i < v.size() - 1; ++i) {
      v[i] = v[i + 1];  // 範囲外アクセス
    }

    // OK: 足し算の形にする
    for (std::size_t i = 0; i + 1 < v.size(); ++i) {
      v[i] = v[i + 1];
    }
    ```

??? failure "`reserve` と `resize` を間違える"
    ```cpp
    std::vector<int> v;
    v.reserve(10);
    v[0] = 1;  // NG: size は 0 のまま。未定義動作

    v.resize(10);
    v[0] = 1;  // OK
    ```

??? failure "関数に値渡しして毎回コピーする"
    ```cpp
    // NG: 呼ぶたびに vector 全体がコピーされる
    void DrawAll(std::vector<Sprite> sprites);

    // OK
    void DrawAll(const std::vector<Sprite>& sprites);
    ```

??? failure "`std::vector<bool>` が普通の vector ではない"
    `std::vector<bool>` はメモリ節約のために 1 ビットずつ詰めた特殊な型です。要素の参照が取れず、`data()` もありません。

    ```cpp
    std::vector<bool> flags(10);
    bool& f = flags[0];  // コンパイルエラー
    ```

    フラグ配列には `std::vector<char>`、`std::vector<std::uint8_t>`、個数が固定なら `std::bitset` を使います。

??? failure "`()` と `{}` を間違える"
    `std::vector<int> v{10};` は「10 が 1 個」です。「0 が 10 個」なら `std::vector<int> v(10);` です。[コンストラクタ](#コンストラクタ) を参照してください。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| `std::array` | 要素数がコンパイル時に固定。ヒープを使わない | 個数が決まっている（4 方向、装備スロットなど） |
| `std::span` | 中身を持たず、配列を「借りる」だけ | 関数の引数で配列を受け取るとき |
| `std::string` | 文字専用の vector のようなもの | 文字列 |
| `std::deque` | 先頭への追加・削除も O(1)。メモリは連続しない | 先頭からも頻繁に出し入れする |
| `std::list` | 途中の挿入・削除が O(1)。とても遅い | ほぼない |
| `std::flat_map` | 中身が vector のソート済み map <span class="ver ver-23">C++23</span> | 読み込み時に作って、あとは検索するだけの表 |
| `std::inplace_vector` | 容量が固定で、ヒープを使わない vector（C++26） | まだ使えない。今は自作するか固定長配列で代用 |

## コンパイラ対応

C++20 までの機能は主要なコンパイラすべてで使えます。C++23 の機能は以下を目安にしてください。

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::erase` / `std::erase_if` <span class="ver ver-20">C++20</span> | ○ | ○ | ○ |
| `append_range` / `std::from_range` <span class="ver ver-23">C++23</span> | VS 2022 17.4〜 | 15〜 | 17〜 |
| `std::ranges::to` <span class="ver ver-23">C++23</span> | VS 2022 17.4〜 | 14〜 | 17〜 |
| `std::println` <span class="ver ver-23">C++23</span> | VS 2022 17.7〜 | 14〜 | 18〜 |
| `std::println("{}", vec)`（range の出力） <span class="ver ver-23">C++23</span> | VS 2022 17.11〜 | 15〜 | 16〜 |

!!! info
    最新の対応状況は [cppreference のコンパイラ対応表](https://en.cppreference.com/w/cpp/compiler_support/23) で確認してください。MSVC では `/std:c++latest` の指定が必要です。

    `int main` があるサンプルには「▶ Compiler Explorer で実行」リンクが付いています。GCC 16.1 + `-std=c++23` でブラウザ上で実行できます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 配列が欲しくなったら、まず `std::vector`
    - [x] 足すのは `push_back` / `emplace_back`、回すのは範囲 for、消すのは `std::erase_if`
    - [x] 個数が分かっているなら `reserve`。`reserve` は `size` を変えない
    - [x] 追加・削除すると、持っていたポインタ・参照・イテレータが壊れることがある
    - [x] 関数には `const std::vector<T>&` か `std::span<const T>` で渡す

## 関連ページ

- [コンテナの選び方](../../basics/container-chart.md)
- [cpprefjp: std::vector](https://cpprefjp.github.io/reference/vector/vector.html)
- [cppreference: std::vector](https://en.cppreference.com/w/cpp/container/vector)

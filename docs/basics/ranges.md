---
title: ranges とビュー
tags:
  - 基礎
  - ranges
---

# ranges とビュー

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
<span class="ver ver-23">C++23</span>
</div>

**ranges**（レンジ）は C++20 で入った、<strong>「範囲」をまとめて 1 つのものとして扱う仕組み</strong>です。昔のアルゴリズムは `std::sort(v.begin(), v.end())` のように始まりと終わりを別々に渡していましたが、ranges 版は `std::ranges::sort(v)` と範囲をそのまま渡せます。さらに**ビュー**（view）を使うと、`v | std::views::filter(...) | std::views::transform(...)` のように、元のデータを変えずに「加工して見る」処理を `|` でつなげて書けます。

!!! tip "ポイント"
    - <strong>アルゴリズムは `std::ranges::` 版を使う。</strong> `begin()` / `end()` を書かなくていい。
    - プロジェクション（`&Enemy::hp` のようにメンバを渡す）で、比べる・探すメンバを指定できる。
    - ビュー（`std::views::...`）は「見るだけ」で、元のデータもコピーもしない。実際の計算は取り出すときに行われる。
    - ビューの結果を保存したいなら `| std::ranges::to<std::vector>()`（C++23）。

!!! info "このページを読む前に"
    [イテレータ](iterator.md) と [ラムダ式](lambda.md) を先に読むと分かりやすいです。

## 基本

### 範囲（range）とは

`begin()` と `end()` で始まりと終わりが分かるものは、全部「範囲」です。

| 範囲の例 |
| --- |
| `std::vector`、`std::array`、`std::string`、`std::map` などのコンテナ |
| C の配列 `int a[10]` |
| `std::span`、`std::string_view` |
| ビュー（`std::views::iota(0, 10)` など） |

### アルゴリズムの ranges 版

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {5, 2, 8, 1};

  std::sort(v.begin(), v.end());  // 昔の書き方
  std::ranges::sort(v);           // ranges 版: 範囲をそのまま渡す

  bool has8 = std::ranges::contains(v, 8);  // C++23
  std::println("{} {}", v, has8);
}
```

```text title="実行結果"
[1, 2, 5, 8] true
```

## 詳しく

### プロジェクション

ranges 版のアルゴリズムの多くは、最後の引数に**プロジェクション**を渡せます。「比べる前・探す前に各要素をこれに変換して」という指定で、メンバポインタを渡すのが定番です。

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {{"A", 30}, {"B", 10}, {"C", 20}};

  std::ranges::sort(enemies, {}, &Enemy::hp);                // hp で並べる
  auto it = std::ranges::find(enemies, "C", &Enemy::name);   // name で探す
  auto weakest = std::ranges::min_element(enemies, {}, &Enemy::hp);

  std::println("{} {} {}", enemies.front().name, it->hp, weakest->name);
}
```

```text title="実行結果"
B 20 B
```

### ビューと遅延評価

ビューは、作った時点では何も計算しません。範囲 for などで**要素を取り出すときに、1 つずつ計算**されます。

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6};

  auto view = v | std::views::filter([](int x) {
                std::println("  filter が {} を見た", x);
                return x % 2 == 0;
              })
              | std::views::take(2);

  std::println("ビューを作った（まだ何も計算していない）");
  for (int x : view) {
    std::println("取り出した: {}", x);
  }
}
```

```text title="実行結果"
ビューを作った（まだ何も計算していない）
  filter が 1 を見た
  filter が 2 を見た
取り出した: 2
  filter が 3 を見た
  filter が 4 を見た
取り出した: 4
  filter が 5 を見た
  filter が 6 を見た
```

ビューを作った時点では何も起きず、取り出すたびに filter が呼ばれているのが分かります。2 個目を取り出したあと、ループが「次」へ進むときに filter は 6 まで見ますが、そこで `take(2)` の数に達して終わり、取り出しはされません。

### パイプ `|` の読み方

```cpp
auto result = enemies
            | std::views::filter(IsAlive)        // ① 生きているものだけ
            | std::views::transform(&Enemy::pos) // ② 位置だけ取り出す
            | std::views::take(10);              // ③ 先頭 10 個
```

左から順に「① → ② → ③」と読みます。`std::views::take(std::views::transform(std::views::filter(enemies, IsAlive), ...), 10)` と同じ意味ですが、パイプのほうがずっと読みやすいです。

### ビューの結果を保存する

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  auto squares = v | std::views::transform([](int x) { return x * x; })
                   | std::ranges::to<std::vector>();  // 実体の vector にする
  std::println("{}", squares);
}
```

```text title="実行結果"
[1, 4, 9, 16]
```

### ビューは元を参照している

ビューは元のデータを指しているだけなので、**元が消えたり再確保されたりするとビューも壊れます**。ビューは作ったその場で使い切るのが基本です。

### 主なビュー

詳しくは [std::views](../stl/algorithms/views.md) を見てください。

| ビュー | 意味 |
| --- | --- |
| `filter` | 条件に合うものだけ |
| `transform` | 変換 |
| `take` / `drop` | 先頭 n 個 / n 個飛ばす |
| `reverse` | 逆順 |
| `iota` | 連番 |
| `enumerate` | 番号付き（C++23） |
| `zip` | 複数の範囲を組に（C++23） |

## ゲームでの例

```cpp
// 生きている敵の中で一番近いもの
auto alive = enemies | std::views::filter([](const Enemy& e) { return e.hp > 0; });
auto nearest = std::ranges::min_element(alive, {}, &Enemy::distance);
```

## よくあるミス

??? failure "古い std:: 版と混ぜて begin() / end() を書く"
    `std::ranges::sort(v.begin(), v.end())` でも動きますが、`std::ranges::sort(v)` で十分です。

??? failure "ビューを保存して元を変える"
    ```cpp
    auto alive = enemies | std::views::filter(IsAlive);
    enemies.push_back(Enemy{});  // 再確保でビューが壊れることがある
    ```

??? failure "Debug ビルドで遅いと感じる"
    ビューは何段も関数を重ねるので、最適化しない Debug ビルドでは普通のループよりかなり遅くなります。Release ではほぼ同じ速さになります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アルゴリズムは `std::ranges::` 版で、範囲をそのまま渡す
    - [x] プロジェクション `&T::member` でメンバを指定
    - [x] ビューは見るだけ・遅延評価。保存するなら `to<std::vector>()`

## 関連ページ

- [std::views](../stl/algorithms/views.md)
- [std::ranges::to](../stl/algorithms/ranges_to.md)
- [cppreference: Ranges library](https://en.cppreference.com/w/cpp/ranges)

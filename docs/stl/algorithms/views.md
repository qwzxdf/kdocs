---
title: std::views（filter / transform など）
tags:
  - アルゴリズム
  - ranges
---

# std::views（filter / transform など）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views` は、<strong>元のデータを変えずに「加工して見る」ための部品（ビュー）</strong>の集まりです。`v | std::views::filter(条件)` と書くと「条件に合う要素だけが見える範囲」が、`| std::views::transform(関数)` と書くと「各要素を変換した結果が見える範囲」ができます。`|` でいくつもつなげられ、実際の計算は範囲 for などで**取り出すときに初めて**行われます（遅延評価）。

!!! tip "ポイント"
    - よく使うのは `filter`（絞り込み）、`transform`（変換）、`reverse`（逆順）、`take` / `drop`（先頭 n 個 / n 個飛ばす）、`iota`（連番）、`enumerate`（番号付き）。
    - <strong>新しい vector は作られない。</strong> 欲しければ最後に [`| std::ranges::to<std::vector>()`](ranges_to.md)。
    - 元のデータを参照しているので、**元が消えたり再確保されたりするとビューも壊れる**。ビューは作ったその場で使い切る。
    - 毎フレームの重い処理に何段もつなげると、普通の for ループより読みにくく・遅くなることもある。2〜3 段までが目安。

!!! info "このページを読む前に"
    [ranges とビュー](../../basics/ranges.md)、[ラムダ式](../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数一覧

| ビュー | 重要度 | 何をする | 追加 |
| --- | --- | --- | --- |
| [`views::filter`](#filter) | <span class="rank rank-must">必須</span> | 条件に合う要素だけ | <span class="ver ver-20">C++20</span> |
| [`views::transform`](#transform) | <span class="rank rank-must">必須</span> | 各要素を変換 | <span class="ver ver-20">C++20</span> |
| [`views::iota`](#iota) | <span class="rank rank-often">よく使う</span> | 連番 `0, 1, 2, ...` | <span class="ver ver-20">C++20</span> |
| [`views::reverse`](#reverse) | <span class="rank rank-often">よく使う</span> | 逆順 | <span class="ver ver-20">C++20</span> |
| [`views::enumerate`](#enumerate) | <span class="rank rank-often">よく使う</span> | `(番号, 要素)` の組 | <span class="ver ver-23">C++23</span> |
| [`views::take`](#take) | <span class="rank rank-often">よく使う</span> | 先頭 n 個 | <span class="ver ver-20">C++20</span> |
| [`views::drop`](#drop) | <span class="rank rank-often">よく使う</span> | 先頭 n 個を飛ばす | <span class="ver ver-20">C++20</span> |
| [`views::zip`](#zip) | <span class="rank rank-often">よく使う</span> | 複数の範囲を組にして並べる | <span class="ver ver-23">C++23</span> |
| [`views::keys`](#keys) | <span class="rank rank-sometimes">たまに</span> | map などのキーだけ | <span class="ver ver-20">C++20</span> |
| [`views::values`](#values) | <span class="rank rank-sometimes">たまに</span> | map などの値だけ | <span class="ver ver-20">C++20</span> |
| [`views::split`](#split) | <span class="rank rank-sometimes">たまに</span> | 区切り文字で分割 | <span class="ver ver-20">C++20</span> |
| [`views::take_while`](#take_while) | <span class="rank rank-sometimes">たまに</span> | 条件を満たす間だけ | <span class="ver ver-20">C++20</span> |
| [`views::drop_while`](#drop_while) | <span class="rank rank-sometimes">たまに</span> | 条件を満たす間は飛ばす | <span class="ver ver-20">C++20</span> |
| [`views::chunk`](#chunk) | <span class="rank rank-sometimes">たまに</span> | n 個ずつに区切る | <span class="ver ver-23">C++23</span> |
| [`views::slide`](#slide) | <span class="rank rank-sometimes">たまに</span> | n 個ずつずらしながら見る | <span class="ver ver-23">C++23</span> |
| [`views::stride`](#stride) | <span class="rank rank-sometimes">たまに</span> | n 個おきに | <span class="ver ver-23">C++23</span> |
| [`views::join`](#join) | <span class="rank rank-sometimes">たまに</span> | 入れ子の範囲を 1 本につなげる | <span class="ver ver-20">C++20</span> |
| [`views::cartesian_product`](#cartesian_product) | <span class="rank rank-rare">知ってるだけ</span> | 全部の組み合わせ | <span class="ver ver-23">C++23</span> |
| [`views::adjacent`](#adjacent) | <span class="rank rank-rare">知ってるだけ</span> | 隣り合う n 個の組 | <span class="ver ver-23">C++23</span> |
| [`views::repeat`](#repeat) | <span class="rank rank-rare">知ってるだけ</span> | 同じ値の繰り返し | <span class="ver ver-23">C++23</span> |
| [`views::elements`](#elements) | <span class="rank rank-rare">知ってるだけ</span> | tuple の N 番目だけ | <span class="ver ver-20">C++20</span> |

## よくある使い方

### 1. 絞り込んで、変換して、回す

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {{"スライム", 0}, {"ゴブリン", 25}, {"ドラゴン", 300}};

  // 生きている敵の名前だけ
  auto alive_names = enemies
                   | std::views::filter([](const Enemy& e) { return e.hp > 0; })
                   | std::views::transform(&Enemy::name);

  for (const auto& name : alive_names) {
    std::println("{}", name);
  }
}
```

```text title="実行結果"
ゴブリン
ドラゴン
```

### 2. 番号付きで回す

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> ranking = {"Alice", "Bob", "Carol"};
  for (auto [i, name] : ranking | std::views::enumerate) {
    std::println("{}位 {}", i + 1, name);
  }
}
```

```text title="実行結果"
1位 Alice
2位 Bob
3位 Carol
```

### 3. 2 つの配列を同時に回す

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> names = {"剣", "盾", "薬"};
  std::vector<int> prices = {300, 200, 50};
  for (auto [name, price] : std::views::zip(names, prices)) {
    std::println("{}: {} G", name, price);
  }
}
```

```text title="実行結果"
剣: 300 G
盾: 200 G
薬: 50 G
```

## 関数の詳しい説明

### views::filter {#filter}

```cpp
template <class Pred>
constexpr /* range adaptor */ filter(Pred&& pred);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pred` | 関数・ラムダ | 要素を受け取り、**残すなら `true`** |

- 戻り値: 条件に合う要素だけが見えるビュー
- 計算量: 取り出すたびに、次に合う要素まで進む

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6};
  for (int x : v | std::views::filter([](int x) { return x % 2 == 0; })) {
    std::print("{} ", x);
  }
  std::println("");
}
```

```text title="実行結果"
2 4 6 
```

!!! note "実際は"
    「消す」のではなく「見ない」だけなので、元の vector はそのままです。本当に消したいなら [`std::erase_if`](erase_if.md)。

### views::transform {#transform}

```cpp
template <class F>
constexpr /* range adaptor */ transform(F&& f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 関数・ラムダ・メンバポインタ | 要素を受け取って、変換した値を返す |

- 戻り値: 各要素に `f` を適用した結果が見えるビュー
- 取り出すたびに `f` が呼ばれる（結果は保存されない）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> base_damage = {10, 20, 30};
  auto critical = base_damage | std::views::transform([](int d) { return d * 2; });
  std::println("{}", critical);
}
```

```text title="実行結果"
[20, 40, 60]
```

### views::iota {#iota}

```cpp
template <class W>
constexpr /* view */ iota(W&& value);                    // value から無限に
template <class W, class Bound>
constexpr /* view */ iota(W&& value, Bound&& bound);     // value から bound の手前まで
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | 整数など | 始まりの値 |
| `bound` | 整数など | 終わり（**含まない**） |

```cpp
#include <print>
#include <ranges>

int main() {
  for (int i : std::views::iota(0, 5)) {
    std::print("{} ", i);
  }
  std::println("");
}
```

```text title="実行結果"
0 1 2 3 4 
```

!!! note "実際は"
    `for (int i = 0; i < 5; ++i)` の代わりに使えます。ほかのビューと組み合わせるときに便利です。

### views::reverse {#reverse}

```cpp
inline constexpr /* range adaptor */ reverse;
```

- 逆順に見えるビュー。元の順番は変えない

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> history = {1, 2, 3};
  std::println("{}", history | std::views::reverse);
}
```

```text title="実行結果"
[3, 2, 1]
```

### views::enumerate <span class="ver ver-23">C++23</span> {#enumerate data-toc-label="views::enumerate"}

```cpp
inline constexpr /* range adaptor */ enumerate;
```

- `(番号, 要素の参照)` の組が見えるビュー。番号は 0 から始まる。要素は参照なので書き換えもできる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> slots = {0, 0, 0};
  for (auto [i, slot] : slots | std::views::enumerate) {
    slot = static_cast<int>(i) * 10;
  }
  std::println("{}", slots);
}
```

```text title="実行結果"
[0, 10, 20]
```

### views::take {#take}

```cpp
constexpr /* range adaptor */ take(std::ranges::range_difference_t<R> count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | 整数 | 先頭から何個見るか（足りなければあるだけ） |

### views::drop {#drop}

```cpp
constexpr /* range adaptor */ drop(std::ranges::range_difference_t<R> count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | 整数 | 先頭から何個飛ばすか |

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> ranking = {980, 870, 860, 700, 650};
  std::println("トップ 3: {}", ranking | std::views::take(3));
  std::println("4 位以下: {}", ranking | std::views::drop(3));
}
```

```text title="実行結果"
トップ 3: [980, 870, 860]
4 位以下: [700, 650]
```

### views::zip <span class="ver ver-23">C++23</span> {#zip data-toc-label="views::zip"}

```cpp
template <class... Rs>
constexpr /* view */ zip(Rs&&... rs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `rs` | 範囲をいくつでも | 並べる範囲。**一番短いもの**に合わせて終わる |

- 戻り値: 各範囲の要素を 1 つずつ取った tuple のビュー

[よくある使い方 3](#3-2-つの配列を同時に回す) を参照してください。

### views::keys {#keys}

```cpp
inline constexpr /* range adaptor */ keys;
```

- map などの `pair` の範囲から、キー（`first`）だけを見る

### views::values {#values}

```cpp
inline constexpr /* range adaptor */ values;
```

- 値（`second`）だけを見る

```cpp
#include <map>
#include <print>
#include <ranges>
#include <string>

int main() {
  std::map<std::string, int> stock = {{"potion", 3}, {"ether", 1}};
  std::println("{}", stock | std::views::keys);
  std::println("{}", stock | std::views::values);
}
```

```text title="実行結果"
["ether", "potion"]
[1, 3]
```

### views::split {#split}

```cpp
template <class Pattern>
constexpr /* range adaptor */ split(Pattern&& pattern);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pattern` | 文字 / 範囲 | 区切り |

- 戻り値: 区切られた各部分（それぞれが範囲）のビュー。文字列なら `std::string_view` に変換して使う

```cpp
#include <print>
#include <ranges>
#include <string>
#include <string_view>

int main() {
  std::string csv = "10,20,30";
  for (auto part : csv | std::views::split(',')) {
    std::println("[{}]", std::string_view(part));
  }
}
```

```text title="実行結果"
[10]
[20]
[30]
```

### views::take_while {#take_while}

```cpp
template <class Pred>
constexpr /* range adaptor */ take_while(Pred&& pred);
```

- 先頭から、`pred` が `true` の間だけ見る。`false` になったところで終わる

### views::drop_while {#drop_while}

```cpp
template <class Pred>
constexpr /* range adaptor */ drop_while(Pred&& pred);
```

- 先頭から、`pred` が `true` の間は飛ばし、そこから先を全部見る

```cpp
#include <print>
#include <ranges>
#include <string>

int main() {
  std::string line = "   name = hero";
  auto trimmed = line | std::views::drop_while([](char c) { return c == ' '; });
  auto key = trimmed | std::views::take_while([](char c) { return c != ' '; });
  std::println("[{}]", key | std::ranges::to<std::string>());
}
```

```text title="実行結果"
[name]
```

### views::chunk <span class="ver ver-23">C++23</span> {#chunk data-toc-label="views::chunk"}

```cpp
constexpr /* range adaptor */ chunk(std::ranges::range_difference_t<R> n);
```

- n 個ずつのかたまりに分ける。最後は n 個に足りないこともある

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> tiles = {1, 2, 3, 4, 5, 6, 7};
  for (auto row : tiles | std::views::chunk(3)) {
    std::println("{}", row);
  }
}
```

```text title="実行結果"
[1, 2, 3]
[4, 5, 6]
[7]
```

### views::slide <span class="ver ver-23">C++23</span> {#slide data-toc-label="views::slide"}

```cpp
constexpr /* range adaptor */ slide(std::ranges::range_difference_t<R> n);
```

- 長さ n の窓を 1 つずつずらしながら見る（移動平均などに使う）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::println("{}", v | std::views::slide(2));
}
```

```text title="実行結果"
[[1, 2], [2, 3], [3, 4]]
```

### views::stride <span class="ver ver-23">C++23</span> {#stride data-toc-label="views::stride"}

```cpp
constexpr /* range adaptor */ stride(std::ranges::range_difference_t<R> n);
```

- n 個おきに見る

```cpp
#include <print>
#include <ranges>

int main() {
  std::println("{}", std::views::iota(0, 10) | std::views::stride(3));
}
```

```text title="実行結果"
[0, 3, 6, 9]
```

### views::join {#join}

```cpp
inline constexpr /* range adaptor */ join;
```

- 「範囲の範囲」を 1 本につなげて見る（`vector<vector<T>>` を平らにする）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<std::vector<int>> waves = {{1, 2}, {3}, {4, 5}};
  std::println("{}", waves | std::views::join);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5]
```

### views::cartesian_product <span class="ver ver-23">C++23</span> {#cartesian_product data-toc-label="views::cartesian_product"}

```cpp
template <class... Rs>
constexpr /* view */ cartesian_product(Rs&&... rs);
```

- すべての組み合わせ。二重 for ループの代わりになる

```cpp
#include <print>
#include <ranges>

int main() {
  for (auto [y, x] : std::views::cartesian_product(std::views::iota(0, 2),
                                                   std::views::iota(0, 3))) {
    std::print("({},{}) ", x, y);
  }
  std::println("");
}
```

```text title="実行結果"
(0,0) (1,0) (2,0) (0,1) (1,1) (2,1) 
```

### views::adjacent <span class="ver ver-23">C++23</span> {#adjacent data-toc-label="views::adjacent"}

```cpp
template <std::size_t N>
inline constexpr /* range adaptor */ adjacent;
```

- 隣り合う N 個を tuple にして見る。`slide` のコンパイル時固定版

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> path = {0, 3, 5};
  for (auto [from, to] : path | std::views::adjacent<2>) {
    std::println("{} → {}", from, to);
  }
}
```

```text title="実行結果"
0 → 3
3 → 5
```

### views::repeat <span class="ver ver-23">C++23</span> {#repeat data-toc-label="views::repeat"}

```cpp
template <class T>
constexpr /* view */ repeat(T&& value, std::size_t count);
```

- 同じ値を count 回繰り返す

### views::elements {#elements}

```cpp
template <std::size_t N>
inline constexpr /* range adaptor */ elements;
```

- tuple / pair の範囲から、N 番目の要素だけを見る（`keys` は `elements<0>`、`values` は `elements<1>`）

```cpp
#include <print>
#include <ranges>
#include <tuple>
#include <vector>

int main() {
  std::println("{}", std::views::repeat('*', 3));
  std::vector<std::tuple<int, char, float>> rows = {{1, 'a', 0.5f}, {2, 'b', 1.5f}};
  std::println("{}", rows | std::views::elements<2>);
}
```

```text title="実行結果"
['*', '*', '*']
[0.5, 1.5]
```

## フラグ・オプション

ビューは `|` でつなげて使います。左から順に適用されます。

```cpp
v | std::views::filter(f) | std::views::transform(g) | std::views::take(3)
// 「f で絞り込み → g で変換 → 先頭 3 個」
```

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    for (std::size_t i = 0; i < ranking.size(); ++i) {
      std::cout << i + 1 << "位 " << ranking[i] << "\n";
    }

    for (std::size_t i = 0; i < names.size() && i < prices.size(); ++i) {
      std::cout << names[i] << ": " << prices[i] << "\n";
    }
    ```

=== "今の書き方（C++23）"

    ```cpp
    for (auto [i, name] : ranking | std::views::enumerate) {
      std::println("{}位 {}", i + 1, name);
    }

    for (auto [name, price] : std::views::zip(names, prices)) {
      std::println("{}: {}", name, price);
    }
    ```

## ゲームでの使いどころ

| 場面 | ビュー |
| --- | --- |
| 生きているものだけ処理 | `filter` |
| 座標だけ取り出して描画 | `transform(&Enemy::pos)` |
| ランキングの上位 | `take(10)` |
| 番号付きの UI リスト | `enumerate` |
| 位置と速度の配列を同時に更新 | `zip(positions, velocities)` |
| マップを行ごとに | `chunk(width)` |

## パフォーマンス

- ビュー自体はほぼタダで作れます（コピーも確保も無し）。
- `filter` は「次に合う要素まで進む」処理が取り出すたびに走ります。同じビューを何度も回すなら、一度 `to<std::vector>()` で実体化したほうが速いこともあります。
- `transform` の関数は取り出すたびに呼ばれます。重い計算なら結果をキャッシュします。
- Debug ビルドではビューの階層がそのまま関数呼び出しになるので、普通のループよりかなり遅く見えることがあります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 元のコンテナが消えた・再確保されたあとでビューを使う | 未定義動作 |
| `filter` の条件で要素を書き換える | 未定義動作になることがある |
| 一時的な vector からビューを作って変数に保存する | コンパイルエラーか未定義動作 |

## よくあるミス

??? failure "ビューを保存して、あとで元が変わる"
    ```cpp
    auto alive = enemies | std::views::filter(IsAlive);
    enemies.push_back(Enemy{});  // 再確保が起きるかもしれない
    for (auto& e : alive) {}     // 未定義動作の可能性
    ```

    ビューは作ったその場で使い切ります。

??? failure "ビューを vector だと思う"
    ビューに `push_back` や `[]`（filter の場合）はありません。vector が欲しいなら `| std::ranges::to<std::vector>()`。

??? failure "filter したビューの size() を呼ぶ"
    `filter` のビューは、全部見ないと個数が分からないので `size()` がありません。`std::ranges::distance(view)` で数えます（O(n)）。

## 理解度チェック

!!! question "Q1. 何が出力される？"
    ```cpp
    auto r = std::views::iota(1, 10)
           | std::views::filter([](int x) { return x % 3 == 0; })
           | std::views::transform([](int x) { return x * x; });
    std::println("{}", r);
    ```

    <div class="spoiler" markdown>

    **答え:** `[9, 36, 81]`。1〜9 のうち 3 の倍数（3, 6, 9）を 2 乗しています。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::to`](ranges_to.md) | ビューを vector などの実体に変える |
| [`std::erase_if`](erase_if.md) | 本当に消す |
| [`std::ranges::copy`](copy_fill.md) | 別のコンテナにコピーする |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `filter` / `transform` / `take` など <span class="ver ver-20">C++20</span> | ○ | ○ | ○ |
| `enumerate` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 未対応（21 時点） |
| `zip` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 17〜 |
| `adjacent` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 未対応（21 時点） |
| `chunk` / `slide` / `stride` / `cartesian_product` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 未対応（21 時点） |
| `repeat` <span class="ver ver-23">C++23</span> | ○ | 13〜 | 17〜 |
| ビューを `println` で出力 <span class="ver ver-23">C++23</span> | VS 2022 17.11〜 | 15〜 | 16〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] `|` でつなげて「加工して見る」。元は変わらない
    - [x] `filter`・`transform`・`enumerate`・`zip`・`take` を覚える
    - [x] vector が欲しければ `| std::ranges::to<std::vector>()`
    - [x] ビューはその場で使い切る

## 関連ページ

- [cpprefjp: <ranges>](https://cpprefjp.github.io/reference/ranges.html)
- [cppreference: Ranges library](https://en.cppreference.com/w/cpp/ranges)

---
title: std::pair / std::tuple
tags:
  - ユーティリティ
---

# std::pair / std::tuple

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11</span>
`#include <utility>` / `#include <tuple>`
</div>

`std::pair` は**2 つの値をひとまとめにする型**、`std::tuple` は**いくつでも値をひとまとめにする型**です。わざわざ構造体を作るほどでもない「ちょっとした組」を表すのに使います。map の要素（キーと値）も pair です。C++17 からは構造化束縛 `auto [a, b] = p;` で、中身に名前を付けて取り出せます。

!!! tip "ポイント"
    - <strong>関数から 2〜3 個の値を返すとき、map の要素を扱うときに使う。</strong>
    - 取り出すのは構造化束縛 `auto [x, y] = pair;` が一番読みやすい。
    - 意味のある組なら、**名前付きのメンバを持つ構造体のほうが読みやすい**（`first` / `second` では何か分からない）。
    - `<`, `==` が最初の要素から順に比べてくれるので、複数の条件での並べ替えにも使える。

## 宣言

```cpp
template <class T1, class T2>
struct pair;

template <class... Types>
class tuple;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `T1`, `T2` | pair の 1 つ目・2 つ目の型 |
| `Types...` | tuple に入れる型を何個でも |

## 関数一覧

| 関数・メンバ | 重要度 | 何をする | 対象 |
| --- | --- | --- | --- |
| [構造化束縛](#structured-binding) | <span class="rank rank-must">必須</span> | `auto [a, b] = p;` で中身に名前を付ける | 両方 |
| [`first` / `second`](#first) | <span class="rank rank-must">必須</span> | 1 つ目 / 2 つ目のメンバ | pair |
| [`{a, b}` で作る](#make) | <span class="rank rank-must">必須</span> | 波かっこで作る | 両方 |
| [`std::get`](#get) | <span class="rank rank-often">よく使う</span> | N 番目（または型で）取り出す | 両方 |
| [比較演算子](#compare) | <span class="rank rank-often">よく使う</span> | 先頭の要素から順に比べる | 両方 |
| [`std::tie`](#tie) | <span class="rank rank-sometimes">たまに</span> | 変数の参照をまとめる（比較・受け取り用） | tuple |
| [`std::make_pair`](#make_pair) | <span class="rank rank-sometimes">たまに</span> | 型を推論して pair を作る | pair |
| [`std::make_tuple`](#make_tuple) | <span class="rank rank-rare">知ってるだけ</span> | 型を推論して tuple を作る | tuple |
| [`std::tuple_size`](#tuple_size) | <span class="rank rank-rare">知ってるだけ</span> | 要素数（コンパイル時） | 両方 |
| [`std::apply`](#apply) | <span class="rank rank-rare">知ってるだけ</span> | tuple の中身を関数の引数として渡す | tuple |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | 両方 |

## よくある使い方

### 1. 関数から 2 つの値を返す

```cpp
#include <print>
#include <utility>
#include <vector>

std::pair<int, int> MinMax(const std::vector<int>& v) {
  int lo = v[0];
  int hi = v[0];
  for (int x : v) {
    lo = x < lo ? x : lo;
    hi = x > hi ? x : hi;
  }
  return {lo, hi};
}

int main() {
  auto [lo, hi] = MinMax({4, 9, 1, 7});
  std::println("{} 〜 {}", lo, hi);
}
```

```text title="実行結果"
1 〜 9
```

### 2. map を回す

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<std::string, int> stock = {{"potion", 3}, {"ether", 1}};
  for (const auto& [name, count] : stock) {  // 要素は pair<const string, int>
    std::println("{} x{}", name, count);
  }
}
```

```text title="実行結果"
ether x1
potion x3
```

### 3. 複数の条件で並べる

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <utility>
#include <vector>

int main() {
  // (レベル, 名前) の組は、レベル → 名前の順に比べられる
  std::vector<std::pair<int, std::string>> units = {{3, "B"}, {1, "Z"}, {3, "A"}};
  std::ranges::sort(units);
  std::println("{}", units);
}
```

```text title="実行結果"
[(1, "Z"), (3, "A"), (3, "B")]
```

## 関数の詳しい説明

### 構造化束縛 <span class="ver ver-17">C++17</span> {#structured-binding data-toc-label="構造化束縛"}

```cpp
auto [a, b] = pair_or_tuple;        // コピー
auto& [a, b] = pair_or_tuple;       // 参照（書き換えると元も変わる）
const auto& [a, b] = pair_or_tuple; // 読むだけ
```

- 中身を順番に、名前を付けた変数として取り出します。**名前の数と要素数は同じ**である必要があります
- pair / tuple のほか、構造体や配列にも使えます

```cpp
#include <print>
#include <tuple>

int main() {
  std::tuple<int, float, char> data = {1, 2.5f, 'x'};
  auto& [id, value, tag] = data;
  value *= 2.0f;  // 参照なので data も変わる
  std::println("{} {} {}", id, std::get<1>(data), tag);
}
```

```text title="実行結果"
1 5 x
```

### first / second {#first}

```cpp
T1 first;
T2 second;
```

- pair の 1 つ目と 2 つ目のメンバ変数です

```cpp
#include <print>
#include <utility>

int main() {
  std::pair<int, int> grid_pos = {3, 5};
  grid_pos.second += 1;
  std::println("({}, {})", grid_pos.first, grid_pos.second);
}
```

```text title="実行結果"
(3, 6)
```

### {a, b} で作る {#make}

```cpp
std::pair<int, std::string> p = {1, "one"};
std::tuple<int, float, bool> t = {1, 2.0f, true};
std::pair q(1, 2.0);  // 型を推論（std::pair<int, double>）
```

- 戻り値の型が決まっている関数では、`return {a, b};` だけで作れます

### std::get {#get}

```cpp
template <std::size_t I, class... Types>
constexpr auto& get(std::tuple<Types...>& t) noexcept;

template <class T, class... Types>
constexpr T& get(std::tuple<Types...>& t) noexcept;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `I` | 何番目か（0 始まり、コンパイル時の定数） |
| `T` | 型で指定（その型が 1 つだけのときに使える） |

```cpp
#include <print>
#include <string>
#include <tuple>

int main() {
  std::tuple<std::string, int, float> enemy = {"スライム", 10, 1.5f};
  std::println("{} {} {}", std::get<0>(enemy), std::get<int>(enemy), std::get<2>(enemy));
}
```

```text title="実行結果"
スライム 10 1.5
```

### 比較演算子 {#compare}

- `==`, `!=`, `<`, `<=`, `>`, `>=`, `<=>` が使えます。**1 つ目を比べて、同じなら 2 つ目を比べる**（辞書順）

```cpp
#include <print>
#include <utility>

int main() {
  std::pair<int, int> a = {1, 9};
  std::pair<int, int> b = {2, 0};
  std::println("{} {}", a < b, a == std::pair{1, 9});
}
```

```text title="実行結果"
true true
```

### std::tie {#tie}

```cpp
template <class... Types>
constexpr std::tuple<Types&...> tie(Types&... args) noexcept;
```

- 変数の**参照**をまとめた tuple を作ります。複数の条件で比べる比較関数を短く書くのに使います

```cpp
#include <print>
#include <string>
#include <tuple>

struct Player {
  int level;
  std::string name;
};

bool Before(const Player& a, const Player& b) {
  // レベルの大きい順、同じなら名前順
  return std::tie(b.level, a.name) < std::tie(a.level, b.name);
}

int main() {
  Player x = {5, "Bob"};
  Player y = {5, "Alice"};
  std::println("{}", Before(y, x));
}
```

```text title="実行結果"
true
```

### std::make_pair {#make_pair}

```cpp
template <class T1, class T2>
constexpr std::pair<V1, V2> make_pair(T1&& t, T2&& u);
```

- 型を推論して pair を作ります。C++17 以降は `std::pair(a, b)` や `{a, b}` で足ります

### std::make_tuple {#make_tuple}

```cpp
template <class... Types>
constexpr std::tuple<VTypes...> make_tuple(Types&&... args);
```

- 型を推論して tuple を作ります

### std::tuple_size {#tuple_size}

```cpp
template <class T>
struct tuple_size;  // std::tuple_size_v<T> で値を取る
```

- 要素数をコンパイル時に取得します。テンプレートを書くとき以外は使いません

### std::apply {#apply}

```cpp
template <class F, class Tuple>
constexpr decltype(auto) apply(F&& f, Tuple&& t);
```

- tuple の中身をばらして、関数の引数として渡します

```cpp
#include <print>
#include <tuple>

int Add(int a, int b, int c) { return a + b + c; }

int main() {
  std::tuple args = {1, 2, 3};
  std::println("{} {}", std::apply(Add, args), std::tuple_size_v<decltype(args)>);
  auto t = std::make_tuple(1, 'a');
  std::println("{}", t);
}
```

```text title="実行結果"
6 3
(1, 'a')
```

### swap {#swap}

```cpp
void swap(pair& other);
```

- 中身を交換します

<div class="anim" data-label="a.swap(b)">
1 2 | 3 4 # a と b
>3 >4 | >1 >2 # 要素ごとに入れ替える
</div>

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::pair<int, int> r = MinMax(v);
    int lo = r.first;
    int hi = r.second;

    int a, b;
    std::tie(a, b) = MinMax(v);
    ```

=== "今の書き方（C++17）"

    ```cpp
    auto [lo, hi] = MinMax(v);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 座標の組 | `std::pair<int, int>`（グリッドの x, y） |
| 経路探索のノード | `std::pair<int, int>`（コスト, マス）を priority_queue に入れる |
| 複数の戻り値 | 当たったか + 位置、成功したか + 値 |
| 比較関数 | `std::tie` で複数条件 |

## パフォーマンス

中身をそのまま並べただけの型なので、構造体と同じ速さ・大きさです。

## よくあるミス

??? failure "first / second だらけで読めなくなる"
    `std::pair<int, std::pair<float, bool>>` のような入れ子は、何が何か分からなくなります。意味がある組なら構造体を作ります。

    ```cpp
    struct HitResult {
      bool hit;
      Vec2 point;
    };
    ```

??? failure "構造化束縛の数が合わない"
    `auto [a, b] = std::tuple{1, 2, 3};` はコンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| 構造体 | メンバに名前が付く。意味のある組はこちら |
| [`std::array`](../containers/array.md) | 同じ型を N 個 |
| [`std::optional`](optional.md) | 「値があるか」+ 値 |

## コンパイラ対応

C++11 からある機能です。構造化束縛は C++17、tuple の `println` 出力は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つなら pair、3 つ以上なら tuple
    - [x] 取り出すのは `auto [a, b] = ...`
    - [x] 意味のある組なら構造体のほうが読みやすい

## 関連ページ

- [cpprefjp: std::pair](https://cpprefjp.github.io/reference/utility/pair.html)
- [cppreference: std::tuple](https://en.cppreference.com/w/cpp/utility/tuple)

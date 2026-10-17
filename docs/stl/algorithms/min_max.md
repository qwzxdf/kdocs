---
title: std::min / std::max / std::minmax
tags:
  - アルゴリズム
---

# std::min / std::max / std::minmax

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++98〜</span>
`#include <algorithm>`
</div>

`std::min` と `std::max` は、**2 つ（または複数）の値のうち小さいほう・大きいほうを返す**関数です。`std::minmax` は両方を一度に返します。C++20 の `std::ranges::min` / `max` を使うと、vector などの範囲を丸ごと渡して最小値・最大値を取ることもできます。

!!! tip "ポイント"
    - 2 つの値なら `std::min(a, b)` / `std::max(a, b)`。HP の下限・上限の処理などで毎日使う。
    - 3 つ以上なら `std::min({a, b, c})`。
    - vector の最小値なら `std::ranges::min(v)`（空だと未定義動作）。位置が欲しいなら [`min_element`](min_element.md)。
    - **2 つの引数は同じ型にする**（`std::min(hp, 0.5f)` のように int と float を混ぜるとコンパイルエラー）。
    - 範囲内に収めたいなら [`std::clamp`](clamp.md) のほうが読みやすい。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::max`](#max) | <span class="rank rank-must">必須</span> | 大きいほう | O(1) / O(n) |
| [`std::min`](#min) | <span class="rank rank-must">必須</span> | 小さいほう | O(1) / O(n) |
| [`std::ranges::max`](#ranges-max) | <span class="rank rank-often">よく使う</span> | 範囲の最大値 <span class="ver ver-20">C++20</span> | O(n) |
| [`std::ranges::min`](#ranges-min) | <span class="rank rank-often">よく使う</span> | 範囲の最小値 <span class="ver ver-20">C++20</span> | O(n) |
| [`std::minmax`](#minmax) | <span class="rank rank-sometimes">たまに</span> | 小さいほうと大きいほうの組 | O(1) / O(n) |
| [`std::ranges::minmax`](#ranges-minmax) | <span class="rank rank-sometimes">たまに</span> | 範囲の最小値と最大値 <span class="ver ver-20">C++20</span> | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  int hp = 30;
  int damage = 50;
  hp = std::max(hp - damage, 0);  // 0 より下にしない
  std::println("HP {}", hp);

  int heal = 120;
  int max_hp = 100;
  hp = std::min(hp + heal, max_hp);  // 最大値を超えない
  std::println("HP {}", hp);

  std::vector<int> scores = {70, 95, 40};
  std::println("最高 {} / 最低 {}", std::ranges::max(scores), std::ranges::min(scores));
}
```

```text title="実行結果"
HP 0
HP 100
最高 95 / 最低 40
```

## 関数の詳しい説明

### std::max {#max}

```cpp
template <class T>
constexpr const T& max(const T& a, const T& b);
template <class T, class Compare>
constexpr const T& max(const T& a, const T& b, Compare comp);
template <class T>
constexpr T max(std::initializer_list<T> ilist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a`, `b` | `const T&` | 比べる 2 つ。**同じ型**である必要がある |
| `ilist` | `{...}` | 3 つ以上を比べるとき |
| `comp` | 比較関数 | 「a < b」の代わりに使う比較 |

- 戻り値: 大きいほう（等しければ `a`）。2 引数版は**参照**を返す
- 計算量: 2 引数は O(1)、`{...}` 版は O(n)

```cpp
#include <algorithm>
#include <print>

int main() {
  std::println("{}", std::max(3, 7));
  std::println("{}", std::max({4, 9, 2}));
  std::println("{}", std::max(2.5f, static_cast<float>(3)));  // 型をそろえる
}
```

```text title="実行結果"
7
9
3
```

### std::min {#min}

```cpp
template <class T>
constexpr const T& min(const T& a, const T& b);
template <class T, class Compare>
constexpr const T& min(const T& a, const T& b, Compare comp);
template <class T>
constexpr T min(std::initializer_list<T> ilist);
```

- 戻り値: 小さいほう（等しければ `a`）
- 引数は `max` と同じ

```cpp
#include <algorithm>
#include <print>

int main() {
  float speed = 12.0f;
  float max_speed = 8.0f;
  std::println("{}", std::min(speed, max_speed));
  std::println("{}", std::min({5, 1, 3}));
}
```

```text title="実行結果"
8
1
```

### std::ranges::max <span class="ver ver-20">C++20</span> {#ranges-max data-toc-label="std::ranges::max"}

```cpp
template <input_range R, class Proj = identity, class Comp = ranges::less>
constexpr range_value_t<R> max(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 調べる範囲。**空だと未定義動作** | 省略不可 |
| `comp` | 比較関数 | 大小の決め方 | `<` |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 最大の要素の**コピー**
- 計算量: O(n)

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Player {
  std::string name;
  int score;
};

int main() {
  std::vector<Player> players = {{"Alice", 300}, {"Bob", 520}, {"Carol", 410}};
  Player top = std::ranges::max(players, {}, &Player::score);
  std::println("1 位: {}", top.name);
}
```

```text title="実行結果"
1 位: Bob
```

### std::ranges::min <span class="ver ver-20">C++20</span> {#ranges-min data-toc-label="std::ranges::min"}

```cpp
template <input_range R, class Proj = identity, class Comp = ranges::less>
constexpr range_value_t<R> min(R&& r, Comp comp = {}, Proj proj = {});
```

- 戻り値: 最小の要素のコピー。**空だと未定義動作**

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<float> distances = {12.5f, 3.2f, 8.0f};
  std::println("一番近い敵まで {}", std::ranges::min(distances));
}
```

```text title="実行結果"
一番近い敵まで 3.2
```

### std::minmax {#minmax}

```cpp
template <class T>
constexpr std::pair<const T&, const T&> minmax(const T& a, const T& b);
template <class T>
constexpr std::pair<T, T> minmax(std::initializer_list<T> ilist);
```

- 戻り値: `{小さいほう, 大きいほう}` の `pair`

```cpp
#include <algorithm>
#include <print>

int main() {
  auto [lo, hi] = std::minmax({7, 2, 9, 4});
  std::println("{} 〜 {}", lo, hi);
}
```

```text title="実行結果"
2 〜 9
```

!!! warning
    2 引数版は**参照の pair** を返すので、`auto [lo, hi] = std::minmax(a + 1, b);` のように一時的な値を渡すと、すぐ消える値を参照してしまいます（未定義動作）。

### std::ranges::minmax <span class="ver ver-20">C++20</span> {#ranges-minmax data-toc-label="std::ranges::minmax"}

```cpp
template <input_range R, class Proj = identity, class Comp = ranges::less>
constexpr minmax_result<range_value_t<R>> minmax(R&& r, Comp comp = {}, Proj proj = {});
```

- 戻り値: `.min` と `.max` を持つ構造体。1 回なめるだけで両方取れる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> heights = {3, 8, 1, 6};
  auto [low, high] = std::ranges::minmax(heights);
  std::println("最低 {} / 最高 {}", low, high);
}
```

```text title="実行結果"
最低 1 / 最高 8
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` など | 大小を逆にする |
| `proj` | <span class="rank rank-often">よく使う</span> | `&Type::member` | メンバで比べる（ranges 版のみ） |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    int hp2 = hp < 0 ? 0 : hp;
    int best = *std::max_element(scores.begin(), scores.end());
    ```

=== "今の書き方（C++20）"

    ```cpp
    int hp2 = std::max(hp, 0);
    int best = std::ranges::max(scores);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| HP・所持金の下限 | `std::max(hp - damage, 0)` |
| 回復の上限 | `std::min(hp + heal, max_hp)` |
| 速度の制限 | `std::min(speed, max_speed)` |
| 最高スコア | `std::ranges::max(scores)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲で `std::ranges::min` / `max` | 未定義動作 |
| 2 引数版の戻り値（参照）を、一時的な値を渡したのに保存する | 未定義動作 |

## よくあるミス

??? failure "型が違ってコンパイルエラー"
    ```cpp
    float x = 1.5f;
    auto m = std::max(x, 0);  // float と int なのでエラー

    auto m2 = std::max(x, 0.0f);    // OK
    auto m3 = std::max<float>(x, 0);  // OK
    ```

??? failure "Windows で min / max がマクロとぶつかる"
    `<windows.h>` を読み込むと `min` / `max` というマクロが定義され、`std::max(a, b)` が壊れます。`windows.h` の前に `#define NOMINMAX` を書くか、`(std::max)(a, b)` と括弧で囲みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::clamp`](clamp.md) | 下限と上限の両方に収める |
| [`std::ranges::min_element`](min_element.md) | 最小値の**位置**を返す |

## コンパイラ対応

`std::min` / `max` は C++98、`std::ranges::min` / `max` / `minmax` は C++20 で、主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つなら `std::min(a, b)` / `std::max(a, b)`、型をそろえる
    - [x] 範囲なら `std::ranges::min(v)` / `max(v)`（空はダメ）
    - [x] Windows では `NOMINMAX`

## 関連ページ

- [cpprefjp: std::max](https://cpprefjp.github.io/reference/algorithm/max.html)
- [cppreference: std::max](https://en.cppreference.com/w/cpp/algorithm/max)

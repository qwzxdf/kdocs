---
title: std::max
summary: "2 つ以上の値や、範囲の中から、大きいほうを求める。"
order: 25
tags:
  - アルゴリズム
---

# std::max

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <algorithm>`
</div>

体力が 0 未満にならないようにする、スコアの最高記録を更新する。ゲームでは、2 つの値のうち大きいほうを選ぶ場面が何度も出てきます。`a > b ? a : b` と書いてもよいのですが、`a` と `b` の式が長いと読みにくく、評価が 2 回走る間違いも起きます。`std::max` は、その比較を 1 つの関数にした部品です。

!!! tip "ポイント"
    - 2 つなら `std::max(a, b)`、3 つ以上なら `std::max({a, b, c})`。
    - 「HP を 0 より下にしない」のような**下限**の処理は `std::max(hp, 0)`。
    - **2 つの引数は同じ型にする**（`float` と `int` を混ぜるとコンパイルエラー）。
    - 位置が欲しいなら [`max_element`](max_element.md)。範囲に収めたいなら [`clamp`](clamp.md)。

!!! info "このページを読む前に"
    [`std::min`](min.md) と対になっています。型をそろえる規則など、共通の話は両方に当てはまります。

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


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` など | 大小の決め方を変える |
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

下限を決めるのが、`max` の主な使いどころです。ダメージを受けた後の体力は `hp = std::max(hp - damage, 0)` と書いて、0 未満にならないようにします。所持金や弾薬数のように、マイナスにならない値で使います。

最高記録の更新にも使います。`best = std::max(best, score)` と書くと、今のスコアが記録を超えたときだけ更新されます。

範囲を渡す `std::ranges::max` は、配列の最大値を調べるときに使います。ただし、空の範囲に使うと未定義動作なので、あらかじめ空でないことを確かめます。最大の要素の位置や、メンバでの比較が必要なら、`max_element` を使います。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲で `std::ranges::max` | 未定義動作 |
| 2 引数版（参照を返す）に一時的な値を渡して、戻り値を保存する | ぶら下がった参照になる（未定義動作） |

## よくあるミス

??? failure "型が違ってコンパイルエラー"
    ```cpp
    float x = 1.5f;
    auto m = std::max(x, 0);  // float と int なのでエラー

    auto m2 = std::max(x, 0.0f);      // OK
    auto m3 = std::max<float>(x, 0);  // OK
    ```

??? failure "Windows で max がマクロとぶつかる"
    `<windows.h>` を読み込むと `max` というマクロが定義され、`std::max(a, b)` が壊れます。`windows.h` の前に `#define NOMINMAX` を書くか、`(std::max)(a, b)` と括弧で囲みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::min`](min.md) | 小さいほうを返す |
| [`std::clamp`](clamp.md) | 下限と上限の両方に収める |
| [`std::ranges::max_element`](max_element.md) | 最大値の**位置**を返す |

## コンパイラ対応

`std::max` は C++98、`std::ranges::max` は C++20 で、主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つなら `std::max(a, b)`、型をそろえる
    - [x] 範囲なら `std::ranges::max(v)`（空はダメ）
    - [x] Windows では `NOMINMAX`

## 関連ページ

- [cpprefjp: std::max](https://cpprefjp.github.io/reference/algorithm/max.html)
- [cppreference: std::max](https://en.cppreference.com/w/cpp/algorithm/max)

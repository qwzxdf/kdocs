---
title: std::min
summary: "2 つ以上の値や、範囲の中から、小さいほうを求める。"
order: 26
tags:
  - アルゴリズム
---

# std::min

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <algorithm>`
</div>

`std::min` は、**2 つ（または複数）の値のうち小さいほうを返す**関数です。C++20 の `std::ranges::min` を使うと、vector などの範囲を丸ごと渡して最小値を取ることもできます。

!!! tip "ポイント"
    - 2 つなら `std::min(a, b)`、3 つ以上なら `std::min({a, b, c})`。
    - 「回復しても最大 HP を超えない」のような**上限**の処理は `std::min(hp + heal, max_hp)`。
    - **2 つの引数は同じ型にする**。型が違うとコンパイルエラー。
    - 位置が欲しいなら [`min_element`](min_element.md)。範囲に収めたいなら [`clamp`](clamp.md)。

## 関数の詳しい説明

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


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-rare">知ってるだけ</span> | `std::greater{}` など | 大小の決め方を変える |
| `proj` | <span class="rank rank-often">よく使う</span> | `&Type::member` | メンバで比べる（ranges 版のみ） |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 回復の上限 | `std::min(hp + heal, max_hp)` |
| 速度の制限 | `std::min(speed, max_speed)` |
| 一番近い敵までの距離 | `std::ranges::min(distances)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲で `std::ranges::min` | 未定義動作 |
| 2 引数版に一時的な値を渡して、戻り値を保存する | ぶら下がった参照になる（未定義動作） |

## よくあるミス

??? failure "Windows で min がマクロとぶつかる"
    `<windows.h>` を読み込むと `min` というマクロが定義され、`std::min(a, b)` が壊れます。`#define NOMINMAX` を `windows.h` より前に書くか、`(std::min)(a, b)` と括弧で囲みます。

??? failure "上限と下限を逆に使う"
    `std::min` は**上限**を作ります（`min(hp, 100)` は 100 を超えない）。下限は [`std::max`](max.md) です。迷うなら [`clamp`](clamp.md)。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::max`](max.md) | 大きいほうを返す |
| [`std::clamp`](clamp.md) | 下限と上限の両方に収める |
| [`std::ranges::min_element`](min_element.md) | 最小値の**位置**を返す |

## コンパイラ対応

`std::min` は C++98、`std::ranges::min` は C++20 で、主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つなら `std::min(a, b)`、型をそろえる
    - [x] 範囲なら `std::ranges::min(v)`（空はダメ）
    - [x] 上限は `min`、下限は `max`

## 関連ページ

- [cpprefjp: std::min](https://cpprefjp.github.io/reference/algorithm/min.html)
- [cppreference: std::min](https://en.cppreference.com/w/cpp/algorithm/min)

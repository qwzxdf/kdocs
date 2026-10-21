---
title: std::uniform_int_distribution
summary: "範囲内の整数を、同じ確率で出す（両端を含む）。"
order: 10
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::uniform_int_distribution

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::uniform_int_distribution` は、**`a` 以上 `b` 以下の整数を、どれも同じ確率で出す分布**です。サイコロ、ランダムな添字、ドロップ数の抽選など、整数の乱数が欲しいときの基本です。**両端を含む**点に注意してください（`[a, b]`）。

!!! tip "ポイント"
    - `uniform_int_distribution<int> dice(1, 6);` は 1〜6（6 を含む）。
    - 添字には `(0, size - 1)`。`size` を含めない。
    - `rand() % n` は偏るので使わない。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::uniform_int_distribution {#uniform_int}

```cpp
template <class IntType = int>
class uniform_int_distribution {
 public:
  explicit uniform_int_distribution(IntType a, IntType b = std::numeric_limits<IntType>::max());
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 整数 | 最小値（**含む**） |
| `b` | 整数 | 最大値（**含む**） |

- `a` 〜 `b` の整数が同じ確率で出ます。`a > b` は未定義動作

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(42);
  std::uniform_int_distribution<int> dice(1, 6);

  bool ok = true;
  for (int i = 0; i < 1000; ++i) {
    int v = dice(rng);
    ok = ok && v >= 1 && v <= 6;   // 1〜6 に収まる（6 を含む）
  }
  std::println("全部 1〜6 の範囲？ {} / {} 〜 {}", ok, dice.min(), dice.max());
}
```

```text title="実行結果"
全部 1〜6 の範囲？ true / 1 〜 6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| サイコロ・ダメージのばらつき | `uniform_int_distribution<int> dmg(8, 12);` |
| 配列からランダムに 1 つ選ぶ | `uniform_int_distribution<size_t> pick(0, v.size() - 1);` |

## よくあるミス

??? failure "上限を含めて範囲外を指す"
    `uniform_int_distribution<size_t> pick(0, v.size());` は `size` も出るので範囲外です。`v.size() - 1` までです。

??? failure "毎回分布を作る"
    分布は軽いですが、同じ範囲を使うなら使い回せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 小数 |
| [`std::mt19937`](mt19937.md) | エンジン |
| [`std::ranges::sample`](../../algorithms/sample.md) | 配列から重複なしで選ぶ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `[a, b]` の整数を同じ確率で
    - [x] 両端を含む
    - [x] `rand() % n` は使わない

## 関連ページ

- [cpprefjp: std::uniform_int_distribution](https://cpprefjp.github.io/reference/random/uniform_int_distribution.html)
- [cppreference: std::uniform_int_distribution](https://en.cppreference.com/w/cpp/numeric/random/uniform_int_distribution)

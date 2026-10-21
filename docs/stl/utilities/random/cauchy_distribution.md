---
title: std::cauchy_distribution
summary: "コーシー分布。極端な外れ値が出やすい。"
order: 25
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::cauchy_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::cauchy_distribution` は、**極端に大きい（小さい）値が、たまに出る**乱数（コーシー分布）を出します。正規分布に比べて裾がとても長く、外れ値が頻繁に出ます。ゲームでは、まれな大事件のような演出にしか使いません。

!!! tip "ポイント"
    - 平均が定義されない（無限大に近い値がたまに出る）。
    - `a` が中心、`b` が尺度。
    - ほとんど使わない。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cauchy_distribution {#cauchy_distribution}

```cpp
explicit cauchy_distribution(double a = 0.0, double b = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `a` | `double` | 中心の位置 | `0.0` |
| `b` | `double` | 尺度（正の数） | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::cauchy_distribution<double> d(0.0, 1.0);
  std::println("a {} / b {}", d.a(), d.b());
}
```

```text title="実行結果"
a 0 / b 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| まれに極端な値が出る演出 | `cauchy_distribution<float> burst(0.0f, 1.0f);` |

## よくあるミス

??? failure "平均が取れると思う"
    平均が存在しない分布なので、たくさん引いて平均を取っても、収束しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`normal_distribution`](normal_distribution.md) | 裾が短い |
| [`student_t_distribution`](student_t_distribution.md) | n = 1 のとき Cauchy と同じ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 裾がとても長い分布
    - [x] 平均が定義されない
    - [x] ほとんど使わない

## 関連ページ

- [cpprefjp: std::cauchy_distribution](https://cpprefjp.github.io/reference/random/cauchy_distribution.html)
- [cppreference: std::cauchy_distribution](https://en.cppreference.com/w/cpp/numeric/random/cauchy_distribution)

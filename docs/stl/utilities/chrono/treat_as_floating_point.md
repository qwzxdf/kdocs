---
title: std::chrono::treat_as_floating_point
summary: "duration の中身（rep）を、小数として扱うかの特性。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::treat_as_floating_point

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`duration` の `rep` が整数か小数かで、変換の可否が変わります（整数への暗黙変換は精度が落ちるので禁止）。この判定に使うのが `treat_as_floating_point` で、`rep` が小数型なら `true` です。

!!! tip "ポイント"
    - `double` や `float` は `true`、`int` は `false`。
    - 自作の数値型を `rep` にするとき、特殊化して知らせる。
    - `_v` 版で bool が取れる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::treat_as_floating_point {#treat_as_floating_point}

```cpp
template <class Rep>
struct treat_as_floating_point : is_floating_point<Rep> {};
template <class Rep>
inline constexpr bool treat_as_floating_point_v = treat_as_floating_point<Rep>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Rep` | 型 | 調べる型 |

- 戻り値: 小数として扱うなら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::treat_as_floating_point_v<double>);
  std::println("{}", std::chrono::treat_as_floating_point_v<int>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作の固定小数点型を duration の rep に使う | `treat_as_floating_point` を特殊化する |

## よくあるミス

??? failure "整数 rep に暗黙変換を期待する"
    小さい単位から大きい単位への変換は、整数 `rep` では暗黙にはできません。`duration_cast` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration_values`](duration_values.md) | rep の 0・最大・最小 |
| [`duration`](duration.md) | 時間の長さ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] rep が小数かの特性
    - [x] double / float は true
    - [x] 自作 rep では特殊化する

## 関連ページ

- [cpprefjp: std::chrono::treat_as_floating_point](https://cpprefjp.github.io/reference/chrono/treat_as_floating_point.html)
- [cppreference: std::chrono::treat_as_floating_point](https://en.cppreference.com/w/cpp/chrono/treat_as_floating_point)

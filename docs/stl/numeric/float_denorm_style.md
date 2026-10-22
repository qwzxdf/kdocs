---
title: std::float_denorm_style
summary: "非正規数を持つかを表す列挙型。"
order: 900
tags:
  - 数値
---

# std::float_denorm_style

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <limits>`
</div>

0 に非常に近い小さな値（非正規数）を持てるかを表す列挙型です。`std::numeric_limits<T>::has_denorm` の型で、多くの環境は `denorm_present`（持てる）です。C++23 で `has_denorm` は非推奨になりました。

!!! tip "ポイント"
    - `numeric_limits` のメンバが返す型。
    - 値: denorm_indeterminate / denorm_absent / denorm_present。
    - ふつうは `numeric_limits` 経由で比べる。

!!! info "このページを読む前に"
    [`std::numeric_limits`](limits.md) を先に読んでください。

## 関数の詳しい説明

### std::float_denorm_style {#float_denorm_style}

```cpp
enum float_denorm_style {
  /* denorm_indeterminate / denorm_absent / denorm_present */
};
```

- 戻り値: なし（列挙型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <limits>
#include <print>

int main() {
  std::println("{}", std::numeric_limits<double>::denorm_min() > 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 環境の浮動小数点の性質を調べる | `std::numeric_limits<float>::has_denorm` |

## よくあるミス

??? failure "実行時に変わると思う"
    この値は型の性質で、`fesetround` で変えた丸めは反映されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型の性質 |
| [`fesetround`](fesetround.md) | 実行時の丸めモード |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 非正規数を持つかを表す列挙型
    - [x] numeric_limits のメンバが返す
    - [x] ふつうは意識しない

## 関連ページ

- [cpprefjp: std::float_denorm_style](https://cpprefjp.github.io/reference/limits/float_denorm_style.html)
- [cppreference: std::float_denorm_style](https://en.cppreference.com/w/cpp/types/numeric_limits/float_denorm_style)

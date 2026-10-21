---
title: std::sinh
summary: "双曲線正弦（sinh）を求める。"
order: 30
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sinh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::sinh` は、**双曲線正弦**を返す関数です。双曲線関数（`sinh`・`cosh`・`tanh`）は、ケーブルの垂れ下がり（懸垂線）や、なめらかな S 字カーブ（`tanh`）に使います。ゲームでは `tanh` を使うことが多いです。

!!! tip "ポイント"
    - `cosh` と `tanh` と一緒に覚える。
    - `sinh(x) = (e^x − e^−x) / 2`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sinh {#sinh}

```cpp
double sinh(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 値 |

- 戻り値: 双曲線正弦
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::sinh(1.0));
}
```

```text title="実行結果"
1.1752
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ロープ・ケーブルの垂れ下がり | `cosh` で懸垂線を描く |

## よくあるミス

??? failure "sin と混同する"
    周期関数ではありません。値は急速に大きくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cosh`](cosh.md) | 双曲線余弦 |
| [`tanh`](tanh.md) | 双曲線正接 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 双曲線正弦
    - [x] 値は急に増える
    - [x] ゲームでは tanh が多い

## 関連ページ

- [cpprefjp: std::sinh](https://cpprefjp.github.io/reference/cmath/sinh.html)
- [cppreference: std::sinh](https://en.cppreference.com/w/cpp/numeric/math/sinh)

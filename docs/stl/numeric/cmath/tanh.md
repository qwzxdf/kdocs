---
title: std::tanh
summary: "双曲線正接（tanh）を求める。−1〜1 になだらかに収まる。"
order: 32
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::tanh

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::tanh` は、**双曲線正接**を返す関数で、**どんな値を入れても −1〜1 になめらかに収まる**S 字カーブです。入力を滑らかに頭打ちにしたい（ジョイスティックの感度、音量のソフトクリップ）ときに便利です。ニューラルネットワークの活性化関数としても使われます。

!!! tip "ポイント"
    - 出力は常に −1〜1。大きな入力は ±1 に近づく。
    - 音のソフトクリッピング、入力のなだらかな頭打ちに。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::tanh {#tanh}

```cpp
double tanh(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 値 |

- 戻り値: −1〜1 の値
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f} {:.4f}", std::tanh(1.0), std::tanh(10.0));
}
```

```text title="実行結果"
0.7616 1.0000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ジョイスティックの入力を滑らかに頭打ちにする | `std::tanh(input * gain)` |
| 音がクリップしないように丸める | `std::tanh(sample)` |

## よくあるミス

??? failure "範囲の外を期待する"
    常に −1〜1 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`clamp`](../../algorithms/clamp.md) | 硬い頭打ち |
| [`sinh`](sinh.md) | 双曲線正弦 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] −1〜1 に収まる S 字
    - [x] なめらかな頭打ち
    - [x] 音のクリップに

## 関連ページ

- [cpprefjp: std::tanh](https://cpprefjp.github.io/reference/cmath/tanh.html)
- [cppreference: std::tanh](https://en.cppreference.com/w/cpp/numeric/math/tanh)

---
title: std::abs
summary: "絶対値を求める（整数・小数に対応）。"
order: 2
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::abs

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

「2 つの値の差が、どれくらい離れているか」を知りたいとき、`a - b` は大小によって符号が変わってしまいます。`std::abs` は符号を取り除いた大きさを返すので、`std::abs(a - b)` で距離が得られます。許容誤差の判定、キャラクターの位置の比較など、ゲームでは常に登場します。

!!! tip "ポイント"
    - 小数は `<cmath>`、整数は `<cstdlib>` が宣言する。どちらの型も `std::abs` で呼べるが、include を忘れると別のオーバーロードが選ばれる。
    - `int` の最小値を渡すと、結果が表せずに未定義動作になる。
    - 浮動小数点の比較では、`std::abs(a - b) < 許容誤差` が定番。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の一覧を先に見ると、ほかの数学関数との関係が分かります。

## 関数の詳しい説明

### std::abs {#abs}

```cpp
int abs(int x);
float abs(float x);
double abs(double x);
```

引数の型で、使われる関数が変わります。`int` なら整数版、`float` なら `float` 版、`double` なら `double` 版です。ヘッダーを include し忘れると、C 由来の `abs(int)` だけが見えて、`float` を渡したときに黙って `int` へ切り捨てられることがあります。`<cmath>` と `<cstdlib>` の両方を include すれば確実です。

`int` の最小値（`-2147483648`）の絶対値は、`int` では表せません。この値を渡すと未定義動作です。値が `INT_MIN` になりうる計算では、`long long` に変換してから呼びます。

- 絶対値（マイナスを取った値）。整数版は `<cstdlib>`、浮動小数点版は `<cmath>` にあります

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::abs(-5), std::abs(-2.5f));
  std::println("{}", std::sqrt(16.0f));
}
```

```text title="実行結果"
5 2.5
4
```

## 実際に動かしてみる

```cpp
#include <cmath>
#include <cstdlib>
#include <print>

int main() {
  std::println("{} {}", std::abs(-3.5), std::abs(-4));
}
```

```text title="実行結果"
3.5 4
```

## ゲームでの使いどころ

浮動小数点の値の比較で、最もよく使います。`a == b` では誤差のせいで一致しないことがあるので、`std::abs(a - b) < 1e-5f` と書いて「十分に近いか」を調べます。目標の位置にほぼ着いたかを判定する、アニメーションが終わりに近いかを判定する、といった場面です。

2 つの位置のずれの大きさを調べるときにも使います。x と y を別々に調べて、`std::abs(dx) < 4 && std::abs(dy) < 4` のように書くと、距離を計算せずに矩形で近さを判定できます。

## よくあるミス

??? failure "浮動小数点を `==` で比べる"
    `0.1f + 0.2f == 0.3f` は偽になります。比較には `std::abs(a - b) < 許容誤差` を使います。許容誤差は、値の大きさに合わせて決めます。

??? failure "`float` に C 由来の `abs` が呼ばれる"
    `std::` を付けずに `abs(x)` と書き、`<cstdlib>` だけを include していると、整数版が呼ばれて `float` が切り捨てられます。`std::abs` と書き、`<cmath>` を include します。

??? failure "`INT_MIN` に使う"
    `std::abs(std::numeric_limits<int>::min())` は未定義動作です。ダメージの差分などで極端な値が来うる場合は、`long long` で計算します。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::fabs` | C 由来の小数用の名前。`std::abs` で足りる |
| [`copysign`](copysign.md) | ある値の大きさに、別の値の符号を付ける |
| [`clamp`](../../algorithms/clamp.md) | 値を範囲の中に収める |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数の比較は `std::abs(a - b) < 許容誤差`。
    - [x] `<cmath>` と `<cstdlib>` の両方を include して、`std::abs` と書く。
    - [x] `INT_MIN` の絶対値は表せない。

## 関連ページ

- [cpprefjp: std::abs](https://cpprefjp.github.io/reference/cmath/abs.html)
- [cppreference: std::abs](https://en.cppreference.com/w/cpp/numeric/math/abs)

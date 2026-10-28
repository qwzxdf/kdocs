---
title: std::isfinite
summary: "値が有限の数（NaN でも無限大でもない）かを調べる。"
order: 28
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isfinite

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

外部ファイルから読み込んだ座標や、計算で求めた速度が無限大や NaN になっていることがあります。それをそのまま描画や物理に渡すと、画面が飛ぶ、物が消える、といった原因のわかりにくい不具合が出ます。

`std::isfinite` は、<strong>値が普通の数か（無限大でも NaN でもないか）</strong>を一度に調べます。

!!! tip "ポイント"
    - `std::isfinite(1.0)` は `true`、無限大と NaN は `false`
    - 0 と非正規化数（とても小さい数）も `true`
    - データを読み込んだ直後や、計算結果を使う前の検査に向く
    - 整数に対しては常に `true`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isfinite {#isfinite}

<span class="ver ver-11">C++11</span>

```cpp
bool isfinite(float x);
bool isfinite(double x);
bool isfinite(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 調べたい値 |

戻り値は、`x` が有限の値（通常の数、非正規化数、ゼロ）なら `true`、±∞ または NaN なら `false` です。`!isinf(x) && !isnan(x)` と同じ意味ですが、1 回の呼び出しで済みます。

不具合の原因を追うときに役立ちます。計算が壊れた場所を特定するため、`assert(std::isfinite(position.x))` のように、結果を使う前に確認を入れます。NaN は一度混ざると以降の計算に広がるので、早い段階で気づくのが重要です。

整数型を渡すと `double` に変換され、常に `true` です。

`-ffast-math` を指定すると、コンパイラが「無限大も NaN も出ない」と仮定するため、`isfinite` が常に `true` を返すように最適化されることがあります。検査が必要なコードでは、このオプションを避けます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double inf = std::numeric_limits<double>::infinity();
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("isfinite(1.5) = {}", std::isfinite(1.5));
  std::println("isfinite(0)   = {}", std::isfinite(0.0));
  std::println("isfinite(inf) = {}", std::isfinite(inf));
  std::println("isfinite(nan) = {}", std::isfinite(nan));
}
```

```text title="実行結果"
isfinite(1.5) = true
isfinite(0)   = true
isfinite(inf) = false
isfinite(nan) = false
```

## ゲームでの使いどころ

計算結果が壊れていないかの確認に使います。

```cpp
// 位置を更新した直後に壊れていないかを検査する（デバッグ中）
position += velocity * dt;
assert(std::isfinite(position.x) && std::isfinite(position.y));
```

リリース版では、`assert` が外れます。ファイルから読み込んだデータのように、外部から来る値は、`if` で検査してエラーとして扱います。

## よくあるミス

??? failure "NaN を `==` や `<` で調べようとして、見逃す"
    NaN との比較は常に偽になります。`std::isnan` か `isfinite` を使います。

??? failure "`-ffast-math` で、検査が効かなくなる"
    検査が必要なコードでは、このオプションを避けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isinf`](isinf.md) | 無限大か |
| [`isnan`](isnan.md) | NaN か |
| [`isnormal`](isnormal.md) | 通常の数か（ゼロと非正規化数を除く） |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `isfinite(x)` は、無限大でも NaN でもないときに `true`
    - [x] 計算結果を使う前、データを読み込んだ直後の検査に使う
    - [x] `-ffast-math` では検査できなくなる

## 関連ページ

- [`std::isinf`](isinf.md)
- [cpprefjp: std::isfinite](https://cpprefjp.github.io/reference/cmath/isfinite.html)
- [cppreference: std::isfinite](https://en.cppreference.com/w/cpp/numeric/math/isfinite)

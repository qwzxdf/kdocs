---
title: std::lcm
summary: "最小公倍数を求める。"
order: 2
group: <numeric> の整数・補間関数
tags:
  - 数値
---

# std::lcm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

3 秒ごとに鳴る合図と、4 秒ごとに鳴る合図があるとき、2 つが同時に鳴るのは何秒後でしょうか。答えは 12 秒後です。3 の倍数と 4 の倍数が最初に重なる数、つまり<strong>最小公倍数</strong>です。

`std::lcm` はこれを返します。周期の異なるイベントを同期させる、模様の繰り返しを揃える、といった処理に使えます。

!!! tip "ポイント"
    - `std::lcm(4, 6)` は 12。両方の倍数のうち最小の、正の数を返す
    - 片方が 0 なら 0。負の値は絶対値で扱い、結果は 0 以上
    - 桁あふれに注意。大きい値どうしなら、結果が型に収まらないことがある。収まらないと未定義動作
    - 整数型だけを受け取る

!!! info "このページを読む前に"
    [`<numeric>`](numeric.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lcm {#lcm}

<span class="ver ver-17">C++17</span>

```cpp
template <class M, class N>
constexpr std::common_type_t<M, N> lcm(M m, N n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `m` | 整数型 | 1 つ目の整数 |
| `n` | 整数型 | 2 つ目の整数 |

引数は整数型のみで、`bool` と浮動小数点数は渡せません。戻り値は 2 つの共通型です。

どちらかが 0 なら、結果は 0 です。0 の倍数は 0 だけなので、「共通の倍数」が 0 しかないためです。負の値は絶対値として扱うので、結果が負になることはありません。

落とし穴は桁あふれです。最小公倍数は、`m / gcd(m, n) * n` のように、2 つの値の積に近い大きさになります。`int` どうしで 10 万と 10 万 + 1 のような、互いに素な大きな値を渡すと、結果が 10 の 10 乗を超え、`int` に収まりません。規格上、結果が共通型で表せない場合は未定義動作です。大きな値を渡す可能性があるなら、あらかじめ `long long` で呼びます。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>

int main() {
  std::println("lcm(4, 6)  = {}", std::lcm(4, 6));    // 両方の倍数のうち最小
  std::println("lcm(3, 4)  = {}", std::lcm(3, 4));    // 互いに素なら積
  std::println("lcm(0, 5)  = {}", std::lcm(0, 5));    // 片方が 0 なら 0
  std::println("lcm(-4, 6) = {}", std::lcm(-4, 6));   // 絶対値で扱う
}
```

```text title="実行結果"
lcm(4, 6)  = 12
lcm(3, 4)  = 12
lcm(0, 5)  = 0
lcm(-4, 6) = 12
```

## ゲームでの使いどころ

### 周期の違うイベントの重なり

敵の攻撃パターンが 3 秒周期、床のトラップが 4 秒周期のとき、2 つが同時に起きる周期は、最小公倍数です。

```cpp
#include <numeric>
#include <print>

int main() {
  const int attack_period = 3;  // 敵の攻撃の周期（秒）
  const int trap_period = 4;    // トラップの周期（秒）
  std::println("3 秒ごとと 4 秒ごとのイベントは {} 秒ごとに重なる",
               std::lcm(attack_period, trap_period));
}
```

```text title="実行結果"
3 秒ごとと 4 秒ごとのイベントは 12 秒ごとに重なる
```

イベントの「ずれ」を見せたいゲームでは、この周期が分かると、演出の繰り返しの長さを決められます。

### 模様の繰り返し

幅 6 マスと幅 4 マスの模様を並べるとき、全体が最初に揃う幅は 12 マスです。それ以上並べても、同じ並びが繰り返されます。

## よくあるミス

??? failure "結果が型に収まらない"
    互いに素な大きい値の最小公倍数は、積に近くなります。`int` の範囲を超えて未定義動作になるので、幅の広い型で呼びます。

??? failure "0 を渡して、0 が返って驚く"
    0 との最小公倍数は 0 です。周期が 0 になるデータは、あらかじめ除外します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gcd`](gcd.md) | 最大公約数。`lcm(a, b) = a / gcd(a, b) * b` の関係にある |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの整数の最小公倍数を返す。`lcm(4, 6)` は 12
    - [x] 片方が 0 なら 0。負の値は絶対値で扱う
    - [x] 周期の違うイベントが重なる間隔を求めるのに使える
    - [x] 結果が型に収まらないと未定義動作。大きな値は `long long` で

## 関連ページ

- [`std::gcd`](gcd.md)
- [cpprefjp: std::lcm](https://cpprefjp.github.io/reference/numeric/lcm.html)
- [cppreference: std::lcm](https://en.cppreference.com/w/cpp/numeric/lcm)

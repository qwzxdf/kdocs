---
title: std::numeric_limits
summary: "型の最大値・最小値・誤差の大きさを、調べる。"
order: 72
tags:
  - 数値
---

# std::numeric_limits

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++98〜</span>
`#include <limits>`
</div>

「いちばん近い敵を探す」ループの初期値には、何を入れればよいでしょうか。0 では、どんな距離も大きく感じて、更新されません。大きい値を自分で決めるのも、不安です。`std::numeric_limits<T>` は、数値の型 `T` の最大値・最小値・誤差の大きさなどを教えてくれます。`std::numeric_limits<int>::max()` のように、型ごとに取り出せます。

!!! tip "ポイント"
    - 最大値は `max()`、最小値は **`lowest()`**（float の `min()` は「一番小さい正の数」なので注意）。
    - 「まだ見つかっていない」の初期値に `max()` / `lowest()` を使う。
    - 無限大は `infinity()`、NaN は `quiet_NaN()`。
    - float の比較の誤差の目安は `epsilon()`（1.0 の近くでの最小の差）。

!!! info "このページを読む前に"
    整数や浮動小数点が表せる範囲と、桁あふれの考え方が分かると読みやすいです。

## 関数一覧

| 関数・定数 | 重要度 | 何を返す | `float` の例 |
| --- | --- | --- | --- |
| [`max()`](#max) | <span class="rank rank-must">必須</span> | 一番大きい値 | 約 3.4e38 |
| [`lowest()`](#lowest) | <span class="rank rank-must">必須</span> | 一番小さい（一番マイナスの）値 | 約 -3.4e38 |
| [`min()`](#min) | <span class="rank rank-often">よく使う</span> | 整数: 一番小さい値 / **浮動小数点: 一番小さい正の数** | 約 1.2e-38 |
| [`infinity()`](#infinity) | <span class="rank rank-sometimes">たまに</span> | 無限大 | inf |
| [`epsilon()`](#epsilon) | <span class="rank rank-sometimes">たまに</span> | 1.0 と次に大きい値の差 | 約 1.19e-7 |
| [`quiet_NaN()`](#quiet_nan) | <span class="rank rank-rare">知ってるだけ</span> | NaN | nan |
| [`digits10`](#digits10) | <span class="rank rank-rare">知ってるだけ</span> | 正しく表せる 10 進数の桁数 | 6 |
| [`is_signed`](#is_signed) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きか | true |
| [`is_integer`](#is_integer) | <span class="rank rank-rare">知ってるだけ</span> | 整数型か | false |
| [`digits`](#digits) | <span class="rank rank-rare">知ってるだけ</span> | 仮数部（整数なら値）のビット数 | 24 |
| [`has_infinity`](#has_infinity) | <span class="rank rank-rare">知ってるだけ</span> | 無限大を表せるか | true |
| [`denorm_min()`](#denorm_min) | <span class="rank rank-rare">知ってるだけ</span> | 一番小さい正の非正規化数 | 約 1.4e-45 |

## よくある使い方

### 一番近い敵を探す初期値

```cpp
#include <limits>
#include <print>
#include <vector>

int main() {
  std::vector<float> distances = {12.5f, 3.2f, 8.0f};
  float nearest = std::numeric_limits<float>::max();  // 「まだ何も見つかっていない」
  for (float d : distances) {
    if (d < nearest) {
      nearest = d;
    }
  }
  std::println("{}", nearest);
}
```

```text title="実行結果"
3.2
```

## 関数の詳しい説明

### max() {#max}

```cpp
static constexpr T max() noexcept;
```

- 型 T が表せる一番大きい値。int なら 2147483647

### lowest() {#lowest}

```cpp
static constexpr T lowest() noexcept;
```

- 一番小さい（マイナス方向に一番大きい）値。最大値を探すループの初期値に使います

### min() {#min}

```cpp
static constexpr T min() noexcept;
```

- 整数では一番小さい値（int なら -2147483648）。<strong>浮動小数点では「0 に一番近い正の数」</strong>なので、最大値探しの初期値に使うと間違えます

```cpp
#include <limits>
#include <print>

int main() {
  std::println("int: {} 〜 {}", std::numeric_limits<int>::min(), std::numeric_limits<int>::max());
  std::println("float min > 0？ {} / lowest < 0？ {}", std::numeric_limits<float>::min() > 0.0f,
               std::numeric_limits<float>::lowest() < 0.0f);
}
```

```text title="実行結果"
int: -2147483648 〜 2147483647
float min > 0？ true / lowest < 0？ true
```

### infinity() {#infinity}

```cpp
static constexpr T infinity() noexcept;
```

- 無限大。どんな有限の値よりも大きいので、`max()` の代わりの初期値にも使えます（浮動小数点のみ）

### epsilon() {#epsilon}

```cpp
static constexpr T epsilon() noexcept;
```

- 1.0 と、その次に表せる値の差。浮動小数点の「ほぼ等しい」の判定の目安になります。ただし値が大きいと誤差も大きくなるので、ゲームでは `0.0001f` のような決まった許容値を使うことが多いです

```cpp
#include <algorithm>
#include <cmath>
#include <limits>
#include <print>

bool NearlyEqual(double a, double b) {
  return std::abs(a - b) <= std::numeric_limits<double>::epsilon() * std::max(1.0, std::abs(a));
}

int main() {
  double x = 0.1 + 0.2;
  std::println("{} {}", x == 0.3, NearlyEqual(x, 0.3));
  std::println("{}", std::numeric_limits<float>::infinity() > 1e38f);
}
```

```text title="実行結果"
false true
true
```

### quiet_NaN() {#quiet_nan}

```cpp
static constexpr T quiet_NaN() noexcept;
```

- NaN（壊れた数）。「値が無い」を表すのに使われることもありますが、[`std::optional`](../utilities/optional.md) のほうが分かりやすいです

### digits10 {#digits10}

```cpp
static constexpr int digits10;
```

- 正しく表せる 10 進数の桁数。float は 6、double は 15。「float は 7 桁くらいしか正確でない」の根拠です

### is_signed {#is_signed}

```cpp
static constexpr bool is_signed;
```

- マイナスを表せる型か

### is_integer {#is_integer}

```cpp
static constexpr bool is_integer;
```

- 整数型か

### digits {#digits}

```cpp
static constexpr int digits;
```

- 整数なら値のビット数（int は 31）、浮動小数点なら仮数部のビット数（float は 24）

### has_infinity {#has_infinity}

```cpp
static constexpr bool has_infinity;
```

- 無限大を表せるか（浮動小数点は true、整数は false）

### denorm_min() {#denorm_min}

```cpp
static constexpr T denorm_min() noexcept;
```

- 一番小さい正の値（非正規化数）。計算がとても遅くなる値なので、ゲームでは出てこないようにすることがあります

```cpp
#include <cstdint>
#include <limits>
#include <print>

int main() {
  using F = std::numeric_limits<float>;
  using U = std::numeric_limits<std::uint8_t>;
  std::println("float: digits10 {} / digits {} / signed {} / integer {} / inf {}", F::digits10,
               F::digits, F::is_signed, F::is_integer, F::has_infinity);
  std::println("uint8: max {} / signed {}", U::max(), U::is_signed);
  std::println("{}", F::denorm_min() > 0.0f);
}
```

```text title="実行結果"
float: digits10 6 / digits 24 / signed true / integer false / inf true
uint8: max 255 / signed false
true
```

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    #include <climits>
    #include <cfloat>
    int a = INT_MAX;
    float b = FLT_MAX;
    ```

=== "今の書き方"

    ```cpp
    #include <limits>
    int a = std::numeric_limits<int>::max();
    float b = std::numeric_limits<float>::max();  // テンプレートの中でも型に合わせて使える
    ```

## ゲームでの使いどころ

最小値や最大値を探すループの初期値に使います。いちばん近い敵を探すとき、最初の距離に `std::numeric_limits<float>::max()` を入れておけば、最初の候補が必ず更新されます。

浮動小数点の比較では、`epsilon()` が目安になります。ただし `epsilon` は 1.0 付近の最小の差なので、値が大きいときは、それより大きな許容誤差が必要です。

無限大を `infinity()`、NaN を `quiet_NaN()` で作れます。「まだ値がない」を NaN で表す、というやり方もありますが、`std::optional` のほうが分かりやすくなります。浮動小数点の最小値は `lowest()` です。`min()` は最小の正の数なので、取り違えないようにします。

## よくあるミス

??? failure "float の min() を一番小さい値だと思う"
    `std::numeric_limits<float>::min()` は約 1.2e-38（正の数）です。一番マイナスの値は `lowest()` です。

??? failure "Windows で max() がマクロとぶつかる"
    `<windows.h>` の `max` マクロのせいでコンパイルエラーになります。`NOMINMAX` を定義するか、`(std::numeric_limits<int>::max)()` と書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大は max()、最小は lowest()
    - [x] float の min() は「一番小さい正の数」
    - [x] 無限大は infinity()

## 関連ページ

- [<cstdint>](cstdint.md)
- [cppreference: std::numeric_limits](https://en.cppreference.com/w/cpp/types/numeric_limits)

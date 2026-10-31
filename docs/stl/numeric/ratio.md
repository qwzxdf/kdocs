---
title: std::ratio
summary: "分数（1/3 など）を、型としてコンパイル時に表す。chrono の単位の土台。"
order: 41
tags:
  - 数値
---

# std::ratio

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

`std::chrono::milliseconds` と `std::chrono::seconds` を混ぜて計算しても、単位を自分で変換しなくて済みます。「ミリ秒は秒の 1000 分の 1」という関係を、型が覚えているからです。この関係を、コンパイル時の分数として表す部品が `std::ratio<分子, 分母>` です。分数の足し算や掛け算も、型の演算(`std::ratio_add<A, B>` など)として行い、結果の分子・分母を `num` と `den` で取り出します。`std::milli` や `std::kilo` のような、SI 接頭辞の別名もあります。

!!! tip "ポイント"
    - 分数は**型**。計算も比較も、コンパイル時に済む。実行時に変わる分数には使えない。
    - 約分された形で保存され、符号は分子につく(`ratio<1, -2>` は `-1/2`)。
    - `ratio<2, 4>` と `ratio<1, 2>` は別の型だが、`::type` を取ると同じ型になる。
    - 値が等しいかは `std::ratio_equal_v` で調べる。型の `==` は使えない。
    - 計算の途中で `std::intmax_t` を超えると、コンパイルエラーになる。

!!! info "このページを読む前に"
    [`std::chrono::duration`](../utilities/chrono/duration.md) の概要を先に読むと、`ratio` がどこで使われるかが分かります。テンプレート引数に値を渡す書き方は、[テンプレート](../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::ratio {#ratio}

```cpp
template <std::intmax_t Num, std::intmax_t Denom = 1>
struct ratio {
  static constexpr std::intmax_t num;
  static constexpr std::intmax_t den;
  using type = ratio<num, den>;
};
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `Num` | `std::intmax_t` | 分子 | (必須) |
| `Denom` | `std::intmax_t` | 分母 | 1 |

`num` と `den` は、`Num` と `Denom` を最大公約数で約分したあとの値です。符号は分子に寄せられるので、`den` は常に正です。

`Denom` を 0 にすると、コンパイルエラーです。値が実行時に決まる分母では使えません。

#### type

`ratio<2, 4>::type` は `ratio<1, 2>` です。約分された形の型を取り出すために使います。`ratio<2, 4>` と `ratio<1, 2>` 自体は別々の型なので、`std::is_same_v` では等しくなりません。値が等しいかを調べるときは、`std::ratio_equal_v` を使います。

#### 計算できる範囲

`num` と `den` は `std::intmax_t`(普通は 64 ビットの符号付き整数)です。計算の途中で、この範囲を超える分子や分母になると、コンパイルエラーです。実行時にあふれて壊れる、ということは起きません。

### 実際に動かす: 約分・計算・比較 {#basic}

```cpp
#include <print>
#include <ratio>
#include <type_traits>

int main() {
  // 約分されて保存される。符号は分子につく
  using Half = std::ratio<2, 4>;
  using NegHalf = std::ratio<1, -2>;
  std::println("ratio<2, 4>  = {}/{}", Half::num, Half::den);
  std::println("ratio<1, -2> = {}/{}", NegHalf::num, NegHalf::den);

  // ratio<2, 4> と ratio<1, 2> は、別の型だが、同じ値
  std::println("同じ型か: {}", std::is_same_v<Half, std::ratio<1, 2>>);
  std::println("::type は約分後の型: {}", std::is_same_v<Half::type, std::ratio<1, 2>>);
  std::println("値は等しいか: {}", std::ratio_equal_v<Half, std::ratio<1, 2>>);

  // 計算も型で行う
  using Sum = std::ratio_add<std::ratio<1, 3>, std::ratio<1, 6>>;       // 1/3 + 1/6
  using Prod = std::ratio_multiply<std::ratio<2, 3>, std::ratio<3, 4>>; // 2/3 * 3/4
  using Quot = std::ratio_divide<std::kilo, std::milli>;                // 1000 / (1/1000)
  std::println("1/3 + 1/6 = {}/{}", Sum::num, Sum::den);
  std::println("2/3 * 3/4 = {}/{}", Prod::num, Prod::den);
  std::println("kilo / milli = {}/{}", Quot::num, Quot::den);

  // 比較
  std::println("1/3 < 1/2: {}", std::ratio_less_v<std::ratio<1, 3>, std::ratio<1, 2>>);
}
```

```text title="実行結果"
ratio<2, 4>  = 1/2
ratio<1, -2> = -1/2
同じ型か: false
::type は約分後の型: true
値は等しいか: true
1/3 + 1/6 = 1/2
2/3 * 3/4 = 1/2
kilo / milli = 1000000/1
1/3 < 1/2: true
```

`ratio<1, -2>` が `-1/2` になるのは、符号が分子に寄るからです。`ratio_divide<kilo, milli>` は `1000` を `1/1000` で割るので `1000000/1` になります。

### 実際に動かす: chrono の単位として使う {#chrono}

`ratio` が最もよく使われる場所は `std::chrono::duration` です。`duration<Rep, Period>` の `Period` が、1 刻みが何秒かを表す `ratio` です。

```cpp
#include <chrono>
#include <print>
#include <ratio>

int main() {
  // 1 フレーム = 1/60 秒 を、時間の単位として定義する
  using Frame = std::chrono::duration<int, std::ratio<1, 60>>;
  std::println("Frame の周期: {}/{} 秒", Frame::period::num, Frame::period::den);

  Frame three{3};   // 3 フレーム
  auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(three);
  std::println("3 フレームは {} ミリ秒", ms.count());

  // ミリ秒を秒(double)に直す
  std::chrono::duration<double> sec = std::chrono::milliseconds(1500);
  std::println("1500 ミリ秒は {} 秒", sec.count());
}
```

```text title="実行結果"
Frame の周期: 1/60 秒
3 フレームは 50 ミリ秒
1500 ミリ秒は 1.5 秒
```

`Frame` は「1 刻みが 1/60 秒」の型です。3 フレームをミリ秒に直すと、3/60 秒 = 50 ミリ秒です。`duration_cast` が、`Frame` と `milliseconds` の `ratio` を割って、換算の係数をコンパイル時に決めています。

## ratio の計算・比較・SI 接頭辞

計算と比較は、それぞれ専用のテンプレートがあります。計算の結果は `ratio` 型で、比較は `bool`(`_v` 版)です。

| 名前 | 何をする |
| --- | --- |
| [`std::ratio_add`](ratio/ratio_add.md) | 2 つの `ratio` の足し算をコンパイル時に計算して `ratio` で返す。 |
| [`std::ratio_subtract`](ratio/ratio_subtract.md) | 2 つの `ratio` の引き算をコンパイル時に計算して `ratio` で返す。 |
| [`std::ratio_multiply`](ratio/ratio_multiply.md) | 2 つの `ratio` のかけ算をコンパイル時に計算して `ratio` で返す。 |
| [`std::ratio_divide`](ratio/ratio_divide.md) | 2 つの `ratio` の割り算をコンパイル時に計算して `ratio` で返す。 |
| [`std::ratio_equal`](ratio/ratio_equal.md) | 2 つの `ratio` を `==` で比べる(コンパイル時)。 |
| [`std::ratio_not_equal`](ratio/ratio_not_equal.md) | 2 つの `ratio` を `!=` で比べる(コンパイル時)。 |
| [`std::ratio_less`](ratio/ratio_less.md) | 2 つの `ratio` を `<` で比べる(コンパイル時)。 |
| [`std::ratio_less_equal`](ratio/ratio_less_equal.md) | 2 つの `ratio` を `<=` で比べる(コンパイル時)。 |
| [`std::ratio_greater`](ratio/ratio_greater.md) | 2 つの `ratio` を `>` で比べる(コンパイル時)。 |
| [`std::ratio_greater_equal`](ratio/ratio_greater_equal.md) | 2 つの `ratio` を `>=` で比べる(コンパイル時)。 |

SI 接頭辞の別名は、大きい側が `kilo`(1000)・`mega`(100 万)・`giga`(10 億)・`tera`(1 兆)・`peta`(1000 兆)・`exa`(100 京)、小さい側が `milli`(1/1000)・`micro`(1/100 万)・`nano`(1/10 億) です。そのほか `deca`(10)・`hecto`(100)・`deci`(1/10)・`centi`(1/100) があります。これらは `std::intmax_t` に収まる範囲までで、それ以上(`zetta` など)は、64 ビットの環境では定義されません。

| 名前 | 何をする |
| --- | --- |
| [`std::deca`](ratio/deca.md) | SI 接頭辞「deca」(10 倍)を表す `ratio` の別名。 |
| [`std::hecto`](ratio/hecto.md) | SI 接頭辞「hecto」(100 倍)を表す `ratio` の別名。 |
| [`std::kilo`](ratio/kilo.md) | SI 接頭辞「kilo」(1000 倍)を表す `ratio` の別名。 |
| [`std::mega`](ratio/mega.md) | SI 接頭辞「mega」(100 万倍)を表す `ratio` の別名。 |
| [`std::giga`](ratio/giga.md) | SI 接頭辞「giga」(10 億倍)を表す `ratio` の別名。 |
| [`std::tera`](ratio/tera.md) | SI 接頭辞「tera」(1 兆倍)を表す `ratio` の別名。 |
| [`std::peta`](ratio/peta.md) | SI 接頭辞「peta」(1000 兆倍)を表す `ratio` の別名。 |
| [`std::exa`](ratio/exa.md) | SI 接頭辞「exa」(100 京倍)を表す `ratio` の別名。 |
| [`std::deci`](ratio/deci.md) | SI 接頭辞「deci」(10 分の 1)を表す `ratio` の別名。 |
| [`std::centi`](ratio/centi.md) | SI 接頭辞「centi」(100 分の 1)を表す `ratio` の別名。 |
| [`std::milli`](ratio/milli.md) | SI 接頭辞「milli」(1000 分の 1)を表す `ratio` の別名。 |
| [`std::micro`](ratio/micro.md) | SI 接頭辞「micro」(100 万分の 1)を表す `ratio` の別名。 |
| [`std::nano`](ratio/nano.md) | SI 接頭辞「nano」(10 億分の 1)を表す `ratio` の別名。 |

## ゲームでの使いどころ

直接 `ratio` を書く場面は多くありません。出番は、`std::chrono::duration` に、ゲーム固有の単位を足したいときです。1 フレームを 1/60 秒とした `duration<int, std::ratio<1, 60>>` を定義しておくと、「3 フレーム待つ」を `Frame{3}` と書けて、ミリ秒との換算を型に任せられます。

型の関係を調べるときにも使います。`std::chrono::duration` のテンプレート引数が何秒を表すのか、`period::num` と `period::den` で確かめられます。

## よくあるミス

??? failure "実行時に決まる値を分子や分母にする"
    `ratio` の引数はテンプレート引数なので、コンパイル時に決まる定数だけです。実行時に変わる分数が必要なら、自作の分数クラスか、`double` を使います。

??? failure "ratio<2, 4> と ratio<1, 2> を同じ型だと思う"
    値は等しくても、別の型です。`std::is_same_v` では偽になります。値を比べるときは `std::ratio_equal_v` か、`::type` をそろえてから比べます。

??? failure "計算の結果があふれる"
    `std::intmax_t` を超える分子や分母になると、コンパイルエラーです。単位の大きなものどうし(`exa` と `atto` を掛ける、など)で起きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::chrono::duration`](../utilities/chrono/duration.md) | `ratio` を単位として使う |
| 自作の分数クラス | 実行時に値が変わる分数が必要なとき |

## コンパイラ対応

C++11 から使えます。`std::ratio_equal_v` のような `_v` 付きの変数テンプレートは C++17 からです。

## 関連ページ

- [cpprefjp: std::ratio](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::ratio](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

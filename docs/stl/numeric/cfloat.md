---
title: <cfloat>（小数の限界マクロ）
summary: "`FLT_EPSILON` など、小数型の精度・範囲を表す C 由来のマクロ。"
order: 31
tags:
  - 数値
---

# <cfloat>（小数の限界マクロ）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cfloat>`
</div>

`float` で `1.0f + 0.0000001f` を計算しても、`1.0f` のまま変わりません。`float` には、1 の次に表せる値が `1.0000001192…` で、その間は表せないからです。こういう浮動小数点数の限界(どこまで細かく、どこまで大きな値を表せるか)を、型ごとに C のマクロで教えてくれるのが `<cfloat>` です。1 の隣との差を表す `FLT_EPSILON`、最大値の `FLT_MAX`、確実に往復できる桁数の `FLT_DIG` などがあります。

!!! tip "ポイント"
    - `FLT_EPSILON` は約 1.19e-07、`DBL_EPSILON` は約 2.22e-16。**`1.0` 付近**での隣との差であり、大きな値の比較にそのまま使えない。
    - `float` は 2 の 24 乗(16,777,216)を超えると、整数を 1 ずつ数えられなくなる(`FLT_MANT_DIG` が 24)。
    - `FLT_DIG`(6)は「10 進から往復して失われない桁数」、`FLT_DECIMAL_DIG`(9)は「`float` を文字にして元に戻せる桁数」で、向きが違う。
    - `FLT_MIN` は最小の**正の正規化数**で、最小の有限値ではない(それは `-FLT_MAX`)。
    - 新しいコードでは、型に合わせて取れる `std::numeric_limits<float>::epsilon()` などを使ってもよい。

!!! info "このページを読む前に"
    [`std::numeric_limits`](limits.md) を先に読むと、同じ値を型ごとに取る書き方が分かります。

## マクロの詳しい説明

マクロは、`float` / `double` / `long double` ごとに、`FLT_`・`DBL_`・`LDBL_` の頭文字で 3 組あります。名前の後ろ（`EPSILON`、`MAX`、`DIG` …）が同じなら意味も同じで、対象の型だけが変わります。

浮動小数点数は、値を `符号 × 仮数 × 2^指数` の形で持ちます。仮数の桁数が精度を、指数の幅が範囲を決めます。

| 型 | 符号 | 指数 | 仮数(保存される桁) | 仮数の実効桁数(`MANT_DIG`) |
| --- | --- | --- | --- | --- |
| `float` | 1 ビット | 8 ビット | 23 ビット | 24 |
| `double` | 1 ビット | 11 ビット | 52 ビット | 53 |

仮数の先頭の「1」は、保存しなくても必ず 1 と決まっているので、保存されません。そのぶん実効桁数は、保存される桁数より 1 多くなります。

### <cfloat> {#cfloat}

```cpp
#include <cfloat>
```

`<cfloat>` は C 言語の `<float.h>` と同じ内容です。値は、コンパイル時に決まる定数式で、`static_assert` や配列の大きさにも使えます。

C++ では、同じ値を [`std::numeric_limits`](limits.md) から型ごとに取れます。`std::numeric_limits<float>::epsilon()` は `FLT_EPSILON` と同じ値です。テンプレートの中で、型 `T` に合わせた値が要るときは `numeric_limits<T>` を使い、型が決まっている所では、どちらでも構いません。

### FLT_RADIX {#FLT_RADIX}

```cpp
#define FLT_RADIX 2
```

指数の基数(何進数か)です。ほぼすべての環境で `2` です。浮動小数点が 2 進数である以上、`0.1` のような 10 進の小数は、ぴったりは表せません。

`float` と `double` で、基数は共通です。値の細かい性質を調べるコードを書かない限り、使うことはありません。

### FLT_MANT_DIG {#FLT_MANT_DIG}

```cpp
#define FLT_MANT_DIG 24
```

`float` の仮数の桁数です。基数 `FLT_RADIX` の何桁か、つまり、2 進で 24 桁です。

この値が、整数を正確に表せる範囲を決めます。`float` は 2 の 24 乗(16,777,216)までの整数を、すべて正確に表せます。それを超えると、奇数が表せなくなり、`16777216.0f + 1.0f` が `16777216.0f` に戻ります。

ゲームの経過時間を、`float` の秒やフレーム数で数え続けると、長時間の起動で精度が落ちる原因になります。60 フレーム／秒で毎フレーム 1 を足し続けると、約 77 時間で 2 の 24 乗を超えます。長く動くものは、`double` か `std::int64_t` で数えます。

### DBL_MANT_DIG {#DBL_MANT_DIG}

```cpp
#define DBL_MANT_DIG 53
```

`double` の仮数の桁数で、2 進で 53 桁です。2 の 53 乗(約 9.0 × 10^15)までの整数を、正確に表せます。`std::int64_t` の全範囲(約 9.2 × 10^18)は、`double` に収まりきりません。大きな ID やハッシュ値を、`double` に入れて持ち回ると、下の桁が壊れます。

### LDBL_MANT_DIG {#LDBL_MANT_DIG}

```cpp
#define LDBL_MANT_DIG /* 実装定義 */
```

`long double` の仮数の桁数です。MSVC では `long double` が `double` と同じで、53 です。GCC や Clang の x86 Linux では 64(80 ビットの拡張精度)、ARM64 の Linux では 113 のように、環境によって大きく違います。

ゲームの計算で `long double` を使うと、環境による結果の違いが出るので、避けるのが無難です。

### FLT_DIG {#FLT_DIG}

```cpp
#define FLT_DIG 6
```

10 進数で書いた小数を `float` に直し、また 10 進数に戻したとき、**元の桁を失わずに戻せる**最大の桁数です。`float` は 6 桁です。

「`float` で、小数点以下 6 桁まで正確」という意味ではなく、有効数字(最初の 0 でない桁から数えた桁数)が 6 桁、という意味です。表示の桁数を決めるとき、`float` の値を 7 桁以上で出しても、後ろの桁には意味がありません。

### DBL_DIG {#DBL_DIG}

```cpp
#define DBL_DIG 15
```

`double` の、10 進数で往復できる桁数で、15 桁です。ユーザーが入力した 15 桁までの小数は、`double` に入れて、同じ桁数で書き戻せば、元の数字になります。

### LDBL_DIG {#LDBL_DIG}

```cpp
#define LDBL_DIG /* 実装定義 */
```

`long double` の、10 進数で往復できる桁数です。MSVC では `double` と同じ 15 です。

### FLT_DECIMAL_DIG {#FLT_DECIMAL_DIG}

```cpp
#define FLT_DECIMAL_DIG 9
```

`FLT_DIG` とは逆向きの量です。`float` を 10 進の文字列に直し、また `float` に戻したとき、**元の値と同じビット列に戻る**ために必要な桁数です。`float` は 9 桁です。

セーブデータなどに `float` をテキストで書き出すときは、9 桁以上で書かないと、読み戻した値が元と少しずれます。`std::to_chars` は、必要最小の桁数で往復できる文字列を作るので、桁数を自分で決めなくて済みます。

### DBL_DECIMAL_DIG {#DBL_DECIMAL_DIG}

```cpp
#define DBL_DECIMAL_DIG 17
```

`double` を文字列にして戻すとき、元の値に戻るために必要な桁数で、17 桁です。`std::printf("%.17g", x)` のように使います。

### DECIMAL_DIG {#DECIMAL_DIG}

```cpp
#define DECIMAL_DIG /* 実装定義 */
```

浮動小数点数の最も広い型(`long double`)について、`FLT_DECIMAL_DIG` に相当する桁数です。MSVC では `long double` が `double` なので、17 です。C99 で追加されましたが、今の C では、型ごとの `FLT_DECIMAL_DIG`・`DBL_DECIMAL_DIG` が推奨されています。

### FLT_EPSILON {#FLT_EPSILON}

```cpp
#define FLT_EPSILON 1.19209290e-07F
```

`float` で、`1.0` と、その次に大きい表せる値との差です。機械イプシロンと呼ばれ、約 1.19 × 10^-7(2 の -23 乗)です。

「1 付近で、これより小さい差は、`float` では区別できない」という目安になります。2 つの `float` の差が `FLT_EPSILON` より小さければ、ほぼ同じ値とみなせる、と書くことが多いですが、これは `1.0` 付近の話です。100 のような大きな値では、隣り合う値の差も 100 倍に広がり、小さな値ではさらに細かくなります。

### DBL_EPSILON {#DBL_EPSILON}

```cpp
#define DBL_EPSILON 2.2204460492503131e-16
```

`double` で、`1.0` と次の値との差で、約 2.22 × 10^-16(2 の -52 乗)です。`FLT_EPSILON` と同じく、値が `1` に近いときの目安にしかなりません。

比較で使うときは、比べる値の大きさに合わせた相対的な許容誤差に直します。

```cpp
bool NearlyEqual(double a, double b) {
  double scale = std::max({1.0, std::abs(a), std::abs(b)});
  return std::abs(a - b) <= DBL_EPSILON * 8 * scale;   // 8 は、計算で溜まる誤差の余裕
}
```

`scale` を 1 以上にしているのは、`a` と `b` が 0 付近のとき、許容誤差が 0 に近づきすぎるのを避けるためです。8 は目安で、計算の回数が多いほど大きくします。

### LDBL_EPSILON {#LDBL_EPSILON}

```cpp
#define LDBL_EPSILON /* 実装定義 */
```

`long double` の機械イプシロンです。MSVC では `DBL_EPSILON` と同じです。

### FLT_MIN {#FLT_MIN}

```cpp
#define FLT_MIN 1.17549435e-38F
```

`float` で表せる、**最小の正の正規化数**です。約 1.18 × 10^-38 です。

「最小の正の数」ではないことに注意してください。これより小さい正の数は、非正規化数(サブノーマル)として、精度を落としながら表せます。`FLT_MIN` は、精度を落とさずに表せる最小値です。

### FLT_TRUE_MIN {#FLT_TRUE_MIN}

```cpp
#define FLT_TRUE_MIN 1.40129846e-45F
```

非正規化数まで含めた、`float` の最小の正の値です。約 1.4 × 10^-45 で、C++17 から使えます。`FLT_MIN` との間にある値は、精度が落ちており、計算も遅くなる環境があります。

値が小さくなりすぎて非正規化数にならないように、物理シミュレーションの減衰などでは、一定以下になったら 0 に切り捨てる、という対策をとります。

### FLT_HAS_SUBNORM {#FLT_HAS_SUBNORM}

```cpp
#define FLT_HAS_SUBNORM 1
```

`float` が非正規化数を持つかを表します。`1` で持つ、`0` で持たない、`-1` で不明です。ほとんどの環境で `1` です。DBL_ と LDBL_ の版もあります。

### DBL_MIN {#DBL_MIN}

```cpp
#define DBL_MIN 2.2250738585072014e-308
```

`double` の最小の正の正規化数で、約 2.23 × 10^-308 です。`FLT_MIN` と同じく、非正規化数は含みません。最小の正の値は `DBL_TRUE_MIN`(約 4.94 × 10^-324)です。

### LDBL_MIN {#LDBL_MIN}

```cpp
#define LDBL_MIN /* 実装定義 */
```

`long double` の最小の正の正規化数です。MSVC では `DBL_MIN` と同じです。

### FLT_MAX {#FLT_MAX}

```cpp
#define FLT_MAX 3.40282347e+38F
```

`float` で表せる最大の有限値で、約 3.4 × 10^38 です。これを超える計算の結果は、無限大(`INFINITY`)になります。

「最小値」ではなく、`-FLT_MAX` が最小の有限値です。`FLT_MIN` は、最小の**正の**値なので、混同しないようにします。

最大値として使うときの典型は、最小値を探すループの初期値です。

```cpp
float nearest = FLT_MAX;   // どんな距離より大きい値から始める
for (float d : distances) nearest = std::min(nearest, d);
```

`FLT_MAX` の加算は、無限大になります。`FLT_MAX + 1.0f` は `FLT_MAX` のままですが、`FLT_MAX * 2.0f` は無限大です。

### DBL_MAX {#DBL_MAX}

```cpp
#define DBL_MAX 1.7976931348623157e+308
```

`double` で表せる最大の有限値で、約 1.8 × 10^308 です。`double` の最大値は、`float` の最大値とは桁違いに大きく、`DBL_MAX` を `float` に直そうとすると、無限大になります。

### LDBL_MAX {#LDBL_MAX}

```cpp
#define LDBL_MAX /* 実装定義 */
```

`long double` で表せる最大の有限値です。MSVC では `DBL_MAX` と同じです。

### FLT_MIN_EXP と FLT_MAX_EXP {#FLT_EXP}

```cpp
#define FLT_MIN_EXP -125
#define FLT_MAX_EXP 128
```

`FLT_RADIX` を何乗まで表せるかを表します。`FLT_MIN` は `2^(FLT_MIN_EXP - 1)`、つまり 2 の -126 乗です。`FLT_MAX` は、2 の `FLT_MAX_EXP` 乗(2 の 128 乗)に、ほぼ届く値です。`DBL_` 版は、-1021 と 1024 です。

10 進で表した版は `FLT_MIN_10_EXP`(-37)・`FLT_MAX_10_EXP`(38)で、`DBL_` 版は -307 と 308 です。数値を表示する桁数を決めるときなどに使いますが、普通のコードでは必要ありません。

### FLT_ROUNDS {#FLT_ROUNDS}

```cpp
#define FLT_ROUNDS 1
```

加算などの結果を、どの向きに丸めるかを表します。

| 値 | 丸め方向 |
| --- | --- |
| `-1` | 不明 |
| `0` | 0 に向けて切り捨て |
| `1` | 最も近い値へ(同じ近さなら偶数へ) |
| `2` | 正の無限大へ |
| `3` | 負の無限大へ |

ほとんどの環境の既定は `1` で、MSVC でも `1` でした。丸め方向を実行中に切り替えられる環境では、実行時の値を知りたいなら、[`fegetround`](fegetround.md) を使います。

### FLT_EVAL_METHOD {#FLT_EVAL_METHOD}

```cpp
#define FLT_EVAL_METHOD 0
```

式を計算するときの内部の精度を表します。

| 値 | 意味 |
| --- | --- |
| `0` | 型どおりの精度で計算する(`float` は `float` で) |
| `1` | `float` と `double` の式を、`double` で計算する |
| `2` | すべて `long double` で計算する |
| `-1` | 不明 |

x64 の MSVC は `0` です。古い 32 ビット x86 の x87 命令を使う環境では、`2` になり、同じコードでも、結果の下の桁が変わることがありました。環境による結果の違いを疑うときは、この値を確かめます。

## 実際に動かしてみる

```cpp
#include <cfloat>
#include <cmath>
#include <print>

int main() {
  // 1 のすぐ隣の値との差(機械イプシロン)
  std::println("FLT_EPSILON = {}", FLT_EPSILON);
  std::println("DBL_EPSILON = {}", DBL_EPSILON);

  // 表せる範囲
  std::println("FLT_MAX = {}", FLT_MAX);
  std::println("FLT_MIN = {}", FLT_MIN);
  std::println("FLT_TRUE_MIN = {}", FLT_TRUE_MIN);
  std::println("DBL_MAX = {}", DBL_MAX);
  std::println("DBL_MIN = {}", DBL_MIN);

  // 桁数
  std::println("FLT_DIG = {}, FLT_DECIMAL_DIG = {}, FLT_MANT_DIG = {}", FLT_DIG, FLT_DECIMAL_DIG, FLT_MANT_DIG);
  std::println("DBL_DIG = {}, DBL_DECIMAL_DIG = {}, DBL_MANT_DIG = {}", DBL_DIG, DBL_DECIMAL_DIG, DBL_MANT_DIG);

  // 型と環境
  std::println("FLT_RADIX = {}, FLT_ROUNDS = {}, FLT_EVAL_METHOD = {}", FLT_RADIX, FLT_ROUNDS, FLT_EVAL_METHOD);
  std::println("long double は double と同じ幅: {}", LDBL_MANT_DIG == DBL_MANT_DIG);

  // float で整数を数えると、2 の 24 乗で止まる
  float count = 16777216.0f;   // 2 の 24 乗
  std::println("16777216 + 1 == 16777216 (float): {}", count + 1.0f == count);
}
```

```text title="実行結果（MSVC）"
FLT_EPSILON = 1.1920929e-07
DBL_EPSILON = 2.220446049250313e-16
FLT_MAX = 3.4028235e+38
FLT_MIN = 1.1754944e-38
FLT_TRUE_MIN = 1e-45
DBL_MAX = 1.7976931348623157e+308
DBL_MIN = 2.2250738585072014e-308
FLT_DIG = 6, FLT_DECIMAL_DIG = 9, FLT_MANT_DIG = 24
DBL_DIG = 15, DBL_DECIMAL_DIG = 17, DBL_MANT_DIG = 53
FLT_RADIX = 2, FLT_ROUNDS = 1, FLT_EVAL_METHOD = 0
long double は double と同じ幅: true
16777216 + 1 == 16777216 (float): true
```

`long double` の幅や `FLT_EVAL_METHOD` は、環境によって違う値になります。

## ゲームでの使いどころ

浮動小数点数の比較に使う許容誤差の目安(`EPSILON`)と、「十分に大きな初期値」(`MAX`)が、主な出番です。最小値を探すループの初期値には `FLT_MAX` を使います。座標を `float` で持つとき、原点から遠く離れる(数万メートル以上)と、隣り合う表せる値の間隔が広がり、見た目にがたつきが出ます。その限界の見積もりに、`FLT_EPSILON` を使います。`1.0` の隣との差が `FLT_EPSILON` なら、値が `x` のときの隣との差は、およそ `x * FLT_EPSILON` です。

セーブデータやログに `float` をテキストで書くときは、`FLT_DECIMAL_DIG`(9)桁以上で出します。

## よくあるミス

??? failure "EPSILON を、どんな値にも使える許容誤差にする"
    `FLT_EPSILON` は、`1.0` 付近での隣との差です。値が 1000 なら、隣との差は約 1000 倍(1.2e-4)になるので、`std::abs(a - b) < FLT_EPSILON` は、ほぼ「完全に同じ」でないと真になりません。値の大きさに合わせた相対的な許容誤差を使います。

??? failure "FLT_MIN を最小の値だと思う"
    `FLT_MIN` は最小の正の正規化数です。負の側の最小は `-FLT_MAX` です。0 に最も近い正の値が必要なら `FLT_TRUE_MIN` です。

??? failure "float で長時間の数えをする"
    2 の 24 乗を超えると、1 を足しても値が変わりません。60 フレーム／秒で、約 77 時間で届きます。`double` か `std::int64_t` で数えます。

??? failure "FLT_DIG と FLT_DECIMAL_DIG を取り違える"
    `FLT_DIG`(6)は 10 進から `float` を経由して戻したときに失われない桁数、`FLT_DECIMAL_DIG`(9)は `float` から 10 進へ出して `float` に戻したときに元のビット列に戻る桁数です。ファイルに書き出すなら後者です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型ごとに取る C++ の書き方。テンプレートの中で、型 `T` の限界を取れる |
| [`<climits>`](climits.md) | 整数の限界のマクロ |
| [`std::fegetround`](fegetround.md) | 丸め方向を実行時に調べる |

## コンパイラ対応

C++98 から使えます。`FLT_TRUE_MIN`・`FLT_DECIMAL_DIG`・`FLT_HAS_SUBNORM` などは C++17 で加わりました。`long double` の幅と `FLT_EVAL_METHOD` は、環境によって違います。

## 関連ページ

- [cpprefjp: <cfloat>（小数の限界マクロ）](https://cpprefjp.github.io/reference/cfloat.html)
- [cppreference: <cfloat>（小数の限界マクロ）](https://en.cppreference.com/w/cpp/types/climits)

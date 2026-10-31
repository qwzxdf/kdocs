---
title: std::complex
summary: "複素数（実部 + 虚部）。回転・波・フーリエ変換に。"
order: 40
tags:
  - 数値
---

# std::complex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <complex>`
</div>

2D のキャラクターを原点のまわりに回転させるとき、`x' = x cosθ - y sinθ`、`y' = x sinθ + y cosθ` と書くのは、少し面倒です。点を複素数 `x + yi` として持つと、同じ回転が「大きさ 1・角度 θ の複素数を掛ける」だけで書けます。`std::complex<T>` は、実部と虚部を持つ複素数のクラスで、四則演算がふつうの数と同じ書き方で使えます。

!!! tip "ポイント"
    - 複素数は `x + yi`。2D の座標を `complex` で持つと、**回転は `std::polar(1.0, θ)` を掛けるだけ**になる。
    - `std::abs(z)` が大きさ、`std::arg(z)` が角度(ラジアン)、`std::norm(z)` が大きさの 2 乗。
    - 型は `float`・`double`・`long double` だけが保証される。`std::complex<int>` は使えない。
    - 大小比較(`<`)は定義されていない。比べられるのは `==` と `!=` だけ。
    - 3D の回転には複素数ではなくクォータニオン(SimpleMath の `Quaternion`)を使う。

!!! info "このページを読む前に"
    三角関数と、ラジアンの扱いが分かると読みやすくなります。[`std::sin`](cmath/sin.md) や [`std::numbers::pi`](numbers.md) を先に見ておくと、角度の話が追いやすくなります。

## 関数の詳しい説明

### std::complex {#complex}

```cpp
template <class T>
class complex {
 public:
  using value_type = T;
  constexpr complex(T re = T(), T im = T());
  constexpr T real() const;
  constexpr T imag() const;
  constexpr void real(T value);
  constexpr void imag(T value);
};
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `re` | `T` | 実部 | 0 |
| `im` | `T` | 虚部 | 0 |

`T` に使えるのは `float`・`double`・`long double` です。`std::complex<int>` のような整数の複素数は、規格が動作を保証していません。コンパイルできても、`std::abs` などが期待どおりに動くとは限りません。整数の座標を回すだけなら、`x` と `y` を別々に持つか、自作の構造体を使います。

#### 作る

```cpp
std::complex<double> a(3.0, 4.0);   // 3 + 4i
std::complex<double> b = 5.0;       // 5 + 0i (実数から作ると、虚部は 0)
std::complex<double> c;             // 0 + 0i
```

`<complex>` を読み込み、`using namespace std::complex_literals;` を書くと、`3.0 + 4.0i` のようなリテラルが使えます。`i` が `double`、`if` が `float`、`il` が `long double` です。

#### 実部と虚部を取る

`real()` と `imag()` で取り出します。引数を渡すと(`z.real(3.0)`)、その値に書き換えます。

#### 四則演算

`+`・`-`・`*`・`/` と、`+=` などの複合代入が使えます。掛け算は `(a+bi)(c+di) = (ac-bd) + (ad+bc)i` です。複素数と実数を混ぜた計算(`z * 2.0`)も書けます。

割り算は、実装によって、分母が 0 に近いときの扱いを丁寧にしているため、掛け算より時間がかかります。

#### 比較

`==` と `!=` は使えますが、`<` や `>` は定義されていません。複素数には、大小の自然な順序がないからです。大きさで並べたいときは、`std::abs` か `std::norm` で比べます。

浮動小数点数なので、`==` は完全に同じビットでないと真になりません。回転を繰り返した結果が、元の点と一致するかを `==` で調べるのは避けます。

#### メモリ上の配置

`sizeof(std::complex<double>)` は `double` 2 個分(16 バイト)で、メモリ上は「実部、虚部」の順に並んでいます。規格が、`double[2]` として扱ってよいと保証しているので、C の API や GPU に渡す配列は、`reinterpret_cast<double*>` でそのまま渡せます。

#### 数学関数

`std::sqrt`・`std::exp`・`std::log`・`std::pow`・`std::sin`・`std::cos` などが、複素数にも用意されています。たとえば `std::sqrt(std::complex<double>(-1.0, 0.0))` は `i` になります。実数の `std::sqrt(-1.0)` は NaN ですが、複素数なら答えが出ます。

### 実際に動かす: 四則演算と大きさ {#basic}

最初は、リテラルで複素数を作り、四則演算と、`abs`・`norm`・`conj` を試します。

```cpp
#include <complex>
#include <print>

int main() {
  using namespace std::complex_literals;   // 3.0i のようなリテラルを使う

  std::complex<double> a = 3.0 + 4.0i;     // 3 + 4i
  std::complex<double> b(1.0, -2.0);       // 1 - 2i

  auto sum = a + b;
  auto prod = a * b;   // (3+4i)(1-2i) = 3 - 6i + 4i - 8i^2 = 11 - 2i
  std::println("a + b = ({}, {})  (実部, 虚部)", sum.real(), sum.imag());
  std::println("a * b = ({}, {})", prod.real(), prod.imag());

  std::println("|a| = {}", std::abs(a));       // 大きさ: 5
  std::println("norm(a) = {}", std::norm(a));  // 大きさの 2 乗: 25
  auto c = std::conj(a);                       // 共役: 3 - 4i
  std::println("conj(a) = ({}, {})", c.real(), c.imag());
  std::println("a * conj(a) = {}", (a * c).real());   // 実数になる(= norm)

  std::println("a == a: {}", a == a);
}
```

```text title="実行結果"
a + b = (4, 2)  (実部, 虚部)
a * b = (11, -2)
|a| = 5
norm(a) = 25
conj(a) = (3, -4)
a * conj(a) = 25
a == a: true
```

`a * conj(a)` の虚部が消えて、実数の `norm(a)`(25)と同じになるのは、共役を掛けると虚部が打ち消し合うからです。

### 実際に動かす: 2D の回転 {#rotate}

次は、点 `(1, 0)` を 4 つの角度で回します。角度 θ の複素数は `std::polar(1.0, θ)`、つまり `cosθ + i sinθ` なので、掛けるだけで回転になります。

```cpp
#include <cmath>
#include <complex>
#include <numbers>
#include <print>

// 浮動小数点の誤差で出る -0.000 を避けるための表示用
double Clean(double x) { return std::abs(x) < 1e-9 ? 0.0 : x; }

int main() {
  std::complex<double> pos(1.0, 0.0);   // x = 1, y = 0 の点

  // 角度 theta の回転は、大きさ 1・角度 theta の複素数を掛けるだけ
  for (int degree : {0, 90, 180, 270}) {
    double theta = degree * std::numbers::pi / 180.0;
    std::complex<double> rotated = pos * std::polar(1.0, theta);
    std::println("{:3}度: ({:.3f}, {:.3f})", degree, Clean(rotated.real()), Clean(rotated.imag()));
  }
}
```

```text title="実行結果"
  0度: (1.000, 0.000)
 90度: (0.000, 1.000)
180度: (-1.000, 0.000)
270度: (0.000, -1.000)
```

`Clean` は、浮動小数点の誤差で出る `-0.000` を、表示のときに 0 にするための関数です。回転の計算自体には要りません。

### 実際に動かす: マンデルブロ集合 {#mandelbrot}

複素数の平面で `z = z*z + c` を繰り返すと、`c` によって、すぐ発散するものと、永遠に発散しないものに分かれます。発散しない `c` の集まりがマンデルブロ集合です。発散するまでの回数で色を付けると、フラクタルの図になります。

```cpp
#include <complex>
#include <print>

// c が マンデルブロ集合に入るかを調べる: z = z*z + c を繰り返し、|z| が 2 を超えたら発散
int EscapeCount(std::complex<double> c, int max_iter) {
  std::complex<double> z = 0;
  for (int i = 1; i <= max_iter; ++i) {
    z = z * z + c;
    if (std::norm(z) > 4.0) return i;   // |z| > 2 と同じ。平方根を避けるため norm で比べる
  }
  return max_iter;
}

int main() {
  std::println("c = 0:  {} 回", EscapeCount(0.0, 50));
  std::println("c = 1:  {} 回", EscapeCount(1.0, 50));
  std::println("c = -1: {} 回", EscapeCount(-1.0, 50));
  std::println("c = 2:  {} 回", EscapeCount(2.0, 50));
}
```

```text title="実行結果"
c = 0:  50 回
c = 1:  3 回
c = -1: 50 回
c = 2:  2 回
```

`c = 0` と `c = -1` は発散しないので、最大回数(50)まで回ります。`c = 1` は `0, 1, 2, 5, …` と増えて、3 回目で `|z|` が 2 を超えます。`std::abs(z) > 2.0` の代わりに `std::norm(z) > 4.0` で比べているのは、平方根の計算を避けるためです。

## 複素数の関数

引数に複素数を取る専用の関数です。それぞれのページで、引数と戻り値、落とし穴を説明しています。

| 名前 | 何をする |
| --- | --- |
| [`std::arg`](complex/arg.md) | 複素数の偏角(実軸からの角度)をラジアンで返す。 |
| [`std::conj`](complex/conj.md) | 共役複素数(虚部の符号を反転したもの)を返す。 |
| [`std::imag`](complex/imag.md) | 複素数の虚部を取り出す。 |
| [`std::norm`](complex/norm.md) | 複素数の大きさの 2 乗を返す。 |
| [`std::polar`](complex/polar.md) | 大きさと角度から複素数を作る。 |
| [`std::proj`](complex/proj.md) | 複素数をリーマン球面への射影に直す(無限大の扱いをそろえる)。 |
| [`std::real`](complex/real.md) | 複素数の実部を取り出す。 |

大きさを返す `std::abs` は、整数や実数の `abs` と同じ名前ですが、複素数の引数では、`sqrt(real² + imag²)` を返します。内部でオーバーフローしにくい計算をするので、[`std::hypot`](cmath/hypot.md) と同じ考え方です。

## ゲームでの使いどころ

2D の回転と、波を扱う場面が主な出番です。キャラクターや弾の向きを `complex<float>` の単位ベクトルで持ち、回転は `dir *= std::polar(1.0f, delta_angle)` と書けます。三角関数を毎回呼ばなくて済み、角度から方向を取る(`cos`・`sin` の両方)手間が 1 回の掛け算になります。

波形の分析(フーリエ変換)でも使います。音のスペクトル表示や、水面の波のシミュレーションでは、周波数ごとの成分を複素数で扱います。フーリエ変換自体は標準ライブラリにはないので、自作するか、外部ライブラリを使います。

頂点を 3D で回すときは、複素数ではなくクォータニオンを使います。

## よくあるミス

??? failure "3D の回転に使う"
    複素数が表せるのは平面の回転だけです。3D の回転は、複素数を拡張したクォータニオン(SimpleMath の `Quaternion`)を使います。

??? failure "std::complex<int> を使う"
    規格が保証するのは `float`・`double`・`long double` だけです。整数の座標で回したいなら、いったん `double` に直します。

??? failure "complex どうしを < で比べる"
    定義されていないのでコンパイルエラーです。大きさで比べるなら `std::abs` か `std::norm` を使います。

??? failure "回転を繰り返して、元に戻るかを == で調べる"
    浮動小数点の誤差が溜まって、完全には戻りません。`std::abs(a - b) < 許容誤差` で比べます。また、回転を何千回も繰り返すと、大きさが少しずつ変わってくるので、必要に応じて `z / std::abs(z)` で長さを 1 に直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hypot`](cmath/hypot.md) | 実数 2 つの大きさだけが欲しいときの関数 |
| [`std::valarray`](../containers/valarray.md) | 数値の配列。`complex` を要素にもできる |
| SimpleMath の `Quaternion` | 3D の回転を表す |

## コンパイラ対応

C++98 から使えます。`constexpr` の対応は C++14 から(`real()` と `imag()` の setter は C++20 から)です。複素数リテラル(`3.0i`)は C++14 からです。

## 関連ページ

- [cpprefjp: std::complex](https://cpprefjp.github.io/reference/complex/complex.html)
- [cppreference: std::complex](https://en.cppreference.com/w/cpp/numeric/complex)

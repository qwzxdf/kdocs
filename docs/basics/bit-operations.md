---
title: ビット演算
tags:
  - 基礎
---

# ビット演算

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

整数は、コンピューターの中では、<strong>0 と 1 の並び（ビット）</strong>です。`&`・`|`・`^`・`~`・`<<`・`>>` の演算子で、そのビットを 1 つずつ、直接、読んだり、書き換えたりできます。ゲームでは、当たり判定のレイヤー、状態のフラグ、色のパッキング、メモリの切り上げ、シェーダーの定数など、あちこちで、出てきます。

!!! tip "ポイント"
    - ビット演算は、整数を、ビットの集まりとして、扱う道具。`&`（両方 1）、`|`（どちらか 1）、`^`（違うと 1）、`~`（反転）、`<<` `>>`（ずらす）。
    - フラグは、`1u << n` で作り、立てる `|=`、落とす `&= ~`、判定 `&`、反転 `^=` の 4 つで、操作する。
    - <strong>`a & b == c` は、`==` が先に評価される。</strong> 必ず括弧を付ける。
    - `uint8_t` などの小さい型は、演算の前に `int` に変わる（整数昇格）。`~` や `<<` の結果を、型に戻すのを、忘れない。
    - ビット数以上のシフト（`1u << 32`）は、未定義動作。数える・回す処理は、自分で書かずに、`<bit>` を使う。

## 基本

### 2 進数と 16 進数

ビット演算では、2 進数（`0b…`）と、16 進数（`0x…`）で、数を書きます。16 進数の 1 桁は、2 進数のちょうど 4 桁に、対応するので、長いビット列を、短く書けます。

| 10 進数 | 2 進数 | 16 進数 |
| --- | --- | --- |
| 5 | `0b0101` | `0x5` |
| 10 | `0b1010` | `0xA` |
| 202 | `0b1100'1010` | `0xCA` |
| 255 | `0b1111'1111` | `0xFF` |

C++14 から、数値リテラルの途中に、`'` を入れて、桁を区切れます（`0b1100'1010`、`0xFF'FF`、`1'000'000`）。ビット列は、4 桁ごとに、区切ると、読めます。

### 6 つの演算子

| 演算子 | 名前 | 動き |
| --- | --- | --- |
| `a & b` | AND（論理積） | 両方が 1 のビットだけ 1 |
| `a \| b` | OR（論理和） | どちらかが 1 のビットが 1 |
| `a ^ b` | XOR（排他的論理和） | 違うビットが 1 |
| `~a` | NOT（ビット反転） | 0 と 1 を入れ替える |
| `a << n` | 左シフト | ビットを左へ n 個ずらす（右から 0 が入る。2 の n 乗を掛けるのと同じ） |
| `a >> n` | 右シフト | ビットを右へ n 個ずらす（2 の n 乗で割るのと同じ） |

```cpp
#include <cstdint>
#include <print>

int main() {
  std::uint8_t a = 0b1100'1010;  // 202
  std::uint8_t b = 0b0101'0110;  // 86

  // 1 ビットずつ、上下に並べて、演算する。
  //   a     = 1100 1010
  //   b     = 0101 0110
  std::println("a & b  = {:08b}", a & b);                                  // 両方 1 → 0100 0010
  std::println("a | b  = {:08b}", a | b);                                  // どちらか 1 → 1101 1110
  std::println("a ^ b  = {:08b}", a ^ b);                                  // 違う → 1001 1100
  std::println("~a     = {:08b}", static_cast<std::uint8_t>(~a));          // 反転 → 0011 0101
  std::println("a << 1 = {:08b}", static_cast<std::uint8_t>(a << 1));      // 左へ 1 → 1001 0100（あふれた上位は消える）
  std::println("a >> 2 = {:08b}", a >> 2);                                 // 右へ 2 → 0011 0010
}
```

```text title="実行結果"
a & b  = 01000010
a | b  = 11011110
a ^ b  = 10011100
~a     = 00110101
a << 1 = 10010100
a >> 2 = 00110010
```

`~a` と `a << 1` に、`static_cast<std::uint8_t>` を付けているのは、次の「整数昇格」のためです。

### 整数昇格：小さい型は、計算の前に int になる

`uint8_t` や `short` は、`&` や `<<` などの演算の前に、`int` に変換されます（整数昇格）。結果も `int` です。

```cpp
std::uint8_t a = 0b1100'1010;
auto x = ~a;       // x は int。~(int)202 = -203。上位ビットが、全部 1 になる
auto y = a << 1;   // y は int。404（0b1'1001'0100）。8 ビットに収まらない
```

8 ビットの結果が、欲しいときは、`static_cast<std::uint8_t>(…)`（または `& 0xFF`）で、型に戻します。戻さないと、`~a` が負の数になって、比較（`~a == 0x35`）が、期待と違う結果になります。

## 詳しく

### フラグ：1 つの整数に、複数のオン・オフを入れる

1 ビットを、1 つの「オン・オフ」に、割り当てると、32 個のフラグを、1 つの `uint32_t` に入れられます。当たり判定のレイヤー、キャラの状態、描画のオプションなどに、使います。

各フラグの値は、`1u << 番号` で作ります（`1u` は `unsigned int` の 1）。

```cpp
enum class Layer : std::uint32_t {
  kNone   = 0,
  kPlayer = 1u << 0,   // 0001
  kEnemy  = 1u << 1,   // 0010
  kWall   = 1u << 2,   // 0100
  kBullet = 1u << 3,   // 1000
};
```

`enum class` は、`|` や `&` が、そのままでは使えないので、演算子を、定義します。

```cpp
#include <cstdint>
#include <print>
#include <utility>

enum class Layer : std::uint32_t {
  kNone = 0,
  kPlayer = 1u << 0,
  kEnemy = 1u << 1,
  kWall = 1u << 2,
  kBullet = 1u << 3,
};

// enum class に、ビット演算を使えるようにする。std::to_underlying は、中の整数を取り出す（C++23）。
constexpr Layer operator|(Layer a, Layer b) {
  return static_cast<Layer>(std::to_underlying(a) | std::to_underlying(b));
}
constexpr Layer operator&(Layer a, Layer b) {
  return static_cast<Layer>(std::to_underlying(a) & std::to_underlying(b));
}
constexpr Layer operator~(Layer a) {
  return static_cast<Layer>(~std::to_underlying(a));
}

// フラグが 1 つでも立っているか。
constexpr bool Has(Layer mask, Layer flag) {
  return (mask & flag) != Layer::kNone;
}

int main() {
  Layer mask = Layer::kPlayer | Layer::kWall;                       // 立てる: プレイヤーと壁
  std::println("mask       = {:04b}", std::to_underlying(mask));    // 0101
  std::println("has enemy  = {}", Has(mask, Layer::kEnemy));        // 敵は、立っていない
  std::println("has wall   = {}", Has(mask, Layer::kWall));         // 壁は、立っている

  mask = mask | Layer::kEnemy;                                      // 敵を、立てる
  std::println("add enemy  = {:04b}", std::to_underlying(mask));    // 0111

  mask = mask & ~Layer::kPlayer;                                    // プレイヤーを、落とす
  std::println("del player = {:04b}", std::to_underlying(mask));    // 0110
}
```

```text title="実行結果"
mask       = 0101
has enemy  = false
has wall   = true
add enemy  = 0111
del player = 0110
```

操作は、次の 4 つの型に、決まっています（`flags` は整数、`kFlag` は 1 つのフラグ）。

| やりたいこと | 書き方 | 仕組み |
| --- | --- | --- |
| 立てる（オンにする） | `flags \|= kFlag;` | OR で、そのビットを 1 にする。ほかは、変わらない |
| 落とす（オフにする） | `flags &= ~kFlag;` | `~kFlag` は、そのビットだけ 0。AND で、そのビットだけ 0 になる |
| 判定する | `(flags & kFlag) != 0` | AND で、そのビットだけ取り出し、0 でないか見る |
| 反転する | `flags ^= kFlag;` | XOR で、そのビットだけ、入れ替わる |

複数のフラグを、まとめて、判定するときは、「全部立っているか」と「どれか立っているか」を、区別します。

```cpp
constexpr std::uint32_t kBoth = kPlayer | kEnemy;
bool any = (flags & kBoth) != 0;        // どちらか 1 つでも立っている
bool all = (flags & kBoth) == kBoth;    // 両方とも立っている
```

### 優先順位の罠：括弧を付ける

ビット演算子は、比較演算子（`==`、`!=`）より、優先順位が低いので、括弧を付けないと、意図と違う順で、評価されます。

```cpp
if (flags & kWall == 0) { ... }     // 間違い！ flags & (kWall == 0) と読まれる
if ((flags & kWall) == 0) { ... }   // 正しい
```

最初の式は、`kWall == 0`（偽 = 0）を先に計算し、`flags & 0` になるので、いつも偽です。コンパイラが警告を出すこともありますが、出ないこともあります。ビット演算は、いつも括弧で囲むと決めておきます。

### シフトの落とし穴

| 書き方 | 結果 |
| --- | --- |
| `1u << 31` | OK（`unsigned` の最上位ビット） |
| `1u << 32` | 未定義動作（`unsigned` は 32 ビットなので、32 以上は、ずらせない） |
| `1 << 31` | C++20 以降は、`int` の最上位ビットが立つ（負の数）。型が `int` なので、`1u` にしたほうが、安全 |
| `x << -1` | 未定義動作（負の数だけ、ずらす） |
| `-8 >> 1` | C++20 以降は、符号を保つ（算術シフト）で `-4` |

ずらす数 `n` が、変数のときは、`n` が、ビット数未満であることを、確かめます。64 ビットの値を、作りたいときは、`1ull << n` にします（`1` のままだと `int` で、31 を超えると、あふれる）。

```cpp
std::uint64_t bit = 1ull << 40;   // OK。1 << 40 は int で、あふれる（未定義動作）
```

ビット演算は、符号なし整数（`uint32_t` など）で、行うのが、基本です。符号付きの、負の数は、表現（2 の補数）の理解が、必要で、バグの元になりやすいので、避けます。

### 標準ライブラリ `<bit>`（C++20）

ビットを数えたり、回したりする処理は、自分で、ループで書かずに、`<bit>` の関数を、使います。CPU の、専用命令に、変換され、速いからです（詳しくは [<bit>](../stl/numeric/bit.md)）。

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::println("popcount(0b1011'0110)    = {}", std::popcount(0b1011'0110u));            // 立っているビットの数
  std::println("countl_zero(0b0001'0000) = {}", std::countl_zero(std::uint8_t{0b0001'0000}));  // 上から連続する 0 の数
  std::println("countr_zero(40)          = {}", std::countr_zero(40u));                  // 下から連続する 0 の数（40 = 101000）
  std::println("bit_width(37)            = {}", std::bit_width(37u));                    // 必要なビット数（37 = 100101）
  std::println("bit_ceil(37)             = {}", std::bit_ceil(37u));                     // 以上の最小の 2 のべき乗
  std::println("has_single_bit(64)       = {}", std::has_single_bit(64u));               // 2 のべき乗か
  std::println("has_single_bit(37)       = {}", std::has_single_bit(37u));
  std::println("rotl(0b1000'0001, 1)     = {:08b}", std::rotl(std::uint8_t{0b1000'0001}, 1));  // 左へ回す（あふれた分が右へ戻る）
}
```

```text title="実行結果"
popcount(0b1011'0110)    = 5
countl_zero(0b0001'0000) = 3
countr_zero(40)          = 3
bit_width(37)            = 6
bit_ceil(37)             = 64
has_single_bit(64)       = true
has_single_bit(37)       = false
rotl(0b1000'0001, 1)     = 00000011
```

`<bit>` の関数は、符号なし整数だけを、受け取ります。`countl_zero` は、型の幅で、結果が変わる（`uint8_t` で 3、`uint32_t` なら 27）ので、型を、はっきりさせます。

### `std::bit_cast`：ビット列を、そのまま別の型に

`float` のビット列を、整数として、見たいときに、`reinterpret_cast` や、ポインタの、キャストを使うと、未定義動作になります。`std::bit_cast`（C++20）は、値のビット列を、そのまま、別の型として、取り出します。

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  float f = 1.0f;
  std::uint32_t bits = std::bit_cast<std::uint32_t>(f);   // 1.0f のビット列を、整数として見る
  std::println("{:#010x}", bits);                         // 符号 0、指数 127、仮数 0 → 0x3f800000
}
```

```text title="実行結果"
0x3f800000
```

## ゲームでの使いどころ

### 色のパッキング

赤・緑・青・アルファの 4 チャンネル（各 8 ビット）を、1 つの `uint32_t` に、詰める処理は、シフトと OR の、典型です。`DXGI_FORMAT_R8G8B8A8_UNORM` は、メモリ上で、R が最下位のバイトになるので、この順に詰めます。

```cpp
#include <cstdint>
#include <print>

constexpr std::uint32_t PackRgba(std::uint8_t r, std::uint8_t g, std::uint8_t b, std::uint8_t a) {
  return (std::uint32_t{a} << 24) | (std::uint32_t{b} << 16) | (std::uint32_t{g} << 8) | std::uint32_t{r};
}

constexpr std::uint8_t UnpackGreen(std::uint32_t color) {
  return static_cast<std::uint8_t>((color >> 8) & 0xFF);   // 8 ビット右へずらして、下位 8 ビットだけ残す
}

int main() {
  std::uint32_t c = PackRgba(255, 128, 64, 255);
  std::println("packed = {:08X}", c);                       // A=FF B=40 G=80 R=FF
  std::println("green  = {}", UnpackGreen(c));
}
```

```text title="実行結果"
packed = FF4080FF
green  = 128
```

取り出すときは、「ずらして、マスクで切り出す」（`(x >> 位置) & マスク`）が、基本の形です。`& 0xFF` が、下位 8 ビットを、残す「マスク」です。

### メモリの切り上げ（アラインメント）

メモリ アドレスや、サイズを、2 のべき乗の倍数に、切り上げる処理は、`+ (a − 1)` して、`& ~(a − 1)` で、下位を、落とします。定数バッファの 16 バイト境界、GPU バッファのアラインメントなどで、よく使います。

```cpp
#include <cstdint>
#include <print>

// alignment は 2 のべき乗であること。
constexpr std::uint32_t AlignUp(std::uint32_t n, std::uint32_t alignment) {
  return (n + alignment - 1) & ~(alignment - 1);
}

int main() {
  std::println("{}", AlignUp(13, 16));    // 13 → 16
  std::println("{}", AlignUp(16, 16));    // すでに、倍数 → 16 のまま
  std::println("{}", AlignUp(100, 64));   // 100 → 128
}
```

```text title="実行結果"
16
16
128
```

`alignment − 1` は、下位の、ビットが、全部 1（16 なら `0b1111`）なので、`~` で反転すると、下位だけ 0 のマスクになります。足してから、このマスクで、AND すると、下位が消えて、倍数に、切り上がります。

### そのほか

| 場面 | 使い方 |
| --- | --- |
| 当たり判定のレイヤー | 「自分が、どのレイヤーか」と「どのレイヤーと、当たるか」を、2 つのマスクで、持つ。`(a.layer & b.mask) != 0` で、1 回の AND で、判定する |
| 状態フラグ | 「地面にいる」「ダッシュ中」「無敵」などを、1 つの整数に、まとめる |
| ハッシュ | `hash ^= value; hash *= prime;` のように、XOR と、シフトで、値を、混ぜる |
| モートン コード（Z オーダー） | 2D・3D の座標の、ビットを、交互に、混ぜて、近い座標を、近いメモリに、置く（空間分割、テクスチャ） |
| シェーダー | HLSL にも、同じ演算子と、`countbits`、`reversebits`、`firstbithigh` が、ある。ライトの、ビット マスクで、「どのライトが、影響するか」を、持つ |

## よくあるミス

??? failure "`a & b == c` と、括弧なしで書いた"
    `==` が先に評価され、`a & (b == c)` になる。ビット演算は、必ず括弧で囲む。

??? failure "`1 << 32` や、`1 << 40` と、書いた"
    `1` は `int` なので、31 を超えると、未定義動作。`1u << n`（32 ビット）か、`1ull << n`（64 ビット）にする。`n` が変数なら、ビット数未満かを、確かめる。

??? failure "`uint8_t` の `~` の結果を、そのまま、比較した"
    `~a` は、整数昇格で、`int` になり、上位ビットも、反転する。`static_cast<std::uint8_t>(~a)` で、型に戻す。

??? failure "フラグを、`enum class` にして、`|` が、使えない"
    `enum class` は、暗黙に整数へ、変換されないので、`operator|`、`operator&`、`operator~` を、自分で、定義する（上の例）。

??? failure "符号付き整数で、ビット演算をした"
    負の数の、シフトや、反転は、表現（2 の補数）に、依存し、読みにくい。ビット演算は、符号なし整数（`uint32_t` など）で、行う。

??? failure "ビット数を、自分で、ループで数えた"
    `popcount`、`countl_zero` など、`<bit>` の関数が、あり、CPU の専用命令で、速い。自分で書かない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `&` AND、`|` OR、`^` XOR、`~` NOT、`<<` `>>` シフト
    - [x] フラグ: 作る `1u << n`、立てる `|=`、落とす `&= ~`、判定 `(x & f) != 0`
    - [x] `a & b == c` は、罠。必ず括弧
    - [x] 小さい型は、`int` に昇格する。結果を、型に戻す
    - [x] ビット数以上のシフトは、未定義動作。64 ビットは `1ull`
    - [x] 数える・回すは、`<bit>`（`popcount`、`countl_zero`、`bit_ceil`、`rotl`）
    - [x] ビット列の、型変換は、`std::bit_cast`

## 関連ページ

- [<bit>（ビット操作）](../stl/numeric/bit.md)
- [std::bitset](../stl/containers/bitset.md)
- [未定義動作](ub.md)
- [cppreference: Bitwise operators](https://en.cppreference.com/w/cpp/language/operators)

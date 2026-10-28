---
title: std::bit_ceil
summary: "自分以上で最小の、2 のべき乗に切り上げる。"
order: 3
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_ceil

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

リング バッファの容量を要求された数以上の 2 の累乗にそろえたい。ハッシュテーブルのバケット数、GPU に渡すバッファの大きさ。「少なくともこの大きさが欲しいが、2 の累乗でなければならない」という場面で使うのが `std::bit_ceil` です。

!!! tip "ポイント"
    - `std::bit_ceil(100u)` は 128、`std::bit_ceil(128u)` は 128
    - `0` や `1` のときは 1
    - 結果が型に収まらないと未定義動作
    - 切り捨てたいときは `bit_floor`

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_ceil {#bit_ceil}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr T bit_ceil(T x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 対象の値 |

戻り値は、`x` 以上で最小の 2 の累乗です。`x` がすでに 2 の累乗ならそのまま返します。`x` が 0 のときは 1 を返します（`bit_floor` は 0 を返すのと異なります）。

結果が型で表せない場合は未定義動作です。たとえば `uint8_t` で `bit_ceil(200)` は 256 になるはずですが、`uint8_t` に収まりません。定数式の中では、コンパイルエラーになります。要求が大きくなる可能性があるときは、広い型で呼びます。

符号なし整数型だけが対象です。

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("bit_ceil(100) = {}", std::bit_ceil(100u));
  std::println("bit_ceil(128) = {}", std::bit_ceil(128u));
  std::println("bit_ceil(1)   = {}", std::bit_ceil(1u));
  std::println("bit_ceil(0)   = {}", std::bit_ceil(0u));
}
```

```text title="実行結果"
bit_ceil(100) = 128
bit_ceil(128) = 128
bit_ceil(1)   = 1
bit_ceil(0)   = 1
```

## ゲームでの使いどころ

要求された容量を 2 の累乗に切り上げて確保します。

```cpp
// 少なくとも requested 個を入れられる、2 の累乗の大きさのリング バッファ
const std::size_t capacity = std::bit_ceil(requested);
std::vector<Event> buffer(capacity);
```

## よくあるミス

??? failure "結果が型に収まらず未定義動作になる"
    大きな値は `std::size_t` など広い型で呼びます。

??? failure "切り捨てと取り違えて、容量が足りなくなる"
    切り上げは `bit_ceil`、切り捨ては `bit_floor` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_floor`](bit_floor.md) | 以下で最大の 2 の累乗 |
| [`bit_width`](bit_width.md) | 必要なビット数 |
| [`has_single_bit`](has_single_bit.md) | 2 の累乗か |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bit_ceil(x)` は `x` 以上で最小の 2 の累乗
    - [x] 0 は 1。結果が型に収まらないと未定義動作
    - [x] 切り捨ては `bit_floor`

## 関連ページ

- [cpprefjp: std::bit_ceil](https://cpprefjp.github.io/reference/bit/bit_ceil.html)
- [cppreference: std::bit_ceil](https://en.cppreference.com/w/cpp/numeric/bit_ceil)

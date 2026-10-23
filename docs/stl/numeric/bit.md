---
title: <bit>（ビット操作）
summary: "ビットを数える（`popcount`）・型を読み替える（`bit_cast`）など、ビット操作。"
order: 75
tags:
  - 数値
---

# &lt;bit&gt;（ビット操作）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`<bit>` は、**整数のビットを調べたり操作したりする関数**をまとめた C++20 のヘッダです。「1 のビットが何個あるか」「2 のべき乗か」「次の 2 のべき乗はいくつか」などを、CPU の専用命令を使って速く計算します。また `std::bit_cast` を使うと、float の中身をビット列として安全に読むこともできます。

!!! tip "ポイント"
    - 1 のビットの数は `std::popcount`、2 のべき乗かは `std::has_single_bit`、次の 2 のべき乗は `std::bit_ceil`。
    - 型を「中身のビットはそのままで」別の型として読むなら `std::bit_cast`（`reinterpret_cast` は未定義動作になりやすい）。
    - 引数は**符号なし整数**（`unsigned`、`std::uint32_t` など）。int を渡すとコンパイルエラー。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::popcount`](bit/popcount.md) | <span class="rank rank-sometimes">たまに</span> | 1 のビットの数 |
| [`std::has_single_bit`](bit/has_single_bit.md) | <span class="rank rank-sometimes">たまに</span> | 2 のべき乗か |
| [`std::bit_ceil`](bit/bit_ceil.md) | <span class="rank rank-sometimes">たまに</span> | 以上で一番小さい 2 のべき乗 |
| [`std::bit_cast`](bit/bit_cast.md) | <span class="rank rank-sometimes">たまに</span> | ビットはそのままで別の型として読む |
| [`std::countr_zero`](bit/countr_zero.md) | <span class="rank rank-sometimes">たまに</span> | 下位から続く 0 の数（一番下の 1 の位置） |
| [`std::bit_floor`](bit/bit_floor.md) | <span class="rank rank-rare">知ってるだけ</span> | 以下で一番大きい 2 のべき乗 |
| [`std::bit_width`](bit/bit_width.md) | <span class="rank rank-rare">知ってるだけ</span> | 表すのに必要なビット数 |
| [`std::countl_zero`](bit/countl_zero.md) | <span class="rank rank-rare">知ってるだけ</span> | 上位から続く 0 の数 |
| [`std::countl_one`](bit/countl_one.md) | <span class="rank rank-rare">知ってるだけ</span> | 上位から続く 1 の数 |
| [`std::countr_one`](bit/countr_one.md) | <span class="rank rank-rare">知ってるだけ</span> | 下位から続く 1 の数 |
| [`std::rotl`](bit/rotl.md) | <span class="rank rank-rare">知ってるだけ</span> | 左回転（はみ出したビットが反対側から入る） |
| [`std::rotr`](bit/rotr.md) | <span class="rank rank-rare">知ってるだけ</span> | 右回転 |
| [`std::byteswap`](bit/byteswap.md) | <span class="rank rank-rare">知ってるだけ</span> | バイトの並びを逆にする <span class="ver ver-23">C++23</span> |
| [`std::endian`](bit/endian.md) | <span class="rank rank-rare">知ってるだけ</span> | 今の CPU のエンディアン |

## よくある使い方

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint32_t flags = 0b1011'0000;  // 取ったアイテムのフラグ
  std::println("取った数: {}", std::popcount(flags));

  std::uint32_t texture_size = 300;
  std::println("2 のべき乗？ {} / 切り上げ {}", std::has_single_bit(texture_size),
               std::bit_ceil(texture_size));

  float f = 1.0f;
  std::println("1.0f のビット: {:#010x}", std::bit_cast<std::uint32_t>(f));
}
```

```text title="実行結果"
取った数: 3
2 のべき乗？ false / 切り上げ 512
1.0f のビット: 0x3f800000
```

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    int count = __builtin_popcount(x);  // GCC 専用
    int count2 = __popcnt(x);           // MSVC 専用
    std::uint32_t bits = *reinterpret_cast<std::uint32_t*>(&f);  // 未定義動作
    ```

=== "今の書き方（C++20）"

    ```cpp
    int count = std::popcount(x);
    auto bits = std::bit_cast<std::uint32_t>(f);
    ```

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| フラグの数を数える | `popcount` |
| テクスチャの大きさを 2 のべき乗に | `has_single_bit`、`bit_ceil` |
| ECS のコンポーネントのビットマスクを回す | `countr_zero` |
| ハッシュ関数 | `rotl`、`bit_cast` |
| ファイル形式の読み込み | `byteswap`、`endian` |

## よくあるミス

??? failure "int を渡してコンパイルエラー"
    `std::popcount(5)` はエラーです。`5u` か `std::uint32_t{5}` のように符号なしにします。

??? failure "reinterpret_cast で float を読む"
    型の違うポインタで読むのは未定義動作（strict aliasing 違反）です。`std::bit_cast` を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数える popcount、2 のべき乗 has_single_bit / bit_ceil
    - [x] 型の読み替えは bit_cast
    - [x] 引数は符号なし整数

## 関連ページ

- [std::bitset](../containers/bitset.md)
- [cppreference: <bit>](https://en.cppreference.com/w/cpp/header/bit)

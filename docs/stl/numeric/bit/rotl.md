---
title: std::rotl
summary: "ビットを左に回転させる（はみ出したビットが反対側に戻る）。"
order: 11
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::rotl

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::rotl` は、**ビットを左に回転させる**関数です。左にずらしてはみ出したビットは、右端に戻ってきます（シフトと違い、捨てられません）。ハッシュ関数や乱数生成の部品で使われます。

!!! tip "ポイント"
    - シフト（`<<`）は、はみ出したビットを捨てる。回転は、戻す。
    - 回す量は 0 以上（負だと逆向きに回る）。
    - 1 命令で動く環境が多い。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::rotl {#rotl}

```cpp
template <class T>
constexpr T rotl(T x, int s) noexcept;
```

- 左に `s` ビット回転します。はみ出したビットは右から入ります（ハッシュ関数や乱数でよく使う）

<div class="anim" data-label="std::rotl(0b1001u, 1)">
1 0 0 1 # ビット列
>0 >0 >1 >1 # 左に 1 つ回す。はみ出した 1 が右端に戻る
</div>

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{:#x}", std::rotl(0x80000001u, 1));  // 左へ 1 回す。はみ出した最上位ビットが右端に戻る
}
```

```text title="実行結果"
0x3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ハッシュの計算（FNV、xorshift など） | `std::rotl(x, 13)` |

## よくあるミス

??? failure "シフトと混同する"
    `<<` はビットを捨てます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rotr`](rotr.md) | 右に回す |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 左に回転
    - [x] はみ出したビットが戻る
    - [x] ハッシュで使う

## 関連ページ

- [cpprefjp: std::rotl](https://cpprefjp.github.io/reference/bit/rotl.html)
- [cppreference: std::rotl](https://en.cppreference.com/w/cpp/numeric/rotl)

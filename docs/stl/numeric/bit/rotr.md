---
title: std::rotr
summary: "ビットを右に回転させる（はみ出したビットが反対側に戻る）。"
order: 12
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::rotr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::rotr` は、**ビットを右に回転させる**関数です。右にずらしてはみ出したビットは、左端に戻ってきます。

!!! tip "ポイント"
    - `rotl(x, n)` は `rotr(x, -n)` と同じ。
    - ハッシュや乱数の部品。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::rotr {#rotr}

```cpp
template <class T>
constexpr T rotr(T x, int s) noexcept;
```

- 右に回転します

<div class="anim" data-label="std::rotr(0b1001u, 1)">
1 0 0 1 # ビット列
>1 >1 >0 >0 # 右に 1 つ回す。はみ出した 1 が左端に戻る
</div>

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{:#x}", std::rotr(0x00000003u, 1));  // 右へ 1 回す。はみ出した最下位ビットが左端に戻る
}
```

```text title="実行結果"
0x80000001
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ハッシュ・乱数の計算 | `std::rotr(x, 7)` |

## よくあるミス

??? failure "シフトと混同する"
    `>>` はビットを捨てます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rotl`](rotl.md) | 左に回す |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 右に回転
    - [x] はみ出したビットが戻る
    - [x] `rotl` の逆

## 関連ページ

- [cpprefjp: std::rotr](https://cpprefjp.github.io/reference/bit/rotr.html)
- [cppreference: std::rotr](https://en.cppreference.com/w/cpp/numeric/rotr)

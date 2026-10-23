---
title: std::feclearexcept
summary: "浮動小数点例外のフラグをクリアする。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::feclearexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

浮動小数点の異常フラグは、一度立つと自動では消えません。ある計算の異常だけを調べたいとき、計算の前にフラグを消しておく必要があります。`std::feclearexcept` は、そのフラグを消します。

!!! tip "ポイント"
    - `std::feclearexcept(FE_ALL_EXCEPT)` で全部のフラグを消す
    - 成功で 0 を返す
    - 計算の直前に呼び、あとで `fetestexcept` で調べる
    - 消すフラグを `|` で選べる

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::feclearexcept {#feclearexcept}

<span class="ver ver-11">C++11</span>

```cpp
int feclearexcept(int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `excepts` | `int` | 消したいフラグ。`FE_ALL_EXCEPT` で全部 |

`excepts` で指定したフラグを消します。成功すれば 0 を返します。指定しなかったフラグには影響しません。

フラグは、計算のたびに累積します。ゲームのループの中で、毎フレーム「このフレームで異常が起きたか」を調べるには、フレームの先頭で `feclearexcept(FE_ALL_EXCEPT)` を呼びます。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feraiseexcept(FE_OVERFLOW);                       // フラグを立てる（実験用）
  std::println("立っている: {}", std::fetestexcept(FE_OVERFLOW) != 0);
  std::feclearexcept(FE_OVERFLOW);
  std::println("消した後  : {}", std::fetestexcept(FE_OVERFLOW) != 0);
}
```

```text title="実行結果"
立っている: true
消した後  : false
```

## ゲームでの使いどころ

フレームの先頭でフラグを消し、フレームの終わりに調べます。

```cpp
std::feclearexcept(FE_ALL_EXCEPT);     // フレームの先頭
Update();
if (std::fetestexcept(FE_INVALID)) { /* このフレームで不正な演算 */ }
```

## よくあるミス

??? failure "消し忘れて、前のフレームの異常を拾う"
    調べる前に消します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fetestexcept`](fetestexcept.md) | フラグを読む |
| [`feraiseexcept`](feraiseexcept.md) | フラグを立てる |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `feclearexcept` は浮動小数点の異常フラグを消す
    - [x] 計算の前に呼び、あとで `fetestexcept` で調べる
    - [x] 成功で 0

## 関連ページ

- [cpprefjp: std::feclearexcept](https://cpprefjp.github.io/reference/cfenv/feclearexcept.html)
- [cppreference: std::feclearexcept](https://en.cppreference.com/w/cpp/numeric/fenv/feclearexcept)

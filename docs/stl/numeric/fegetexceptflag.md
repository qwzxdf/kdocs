---
title: std::fegetexceptflag
summary: "浮動小数点例外のフラグの状態を保存する。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fegetexceptflag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

異常フラグを一時的に消して別の計算をしたあとで、元の状態に戻したい場面があります。`std::fegetexceptflag` は、<strong>いまのフラグの状態を保存</strong>します。

!!! tip "ポイント"
    - `std::fegetexceptflag(&flags, FE_ALL_EXCEPT)` でフラグの状態を保存する
    - 保存先は `std::fexcept_t` 型の変数
    - 復元は `fesetexceptflag`
    - 成功で 0 を返す

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fegetexceptflag {#fegetexceptflag}

<span class="ver ver-11">C++11</span>

```cpp
int fegetexceptflag(std::fexcept_t* flagp, int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `flagp` | `fexcept_t*` | 保存先 |
| `excepts` | `int` | 保存したいフラグ |

`excepts` で指定したフラグの現在の状態を `*flagp` に保存します。成功すれば 0 を返します。

`fexcept_t` の中身は環境依存で、直接読み書きしてはいけません。保存した値は、`fesetexceptflag` に渡して復元するためのものです。

用途は、「呼び出し側の異常フラグを壊さずに、自分の計算の異常を調べる」ことです。保存、消去、計算、調査、復元の順に行います。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feclearexcept(FE_ALL_EXCEPT);
  std::feraiseexcept(FE_DIVBYZERO);                     // 呼び出し側のフラグ

  std::fexcept_t saved;
  std::fegetexceptflag(&saved, FE_ALL_EXCEPT);          // 保存する
  std::feclearexcept(FE_ALL_EXCEPT);
  std::println("消した後: {}", std::fetestexcept(FE_DIVBYZERO) != 0);

  std::fesetexceptflag(&saved, FE_ALL_EXCEPT);          // 復元する
  std::println("復元後  : {}", std::fetestexcept(FE_DIVBYZERO) != 0);
  std::feclearexcept(FE_ALL_EXCEPT);
}
```

```text title="実行結果"
消した後: false
復元後  : true
```

## ゲームでの使いどころ

自分の計算の異常だけを調べたい関数で、呼び出し側のフラグを保存・復元します。

```cpp
std::fexcept_t saved;
std::fegetexceptflag(&saved, FE_ALL_EXCEPT);
std::feclearexcept(FE_ALL_EXCEPT);
const double r = Compute();
const bool bad = std::fetestexcept(FE_INVALID) != 0;
std::fesetexceptflag(&saved, FE_ALL_EXCEPT);   // 呼び出し側の状態に戻す
```

## よくあるミス

??? failure "`fexcept_t` の中身を直接読む"
    環境依存です。`fesetexceptflag` に渡すだけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetexceptflag`](fesetexceptflag.md) | 保存したフラグを復元する |
| [`fegetenv`](fegetenv.md) | 環境全体を保存する |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fegetexceptflag` は異常フラグの状態を保存する
    - [x] 復元は `fesetexceptflag`
    - [x] `fexcept_t` の中身は触らない

## 関連ページ

- [cpprefjp: std::fegetexceptflag](https://cpprefjp.github.io/reference/cfenv/fegetexceptflag.html)
- [cppreference: std::fegetexceptflag](https://en.cppreference.com/w/cpp/numeric/fenv/fegetexceptflag)

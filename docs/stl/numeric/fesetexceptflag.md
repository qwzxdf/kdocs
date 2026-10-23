---
title: std::fesetexceptflag
summary: "保存しておいた浮動小数点例外のフラグを復元する。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fesetexceptflag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

`std::fegetexceptflag` で保存した異常フラグの状態を、元に戻すのが `std::fesetexceptflag` です。フラグを消して別の計算をしたあとに、呼び出し側のフラグを復元するために使います。

!!! tip "ポイント"
    - `std::fesetexceptflag(&flags, FE_ALL_EXCEPT)` で保存した状態に戻す
    - `flags` は `fegetexceptflag` で保存した値
    - 例外は発生しない（フラグが書き戻されるだけ）
    - 成功で 0 を返す

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fesetexceptflag {#fesetexceptflag}

<span class="ver ver-11">C++11</span>

```cpp
int fesetexceptflag(const std::fexcept_t* flagp, int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `flagp` | `const fexcept_t*` | `fegetexceptflag` で保存した値 |
| `excepts` | `int` | 復元したいフラグ |

`*flagp` に保存されているフラグの状態を、`excepts` で指定した分だけ現在の状態に書き戻します。成功すれば 0 を返します。

`feraiseexcept` との違いは、例外そのものを発生させず、フラグの状態だけを復元する点です。トラップが有効な環境でも、シグナルは飛びません。

`flagp` は、`fegetexceptflag` で得た値に限ります。それ以外の値を渡すと動作は不定です。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feclearexcept(FE_ALL_EXCEPT);
  std::feraiseexcept(FE_INVALID);
  std::fexcept_t saved;
  std::fegetexceptflag(&saved, FE_INVALID);
  std::feclearexcept(FE_ALL_EXCEPT);

  std::fesetexceptflag(&saved, FE_INVALID);
  std::println("復元された: {}", std::fetestexcept(FE_INVALID) != 0);
  std::feclearexcept(FE_ALL_EXCEPT);
}
```

```text title="実行結果"
復元された: true
```

## ゲームでの使いどころ

保存したフラグの状態を、計算の後で元に戻します。使い方の全体は `fegetexceptflag` のページを参照してください。

## よくあるミス

??? failure "保存していない値を渡す"
    `fegetexceptflag` で得た値だけを渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fegetexceptflag`](fegetexceptflag.md) | フラグを保存する |
| [`feraiseexcept`](feraiseexcept.md) | 異常を発生させる |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fesetexceptflag` は保存したフラグを復元する
    - [x] 例外は発生しない
    - [x] `fegetexceptflag` とセットで使う

## 関連ページ

- [cpprefjp: std::fesetexceptflag](https://cpprefjp.github.io/reference/cfenv/fesetexceptflag.html)
- [cppreference: std::fesetexceptflag](https://en.cppreference.com/w/cpp/numeric/fenv/fesetexceptflag)

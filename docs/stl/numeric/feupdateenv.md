---
title: std::feupdateenv
summary: "保存した環境を復元し、保留中の例外を再び発生させる。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::feupdateenv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

`std::feholdexcept` で保存した環境に戻すとき、その間に立った異常フラグを捨ててしまうと、呼び出し側が異常に気づけません。`std::feupdateenv` は、<strong>環境を戻し、その間に立った異常を、戻した環境に引き継ぎます</strong>。

!!! tip "ポイント"
    - `std::feupdateenv(&env)` で環境を戻し、その間のフラグも引き継ぐ
    - `env` は `feholdexcept` か `fegetenv` で得た値
    - `fesetenv` との違いは、フラグを捨てるか引き継ぐか
    - 成功で 0 を返す

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::feupdateenv {#feupdateenv}

<span class="ver ver-11">C++11</span>

```cpp
int feupdateenv(const std::fenv_t* envp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `envp` | `const fenv_t*` | 保存した環境 |

`*envp` が表す環境に戻し、そのうえで、戻す前に立っていた異常フラグを、戻したあとの環境で再び発生させます。成功すれば 0 を返します。

`fesetenv(&env)` だと、保存後に立った異常フラグが消えます。`feupdateenv` は、それらを呼び出し側に見せます。内部の計算で起きた `FE_INVALID` や `FE_OVERFLOW` を、呼び出し側の `fetestexcept` で検出できるようにするための関数です。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feclearexcept(FE_ALL_EXCEPT);
  std::fenv_t env;
  std::feholdexcept(&env);
  std::feraiseexcept(FE_OVERFLOW);                     // 内部の計算で異常が起きた
  std::feupdateenv(&env);                              // 戻しつつ、異常を引き継ぐ
  std::println("異常が引き継がれた: {}", std::fetestexcept(FE_OVERFLOW) != 0);
  std::feclearexcept(FE_ALL_EXCEPT);
}
```

```text title="実行結果"
異常が引き継がれた: true
```

## ゲームでの使いどころ

ライブラリの関数が、内部で起きた異常を、呼び出し側に報告するときに使います。通常のゲームのコードでは使いません。

## よくあるミス

??? failure "`fesetenv` で戻して、異常が消える"
    異常を引き継ぎたいなら `feupdateenv` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feholdexcept`](feholdexcept.md) | 保存してフラグを消す |
| [`fesetenv`](fesetenv.md) | 環境を戻す（フラグは捨てる） |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `feupdateenv` は環境を戻し、立ったフラグを引き継ぐ
    - [x] `fesetenv` はフラグを捨てる
    - [x] `feholdexcept` とセット

## 関連ページ

- [cpprefjp: std::feupdateenv](https://cpprefjp.github.io/reference/cfenv/feupdateenv.html)
- [cppreference: std::feupdateenv](https://en.cppreference.com/w/cpp/numeric/fenv/feupdateenv)

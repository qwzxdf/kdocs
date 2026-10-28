---
title: std::feraiseexcept
summary: "浮動小数点例外を、意図して発生させる。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::feraiseexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

自分で作った関数が浮動小数点の異常を起こしたことを呼び出し側に標準の方法で伝えたい。たとえば、定義域の外の入力を受けたときに `FE_INVALID` を立てる。`std::feraiseexcept` は、<strong>指定した異常フラグを立てます</strong>。

!!! tip "ポイント"
    - `std::feraiseexcept(FE_INVALID)` で無効な演算のフラグを立てる
    - 成功で 0 を返す
    - 実際にその異常を起こす（環境によっては例外のトラップも）
    - 主に数値計算ライブラリの実装や、テストで使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::feraiseexcept {#feraiseexcept}

<span class="ver ver-11">C++11</span>

```cpp
int feraiseexcept(int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `excepts` | `int` | 立てたいフラグ |

`excepts` で指定した異常を発生させます。フラグが立ち、環境が例外のトラップを有効にしていれば、シグナルが発生します。成功すれば 0 を返します。

数値計算ライブラリが標準の数学関数と同じ作法で、異常を知らせたいときに使います。また、`fetestexcept` を使うコードのテストで、わざとフラグを立てる用途にも使えます。

ゲームのコードで直接呼ぶ場面はほとんどありません。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feclearexcept(FE_ALL_EXCEPT);
  std::feraiseexcept(FE_INVALID);
  std::println("FE_INVALID が立った: {}", std::fetestexcept(FE_INVALID) != 0);
  std::feclearexcept(FE_ALL_EXCEPT);
}
```

```text title="実行結果"
FE_INVALID が立った: true
```

## ゲームでの使いどころ

自前の数学関数が標準関数と同じ方法で異常を知らせたいときに使います。

```cpp
double MySqrt(double x) {
  if (x < 0) {
    std::feraiseexcept(FE_INVALID);
    return std::numeric_limits<double>::quiet_NaN();
  }
  return std::sqrt(x);
}
```

## よくあるミス

??? failure "トラップが有効な環境で、意図せずシグナルが飛ぶ"
    開発環境の設定を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feclearexcept`](feclearexcept.md) | フラグを消す |
| [`fetestexcept`](fetestexcept.md) | フラグを読む |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `feraiseexcept` は異常フラグを立てる
    - [x] 成功で 0
    - [x] 数値計算ライブラリやテストで使う

## 関連ページ

- [cpprefjp: std::feraiseexcept](https://cpprefjp.github.io/reference/cfenv/feraiseexcept.html)
- [cppreference: std::feraiseexcept](https://en.cppreference.com/w/cpp/numeric/fenv/feraiseexcept)

---
title: std::feholdexcept
summary: "環境を保存し、例外フラグをクリアして、例外を止めるモードに入る。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::feholdexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

他人の計算の異常フラグを壊さず、しかも自分の計算では異常で止まらないようにしたい。`std::feholdexcept` は、<strong>現在の環境を保存し、異常フラグを消し、以降の異常でトラップが発生しない状態</strong>にします。

!!! tip "ポイント"
    - `std::feholdexcept(&env)` で環境の保存とフラグの消去を同時に行う
    - 以降の異常は、シグナルを発生させない（非停止モード）
    - 終わったら `feupdateenv` で戻す
    - 成功で 0 を返す

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::feholdexcept {#feholdexcept}

<span class="ver ver-11">C++11</span>

```cpp
int feholdexcept(std::fenv_t* envp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `envp` | `fenv_t*` | 保存先 |

現在の浮動小数点環境を `*envp` に保存したうえで、異常フラグをすべて消し、以降の浮動小数点の異常でトラップ（シグナル）が発生しない「非停止モード」にします。成功すれば 0 を返します。

数値計算ライブラリが、内部の計算で起きる異常（途中の `FE_INEXACT` など）を外に漏らさず、必要な異常だけを最後に引き継ぐために使います。引き継ぐ処理は `feupdateenv` が行います。

通常は `fegetenv` と `fesetenv` で足り、`feholdexcept` を使うのはライブラリの実装者です。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fenv_t env;
  const int result = std::feholdexcept(&env);          // 保存して、フラグを消す
  std::println("成功: {}", result == 0);
  std::feupdateenv(&env);                              // 元の環境に戻す
}
```

```text title="実行結果"
成功: true
```

## ゲームでの使いどころ

ライブラリの関数が、呼び出し側の環境を保存して、内部の計算を非停止で行い、最後に環境を戻します。

```cpp
std::fenv_t env;
std::feholdexcept(&env);
const double r = InternalCompute();
std::feupdateenv(&env);     // 内部で立ったフラグを呼び出し側に引き継ぐ
```

## よくあるミス

??? failure "`fegetenv` と取り違える"
    `feholdexcept` はフラグも消し、トラップも無効にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feupdateenv`](feupdateenv.md) | 環境を戻し、立ったフラグを引き継ぐ |
| [`fegetenv`](fegetenv.md) | 保存だけ行う |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `feholdexcept` は環境を保存し、フラグを消し、非停止モードにする
    - [x] 戻すには `feupdateenv`
    - [x] ライブラリの実装者向け

## 関連ページ

- [cpprefjp: std::feholdexcept](https://cpprefjp.github.io/reference/cfenv/feholdexcept.html)
- [cppreference: std::feholdexcept](https://en.cppreference.com/w/cpp/numeric/fenv/feholdexcept)

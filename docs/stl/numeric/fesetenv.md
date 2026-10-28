---
title: std::fesetenv
summary: "保存しておいた浮動小数点環境を復元する。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fesetenv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

`std::fegetenv` で保存した浮動小数点環境を元に戻すのが `std::fesetenv` です。丸めモードを一時的に変えた計算の後始末に使います。

!!! tip "ポイント"
    - `std::fesetenv(&env)` で保存した環境に戻す
    - `env` は `fegetenv` か `feholdexcept` で得た値
    - 環境にはフラグも含まれ、保存時の状態に戻る
    - 成功で 0 を返す

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fesetenv {#fesetenv}

<span class="ver ver-11">C++11</span>

```cpp
int fesetenv(const std::fenv_t* envp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `envp` | `const fenv_t*` | `fegetenv` / `feholdexcept` で得た値。または `FE_DFL_ENV`（既定の環境） |

浮動小数点環境を `*envp` が表す状態に設定します。成功すれば 0 を返します。特別な値 `FE_DFL_ENV` を渡すと、プログラム開始時の既定の環境に戻ります。

保存した時点の異常フラグも書き戻されます。そのため、保存後にその計算で立ったフラグも消えます。その計算の異常を調べたいときは、`fesetenv` の前に `fetestexcept` で調べるか、異常を引き継ぐ `feupdateenv` を使います。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fenv_t saved;
  std::fegetenv(&saved);

  std::fesetround(FE_TOWARDZERO);
  std::println("変更後: {}", std::fegetround() == FE_TOWARDZERO);

  std::fesetenv(FE_DFL_ENV);                 // 既定の環境に戻す
  std::println("既定  : {}", std::fegetround() == FE_TONEAREST);
  std::fesetenv(&saved);
}
```

```text title="実行結果"
変更後: true
既定  : true
```

## ゲームでの使いどころ

一時的に環境を変えた処理の後始末に使います。例外が起きても必ず戻したい場合は、デストラクターで `fesetenv` を呼ぶクラスを作ります（RAII）。

```cpp
struct FenvGuard {
  std::fenv_t saved;
  FenvGuard() { std::fegetenv(&saved); }
  ~FenvGuard() { std::fesetenv(&saved); }
};
```

## よくあるミス

??? failure "保存せずに `fesetenv` して、環境を壊す"
    先に `fegetenv` で保存します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fegetenv`](fegetenv.md) | 環境を保存する |
| [`feupdateenv`](feupdateenv.md) | 環境を戻し、その間に立ったフラグを引き継ぐ |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fesetenv` は保存した環境に戻す
    - [x] `FE_DFL_ENV` で既定の環境に戻る
    - [x] RAII のクラスで包むと確実

## 関連ページ

- [cpprefjp: std::fesetenv](https://cpprefjp.github.io/reference/cfenv/fesetenv.html)
- [cppreference: std::fesetenv](https://en.cppreference.com/w/cpp/numeric/fenv/fesetenv)

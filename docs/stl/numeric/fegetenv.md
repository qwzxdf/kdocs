---
title: std::fegetenv
summary: "浮動小数点環境（フラグと丸めモード）を丸ごと保存する。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fegetenv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

丸めモードと異常フラグをまとめて一時的に変更する関数を作るとき、呼び出し側の環境を壊さないように、先に保存しておく必要があります。`std::fegetenv` は、<strong>浮動小数点環境の全体を保存</strong>します。

!!! tip "ポイント"
    - `std::fegetenv(&env)` で浮動小数点環境を保存する
    - 保存先は `std::fenv_t` 型の変数
    - 復元は `fesetenv`
    - 丸めモードと異常フラグの両方を含む

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fegetenv {#fegetenv}

<span class="ver ver-11">C++11</span>

```cpp
int fegetenv(std::fenv_t* envp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `envp` | `fenv_t*` | 保存先 |

現在の浮動小数点環境（丸めモード、異常フラグ、環境によってはトラップの設定）を、`*envp` に保存します。成功すれば 0 を返します。

`fenv_t` の中身は環境依存です。`fesetenv` に渡して復元するための値として扱います。

丸めモードだけ、あるいはフラグだけを扱うなら `fegetround` や `fegetexceptflag` のほうが目的に合いますが、全体を一度に保存したいなら `fegetenv` が簡単です。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fenv_t env;
  std::fegetenv(&env);                      // 環境を保存する

  std::fesetround(FE_UPWARD);               // 変更する
  std::println("変更後: {}", std::fegetround() == FE_UPWARD);

  std::fesetenv(&env);                      // 元に戻す
  std::println("復元後: {}", std::fegetround() == FE_TONEAREST);
}
```

```text title="実行結果"
変更後: true
復元後: true
```

## ゲームでの使いどころ

浮動小数点環境を一時的に変える処理で、前後を保存・復元します。

```cpp
std::fenv_t saved;
std::fegetenv(&saved);
std::fesetround(FE_DOWNWARD);
const double lower = Compute();
std::fesetenv(&saved);        // 環境を丸ごと元に戻す
```

## よくあるミス

??? failure "`fenv_t` の中身を触る"
    環境依存です。`fesetenv` に渡すだけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetenv`](fesetenv.md) | 環境を復元する |
| [`feholdexcept`](feholdexcept.md) | 保存して、フラグを消し、トラップを無効にする |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fegetenv` は浮動小数点環境の全体を保存する
    - [x] 復元は `fesetenv`
    - [x] 丸めモードとフラグの両方を含む

## 関連ページ

- [cpprefjp: std::fegetenv](https://cpprefjp.github.io/reference/cfenv/fegetenv.html)
- [cppreference: std::fegetenv](https://en.cppreference.com/w/cpp/numeric/fenv/fegetenv)

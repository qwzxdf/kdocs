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

`feholdexcept` で止めていた間に起きた例外を、環境を戻すときにまとめて発生させます。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::feupdateenv {#feupdateenv}

```cpp
int feupdateenv(const std::fenv_t* envp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `envp` | const fenv_t* | 復元する環境 |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fenv_t env;
  std::feholdexcept(&env);
  std::feraiseexcept(FE_INEXACT);
  std::feupdateenv(&env);
  std::println("{}", std::fetestexcept(FE_INEXACT) != 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 例外を一時的に止めた後で、起きたものを引き継ぐ |

## よくあるミス

??? failure "`fesetenv` と取り違える"
    `fesetenv` は保留中の例外を捨て、`feupdateenv` は再発生させます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 保存した環境を復元し、保留中の例外を再び発生させる
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::feupdateenv](https://cpprefjp.github.io/reference/cfenv/feupdateenv.html)
- [cppreference: std::feupdateenv](https://en.cppreference.com/w/cpp/numeric/fenv/feupdateenv)

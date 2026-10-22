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

`fegetenv` で保存した環境（フラグと丸めモード）を元に戻します。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::fesetenv {#fesetenv}

```cpp
int fesetenv(const std::fenv_t* envp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `envp` | const fenv_t* | 復元する環境（`FE_DFL_ENV` も指定可） |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fenv_t env;
  std::fegetenv(&env);
  std::fesetround(FE_DOWNWARD);
  std::fesetenv(&env);
  std::println("{}", std::fegetround() == FE_TONEAREST);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 丸めモードを一時的に変える処理の後始末 |

## よくあるミス

??? failure "例外フラグも元に戻ると気づかない"
    保存時点のフラグに戻ります。その後に起きたフラグは消えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 保存しておいた浮動小数点環境を復元する
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fesetenv](https://cpprefjp.github.io/reference/cfenv/fesetenv.html)
- [cppreference: std::fesetenv](https://en.cppreference.com/w/cpp/numeric/fenv/fesetenv)

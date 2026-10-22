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

例外フラグと丸めモードなどを、1 つにまとめて保存します。`fesetenv` で復元します。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::fegetenv {#fegetenv}

```cpp
int fegetenv(std::fenv_t* envp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `envp` | fenv_t* | 保存先 |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fenv_t env;
  std::fegetenv(&env);
  std::fesetround(FE_UPWARD);
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
| 使いどころ | 計算の前後で環境を元に戻す |

## よくあるミス

??? failure "保存した環境を、別のスレッドに持ち込む"
    環境はスレッドごとです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点環境（フラグと丸めモード）を丸ごと保存する
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fegetenv](https://cpprefjp.github.io/reference/cfenv/fegetenv.html)
- [cppreference: std::fegetenv](https://en.cppreference.com/w/cpp/numeric/fenv/fegetenv)

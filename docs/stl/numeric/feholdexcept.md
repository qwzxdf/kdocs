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

計算中に起きる例外を気にせず、まとめて後で処理したいときに使います。環境を保存してフラグを消し、以降の例外ではトラップしない状態にします。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::feholdexcept {#feholdexcept}

```cpp
int feholdexcept(std::fenv_t* envp);
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
  std::println("{}", std::feholdexcept(&env) == 0);
  std::feupdateenv(&env);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 計算の例外をまとめて処理する |

## よくあるミス

??? failure "`feupdateenv` で戻し忘れる"
    必ず `feupdateenv` か `fesetenv` で元の環境に戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 環境を保存し、例外フラグをクリアして、例外を止めるモードに入る
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::feholdexcept](https://cpprefjp.github.io/reference/cfenv/feholdexcept.html)
- [cppreference: std::feholdexcept](https://en.cppreference.com/w/cpp/numeric/fenv/feholdexcept)

---
title: std::feclearexcept
summary: "浮動小数点例外のフラグをクリアする。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::feclearexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

ゼロ除算やオーバーフローが起きると、CPU の浮動小数点例外フラグが立ちます。計算の前にいったんクリアしておくと、その計算で起きた例外だけを調べられます。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::feclearexcept {#feclearexcept}

```cpp
int feclearexcept(int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `excepts` | int | クリアする例外のビットのマスク（`FE_ALL_EXCEPT` など） |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feraiseexcept(FE_DIVBYZERO);
  std::feclearexcept(FE_ALL_EXCEPT);
  std::println("{}", std::fetestexcept(FE_DIVBYZERO) != 0);
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 計算の前にフラグを初期化する |

## よくあるミス

??? failure "クリアし忘れる"
    前の計算のフラグが残ったまま調べると、別の計算の例外を拾ってしまいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点例外のフラグをクリアする
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::feclearexcept](https://cpprefjp.github.io/reference/cfenv/feclearexcept.html)
- [cppreference: std::feclearexcept](https://en.cppreference.com/w/cpp/numeric/fenv/feclearexcept)

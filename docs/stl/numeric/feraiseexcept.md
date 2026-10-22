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

テストなどで、例外が起きた状態を作りたいときに、指定した例外のフラグを立てます。ハードウェアの例外の設定によっては、トラップ（割り込み）になります。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::feraiseexcept {#feraiseexcept}

```cpp
int feraiseexcept(int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `excepts` | int | 発生させる例外のビットのマスク |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feclearexcept(FE_ALL_EXCEPT);
  std::feraiseexcept(FE_OVERFLOW);
  std::println("{}", std::fetestexcept(FE_OVERFLOW) != 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 例外処理のテスト |

## よくあるミス

??? failure "トラップが有効な環境で呼ぶ"
    環境によってはプログラムが止まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点例外を、意図して発生させる
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::feraiseexcept](https://cpprefjp.github.io/reference/cfenv/feraiseexcept.html)
- [cppreference: std::feraiseexcept](https://en.cppreference.com/w/cpp/numeric/fenv/feraiseexcept)

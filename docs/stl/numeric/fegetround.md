---
title: std::fegetround
summary: "現在の浮動小数点の丸めモードを調べる。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fegetround

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

丸めの規則（最も近い値、切り上げ、切り捨てなど）は切り替えられます。いまの設定を調べるのが `fegetround` で、変えるのは `fesetround` です。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::fegetround {#fegetround}

```cpp
int fegetround();
```

- 戻り値: `FE_TONEAREST`・`FE_UPWARD`・`FE_DOWNWARD`・`FE_TOWARDZERO` のどれか
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::println("{}", std::fegetround() == FE_TONEAREST);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 丸めモードを変えた後に元へ戻す |

## よくあるミス

??? failure "設定を覚えずに変える"
    先に `fegetround` で保存してから `fesetround` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在の浮動小数点の丸めモードを調べる
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fegetround](https://cpprefjp.github.io/reference/cfenv/fegetround.html)
- [cppreference: std::fegetround](https://en.cppreference.com/w/cpp/numeric/fenv/fegetround)

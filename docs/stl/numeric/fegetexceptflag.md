---
title: std::fegetexceptflag
summary: "浮動小数点例外のフラグの状態を保存する。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fegetexceptflag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

いまのフラグの状態を、あとで戻すために保存します。`fesetexceptflag` で復元します。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::fegetexceptflag {#fegetexceptflag}

```cpp
int fegetexceptflag(std::fexcept_t* flagp, int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `flagp` | fexcept_t* | 保存先 |
| `excepts` | int | 保存する例外のビットのマスク |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fexcept_t saved;
  std::feraiseexcept(FE_INEXACT);
  std::fegetexceptflag(&saved, FE_ALL_EXCEPT);
  std::feclearexcept(FE_ALL_EXCEPT);
  std::fesetexceptflag(&saved, FE_ALL_EXCEPT);
  std::println("{}", std::fetestexcept(FE_INEXACT) != 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ライブラリを呼ぶ前後でフラグを保つ |

## よくあるミス

??? failure "保存せずにクリアする"
    呼び出し元が気にしているフラグまで消してしまいます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点例外のフラグの状態を保存する
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fegetexceptflag](https://cpprefjp.github.io/reference/cfenv/fegetexceptflag.html)
- [cppreference: std::fegetexceptflag](https://en.cppreference.com/w/cpp/numeric/fenv/fegetexceptflag)

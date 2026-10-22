---
title: std::fesetexceptflag
summary: "保存しておいた浮動小数点例外のフラグを復元する。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fesetexceptflag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

`fegetexceptflag` で保存した状態を元に戻します。例外そのものは発生させず、フラグだけ設定します。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::fesetexceptflag {#fesetexceptflag}

```cpp
int fesetexceptflag(const std::fexcept_t* flagp, int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `flagp` | const fexcept_t* | 復元する状態 |
| `excepts` | int | 復元する例外のビットのマスク |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::fexcept_t saved;
  std::feclearexcept(FE_ALL_EXCEPT);
  std::fegetexceptflag(&saved, FE_ALL_EXCEPT);
  std::feraiseexcept(FE_OVERFLOW);
  std::fesetexceptflag(&saved, FE_ALL_EXCEPT);
  std::println("{}", std::fetestexcept(FE_OVERFLOW) != 0);
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 計算の途中で起きたフラグを取り消す |

## よくあるミス

??? failure "`excepts` の指定が足りない"
    指定したビットだけが復元されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 保存しておいた浮動小数点例外のフラグを復元する
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fesetexceptflag](https://cpprefjp.github.io/reference/cfenv/fesetexceptflag.html)
- [cppreference: std::fesetexceptflag](https://en.cppreference.com/w/cpp/numeric/fenv/fesetexceptflag)

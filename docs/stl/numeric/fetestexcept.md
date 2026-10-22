---
title: std::fetestexcept
summary: "浮動小数点例外のフラグを調べる。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fetestexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

計算のあとで、ゼロ除算やオーバーフローなど、どんな例外が起きたかを調べます。例外を投げるのではなく、フラグが立つだけなので、自分で確認します。

!!! tip "ポイント"
    - `<cfenv>` の関数（浮動小数点環境の操作）。
    - 例外を投げず、フラグで知らせる。
    - ほとんどのゲームでは使わない。

!!! info "このページを読む前に"
    [`std::fesetround`](fesetround.md) を先に読んでください。

## 関数の詳しい説明

### std::fetestexcept {#fetestexcept}

```cpp
int fetestexcept(int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `excepts` | int | 調べる例外のビットのマスク |

- 戻り値: 立っていたビットの組み合わせ（`0` なら立っていない）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feclearexcept(FE_ALL_EXCEPT);
  std::feraiseexcept(FE_DIVBYZERO);
  std::println("{}", std::fetestexcept(FE_DIVBYZERO) != 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 計算の異常を後からまとめて検知する |

## よくあるミス

??? failure "最適化で計算が消える"
    結果を使わない計算は、最適化で削除されることがあります。結果を使うか、`volatile` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fesetround`](fesetround.md) | 丸めモードを変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点例外のフラグを調べる
    - [x] `<cfenv>` の関数（浮動小数点環境の操作）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fetestexcept](https://cpprefjp.github.io/reference/cfenv/fetestexcept.html)
- [cppreference: std::fetestexcept](https://en.cppreference.com/w/cpp/numeric/fenv/fetestexcept)

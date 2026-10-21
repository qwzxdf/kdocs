---
title: std::overflow_error
summary: "計算結果が大きすぎて、表せないことを表す例外。"
order: 14
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::overflow_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <stdexcept>`
</div>

`std::overflow_error` は、**計算の結果が大きすぎて、型で表せなくなった**ことを表す例外です。標準ライブラリが自動で投げることは少なく、自分で桁あふれを検出したときに投げて使います。`underflow_error`（小さすぎる）の対です。

!!! tip "ポイント"
    - `runtime_error` の派生クラス。
    - 整数の桁あふれは、通常は未定義動作で、検出されない。自分で検査して投げる。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::overflow_error {#overflow_error}

```cpp
class overflow_error : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::overflow_error("加算が桁あふれ");
  } catch (const std::overflow_error& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
加算が桁あふれ
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 所持金の加算が上限を超えたとき | `throw std::overflow_error("gold overflow");` |

## よくあるミス

??? failure "標準が自動で投げると思う"
    整数の桁あふれは検出されません。`std::add_sat` などで防ぎます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`runtime_error`](runtime_error.md) | 親 |
| [`std::add_sat`](../../numeric/add_sat.md) | 桁あふれさせない足し算 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 結果が大きすぎる
    - [x] 自分で検査して投げる
    - [x] 整数は自動検出されない

## 関連ページ

- [cpprefjp: std::overflow_error](https://cpprefjp.github.io/reference/stdexcept/overflow_error.html)
- [cppreference: std::overflow_error](https://en.cppreference.com/w/cpp/error/overflow_error)

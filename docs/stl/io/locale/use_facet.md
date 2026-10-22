---
title: std::use_facet
summary: "ロケールから、ファセット（部品）を取り出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::use_facet

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`std::use_facet<ファセット>(ロケール)` で、そのロケールが持つ部品への参照を取り出します。持っていない部品を指定すると、`std::bad_cast` が投げられます。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::use_facet {#use_facet}

```cpp
template <class Facet>
const Facet& use_facet(const std::locale& loc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Facet` | テンプレート引数 | 取り出したいファセットの型 |
| `loc` | locale | 対象のロケール |

- 戻り値: ファセットへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  const auto& np = std::use_facet<std::numpunct<char>>(std::locale::classic());
  std::println("{}", np.decimal_point());
}
```

```text title="実行結果"
.
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ロケールごとの小数点記号を取り出す |

## よくあるミス

??? failure "存在しないファセットを指定する"
    持っていないと `bad_cast` が投げられます。`has_facet` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`has_facet`](has_facet.md) | あるかを調べる |
| [`numpunct`](numpunct.md) | 数字の記号 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロケールから、ファセット（部品）を取り出す
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::use_facet](https://cpprefjp.github.io/reference/locale/use_facet.html)
- [cppreference: std::use_facet](https://en.cppreference.com/w/cpp/locale/use_facet)

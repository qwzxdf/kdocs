---
title: std::numpunct
summary: "数値の書式（小数点・桁区切り）を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::numpunct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

小数点が `.` か `,` か、1000 ごとの区切りを何にするかは、国によって違います。その規則を持っているのが `numpunct` ファセットです。`decimal_point()`・`thousands_sep()`・`grouping()` などを返します。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::numpunct {#numpunct}

```cpp
template <class CharT>
class numpunct {
 public:
  CharT decimal_point() const;
  CharT thousands_sep() const;
  std::string grouping() const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |

- 戻り値: 小数点・桁区切りなど
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
| 使いどころ | 桁区切りを国ごとに変える |

## よくあるミス

??? failure "ストリームに設定し忘れる"
    ロケールを `imbue` しないと、書式は変わりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`num_put`](num_put.md) | 数値を書き出す |
| [`use_facet`](use_facet.md) | 取り出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数値の書式（小数点・桁区切り）を担当するファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::numpunct](https://cpprefjp.github.io/reference/locale/numpunct.html)
- [cppreference: std::numpunct](https://en.cppreference.com/w/cpp/locale/numpunct)

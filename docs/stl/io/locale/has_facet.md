---
title: std::has_facet
summary: "ロケールが、指定したファセット（部品）を持っているかを調べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::has_facet

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`use_facet` は、持っていない部品を指定すると例外になります。`has_facet<ファセット>(ロケール)` で先に調べられます。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::has_facet {#has_facet}

```cpp
template <class Facet>
bool has_facet(const std::locale& loc) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Facet` | テンプレート引数 | 調べるファセットの型 |
| `loc` | locale | 対象のロケール |

- 戻り値: 持っていれば `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  std::println("{}", std::has_facet<std::ctype<char>>(std::locale::classic()));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 独自のファセットが入っているか確かめる |

## よくあるミス

??? failure "標準のファセットを疑う"
    標準のロケールは、標準のファセットをすべて持っています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`use_facet`](use_facet.md) | 取り出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロケールが、指定したファセット（部品）を持っているかを調べる
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::has_facet](https://cpprefjp.github.io/reference/locale/has_facet.html)
- [cppreference: std::has_facet](https://en.cppreference.com/w/cpp/locale/has_facet)

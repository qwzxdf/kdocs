---
title: std::codecvt
summary: "文字コードの変換を行う、ロケールの部品。"
order: 100
tags:
  - 入出力・文字列
---

# std::codecvt

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11〜</span>
`#include <locale>`
</div>

`std::codecvt` は、ロケールの中で文字コード（UTF-8 と UTF-16 など）を変換する部品です。C++17 で `codecvt_utf8` などの便利な派生が非推奨になり、代わりになる標準の変換関数がありません。いまは Windows の `MultiByteToWideChar` や、ICU などのライブラリを使うのが現実的です。

!!! tip "ポイント"
    - `codecvt_utf8` などは C++17 で非推奨。
    - 代わりの標準 API は無い。
    - Windows では `MultiByteToWideChar` / `WideCharToMultiByte`。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::codecvt {#codecvt}

```cpp
template <class InternT, class ExternT, class StateT>
class codecvt;
```

| 引数 | 意味 |
| --- | --- |
| `InternT` | 内部の文字型 |
| `ExternT` | 外部の文字型 |

- `in` / `out` で変換します。通常は直接使わず、`wstring_convert` などから使いました

## 実際に動かしてみる

```cpp
#include <iostream>
#include <locale>

int main() {
  std::cout << std::has_facet<std::codecvt<char16_t, char, std::mbstate_t>>(std::locale()) << "\n";
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| UTF-8 と UTF-16 の変換 | Windows API / ICU を使う |

## よくあるミス

??? failure "wstring_convert を新しいコードで使う"
    C++17 で非推奨になりました。Windows API などの別の方法に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [文字コード](../../encoding/index.md) | UTF-8 統一の考え方 |
| [`std::locale`](locale.md) | ロケール |

## コンパイラ対応

C++11 から使えます。便利な派生（`codecvt_utf8` など）は C++17 で非推奨になりました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロケールの文字コード変換の部品。
    - [x] 便利な派生は非推奨。
    - [x] 代わりに Windows API / ICU。

## 関連ページ

- [cpprefjp: std::codecvt](https://cpprefjp.github.io/reference/locale/codecvt.html)
- [cppreference: std::codecvt](https://en.cppreference.com/w/cpp/locale/codecvt)

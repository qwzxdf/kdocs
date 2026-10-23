---
title: std::iswctype
summary: "ワイド文字が、指定した分類に属するかを調べる。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::iswctype

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

文字の種類を、実行時に選んだ分類で判定したい。`std::wctype` で分類を表す値を取り、`std::iswctype` で、ワイド文字がその分類に属するかを調べます。

!!! tip "ポイント"
    - `std::iswctype(wc, desc)` は、`wc` が分類 `desc` に属すれば 0 以外
    - `desc` は `std::wctype("alpha")` などで得る
    - `iswalpha(wc)` は `iswctype(wc, wctype("alpha"))` と同じ
    - 分類を実行時に切り替えたいときに使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::iswctype {#iswctype}

```cpp
int iswctype(std::wint_t wc, std::wctype_t desc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | `wint_t` | 調べるワイド文字 |
| `desc` | `wctype_t` | `wctype` で得た分類 |

戻り値は、`wc` が `desc` の分類に当てはまれば 0 以外、当てはまらなければ 0 です。`desc` が 0（未知の名前）のときの動作は決まっていないので、`wctype` の戻り値を確かめてから渡します。

固定の分類なら、`iswalpha` のような専用の関数のほうが短く、速いです。`iswctype` は、分類を設定や引数で切り替える、汎用の入口が必要なときだけ使います。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  const std::wctype_t digit = std::wctype("digit");
  std::println("iswctype(L'5', digit) = {}", std::iswctype(L'5', digit) != 0);
  std::println("iswctype(L'a', digit) = {}", std::iswctype(L'a', digit) != 0);
}
```

```text title="実行結果"
iswctype(L'5', digit) = true
iswctype(L'a', digit) = false
```

## ゲームでの使いどころ

分類を表す文字列を引数に受け取る、汎用の検査関数を作るときに使います。

```cpp
bool AllOf(std::wstring_view text, const char* category) {
  const std::wctype_t cat = std::wctype(category);
  return cat != 0 && std::ranges::all_of(text, [&](wchar_t c) { return std::iswctype(c, cat) != 0; });
}
```

## よくあるミス

??? failure "`wctype` が 0 を返したのに、そのまま渡す"
    戻り値を確かめてから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wctype`](wctype.md) | 分類を名前から得る |
| [`iswalpha`](iswalpha.md) | 英字か（専用の関数） |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `iswctype(wc, desc)` は分類で判定する
    - [x] `desc` は `wctype` で得る
    - [x] 固定の分類なら専用の関数が簡単

## 関連ページ

- [cpprefjp: std::iswctype](https://cpprefjp.github.io/reference/cwctype/iswctype.html)
- [cppreference: std::iswctype](https://en.cppreference.com/w/cpp/string/wide/iswctype)

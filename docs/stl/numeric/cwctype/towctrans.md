---
title: std::towctrans
summary: "ワイド文字を、指定した変換で変換する。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::towctrans

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cwctype>`
</div>

`std::wctrans` で選んだ変換を実際に 1 文字に適用するのが `std::towctrans` です。`towlower` や `towupper` を変換の種類を引数で受け取る形にしたものです。

!!! tip "ポイント"
    - `std::towctrans(wc, desc)` は、`wc` に変換 `desc` を適用して返す
    - `desc` は `std::wctrans("toupper")` などで得る
    - `towupper(wc)` は `towctrans(wc, wctrans("toupper"))` と同じ
    - 戻り値は `wint_t`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::towctrans {#towctrans}

```cpp
std::wint_t towctrans(std::wint_t wc, std::wctrans_t desc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | `wint_t` | 変換するワイド文字 |
| `desc` | `wctrans_t` | `wctrans` で得た変換 |

戻り値は、`wc` に変換 `desc` を適用した結果です。変換できない文字はそのまま返ります。

`desc` が 0（未知の名前）のときは、動作が決まっていません。`wctrans` の戻り値を確かめてから渡します。

固定の変換なら、専用の `towlower` と `towupper` が簡潔で速いので、`towctrans` を使う場面は限られます。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  const std::wctrans_t to_upper = std::wctrans("toupper");
  std::println("towctrans(L'a', toupper) = {}", static_cast<int>(std::towctrans(L'a', to_upper)));
}
```

```text title="実行結果"
towctrans(L'a', toupper) = 65
```

## ゲームでの使いどころ

変換の種類を引数にする汎用の関数で使います。

```cpp
std::wstring Convert(std::wstring s, const char* mode) {   // mode は "tolower" か "toupper"
  const std::wctrans_t t = std::wctrans(mode);
  if (t == 0) return s;
  for (auto& c : s) c = static_cast<wchar_t>(std::towctrans(c, t));
  return s;
}
```

## よくあるミス

??? failure "`wctrans` の戻り値 0 をそのまま渡す"
    先に確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wctrans`](wctrans.md) | 変換を名前から得る |
| [`towupper`](towupper.md) | 大文字化（専用） |
| [`towlower`](towlower.md) | 小文字化（専用） |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `towctrans(wc, desc)` は変換を適用する
    - [x] `desc` は `wctrans` で得る
    - [x] 固定なら `towlower` / `towupper`

## 関連ページ

- [cpprefjp: std::towctrans](https://cpprefjp.github.io/reference/cwctype/towctrans.html)
- [cppreference: std::towctrans](https://en.cppreference.com/w/cpp/string/wide/towctrans)

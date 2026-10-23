---
title: std::towupper
summary: "ワイド文字を大文字にする。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::towupper

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwctype>`
</div>

ワイド文字列で大文字小文字を区別せずに比べたいときは、両方を同じ側にそろえます。`std::towupper` は、<strong>ワイド文字の小文字を大文字に変換</strong>します。`<cctype>` の `toupper` の、`wchar_t` 版です。

!!! tip "ポイント"
    - 小文字を大文字に変換し、他の文字はそのまま返す
    - 戻り値は `wint_t`
    - ロケールによって、ASCII 以外の変換が変わる
    - `char` 版は `<cctype>` の `toupper`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::towupper {#towupper}

```cpp
std::wint_t towupper(std::wint_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | `wint_t` | 変換するワイド文字 |

戻り値は、`wc` が小文字なら対応する大文字、それ以外なら `wc` そのままです。

既定の "C" ロケールでは、ASCII の英字だけが変換されます。Windows で `setlocale(LC_ALL, "")` を呼ぶと、ギリシャ文字やキリル文字なども変換できます。ただし、1 文字ずつの変換なので、ドイツ語の ß のように大文字が 2 文字になる変換や、トルコ語のような言語固有の規則は扱えません。

大文字小文字を区別しない比較は、本来は、Unicode の大文字小文字の折り畳み規則を使うべきですが、ゲームのファイル名や ASCII のコマンドの比較であれば、この関数で足ります。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("towupper(L'a') = {}", static_cast<int>(std::towupper(L'a')));
  std::println("towupper(L'Z') = {}", static_cast<int>(std::towupper(L'Z')));
  std::println("towupper(L'5') = {}", static_cast<int>(std::towupper(L'5')));
}
```

```text title="実行結果"
towupper(L'a') = 65
towupper(L'Z') = 90
towupper(L'5') = 53
```

## ゲームでの使いどころ

ファイル名やコマンドを、大文字小文字を区別せずに比べるときに使います。

```cpp
#include <algorithm>
#include <string>

std::wstring Lower(std::wstring s) {
  std::ranges::transform(s, s.begin(), [](wchar_t c) { return static_cast<wchar_t>(std::towupper(c)); });
  return s;
}
```

## よくあるミス

??? failure "1 文字ずつの変換で、言語固有の規則を期待する"
    Unicode 対応のライブラリを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`towlower`](towlower.md) | 逆の変換 |
| [`std::toupper`](../cctype/toupper.md) | `char` 版 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `towupper` は小文字を大文字に変換する
    - [x] 他の文字はそのまま返る
    - [x] ロケールに依存する

## 関連ページ

- [cpprefjp: std::towupper](https://cpprefjp.github.io/reference/cwctype/towupper.html)
- [cppreference: std::towupper](https://en.cppreference.com/w/cpp/string/wide/towupper)

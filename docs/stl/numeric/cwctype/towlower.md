---
title: std::towlower
summary: "ワイド文字を小文字にする。"
order: 900
group: <cwctype> のワイド文字の判定・変換
tags:
  - 数値
---

# std::towlower

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwctype>`
</div>

ワイド文字列で大文字小文字を区別せずに比べたいときは、両方を同じ側にそろえます。`std::towlower` は、<strong>ワイド文字の大文字を小文字に変換</strong>します。`<cctype>` の `tolower` の、`wchar_t` 版です。

!!! tip "ポイント"
    - 大文字を小文字に変換し、他の文字はそのまま返す
    - 戻り値は `wint_t`
    - ロケールによって、ASCII 以外の変換が変わる
    - `char` 版は `<cctype>` の `tolower`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::towlower {#towlower}

```cpp
std::wint_t towlower(std::wint_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `wc` | `wint_t` | 変換するワイド文字 |

戻り値は、`wc` が大文字なら対応する小文字、それ以外なら `wc` そのままです。

既定の "C" ロケールでは、ASCII の英字だけが変換されます。Windows で `setlocale(LC_ALL, "")` を呼ぶと、ギリシャ文字やキリル文字なども変換できます。ただし、1 文字ずつの変換なので、ドイツ語の ß のように大文字が 2 文字になる変換や、トルコ語のような言語固有の規則は扱えません。

大文字小文字を区別しない比較は、本来は、Unicode の大文字小文字の折り畳み規則を使うべきですが、ゲームのファイル名や ASCII のコマンドの比較であれば、この関数で足ります。

## 実際に動かしてみる

```cpp
#include <cwctype>
#include <print>

int main() {
  std::println("towlower(L'A') = {}", static_cast<int>(std::towlower(L'A')));
  std::println("towlower(L'z') = {}", static_cast<int>(std::towlower(L'z')));
  std::println("towlower(L'5') = {}", static_cast<int>(std::towlower(L'5')));
}
```

```text title="実行結果"
towlower(L'A') = 97
towlower(L'z') = 122
towlower(L'5') = 53
```

## ゲームでの使いどころ

ファイル名やコマンドを大文字小文字を区別せずに比べるときに使います。

```cpp
#include <algorithm>
#include <string>

std::wstring Lower(std::wstring s) {
  std::ranges::transform(s, s.begin(), [](wchar_t c) { return static_cast<wchar_t>(std::towlower(c)); });
  return s;
}
```

## よくあるミス

??? failure "1 文字ずつの変換で、言語固有の規則を期待する"
    Unicode 対応のライブラリを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`towupper`](towupper.md) | 逆の変換 |
| [`std::tolower`](../cctype/tolower.md) | `char` 版 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cwctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `towlower` は大文字を小文字に変換する
    - [x] 他の文字はそのまま返る
    - [x] ロケールに依存する

## 関連ページ

- [cpprefjp: std::towlower](https://cpprefjp.github.io/reference/cwctype/towlower.html)
- [cppreference: std::towlower](https://en.cppreference.com/w/cpp/string/wide/towlower)

---
title: std::wcin
summary: "`wchar_t` の標準入力。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::wcin` は、`cin` の `wchar_t` 版です。`wchar_t` の文字列（`std::wstring`）を標準入力から読みます。`cin` と混ぜて使うと、文字化けや動作不良の原因になることがあります。

!!! tip "ポイント"
    - `cin` の`wchar_t` 版。
    - 出力先・入力元は同じ標準ストリーム。
    - ゲームでは `std::println` やログライブラリを使うことが多い。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wcin {#wcin}

```cpp
extern std::wistream wcin;
```

- 戻り値: `wistream`
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>
#include <string>

int main() {
  std::wstring name;
  std::wcin >> name;
  std::wcout << name << L"\n";
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ワイド文字の入力・出力 | `std::wcin >> name;` |

## よくあるミス

??? failure "`cin` と混ぜて使う"
    `cin` と `wcin` を 1 つのプログラムで混ぜると、向き（orientation）が食い違って、出力が壊れることがあります。どちらかに統一します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cin`](cin.md) | char 版 |
| [`std::println`](../utilities/print.md) | 新しい書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wchar_t` の標準入力
    - [x] cin のwchar_t 版
    - [x] 混ぜて使わない

## 関連ページ

- [cpprefjp: std::wcin](https://cpprefjp.github.io/reference/iostream/wcin.html)
- [cppreference: std::wcin](https://en.cppreference.com/w/cpp/io/wcin)

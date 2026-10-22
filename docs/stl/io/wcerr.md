---
title: std::wcerr
summary: "`wchar_t` の標準エラー出力。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcerr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::wcerr` は、`cerr` の `wchar_t` 版です。`wchar_t` の文字列（`L"..."`）を、標準エラー出力に出します。1 つのプログラムで `cerr` と `wcerr` を混ぜて使うと、文字化けや動作不良の原因になることがあります。

!!! tip "ポイント"
    - `cerr` の`wchar_t` 版。
    - 出力先・入力元は同じ標準ストリーム。
    - ゲームでは `std::println` やログライブラリを使うことが多い。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wcerr {#wcerr}

```cpp
extern std::wostream wcerr;
```

- 戻り値: `wostream`
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::wcerr << L"error\n";
}
```

```text title="実行結果"
error
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログ・エラーの出力 | `std::wcerr << ...;` |

## よくあるミス

??? failure "`cerr` と混ぜて使う"
    `cerr` と `wcerr` を 1 つのプログラムで混ぜると、向き（orientation）が食い違って、出力が壊れることがあります。どちらかに統一します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cerr`](cerr.md) | char 版 |
| [`std::println`](../utilities/print.md) | 新しい書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wchar_t` の標準エラー出力
    - [x] cerr のwchar_t 版
    - [x] 混ぜて使わない

## 関連ページ

- [cpprefjp: std::wcerr](https://cpprefjp.github.io/reference/iostream/wcerr.html)
- [cppreference: std::wcerr](https://en.cppreference.com/w/cpp/io/wcerr)

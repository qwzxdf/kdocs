---
title: std::wcout
summary: "`wchar_t` の標準出力。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcout

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::wcout` は、`cout` の `wchar_t` 版です。`wchar_t` の文字列（`L"..."`）を、標準出力に出します。`cout` と混ぜて使うと、文字化けや動作不良の原因になることがあります。

!!! tip "ポイント"
    - `cout` の`wchar_t` 版。
    - 出力先・入力元は同じ標準ストリーム。
    - ゲームでは `std::println` やログライブラリを使うことが多い。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wcout {#wcout}

```cpp
extern std::wostream wcout;
```

- 戻り値: `wostream`
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::wcout << L"hello " << 42 << L"\n";
}
```

```text title="実行結果"
hello 42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ワイド文字の入力・出力 | `std::wcout << ...;` |

## よくあるミス

??? failure "`cout` と混ぜて使う"
    `cout` と `wcout` を 1 つのプログラムで混ぜると、向き（orientation）が食い違って、出力が壊れることがあります。どちらかに統一します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cout`](cout.md) | char 版 |
| [`std::println`](../utilities/print.md) | 新しい書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wchar_t` の標準出力
    - [x] cout のwchar_t 版
    - [x] 混ぜて使わない

## 関連ページ

- [cpprefjp: std::wcout](https://cpprefjp.github.io/reference/iostream/wcout.html)
- [cppreference: std::wcout](https://en.cppreference.com/w/cpp/io/wcout)

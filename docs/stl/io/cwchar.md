---
title: <cwchar>
summary: "ワイド文字（`wchar_t`）の C 由来の関数群。"
order: 100
tags:
  - 入出力・文字列
---

# <cwchar>

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cwchar>`
</div>

`<cwchar>` には、`wcslen`・`wcscpy`・`wprintf` など、ワイド文字列を扱う C 由来の関数があります。Windows の API は `wchar_t`（UTF-16）が中心なので、Windows API との橋渡しで目にします。新しいコードでは `std::wstring` と `std::format` を使います。

!!! tip "ポイント"
    - `wcslen` などは `strlen` のワイド版。
    - Windows では `wchar_t` は 16 ビット（UTF-16）。
    - 新しいコードは `std::wstring`。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### wcslen {#wcslen}

```cpp
size_t wcslen(const wchar_t* s);
```

| 引数 | 意味 |
| --- | --- |
| `s` | ヌル終端のワイド文字列 |

- 終端を除いた文字数を返します。O(n) です

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <iostream>

int main() {
  std::cout << std::wcslen(L"abc") << "\n";
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| Windows API に渡す文字列の長さ | `std::wcslen(path)` |

## よくあるミス

??? failure "wchar_t を UTF-32 と考える"
    Windows の `wchar_t` は UTF-16 です。サロゲートペアで 1 文字が 2 要素になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string`](../containers/string.md) | C++ の文字列 |
| [文字コード](../../encoding/index.md) | UTF-8 と Windows API |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字の C 由来の関数群。
    - [x] Windows の `wchar_t` は UTF-16。
    - [x] 新しいコードは `std::wstring`。

## 関連ページ

- [cpprefjp: wcslen](https://cpprefjp.github.io/reference/cwchar/index.html)
- [cppreference: wcslen](https://en.cppreference.com/w/cpp/header/cwchar)

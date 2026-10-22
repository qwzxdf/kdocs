---
title: std::wstring
summary: "`wchar_t` を文字の型にもつ文字列。"
order: 900
tags:
  - コンテナ
---

# std::wstring

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

Windows の API は `wchar_t`（UTF-16）の文字列を使います。`std::wstring` は、その `wchar_t` の並びを扱う文字列です。`std::string` と同じ関数がそのまま使えます。

!!! tip "ポイント"
    - `std::basic_string<wchar_t>` の別名。
    - 文字列リテラルは `L"..."` と書く。
    - `std::string` と同じ関数が使える。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::wstring {#wstring}

```cpp
using wstring = basic_string<wchar_t>;
```

- 戻り値: `wstring` の値
- 計算量: string と同じ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::wstring s = L"abc";
  std::println("{}", s.size());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| プラットフォームの API に渡す | `std::wstring` |

## よくあるミス

??? failure "文字列の長さ = 文字数だと思う"
    `size()` は**コード単位**の数です。サロゲートペアや結合文字が入ると、見た目の文字数と一致しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string`](string.md) | char の文字列 |
| [`basic_string`](basic_string.md) | 元になるテンプレート |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] wchar_t の文字列
    - [x] std::string と同じ使い方
    - [x] size() はコード単位の数

## 関連ページ

- [cpprefjp: std::wstring](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::wstring](https://en.cppreference.com/w/cpp/string/basic_string)

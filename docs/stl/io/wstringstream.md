---
title: std::wstringstream
summary: "`wchar_t` の文字列ストリーム。"
order: 900
tags:
  - 入出力・文字列
---

# std::wstringstream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <sstream>`
</div>

`std::wstringstream` は、`stringstream` の `wchar_t` 版です。`wchar_t` の文字列を、組み立てたり解析したりするときに使います。

!!! tip "ポイント"
    - `stringstream` の `wchar_t` 版。
    - `wstring` を扱う。
    - ゲームでは UTF-8 の `string` を使うことが多い。

!!! info "このページを読む前に"
    [`std::stringstream`](stringstream.md) を先に読んでください。

## 関数の詳しい説明

### std::wstringstream {#wstringstream}

```cpp
using wstringstream = basic_stringstream<wchar_t>;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <print>
#include <sstream>

int main() {
  std::wstringstream ss;
  ss << L"abc" << 42;
  std::println("{}", ss.str().size());
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| Windows API と文字列をやり取りする | `std::wstringstream` |

## よくあるミス

??? failure "文字コードを考えない"
    `wchar_t` は Windows では UTF-16、Linux では UTF-32 です。環境で意味が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stringstream`](stringstream.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wchar_t` の文字列ストリーム
    - [x] stringstream の wchar_t 版
    - [x] UTF-8 の string が主流

## 関連ページ

- [cpprefjp: std::wstringstream](https://cpprefjp.github.io/reference/sstream/wstringstream.html)
- [cppreference: std::wstringstream](https://en.cppreference.com/w/cpp/io/wstringstream)

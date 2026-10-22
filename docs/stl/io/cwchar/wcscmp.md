---
title: std::wcscmp
summary: "2 つのワイド文字列を比べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcscmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`strcmp` の `wchar_t` 版です。辞書順ではなく、文字コードの順で比べます。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wcscmp {#wcscmp}

```cpp
int wcscmp(const wchar_t* lhs, const wchar_t* rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs, rhs` | const wchar_t* | 比べる 2 つの文字列 |

- 戻り値: `lhs < rhs` なら負、等しければ 0、大きければ正
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("{}", std::wcscmp(L"a", L"b") < 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字列の比較 |

## よくあるミス

??? failure "戻り値を `-1` / `1` と思う"
    負・0・正のどれかです。値は決まっていません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcmp`](../../memory/cstring/strcmp.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つのワイド文字列を比べる
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wcscmp](https://cpprefjp.github.io/reference/cwchar/wcscmp.html)
- [cppreference: std::wcscmp](https://en.cppreference.com/w/cpp/string/wide/wcscmp)

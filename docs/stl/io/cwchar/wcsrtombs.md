---
title: std::wcsrtombs
summary: "ワイド文字列を、マルチバイト文字列に変換する（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcsrtombs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wcstombs` の再入可能版です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wcsrtombs {#wcsrtombs}

```cpp
std::size_t wcsrtombs(char* dst, const wchar_t** src, std::size_t len, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dst` | char* | 変換結果の書き込み先 |
| `src` | const wchar_t** | 変換元（変換した位置まで進む） |
| `len` | size_t | 書き込む最大のバイト数 |
| `ps` | mbstate_t* | 変換の途中状態 |

- 戻り値: 書き込んだバイト数。不正なら `(size_t)-1`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  const wchar_t* s = L"abc";
  char buf[8];
  std::mbstate_t st{};
  std::println("{}", std::wcsrtombs(buf, &s, 8, &st));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字列を UTF-8 などに戻す |

## よくあるミス

??? failure "元の文字列を失う"
    `src` が進みます。元のポインタを別に持っておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wcstombs`](../../numeric/cstdlib/wcstombs.md) | 途中状態なし |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字列を、マルチバイト文字列に変換する（途中状態つき）
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wcsrtombs](https://cpprefjp.github.io/reference/cwchar/wcsrtombs.html)
- [cppreference: std::wcsrtombs](https://en.cppreference.com/w/cpp/string/wide/wcsrtombs)

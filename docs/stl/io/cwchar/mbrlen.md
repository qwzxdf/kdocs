---
title: std::mbrlen
summary: "マルチバイト文字 1 文字のバイト数を返す（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::mbrlen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`mblen` の再入可能版です。変換の途中状態（`mbstate_t`）を引数で受け取るので、スレッドで安全です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::mbrlen {#mbrlen}

```cpp
std::size_t mbrlen(const char* s, std::size_t n, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | const char* | 調べるバイト列 |
| `n` | size_t | 調べる最大のバイト数 |
| `ps` | mbstate_t* | 変換の途中状態 |

- 戻り値: 1 文字のバイト数。不正なら `(size_t)-1`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::mbstate_t st{};
  std::println("{}", std::mbrlen("A", 1, &st));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 可変長の文字列の文字数を数える |

## よくあるミス

??? failure "`mbstate_t` を初期化しない"
    最初に `std::mbstate_t st{};` で 0 に初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mblen`](../../numeric/cstdlib/mblen.md) | 途中状態なし |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] マルチバイト文字 1 文字のバイト数を返す（途中状態つき）
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::mbrlen](https://cpprefjp.github.io/reference/cwchar/mbrlen.html)
- [cppreference: std::mbrlen](https://en.cppreference.com/w/cpp/string/wide/mbrlen)

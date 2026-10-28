---
title: std::mbstate_t
summary: "マルチバイト文字の変換の途中状態を入れる型。"
order: 900
tags:
  - 入出力・文字列
---

# std::mbstate_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

UTF-8 のように、1 文字が複数バイトの文字列を変換するとき、途中で区切られた文字の続きを覚えておく必要があります。その状態を入れる型が `mbstate_t` で、`mbrtowc` などの関数が受け取ります。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::mbstate_t {#mbstate_t}

```cpp
using mbstate_t = /* 実装定義 */;
```

- 戻り値: なし（型）
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
| 使いどころ | 文字コードの変換を 1 文字ずつ行う |

## よくあるミス

??? failure "初期化しない"
    変換を始める前に `std::mbstate_t st{};` で 0 に初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbrtowc`](mbrtowc.md) | この型を使う関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] マルチバイト文字の変換の途中状態を入れる型
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::mbstate_t](https://cpprefjp.github.io/reference/cwchar/mbstate_t.html)
- [cppreference: std::mbstate_t](https://en.cppreference.com/w/cpp/string/wide/mbstate_t)

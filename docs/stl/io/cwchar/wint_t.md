---
title: std::wint_t
summary: "ワイド文字と WEOF を入れられる整数型。"
order: 900
tags:
  - 入出力・文字列
---

# std::wint_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wchar_t` の値に加えて、終端を表す `WEOF` を入れられる整数型です。`fgetwc` などの戻り値で、`wchar_t` ではなく `wint_t` を使うのは、この `WEOF` を区別するためです。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wint_t {#wint_t}

```cpp
using wint_t = /* 整数型 */;
```

- 戻り値: なし（型）
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::wint_t c = L'A';
  std::println("{}", static_cast<int>(c));
}
```

```text title="実行結果"
65
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字の読み込みの戻り値を受ける |

## よくあるミス

??? failure "`wchar_t` で受ける"
    `WEOF` と文字を区別できなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`WEOF`](weof.md) | 終端を表す定数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字と WEOF を入れられる整数型
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wint_t](https://cpprefjp.github.io/reference/cwchar/wint_t.html)
- [cppreference: std::wint_t](https://en.cppreference.com/w/cpp/string/wide/wint_t)

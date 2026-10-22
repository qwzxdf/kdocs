---
title: WEOF
summary: "ワイド文字の終端またはエラーを表す定数。"
order: 900
tags:
  - 入出力・文字列
---

# WEOF

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fgetwc` などが、終端やエラーを知らせるときに返す値です。`wchar_t` の文字とは区別できる値です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### WEOF {#weof}

```cpp
#define WEOF /* wint_t の値（実装定義） */
```

- 戻り値: 終端を表す `wint_t` の値
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::println("{}", std::fgetwc(f) == WEOF);
  std::fclose(f);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `fgetwc` の結果の判定 |

## よくあるミス

??? failure "`wchar_t` と比べる"
    `wint_t` で受けて比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wint_t`](wint_t.md) | ワイド文字を受ける型 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字の終端またはエラーを表す定数
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: WEOF](https://cpprefjp.github.io/reference/cwchar/weof.html)
- [cppreference: WEOF](https://en.cppreference.com/w/cpp/string/wide/WEOF)

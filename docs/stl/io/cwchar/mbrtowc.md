---
title: std::mbrtowc
summary: "マルチバイト文字を、ワイド文字に変換する（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::mbrtowc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`mbtowc` の再入可能版です。途中で区切られた文字も、続きから変換できます。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::mbrtowc {#mbrtowc}

```cpp
std::size_t mbrtowc(wchar_t* pwc, const char* s, std::size_t n, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pwc` | wchar_t* | 変換結果の書き込み先 |
| `s` | const char* | 変換元 |
| `n` | size_t | 調べる最大のバイト数 |
| `ps` | mbstate_t* | 変換の途中状態 |

- 戻り値: 使ったバイト数。不正なら `(size_t)-1`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::mbstate_t st{};
  wchar_t w = 0;
  std::size_t n = std::mbrtowc(&w, "A", 1, &st);
  std::println("{} {}", n, static_cast<int>(w));
}
```

```text title="実行結果"
1 65
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | UTF-8 の文字列を 1 文字ずつワイド文字にする |

## よくあるミス

??? failure "ロケールを設定しない"
    既定の `"C"` ロケールでは ASCII のみです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbtowc`](../../numeric/cstdlib/mbtowc.md) | 途中状態なし |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] マルチバイト文字を、ワイド文字に変換する（途中状態つき）
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::mbrtowc](https://cpprefjp.github.io/reference/cwchar/mbrtowc.html)
- [cppreference: std::mbrtowc](https://en.cppreference.com/w/cpp/string/wide/mbrtowc)

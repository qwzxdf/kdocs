---
title: std::wcrtomb
summary: "ワイド文字を、マルチバイト文字に変換する（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcrtomb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wctomb` の再入可能版です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wcrtomb {#wcrtomb}

```cpp
std::size_t wcrtomb(char* s, wchar_t wc, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | char* | 変換結果の書き込み先（`MB_CUR_MAX` バイト以上） |
| `wc` | wchar_t | 変換するワイド文字 |
| `ps` | mbstate_t* | 変換の途中状態 |

- 戻り値: 書き込んだバイト数。変換できなければ `(size_t)-1`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <climits>
#include <cwchar>
#include <print>

int main() {
  char buf[MB_LEN_MAX];
  std::mbstate_t st{};
  std::println("{}", std::wcrtomb(buf, L'A', &st));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字を UTF-8 などに戻す |

## よくあるミス

??? failure "バッファが小さい"
    `MB_CUR_MAX`（最大のバイト数）以上の大きさが必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wctomb`](../../numeric/cstdlib/wctomb.md) | 途中状態なし |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字を、マルチバイト文字に変換する（途中状態つき）
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wcrtomb](https://cpprefjp.github.io/reference/cwchar/wcrtomb.html)
- [cppreference: std::wcrtomb](https://en.cppreference.com/w/cpp/string/wide/wcrtomb)

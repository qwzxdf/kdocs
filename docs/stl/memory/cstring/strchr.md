---
title: strchr
summary: "C 文字列の中から、1 文字を探す。"
order: 9
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strchr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strchr` は、**C 文字列の中から、指定した文字を先頭から探す**関数です。見つかれば位置のポインター、なければ `nullptr` を返します。`std::string::find` が同じことをします。

!!! tip "ポイント"
    - `strrchr` は後ろから探す版。
    - 終端の `\0` も探せる。
    - C++ では `std::string::find` を使う。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strchr {#strchr}

```cpp
const char* strchr(const char* str, int ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 探す C 文字列 |
| `ch` | `int` | 探す文字 |

- 戻り値: 最初に見つかった位置のポインタ。なければ `nullptr`。`ch` に `'\0'` を渡すと、終端の位置が返る
- `std::string_view::find` のほうが安全です。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* s = "hello";
  std::println("{} {}", std::strchr(s, 'l') - s, std::strrchr(s, 'l') - s);
}
```

```text title="実行結果"
2 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パスの拡張子（最後の `.`）を探す | `strrchr(path, '.')` |

## よくあるミス

??? failure "戻り値を調べずに使う"
    `nullptr` のことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::string::find` | C++ の同等品 |
| [`memchr`](memchr.md) | バイト列用 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字を探す
    - [x] 無ければ nullptr
    - [x] C++ では `find`

## 関連ページ

- [cpprefjp: strchr](https://cpprefjp.github.io/reference/cstring/strchr.html)
- [cppreference: strchr](https://en.cppreference.com/w/cpp/string/byte/strchr)

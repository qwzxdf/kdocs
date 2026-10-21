---
title: snprintf
summary: "書式に従って、バッファの大きさを守って文字列を書き込む。"
order: 14
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# snprintf

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

`snprintf` は、**書式に従って文字列を作り、指定した大きさを超えないようにバッファへ書き込む**関数です。必ず終端 `\0` が付きます。`printf` の「文字列版」で、C のライブラリとのやり取りで今でも使われます。C++20 以降は [`std::format_to_n`](../../utilities/format_to.md) が型安全な代わりです。

!!! tip "ポイント"
    - `snprintf(buf, sizeof(buf), "HP %d/%d", hp, max_hp);`
    - 戻り値は「あふれなければ書かれたはずの文字数」。大きさの確認に使える。
    - 書式と引数の型を合わせないと未定義動作（`std::format` は安全）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### snprintf {#snprintf}

```cpp
int snprintf(char* buffer, std::size_t bufsz, const char* format, ...);  // <cstdio>
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 書き込み先 |
| `bufsz` | `std::size_t` | `buffer` の大きさ（終端の `'\0'` を含む） |
| `format` | `const char*` | `printf` 形式の書式 |

- 戻り値: **書き込めていれば書かれたはずの文字数**（`bufsz` 以上なら、切り捨てられている）
- 必ず終端の `'\0'` を書いてくれる、**大きさを守る安全な書式付き出力**です（`sprintf` は大きさを見ないので使いません）
- C++ では、[`std::format_to_n`](../../utilities/format_to.md#format_to_n) が型安全な代わりです。

```cpp
char label[16];
std::snprintf(label, sizeof(label), "HP %d/%d", 30, 100);  // 長すぎても、15 文字で切れて安全
```

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cstring>
#include <print>

int main() {
  char buf[16];
  int n = std::snprintf(buf, sizeof(buf), "HP %d/%d", 45, 120);
  std::println("{} {}", buf, n);
}
```

```text title="実行結果"
HP 45/120 9
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定長のバッファに HUD の文字列を書く | `snprintf(buf, sizeof(buf), ...)` |

## よくあるミス

??? failure "書式と型が合わない"
    `%d` に `float` を渡すと未定義動作です。型安全な `std::format` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format_to_n`](../../utilities/format_to.md) | 型安全な代わり |
| [`std::println`](../../utilities/print.md) | 出力するなら |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きさを守って書式化する
    - [x] 終端が必ず付く
    - [x] 型安全なのは `format_to_n`

## 関連ページ

- [cpprefjp: snprintf](https://cpprefjp.github.io/reference/cstring/snprintf.html)
- [cppreference: snprintf](https://en.cppreference.com/w/cpp/string/byte/snprintf)

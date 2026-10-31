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

数値を含む文字列を、固定長のバッファに組み立てたい。`std::snprintf(buf, n, fmt, ...)` は、`printf` と同じ書式で、最大 `n - 1` 文字を `buf` に書き、必ず終端を付けます。あふれても安全で、本来の長さも返すので、切り詰められたかが分かります。

!!! tip "ポイント"
    - 最大 `n - 1` 文字を書き、必ず終端を付ける（`n` が 0 でなければ）
    - 戻り値は、省略されなかった場合の本来の長さ（終端を除く）
    - 戻り値が `n` 以上なら、切り詰められた
    - `buf` を `nullptr`、`n` を 0 にすると、長さだけが得られる

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::snprintf {#snprintf}

```cpp
int snprintf(char* buffer, std::size_t bufsz, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 書き込み先 |
| `bufsz` | `std::size_t` | `buffer` の大きさ（終端を含む） |
| `format` | `const char*` | 書式 |

`sprintf` は大きさを指定できず、あふれる危険がありますが、`snprintf` は大きさを渡します。

戻り値で、必要な大きさが分かるので、切り詰められたときに、大きな領域で作り直せます。

```cpp
int len = std::snprintf(nullptr, 0, "%d", value);   // 必要な長さ
std::string s(len, '\0');
std::snprintf(s.data(), len + 1, "%d", value);
```

C++20 以降は、`std::format` / `std::format_to_n` のほうが、型の安全があり、書式の誤りをコンパイル時に検出できます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  char buf[16];
  const int n = std::snprintf(buf, sizeof(buf), "HP %d/%d", 30, 100);
  std::println("{} ({} 文字)", buf, n);

  // 小さいバッファ: 切り詰められるが、本来の長さが分かる
  char small[6];
  const int m = std::snprintf(small, sizeof(small), "HP %d/%d", 30, 100);
  std::println("{} 本来の長さ {} 切り詰められた {}", small, m, m >= static_cast<int>(sizeof(small)));
}
```

```text title="実行結果"
HP 30/100 (9 文字)
HP 30 本来の長さ 9 切り詰められた true
```

## ゲームでの使いどころ

C の API に渡す固定長のバッファに、書式つきで文字列を作るときに使います。C++ の新しいコードは `std::format` です。

## よくあるミス

??? failure "戻り値を調べない"
    切り詰められても気づきません。

??? failure "bufsz に文字数を渡す"
    終端の分を含む、バッファの大きさを渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_to_n`](../../utilities/format_to_n.md) | C++20 の同様の関数 |
| `std::format` | 文字列を返す |
| [`strcpy`](strcpy.md) | あふれる危険がある |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: snprintf](https://cpprefjp.github.io/reference/cstring/snprintf.html)
- [cppreference: snprintf](https://en.cppreference.com/w/cpp/string/byte/snprintf)

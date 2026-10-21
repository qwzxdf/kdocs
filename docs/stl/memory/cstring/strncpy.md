---
title: strncpy
summary: "C 文字列を最大 n 文字コピーする（終端に注意）。"
order: 12
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strncpy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strncpy` は、**C 文字列を最大 n 文字までコピーする**関数です。`strcpy` より安全に見えますが、**n 文字を使い切ると終端の `\0` が付かない**落とし穴があります。

!!! tip "ポイント"
    - 終端 `\0` を、自分で付ける必要がある。
    - 短いときは、残りを `\0` で埋める（余計な時間）。
    - 新しいコードでは `snprintf` や `std::string`。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strncpy {#strncpy}

```cpp
char* strncpy(char* dest, const char* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | コピー先 |
| `src` | `const char*` | コピー元 |
| `count` | `std::size_t` | コピーする最大の文字数 |

- 戻り値: `dest`
- 安全そうに見えますが、**`src` が `count` 以上の長さのとき、終端の `'\0'` を書いてくれません**。そのまま `strlen` や `printf` に渡すと範囲外を読みます。短いときは、残りを `'\0'` で埋めるので、無駄に遅い場合もあります
- 使うなら、最後に自分で `dest[count - 1] = '\0';` と書きます。基本は `std::string` を使います

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char dst[4] = {};
  std::strncpy(dst, "abcdef", 3);
  dst[3] = '\0';  // 終端は自分で付ける
  std::println("{}", dst);
}
```

```text title="実行結果"
abc
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定長バッファへ名前をコピーする（古い書き方） | `strncpy(name, src, sizeof(name) - 1); name[sizeof(name) - 1] = 0;` |

## よくあるミス

??? failure "終端を付け忘れる"
    `n` 文字ぴったりだと終端が付かず、後で読むと暴走します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcpy`](strcpy.md) | 長さを確認しない |
| [`snprintf`](snprintf.md) | 終端が必ず付く |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大 n 文字コピー
    - [x] 終端が付かないことがある
    - [x] `snprintf` のほうが安全

## 関連ページ

- [cpprefjp: strncpy](https://cpprefjp.github.io/reference/cstring/strncpy.html)
- [cppreference: strncpy](https://en.cppreference.com/w/cpp/string/byte/strncpy)

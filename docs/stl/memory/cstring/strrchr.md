---
title: std::strrchr
summary: "文字列の中から、指定した文字が最後に現れる位置を探す。"
order: 900
tags:
  - メモリ
---

# std::strrchr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

ファイルのパスから拡張子を取り出したい。最後の `.` の位置が必要です。`std::strrchr(s, ch)` は、`strchr` と逆に、<strong>最後に現れる</strong> `ch` の位置を返します。

!!! tip "ポイント"
    - 最後に見つかった位置へのポインタを返す。なければ `nullptr`
    - `strchr` の逆方向版
    - 拡張子や、パスの最後の区切りを探すのに使う
    - `ch` が `'\0'` なら、終端の位置

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strrchr {#strrchr}

```cpp
const char* strrchr(const char* str, int ch);
char* strrchr(char* str, int ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 探す対象の文字列 |
| `ch` | `int` | 探す文字 |

`nullptr` の確認が必要な点は `strchr` と同じです。

パスの扱いでは、区切りの文字が `/` と `\` の両方ありうる Windows に注意します。ファイル名やパスの操作は、`std::filesystem::path` を使うほうが確実です。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* path = "assets/hero.png";
  const char* dot = std::strrchr(path, '.');
  const char* slash = std::strrchr(path, '/');
  std::println("拡張子: {}", dot != nullptr ? dot + 1 : "なし");
  std::println("ファイル名: {}", slash != nullptr ? slash + 1 : path);
}
```

```text title="実行結果"
拡張子: png
ファイル名: hero.png
```

## ゲームでの使いどころ

拡張子の判定に使いますが、`std::filesystem::path::extension()` のほうが安全です。

## よくあるミス

??? failure "ディレクトリ名の中の . を拡張子と間違える"
    `dir.v2/file` では、最後の `.` が拡張子ではありません。`path` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strchr`](strchr.md) | 最初の位置を探す |
| `std::filesystem::path` | パスの専用の型 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strrchr](https://cpprefjp.github.io/reference/cstring/strrchr.html)
- [cppreference: std::strrchr](https://en.cppreference.com/w/cpp/string/byte/strrchr)

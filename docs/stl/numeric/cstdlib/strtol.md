---
title: std::strtol
summary: "文字列を整数に変換する（進数の指定・終了位置・エラーの検出ができる）。"
order: 3
group: <cstdlib> の関数
tags:
  - 数値
---

# std::strtol

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::strtol` は、**文字列を `long` に変換する**C 由来の関数で、`atoi` より多機能です。進数を指定でき（16 進数なら 16）、読み終えた位置が分かり、範囲外のときは `errno` に `ERANGE` が入ります。

!!! tip "ポイント"
    - `strtol(str, &end, 16)` で 16 進数を読む。
    - `end` が読み終えた位置。`*end != '\0'` なら、数字以外が残っている。
    - 新しいコードでは `from_chars`（高速で例外なし）。

## 関数の詳しい説明

### std::strtol {#strtol}

```cpp
long strtol(const char* str, char** end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 変換する文字列 |
| `end` | `char**` | 読み終えた位置の書き込み先（`nullptr` 可） |
| `base` | `int` | 進数（0 なら接頭辞で自動判定） |

- 戻り値: 変換した値
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <print>

int main() {
  char* end = nullptr;
  long v = std::strtol("ff", &end, 16);   // 16 進数
  std::println("{} {}", v, *end == '\0');
}
```

```text title="実行結果"
255 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 色コード（16 進数）の文字列を数値にする | `std::strtol(hex, nullptr, 16)` |

## よくあるミス

??? failure "エラーを確認しない"
    `errno` と `end` の両方を確認しないと、失敗に気づきません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::from_chars`](../../io/from_chars.md) | 新しい書き方 |
| [`atoi`](atoi.md) | 失敗が分からない簡易版 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 進数指定・終了位置・エラー検出ができる
    - [x] `errno == ERANGE` で範囲外
    - [x] 新しいコードは from_chars

## 関連ページ

- [cpprefjp: std::strtol](https://cpprefjp.github.io/reference/cstdlib/strtol.html)
- [cppreference: std::strtol](https://en.cppreference.com/w/cpp/numeric/math/strtol)

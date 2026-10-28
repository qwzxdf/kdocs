---
title: std::strtold
summary: "文字列を long double に変換する（読み終えた位置が分かる）。"
order: 900
tags:
  - 数値
---

# std::strtold

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

小数の文字列を数値にするとき、`std::strtod` は `double` を返します。`long double`で受けたい場合に型違いの `std::strtold` を使います。読み終えた位置を教えてくれる点は同じです。

!!! tip "ポイント"
    - 戻り値は `long double`
    - 読み終えた位置が `str_end` に入る
    - 指数表記、`inf`、`nan` も読める
    - 範囲を超えると `HUGE_VAL` 系の値と `ERANGE`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::strtold {#strtold}

```cpp
long double strtold(const char* str, char** str_end);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 変換する文字列 |
| `str_end` | `char**` | 読み終えた位置の書き込み先。不要なら `nullptr` |

戻り値は変換した値で、型は long double です。先頭の空白を飛ばし、符号、数字、小数点、指数（`e` または `E`）を読みます。

`str_end` に、読めなかった最初の文字の位置が入ります。何も読めなければ `*str_end == str` で、0 を返します。

`long double` は環境で精度が違います（MSVC では `double` と同じ 64 ビット、GCC の x86 では 80 ビット）。精度を頼りにするコードは移植に注意します。

小数点はロケールに依存します。新しいコードでは `std::from_chars` が、ロケール非依存で速く、精度も正確です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  char* end = nullptr;
  const long double a = std::strtold("3.5xyz", &end);
  std::println("値 = {}, 残り = {}", a, end);
  std::println("1e2 = {}", std::strtold("1e2", nullptr));
}
```

```text title="実行結果"
値 = 3.5, 残り = xyz
1e2 = 100
```

## ゲームでの使いどころ

設定ファイルから小数を読む処理で、失敗を検出したいときに使います。

```cpp
char* end = nullptr;
const long double v = std::strtold(text.c_str(), &end);
if (end == text.c_str()) { /* 数値として読めなかった */ }
```

## よくあるミス

??? failure "ロケールの小数点で読み込みが壊れる"
    ロケールを変えない、または `from_chars` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strtod`](strtod.md) | `double` を返す |
| [`atof`](atof.md) | 失敗が分からない簡易版 |
| [`from_chars`](../../io/from_chars.md) | ロケール非依存 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `strtold` は文字列を long double に変換する
    - [x] `str_end` で読み終えた位置が分かる
    - [x] ロケールの影響を受ける。新しいコードは `from_chars`

## 関連ページ

- [cpprefjp: std::strtold](https://cpprefjp.github.io/reference/cstdlib/strtold.html)
- [cppreference: std::strtold](https://en.cppreference.com/w/cpp/c/strtold)

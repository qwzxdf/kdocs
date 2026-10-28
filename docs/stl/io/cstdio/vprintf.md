---
title: std::vprintf
summary: "可変引数のリスト（va_list）を使って、標準出力に出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::vprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

自作のログ関数 `Log("HP: %d", hp)` を作りたい。引数の数が決まっていない（可変個引数）関数の中で、受け取った引数をそのまま `printf` に渡したい。ところが、`printf(fmt, ...)` の `...` を、別の関数に転送する方法はありません。

そのために、可変個引数を `va_list` という 1 つの値にまとめて渡す、`std::vprintf` があります。

!!! tip "ポイント"
    - `vprintf(書式, va_list)`。`printf` の可変個引数を、`va_list` に置き換えた版
    - 自作のログ関数で、受け取った `...` を、`va_start` で `va_list` にして渡す
    - 使ったあとは `va_end` を呼ぶ
    - 戻り値は、書いた文字数。失敗は負の値

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vprintf {#vprintf}

```cpp
int vprintf(const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び。`va_start` で作る |

自作のログ関数は、次の形になります。

```cpp
void Log(const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);      // fmt の次の引数から
  std::vprintf(fmt, args);
  va_end(args);
}
```

`va_start` は、最後の固定引数（ここでは `fmt`）を渡します。`va_end` を忘れると、環境によってはメモリがリークします。

`va_list` は、一度 `vprintf` に渡すと、中身が壊れる場合があります。同じ引数で 2 回出力したいときは、`va_copy` でコピーを作ってから使います。

書式と値の型が合わないと、未定義動作になる点は、`printf` と同じです。GCC / Clang の `__attribute__((format(printf, 1, 2)))` を付けると、自作のログ関数にも書式のチェックが効きます。C++20 以降なら `std::format` を使うと、この問題はコンパイル時に検出されます。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>

void Log(const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vprintf(fmt, args);   // 受け取った ... を、そのまま渡す
  va_end(args);
}

int main() {
  Log("HP: %d / %d\n", 85, 120);
  Log("名前: %s\n", "hero");
}
```

```text title="実行結果"
HP: 85 / 120
名前: hero
```

## ゲームでの使いどころ

自作のログ関数やデバッグ出力の関数で、`printf` と同じ書き方を提供するときに使います。ログ レベルや時刻の接頭辞を付けたい場合も、この形でラップします。

C++20 以降では、`std::format` / `std::vformat` を使った、型安全なログ関数のほうが、書式のミスを防げます。C のライブラリとの境界など、`va_list` が必要な場面で使います。

## よくあるミス

??? failure "`va_end` を忘れる"
    必ず対にして呼びます。

??? failure "`va_list` を 2 回使って、壊れた値が出る"
    `va_copy` でコピーしてから使います。

??? failure "ユーザー入力を書式にして渡す"
    `Log("%s", input)` のように、値として渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vfprintf`](vfprintf.md) | 出力先を選べる |
| [`vsnprintf`](vsnprintf.md) | 文字配列に、大きさを指定して書く |
| [`printf`](printf.md) | 可変個引数のまま受け取る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `va_list` を受け取る `printf`
    - [x] 自作のログ関数で使う
    - [x] `va_start` と `va_end` を対にする

## 関連ページ

- [cpprefjp: std::vprintf](https://cpprefjp.github.io/reference/cstdio/vprintf.html)
- [cppreference: std::vprintf](https://en.cppreference.com/w/cpp/io/c/vprintf)

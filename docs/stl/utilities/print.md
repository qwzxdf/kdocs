---
title: std::print
summary: "書式に従って、そのまま画面（標準出力）に出す。println は末尾に改行を付ける。"
order: 46
tags:
  - ユーティリティ
---

# std::print

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-23">C++23</span>
`#include <print>`
</div>

デバッグ中にゲームの状態を画面に出したいとき、`std::cout << name << " HP " << hp << "/" << max_hp << "\n"` のように `<<` を並べると、読みにくく、書式の指定も面倒です。`printf` は書式を書きやすい反面、型を間違えると未定義動作になります。`std::println` は、`{}` に値を埋め込める書き方で、型は自動で合い、間違えればコンパイルエラーになります。

!!! tip "ポイント"
    - 普段は **`std::println("HP {}/{}", hp, max_hp);`** と書けばよい。改行が要らないときだけ `std::print`。
    - `std::println(stderr, ...)` で標準エラー出力に出せる。
    - 書式文字列は**コンパイル時に決まっている**必要がある（実行時に決めるなら [`std::vformat`](vformat.md)）。
    - Windows のコンソールでも、UTF-8 の文字列を正しく出せる（`/utf-8` が必要）。

!!! info "このページを読む前に"
    書式文字列の書き方は [`std::format`](format.md) と共通です。`{}` の中に書ける指定は、そちらで説明しています。

## 関数の詳しい説明

### std::print <span class="ver ver-23">C++23</span> {#print data-toc-label="std::print"}

```cpp
template <class... Args>
void print(std::format_string<Args...> fmt, Args&&... args);
```

- `println` の改行なし版です

```cpp
#include <print>

int main() {
  for (int i = 0; i < 3; ++i) {
    std::print("{} ", i);
  }
  std::print("\n");
}
```

```text title="実行結果"
0 1 2 
```

## ゲームでの使いどころ

デバッグ表示とログの出力がいちばん多い使いどころです。`std::println("{} HP {}/{}", name, hp, max_hp);` のように、値を見やすく出せます。座標や配列も、そのまま `{}` に渡して出せます。

エラーは標準エラー出力に出すと、通常の出力と分けて扱えます。`std::println(stderr, "エラー: {}", code);` と書きます。

ゲームの本番では、コンソールを出さない構成が多いので、`println` はデバッグ専用です。製品のログは、ファイルや画面内のコンソールに書き出す仕組みを別に作り、そこでは `std::format` で文字列を作ります。

## よくあるミス

??? failure "古いコンパイラで使えない"
    `<print>` は C++23 で入りました。Visual Studio 2022 の 17.7 以降、GCC 14 以降、Clang 18 以降が必要です。古いコンパイラでは、`std::format` で文字列を作って `std::cout` に出す方法で代用します。

??? failure "書式文字列を変数にする"
    `std::println(fmt, x)` で `fmt` が実行時に決まる文字列だと、コンパイル時の検査ができないため、コンパイルエラーになります。実行時に決まる書式を使うときは、`std::vformat` と `std::make_format_args` を使います。

??? failure "波かっこそのものを出す"
    `std::println("{")` は書式エラーです。波かっこそのものを出すには、`{{` と `}}` と二重に書きます。

??? failure "`println` の引数で副作用のある関数を複数回呼ぶ"
    `std::println("{} {}", Next(), Next())` のように、同じ関数を引数の式で複数回呼ぶと、評価の順番が決まっていないため、出力の順番が環境によって変わります。値を変数に受けてから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](format.md) | 文字列を作る（出力はしない） |
| [`std::cout`](../io/cout.md) | 従来の出力。`<<` でつなぐ |
| `printf` | C 由来。型の安全がない |

## コンパイラ対応

C++23 の機能です。GCC 14 / Clang 18 / MSVC 19.37（VS 2022 17.7）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 表示は `std::println("...{}", x);`
    - [x] 書式は `std::format` と同じ
    - [x] C++23（`<print>`）

## 関連ページ

- [cpprefjp: std::println](https://cpprefjp.github.io/reference/print/println.html)
- [cppreference: std::println](https://en.cppreference.com/w/cpp/io/println)

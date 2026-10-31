---
title: std::isalpha
summary: "英字（A-Z, a-z）かを調べる。"
order: 1
group: <cctype> の文字判定
tags:
  - 数値
---

# std::isalpha

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cctype>`
</div>

文字列を解析していると、「この文字は何の仲間か」を調べたくなります。数字の連なりを読み取る、識別子に使える文字か確かめる、空白を飛ばす。`std::isalpha` は、<strong>文字が英字か</strong>を調べます。

!!! tip "ポイント"
    - 調べる対象は、アルファベット（A〜Z、a〜z）
    - 戻り値は `int`。条件を満たせば 0 以外、満たさなければ 0（`bool` ではない）
    - 引数は `unsigned char` の範囲の値にして渡す。`char` のまま渡すと、負の値で未定義動作になることがある
    - 全角文字や日本語は判定できない。ASCII の範囲だけが対象

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isalpha {#isalpha}

```cpp
int isalpha(int c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `int` | 調べる文字。`unsigned char` の範囲の値か `EOF` |

戻り値は、`c` がアルファベット（A〜Z、a〜z）に当てはまれば 0 以外の値、当てはまらなければ 0 です。真偽値として使えますが、型は `int` なので、`== true` と比べてはいけません。`!= 0` か、条件式にそのまま書きます。

引数が `int` なのは、`EOF`（-1）を受け取れるようにするためです。`EOF` 以外の値は、`unsigned char` で表せる範囲（0〜255）でなければなりません。`char` が符号つきの環境で、`char` の値をそのまま渡すと、UTF-8 の日本語のように 128 以上のバイトが負の値になり、未定義動作です。Visual Studio のデバッグ ビルドでは、アサートで止まります。呼ぶときは、必ず `static_cast<unsigned char>(ch)` を挟みます。

判定の基準はロケールで変わります。既定の "C" ロケールでは ASCII の範囲だけが対象で、日本語の文字はどれも「満たさない」になります。UTF-8 の文字を判定したい場合は、別の方法（Unicode のライブラリ）が必要です。

## 実際に動かしてみる

```cpp
#include <cctype>
#include <print>

int main() {
  for (char ch : {'A', 'z', '5', '_', ' '}) {
    // char を unsigned char にしてから渡す
    std::println("'{}' -> {}", ch, std::isalpha(static_cast<unsigned char>(ch)) != 0);
  }
}
```

```text title="実行結果"
'A' -> true
'z' -> true
'5' -> false
'_' -> false
' ' -> false
```

## ゲームでの使いどころ

識別子を読み取るトークナイザーで、先頭の文字が英字かを調べます。

```cpp
bool IsIdentStart(unsigned char c) { return std::isalpha(c) || c == '_'; }   // 識別子の先頭は英字か _
```

## よくあるミス

??? failure "`char` をそのまま渡して、日本語の文字列でクラッシュする"
    `static_cast<unsigned char>(ch)` を挟みます。ラムダの引数を `unsigned char` にしても同じです。

??? failure "é や ü などのアクセント付きの文字を、英字と思う"
    既定の "C" ロケールでは偽です。ロケールを変えると結果が変わるので、環境に依存しない判定が要るなら、自前の表を用意します。

??? failure "戻り値を `true` と比べて、一致しない"
    戻り値は 0 以外が真です。`!= 0` か、条件式でそのまま使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iswalpha`](../cwctype/iswalpha.md) | `wchar_t` 版 |
| [`isalnum`](isalnum.md) | 英字か数字か |
| [`islower`](islower.md) | 小文字か |
| [`isupper`](isupper.md) | 大文字か |
| [`std::all_of`](../../algorithms/all_of.md) | 文字列全体で条件を調べる |

## コンパイラ対応

C++98 から使えます。`<cctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `isalpha` は文字が英字か
    - [x] 戻り値は `int`（0 以外が真）
    - [x] `char` は `unsigned char` にキャストして渡す
    - [x] ASCII のみ。日本語は判定できない

## 関連ページ

- [cpprefjp: std::isalpha](https://cpprefjp.github.io/reference/cctype/isalpha.html)
- [cppreference: std::isalpha](https://en.cppreference.com/w/cpp/string/byte/isalpha)

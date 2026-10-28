---
title: std::toupper
summary: "英字を大文字にする。"
order: 4
group: <cctype> の文字判定
tags:
  - 数値
---

# std::toupper

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cctype>`
</div>

プレイヤーが入力したコマンドを大文字小文字を区別せずに比べたい。ファイル名の拡張子を `.PNG` でも `.png` でも同じに扱いたい。そのとき、先に両方を同じ側の文字にそろえてから比べます。

`std::toupper` は、<strong>小文字を大文字に変換</strong>します。それ以外の文字はそのまま返します。

!!! tip "ポイント"
    - `std::toupper('a')` は 'A'
    - 変換できない文字（数字や記号）はそのまま返す
    - 戻り値は `int`。`char` に戻すには `static_cast<char>` が要る
    - 引数は `unsigned char` の範囲の値にして渡す。ASCII だけが対象

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::toupper {#toupper}

```cpp
int toupper(int c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `int` | 変換する文字。`unsigned char` の範囲の値か `EOF` |

戻り値は、`c` が小文字なら対応する大文字、それ以外なら `c` そのままです。結果は `int` なので、`char` の変数に入れるときは `static_cast<char>` で戻します。

文字列全体を変換するときは、`std::transform` に渡します。このとき、ラムダの引数は `unsigned char` にします。`char` のままだと、128 以上のバイト（日本語の UTF-8 など）で負の値になり、未定義動作になるからです。

変換できるのは、ASCII の英字だけです。日本語のひらがな・カタカナや、ドイツ語の ß のような、ASCII の外の文字は、既定のロケールでは変化しません。大文字と小文字を区別しない比較は、両方を同じ側に変換してから比べる方法が基本です。

## 実際に動かしてみる

```cpp
#include <cctype>
#include <print>

int main() {
  for (char ch : {'a', 'Z', '5'}) {
    const char converted = static_cast<char>(std::toupper(static_cast<unsigned char>(ch)));
    std::println("'{}' -> '{}'", ch, converted);
  }
}
```

```text title="実行結果"
'a' -> 'A'
'Z' -> 'Z'
'5' -> '5'
```

## ゲームでの使いどころ

コマンドや拡張子を大文字小文字を区別せずに比べるときに使います。

```cpp
#include <algorithm>
#include <string>

// 文字列全体を大文字にそろえる
std::string ToUpper(std::string s) {
  std::ranges::transform(s, s.begin(), [](unsigned char c) { return static_cast<char>(std::toupper(c)); });
  return s;
}
```

ラムダの引数を `unsigned char` にしているのが要点です。`char` のままにすると、日本語を含む文字列で未定義動作になります。

## よくあるミス

??? failure "`char` をそのまま渡して、日本語の文字列でクラッシュする"
    ラムダの引数を `unsigned char` にするか、キャストを挟みます。

??? failure "戻り値を `char` に戻さず、数値が表示される"
    `static_cast<char>` で戻します。

??? failure "全角の英字を変換しようとする"
    ASCII の範囲だけが対象です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tolower`](tolower.md) | 逆の変換 |
| [`isupper`](isupper.md) | 大文字か |
| [`islower`](islower.md) | 小文字か |

## コンパイラ対応

C++98 から使えます。`<cctype>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `toupper` は小文字を大文字に変換する
    - [x] 他の文字はそのまま返る。戻り値は `int`
    - [x] `unsigned char` にして渡す。ASCII のみ

## 関連ページ

- [cpprefjp: std::toupper](https://cpprefjp.github.io/reference/cctype/toupper.html)
- [cppreference: std::toupper](https://en.cppreference.com/w/cpp/string/byte/toupper)

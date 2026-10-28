---
title: std::endl
summary: "改行を出して、バッファを書き出す（flush する）。"
order: 74
tags:
  - 入出力・文字列
---

# std::endl

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ostream>`
</div>

画面に 1 行出して、改行したい。`'\n'` でも改行できますが、`std::endl` は、改行を出したうえで、<strong>バッファーを書き出す</strong>ところまで行います。便利に見えますが、使いすぎると出力が遅くなることでも有名な操作子です。

!!! tip "ポイント"
    - `std::endl` は、`'\n'` を出して `flush` する
    - 毎回 `flush` するので、大量の出力では `'\n'` より、はるかに遅くなる
    - クラッシュの直前のログを確実に残したいときには役立つ
    - 普段の改行は `'\n'` で十分。必要なときだけ `flush` を足す

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::endl {#endl}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& endl(std::basic_ostream<CharT, Traits>& os);
```

`os.put(os.widen('\n'))` を呼んだあと、`os.flush()` を呼びます。2 つの動作が 1 つにまとまっているのがこの操作子で、ここが誤解のもとです。

`flush` は、バッファーに溜まった出力を、OS に渡す処理です。ファイルやコンソールへの書き込みは、まとめて行うほうが効率が良いので、ストリームは溜めてから書き出します。`endl` を毎回使うと、その溜める利点が失われ、1 行ごとに書き込み処理が走ります。10 万行を出力するようなループでは、`'\n'` との差が、数倍から数十倍になることがあります。

書き出しが必要なのは、クラッシュしても最後のログを残したい場合や、対話型の入出力で、プロンプトを出してから入力を待つ場合です。その場面では、`std::flush` を明示するほうが、意図が伝わります。

C++23 の `std::println` は、改行だけを出します。`flush` が必要なときは、別に `std::fflush` などを呼びます。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <sstream>

int main() {
  std::ostringstream out;
  out << "line1" << std::endl;      // 改行 + flush
  out << "line2" << '\n';           // 改行だけ
  std::cout << out.str();
}
```

```text title="実行結果"
line1
line2
```

## ゲームでの使いどころ

クラッシュ ログのように、書いた直後に確実に残したい出力に使います。通常のログや、大量の出力では、`'\n'` を使います。ゲームのデバッグ ログで、毎フレーム `endl` を出すと、フレームレートが落ちる原因になることがあります。

## よくあるミス

??? failure "大量の出力で `endl` を使って、遅くなる"
    `'\n'` に置き換えます。

??? failure "`endl` を改行の標準だと思って、いつも使う"
    改行と書き出しは別の操作です。必要なときだけ `flush` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`flush`](flush.md) | 書き出しだけ（改行なし） |
| [`ends`](ends.md) | `'\0'` を出す |
| `'\n'` | 改行だけ。通常はこれ |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 改行して、書き出す
    - [x] 毎回使うと遅い
    - [x] 普段は `'\n'`

## 関連ページ

- [cpprefjp: std::endl](https://cpprefjp.github.io/reference/ostream/endl.html)
- [cppreference: std::endl](https://en.cppreference.com/w/cpp/io/manip/endl)

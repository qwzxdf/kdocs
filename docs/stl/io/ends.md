---
title: std::ends
summary: "文字列の終端（`'\\0'`）を出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::ends

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <sstream>`
</div>

`ostringstream` に書いた内容を、C の文字列のように `'\0'` で終わらせたいときに、`ends` を書き込みます。ふつうは `str()` で足ります。

!!! tip "ポイント"
    - `'\0'` を 1 文字書き込む。
    - `ostringstream` の `str()` には終端が含まれることになる。
    - ふつうは不要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::ends {#ends}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& ends(std::basic_ostream<CharT, Traits>& os);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `os` | ostream& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <sstream>

int main() {
  std::ostringstream os;
  os << "ab" << std::ends;
  std::println("{}", os.str().size());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`str()` の長さがずれる"
    終端も含まれるので、長さが 1 増えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`endl`](endl.md) | 改行してフラッシュ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列の終端（`'\0'`）を出力する
    - [x] `'\0'` を 1 文字書き込む
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ends](https://cpprefjp.github.io/reference/ios/ends.html)
- [cppreference: std::ends](https://en.cppreference.com/w/cpp/io/manip/ends)

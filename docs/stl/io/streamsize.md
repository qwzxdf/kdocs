---
title: std::streamsize
summary: "ストリームで読み書きする文字数を表す符号付き整数型。"
order: 900
tags:
  - 入出力・文字列
---

# std::streamsize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`read(buf, n)` の `n` や `gcount()` の戻り値のように、「何文字読み書きするか」を表す型です。符号付きなので、`-1` のような値も表せます。

!!! tip "ポイント"
    - 入出力の位置・大きさを表す型。
    - `<ios>` で定義される。
    - ふつうは `auto` で受ける。

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::streamsize {#streamsize}

```cpp
using streamsize = /* 実装定義の整数型 */;
```

- 戻り値: なし（型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <fstream>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("abc");
  in.get();
  std::streamsize n = in.gcount();
  std::println("{}", static_cast<long long>(n));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルの途中に戻る | `auto pos = in.tellg(); ... in.seekg(pos);` |

## よくあるミス

??? failure "`int` で受ける"
    大きなファイルで桁あふれします。`auto` か、この型で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ios_base`](ios_base.md) | ストリームの土台 |
| [`ifstream`](ifstream.md) | ファイル入力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームで読み書きする文字数を表す符号付き整数型
    - [x] tellg / seekg で使う
    - [x] auto で受けるのが安全

## 関連ページ

- [cpprefjp: std::streamsize](https://cpprefjp.github.io/reference/ios/streamsize.html)
- [cppreference: std::streamsize](https://en.cppreference.com/w/cpp/io/streamsize)

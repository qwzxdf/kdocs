---
title: std::fpos
summary: "ストリームの位置を状態つきで表すクラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::fpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

マルチバイト文字のように、位置に状態が必要なストリームのための位置の型です。`tellg()` の戻り値（`streampos`）がこれです。整数のように `streamoff` を足し引きできますが、`tellg()` で得た値以外の演算は移植性がありません。

!!! tip "ポイント"
    - 入出力の位置・大きさを表す型。
    - `<ios>` で定義される。
    - ふつうは `auto` で受ける。

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::fpos {#fpos}

```cpp
template <class StateT>
class fpos;
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
  std::streampos pos = in.tellg();
  std::println("{}", static_cast<long long>(pos));
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
    - [x] ストリームの位置を状態つきで表すクラス
    - [x] tellg / seekg で使う
    - [x] auto で受けるのが安全

## 関連ページ

- [cpprefjp: std::fpos](https://cpprefjp.github.io/reference/ios/fpos.html)
- [cppreference: std::fpos](https://en.cppreference.com/w/cpp/io/fpos)

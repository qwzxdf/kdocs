---
title: std::out_of_range
summary: "範囲外の添字・キーにアクセスしたときの例外。"
order: 3
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::out_of_range

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <stdexcept>`
</div>

`vector` の添え字に範囲外の値を渡すと、`v[i]` は何も検査せず、メモリのどこかを読んでしまいます。バグの原因は後から別の場所で壊れた形で現れ、探すのが大変です。`v.at(i)` は添え字を検査して、範囲外なら `std::out_of_range` の例外を投げます。`std::out_of_range` は、範囲外の添え字やキーにアクセスしたときの例外です。

!!! tip "ポイント"
    - `at()` は範囲を検査して `out_of_range` を投げる。`[]` は検査しない。
    - `logic_error` の派生クラス。

!!! info "このページを読む前に"
    [例外の基本](../exceptions.md)（`try` と `catch`）を先に読んでください。

## 関数の詳しい説明

### std::out_of_range {#out_of_range}

```cpp
class out_of_range : public logic_error;
```

- 範囲外を表します。`vector::at`、`string::at`、`string::substr`、`map::at`、`stoi`（int に入らない）が投げます

## しくみ

`out_of_range` は `std::logic_error` の派生クラスで、「プログラムを正しく書いていれば起きないはずのエラー」を表します。呼び出す側のミスで起きるものなので、実行時に起きうる失敗（ファイルが無いなど）を表す `runtime_error` とは区別されます。

`vector::at()`、`string::at()`、`map::at()`、`bitset::test()` などが投げます。`bitset::operator[]` や `vector::operator[]` は投げません。検査のコストを避けるためです。

メッセージは `what()` で取り出せますが、文言は実装によって違います。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  try {
    v.at(10);   // at は範囲を検査する
  } catch (const std::out_of_range&) {
    std::println("範囲外");
  }
}
```

```text title="実行結果"
範囲外
```

## ゲームでの使いどころ

開発中のデバッグ用に検査付きの `at()` を使う場面があります。範囲外のアクセスをしたときに、すぐ例外で止まるので、原因の場所が分かります。ただし、毎フレーム回るループでは、検査のコストが積み重なるので、リリースビルドでは `[]` を使うことが多いです。

設定ファイルの値を `map::at` で引くと、キーが無いときに `out_of_range` が出ます。設定ファイルは外部の入力なので、`try` と `catch` で受けて、初期値で補う形が使われます。

自分で例外を投げるときにも使えます。`if (index >= size) throw std::out_of_range("index");` と書くと、標準の例外と同じ形で伝えられます。

## よくあるミス

??? failure "`[]` が例外を投げると思う"
    `vector::operator[]` は範囲を検査しません。範囲外では未定義動作で、例外は投げられません。検査したいなら `at()` を使います。

??? failure "例外を `catch` しないで落ちる"
    `at()` の例外を捕まえていないと、プログラムが異常終了します。外部の入力に由来する添え字は、`try` で守るか、事前に範囲を確かめます。

??? failure "例外を握りつぶす"
    `catch (...) {}` で何もせず無視すると、バグが見えなくなります。ログを出すか、再度投げます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::runtime_error`](runtime_error.md) | 実行時に起きうる失敗。プログラムのミスではないもの |
| [`std::invalid_argument`](invalid_argument.md) | 引数の値が不正なとき |
| [`std::logic_error`](logic_error.md) | `out_of_range` の親。プログラムのミスを表す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `at()` は範囲を検査して `out_of_range` を投げる。`[]` は投げない。
    - [x] `logic_error` の派生クラス。
    - [x] 外部の入力に由来する添え字は、`try` で守る。

## 関連ページ

- [cpprefjp: std::out_of_range](https://cpprefjp.github.io/reference/stdexcept/out_of_range.html)
- [cppreference: std::out_of_range](https://en.cppreference.com/w/cpp/error/out_of_range)

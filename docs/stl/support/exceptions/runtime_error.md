---
title: std::runtime_error
summary: "実行してみないと分からないエラー（ファイルが無い、通信失敗など）を表す例外。"
order: 2
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::runtime_error

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <stdexcept>`
</div>

ファイルが開けない、データが壊れている、通信に失敗した。プログラムを正しく書いていても起きるエラーを、呼び出し元へ伝えるには、例外が便利です。`std::runtime_error` は、実行時に起こりうるエラーを表す例外で、メッセージの文字列を渡して投げます。自作の例外クラスの基底としてもよく使われます。

!!! tip "ポイント"
    - `throw std::runtime_error("ファイルが開けない: " + path);`
    - 派生クラスに `overflow_error`、`range_error`、`system_error` など。
    - プログラマーのミス（引数が不正など）は `logic_error`。

!!! info "このページを読む前に"
    [例外の基本](../exceptions.md)（`try`、`catch`、`throw`）を先に読んでください。

## 関数の詳しい説明

### std::runtime_error {#runtime_error}

```cpp
class runtime_error : public exception {
 public:
  explicit runtime_error(const std::string& what_arg);
};
```

- 実行してみないと分からない失敗（ファイルが壊れていた、など）。自分で投げるときに一番よく使います

```cpp
#include <print>
#include <stdexcept>
#include <string>

int LoadLevel(const std::string& name) {
  if (name.empty()) {
    throw std::runtime_error("ステージ名が空です");
  }
  return 1;
}

int main() {
  try {
    LoadLevel("");
  } catch (const std::exception& e) {
    std::println("失敗: {}", e.what());
  }
}
```

```text title="実行結果"
失敗: ステージ名が空です
```

## しくみ

`runtime_error` は `std::exception` の派生クラスで、コンストラクターに文字列を渡します。`catch (const std::exception& e)` で受けると、`e.what()` でそのメッセージが取れます。

`logic_error`（プログラムのミス）と対になる分類です。`runtime_error` は、環境や入力が原因で、プログラムの正しさとは関係なく起きるエラーに使います。派生に `range_error`、`overflow_error`、`underflow_error`、`system_error` があります。

自作の例外は、`runtime_error` を継承して作ると、`std::exception` で受けるコードがそのまま動きます。`struct LoadError : std::runtime_error { using std::runtime_error::runtime_error; };` と 1 行で書けます。

## ゲームでの使いどころ

ファイルの読み込みやセーブデータの解析で、失敗を投げる用途が代表的です。`throw std::runtime_error("セーブデータが壊れている: " + path);` と書き、ゲームの上位の層で `catch` して、エラー画面を出します。

ゲームでは、例外を使わない設定でビルドすることも多いです。そのときは、`std::expected` や戻り値でエラーを返す設計にします。

ツールやエディターの側では、例外のほうが書きやすく、広く使われます。ファイルが無い、形式が違うといったエラーは、`runtime_error` を継承した自作の例外で区別します。

## よくあるミス

??? failure "値渡しで `catch` して、派生クラスの情報が切れる"
    `catch (std::exception e)` と値で受けると、派生クラスの部分が切り取られます。`catch (const std::exception& e)` と、参照で受けます。

??? failure "メッセージに `std::string` を渡して、`what()` のポインターが無効になる"
    `what()` が返す `const char*` は、例外オブジェクトが生きている間だけ有効です。`catch` の外へ持ち出さず、中で使い切ります。

??? failure "プログラムのミスを `runtime_error` で表す"
    引数が範囲外といったミスは、`logic_error` や `out_of_range` を使います。分類を分けておくと、`catch` で扱い方を変えられます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::logic_error`](logic_error.md) | プログラムのミスを表す |
| [`std::system_error`](system_error.md) | OS のエラーコードを持つ |
| [`std::out_of_range`](out_of_range.md) | 範囲外のアクセス。`logic_error` の派生 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行時に起こりうるエラーは `runtime_error` で投げる。
    - [x] `catch` は `const std::exception&` で受ける。
    - [x] 自作の例外は `runtime_error` を継承すると扱いやすい。

## 関連ページ

- [cpprefjp: std::runtime_error](https://cpprefjp.github.io/reference/stdexcept/runtime_error.html)
- [cppreference: std::runtime_error](https://en.cppreference.com/w/cpp/error/runtime_error)

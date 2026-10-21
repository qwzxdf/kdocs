---
title: std::exception
summary: "すべての標準例外の基底クラス。what() でメッセージを取れる。"
order: 1
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::exception

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <exception>`
</div>

`std::exception` は、**標準ライブラリの例外すべての親クラス**です。`catch (const std::exception& e)` で、標準の例外をまとめて受け取り、`e.what()` でメッセージを読めます。自作の例外も、これを継承して作るのが普通です。

!!! tip "ポイント"
    - `catch (const std::exception& e)` と**参照で**受ける（スライシングを避ける）。
    - `what()` は C 文字列を返す（文字コードは環境しだい）。
    - 自作の例外は `std::runtime_error` などを継承すると楽。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::exception {#exception}

```cpp
class exception {
 public:
  virtual const char* what() const noexcept;
};
```

- すべての標準例外の親。`what()` で説明の文字列が取れます

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::runtime_error("ファイルが無い");
  } catch (const std::exception& e) {   // 参照で受ける
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
ファイルが無い
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 最上位でまとめて受けてログに出す | `catch (const std::exception& e) { log(e.what()); }` |

## よくあるミス

??? failure "値で受ける"
    スライシングで派生クラスの情報が失われます。参照で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`runtime_error`](runtime_error.md) | 実行時のエラー |
| [`logic_error`](logic_error.md) | プログラムの間違い |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準例外の基底クラス
    - [x] 参照で受ける
    - [x] `what()` でメッセージ

## 関連ページ

- [cpprefjp: std::exception](https://cpprefjp.github.io/reference/stdexcept/exception.html)
- [cppreference: std::exception](https://en.cppreference.com/w/cpp/error/exception)

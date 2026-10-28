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

例外を投げるとき、どんな型の値でも投げられます（`throw 42;`）。でも、`int` を投げると、何が起きたか、受け取る側には分かりません。標準ライブラリの例外は、すべて `std::exception` から派生していて、<strong>`catch (const std::exception&)` で、まとめて受け取れ、`what()` で説明文を取り出せます</strong>。

!!! tip "ポイント"
    - 標準ライブラリの例外の基底クラス
    - `what()` で説明文（`const char*`）を返す
    - `catch (const std::exception&)` で、標準の例外をまとめて捕まえられる
    - 自作の例外も、これを継承する

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exception {#exception}

```cpp
class exception {
 public:
  exception() noexcept;
  virtual ~exception();
  virtual const char* what() const noexcept;
};
```

`what()` は仮想関数で、派生クラスが説明文を返すように上書きします。標準の派生クラス（`std::runtime_error` など）は、コンストラクターに渡された文字列を返します。

`catch (const std::exception& e)` は、標準の例外と、それを継承した自作の例外をすべて受け取ります。ただし、継承していない型（`throw 42;`）は受け取れません。最後の砦として `catch (...)` を置くことがあります。

必ず `const` 参照で捕まえます。値で捕まえると、派生クラスの部分が切り取られます（スライシング）。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::runtime_error("読み込み失敗");
  } catch (const std::exception& e) {          // 派生クラスもまとめて受け取れる
    std::println("エラー: {}", e.what());
  }
}
```

```text title="実行結果"
エラー: 読み込み失敗
```

## ゲームでの使いどころ

プログラムの最上位で、予期しない例外を受け取って、ログに残します。

```cpp
int main() {
  try {
    RunGame();
  } catch (const std::exception& e) {
    LogError(e.what());
    return EXIT_FAILURE;
  }
}
```

## よくあるミス

??? failure "値で捕まえて、派生クラスの情報が切り取られる"
    `const` 参照で捕まえます。

??? failure "`what()` の内容が環境で同じだと思う"
    標準ライブラリが投げる例外の説明文は、実装で違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`runtime_error`](runtime_error.md) | 実行時の誤り |
| [`logic_error`](logic_error.md) | プログラムの誤り |
| [`bad_alloc`](bad_alloc.md) | メモリ確保の失敗 |

## コンパイラ対応

C++98 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::exception` は標準の例外の基底クラス
    - [x] `what()` で説明文を取る
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::exception](https://cpprefjp.github.io/reference/stdexcept/exception.html)
- [cppreference: std::exception](https://en.cppreference.com/w/cpp/error/exception)

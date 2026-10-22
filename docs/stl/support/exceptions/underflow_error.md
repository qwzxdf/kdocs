---
title: std::underflow_error
summary: "計算の結果が小さすぎて表せないことを表す例外。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::underflow_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <stdexcept>`
</div>

浮動小数点で、0 に近すぎて表せない結果（アンダーフロー）になったことを表します。標準のライブラリが自動で投げることは少なく、自分のコードで使います。

!!! tip "ポイント"
    - `runtime_error` から派生。
    - `throw` するときに説明の文字列を渡す。
    - `what()` で説明を取り出す。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::underflow_error {#underflow_error}

```cpp
class underflow_error : public runtime_error {
 public:
  explicit underflow_error(const std::string& what_arg);
  explicit underflow_error(const char* what_arg);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `what_arg` | 文字列 | エラーの説明（`what()` で取り出せる） |

- 戻り値: `what()` が説明を返す
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::underflow_error("bad input");
  } catch (const std::runtime_error& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
bad input
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の関数で、引数や結果の異常を知らせる |

## よくあるミス

??? failure "ゲームの通常のフローに使う"
    例外は遅いので、頻繁に起きるエラーには使いません。戻り値や `expected` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`runtime_error`](runtime_error.md) | 親のクラス |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計算の結果が小さすぎて表せないことを表す例外
    - [x] `runtime_error` から派生
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::underflow_error](https://cpprefjp.github.io/reference/exception/underflow_error.html)
- [cppreference: std::underflow_error](https://en.cppreference.com/w/cpp/error/underflow_error)

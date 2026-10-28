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

実行してみないと分からない計算の失敗は、`std::runtime_error` の仲間の例外で表します。`std::underflow_error` は、<strong>計算が下限を下回ったことを表す例外</strong>です。

!!! tip "ポイント"
    - `throw std::underflow_error("メッセージ")` で投げる
    - `what()` でメッセージを取り出せる
    - `std::runtime_error` と `std::exception` の派生クラス
    - `catch (const std::underflow_error&)` で、この種類だけを捕まえられる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

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
| `what_arg` | 文字列 | `what()` で返すメッセージ |

数値計算のライブラリが結果が小さすぎて表せないと判断したとき。標準ライブラリ自身が投げることはほとんどありません に投げます。呼び出し側は、`catch (const std::underflow_error&)` で、この種類だけを捕まえられます。

`std::runtime_error` の仲間は、プログラムの誤りというより、実行時の状況（データの値、環境）によって起こる失敗を表します。`std::logic_error` の仲間との違いです。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::underflow_error("結果が小さすぎる");
  } catch (const std::underflow_error& e) {
    std::println("エラー: {}", e.what());
  }
}
```

```text title="実行結果"
エラー: 結果が小さすぎる
```

## ゲームでの使いどころ

数値を扱う自作のライブラリで、計算の失敗を知らせます。

```cpp
int Checked(long long v) {
  if (v > INT_MAX) throw std::overflow_error("int に収まらない");
  return static_cast<int>(v);
}
```

## よくあるミス

??? failure "値で捕まえて、派生クラスの情報が切り取られる"
    `const` 参照で捕まえます。

??? failure "エラーを握りつぶす"
    何もしない `catch (...)` は避けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`runtime_error`](runtime_error.md) | 基底クラス |
| [`logic_error`](logic_error.md) | プログラムの誤り |
| [`exception`](exception.md) | すべての標準例外の基底 |

## コンパイラ対応

C++98 から使えます。`<stdexcept>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::underflow_error` は計算が下限を下回ったことを表す例外
    - [x] `std::runtime_error` の派生
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::underflow_error](https://cpprefjp.github.io/reference/exception/underflow_error.html)
- [cppreference: std::underflow_error](https://en.cppreference.com/w/cpp/error/underflow_error)

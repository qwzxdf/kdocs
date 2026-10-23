---
title: std::overflow_error
summary: "計算結果が大きすぎて、表せないことを表す例外。"
order: 14
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::overflow_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <stdexcept>`
</div>

実行してみないと分からない計算の失敗は、`std::runtime_error` の仲間の例外で表します。`std::overflow_error` は、<strong>計算が上限を超えたことを表す例外</strong>です。

!!! tip "ポイント"
    - `throw std::overflow_error("メッセージ")` で投げる
    - `what()` でメッセージを取り出せる
    - `std::runtime_error` と `std::exception` の派生クラス
    - `catch (const std::overflow_error&)` で、この種類だけを捕まえられる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::overflow_error {#overflow_error}

```cpp
class overflow_error : public runtime_error {
 public:
  explicit overflow_error(const std::string& what_arg);
  explicit overflow_error(const char* what_arg);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `what_arg` | 文字列 | `what()` で返すメッセージ |

`std::bitset::to_ulong` で、値が `unsigned long` に収まらないとき に投げます。呼び出し側は、`catch (const std::overflow_error&)` で、この種類だけを捕まえられます。

`std::runtime_error` の仲間は、プログラムの誤りというより、実行時の状況（データの値、環境）によって起こる失敗を表します。`std::logic_error` の仲間との違いです。

## 実際に動かしてみる

```cpp
#include <bitset>
#include <print>
#include <stdexcept>

int main() {
  std::bitset<70> bits;
  bits.set();                           // 70 ビット全部を 1 にする
  try {
    bits.to_ullong();                   // 64 ビットに収まらない
  } catch (const std::overflow_error&) {
    std::println("overflow_error を捕まえた");
  }
}
```

```text title="実行結果"
overflow_error を捕まえた
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
    - [x] `std::overflow_error` は計算が上限を超えたことを表す例外
    - [x] `std::runtime_error` の派生
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::overflow_error](https://cpprefjp.github.io/reference/stdexcept/overflow_error.html)
- [cppreference: std::overflow_error](https://en.cppreference.com/w/cpp/error/overflow_error)

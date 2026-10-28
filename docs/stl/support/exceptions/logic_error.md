---
title: std::logic_error
summary: "プログラムの論理の間違い（呼び出し側のミス）を表す例外。"
order: 5
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::logic_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <stdexcept>`
</div>

呼び出す前に検査すれば防げたはずの、プログラムの誤りを表す例外が `std::logic_error` です。`std::invalid_argument`、`std::domain_error`、`std::length_error`、`std::out_of_range` の基底クラスです。

!!! tip "ポイント"
    - プログラムの論理的な誤りを表す例外の基底クラス
    - `std::exception` の派生で、`what()` を持つ
    - 派生: `invalid_argument`、`domain_error`、`length_error`、`out_of_range`
    - 直接投げるより、派生クラスを投げる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logic_error {#logic_error}

```cpp
class logic_error : public std::exception {
 public:
  explicit logic_error(const std::string& what_arg);
  explicit logic_error(const char* what_arg);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `what_arg` | 文字列 | `what()` で返すメッセージ |

`logic_error` の仲間は、呼び出し側が事前に条件を確かめれば、起こらずに済む失敗を表します。ファイルがない、ネットワークが切れた、といった外部要因の失敗は、`std::runtime_error` の仲間で表します。

この区別は設計の指針です。ただし、実際の使い分けは、あいまいなことも多く、`std::runtime_error` を投げるプロジェクトも多いです。チームで方針を決めておきます。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::logic_error("あり得ない状態");
  } catch (const std::logic_error& e) {
    std::println("エラー: {}", e.what());
  }
}
```

```text title="実行結果"
エラー: あり得ない状態
```

## ゲームでの使いどころ

不変条件が破れたことを表すために使います。

```cpp
if (hp > max_hp) throw std::logic_error("hp が最大値を超えている");
```

## よくあるミス

??? failure "外部要因の失敗に使う"
    `std::runtime_error` の仲間を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`runtime_error`](runtime_error.md) | 実行時の誤り |
| [`invalid_argument`](invalid_argument.md) | 引数が不正 |
| [`exception`](exception.md) | 基底クラス |

## コンパイラ対応

C++98 から使えます。`<stdexcept>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `logic_error` はプログラムの誤りを表す
    - [x] 派生クラスを投げるのが普通
    - [x] 外部要因は `runtime_error`

## 関連ページ

- [cpprefjp: std::logic_error](https://cpprefjp.github.io/reference/stdexcept/logic_error.html)
- [cppreference: std::logic_error](https://en.cppreference.com/w/cpp/error/logic_error)

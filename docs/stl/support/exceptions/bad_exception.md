---
title: std::bad_exception
summary: "予期しない例外を表す例外クラス。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_exception

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <exception>`
</div>

かつての「動的例外仕様」に反する例外が出たときに、投げられていた型です。例外仕様は C++17 で削除されたので、いまは使われません。名前だけが残っている、歴史的な型です。

!!! tip "ポイント"
    - `std::exception` から派生。
    - C++17 で削除された例外仕様（`throw(...)`）に関係していた。
    - いまは使わない。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_exception {#bad_exception}

```cpp
class bad_exception : public exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: `what()` はエラーを表す文字列
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>

int main() {
  try {
    throw std::bad_exception();
  } catch (const std::exception& e) {
    std::println("caught");
  }
}
```

```text title="実行結果"
caught
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （現在はほぼ使われない） |

## よくあるミス

??? failure "新しいコードで期待する"
    動的例外仕様は削除されたので、標準が自動でこれを投げることはありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception`](exception.md) | 親のクラス |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 予期しない例外を表す例外クラス
    - [x] `std::exception` から派生
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::bad_exception](https://cpprefjp.github.io/reference/exception/bad_exception.html)
- [cppreference: std::bad_exception](https://en.cppreference.com/w/cpp/error/bad_exception)

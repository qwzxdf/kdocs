---
title: std::length_error
summary: "許される最大の長さを超えたときの例外。"
order: 13
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::length_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <stdexcept>`
</div>

関数に不正な値を渡されたとき、呼び出し側に何が悪かったかを伝える方法が必要です。`std::length_error` は、<strong>長さの制限を超えることを表す例外</strong>です。`std::logic_error` から派生した例外クラスの 1 つで、エラーの種類を型で区別できます。

!!! tip "ポイント"
    - `throw std::length_error("メッセージ")` で投げる
    - `what()` でメッセージを取り出せる
    - `std::logic_error` と `std::exception` の派生クラス
    - `catch (const std::length_error&)` で、この種類だけを捕まえられる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::length_error {#length_error}

```cpp
class length_error : public logic_error {
 public:
  explicit length_error(const std::string& what_arg);
  explicit length_error(const char* what_arg);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `what_arg` | 文字列 | `what()` で返すメッセージ |

`max_size()` を超えるサイズを要求されたとき に投げます。呼び出し側は、`catch (const std::length_error&)` で、この種類のエラーだけを捕まえて、対処できます。

`what()` が返すメッセージは、コンストラクターに渡した文字列です。標準ライブラリの関数が投げる場合のメッセージは、実装で違います。

`std::length_error` は `std::logic_error` の仲間で、プログラムの誤りとして、呼び出し前の検査で防げるはずのエラーを表します。実行時の環境（ファイルがない、ネットワーク切断）による失敗は、`std::runtime_error` 系で表します。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>
#include <vector>

int main() {
  std::vector<int> v;
  try {
    v.reserve(v.max_size() + 1);        // 許される最大の長さを超える
  } catch (const std::length_error&) {
    std::println("length_error を捕まえた");
  }
}
```

```text title="実行結果"
length_error を捕まえた
```

## ゲームでの使いどころ

自作の関数で、引数の検査に使います。

```cpp
void Spawn(int count) {
  if (count < 0) throw std::length_error("count は 0 以上");
  // …
}
```

ゲームでは、例外を使わない設計（戻り値でエラーを返す）も多いです。例外を使うのは、ファイルの読み込みなど、まれな失敗に限るのが一般的です。

## よくあるミス

??? failure "値で捕まえて、派生クラスの情報が切り取られる"
    `catch (const std::length_error&)` のように、`const` 参照で捕まえます。

??? failure "エラーを握りつぶす"
    `catch (...) {}` で何もしないと、原因が分からなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logic_error`](logic_error.md) | 基底クラス |
| [`runtime_error`](runtime_error.md) | 実行時の誤り |
| [`exception`](exception.md) | すべての標準例外の基底 |

## コンパイラ対応

C++98 から使えます。`<stdexcept>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::length_error` は長さの制限を超えることを表す例外
    - [x] `std::logic_error` の派生で、`what()` でメッセージを取れる
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::length_error](https://cpprefjp.github.io/reference/stdexcept/length_error.html)
- [cppreference: std::length_error](https://en.cppreference.com/w/cpp/error/length_error)

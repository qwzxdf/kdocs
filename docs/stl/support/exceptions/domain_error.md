---
title: std::domain_error
summary: "関数の定義域の外の引数を表す例外。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::domain_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <stdexcept>`
</div>

関数に不正な値を渡されたとき、呼び出し側に何が悪かったかを伝える方法が必要です。`std::domain_error` は、<strong>引数が関数の定義域の外であることを表す例外</strong>です。`std::logic_error` から派生した例外クラスの 1 つで、エラーの種類を型で区別できます。

!!! tip "ポイント"
    - `throw std::domain_error("メッセージ")` で投げる
    - `what()` でメッセージを取り出せる
    - `std::logic_error` と `std::exception` の派生クラス
    - `catch (const std::domain_error&)` で、この種類だけを捕まえられる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::domain_error {#domain_error}

```cpp
class domain_error : public logic_error {
 public:
  explicit domain_error(const std::string& what_arg);
  explicit domain_error(const char* what_arg);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `what_arg` | 文字列 | `what()` で返すメッセージ |

負の数の平方根など、数学的に意味のない入力を渡されたとき に投げます。呼び出し側は、`catch (const std::domain_error&)` で、この種類のエラーだけを捕まえて、対処できます。

`what()` が返すメッセージは、コンストラクターに渡した文字列です。標準ライブラリの関数が投げる場合のメッセージは、実装で違います。

`std::domain_error` は `std::logic_error` の仲間で、プログラムの誤りとして、呼び出し前の検査で防げるはずのエラーを表します。実行時の環境（ファイルがない、ネットワーク切断）による失敗は、`std::runtime_error` 系で表します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>
#include <stdexcept>

double SafeSqrt(double x) {
  if (x < 0) throw std::domain_error("負の数に平方根はない");
  return std::sqrt(x);
}

int main() {
  try {
    SafeSqrt(-1.0);
  } catch (const std::domain_error& e) {
    std::println("エラー: {}", e.what());
  }
}
```

```text title="実行結果"
エラー: 負の数に平方根はない
```

## ゲームでの使いどころ

自作の関数で、引数の検査に使います。

```cpp
void Spawn(int count) {
  if (count < 0) throw std::domain_error("count は 0 以上");
  // …
}
```

ゲームでは、例外を使わない設計（戻り値でエラーを返す）も多いです。例外を使うのは、ファイルの読み込みなど、まれな失敗に限るのが一般的です。

## よくあるミス

??? failure "値で捕まえて、派生クラスの情報が切り取られる"
    `catch (const std::domain_error&)` のように、`const` 参照で捕まえます。

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
    - [x] `std::domain_error` は引数が関数の定義域の外であることを表す例外
    - [x] `std::logic_error` の派生で、`what()` でメッセージを取れる
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::domain_error](https://cpprefjp.github.io/reference/exception/domain_error.html)
- [cppreference: std::domain_error](https://en.cppreference.com/w/cpp/error/domain_error)

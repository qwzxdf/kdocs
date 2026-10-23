---
title: std::invalid_argument
summary: "引数の値が不正なときの例外。"
order: 4
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::invalid_argument

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <stdexcept>`
</div>

関数に不正な値を渡されたとき、呼び出し側に何が悪かったかを伝える方法が必要です。`std::invalid_argument` は、<strong>引数が不正であることを表す例外</strong>です。`std::logic_error` から派生した例外クラスの 1 つで、エラーの種類を型で区別できます。

!!! tip "ポイント"
    - `throw std::invalid_argument("メッセージ")` で投げる
    - `what()` でメッセージを取り出せる
    - `std::logic_error` と `std::exception` の派生クラス
    - `catch (const std::invalid_argument&)` で、この種類だけを捕まえられる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::invalid_argument {#invalid_argument}

```cpp
class invalid_argument : public logic_error {
 public:
  explicit invalid_argument(const std::string& what_arg);
  explicit invalid_argument(const char* what_arg);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `what_arg` | 文字列 | `what()` で返すメッセージ |

範囲外の音量や、空の名前など、関数に渡された値が受け付けられないとき に投げます。呼び出し側は、`catch (const std::invalid_argument&)` で、この種類のエラーだけを捕まえて、対処できます。

`what()` が返すメッセージは、コンストラクターに渡した文字列です。標準ライブラリの関数が投げる場合のメッセージは、実装で違います。

`std::invalid_argument` は `std::logic_error` の仲間で、プログラムの誤りとして、呼び出し前の検査で防げるはずのエラーを表します。実行時の環境（ファイルがない、ネットワーク切断）による失敗は、`std::runtime_error` 系で表します。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>

void SetVolume(int v) {
  if (v < 0 || v > 100) throw std::invalid_argument("volume は 0〜100");
}

int main() {
  try {
    SetVolume(150);
  } catch (const std::invalid_argument& e) {
    std::println("エラー: {}", e.what());
  }
}
```

```text title="実行結果"
エラー: volume は 0〜100
```

## ゲームでの使いどころ

自作の関数で、引数の検査に使います。

```cpp
void Spawn(int count) {
  if (count < 0) throw std::invalid_argument("count は 0 以上");
  // …
}
```

ゲームでは、例外を使わない設計（戻り値でエラーを返す）も多いです。例外を使うのは、ファイルの読み込みなど、まれな失敗に限るのが一般的です。

## よくあるミス

??? failure "値で捕まえて、派生クラスの情報が切り取られる"
    `catch (const std::invalid_argument&)` のように、`const` 参照で捕まえます。

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
    - [x] `std::invalid_argument` は引数が不正であることを表す例外
    - [x] `std::logic_error` の派生で、`what()` でメッセージを取れる
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::invalid_argument](https://cpprefjp.github.io/reference/stdexcept/invalid_argument.html)
- [cppreference: std::invalid_argument](https://en.cppreference.com/w/cpp/error/invalid_argument)

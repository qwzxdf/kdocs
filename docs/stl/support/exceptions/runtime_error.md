---
title: std::runtime_error
summary: "実行してみないと分からないエラー（ファイルが無い、通信失敗など）を表す例外。"
order: 2
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::runtime_error

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <stdexcept>`
</div>

`std::runtime_error` は、**実行時に起こりうるエラー**（ファイルが開けない、データが壊れている、通信に失敗した）を表す例外です。メッセージの文字列を渡して投げます。自作の例外の基底にもよく使われます。

!!! tip "ポイント"
    - `throw std::runtime_error("ファイルが開けない: " + path);`
    - 派生クラスに `overflow_error`、`range_error`、`system_error` など。
    - プログラマーのミス（引数が不正など）は `logic_error`。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::runtime_error {#runtime_error}

```cpp
class runtime_error : public exception {
 public:
  explicit runtime_error(const std::string& what_arg);
};
```

- 実行してみないと分からない失敗（ファイルが壊れていた、など）。自分で投げるときに一番よく使います

```cpp
#include <print>
#include <stdexcept>
#include <string>

int LoadLevel(const std::string& name) {
  if (name.empty()) {
    throw std::runtime_error("ステージ名が空です");
  }
  return 1;
}

int main() {
  try {
    LoadLevel("");
  } catch (const std::exception& e) {
    std::println("失敗: {}", e.what());
  }
}
```

```text title="実行結果"
失敗: ステージ名が空です
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アセットの読み込み失敗を伝える | `throw std::runtime_error("load failed");` |

## よくあるミス

??? failure "例外を使わない方針のコードで投げる"
    ゲームでは例外を切ることがあります。その場合は `std::expected` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logic_error`](logic_error.md) | プログラムの論理の間違い |
| [`std::expected`](../../utilities/expected.md) | 例外を使わない方法 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行時のエラー
    - [x] メッセージを渡して投げる
    - [x] プログラマーのミスは logic_error

## 関連ページ

- [cpprefjp: std::runtime_error](https://cpprefjp.github.io/reference/stdexcept/runtime_error.html)
- [cppreference: std::runtime_error](https://en.cppreference.com/w/cpp/error/runtime_error)

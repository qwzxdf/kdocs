---
title: std::bad_expected_access
summary: "エラーを持つ expected から value() で値を取り出したときの例外。"
order: 72
tags:
  - ユーティリティ
---

# std::bad_expected_access

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <expected>`
</div>

`std::bad_expected_access<E>` は、**エラーを持つ `std::expected` に対して `value()` を呼んだ**ときに投げられる例外です。`error()` でエラーの値を取り出せます。例外を使わない方針なら、`has_value()` で確かめてから `*e` で取り出します。

!!! tip "ポイント"
    - `e.error()` が、`expected` に入っていたエラーの値。
    - `value()` は例外を投げる。`*e`（`operator*`）は未定義動作。
    - `value_or(既定値)` なら安全。

## 関数の詳しい説明

### std::bad_expected_access {#bad_expected_access}

```cpp
template <class E>
class bad_expected_access : public bad_expected_access<void> {
 public:
  E& error() noexcept;
};
```

- 戻り値: （例外クラス）
- 計算量: O(1)

```cpp
#include <expected>
#include <print>

int main() {
  std::expected<int, int> e = std::unexpected(5);
  try {
    e.value();
  } catch (const std::bad_expected_access<int>& ex) {
    std::println("エラーコード {}", ex.error());
  }
}
```

```text title="実行結果"
エラーコード 5
```

### error {#error}

```cpp
E& error() & noexcept;
const E& error() const& noexcept;
```

- 計算量: 定数

`expected` が持っていたエラーの値への参照。`value()` が失敗したときに、原因を取り出せます。

### what {#what}

```cpp
const char* what() const noexcept override;
```

- 計算量: 定数

エラーを表す文字列（実装定義）。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 失敗を例外にして、上位でまとめて処理する | `e.value()` を使う |

## よくあるミス

??? failure "空の expected を * で読む"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::expected`](expected.md) | 本体 |
| [`unexpected`](unexpected.md) | エラーを入れる包み |

## コンパイラ対応

C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エラーを持つ expected の value() が投げる
    - [x] `error()` で値を取る
    - [x] 安全なのは value_or

## 関連ページ

- [cpprefjp: std::bad_expected_access](https://cpprefjp.github.io/reference/expected/bad_expected_access.html)
- [cppreference: std::bad_expected_access](https://en.cppreference.com/w/cpp/utility/expected/bad_expected_access)

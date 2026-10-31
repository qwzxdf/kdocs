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

`std::expected<T, E>` に値がない（エラーが入っている）のに、`value()` で値を取り出そうとすると、例外が投げられます。その例外が `std::bad_expected_access<E>` で、入っているエラーの値を、`error()` で取り出せます。

!!! tip "ポイント"
    - `expected::value()` が、エラーの状態のときに投げる
    - `error()` で、入っていたエラーの値を取れる
    - 例外を使わずに済ませるなら、`has_value()` で調べるか、`value_or()` を使う
    - C++23

!!! info "このページを読む前に"
    [`std::expected`](expected.md) と [`std::unexpect`](unexpect.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_expected_access {#bad_expected_access}

<span class="ver ver-23">C++23</span>

```cpp
template <class E>
class bad_expected_access : public bad_expected_access<void> {
 public:
  E& error() & noexcept;
  const E& error() const& noexcept;
  E&& error() && noexcept;
};
```

`bad_expected_access<void>` が共通の基底クラスで、`E` を知らなくても、`catch (const std::bad_expected_access<void>&)` で、すべての `E` の例外を捕まえられます。`what()` のメッセージは、実装ごとに違います。

`E` を指定して `catch` すれば、`error()` で原因が取れます。

```cpp
try {
  auto v = result.value();
} catch (const std::bad_expected_access<std::string>& ex) {
  std::println("失敗: {}", ex.error());
}
```

`expected` の設計思想は、例外を使わずに、戻り値でエラーを扱うことです。`value()` は、「エラーはないはずだ」という前提で呼ぶ関数で、違ったときに、例外にして知らせます。エラーがありうる場面では、`has_value()` か `if (result)` で調べてから、`*result` で取り出します。

## 実際に動かしてみる

```cpp
#include <expected>
#include <print>
#include <string>

std::expected<int, std::string> Parse(bool ok) {
  if (ok) return 42;
  return std::unexpected("parse error");
}

int main() {
  // エラーの状態で value() を呼ぶと例外
  try {
    const int v = Parse(false).value();
    std::println("{}", v);
  } catch (const std::bad_expected_access<std::string>& ex) {
    std::println("失敗: {}", ex.error());
  }

  // 基底クラスで捕まえることもできる
  try {
    Parse(false).value();
  } catch (const std::bad_expected_access<void>&) {
    std::println("エラーの型を問わず捕まえた");
  }

  // 例外を使わない取り出し
  const auto r = Parse(false);
  std::println("既定値: {}", r.value_or(-1));
}
```

```text title="実行結果"
失敗: parse error
エラーの型を問わず捕まえた
既定値: -1
```

## ゲームでの使いどころ

アセットの読み込みが失敗したとき、`value()` で例外にして、ゲーム全体のエラー画面に飛ばす、といった処理で使います。

## よくあるミス

??? failure "エラーがありうる場面で value() を使う"
    例外が飛んで、処理が止まります。`has_value()` で調べるか、`value_or` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::expected`](expected.md) | 本体 |
| [`std::unexpected`](unexpected.md) | エラーの値を包む型 |
| `std::bad_optional_access` | `optional` の同様の例外 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::bad_expected_access](https://cpprefjp.github.io/reference/expected/bad_expected_access.html)
- [cppreference: std::bad_expected_access](https://en.cppreference.com/w/cpp/utility/expected/bad_expected_access)

---
title: std::bad_optional_access
summary: "空の optional から `value()` で取り出したときの例外。"
order: 10
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_optional_access

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <optional>`
</div>

`std::bad_optional_access` は、**中身が空の `std::optional` に対して `value()` を呼んだ**ときに投げられる例外です。`*opt`（`operator*`）は例外を投げず、空だと未定義動作なので、値があると確かめてから使うか、`value_or` を使うのが安全です。

!!! tip "ポイント"
    - `value()` は空だと例外、`*opt` は未定義動作、`value_or(既定値)` は安全。
    - ゲームで例外を切っているなら、`has_value()` で先に確認する。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_optional_access {#bad_optional_access}

```cpp
class bad_optional_access : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <optional>
#include <print>

int main() {
  std::optional<int> hp;
  try {
    hp.value();
  } catch (const std::bad_optional_access&) {
    std::println("値が入っていない");
  }
}
```

```text title="実行結果"
値が入っていない
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 検索結果が見つからなかったことを検出する | `value_or(0)` か `has_value()` |

## よくあるミス

??? failure "例外を投げると思って *opt する"
    `*opt` は空だと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::optional`](../../utilities/optional.md) | 本体 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の optional の value() が投げる
    - [x] `*opt` は投げない（未定義）
    - [x] value_or が安全

## 関連ページ

- [cpprefjp: std::bad_optional_access](https://cpprefjp.github.io/reference/optional/bad_optional_access.html)
- [cppreference: std::bad_optional_access](https://en.cppreference.com/w/cpp/utility/bad_optional_access)

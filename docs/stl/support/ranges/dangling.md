---
title: std::ranges::dangling
summary: "「一時オブジェクトのイテレータは危険」と知らせるための印の型。"
order: 4
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::dangling

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::dangling` は、**ranges のアルゴリズムが、一時オブジェクトのイテレータを返せないときに、代わりに返す空の型**です。`std::ranges::find(GetVector(), 3)` は、一時的な `vector` を指すイテレータを返すとぶら下がるので、`dangling` を返し、使おうとするとコンパイルエラーになります。

!!! tip "ポイント"
    - コンパイルエラーの原因として出会うことが多い。
    - 左辺値（変数）に対して呼べば、普通のイテレータが返る。
    - `std::ranges::borrowed_range` は、一時オブジェクトでも安全な範囲（`span`、`string_view`）。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::ranges::dangling {#dangling}

```cpp
struct dangling {
  constexpr dangling() = default;
  template <class... Args> constexpr dangling(Args&&...) noexcept {}
};
```

- 戻り値: 空の型
- 計算量: O(1)

```cpp
#include <algorithm>
#include <print>
#include <ranges>
#include <vector>

int main() {
  auto it = std::ranges::find(std::vector{1, 2, 3}, 2);  // 一時的な vector
  std::println("{}", std::is_same_v<decltype(it), std::ranges::dangling>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| エラーメッセージに dangling が出たとき | 変数に入れた範囲を渡し直す |

## よくあるミス

??? failure "dangling のエラーを無理に消す"
    一時オブジェクトを変数に入れてからアルゴリズムに渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find`](../../algorithms/find.md) | dangling を返しうる |
| [`std::span`](../../containers/span.md) | 借りた範囲として安全 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一時オブジェクトのイテレータは使えない印
    - [x] 変数に入れ直す
    - [x] span / string_view は安全

## 関連ページ

- [cpprefjp: std::ranges::dangling](https://cpprefjp.github.io/reference/ranges/dangling.html)
- [cppreference: std::ranges::dangling](https://en.cppreference.com/w/cpp/ranges/dangling)

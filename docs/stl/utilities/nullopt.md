---
title: std::nullopt
summary: "optional を「空」にするための印。"
order: 71
tags:
  - ユーティリティ
---

# std::nullopt

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <optional>`
</div>

「見つからなかった」ことを関数の戻り値で伝えたい。`std::optional` を返す関数で、値がない状態を表すには、何かの印が必要です。`std::nullopt` は、`std::optional` を「値がない（空）」状態にするための印です。`return std::nullopt;` と書けば、「ない」を返せます。

!!! tip "ポイント"
    - `return std::nullopt;` で「無し」を返す。
    - `o = std::nullopt;` や `o.reset()` で、中身を捨てて空にする。
    - `o == std::nullopt` で空か調べられる（`has_value()` でも同じ）。

!!! info "このページを読む前に"
    [`std::optional`](optional.md) を先に読んでください。`nullopt` は、その空の状態を表す印です。

## 関数の詳しい説明

### std::nullopt {#nullopt}

```cpp
inline constexpr std::nullopt_t nullopt{};
```

- 戻り値: （タグ）
- 計算量: O(1)

```cpp
#include <optional>
#include <print>

std::optional<int> Find(bool found) {
  if (!found) {
    return std::nullopt;  // 見つからなかった
  }
  return 42;
}

int main() {
  std::println("{} {}", Find(false).has_value(), Find(true).value());
}
```

```text title="実行結果"
false 42
```

## ゲームでの使いどころ

検索関数の戻り値で、「見つからなかった」を返すときに使います。`std::optional<Enemy*> FindNearest(Vec2 pos)` が、敵がいなければ `return std::nullopt;` と書きます。

`optional` を空に戻すには、`o = std::nullopt;` か `o.reset()` です。選択中のユニットを解除する、といった処理に使います。

空かどうかは、`o == std::nullopt` でも調べられますが、`has_value()` や `if (o)` のほうが読みやすくなります。

## よくあるミス

??? failure "nullptr と混同する"
    `optional` の空は `nullopt` です。`nullptr` ではありません。

??? failure "`nullptr` と取り違える"
    `optional` に `nullptr` を入れると、`nullptr` という値が入った状態になります。空にするのは `nullopt` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::optional`](optional.md) | 本体 |
| [`in_place`](in_place.md) | その場で構築する |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] optional を空にする印
    - [x] `return std::nullopt;`
    - [x] `reset()` でも空にできる

## 関連ページ

- [cpprefjp: std::nullopt](https://cpprefjp.github.io/reference/optional/nullopt.html)
- [cppreference: std::nullopt](https://en.cppreference.com/w/cpp/utility/optional/nullopt)

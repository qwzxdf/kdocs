---
title: std::unreachable
summary: "「ここには絶対に来ない」とコンパイラに伝える。"
order: 7
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::unreachable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <utility>`
</div>

`std::unreachable()` は、**「この行には、絶対に到達しない」とコンパイラに伝える**関数です。最適化のヒントになります。**もし実際に到達すると未定義動作**なので、本当に来ないと確信できる場所だけに書きます。`switch` の `default:` で、列挙値をすべて処理したあとなどに使います。

!!! tip "ポイント"
    - 到達すると**未定義動作**。デバッグ時は `assert` を併用する。
    - MSVC の `__assume(0)`、GCC の `__builtin_unreachable()` と同じ。
    - C++23 の機能。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::unreachable {#unreachable}

<span class="ver ver-23">C++23</span>

```cpp
[[noreturn]] void unreachable();
```

- 「ここには絶対に来ない」とコンパイラに伝えます。最適化に使われますが、**本当に来てしまうと未定義動作**です。switch で全部の enum を扱ったあとの最後などに使います

```cpp
#include <print>
#include <utility>

enum class Shape { kCircle, kSquare };

const char* Name(Shape s) {
  switch (s) {
    case Shape::kCircle:
      return "円";
    case Shape::kSquare:
      return "四角";
  }
  std::unreachable();  // 全部の case を書いたので、ここには来ない
}

int main() { std::println("{}", Name(Shape::kSquare)); }
```

```text title="実行結果"
四角
```

!!! warning
    デバッグ中は `assert(false)` のほうが、来てしまったときに気づけて安全です。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| enum のすべてを処理した switch のあと | `std::unreachable();` |

## よくあるミス

??? failure "実は到達する"
    未定義動作でクラッシュするか、おかしな動きをします。デバッグビルドでは `assert(false)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| `assert(false)` | デバッグで検出する |
| `[[noreturn]]` | 戻らない関数に付ける |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 到達しない箇所を伝える
    - [x] 到達したら未定義動作
    - [x] デバッグでは assert

## 関連ページ

- [cpprefjp: std::unreachable](https://cpprefjp.github.io/reference/utility/unreachable.html)
- [cppreference: std::unreachable](https://en.cppreference.com/w/cpp/utility/unreachable)

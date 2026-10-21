---
title: std::monostate
summary: "何も入っていない状態を表す、空の型。variant の先頭に置く。"
order: 58
tags:
  - ユーティリティ
---

# std::monostate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::monostate` は、**何の情報も持たない空の型**です。`std::variant` の先頭に入れておくと、「まだ何も入っていない」状態を表せます。`variant` は、最初の型が既定で構築できないと作れないので、そのときの逃げ道にもなります。

!!! tip "ポイント"
    - `std::variant<std::monostate, A, B>` と書くと、「空 / A / B」の 3 状態。
    - `monostate` どうしは、すべて等しい。
    - 既定コンストラクタを持たない型のための、ダミー。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::monostate {#monostate}

```cpp
struct monostate {};
```

- 候補の最初に置くと「まだ何も入っていない」状態を表せます。最初の型にデフォルトコンストラクタが無いときにも使います

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<std::monostate, int> v;
  std::println("空？ {}", std::holds_alternative<std::monostate>(v));
}
```

```text title="実行結果"
空？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「未設定」を含む状態を表す variant | `std::variant<std::monostate, Idle, Moving>` |

## よくあるミス

??? failure "monostate を忘れて、既定構築できない"
    最初の型が既定構築できない `variant` は、既定で作れません。先頭に `std::monostate` を足します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::optional`](optional.md) | 「ある / ない」の 2 状態なら、こちら |
| [`std::variant`](variant.md) | 本体 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の型。variant の先頭に置く
    - [x] 「未設定」を表せる
    - [x] 既定構築できない型のための逃げ道

## 関連ページ

- [cpprefjp: std::monostate](https://cpprefjp.github.io/reference/variant/monostate.html)
- [cppreference: std::monostate](https://en.cppreference.com/w/cpp/utility/variant/monostate)

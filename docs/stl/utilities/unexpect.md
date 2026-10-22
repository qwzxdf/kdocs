---
title: std::unexpect
summary: "expected に、エラー側をその場で作らせる目印。"
order: 900
tags:
  - ユーティリティ
---

# std::unexpect

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <expected>`
</div>

`std::expected<int, std::string>` に、成功ではなく失敗を作りたいとき、コンストラクタ引数だけでは成功側と区別できません。先頭に `std::unexpect` を置くと、「次の引数でエラー側を作る」と指定できます。

!!! tip "ポイント"
    - `std::unexpect_t` 型の定数。
    - `expected(std::unexpect, エラーの引数...)` の形で使う。
    - エラーの値を作ってから包む [`std::unexpected`](unexpected.md) の別の書き方。

!!! info "このページを読む前に"
    [`std::expected`](expected.md) を先に読んでください。

## 関数の詳しい説明

### std::unexpect {#unexpect}

```cpp
struct unexpect_t { explicit unexpect_t() = default; };
inline constexpr unexpect_t unexpect{};
```

- 戻り値: なし（目印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <expected>
#include <print>
#include <string>

int main() {
  std::expected<int, std::string> e(std::unexpect, "error");
  std::println("{}", e.error());
}
```

```text title="実行結果"
error
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| エラーをその場で作った expected を返す | `return std::expected<int, std::string>(std::unexpect, "failed");` |

## よくあるミス

??? failure "成功側に使う"
    成功側を作る場合は [`in_place`](in_place.md) です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unexpected`](unexpected.md) | エラーを包む型 |
| [`in_place`](in_place.md) | 成功側をその場で作る |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エラー側をその場で作る目印
    - [x] expected の第 1 引数に置く
    - [x] unexpected の別の書き方

## 関連ページ

- [cpprefjp: std::unexpect](https://cpprefjp.github.io/reference/expected/unexpect.html)
- [cppreference: std::unexpect](https://en.cppreference.com/w/cpp/utility/expected/unexpect)

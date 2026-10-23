---
title: std::error_condition
summary: "環境に依存しない「エラーの種類」を表す。error_code と比べる相手。"
order: 31
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::error_condition

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`std::error_condition` は、**環境に依存しない「エラーの種類」**を表すクラスです。`error_code` は OS ごとに値が違いますが、`error_condition` は共通の名前（`errc`）で表します。`ec == condition` と書くと、環境の違いを吸収して比べてくれます。

!!! tip "ポイント"
    - `std::errc` から暗黙に作れる。
    - `error_code` と `error_condition` を `==` で比べると、環境の差が吸収される。
    - 自分で作る機会は少ない。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::error_condition {#error_condition}

```cpp
class error_condition {
 public:
  int value() const noexcept;
  const error_category& category() const noexcept;
  explicit operator bool() const noexcept;
};
```

- 戻り値: （クラス）
- 計算量: O(1)

```cpp
#include <print>
#include <system_error>

int main() {
  std::error_condition cond = std::errc::permission_denied;
  std::error_code ec = std::make_error_code(std::errc::permission_denied);
  std::println("{} {}", cond == std::errc::permission_denied, ec == cond);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| OS の違いを意識せずに、エラーの種類で分岐する | `if (ec == std::errc::permission_denied)` |

## よくあるミス

??? failure "error_code の value を直接 switch する"
    OS ごとに値が違います。条件と比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_code`](error_code.md) | 環境に依存する側 |
| [`errc`](errc.md) | 種類の名前 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 環境に依存しない種類
    - [x] error_code と比べる
    - [x] 普段は errc を使う

## 関連ページ

- [cpprefjp: std::error_condition](https://cpprefjp.github.io/reference/system_error/error_condition.html)
- [cppreference: std::error_condition](https://en.cppreference.com/w/cpp/error/error_condition)

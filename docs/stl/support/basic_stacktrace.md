---
title: std::basic_stacktrace
summary: "stacktrace の元になる、アロケータを選べるテンプレート。"
order: 900
tags:
  - 型・言語サポート
---

# std::basic_stacktrace

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <stacktrace>`
</div>

`std::stacktrace` は、`basic_stacktrace<std::allocator<stacktrace_entry>>` の別名です。スタックトレースを保存するときのメモリ確保を自分で管理したい（pmr など）なら、`basic_stacktrace<MyAlloc>` を直接使います。ふつうは別名の `stacktrace` で足ります。

!!! tip "ポイント"
    - `stacktrace` = `basic_stacktrace<std::allocator<stacktrace_entry>>`。
    - アロケータを差し替えられる。
    - ふつうは `stacktrace` を使う。

!!! info "このページを読む前に"
    [`std::stacktrace`](stacktrace.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_stacktrace {#basic_stacktrace}

```cpp
template <class Allocator>
class basic_stacktrace;
using stacktrace = basic_stacktrace<allocator<stacktrace_entry>>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Allocator` | 型 | 要素を保持するアロケータ |

- 戻り値: `stacktrace` と同じ関数をもつ
- 計算量: `stacktrace` と同じ


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <stacktrace>
#include <type_traits>

int main() {
  using Alias = std::basic_stacktrace<std::allocator<std::stacktrace_entry>>;
  std::println("{}", std::is_same_v<Alias, std::stacktrace>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スタックトレースを pmr のメモリに保存する | `std::basic_stacktrace<std::pmr::polymorphic_allocator<std::stacktrace_entry>>` |

## よくあるミス

??? failure "別名と取り違える"
    アロケータを変えない限り、`stacktrace` と書けば十分です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stacktrace`](stacktrace.md) | 別名 |

## コンパイラ対応

C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] stacktrace の元のテンプレート
    - [x] アロケータを選べる
    - [x] ふつうは別名で足りる

## 関連ページ

- [cpprefjp: std::basic_stacktrace](https://cpprefjp.github.io/reference/stacktrace/basic_stacktrace.html)
- [cppreference: std::basic_stacktrace](https://en.cppreference.com/w/cpp/utility/basic_stacktrace)

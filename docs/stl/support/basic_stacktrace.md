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

`std::stacktrace` は、履歴の保存先に、普通の `new` のメモリを使います。例外処理の中や、メモリが逼迫した状況では、確保そのものが失敗するかもしれません。ゲーム機の固定のメモリ プールや、`std::pmr` のリソースから確保させたいときは、アロケーターを差し替える必要があります。それができるクラス テンプレートが `std::basic_stacktrace<Allocator>` で、`std::stacktrace` は、その標準のアロケーター版の別名です。

!!! tip "ポイント"
    - `std::stacktrace` は `basic_stacktrace<std::allocator<stacktrace_entry>>` の別名
    - アロケーターを渡して、履歴の保存先を決められる
    - `std::pmr::stacktrace` は `pmr` のアロケーター版の別名
    - 通常は `std::stacktrace` で足りる

!!! info "このページを読む前に"
    [`std::stacktrace`](stacktrace.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_stacktrace {#basic_stacktrace}

<span class="ver ver-23">C++23</span>

```cpp
template <class Allocator>
class basic_stacktrace;

using stacktrace = basic_stacktrace<std::allocator<stacktrace_entry>>;

namespace pmr {
using stacktrace = basic_stacktrace<std::pmr::polymorphic_allocator<stacktrace_entry>>;
}
```

| 引数 | 意味 |
| --- | --- |
| `Allocator` | 履歴の保存に使うアロケーター。要素の型は `stacktrace_entry` |

メンバーは、[`std::stacktrace`](stacktrace.md) と同じです。`current` や `size`、`operator[]` などが、そのまま使えます。違うのは、`current` の最後の引数にアロケーターを渡せることと、`get_allocator()` で取り出せることです。

#### std::pmr::stacktrace

`std::pmr::stacktrace` は、`polymorphic_allocator` を使う別名です。`std::pmr::monotonic_buffer_resource` のような、事前に確保した領域から配るリソースを渡せます。履歴の保存で、`new` を呼ばせたくない場面に向きます。

#### 取得時の確保

履歴を取得する OS の呼び出し自体が内部でメモリを確保することもあるので、アロケーターの差し替えだけで、完全に確保ゼロにできるとは限りません。確かめるには、実装ごとに計測します。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <stacktrace>
#include <type_traits>

int main() {
  // std::stacktrace は標準アロケーター版の別名
  static_assert(std::is_same_v<std::stacktrace,
                               std::basic_stacktrace<std::allocator<std::stacktrace_entry>>>);

  // 自前のメモリ領域から、履歴の保存先を確保する
  std::byte buffer[4096];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));
  std::pmr::stacktrace trace = std::pmr::stacktrace::current(&pool);

  std::println("履歴は空ではない: {}", !trace.empty());
  std::println("保存先は pool: {}", trace.get_allocator().resource() == &pool);
}
```

```text title="実行結果"
履歴は空ではない: true
保存先は pool: true
```

## ゲームでの使いどころ

メモリを使い切った後のエラー処理や、固定のメモリ プールだけを使うゲーム機向けのコードで、履歴の保存先を指定したいときに使います。

## よくあるミス

??? failure "pmr のリソースを先に壊す"
    履歴は、リソースが消えた後に使えません。履歴より長生きする場所に置きます。

??? failure "異なるアロケーターの履歴どうしを比べる"
    型が違うので、そのままでは比べられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stacktrace`](stacktrace.md) | 標準アロケーター版 |
| [`stacktrace_entry`](stacktrace_entry.md) | 履歴の 1 段 |
| [`polymorphic_allocator`](../memory/pmr/polymorphic_allocator.md) | `pmr` のアロケーター |

## コンパイラ対応

C++23 です。MSVC は Visual Studio 2022 17.4 以降、GCC 12 以降が対応しています。

## 関連ページ

- [cpprefjp: std::basic_stacktrace](https://cpprefjp.github.io/reference/stacktrace/basic_stacktrace.html)
- [cppreference: std::basic_stacktrace](https://en.cppreference.com/w/cpp/utility/basic_stacktrace)

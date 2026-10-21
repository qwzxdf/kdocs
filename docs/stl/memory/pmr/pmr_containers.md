---
title: std::pmr::vector
summary: "メモリの取り先を渡せる、pmr 版のコンテナ（vector・string・map など）。"
order: 9
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::vector

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <memory_resource>`
</div>

`std::pmr::vector` のような **pmr 版のコンテナ**は、普通のコンテナと同じ使い方で、**コンストラクタにメモリリソースを渡せる**ものです。`std::pmr::string`、`std::pmr::map`、`std::pmr::unordered_map` なども同じです。型は変わらないので、関数の引数や戻り値にも使えます。

!!! tip "ポイント"
    - `std::pmr::vector<int> v(&pool);` のようにリソースのアドレスを渡す。
    - 要素が pmr 対応の型（`pmr::string` など）なら、同じリソースが引き継がれる。
    - 渡さなければ、既定のリソース（普通の new / delete）。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### pmr::vector などの pmr コンテナ {#pmr_containers data-toc-label="pmr::vector などのコンテナ"}

```cpp
namespace std::pmr {
template <class T> using vector = std::vector<T, polymorphic_allocator<T>>;
using string = std::basic_string<char, std::char_traits<char>, polymorphic_allocator<char>>;
template <class K, class V> using map = std::map<K, V, std::less<K>, polymorphic_allocator<std::pair<const K, V>>>;
template <class K, class V> using unordered_map = /* 同様 */;
}
```

| 型 | ヘッダ |
| --- | --- |
| `std::pmr::vector<T>` | `<vector>` |
| `std::pmr::string` | `<string>` |
| `std::pmr::list<T>`、`std::pmr::deque<T>` | `<list>`、`<deque>` |
| `std::pmr::map<K, V>`、`std::pmr::set<T>` | `<map>`、`<set>` |
| `std::pmr::unordered_map<K, V>`、`std::pmr::unordered_set<T>` | `<unordered_map>`、`<unordered_set>` |

- 戻り値: なし（型の別名）
- コンストラクタの最後の引数に `std::pmr::memory_resource*` を渡します（`std::pmr::vector<int> v(&pool);`、`v(10, 0, &pool);` など）
- <strong>入れ子にしたとき、中の要素にもリソースが自動で伝わります。</strong> `std::pmr::vector<std::pmr::string>` なら、文字列の確保も同じリソースから行われます（これを *uses-allocator construction* と呼びます）。`std::vector<std::string>` ではこうなりません

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <memory_resource>
#include <print>
#include <string>
#include <vector>

int main() {
  std::byte buffer[512];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));

  std::pmr::vector<std::pmr::string> names(&pool);  // 文字列も同じ pool から確保される
  names.emplace_back("スライム");
  names.emplace_back("ゴブリン");
  std::println("{}", names);
}
```

```text title="実行結果"
["スライム", "ゴブリン"]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フレーム用の一時的な配列 | `std::pmr::vector<Enemy*> hits(&frame_pool);` |

## よくあるミス

??? failure "リソースを先に破棄する"
    コンテナより先にリソースを消すと、ダングリングです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::vector`](../../containers/vector.md) | 普通のコンテナ |
| [`monotonic_buffer_resource`](monotonic_buffer_resource.md) | 組み合わせる |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] pmr 版のコンテナ
    - [x] リソースを渡して使う
    - [x] コンテナより長生きさせる

## 関連ページ

- [cpprefjp: std::pmr::vector](https://cpprefjp.github.io/reference/memory_resource/pmr_containers.html)
- [cppreference: std::pmr::vector](https://en.cppreference.com/w/cpp/memory/pmr_containers)

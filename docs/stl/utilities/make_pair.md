---
title: std::make_pair
summary: "型を推論して pair を作る。"
order: 52
tags:
  - ユーティリティ
---

# std::make_pair

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <utility>`
</div>

2 つの値を `pair` にするとき、`std::pair<int, std::string>(1, "a")` と型を全部書くのは長すぎます。`std::make_pair(1, std::string("a"))` なら、型を推論して `pair` を作ってくれます。C++17 以降は、クラステンプレートの型推論（CTAD）が使えるので、`std::pair(a, b)` や `{a, b}` と書けば足ります。古いコードを読むために知っておく関数です。

!!! tip "ポイント"
    - C++17 以降は `std::pair(a, b)` / `{a, b}` で足りる
    - 引数の型を `decay` して保持する。文字列リテラルは `const char*` になる
    - `std::ref(x)` を渡した所は、参照になる
    - `std::map::insert` の引数に、`make_pair` を使うコードが古い資料に多い

!!! info "このページを読む前に"
    [`std::make_tuple`](make_tuple.md) を先に読んでください。`pair` は 2 要素の `tuple` のようなものです。

## 関数の詳しい説明

### std::make_pair {#make_pair}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class T1, class T2>
constexpr std::pair<std::unwrap_ref_decay_t<T1>, std::unwrap_ref_decay_t<T2>>
make_pair(T1&& t1, T2&& t2);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t1` | 任意 | 1 つ目の値（`first`） |
| `t2` | 任意 | 2 つ目の値（`second`） |

各引数は `decay` された型で保持されます。`make_pair(1, "abc")` は `pair<int, const char*>` です。`std::string` にしたいなら、`std::string("abc")` と書きます。

C++17 の CTAD では、`std::pair p(1, 2.5);` のように、型を書かずに作れます。ただし、CTAD は文字列リテラルを `const char*` とするだけでなく、配列や参照を `decay` する点が `make_pair` と同じです。`pair` の型を明示したい場面では、`std::pair<int, std::string>{1, "abc"}` と書きます。こちらは、`"abc"` から `std::string` への変換が、暗黙に行われます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <map>
#include <print>
#include <string>
#include <utility>

int main() {
  auto p = std::make_pair(1, std::string("Hero"));  // pair<int, string>
  std::println("{} {}", p.first, p.second);

  // 文字列リテラルは const char*
  auto q = std::make_pair(1, "abc");
  static_assert(std::is_same_v<decltype(q), std::pair<int, const char*>>);

  // C++17: CTAD で足りる
  std::pair r(2, 3.5);
  std::println("{} {}", r.first, r.second);

  // map への挿入
  std::map<std::string, int> m;
  m.insert(std::make_pair("hero", 5));
  std::println("{}", m.at("hero"));
}
```

```text title="実行結果"
1 Hero
2 3.5
5
```

## ゲームでの使いどころ

古いコードの読解です。新しく書くなら、`std::pair(a, b)` か、`m.emplace(a, b)` のほうが短く書けます。

## よくあるミス

??? failure "文字列リテラルが std::string になると思う"
    `const char*` です。比較や連結で、意図と違う結果になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_tuple`](make_tuple.md) | 任意の個数の `tuple` |
| [`std::piecewise_construct`](piecewise_construct.md) | 各要素のコンストラクター引数を渡して作る |
| `std::pair` の CTAD | C++17 以降の書き方 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::make_pair](https://cpprefjp.github.io/reference/utility/make_pair.html)
- [cppreference: std::make_pair](https://en.cppreference.com/w/cpp/utility/pair/make_pair)

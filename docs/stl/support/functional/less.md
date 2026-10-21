---
title: std::less
summary: "「小さいか」を比べる関数オブジェクト（`<` の代わり）。"
order: 1
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::less

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <functional>`
</div>

`std::less<T>` は、**`a < b` を関数オブジェクトとして使えるようにしたもの**です。`std::map` や `std::set` の既定の並び順、`sort` の比較関数として使われています。型を省略した `std::less<>` は、型が違う値どうしも比べられます。

!!! tip "ポイント"
    - `std::map<K, V, std::less<>>` のように `<>` を使うと、`string_view` などでの検索が楽になる（透過比較）。
    - 逆順にしたいなら [`std::greater`](greater.md)。
    - 自作の比較は、ラムダ式でも書ける。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::less {#less}

```cpp
template <class T = void>
struct less;  // a < b
```

- `a < b`。sort や map のデフォルトです。`std::less<>`（型なし）にすると、型の違う値（`std::string` と `const char*`）でも比べられます（透過比較）

```cpp
#include <functional>
#include <map>
#include <print>
#include <string>
#include <string_view>

int main() {
  std::map<std::string, int, std::less<>> prices = {{"potion", 50}};
  std::string_view key = "potion";
  std::println("{} {}", prices.find(key)->second, std::greater{}(3, 1));  // string を作らず検索
}
```

```text title="実行結果"
50 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| map・set の並び順を明示する | `std::map<std::string, int, std::less<>>` |

## よくあるミス

??? failure "ポインターの比較に < を使う"
    無関係なポインターを `<` で比べるのは未規定ですが、`std::less` なら全順序が保証されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`greater`](greater.md) | 逆の順序 |
| [`std::ranges::less`](less.md) | ranges 用の比較 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<` を関数オブジェクトにしたもの
    - [x] `std::less<>` は型が違っても比べられる
    - [x] 逆順は greater

## 関連ページ

- [cpprefjp: std::less](https://cpprefjp.github.io/reference/functional/less.html)
- [cppreference: std::less](https://en.cppreference.com/w/cpp/utility/functional/less)

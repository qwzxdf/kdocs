---
title: std::is_pod
summary: "型が POD（トリビアルかつ標準レイアウト）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_pod

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

古い名前です。C++20 で非推奨になりました。`std::is_trivial` と `std::is_standard_layout` の両方を調べるほうが、意図が明確です。

!!! tip "ポイント"
    - `std::is_pod_v<T>` は、`T` が POD 型（トリビアルかつ標準レイアウト）か
    - C++20 で非推奨
    - `std::is_pod<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - C++20 で非推奨
    - `is_trivial` と `is_standard_layout` を並べて書く

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_pod_v {#is_pod}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_pod_v = is_pod<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`is_trivial` と `is_standard_layout` の両方が `true` の型が `true` です。C 言語の構造体と同じ形の型の目印でしたが、C++20 で非推奨になり、コンパイラが警告を出すことがあります。

C++20 で非推奨です。代わりに `std::is_trivial_v<T> && std::is_standard_layout_v<T>` と書きます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                     -> {}", std::is_pod_v<Player>);
  std::println("std::string                -> {}", std::is_pod_v<std::string>);
}
```

```text title="実行結果"
Player                     -> true
std::string                -> false
```

## ゲームでの使いどころ

C 言語の API に渡す構造体が、C と同じ作りかを確かめます。`is_pod` の代わりに、2 つを並べて書きます。

```cpp
struct Header {
  std::uint32_t magic;
  std::uint32_t version;
};

static_assert(std::is_trivial_v<Header> && std::is_standard_layout_v<Header>);
```

## よくあるミス

??? failure "C++20 以降で is_pod を使う"
    非推奨で、警告が出ることがあります。`is_trivial` と `is_standard_layout` を使います。

??? failure "is_pod が true なら、ファイルに書き出してよいと思う"
    パディングやエンディアンの違いは別の問題です。環境をまたぐなら、`std::uint32_t` などの幅が決まった型にして、書き出しを自分で書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_trivial`](is_trivial.md) | 構築・コピー・破棄が自明か |
| [`is_standard_layout`](is_standard_layout.md) | C と同じメモリ配置か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_pod_v<T>` は、`T` が POD 型（トリビアルかつ標準レイアウト）か
    - [x] `is_trivial` かつ `is_standard_layout`
    - [x] C++20 以降は、2 つを並べて使う

## 関連ページ

- [cpprefjp: std::is_pod](https://cpprefjp.github.io/reference/type_traits/is_pod.html)
- [cppreference: std::is_pod](https://en.cppreference.com/w/cpp/types/is_pod)

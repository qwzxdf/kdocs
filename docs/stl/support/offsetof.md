---
title: offsetof
summary: "構造体のメンバが、先頭から何バイト目にあるかを求める。"
order: 24
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# offsetof

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstddef>`
</div>

構造体のメンバーが、先頭から何バイト目にあるかを知りたい場面があります。GPU に渡す頂点データの入力レイアウトで、各メンバーのオフセットを指定するときです。`offsetof(型, メンバー)` は、<strong>メンバーの先頭からのバイト位置</strong>を返します。

!!! tip "ポイント"
    - `offsetof(T, member)` は、`member` の先頭からのバイト数
    - 戻り値は `std::size_t`
    - 標準レイアウト型でのみ有効
    - 頂点レイアウトの定義によく使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### offsetof {#offsetof}

<span class="ver ver-98">C++98</span>

```cpp
#define offsetof(type, member) /* 定数式 */
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `type` | 型 | 構造体の型 |
| `member` | メンバー名 | 位置を知りたいメンバー |

結果はコンパイル時の定数です。構造体のパディング（詰め物）も含めた、実際のメモリ上の位置が得られます。

標準レイアウトでない型（仮想関数を持つクラスなど）に使うと、動作が保証されません（GCC や Clang は警告を出します）。頂点のような単純な構造体で使います。

DirectX の入力レイアウト（`D3D11_INPUT_ELEMENT_DESC`）の `AlignedByteOffset` に、`offsetof` の結果を渡すと、メンバーの順序を変えても、レイアウトの記述がずれません。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>

struct Vertex {
  float position[3];
  float color[4];
};

int main() {
  std::println("position の位置 = {}", offsetof(Vertex, position));
  std::println("color の位置    = {}", offsetof(Vertex, color));
}
```

```text title="実行結果"
position の位置 = 0
color の位置    = 12
```

## ゲームでの使いどころ

頂点データのレイアウトの記述に使います。

```cpp
{"COLOR", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, offsetof(Vertex, color), D3D11_INPUT_PER_VERTEX_DATA, 0}
```

## よくあるミス

??? failure "標準レイアウトでない型に使う"
    単純な構造体にだけ使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_standard_layout`](type_traits/is_standard_layout.md) | 標準レイアウトか |
| [`size_t`](size_t.md) | 戻り値の型 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `offsetof(T, member)` はメンバーの位置（バイト）
    - [x] 標準レイアウト型でのみ有効
    - [x] 頂点レイアウトの記述に使う

## 関連ページ

- [cpprefjp: offsetof](https://cpprefjp.github.io/reference/cstddef/offsetof.html)
- [cppreference: offsetof](https://en.cppreference.com/w/cpp/types/offsetof)

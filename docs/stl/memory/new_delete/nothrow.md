---
title: std::nothrow
summary: "new が失敗したとき、例外ではなく nullptr を返させる指定。"
order: 4
group: new / delete まわり
tags:
  - メモリ
---

# std::nothrow

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

`new` は、失敗すると例外を投げます。例外を使わない設計（ゲーム機の組み込みなど）で、失敗したら `nullptr` を返してほしいとき、`new (std::nothrow) T` と書きます。`std::nothrow` は、そのための印です。

!!! tip "ポイント"
    - `new (std::nothrow) T` は、失敗したら `nullptr` を返す
    - `T` のコンストラクターが投げる例外は、そのまま出る（確保だけが対象）
    - `delete` は普通に使える
    - 配列版も `new (std::nothrow) T[n]`

!!! info "このページを読む前に"
    [`operator new`](operator_new.md) を先に読んでください。

## 関数の詳しい説明

### std::nothrow {#nothrow}

```cpp
struct nothrow_t { explicit nothrow_t() = default; };
inline constexpr std::nothrow_t nothrow{};
```

`nothrow` は、値を持たない空の印で、`operator new` のオーバーロードを選ぶために渡します。

```cpp
int* p = new (std::nothrow) int[1000];
if (p == nullptr) {
  // 確保に失敗した
}
```

`set_new_handler` で登録したハンドラーは、`nothrow` 版でも、確保の失敗のたびに呼ばれます。ハンドラーが例外を投げると、`nothrow` 版はそれを捕まえて、`nullptr` を返します。

例外を使わない設計でも、標準ライブラリのコンテナ（`std::vector` など）は、確保の失敗で `bad_alloc` を投げます。`nothrow` を使えるのは、自分で `new` するところだけです。

## 実際に動かしてみる

```cpp
#include <limits>
#include <new>
#include <print>

int main() {
  // 通常の確保は成功する
  int* ok = new (std::nothrow) int(7);
  std::println("成功: {}", ok != nullptr);
  delete ok;

  // 確保できない大きさは nullptr になる（例外は投げない）
  char* big = new (std::nothrow) char[std::numeric_limits<std::size_t>::max() / 2];
  std::println("失敗: {}", big == nullptr);
  delete[] big;
}
```

```text title="実行結果"
成功: true
失敗: true
```

## ゲームでの使いどころ

例外を無効にしたビルドで、確保の失敗を検査する自作のアロケーターに使います。

## よくあるミス

??? failure "nullptr を確かめない"
    失敗しても例外が出ないので、そのまま使うとクラッシュします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`set_new_handler`](set_new_handler.md) | 失敗時の回復 |
| [`bad_array_new_length`](bad_array_new_length.md) | 配列の長さが不正なときの例外 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::nothrow](https://cpprefjp.github.io/reference/new/new.html)
- [cppreference: std::nothrow](https://en.cppreference.com/w/cpp/memory/new/nothrow)

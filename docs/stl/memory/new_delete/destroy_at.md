---
title: std::destroy_at
summary: "オブジェクトのデストラクターを呼ぶ（メモリは解放しない）。"
order: 7
group: new / delete まわり
tags:
  - メモリ
---

# std::destroy_at

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`std::destroy_at` は、**オブジェクトのデストラクターを呼ぶ**関数です。メモリそのものは解放しません。[`construct_at`](construct_at.md) や配置 new で作ったものを壊すときに使います。

!!! tip "ポイント"
    - `p->~T()` と同じ意味を、型に依存せず書ける。
    - メモリは自分で戻す（プールに返すなど）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::destroy_at <span class="ver ver-17">C++17</span> {#destroy_at data-toc-label="std::destroy_at"}

```cpp
template <class T>
constexpr void destroy_at(T* p);
template <class It>
constexpr void destroy(It first, It last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `T*` | 破棄するオブジェクト |
| `first`, `last` | `It` | 破棄する範囲 |

- 戻り値: なし
- デストラクタを呼びます。メモリは返しません。`p->~T();` の代わりに書けて、`T` が変わっても書き換える場所が減ります
- `std::destroy(first, last)` で、範囲の全部をまとめて破棄できます

## 実際に動かしてみる

```cpp
#include <memory>
#include <new>
#include <print>

struct Noisy {
  ~Noisy() { std::println("破棄"); }
};

int main() {
  alignas(Noisy) unsigned char buffer[sizeof(Noisy)];
  Noisy* p = new (buffer) Noisy();
  std::destroy_at(p);  // デストラクターだけを呼ぶ（メモリは解放しない）
}
```

```text title="実行結果"
破棄
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| メモリプールに返す前にオブジェクトを壊す | `std::destroy_at(p);` |

## よくあるミス

??? failure "delete と混同する"
    `destroy_at` はメモリを解放しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`construct_at`](construct_at.md) | 作る |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] デストラクターだけを呼ぶ
    - [x] メモリは解放しない
    - [x] C++17

## 関連ページ

- [cpprefjp: std::destroy_at](https://cpprefjp.github.io/reference/new/destroy_at.html)
- [cppreference: std::destroy_at](https://en.cppreference.com/w/cpp/memory/new/destroy_at)

---
title: std::uninitialized_copy
summary: "未初期化のメモリへ、要素を（コンストラクターで）コピーして作る。"
order: 9
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_copy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <memory>`
</div>

`std::uninitialized_copy` は、**まだオブジェクトがない（未初期化の）メモリへ、要素をコピーして作る**関数です。普通のコピー（`std::copy`）は代入ですが、こちらはコンストラクターを呼びます。自作のコンテナを作るときの部品です。

!!! tip "ポイント"
    - `std::copy` は「すでにあるオブジェクトへ代入」、こちらは「メモリの上に新しく作る」。
    - 途中で例外が出ると、作った分を壊してくれる。
    - 仲間に `uninitialized_fill`、`uninitialized_move`、`uninitialized_default_construct` など。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::uninitialized_copy など {#uninitialized data-toc-label="uninitialized_copy など"}

```cpp
template <class In, class Out> Out uninitialized_copy(In first, In last, Out dest);
template <class It, class T> void uninitialized_fill(It first, It last, const T& value);
template <class It> void uninitialized_default_construct(It first, It last);
template <class It> void uninitialized_value_construct(It first, It last);
template <class In, class Out> Out uninitialized_move(In first, In last, Out dest);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | `In` | コピー元・埋める範囲 |
| `dest` | `Out` | 作る先（**未初期化の領域**） |
| `value` | `const T&` | 埋める値 |

- 戻り値: `uninitialized_copy` などは、作り終えた最後の次の位置
- 未初期化の領域に、**配置 new でまとめて作る**関数です。`std::copy` は、すでにオブジェクトがある場所への**代入**ですが、こちらは**新しく作ります**。
- 途中で例外が出たら、そこまで作ったものを自動で破棄してくれます（例外安全）。`vector` の再確保が、これを使っています

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <string>

int main() {
  alignas(std::string) unsigned char buffer[sizeof(std::string) * 2];
  auto* dst = reinterpret_cast<std::string*>(buffer);

  std::string src[2] = {"a", "b"};
  std::uninitialized_copy(src, src + 2, dst);  // 未初期化のメモリの上に作ってコピー
  std::println("{} {}", dst[0], dst[1]);
  std::destroy(dst, dst + 2);
}
```

```text title="実行結果"
a b
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作コンテナの再確保時に、要素を新しい領域へ作る | `std::uninitialized_copy(first, last, dest)` |

## よくあるミス

??? failure "すでにオブジェクトがあるメモリに使う"
    二重にコンストラクターが走って、リークや二重破棄になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::copy`](../../algorithms/copy.md) | 代入でコピー |
| [`construct_at`](construct_at.md) | 1 つだけ作る |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 未初期化のメモリに作ってコピー
    - [x] `std::copy` は代入
    - [x] 自作コンテナの部品

## 関連ページ

- [cpprefjp: std::uninitialized_copy](https://cpprefjp.github.io/reference/new/uninitialized_copy.html)
- [cppreference: std::uninitialized_copy](https://en.cppreference.com/w/cpp/memory/new/uninitialized_copy)

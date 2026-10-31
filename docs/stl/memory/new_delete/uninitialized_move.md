---
title: std::uninitialized_move
summary: "未初期化のメモリに、範囲の要素をムーブして作る。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_move

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`std::vector` が容量を増やすとき、古い領域の要素を、新しい生の領域にムーブして作ります。この操作を行うのが `std::uninitialized_move(first, last, d_first)` です。`[first, last)` の要素をムーブして、`d_first` から始まる生のメモリに作ります。

!!! tip "ポイント"
    - 生のメモリにムーブして作る
    - 元の範囲は、ムーブ後の状態（中身が空など）で残る。壊す責任は呼び出し側
    - 途中で例外が出たら、作ったものを壊してから伝える
    - 戻り値は、書き込んだ範囲の次の位置

!!! info "このページを読む前に"
    [`uninitialized_fill`](uninitialized_fill.md) を先に読んでください。

## 関数の詳しい説明

### std::uninitialized_move {#uninitialized_move}

<span class="ver ver-17">C++17</span>

```cpp
template <class InputIt, class NoThrowForwardIt>
NoThrowForwardIt uninitialized_move(InputIt first, InputIt last, NoThrowForwardIt d_first);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | 入力イテレータ | ムーブ元の範囲 |
| `d_first` | 前方イテレータ | ムーブ先の先頭（生のメモリ） |

元の要素は、ムーブされたあとも、有効だけれど値が不定の状態で残ります。元の領域を解放する前に、元の要素を `destroy` で壊します。

ムーブコンストラクターが `noexcept` でない型では、例外を投げた場合に元の要素が壊れてしまうため、`std::move_if_noexcept` を使う設計のコンテナもあります。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <string>

int main() {
  std::string src[2] = {"Hero", "Mage"};

  alignas(std::string) unsigned char buf[sizeof(std::string) * 2];
  auto* dst = reinterpret_cast<std::string*>(buf);

  std::uninitialized_move(src, src + 2, dst);
  std::println("{} {}", dst[0], dst[1]);
  std::println("元の先頭は空: {}", src[0].empty());

  std::destroy(dst, dst + 2);
}
```

```text title="実行結果"
Hero Mage
元の先頭は空: true
```

## ゲームでの使いどころ

自作の動的配列で、容量を増やす処理に使います。

## よくあるミス

??? failure "元の範囲を壊し忘れる"
    ムーブされた要素にも、デストラクターが必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uninitialized_fill`](uninitialized_fill.md) | 同じ値で作る |
| `std::uninitialized_copy` | コピーして作る |
| [`move_if_noexcept`](../../utilities/move_if_noexcept.md) | 例外を考えてムーブかコピーを選ぶ |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::uninitialized_move](https://cpprefjp.github.io/reference/memory/uninitialized_move.html)
- [cppreference: std::uninitialized_move](https://en.cppreference.com/w/cpp/memory/uninitialized_move)

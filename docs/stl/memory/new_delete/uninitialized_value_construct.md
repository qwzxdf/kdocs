---
title: std::uninitialized_value_construct
summary: "未初期化のメモリに、値初期化でオブジェクトを作る。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_value_construct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`uninitialized_default_construct` は、基本型を初期化しません。生のメモリに、`int` を 0 に初期化して作りたいなら、`std::uninitialized_value_construct(first, last)` を使います。値初期化（`T()`）で作ります。

!!! tip "ポイント"
    - 値初期化で作る。基本型は 0、クラスは既定のコンストラクター
    - `vector<T>(n)` が使うのと同じ初期化
    - 時間は `default_construct` より余計にかかる
    - 途中で例外が出たら、作ったものを壊す

!!! info "このページを読む前に"
    [`uninitialized_default_construct`](uninitialized_default_construct.md) を先に読んでください。

## 関数の詳しい説明

### std::uninitialized_value_construct {#uninitialized_value_construct}

<span class="ver ver-17">C++17</span>

```cpp
template <class ForwardIt>
void uninitialized_value_construct(ForwardIt first, ForwardIt last);
```

`::new (p) T()` と同じです。ユーザー定義の既定のコンストラクターを持たないクラスは、まず全メンバーをゼロ初期化してから、暗黙の既定のコンストラクターが呼ばれます。

基本型は 0 になるので、あとで読んでも安全です。時間が要るのは、ゼロクリアの分です。

`_n` 版が、個数を指定する形です。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  // 汚れた領域を用意する
  alignas(int) unsigned char buf[sizeof(int) * 3];
  for (auto& b : buf) b = 0xFF;
  auto* p = reinterpret_cast<int*>(buf);

  std::uninitialized_value_construct(p, p + 3);
  std::println("{} {} {}", p[0], p[1], p[2]);

  std::destroy(p, p + 3);
}
```

```text title="実行結果"
0 0 0
```

## ゲームでの使いどころ

0 で初期化された配列が必要な、自作のコンテナで使います。

## よくあるミス

??? failure "default_construct と取り違える"
    基本型は、`default` では初期化されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uninitialized_default_construct`](uninitialized_default_construct.md) | 初期化しない |
| [`uninitialized_fill`](uninitialized_fill.md) | 同じ値で作る |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::uninitialized_value_construct](https://cpprefjp.github.io/reference/memory/uninitialized_value_construct.html)
- [cppreference: std::uninitialized_value_construct](https://en.cppreference.com/w/cpp/memory/uninitialized_value_construct)

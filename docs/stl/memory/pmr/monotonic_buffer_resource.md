---
title: std::pmr::monotonic_buffer_resource
summary: "積むだけで、個別には解放しないメモリ領域。フレーム用に一括解放する。"
order: 1
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::monotonic_buffer_resource

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <memory_resource>`
</div>

`std::pmr::monotonic_buffer_resource` は、**メモリを前から順に「積んでいく」だけで、個別の解放をしない**メモリリソースです。確保は非常に速く、`release()` で全部を一括解放します。1 フレームだけ使う一時データの置き場として最適です。

!!! tip "ポイント"
    - 配列（`std::byte buffer[N]`）を渡すと、まずそこから確保し、足りなくなったら親のリソースから足す。
    - 個別の `deallocate` は何もしない。メモリは `release()` か破棄まで戻らない。
    - **スレッドセーフではない**。スレッドごとに持つ。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### monotonic_buffer_resource {#monotonic_buffer_resource}

```cpp
class monotonic_buffer_resource : public memory_resource {
 public:
  monotonic_buffer_resource();
  explicit monotonic_buffer_resource(memory_resource* upstream);
  monotonic_buffer_resource(void* buffer, std::size_t size);
  monotonic_buffer_resource(void* buffer, std::size_t size, memory_resource* upstream);
  explicit monotonic_buffer_resource(std::size_t initial_size);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer`, `size` | `void*`, `size_t` | 最初に使う領域（スタックの配列など）。`nullptr` / 0 なら、すぐ上流から取る |
| `upstream` | `std::pmr::memory_resource*` | **領域が足りなくなったとき**に、追加のメモリを取りに行く先。デフォルトは `get_default_resource()`（普通の `new`） |
| `initial_size` | `std::size_t` | 最初に上流から取る大きさ（目安） |

- 戻り値: なし（コンストラクタ）
- 確保は「今の位置から、必要な大きさだけ進める」だけです。**探す処理がないので非常に速く**、メモリの断片化もしません
- <strong>個別の解放（`deallocate`）は何もしません。</strong> `v.pop_back()` や `v.clear()`、再確保で捨てた領域は、**`release()` か、リソースの破棄まで戻ってきません**
- 領域が足りなくなると、上流から**前の約 1.5〜2 倍の大きさ**で追加のブロックを取ります。つまり、バッファが小さくても動きますが、そのぶんヒープを使います
- スレッドセーフではありません（1 つのスレッドから使う）

<div class="anim" data-label="monotonic_buffer_resource（バッファ 8 個ぶん）">
_ _ _ _ _ _ _ _ # 渡した領域。まだ空
+A +A +A _ _ _ _ _ # allocate：先頭から切り出す
+A +A +A +B +B _ _ _ # 続けて切り出す。探さないので速い
x x x x x x _ _ # 個別に deallocate しても、領域は戻らない（残る）
_ _ _ _ _ _ _ _ # release() で一括して空に戻る
</div>

!!! note "vector を増やしていくときの落とし穴"
    `push_back` を繰り返すと、`vector` は**古い領域を捨てて、より大きい領域を確保し直します**。monotonic では古い領域が戻らないので、**最終的な大きさの 2 倍近くを消費**します。使う量が分かるなら **`reserve`** を先に呼びます。

### release {#release}

```cpp
void release();
```

- 戻り値: なし
- 領域をまとめて上流に返し、**最初の状態に戻します**。渡したバッファは、また最初から使えます
- デストラクタも内部で `release()` を呼ぶので、リソースを破棄すれば自動で返されます
- 呼ぶ前に、そのリソースを使っているコンテナをすべて破棄してください

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  std::byte buffer[256];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));

  std::pmr::vector<int> v(&pool);  // pool からメモリを取る
  v.push_back(1);
  v.push_back(2);
  v.push_back(3);
  std::println("{}", v);
  pool.release();  // 一括解放（コンテナを使い終わってから）
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 フレームだけ使う一時配列の置き場 | `std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));` |
| フレームの終わりに一括解放 | `pool.release();` |

## よくあるミス

??? failure "コンテナより先にリソースを破棄する"
    リソースを先に消すと、コンテナが使うメモリが無効になります。リソースは必ずコンテナより長生きさせます。

??? failure "長く使い続けて増え続ける"
    解放されないので、`release()` を呼ばないとメモリが増え続けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unsynchronized_pool_resource`](unsynchronized_pool_resource.md) | 解放した分を再利用する |
| [`new_delete_resource`](new_delete_resource.md) | 普通の new / delete |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 積むだけの速い領域
    - [x] `release()` で一括解放
    - [x] コンテナより長生きさせる

## 関連ページ

- [cpprefjp: std::pmr::monotonic_buffer_resource](https://cpprefjp.github.io/reference/memory_resource/monotonic_buffer_resource.html)
- [cppreference: std::pmr::monotonic_buffer_resource](https://en.cppreference.com/w/cpp/memory/monotonic_buffer_resource)

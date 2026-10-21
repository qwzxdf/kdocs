---
title: std::pmr::synchronized_pool_resource
summary: "大きさごとの置き場を持つ、スレッドセーフなメモリ領域。"
order: 4
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::synchronized_pool_resource

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory_resource>`
</div>

`std::pmr::synchronized_pool_resource` は、[`unsynchronized_pool_resource`](unsynchronized_pool_resource.md) の**スレッドセーフ版**です。複数のスレッドから同時に確保・解放できますが、ロックのぶん少し遅くなります。

!!! tip "ポイント"
    - 複数スレッドから使うときだけ。
    - スレッドごとに `unsynchronized` を持つほうが速い。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### synchronized_pool_resource {#synchronized_pool_resource}

```cpp
class synchronized_pool_resource : public memory_resource;
```

- `unsynchronized_pool_resource` の**スレッドセーフ版**です。複数のスレッドから同じリソースを使うときだけ使います（ロックのぶん遅くなります）
- スレッドごとにリソースを持てるなら、`unsynchronized_pool_resource` を `thread_local` にするほうが速いです

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  std::pmr::synchronized_pool_resource pool;
  std::pmr::vector<int> v(&pool);
  v.assign({1, 2, 3});
  std::println("{}", v.size());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 複数のスレッドが共有するオブジェクトプール | `std::pmr::synchronized_pool_resource pool;` |

## よくあるミス

??? failure "単一スレッドなのにこちらを使う"
    ロックのぶん遅くなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unsynchronized_pool_resource`](unsynchronized_pool_resource.md) | 単一スレッド用 |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スレッドセーフなプール
    - [x] ロックのぶん少し遅い
    - [x] スレッドごとに持てるなら unsynchronized

## 関連ページ

- [cpprefjp: std::pmr::synchronized_pool_resource](https://cpprefjp.github.io/reference/memory_resource/synchronized_pool_resource.html)
- [cppreference: std::pmr::synchronized_pool_resource](https://en.cppreference.com/w/cpp/memory/synchronized_pool_resource)

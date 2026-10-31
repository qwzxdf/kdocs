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

複数のスレッドから、同じプール リソースを使いたい。`std::pmr::unsynchronized_pool_resource` は、ロックを持たず、スレッドから同時に触ると壊れます。`std::pmr::synchronized_pool_resource` は、同じ機能のプールに、スレッド安全を足したものです。

!!! tip "ポイント"
    - 複数のスレッドが、同じリソースから確保・解放できる
    - 内部の排他制御のぶん、`unsynchronized` より遅い
    - スレッドごとに別のプールを持てるなら、`unsynchronized` のほうが速い
    - 個別の解放ができる。解放した領域は再利用される

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::synchronized_pool_resource {#synchronized_pool_resource}

<span class="ver ver-17">C++17</span>

```cpp
class synchronized_pool_resource : public std::pmr::memory_resource {
 public:
  synchronized_pool_resource(const std::pmr::pool_options& opts, std::pmr::memory_resource* upstream);
  synchronized_pool_resource();
  void release();
  std::pmr::memory_resource* upstream_resource() const;
  std::pmr::pool_options options() const;
};
```

大きさごとのプールを持ち、解放された領域を同じ大きさの確保で再利用します。`monotonic_buffer_resource` と違い、個別の解放が意味を持ちます。

スレッドの安全性は、プールの内部にある排他制御で実現されています。実装によっては、スレッドごとのプールを持つ工夫もあります。

`release()` は、確保した領域を、上流にすべて返します。まだ使っているオブジェクトがあるときに呼ぶと、ぶら下がります。

設定は [`pool_options`](pool_options.md) で渡します。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <numeric>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::pmr::synchronized_pool_resource pool;

  // 2 つのスレッドが、同じプールから確保する
  long long sum1 = 0;
  long long sum2 = 0;
  auto work = [&pool](long long& out) {
    std::pmr::vector<int> v(&pool);
    for (int i = 1; i <= 1000; ++i) v.push_back(i);
    out = std::accumulate(v.begin(), v.end(), 0LL);
  };

  std::thread t1(work, std::ref(sum1));
  std::thread t2(work, std::ref(sum2));
  t1.join();
  t2.join();

  std::println("{} {}", sum1, sum2);
}
```

```text title="実行結果"
500500 500500
```

## ゲームでの使いどころ

複数のワーカー スレッドが、共通のプールから小さなオブジェクトを確保するジョブ システムで使います。

## よくあるミス

??? failure "スレッドが 1 つなのに使う"
    ロックのぶん遅くなります。`unsynchronized` で足ります。

??? failure "release の後に、古いオブジェクトを使う"
    ぶら下がります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unsynchronized_pool_resource`](unsynchronized_pool_resource.md) | スレッド セーフでない、速いプール |
| [`pool_options`](pool_options.md) | 設定 |
| [`monotonic_buffer_resource`](monotonic_buffer_resource.md) | 解放しない単純なリソース |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::synchronized_pool_resource](https://cpprefjp.github.io/reference/memory_resource/synchronized_pool_resource.html)
- [cppreference: std::pmr::synchronized_pool_resource](https://en.cppreference.com/w/cpp/memory/synchronized_pool_resource)

---
title: スレッドとアロケータ
tags:
  - 最適化
  - アロケータ
---

# スレッドとアロケータ

アロケータを**複数のスレッド**から使うときは、同時に触って壊れないようにする必要があります。ロックで守ると安全ですが、待ちが発生して遅くなります。速くて安全な方法は、スレッドごとに別のアロケータを持つことです。このページはロックの問題、スレッドごとのアロケータ、スレッドキャッシュ（tcmalloc 風）、ロックフリーのプール、キャッシュの競合（false sharing）をまとめます。

!!! tip "ポイント"
    - <strong>共有のアロケータに、複数スレッドが同時に触ると、ロックが必要</strong>。<strong>ロックは待ちとキャッシュの競合で、遅い</strong>。
    - 一番速い対策はスレッドごとに、別のアロケータ（`thread_local`）。ロックなし。
    - スレッドキャッシュ：スレッドごとの小さなキャッシュ ＋ 共有の中央ヒープ。普段はロックなし、足りなくなったときだけ、中央へ。
    - 別のスレッドが確保したものを返す（クロススレッド解放）は、難しい。返却用のキューを持つ。
    - ロックフリーのプールは、`compare_exchange` で作れるが、ABA 問題に注意。タグ付きで防ぐ。
    - スレッドごとのデータは、キャッシュラインを分ける（false sharing）。

!!! info "このページを読む前に"
    - [optimize/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [メモリ確保](../allocation.md)（メモリ確保が遅い理由）

## 共有のアロケータの問題

<svg class="fig flow" viewBox="0 0 501 280" role="img" aria-label="共有のアロケータ：複数スレッドが同時に頼むと、ロックで順番待ちになる"><defs><marker id="fl14919" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">共有のアロケータ：複数スレッドが同時に頼むと、ロックで順番待ちになる</text><line x1="113.2" y1="87.0" x2="179.8" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl14919)"/><line x1="121.0" y1="148.0" x2="179.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl14919)"/><line x1="113.2" y1="209.0" x2="179.8" y2="171.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl14919)"/><line x1="261.0" y1="148.0" x2="319.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl14919)"/><text x="290.0" y="142.0" text-anchor="middle" style="font-size:12px">1つずつ</text><rect x="28.0" y="44.0" width="90" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="73.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">スレッド1</text><rect x="28.0" y="128.0" width="90" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="73.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">スレッド2</text><rect x="28.0" y="212.0" width="90" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="73.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">スレッド3</text><rect x="182.0" y="128.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="220.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ロック</text><rect x="322.0" y="128.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="370.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">共有ヒープ</text></svg>

| 問題 | 説明 |
| --- | --- |
| **待ち** | 1 つのスレッドが確保している間、ほかは待つ |
| キャッシュの競合 | 複数コアが同じ管理データを書き換えて、キャッシュラインが行ったり来たり |
| スケールしない | スレッドを増やしても速くならない（むしろ遅い） |
| 時間が読めない | 待ち時間が不定でカクつく |

## 対策 1：スレッドごとに別のアロケータ

**各スレッドが自分専用のアロケータ**を持てば、ロックが不要です。

```cpp
thread_local LinearAllocator t_arena(buffer, size);
thread_local PoolAllocator t_pool(sizeof(Bullet), 1024);
```

| 長所 | 短所 |
| --- | --- |
| ロックなし（最速） | スレッド数 × メモリを使う |
| 競合なし | ほかのスレッドが確保したものを、返せない |
| キャッシュに優しい（自分のデータだけ） | スレッド間でメモリを融通できない |

ジョブシステムでは、各ワーカー スレッドに、フレームアロケータを持たせるのが定番です（[フレームアロケータ](frame.md)）。

## 対策 2：スレッドキャッシュ

**スレッドごとの小さなキャッシュ**から、ロックなしで確保し、足りなくなったときだけ、共有の中央ヒープ（ロックあり）から、まとめて補充します。tcmalloc・mimalloc・jemalloc がこの方式です。

<div class="anim" data-type="graph" data-label="スレッドキャッシュ：普段はロックなし。足りないときだけ、中央から、まとめて補充する">
n t スレッド 0 1 hit
n c スレッド_キャッシュ 1 1
n h 中央ヒープ_（ロックあり） 2 1
l t c hit 確保（ロックなし）
---
n t スレッド 0 1
n c スレッド_キャッシュ_（空） 1 1 gone
n h 中央ヒープ_（ロックあり） 2 1 hit
l t c gone 足りない
l c h hit まとめて補充
---
n t スレッド 0 1
n c スレッド_キャッシュ_（補充済み） 1 1 new
n h 中央ヒープ_（ロックあり） 2 1
l h c hit 32個ぶん
l t c hit 以後はロックなし
</div>

| 動き | ロック |
| --- | --- |
| 確保 | スレッドキャッシュから（ロックなし） |
| 解放 | スレッドキャッシュに戻す（ロックなし） |
| キャッシュが空 | 中央から、まとめて補充（ロックあり、頻度は低い） |
| キャッシュが一杯 | 中央にまとめて返す（ロックあり） |

「まとめて」運ぶことでロックを取る回数を数十分の一に減らします。

## クロススレッド解放

**スレッド A が確保したものを、スレッド B が返す**場合は、難しい問題があります。A のキャッシュは、A しか触れない（ロックなしのため）からです。

| 方法 | 説明 |
| --- | --- |
| 返却キュー（リモートフリー） | 所有者のスレッドごとに、ロックフリーのキューを持つ。B は、A のキューにブロックを積む。A が自分のタイミングで取り込む（mimalloc の方式） |
| 中央ヒープに返す | ロックを取って、中央ヒープに返す。簡単だが遅い |
| 所有者のスレッドで解放させる | 「解放してね」というメッセージを送る |
| 設計で避ける | 確保したスレッドが解放するルールにする（最も簡単で速い） |

設計の段階で、「確保したスレッドが解放する」ようにできれば、この問題は起きません。

## 対策 3：ロックフリーのプール

<strong>ロックを使わず、原子操作（`compare_exchange`）</strong>で、共有のプールを作れます。

```cpp
class LockFreePool {
 public:
  LockFreePool(size_t block_size, uint32_t count) {
    storage_ = std::make_unique<std::byte[]>(block_size * count);
    block_size_ = block_size;
    for (uint32_t i = 0; i < count; ++i) {
      *reinterpret_cast<uint32_t*>(Block(i)) = (i + 1 < count) ? i + 1 : kNull;
    }
    head_.store(Pack(0, 0));
  }

  void* Allocate() {
    uint64_t old_head = head_.load(std::memory_order_acquire);
    for (;;) {
      uint32_t index = Index(old_head);
      if (index == kNull) return nullptr;
      uint32_t next = *reinterpret_cast<uint32_t*>(Block(index));
      uint64_t new_head = Pack(next, Tag(old_head) + 1);
      if (head_.compare_exchange_weak(old_head, new_head, std::memory_order_acq_rel)) {
        return Block(index);
      }
    }
  }

  void Deallocate(void* ptr) {
    uint32_t index = static_cast<uint32_t>((static_cast<std::byte*>(ptr) - storage_.get()) / block_size_);
    uint64_t old_head = head_.load(std::memory_order_acquire);
    for (;;) {
      *reinterpret_cast<uint32_t*>(ptr) = Index(old_head);
      uint64_t new_head = Pack(index, Tag(old_head) + 1);
      if (head_.compare_exchange_weak(old_head, new_head, std::memory_order_acq_rel)) return;
    }
  }

 private:
  static constexpr uint32_t kNull = 0xFFFFFFFF;
  static uint64_t Pack(uint32_t index, uint32_t tag) { return (static_cast<uint64_t>(tag) << 32) | index; }
  static uint32_t Index(uint64_t v) { return static_cast<uint32_t>(v); }
  static uint32_t Tag(uint64_t v) { return static_cast<uint32_t>(v >> 32); }
  std::byte* Block(uint32_t i) { return storage_.get() + i * block_size_; }

  std::unique_ptr<std::byte[]> storage_;
  size_t block_size_;
  std::atomic<uint64_t> head_;
};
```

| 点 | 説明 |
| --- | --- |
| 空きリストの先頭を、`atomic` | 「番号 32 ビット ＋ タグ 32 ビット」を、1 つの 64 ビット整数にまとめる |
| `compare_exchange_weak` | 「今の先頭が読んだときと同じなら、新しい値に」。同時に変えた人がいれば、失敗してやり直し |
| ブロックの番号（インデックス） | ポインタではなく番号にして、タグと 64 ビットに収める |

### ABA 問題

ロックフリーのリストの、有名な罠です。

```text
スレッド 1：先頭が A、その次が B と読む（compare_exchange の直前）
スレッド 2：A を取り、B を取り、A を戻す（先頭は、また A。ただし、次は C）
スレッド 1：「先頭は、まだ A だ」と思って、「先頭を B に」と書き込む → B は、すでに使用中（壊れる）
```

「値が同じ」でも、「その間に変わっていた」ことに気づけません。対策はタグ（バージョン番号）を、毎回増やして一緒に比較することです（上のコードの `Tag + 1`）。

!!! warning "ロックフリーは、難しい"
    メモリオーダー・ABA・解放のタイミングなど、間違えやすい点が多く、テストでも見つけにくいバグになります。実績のあるライブラリ（mimalloc・Boost.Lockfree・moodycamel など）を使うのが安全です。自作は本当に必要なときだけにします。

## false sharing（キャッシュラインの共有）

**スレッドごとのデータを、近くに並べる**と別のスレッドの書き込みで、キャッシュラインが無効になり、遅くなります。

```cpp
struct alignas(64) PerThread {
  LinearAllocator arena;
  size_t allocation_count;
};

PerThread per_thread[kMaxThreads];
```

| 方法 | 説明 |
| --- | --- |
| `alignas(64)` | スレッドごとの構造体を、キャッシュラインに揃えて、分ける |
| `std::hardware_destructive_interference_size` | 分けるべきサイズ（C++17） |

（詳しくは、[データ構造の配置](../data-layout.md#false-sharing)）

## 選び方

| 状況 | 方法 |
| --- | --- |
| **ジョブシステム・フレームの一時データ** | スレッドごとにフレームアロケータ（ロックなし） |
| 汎用の `new` / `delete` | mimalloc などに置き換え（スレッドキャッシュ入り）（[malloc の置き換え](global-replace.md)） |
| 共有のオブジェクトプール | ロックで守る（競合が少なければ）、またはスレッドごとのプール |
| 競合が激しい、共有のプール | ロックフリー（実績のあるライブラリで） |
| クロススレッド解放が多い | 設計を見直す（確保した本人が解放） |

## よくあるミス

??? failure "共有のアロケータを、ロックなしで複数スレッドから使う"
    **データ競合**で壊れます。スレッドごとに持つか、ロックで守ります。

??? failure "`thread_local` のアロケータを、別のスレッドで解放する"
    所有者でないスレッドが、キャッシュを書き換えます。確保した本人が解放します。

??? failure "ロックフリーで、ABA 問題に気づかない"
    タグ付きにします。自作せず、実績のあるライブラリを使います。

??? failure "スレッドごとの構造体が、隣り合っていて、false sharing"
    `alignas(64)` で分けます。

??? failure "スレッドごとのアロケータで、メモリを使いすぎる"
    スレッド数 × 容量です。スレッドの数と、1 スレッドの使用量を見積もります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>共有のアロケータは、ロックで遅くなる</strong>。最速はスレッドごとに別のアロケータ（`thread_local`）
    - [x] スレッドキャッシュ ＋ 中央ヒープで、普段はロックなし（tcmalloc・mimalloc の方式）
    - [x] クロススレッド解放は難しい。設計で避ける（確保した本人が解放）
    - [x] ロックフリーはABA 問題に、タグで対策。自作より、ライブラリ
    - [x] スレッドごとのデータは、`alignas(64)` で分ける

## 関連ページ

- [アロケータ（目次）](index.md)
- [フレームアロケータ](frame.md)
- [プールアロケータ](pool.md)
- [malloc の置き換え](global-replace.md)
- [マルチスレッド化](../multithreading.md)
- [std::atomic](../../stl/concurrency/atomic.md)
- [データ構造の配置](../data-layout.md)

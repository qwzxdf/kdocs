---
title: スラブアロケータ（サイズクラス）
tags:
  - 最適化
  - アロケータ
---

# スラブアロケータ（サイズクラス）

**スラブアロケータ**（slab allocator）は、**大きさの段階（サイズクラス）ごとに、[プール](pool.md)を持つ**アロケータです。**要求の大きさを、最も近い段階に切り上げ**、**その段階のプールから、O(1) で貸します**。**汎用の確保を、プールの速さで**できます。Linux カーネルが、**小さなオブジェクトの確保**に使うほか、**mimalloc・tcmalloc・jemalloc** など、多くの高速な `malloc` が、<strong>この考え方（サイズクラス）</strong>を、土台にしています。

!!! tip "ポイント"
    - <strong>大きさの段階（サイズクラス）</strong>を決める（16、32、48、64、80 ... のように）。
    - <strong>クラスごとに、専用のプール（スラブ）</strong>。<strong>要求を、近いクラスへ切り上げて、O(1) で確保</strong>。
    - <strong>スラブ（まとまったメモリの塊）</strong>は、<strong>同じ大きさのブロックに、区切ってある</strong>。
    - <strong>ブロックのアドレスから、スラブの位置が、計算で分かる</strong>（スラブを、境界に置く）。<strong>ブロックごとのヘッダが、いらない</strong>。
    - 弱点：<strong>クラス間の無駄</strong>（内部断片化）、<strong>大きなものは別扱い</strong>。
    - 汎用の、高速な `malloc` の<strong>基本形</strong>。

## 仕組み

<div class="anim" data-type="graph" data-label="スラブ：要求の大きさを、サイズクラスに切り上げて、そのクラスのプールから貸す">
n req 要求_40バイト 0 1 hit
---
n req 要求_40バイト 0 1
n cls サイズクラス_48バイト 1 1 new
l req cls hit 切り上げ
---
n req 要求_40バイト 0 1 dim
n c32 クラス32_のプール 1 0
n cls クラス48_のプール 1 1 hit
n c64 クラス64_のプール 1 2
n blk ブロック_(48バイト) 2 1 new
l cls blk hit 先頭を貸す
</div>

### サイズクラス

| クラス（バイト） | 使える範囲（要求の大きさ） |
| --- | --- |
| 16 | 1〜16 |
| 32 | 17〜32 |
| 48 | 33〜48 |
| 64 | 49〜64 |
| 80、96、112、128 | 16 刻み |
| 160、192、224、256 | 32 刻み |
| 320、384、448、512 | 64 刻み |
| … | **大きくなるほど、刻みを粗く**（無駄を、約 12.5〜25% 以内に抑える） |

**小さいうちは細かく、大きくなるほど粗く**分けるのが定番です。**クラスが多いほど、無駄は減りますが、プールが増えて、管理が重く**なります。

```cpp
size_t ClassIndex(size_t size) {
  if (size <= 128) return (size + 15) / 16 - 1;
  ...
}

constexpr size_t kClassSizes[] = {16, 32, 48, 64, 80, 96, 112, 128, 160, 192, 224, 256};
```

## スラブ

**スラブ**は、**1 つのクラスの、ブロックを、まとめて入れた、大きなメモリの塊**です（たとえば 64KB）。**スラブの中は、プールと同じ**（空きブロックのリスト）です。

```text
スラブ（64KB、サイズクラス 48）
[ ヘッダ ][ 48 ][ 48 ][ 48 ][ 48 ] ... 
 ↑ 空きリストの先頭、使用中の数
```

| スラブの状態 | 意味 |
| --- | --- |
| <strong>空き（empty）</strong> | **全ブロックが空き**（OS に返せる・ほかのクラスに回せる） |
| <strong>一部使用（partial）</strong> | 空きブロックがある → **ここから貸す** |
| <strong>満杯（full）</strong> | **空きなし** → 貸す対象から外す |

**クラスごとに、一部使用のスラブを、リスト**で持ち、**空きがなくなったら、新しいスラブを足します**。

## 実装（ブロックのアドレスから、スラブを見つける）

**スラブを、スラブの大きさの境界に置く**と、**ブロックのアドレスの、下位ビットを切り捨てるだけで、スラブの先頭**に行けます。**ブロックごとのヘッダが、いりません**。

```cpp
constexpr size_t kSlabSize = 64 * 1024;

struct Slab {
  Slab* next;
  void* free_head;
  uint32_t block_size;
  uint32_t used;
  uint32_t capacity;
};

Slab* SlabOf(void* ptr) {
  return reinterpret_cast<Slab*>(reinterpret_cast<uintptr_t>(ptr) & ~(kSlabSize - 1));
}
```

```cpp
class SlabAllocator {
 public:
  void* Allocate(size_t size) {
    size_t cls = ClassIndex(size);
    Slab* slab = partial_[cls];
    if (slab == nullptr) {
      slab = NewSlab(kClassSizes[cls]);
      if (slab == nullptr) return nullptr;
      partial_[cls] = slab;
    }

    void* block = slab->free_head;
    slab->free_head = *static_cast<void**>(block);
    ++slab->used;

    if (slab->free_head == nullptr) {
      partial_[cls] = slab->next;
    }
    return block;
  }

  void Deallocate(void* ptr) {
    Slab* slab = SlabOf(ptr);
    *static_cast<void**>(ptr) = slab->free_head;
    slab->free_head = ptr;
    --slab->used;
    ...
  }

 private:
  Slab* partial_[kClassCount] = {};
};
```

| 点 | 説明 |
| --- | --- |
| **`SlabOf(ptr)`** | **ポインタの下位ビットを切って、スラブの先頭**へ（**スラブが、境界に整列**している前提） |
| **`Deallocate` に、`size` がいらない** | **スラブのヘッダに、ブロックの大きさ**が入っている |
| **満杯になったスラブ** | **`partial_` から外す**。**解放されたら、戻す** |
| **空になったスラブ** | **OS に返す・ほかのクラスに再利用**（一定数は、残す） |

!!! note "スラブを、境界に整列して確保する"
    **`_aligned_malloc(kSlabSize, kSlabSize)`** や、**`VirtualAlloc`**（64KB の粒度）で、**境界に揃った**メモリを得ます（[malloc の置き換え](global-replace.md)）。

## 大きなオブジェクト

**最大のサイズクラスを超える**要求（たとえば 32KB 以上）は、**スラブでは扱わず**、**別の方法**にします。

| 方法 | 説明 |
| --- | --- |
| **OS に、直接頼む** | `VirtualAlloc` / 通常の `malloc`（**大きいので、回数は少ない**） |
| **別の汎用アロケータ** | [TLSF](tlsf.md) や [バディ](buddy.md) |
| **専用の領域** | ゲームでは、**アセットの置き場**を、別に持つ |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| <strong>確保・解放が、O(1)</strong> | **クラス間の無駄**（内部断片化）。数%〜25% |
| **ブロックごとのヘッダが、いらない** | **大きなものは、別扱い** |
| **同じ大きさが、まとまる**（キャッシュに優しい） | **スラブ単位で、メモリが残る**（空きの返却が難しい） |
| **断片化しにくい**（同じ大きさだけが、同じスラブに） | **クラスの設計**（刻み方）が、難しい |
| **スレッドごとに、キャッシュを持てる** | |

## プールとの違い

| | プール | スラブ（サイズクラス） |
| --- | --- | --- |
| **大きさ** | **1 種類** | **複数の段階** |
| **用途** | 同じ型の、大量のオブジェクト | **汎用の、`malloc` の代わり** |
| **構成** | プール 1 つ | <strong>クラスの数だけ、プール（スラブ）</strong> |

## 使いどころ

| 場面 | 例 |
| --- | --- |
| **汎用の小さな確保** | `malloc` の高速な代替（mimalloc などの土台） |
| **カーネル・ドライバ** | 小さなオブジェクトの管理（Linux の SLAB / SLUB） |
| **ゲームのヒープ** | **小さな確保が大量**にあるとき |
| **スクリプト言語・VM** | オブジェクトの確保 |

## よくあるミス

??? failure "スラブを、境界に揃えずに、`SlabOf` で壊れる"
    **`kSlabSize` の境界**に置くことが、前提です。

??? failure "返却のとき、別のアロケータのポインタを渡す"
    **`SlabOf` が、無関係なアドレス**を指して、**メモリが壊れます**。

??? failure "クラスの刻みが、粗すぎる"
    **無駄が大きく**なります。**要求の分布**を測って、**刻みを決めます**。

??? failure "空きスラブを、返さずに、メモリを使い続ける"
    **一定数を超えたら、OS に返す**方針を決めます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>サイズクラスごとに、プール（スラブ）</strong>を持つ。<strong>要求を切り上げて、O(1) で確保</strong>
    - [x] <strong>スラブを、境界に整列</strong>して置けば、<strong>ポインタから、スラブが分かる</strong>（ヘッダ不要）
    - [x] <strong>小さいうちは細かく、大きくなるほど粗く</strong>クラスを分ける
    - [x] 大きな要求は<strong>別扱い</strong>。<strong>汎用の高速な `malloc` の、基本形</strong>

## 関連ページ

- [アロケータ（目次）](index.md)
- [プールアロケータ](pool.md)
- [TLSF](tlsf.md)
- [スレッドとアロケータ](thread-local.md)
- [malloc の置き換え](global-replace.md)

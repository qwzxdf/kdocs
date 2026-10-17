---
title: バディアロケータ
tags:
  - 最適化
  - アロケータ
---

# バディアロケータ

**バディアロケータ**（buddy allocator）は、**メモリを、2 のべき乗の大きさのブロックに、半分ずつ分割**して貸すアロケータです。<strong>分割したときの「相棒」（バディ）</strong>は、**アドレスの計算だけで、すぐに見つかる**ので、**返すとき、相棒が空いていれば、すぐに合体**できます。**結合が速く、断片化も抑えられます**。Linux カーネルの、**ページ単位の管理**に使われています。

!!! tip "ポイント"
    - <strong>ブロックの大きさは、すべて 2 のべき乗</strong>（64、128、256 ...）。<strong>要求は、次の 2 のべき乗に切り上げ</strong>。
    - <strong>大きいブロックを、半分に割って</strong>、<strong>片方を貸し、片方を空きに</strong>。
    - <strong>相棒（バディ）のアドレス ＝ `オフセット XOR 大きさ`</strong>。<strong>計算だけで見つかる</strong>。
    - <strong>返したとき、相棒も空きなら、合体</strong>（さらに、親の相棒とも、合体できる）。
    - 弱点：<strong>切り上げによる無駄</strong>（内部断片化。最大で約 50%）。
    - 向く用途：<strong>ページ単位のメモリ管理、大きなブロックの、汎用的な確保</strong>。

## 仕組み

メモリ全体（たとえば 256 バイト）を、**1 つの大きなブロック**とします。**要求が来たら、必要な大きさになるまで、半分に分割**します。

<div class="anim" data-type="graph" data-label="バディ：32 バイトを取りたい。256 → 128 → 64 → 32 と、半分ずつ割る">
n b256 256 0 1 hit
---
n b256 256 0 1 dim
n b128a 128 1 0 new
n b128b 128_（空き） 1 2 new
l b256 b128a hit 割る
l b256 b128b hit 割る
---
n b128a 128 1 0 dim
n b64a 64 2 -0.5 new
n b64b 64_（空き） 2 0.5 new
n b128b 128_（空き） 1 2
l b128a b64a hit 割る
l b128a b64b hit 割る
---
n b64a 64 2 -0.5 dim
n b32a 32_（貸す） 3 -1 hit
n b32b 32_（空き） 3 0 new
n b64b 64_（空き） 2 0.5
n b128b 128_（空き） 1 2
l b64a b32a hit 割る
l b64a b32b hit 割る
</div>

### 相棒（バディ）の見つけ方

ブロックを、**割ったときに生まれる 2 つ**が、**お互いの相棒**です。**相棒のアドレスは、XOR で求まります**。

```text
ブロックのオフセット ＝ 64、大きさ ＝ 64   → 相棒のオフセット ＝ 64 XOR 64 ＝ 0
ブロックのオフセット ＝  0、大きさ ＝ 64   → 相棒のオフセット ＝  0 XOR 64 ＝ 64
```

| 項目 | 式 |
| --- | --- |
| **相棒のオフセット** | **`offset ^ size`** |
| **ブロックの大きさ** | `最小の大きさ << order`（`order` は、段階の番号） |

**大きさが 2 のべき乗**で、**そのべき乗の境界に置かれている**ので、**XOR だけで、相棒に行きます**（検索いらず）。

### 合体（結合）

**返されたブロックの相棒が、空き**なら、**2 つを合体**して、**1 つ大きなブロック**にします。**さらに、その親の相棒も空き**なら、**合体を続けます**。

<div class="anim" data-type="graph" data-label="返却：相棒も空きなら、合体して、大きなブロックに戻る">
n a 32_（返す） 0 0 hit
n b 32_（相棒：空き） 0 1
n c 64_（空き） 1 0.5
---
n a 32_（返す） 0 0 hit
n b 32_（相棒：空き） 0 1 hit
n c 64_（空き） 1 0.5
l a b hit 相棒
---
n m 合体_64 1 0.5 new
n c 64_（相棒：空き） 1 1.5
---
n m2 合体_128 2 1 new
</div>

## 実装

```cpp
#include <bit>
#include <vector>

class BuddyAllocator {
 public:
  BuddyAllocator(void* buffer, size_t total_size, size_t min_block)
      : base_(static_cast<std::byte*>(buffer)), min_block_(min_block) {
    max_order_ = std::bit_width(total_size / min_block) - 1;
    free_lists_.resize(max_order_ + 1);
    free_lists_[max_order_].push_back(0);
  }

  void* Allocate(size_t size) {
    int order = OrderFor(size);
    int found = order;
    while (found <= max_order_ && free_lists_[found].empty()) ++found;
    if (found > max_order_) return nullptr;

    size_t offset = free_lists_[found].back();
    free_lists_[found].pop_back();

    while (found > order) {
      --found;
      size_t buddy = offset + BlockSize(found);
      free_lists_[found].push_back(buddy);
    }
    return base_ + offset;
  }

  void Deallocate(void* ptr, size_t size) {
    size_t offset = static_cast<std::byte*>(ptr) - base_;
    int order = OrderFor(size);

    while (order < max_order_) {
      size_t buddy = offset ^ BlockSize(order);
      auto& list = free_lists_[order];
      auto it = std::find(list.begin(), list.end(), buddy);
      if (it == list.end()) break;
      list.erase(it);
      offset = std::min(offset, buddy);
      ++order;
    }
    free_lists_[order].push_back(offset);
  }

 private:
  size_t BlockSize(int order) const { return min_block_ << order; }

  int OrderFor(size_t size) const {
    size_t blocks = (size + min_block_ - 1) / min_block_;
    return std::bit_width(std::bit_ceil(blocks)) - 1;
  }

  std::byte* base_;
  size_t min_block_;
  int max_order_;
  std::vector<std::vector<size_t>> free_lists_;
};
```

| 点 | 説明 |
| --- | --- |
| **`free_lists_[order]`** | **大きさごとの空きリスト**（オフセットを入れる） |
| **`OrderFor`** | **要求を、次の 2 のべき乗に切り上げ**（`std::bit_ceil`） |
| **`Allocate` の分割** | **大きな空きを見つけたら、必要な大きさになるまで、半分に割り**、**片方（相棒）を、空きリストへ** |
| **`Deallocate` の合体** | **相棒が空きなら、リストから取り出して、合体**。`order` を上げて、繰り返す |
| **`offset ^ BlockSize(order)`** | **相棒のオフセット** |
| **`std::min(offset, buddy)`** | **合体後のブロックの先頭**は、小さい方のオフセット |

!!! note "実用版は、もっと工夫する"
    この実装は、**仕組みを見る**ためのものです（相棒の探索が `std::find` で、遅い）。実際は、**侵入型の双方向リスト**（O(1) で取り出し）や、**ビットマップ**で、**相棒が空きか**を、速く調べます。**`Deallocate` に `size` を渡す**のは、**ブロックのヘッダを持たない**ためです（ヘッダを持つ実装もあります）。

## 内部断片化

**要求を、2 のべき乗に切り上げる**ので、**無駄**が出ます。

| 要求 | 実際の確保 | 無駄 |
| --- | --- | --- |
| 33 バイト | 64 バイト | <strong>31 バイト（約 48%）</strong> |
| 64 バイト | 64 バイト | 0 |
| 65 バイト | 128 バイト | <strong>63 バイト（約 49%）</strong> |
| 100 バイト | 128 バイト | 28 バイト（22%） |

**最悪で、ほぼ 50%** が無駄になります。**平均では 25% 程度**です。**要求の大きさが、2 のべき乗に近い**場合は、無駄が少なくなります。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **結合が速い**（XOR で相棒が見つかる） | **内部断片化**（最大約 50%） |
| **外部断片化が、抑えられる** | 要求は、**2 のべき乗に、切り上げ** |
| **確保・解放が、速く**、**時間が読める**（段階の数だけ） | **小さなブロックには、不向き**（管理が重い） |
| **仕組みが単純** | **最小のブロックサイズ**が、決まっている |

## 使いどころ

| 場面 | 理由 |
| --- | --- |
| **ページ単位のメモリ管理**（OS のカーネル、VM） | **ページは、2 のべき乗**。無駄が出にくい |
| **大きなアセットの置き場** | 大きなブロックの、確保と返却が多い |
| **テクスチャ・バッファの管理**（GPU メモリのサブ割り当て） | 2 のべき乗の大きさが、多い |
| **ほかのアロケータの、土台** | **大きなチャンク**を、バディで切り出し、**中は、プールやスラブ** |

**小さなオブジェクト**の汎用の確保には、[スラブ](slab.md)や [TLSF](tlsf.md) が向いています。

## よくあるミス

??? failure "要求の大きさを、切り上げ忘れて、ブロックを壊す"
    **要求の大きさ以上の、最も小さい 2 のべき乗**に、切り上げます。

??? failure "返却時に、確保したときと違う大きさを渡す"
    **`order` が違い**、**間違った相棒**を探して、**メモリが壊れます**。**ヘッダに大きさを記録**する方法もあります。

??? failure "最小ブロックを、小さくしすぎる"
    **管理の情報（リスト）のほうが、大きく**なります。**64 バイト以上**など、**用途に合わせて**決めます。

??? failure "全体の大きさが、2 のべき乗でない"
    **最大のブロックが取れず**、**端が無駄**になります。**全体を、2 のべき乗にする**か、**複数の木**で管理します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>2 のべき乗のブロックを、半分ずつ割って</strong>貸す。<strong>返されたら、相棒と合体</strong>
    - [x] <strong>相棒のアドレス ＝ `offset ^ size`</strong>。<strong>計算だけで見つかる</strong>
    - [x] <strong>結合が速く、外部断片化を抑えられる</strong>。<strong>代わりに、内部断片化（最大約 50%）</strong>
    - [x] 向くのは<strong>ページ単位・大きなブロックの管理</strong>。<strong>小さなオブジェクトは、スラブ・TLSF</strong>

## 関連ページ

- [アロケータ（目次）](index.md)
- [フリーリストアロケータ](free-list.md)
- [スラブアロケータ](slab.md)
- [TLSF](tlsf.md)

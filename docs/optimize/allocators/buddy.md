---
title: バディアロケータ
tags:
  - 最適化
  - アロケータ
---

# バディアロケータ

**バディアロケータ**（buddy allocator）は、メモリを 2 のべき乗の大きさのブロックに半分ずつ分割して貸すアロケータです。分割したときの「相棒」（バディ）は、アドレスの計算だけですぐに見つかるので返すとき、相棒が空いていれば、すぐに合体できます。結合が速く、断片化も抑えられます。Linux カーネルの、ページ単位の管理に使われています。

!!! tip "ポイント"
    - <strong>ブロックの大きさは、すべて 2 のべき乗</strong>（64、128、256 ...）。<strong>要求は次の 2 のべき乗に切り上げ</strong>。
    - 大きいブロックを半分に割って、片方を貸し、片方を空きに。
    - 相棒（バディ）のアドレス ＝ `オフセット XOR 大きさ`。計算だけで見つかる。
    - 返したとき、相棒も空きなら、合体（さらに親の相棒とも合体できる）。
    - 弱点：切り上げによる無駄（内部断片化。最大で約 50%）。
    - 向く用途：ページ単位のメモリ管理、大きなブロックの汎用的な確保。

!!! info "このページを読む前に"
    - [optimize/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [メモリ確保](../allocation.md)（メモリ確保が遅い理由）

## 仕組み

メモリ全体（たとえば 256 バイト）を**1 つの大きなブロック**とします。要求が来たら、必要な大きさになるまで、半分に分割します。

<svg class="fig flow" viewBox="0 0 647 364" role="img" aria-label="バディ：32 バイトを取りたい。256 → 128 → 64 → 32 と、半分ずつ割る"><defs><marker id="fl81686" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">バディ：32 バイトを取りたい。256 → 128 → 64 → 32 と、半分ずつ割る</text><line x1="107.0" y1="210.3" x2="183.5" y2="169.7" stroke="currentColor" stroke-width="2" marker-end="url(#fl81686)"/><text x="145.2" y="184.0" text-anchor="middle" style="font-size:12px">割る</text><line x1="107.0" y1="253.7" x2="181.1" y2="293.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl81686)"/><text x="144.1" y="267.4" text-anchor="middle" style="font-size:12px">割る</text><line x1="265.5" y1="138.0" x2="356.5" y2="116.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl81686)"/><text x="311.0" y="121.0" text-anchor="middle" style="font-size:12px">割る</text><line x1="265.5" y1="158.0" x2="342.0" y2="176.5" stroke="currentColor" stroke-width="2" marker-end="url(#fl81686)"/><text x="303.8" y="161.2" text-anchor="middle" style="font-size:12px">割る</text><line x1="438.5" y1="95.8" x2="511.0" y2="77.8" stroke="currentColor" stroke-width="2" marker-end="url(#fl81686)"/><text x="474.8" y="80.8" text-anchor="middle" style="font-size:12px">割る</text><line x1="438.5" y1="116.2" x2="511.0" y2="134.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl81686)"/><text x="474.8" y="119.2" text-anchor="middle" style="font-size:12px">割る</text><rect x="28.0" y="212.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2" opacity="0.55"/><text x="66.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">256</text><circle cx="30.0" cy="214.0" r="10" fill="#4c8bf5"/><text x="30.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="186.5" y="128.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2" opacity="0.55"/><text x="224.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">128</text><circle cx="188.5" cy="130.0" r="10" fill="#2ea043"/><text x="188.5" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="168.0" y="296.0" width="113" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="224.5" y="316.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">128 （空き）</text><circle cx="170.0" cy="298.0" r="10" fill="#2ea043"/><text x="170.0" y="298.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="359.5" y="86.0" width="76" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2" opacity="0.55"/><text x="397.5" y="106.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">64</text><circle cx="361.5" cy="88.0" r="10" fill="#e5a828"/><text x="361.5" y="88.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="345.0" y="170.0" width="105" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="397.5" y="190.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">64 （空き）</text><circle cx="347.0" cy="172.0" r="10" fill="#e5a828"/><text x="347.0" y="172.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="514.0" y="44.0" width="105" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="566.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">32 （貸す）</text><circle cx="516.0" cy="46.0" r="10" fill="#e5484d"/><text x="516.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="514.0" y="128.0" width="105" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="566.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">32 （空き）</text><circle cx="516.0" cy="130.0" r="10" fill="#e5484d"/><text x="516.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

### 相棒（バディ）の見つけ方

ブロックを割ったときに生まれる 2 つが、お互いの相棒です。相棒のアドレスは、XOR で求まります。

```text
ブロックのオフセット ＝ 64、大きさ ＝ 64   → 相棒のオフセット ＝ 64 XOR 64 ＝ 0
ブロックのオフセット ＝  0、大きさ ＝ 64   → 相棒のオフセット ＝  0 XOR 64 ＝ 64
```

| 項目 | 式 |
| --- | --- |
| 相棒のオフセット | `offset ^ size` |
| ブロックの大きさ | `最小の大きさ << order`（`order` は、段階の番号） |

大きさが 2 のべき乗で、そのべき乗の境界に置かれているので、XOR だけで相棒に行きます（検索いらず）。

### 合体（結合）

返されたブロックの相棒が空きなら、2 つを合体して、1 つ大きなブロックにします。さらにその親の相棒も空きなら、合体を続けます。

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
| **`free_lists_[order]`** | 大きさごとの空きリスト（オフセットを入れる） |
| `OrderFor` | 要求を次の 2 のべき乗に切り上げ（`std::bit_ceil`） |
| `Allocate` の分割 | 大きな空きを見つけたら、必要な大きさになるまで、半分に割り、片方（相棒）を空きリストへ |
| `Deallocate` の合体 | 相棒が空きなら、リストから取り出して、合体。`order` を上げて、繰り返す |
| `offset ^ BlockSize(order)` | 相棒のオフセット |
| `std::min(offset, buddy)` | 合体後のブロックの先頭は、小さい方のオフセット |

!!! note "実用版は、もっと工夫する"
    この実装は仕組みを見るためのものです（相棒の探索が `std::find` で遅い）。実際は侵入型の双方向リスト（O(1) で取り出し）や、ビットマップで相棒が空きかを速く調べます。`Deallocate` に `size` を渡すのは、ブロックのヘッダを持たないためです（ヘッダを持つ実装もあります）。

## 内部断片化

**要求を 2 のべき乗に切り上げる**ので、無駄が出ます。

| 要求 | 実際の確保 | 無駄 |
| --- | --- | --- |
| 33 バイト | 64 バイト | 31 バイト（約 48%） |
| 64 バイト | 64 バイト | 0 |
| 65 バイト | 128 バイト | 63 バイト（約 49%） |
| 100 バイト | 128 バイト | 28 バイト（22%） |

最悪でほぼ 50% が無駄になります。平均では 25% 程度です。要求の大きさが、2 のべき乗に近い場合は、無駄が少なくなります。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **結合が速い**（XOR で相棒が見つかる） | 内部断片化（最大約 50%） |
| 外部断片化が抑えられる | 要求は、2 のべき乗に切り上げ |
| 確保・解放が速く、時間が読める（段階の数だけ） | 小さなブロックには、不向き（管理が重い） |
| 仕組みが単純 | 最小のブロックサイズが決まっている |

## 使いどころ

| 場面 | 理由 |
| --- | --- |
| **ページ単位のメモリ管理**（OS のカーネル、VM） | ページは、2 のべき乗。無駄が出にくい |
| 大きなアセットの置き場 | 大きなブロックの確保と返却が多い |
| テクスチャ・バッファの管理（GPU メモリのサブ割り当て） | 2 のべき乗の大きさが、多い |
| ほかのアロケータの土台 | 大きなチャンクをバディで切り出し、中はプールやスラブ |

小さなオブジェクトの汎用の確保には、[スラブ](slab.md)や [TLSF](tlsf.md) が向いています。

## よくあるミス

??? failure "要求の大きさを切り上げ忘れて、ブロックを壊す"
    **要求の大きさ以上の最も小さい 2 のべき乗**に切り上げます。

??? failure "返却時に確保したときと違う大きさを渡す"
    `order` が違い、間違った相棒を探して、メモリが壊れます。ヘッダに大きさを記録する方法もあります。

??? failure "最小ブロックを小さくしすぎる"
    管理の情報（リスト）のほうが大きくなります。64 バイト以上など、用途に合わせて決めます。

??? failure "全体の大きさが、2 のべき乗でない"
    最大のブロックが取れず、端が無駄になります。全体を 2 のべき乗にするか、複数の木で管理します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>2 のべき乗のブロックを半分ずつ割って</strong>貸す。返されたら、相棒と合体
    - [x] 相棒のアドレス ＝ `offset ^ size`。計算だけで見つかる
    - [x] 結合が速く、外部断片化を抑えられる。代わりに内部断片化（最大約 50%）
    - [x] 向くのはページ単位・大きなブロックの管理。小さなオブジェクトは、スラブ・TLSF

## 関連ページ

- [アロケータ（目次）](index.md)
- [フリーリストアロケータ](free-list.md)
- [スラブアロケータ](slab.md)
- [TLSF](tlsf.md)

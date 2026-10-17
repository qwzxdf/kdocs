---
title: フリーリストアロケータ
tags:
  - 最適化
  - アロケータ
---

# フリーリストアロケータ

**フリーリストアロケータ**（free list allocator）は、**大きさがバラバラの要求**に応えるための、**汎用のアロケータ**です。**空いている領域を、リスト（フリーリスト）でつなぎ**、**要求に合う空きを探して**貸します。**返されたら、リストに戻し、隣り合う空きは結合**します。`malloc` の基本の仕組みと、同じ考え方です。**リニアやプールより柔軟**ですが、**探す時間と、断片化**という弱点があります。

!!! tip "ポイント"
    - <strong>空き領域を、リストでつなぐ</strong>。<strong>要求の大きさに合う空きを、探して貸す</strong>。
    - 探し方：<strong>first-fit（最初に見つけた）、best-fit（一番ぴったり）、next-fit（前回の続き）</strong>。
    - <strong>貸すとき、空きが大きすぎたら、分割（split）</strong>。<strong>返されたとき、隣の空きと結合（coalesce）</strong>。
    - 各ブロックの前に、<strong>ヘッダ（大きさなど）</strong>を置く。<strong>解放のとき、大きさが分かる</strong>。
    - 弱点：<strong>探す時間がかかる（O(n)）</strong>、<strong>断片化</strong>（細かい空きが増える）。
    - 速さと断片化の改善版が、<strong>バディ・TLSF・スラブ</strong>。

## 仕組み

メモリを、**使用中のブロック**と、**空きのブロック**に分けて、**空きだけを、リストでつなぎます**。

<svg class="fig" viewBox="0 0 640 170" role="img" aria-label="フリーリストのメモリ">
<text x="20" y="22" class="fig-title">メモリ全体（使用中・空きが混ざる）</text>
<rect x="20" y="40" width="80" height="40" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="30" y="65">使用 A</text>
<rect x="100" y="40" width="60" height="40" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-dasharray="4 3"/><text x="108" y="65">空き 1</text>
<rect x="160" y="40" width="100" height="40" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="172" y="65">使用 B</text>
<rect x="260" y="40" width="120" height="40" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-dasharray="4 3"/><text x="285" y="65">空き 2</text>
<rect x="380" y="40" width="70" height="40" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="392" y="65">使用 C</text>
<rect x="450" y="40" width="170" height="40" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-dasharray="4 3"/><text x="500" y="65">空き 3</text>
<text x="20" y="112" class="fig-title">フリーリスト：空きだけを、つなぐ</text>
<text x="20" y="138">head → [空き 1] → [空き 2] → [空き 3] → null</text>
</svg>

### ブロックのヘッダ

**解放のとき、「どれだけの大きさか」が分からない**ので、**各ブロックの前に、ヘッダ**を置きます。

```text
[ ヘッダ(size) ][ ユーザーが使う領域 ... ]
                ↑ Allocate が、返すアドレス
```

```cpp
struct Header {
  size_t size;
  size_t adjustment;
};

struct FreeBlock {
  size_t size;
  FreeBlock* next;
};
```

| ヘッダの内容 | 意味 |
| --- | --- |
| **`size`** | ブロックの大きさ |
| **`adjustment`** | アライメントのために、**空けた隙間**（解放のとき、元の位置に戻る） |

## 探し方

要求の大きさに合う、**空きブロックを探す方法**が、いくつかあります。

| 方法 | 動き | 長所 | 短所 |
| --- | --- | --- | --- |
| **first-fit** | **先頭から探して、最初に入るもの** | **速い**（途中で止まる） | 先頭に、小さな空きが溜まる |
| **best-fit** | **全部見て、最も小さく収まるもの** | **無駄が少ない** | **全部探すので、遅い** |
| **worst-fit** | 全部見て、**最も大きいもの** | 余りが大きく、使いやすい | 大きな空きがなくなる |
| **next-fit** | **前回の続きから**探す | 速い | 断片化しやすい |

**普通は、first-fit か best-fit**です。

### 分割（split）

**空きブロックが、要求より大きい**とき、**必要な分を貸して、残りを、新しい空きブロックとして、リストに戻します**。

<svg class="fig flow" viewBox="0 0 408 280" role="img" aria-label="分割：大きな空きから、必要な分だけを貸し、残りを空きに戻す"><defs><marker id="fl74080" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">分割：大きな空きから、必要な分だけを貸し、残りを空きに戻す</text><line x1="148.5" y1="125.0" x2="242.5" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74080)"/><text x="195.5" y="100.0" text-anchor="middle" style="font-size:12px">分割</text><line x1="148.5" y1="171.0" x2="242.5" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74080)"/><text x="195.5" y="184.0" text-anchor="middle" style="font-size:12px">残りを空きへ</text><rect x="28.0" y="128.0" width="127" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2" opacity="0.55"/><text x="91.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">空き 100バイト</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="240.0" y="44.0" width="119" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="299.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">貸す 40バイト</text><circle cx="242.0" cy="46.0" r="10" fill="#2ea043"/><text x="242.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="219.0" y="212.0" width="161" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="299.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">残りの空き 60バイト</text><circle cx="221.0" cy="214.0" r="10" fill="#2ea043"/><text x="221.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text></svg>

**残りが小さすぎる**（ヘッダの大きさ未満）ときは、**分割せず、全部貸します**（無駄が出るが、管理が簡単）。

### 結合（coalesce）

**返されたブロックの、隣が空き**なら、**くっつけて、1 つの大きな空き**にします。**結合しないと、細かい空きばかりになり、大きな要求に応えられません**。

<div class="anim" data-type="graph" data-label="結合：返したブロックが、隣の空きとくっつく">
n a 空き_40 0 1
n b 使用中_30_（これを返す） 1 1 hit
n c 空き_50 2 1
---
n a 空き_40 0 1 hit
n b 返した_30 1 1 hit
n c 空き_50 2 1 hit
l b a hit 隣と結合
l b c hit 隣と結合
---
n m 1つの空き_120 1 1 new
</div>

| 結合の方法 | 説明 |
| --- | --- |
| **アドレス順のリスト** | 空きリストを、**アドレス順**に並べておく。**返すとき、前後の空きと隣り合うか**を調べる |
| **境界タグ**（boundary tag） | 各ブロックの**後ろにも、ヘッダ**を置く。**隣のブロックを、すぐに調べられる**（O(1)） |

## 実装（first-fit、アドレス順のリスト）

```cpp
class FreeListAllocator {
 public:
  FreeListAllocator(void* buffer, size_t size)
      : begin_(static_cast<std::byte*>(buffer)), size_(size) {
    Reset();
  }

  void* Allocate(size_t size, size_t alignment = alignof(std::max_align_t)) {
    FreeBlock* prev = nullptr;
    for (FreeBlock* block = head_; block != nullptr; prev = block, block = block->next) {
      uintptr_t user = reinterpret_cast<uintptr_t>(block) + sizeof(Header);
      uintptr_t aligned = (user + alignment - 1) & ~(alignment - 1);
      size_t adjustment = static_cast<size_t>(aligned - user);
      size_t total = sizeof(Header) + adjustment + size;
      if (block->size < total) continue;

      size_t remaining = block->size - total;
      if (remaining >= sizeof(FreeBlock) + 8) {
        FreeBlock* rest = reinterpret_cast<FreeBlock*>(reinterpret_cast<std::byte*>(block) + total);
        rest->size = remaining;
        rest->next = block->next;
        Link(prev, rest);
      } else {
        total = block->size;
        Link(prev, block->next);
      }

      Header* header = reinterpret_cast<Header*>(aligned - sizeof(Header));
      header->size = total;
      header->adjustment = adjustment;
      return reinterpret_cast<void*>(aligned);
    }
    return nullptr;
  }

  void Deallocate(void* ptr) {
    uintptr_t user = reinterpret_cast<uintptr_t>(ptr);
    Header* header = reinterpret_cast<Header*>(user - sizeof(Header));
    FreeBlock* block = reinterpret_cast<FreeBlock*>(user - sizeof(Header) - header->adjustment);
    block->size = header->size;

    FreeBlock* prev = nullptr;
    FreeBlock* next = head_;
    while (next != nullptr && next < block) {
      prev = next;
      next = next->next;
    }
    block->next = next;
    Link(prev, block);

    Coalesce(block, next);
    if (prev != nullptr) Coalesce(prev, block);
  }

  void Reset() {
    head_ = reinterpret_cast<FreeBlock*>(begin_);
    head_->size = size_;
    head_->next = nullptr;
  }

 private:
  struct Header {
    size_t size;
    size_t adjustment;
  };
  struct FreeBlock {
    size_t size;
    FreeBlock* next;
  };

  void Link(FreeBlock* prev, FreeBlock* next) {
    if (prev == nullptr) head_ = next;
    else prev->next = next;
  }

  void Coalesce(FreeBlock* a, FreeBlock* b) {
    if (a != nullptr && b != nullptr &&
        reinterpret_cast<std::byte*>(a) + a->size == reinterpret_cast<std::byte*>(b)) {
      a->size += b->size;
      a->next = b->next;
    }
  }

  std::byte* begin_;
  size_t size_;
  FreeBlock* head_ = nullptr;
};
```

| 点 | 説明 |
| --- | --- |
| **ヘッダの置き場所** | **返すアドレスの、すぐ前**に `Header`。**`Deallocate` で、引き算で見つかる** |
| **`adjustment`** | **アライメントの隙間**。解放時に、**ブロックの先頭**に戻すために保存 |
| **分割** | `remaining` が、**空きブロックとして成り立つ大きさ**あれば、残りを空きに |
| **アドレス順の挿入** | **`Deallocate` で、アドレス順の位置に挿入** → **隣と結合しやすい** |
| **`Coalesce`** | **隣り合っていれば、くっつける** |

!!! note "実用では、もっと工夫する"
    この実装は、**仕組みを見る**ためのものです。実際は、**境界タグ**（O(1) の結合）、**サイズごとの複数のリスト**（探すのを速く）、**最小ブロックの大きさ**などを、入れます。<strong>速さが必要なら、[TLSF](tlsf.md)</strong>を使います。

## 断片化

**確保と解放を繰り返す**と、**細かい空きが散らばって**、**合計の空きは足りているのに、大きな要求に応えられない**状態になります。

<svg class="fig" viewBox="0 0 640 150" role="img" aria-label="外部断片化">
<text x="20" y="22" class="fig-title">外部断片化：空きの合計は 80 なのに、連続した 50 は取れない</text>
<rect x="20" y="40" width="60" height="40" fill="rgba(76,139,245,0.45)" stroke="currentColor"/>
<rect x="80" y="40" width="40" height="40" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-dasharray="4 3"/><text x="86" y="65">空き</text>
<rect x="120" y="40" width="60" height="40" fill="rgba(76,139,245,0.45)" stroke="currentColor"/>
<rect x="180" y="40" width="40" height="40" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-dasharray="4 3"/><text x="186" y="65">空き</text>
<rect x="220" y="40" width="60" height="40" fill="rgba(76,139,245,0.45)" stroke="currentColor"/>
<text x="20" y="110">細かい空きが、あちこちに（40 ＋ 40 ＝ 80。しかし、連続していない）</text>
</svg>

| 種類 | 意味 | 対策 |
| --- | --- | --- |
| **外部断片化** | 空きが細かく分かれて、**大きな要求に応えられない** | **結合・best-fit・サイズクラス・まとめて捨てる** |
| **内部断片化** | ブロックの中に、**使われない余り**（アライメント、丸め） | **サイズクラスを細かく** |

**ゲームでは、断片化が、長時間のプレイで、効いてきます**。**寿命の似たもの同士を、同じアロケータにまとめる**（フレーム・ロード・プール）と、**抑えられます**。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **大きさがバラバラでも OK** | **探す時間がかかる**（O(n)） |
| **個別に返せる** | **断片化する** |
| **仕組みが単純**（理解しやすい） | **ヘッダのぶん、無駄**（ブロックごと数バイト） |
| 汎用 | **時間が一定でない**（リアルタイム向きでない） |

## よくあるミス

??? failure "結合しない"
    **細かい空きばかり**になって、**すぐに大きな要求に応えられなくなります**。

??? failure "ヘッダを、ユーザーの領域の前に置いたまま、後ろへ書き込む"
    **範囲外書き込み**で、**ヘッダが壊れて**、解放時に**メモリ全体が壊れます**（[AddressSanitizer](../../vs/asan.md)、[デバッグ用](debug.md)）。

??? failure "アライメントの隙間を、記録しない"
    **解放時に、ブロックの先頭が分からず**、**リストが壊れます**。

??? failure "二重解放する"
    **同じブロックが、リストに 2 回入り**、**同じ領域が 2 回貸される**ことがあります。

??? failure "リアルタイムな処理で、O(n) の探索を使う"
    **探す時間が、読めず**、**カクつき**ます。**TLSF**（O(1)）にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>空きをリストでつなぎ、合う空きを探して貸す</strong>。<strong>ブロックの前にヘッダ</strong>（大きさ・隙間）
    - [x] <strong>first-fit は速く、best-fit は無駄が少ない</strong>。<strong>分割して貸し、返されたら結合</strong>
    - [x] <strong>アドレス順のリスト or 境界タグ</strong>で、結合しやすくする
    - [x] 弱点は<strong>探す時間（O(n)）と断片化</strong>。<strong>リアルタイムなら TLSF</strong>
    - [x] <strong>寿命の似たものを、同じアロケータにまとめる</strong>と、断片化を抑えられる

## 関連ページ

- [アロケータ（目次）](index.md)
- [バディアロケータ](buddy.md)
- [スラブアロケータ](slab.md)
- [TLSF](tlsf.md)
- [デバッグ用アロケータ](debug.md)
- [メモリ確保](../allocation.md)

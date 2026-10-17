---
title: TLSF アロケータ
tags:
  - 最適化
  - アロケータ
---

# TLSF アロケータ

**TLSF**（Two-Level Segregated Fit：ティー・エル・エス・エフ）は、<strong>確保も解放も必ず O(1)</strong> で終わる、**リアルタイム向けの汎用アロケータ**です。**空きブロックを大きさで 2 段階に分類**し、**ビットマップで合う空きを一瞬で見つけます**。[フリーリスト](free-list.md)のように**大きさがバラバラ**でも扱えて、**探す時間が一定**で**断片化も小さく**抑えられます。**ゲームの固定領域の中の汎用の確保**に向いています。

!!! tip "ポイント"
    - <strong>確保・解放が必ず O(1)</strong>。<strong>最悪の時間が読める</strong>（リアルタイム向き）。
    - 空きブロックを<strong>2 段階で分類</strong>：<strong>第 1 段（FL）＝ 大きさの 2 のべき乗の範囲</strong>、<strong>第 2 段（SL）＝ その範囲を等分した細かい区間</strong>。
    - <strong>ビットマップ</strong>で<strong>空きがある分類をビット探索命令（`countr_zero`）で、一瞬</strong>で見つける。
    - <strong>解放で隣の空きと結合</strong>（境界タグ）。<strong>断片化を抑える</strong>。
    - 内部断片化は、<strong>約 3% 以下</strong>（SL を細かくすれば、さらに小さく）。
    - 実装は複雑なので<strong>実績のあるライブラリ</strong>（tlsf、mimalloc ほか）を使うのが現実的。

## なぜ TLSF か

| アロケータ | 探す時間 | 断片化 | 時間が読めるか |
| --- | --- | --- | --- |
| **フリーリスト**（first-fit / best-fit） | <strong>O(n)</strong>（空きの数に比例） | 中 | **読めない** |
| **バディ** | O(段階の数) | 内部断片化が大きい | 読める |
| **スラブ** | O(1) | クラス間の無駄 | 読める（大きなものは別） |
| **TLSF** | <strong>O(1)</strong> | **小さい** | **読める** |

**フリーリストの弱点**（探す時間・断片化）を、**両方、解決**したものです。

## 仕組み

### 空きブロックの 2 段階の分類

**空きブロックを大きさで分類**し、**分類ごとにリストを持ちます**。

| 段階 | 分け方 | 例 |
| --- | --- | --- |
| <strong>第 1 段（FL）</strong> | **大きさの、2 のべき乗の範囲**：`[2^fl, 2^(fl+1))` | 大きさ 300 は、`fl = 8`（256〜511） |
| <strong>第 2 段（SL）</strong> | **その範囲を等分**（たとえば 32 区間） | 256〜511 を、32 等分（8 バイト刻み）。300 は、`sl = 5` |

<svg class="fig" viewBox="0 0 640 260" role="img" aria-label="TLSF の 2 段階の分類">
<text x="20" y="22" class="fig-title">空きリストの表：第 1 段（行）× 第 2 段（列）</text>
<text x="20" y="60">FL＼SL</text>
<text x="90" y="60">0</text><text x="150" y="60">1</text><text x="210" y="60">2</text><text x="270" y="60">3</text><text x="330" y="60">…</text><text x="390" y="60">31</text>
<text x="20" y="100">fl=7（128〜255）</text>
<rect x="80" y="82" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="140" y="82" width="50" height="26" fill="rgba(76,139,245,0.5)" stroke="currentColor"/><rect x="200" y="82" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="260" y="82" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="380" y="82" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/>
<text x="20" y="140">fl=8（256〜511）</text>
<rect x="80" y="122" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="140" y="122" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="200" y="122" width="50" height="26" fill="rgba(76,139,245,0.5)" stroke="currentColor"/><rect x="260" y="122" width="50" height="26" fill="rgba(76,139,245,0.5)" stroke="currentColor"/><rect x="380" y="122" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/>
<text x="20" y="180">fl=9（512〜1023）</text>
<rect x="80" y="162" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="140" y="162" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="200" y="162" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="260" y="162" width="50" height="26" fill="rgba(150,150,150,0.2)" stroke="currentColor"/><rect x="380" y="162" width="50" height="26" fill="rgba(76,139,245,0.5)" stroke="currentColor"/>
<text x="20" y="225">青＝空きブロックのリストがある分類（ビットマップで 1）、灰＝空き（ビットマップで 0）</text>
<text x="20" y="245" style="font-size:12px">各マスは、その大きさの範囲の、空きブロックのリストの先頭</text>
</svg>

### ビットマップで、空きを探す

**どの分類に空きがあるか**を、**ビットマップ**に記録します。

| ビットマップ | 意味 |
| --- | --- |
| **`fl_bitmap`** | 第 1 段で**空きのある行**のビット |
| **`sl_bitmap[fl]`** | その行の中で**空きのある列**のビット |

**探すときはビットマップを調べるだけ**です。

```cpp
int fl = FirstLevel(size);
int sl = SecondLevel(size, fl);

uint32_t sl_map = sl_bitmap_[fl] & (~0u << sl);
if (sl_map == 0) {
  uint32_t fl_map = fl_bitmap_ & (~0u << (fl + 1));
  if (fl_map == 0) return nullptr;
  fl = std::countr_zero(fl_map);
  sl_map = sl_bitmap_[fl];
}
sl = std::countr_zero(sl_map);
Block* block = free_lists_[fl][sl];
```

| 行 | 意味 |
| --- | --- |
| `sl_bitmap_[fl] & (~0u << sl)` | **同じ行で、`sl` 以上の列**に空きがあるか |
| `fl_bitmap_ & (~0u << (fl + 1))` | **なければ、上の行**（大きい範囲）に、空きがあるか |
| **`std::countr_zero`** | **最も下位の、1 のビットの位置**（CPU の 1 命令）。**これが、O(1) の秘密** |
| `free_lists_[fl][sl]` | **見つかった分類のリストの先頭**を取り出す |

**ループがありません**。**ビット演算だけ**で**どの空きを使うか**が決まります。

### 分類の計算

```cpp
constexpr int kSlBits = 5;
constexpr int kSlCount = 1 << kSlBits;

void Mapping(size_t size, int& fl, int& sl) {
  fl = std::bit_width(size) - 1;
  sl = static_cast<int>((size >> (fl - kSlBits)) - kSlCount);
}
```

| 式 | 意味 |
| --- | --- |
| `fl = bit_width(size) - 1` | **最上位ビットの位置**（`floor(log2(size))`） |
| `size >> (fl - kSlBits)` | **上位の 6 ビット**（最上位の 1 ＋ 続く 5 ビット） |
| `- kSlCount` | **最上位の 1 を引いて**、`0..31` にする |

**確保のとき**は**要求の大きさを分類の下限に切り上げて**から探します（**探した空きが必ず、要求より大きい**ことを保証するため）。

```cpp
size_t RoundUp(size_t size) {
  int fl = std::bit_width(size) - 1;
  size_t round = (size_t{1} << (fl - kSlBits)) - 1;
  return size + round;
}
```

## 確保と解放

<svg class="fig flow" viewBox="0 0 1181 280" role="img" aria-label="TLSF：分類を計算し、ビットマップで空きを O(1) で見つけ、残りは分割して戻す"><defs><marker id="fl74959" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">TLSF：分類を計算し、ビットマップで空きを O(1) で見つけ、残りは分割して戻す</text><line x1="158.0" y1="148.0" x2="216.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74959)"/><text x="187.0" y="142.0" text-anchor="middle" style="font-size:12px">切り上げ</text><line x1="395.0" y1="148.0" x2="453.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74959)"/><text x="424.0" y="142.0" text-anchor="middle" style="font-size:12px">countr zero</text><line x1="627.2" y1="125.0" x2="743.3" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74959)"/><text x="685.2" y="100.0" text-anchor="middle" style="font-size:12px">取り出す</text><line x1="908.0" y1="64.0" x2="1015.5" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74959)"/><text x="961.8" y="58.0" text-anchor="middle" style="font-size:12px">分割</text><line x1="847.4" y1="87.0" x2="1027.1" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74959)"/><text x="937.2" y="142.0" text-anchor="middle" style="font-size:12px">残り</text><rect x="28.0" y="128.0" width="127" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="91.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">要求 300バイト</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="219.0" y="128.0" width="173" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="305.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">分類を計算 fl=8 sl=5</text><circle cx="221.0" cy="130.0" r="10" fill="#2ea043"/><text x="221.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="456.0" y="128.0" width="202" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="557.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ビットマップで 空きを探す</text><circle cx="458.0" cy="130.0" r="10" fill="#e5a828"/><text x="458.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="722.0" y="44.0" width="183" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="813.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">空きブロック 400バイト</text><circle cx="724.0" cy="46.0" r="10" fill="#e5484d"/><text x="724.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="1018.5" y="44.0" width="85" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="1061.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">貸す 300</text><circle cx="1020.5" cy="46.0" r="10" fill="#e5484d"/><text x="1020.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="969.0" y="212.0" width="184" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="1061.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">残り 100 → 空きに戻す</text><circle cx="971.0" cy="214.0" r="10" fill="#e5484d"/><text x="971.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

### 確保

| 手順 | 内容 |
| --- | --- |
| **1. 切り上げ** | 要求の大きさを**分類の境界に切り上げる** |
| **2. 分類を計算** | `(fl, sl)` を求める |
| **3. ビットマップで探す** | **`(fl, sl)` 以上**の空きのある分類を探す（<strong>O(1)</strong>） |
| **4. 取り出す** | その分類の**リストの先頭**を取り出す。リストが空になれば、**ビットを 0 に** |
| **5. 分割** | **大きすぎれば、要求の分だけ貸し**、**残りを空きに戻す**（その分類のリストに挿入） |

### 解放

| 手順 | 内容 |
| --- | --- |
| **1. 隣を調べる** | **前の物理ブロック**・**次の物理ブロック**が空きか（**境界タグ**） |
| **2. 結合** | 空きなら、**リストから外して、合体** |
| **3. 分類して挿入** | 合体後の大きさで、**`(fl, sl)` のリストに挿入**。**ビットを 1 に** |

**すべて、リストの先頭への挿入・取り出し**と**ビット演算**です。<strong>ループがなく、O(1)</strong> です。

### ブロックの構造（境界タグ）

```cpp
struct Block {
  Block* prev_physical;
  size_t size_and_flags;
  Block* next_free;
  Block* prev_free;
};
```

| メンバ | 意味 |
| --- | --- |
| **`prev_physical`** | **メモリ上の、1 つ前のブロック**（結合のため） |
| **`size_and_flags`** | **大きさ**と**自分と前のブロックが空きか**（下位ビットのフラグ） |
| **`next_free` / `prev_free`** | **空きの双方向リスト**（空きのときだけ有効） |

**使用中のブロックでは、`next_free` / `prev_free` の領域も、ユーザーのデータ**に使い、**ヘッダを小さく**します。

## 特徴

| 項目 | 内容 |
| --- | --- |
| **確保・解放の時間** | <strong>O(1)</strong>。**最悪も一定** |
| **断片化** | **小さい**（best-fit に近い選び方・結合あり）。**内部断片化は、SL の細かさで決まる**（SL = 32 なら、約 3% 以下） |
| **メモリのオーバーヘッド** | **ブロックごとに数十バイトのヘッダ**。**ビットマップ・リスト表**で数 KB |
| **スレッド** | **ロックなし**（1 スレッド専用）。**共有するなら、ロックで守る** |
| **領域** | **事前に確保した、1 つの大きな領域**をプールとして使う |

## 使いどころ

| 場面 | 理由 |
| --- | --- |
| **ゲーム機・組み込みの固定メモリ** | **決まった領域**の中で**汎用の確保**。**時間が読める** |
| **リアルタイムのオーディオ・描画** | **確保の時間が一定**で**カクつかない** |
| **アセット・ゲームの状態の置き場** | **大きさがバラバラ**で**個別に返す** |
| **GPU のメモリのサブ割り当て** | 大きなバッファの一部を貸す（オフセットの管理） |

## ライブラリ

| ライブラリ | 特徴 |
| --- | --- |
| **tlsf**（Matthew Conte の実装） | **単純な C の実装**。1 つの `.c` と `.h`。**領域を渡して使う** |
| **mimalloc / jemalloc / tcmalloc** | **サイズクラス ＋ スレッドキャッシュ**の、汎用の高速な `malloc`（TLSF ではない）。**普通のゲームには、こちらが手軽**（[malloc の置き換え](global-replace.md)） |
| **VMA**（Vulkan Memory Allocator）など | **GPU メモリ**の、TLSF 風の管理 |

```cpp
#include "tlsf.h"

alignas(16) static std::byte pool[16 * 1024 * 1024];
tlsf_t tlsf = tlsf_create_with_pool(pool, sizeof(pool));

void* p = tlsf_malloc(tlsf, 300);
tlsf_free(tlsf, p);
```

## よくあるミス

??? failure "要求の大きさを、切り上げずに分類で探す"
    **探した空きが要求より小さい**ことがあり、**メモリを壊します**。**分類の下限に切り上げてから探す**のが、TLSF の約束です。

??? failure "プールの外のポインタを、`free` する"
    **ヘッダを読みに行って、メモリが壊れます**。**どのアロケータのものか**を、管理します。

??? failure "複数のスレッドから、ロックなしで使う"
    **リストとビットマップが壊れます**。**スレッドごとに別の TLSF** にするか、**ロック**で守ります。

??? failure "小さな領域に、大きなヘッダの構造で使う"
    **ヘッダのオーバーヘッド**が、無視できなくなります。**小さな固定サイズ**は、**プール**のほうが向いています。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>確保・解放が必ず O(1)</strong>。<strong>最悪の時間が読める</strong>
    - [x] <strong>空きを大きさで 2 段階に分類</strong>（FL ＝ 2 のべき乗、SL ＝ その中の等分）。<strong>ビットマップ ＋ `countr_zero`</strong> で一瞬
    - [x] <strong>確保は、分類の下限に切り上げ</strong>、<strong>余りは分割して戻す</strong>。<strong>解放は隣と結合</strong>
    - [x] 向くのは<strong>リアルタイム・固定領域の汎用確保</strong>。<strong>実装はライブラリを使う</strong>

## 関連ページ

- [アロケータ（目次）](index.md)
- [フリーリストアロケータ](free-list.md)
- [スラブアロケータ](slab.md)
- [malloc の置き換え](global-replace.md)
- [計算量（基礎）](../../basics/big-o.md)

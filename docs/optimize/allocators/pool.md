---
title: プールアロケータ
tags:
  - 最適化
  - アロケータ
---

# プールアロケータ

**プールアロケータ**（pool allocator）は、同じ大きさのブロックを、あらかじめ並べておき、貸したり返したりするアロケータです。確保も解放も、数ナノ秒で、個別に返せます。断片化もしません。弾・敵・パーティクル・コンポーネントなど、同じ種類のものを、大量に作っては消す用途に、最も向いています（設計の考え方は [オブジェクトプール](../../design/patterns/object-pool.md)）。

!!! tip "ポイント"
    - <strong>ブロックの大きさが、すべて同じ</strong>。<strong>空きブロックを、リスト（フリーリスト）</strong>でつなぐ。
    - 確保 ＝ リストの先頭を取る、解放 ＝ 先頭に戻す（どちらも O(1)）。
    - 空きブロックの中に、「次の空き」のポインタを入れるので、追加のメモリがいらない。
    - 断片化しない。個別に返せる（リニアとの違い）。
    - 大きさが違うものは、置けない。種類ごとに、別のプール。
    - 満杯になったら、`nullptr` か、次のブロック群を足す。

!!! info "このページを読む前に"
    - [optimize/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [メモリ確保](../allocation.md)（メモリ確保が遅い理由）

## 仕組み

メモリを、**同じ大きさのブロック**に区切り、空きブロックを、リストでつなぎます。

<div class="anim" data-type="graph" data-label="プール：空きブロックのリストから、先頭を取る（確保）、先頭に戻す（解放）">
n h 空きリストの先頭 0 1 hit
n b0 ブロック0 1 0
n b1 ブロック1 2 0
n b2 ブロック2 3 0
l h b0 hit
l b0 b1
l b1 b2
---
n h 空きリストの先頭 0 1
n b0 ブロック0_（使用中） 1 0 new
n b1 ブロック1 2 0 hit
n b2 ブロック2 3 0
l h b1 hit
l b1 b2
---
n h 空きリストの先頭 0 1
n b0 ブロック0_（使用中） 1 0
n b1 ブロック1_（使用中） 2 0 new
n b2 ブロック2 3 0 hit
l h b2 hit
---
n h 空きリストの先頭 0 1
n b0 ブロック0_（返却） 1 0 hit
n b1 ブロック1_（使用中） 2 0
n b2 ブロック2 3 0
l h b0 hit
l b0 b2 hit
</div>

| 操作 | 内部の動き |
| --- | --- |
| 確保 | 空きリストの先頭ブロックを取り出し、先頭を次へ進める |
| 解放 | 返されたブロックを、空きリストの先頭に差し込む |
| コスト | どちらも、ポインタ数個の書き換え（O(1)） |

### 空きブロックを、リストにする（侵入型）

空いているブロックの中身は、誰も使っていません。その中に、「次の空きブロックへのポインタ」を書き込みます。リストのための、追加のメモリがいりません。

```text
空き：   [ next ─→ ][ next ─→ ][ next ─→ null ]
使用中： [ 中身（オブジェクト）...             ]
```

## 実装

```cpp
class PoolAllocator {
 public:
  PoolAllocator(size_t block_size, size_t block_count, size_t alignment = alignof(std::max_align_t))
      : block_size_(AlignUp(std::max(block_size, sizeof(FreeNode)), alignment)),
        block_count_(block_count) {
    memory_ = static_cast<std::byte*>(
        ::operator new(block_size_ * block_count_, std::align_val_t(alignment)));
    alignment_ = alignment;
    Reset();
  }

  ~PoolAllocator() { ::operator delete(memory_, std::align_val_t(alignment_)); }

  PoolAllocator(const PoolAllocator&) = delete;
  PoolAllocator& operator=(const PoolAllocator&) = delete;

  void* Allocate() {
    if (head_ == nullptr) return nullptr;
    FreeNode* node = head_;
    head_ = node->next;
    ++used_;
    return node;
  }

  void Deallocate(void* ptr) {
    FreeNode* node = static_cast<FreeNode*>(ptr);
    node->next = head_;
    head_ = node;
    --used_;
  }

  void Reset() {
    head_ = nullptr;
    for (size_t i = block_count_; i > 0; --i) {
      FreeNode* node = reinterpret_cast<FreeNode*>(memory_ + (i - 1) * block_size_);
      node->next = head_;
      head_ = node;
    }
    used_ = 0;
  }

  size_t Used() const { return used_; }

 private:
  struct FreeNode {
    FreeNode* next;
  };

  static size_t AlignUp(size_t v, size_t a) { return (v + a - 1) & ~(a - 1); }

  std::byte* memory_ = nullptr;
  FreeNode* head_ = nullptr;
  size_t block_size_;
  size_t block_count_;
  size_t alignment_ = 0;
  size_t used_ = 0;
};
```

| 点 | 説明 |
| --- | --- |
| **`block_size_`** | `FreeNode`（ポインタ 1 つ）以上にする。アライメントに切り上げ |
| `Reset()` | 全ブロックを、空きリストにつなぐ（最初に 1 回。後ろから前へ、順に差し込む） |
| `Allocate` | 先頭を取るだけ。満杯なら `nullptr` |
| `Deallocate` | 先頭に戻すだけ。自分のプールのブロックだけを渡す |
| `::operator new(size, align_val_t)` | アライメント指定の確保（C++17） |

### 型つきのプール

```cpp
template <typename T>
class ObjectPool {
 public:
  explicit ObjectPool(size_t count) : pool_(sizeof(T), count, alignof(T)) {}

  template <typename... Args>
  T* Create(Args&&... args) {
    void* memory = pool_.Allocate();
    return memory ? new (memory) T(std::forward<Args>(args)...) : nullptr;
  }

  void Destroy(T* object) {
    object->~T();
    pool_.Deallocate(object);
  }

 private:
  PoolAllocator pool_;
};

ObjectPool<Bullet> bullets(1024);
Bullet* b = bullets.Create(position, velocity);
bullets.Destroy(b);
```

型ごとに、別のプールを持つのが、基本です。`Create` で `placement new`、`Destroy` で、デストラクタを呼びます。

## インデックス版（ポインタの代わりに番号）

<strong>空きリストを、ポインタでなく、「ブロックの番号（32 ビット）」</strong>でつなぐ方法です。

| 項目 | ポインタ版 | インデックス版 |
| --- | --- | --- |
| 空きの目印 | 8 バイトのポインタ | 4 バイトの番号 |
| 最小のブロックサイズ | 8 バイト | 4 バイト |
| ハンドルに向く | — | 番号 ＋ 世代で、ハンドルにできる（[ハンドル](../../engine/handle.md)） |
| メモリの再配置 | ポインタが無効 | 番号なので、移動しても有効 |

```cpp
uint32_t Allocate() {
  if (free_head_ == kInvalid) return kInvalid;
  uint32_t index = free_head_;
  free_head_ = *reinterpret_cast<uint32_t*>(Block(index));
  return index;
}
```

ECS・ゲームオブジェクトの管理では、インデックス + 世代が、よく使われます（[ECS](../../design/patterns/ecs.md)）。

## 満杯になったとき

| 方法 | 説明 |
| --- | --- |
| **`nullptr` を返す** | 呼び出し側で、作れなかったときの処理（敵を出さない・弾を撃たない） |
| 古いものを、再利用する | 一番古い弾を、消して使う（リングバッファ的） |
| ブロック群を足す（チャンク） | プールを、リストで増やす。ポインタが動かないので安全 |
| assert | 容量が足りないことを、開発中に気づく |

チャンク方式は、1 つの大きなプールを、複数の小さなチャンクにして、足りなければ追加します。既存のブロックを動かさないので、ポインタが無効になりません。

## 使いどころ

| 場面 | 例 |
| --- | --- |
| **弾・パーティクル・エフェクト** | 短命で、大量 |
| 敵・NPC | 出現と消滅を繰り返す |
| ECS のコンポーネント | 型ごとに、プール |
| ノード・リンクリストの要素 | `std::list` の代わり |
| ネットワークのパケット・イベント | 同じ大きさのメッセージ |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| <strong>確保・解放が O(1)</strong>（数ナノ秒） | ブロックの大きさが、1 種類 |
| 断片化しない | 容量が固定（先に決める） |
| 個別に返せる | 使われないブロックも、メモリを占める |
| ロックフリー化もしやすい（[スレッド](thread-local.md)） | 二重解放に、気づきにくい（デバッグ時に検出） |
| 連続した領域で、キャッシュに優しい | |

## デバッグのための工夫

| 方法 | 説明 |
| --- | --- |
| **解放時に、特別な値で埋める** | `0xDD` など。解放後の使用に気づく |
| 二重解放の検出 | 空きリストに、すでに入っているかを調べる（デバッグだけ） |
| 範囲チェック | 渡されたポインタが、プールの範囲内で、ブロックの境界か確認 |
| 使用数・最大数 | 容量の見積もりに使う |

（[デバッグ用アロケータ](debug.md)）

## よくあるミス

??? failure "プールのブロックより、大きいオブジェクトを置く"
    `sizeof(T)` が、**ブロックサイズを超える**と、隣のブロックを壊します。`static_assert(sizeof(T) <= block_size)` で防ぎます。

??? failure "デストラクタを呼ばずに、`Deallocate` する"
    リソースを持つ型は、`~T()` を先に呼びます。

??? failure "二重に `Deallocate` する"
    空きリストが、循環して、同じブロックが、2 回貸し出されます。デバッグ時に、検出します。

??? failure "別のプールのポインタを、返す"
    別の大きさのブロックを、リストに混ぜてしまいます。どのプールのものか、確かめます。

??? failure "解放済みのブロックを、まだ使う"
    空きリストの `next` ポインタで、上書きされています。解放後は、触らない（ハンドルの世代で防ぐ）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>同じ大きさのブロックを、空きリスト（侵入型）でつなぐ</strong>
    - [x] 確保 ＝ 先頭を取る、解放 ＝ 先頭に戻す（O(1)）。断片化しない
    - [x] 型ごとに、別のプール。`placement new` ＋ 自分でデストラクタ
    - [x] ハンドルには、インデックス ＋ 世代。満杯の動きを、決めておく
    - [x] 向くのは弾・敵・パーティクルなど、大量に作っては消すもの

## 関連ページ

- [アロケータ（目次）](index.md)
- [オブジェクトプール（パターン）](../../design/patterns/object-pool.md)
- [スラブアロケータ](slab.md)
- [ハンドル](../../engine/handle.md)
- [スレッドとアロケータ](thread-local.md)

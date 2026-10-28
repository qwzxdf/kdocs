---
title: フレームアロケータ
tags:
  - 最適化
  - アロケータ
---

# フレームアロケータ

**フレームアロケータ**（frame allocator）は、1 フレームの間だけ使う一時データのための、[リニアアロケータ](linear.md)です。フレームの最初に `Reset()` して、そのフレーム内の確保は、すべて、ポインタを進めるだけで済ませます。解放を考えなくてよく、最速で、毎フレームのヒープ確保をなくせます（[毎フレームのヒープ確保を避ける](../frame-allocation.md)）。スクラッチ（作業用）メモリや、ダブルバッファも、このページで扱います。

!!! tip "ポイント"
    - <strong>フレームの頭で `Reset()`</strong>。<strong>そのフレームで確保したものは、フレームの終わりで、すべて無効</strong>。
    - 確保 ＝ ポインタを進めるだけ。`vector` を `reserve` するより、さらに速い。
    - 次のフレームにまたがって使うものは、置けない。寿命のルールを守る。
    - 別のスレッド（描画スレッド）が次のフレームで使うなら、ダブルバッファ（2 つを交互に）。
    - スレッドごとに、フレームアロケータを持てば、ロックなし。
    - デバッグ時は、Reset で、メモリを特定の値で埋めて、古いポインタの使用に気づく。

!!! info "このページを読む前に"
    - [optimize/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [メモリ確保](../allocation.md)（メモリ確保が遅い理由）

## 仕組み

<div class="anim" data-type="graph" data-label="フレームアロケータ：フレームの頭でリセットし、フレーム中は積むだけ">
n f1 フレーム_N 0 1 hit
n a1 一時データ 1 0 new
n b1 一時データ 2 0 new
l f1 a1 hit 確保
l f1 b1 hit 確保
---
n f1 フレーム_N_の終わり 0 1
n a1 一時データ 1 0 dim
n b1 一時データ 2 0 dim
---
n f2 フレーム_N+1_の頭 0 1 hit
n r Reset 1 1 new
n a2 一時データ 2 0 new
l f2 r hit 先頭に戻す
l r a2 hit 確保
</div>

| 時点 | 動き |
| --- | --- |
| **フレームの頭** | `Reset()`（`offset = 0`）。前のフレームのデータは、すべて無効 |
| フレーム中 | `Allocate`（ポインタを進めるだけ） |
| フレームの終わり | 何もしない（次のフレームの頭で、まとめて捨てる） |

## 実装

```cpp
class FrameAllocator {
 public:
  explicit FrameAllocator(size_t capacity)
      : buffer_(static_cast<std::byte*>(::operator new(capacity, std::align_val_t(64)))),
        capacity_(capacity) {}

  ~FrameAllocator() { ::operator delete(buffer_, std::align_val_t(64)); }

  void BeginFrame() {
    peak_ = std::max(peak_, offset_);
    offset_ = 0;
#ifdef _DEBUG
    std::memset(buffer_, 0xDD, capacity_);
#endif
  }

  void* Allocate(size_t size, size_t alignment = alignof(std::max_align_t)) {
    size_t aligned = (offset_ + alignment - 1) & ~(alignment - 1);
    if (aligned + size > capacity_) {
      assert(false && "frame allocator exhausted");
      return nullptr;
    }
    offset_ = aligned + size;
    return buffer_ + aligned;
  }

  template <typename T>
  T* AllocateArray(size_t count) {
    return static_cast<T*>(Allocate(sizeof(T) * count, alignof(T)));
  }

  size_t Peak() const { return peak_; }

 private:
  std::byte* buffer_;
  size_t capacity_;
  size_t offset_ = 0;
  size_t peak_ = 0;
};
```

| 点 | 説明 |
| --- | --- |
| **`BeginFrame()`** | `offset = 0`。最大使用量を記録 |
| デバッグ時の `memset(0xDD)` | 古いポインタを使うと、`0xDD` を読むので、バグに気づきやすい |
| `assert` | 容量不足を開発中に気づく |
| `Peak()` | 実際の最大使用量。容量を決める材料 |
| 64 バイト整列 | キャッシュラインに揃える |

### 使い方

```cpp
void Game::Frame() {
  frame_allocator_.BeginFrame();

  Enemy** nearby = frame_allocator_.AllocateArray<Enemy*>(256);
  size_t count = 0;
  for (Enemy& e : enemies_) {
    if (IsNear(e) && count < 256) nearby[count++] = &e;
  }

  Update(nearby, count);
  Render();
}
```

毎フレームの `std::vector` の代わりになります。確保は 1 回の `AllocateArray`、解放は不要です。

### std::pmr と組み合わせる

```cpp
std::pmr::monotonic_buffer_resource resource(buffer, capacity, std::pmr::null_memory_resource());

void Frame() {
  resource.release();
  std::pmr::vector<Enemy*> nearby(&resource);
  nearby.push_back(...);
}
```

`monotonic_buffer_resource` は、フレームアロケータの標準版です（`release()` で、先頭に戻す）。`std::pmr::vector` / `std::pmr::string` をそのまま、フレームアロケータに乗せられます（[STL との接続](stl-adapter.md)、[std::pmr](../../stl/memory/pmr.md)）。

## 寿命のルール

**フレームアロケータのデータは、そのフレームの中だけ**で使います。

| やってよい | やってはいけない |
| --- | --- |
| フレーム内の一時配列（衝突の候補・描画の並び替え） | 次のフレームまで、ポインタを持ち越す |
| 一時的な文字列・ログのバッファ | メンバ変数にポインタを保存する |
| フレーム内で完結する、作業用メモリ | フレームをまたぐ、コンテナの要素にする |

!!! warning "持ち越すと、次のフレームで壊れる"
    次のフレームの頭で、`Reset` されたメモリは、別のデータで上書きされます。持ち越したポインタを読むと、無関係なデータが見えます（クラッシュしないので、見つけにくいバグ）。デバッグ時の `0xDD` 埋めで、気づきやすくします。

フレームをまたぐデータは、通常のコンテナか、[プール](pool.md)に置きます。

## ダブルバッファ

**別のスレッド**（描画スレッド・ジョブ）が前のフレームで作ったデータを次のフレームで使うときは、すぐに `Reset` できません。2 つのアロケータを交互に使います。

<div class="anim" data-type="graph" data-label="ダブルバッファ：フレームごとに、使うアロケータを交互に切り替える">
n a アロケータ_A 0 0 hit
n b アロケータ_B 0 2
n u1 フレーム_N_で書く 1 0 new
l a u1 hit 確保
---
n a アロケータ_A_（描画が読む） 0 0 dim
n b アロケータ_B 0 2 hit
n u1 フレーム_N_のデータ 1 0 dim
n u2 フレーム_N+1_で書く 1 2 new
n r 描画スレッド 2 0 new
l b u2 hit 確保
l u1 r hit 読む
---
n a アロケータ_A_（Reset） 0 0 hit
n b アロケータ_B_（描画が読む） 0 2 dim
n u3 フレーム_N+2_で書く 1 0 new
l a u3 hit 確保
</div>

```cpp
class DoubleBufferedFrameAllocator {
 public:
  void BeginFrame() {
    index_ ^= 1;
    allocators_[index_].BeginFrame();
  }
  FrameAllocator& Current() { return allocators_[index_]; }

 private:
  FrameAllocator allocators_[2];
  int index_ = 0;
};
```

| 項目 | 説明 |
| --- | --- |
| 書く側 | 今のフレームの側（`Current()`）に確保 |
| 読む側（描画・ジョブ） | 前のフレームの側を読むだけ |
| 切り替え | フレームの頭で、`index` を反転し、その側を `Reset`（前々回のデータは、もう使われない） |
| N 重バッファ | GPU のフレームが数フレーム遅れるときは、3 つ以上 |

## スクラッチ（作業用）メモリ

**関数の中だけで使う、一時的な作業領域**をフレームアロケータ（または[スタック](stack.md)）から借ります。

```cpp
void FindPath(const Graph& graph, int start, int goal, FrameAllocator& scratch) {
  auto* open = scratch.AllocateArray<Node>(graph.node_count);
  auto* closed = scratch.AllocateArray<bool>(graph.node_count);
}
```

| 方法 | 説明 |
| --- | --- |
| フレームアロケータから | フレームの終わりで、まとめて捨てる（関数ごとの解放は不要） |
| [スタックアロケータ](stack.md)から | 関数の終わりで、マーカーまで戻す（フレーム内でも、早く返せる） |

## スレッドごとのフレームアロケータ

**ジョブシステム**で、複数のスレッドが同時にフレームアロケータを使うと、ロックが必要になります。スレッドごとに、別のフレームアロケータを持てば、ロックなしで済みます（[スレッドとアロケータ](thread-local.md)）。

```cpp
thread_local FrameAllocator t_frame_allocator(8 * 1024 * 1024);
```

| 注意 | 説明 |
| --- | --- |
| `BeginFrame` を全スレッドで呼ぶ | 各スレッドの、アロケータをリセット |
| ほかのスレッドのデータを読む | そのスレッドのフレームが終わるまで有効 |
| 容量 | スレッド数 × 容量のメモリを使う |

## 容量の決め方

| 手順 | 説明 |
| --- | --- |
| **1. 大きめに確保して動かす** | たとえば 16MB |
| 2. `Peak()` を記録 | 最も重いシーンで、最大使用量を測る |
| 3. 余裕を持たせる | 最大使用量の 1.5〜2 倍 |
| 4. 画面に表示 | 使用量をデバッグ画面に出す（[計測](../measure.md)） |
| 5. 超えたら assert | 開発中に気づけるように |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **確保が最速**（ポインタを進めるだけ） | フレームをまたげない |
| 解放が不要（Reset だけ） | デストラクタが呼ばれない |
| ヒープ確保をゼロにできる | 容量を先に決める |
| 連続するのでキャッシュに優しい | 持ち越しのバグが見つけにくい |

## よくあるミス

??? failure "フレームアロケータのポインタをメンバ変数に保存する"
    **次のフレームで、別のデータに上書き**されます。フレーム内だけで使います。

??? failure "`std::string` / `std::vector` をそのまま置く"
    中身の確保がヒープで、リークします。`pmr` のコンテナか、PODだけを置きます。

??? failure "描画スレッドが次のフレームでも読むのに、すぐに Reset する"
    ダブルバッファにします。

??? failure "デバッグ時に Reset 後のデータが前のまま残っていて、バグに気づかない"
    `0xDD` などで、埋めて、古いポインタを使うと、すぐ分かるようにします。

??? failure "容量を小さく決めて、特定のシーンだけ落ちる"
    最も重いシーンで測る。`assert` で、開発中に気づきます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フレームの頭で `Reset`。フレーム内の確保は、ポインタを進めるだけ
    - [x] フレームをまたぐデータは置かない。デバッグ時は、Reset でメモリを埋める
    - [x] 別スレッドが次のフレームで読むなら、ダブルバッファ。スレッドごとに持てば、ロックなし
    - [x] `std::pmr::monotonic_buffer_resource` と、組み合わせられる
    - [x] `Peak()` で最大使用量を測って、容量を決める

## 関連ページ

- [アロケータ（目次）](index.md)
- [リニアアロケータ](linear.md)
- [スタックアロケータ](stack.md)
- [毎フレームのヒープ確保を避ける](../frame-allocation.md)
- [フレーム時間の設計](../frame-budget.md)
- [std::pmr](../../stl/memory/pmr.md)

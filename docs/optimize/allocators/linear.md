---
title: リニアアロケータ（アリーナ）
tags:
  - 最適化
  - アロケータ
---

# リニアアロケータ（アリーナ）

**リニアアロケータ**（linear allocator）は、確保するたびにポインタを前に進めるだけのアロケータです。バンプアロケータ（bump allocator）、アリーナ（arena）、モノトニックアロケータとも呼ばれます。個別には返せません。使い終わったらまとめて先頭に戻します。最も単純で最も速いアロケータです。

!!! tip "ポイント"
    - <strong>確保 ＝ ポインタを進めるだけ</strong>（数ナノ秒）。<strong>解放 ＝ なし</strong>（個別には返せない）。
    - `Reset()` でまとめて、先頭に戻す。デストラクタは呼ばれない。
    - 向く用途：フレームの一時データ、ロード中の一時データ、パース結果など まとめて捨てられるもの。
    - メモリが連続して並ぶので、キャッシュに優しい。断片化しない。
    - アライメントを確保ごとに合わせる。
    - 標準では`std::pmr::monotonic_buffer_resource`が、同じもの（[std::pmr](../../stl/memory/pmr.md)）。

!!! info "このページを読む前に"
    - [optimize/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [メモリ確保](../allocation.md)（メモリ確保が遅い理由）

## 仕組み

```text
[ A ][ B ][ C ]                  ← 空き →
              ↑ offset（次に貸す位置）
```

<div class="anim" data-type="graph" data-label="リニアアロケータ：確保するたびに offset が進み、Reset で先頭に戻る">
n buf バッファ_offset=0 0 1 hit
---
n buf バッファ_offset=32 0 1
n a A_（32バイト） 1 0 new
l buf a hit 確保
---
n buf バッファ_offset=80 0 1
n a A_（32バイト） 1 0
n b B_（48バイト） 2 0 new
l buf b hit 確保
---
n buf バッファ_offset=96 0 1
n a A 1 0
n b B 2 0
n c C_（16バイト） 3 0 new
l buf c hit 確保
---
n buf バッファ_offset=0 0 1 hit
n a A 1 0 gone
n b B 2 0 gone
n c C 3 0 gone
l buf a gone Reset
</div>

| 操作 | 内部の動き | コスト |
| --- | --- | --- |
| **`Allocate(size, align)`** | `offset` を境界に合わせ `size` ぶん進める | 数ナノ秒 |
| `Reset()` | `offset = 0` に戻す | 一瞬（個数に依らない） |
| 個別の解放 | できない | — |

## 実装

```cpp
#include <cstddef>
#include <cstdint>
#include <new>
#include <utility>

class LinearAllocator {
 public:
  LinearAllocator(void* buffer, size_t capacity)
      : begin_(static_cast<std::byte*>(buffer)), capacity_(capacity) {}

  void* Allocate(size_t size, size_t alignment = alignof(std::max_align_t)) {
    uintptr_t base = reinterpret_cast<uintptr_t>(begin_);
    uintptr_t current = base + offset_;
    uintptr_t aligned = (current + alignment - 1) & ~(alignment - 1);
    size_t new_offset = static_cast<size_t>(aligned - base) + size;
    if (new_offset > capacity_) {
      return nullptr;
    }
    offset_ = new_offset;
    return reinterpret_cast<void*>(aligned);
  }

  template <typename T, typename... Args>
  T* New(Args&&... args) {
    void* memory = Allocate(sizeof(T), alignof(T));
    return memory ? new (memory) T(std::forward<Args>(args)...) : nullptr;
  }

  void Reset() { offset_ = 0; }
  size_t Used() const { return offset_; }
  size_t Capacity() const { return capacity_; }

 private:
  std::byte* begin_;
  size_t capacity_;
  size_t offset_ = 0;
};
```

| 行 | 意味 |
| --- | --- |
| `current + alignment - 1) & ~(alignment - 1)` | **`current` を `alignment` の倍数に切り上げる**（`alignment` は 2 のべき乗） |
| `new_offset > capacity_` | 足りなければ、`nullptr` |
| `offset_ = new_offset` | ポインタを進める（これだけで確保が終わる） |
| `New<T>` | `placement new` でオブジェクトを作る |
| `Reset()` | 全部、まとめて捨てる（デストラクタは呼ばれない） |

### 使い方

```cpp
alignas(64) static std::byte buffer[1 << 20];
LinearAllocator arena(buffer, sizeof(buffer));

Enemy* e = arena.New<Enemy>(position);
auto* temp = static_cast<float*>(arena.Allocate(sizeof(float) * 256, alignof(float)));

arena.Reset();
```

バッファは静的な配列でも起動時に 1 回 `new` したメモリでも、`VirtualAlloc` したメモリでも構いません。

## デストラクタ

**`Reset` はメモリを戻すだけ**で、デストラクタを呼びません。

| 置く型 | 扱い |
| --- | --- |
| トリビアルな型（`int`、`float`、POD の構造体、`Vector3`） | そのままでよい（デストラクタが何もしない） |
| リソースを持つ型（`std::vector`、`std::string`、ファイルハンドル） | `Reset` の前に自分で `~T()` を呼ぶ。または、置かない |
| `std::pmr` コンテナ | アリーナに乗せる場合、コンテナの中身の確保はアリーナから。`vector` 自体のデストラクタは解放を何もしないので、呼んでも安全 |

!!! warning "std::string や std::vector を、そのまま置かない"
    `arena.New<std::string>()` で作った文字列は中身を `new` で確保します。`Reset` してもその `new` した分はリークします。アリーナで使うなら `std::pmr::string`（アリーナから確保）にします。

## 満杯になったとき

| 方法 | 説明 |
| --- | --- |
| **`nullptr` を返す** | 呼び出し側で、確認する（`assert` で開発中に気づく） |
| 例外を投げる | `std::bad_alloc`（ゲームでは、あまり使わない） |
| assert して止める | 容量の見積もりが足りないので、開発中に気づいて増やす |
| 次のブロックを足す | ブロックのリストにして、足りなければ新しいブロックを確保（`monotonic_buffer_resource` の動き） |
| 最大使用量を記録 | 本番の容量を決める材料 |

```cpp
void* Allocate(size_t size, size_t alignment) {
  ...
  if (new_offset > capacity_) {
    assert(false && "arena exhausted");
    return nullptr;
  }
  ...
}
```

## 使いどころ

| 場面 | 例 |
| --- | --- |
| **フレームの一時データ** | 描画命令・衝突の候補・一時的な配列（[フレーム](frame.md)） |
| ロード中の一時データ | ファイルの解析結果・変換中の頂点（ロード後に `Reset`） |
| パーサーの木 | JSON・シーンファイルの解析（解析が終わったらまとめて捨てる） |
| ステージごとのデータ | ステージを出るときにまとめて捨てる |
| スコープ内の一時データ | 関数の中だけの一時配列 |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **確保が最速**（数ナノ秒） | 個別に返せない |
| 解放も一瞬（`Reset`） | デストラクタが呼ばれない |
| 断片化しない・連続している | 寿命が違うものを混ぜられない |
| 実装が単純（バグが少ない） | 容量を先に決める必要がある |
| スレッドごとに持てば、ロック不要 | 共有するならロックが必要（[スレッド](thread-local.md)） |

## よくあるミス

??? failure "寿命が違うものを同じアリーナに入れる"
    **1 つだけ長生きしたい**データがあると、アリーナ全体を捨てられません。寿命ごとに別のアリーナにします。

??? failure "`Reset` の後に古いポインタを使う"
    すべて無効です。デバッグ時は `Reset` でメモリを特定の値で埋めると気づきやすい（[デバッグ用アロケータ](debug.md)）。

??? failure "アライメントを考えない"
    `float4`・SIMD の型は、16 バイト境界が必要です。`Allocate(size, alignof(T))` と型のアライメントを渡します。

??? failure "`std::string` / `std::vector` をアリーナに置いて、リークする"
    `pmr` のコンテナを使うかトリビアルな型だけを置きます。

??? failure "容量を小さく決めすぎて、`nullptr` で落ちる"
    最大使用量を計測して、余裕を持たせて決めます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>確保 ＝ ポインタを進めるだけ</strong>。`Reset` でまとめて捨てる
    - [x] 個別には返せない。デストラクタは呼ばれない（トリビアルな型 or `pmr`）
    - [x] アライメントを確保ごとに合わせる
    - [x] 向くのはフレーム・ロード・パースなど まとめて捨てられるもの
    - [x] 寿命ごとに別のアリーナ。最大使用量を測って容量を決める

## 関連ページ

- [アロケータ（目次）](index.md)
- [スタックアロケータ](stack.md)
- [フレームアロケータ](frame.md)
- [STL との接続](stl-adapter.md)
- [std::pmr](../../stl/memory/pmr.md)
- [毎フレームのヒープ確保を避ける](../frame-allocation.md)

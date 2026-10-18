---
title: スタックアロケータ
tags:
  - 最適化
  - アロケータ
---

# スタックアロケータ

**スタックアロケータ**（stack allocator）は、[リニアアロケータ](linear.md)に <strong>「ここまで戻す」という目印（マーカー）</strong>を足したものです。**後から確保したものから先に返す**（**LIFO**：後入れ先出し）という順番を守れば、**途中まで巻き戻せます**。**関数の中の一時データ**や**入れ子になった作業**に向きます。

!!! tip "ポイント"
    - <strong>リニア ＋ マーカー（その時点の位置）</strong>。<strong>`Rewind(marker)` でその位置まで戻す</strong>。
    - <strong>解放は確保の逆順だけ</strong>（LIFO）。<strong>順番を破ると壊れる</strong>。
    - <strong>スコープ（`{ }`）に合わせて、自動で巻き戻す</strong>（RAII）と安全。
    - <strong>両端から使う（ダブルエンド）</strong>と <strong>寿命の違う 2 種類を 1 つのバッファ</strong>に入れられる。
    - 確保はリニアと同じく<strong>最速</strong>。

## 仕組み

```text
確保：  A → B → C
        [ A ][ B ][ C ]
                     ↑ top
マーカー保存：  marker_B = B の確保前の位置
巻き戻し：  Rewind(marker_B)   → B・C を、まとめて捨てる
        [ A ]
            ↑ top
```

<div class="anim" data-type="graph" data-label="スタックアロケータ：マーカーまで巻き戻して、その後の確保を、まとめて捨てる">
n a A 0 1 hit
---
n a A 0 1
n m マーカー保存 1 0 new
n b B 1 1 new
l a b hit 確保
---
n a A 0 1
n m マーカー保存 1 0
n b B 1 1
n c C 2 1 new
l b c hit 確保
---
n a A 0 1 hit
n m マーカー保存 1 0 hit
n b B 1 1 gone
n c C 2 1 gone
l m b gone Rewind
</div>

## 実装

```cpp
class StackAllocator {
 public:
  using Marker = size_t;

  StackAllocator(void* buffer, size_t capacity)
      : begin_(static_cast<std::byte*>(buffer)), capacity_(capacity) {}

  void* Allocate(size_t size, size_t alignment = alignof(std::max_align_t)) {
    uintptr_t base = reinterpret_cast<uintptr_t>(begin_);
    uintptr_t aligned = (base + top_ + alignment - 1) & ~(alignment - 1);
    size_t new_top = static_cast<size_t>(aligned - base) + size;
    if (new_top > capacity_) return nullptr;
    top_ = new_top;
    return reinterpret_cast<void*>(aligned);
  }

  Marker GetMarker() const { return top_; }

  void Rewind(Marker marker) {
    assert(marker <= top_);
    top_ = marker;
  }

  void Reset() { top_ = 0; }

 private:
  std::byte* begin_;
  size_t capacity_;
  size_t top_ = 0;
};
```

| 関数 | 意味 |
| --- | --- |
| **`GetMarker()`** | **今の位置を覚える**（巻き戻し先） |
| **`Rewind(marker)`** | **そのマーカーまで、`top` を戻す**。それ以後に確保したものは**すべて無効** |
| `assert(marker <= top_)` | **未来のマーカーには戻れない**（順番を破った） |

### スコープで自動的に巻き戻す（RAII）

```cpp
class ScopedStack {
 public:
  explicit ScopedStack(StackAllocator& allocator)
      : allocator_(allocator), marker_(allocator.GetMarker()) {}
  ~ScopedStack() { allocator_.Rewind(marker_); }

  ScopedStack(const ScopedStack&) = delete;
  ScopedStack& operator=(const ScopedStack&) = delete;

 private:
  StackAllocator& allocator_;
  StackAllocator::Marker marker_;
};

void Process(StackAllocator& stack) {
  ScopedStack scope(stack);
  auto* temp = static_cast<int*>(stack.Allocate(sizeof(int) * 100, alignof(int)));
}
```

**関数を出る（`}` で閉じる）と自動で、元の位置に戻ります**。**早期 `return` や例外でも巻き戻される**ので、**戻し忘れがありません**（[RAII](../../design/patterns/raii.md)）。

## 解放の順番（LIFO）

**後から確保したものを先に返す**必要があります。

| 順番 | 結果 |
| --- | --- |
| **A → B → C と確保、C → B → A と解放** | **OK**（スコープの入れ子と同じ） |
| **A → B → C と確保、A を先に返す** | **NG**。B・C が巻き込まれて消える |
| **`Rewind` は 1 つのマーカーで、まとめて** | **OK**（途中のものを個別に返さなくてよい） |

**関数呼び出しの入れ子**と同じ形（スコープ）で使えば、**自然に LIFO**になります。

## ダブルエンド スタック

**バッファの両端から**、中央に向かって確保します。

```text
[ 下から →  ──────  空き  ──────  ← 上から ]
  [A][B]                           [Y][X]
```

<svg class="fig" viewBox="0 0 620 130" role="img" aria-label="ダブルエンド スタック">
<rect x="20" y="40" width="580" height="36" fill="none" stroke="currentColor" stroke-width="2"/>
<rect x="20" y="40" width="70" height="36" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="35" y="63">A</text>
<rect x="90" y="40" width="90" height="36" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="115" y="63">B</text>
<rect x="470" y="40" width="70" height="36" fill="rgba(229,170,40,0.5)" stroke="currentColor"/><text x="495" y="63">Y</text>
<rect x="540" y="40" width="60" height="36" fill="rgba(229,170,40,0.5)" stroke="currentColor"/><text x="560" y="63">X</text>
<text x="20" y="25" class="fig-title">下から（長く使う：レベルのデータ）</text><text x="360" y="25" class="fig-title">上から（短く使う：一時データ）</text>
<text x="20" y="105">真ん中で、ぶつからなければ OK。使い方に合わせて、境界が動く</text>
</svg>

| 端 | 使い方 |
| --- | --- |
| **下の端** | **長生きするデータ**（レベルのデータ） |
| **上の端** | **短命な一時データ**（毎フレーム） |

**2 種類のデータが柔軟に容量を分け合える**（片方が大きいときは、もう片方が小さく）ので**固定の分割より無駄がありません**。

```cpp
void* AllocateTop(size_t size, size_t alignment) {
  uintptr_t end = reinterpret_cast<uintptr_t>(begin_) + top_end_;
  uintptr_t aligned = (end - size) & ~(alignment - 1);
  size_t new_top_end = static_cast<size_t>(aligned - reinterpret_cast<uintptr_t>(begin_));
  if (new_top_end < bottom_) return nullptr;
  top_end_ = new_top_end;
  return reinterpret_cast<void*>(aligned);
}
```

## 使いどころ

| 場面 | 例 |
| --- | --- |
| **関数の中の一時配列** | 経路探索の途中の作業メモリ（関数の出口で巻き戻し） |
| **入れ子の処理** | 再帰・階層の処理で、各階層ごとに一時データ |
| **ステージの階層ロード** | ゲーム全体 → ステージ → エリア。**出るたびに巻き戻す** |
| **ダブルエンド** | 下：レベルのデータ、上：一時データ |

## リニアとの違い

| | リニア | スタック |
| --- | --- | --- |
| **一括の解放** | `Reset()`（全部） | `Reset()`（全部） |
| **部分的な解放** | **できない** | **マーカーまで巻き戻せる** |
| **順番の制約** | なし | **LIFO を守る** |
| **使いどころ** | フレーム・ロード全体 | **スコープごとの一時データ** |

## よくあるミス

??? failure "LIFO を破って、途中のものを返す"
    **後のものが巻き込まれて**消えます。**マーカーまでまとめて戻す**使い方にします。

??? failure "マーカーを取った後に `Reset()` してから、古いマーカーに `Rewind` する"
    **未来のマーカー**は無効です。`assert` で気づけるようにします。

??? failure "`ScopedStack` を一時オブジェクトとして書く（変数名なし）"
    `ScopedStack(stack);` は**すぐに破棄**されて、巻き戻しが一瞬で終わります。**変数名をつけます**（`ScopedStack scope(stack);`）。

??? failure "巻き戻した後のポインタを使う"
    **すべて無効**です。巻き戻し以前に確保したものだけが、有効です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>リニア ＋ マーカー</strong>。<strong>`Rewind(marker)` で途中まで戻せる</strong>
    - [x] <strong>解放は確保の逆順（LIFO）</strong>。<strong>スコープ（RAII）で自動的に巻き戻す</strong>
    - [x] <strong>ダブルエンド</strong>で、<strong>長命と短命の 2 種類</strong>を 1 つのバッファに
    - [x] <strong>デストラクタは呼ばれない</strong>（リニアと同じ）

## 関連ページ

- [アロケータ（目次）](index.md)
- [リニアアロケータ](linear.md)
- [フレームアロケータ](frame.md)
- [RAII](../../design/patterns/raii.md)

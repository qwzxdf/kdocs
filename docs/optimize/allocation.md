---
title: メモリ確保
tags:
  - 最適化
---

# メモリ確保

`new`、`malloc`、そして `std::vector` や `std::string` が中で行うメモリの確保は、**1 回が遅く、かかる時間も一定ではありません**。ヒープ（自由に使えるメモリ領域）の中から、空いている場所を**探して**、管理情報を更新するためです。1 回は数十〜数百ナノ秒ですが、**毎フレーム何千回も呼ぶ**と、数ミリ秒になります。しかもヒープの状態によって、たまに**とても遅い確保**が起きるので、**カクつき**の原因になります。このページはメモリ確保を**減らす・まとめる・避ける**方法をまとめます（仕組みは [アロケータ](../stl/memory/allocator.md)、[std::pmr](../stl/memory/pmr.md) を見てください）。

!!! tip "ポイント"
    - <strong>毎フレームの `new` / `vector` の作成を、やめる。</strong>使い回す。
    - `vector` は、<strong>`reserve` で先に容量を確保</strong>する。`clear()` しても容量は残るので使い回せる。
    - 作っては消すものは<strong>オブジェクトプール</strong>、フレームごとの一時データは<strong>フレーム用アリーナ</strong>。
    - 小さくて、大きさが決まっているものは<strong>スタック</strong>（`std::array`、ローカル変数）に置く。
    - 確保の回数は、<strong>プロファイラーか自作のカウンター</strong>で数える。

## なぜ遅いのか

<svg class="fig flow" viewBox="0 0 753 112" role="img" aria-label="new は、空きを探して、管理情報を更新する"><defs><marker id="fl84266" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">new は、空きを探して、管理情報を更新する</text><line x1="126.0" y1="64.0" x2="184.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl84266)"/><line x1="308.0" y1="64.0" x2="366.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl84266)"/><text x="337.0" y="58.0" text-anchor="middle" style="font-size:12px">断片化で遅い</text><line x1="518.0" y1="64.0" x2="576.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl84266)"/><text x="547.0" y="58.0" text-anchor="middle" style="font-size:12px">ロックで待たされる</text><rect x="28.0" y="44.0" width="95" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="75.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">new Enemy</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="187.0" y="44.0" width="118" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="246.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">① 空きを探す</text><circle cx="189.0" cy="46.0" r="10" fill="#2ea043"/><text x="189.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="369.0" y="44.0" width="146" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="442.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">② 管理情報を更新</text><circle cx="371.0" cy="46.0" r="10" fill="#e5a828"/><text x="371.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="579.0" y="44.0" width="146" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="652.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">③ コンストラクタ</text><circle cx="581.0" cy="46.0" r="10" fill="#e5484d"/><text x="581.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

| 問題 | 説明 |
| --- | --- |
| **探す時間が一定でない** | 空きが小さく分かれている（断片化）と、探すのに時間がかかる |
| **ロックの待ち** | 標準のヒープは、複数スレッドで共有されるので、同時に確保するとロックで待つ |
| **キャッシュに優しくない** | 確保した場所は、あちこちに散らばる（[メモリとキャッシュ](memory-cache.md)） |
| **解放も遅い** | `delete` も管理情報を更新する。まとめて大量に解放すると、カクつく |
| **断片化** | 確保と解放を繰り返すと、使えない細かい空きが増える |

## 1. 確保を減らす

### vector の reserve

```cpp
// 遅い：push_back のたびに、容量が足りなくなると再確保（引っ越し）
std::vector<Bullet> bullets;
for (int i = 0; i < 1000; ++i) {
  bullets.push_back(MakeBullet());      // 容量 1, 2, 4, 8, ... と、何度も確保し直す
}

// 速い：先に容量を決めて、1 回だけ確保する
std::vector<Bullet> bullets;
bullets.reserve(1000);
for (int i = 0; i < 1000; ++i) {
  bullets.push_back(MakeBullet());
}
```

詳しくは [vector の再確保](../stl/containers/vector.md#realloc) を見てください。

### 作り直さずに使い回す

```cpp
// 遅い：毎フレーム、vector を作って、捨てる
void Update() {
  std::vector<int> nearby;              // 毎フレーム、確保と解放
  FindNearby(nearby);
}

// 速い：メンバに持つ。clear() は容量を残す（解放しない）
class Scene {
  void Update() {
    nearby_.clear();                    // 要素だけ消す。メモリはそのまま
    FindNearby(nearby_);
  }
  std::vector<int> nearby_;
};
```

| 使い回せるもの | 方法 |
| --- | --- |
| `std::vector` | メンバに持って `clear()`。容量が残る |
| `std::string` | 同上。`clear()` で、容量が残る |
| `std::unordered_map` | `clear()`（バケットは残る）。ただし、ノードは解放される |
| 一時的なバッファ | `thread_local` や、メンバの作業用バッファ |

### 文字列の連結

| 遅い | 速い |
| --- | --- |
| `s = a + b + c;`（一時オブジェクトが何度も作られる） | `s.reserve(...)` してから `+=`、または `std::format` / `std::format_to` |
| ループで `s += ...`（再確保を繰り返す） | 先に `reserve` する |
| 毎フレーム `std::to_string` で文字列を作る | `std::format_to` で、使い回すバッファに書く、または `std::to_chars` |

## 2. まとめて確保する

### オブジェクトプール

**作っては消すもの**（弾、パーティクル、エフェクト）を、あらかじめ**まとめて確保しておき、使い回す**方法です。

<div class="anim" data-label="オブジェクトプール：確保も解放もしない">
_ _ _ _ # 最初に、4 個ぶんの場所を用意しておく
+弾1 _ _ _ # 借りる：空きを使う（新しく確保しない）
弾1 +弾2 _ _ # もう 1 つ借りる
x弾1 弾2 _ _ # 弾1 が役目を終えた
_ 弾2 _ _ # 返す：解放はせず、空きに戻る
+弾3 弾2 _ _ # 次は、空いた場所を再利用する
</div>

詳しくは [オブジェクトプール](../design/patterns/object-pool.md) を見てください。

### フレーム用アリーナ（積むだけの確保）

**1 フレームの間だけ使う一時データ**は、<strong>積むだけの領域（アリーナ）</strong>から取り、**フレームの最後に一括で解放**します。確保が**ポインタを進めるだけ**なので、とても速く、解放も一瞬です。

```cpp
#include <cstddef>
#include <memory_resource>
#include <vector>

class FrameMemory {
 public:
  std::pmr::memory_resource* resource() { return &pool_; }
  void NextFrame() { pool_.release(); }       // 一括で返す

 private:
  std::byte buffer_[256 * 1024];               // 1 フレームで使う領域（256 KB）
  std::pmr::monotonic_buffer_resource pool_{buffer_, sizeof(buffer_)};
};

void Update(FrameMemory& frame) {
  std::pmr::vector<Hit> hits(frame.resource());   // このフレームだけの一時データ
  CollectHits(hits);
}   // hits を破棄したあとに、frame.NextFrame() を呼ぶ
```

詳しくは [std::pmr](../stl/memory/pmr.md) を見てください。

### 起動時やロード時に、まとめて確保する

| 方法 | 説明 |
| --- | --- |
| **ステージの読み込み時に、必要な量を計算して、1 回で確保** | ゲーム中の確保がなくなる |
| **レベル用のアリーナ** | ステージの間だけ使うものを積んで、ステージ終了時に一括解放 |
| **固定のサイズの配列**（`std::array`、上限を決める） | 「敵は最大 256 体」と決めて、最初に確保 |

## 3. スタックを使う

**スタック**（ローカル変数の領域）は、確保が**一瞬**（スタック ポインタを動かすだけ）で、解放も自動です。

| 方法 | 説明 |
| --- | --- |
| **ローカル変数 / `std::array`** | 大きさが決まっている小さなものは、スタックに |
| **小さな配列の最適化**（SSO、small vector） | `std::string` は短い文字列を中に持つ（確保なし）。自作や `boost::small_vector` で、同じことができる |
| **`alloca`** | スタックから、動的な大きさを確保（非標準・危険）。基本使わない |
| **注意：スタックは小さい**（Windows で約 1 MB） | 大きな配列はスタックに置かない（スタック オーバーフロー） |

```cpp
// 確保なし：最大 16 個までなら、スタック上の配列で足りる
std::array<Hit, 16> hits;
std::size_t count = 0;
for (auto& e : enemies) {
  if (count < hits.size() && Overlaps(e, player)) {
    hits[count++] = {e.id};
  }
}
```

## 4. 確保のしかたを選ぶ

| 方法 | 確保の速さ | 解放 | 向いている場面 |
| --- | --- | --- | --- |
| **`new` / `malloc`** | 遅い（探す・ロック） | 1 つずつ | 長生きする、数の少ないもの |
| **`reserve` 済みの `vector`** | 追加は速い | `clear()` で容量が残る | 数が変わるリスト |
| **オブジェクトプール** | 速い（空きを返すだけ） | 返すだけ（解放しない） | 作っては消す、同じ種類のもの |
| **フレーム用アリーナ** | **最速**（ポインタを進める） | **一括** | 1 フレームだけの一時データ |
| **スタック** | **最速** | 自動 | 小さくて、大きさが決まっているもの |
| **グローバル アロケータの差し替え**（mimalloc、jemalloc） | 速い・並列に強い | 1 つずつ | 全体の確保をまとめて速くしたい |

### グローバルの確保を、速いものに替える

コードを変えずに、**`new` / `malloc` 全体を、速いアロケータに差し替える**方法もあります。

| ライブラリ | 特徴 |
| --- | --- |
| **mimalloc**（Microsoft） | 速く、小さい。Windows で使いやすい。vcpkg: `mimalloc` |
| **jemalloc** / **tcmalloc** | 並列に強い。Linux で多い |
| **Tracy のメモリ追跡** | 確保の場所と回数を可視化できる |

## 確保の回数を数える

直す前に**どこで何回確保されているか**を知ります。

```cpp
// グローバルの new を差し替えて、回数と大きさを数える（デバッグ用）
inline std::atomic<std::size_t> g_alloc_count = 0;
inline std::atomic<std::size_t> g_alloc_bytes = 0;

void* operator new(std::size_t size) {
  ++g_alloc_count;
  g_alloc_bytes += size;
  if (void* p = std::malloc(size)) return p;
  throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }

// 1 フレームの前後で、差を見る
std::size_t before = g_alloc_count;
Update();
std::println("このフレームの確保: {} 回", g_alloc_count - before);
```

**毎フレームの確保が 0 回**（またはごく少数）になるのが目標です。Visual Studio の「メモリ使用量」プロファイラーや Tracy でも、確保の場所を追えます（[計測](measure.md)）。

## ゲームでの使いどころ

| 場面 | 直し方 |
| --- | --- |
| 弾・エフェクトを毎フレーム作って消す | オブジェクトプール |
| 当たり判定の一時リスト | メンバの `vector` を使い回す、またはフレーム用アリーナ |
| 毎フレームの文字列作成（スコア表示） | `format_to` で、バッファを使い回す。変わったときだけ作り直す |
| ステージのデータ | ロード時にレベル用アリーナにまとめて確保 |
| 描画コマンドの一時リスト | フレーム用アリーナ |
| `std::function` やラムダを、毎フレーム生成 | 大きなキャプチャは、ヒープを使う。メンバに持つ |
| 小さな `shared_ptr` を、大量に作る | 1 つずつ確保・参照カウントが重い。ハンドルやプールの ID にする |

## よくあるミス

??? failure "`clear()` で、メモリが解放されると思う"
    `vector::clear()` は、要素を破棄するだけで容量は残ります。**使い回すには都合がよい**ですが、メモリを返したいなら `shrink_to_fit()`（保証はない）、またはスワップ（`std::vector<T>().swap(v)`）を使います。

??? failure "reserve した容量を超えて、再確保が起きる"
    `reserve(100)` したのに 101 個入れると、再確保（引っ越し）が起きます。上限を決められるなら、余裕を持たせるか、上限を超えない設計にします。

??? failure "プールが満杯のときの動きを決めていない"
    プールの上限を超えたら、確保に失敗するのか、古いものを再利用するのか、ヒープに逃げるのかを設計で決めます（[オブジェクトプール](../design/patterns/object-pool.md)）。

??? failure "フレーム用アリーナを、次のフレームまで持ち越す"
    `release()` したあとの領域は、上書きされます。そのフレームのデータを、次のフレームで使うとバグになります。持ち越すものは、通常のヒープに置きます。

??? failure "スタックに大きな配列を置く"
    `float buffer[1000000];` のような配列は、スタックに載りきらず、スタック オーバーフローになります。`std::vector` にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 確保は<strong>遅く、時間も不安定</strong>。毎フレームの確保がカクつきの原因
    - [x] `vector` は<strong>`reserve`</strong>、メンバに持って<strong>`clear()` で使い回す</strong>
    - [x] 作っては消すものは<strong>プール</strong>、1 フレームの一時データは<strong>アリーナ</strong>、小さいものは<strong>スタック</strong>
    - [x] 確保の回数を<strong>数えて</strong>、毎フレームの確保を 0 に近づける
    - [x] 全体を速くしたいなら、mimalloc などで、グローバルの確保を差し替える

## 関連ページ

- [最適化の進め方](index.md)
- [std::allocator](../stl/memory/allocator.md)
- [std::pmr](../stl/memory/pmr.md)
- [オブジェクトプール](../design/patterns/object-pool.md)
- [メモリとキャッシュ](memory-cache.md)
- [new / delete](../stl/memory/new_delete.md)
- [ハンドル](../engine/handle.md)
- [パフォーマンス設計](../design/practice/performance-design.md)
- [アロケータ（種類ごとの解説）](allocators/index.md)

---
title: std::pmr
tags:
  - メモリ
---

# std::pmr

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い（リソース次第）</span>
<span class="ver ver-17">C++17〜</span>
`#include <memory_resource>`
</div>

**`std::pmr`<strong>（polymorphic memory resource：多態的なメモリリソース）は、</strong>コンテナの型を変えずに、メモリの取り先を実行時に切り替えられる**仕組みです。[自作アロケータ](allocator.md) は、アロケータの種類がコンテナの型に入るので、`std::vector<int>` と `std::vector<int, MyAlloc<int>>` が別の型になってしまいました。pmr では、`std::pmr::vector<int>` という**1 つの型**のまま、「どのメモリを使うか」を値（`memory_resource` へのポインタ）として渡します。標準で用意されているのが、**積むだけで超高速な `monotonic_buffer_resource`<strong>（フレーム用の領域に最適）と、</strong>サイズ別のプール `unsynchronized_pool_resource`** です。ゲームのフレームごとの一時データには、ほぼこれで足ります。

!!! tip "ポイント"
    - <strong>「確保が遅い」と計測で分かったら、まず `std::pmr::monotonic_buffer_resource` を試す。</strong> 自作アロケータより簡単。
    - 型は **`std::pmr::vector<T>`<strong>、</strong>`std::pmr::string`<strong>、</strong>`std::pmr::unordered_map<K, V>`** など（`std::pmr::` を付けるだけ）。
    - フレーム用の領域は、**`std::byte buffer[N]` を渡して、フレームの最後に `release()`** で一括解放する。
    - リソースは**コンテナより長生きさせる**。先に消すとダングリングになる。
    - 渡さなければ、デフォルト（普通の `new` / `delete`）が使われる。

!!! info "このページを読む前に"
    [std::allocator](allocator.md) を先に読むと、pmr が何を楽にしてくれるかが分かります。[継承と仮想関数](../../basics/virtual.md) も関係します（`memory_resource` は仮想関数を持つ基底クラスです）。

## 仕組み

<div class="anim" data-type="graph" data-label="pmr のしくみ：リソースを差し替える">
n vec pmr::vector 0 1 hit
n alloc polymorphic_allocator 1.5 1
n res memory_resource 3.2 1
l vec alloc hit 持つ
l alloc res hit 持つ
# コンテナは、アロケータを通して、メモリのリソース（取り先）へ頼む
---
n vec pmr::vector 0 1
n alloc polymorphic_allocator 1.5 1
n res monotonic 3.2 0 hit
n res2 pool 3.2 1 dim
n res3 new_delete 3.2 2 dim
l vec alloc
l alloc res hit 積むだけ
# リソースは、実行時に選べる。monotonic（積むだけ・一括解放）
---
n vec pmr::vector 0 1
n alloc polymorphic_allocator 1.5 1
n res monotonic 3.2 0 dim
n res2 pool 3.2 1 hit
n res3 new_delete 3.2 2 dim
l vec alloc
l alloc res2 hit サイズ別
# pool（サイズ別のプール）に替えても、vector の型は変わらない
</div>


- **`memory_resource`**: メモリの確保・解放を行う基底クラス。3 つの仮想関数（`do_allocate`、`do_deallocate`、`do_is_equal`）を持つ
- **`polymorphic_allocator<T>`**: `memory_resource*` を 1 つ持つアロケータ。コンテナが使う
- **`std::pmr::vector<T>`**: `std::vector<T, std::pmr::polymorphic_allocator<T>>` の別名

## 関数・型一覧

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`monotonic_buffer_resource`](#monotonic_buffer_resource) | <span class="rank rank-sometimes">たまに</span> | 積むだけで高速。一括解放 |
| [`pmr::vector` など](#pmr_containers) | <span class="rank rank-sometimes">たまに</span> | pmr 版のコンテナ |
| [`polymorphic_allocator`](#polymorphic_allocator) | <span class="rank rank-sometimes">たまに</span> | memory_resource を使うアロケータ |
| [`release`](#release) | <span class="rank rank-sometimes">たまに</span> | monotonic の領域をまとめて返す |
| [`unsynchronized_pool_resource`](#unsynchronized_pool_resource) | <span class="rank rank-rare">知ってるだけ</span> | サイズ別のプール（スレッド非対応） |
| [`synchronized_pool_resource`](#synchronized_pool_resource) | <span class="rank rank-rare">知ってるだけ</span> | サイズ別のプール（スレッド対応） |
| [`new_delete_resource`](#new_delete_resource) | <span class="rank rank-rare">知ってるだけ</span> | 普通の `new` / `delete` を使うリソース |
| [`null_memory_resource`](#null_memory_resource) | <span class="rank rank-rare">知ってるだけ</span> | 確保させず、例外を投げるリソース |
| [`get_default_resource`](#get_default_resource) | <span class="rank rank-rare">知ってるだけ</span> | デフォルトのリソースを取得 |
| [`set_default_resource`](#set_default_resource) | <span class="rank rank-rare">知ってるだけ</span> | デフォルトのリソースを変更 |
| [`memory_resource`](#memory_resource) | <span class="rank rank-rare">知ってるだけ</span> | 自作リソースの基底クラス |

## よくある使い方

```cpp
#include <cstddef>
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  // スタックに置いた 256 バイトの領域を、メモリの取り先にする
  std::byte buffer[256];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));

  std::pmr::vector<int> v(&pool);  // pool から取る vector
  for (int i = 0; i < 10; ++i) {
    v.push_back(i);  // 領域の範囲内なら、ヒープは一切使わない
  }
  std::println("{}", v);
}
```

```text title="実行結果"
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

`std::pmr::vector<int> v(&pool);` のように、**コンストラクタの引数にリソースのアドレスを渡す**だけです。型は `std::pmr::vector<int>` のままなので、同じ型の別の `vector`（デフォルトのリソースを使うもの）と、そのまま関数に渡したり代入したりできます。

### フレームごとに一括解放する

ゲームでは、フレームごとに作って、フレームの最後にすべて捨てるデータがたくさんあります。

```cpp
#include <cstddef>
#include <memory_resource>
#include <print>
#include <vector>

struct Hit {
  int enemy_id;
  float distance;
};

class FrameMemory {
 public:
  std::pmr::memory_resource* resource() { return &pool_; }
  void NextFrame() { pool_.release(); }  // 一括で返す

 private:
  std::byte buffer_[64 * 1024];  // フレームで使う領域（64 KB）
  std::pmr::monotonic_buffer_resource pool_{buffer_, sizeof(buffer_)};
};

int main() {
  FrameMemory frame;
  for (int f = 0; f < 3; ++f) {
    {
      std::pmr::vector<Hit> hits(frame.resource());  // このフレームだけの一時データ
      hits.push_back({1, 2.5f});
      hits.push_back({7, 0.5f});
      std::println("frame {}: {} hits", f, hits.size());
    }  // hits を先に破棄
    frame.NextFrame();  // そのあとで領域を戻す
  }
}
```

```text title="実行結果"
frame 0: 2 hits
frame 1: 2 hits
frame 2: 2 hits
```

!!! warning "release の前に、コンテナを破棄する"
    `release()` したあと、その領域を使っていたコンテナ（`hits` など）は**使えません**（中身は上書きされます）。上の例のように、コンテナのスコープを先に閉じてから `release()` を呼びます。

## 関数・型の詳しい説明

### monotonic_buffer_resource {#monotonic_buffer_resource}

```cpp
class monotonic_buffer_resource : public memory_resource {
 public:
  monotonic_buffer_resource();
  explicit monotonic_buffer_resource(memory_resource* upstream);
  monotonic_buffer_resource(void* buffer, std::size_t size);
  monotonic_buffer_resource(void* buffer, std::size_t size, memory_resource* upstream);
  explicit monotonic_buffer_resource(std::size_t initial_size);
};
```

| 引数 | 意味 |
| --- | --- |
| `buffer`, `size` | 最初に使う領域（スタックの配列など）。`nullptr` / 0 なら、すぐ上流から取る |
| `upstream` | **領域が足りなくなったとき**に、追加のメモリを取りに行く先。デフォルトは `get_default_resource()`（普通の `new`） |
| `initial_size` | 最初に上流から取る大きさ（目安） |

- 戻り値: なし（コンストラクタ）
- 確保は「今の位置から、必要な大きさだけ進める」だけです。**探す処理がないので非常に速く**、メモリの断片化もしません
- <strong>個別の解放（`deallocate`）は何もしません。</strong> `v.pop_back()` や `v.clear()`、再確保で捨てた領域は、**`release()` か、リソースの破棄まで戻ってきません**
- 領域が足りなくなると、上流から**前の約 1.5〜2 倍の大きさ**で追加のブロックを取ります。つまり、バッファが小さくても動きますが、そのぶんヒープを使います
- スレッドセーフではありません（1 つのスレッドから使う）

<div class="anim" data-label="monotonic_buffer_resource（バッファ 8 個ぶん）">
_ _ _ _ _ _ _ _ # 渡した領域。まだ空
+A +A +A _ _ _ _ _ # allocate：先頭から切り出す
+A +A +A +B +B _ _ _ # 続けて切り出す。探さないので速い
x x x x x x _ _ # 個別に deallocate しても、領域は戻らない（残る）
_ _ _ _ _ _ _ _ # release() で一括して空に戻る
</div>

!!! note "vector を増やしていくときの落とし穴"
    `push_back` を繰り返すと、`vector` は**古い領域を捨てて、より大きい領域を確保し直します**。monotonic では古い領域が戻らないので、**最終的な大きさの 2 倍近くを消費**します。使う量が分かるなら **`reserve`** を先に呼びます。

### pmr::vector などの pmr コンテナ {#pmr_containers data-toc-label="pmr::vector などのコンテナ"}

```cpp
namespace std::pmr {
template <class T> using vector = std::vector<T, polymorphic_allocator<T>>;
using string = std::basic_string<char, std::char_traits<char>, polymorphic_allocator<char>>;
template <class K, class V> using map = std::map<K, V, std::less<K>, polymorphic_allocator<std::pair<const K, V>>>;
template <class K, class V> using unordered_map = /* 同様 */;
}
```

| 型 | ヘッダ |
| --- | --- |
| `std::pmr::vector<T>` | `<vector>` |
| `std::pmr::string` | `<string>` |
| `std::pmr::list<T>`、`std::pmr::deque<T>` | `<list>`、`<deque>` |
| `std::pmr::map<K, V>`、`std::pmr::set<T>` | `<map>`、`<set>` |
| `std::pmr::unordered_map<K, V>`、`std::pmr::unordered_set<T>` | `<unordered_map>`、`<unordered_set>` |

- 戻り値: なし（型の別名）
- コンストラクタの最後の引数に `std::pmr::memory_resource*` を渡します（`std::pmr::vector<int> v(&pool);`、`v(10, 0, &pool);` など）
- <strong>入れ子にしたとき、中の要素にもリソースが自動で伝わります。</strong> `std::pmr::vector<std::pmr::string>` なら、文字列の確保も同じリソースから行われます（これを *uses-allocator construction* と呼びます）。`std::vector<std::string>` ではこうなりません

### polymorphic_allocator {#polymorphic_allocator}

```cpp
template <class T>
class polymorphic_allocator {
 public:
  polymorphic_allocator() noexcept;                              // デフォルトのリソース
  polymorphic_allocator(memory_resource* r);                     // r を使う
  T* allocate(std::size_t n);
  void deallocate(T* p, std::size_t n);
  memory_resource* resource() const;
};
```

| 引数 | 意味 |
| --- | --- |
| `r` | 使うリソースへのポインタ（`nullptr` は不可） |

- 戻り値: `resource()` は持っているリソースへのポインタ
- 自作のクラスで「渡されたリソースを使ってメンバのコンテナを作りたい」ときは、コンストラクタに `std::pmr::memory_resource*` を受け取り、メンバのコンテナに渡します。
- **代入のとき、アロケータは移りません**（`propagate_on_*` が `false`）。`a = b` の後も、`a` は元のリソースを使い続けます。コピーされるのは要素だけです

### release {#release}

```cpp
void release();
```

- 戻り値: なし
- 領域をまとめて上流に返し、**最初の状態に戻します**。渡したバッファは、また最初から使えます
- デストラクタも内部で `release()` を呼ぶので、リソースを破棄すれば自動で返されます
- 呼ぶ前に、そのリソースを使っているコンテナをすべて破棄してください

### unsynchronized_pool_resource {#unsynchronized_pool_resource}

```cpp
class unsynchronized_pool_resource : public memory_resource {
 public:
  unsynchronized_pool_resource();
  explicit unsynchronized_pool_resource(memory_resource* upstream);
  unsynchronized_pool_resource(const pool_options& opts, memory_resource* upstream);
};
```

| 引数 | 意味 |
| --- | --- |
| `upstream` | プールが足りないときに取りに行く先 |
| `opts` | `max_blocks_per_chunk`（1 回に取るブロック数）、`largest_required_pool_block`（プールで扱う最大の大きさ）の設定 |

- **大きさごとのプール**（8、16、32…バイト）を持ち、解放されたブロックを**再利用**します。monotonic と違い、個別に `deallocate` したものが次の確保で使い回されます
- 要素を 1 つずつ確保して、どんどん追加・削除する `std::pmr::map`、`std::pmr::list`、`std::pmr::unordered_map` に向いています
- 大きすぎるものは上流に任せます。スレッドセーフではありません

### synchronized_pool_resource {#synchronized_pool_resource}

```cpp
class synchronized_pool_resource : public memory_resource;
```

- `unsynchronized_pool_resource` の**スレッドセーフ版**です。複数のスレッドから同じリソースを使うときだけ使います（ロックのぶん遅くなります）
- スレッドごとにリソースを持てるなら、`unsynchronized_pool_resource` を `thread_local` にするほうが速いです

### new_delete_resource {#new_delete_resource}

```cpp
memory_resource* new_delete_resource() noexcept;
```

- 戻り値: 普通の `operator new` / `operator delete` を使うリソースへのポインタ（グローバルに 1 つ）
- デフォルトで使われるリソースです。`monotonic_buffer_resource` や pool の**上流**に指定するのが主な使い方です

### null_memory_resource {#null_memory_resource}

```cpp
memory_resource* null_memory_resource() noexcept;
```

- 戻り値: 確保しようとすると `std::bad_alloc` を投げるリソース
- 「**ヒープは絶対に使わせない**」ときの上流に指定します。固定のバッファが足りなくなると、ヒープに逃げずに例外が飛ぶので、バッファの大きさが足りないことにすぐ気づけます

```cpp
std::byte buffer[1024];
std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer),
                                         std::pmr::null_memory_resource());
```

### get_default_resource {#get_default_resource}

```cpp
memory_resource* get_default_resource() noexcept;
```

- 戻り値: 今のデフォルトのリソース。最初は `new_delete_resource()`
- リソースを渡さなかった pmr コンテナが、これを使います

### set_default_resource {#set_default_resource}

```cpp
memory_resource* set_default_resource(memory_resource* r) noexcept;
```

| 引数 | 意味 |
| --- | --- |
| `r` | 新しいデフォルトのリソース。`nullptr` なら `new_delete_resource()` に戻る |

- 戻り値: 前のデフォルト
- 以降に作る pmr コンテナ（リソースを渡さないもの）が、`r` を使うようになります。**プログラム全体に効く**ので、普通は使わず、リソースを明示的に渡します

### memory_resource {#memory_resource}

```cpp
class memory_resource {
 public:
  void* allocate(std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));
  void deallocate(void* p, std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));
  bool is_equal(const memory_resource& other) const noexcept;

 private:
  virtual void* do_allocate(std::size_t bytes, std::size_t alignment) = 0;
  virtual void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) = 0;
  virtual bool do_is_equal(const memory_resource& other) const noexcept = 0;
};
```

| 引数 | 意味 |
| --- | --- |
| `bytes` | 確保するバイト数（**要素の数ではない**） |
| `alignment` | 置き場所の約束（2 の累乗）。デフォルトは一番大きい型の約束 |
| `p` | `allocate` が返したポインタ |

- 自作のリソースを作るときの基底クラスです。3 つの `do_` 関数を実装します
- 戻り値: `allocate` は `bytes` 個の生のメモリへのポインタ
- **アロケータとの違い:** アロケータは `T` の数で確保しますが、`memory_resource` は**バイト数とアラインメント**で確保します

```cpp
#include <cstddef>
#include <memory_resource>
#include <print>

// 確保の回数を数えながら、上流に任せるリソース
class CountingResource : public std::pmr::memory_resource {
 public:
  explicit CountingResource(std::pmr::memory_resource* upstream) : upstream_(upstream) {}
  int allocations() const { return allocations_; }

 private:
  void* do_allocate(std::size_t bytes, std::size_t alignment) override {
    ++allocations_;
    return upstream_->allocate(bytes, alignment);
  }
  void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) override {
    upstream_->deallocate(p, bytes, alignment);
  }
  bool do_is_equal(const memory_resource& other) const noexcept override {
    return this == &other;
  }

  std::pmr::memory_resource* upstream_;
  int allocations_ = 0;
};

int main() {
  CountingResource counter(std::pmr::new_delete_resource());
  std::pmr::vector<int> v(&counter);
  v.reserve(100);
  std::println("確保 {} 回", counter.allocations());
}
```

```text title="実行結果"
確保 1 回
```

## どのリソースを選ぶか

| 場面 | 選ぶもの |
| --- | --- |
| フレームの一時データ（捨てるときは一括） | `monotonic_buffer_resource`（スタックの配列 + `release`） |
| 追加・削除を繰り返す `map` / `list` / `unordered_map` | `unsynchronized_pool_resource` |
| ヒープを絶対に使いたくない | `monotonic_buffer_resource` + `null_memory_resource` |
| 複数スレッドで共有する | `synchronized_pool_resource`（または、スレッドごとに別のリソース） |
| 確保の回数・大きさを調べたい | 自作の `CountingResource` |

## 速さの特徴

| リソース | 確保 | 解放 | 向いている形 |
| --- | --- | --- | --- |
| `new_delete_resource` | 普通のヒープ | 普通のヒープ | 何でも |
| `monotonic_buffer_resource` | **ポインタを進めるだけ**（数ナノ秒） | 何もしない（`release` で一括） | 一時データ、作って最後にまとめて捨てるもの |
| `unsynchronized_pool_resource` | 空きリストから取る（速い） | 空きリストに戻す | 小さいものを大量に作る・消す |
| `synchronized_pool_resource` | 上と同じ + ロック | 上と同じ + ロック | 複数スレッド |

!!! note "仮想関数のコスト"
    `memory_resource` は仮想関数なので、確保のたびに 1 回の仮想呼び出しが入ります。ただし、確保そのものと比べればごくわずかです。

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 毎フレームの当たり判定の候補、描画コマンドのリスト | フレーム用の `monotonic_buffer_resource`。フレームの最後に `release()` |
| ステージを読み込む間の一時的な文字列やデータ | ロード用の `monotonic_buffer_resource`。ロードが終わったら `release()` |
| 弾・エフェクトなど、小さいものの追加と削除 | `unsynchronized_pool_resource` を上流に持つ `std::pmr::list` など |
| 「うっかりヒープを使っていないか」の確認 | `null_memory_resource()` を上流にして、例外で見つける |

## よくあるミス

??? failure "リソースをコンテナより先に破棄する"
    ```cpp
    std::pmr::vector<int>* MakeList() {
      std::byte buffer[256];
      std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));
      return new std::pmr::vector<int>(&pool);  // pool もバッファも関数を出ると消える
    }
    ```
    コンテナが使っているリソース（と、そのバッファ）は、コンテナより**長く生きている**必要があります。

??? failure "monotonic で、push_back を繰り返して領域を使い切る"
    再確保のたびに古い領域が戻らず残るので、思ったより早く領域が尽きます。大きさが分かるなら `reserve` で先に取ります。

??? failure "pmr 版でないコンテナに渡そうとする"
    `std::vector<int> v(&pool);` はコンパイルエラーです。`std::pmr::vector<int>` を使います。`std::string` の代わりも `std::pmr::string` です（`std::string` と `std::pmr::string` は別の型で、相互に代入できません）。

??? failure "`release` の後にコンテナを使う"
    `release` は領域を最初の状態に戻すだけで、コンテナには知らせません。コンテナは古い（もう無効な）ポインタを持ったままなので、使うと未定義動作です。

??? failure "swap やムーブでリソースが入れ替わると思う"
    pmr のコンテナは、代入・ムーブ代入でリソースが**移らない**のが基本です。リソースが違うコンテナ同士の代入は、要素を 1 つずつコピー・ムーブするので、遅く、**代入先のリソースの領域を使います**。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::allocator`](allocator.md) | 型にアロケータが入る。自作すると型が変わる |
| オブジェクトプール（[ゲームエンジン](../../design/patterns/object-pool.md)） | 1 種類のオブジェクトを使い回す。pmr のプールは大きさごとに自動で分ける |
| 自作のアリーナ | monotonic と同じ考え方。標準があるので自作は不要 |

## コンパイラ対応

| 機能 | GCC | Clang (libc++) | MSVC |
| --- | --- | --- | --- |
| `<memory_resource>` | 9〜 | 16〜（それ以前は `<experimental/memory_resource>`） | VS2017 15.6〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型を変えずにメモリの取り先を切り替える → `std::pmr::vector<T>` など
    - [x] フレームの一時データは、スタックの配列 + `monotonic_buffer_resource` + 最後に `release()`
    - [x] 追加・削除を繰り返すなら `unsynchronized_pool_resource`
    - [x] リソースは、コンテナより長く生かす
    - [x] monotonic は個別の解放をしない。`reserve` してから使う

## 関連ページ

- [std::allocator](allocator.md)
- [new と delete・配置 new](new_delete.md)
- [オブジェクトプール](../../design/patterns/object-pool.md)
- [std::vector](../containers/vector.md)
- [cppreference: std::pmr::memory_resource](https://en.cppreference.com/w/cpp/memory/memory_resource)

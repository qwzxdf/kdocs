---
title: std::allocator
tags:
  - メモリ
---

# std::allocator

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <memory>`
</div>

<strong>アロケータ（allocator）</strong> は、コンテナが**メモリを確保・解放するときの窓口**になるオブジェクトです。`std::vector<int>` と書くと、本当は `std::vector<int, std::allocator<int>>` という意味で、2 つ目のテンプレート引数がアロケータです。何も指定しなければ、標準の `std::allocator`（中で `new` / `delete` を呼ぶだけ）が使われます。自分でアロケータを作ってコンテナに渡すと、<strong>「どこから」「どうやって」メモリを取るか</strong>を差し替えられます。たとえば、フレームごとに一気に捨てられる領域、固定サイズのプール、デバッグ用の確保回数カウンタなどです。ゲームでは「確保が速いこと」と「確保が一定時間で終わること」が大事なので、アロケータはパフォーマンス調整の道具として使われます。

!!! tip "ポイント"
    - <strong>ほとんどの人は `std::allocator`（何も指定しない）のままでよい。</strong> 変えたくなるのは、確保がボトルネックだと計測で分かったときだけ。
    - 変えたいときは、自作アロケータよりも <strong>[`std::pmr`](pmr.md)（型を変えずにメモリの取り先を切り替えられる仕組み）</strong> のほうが簡単。
    - 自作するなら必要なのは **`value_type`、`allocate`、`deallocate`、`operator==`、型変換用のコンストラクタ** の 5 つだけ（C++11 以降）。
    - アロケータは「<strong>メモリ（確保した生の領域）</strong>」を扱う。オブジェクトの作成・破棄（コンストラクタ・デストラクタ）はコンテナ側の仕事。
    - **アロケータが違うと型が違う**。`std::vector<int>` と `std::vector<int, MyAlloc<int>>` は別の型で、代入や関数の引数に渡せない。

!!! info "このページを読む前に"
    [`new` と `delete`](new_delete.md)、[テンプレート](../../basics/template.md)、[所有権](../../basics/ownership.md) を先に読むと分かりやすいです。C 由来の `malloc` は [malloc / free](c-memory.md) を見てください。

## 宣言

```cpp
template <class T>
struct allocator {
  using value_type = T;
  constexpr allocator() noexcept;
  template <class U> constexpr allocator(const allocator<U>&) noexcept;
  [[nodiscard]] constexpr T* allocate(std::size_t n);
  constexpr void deallocate(T* p, std::size_t n);
};
```

| 部分 | 意味 |
| --- | --- |
| `value_type` | このアロケータが確保する要素の型 |
| `allocate(n)` | `T` を `n` 個ぶん入れられる**生のメモリ**を確保して、先頭のポインタを返す |
| `deallocate(p, n)` | `allocate(n)` で確保した領域を返す。`n` は**確保したときと同じ数**を渡す |
| 型変換用のコンストラクタ | `allocator<int>` から `allocator<Node>` を作れる（リストなどが内部のノード型に合わせるため） |

## どこで使われているか

| コンテナ | アロケータの使い方 |
| --- | --- |
| [`std::vector`](../containers/vector.md) | 要素の配列を 1 つの大きな領域として確保する（`reserve` や再確保のたび） |
| [`std::deque`](../containers/deque.md) | 小さなブロックを複数確保する |
| [`std::list`](../containers/list.md) / [`std::map`](../containers/map.md) / [`std::set`](../containers/set.md) | **要素 1 個ごとに**ノードを確保する（そのため遅く、アロケータの影響が大きい） |
| [`std::unordered_map`](../containers/unordered_map.md) | ノードとバケット配列を確保する |
| [`std::string`](../containers/string.md) | 文字数が長いときだけ確保する（短い文字列は中に持つ） |
| [`std::shared_ptr`](../utilities/shared_ptr.md) | `std::allocate_shared` で制御ブロックごと確保できる |

`std::list<int, MyAlloc<int>>` のとき、リストが確保したいのは `int` ではなく `Node<int>` です。そこで、アロケータの型変換用コンストラクタ（`rebind`）を使って、`MyAlloc<int>` から `MyAlloc<Node<int>>` を作って使います。自作アロケータに「型変換用のコンストラクタ」が必要なのはこのためです。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`allocate`](#allocate) | <span class="rank rank-sometimes">たまに</span> | 生のメモリを確保する |
| [`deallocate`](#deallocate) | <span class="rank rank-sometimes">たまに</span> | メモリを返す |
| [`allocator_traits`](#allocator_traits) | <span class="rank rank-sometimes">たまに</span> | アロケータの機能に統一的にアクセスする |
| [`construct`](#construct) | <span class="rank rank-rare">知ってるだけ</span> | 確保した場所にオブジェクトを作る |
| [`destroy`](#destroy) | <span class="rank rank-rare">知ってるだけ</span> | オブジェクトを破棄する（メモリは返さない） |
| [`allocate_at_least`](#allocate_at_least) <span class="ver ver-23">C++23</span> | <span class="rank rank-rare">知ってるだけ</span> | 要求以上のメモリが取れたときは、その大きさも返す |
| [`max_size`](#max_size) | <span class="rank rank-rare">知ってるだけ</span> | 確保できる最大の要素数 |
| [`select_on_container_copy_construction`](#select_on_container_copy_construction) | <span class="rank rank-rare">知ってるだけ</span> | コンテナをコピーするときに使うアロケータを決める |
| [`std::allocate_shared`](#allocate_shared) | <span class="rank rank-rare">知ってるだけ</span> | アロケータを指定して shared_ptr を作る |

## よくある使い方

アロケータを直接呼ぶことはほとんどありません。コンテナに渡して、確保の仕方を変えます。

```cpp
#include <cstddef>
#include <memory>
#include <print>
#include <vector>

// 確保の回数とバイト数を数える、最小のアロケータ
template <class T>
struct CountingAllocator {
  using value_type = T;

  CountingAllocator() = default;
  template <class U>
  CountingAllocator(const CountingAllocator<U>&) noexcept {}  // 型変換用

  T* allocate(std::size_t n) {
    ++allocations;
    bytes += n * sizeof(T);
    return std::allocator<T>().allocate(n);  // 実際の確保は標準に任せる
  }

  void deallocate(T* p, std::size_t n) noexcept {
    std::allocator<T>().deallocate(p, n);
  }

  // 全部の CountingAllocator で共有する数え台
  static inline int allocations = 0;
  static inline std::size_t bytes = 0;
};

template <class T, class U>
bool operator==(const CountingAllocator<T>&, const CountingAllocator<U>&) {
  return true;  // 状態を持たないので、いつも「同じ」
}

int main() {
  std::vector<int, CountingAllocator<int>> v;
  v.reserve(10);  // 10 個ぶんを 1 回で確保する
  for (int i = 0; i < 10; ++i) {
    v.push_back(i);  // 容量が足りているので確保は起きない
  }
  std::println("確保 {} 回 / {} バイト", CountingAllocator<int>::allocations,
               CountingAllocator<int>::bytes);
}
```

```text title="実行結果"
確保 1 回 / 40 バイト
```

この 5 つ（`value_type`、型変換用コンストラクタ、`allocate`、`deallocate`、`operator==`）がそろっていれば、C++11 以降はコンテナに渡せます。`construct` や `destroy`、`rebind` などは、省略すると標準の `allocator_traits` が代わりに用意してくれます。

## 関数の詳しい説明

### allocate {#allocate}

```cpp
[[nodiscard]] T* allocate(std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `std::size_t` | 確保したい**要素の数**（バイト数ではない） |

- 戻り値: `T` を `n` 個入れられる領域の先頭ポインタ。**中身は未初期化**で、コンストラクタも呼ばれていない
- 計算量: 実装による（標準の `std::allocator` は `operator new` を 1 回呼ぶので、システムの確保と同じ）
- 例外: 確保できないと `std::bad_alloc`。`n` が大きすぎると `std::bad_array_new_length`
- 返るポインタは `T` の**アラインメント**（置ける場所の約束）を満たしている

<div class="anim" data-label="allocator.allocate(4)  ※バンプ（積むだけ）方式">
_ _ _ _ _ _ # 用意した領域。まだ何も使っていない
+A +A _ _ _ _ # 1 回目 allocate(2)：先頭から切り出す
+A +A +B +B +B _ # 2 回目 allocate(3)：続きから切り出す。探さないので速い
</div>

### deallocate {#deallocate}

```cpp
void deallocate(T* p, std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `T*` | `allocate` が返したポインタ |
| `n` | `std::size_t` | `allocate` に渡した**同じ数** |

- 戻り値: なし
- 計算量: 実装による
- `p` と `n` は `allocate` のときと**完全に一致**していなければなりません（`n` を変えると未定義動作）。コンテナは自分の容量（`capacity`）を覚えているので、それを渡してくれます
- ここでは**要素のデストラクタは呼ばれません**。先に `destroy` を呼ぶのはコンテナの役目です

### allocator_traits {#allocator_traits}

```cpp
template <class Alloc>
struct allocator_traits {
  using pointer = /* ... */;
  static pointer allocate(Alloc& a, size_type n);
  static void deallocate(Alloc& a, pointer p, size_type n);
  template <class T, class... Args>
  static void construct(Alloc& a, T* p, Args&&... args);
  template <class T>
  static void destroy(Alloc& a, T* p);
};
```

| 引数 | 意味 |
| --- | --- |
| `Alloc` | アロケータの型 |
| `a` | アロケータの値 |

- アロケータが持っていない機能（`construct` など）を、**標準のやり方で補ってくれる**クラスです。コンテナは、アロケータを直接ではなく必ずこれ経由で呼びます
- 自作アロケータは最小限だけ書けば済みます。足りない部分は traits が埋めます

| traits が補ってくれるもの | 自作で省略したときの動き |
| --- | --- |
| `construct` / `destroy` | placement new と、デストラクタ呼び出し |
| `rebind_alloc<U>` | `Alloc<T>` なら `Alloc<U>` を作る |
| `max_size` | その型で表せる最大値 |
| `propagate_on_container_copy_assignment` など | `false_type`（代入してもアロケータはコピーしない） |
| `is_always_equal` | 状態を持たない空のアロケータなら `true_type` |
| `select_on_container_copy_construction` | 渡されたアロケータをそのままコピー |

### construct {#construct}

```cpp
template <class T, class... Args>
void construct(T* p, Args&&... args);  // allocator_traits 経由で呼ぶ
```

| 引数 | 意味 |
| --- | --- |
| `p` | オブジェクトを作る場所（`allocate` した領域の中） |
| `args` | コンストラクタに渡す引数 |

- 戻り値: なし
- 標準の動きは `::new (p) T(std::forward<Args>(args)...)`（[配置 new](new_delete.md#placement_new)）です
- 自作アロケータで `construct` を書くのは、構築のときにアロケータ自身を要素に渡したい特殊な場合（[`std::pmr`](pmr.md) が内部でやっていること）だけです

### destroy {#destroy}

```cpp
template <class T>
void destroy(T* p);  // allocator_traits 経由で呼ぶ
```

| 引数 | 意味 |
| --- | --- |
| `p` | 破棄するオブジェクトの場所 |

- 戻り値: なし
- `p->~T()`（デストラクタ）を呼ぶだけで、**メモリは返しません**。返すのは `deallocate` の役目です

### allocate_at_least <span class="ver ver-23">C++23</span> {#allocate_at_least data-toc-label="allocate_at_least"}

```cpp
[[nodiscard]] std::allocation_result<T*> allocate_at_least(std::size_t n);
```

| 引数 | 意味 |
| --- | --- |
| `n` | 最低限ほしい要素の数 |

- 戻り値: `{ptr, count}`。`count >= n` で、実際に使える数
- ヒープは、要求より少し大きく確保するのが普通です（たとえば 40 バイト頼むと 48 バイト取れる）。この余りを捨てずに使えるように、確保できた数も返します。`std::vector` や `std::string` が、無駄なく容量を使うための機能です
- `deallocate` に渡す `n` は、`count`（実際に確保できた数）にします

### max_size {#max_size}

```cpp
size_type max_size() const noexcept;
```

- 戻り値: 1 回で確保できる最大の要素数の目安
- コンテナの `max_size()` が、これを使って答えています

### select_on_container_copy_construction {#select_on_container_copy_construction data-toc-label="select_on_container_copy_construction"}

```cpp
Alloc select_on_container_copy_construction() const;
```

- 戻り値: コピーされたコンテナが使うアロケータ
- 書かなければ、元のアロケータのコピーが使われます。「コピー先は新しいアロケータ（デフォルトのもの）にしたい」ときだけ自作します

### std::allocate_shared {#allocate_shared data-toc-label="std::allocate_shared"}

```cpp
template <class T, class Alloc, class... Args>
std::shared_ptr<T> allocate_shared(const Alloc& a, Args&&... args);
```

| 引数 | 意味 |
| --- | --- |
| `a` | 使うアロケータ |
| `args` | `T` のコンストラクタに渡す引数 |

- `std::make_shared` の、アロケータを指定できる版です。オブジェクトと制御ブロック（参照カウントなど）を**まとめて 1 回で**確保します

## アロケータの「状態」と operator==

アロケータは、**自分の中に状態を持てます**。たとえば「この領域（アリーナ）から取る」という情報です。そのため、`operator==` が大事になります。

| 場面 | operator== の意味 |
| --- | --- |
| コンテナの `swap` やムーブ | 等しければ、ポインタをそのまま渡せる（中身のコピーなし） |
| 等しくないとき | 要素を 1 つずつ移す（遅くなる）か、そもそもできない |
| `a == b` が `true` | 「`a` で確保したものを `b` で解放してよい」という約束 |

状態を持たない（空の）アロケータは、必ず `true` を返します。状態を持つなら、状態が同じかを比べます。

```cpp
template <class T, class U>
bool operator==(const ArenaAllocator<T>& a, const ArenaAllocator<U>& b) {
  return a.arena() == b.arena();  // 同じアリーナを使っていれば等しい
}
```

### コンテナの代入・ムーブ・swap で何が起きるか

コンテナを代入・ムーブ・swap するときに、アロケータもいっしょに移るかは、アロケータの **`propagate_on_container_xxx`** という設定で決まります。

| 設定 | `true` のとき | デフォルト |
| --- | --- | --- |
| `propagate_on_container_copy_assignment` | `a = b` でアロケータもコピーされる | `false` |
| `propagate_on_container_move_assignment` | `a = std::move(b)` でアロケータもムーブされる | `false` |
| `propagate_on_container_swap` | `swap` でアロケータも入れ替わる | `false` |

デフォルトは**どれも `false`<strong> です。つまり、アロケータが違うコンテナ同士で代入すると、</strong>要素を 1 つずつコピー・ムーブ**して、アロケータは変わりません。これを知らないと、「ムーブしたのに遅い」「ムーブしたのにアリーナの外に出てしまった」という問題が起きます。

## 自作の例：アリーナ（積むだけの領域）

「先頭から順に切り出していくだけ」で、解放は**まとめて 1 回**だけ、という領域がアリーナ（バンプアロケータ）です。確保がポインタを進めるだけなので、とても速く、メモリの断片化もありません。

```cpp
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>
#include <print>
#include <vector>

// 固定サイズの領域から、先頭順に切り出す
class Arena {
 public:
  void* Allocate(std::size_t bytes, std::size_t align) {
    std::size_t start = (used_ + align - 1) / align * align;  // 境界をそろえる
    if (start + bytes > sizeof(buffer_)) {
      throw std::bad_alloc();
    }
    used_ = start + bytes;
    return buffer_ + start;
  }
  void Reset() { used_ = 0; }  // 全部まとめて解放
  std::size_t used() const { return used_; }

 private:
  alignas(std::max_align_t) std::byte buffer_[1024];
  std::size_t used_ = 0;
};

template <class T>
class ArenaAllocator {
 public:
  using value_type = T;

  explicit ArenaAllocator(Arena* arena) : arena_(arena) {}
  template <class U>
  ArenaAllocator(const ArenaAllocator<U>& other) noexcept : arena_(other.arena()) {}

  T* allocate(std::size_t n) {
    return static_cast<T*>(arena_->Allocate(n * sizeof(T), alignof(T)));
  }
  void deallocate(T*, std::size_t) noexcept {}  // 個別には返さない

  Arena* arena() const { return arena_; }

 private:
  Arena* arena_;
};

template <class T, class U>
bool operator==(const ArenaAllocator<T>& a, const ArenaAllocator<U>& b) {
  return a.arena() == b.arena();
}

int main() {
  Arena arena;
  std::vector<int, ArenaAllocator<int>> v{ArenaAllocator<int>(&arena)};
  v.reserve(8);  // 8 個ぶん（32 バイト）をアリーナから取る
  for (int i = 0; i < 8; ++i) {
    v.push_back(i * i);
  }
  std::println("{}", v);
  std::println("アリーナの使用量 {} バイト", arena.used());
}
```

```text title="実行結果"
[0, 1, 4, 9, 16, 25, 36, 49]
アリーナの使用量 32 バイト
```

!!! warning "アリーナの注意"
    - `deallocate` が何もしないので、`reserve` なしで `push_back` を繰り返して再確保が起きると、**古い領域もアリーナに残り続けます**。アリーナを使うコンテナは、先に `reserve` するのが基本です。
    - `Reset()` したあとは、そのアリーナを使っていたコンテナを**使ってはいけません**（中身はもう無効です）。先にコンテナを破棄します。
    - 自作せずに、標準の [`std::pmr::monotonic_buffer_resource`](pmr.md#monotonic_buffer_resource) を使うのがおすすめです。

## 速さの特徴

| 場面 | 速さ |
| --- | --- |
| 標準の `std::allocator` | システムのヒープ（`malloc` と同じ）。1 回の確保は数十〜数百ナノ秒。確保にかかる時間が**一定とは限らない** |
| アリーナ（バンプ） | ポインタを進めるだけ。数ナノ秒で一定。解放は一括 |
| プール（固定サイズのブロック） | 空きリストをたどるだけ。一定時間。同じ大きさのものだけ |
| ノード型コンテナ（`list`、`map`） | 要素ごとに確保するので、アロケータの差が**とても大きく**出る |
| `vector` | 確保の回数が少ないので、アロケータを変えても差は小さい（`reserve` で十分なことが多い） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| フレームごとの一時データ（当たり判定の候補など） | フレーム用アリーナから取り、フレームの最後に `Reset()` |
| 同じ大きさのオブジェクトを大量に作って消す（弾、パーティクル） | 固定サイズのプール（[オブジェクトプール](../../design/patterns/object-pool.md)） |
| ロード中のデータ | レベル用のアリーナ。ステージを抜けるときにまとめて破棄 |
| メモリの使い方のデバッグ | 確保の回数・バイト数を数える `CountingAllocator` |
| ゲーム機のメモリ制限 | 用途ごとに上限のある領域を割り当てる |

## よくあるミス

??? failure "`allocate` が返したメモリを、そのまま使ってしまう"
    `allocate` は**未初期化の生のメモリ**です。`int` なら読む前に代入すれば使えますが、`std::string` などは、**`construct`（配置 new）で作る前に触ってはいけません**。普通はコンテナがやってくれるので、アロケータを直接使うときだけ注意します。

??? failure "`deallocate` に違う `n` を渡す"
    `allocate(10)` したものに `deallocate(p, 5)` と渡すのは未定義動作です。確保したときと同じ数を渡します。

??? failure "operator== を `true` 固定にしてしまう"
    状態を持つアロケータで、`operator==` がいつも `true` だと、コンテナが「別のアリーナのメモリを、こちらのアロケータで解放してよい」と判断してしまいます。状態（アリーナのポインタなど）を比べます。

??? failure "アロケータが違うコンテナを代入しようとする"
    `std::vector<int>` と `std::vector<int, ArenaAllocator<int>>` は別の型なので、`a = b` や関数の引数に渡せません。型をそろえるか、アロケータの型を変えずに済む [`std::pmr`](pmr.md) を使います。

??? failure "アリーナを `Reset` したあとにコンテナを使う"
    アリーナの領域は再利用されるので、別のものを入れたとたんにコンテナの中身が壊れます。コンテナを先に破棄（または `clear` して小さくして）から `Reset` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::pmr`](pmr.md) | 型を変えずに、メモリの取り先を実行時に切り替えられる。まずはこちらを使う |
| [`new` / `delete`](new_delete.md) | オブジェクト 1 つの確保と作成を同時にやる。アロケータは確保だけ |
| [`malloc` / `free`](c-memory.md) | C 言語の確保関数。コンストラクタは呼ばれない |

## コンパイラ対応

| 機能 | GCC | Clang (libc++) | MSVC |
| --- | --- | --- | --- |
| アロケータの基本（C++11） | 4.8〜 | 3.x〜 | VS2015〜 |
| `std::allocate_at_least`（C++23） | 14〜 | 15〜 | VS2022 17.x〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何も指定しなければ `std::allocator`（中身は `new` / `delete`）
    - [x] 変えたいときは、まず [`std::pmr`](pmr.md)。自作は `allocate`・`deallocate`・`operator==` など 5 つ
    - [x] アロケータは**生のメモリ**だけを扱う。オブジェクトの作成・破棄はコンテナの仕事
    - [x] アロケータが違うと型が違う。代入・ムーブで `propagate_on_*` が効く
    - [x] ゲームでは、フレーム用のアリーナと、固定サイズのプールがよく使われる

## 関連ページ

- [std::pmr（メモリリソース）](pmr.md)
- [new と delete・配置 new](new_delete.md)
- [malloc / free（C 由来のメモリ確保）](c-memory.md)
- [std::vector](../containers/vector.md)
- [オブジェクトプール](../../design/patterns/object-pool.md)
- [cppreference: std::allocator](https://en.cppreference.com/w/cpp/memory/allocator)

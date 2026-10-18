---
title: STL との接続（アロケータ対応）
tags:
  - 最適化
  - アロケータ
---

# STL との接続（アロケータ対応）

自作のアロケータを作っても**`std::vector` や `std::string` などの標準のコンテナ**が、**それを使ってくれなければ**、役に立ちません。C++ には**コンテナにアロケータを渡す仕組み**が 2 つあります。**① 型にアロケータを持たせる**（古くからある方式：`std::allocator<T>` の置き換え）、**② 実行時に差し替える**（C++17 の **`std::pmr`**）です。このページは**両方の方法**と**使い分け**をまとめます（標準のアロケータ自体は [std::allocator](../../stl/memory/allocator.md)、[std::pmr](../../stl/memory/pmr.md)）。

!!! tip "ポイント"
    - コンテナは<strong>アロケータをテンプレート引数</strong>に持つ：<strong>`std::vector<int, MyAllocator<int>>`</strong>。
    - 自作は<strong>`value_type`・`allocate(n)`・`deallocate(p, n)`・比較演算子・変換コンストラクタ</strong>が必要。
    - <strong>アロケータが違うとコンテナの「型」が違う</strong>（`vector<int>` と `vector<int, A>` は別物）。これが<strong>不便</strong>。
    - <strong>`std::pmr`（C++17）</strong>は <strong>型を変えず実行時にアロケータを差し替える</strong>。<strong>こちらが現代の定番</strong>。
    - <strong>`std::pmr::memory_resource` を継承</strong>して、<strong>自作のアロケータを `pmr` に乗せる</strong>。
    - <strong>リニア ＋ pmr</strong>で、<strong>フレームの一時コンテナ</strong>をヒープ確保なしにできる。

## 方法 1：アロケータを型にする

### 標準の要件

アロケータは**最低限、次のものを持つ**クラス（テンプレート）です。

```cpp
template <typename T>
class ArenaAllocator {
 public:
  using value_type = T;

  explicit ArenaAllocator(LinearAllocator* arena) noexcept : arena_(arena) {}

  template <typename U>
  ArenaAllocator(const ArenaAllocator<U>& other) noexcept : arena_(other.arena()) {}

  T* allocate(size_t n) {
    void* p = arena_->Allocate(n * sizeof(T), alignof(T));
    if (p == nullptr) throw std::bad_alloc();
    return static_cast<T*>(p);
  }

  void deallocate(T*, size_t) noexcept {}

  LinearAllocator* arena() const noexcept { return arena_; }

  template <typename U>
  bool operator==(const ArenaAllocator<U>& other) const noexcept {
    return arena_ == other.arena();
  }

 private:
  LinearAllocator* arena_;
};
```

| 要素 | 意味 |
| --- | --- |
| **`value_type`** | **確保する要素の型** |
| **`allocate(n)`** | **`n` 個ぶんのメモリを貸す**（要素の構築は、コンテナがやる） |
| **`deallocate(p, n)`** | **返す**。**リニアなら何もしない** |
| **変換コンストラクタ**（`ArenaAllocator<U>` から） | **コンテナが、内部のノード型（`std::list` のノードなど）用に `rebind`** するときに使う |
| **`operator==`** | <strong>「同じアロケータか」</strong>。**一方で確保したものを他方で解放できるか**の判断（C++20 は、`!=` を自動で作る） |

### 使い方

```cpp
LinearAllocator arena(buffer, sizeof(buffer));
ArenaAllocator<int> allocator(&arena);

std::vector<int, ArenaAllocator<int>> v(allocator);
v.push_back(1);
v.push_back(2);

std::list<int, ArenaAllocator<int>> l(allocator);
```

### ステートフルなアロケータ

<strong>上の例は「どのアリーナを使うか」という状態（`arena_`）</strong>を持つ**ステートフル**です。

| 種類 | 説明 |
| --- | --- |
| **ステートレス**（`std::allocator`） | **状態を持たない**。**どれも同じ**（`==` は常に `true`） |
| **ステートフル**（自作） | <strong>状態（アリーナのポインタ）</strong>を持つ。**`==` は状態を比べる** |

**コンテナのコピー・ムーブのときにアロケータをどうするか**は、**`allocator_traits` の `propagate_on_container_*`**で決まります。

| 設定 | 意味 | 既定 |
| --- | --- | --- |
| `propagate_on_container_copy_assignment` | **コピー代入で、アロケータも**コピー | `false` |
| `propagate_on_container_move_assignment` | **ムーブ代入で、アロケータも**ムーブ | `false` |
| `propagate_on_container_swap` | **`swap` でアロケータも**入れ替え | `false` |

**既定は `false`**（アロケータは**コンテナと一緒に動かない**）です。**アロケータが違うコンテナ同士のムーブ代入は、要素を 1 つずつ移す**ことになり**遅く**なる場合があります。

### 型が変わる問題

```cpp
std::vector<int> a;
std::vector<int, ArenaAllocator<int>> b;

void Process(const std::vector<int>& v);
Process(a);
Process(b);
```

**アロケータの違うコンテナは別の型**です。**`Process(b)` はコンパイルエラー**です。**関数をテンプレートにする**か `std::span<const int>` で受け取るしかありません。**この不便さが `pmr` ができた理由**です。

## 方法 2：std::pmr（実行時に差し替える）

**`std::pmr`**（Polymorphic Memory Resource、C++17）は**コンテナの型を変えずアロケータ（`memory_resource`）を実行時に差し替える**仕組みです。

```cpp
#include <memory_resource>

std::pmr::monotonic_buffer_resource resource(buffer, sizeof(buffer));
std::pmr::vector<int> v(&resource);
v.push_back(1);

void Process(const std::pmr::vector<int>& v);
Process(v);
```

| 型 | 意味 |
| --- | --- |
| **`std::pmr::memory_resource`** | **アロケータの抽象クラス**（仮想関数 3 つ） |
| **`std::pmr::polymorphic_allocator<T>`** | **`memory_resource` を使うアロケータ**（コンテナの既定） |
| **`std::pmr::vector<T>`** | **`std::vector<T, polymorphic_allocator<T>>` の別名** |
| `std::pmr::string`、`std::pmr::map`、`std::pmr::unordered_map` ... | **同様**に用意されている |

**`pmr::vector<int>` はどの `memory_resource` を使っていても、同じ型**です。**関数の引数にそのまま渡せます**。

### 標準の memory_resource

| クラス | 動き |
| --- | --- |
| **`std::pmr::new_delete_resource()`** | **普通の `new` / `delete`**（既定） |
| **`std::pmr::null_memory_resource()`** | **常に失敗**（`std::bad_alloc`）。**上流を禁止**したいときに |
| **`std::pmr::monotonic_buffer_resource`** | <strong>[リニア](linear.md)</strong>。**解放は無視**、**`release()` でまとめて捨てる** |
| **`std::pmr::unsynchronized_pool_resource`** | <strong>プール（サイズクラス）</strong>、**スレッド非安全**（速い） |
| **`std::pmr::synchronized_pool_resource`** | 上の**スレッド安全版** |

```cpp
alignas(64) std::byte buffer[1 << 16];
std::pmr::monotonic_buffer_resource frame_resource(buffer, sizeof(buffer), std::pmr::null_memory_resource());

std::pmr::unsynchronized_pool_resource pool;
```

### 自作の memory_resource

自作のアロケータを**`pmr` に乗せる**には、**`memory_resource` を継承**して**3 つの関数をオーバーライド**します。

```cpp
class PoolResource : public std::pmr::memory_resource {
 public:
  explicit PoolResource(PoolAllocator* pool) : pool_(pool) {}

 private:
  void* do_allocate(size_t bytes, size_t alignment) override {
    void* p = pool_->Allocate();
    if (p == nullptr) throw std::bad_alloc();
    return p;
  }

  void do_deallocate(void* p, size_t bytes, size_t alignment) override {
    pool_->Deallocate(p);
  }

  bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
    return this == &other;
  }

  PoolAllocator* pool_;
};
```

| 関数 | 意味 |
| --- | --- |
| **`do_allocate(bytes, alignment)`** | **メモリを貸す**（足りなければ `std::bad_alloc`） |
| **`do_deallocate(p, bytes, alignment)`** | **返す** |
| **`do_is_equal(other)`** | **同じ資源か**（**一方で確保したものを他方で解放できるか**） |

<strong>これだけで自作のアロケータが、`std::pmr::vector` などに使えます。</strong>

### pmr のコンテナの入れ子

**`pmr` のコンテナの中に `pmr` のコンテナ**を入れると、**中のコンテナも同じ `memory_resource`** を使います（**アロケータが、自動で伝わる**）。

```cpp
std::pmr::monotonic_buffer_resource resource(buffer, sizeof(buffer));
std::pmr::vector<std::pmr::string> names(&resource);
names.emplace_back("Alice");
```

**`names` の中の `pmr::string` も `resource` から確保**されます（**`uses_allocator` 構築**）。**普通の `std::vector<std::string>` では文字列の中身が、ヒープに行ってしまう**のと対照的です。

### 既定の memory_resource を替える

```cpp
std::pmr::set_default_resource(&my_resource);
```

**`pmr` のコンテナで `memory_resource` を渡さなかったとき**の既定を替えます（**グローバルな設定**。使いすぎない）。

## 2 つの方法の比べ

| | 型にするアロケータ | **`std::pmr`** |
| --- | --- | --- |
| **コンテナの型** | **アロケータごとに別の型** | **同じ型**（`pmr::vector<T>`） |
| **差し替え** | **コンパイル時** | **実行時** |
| **関数の引数** | **テンプレートにする必要** | **そのまま渡せる** |
| **速度** | **仮想呼び出しなし**（わずかに速い） | **`memory_resource` の仮想呼び出し**（わずかに遅い） |
| **入れ子のコンテナ** | **自分で伝える** | **自動で伝わる** |
| **向いている** | **極限の速さ**、**古いコード** | <strong>普通の用途（推奨）</strong> |

**ほとんどの場合、`std::pmr` が扱いやすい**です。**確保の速さに比べれば仮想呼び出しのコストは、ほぼ無視できます**。

## ゲームでの使い方

| 場面 | 使い方 |
| --- | --- |
| **フレームの一時コンテナ** | **`monotonic_buffer_resource`**（フレームごとに `release()`）。**`pmr::vector` を使う** |
| **ロード中の一時データ** | **`monotonic_buffer_resource`**（ロード後に捨てる） |
| **同じ大きさの小さな要素が多い `map` / `list`** | **`unsynchronized_pool_resource`** |
| **自作のプールをコンテナで使う** | **`memory_resource` を継承**して、**包む** |

```cpp
void Frame() {
  frame_resource.release();

  std::pmr::vector<Enemy*> nearby(&frame_resource);
  std::pmr::unordered_map<int, float> distances(&frame_resource);
}
```

## よくあるミス

??? failure "`pmr` のコンテナを `memory_resource` より長生きさせる"
    **`memory_resource` が先に消える**と**コンテナが、消えたメモリを使う**ことになります。**`memory_resource` はコンテナより長く生かす**。

??? failure "`monotonic_buffer_resource` の `release()` 後にコンテナを使う"
    **すべての確保が無効**です。**コンテナも同時に破棄**します。

??? failure "別の `memory_resource` のコンテナをムーブ・コピーして、確保が起きる"
    **`memory_resource` が違う**と**要素を 1 つずつ移す**（コピー）ことになります。**同じ `memory_resource`** を使います。

??? failure "自作アロケータの `operator==` を常に `true` にする"
    **別のアリーナで確保したもの**を**間違って解放**します。**状態を正しく比べます**。

??? failure "`monotonic_buffer_resource` に `vector` を使って、拡張のたびにメモリが増える"
    **古いバッファは返らず**、**積み上がります**。**`reserve` で最初に確保**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンテナは<strong>アロケータをテンプレート引数</strong>に持つ。<strong>自作は `value_type`・`allocate`・`deallocate`・`==`・変換コンストラクタ</strong>
    - [x] <strong>アロケータが違うとコンテナの型が違う</strong>。これを解決したのが <strong>`std::pmr`</strong>
    - [x] <strong>`std::pmr::vector` などは型が同じで、実行時に `memory_resource` を差し替える</strong>
    - [x] 自作は<strong>`memory_resource` を継承</strong>（<strong>`do_allocate`・`do_deallocate`・`do_is_equal`</strong>）
    - [x] <strong>フレームの一時コンテナ ＝ `monotonic_buffer_resource` ＋ `pmr::vector`</strong>
    - [x] <strong>`memory_resource` はコンテナより長生きさせる</strong>

## 関連ページ

- [アロケータ（目次）](index.md)
- [リニアアロケータ](linear.md)
- [プールアロケータ](pool.md)
- [フレームアロケータ](frame.md)
- [std::allocator](../../stl/memory/allocator.md)
- [std::pmr](../../stl/memory/pmr.md)

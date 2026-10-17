---
title: new と delete・配置 new
tags:
  - メモリ
---

# new と delete・配置 new

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>` / `#include <memory>`
</div>

**`new`** は「**メモリを確保して、そこにオブジェクトを作る<strong>」を 1 回でやる演算子で、</strong>`delete`** は「**オブジェクトを破棄して、メモリを返す<strong>」演算子です。ヒープ（自由に使えるメモリ領域）にオブジェクトを置くときの基本です。ただし、</strong>`new` の結果を生のポインタで持ち、自分で `delete` する書き方は、今はほとんど使いません**。`delete` を忘れるとメモリリーク、2 回やると二重解放で、バグの温床だからです。普通は `std::make_unique` と `std::vector` に任せます。それでも、**確保と作成を分けたいとき**（アロケータ、プール、オブジェクトを使い回すとき）のために、**配置 new**（確保済みの場所に作る）と、その後始末（`destroy_at`）を知っておく必要があります。

!!! tip "ポイント"
    - <strong>生の `new` / `delete` を書かない。</strong> 1 個なら `std::make_unique<T>(...)`、複数なら `std::vector<T>`。
    - `new` は「**確保 + コンストラクタ呼び出し**」、`delete` は「**デストラクタ呼び出し + 解放**」の 2 段階。
    - **`new[]` で作ったものは `delete[]`** で消す（`delete` ではなく）。1 個の `new` は `delete`。
    - `malloc` / `free` と **混ぜない**（[malloc / free](c-memory.md)）。
    - 確保済みの場所にオブジェクトを作る **配置 new** は、プールやアロケータの内部で使う。普通は `std::construct_at` を使うほうが安全。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md)、[所有権](../../basics/ownership.md)、[unique_ptr](../utilities/unique_ptr.md) を先に読んでください。メモリの置き場所の話は [キャッシュ効率](../../basics/cache.md) とつながります。

## 4 つの組み合わせ

| 作る | 消す | 書き方 |
| --- | --- | --- |
| オブジェクト 1 個 | `delete` | `Enemy* e = new Enemy(10);` → `delete e;` |
| オブジェクトの配列 | `delete[]` | `int* a = new int[100];` → `delete[] a;` |
| 確保済みの場所に作る | デストラクタを直接呼ぶ | `new (p) Enemy(10);` → `e->~Enemy();` |
| 確保だけ | `operator delete` | `void* p = operator new(sizeof(Enemy));` → `operator delete(p);` |

`new` 式の中では、実は次の 2 つが順に行われます。

```text
new Enemy(10)
  ① operator new(sizeof(Enemy))   … メモリを確保（失敗したら std::bad_alloc）
  ② Enemy のコンストラクタ(10)     … 確保した場所にオブジェクトを作る
  （② で例外が出たら、① のメモリは自動で返される）

delete e
  ① Enemy のデストラクタ          … オブジェクトを破棄
  ② operator delete(e)            … メモリを返す
```

## 関数・演算子一覧

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`new` 式](#new) | <span class="rank rank-often">よく使う</span> | 確保 + 作成 |
| [`delete` 式](#delete) | <span class="rank rank-often">よく使う</span> | 破棄 + 解放 |
| [`new[]` / `delete[]`](#new_array) | <span class="rank rank-sometimes">たまに</span> | 配列の確保・解放 |
| [`std::nothrow`](#nothrow) | <span class="rank rank-sometimes">たまに</span> | 失敗したとき例外ではなく `nullptr` を返す |
| [配置 new](#placement_new) | <span class="rank rank-sometimes">たまに</span> | 確保済みの場所に作る |
| [`std::construct_at`](#construct_at) <span class="ver ver-20">C++20</span> | <span class="rank rank-sometimes">たまに</span> | 配置 new の安全な書き方 |
| [`std::destroy_at`](#destroy_at) <span class="ver ver-17">C++17</span> | <span class="rank rank-sometimes">たまに</span> | デストラクタだけを呼ぶ |
| [`operator new` / `operator delete`](#operator_new) | <span class="rank rank-rare">知ってるだけ</span> | 確保だけ・解放だけ、差し替え |
| [`std::uninitialized_copy` など](#uninitialized) | <span class="rank rank-rare">知ってるだけ</span> | 未初期化の領域にまとめて作る |
| [`std::launder`](#launder) <span class="ver ver-17">C++17</span> | <span class="rank rank-rare">知ってるだけ</span> | 同じ場所に作り直したオブジェクトを指し直す |
| [`std::align_val_t`](#align_val_t) <span class="ver ver-17">C++17</span> | <span class="rank rank-rare">知ってるだけ</span> | アラインメントを指定した確保 |

## よくある使い方

```cpp
#include <memory>
#include <print>

struct Enemy {
  explicit Enemy(int hp) : hp(hp) { std::println("作成 hp={}", hp); }
  ~Enemy() { std::println("破棄 hp={}", hp); }
  int hp;
};

int main() {
  // × 古い書き方：delete を書き忘れるとリークする
  Enemy* a = new Enemy(10);
  delete a;

  // ○ 今の書き方：スコープを出ると自動で delete される
  auto b = std::make_unique<Enemy>(20);
  std::println("b の hp は {}", b->hp);
}
```

```text title="実行結果"
作成 hp=10
破棄 hp=10
作成 hp=20
b の hp は 20
破棄 hp=20
```

## 関数・演算子の詳しい説明

### new 式 {#new data-toc-label="new 式"}

```cpp
T* p = new T(args...);       // () の初期化
T* p = new T{args...};       // {} の初期化
T* p = new T;                // 基本型は未初期化、クラスはデフォルトコンストラクタ
```

| 引数 | 意味 |
| --- | --- |
| `args...` | `T` のコンストラクタに渡す引数 |

- 戻り値: 作ったオブジェクトへのポインタ
- 例外: メモリが確保できないと `std::bad_alloc`。コンストラクタが例外を投げたら、確保したメモリは自動で返される
- `new int;` だと**中身が不定**です。`new int();` か `new int{}` とすると 0 で初期化されます
- 確保の中身（どこから取るか）は [`operator new`](#operator_new) が決めます

!!! warning "`new` の結果は、すぐ unique_ptr に入れる"
    `new` で得たポインタを、生のまま持ち回らないでください。例外が出たときにリークします。`std::make_unique<T>(...)` なら、確保と所有を同時に行えます。

### delete 式 {#delete data-toc-label="delete 式"}

```cpp
delete p;
```

| 引数 | 意味 |
| --- | --- |
| `p` | `new` で得たポインタ。`nullptr` なら何もしない |

- 戻り値: なし
- デストラクタを呼んでから、メモリを返します
- **同じポインタを 2 回 `delete` する<strong>（二重解放）、</strong>`new[]` で作ったものを `delete` する<strong>、</strong>`malloc` したものを `delete` する**のは、どれも未定義動作です
- `delete` したあとのポインタは使えません（ダングリング）。`p = nullptr;` としておくと、うっかり使ったときに気づけます（unique_ptr ならこの心配自体がありません）
- 基底クラスのポインタで `delete` するなら、基底クラスのデストラクタは **`virtual`** にします（[継承と仮想関数](../../basics/virtual.md)）

### new[] / delete[] {#new_array data-toc-label="new[] と delete[]"}

```cpp
T* p = new T[n];       // n 個。各要素はデフォルトコンストラクタ
T* p = new T[n]{};     // 値で初期化（基本型は 0）
delete[] p;            // 配列は必ず delete[]
```

| 引数 | 意味 |
| --- | --- |
| `n` | 要素の数 |

- 戻り値: 先頭の要素へのポインタ
- **`delete[]` で消す**ことが大事です。`delete`（`[]` なし）だと、先頭の 1 個のデストラクタしか呼ばれず、未定義動作です
- 配列の大きさはポインタからは取れません。自分で覚えておく必要があります
- ほぼ使いません。`std::vector<T>` や `std::unique_ptr<T[]>`、`std::array<T, N>` を使います

### std::nothrow {#nothrow}

```cpp
T* p = new (std::nothrow) T(args...);
```

| 引数 | 意味 |
| --- | --- |
| `std::nothrow` | 失敗したとき、例外ではなく `nullptr` を返す印 |

- 戻り値: 成功なら `T*`、失敗なら `nullptr`
- 例外を使わないプロジェクトで使われます。**`nullptr` かどうかを必ず確認**します（確認しないと、結局クラッシュします）

### 配置 new {#placement_new data-toc-label="配置 new"}

```cpp
void* place = /* 確保済みの領域 */;
T* p = new (place) T(args...);   // place の場所に T を作る
p->~T();                         // 後始末は、デストラクタを自分で呼ぶ
```

| 引数 | 意味 |
| --- | --- |
| `place` | オブジェクトを作る場所。**大きさと、アラインメントが足りている**必要がある |
| `args...` | コンストラクタの引数 |

- 戻り値: 作ったオブジェクトへのポインタ
- **メモリは確保しません**。すでにある領域の中でコンストラクタを呼ぶだけです
- 後始末は `delete` ではなく、**デストラクタを直接呼ぶ**（`p->~T();`）。そのあと、領域は自分で返します。
- コンテナ、プール、アロケータの内部で使われています。通常のコードでは不要です

```cpp
#include <cstddef>
#include <new>
#include <print>

struct Bullet {
  Bullet(float x, float y) : x(x), y(y) {}
  float x, y;
};

int main() {
  // Bullet 2 個ぶんの領域を、先にまとめて確保しておく（まだ Bullet ではない）
  alignas(Bullet) std::byte storage[sizeof(Bullet) * 2];

  Bullet* a = new (storage) Bullet(1.0f, 2.0f);                       // 1 個目の場所
  Bullet* b = new (storage + sizeof(Bullet)) Bullet(3.0f, 4.0f);      // 2 個目の場所
  std::println("{} {} / {} {}", a->x, a->y, b->x, b->y);

  a->~Bullet();  // デストラクタを呼ぶ（領域 storage は配列なので、自動で戻る）
  b->~Bullet();
}
```

```text title="実行結果"
1 2 / 3 4
```

### std::construct_at <span class="ver ver-20">C++20</span> {#construct_at data-toc-label="std::construct_at"}

```cpp
template <class T, class... Args>
constexpr T* construct_at(T* p, Args&&... args);
```

| 引数 | 意味 |
| --- | --- |
| `p` | 作る場所 |
| `args...` | コンストラクタの引数 |

- 戻り値: `p`
- 配置 new を、`::new` と間違えにくく書ける関数です。`constexpr` の中でも使えます。**配置 new が必要なら、こちらを優先**します

### std::destroy_at <span class="ver ver-17">C++17</span> {#destroy_at data-toc-label="std::destroy_at"}

```cpp
template <class T>
constexpr void destroy_at(T* p);
template <class It>
constexpr void destroy(It first, It last);
```

| 引数 | 意味 |
| --- | --- |
| `p` | 破棄するオブジェクト |
| `first`, `last` | 破棄する範囲 |

- 戻り値: なし
- デストラクタを呼びます。メモリは返しません。`p->~T();` の代わりに書けて、`T` が変わっても書き換える場所が減ります
- `std::destroy(first, last)` で、範囲の全部をまとめて破棄できます

### operator new / operator delete {#operator_new data-toc-label="operator new と operator delete"}

```cpp
void* operator new(std::size_t size);
void* operator new(std::size_t size, std::align_val_t alignment);   // C++17
void* operator new(std::size_t size, const std::nothrow_t&) noexcept;
void  operator delete(void* p) noexcept;
void  operator delete(void* p, std::size_t size) noexcept;          // サイズ付き（C++14）
```

| 引数 | 意味 |
| --- | --- |
| `size` | 確保するバイト数 |
| `alignment` | 置き場所の約束 |
| `p` | 解放するポインタ |

- 戻り値: 確保した領域の先頭（コンストラクタは呼ばれない）
- `new` 式の「確保の部分」だけです。普通は `malloc` のような動きをします
- <strong>差し替えられます。</strong> ゲームのメモリ計測や、全体のアロケータ変更に使います。

```cpp
// グローバルの new をすべて差し替える（プロジェクトに 1 つだけ）
void* operator new(std::size_t size) {
  g_allocated_bytes += size;
  if (void* p = std::malloc(size)) return p;
  throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
```

- **クラスごとの `operator new`** も書けます。`class Bullet { static void* operator new(std::size_t); ... };` とすると、`new Bullet` のときだけ、そのクラス用のプールから取れます。
- 差し替えるときは、`new` と `delete` の**両方**を同じ方針で差し替えます（片方だけだと、別のところから確保したものを解放してしまいます）

### std::uninitialized_copy など {#uninitialized data-toc-label="uninitialized_copy など"}

```cpp
template <class In, class Out> Out uninitialized_copy(In first, In last, Out dest);
template <class It, class T> void uninitialized_fill(It first, It last, const T& value);
template <class It> void uninitialized_default_construct(It first, It last);
template <class It> void uninitialized_value_construct(It first, It last);
template <class In, class Out> Out uninitialized_move(In first, In last, Out dest);
```

| 引数 | 意味 |
| --- | --- |
| `first`, `last` | コピー元・埋める範囲 |
| `dest` | 作る先（**未初期化の領域**） |
| `value` | 埋める値 |

- 戻り値: `uninitialized_copy` などは、作り終えた最後の次の位置
- 未初期化の領域に、**配置 new でまとめて作る**関数です。`std::copy` は、すでにオブジェクトがある場所への**代入**ですが、こちらは**新しく作ります**。
- 途中で例外が出たら、そこまで作ったものを自動で破棄してくれます（例外安全）。`vector` の再確保が、これを使っています

### std::launder <span class="ver ver-17">C++17</span> {#launder data-toc-label="std::launder"}

```cpp
template <class T>
[[nodiscard]] constexpr T* launder(T* p) noexcept;
```

| 引数 | 意味 |
| --- | --- |
| `p` | 同じ場所に新しく作ったオブジェクトを指すポインタ |

- 戻り値: その場所にある**新しいオブジェクト**を正しく指すポインタ
- `const` メンバや参照メンバを持つクラスを、同じ場所で作り直したとき、古いポインタをそのまま使うと未定義動作になることがあります。そのときのための関数で、普通のコードでは使いません

### std::align_val_t {#align_val_t data-toc-label="std::align_val_t"}

```cpp
struct alignas(64) CacheLine {
  float data[16];
};
auto* p = new CacheLine;  // C++17 以降、64 バイト境界で確保される
```

- C++17 から、`alignas` で大きなアラインメントを指定した型を `new` すると、**正しい位置**に確保されます（それまでは、`new` が合わせてくれないことがありました）
- `aligned_alloc` で C スタイルに取ることもできます（[malloc / free](c-memory.md#aligned_alloc)）

## 例外安全：new を複数使うとき

```cpp
// × 危ない：2 つ目の new が例外を投げると、1 つ目がリークする（関数の引数の評価順が未定）
Process(new Enemy(1), new Enemy(2));

// ○ 安全：make_unique ならリークしない
Process(std::make_unique<Enemy>(1), std::make_unique<Enemy>(2));
```

## 速さの特徴

| 項目 | 特徴 |
| --- | --- |
| `new` / `delete` | ヒープへの確保・解放。1 回数十〜数百ナノ秒かかり、時間も一定ではない |
| 小さいオブジェクトを大量に `new` | 遅く、メモリも散らばる（[キャッシュ効率](../../basics/cache.md)） |
| 配置 new | メモリの確保が無いので、コンストラクタを呼ぶ時間だけ |
| 対策 | `std::vector` にまとめる、[プール](pmr.md)、[オブジェクトプール](../../engine/object-pool.md) |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 敵・弾の動的な生成 | `std::make_unique`。大量なら [オブジェクトプール](../../engine/object-pool.md) |
| 弾・エフェクトを使い回す | 先にまとめて確保して、配置 new / `construct_at` で作り直す |
| 確保回数の計測 | グローバルの `operator new` を差し替えて数える |
| キャッシュラインをそろえたデータ | `alignas(64)` を付けた型を `new` する |

## よくあるミス

??? failure "`delete` を書き忘れる（メモリリーク）"
    関数の途中で `return` したり、例外が出たりすると、`delete` に届きません。`std::unique_ptr` にします。

??? failure "同じポインタを 2 回 delete する（二重解放）"
    ```cpp
    Enemy* a = new Enemy(10);
    Enemy* b = a;
    delete a;
    delete b;  // 同じものをもう一度消している。未定義動作
    ```
    所有者を 1 人に決めて、他は借りるだけ（生ポインタか参照）にします（[所有権](../../basics/ownership.md)）。

??? failure "`new[]` を `delete` で消す"
    `int* a = new int[10]; delete a;` は未定義動作です。`delete[] a;` と書きます。分からないなら、`std::vector` を使います。

??? failure "`malloc` したものを `delete`、`new` したものを `free`"
    確保と解放の組は、**必ず同じ系統**にそろえます。`new` ↔ `delete`、`new[]` ↔ `delete[]`、`malloc` ↔ `free`。

??? failure "配置 new した場所に、デストラクタを呼ばない"
    配置 new で作ったオブジェクトは、`delete` できません。デストラクタを自分で呼ばないと、中のリソース（`std::string` のメモリなど）が漏れます。

??? failure "アラインメントが足りない場所に配置 new する"
    `char buffer[sizeof(T)]` の上に `T` を作ると、アラインメント違反で壊れることがあります。`alignas(T) std::byte buffer[sizeof(T)];` と書きます。

## 理解度チェック

!!! question "Q1. `Enemy* e = new Enemy[3]; delete e;` の何が問題？"
    <div class="spoiler" markdown>

    **答え:** `new[]` で作ったものは `delete[]` で消す必要があります。`delete e;` では先頭の 1 個のデストラクタしか呼ばれず、未定義動作です。そもそも `std::vector<Enemy>` を使うほうが安全です。

    </div>

!!! question "Q2. 配置 new で作ったオブジェクトを破棄するには？"
    <div class="spoiler" markdown>

    **答え:** `p->~T();`（または `std::destroy_at(p)`）でデストラクタを呼びます。`delete p;` は、メモリも返そうとするのでダメです。領域は、確保した方法に合わせて別に返します。

    </div>

!!! question "Q3. `Process(new A, new B);` が危ないのはなぜ？"
    <div class="spoiler" markdown>

    **答え:** 引数の評価順は決まっていないので、`new A` のあとに `new B` が例外を投げると、`A` が `delete` されずにリークするからです。`std::make_unique` を使えば、確保した時点で所有者がいるので安全です。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_unique`](../utilities/unique_ptr.md) | `new` と所有を一緒にやる。通常はこちら |
| [`malloc` / `free`](c-memory.md) | C の確保関数。コンストラクタ・デストラクタは呼ばれない |
| [`std::allocator`](allocator.md) | 確保だけ（作成は別）。`new` を分解したもの |
| [`std::vector`](../containers/vector.md) | 配列の確保・作成・破棄を全部任せられる |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 生の `new` / `delete` は書かない。`std::make_unique` と `std::vector`
    - [x] `new` ＝ 確保 + 作成、`delete` ＝ 破棄 + 解放
    - [x] `new[]` は `delete[]`。`new` と `malloc` の系統は混ぜない
    - [x] 配置 new は「確保済みの場所に作る」。後始末は `destroy_at`（デストラクタ）
    - [x] 配置 new が必要なら、`std::construct_at` を使う

## 関連ページ

- [std::allocator](allocator.md)
- [std::pmr](pmr.md)
- [malloc / free（C 由来のメモリ確保）](c-memory.md)
- [std::unique_ptr](../utilities/unique_ptr.md)
- [所有権](../../basics/ownership.md)
- [cppreference: new 式](https://en.cppreference.com/w/cpp/language/new)

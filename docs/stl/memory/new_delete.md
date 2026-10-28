---
title: new と delete・配置 new
summary: "メモリの確保と、オブジェクトの作成・破棄。配置 `new`、`construct_at` も含む。"
order: 59
tags:
  - メモリ
---

# new と delete・配置 new

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>` / `#include <memory>`
</div>

ゲームのオブジェクトを関数を抜けたあとも生かしたいとき、ヒープ（自由に使えるメモリ領域）に置く必要があります。`new` は、メモリを確保して、そこにオブジェクトを作る演算子です。`delete` は、オブジェクトを破棄して、メモリを返す演算子です。基本の仕組みですが、`delete` の書き忘れはメモリリークに二重の `delete` はクラッシュにつながります。いまの C++ では、`new` の結果を生のポインターで持たず、`make_unique` に任せます。

!!! tip "ポイント"
    - <strong>生の `new` / `delete` を書かない。</strong> 1 個なら `std::make_unique<T>(...)`、複数なら `std::vector<T>`。
    - `new` は「**確保 + コンストラクタ呼び出し**」、`delete` は「**デストラクタ呼び出し + 解放**」の 2 段階。
    - **`new[]` で作ったものは `delete[]`** で消す（`delete` ではなく）。1 個の `new` は `delete`。
    - `malloc` / `free` と **混ぜない**（[malloc / free](malloc.md)）。
    - 確保済みの場所にオブジェクトを作る **配置 new** は、プールやアロケータの内部で使う。普通は `std::construct_at` を使うほうが安全。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md)、[所有権](../../basics/ownership.md)、[unique_ptr](../utilities/unique_ptr.md) を先に読んでください。メモリの置き場所の話は [キャッシュ効率](../../basics/cache.md) とつながります。

## 4 つの組み合わせ

<svg class="fig" viewBox="0 0 640 250" role="img" aria-label="スタックとヒープ"><defs><marker id="h1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">スタック（自動で片付く）</text><rect x="30" y="40" width="190" height="150" fill="none" stroke="currentColor" stroke-width="2"/><rect x="40" y="50" width="170" height="36" fill="rgba(76,139,245,0.3)" stroke="currentColor"/><text x="50" y="73">int a = 5</text><rect x="40" y="94" width="170" height="36" fill="rgba(76,139,245,0.3)" stroke="currentColor"/><text x="50" y="117">Enemy* p（ポインタ）</text><text x="30" y="215">関数を出ると、自動で消える</text><text x="330" y="20" class="fig-title">ヒープ（new で確保・delete で解放）</text><rect x="340" y="40" width="250" height="150" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/><rect x="400" y="80" width="130" height="50" fill="rgba(229,72,77,0.3)" stroke="currentColor"/><text x="412" y="110">Enemy の実体</text><line x1="210" y1="112" x2="398" y2="108" stroke="currentColor" stroke-width="2" marker-end="url(#h1)" /><text x="260" y="98">指す</text><text x="340" y="215">delete を忘れると、消えない（リーク）</text><text x="340" y="235">ポインタが先に消えると、場所が分からなくなる</text></svg>

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
| [`new` 式](new_delete/new.md) | <span class="rank rank-often">よく使う</span> | 確保 + 作成 |
| [`delete` 式](new_delete/delete.md) | <span class="rank rank-often">よく使う</span> | 破棄 + 解放 |
| [`new[]` / `delete[]`](new_delete/new_array.md) | <span class="rank rank-sometimes">たまに</span> | 配列の確保・解放 |
| [`std::nothrow`](new_delete/nothrow.md) | <span class="rank rank-sometimes">たまに</span> | 失敗したとき例外ではなく `nullptr` を返す |
| [配置 new](new_delete/placement_new.md) | <span class="rank rank-sometimes">たまに</span> | 確保済みの場所に作る |
| [`std::construct_at`](new_delete/construct_at.md) <span class="ver ver-20">C++20</span> | <span class="rank rank-sometimes">たまに</span> | 配置 new の安全な書き方 |
| [`std::destroy_at`](new_delete/destroy_at.md) <span class="ver ver-17">C++17</span> | <span class="rank rank-sometimes">たまに</span> | デストラクタだけを呼ぶ |
| [`operator new` / `operator delete`](new_delete/operator_new.md) | <span class="rank rank-rare">知ってるだけ</span> | 確保だけ・解放だけ、差し替え |
| [`std::uninitialized_copy` など](new_delete/uninitialized_copy.md) | <span class="rank rank-rare">知ってるだけ</span> | 未初期化の領域にまとめて作る |
| [`std::launder`](new_delete/launder.md) <span class="ver ver-17">C++17</span> | <span class="rank rank-rare">知ってるだけ</span> | 同じ場所に作り直したオブジェクトを指し直す |
| [`std::align_val_t`](new_delete/align_val_t.md) <span class="ver ver-17">C++17</span> | <span class="rank rank-rare">知ってるだけ</span> | アラインメントを指定した確保 |

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
| 対策 | `std::vector` にまとめる、[プール](pmr.md)、[オブジェクトプール](../../design/patterns/object-pool.md) |

## ゲームでの使いどころ

通常のゲームのコードでは、`new` や `delete` を直接書く場面は、ほとんどありません。オブジェクトの持ち主は、`std::make_unique` と `unique_ptr` で表し、可変長の配列は `std::vector` を使います。

直接使うのは、メモリを自分で管理するときです。オブジェクトプールのように、あらかじめ確保した大きな領域の中にオブジェクトを作りたいとき、配置 `new` や `std::construct_at` で、決まった場所にオブジェクトを作ります。この場合、破棄は `std::destroy_at` で行います。

エンジンの内部で、独自のアロケーターを書くときも、これらの知識が必要です。`new` が「確保」と「構築」の 2 段階であることを理解していると、仕組みが追いやすくなります。

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

??? failure "配置 new した場所にデストラクタを呼ばない"
    配置 new で作ったオブジェクトは、`delete` できません。デストラクタを自分で呼ばないと、中のリソース（`std::string` のメモリなど）が漏れます。

??? failure "アラインメントが足りない場所に配置 new する"
    `char buffer[sizeof(T)]` の上に `T` を作ると、アラインメント違反で壊れることがあります。`alignas(T) std::byte buffer[sizeof(T)];` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_unique`](../utilities/unique_ptr.md) | `new` と所有を一緒にやる。通常はこちら |
| [`malloc` / `free`](malloc.md) | C の確保関数。コンストラクタ・デストラクタは呼ばれない |
| [`std::allocator`](allocator.md) | 確保だけ（作成は別）。`new` を分解したもの |
| [`std::vector`](../containers/vector.md) | 配列の確保・作成・破棄を全部任せられる |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 生の `new` / `delete` を書かない。`make_unique` か `vector` を使う。
    - [x] `new[]` で作ったものは `delete[]` で消す。
    - [x] 確保と構築は別の段階。配置 `new` で、確保済みの場所に作れる。

## 関連ページ

- [std::allocator](allocator.md)
- [std::pmr](pmr.md)
- [malloc / free（C 由来のメモリ確保）](malloc.md)
- [std::unique_ptr](../utilities/unique_ptr.md)
- [所有権](../../basics/ownership.md)
- [cppreference: new 式](https://en.cppreference.com/w/cpp/language/new)

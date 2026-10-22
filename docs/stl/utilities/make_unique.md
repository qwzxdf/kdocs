---
title: std::make_unique
summary: "オブジェクトを作って unique_ptr にする。普通はこれで unique_ptr を作る。"
order: 47
tags:
  - ユーティリティ
---

# std::make_unique

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-14">C++14</span>
`#include <memory>`
</div>

ゲームのオブジェクトを `new` で作って、持ち主を 1 人に決めたいときは `unique_ptr` を使います。`std::unique_ptr<Enemy> e(new Enemy(hp))` と書くと、型名が 2 回出てきて、`new` が目に入ります。`std::make_unique<Enemy>(hp)` は、これを 1 回の型名で書ける関数です。`new` と `delete` を直接書かないので、解放のし忘れも起きません。

!!! tip "ポイント"
    - `new` を直接書かずに、`std::make_unique<T>(コンストラクターの引数)` で作る。
    - 配列は `std::make_unique<T[]>(個数)` で作る。全要素が 0 などに初期化される。
    - 共有が必要になるまでは、`shared_ptr` ではなく `unique_ptr` を選ぶ。

!!! info "このページを読む前に"
    [`std::unique_ptr`](unique_ptr.md) の「持ち主が 1 人」という考え方を先に読んでください。

## 関数の詳しい説明

### std::make_unique <span class="ver ver-14">C++14</span> {#make_unique data-toc-label="std::make_unique"}

```cpp
template <class T, class... Args>
std::unique_ptr<T> make_unique(Args&&... args);

template <class T>
std::unique_ptr<T> make_unique(std::size_t size);  // T が配列 U[] のとき
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 何個でも | `T` のコンストラクタにそのまま渡す引数 |
| `size` | `std::size_t` | 配列版の要素数 |

`args` は、`T` のコンストラクターにそのまま転送されます。`make_unique<std::string>(3, 'a')` なら `std::string(3, 'a')` が呼ばれます。引数を渡さなければ値初期化になり、`int` なら 0 です。

波かっこ初期化は転送されません。丸かっこで呼ばれるので、コンストラクターを持たない構造体に使えるのは C++20 からです。

配列版の `size` は、要素の数です。`make_unique<int[]>(100)` で、100 個の `int` がすべて 0 に初期化された配列ができます。配列版は、要素の数が実行時に決まるときに使います。数が固定なら `std::array` のほうが簡単です。

- 戻り値: 新しく作ったオブジェクトを持つ unique_ptr
- 例外: メモリ不足なら `std::bad_alloc`

<div class="anim" data-label="auto p = std::make_unique<Enemy>()">
_ # p は空
+A # Enemy を作り、p が所有する
</div>

```cpp
#include <memory>
#include <print>

struct Vec2 {
  float x;
  float y;
};

int main() {
  auto pos = std::make_unique<Vec2>(1.0f, 2.0f);
  std::println("({}, {})", pos->x, pos->y);
}
```

```text title="実行結果"
(1, 2)
```

!!! note "実際は"
    `new` を書く場面は、ほぼすべて `make_unique` に置き換えられます。

### std::make_unique_for_overwrite <span class="ver ver-20">C++20</span> {#make_unique_for_overwrite data-toc-label="std::make_unique_for_overwrite"}

```cpp
template <class T>
unique_ptr<T> make_unique_for_overwrite();
template <class T>
unique_ptr<T> make_unique_for_overwrite(size_t n);  // T[] 用
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | size_t | 配列の要素数（`T[]` のとき） |

- 戻り値: `unique_ptr<T>`
- 計算量: 確保 1 回 + 初期化（なし）

`make_unique<int[]>(n)` は全要素を 0 で値初期化します。`make_unique_for_overwrite` は**初期化せず**確保だけします（`int` なら中身は不定）。あとで全部上書きすると分かっている大きな配列で、0 埋めの時間を省けます。

## しくみ

`unique_ptr` は、中に生ポインターを 1 つ持っているだけの小さなオブジェクトです。コピーはできず、ムーブだけができます。ムーブすると、元のポインターは `nullptr` になり、持ち主が移ります。スコープを抜けるとき、持ち主のデストラクターが `delete` を呼びます。

`make_unique` が例外に強いのは、`new` から `unique_ptr` への受け渡しが関数の中で完結するからです。`f(std::unique_ptr<A>(new A), g())` のように書いた場合、C++14 までは `g()` が例外を投げるとリークする可能性がありました（C++17 で評価順が決まり、起きなくなりました）。`make_unique` を使えば、どの版でも気にする必要がありません。

`shared_ptr` の `make_shared` とは違って、メモリの確保が 1 回になる、という違いはありません。`unique_ptr` には参照カウントがないので、`new` で作るのと同じ 1 回の確保です。

## ゲームでの使いどころ

エンジンの中で、1 つの場所だけが持つオブジェクトに使います。シーンが持つカメラ、プレイヤーが持つ入力処理、ゲームが持つレンダラーなどです。`std::unique_ptr<Renderer> renderer_ = std::make_unique<Renderer>(device);` と書いておけば、ゲームが終わるときに自動で解放されます。

ポリモーフィズム（基底クラスのポインターで派生クラスを扱う）にもよく使います。`std::vector<std::unique_ptr<Enemy>>` に、`Slime`、`Goblin` のような派生クラスを `make_unique` で作って入れます。`vector` が破棄されるとき、全員が正しく解放されます。基底クラスのデストラクターは `virtual` にしておきます。

他の場所に渡したいときは、`std::move` で持ち主を移します。見るだけの相手には、`unique_ptr` ではなく生ポインターや参照を渡します（持ち主は変わりません）。

## よくあるミス

??? failure "`unique_ptr` をコピーしようとする"
    `auto b = a;` はコンパイルエラーです。`unique_ptr` はコピーできません。持ち主を移すなら `auto b = std::move(a);` と書きます。移したあとの `a` は `nullptr` なので、使わないようにします。

??? failure "`get()` で取り出した生ポインターを `delete` する"
    `p.get()` は、持ち主を変えずにポインターを見せるだけです。これを `delete` すると、`unique_ptr` のデストラクターが二重に `delete` して未定義動作になります。`release()` で持ち主を手放してから、自分で `delete` する書き方もありますが、普通は必要ありません。

??? failure "`make_unique<Base>(Derived{})` のつもりで書く"
    `make_unique<T>` は `T` を作ります。派生クラスを作って基底クラスの `unique_ptr` に入れるなら、`std::unique_ptr<Base> p = std::make_unique<Derived>(...);` と書きます。派生クラスから基底クラスへの変換は暗黙に行われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_shared`](make_shared.md) | `shared_ptr` を作る。複数の持ち主が必要なときだけ使う |
| [`std::unique_ptr`](unique_ptr.md) | 作られる側。デリーターの指定や配列の扱いを説明している |
| `new` | 直接書くのは、`unique_ptr` にデリーターを渡すときなど、まれな場面だけ |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `unique_ptr` は `make_unique` で作る。`new` を直接書かない。
    - [x] コピーはできない。持ち主を移すときは `std::move`。
    - [x] 共有が必要になるまでは `shared_ptr` を使わない。

## 関連ページ

- [cpprefjp: std::make_unique](https://cpprefjp.github.io/reference/memory/make_unique.html)
- [cppreference: std::make_unique](https://en.cppreference.com/w/cpp/memory/unique_ptr/make_unique)

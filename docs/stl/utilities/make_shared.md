---
title: std::make_shared
summary: "オブジェクトを作って shared_ptr にする。普通はこれで shared_ptr を作る。"
order: 51
tags:
  - ユーティリティ
---

# std::make_shared

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`shared_ptr` を作るとき、`std::shared_ptr<Enemy> p(new Enemy(hp))` と書くと、`new` と `shared_ptr` の 2 か所に同じ型名が出てきます。しかも、この書き方は裏でメモリの確保を 2 回行います。`std::make_shared<Enemy>(hp)` は、この 2 つをまとめて、短く書けて確保も 1 回で済む関数です。共有ポインターを作るなら、まずこちらを使います。

!!! tip "ポイント"
    - `new` を直接書かずに、`std::make_shared<T>(コンストラクターの引数)` で作る。9 割はこれだけで足りる。
    - オブジェクトと参照カウントを 1 回の確保で作るので、`new` を使う書き方より速く、メモリの断片化も減る。
    - 自作のデリーターを渡したいとき、または private なコンストラクターを呼びたいときだけ、`shared_ptr<T>(new T, deleter)` を使う。

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) の「参照カウントで持ち主を数える」仕組みを先に読んでください。このページの「しくみ」は、その続きの話です。

## 関数の詳しい説明

### std::make_shared {#make_shared}

```cpp
template <class T, class... Args>
std::shared_ptr<T> make_shared(Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 何個でも | `T` のコンストラクタ引数 |

`args` は、`T` のコンストラクターにそのまま転送されます。`make_shared<std::string>(3, 'a')` なら `std::string(3, 'a')` が呼ばれて `"aaa"` になります。引数を 1 つも渡さなければ値初期化になり、`int` なら 0 に初期化されます。

波かっこ初期化（`T{1, 2}`）は転送されません。中では丸かっこ（`T(1, 2)`）で呼ばれます。C++20 からは、コンストラクターを持たない構造体（集成体）にも丸かっこで初期化できるので、`make_shared<Point>(1, 2)` が書けます。C++17 までは、集成体にはコンストラクターを書く必要があります。

型は `T` を必ず書きます。`make_shared(Enemy(5))` のような推論はできません。

`args` は、`T` のコンストラクターにそのまま転送されます。`make_shared<std::string>(3, 'a')` なら `std::string(3, 'a')` が呼ばれて `"aaa"` になります。引数を 1 つも渡さなければ値初期化になり、`int` なら 0 に初期化されます。

波かっこ初期化（`T{1, 2}`）は転送されません。中では丸かっこ（`T(1, 2)`）で呼ばれます。C++20 からは、コンストラクターを持たない構造体（集成体）にも丸かっこで初期化できるので、`make_shared<Point>(1, 2)` が書けます。C++17 までは、集成体にはコンストラクターを書く必要があります。

型は `T` を必ず書きます。`make_shared(Enemy(5))` のような推論はできません。

- オブジェクトと参照カウントを**1 回の確保**でまとめて作ります（`new` してから shared_ptr に渡すより速い）

<div class="anim" data-label="auto p = std::make_shared<Enemy>()">
_ # p は空
+A:1 # 作って、参照数は 1
</div>

### std::make_shared_for_overwrite <span class="ver ver-20">C++20</span> {#make_shared_for_overwrite data-toc-label="std::make_shared_for_overwrite"}

```cpp
template <class T>
shared_ptr<T> make_shared_for_overwrite();
template <class T>
shared_ptr<T> make_shared_for_overwrite(size_t n);  // T[] 用
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | size_t | 配列の要素数（`T[]` のとき） |

- 戻り値: `shared_ptr<T>`
- 計算量: 確保 1 回 + 初期化（なし）

`make_shared<int[]>(n)` は全要素を 0 で値初期化します。`make_shared_for_overwrite` は**初期化せず**確保だけします。あとで全部上書きする大きな配列で、0 埋めを省くために使います。

## しくみ

`shared_ptr` は、参照カウントを入れた小さな領域（制御ブロック）をオブジェクトとは別に持っています。`new` を使う書き方では、オブジェクトの確保と制御ブロックの確保が別々に起きます。`make_shared` は、この 2 つを 1 回の大きな確保にまとめて、先頭に制御ブロック、続けてオブジェクトを置きます。

<div class="anim" data-label="確保の回数">
*Enemy | *制御 # shared_ptr<Enemy>(new Enemy) は、2 か所に別々に確保する
*制御 *Enemy # make_shared<Enemy>() は、1 回の確保に並べて置く
</div>

確保が 1 回で済むのは、速さだけの話ではありません。2 つが隣り合うので、参照カウントを増減するときにキャッシュに乗りやすくなります。

この作りには、1 つだけ副作用があります。オブジェクトのデストラクターは、強い参照（`shared_ptr`）が 0 になった時点で呼ばれます。ところが、メモリそのものは、弱い参照（`weak_ptr`）も 0 になるまで解放できません。制御ブロックとオブジェクトが同じ領域にあるからです。`weak_ptr` が長く生き残ると、中身が死んだ後も、サイズの大きいオブジェクトの分のメモリが残ります。

例外に対する安全性についても触れておきます。C++14 までは、`f(shared_ptr<T>(new T), g())` と書くと、`new T` のあとで `g()` が例外を投げたとき、`new` したメモリが誰にも持たれずにリークする可能性がありました。C++17 で引数の評価順の規則が変わり、この問題は起きなくなりました。ただし、`make_shared` を使っていれば、規格の版を気にする必要がありません。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  auto p = std::make_shared<int>(5);
  auto q = p;   // 持ち主が 2 人になる
  std::println("{} {}", *p, p.use_count());
}
```

```text title="実行結果"
5 2
```

## make_shared を使えない場面

次の 3 つの場合は、`shared_ptr<T>(new T(...), ...)` と書きます。

1 つ目は、自作のデリーターを渡したいときです。`make_shared` はデリーターを受け取りません。ファイルハンドルを `fclose` で閉じるような場面で、`shared_ptr<FILE>(fopen(...), fclose)` と書きます。

2 つ目は、コンストラクターが private のときです。`make_shared` は、`T` の外から `new` に相当する処理をするので、private のコンストラクターを呼べません。ファクトリー関数の中で `shared_ptr<T>(new T)` と書くのが定番です。

```cpp
#include <memory>
#include <print>

class Config {
 public:
  // 作り方を static 関数に限定する。コンストラクターは外から呼ばせない
  static std::shared_ptr<Config> Create(int level) {
    // make_shared<Config>(level) は private のコンストラクターを呼べないので new を使う
    return std::shared_ptr<Config>(new Config(level));
  }
  int level() const { return level_; }

 private:
  explicit Config(int level) : level_(level) {}
  int level_;
};

int main() {
  auto c = Config::Create(3);
  auto d = c;  // 同じ制御ブロックを共有する
  std::println("{} {}", c->level(), c.use_count());
}
```

```text title="実行結果"
3 2
```

3 つ目は、独自のアロケーターでメモリを取りたいときです。この場合は [`allocate_shared`](allocate_shared.md) を使います。

## ゲームでの使いどころ

共有するリソースの作成がいちばん多い使いどころです。テクスチャやメッシュのように、複数のオブジェクトが同じものを指すとき、リソース管理クラスの中で `auto tex = std::make_shared<Texture>(path);` と作って、必要な場所に `shared_ptr` を配ります。最後の持ち主が手放した時点で、自動的に解放されます。

シーンのオブジェクト間の参照では、`shared_ptr` を増やしすぎないことが大切です。親が子を `shared_ptr` で持ち、子も親を `shared_ptr` で持つと、お互いが生き残らせ合って解放されません。逆向きの参照（子から親）は [`weak_ptr`](weak_ptr.md) にします。

毎フレーム大量に作る小さなオブジェクト（弾やエフェクトなど）には、`make_shared` でも確保のコストは小さくありません。数が多い場合は、オブジェクトプールや `vector` に入れて、番号で参照するほうが速くなります。

## よくあるミス

??? failure "`new` を直接 `shared_ptr` に渡す"
    `std::shared_ptr<Enemy> p(new Enemy(5));` は動きますが、確保が 2 回になり、型名も 2 回書くことになります。C++14 以前では例外安全性の問題もあります。迷ったら `make_shared` に書き換えます。

??? failure "同じ生ポインターから、2 つの `shared_ptr` を作る"
    ```cpp
    Enemy* raw = new Enemy(5);
    std::shared_ptr<Enemy> a(raw);
    std::shared_ptr<Enemy> b(raw);  // 別の制御ブロックができて、二重に delete される
    ```
    `shared_ptr` 同士は、コピーでしか制御ブロックを共有できません。生ポインターから作り直すと、参照カウントが別になり、片方が解放したあともう片方が `delete` して未定義動作になります。最初から `make_shared` で作れば、生ポインターが手元に残らないので、この間違いを避けられます。

??? failure "`weak_ptr` が残っているのにメモリが減らない"
    「しくみ」で説明したとおり、`make_shared` で作ったオブジェクトは、`weak_ptr` が残る間、メモリそのものが解放されません。大きなオブジェクトで長く生きる `weak_ptr`（キャッシュなど）を持つ場合は、`shared_ptr<T>(new T)` に切り替えると、オブジェクトの分のメモリだけ先に返せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_unique`](make_unique.md) | `unique_ptr` を作る。持ち主が 1 人でよいなら、こちらを先に考える |
| [`std::shared_ptr`](shared_ptr.md) | 作られる側。参照カウントと弱い参照の仕組みを説明している |
| [`std::allocate_shared`](allocate_shared.md) | アロケーターを指定して作る。`pmr` やプールのメモリを使うとき |
| [`std::enable_shared_from_this`](enable_shared_from_this.md) | 自分自身を指す `shared_ptr` を作れるようにする。`make_shared` で作ったものに使う |

## コンパイラ対応

C++11 から使えます。配列版（`make_shared<T[]>`）は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `shared_ptr` は `new` を書かずに `make_shared` で作る。確保が 1 回になる。
    - [x] デリーターの指定、private なコンストラクター、独自のアロケーターのときだけは使えない。
    - [x] `weak_ptr` が残ると、オブジェクトが死んだ後もメモリは残る。

## 関連ページ

- [cpprefjp: std::make_shared](https://cpprefjp.github.io/reference/memory/make_shared.html)
- [cppreference: std::make_shared](https://en.cppreference.com/w/cpp/memory/shared_ptr/make_shared)

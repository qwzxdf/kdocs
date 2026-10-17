---
title: malloc / free（C 由来のメモリ確保）
tags:
  - メモリ
  - C由来
---

# malloc / free（C 由来のメモリ確保）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C 言語由来</span>
`#include <cstdlib>`
</div>

**`malloc`** と **`free`** は、C 言語から引き継いでいる**メモリ確保・解放の関数**です。C++ の [`new` / `delete`](new_delete.md) と違って、**ただの「メモリの塊」を返すだけ**で、コンストラクタもデストラクタも呼びません。C++ の普通のコードでは使いません（`std::vector` や `std::make_unique` を使います）が、**C のライブラリ（OS の API、画像・音声ライブラリ、ゲーム機の SDK）が `malloc` で確保したものを `free` で返す**約束になっていることが多いので、仕組みと注意点を知っておく必要があります。また、昔のコードや、C との橋渡しをするコードを読むときに必ず出てきます。

!!! tip "ポイント"
    - <strong>自分のコードでは `malloc` / `free` を使わない。</strong> `std::vector`、`std::make_unique`、`std::unique_ptr<T[]>` を使う。
    - 使うのは、**C のライブラリが `malloc` 前提のとき**（`free` で返す約束のものを受け取る）だけ。
    - <strong>`malloc` したものは `free`、`new` したものは `delete`。</strong> 混ぜると未定義動作。
    - `malloc` は**コンストラクタを呼ばない**。`std::string` など、クラスのオブジェクトを `malloc` した場所で使ってはいけない。
    - <strong>`p = realloc(p, n)` と書かない。</strong> 失敗すると元のポインタを失ってリークする。
    - 確保した大きさは **`sizeof(型) * 個数`**。ポインタの `sizeof` を取る間違いが多い。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md)、[`new` と `delete`](new_delete.md)、[未定義動作](../../basics/ub.md) を先に読んでください。`memcpy` など、確保した領域を操作する関数は [文字列・メモリ操作（cstring）](cstring.md) にあります。

## new / delete との違い

| 項目 | `malloc` / `free` | `new` / `delete` |
| --- | --- | --- |
| 何を返すか | `void*`（型なし。使う側で型変換が必要） | `T*`（型付き） |
| コンストラクタ・デストラクタ | **呼ばれない** | 呼ばれる |
| 大きさの指定 | **バイト数**（自分で `sizeof` を掛ける） | 型と個数（自動で計算） |
| 失敗したとき | `nullptr` を返す | 例外 `std::bad_alloc`（`nothrow` なら `nullptr`） |
| 初期化 | されない（`calloc` なら 0） | `new T()` / `new T{}` でされる |
| 後から大きさを変える | `realloc` できる | できない |
| 書ける型 | 数値・構造体など**単純な型だけ** | 何でも |

```text
malloc(40)     … 40 バイトの「生のメモリ」だけが返る（中身は不定、型もない）
new int[10]    … 40 バイトを確保 + int の初期化を 10 個ぶん行う
```

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`malloc`](#malloc) | <span class="rank rank-sometimes">たまに</span> | メモリを確保する |
| [`free`](#free) | <span class="rank rank-sometimes">たまに</span> | メモリを返す |
| [`calloc`](#calloc) | <span class="rank rank-rare">知ってるだけ</span> | 0 で埋めて確保する |
| [`realloc`](#realloc) | <span class="rank rank-rare">知ってるだけ</span> | 確保した大きさを変える |
| [`aligned_alloc`](#aligned_alloc) | <span class="rank rank-rare">知ってるだけ</span> | アラインメントを指定して確保する |
| [`_aligned_malloc`（MSVC）](#aligned_malloc_msvc) | <span class="rank rank-rare">知ってるだけ</span> | Windows でのアラインメント付き確保 |

## よくある使い方：C のライブラリから受け取ったメモリを返す

```cpp
#include <cstdlib>
#include <memory>
#include <print>

// C のライブラリを想定：呼び出し側が free で返す約束の関数
char* LoadTextFromLibrary() {
  char* text = static_cast<char*>(std::malloc(6));
  std::memcpy(text, "Hello", 6);  // 終端の '\0' まで 6 バイト
  return text;
}

int main() {
  // unique_ptr に「free で返す」という後始末を教える
  std::unique_ptr<char, decltype(&std::free)> text(LoadTextFromLibrary(), &std::free);
  std::println("{}", text.get());
}  // スコープを出ると自動で free が呼ばれる
```

```text title="実行結果"
Hello
```

C のライブラリが返したポインタを**すぐ `unique_ptr`（カスタムデリータ付き）に入れる**のが、C++ での安全な扱い方です。途中で `return` や例外があっても、`free` を忘れません。

## 関数の詳しい説明

### malloc {#malloc}

```cpp
void* malloc(std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `size` | `std::size_t` | 確保する**バイト数**（要素の数ではない） |

- 戻り値: 確保した領域の先頭。失敗したら `nullptr`。**中身は不定**（0 とは限らない）
- 計算量: ヒープ管理の実装による（普通は `new` と同程度）
- 返る領域は、どの基本型にも使える**アラインメント**（`alignof(std::max_align_t)`、普通は 16 バイト）にそろっています
- `size` が 0 のときは、`nullptr` か、使えないポインタが返ります（実装による）。`free` はできますが、使わないでください
- **C++ では `void*` を自動で他の型に変換できない**ので、`static_cast<int*>(malloc(...))` のようにキャストが必要です

```cpp
int* a = static_cast<int*>(std::malloc(10 * sizeof(int)));  // int を 10 個ぶん
if (a == nullptr) {
  return;  // 失敗（メモリ不足）。必ず確認する
}
a[0] = 5;
std::free(a);
```

!!! warning "sizeof の間違い"
    `std::malloc(sizeof(a))` の `a` がポインタだと、ポインタ自身の大きさ（8 バイト）しか確保されません。`sizeof(int) * 10` か、`sizeof(*a) * 10` と書きます。

### free {#free}

```cpp
void free(void* ptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `void*` | `malloc` / `calloc` / `realloc` / `aligned_alloc` が返したポインタ。`nullptr` なら何もしない |

- 戻り値: なし
- **必ず `malloc` 系で確保したポインタ**を渡します。`new` したものや、配列の途中のポインタ、スタックのアドレスを渡すのは未定義動作です
- **2 回 `free` するのは未定義動作**（二重解放）。`free` したあとは `ptr = nullptr;` にしておくと安全です（`free(nullptr)` は何もしないので）
- デストラクタは呼ばれません。`std::string` などのクラスを `malloc` で作っていたなら、先に自分でデストラクタを呼ぶ必要があります（普通はそんなことをしません）

### calloc {#calloc}

```cpp
void* calloc(std::size_t count, std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | `std::size_t` | 要素の数 |
| `size` | `std::size_t` | 1 要素のバイト数 |

- 戻り値: `count * size` バイトの領域。**すべて 0 で埋められている**。失敗したら `nullptr`
- `malloc(count * size)` + 0 埋め、と同じ意味ですが、**`count * size` がオーバーフローするときは、失敗（`nullptr`）として扱ってくれる**のが安全な点です
- 整数や構造体の配列を 0 で始めたいときに便利です。ただし、**浮動小数点やポインタの「全ビット 0」が 0.0 / `nullptr` とは限らない**環境がありえます（実際の PC やゲーム機ではそうなっています）

### realloc {#realloc}

```cpp
void* realloc(void* ptr, std::size_t new_size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `void*` | 以前に確保したポインタ。`nullptr` なら `malloc(new_size)` と同じ |
| `new_size` | `std::size_t` | 新しいバイト数 |

- 戻り値: 新しい領域の先頭。**元のポインタと同じとは限らない**（引っ越すことがある）。失敗したら `nullptr`（元の領域はそのまま残る）
- 中身は、小さい方の大きさまでコピーされます。**広げた部分は未初期化**です
- 引っ越したときは、古いポインタ（や、その中を指していたポインタ）は**無効**になります。[`vector` の再確保](../containers/vector.md#realloc)と同じ考え方です
- **コンストラクタを持つ型には使えません**。ビット単位でコピーされるだけで、ムーブコンストラクタが呼ばれないためです

```cpp
// × 失敗すると、元の領域を指すポインタを失ってリークする
data = static_cast<int*>(std::realloc(data, new_count * sizeof(int)));

// ○ 別の変数で受けてから、成功したら置き換える
void* bigger = std::realloc(data, new_count * sizeof(int));
if (bigger == nullptr) {
  std::free(data);  // 元の領域は残っているので、自分で返す
  return false;
}
data = static_cast<int*>(bigger);
```

### aligned_alloc {#aligned_alloc}

```cpp
void* aligned_alloc(std::size_t alignment, std::size_t size);  // C11 / C++17
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `alignment` | `std::size_t` | 先頭アドレスの約束（2 の累乗。64 ならキャッシュラインにそろう） |
| `size` | `std::size_t` | バイト数。**`alignment` の倍数**にする必要がある（実装による） |

- 戻り値: `alignment` の倍数のアドレスから始まる領域。失敗したら `nullptr`。`free` で返す
- SIMD（SSE / AVX）の命令や、キャッシュラインにそろえたいデータで使います
- **MSVC（Visual Studio）は `aligned_alloc` に対応していません**（Windows のヒープの仕様のため）。次の `_aligned_malloc` を使うか、`alignas` 付きの型を `new` します

### _aligned_malloc（MSVC） {#aligned_malloc_msvc data-toc-label="_aligned_malloc（MSVC）"}

```cpp
void* _aligned_malloc(std::size_t size, std::size_t alignment);  // 引数の順番が逆
void _aligned_free(void* ptr);                                    // free ではなくこちらで返す
```

| 引数 | 意味 |
| --- | --- |
| `size` | バイト数 |
| `alignment` | アラインメント |

- Windows（`<malloc.h>`）の、アラインメント付き確保です。**`aligned_alloc` と引数の順番が逆**で、解放も `_aligned_free` を使います（`free` で返すと壊れます）
- 移植したいなら、`alignas(64)` を付けた型を `new` する方法（C++17）が一番簡単です

## C++ での置き換え

| C のやり方 | C++ のやり方 |
| --- | --- |
| `int* a = malloc(n * sizeof(int));` | `std::vector<int> a(n);` |
| `T* p = malloc(sizeof(T));` | `auto p = std::make_unique<T>();` |
| `calloc(n, sizeof(int))` | `std::vector<int> a(n);`（0 で初期化される） |
| `realloc` で大きくする | `v.resize(n)` / `v.reserve(n)` |
| `malloc` した文字列 | `std::string` |
| C の API が `malloc` したものを返す | `std::unique_ptr<T, decltype(&std::free)>` で受ける |
| 配列を `free` で返す | `std::unique_ptr<T[]>` |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| C のライブラリ（stb_image など）が返す画像データ | 返されたポインタを、ライブラリの解放関数（`stbi_image_free` など）か `free` で返す。`unique_ptr` + カスタムデリータで包む |
| 昔のコードを読む | `malloc` / `memset` / `memcpy` の組み合わせを、`vector` や `std::copy` に置き換える |
| SIMD やキャッシュラインにそろえた確保 | `alignas(64)` を付けた型を `new`、またはアラインメント付きのアロケータ |
| 大量の同じ大きさのものの確保 | `malloc` を毎回呼ばず、[プールやアリーナ](pmr.md) を使う |

## よくあるミス

??? failure "`new` したものを `free`、`malloc` したものを `delete`"
    ヒープの管理方法が違うことがあり、未定義動作になります。組は必ずそろえます。`new` ↔ `delete`、`new[]` ↔ `delete[]`、`malloc` ↔ `free`。

??? failure "クラスのオブジェクトを `malloc` で作って使う"
    ```cpp
    std::string* s = static_cast<std::string*>(std::malloc(sizeof(std::string)));
    *s = "hello";  // コンストラクタが呼ばれていない領域に代入している。未定義動作
    ```
    コンストラクタが呼ばれていないので、`std::string` の中身は不定です。`new` か、[配置 new](new_delete.md#placement_new) を使います。

??? failure "`p = realloc(p, n)` と書く"
    失敗すると `nullptr` が返って `p` を上書きしてしまい、元のメモリを返せなくなります（リーク）。別の変数で受けて、確認してから置き換えます。

??? failure "確保したあとの `nullptr` チェックを忘れる"
    メモリ不足のとき `malloc` は `nullptr` を返します。確認せずに使うと、`nullptr` への書き込みでクラッシュします。

??? failure "`free` したあとのポインタを使う（use-after-free）"
    `free` した領域は、すぐ別の確保で再利用されます。読み書きすると、別のデータを壊します。`free` のあとは `ptr = nullptr;` にします。

??? failure "確保した大きさより後ろに書く（バッファオーバーラン）"
    `malloc(10)` で確保したのに 11 バイト目に書くと、ヒープの管理情報を壊します。のちの `free` や `malloc` で、**関係のない場所で**クラッシュします。`std::vector` と `at`、または `std::span` で範囲を守ります。

## 理解度チェック

!!! question "Q1. このコードの問題は？"
    ```cpp
    int* a = static_cast<int*>(std::malloc(10));
    a[9] = 1;
    ```

    <div class="spoiler" markdown>

    **答え:** `malloc` はバイト数なので、10 バイトしか確保されていません。`int` が 10 個ほしいなら `10 * sizeof(int)`（40 バイト）です。`a[9]` は 36〜39 バイト目なので、確保した範囲の外への書き込み（バッファオーバーラン）です。

    </div>

!!! question "Q2. C のライブラリが `malloc` で確保して返したデータを、`delete` してよい？"
    <div class="spoiler" markdown>

    **答え:** いけません。`malloc` ↔ `free` の組です（または、そのライブラリが用意した解放関数）。`unique_ptr<T, decltype(&std::free)>` で受ければ、`free` が自動で呼ばれます。

    </div>

!!! question "Q3. `realloc` で、他の変数が古いポインタを持っているとどうなる？"
    <div class="spoiler" markdown>

    **答え:** `realloc` が別の場所に引っ越すと、古いポインタは無効になります（ダングリングポインタ）。`std::vector` の再確保と同じです。ポインタではなく、番号（添字）で持つと安全です。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`new` / `delete`](new_delete.md) | 型付き。コンストラクタ・デストラクタを呼ぶ。C++ ではこちら |
| [`std::allocator`](allocator.md) | 確保だけを担当する C++ の仕組み。型付き |
| [`std::vector`](../containers/vector.md) | 確保・大きさ変更・解放をすべて任せられる |
| [文字列・メモリ操作](cstring.md) | `memcpy` など。`malloc` した領域を操作する |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自分のコードでは使わない。`vector`・`make_unique` を使う
    - [x] C のライブラリから受け取ったものは `unique_ptr` + `std::free` で包む
    - [x] `malloc` ↔ `free`、`new` ↔ `delete`、`new[]` ↔ `delete[]` を混ぜない
    - [x] `malloc` はコンストラクタを呼ばない。バイト数で指定する
    - [x] `realloc` は別の変数で受ける。`nullptr` チェックを忘れない

## 関連ページ

- [new と delete・配置 new](new_delete.md)
- [文字列・メモリ操作（cstring）](cstring.md)
- [std::allocator](allocator.md)
- [所有権](../../basics/ownership.md)
- [cppreference: malloc](https://en.cppreference.com/w/cpp/memory/c/malloc)

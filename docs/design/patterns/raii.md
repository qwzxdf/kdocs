---
title: RAII とスマートポインタ
tags:
  - 設計
---

# RAII とスマートポインタ

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

**RAII**（アールエーアイアイ、Resource Acquisition Is Initialization）は、C++ の設計の**中心になる考え方**です。「**リソース（メモリ、ファイル、ロック、GPU のバッファなど）の取得を、オブジェクトの作成（コンストラクタ）で行い、解放を、オブジェクトの破棄（デストラクタ）で行う**」というものです。C++ では、オブジェクトがスコープを出るとき、**必ずデストラクタが呼ばれます**（`return` でも、例外でも）。この性質を使うと、<strong>「解放し忘れ」がコードから消えます</strong>。スマートポインタ（`unique_ptr`、`shared_ptr`）は、RAII の代表例で、メモリを自動で解放してくれます。

!!! tip "ポイント"
    - <strong>「取る」と「返す」を、コンストラクタとデストラクタにまとめる</strong>。解放を、手で書かない。
    - メモリは<strong>スマートポインタ（`unique_ptr`）</strong>、配列は **`vector`**、文字列は **`string`**、ファイルは **`ifstream`**、ロックは **`lock_guard`**。全部 RAII。
    - 自作のリソース（GPU のバッファ、ソケット、OS のハンドル）も、**RAII のクラスで包む**。
    - `new` / `delete`、`fopen` / `fclose`、`lock` / `unlock` を、**自分で書かない**。
    - 資源の解放を忘れる・例外で飛ばされる、が起きなくなる。

## 悪い例：手で解放する

```cpp
void LoadLevel(const char* path) {
  FILE* file = std::fopen(path, "rb");
  if (!file) {
    return;
  }

  Level* level = new Level();
  if (!level->Read(file)) {
    return;              // ← file も level も解放していない（リーク）
  }
  Apply(*level);          // ← ここで例外が出ても、解放されない
  delete level;
  std::fclose(file);
}
```

### 何が困るか

| 問題 | 説明 |
| --- | --- |
| **途中の `return` で、解放が飛ぶ** | 出口が増えるたびに、全部の解放を書き足す必要がある |
| **例外で、解放が飛ぶ** | `Apply` が例外を投げると、`delete` に届かない |
| **解放を書き忘れる** | リークは、気づかれないまま溜まっていく |
| **二重解放** | 解放したものを、もう一度解放する |

## 良い例：RAII のクラスに任せる

```cpp
void LoadLevel(const std::string& path) {
  std::ifstream file(path, std::ios::binary);   // 取得：コンストラクタで開く
  if (!file) {
    return;                                      // 返す：自動で閉じる
  }

  auto level = std::make_unique<Level>();        // 取得：メモリ
  if (!level->Read(file)) {
    return;                                      // 返す：level も自動で解放
  }
  Apply(*level);                                 // 例外が出ても、解放される
}                                                // スコープを出るとき、逆順に自動で解放
```

<strong>解放のコードがありません。</strong> どの出口でも、例外でも、**逆の順番で（`level` → `file`）自動で解放**されます。

<div class="anim" data-label="RAII：スコープを出ると、逆順に自動で片付く">
file level _ # 関数に入る
+file _ _ # file を開く（コンストラクタ）
+file +level _ # level を確保（コンストラクタ）
file xlevel _ # スコープを出る：後に作った level が先に片付く
xfile _ _ # 次に file が片付く（デストラクタ）
</div>

## RAII の例

標準ライブラリは、ほとんどが RAII です。

| リソース | RAII のクラス | デストラクタがすること |
| --- | --- | --- |
| メモリ（1 個） | [`std::unique_ptr`](../../stl/utilities/unique_ptr.md) | `delete` |
| メモリ（共有） | [`std::shared_ptr`](../../stl/utilities/shared_ptr.md) | 最後の 1 人が `delete` |
| 動的な配列 | [`std::vector`](../../stl/containers/vector.md) | 要素のデストラクタと、メモリの解放 |
| 文字列 | [`std::string`](../../stl/containers/string.md) | メモリの解放 |
| ファイル | `std::ifstream` / `std::ofstream` | ファイルを閉じる |
| ロック | `std::lock_guard` / `std::scoped_lock` | ロックを解除 |
| スレッド | `std::jthread` | `join`（スレッドの終了を待つ） |
| 時間の計測 | 自作の `ScopedTimer` | 経過時間を出力 |

## 自作の RAII クラス

C の API やゲーム機の SDK のリソースを、RAII で包みます。

### unique_ptr に、解放の仕方を教える（簡単）

```cpp
// C のライブラリのハンドル（fopen / fclose のような組）
struct FileCloser {
  void operator()(FILE* f) const { if (f) std::fclose(f); }
};
using FilePtr = std::unique_ptr<FILE, FileCloser>;

FilePtr file(std::fopen("save.dat", "rb"));   // 閉じるのは自動
```

### 自作のクラスで包む

```cpp
// OpenGL のバッファ（glGenBuffers / glDeleteBuffers）を、RAII で包む
class GpuBuffer {
 public:
  GpuBuffer() { glGenBuffers(1, &id_); }              // 取得
  ~GpuBuffer() { if (id_ != 0) glDeleteBuffers(1, &id_); }  // 解放

  GpuBuffer(const GpuBuffer&) = delete;               // コピーすると、二重に解放される
  GpuBuffer& operator=(const GpuBuffer&) = delete;

  GpuBuffer(GpuBuffer&& other) noexcept : id_(std::exchange(other.id_, 0)) {}  // ムーブは OK
  GpuBuffer& operator=(GpuBuffer&& other) noexcept {
    if (this != &other) {
      if (id_ != 0) glDeleteBuffers(1, &id_);
      id_ = std::exchange(other.id_, 0);
    }
    return *this;
  }

  unsigned int id() const { return id_; }

 private:
  unsigned int id_ = 0;
};
```

| 決まり | 理由 |
| --- | --- |
| **コピーを禁止する**（`= delete`） | コピーすると、同じリソースを 2 人が持ち、二重解放になる |
| **ムーブは許す** | 持ち主を移せる（`std::exchange` で元を空にする） |
| **デストラクタで解放し、例外を投げない** | デストラクタは `noexcept` が既定 |
| **`explicit` コンストラクタ**（引数 1 つのとき） | 意図しない変換を防ぐ |

「コピー禁止 + ムーブ可能」の型は、**Rule of Five**（コピーコンストラクタ、コピー代入、ムーブコンストラクタ、ムーブ代入、デストラクタ）を考えます。可能なら、`unique_ptr` や `vector` のメンバだけで作って、自分では何も書かない（**Rule of Zero**、[クラス設計](../foundations/class-design.md)）のが一番です。

### スコープ ガード（後始末を、スコープの最後にやる）

```cpp
// 関数を出るとき、必ず何かをする
template <class F>
class ScopeExit {
 public:
  explicit ScopeExit(F f) : f_(std::move(f)) {}
  ~ScopeExit() { f_(); }
  ScopeExit(const ScopeExit&) = delete;
  ScopeExit& operator=(const ScopeExit&) = delete;

 private:
  F f_;
};

void RenderFrame() {
  device.BeginFrame();
  ScopeExit end_frame([] { device.EndFrame(); });  // どの出口でも、EndFrame が呼ばれる
  // ... 描画（途中で return しても OK）
}
```

## スマートポインタの選び方

| 型 | 意味 | 使うとき |
| --- | --- | --- |
| **`std::unique_ptr<T>`** | **持ち主が 1 人**。コピー不可、ムーブ可 | **基本はこれ**。ほとんどの動的なオブジェクト |
| `std::shared_ptr<T>` | **持ち主が複数**。参照カウント | 本当に共有が必要なもの（リソースの共有など） |
| `std::weak_ptr<T>` | 持たない（消えたか確認できる） | `shared_ptr` の循環を避ける、キャッシュ |
| 生ポインタ `T*` / 参照 `T&` | **借りるだけ**（持ち主ではない） | 引数や、持ち主が別にあるとき |

```cpp
auto enemy = std::make_unique<Enemy>();              // 作る（new は書かない）
enemies.push_back(std::move(enemy));                  // 持ち主を移す
```

詳しい選び方は [所有権とライフタイム設計](../foundations/ownership-lifetime.md) を見てください。

## RAII でない書き方を、RAII に直す

| 手で書いていたこと | RAII の書き方 |
| --- | --- |
| `new T` / `delete` | `std::make_unique<T>()` |
| `new T[n]` / `delete[]` | `std::vector<T>(n)` |
| `malloc` / `free` | `std::vector`、`unique_ptr<T, decltype(&std::free)>`（[C 由来のメモリ](../../stl/memory/c-memory.md)） |
| `fopen` / `fclose` | `std::ifstream`、または `unique_ptr<FILE, FileCloser>` |
| `mutex.lock()` / `unlock()` | `std::lock_guard<std::mutex> lock(m);` |
| `glGenBuffers` / `glDeleteBuffers` | 自作の `GpuBuffer` |
| `BeginFrame()` / `EndFrame()` | スコープ ガード（`ScopeExit`） |
| `thread.join()` | `std::jthread`（デストラクタで `join`） |

## ゲームでの使いどころ

| 場面 | RAII の使い方 |
| --- | --- |
| テクスチャ・バッファ・シェーダー | GPU のリソースを包むクラス。シーンを抜けると自動で解放 |
| ロード画面の「ロード中」表示 | `ScopedLoadingScreen`（作ると表示、破棄すると消える） |
| プロファイラーの計測区間 | `ScopedTimer`（スコープの長さを自動で測る） |
| ミューテックスのロック | `std::scoped_lock` |
| デバッグの描画の状態（色、線の太さ）を、一時的に変える | `ScopedState`（戻すのを忘れない） |
| ファイルへの書き込み | `ofstream`。書き込み中にエラーでも、閉じられる |

## よくあるミス

??? failure "RAII のクラスを、コピーできるままにしてしまう"
    ハンドルを持つクラスを、コピーできる（コンパイラが勝手に作る）ままにすると、同じハンドルを 2 つのオブジェクトが持ち、**二重に解放**されます。`= delete` するか、`unique_ptr` のメンバだけで作ります。

??? failure "一時オブジェクトに名前を付けない"
    `std::lock_guard<std::mutex>(m);` と書くと、**変数名がないので、すぐ破棄**され、ロックが一瞬で外れます。`std::lock_guard<std::mutex> lock(m);` と、名前を付けます。

??? failure "デストラクタで例外を投げる"
    デストラクタは例外を出さない約束です。解放の失敗は、ログに出して、飲み込みます（`noexcept`）。

??? failure "生ポインタを、新しい `unique_ptr` に 2 回入れる"
    `unique_ptr<T> a(raw); unique_ptr<T> b(raw);` は、同じ生ポインタを 2 人が持ち、二重に解放します。ポインタは、**作ったその場で**スマートポインタに入れます（`make_unique`）。

??? failure "デストラクタの順番を考えない"
    メンバ変数は、**宣言と逆の順**で破棄されます。A が B を使っているなら、**B を先に宣言**します（B は後に破棄される）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] RAII ＝ 取得はコンストラクタ、解放はデストラクタ。解放を手で書かない
    - [x] メモリは `unique_ptr` と `vector`、ロックは `lock_guard`、ファイルは `ofstream`
    - [x] 自作のリソースも、RAII のクラスで包む（コピー禁止、ムーブ可）
    - [x] 一時オブジェクトに名前を付ける（`lock_guard` など）
    - [x] メンバの破棄の順番は、宣言の逆

## 関連ページ

- [所有権（基礎）](../../basics/ownership.md)
- [所有権とライフタイム設計](../foundations/ownership-lifetime.md)
- [クラス設計（Rule of Zero）](../foundations/class-design.md)
- [std::unique_ptr](../../stl/utilities/unique_ptr.md) / [std::shared_ptr](../../stl/utilities/shared_ptr.md)
- [エラー処理の方針](../foundations/error-handling.md)

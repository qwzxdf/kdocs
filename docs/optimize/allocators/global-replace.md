---
title: malloc の置き換え（mimalloc ほか）
tags:
  - 最適化
  - アロケータ
---

# malloc の置き換え（mimalloc ほか）

ゲーム全体の、**`new` / `delete` / `malloc` / `free` を、丸ごと高速なアロケータに置き換える**と、コードをほとんど変えずに、確保が速くなり、断片化も減ります。mimalloc（マイマロック）、jemalloc、tcmalloc などの、高性能な汎用アロケータが、無料で使えます。自作の専用アロケータ（リニア・プール）で、ホットな場所を置き換えたアロケータで、それ以外全体を速くする、という二段構えが現実的です。

!!! tip "ポイント"
    - OS・標準ライブラリの `malloc` は<strong>万能型</strong>。<strong>高性能な代替</strong>に替えると、確保が速く、断片化も減ることが多い。
    - 定番はmimalloc（Microsoft 製・MIT ライセンス）。Windows・Visual Studio で、導入しやすい。
    - 置き換え方：① `new` / `delete` だけを差し替える（簡単）、② `malloc` / `free` も含めて、全部（動的リンクの仕組み）。
    - 測ってから決める。効果はアプリによる（数%〜数十%）。
    - ホットなデータは、専用アロケータ、残りは置き換え、と組み合わせる。
    - DLL をまたぐとき、確保した側が解放する（アロケータが違うと壊れる）。

## 代表的なアロケータ

| 名前 | 作者 | 特徴 | Windows |
| --- | --- | --- | --- |
| **mimalloc** | Microsoft | 小さく速い。断片化に強い。MIT ライセンス。スレッドごとのヒープ（クロススレッド解放も得意） | ◎ 公式に対応（Visual Studio で使える） |
| jemalloc | Meta（旧 Facebook） | 断片化に強く、サーバーで実績。細かい調整ができる | △（ビルド・利用はやや面倒） |
| tcmalloc | Google | スレッドキャッシュが有名。大規模サーバー向け | △ |
| rpmalloc | Mattias Jansson | 非常に小さな実装。ゲームで人気（ロックフリー） | ○ |
| snmalloc | Microsoft Research | メッセージパッシングで、クロススレッド解放が速い | ○ |
| OS の標準（Windows） | Microsoft | Low Fragmentation Heap（LFH）で、普通に十分速い（既定） | — |

Visual Studio で試すなら、mimalloc が最も手軽です。

## mimalloc を入れる（Visual Studio）

### vcpkg

```powershell
vcpkg install mimalloc:x64-windows
```

（導入の基本は [外部ライブラリの入れ方](../../vs/libraries.md)）

### new / delete だけを置き換える

**一番簡単な方法**です。1 つの `.cpp` に、ヘッダを include するだけで、`operator new` / `operator delete`（全形式）が、mimalloc になります。

```cpp
#include <mimalloc-new-delete.h>
```

| 点 | 説明 |
| --- | --- |
| 1 つの `.cpp` だけ | プロジェクトの 1 か所（たとえば `main.cpp`）に書く。複数に書くと二重定義 |
| `new` / `delete` が、すべて置き換わる | `std::vector`・`std::string`・`std::make_shared` の確保も、含まれる |
| `malloc` / `free` は、そのまま | 古い C のコードは、変わらない（混ぜても問題ない） |
| リンク | `mimalloc.lib` を、リンクに追加（vcpkg なら、自動） |

### 自分で書く場合

```cpp
#include <mimalloc.h>

void* operator new(size_t size) {
  void* p = mi_malloc(size);
  if (p == nullptr) throw std::bad_alloc();
  return p;
}

void operator delete(void* p) noexcept { mi_free(p); }
void operator delete(void* p, size_t) noexcept { mi_free(p); }
```

C++17 のアライメント指定版（`std::align_val_t`）や、`new[]` / `delete[]`、`nothrow` 版もすべて、そろえて置き換える必要があります（片方だけ置き換えると、`new` と `delete` が、別のアロケータを使い、壊れる）。`mimalloc-new-delete.h` を使うほうが、安全です。

### malloc / free も含めて、全部置き換える（Windows）

`malloc` / `free` も、まとめて、mimalloc にしたい（サードパーティのライブラリの確保も含めて）場合は動的リンクの仕組みを使います。

| 項目 | 説明 |
| --- | --- |
| `mimalloc-override.dll` と `mimalloc-redirect.dll` | 実行ファイルと同じフォルダーに置く |
| リンクの設定 | `mimalloc-override.lib` を、リンクし、`mi_version()` などを、1 つ呼ぶ（DLL を確実に読み込ませる） |
| ランタイム | `/MD`（DLL 版のランタイム） が、前提 |
| 効果 | CRT の `malloc` / `free` / `new` / `delete` が、すべて mimalloc に転送される |

詳しい手順は、mimalloc の公式ドキュメント（Windows の項）を、確認してください（バージョンで手順が変わることがあります）。

### 使い方を確かめる

```cpp
#include <mimalloc.h>

int main() {
  mi_stats_print(nullptr);
}
```

| 方法 | 説明 |
| --- | --- |
| `mi_stats_print` | 確保の回数・使用量などの統計を表示 |
| 環境変数 `MIMALLOC_SHOW_STATS=1` | 終了時に統計を表示 |
| `mi_version()` | バージョンを返す。読み込まれているかの確認 |

## OS のアロケータ（Windows）

**何もしなくても、Windows の標準のヒープは、そこそこ速い**です。

| API | 内容 |
| --- | --- |
| 既定のヒープ（`GetProcessHeap`） | `malloc` / `new` が、裏で使う。LFH（Low Fragmentation Heap）が、小さな確保を高速化（Vista 以降、既定） |
| `HeapCreate` / `HeapAlloc` | 専用のヒープを作る。`HEAP_NO_SERIALIZE` で、ロックなし（1 スレッド専用） |
| `VirtualAlloc` | ページ単位（通常 4KB、最小の確保単位は 64KB）で、OS から、メモリをもらう。予約（`MEM_RESERVE`）と、確保（`MEM_COMMIT`）を、分けられる |
| `_aligned_malloc` | アライメント指定の確保（SIMD・キャッシュライン用）。`_aligned_free` で解放 |

### VirtualAlloc（OS に直接頼む）

自作のアロケータの大きな土台として、使います。

```cpp
void* base = VirtualAlloc(nullptr, 1 << 30, MEM_RESERVE, PAGE_NOACCESS);
VirtualAlloc(base, 64 * 1024, MEM_COMMIT, PAGE_READWRITE);
```

| 操作 | 意味 |
| --- | --- |
| `MEM_RESERVE` | アドレス空間だけを予約する（メモリはまだ使わない） |
| `MEM_COMMIT` | 実際に使えるようにする（物理メモリが割り当てられる） |
| `VirtualFree` | 返す（`MEM_DECOMMIT` / `MEM_RELEASE`） |

大きく予約して、必要なぶんだけ確保（コミット）するとアドレスが安定し、メモリを無駄にしません（[リニア](linear.md)・[TLSF](tlsf.md) の土台に便利）。

## 置き換えの効果

| 効果 | 説明 |
| --- | --- |
| **確保・解放が速くなる** | 特に小さな確保が大量のとき、スレッドが多いとき |
| 断片化が減る | 長時間のプレイでもメモリが膨らみにくい |
| スレッドのスケール | スレッドごとのヒープで、ロックの競合が減る |
| メモリの使用量 | やや増える／減る（アプリによる）。測る |

!!! warning "効果は、アプリ次第"
    確保が少ないゲームでは、ほとんど、変わらないこともあります。プロファイラー（[プロファイラー](../../vs/profiler.md)）で、`new` / `malloc` が、時間を占めていると分かってから、試します。必ず、前後を測って比べます。

## DLL をまたぐときの注意

<strong>EXE と DLL が、別々のアロケータ（別の CRT）</strong>を使っていると、DLL で確保したものを、EXE で `delete` すると、壊れます。

| 方法 | 説明 |
| --- | --- |
| `/MD`（DLL 版のランタイム）にそろえる | EXE も DLL も、同じ CRT を共有する（推奨） |
| 確保した側が解放する | DLL が、`Create` と `Destroy` の関数を公開する |
| 全体を同じ置き換えアロケータにする | mimalloc の override で、全モジュールが同じアロケータ |

## 置き換えと専用アロケータの使い分け

| | 置き換え（mimalloc） | 専用（リニア・プール・フレーム） |
| --- | --- | --- |
| **手間** | ほとんどない | コードの変更が必要 |
| 効果 | 全体が均等に速くなる | ホットな場所が劇的に速くなる |
| 確保の速さ | 数十ナノ秒 | 数ナノ秒 |
| 解放 | 個別 | まとめて（リニア）・個別（プール） |

まず、全体を置き換えて、それでも遅い、ホットな場所を専用のアロケータにします。

## よくあるミス

??? failure "`new` だけ置き換えて、`delete` を替えない（または逆）"
    **確保と解放で別のアロケータ**になり、クラッシュします。全形式をそろえる（`mimalloc-new-delete.h`）。

??? failure "`mimalloc-new-delete.h` を、複数の `.cpp` に include する"
    二重定義（`LNK2005`）になります。1 つだけ。

??? failure "EXE と DLL で、ランタイム（`/MD` と `/MT`）が違う"
    別の CRT のヒープで、確保と解放が混ざって、壊れます。そろえます。

??? failure "測らずに置き換えて、効果がないまま、複雑さだけが増える"
    先にプロファイラーで確保が遅いことを確かめます。

??? failure "リリースだけ置き換えて、デバッグでメモリのバグが、再現しない"
    デバッグビルドも同じ構成で試します。メモリのバグは、アロケータで挙動が変わります（[AddressSanitizer](../../vs/asan.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`malloc` / `new` を、mimalloc など高性能なアロケータに替える</strong>と、コードを変えずに速くなることもある
    - [x] Visual Studio なら mimalloc が手軽（`vcpkg install mimalloc`、`#include <mimalloc-new-delete.h>` を 1 か所）
    - [x] `new` と `delete` は、全形式をそろえて置き換える。EXE と DLL は、`/MD` でそろえる
    - [x] `VirtualAlloc` は、予約とコミットを分けられる（自作アロケータの土台）
    - [x] 測ってから。全体は置き換え、ホットな場所は専用アロケータ

## 関連ページ

- [アロケータ（目次）](index.md)
- [スラブアロケータ](slab.md)
- [スレッドとアロケータ](thread-local.md)
- [デバッグ用アロケータ](debug.md)
- [メモリ確保](../allocation.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
- [プロファイラー](../../vs/profiler.md)

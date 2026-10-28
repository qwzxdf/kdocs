---
title: デバッグ用アロケータ
tags:
  - 最適化
  - アロケータ
---

# デバッグ用アロケータ

**メモリのバグ**（範囲外の書き込み・解放後の使用・二重解放・リーク）は、原因から離れた場所で突然クラッシュするので、見つけにくいバグです。アロケータを自作したら、デバッグ用の機能も一緒に作っておくとバグがその場で見つかります。このページはガードバイト、解放時の埋め立て、確保の追跡（リーク検出）、使用量の統計、ページヒープなどをまとめます。自作しなくても使える、Visual Studio や OS の機能もあわせて紹介します。

!!! tip "ポイント"
    - <strong>ガードバイト</strong>：<strong>確保した領域の前後に特別な値（番兵）</strong>を置き、解放時に壊れていないか確認（範囲外書き込みを検出）。
    - 埋め立て：確保時は `0xCD`、解放時は `0xDD` などで埋める。未初期化・解放後の使用に気づきやすい。
    - 追跡：確保したものを記録（場所・大きさ・呼び出し元）。終了時に残っていればリーク。
    - 統計：確保の回数・現在の使用量・最大使用量。容量の見積もり・予算管理に。
    - これらはデバッグビルドだけ。リリースでは無効（遅く・大きくなる）。
    - まず、AddressSanitizer・CRT のデバッグヒープで見つける。自作アロケータの中は、自作の仕組みで。

!!! info "このページを読む前に"
    - [optimize/index.md](../index.md)（このセクション全体の地図と、読む順番）
    - [メモリ確保](../allocation.md)（メモリ確保が遅い理由）

## 見つけたいバグ

| バグ | 症状 | 検出の方法 |
| --- | --- | --- |
| **範囲外への書き込み**（バッファオーバーラン） | 隣のデータが壊れる。後で別の場所でクラッシュ | ガードバイトの破壊を検出 |
| 解放後の使用（use-after-free） | 解放済みのメモリを読み書き。たまたま動く | 解放時の埋め立て（`0xDD`）。ポイズニング |
| 未初期化メモリの使用 | 確保直後のでたらめな値を読む | 確保時の埋め立て（`0xCD`） |
| 二重解放 | 同じメモリを 2 回返す。リストが壊れる | 追跡（解放済みの記録）、状態フラグ |
| リーク | 返し忘れ。メモリが増え続ける | 追跡（終了時に残っているもの） |
| 不正な解放 | 確保していないポインタ・別のアロケータのものを返す | 範囲チェック・ヘッダの検証 |

## ガードバイト（番兵）

**確保した領域の前と後ろに特別な値**を置きます。解放のとき、その値が変わっていないか確かめます。変わっていれば、範囲外に書き込まれた証拠です。

<svg class="fig" viewBox="0 0 640 150" role="img" aria-label="ガードバイト">
<text x="20" y="22" class="fig-title">確保した領域の、前後に番兵（ガードバイト）を置く</text>
<rect x="20" y="40" width="80" height="40" fill="rgba(229,170,40,0.5)" stroke="currentColor"/><text x="28" y="65">ヘッダ</text>
<rect x="100" y="40" width="60" height="40" fill="rgba(150,150,150,0.4)" stroke="currentColor"/><text x="108" y="65">FD FD FD</text>
<rect x="160" y="40" width="220" height="40" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="210" y="65">ユーザーのデータ</text>
<rect x="380" y="40" width="60" height="40" fill="rgba(150,150,150,0.4)" stroke="currentColor"/><text x="388" y="65">FD FD FD</text>
<text x="20" y="115">解放時に FD が変わっていたら → 範囲外書き込みがあった（どの確保かも分かる）</text>
</svg>

```cpp
constexpr size_t kGuardSize = 16;
constexpr uint8_t kGuardByte = 0xFD;

struct DebugHeader {
  size_t size;
  const char* file;
  int line;
};

void* DebugAllocate(size_t size, const char* file, int line) {
  size_t total = sizeof(DebugHeader) + kGuardSize + size + kGuardSize;
  auto* raw = static_cast<std::byte*>(std::malloc(total));

  auto* header = reinterpret_cast<DebugHeader*>(raw);
  header->size = size;
  header->file = file;
  header->line = line;

  std::byte* front = raw + sizeof(DebugHeader);
  std::byte* user = front + kGuardSize;
  std::byte* back = user + size;

  std::memset(front, kGuardByte, kGuardSize);
  std::memset(user, 0xCD, size);
  std::memset(back, kGuardByte, kGuardSize);
  return user;
}

void DebugDeallocate(void* ptr) {
  auto* user = static_cast<std::byte*>(ptr);
  auto* header = reinterpret_cast<DebugHeader*>(user - kGuardSize - sizeof(DebugHeader));
  std::byte* front = user - kGuardSize;
  std::byte* back = user + header->size;

  for (size_t i = 0; i < kGuardSize; ++i) {
    assert(static_cast<uint8_t>(front[i]) == kGuardByte && "buffer underrun");
    assert(static_cast<uint8_t>(back[i]) == kGuardByte && "buffer overrun");
  }

  std::memset(user, 0xDD, header->size);
  std::free(reinterpret_cast<std::byte*>(header));
}
```

| 点 | 説明 |
| --- | --- |
| 前後のガード | アンダーラン（手前）とオーバーラン（奥）の両方を検出 |
| `0xCD` で確保直後を埋める | 未初期化の読み込みに気づきやすい |
| `0xDD` で解放時に埋める | 解放後の使用に気づきやすい |
| ヘッダにファイル・行 | どこで確保したかが分かる |
| 検出が遅れる | 解放時にしか、確認できない（書き込みの瞬間には、止まらない） |

!!! note "MSVC のデバッグ ヒープの値"
    Visual Studio の Debug ビルドの CRT（`/MDd`）も、同じ考え方で`0xCD`（新しい確保）、`0xDD`（解放済み）、`0xFD`（ガード領域）、`0xCC`（初期化していないスタック）を使います。デバッガーでこれらの値を見たら、原因が分かります（[デバッグのやり方](../../vs/debugging.md)）。

## 追跡（リーク検出）

**確保したものをすべて記録**し、解放時に消します。終了時に残っていたものがリークです。

```cpp
struct Allocation {
  size_t size;
  const char* file;
  int line;
};

class AllocationTracker {
 public:
  void OnAllocate(void* ptr, size_t size, const char* file, int line) {
    std::lock_guard lock(mutex_);
    allocations_[ptr] = {size, file, line};
    current_ += size;
    peak_ = std::max(peak_, current_);
    ++count_;
  }

  void OnDeallocate(void* ptr) {
    std::lock_guard lock(mutex_);
    auto it = allocations_.find(ptr);
    assert(it != allocations_.end() && "double free or invalid pointer");
    current_ -= it->second.size;
    allocations_.erase(it);
  }

  void ReportLeaks() {
    for (auto& [ptr, a] : allocations_) {
      std::println("leak: {} bytes at {}:{}", a.size, a.file, a.line);
    }
  }

 private:
  std::mutex mutex_;
  std::unordered_map<void*, Allocation> allocations_;
  size_t current_ = 0;
  size_t peak_ = 0;
  size_t count_ = 0;
};
```

| 点 | 説明 |
| --- | --- |
| `OnDeallocate` で、見つからない | 二重解放、または不正なポインタ（`assert`） |
| `ReportLeaks` | 終了時に残っているものを表示。確保した場所（ファイル・行）が分かる |
| ロック | 複数スレッドから呼ばれるなら、ロックが必要（デバッグ用なので遅くてよい） |
| 呼び出し履歴（コールスタック） | `CaptureStackBackTrace`（Windows）で、確保時のスタックを記録すると、リークの原因がさらに分かる |

### 確保の場所を記録する

```cpp
#ifdef _DEBUG
#define MY_NEW(T, ...) NewDebug<T>(__FILE__, __LINE__, __VA_ARGS__)
#else
#define MY_NEW(T, ...) NewRelease<T>(__VA_ARGS__)
#endif
```

`__FILE__` / `__LINE__` をマクロで渡すことでファイル名と行番号を記録します（`std::source_location`（C++20）を引数の既定値にする方法もあります）。

## 統計

**確保の傾向を数字で見る**と容量の見積もりや無駄の発見に役立ちます。

| 指標 | 意味 |
| --- | --- |
| 確保の回数 | 多すぎれば、確保を減らす候補 |
| 現在の使用量 | 今、いくつ使っているか |
| 最大使用量（ピーク） | 容量の見積もり。最も重いシーンで測る |
| 確保の失敗の回数 | 容量不足の検出 |
| 大きさの分布 | サイズクラスの設計に使う（どの大きさが多いか） |
| システムごとの使用量 | タグ付きでどの機能が使っているか（予算管理） |

```cpp
struct AllocatorStats {
  size_t allocation_count = 0;
  size_t current_bytes = 0;
  size_t peak_bytes = 0;
  size_t failed_count = 0;
};
```

ImGui などのデバッグ画面に表示すると、常に使用量が見えます（[Dear ImGui](../../libs/imgui/index.md)、[計測](../measure.md)）。

## ページヒープ（ガードページ）

**ガードバイト**は、解放時にしか検出できません。書き込みの瞬間に止めるには、OS のメモリ保護を使います。

```text
[ ガードページ(アクセス不可) ][ ユーザーのデータ ][ ガードページ(アクセス不可) ]
```

| 方法 | 説明 |
| --- | --- |
| 確保の後ろにアクセス不可のページを置く | 範囲外に書いた瞬間にアクセス違反でその場で止まる |
| 解放後にページごとアクセス不可に | 解放後の使用がその場で止まる |
| `VirtualAlloc` ＋ `VirtualProtect` | 自作できる。確保ごとにページ単位（4KB 以上）を使うのでメモリをとても使う・遅い |
| Windows の PageHeap（`gflags /p`）・Application Verifier | OS の機能で自作せずに同じことができる |

メモリを大量に使い、遅いので特定のバグを調べるときだけ使います。

### Windows のツール

| ツール | 内容 |
| --- | --- |
| Application Verifier | ヒープの不正・ハンドルのリークなどを実行中に検出（マイクロソフトの無料ツール） |
| gflags の PageHeap | 全ヒープ確保をガードページ付きにする（`gflags /p /enable app.exe /full`） |
| CRT のデバッグ ヒープ | `_CrtSetDbgFlag`・`_CRTDBG_MAP_ALLOC` で、リーク報告（[デバッグ](../../vs/debugging.md)） |
| AddressSanitizer（ASan） | 範囲外・解放後の使用を書き込みの瞬間に検出（[AddressSanitizer](../../vs/asan.md)） |

!!! note "自作アロケータの中は、ASan に見えない"
    自作のアロケータ（プール・リニア）の中の範囲外や解放後の使用は、ASan に見えません（OS の `malloc` を通らないため）。ASan のポイズニング API（`ASAN_POISON_MEMORY_REGION` / `ASAN_UNPOISON_MEMORY_REGION`）で、解放した領域を毒化すれば、ASan が検出できます。

```cpp
#include <sanitizer/asan_interface.h>

void Deallocate(void* ptr, size_t size) {
  ASAN_POISON_MEMORY_REGION(ptr, size);
}

void* Allocate(size_t size) {
  void* p = ...;
  ASAN_UNPOISON_MEMORY_REGION(p, size);
  return p;
}
```

## 解放時の埋め立てと、リセット時の埋め立て

| 場面 | 埋める値 | 検出できるもの |
| --- | --- | --- |
| **確保直後** | `0xCD` | 未初期化の読み込み |
| 解放直後 | `0xDD` | 解放後の使用 |
| フレームアロケータの Reset | `0xDD` | 前のフレームのポインタの持ち越し（[フレームアロケータ](frame.md)） |
| ガード領域 | `0xFD` | 範囲外の書き込み |

値が特別なのでデバッガーですぐに気づけます（`0xDDDDDDDD` のポインタは、無効なアドレスでアクセス違反にもなる）。

## 構成に応じて切り替える

```cpp
#ifdef _DEBUG
constexpr bool kDebugAllocator = true;
#else
constexpr bool kDebugAllocator = false;
#endif
```

| 構成 | 機能 |
| --- | --- |
| **Debug** | ガード・埋め立て・追跡（すべて有効） |
| Profile | 統計だけ（軽い）。ガード・追跡は無効 |
| Release | すべて無効（ゼロコスト） |

（[プリプロセッサマクロ](../../vs/preprocessor.md)）

## よくあるミス

??? failure "リリースにも、デバッグ機能（追跡・ガード）を残す"
    **遅く、メモリを多く使います**。`#ifdef _DEBUG` で、無効にします。

??? failure "`assert` だけで、ガードの破壊を検出する（リリースで消える）"
    リリースでは検出されないのは、意図どおりですがデバッグビルドで確実に実行してください。

??? failure "追跡のマップが確保のたびに `new` して、再帰的に自分を呼ぶ"
    追跡の内部で追跡対象のアロケータを使うと、無限再帰します。追跡用のメモリは、別のアロケータ（`malloc`）を使います。

??? failure "ASan で、自作アロケータの内部のバグが見つからない"
    ポイズニング API で、未使用領域を毒化します。

??? failure "ページヒープを常時有効にして、遅すぎて使えない"
    特定のバグを調べるときだけ使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ガードバイト（`0xFD`）</strong>で範囲外書き込み、埋め立て（`0xCD` / `0xDD`）で未初期化・解放後の使用に気づく
    - [x] 追跡（ポインタ → 場所・大きさ）でリーク・二重解放を検出。統計で使用量と最大使用量を測る
    - [x] ページヒープ・ASan・Application Verifier は、書き込みの瞬間に止められる
    - [x] 自作アロケータの内部は、ASan に見えない。ポイズニング APIで補う
    - [x] デバッグ機能は、Debug ビルドだけ。リリースではゼロコスト

## 関連ページ

- [アロケータ（目次）](index.md)
- [フレームアロケータ](frame.md)
- [AddressSanitizer](../../vs/asan.md)
- [デバッグのやり方](../../vs/debugging.md)
- [プリプロセッサマクロ](../../vs/preprocessor.md)
- [計測（プロファイリング）](../measure.md)

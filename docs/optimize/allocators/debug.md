---
title: デバッグ用アロケータ
tags:
  - 最適化
  - アロケータ
---

# デバッグ用アロケータ

**メモリのバグ**（範囲外の書き込み・解放後の使用・二重解放・リーク）は、**原因から離れた場所で、突然クラッシュ**するので、見つけにくいバグです。アロケータを**自作**したら、**デバッグ用の機能**も、一緒に作っておくと、**バグが、その場で見つかります**。このページは、**ガードバイト**、**解放時の埋め立て**、<strong>確保の追跡（リーク検出）</strong>、**使用量の統計**、**ページヒープ**などを、まとめます。**自作しなくても使える**、Visual Studio や OS の機能もあわせて紹介します。

!!! tip "ポイント"
    - <strong>ガードバイト</strong>：<strong>確保した領域の前後に、特別な値（番兵）</strong>を置き、<strong>解放時に、壊れていないか確認</strong>（範囲外書き込みを検出）。
    - <strong>埋め立て</strong>：<strong>確保時は `0xCD`、解放時は `0xDD`</strong> などで埋める。<strong>未初期化・解放後の使用に、気づきやすい</strong>。
    - <strong>追跡</strong>：<strong>確保したものを記録</strong>（場所・大きさ・呼び出し元）。<strong>終了時に、残っていればリーク</strong>。
    - <strong>統計</strong>：<strong>確保の回数・現在の使用量・最大使用量</strong>。<strong>容量の見積もり・予算管理</strong>に。
    - <strong>これらは、デバッグビルドだけ</strong>。<strong>リリースでは、無効</strong>（遅く・大きくなる）。
    - <strong>まず、AddressSanitizer・CRT のデバッグヒープ</strong>で見つける。<strong>自作アロケータの中は、自作の仕組みで</strong>。

## 見つけたいバグ

| バグ | 症状 | 検出の方法 |
| --- | --- | --- |
| **範囲外への書き込み**（バッファオーバーラン） | **隣のデータが壊れる**。後で、別の場所でクラッシュ | **ガードバイト**の破壊を検出 |
| **解放後の使用**（use-after-free） | **解放済みのメモリを読み書き**。たまたま動く | **解放時の埋め立て**（`0xDD`）。**ポイズニング** |
| **未初期化メモリの使用** | 確保直後の、**でたらめな値**を読む | **確保時の埋め立て**（`0xCD`） |
| **二重解放** | **同じメモリを、2 回返す**。リストが壊れる | **追跡**（解放済みの記録）、**状態フラグ** |
| **リーク** | **返し忘れ**。メモリが増え続ける | **追跡**（終了時に残っているもの） |
| **不正な解放** | **確保していないポインタ**・**別のアロケータのもの**を、返す | **範囲チェック**・**ヘッダの検証** |

## ガードバイト（番兵）

**確保した領域の、前と後ろに、特別な値**を置きます。**解放のとき、その値が、変わっていないか確かめます**。**変わっていれば、範囲外に書き込まれた**証拠です。

<svg class="fig" viewBox="0 0 640 150" role="img" aria-label="ガードバイト">
<text x="20" y="22" class="fig-title">確保した領域の、前後に、番兵（ガードバイト）を置く</text>
<rect x="20" y="40" width="80" height="40" fill="rgba(229,170,40,0.5)" stroke="currentColor"/><text x="28" y="65">ヘッダ</text>
<rect x="100" y="40" width="60" height="40" fill="rgba(150,150,150,0.4)" stroke="currentColor"/><text x="108" y="65">FD FD FD</text>
<rect x="160" y="40" width="220" height="40" fill="rgba(76,139,245,0.4)" stroke="currentColor"/><text x="210" y="65">ユーザーのデータ</text>
<rect x="380" y="40" width="60" height="40" fill="rgba(150,150,150,0.4)" stroke="currentColor"/><text x="388" y="65">FD FD FD</text>
<text x="20" y="115">解放時に、FD が変わっていたら → 範囲外書き込みがあった（どの確保かも分かる）</text>
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
| **前後のガード** | <strong>アンダーラン（手前）</strong>と<strong>オーバーラン（奥）</strong>の両方を検出 |
| **`0xCD` で、確保直後を埋める** | **未初期化の読み込み**に、気づきやすい |
| **`0xDD` で、解放時に埋める** | **解放後の使用**に、気づきやすい |
| **ヘッダに、ファイル・行** | **どこで確保したか**が分かる |
| **検出が遅れる** | **解放時**にしか、**確認できない**（書き込みの瞬間には、止まらない） |

!!! note "MSVC のデバッグ ヒープの値"
    <strong>Visual Studio の Debug ビルドの CRT（`/MDd`）</strong>も、同じ考え方で、<strong>`0xCD`（新しい確保）</strong>、<strong>`0xDD`（解放済み）</strong>、<strong>`0xFD`（ガード領域）</strong>、<strong>`0xCC`（初期化していないスタック）</strong>を使います。**デバッガーで、これらの値を見たら、原因が分かります**（[デバッグのやり方](../../vs/debugging.md)）。

## 追跡（リーク検出）

**確保したものを、すべて記録**し、**解放時に消します**。**終了時に、残っていたもの**が、**リーク**です。

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
| **`OnDeallocate` で、見つからない** | **二重解放**、または**不正なポインタ**（`assert`） |
| **`ReportLeaks`** | **終了時に、残っているもの**を表示。**確保した場所（ファイル・行）が、分かる** |
| **ロック** | **複数スレッド**から呼ばれるなら、**ロックが必要**（**デバッグ用**なので、遅くてよい） |
| <strong>呼び出し履歴（コールスタック）</strong> | **`CaptureStackBackTrace`**（Windows）で、**確保時のスタックを記録**すると、**リークの原因が、さらに分かる** |

### 確保の場所を、記録する

```cpp
#ifdef _DEBUG
#define MY_NEW(T, ...) NewDebug<T>(__FILE__, __LINE__, __VA_ARGS__)
#else
#define MY_NEW(T, ...) NewRelease<T>(__VA_ARGS__)
#endif
```

`__FILE__` / `__LINE__` を、**マクロで渡す**ことで、**ファイル名と行番号**を記録します（`std::source_location`（C++20）を、**引数の既定値**にする方法もあります）。

## 統計

**確保の傾向を、数字で見る**と、**容量の見積もり**や**無駄の発見**に役立ちます。

| 指標 | 意味 |
| --- | --- |
| **確保の回数** | **多すぎれば、確保を減らす**候補 |
| **現在の使用量** | 今、**いくつ使っているか** |
| <strong>最大使用量（ピーク）</strong> | **容量の見積もり**。**最も重いシーンで測る** |
| **確保の失敗の回数** | **容量不足**の、検出 |
| **大きさの分布** | **サイズクラスの設計**に使う（どの大きさが多いか） |
| **システムごとの使用量** | **タグ付き**で、**どの機能が使っているか**（予算管理） |

```cpp
struct AllocatorStats {
  size_t allocation_count = 0;
  size_t current_bytes = 0;
  size_t peak_bytes = 0;
  size_t failed_count = 0;
};
```

**ImGui などの、デバッグ画面に表示**すると、**常に、使用量が見えます**（[Dear ImGui](../../libs/imgui/index.md)、[計測](../measure.md)）。

## ページヒープ（ガードページ）

**ガードバイト**は、**解放時**にしか検出できません。**書き込みの瞬間に、止める**には、**OS の、メモリ保護**を使います。

```text
[ ガードページ(アクセス不可) ][ ユーザーのデータ ][ ガードページ(アクセス不可) ]
```

| 方法 | 説明 |
| --- | --- |
| **確保の後ろに、アクセス不可のページ**を置く | **範囲外に書いた瞬間**に、**アクセス違反**で、**その場で止まる** |
| **解放後に、ページごと、アクセス不可に** | **解放後の使用が、その場で**止まる |
| **`VirtualAlloc` ＋ `VirtualProtect`** | **自作**できる。**確保ごとに、ページ単位**（4KB 以上）を使うので、**メモリを、とても使う・遅い** |
| **Windows の PageHeap（`gflags /p`）・Application Verifier** | **OS の機能**で、**自作せずに**、同じことができる |

**メモリを大量に使い、遅い**ので、**特定のバグを調べるとき**だけ使います。

### Windows のツール

| ツール | 内容 |
| --- | --- |
| **Application Verifier** | **ヒープの不正**・ハンドルのリークなどを、**実行中に検出**（マイクロソフトの無料ツール） |
| **gflags の PageHeap** | **全ヒープ確保を、ガードページ付き**にする（`gflags /p /enable app.exe /full`） |
| **CRT のデバッグ ヒープ** | `_CrtSetDbgFlag`・**`_CRTDBG_MAP_ALLOC`** で、**リーク報告**（[デバッグ](../../vs/debugging.md)） |
| <strong>AddressSanitizer（ASan）</strong> | **範囲外・解放後の使用**を、**書き込みの瞬間**に検出（[AddressSanitizer](../../vs/asan.md)） |

!!! note "自作アロケータの中は、ASan に見えない"
    **自作のアロケータ**（プール・リニア）の中の、**範囲外**や**解放後の使用**は、**ASan に、見えません**（OS の `malloc` を通らないため）。**ASan の、ポイズニング API**（`ASAN_POISON_MEMORY_REGION` / `ASAN_UNPOISON_MEMORY_REGION`）で、**解放した領域を毒化**すれば、**ASan が検出**できます。

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
| **確保直後** | `0xCD` | **未初期化の読み込み** |
| **解放直後** | `0xDD` | **解放後の使用** |
| **フレームアロケータの Reset** | `0xDD` | **前のフレームのポインタの持ち越し**（[フレームアロケータ](frame.md)） |
| **ガード領域** | `0xFD` | **範囲外の書き込み** |

**値が、特別**なので、**デバッガーで、すぐに気づけます**（`0xDDDDDDDD` のポインタは、**無効なアドレス**で、**アクセス違反**にもなる）。

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
| **Debug** | **ガード・埋め立て・追跡**（すべて有効） |
| **Profile** | **統計だけ**（軽い）。**ガード・追跡は無効** |
| **Release** | **すべて無効**（**ゼロコスト**） |

（[プリプロセッサマクロ](../../vs/preprocessor.md)）

## よくあるミス

??? failure "リリースにも、デバッグ機能（追跡・ガード）を、残す"
    **遅く、メモリを多く使います**。`#ifdef _DEBUG` で、**無効**にします。

??? failure "`assert` だけで、ガードの破壊を検出する（リリースで消える）"
    **リリースでは、検出されない**のは、**意図どおり**ですが、**デバッグビルドで、確実に実行して**ください。

??? failure "追跡のマップが、確保のたびに `new` して、再帰的に自分を呼ぶ"
    **追跡の内部**で、**追跡対象のアロケータ**を使うと、**無限再帰**します。**追跡用のメモリは、別のアロケータ**（`malloc`）を使います。

??? failure "ASan で、自作アロケータの内部のバグが見つからない"
    **ポイズニング API** で、**未使用領域を毒化**します。

??? failure "ページヒープを、常時有効にして、遅すぎて使えない"
    **特定のバグを調べるとき**だけ使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ガードバイト（`0xFD`）</strong>で範囲外書き込み、<strong>埋め立て（`0xCD` / `0xDD`）</strong>で未初期化・解放後の使用に気づく
    - [x] <strong>追跡</strong>（ポインタ → 場所・大きさ）で<strong>リーク・二重解放</strong>を検出。<strong>統計</strong>で使用量と最大使用量を測る
    - [x] <strong>ページヒープ・ASan・Application Verifier</strong> は、<strong>書き込みの瞬間</strong>に止められる
    - [x] <strong>自作アロケータの内部は、ASan に見えない</strong>。<strong>ポイズニング API</strong>で補う
    - [x] <strong>デバッグ機能は、Debug ビルドだけ</strong>。<strong>リリースでは、ゼロコスト</strong>

## 関連ページ

- [アロケータ（目次）](index.md)
- [フレームアロケータ](frame.md)
- [AddressSanitizer](../../vs/asan.md)
- [デバッグのやり方](../../vs/debugging.md)
- [プリプロセッサマクロ](../../vs/preprocessor.md)
- [計測（プロファイリング）](../measure.md)

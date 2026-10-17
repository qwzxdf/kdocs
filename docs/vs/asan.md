---
title: AddressSanitizer
tags:
  - Visual Studio
---

# AddressSanitizer

C++ では、**配列の範囲外アクセス**や、**解放したメモリを使う**ミスが起きても、**その場では、何も起きず**、**あとで、まったく別の場所で壊れる**ことがあります。原因が見つけにくい、**メモリのバグ**です。<strong>AddressSanitizer（アドレス サニタイザー、ASan）</strong>は、**実行中にメモリアクセスを監視**し、**不正があった瞬間に、止めて、詳しく教えてくれる**ツールです。Visual Studio 2019（16.9）以降の MSVC で、使えます。このページは、**有効にする方法**、**見つけられるバグ**、**エラー出力の読み方**、**注意点**をまとめます。

!!! tip "ポイント"
    - ASan は、<strong>範囲外アクセス・解放済みメモリの使用（use-after-free）・二重解放</strong>などを、<strong>その場で止めて報告</strong>する。
    - 有効化：<strong>プロジェクトのプロパティ → C/C++ → 全般 → 「アドレス サニタイザーを有効にする」→ はい（/fsanitize=address）</strong>。
    - <strong>インストーラーで「C++ AddressSanitizer」のコンポーネント</strong>が必要。
    - 速さは<strong>約 2 倍遅く、メモリは増える</strong>。<strong>開発・テスト中だけ</strong>使う（製品には入れない）。
    - <strong>`/RTC1`・`/ZI`（編集して続行）・増分リンクとは併用できない</strong>。設定を調整する。
    - <strong>エラーの先頭の行（種類）と、「どこで確保したか」</strong>を読む。

## 何を見つけるのか

| バグ | 例 | ASan の報告名 |
| --- | --- | --- |
| **ヒープの範囲外アクセス** | `new int[3]` の、5 番目を読む | `heap-buffer-overflow` |
| **スタックの範囲外アクセス** | `int a[3];` の、5 番目を書く | `stack-buffer-overflow` |
| **グローバル変数の範囲外** | 静的な配列の外 | `global-buffer-overflow` |
| **解放済みメモリの使用** | `delete p;` の後で、`*p` | `heap-use-after-free` |
| **二重解放** | `delete p;` を、2 回 | `attempting double-free` |
| **不正な解放** | `new[]` を `delete` で | `alloc-dealloc-mismatch` |
| **スコープ外のスタック使用** | 関数を出た後の、ローカル変数へのポインタ | `stack-use-after-scope` / `stack-use-after-return` |
| **`memcpy` などの範囲外** | `memcpy(dst, src, 100)`（dst が 10 バイト） | `*-buffer-overflow` |

!!! note "メモリリークは、見つからない（MSVC）"
    Linux の **LeakSanitizer** のような、**リークの検出**は、MSVC の ASan では、**サポートされません**。**リーク**の調査は、[デバッグのやり方](debugging.md)の CRT のリーク検出や、プロファイラーの**メモリ使用量**で行います。

### 普通のデバッグで、見つけにくい理由

```cpp
int* p = new int[3];
p[5] = 100;
```

**この書き込みは、多くの場合、クラッシュしません**。**ヒープの別の場所を、こっそり壊す**だけで、**あとで、無関係な場所**がクラッシュします。**ASan は、この `p[5]` の瞬間**に止めます。

## 有効にする

### 1. コンポーネントを入れる

**Visual Studio Installer** → **変更** → **個別のコンポーネント**（または、**C++ によるデスクトップ開発**の、オプション）で、<strong>「C++ AddressSanitizer」</strong>に、チェックを入れて、インストールします。

### 2. プロパティで有効にする

1. **プロジェクトを右クリック → プロパティ**
2. 構成を **Debug**、プラットフォームを **x64** にする
3. **C/C++ → 全般 → アドレス サニタイザーを有効にする** → <strong>はい (/fsanitize=address)</strong>
4. ビルドして、**デバッグ実行**（F5）する

**ソリューション全体**（ライブラリを含む）で**有効にする**と、**ライブラリの中のバグも**見つかります。

### 3. 競合する設定を直す

ASan は、次の設定と**併用できません**。**エラー**や**警告**が出たら、直します。

| 競合する設定 | 直し方 |
| --- | --- |
| **`/RTC1`**（ランタイム エラー チェック） | **C/C++ → コード生成 → 基本ランタイム チェック → 既定**（なし） |
| **`/ZI`**（編集して続行） | **C/C++ → 全般 → デバッグ情報の形式 → `/Zi`**（プログラム データベース） |
| <strong>増分リンク（`/INCREMENTAL`）</strong> | **リンカー → 全般 → 増分リンクを有効にする → いいえ** |
| **`/clr`** | ASan は、**マネージドコード**とは使えない |
| **`/MTd` と `/MDd` の混在** | ランタイム ライブラリを、**そろえる** |

### CMake の場合

```cmake
if(MSVC)
  target_compile_options(app PRIVATE /fsanitize=address /Zi)
  target_link_options(app PRIVATE /INCREMENTAL:NO)
endif()
```

**Debug 構成の、`/RTC1` を外す**必要があります。

```cmake
string(REPLACE "/RTC1" "" CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
```

### コマンドラインの場合

```text
cl /fsanitize=address /Zi /std:c++latest main.cpp
```

## 実行する

### Visual Studio から

<strong>F5（デバッグ実行）</strong>で、不正アクセスがあると、**デバッガーが、その行で止まり**ます。**出力ウィンドウ**に、詳しい報告が出ます。

### 単体で実行するとき

**Visual Studio の外**（コマンドプロンプトなど）で `.exe` を実行するときは、**ASan のランタイム DLL**（`clang_rt.asan_dynamic-x86_64.dll`）が、**見つかる**必要があります。

| 方法 | 説明 |
| --- | --- |
| **Developer コマンド プロンプトから実行** | 環境変数（`PATH`）が設定されていて、見つかる |
| **DLL を、実行ファイルの横にコピー** | VS の `VC\Tools\MSVC\<バージョン>\bin\Hostx64\x64\` にある |
| **PATH に追加** | 同じフォルダーを、`PATH` に |

**DLL が見つからない**と、起動時に、**エラー**（`clang_rt.asan_dynamic-x86_64.dll が見つかりません`）が出ます。

## エラー出力の読み方

```cpp
int main() {
  int* p = new int[3];
  p[5] = 100;
  delete[] p;
}
```

```text
=================================================================
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x... at pc 0x... bp 0x... sp 0x...
WRITE of size 4 at 0x... thread T0
    #0 0x... in main main.cpp:3
    #1 0x... in invoke_main ...

0x... is located 8 bytes after 12-byte region [0x...,0x...)
allocated by thread T0 here:
    #0 0x... in operator new[] ...
    #1 0x... in main main.cpp:2
```

| 部分 | 意味 |
| --- | --- |
| **`ERROR: AddressSanitizer: heap-buffer-overflow`** | **バグの種類**（ヒープの範囲外） |
| **`WRITE of size 4`** | **書き込み**（または `READ`）。**4 バイト**のアクセス |
| **`#0 ... main.cpp:3`** | **不正アクセスをした場所**（呼び出し履歴の最初） |
| **`located 8 bytes after 12-byte region`** | **確保した領域（12 バイト）の、8 バイト後ろ**にアクセスした |
| **`allocated by thread T0 here:`** | **そのメモリを、確保した場所**（`main.cpp:2`） |
| **`freed by thread T0 here:`**（use-after-free のとき） | **解放した場所**。**誰が解放したか** |

**読む順番**：(1) **種類**、(2) <strong>アクセスの場所（#0）</strong>、(3) **確保・解放の場所**。**use-after-free** では、**解放した場所と、使った場所**の 2 つを見比べます。

### use-after-free の例

```cpp
int* p = new int(42);
delete p;
*p = 1;
```

```text
ERROR: AddressSanitizer: heap-use-after-free on address 0x...
WRITE of size 4 at ...
    #0 ... main.cpp:3
freed by thread T0 here:
    #0 ... operator delete
    #1 ... main.cpp:2
previously allocated by thread T0 here:
    #0 ... operator new
    #1 ... main.cpp:1
```

### スタックの範囲外の例

```cpp
int a[3];
a[5] = 1;
```

```text
ERROR: AddressSanitizer: stack-buffer-overflow on address 0x...
WRITE of size 4 ...
Address 0x... is located in stack of thread T0 at offset 52 in frame
    #0 ... main main.cpp:1
  This frame has 1 object(s):
    [32, 44) 'a' <== Memory access at offset 52 overflows this variable
```

## 設定のオプション

**環境変数 `ASAN_OPTIONS`** で、動きを変えられます。

| オプション | 効果 |
| --- | --- |
| **`halt_on_error=0`** | **最初のエラーで止まらず、続行**（`-fsanitize-recover=address` でビルドが必要。MSVC では制約あり） |
| **`detect_stack_use_after_return=1`** | **関数を出た後の、ローカル変数の使用**も検出（**有効にすると、メモリを多く使う**） |
| **`detect_container_overflow=0`** | `std::vector` などの**コンテナの余白へのアクセス**の検出を、止める |
| **`symbolize=1`** | 関数名の解決 |

```text
set ASAN_OPTIONS=detect_stack_use_after_return=1
```

### STL のコンテナの検出

MSVC の `std::vector` と `std::string` は、**ASan に対応した注釈**（annotation）を持っています。**`capacity` の範囲内でも、`size` の外**（使っていない余白）への**アクセス**を、**検出**できます（`container-overflow`）。

```cpp
std::vector<int> v;
v.reserve(10);
v.push_back(1);
int x = v[3];
```

**普通は気づかない**バグが、見つかります。

!!! warning "ASan あり・なしのバイナリを、混ぜない"
    **ASan を有効にしてビルドしたライブラリ**と、**無効のもの**を、**混ぜてリンク**すると、<strong>`LNK2038`（不一致）</strong>や、**誤検出**が出ることがあります。**全体を、そろえる**か、`_DISABLE_VECTOR_ANNOTATION` / `_DISABLE_STRING_ANNOTATION`（プリプロセッサマクロ）で、**注釈を無効**にします（[プリプロセッサマクロ](preprocessor.md)）。

## 注意点

| 注意 | 説明 |
| --- | --- |
| **速さが遅くなる** | **約 2 倍**。メモリも、**2〜3 倍**。**開発・テスト用** |
| **製品には入れない** | 速度・サイズ・**DLL の依存**。Release の製品ビルドは、ASan なし |
| **カスタム アロケーター** | **自作のメモリプール**の中の不正は、ASan に**見えない**。**ASan の注釈 API**（`ASAN_POISON_MEMORY_REGION`）で、**未使用部分を毒化**できる |
| **確保した領域の外に、まだ別の領域がある** | ASan は、<strong>確保の周囲に、危険地帯（レッドゾーン）</strong>を置いて検出する。**大きく飛び越えた**アクセスは、**ほかの領域**に当たって、見逃すことがある |
| **未初期化メモリの読み込み** | ASan は、見つけない（**MemorySanitizer** の領域。MSVC は対応しない） |
| <strong>スレッドの競合（データ競合）</strong> | ASan は、見つけない（**ThreadSanitizer** の領域） |
| **整数のオーバーフロー・未定義動作** | ASan は、見つけない（**UBSan**。MSVC は未対応） |
| **ビルドが遅くなる・ファイルが増える** | `.pdb` の大きさ、実行ファイルのサイズが増える |

## 普通のデバッグと組み合わせる

| 症状 | 使う道具 |
| --- | --- |
| <strong>原因不明のクラッシュ（ヒープ・スタックの破壊）</strong> | **ASan** |
| <strong>リーク（使い終わったメモリが、残る）</strong> | CRT のリーク検出（`_CRTDBG_MAP_ALLOC`）、**プロファイラーのメモリ使用量** |
| **スレッドの競合** | デバッガーの**並列ウォッチ**、設計の見直し（[並行処理の設計](../design/practice/concurrency-design.md)） |
| **未初期化の変数** | **警告レベル /W4**、**`/sdl`**（セキュリティ チェック）、**`= {}` で初期化** |
| **ロジックの間違い** | **デバッガー**（ブレークポイント、ウォッチ） |

**ASan で、メモリのバグが見つからないとき**は、別のバグかもしれません。**ASan は、メモリのアクセスだけ**を、見ます。

## CI での利用

**ASan つきのビルドを、定期的に（または、CI で毎回）実行**すると、**メモリのバグを早く**見つけられます。

| 方法 | 説明 |
| --- | --- |
| **テストを ASan つきで実行** | **単体テスト**を、ASan 付きでビルド・実行 |
| **夜間ビルド** | 重いテスト（ゲームの自動プレイ）を、ASan 付きで |
| **ファジング** | ランダムな入力で、ASan つきで実行（**libFuzzer**） |

CMake に **`SANITIZE` オプション**を作って、**切り替えられる**ようにしておくと、使いやすくなります（[ビルドと CMake の構成](../design/practice/build-cmake.md)）。

## よくあるミス

??? failure "「C++ AddressSanitizer」をインストールしていなくて、ビルドエラーになる"
    **Visual Studio Installer** で、<strong>「C++ AddressSanitizer」</strong>の**コンポーネント**を追加します。

??? failure "`/RTC1` と併用してエラー（D8016）になる"
    **基本ランタイム チェック**を、<strong>既定（なし）</strong>にします。

??? failure "「編集して続行（/ZI）」と競合する"
    **デバッグ情報の形式**を、**`/Zi`** に変えます。

??? failure "単体で実行すると、`clang_rt.asan_dynamic-x86_64.dll` が見つからない"
    **DLL を、実行ファイルの横にコピー**するか、**Developer コマンド プロンプト**から実行します。

??? failure "ASan 付きと、なしのライブラリを混ぜて、`LNK2038` や誤検出が出る"
    **全体を、同じ設定**でビルドします。または、**コンテナの注釈**を無効にします。

??? failure "製品ビルドに、ASan を入れたまま配布した"
    **遅く・大きく**なり、**DLL の依存**も増えます。**開発・テストだけ**にします。

??? failure "自作のメモリプールの中の不正が、見つからない"
    ASan は、**プールの内側**を、知りません。**注釈の API**で、**未使用の領域を毒化**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>AddressSanitizer</strong> は、<strong>範囲外アクセス・use-after-free・二重解放</strong>を、<strong>その場で止めて報告</strong>する
    - [x] 有効化は<strong>C/C++ → 全般 → アドレス サニタイザーを有効にする（/fsanitize=address）</strong>。<strong>インストーラーでコンポーネント</strong>が必要
    - [x] <strong>`/RTC1`・`/ZI`・増分リンク</strong>は、<strong>外す</strong>
    - [x] 報告は、<strong>「種類」→「アクセスした場所」→「確保・解放した場所」</strong>の順に読む
    - [x] <strong>約 2 倍遅い</strong>。<strong>開発・テスト・CI だけ</strong>。<strong>メモリリーク・スレッドの競合・未初期化は、見つからない</strong>

## 関連ページ

- [Visual Studio（目次）](index.md)
- [デバッグのやり方](debugging.md)
- [パフォーマンス プロファイラー](profiler.md)
- [よくあるエラー](errors.md)
- [ビルドと CMake の構成](../design/practice/build-cmake.md)
- [未定義動作（基礎）](../basics/ub.md)

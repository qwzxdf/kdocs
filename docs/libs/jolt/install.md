---
title: Jolt の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt の導入（Visual Studio）

Visual Studio での Jolt の入れ方です。Jolt は**ソースからビルドする**ライブラリで、`.lib` を作ります。

!!! info "このページを読む前に"
    - [Jolt Physics](index.md)（このセクション全体の地図と、読む順番）
    - [物理演算の全体像](overview.md)（Jolt の全体像）


Visual Studio での入れ方を先に説明します。Jolt はソースからビルドするライブラリで、`.lib` を作ります。次の 2 つの方法があります。

## 方法 1：Jolt のソースから Visual Studio のプロジェクトを作ってビルドする

1. [GitHub の JoltPhysics](https://github.com/jrouwe/JoltPhysics) を取得する（`git clone`。タグ（`v5.x.x`）を指定してバージョンを固定する）
2. `Build` フォルダーにある<strong>`cmake_vs2026_cl.bat`</strong>（Visual Studio 2026・MSVC 用）を実行する
3. `Build/VS2026_CL` に、Visual Studio のソリューション（`Jolt.slnx`。CMake の版によっては `Jolt.sln`）ができる。Visual Studio で開く
4. 構成を Debug と Release の両方でビルドして、`Jolt.lib` を作る
5. 自分のプロジェクトで次の 3 つを設定する（[手動の設定](../../vs/libraries.md#lib_dll)）

| 設定 | 値 |
| --- | --- |
| 追加のインクルード ディレクトリ | `$(SolutionDir)third_party\JoltPhysics`（`Jolt/Jolt.h` が見える親フォルダー） |
| 追加のライブラリ ディレクトリ | `Jolt.lib` のあるフォルダー（`$(Configuration)` を使って Debug / Release を分ける） |
| 追加の依存ファイル | `Jolt.lib` |

!!! warning "ビルド設定を一致させる（重要）"
    Jolt はビルドのときのプリプロセッサの定義によって、クラスの中身（メンバ）が変わります。ライブラリを作ったときと自分のプロジェクトで `#include` するときで、次の定義が食い違うと実行時に原因のわからないクラッシュが起きます。

    | 定義 | 意味 |
    | --- | --- |
    | `JPH_DEBUG_RENDERER` | デバッグ描画の機能を入れる（Debug で有効にするのが普通） |
    | `JPH_PROFILE_ENABLED` | プロファイラーを入れる |
    | `JPH_OBJECT_STREAM` | シーンをファイルに保存する機能を入れる |
    | `JPH_DOUBLE_PRECISION` | 位置を `double`（倍精度）で扱う（広い世界用） |
    | `JPH_ENABLE_ASSERTS` | アサートを有効にする |
    | `JPH_CROSS_PLATFORM_DETERMINISTIC` | プラットフォームをまたいで同じ結果を出す（少し遅い） |

    CMake で作ったライブラリを使うなら `Jolt` のターゲットが必要な定義を自動で付けるので、そちらを使うのが安全です（[CMake で使う](../../vs/cmake.md)）。

## 方法 2：CMake の FetchContent

```cmake
include(FetchContent)
FetchContent_Declare(
  JoltPhysics
  GIT_REPOSITORY https://github.com/jrouwe/JoltPhysics.git
  GIT_TAG v5.3.0          # 最新のタグは Releases で確認する
  SOURCE_SUBDIR Build)     # CMakeLists.txt は Build/ フォルダーにある
FetchContent_MakeAvailable(JoltPhysics)

target_link_libraries(MyGame PRIVATE Jolt)  # 定義も自動で引き継がれる
```

## 方法 3：vcpkg

```powershell
vcpkg install joltphysics:x64-windows
```

- vcpkg がダウンロード、ビルド、パスの設定まで**まとめてやってくれます**（初回は数分かかります）
- ビルド設定（Debug / Release、定義）はvcpkg の既定で作られます
- マニフェスト モード（`vcpkg.json`）なら次のように書きます

```json
{
  "dependencies": [ "joltphysics" ]
}
```

- プロジェクトでは `#include <Jolt/Jolt.h>` と書くだけで使えます。リンクも自動で通ります（`vcpkg integrate install` が済んでいれば。[外部ライブラリの入れ方](../../vs/libraries.md#vcpkg)）
- 注意: vcpkg の既定は `/MD`（DLL 版のランタイム） です。プロジェクトの設定も合わせます（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)）

## 動作確認：Jolt を初期化してみる

導入できたかは <strong>初期化と後始末だけ</strong>の小さなプログラムで、確かめます。

```cpp
#include <Jolt/Jolt.h>

#include <Jolt/Core/Factory.h>
#include <Jolt/Core/Memory.h>
#include <Jolt/RegisterTypes.h>

#include <print>

JPH_SUPPRESS_WARNINGS                                      // Jolt のヘッダーが出す、警告を抑える

int main() {
  JPH::RegisterDefaultAllocator();                         // メモリ確保の関数を登録（最初に 1 回）
  JPH::Factory::sInstance = new JPH::Factory();            // 型の登録に必要な、ファクトリー
  JPH::RegisterTypes();                                    // Jolt の、標準の型（形状、制約など）を登録

  std::println("Jolt を、初期化できました");

  JPH::UnregisterTypes();                                  // 後始末（逆の順序）
  delete JPH::Factory::sInstance;
  JPH::Factory::sInstance = nullptr;
}
```

この 3 つ（アロケーターの登録、ファクトリー、型の登録）は Jolt を何かに使う前に必ず 1 回行う決まりの手順です。メッセージが出てクラッシュしなければ導入は、成功です（[世界の初期化と更新](system.md)）。

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2038`（`_ITERATOR_DEBUG_LEVEL` の不一致） | `Jolt.lib` を Release で作ったのに、自分のプロジェクトが Debug（または、逆） | Debug と Release の両方で、`Jolt.lib` を作り構成ごとに正しいほうをリンクする |
| `LNK2038`（`RuntimeLibrary` の不一致） | `/MD` と `/MT` の取り違え | Jolt のビルドと、自分のプロジェクトでランタイム ライブラリをそろえる（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)） |
| 実行時に原因の分からない、クラッシュ | `JPH_DEBUG_RENDERER` などの定義がライブラリと自分のプロジェクトで、違う | 定義をライブラリのビルドとそろえる。CMake の `Jolt` ターゲットを使えば自動で、そろう |
| `LNK2019`（`JPH::…` が未解決） | `Jolt.lib` をリンクしていない | 追加の依存ファイルに `Jolt.lib` |
| `C1083`（`Jolt/Jolt.h` を開けない） | インクルード ディレクトリが違う | `Jolt` フォルダーの <strong>親</strong>を指定する（`JoltPhysics` のルート） |
| `C4324` などの警告が大量 | Jolt のアラインメント指定 | `JPH_SUPPRESS_WARNINGS` を `#include` の後に書く |

## C++ の設定

Jolt は C++17 以降が必要です。プロジェクトの <strong>C++ 言語標準</strong>を `/std:c++17` 以上（このサイトでは `/std:c++latest`）にします（[C++23 を使えるようにする設定](../../vs/settings.md)）。

| 設定 | 値 |
| --- | --- |
| C++ 言語標準 | `/std:c++17` 以上 |
| 浮動小数点モデル | `/fp:precise`（既定）。`/fp:fast` は再現性を壊すことがある |
| 例外 | 無効でも有効でも動く（Jolt は、例外を使わない）。ライブラリとそろえる |
| RTTI | Jolt は独自の型情報を使うので、不要 |

## バージョンを固定する

物理演算はバージョンで <strong>挙動の細部</strong>（接触の解決の順序、数値の誤差）が変わります。リプレイやネットワークの同期（決定論）を使うならバージョンを固定します。

| 方法 | 内容 |
| --- | --- |
| Git のタグ | `v5.3.0` などタグを指定して、`git checkout` する |
| vcpkg（マニフェスト） | `vcpkg.json` の `builtin-baseline` で、固定 |
| FetchContent | `GIT_TAG` にタグ（またはコミット ハッシュ） |

## 関連ページ

- [Jolt Physics（目次）](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)


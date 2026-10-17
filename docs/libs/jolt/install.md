---
title: Jolt の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt の導入（Visual Studio）

Visual Studio での、Jolt の入れ方です。Jolt は**ソースからビルドする**ライブラリで、`.lib` を作ります。

Visual Studio での入れ方を先に説明します。Jolt は**ソースからビルドする**ライブラリで、`.lib` を作ります。次の 2 つの方法があります。

## 方法 1：Jolt のソースから Visual Studio のプロジェクトを作ってビルドする

1. [GitHub の JoltPhysics](https://github.com/jrouwe/JoltPhysics) を取得する（`git clone`。タグ（`v5.x.x`）を指定して、バージョンを固定する）
2. `Build` フォルダーにある、**`cmake_vs2022_cl.bat`**（Visual Studio 2022・MSVC 用）を実行する
3. `Build/VS2022_CL/Jolt.sln` ができる。Visual Studio で開く
4. 構成を **Debug** と **Release** の両方でビルドして、`Jolt.lib` を作る
5. 自分のプロジェクトで、次の 3 つを設定する（[手動の設定](../../vs/libraries.md#lib_dll)）

| 設定 | 値 |
| --- | --- |
| 追加のインクルード ディレクトリ | `$(SolutionDir)third_party\JoltPhysics`（`Jolt/Jolt.h` が見える親フォルダー） |
| 追加のライブラリ ディレクトリ | `Jolt.lib` のあるフォルダー（`$(Configuration)` を使って Debug / Release を分ける） |
| 追加の依存ファイル | `Jolt.lib` |

!!! warning "ビルド設定を一致させる（重要）"
    Jolt は、ビルドのときの**プリプロセッサの定義**によって、**クラスの中身（メンバ）が変わります**。ライブラリを作ったときと、**自分のプロジェクトで `#include` するとき**で、次の定義が**食い違うと、実行時に原因のわからないクラッシュ**が起きます。

    | 定義 | 意味 |
    | --- | --- |
    | `JPH_DEBUG_RENDERER` | デバッグ描画の機能を入れる（Debug で有効にするのが普通） |
    | `JPH_PROFILE_ENABLED` | プロファイラーを入れる |
    | `JPH_OBJECT_STREAM` | シーンをファイルに保存する機能を入れる |
    | `JPH_DOUBLE_PRECISION` | 位置を `double`（倍精度）で扱う（広い世界用） |
    | `JPH_ENABLE_ASSERTS` | アサートを有効にする |
    | `JPH_CROSS_PLATFORM_DETERMINISTIC` | プラットフォームをまたいで同じ結果を出す（少し遅い） |

    CMake で作ったライブラリを使うなら、`Jolt` のターゲットが**必要な定義を自動で付ける**ので、そちらを使うのが安全です（[CMake で使う](../../vs/cmake.md)）。

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

- vcpkg が、ダウンロード、ビルド、パスの設定まで**まとめてやってくれます**（初回は数分かかります）
- ビルド設定（Debug / Release、定義）は、**vcpkg の既定**で作られます
- マニフェスト モード（`vcpkg.json`）なら、次のように書きます

```json
{
  "dependencies": [ "joltphysics" ]
}
```

- プロジェクトでは、`#include <Jolt/Jolt.h>` と書くだけで使えます。リンクも自動で通ります（`vcpkg integrate install` が済んでいれば。[外部ライブラリの入れ方](../../vs/libraries.md#vcpkg)）
- 注意: vcpkg の既定は <strong>`/MD`（DLL 版のランタイム）</strong> です。プロジェクトの設定も合わせます（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)）

## 関連ページ

- [Jolt Physics（目次）](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)


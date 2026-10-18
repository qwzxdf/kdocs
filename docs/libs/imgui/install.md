---
title: Dear ImGui の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - GUI
---

# Dear ImGui の導入（Visual Studio）

Visual Studio での Dear ImGui の入れ方です。Dear ImGui は**ソースファイルをプロジェクトに入れる**のが基本です（ヘッダだけではなく `.cpp` もあります）。

**まず Visual Studio での入れ方**を説明します。Dear ImGui は**ソースファイルをプロジェクトに入れる**のが基本です（ヘッダだけではなく `.cpp` もあります）。バックエンドのファイルも必要です。

## 方法 1：ソースを入れる

1. [GitHub の ImGui](https://github.com/ocornut/imgui) から取得する（`git clone`、または Releases の ZIP）。`third_party/imgui/` に置く
2. 次のファイルをソリューション エクスプローラーで**プロジェクトに追加**（追加 → 既存の項目）

| ファイル | 内容 |
| --- | --- |
| `imgui.cpp`, `imgui_draw.cpp`, `imgui_tables.cpp`, `imgui_widgets.cpp` | ImGui 本体 |
| `imgui_demo.cpp` | **デモ ウィンドウ**（全部の部品の見本。勉強に最適） |
| `backends/imgui_impl_win32.cpp` | プラットフォーム：Win32 |
| `backends/imgui_impl_dx11.cpp` | 描画：DirectX 11 |

3. プロジェクトのプロパティ → **C/C++ → 全般 → 追加のインクルード ディレクトリ** に、次を追加

```text
$(SolutionDir)third_party\imgui
$(SolutionDir)third_party\imgui\backends
```

4. リンカー → 入力 → 追加の依存ファイル に `d3d11.lib`、`dxgi.lib` を追加する（DirectX 11 を使う場合。サンプルの DirectX の初期化コードが `#pragma comment(lib, ...)` で入れることもあります）

!!! note "ImGui の C++ 言語標準"
    ImGui 本体は古い C++ でも動くように書かれていて、C++23 でもそのままビルドできます。ビルドの警告が気になるなら `third_party` を「外部インクルード ディレクトリ」に入れます（[外部ヘッダの警告](../../vs/libraries.md#external_include)）。

## 方法 2：vcpkg で入れる

```powershell
vcpkg install imgui[win32-binding,dx11-binding]:x64-windows
```

- `[ ]` の中は**使うバックエンド**（機能）の指定です。マニフェスト モード（`vcpkg.json`）なら次のように書きます

```json
{
  "dependencies": [
    { "name": "imgui", "features": ["win32-binding", "dx11-binding", "docking-experimental"] }
  ]
}
```

- `docking-experimental` はウィンドウをドッキングできる機能です（[ドッキングとビューポート](docking.md)）
- vcpkg 版を使うと `#include <imgui.h>` や `#include <backends/imgui_impl_dx11.h>` のように書きます（インクルードの書き方がソースを入れる方法と少し違います）

## 方法 3：CMake（FetchContent）

```cmake
include(FetchContent)
FetchContent_Declare(
  imgui
  GIT_REPOSITORY https://github.com/ocornut/imgui.git
  GIT_TAG v1.91.9)  # 最新のタグは Releases で確認する
FetchContent_MakeAvailable(imgui)
# imgui は CMakeLists.txt を持たないので、自分でライブラリを定義する
add_library(imgui STATIC
  ${imgui_SOURCE_DIR}/imgui.cpp
  ${imgui_SOURCE_DIR}/imgui_draw.cpp
  ${imgui_SOURCE_DIR}/imgui_tables.cpp
  ${imgui_SOURCE_DIR}/imgui_widgets.cpp
  ${imgui_SOURCE_DIR}/backends/imgui_impl_win32.cpp
  ${imgui_SOURCE_DIR}/backends/imgui_impl_dx11.cpp)
target_include_directories(imgui PUBLIC ${imgui_SOURCE_DIR} ${imgui_SOURCE_DIR}/backends)
```

## 動作確認：コンパイルとリンクの確認

導入できたかをまず <strong>ImGui のバージョンを表示する</strong>だけで、確かめます。画面に何かを出す前にリンクの段階で、問題がないかを見られます。

```cpp
#include <print>

#include "imgui.h"

int main() {
  IMGUI_CHECKVERSION();                                    // ヘッダーと、ライブラリの、バージョンが、合っているかを確認
  ImGuiContext* context = ImGui::CreateContext();
  std::println("Dear ImGui {}", ImGui::GetVersion());      // 例: 1.91.x
  ImGui::DestroyContext(context);
}
```

`IMGUI_CHECKVERSION()` は <strong>ヘッダーとコンパイルした `.cpp` のバージョンが、食い違っていないか</strong>を実行時に確かめます（食い違うとアサートで止まる）。バージョンが表示されれば ImGui 本体の導入は、成功です。次に、バックエンド（DX11、Win32）を足して画面に出します（[仕組みと最小のコード](basics.md)）。

## 追加するファイル

ソースを入れる場合、プロジェクトに次のファイルを追加します。

| 区分 | ファイル | 役割 |
| --- | --- | --- |
| 本体 | `imgui.cpp`、`imgui_draw.cpp`、`imgui_tables.cpp`、`imgui_widgets.cpp` | ImGui の中核 |
| バックエンド（Windows） | `imgui_impl_win32.cpp` | ウィンドウ、入力 |
| バックエンド（DX11） | `imgui_impl_dx11.cpp` | 描画 |
| バックエンド（DX12） | `imgui_impl_dx12.cpp` | 描画（DX12 のとき） |
| デモ（任意） | `imgui_demo.cpp` | `ImGui::ShowDemoWindow()` が使える。使い方を学ぶのに便利 |

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2019`（`ImGui::…` が未解決） | `imgui.cpp` などをプロジェクトに追加していない | 上の表のファイルを全部、追加する |
| `LNK2019`（`ImGui_ImplWin32_…` が未解決） | バックエンドの `.cpp` を追加していない | `imgui_impl_win32.cpp` と `imgui_impl_dx11.cpp` を追加 |
| `C1083`（`imgui_impl_win32.h` を開けない） | バックエンドは、`backends/` フォルダーにある | インクルード ディレクトリに `backends` も追加 |
| `IM_ASSERT` で止まる（起動時） | `IMGUI_CHECKVERSION` の食い違いまたは、`CreateContext` の前に ImGui の関数を呼んだ | ヘッダーと `.cpp` を同じバージョンにする。`CreateContext` を最初に呼ぶ |
| 日本語が `???` になる | 既定のフォントに日本語が、入っていない | 日本語フォントを読み込む（[フォント](fonts.md)） |

## バージョンの注意

ImGui はバージョンが上がると、<strong>バックエンドの API が変わる</strong>ことがあります。本体（`imgui.cpp`）とバックエンド（`imgui_impl_*.cpp`）は <strong>同じバージョン</strong>の組み合わせで使います。別々の場所から取得すると食い違いやすいので同じリポジトリ（同じタグ）から、まとめて取得します。

## 関連ページ

- [Dear ImGui（目次）](index.md)
- [ウィジェット一覧](widgets.md)
- [レイアウトとウィンドウ](layout.md)


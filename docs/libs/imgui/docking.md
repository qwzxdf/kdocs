---
title: ドッキングとビューポート
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のドッキングとビューポート

**ドッキング**は、**ウィンドウを、ドラッグして、ほかのウィンドウの横やタブに、くっつける**機能です。Unity や Unreal のエディタのように、**自由にパネルを並べ替えられる画面**が作れます。**マルチビューポート**は、**ImGui のウィンドウを、アプリのウィンドウの外**（別の OS ウィンドウ）に**出せる**機能です。どちらも、**`docking` ブランチ**（または、対応する vcpkg の機能）で使えます。

!!! tip "ポイント"
    - ドッキングは、<strong>`docking` ブランチ</strong>の機能（<strong>通常のリリースには、含まれない</strong>）。vcpkg なら <strong>`imgui[docking-experimental]`</strong>。
    - 有効化は <strong>`io.ConfigFlags |= ImGuiConfigFlags_DockingEnable`</strong>。
    - <strong>メイン ウィンドウ全体を、ドッキング領域にする</strong>のは <strong>`DockSpaceOverViewport`</strong>。
    - <strong>レイアウト</strong>は、<strong>`imgui.ini` に、自動で保存・復元</strong>される。
    - <strong>マルチビューポート</strong>は <strong>`ImGuiConfigFlags_ViewportsEnable`</strong>。<strong>バックエンドの対応</strong>が必要で、<strong>描画の呼び出しが、少し増える</strong>。
    - <strong>ゲームの画面は、レンダー ターゲットに描いて、ウィンドウの中の画像として出す</strong>（[テクスチャ](textures.md)）。

## ドッキングを有効にする

### docking ブランチ

ドッキングは、**ImGui の `docking` ブランチ**に入っています（**正式版の `master` には、まだ入っていません**。安定していて、広く使われています）。

| 入手方法 | 説明 |
| --- | --- |
| **GitHub の `docking` ブランチ** | `git clone -b docking https://github.com/ocornut/imgui`。**ソースを入れる**方法（[導入](index.md#install)）で使う |
| **vcpkg** | `vcpkg install imgui[docking-experimental,dx11-binding,win32-binding]:x64-windows`（**機能名は、ポートの定義を確認**） |

!!! note "vcpkg の機能名"
    vcpkg の `imgui` ポートは、**`docking-experimental`**（ドッキング）、**`multi-viewport`**（マルチビューポート）、**`dx11-binding`**、**`win32-binding`** などの、<strong>機能（feature）</strong>を持ちます。**バージョンで名前が変わる**ことがあるので、`vcpkg search imgui` や、ポートのドキュメントで確認します。

### 有効化

```cpp
ImGuiIO& io = ImGui::GetIO();
io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
```

**これだけで、ウィンドウの、タイトルバーをドラッグして、ほかのウィンドウの縁やタブに、ドッキングできます**（**Shift を押しながらドラッグ**する設定もある：`io.ConfigDockingWithShift`）。

## メインウィンドウ全体をドッキング領域にする

**エディタのように、アプリの画面全体**を、ドッキング領域にします。

```cpp
ImGui::DockSpaceOverViewport(0, ImGui::GetMainViewport());
```

| 点 | 説明 |
| --- | --- |
| **`DockSpaceOverViewport(...)`** | **メイン ビューポート全体**に、**ドッキング領域**を作る（**メニューバーの下**など、作業領域に合わせる） |
| **毎フレーム、`NewFrame` の後に呼ぶ** | ほかのウィンドウを作る**前**に |
| **シグネチャ** | **バージョンで引数が違う**（`dockspace_id`、`viewport`、`flags`、…）。**使っているバージョンのヘッダ**で確認 |

### 背景を透けさせる（ゲームの画面を見せる）

**ドッキング領域の「中央」を、空けて**おくと、**ゲームの画面が、背景に見えます**。

```cpp
ImGui::DockSpaceOverViewport(0, ImGui::GetMainViewport(), ImGuiDockNodeFlags_PassthruCentralNode);
```

| フラグ | 意味 |
| --- | --- |
| **`ImGuiDockNodeFlags_PassthruCentralNode`** | **中央のノードを、透明**にして、**後ろの描画（ゲーム）が見える** |
| `ImGuiDockNodeFlags_NoDockingInCentralNode` | **中央に、ドッキングさせない** |
| `ImGuiDockNodeFlags_AutoHideTabBar` | **1 つしかないタブの、タブバーを隠す** |

**ゲームの画面を、そのまま背景に出し、周りにパネルを並べる**構成です。**シーンビューを、ウィンドウに入れたい**場合は、**レンダー ターゲット**にします（[テクスチャ](textures.md)）。

## 自分でドックスペース ウィンドウを作る

**メニューバーを含む、自作のウィンドウ**に、**ドッキング領域**を置く方法です。

```cpp
ImGuiViewport* viewport = ImGui::GetMainViewport();
ImGui::SetNextWindowPos(viewport->WorkPos);
ImGui::SetNextWindowSize(viewport->WorkSize);
ImGui::SetNextWindowViewport(viewport->ID);

ImGuiWindowFlags flags = ImGuiWindowFlags_MenuBar | ImGuiWindowFlags_NoDocking |
                         ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse |
                         ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
                         ImGuiWindowFlags_NoBringToFrontOnFocus | ImGuiWindowFlags_NoNavFocus;

ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);
ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
ImGui::Begin("DockSpaceWindow", nullptr, flags);
ImGui::PopStyleVar(3);

ImGuiID dockspace_id = ImGui::GetID("MyDockSpace");
ImGui::DockSpace(dockspace_id, ImVec2(0, 0), ImGuiDockNodeFlags_None);

if (ImGui::BeginMenuBar()) {
  if (ImGui::BeginMenu("ファイル")) {
    ImGui::MenuItem("終了");
    ImGui::EndMenu();
  }
  ImGui::EndMenuBar();
}
ImGui::End();
```

**`DockSpace`** は、**ドッキング領域そのもの**を作ります。**この方法**だと、**自作のメニューバーや、固定のツールバー**を、**同じウィンドウに入れられます**。

## レイアウトの保存と読み込み

| 方法 | 説明 |
| --- | --- |
| <strong>`imgui.ini`（自動）</strong> | **ウィンドウの位置・大きさ・ドッキングの配置**が、**自動で保存・復元**される（`io.IniFilename`） |
| **保存先を変える** | `io.IniFilename = "layout.ini";`、または **`nullptr` で、保存しない** |
| **文字列で保存・読み込み** | `ImGui::SaveIniSettingsToMemory()` / `LoadIniSettingsFromMemory(data)` で、**独自のファイル・メモリ**へ |
| **`SaveIniSettingsToDisk(path)` / `LoadIniSettingsFromDisk(path)`** | **別のファイルへ**保存・読み込み（**複数のレイアウト切り替え**に） |

```cpp
if (ImGui::MenuItem("レイアウトを保存")) ImGui::SaveIniSettingsToDisk("layouts/my_layout.ini");
if (ImGui::MenuItem("レイアウトを読み込み")) ImGui::LoadIniSettingsFromDisk("layouts/my_layout.ini");
```

### 初期のレイアウトをコードで作る（DockBuilder）

**初回起動のとき**に、**決まったレイアウト**（左に階層、右にインスペクタ、下にログ）にしたい場合は、**`DockBuilder`**（`imgui_internal.h`）を使います。

```cpp
#include "imgui_internal.h"

ImGuiID dockspace_id = ImGui::GetID("MyDockSpace");

if (ImGui::DockBuilderGetNode(dockspace_id) == nullptr) {
  ImGui::DockBuilderRemoveNode(dockspace_id);
  ImGui::DockBuilderAddNode(dockspace_id, ImGuiDockNodeFlags_DockSpace);
  ImGui::DockBuilderSetNodeSize(dockspace_id, viewport->Size);

  ImGuiID left, right, bottom;
  ImGuiID center = dockspace_id;
  left = ImGui::DockBuilderSplitNode(center, ImGuiDir_Left, 0.2f, nullptr, &center);
  right = ImGui::DockBuilderSplitNode(center, ImGuiDir_Right, 0.25f, nullptr, &center);
  bottom = ImGui::DockBuilderSplitNode(center, ImGuiDir_Down, 0.25f, nullptr, &center);

  ImGui::DockBuilderDockWindow("階層", left);
  ImGui::DockBuilderDockWindow("インスペクタ", right);
  ImGui::DockBuilderDockWindow("ログ", bottom);
  ImGui::DockBuilderDockWindow("シーン", center);
  ImGui::DockBuilderFinish(dockspace_id);
}
```

| 関数 | 意味 |
| --- | --- |
| **`DockBuilderSplitNode(node, 向き, 割合, 新しい側, 残りの側)`** | **領域を分割** |
| **`DockBuilderDockWindow("名前", node)`** | **ウィンドウを、その領域に**置く |
| `DockBuilderFinish` | 確定 |

**`imgui_internal.h`** は、**内部 API** で、**バージョンで変わる**ことがあります。

## マルチビューポート

**ImGui のウィンドウを、アプリのウィンドウの外（別の OS ウィンドウ）に出せる**機能です（**デュアルモニターで、パネルを別の画面へ**）。

```cpp
io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;
```

| 点 | 説明 |
| --- | --- |
| **バックエンドの対応が必要** | **Win32 + DirectX 11** は、**対応**している |
| **描画のあとに、追加の呼び出し** | **メインの描画が終わったあと**に、**`UpdatePlatformWindows()` と `RenderPlatformWindowsDefault()`** を呼ぶ |
| **スタイルの調整** | **ウィンドウの角丸・背景の透明**が、OS ウィンドウでは違和感がある → `WindowRounding = 0`、`WindowBg.w = 1` |

```cpp
ImGui::Render();
ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
  ImGui::UpdatePlatformWindows();
  ImGui::RenderPlatformWindowsDefault();
}
```

!!! warning "デバイス・スワップチェーンの扱い"
    **マルチビューポート**では、**ImGui が、追加のスワップチェーン**を作ります。<strong>デバイスのコンテキストの設定（レンダー ターゲット・ビューポート）</strong>を、**メインの描画の後に、再設定**する必要があるかもしれません。**公式サンプル**（`example_win32_directx11`）を、参考にします。

## ゲームの画面を、ドッキングできるウィンドウにする

**エディタ風**に、**ゲームの画面を、ウィンドウの中に出す**には、**レンダー ターゲットに描画**し、**`ImGui::Image`** で表示します（[テクスチャ](textures.md#sceneview)）。

```cpp
ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
if (ImGui::Begin("シーン")) {
  ImVec2 size = ImGui::GetContentRegionAvail();
  ResizeSceneIfNeeded(size);
  ImGui::Image((ImTextureID)(intptr_t)scene_srv, size);
}
ImGui::End();
ImGui::PopStyleVar();
```

**ウィンドウの大きさに合わせて、レンダー ターゲットを作り直す**ことが、ポイントです。

## よくあるミス

??? failure "ドッキングできない"
    **`docking` ブランチではない**、または **`ImGuiConfigFlags_DockingEnable` を設定していません**。

??? failure "`DockSpaceOverViewport` を、ウィンドウより後に呼んでいる"
    **ドッキング領域より、先にウィンドウを作る**と、**ドッキングが、うまく効かない**ことがあります。**`NewFrame` の直後**に呼びます。

??? failure "`imgui.ini` が、古いレイアウトを復元して、初期レイアウトが反映されない"
    **`imgui.ini` を消す**か、**`DockBuilderGetNode` で、ノードがないときだけ**作る処理にします。

??? failure "マルチビューポートで、ウィンドウが真っ黒・描画が崩れる"
    **`RenderPlatformWindowsDefault()`** を呼んでいません。**描画後に呼び出し**ます。

??? failure "シーンビューが、ぼやける・伸びる"
    **ウィンドウの大きさに合わせて、レンダー ターゲットのサイズを変えて**います。**拡大縮小で、伸びて**いませんか。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ドッキングは<strong>`docking` ブランチ</strong>（vcpkg は <strong>`docking-experimental`</strong>）。<strong>`ImGuiConfigFlags_DockingEnable`</strong> で有効に
    - [x] <strong>`DockSpaceOverViewport`</strong> で、画面全体をドッキング領域に。<strong>`PassthruCentralNode`</strong> で、中央を透かす
    - [x] <strong>レイアウトは `imgui.ini` に自動保存</strong>。<strong>初期レイアウトは `DockBuilder`</strong>
    - [x] <strong>マルチビューポート</strong>は <strong>`ViewportsEnable`</strong> ＋ <strong>描画後に `UpdatePlatformWindows` / `RenderPlatformWindowsDefault`</strong>
    - [x] <strong>シーンビューは、レンダー ターゲット ＋ `ImGui::Image`</strong>

## 関連ページ

- [Dear ImGui](index.md)
- [レイアウトとウィンドウ](layout.md)
- [テクスチャと画像](textures.md)
- [スタイルとテーマ](style.md)
- [ImGuizmo](imguizmo.md)

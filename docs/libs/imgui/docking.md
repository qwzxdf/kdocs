---
title: ドッキングとビューポート
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のドッキングとビューポート

**ドッキング**はウィンドウをドラッグして、ほかのウィンドウの横やタブにくっつける機能です。Unity や Unreal のエディタのように自由にパネルを並べ替えられる画面が作れます。マルチビューポートはImGui のウィンドウをアプリのウィンドウの外（別の OS ウィンドウ）に出せる機能です。どちらも、`docking` ブランチ（または対応する vcpkg の機能）で使えます。

!!! tip "ポイント"
    - ドッキングは <strong>`docking` ブランチ</strong>の機能（<strong>通常のリリースには、含まれない</strong>）。vcpkg なら `imgui[docking-experimental]`。
    - 有効化は `io.ConfigFlags |= ImGuiConfigFlags_DockingEnable`。
    - メイン ウィンドウ全体をドッキング領域にするのは `DockSpaceOverViewport`。
    - レイアウトは `imgui.ini` に自動で保存・復元される。
    - マルチビューポートは `ImGuiConfigFlags_ViewportsEnable`。バックエンドの対応が必要で、描画の呼び出しが少し増える。
    - ゲームの画面はレンダー ターゲットに描いて、ウィンドウの中の画像として出す（[テクスチャ](textures.md)）。

## ドッキングを有効にする

### docking ブランチ

ドッキングは**ImGui の `docking` ブランチ**に入っています（正式版の `master` には、まだ入っていません。安定していて広く使われています）。

| 入手方法 | 説明 |
| --- | --- |
| GitHub の `docking` ブランチ | `git clone -b docking https://github.com/ocornut/imgui`。ソースを入れる方法（[導入](install.md)）で使う |
| vcpkg | `vcpkg install imgui[docking-experimental,dx11-binding,win32-binding]:x64-windows`（機能名は、ポートの定義を確認） |

!!! note "vcpkg の機能名"
    vcpkg の `imgui` ポートは、`docking-experimental`（ドッキング）、`multi-viewport`（マルチビューポート）、`dx11-binding`、`win32-binding` などの 機能（feature）を持ちます。バージョンで名前が変わることがあるので `vcpkg search imgui` やポートのドキュメントで確認します。

### 有効化

```cpp
ImGuiIO& io = ImGui::GetIO();
io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
```

これだけでウィンドウのタイトルバーをドラッグして、ほかのウィンドウの縁やタブにドッキングできます（Shift を押しながらドラッグする設定もある：`io.ConfigDockingWithShift`）。

<svg class="fig imgui motion" data-fig="imgui-docking-layout" viewBox="0 0 780 420" role="img" aria-label="ドッキング レイアウトの例"><rect x="0" y="0" width="780" height="420" fill="#1b1b1f" rx="6"/><rect x="10.0" y="10.0" width="760.0" height="400.0" rx="4" fill="#0c0c10" stroke="#4b4b57" stroke-width="1" /><rect x="10.0" y="10.0" width="760.0" height="19.0" rx="0" fill="#232329" /><text x="20.0" y="24.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >File</text><text x="66.0" y="24.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Edit</text><text x="112.0" y="24.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >View</text><text x="158.0" y="24.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Help</text><rect x="14.0" y="31.0" width="180.0" height="361.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="14.0" y="31.0" width="180.0" height="19.0" rx="0" fill="#294a7a" /><path d="M21,37 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="34.0" y="45.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Hierarchy</text><path d="M24,64 l10,0 l-5,9 z" fill="#ffffff"/><text x="40.0" y="72.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Scene</text><rect x="16.0" y="81.0" width="176.0" height="19.0" rx="0" fill="#24435f" /><path d="M41,85 l0,10 l9,-5 z" fill="#ffffff"/><text x="56.0" y="95.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Player</text><path d="M41,108 l0,10 l9,-5 z" fill="#ffffff"/><text x="56.0" y="118.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Enemy</text><path d="M41,131 l0,10 l9,-5 z" fill="#ffffff"/><text x="56.0" y="141.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Light</text><rect x="198.0" y="31.0" width="380.0" height="250.0" rx="0" fill="#101018" stroke="#4b4b57" stroke-width="1" /><rect x="198.0" y="31.0" width="380.0" height="19.0" rx="0" fill="#294a7a" /><text x="218.0" y="45.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Scene View</text><path d="M205,58 l5,0 l-2.5,7 z" fill="#fff"/><line x1="198" y1="50" x2="198" y2="281" stroke="#222" /><line x1="236" y1="50" x2="236" y2="281" stroke="#222" /><line x1="274" y1="50" x2="274" y2="281" stroke="#222" /><line x1="312" y1="50" x2="312" y2="281" stroke="#222" /><line x1="350" y1="50" x2="350" y2="281" stroke="#222" /><line x1="388" y1="50" x2="388" y2="281" stroke="#222" /><line x1="426" y1="50" x2="426" y2="281" stroke="#222" /><line x1="464" y1="50" x2="464" y2="281" stroke="#222" /><line x1="502" y1="50" x2="502" y2="281" stroke="#222" /><line x1="540" y1="50" x2="540" y2="281" stroke="#222" /><line x1="198" y1="50" x2="578" y2="50" stroke="#222" /><line x1="198" y1="88" x2="578" y2="88" stroke="#222" /><line x1="198" y1="126" x2="578" y2="126" stroke="#222" /><line x1="198" y1="164" x2="578" y2="164" stroke="#222" /><line x1="198" y1="202" x2="578" y2="202" stroke="#222" /><line x1="198" y1="240" x2="578" y2="240" stroke="#222" /><line x1="198" y1="278" x2="578" y2="278" stroke="#222" /><rect x="330.0" y="121.0" width="70.0" height="70.0" rx="3" fill="#3a6ea5" /><circle cx="460" cy="151" r="26" fill="#a5543a"/><text x="206.0" y="71.0" style="fill:#a0e0a0;font-family:Consolas,'Courier New',monospace;font-size:13px;" >FPS 60</text><rect x="198.0" y="285.0" width="380.0" height="107.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="198.0" y="285.0" width="380.0" height="19.0" rx="0" fill="#0a0a0a" /><path d="M205,291 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="218.0" y="299.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Console</text><text x="206.0" y="326.0" style="fill:#9fe0a0;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[info] Scene loaded</text><text x="206.0" y="349.0" style="fill:#e8c060;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[warn] Texture missing: wall.png</text><text x="206.0" y="372.0" style="fill:#f07070;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[error] Shader compile failed</text><rect x="582.0" y="31.0" width="184.0" height="361.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="582.0" y="31.0" width="184.0" height="19.0" rx="0" fill="#0a0a0a" /><path d="M589,37 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="602.0" y="45.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Inspector</text><text x="590.0" y="72.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Player</text><rect x="583.0" y="83.0" width="182.0" height="1.0" rx="0" fill="#5c5c6e" /><rect x="584.0" y="89.0" width="180.0" height="19.0" rx="0" fill="#24435f" /><path d="M592,95 l10,0 l-5,9 z" fill="#ffffff"/><text x="608.0" y="103.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Transform</text><rect x="590.0" y="112.0" width="104.0" height="19.0" rx="3" fill="#1d2f49" /><text x="626.0" y="126.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >0.00</text><text x="702.0" y="126.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >x</text><rect x="590.0" y="135.0" width="104.0" height="19.0" rx="3" fill="#1d2f49" /><text x="626.0" y="149.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >1.50</text><text x="702.0" y="149.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >y</text><rect x="584.0" y="158.0" width="180.0" height="19.0" rx="0" fill="#24435f" /><path d="M592,164 l10,0 l-5,9 z" fill="#ffffff"/><text x="608.0" y="172.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Rigidbody</text><rect x="590.0" y="181.0" width="17.0" height="17.0" rx="3" fill="#1d2f49" /><path d="M594,190 l4,4 l7,-8" fill="none" stroke="#4296fa" stroke-width="2.2"/><text x="611.0" y="195.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Gravity</text><rect x="198" y="31" width="380" height="250" fill="none" stroke="#4296fa" stroke-width="2" stroke-dasharray="6 4" opacity="0"><animate attributeName="opacity" dur="4s" repeatCount="indefinite" values="0;0;0.9;0;0"/></rect></svg>

ドッキングするとウィンドウが 1 つの画面にまとまります（Scene・Hierarchy・Inspector・Console）。点線の枠はウィンドウをドラッグしたときに出るドロップ先の目印のイメージです。

## メインウィンドウ全体をドッキング領域にする

**エディタのようにアプリの画面全体**をドッキング領域にします。

```cpp
ImGui::DockSpaceOverViewport(0, ImGui::GetMainViewport());
```

| 点 | 説明 |
| --- | --- |
| `DockSpaceOverViewport(...)` | メイン ビューポート全体にドッキング領域を作る（メニューバーの下など、作業領域に合わせる） |
| 毎フレーム、`NewFrame` の後に呼ぶ | ほかのウィンドウを作る前に |
| シグネチャ | バージョンで引数が違う（`dockspace_id`、`viewport`、`flags`、…）。使っているバージョンのヘッダで確認 |

### 背景を透けさせる（ゲームの画面を見せる）

ドッキング領域の「中央」を空けておくとゲームの画面が、背景に見えます。

```cpp
ImGui::DockSpaceOverViewport(0, ImGui::GetMainViewport(), ImGuiDockNodeFlags_PassthruCentralNode);
```

| フラグ | 意味 |
| --- | --- |
| `ImGuiDockNodeFlags_PassthruCentralNode` | 中央のノードを透明にして、後ろの描画（ゲーム）が見える |
| `ImGuiDockNodeFlags_NoDockingInCentralNode` | 中央にドッキングさせない |
| `ImGuiDockNodeFlags_AutoHideTabBar` | 1 つしかないタブのタブバーを隠す |

ゲームの画面をそのまま背景に出し、周りにパネルを並べる構成です。シーンビューをウィンドウに入れたい場合は、レンダー ターゲットにします（[テクスチャ](textures.md)）。

## 自分でドックスペース ウィンドウを作る

**メニューバーを含む自作のウィンドウ**にドッキング領域を置く方法です。

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

`DockSpace` はドッキング領域そのものを作ります。この方法だと自作のメニューバーや固定のツールバーを同じウィンドウに入れられます。

## レイアウトの保存と読み込み

| 方法 | 説明 |
| --- | --- |
| <strong>`imgui.ini`（自動）</strong> | ウィンドウの位置・大きさ・ドッキングの配置が、自動で保存・復元される（`io.IniFilename`） |
| 保存先を変える | `io.IniFilename = "layout.ini";`、または `nullptr` で保存しない |
| 文字列で保存・読み込み | `ImGui::SaveIniSettingsToMemory()` / `LoadIniSettingsFromMemory(data)` で、独自のファイル・メモリへ |
| `SaveIniSettingsToDisk(path)` / `LoadIniSettingsFromDisk(path)` | 別のファイルへ保存・読み込み（複数のレイアウト切り替えに） |

```cpp
if (ImGui::MenuItem("レイアウトを保存")) ImGui::SaveIniSettingsToDisk("layouts/my_layout.ini");
if (ImGui::MenuItem("レイアウトを読み込み")) ImGui::LoadIniSettingsFromDisk("layouts/my_layout.ini");
```

### 初期のレイアウトをコードで作る（DockBuilder）

初回起動のときに決まったレイアウト（左に階層、右にインスペクタ、下にログ）にしたい場合は`DockBuilder`（`imgui_internal.h`）を使います。

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
| `DockBuilderSplitNode(node, 向き, 割合, 新しい側, 残りの側)` | 領域を分割 |
| `DockBuilderDockWindow("名前", node)` | ウィンドウをその領域に置く |
| `DockBuilderFinish` | 確定 |

`imgui_internal.h` は内部 API で、バージョンで変わることがあります。

## マルチビューポート

**ImGui のウィンドウをアプリのウィンドウの外（別の OS ウィンドウ）に出せる**機能です（デュアルモニターで、パネルを別の画面へ）。

```cpp
io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;
```

| 点 | 説明 |
| --- | --- |
| バックエンドの対応が必要 | Win32 + DirectX 11 は、対応している |
| 描画のあとに追加の呼び出し | メインの描画が終わったあとに、`UpdatePlatformWindows()` と `RenderPlatformWindowsDefault()` を呼ぶ |
| スタイルの調整 | ウィンドウの角丸・背景の透明が、OS ウィンドウでは違和感がある → `WindowRounding = 0`、`WindowBg.w = 1` |

```cpp
ImGui::Render();
ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
  ImGui::UpdatePlatformWindows();
  ImGui::RenderPlatformWindowsDefault();
}
```

!!! warning "デバイス・スワップチェーンの扱い"
    マルチビューポートでは、ImGui が追加のスワップチェーンを作ります。デバイスのコンテキストの設定（レンダー ターゲット・ビューポート）を、メインの描画の後に再設定する必要があるかもしれません。公式サンプル（`example_win32_directx11`）を参考にします。

## ゲームの画面をドッキングできるウィンドウにする

**エディタ風**にゲームの画面をウィンドウの中に出すには、レンダー ターゲットに描画し、`ImGui::Image` で表示します（[テクスチャ](textures.md#sceneview)）。

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

ウィンドウの大きさに合わせて、レンダー ターゲットを作り直すことが、ポイントです。

## よくあるミス

??? failure "ドッキングできない"
    **`docking` ブランチではない**、または `ImGuiConfigFlags_DockingEnable` を設定していません。

??? failure "`DockSpaceOverViewport` をウィンドウより後に呼んでいる"
    ドッキング領域より先にウィンドウを作るとドッキングが、うまく効かないことがあります。`NewFrame` の直後に呼びます。

??? failure "`imgui.ini` が、古いレイアウトを復元して初期レイアウトが反映されない"
    `imgui.ini` を消すか`DockBuilderGetNode` で、ノードがないときだけ作る処理にします。

??? failure "マルチビューポートで、ウィンドウが真っ黒・描画が崩れる"
    `RenderPlatformWindowsDefault()` を呼んでいません。描画後に呼び出します。

??? failure "シーンビューが、ぼやける・伸びる"
    ウィンドウの大きさに合わせて、レンダー ターゲットのサイズを変えています。拡大縮小で伸びていませんか。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ドッキングは<strong>`docking` ブランチ</strong>（vcpkg は `docking-experimental`）。`ImGuiConfigFlags_DockingEnable` で有効に
    - [x] `DockSpaceOverViewport` で、画面全体をドッキング領域に。`PassthruCentralNode` で中央を透かす
    - [x] レイアウトは `imgui.ini` に自動保存。初期レイアウトは `DockBuilder`
    - [x] マルチビューポートは `ViewportsEnable` ＋ 描画後に `UpdatePlatformWindows` / `RenderPlatformWindowsDefault`
    - [x] シーンビューは、レンダー ターゲット ＋ `ImGui::Image`

## 関連ページ

- [Dear ImGui](index.md)
- [レイアウトとウィンドウ](layout.md)
- [テクスチャと画像](textures.md)
- [スタイルとテーマ](style.md)
- [ImGuizmo](imguizmo.md)

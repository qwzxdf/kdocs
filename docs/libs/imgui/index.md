---
title: Dear ImGui
tags:
  - 外部ライブラリ
  - GUI
---

# Dear ImGui

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11〜</span>
`#include "imgui.h"`
</div>

**Dear ImGui**（ディア・イムグイ）は、ゲームの**デバッグ画面**や**エディタ**を、**とても少ないコードで作れる GUI ライブラリ**です。ボタンもスライダーも、`if (ImGui::Button("Reset")) { ... }` のように**毎フレーム、関数を呼ぶだけ**で出せます。ウィンドウの部品を作って保持する、という普通の GUI の面倒さがありません。この仕組みを <strong>即時モード GUI（Immediate Mode GUI）</strong> と言います。ゲームのパラメータを実行中に変える、オブジェクトの一覧を出す、フレーム時間のグラフを出す、といった用途で、ゲーム業界で広く使われています。ここから、ギズモ（[ImGuizmo](imguizmo.md)）、タイムライン（[ImSequencer](imsequencer.md)）、ノード エディタ（[imgui-node-editor](node-editor.md)）などの拡張ライブラリも広がっています。

!!! tip "ポイント"
    - <strong>毎フレーム、`ImGui::` の関数を呼んで画面を作る。</strong> 部品を作って保持しない（即時モード）。
    - 1 フレームは **`NewFrame()` → 好きな ImGui の関数 → `Render()` → 描画** の流れ。
    - ImGui 本体は**描画そのものをしない**。描画する **バックエンド**（DirectX 11、OpenGL、Vulkan など）と、ウィンドウの**プラットフォーム**（Win32、GLFW、SDL）の組み合わせを選ぶ。
    - Windows + Visual Studio なら、**Win32 + DirectX 11** の組み合わせが一番簡単。
    - 同じ名前のウィジェットは**同じもの**として扱われる。複数並べるなら `##id` や `PushID` で区別する。

!!! warning "TODO"
    このページは、**導入と基本の流れ**だけを書いています。ウィジェットの一覧、レイアウト、ドッキング、日本語フォント、テーブルなどは、下の「これから書くページ」に分けて追加していきます。

## 導入（Visual Studio） {#install}

**まず Visual Studio での入れ方**を説明します。Dear ImGui は、**ソースファイルをプロジェクトに入れる**のが基本です（ヘッダだけではなく `.cpp` もあります）。バックエンドのファイルも必要です。

### 方法 1：ソースを入れる（おすすめ・一番確実）

1. [GitHub の ImGui](https://github.com/ocornut/imgui) から取得する（`git clone`、または Releases の ZIP）。`third_party/imgui/` に置く
2. 次のファイルを、ソリューション エクスプローラーで**プロジェクトに追加**（追加 → 既存の項目）

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
    ImGui 本体は古い C++ でも動くように書かれていて、C++23 でもそのままビルドできます。ビルドの警告が気になるなら、`third_party` を「外部インクルード ディレクトリ」に入れます（[外部ヘッダの警告](../../vs/libraries.md#external_include)）。

### 方法 2：vcpkg で入れる

```powershell
vcpkg install imgui[win32-binding,dx11-binding]:x64-windows
```

- `[ ]` の中は**使うバックエンド**（機能）の指定です。マニフェスト モード（`vcpkg.json`）なら、次のように書きます

```json
{
  "dependencies": [
    { "name": "imgui", "features": ["win32-binding", "dx11-binding", "docking-experimental"] }
  ]
}
```

- `docking-experimental` は、ウィンドウをドッキングできる機能です（[ドッキング](#todo_pages)）
- vcpkg 版を使うと、`#include <imgui.h>` や `#include <backends/imgui_impl_dx11.h>` のように書きます（インクルードの書き方がソースを入れる方法と少し違います）

### 方法 3：CMake（FetchContent）

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

## 仕組み：即時モード GUI

普通の GUI（Windows のフォーム、Unity の UI など）は、**部品（オブジェクト）を作って、画面に置いて、イベントを待つ**「保持モード」です。ImGui は逆に、**毎フレーム、「今こうなっている」と描くたびに伝える**だけです。

```cpp
// 保持モード（イメージ）
Button* reset = new Button("Reset");
reset->OnClick([] { Reset(); });
window->Add(reset);

// 即時モード（ImGui）：毎フレーム、これを呼ぶだけ
if (ImGui::Button("Reset")) {  // 押されたフレームだけ true
  Reset();
}
```

| 項目 | 保持モード | 即時モード（ImGui） |
| --- | --- | --- |
| 部品の管理 | 作って、保持して、消す | **しない** |
| 値の同期 | 変数と部品の値を合わせる | **変数そのものを渡す**（`SliderFloat("速さ", &speed, ...)`） |
| 表示・非表示 | 部品の表示フラグ | `if` で呼ぶか呼ばないか |
| コードの量 | 多い | **少ない** |
| 弱点 | — | 見た目の自由度が低い（デバッグ・ツール向き）。毎フレーム再構築するので、重い画面は工夫が必要 |

## 1 フレームの流れ

<div class="anim" data-type="graph" data-label="ImGui を使う 1 フレーム">
n a ゲーム更新 0 0 hit
n b NewFrame 1 0
n c ウィジェット 2 0
n d Render 3 0
n e ゲーム描画 4 0
l a b
l b c
l c d
l d e
# ゲームの更新をする
---
n a ゲーム更新 0 0
n b NewFrame 1 0 hit
n c ウィジェット 2 0
n d Render 3 0
n e ゲーム描画 4 0
l a b hit
l b c
l c d
l d e
# NewFrame：バックエンドと ImGui のフレームを始める
---
n a ゲーム更新 0 0
n b NewFrame 1 0
n c ウィジェット 2 0 hit
n d Render 3 0
n e ゲーム描画 4 0
l a b
l b c hit
l c d
l d e
# Begin / Button / Slider など、ImGui の関数を好きなだけ呼ぶ
---
n a ゲーム更新 0 0
n b NewFrame 1 0
n c ウィジェット 2 0
n d Render 3 0 hit
n e ゲーム描画 4 0
l a b
l b c
l c d hit
l d e
# Render：描画データを作る（まだ画面には出ない）
---
n a ゲーム更新 0 0
n b NewFrame 1 0
n c ウィジェット 2 0
n d Render 3 0
n e ゲーム描画 4 0 hit
l a b
l b c
l c d
l d e hit
# ゲームの画面を描いたあと、最後に RenderDrawData で ImGui を重ねる
</div>


### 最小のコード（DirectX 11 + Win32）

ウィンドウと DirectX 11 の初期化（`CreateDeviceD3D`、`WndProc` など）は、ImGui の `examples/example_win32_directx11/main.cpp` と同じです。**そのファイルをプロジェクトにコピーして動かすのが、一番確実な最初の一歩**です。ImGui に関係する部分だけ抜き出すと、次のようになります。

```cpp
#include "imgui.h"
#include "imgui_impl_dx11.h"
#include "imgui_impl_win32.h"

// WndProc の中で、ImGui にもメッセージを渡す（これを忘れるとマウス・キーが効かない）
extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(
    HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);

LRESULT CALLBACK WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
  if (ImGui_ImplWin32_WndProcHandler(hWnd, msg, wParam, lParam)) {
    return true;
  }
  // ... 自分のメッセージ処理 ...
  return DefWindowProcW(hWnd, msg, wParam, lParam);
}

// ---- 初期化（ウィンドウと DirectX のデバイスを作った後で 1 回） ----
void InitImGui(HWND hwnd, ID3D11Device* device, ID3D11DeviceContext* context) {
  IMGUI_CHECKVERSION();
  ImGui::CreateContext();
  ImGuiIO& io = ImGui::GetIO();
  io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;  // キーボードで操作

  ImGui::StyleColorsDark();  // 見た目（ダーク）

  ImGui_ImplWin32_Init(hwnd);
  ImGui_ImplDX11_Init(device, context);
}

// ---- 毎フレーム ----
void DrawDebugUi(float& speed, bool& paused) {
  ImGui_ImplDX11_NewFrame();
  ImGui_ImplWin32_NewFrame();
  ImGui::NewFrame();

  ImGui::Begin("デバッグ");  // ウィンドウを開く（なければ作られる）
  ImGui::Text("FPS: %.1f", ImGui::GetIO().Framerate);
  ImGui::SliderFloat("速さ", &speed, 0.0f, 10.0f);
  ImGui::Checkbox("一時停止", &paused);
  if (ImGui::Button("リセット")) {
    speed = 1.0f;
    paused = false;
  }
  ImGui::End();

  ImGui::Render();
  // ここでゲームの画面を描いたあと、最後に ImGui を重ねる
  ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
}

// ---- 終了 ----
void ShutdownImGui() {
  ImGui_ImplDX11_Shutdown();
  ImGui_ImplWin32_Shutdown();
  ImGui::DestroyContext();
}
```

!!! warning "日本語が `?` になる"
    ImGui の標準フォントには**日本語の字がありません**。日本語を出すには、日本語に対応したフォント（Windows の `C:\Windows\Fonts\meiryo.ttc` など）を読み込む必要があります。[日本語フォント](#todo_pages) のページで説明します（これから書きます）。ひとまず、`io.Fonts->AddFontFromFileTTF("C:\\Windows\\Fonts\\meiryo.ttc", 18.0f, nullptr, io.Fonts->GetGlyphRangesJapanese());` を初期化の最後に書くと表示できます。

## バックエンドの組み合わせ

ImGui は、**プラットフォーム**（ウィンドウ・入力）と**レンダラー**（描画）を別々に選びます。

| プラットフォーム | 説明 |
| --- | --- |
| `imgui_impl_win32` | Win32 API（Windows 専用）。ウィンドウを自分で作る場合 |
| `imgui_impl_glfw` | GLFW。OpenGL / Vulkan で、ウィンドウを簡単に作れる |
| `imgui_impl_sdl2` / `imgui_impl_sdl3` | SDL。ゲームの入力（ゲームパッド）にも強い |

| レンダラー | 説明 |
| --- | --- |
| `imgui_impl_dx11` | DirectX 11。Windows で一番よく使われる |
| `imgui_impl_dx12` | DirectX 12 |
| `imgui_impl_opengl3` | OpenGL 3 以降 |
| `imgui_impl_vulkan` | Vulkan |

自作のゲームエンジンで、すでに DirectX 11 を使っているなら、`imgui_impl_win32` + `imgui_impl_dx11` が最も簡単です。

## よく使う関数（入口だけ）

| 関数 | 何をする |
| --- | --- |
| `ImGui::Begin("名前")` / `ImGui::End()` | ウィンドウを開始・終了する。ここまでの間に部品を並べる |
| `ImGui::Text("...")` | 文字を出す（`printf` の書式が使える） |
| `ImGui::Button("名前")` | ボタン。押されたフレームだけ `true` |
| `ImGui::Checkbox("名前", &flag)` | チェックボックス。`bool` を直接渡す |
| `ImGui::SliderFloat("名前", &v, min, max)` | スライダー |
| `ImGui::InputText("名前", buf, size)` | 文字の入力欄 |
| `ImGui::ColorEdit3("名前", color)` | 色の選択 |
| `ImGui::TreeNode("名前")` | 折りたためる項目（`TreePop()` で閉じる） |
| `ImGui::ShowDemoWindow()` | **デモ ウィンドウ**。全部の部品が動いて見える |

!!! tip "デモ ウィンドウを見る"
    ImGui の使い方で迷ったら、**`ImGui::ShowDemoWindow();` を毎フレーム呼んで、動かして<strong>見ます。ほとんどの部品の見た目と、</strong>その部品を出すコードの場所**が分かります（`imgui_demo.cpp` に全部書いてあります）。

## よくあるミス

??? failure "ウィジェットの名前が重複して、片方しか動かない"
    ImGui は、**名前から ID を作って**部品を区別しています。同じ名前のボタンを 2 つ並べると、同じ部品とみなされて、一方しか反応しません。`ImGui::Button("削除##1")`、`ImGui::Button("削除##2")` のように、`##` のあとに ID を付けます（`##` より後ろは表示されません）。ループの中では `ImGui::PushID(i);` ... `ImGui::PopID();` で囲みます。

??? failure "`Begin` と `End`、`TreeNode` と `TreePop` の組が合っていない"
    `Begin()` は、返り値が `false` でも、**必ず `End()` を呼びます**（これは例外）。`TreeNode()` が `true` のときだけ `TreePop()` を呼びます。合っていないと、実行時にアサートで止まります。

??? failure "ImGui の上でクリックしたのに、ゲームの操作も反応する"
    ImGui のウィンドウ上でマウスを使っているのに、ゲーム側もクリックを受け取ってしまいます。`ImGui::GetIO().WantCaptureMouse` が `true` のときは、ゲーム側でマウスの入力を無視します（キーボードは `WantCaptureKeyboard`）。

??? failure "NewFrame を呼ぶ順番が違う"
    `ImGui_ImplDX11_NewFrame()` → `ImGui_ImplWin32_NewFrame()` → `ImGui::NewFrame()` の順番を守ります。`Render()` の後に、画面の描画で ImGui を呼ぶのを忘れると、何も表示されません。

??? failure "リリースビルドにも ImGui が入っている"
    デバッグ用の画面なので、製品版では**ビルドに含めない**ようにします（`#ifdef _DEBUG` で囲む、`IMGUI_DISABLE` を定義する、など）。

## これから書くページ {#todo_pages}

| ページ | 内容 | 状態 |
| --- | --- | --- |
| [ImGuizmo](imguizmo.md) | 3D のギズモ（移動・回転・拡大の矢印） | **書いた** |
| [ImSequencer](imsequencer.md) | タイムラインの編集 | **書いた** |
| [imgui-node-editor](node-editor.md) | ノード エディタ | **書いた** |
| [ウィジェット一覧](widgets.md) | ボタン、スライダー、入力、リスト、コンボ、テーブル | TODO |
| [レイアウトとウィンドウ](layout.md) | 配置、`SameLine`、`Columns`、ウィンドウのフラグ、子ウィンドウ | TODO |
| [ドッキングとビューポート](docking.md) | ウィンドウのドッキング、ウィンドウをアプリの外に出す | TODO |
| [日本語フォントとアイコン](fonts.md) | 日本語の表示、アイコン フォント、フォントのサイズ | TODO |
| [スタイルとテーマ](style.md) | 色、角の丸み、余白、ダーク / ライト | TODO |
| [テクスチャと画像](textures.md) | `ImGui::Image`、ゲームの画面をウィンドウの中に出す | TODO |
| [ゲームでのデバッグ画面](debug-ui.md) | フレーム時間のグラフ、ログ、エンティティのインスペクター | TODO |

## 関連ページ

- [ImGuizmo](imguizmo.md)
- [ImSequencer](imsequencer.md)
- [imgui-node-editor](node-editor.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
- [Dear ImGui（GitHub）](https://github.com/ocornut/imgui)
- [ImGui の Wiki](https://github.com/ocornut/imgui/wiki)

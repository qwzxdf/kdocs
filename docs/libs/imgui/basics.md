---
title: ImGui の仕組みと最小のコード
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui の仕組みと最小のコード

**即時モード**の考え方、1 フレームの流れ、DirectX 11 + Win32 の最小のコード、バックエンドの選び方、よくあるミスをまとめます。

## 仕組み：即時モード GUI

普通の GUI（Windows のフォーム、Unity の UI など）は、**部品（オブジェクト）を作って、画面に置いて、イベントを待つ**「保持モード」です。ImGui は逆に、毎フレーム、「今こうなっている」と描くたびに伝えるだけです。

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
| 部品の管理 | 作って、保持して、消す | しない |
| 値の同期 | 変数と部品の値を合わせる | 変数そのものを渡す（`SliderFloat("速さ", &speed, ...)`） |
| 表示・非表示 | 部品の表示フラグ | `if` で呼ぶか呼ばないか |
| コードの量 | 多い | 少ない |
| 弱点 | — | 見た目の自由度が低い（デバッグ・ツール向き）。毎フレーム再構築するので、重い画面は工夫が必要 |


## 1 フレームの流れ

<svg class="fig flow" viewBox="0 0 778 112" role="img" aria-label="ImGui を使う 1 フレーム"><defs><marker id="fl55364" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ImGui を使う 1 フレーム</text><line x1="127.0" y1="64.0" x2="185.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl55364)"/><line x1="279.0" y1="64.0" x2="337.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl55364)"/><line x1="453.0" y1="64.0" x2="511.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl55364)"/><line x1="593.0" y1="64.0" x2="651.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl55364)"/><rect x="28.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="76.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム更新</text><rect x="188.0" y="44.0" width="88" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="232.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">NewFrame</text><rect x="340.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="395.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ウィジェット</text><rect x="514.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="552.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Render</text><rect x="654.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="702.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム描画</text></svg>


## 最小のコード（DirectX 11 + Win32）

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
    ImGui の標準フォントには日本語の字がありません。日本語を出すには、日本語に対応したフォント（Windows の `C:\Windows\Fonts\meiryo.ttc` など）を読み込む必要があります。[日本語フォントとアイコン](fonts.md) のページで説明します。ひとまず、`io.Fonts->AddFontFromFileTTF("C:\\Windows\\Fonts\\meiryo.ttc", 18.0f, nullptr, io.Fonts->GetGlyphRangesJapanese());` を初期化の最後に書くと表示できます。


## バックエンドの組み合わせ

ImGui は、**プラットフォーム**（ウィンドウ・入力）とレンダラー（描画）を別々に選びます。

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


!!! info "このページを読む前に"
    - [Dear ImGui](index.md)（このセクション全体の地図と、読む順番）
    - [Dear ImGui の導入（Visual Studio）](install.md)（ImGui の入れ方）

<!-- fig:imgui-frame-loop:begin -->

<svg class="fig illust motion" data-fig="imgui-frame-loop" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-imgui-frame-loop" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ImGui は毎フレーム、画面を最初から組み立て直す(状態は自分の変数に持つ)</text>
<rect x="70" y="120" width="190" height="80" fill="#ffffff" stroke="#94a3b8" stroke-width="2.5"/>
<text x="165" y="166" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">NewFrame()</text>
<line x1="262" y1="160" x2="366" y2="160" stroke="#64748b" stroke-width="3" marker-end="url(#arr-imgui-frame-loop)" opacity="1"/>
<rect x="300" y="120" width="190" height="80" fill="#ffffff" stroke="#94a3b8" stroke-width="2.5"/>
<text x="395" y="166" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">Button() などの呼び出し</text>
<line x1="492" y1="160" x2="596" y2="160" stroke="#64748b" stroke-width="3" marker-end="url(#arr-imgui-frame-loop)" opacity="1"/>
<rect x="530" y="120" width="190" height="80" fill="#ffffff" stroke="#94a3b8" stroke-width="2.5"/>
<text x="625" y="166" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">Render() → 描画</text>
<rect x="70" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.1255;0.1257;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="300" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1255;0.1257;0.1941;0.1943;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="530" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2626;0.2629;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="70" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3141;0.3143;0.3826;0.3829;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="300" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3826;0.3829;0.4512;0.4514;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="530" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4512;0.4514;0.5198;0.5200;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="70" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5712;0.5714;0.6398;0.6400;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="300" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6398;0.6400;0.7083;0.7086;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<rect x="530" y="120" width="190" height="80" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.7083;0.7086;0.7769;0.7771;1.0000" values="0;0;0.35;0.35;0;0"/></rect>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ゲームのループが 1 回まわるのが、1 フレーム<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 1: ボタンは押されていない → Button() は false を返す。hp = 100<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.3141;0.3143;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 2: ボタンが押された → Button() が true を返す。if の中で hp-- して 99 に<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3141;0.3143;0.5712;0.5714;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 3: 押されていない → false。hp は 99 のまま(変数に残っている)<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5712;0.5714;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">UI の部品は残らない。毎回「いま何を表示するか」を書き直す(即時モード)</text>
</svg>

<!-- fig:imgui-frame-loop:end -->

## よくあるミス

??? failure "ウィジェットの名前が重複して、片方しか動かない"
    ImGui は、**名前から ID を作って**部品を区別しています。同じ名前のボタンを 2 つ並べると、同じ部品とみなされて、一方しか反応しません。`ImGui::Button("削除##1")`、`ImGui::Button("削除##2")` のように、`##` のあとに ID を付けます（`##` より後ろは表示されません）。ループの中では `ImGui::PushID(i);` ... `ImGui::PopID();` で囲みます。

??? failure "`Begin` と `End`、`TreeNode` と `TreePop` の組が合っていない"
    `Begin()` は、返り値が `false` でも、必ず `End()` を呼びます（これは例外）。`TreeNode()` が `true` のときだけ `TreePop()` を呼びます。合っていないと、実行時にアサートで止まります。

??? failure "ImGui の上でクリックしたのに、ゲームの操作も反応する"
    ImGui のウィンドウ上でマウスを使っているのに、ゲーム側もクリックを受け取ってしまいます。`ImGui::GetIO().WantCaptureMouse` が `true` のときは、ゲーム側でマウスの入力を無視します（キーボードは `WantCaptureKeyboard`）。

??? failure "NewFrame を呼ぶ順番が違う"
    `ImGui_ImplDX11_NewFrame()` → `ImGui_ImplWin32_NewFrame()` → `ImGui::NewFrame()` の順番を守ります。`Render()` の後に画面の描画で ImGui を呼ぶのを忘れると、何も表示されません。

??? failure "リリースビルドにも ImGui が入っている"
    デバッグ用の画面なので、製品版ではビルドに含めないようにします（`#ifdef _DEBUG` で囲む、`IMGUI_DISABLE` を定義する、など）。

## 関連ページ

- [Dear ImGui（目次）](index.md)
- [ウィジェット一覧](widgets.md)
- [レイアウトとウィンドウ](layout.md)


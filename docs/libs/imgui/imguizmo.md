---
title: ImGuizmo
tags:
  - 外部ライブラリ
  - GUI
---

# ImGuizmo

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11〜</span>
`#include "ImGuizmo.h"`
</div>

**ImGuizmo**（イムグイズモ）は、[Dear ImGui](index.md) の拡張ライブラリで、3D シーンの中に、移動・回転・拡大の矢印（ギズモ）を出して、マウスで操作できるようにします。Unity や Blender で、オブジェクトを選ぶと出てくる、赤・緑・青の矢印と同じものです。ゲーム エディタを自作するときの、オブジェクトの配置に欠かせない部品です。使い方は「カメラの行列（ビューとプロジェクション）と、オブジェクトのワールド行列を渡す → 操作された結果が、行列に書き戻される」の 1 つの関数 `Manipulate` が中心です。

!!! tip "ポイント"
    - 毎フレーム、**`ImGui::NewFrame()` の後に `ImGuizmo::BeginFrame()`** を呼ぶ。
    - ギズモを出すには、**ビュー行列・プロジェクション行列・オブジェクトのワールド行列**（それぞれ `float[16]`）を `ImGuizmo::Manipulate` に渡す。
    - ワールド行列は参照渡しで、操作するとその場で書き換わる。書き換わった行列を、ゲーム側のオブジェクトの位置・回転・拡大に戻す。
    - 行列は 列優先（OpenGL・glm と同じ並び） の `float[16]`。DirectX の行優先（DirectXMath）で持っているなら、転置して渡す。
    - 描く場所は `SetRect` と `SetDrawlist` で指定する。シーン ビューのウィンドウの中に出すのが定番。
    - 操作の種類（移動・回転・拡大）と、空間（ローカル・ワールド）は、`OPERATION` と `MODE` で切り替える。

## 導入（Visual Studio）

ImGuizmo は、**ソースを数ファイル、プロジェクトに追加する**だけで使えます。先に [Dear ImGui の導入](install.md) を済ませておきます。

### 方法 1：ソースを入れる

1. [GitHub の ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo) を取得して、`third_party/ImGuizmo/` に置く
2. 次のファイルをプロジェクトに追加（追加 → 既存の項目）

| ファイル | 内容 |
| --- | --- |
| `ImGuizmo.h` / `ImGuizmo.cpp` | ギズモ本体 |
| `ImSequencer.h` / `ImSequencer.cpp` | タイムライン（[ImSequencer](imsequencer.md) でも使う） |
| `ImCurveEdit.h` / `ImCurveEdit.cpp` | カーブ エディタ（使わなければ入れなくてよい） |
| `GraphEditor.h` / `GraphEditor.cpp` | 簡易ノード エディタ（使わなければ入れなくてよい） |

3. 追加のインクルード ディレクトリ に `$(SolutionDir)third_party\ImGuizmo` を追加する
4. ImGuizmo は ImGui の内部ヘッダ（`imgui_internal.h`）を使うので、ImGui のインクルード パスも通しておく

### 方法 2：vcpkg

```powershell
vcpkg install imguizmo:x64-windows
```

ポートの名前やバージョンは変わることがあるので、`vcpkg search imguizmo` で確認します。vcpkg の ImGui（`imgui`）と一緒に入れます。

!!! note "数学ライブラリ"
    ギズモに渡す行列は `float[16]` です。ゲーム側で glm（`vcpkg install glm`）や DirectXMath を使っていれば、そこから取り出して渡します。ImGuizmo 自身は、行列の計算に使う関数（`DecomposeMatrixToComponents` など）を持っています。

## 基本の使い方

最小の流れは、次のとおりです。シーン ビューのウィンドウの中に、オブジェクトを動かせるギズモを出します。

```cpp
#include "ImGuizmo.h"
#include "imgui.h"

struct SceneView {
  float view[16];        // カメラのビュー行列（列優先）
  float projection[16];  // プロジェクション行列
  float model[16];       // 選択中のオブジェクトのワールド行列

  ImGuizmo::OPERATION operation = ImGuizmo::TRANSLATE;  // 移動
  ImGuizmo::MODE mode = ImGuizmo::LOCAL;                // ローカル座標
};

void DrawSceneView(SceneView& scene) {
  ImGui::Begin("シーン");

  // ① ギズモを描く場所（このウィンドウの中）を教える
  ImGuizmo::SetOrthographic(false);        // 透視投影なら false
  ImGuizmo::SetDrawlist();                 // 今の ImGui ウィンドウに描く
  ImVec2 pos = ImGui::GetWindowPos();
  ImVec2 size = ImGui::GetWindowSize();
  ImGuizmo::SetRect(pos.x, pos.y, size.x, size.y);

  // ② ギズモを出して、操作を受け付ける。操作すると scene.model が書き換わる
  ImGuizmo::Manipulate(scene.view, scene.projection, scene.operation, scene.mode,
                       scene.model);

  ImGui::End();
}

// ---- 毎フレームの流れ ----
void Frame(SceneView& scene) {
  ImGui_ImplDX11_NewFrame();
  ImGui_ImplWin32_NewFrame();
  ImGui::NewFrame();
  ImGuizmo::BeginFrame();  // ← NewFrame の直後に必ず呼ぶ

  DrawSceneView(scene);

  ImGui::Render();
  ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
}
```

### 流れ

<svg class="fig flow" viewBox="0 0 535 280" role="img" aria-label="ギズモの流れ"><defs><marker id="fl6237" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ギズモの流れ</text><line x1="124.0" y1="84.2" x2="206.8" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl6237)"/><text x="165.4" y="98.6" text-anchor="middle" style="font-size:12px">view projection</text><line x1="129.7" y1="209.0" x2="206.8" y2="171.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl6237)"/><text x="168.2" y="184.0" text-anchor="middle" style="font-size:12px">ワールド行列</text><line x1="308.0" y1="148.0" x2="366.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl6237)"/><text x="337.0" y="142.0" text-anchor="middle" style="font-size:12px">ドラッグで書き換え</text><line x1="366.0" y1="165.0" x2="141.0" y2="218.3" stroke="currentColor" stroke-width="2" marker-end="url(#fl6237)"/><text x="253.5" y="185.7" text-anchor="middle" style="font-size:12px">Decompose</text><rect x="45.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="83.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">カメラ</text><rect x="28.0" y="212.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="83.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">オブジェクト</text><rect x="202.0" y="128.0" width="103" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="253.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Manipulate</text><rect x="369.0" y="128.0" width="138" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="438.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">書き換わった行列</text></svg>


## 位置・回転・拡大を行列と相互に変換する

エディタでは、オブジェクトの <strong>位置（Translation）・回転（Rotation：度）・拡大（Scale）</strong> を、インスペクター（ImGui の入力欄）で数値でも編集します。ギズモは行列を直接書き換えるので、行列 ⇔ 3 つの値の変換が必要です。ImGuizmo が用意しています。

```cpp
struct Transform {
  float translation[3] = {0.0f, 0.0f, 0.0f};
  float rotation[3] = {0.0f, 0.0f, 0.0f};  // 度（オイラー角）
  float scale[3] = {1.0f, 1.0f, 1.0f};
};

void EditTransform(Transform& t, const float* view, const float* projection,
                   ImGuizmo::OPERATION operation) {
  // ① 3 つの値から行列を作る
  float model[16];
  ImGuizmo::RecomposeMatrixFromComponents(t.translation, t.rotation, t.scale, model);

  // ② インスペクター（数値で編集）
  ImGui::InputFloat3("位置", t.translation);
  ImGui::InputFloat3("回転", t.rotation);
  ImGui::InputFloat3("拡大", t.scale);
  ImGuizmo::RecomposeMatrixFromComponents(t.translation, t.rotation, t.scale, model);

  // ③ ギズモ（マウスで編集）
  ImGuizmo::Manipulate(view, projection, operation, ImGuizmo::LOCAL, model);

  // ④ 操作された行列から、3 つの値を取り出して戻す
  if (ImGuizmo::IsUsing()) {
    ImGuizmo::DecomposeMatrixToComponents(model, t.translation, t.rotation, t.scale);
  }
}
```

## 関数・型の詳しい説明

### BeginFrame {#beginframe}

```cpp
namespace ImGuizmo {
void BeginFrame();
}
```

- 戻り値: なし
- 毎フレーム、**`ImGui::NewFrame()` の直後**に 1 回だけ呼びます。ギズモの内部状態（マウスの位置など）をそのフレーム用に準備します
- 呼び忘れると、ギズモが反応しないか、アサートで止まります

### SetDrawlist {#setdrawlist}

```cpp
void SetDrawlist(ImDrawList* drawlist = nullptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `drawlist` | `ImDrawList*` | ギズモを描く先。`nullptr` なら、今の ImGui ウィンドウの描画先 |

- 戻り値: なし
- ギズモは、ImGui の描画リストに線や面を足して描きます。どのウィンドウの上に描くかをここで決めます
- 普通は `ImGui::Begin("シーン")` の後に引数なしで呼びます。全画面に出したいなら、`ImGui::GetBackgroundDrawList()` を渡します

### SetRect {#setrect}

```cpp
void SetRect(float x, float y, float width, float height);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x`, `y` | `float` | ギズモを出す領域の左上（画面上の座標） |
| `width`, `height` | `float` | 領域の大きさ |

- 戻り値: なし
- 3D の画面（ビューポート）が、画面のどこにあるかを教えます。ここがずれると、ギズモの位置がオブジェクトとずれます
- ウィンドウの中に出すときは、`ImGui::GetWindowPos()` / `GetWindowSize()` を使います（タイトル バーの分がずれるので、`ImGui::GetCursorScreenPos()` や、`GetContentRegionAvail()` を使うと正確です）
- ゲームの画面をウィンドウの中にテクスチャとして出しているエディタでは、そのテクスチャを出した位置と大きさを渡します

### SetOrthographic {#setorthographic}

```cpp
void SetOrthographic(bool isOrthographic);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `isOrthographic` | `bool` | カメラが正射影なら `true`。透視投影なら `false` |

- 戻り値: なし
- 2D のエディタ（真上から見る、側面から見る）では `true` にします。プロジェクション行列の種類と合わせます

### Manipulate {#manipulate}

```cpp
bool Manipulate(const float* view, const float* projection,
                OPERATION operation, MODE mode, float* matrix,
                float* deltaMatrix = nullptr, const float* snap = nullptr,
                const float* localBounds = nullptr, const float* boundsSnap = nullptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `view` | `const float*` | ビュー行列（`float[16]`、列優先） |
| `projection` | `const float*` | プロジェクション行列（`float[16]`） |
| `operation` | `OPERATION` | 操作の種類（`TRANSLATE`、`ROTATE`、`SCALE` など。[OPERATION](#operation)） |
| `mode` | `MODE` | `LOCAL`（オブジェクトの向きに合わせる）か `WORLD`（世界の軸に合わせる） |
| `matrix` | `float*` | 操作するオブジェクトのワールド行列。操作すると書き換わる |
| `deltaMatrix` | `float*` | 今回の操作で動いた差分の行列を受け取る（`nullptr` なら不要） |
| `snap` | `const float*` | 動かす量の刻み（`float[3]`）。たとえば `{1.0f, 1.0f, 1.0f}` で 1 ずつ動く。`nullptr` なら刻みなし |
| `localBounds` | `const float*` | `BOUNDS` 操作で使う、囲み（`float[6]`） |
| `boundsSnap` | `const float*` | `BOUNDS` 操作の刻み |

- 戻り値: ギズモが操作されたフレームで `true`（`IsUsing()` とほぼ同じ）
- 一番よく使う関数です。`matrix` が書き換わるので、そのあと、行列から位置・回転・拡大を取り出して、ゲーム側に戻します
- `snap` は、Ctrl を押している間だけ刻みを有効にする、という使い方が定番です

```cpp
// Ctrl を押している間だけ、1 刻みで動かす
bool snap = ImGui::GetIO().KeyCtrl;
float snap_value[3] = {1.0f, 1.0f, 1.0f};
ImGuizmo::Manipulate(view, projection, operation, mode, model, nullptr,
                     snap ? snap_value : nullptr);
```

### OPERATION {#operation data-toc-label="OPERATION（操作の種類）"}

```cpp
enum OPERATION {
  TRANSLATE_X, TRANSLATE_Y, TRANSLATE_Z,
  ROTATE_X, ROTATE_Y, ROTATE_Z, ROTATE_SCREEN,
  SCALE_X, SCALE_Y, SCALE_Z,
  BOUNDS,
  SCALE_XU, SCALE_YU, SCALE_ZU,

  TRANSLATE = TRANSLATE_X | TRANSLATE_Y | TRANSLATE_Z,
  ROTATE = ROTATE_X | ROTATE_Y | ROTATE_Z | ROTATE_SCREEN,
  SCALE = SCALE_X | SCALE_Y | SCALE_Z,
  SCALEU = SCALE_XU | SCALE_YU | SCALE_ZU,   // 均等なスケール
  UNIVERSAL = TRANSLATE | ROTATE | SCALEU
};
```

| 値 | 意味 |
| --- | --- |
| `TRANSLATE` | 移動。3 つの矢印（X・Y・Z）と、平面を動かす四角が出る |
| `ROTATE` | 回転。3 つの輪（X・Y・Z）と、画面に向く輪が出る |
| `SCALE` | 拡大・縮小。軸ごとに伸ばす |
| `SCALEU` | 均等な拡大・縮小（縦横高さが同じ比率） |
| `UNIVERSAL` | 移動 + 回転 + 均等拡大を、1 つのギズモにまとめる |
| `BOUNDS` | 箱（バウンディング ボックス）の面をドラッグして、大きさを変える |
| `TRANSLATE_X` など | 軸を 1 つだけ出したいとき。`|` で組み合わせられる（`TRANSLATE_X | TRANSLATE_Z`） |

### MODE {#mode data-toc-label="MODE（空間）"}

```cpp
enum MODE { LOCAL, WORLD };
```

| 値 | 意味 |
| --- | --- |
| `LOCAL` | オブジェクト自身の向きに軸を合わせる。回転したオブジェクトの「前」へ動かせる |
| `WORLD` | 世界の軸（X が右、Y が上、Z が奥）に合わせる。常に同じ向きの矢印 |

- 回転のギズモは、`LOCAL` で使うと分かりやすいです。多くのエディタでは、キーで `LOCAL` と `WORLD` を切り替えられます（Unity の「Local / Global」）

### IsUsing {#isusing}

```cpp
bool IsUsing();
```

- 戻り値: 今、ギズモをドラッグしている最中なら `true`
- 操作中は、カメラの操作（マウスでの視点移動）や、オブジェクトの選択を無効にするために使います。操作が終わったフレームで、アンドゥの履歴に積むこともできます

### IsOver {#isover}

```cpp
bool IsOver();
bool IsOver(OPERATION op);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `op` | `OPERATION` | 調べたい操作の種類（指定したギズモの上かどうか） |

- 戻り値: マウスがギズモの上にあるなら `true`
- 「ギズモの上でクリックしたら、オブジェクトの選択を変えない」ための判定に使います

### Enable {#enable}

```cpp
void Enable(bool enable);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `enable` | `bool` | `false` で、ギズモを見えるが、操作できない状態にする |

- 再生中（ゲームを実行している間）は、オブジェクトを動かせないようにする、といった使い方です

### SetID {#setid}

```cpp
void SetID(int id);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `id` | `int` | ギズモの ID |

- ImGui の `PushID` のように、複数のギズモを同時に出すときに、ギズモを区別します（それぞれ違う `id` を、`Manipulate` の前に設定する）

### DecomposeMatrixToComponents {#decompose}

```cpp
void DecomposeMatrixToComponents(const float* matrix, float* translation,
                                 float* rotation, float* scale);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `matrix` | `const float*` | 分解する行列（`float[16]`） |
| `translation` | `float*` | 位置を受け取る `float[3]` |
| `rotation` | `float*` | 回転を受け取る `float[3]`（度のオイラー角） |
| `scale` | `float*` | 拡大を受け取る `float[3]` |

- 戻り値: なし
- ワールド行列から、位置・回転・拡大を取り出します。ギズモで書き換わった行列を、ゲームのオブジェクトの値に戻すときに使います

### RecomposeMatrixFromComponents {#recompose}

```cpp
void RecomposeMatrixFromComponents(const float* translation, const float* rotation,
                                   const float* scale, float* matrix);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `translation` | `const float*` | 位置（`float[3]`） |
| `rotation` | `const float*` | 回転（`float[3]`、度） |
| `scale` | `const float*` | 拡大（`float[3]`） |
| `matrix` | `float*` | 結果の行列を受け取る `float[16]` |

- 戻り値: なし
- `DecomposeMatrixToComponents` の逆です。ゲームのオブジェクトの値から、ギズモに渡す行列を作ります

### DrawGrid {#drawgrid}

```cpp
void DrawGrid(const float* view, const float* projection, const float* matrix,
              const float gridSize);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `view`, `projection` | `const float*` | カメラの行列 |
| `matrix` | `const float*` | グリッドの位置・向き（普通は単位行列） |
| `gridSize` | `float` | グリッドの大きさ（たとえば `10.0f`） |

- 戻り値: なし
- 床のグリッド線を描きます。エディタのシーン ビューに、これを出すと、空間の感覚が分かりやすくなります

### DrawCubes {#drawcubes}

```cpp
void DrawCubes(const float* view, const float* projection, const float* matrices,
               int matrixCount);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `view`, `projection` | `const float*` | カメラの行列 |
| `matrices` | `const float*` | 立方体のワールド行列を並べた配列（`float[16 * matrixCount]`） |
| `matrixCount` | `int` | 立方体の数 |

- 戻り値: なし
- 簡単な立方体を描きます。ギズモの動作確認用です（本物のゲームのモデルは、自分の描画で出します）

### ViewManipulate {#viewmanipulate}

```cpp
void ViewManipulate(float* view, float length, ImVec2 position, ImVec2 size,
                    ImU32 backgroundColor);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `view` | `float*` | ビュー行列。カメラの向きが書き換わる |
| `length` | `float` | カメラと注視点の距離 |
| `position` | `ImVec2` | キューブを出す画面上の位置（左上） |
| `size` | `ImVec2` | キューブの大きさ（ピクセル） |
| `backgroundColor` | `unsigned int` | 背景の色（`0` で透明） |

- 戻り値: なし
- 画面の隅に出る、ビュー キューブ（カメラの向きを示す小さな立方体）です。面をクリックすると、その向き（前・上・右など）にカメラが回ります（Blender の右上と同じもの）

### AllowAxisFlip {#allowaxisflip}

```cpp
void AllowAxisFlip(bool value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `bool` | `true`（既定）なら、カメラの向きによって、軸の矢印を手前に向くよう反転する |

- 戻り値: なし
- 矢印が奥を向いて、掴みにくくなるのを防ぐ機能です。反転されると困る（常に同じ向きが良い）ときは `false` にします

### SetGizmoSizeClipSpace {#setgizmosize}

```cpp
void SetGizmoSizeClipSpace(float value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `float` | ギズモの大きさ（画面の割合。既定は約 `0.1`） |

- 戻り値: なし
- ギズモを、画面に対して大きく・小さくします。カメラが離れてもギズモは同じ大きさで見えます

## DirectX で使うときの注意（行列の並び）

ImGuizmo は、行列を **列優先（column-major）の `float[16]`**（OpenGL・glm と同じ）として扱います。DirectXMath（`XMMATRIX`）は行優先で、行ベクトルを掛ける約束です。そのため、転置が必要です。

| ライブラリ | 並び | ImGuizmo に渡すとき |
| --- | --- | --- |
| glm | 列優先 | そのまま `glm::value_ptr(m)` |
| DirectXMath | 行優先 | `XMMatrixTranspose` で転置してから渡す。書き換わった行列も、転置し直して戻す |
| 自作の `Mat4`（行優先） | 行優先 | 転置して渡す・戻す |

```cpp
// DirectXMath の例
DirectX::XMFLOAT4X4 model_dx;
DirectX::XMStoreFloat4x4(&model_dx, DirectX::XMMatrixTranspose(model_matrix));
ImGuizmo::Manipulate(view_t, proj_t, op, mode, &model_dx.m[0][0]);   // 転置したものを渡す
model_matrix = DirectX::XMMatrixTranspose(DirectX::XMLoadFloat4x4(&model_dx));  // 戻すときも転置
```

!!! warning "左手系と右手系"
    このサイトは左手系（DirectX 流）です。ImGuizmo は OpenGL 流（右手系）を想定した動作で、左手系の行列だと、回転の方向や、矢印の向きが逆になることがあります。ビューとプロジェクションを左手系（`XMMatrixLookAtLH` など）で作り、転置して渡し、合わなければ Z の向き（回転の符号）を確認します。ImGuizmo のフォークには、DirectX 向けの修正が入ったものもあります。

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| レベル エディタで、オブジェクトを配置する | 選択したオブジェクトに `TRANSLATE` / `ROTATE` / `SCALE` を出す |
| ライトやカメラの位置を調整する | ギズモで動かして、インスペクターで細かい数値を確認 |
| コリジョンの形を編集 | `BOUNDS` で箱の大きさを変える |
| カメラの向きを変える | `ViewManipulate` のビュー キューブ |
| 実行中のオブジェクトを調べる | ゲームを止めて、ギズモで位置を動かして試す |

## よくあるミス

??? failure "`BeginFrame()` を呼んでいない"
    `ImGui::NewFrame()` の後に、**毎フレーム** `ImGuizmo::BeginFrame()` を呼びます。呼ばないと、ギズモがまったく反応しません。

??? failure "ギズモの位置がオブジェクトとずれる"
    `SetRect` に渡した領域が、実際の 3D 画面の領域と違います。ウィンドウのタイトル バーの高さや、画像を出した位置を足します。ビュー・プロジェクションの行列が、描画に使っているものと同じかも確認します。

??? failure "行列の並びが違って、動きがおかしい"
    列優先と行優先を取り違えると、ギズモが画面の外に出たり、矢印がでたらめな方向を向いたりします。DirectXMath の行列は転置して渡します。

??? failure "ギズモを操作しているのに、カメラも一緒に動く"
    `ImGuizmo::IsUsing()` や `IsOver()` が `true` のときは、カメラ操作（マウスのドラッグ）を無効にします。

??? failure "回転が度とラジアンで食い違う"
    `DecomposeMatrixToComponents` と `RecomposeMatrixFromComponents` の回転は度です。ゲーム側がラジアンなら、変換します。

??? failure "拡大に 0 を入れる"
    `scale` に 0 があると、行列が壊れて（逆行列が作れず）、ギズモが消えます。拡大は 0 にならないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [ImSequencer](imsequencer.md) | 同じ作者のタイムライン編集 UI |
| [imgui-node-editor](node-editor.md) | ノードを線でつなぐ GUI |
| 自作のギズモ | レイとの交差判定を自分で書く。学習にはなるが、手間が大きい |
| ImGuizmo の派生（ImGuizmo.Quat など） | クォータニオンの対応や、不具合の修正が入ったもの |

## これだけ覚える

!!! abstract "まとめ"
    - [x] `NewFrame()` の後に `ImGuizmo::BeginFrame()`
    - [x] `SetRect` で 3D 画面の領域を教え、`Manipulate(view, projection, 操作, 空間, model)` を呼ぶ
    - [x] `model` が書き換わるので、`DecomposeMatrixToComponents` でゲーム側に戻す
    - [x] 行列は列優先の `float[16]`。DirectXMath は転置する
    - [x] 操作中は `IsUsing()` でカメラ操作を止める

## 関連ページ

- [Dear ImGui](index.md)
- [ImSequencer](imsequencer.md)
- [imgui-node-editor](node-editor.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
- [ImGuizmo（GitHub）](https://github.com/CedricGuillemet/ImGuizmo)

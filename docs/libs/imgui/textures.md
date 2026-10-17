---
title: テクスチャと画像
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のテクスチャと画像

ImGui には、**画像を表示する部品**（`Image`・`ImageButton`）があります。<strong>画像の中身（テクスチャ）</strong>は、**ImGui ではなく、自分の描画 API（DirectX 11）で作り、その「ハンドル」を ImGui に渡します**。このページは、**`ImTextureID`** の意味、**DX11 の Shader Resource View を渡す方法**、**画像ファイルの読み込み**、**ゲームの画面を、ウィンドウの中に出す**（シーンビュー）方法、**アイコン・スプライトシート**をまとめます。

!!! tip "ポイント"
    - ImGui は、<strong>画像そのものを、持たない</strong>。<strong>`ImTextureID`（テクスチャを指す「札」）</strong>を、受け取って、描画する。
    - <strong>DirectX 11 では、`ImTextureID` ＝ `ID3D11ShaderResourceView*`</strong>（SRV）。
    - 画像の表示は <strong>`ImGui::Image(texture_id, 大きさ, uv0, uv1)`</strong>。
    - 画像ファイルは、<strong>`stb_image` などで読み込み、DX11 のテクスチャと SRV にして、渡す</strong>。
    - <strong>ゲームの画面を、レンダー ターゲットに描いて、SRV を `Image` で出す</strong>と、<strong>エディタのシーン ビュー</strong>ができる。
    - <strong>テクスチャは、ImGui が使い終わるまで、解放しない</strong>（<strong>`Render` が終わるまで、生きている</strong>必要）。

## ImTextureID

**`ImTextureID`** は、<strong>テクスチャを識別する、ImGui 用の「ID」</strong>です。**中身は、バックエンドによって違います**。

| 描画 API | `ImTextureID` に入れるもの |
| --- | --- |
| **DirectX 11** | **`ID3D11ShaderResourceView*`**（SRV） |
| DirectX 12 | GPU ディスクリプタ ハンドル |
| OpenGL | テクスチャ名（`GLuint`） |
| Vulkan | `VkDescriptorSet` |

**ImGui は、この値を、中身を知らずに、そのまま、バックエンドの描画関数に渡す**だけです。

!!! note "型が、バージョンで変わる"
    `ImTextureID` は、**以前は `void*`<strong>、</strong>新しい版（1.91.4 以降）では、整数型（`ImU64`）<strong>です。</strong>キャストの書き方**が、少し変わります。

```cpp
ImTextureID id = (ImTextureID)(intptr_t)srv;
```

**`(ImTextureID)(intptr_t)srv`** と書くと、**どちらの版でも、動きます**。

## DX11 のテクスチャを渡す

### 画像を表示する

```cpp
ID3D11ShaderResourceView* srv = ...;

ImGui::Image((ImTextureID)(intptr_t)srv, ImVec2(128, 128));
```

| 引数 | 意味 |
| --- | --- |
| **`texture_id`** | **SRV を、キャスト**したもの |
| **`size`** | **画面上の、表示の大きさ**（ピクセル） |
| `uv0`（既定 `(0,0)`） | **画像の、左上の UV** |
| `uv1`（既定 `(1,1)`） | **画像の、右下の UV** |
| `tint_col` / `border_col`（旧版） | **色味・枠線**（新しい版では、別の関数・スタイルに） |

**`Image` は、画像を表示するだけ**です。**クリックできる画像**は、**`ImageButton`**、または **`Image` ＋ `IsItemClicked()`** です。

```cpp
ImGui::Image((ImTextureID)(intptr_t)srv, ImVec2(64, 64));
if (ImGui::IsItemClicked()) OnClick();
if (ImGui::IsItemHovered()) ImGui::SetTooltip("クリックして選択");
```

### 画像ファイルを読み込む（stb_image）

**画像ファイル（PNG・JPG）を、ピクセルに展開**するのに、**`stb_image.h`**（ImGui のサンプルでも使われる、単一ヘッダ）を使います。

```cpp
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

bool LoadTextureFromFile(ID3D11Device* device, const char* path,
                         ID3D11ShaderResourceView** out_srv, int* out_width, int* out_height) {
  int width = 0;
  int height = 0;
  unsigned char* pixels = stbi_load(path, &width, &height, nullptr, 4);
  if (pixels == nullptr) return false;

  D3D11_TEXTURE2D_DESC desc = {};
  desc.Width = width;
  desc.Height = height;
  desc.MipLevels = 1;
  desc.ArraySize = 1;
  desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
  desc.SampleDesc.Count = 1;
  desc.Usage = D3D11_USAGE_DEFAULT;
  desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;

  D3D11_SUBRESOURCE_DATA data = {};
  data.pSysMem = pixels;
  data.SysMemPitch = width * 4;

  ID3D11Texture2D* texture = nullptr;
  device->CreateTexture2D(&desc, &data, &texture);

  D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
  srv_desc.Format = desc.Format;
  srv_desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
  srv_desc.Texture2D.MipLevels = 1;
  device->CreateShaderResourceView(texture, &srv_desc, out_srv);

  texture->Release();
  stbi_image_free(pixels);
  *out_width = width;
  *out_height = height;
  return true;
}
```

| 点 | 説明 |
| --- | --- |
| **`stbi_load(path, &w, &h, nullptr, 4)`** | **画像を、RGBA（4 チャンネル）に展開**（最後の `4` ＝ 強制的に 4 チャンネル） |
| **`CreateTexture2D`** | **GPU のテクスチャ**を、作る |
| **`CreateShaderResourceView`** | **シェーダー（ImGui の描画）から読むための、SRV**を作る |
| **テクスチャを `Release`** | **SRV が、参照を保持**するので、**テクスチャ本体は、手放してよい**（SRV を解放するときに、一緒に解放される） |
| **`stbi_image_free`** | **ピクセルの一時領域**を解放 |

**ゲーム本体のテクスチャ読み込み**（[メッシュとテクスチャ](../../3d/mesh-textures.md)）と、**同じ仕組み**です。**ゲーム側で読み込んだテクスチャの SRV を、そのまま `ImGui::Image` に渡せます**（**アセットブラウザー**など）。

### 解放のタイミング

**ImGui は、`ImGui::Render()` で、描画データを作り、`RenderDrawData` で実際に描画**します。**`Image` を呼んだ後、描画が終わるまで**、**SRV は、生きている必要があります**。

!!! warning "フレーム内で、SRV を解放しない"
    **`Image` に渡した SRV を、同じフレームの描画前に `Release`** すると、**クラッシュ**します。**テクスチャを入れ替えるときは、次のフレームまで**、**古いものを保持**します。

## シーンビュー（ゲームの画面を、ウィンドウに出す） {#sceneview}

**エディタのように、ゲームの 3D 画面を、ImGui のウィンドウの中**に出します。**ゲームの描画を、バックバッファではなく、レンダー ターゲット（テクスチャ）に描き**、**その SRV を `Image` で表示**します。

<div class="anim" data-type="graph" data-label="シーンビュー：ゲームの画面をテクスチャに描いて、ImGui のウィンドウの中に出す">
n game ゲームの描画 0 1 hit
---
n game ゲームの描画 0 1
n rt レンダー_ターゲット_（テクスチャ） 1 1 new
l game rt hit 描く
---
n rt レンダー_ターゲット_（テクスチャ） 1 1
n srv SRV 2 1 new
l rt srv hit 読む
---
n srv SRV 2 1
n img ImGui::Image 3 1 new
n win シーン_ウィンドウ 4 1 new
l srv img hit 渡す
l img win hit 表示
</div>

```cpp
class SceneView {
 public:
  void Resize(ID3D11Device* device, int width, int height) {
    if (width == width_ && height == height_) return;
    width_ = width;
    height_ = height;

    D3D11_TEXTURE2D_DESC desc = {};
    desc.Width = width;
    desc.Height = height;
    desc.MipLevels = 1;
    desc.ArraySize = 1;
    desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    desc.SampleDesc.Count = 1;
    desc.Usage = D3D11_USAGE_DEFAULT;
    desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;

    texture_.Reset();
    rtv_.Reset();
    srv_.Reset();
    device->CreateTexture2D(&desc, nullptr, &texture_);
    device->CreateRenderTargetView(texture_.Get(), nullptr, &rtv_);
    device->CreateShaderResourceView(texture_.Get(), nullptr, &srv_);
  }

  ID3D11RenderTargetView* Rtv() const { return rtv_.Get(); }
  ID3D11ShaderResourceView* Srv() const { return srv_.Get(); }

 private:
  Microsoft::WRL::ComPtr<ID3D11Texture2D> texture_;
  Microsoft::WRL::ComPtr<ID3D11RenderTargetView> rtv_;
  Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv_;
  int width_ = 0;
  int height_ = 0;
};
```

| 設定 | 意味 |
| --- | --- |
| **`BindFlags = RENDER_TARGET \| SHADER_RESOURCE`** | <strong>描き込める（レンダー ターゲット）</strong>し、<strong>読める（SRV）</strong> |
| **`Resize`** | **ウィンドウの大きさが変わったら、作り直す** |

### 毎フレームの流れ

```cpp
ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
if (ImGui::Begin("シーン")) {
  ImVec2 size = ImGui::GetContentRegionAvail();
  scene_view.Resize(device, (int)size.x, (int)size.y);
  ImGui::Image((ImTextureID)(intptr_t)scene_view.Srv(), size);
}
ImGui::End();
ImGui::PopStyleVar();

context->OMSetRenderTargets(1, &rtv_of_scene, depth_stencil_view);
RenderGame();

context->OMSetRenderTargets(1, &back_buffer_rtv, nullptr);
ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
```

| 順番 | 内容 |
| --- | --- |
| **1. ImGui で、ウィンドウの大きさを得る** | **`GetContentRegionAvail`** |
| **2. レンダー ターゲットを、その大きさに** | **`Resize`**（大きさが変わったときだけ） |
| **3. ゲームを、レンダー ターゲットに描く** | **ゲームの描画**（カメラの `aspect` も、**この大きさ**に合わせる） |
| **4. バックバッファに戻し、ImGui を描く** | **`RenderDrawData`** |

### 注意

| 注意 | 説明 |
| --- | --- |
| **アスペクト比** | **ウィンドウの縦横比**を、**カメラの `aspect`** に反映（[射影](../../3d/projection.md)） |
| **ウィンドウの大きさが、0** | **ウィンドウが、折りたたまれた**とき。**`Resize` を、スキップ** |
| **マウスの位置** | **ゲーム内のクリック位置**は、**ウィンドウの左上**を、原点にして、**画像の座標**に変換（[ピッキング](../../3d/picking-raycast.md)） |
| **ホバー・フォーカス** | **`IsWindowHovered()` / `IsWindowFocused()`**で、**ゲームの入力を受けるか**を、判断 |
| **ImGui のマウス占有** | **`io.WantCaptureMouse`** が `true` のときは、**ゲームに入力を渡さない** |

## 画像ボタン・アイコン

```cpp
if (ImGui::ImageButton("##play", (ImTextureID)(intptr_t)icon_play, ImVec2(24, 24))) {
  Play();
}
```

**`ImageButton`** は、**画像が、そのままボタン**になります（**第 1 引数の ID が必要**。新しい版）。

| 方法 | 説明 |
| --- | --- |
| **`ImageButton`** | **画像のボタン**。ツールバーのアイコンに |
| **アイコン フォント** | **画像ファイルを使わず**、**文字として、アイコンを出す**（[フォント](fonts.md#icons)）。**色・大きさを、簡単に変えられる** |

## UV とスプライトシート

**`uv0` / `uv1`** で、**画像の一部だけ**を、表示できます。**スプライトシート**（**複数のアイコンを、1 枚の画像**にまとめたもの）から、**1 つを切り出す**のに使います。

```cpp
const int kColumns = 8;
const int kRows = 8;
const float cell_u = 1.0f / kColumns;
const float cell_v = 1.0f / kRows;

int index = 10;
int column = index % kColumns;
int row = index / kColumns;

ImVec2 uv0(column * cell_u, row * cell_v);
ImVec2 uv1((column + 1) * cell_u, (row + 1) * cell_v);
ImGui::Image((ImTextureID)(intptr_t)sheet_srv, ImVec2(32, 32), uv0, uv1);
```

| 点 | 説明 |
| --- | --- |
| **UV は 0〜1** | <strong>画像全体が、(0,0)〜(1,1)</strong> |
| **DirectX は、左上が原点** | `uv0` が、**左上**、`uv1` が、**右下** |
| **1 枚にまとめる利点** | **テクスチャの数が、減る**（読み込み・メモリが、少ない） |

## 描画の注意

| 注意 | 説明 |
| --- | --- |
| **ステートの保存** | **`ImGui_ImplDX11_RenderDrawData`** は、**描画のステートを、保存・復元**する（自分のステートを、壊さない） |
| **ガンマ・色空間** | <strong>sRGB のテクスチャ（`_SRGB`）</strong> を渡すと、**色が、薄く見える**ことがある。**ImGui は、基本的に、リニアでなく、そのままの値**で表示するので、<strong>`UNORM`（非 sRGB）</strong> のほうが、見た目が、そのまま |
| <strong>透明（アルファ）</strong> | **RGBA の PNG**の透明は、**そのまま**表示される |
| **大きな画像** | **表示サイズに、縮小**される。**重い大画像は、縮小版（サムネイル）を作る** |
| **毎フレームの再作成** | **テクスチャを、毎フレーム作らない**（**読み込みは、1 回**） |

## よくあるミス

??? failure "画像が、真っ黒・何も出ない"
    **SRV が `nullptr`**、**`stbi_load` が失敗**（パスが違う）、**`BindFlags` に `SHADER_RESOURCE` がない**、が考えられます。

??? failure "`ImGui::Image` に、テクスチャそのもの（`ID3D11Texture2D*`）を渡している"
    **SRV**（`ID3D11ShaderResourceView*`）を渡します。

??? failure "フレーム内で、SRV を解放してクラッシュする"
    **描画が終わるまで、保持**します。

??? failure "シーンビューが、ぼやける・伸びる"
    **ウィンドウの大きさに合わせて、レンダー ターゲットを、作り直して**いません。

??? failure "シーンビューのクリックが、ゲームに届かない・ずれる"
    **`WantCaptureMouse`**、**ウィンドウの原点からの座標変換**を確認します。

??? failure "画像が、上下逆に出る"
    **UV の向き**（`uv0` と `uv1` の入れ替え）、または **レンダー ターゲットの、Y の向き**です。

??? failure "色が、暗い・薄い"
    **sRGB の扱い**（`_SRGB` の使用）を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ImGui は<strong>画像を持たず</strong>、<strong>`ImTextureID`（DX11 では SRV）</strong>を受け取って描く
    - [x] 表示は<strong>`ImGui::Image((ImTextureID)(intptr_t)srv, 大きさ, uv0, uv1)`</strong>
    - [x] 画像ファイルは<strong>stb_image で展開 → `CreateTexture2D` → SRV</strong>
    - [x] <strong>シーンビュー ＝ ゲームをレンダー ターゲットに描き、その SRV を `Image` で出す</strong>。<strong>ウィンドウの大きさに合わせて、作り直す</strong>
    - [x] <strong>`io.WantCaptureMouse`</strong> で、入力の取り合いを避ける
    - [x] <strong>SRV は、フレームの描画が終わるまで解放しない</strong>

## 関連ページ

- [Dear ImGui](index.md)
- [ドッキングとビューポート](docking.md)
- [日本語フォントとアイコン](fonts.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [射影](../../3d/projection.md)
- [ImGuizmo](imguizmo.md)

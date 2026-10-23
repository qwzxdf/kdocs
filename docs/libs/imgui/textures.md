---
title: テクスチャと画像
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のテクスチャと画像

ImGui には、**画像を表示する部品**（`Image`・`ImageButton`）があります。画像の中身（テクスチャ）は、ImGui ではなく、自分の描画 API（DirectX 11）で作り、その「ハンドル」を ImGui に渡します。このページは、`ImTextureID` の意味、DX11 の Shader Resource View を渡す方法、画像ファイルの読み込み、ゲームの画面をウィンドウの中に出す（シーンビュー）方法、アイコン・スプライトシートをまとめます。

!!! tip "ポイント"
    - ImGui は、<strong>画像そのものを持たない</strong>。<strong>`ImTextureID`（テクスチャを指す「札」）</strong>を、受け取って、描画する。
    - DirectX 11 では、`ImTextureID` ＝ `ID3D11ShaderResourceView*`（SRV）。
    - 画像の表示は `ImGui::Image(texture_id, 大きさ, uv0, uv1)`。
    - 画像ファイルは、`stb_image` などで読み込み、DX11 のテクスチャと SRV にして、渡す。
    - ゲームの画面をレンダー ターゲットに描いて、SRV を `Image` で出すと、エディタのシーン ビューができる。
    - テクスチャは、ImGui が使い終わるまで、解放しない（`Render` が終わるまで、生きている必要）。

!!! info "このページを読む前に"
    - [Dear ImGui](index.md)（このセクション全体の地図と、読む順番）
    - [Dear ImGui の導入（Visual Studio）](install.md)（ImGui の入れ方）

## ImTextureID

**`ImTextureID`** は、テクスチャを識別する、ImGui 用の「ID」です。中身はバックエンドによって違います。

| 描画 API | `ImTextureID` に入れるもの |
| --- | --- |
| DirectX 11 | **`ID3D11ShaderResourceView*`**（SRV） |
| DirectX 12 | GPU ディスクリプタ ハンドル |
| OpenGL | テクスチャ名（`GLuint`） |
| Vulkan | `VkDescriptorSet` |

ImGui は、この値を中身を知らずにそのまま、バックエンドの描画関数に渡すだけです。

!!! note "型が、バージョンで変わる"
    `ImTextureID` は、**以前は `void*`、新しい版（1.91.4 以降）では整数型（`ImU64`）です。キャストの書き方**が少し変わります。

```cpp
ImTextureID id = (ImTextureID)(intptr_t)srv;
```

`(ImTextureID)(intptr_t)srv` と書くとどちらの版でも動きます。

## DX11 のテクスチャを渡す

### 画像を表示する

```cpp
ID3D11ShaderResourceView* srv = ...;

ImGui::Image((ImTextureID)(intptr_t)srv, ImVec2(128, 128));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| **`texture_id`** | `ImTextureID` | SRV をキャストしたもの |
| `size` | `ImVec2` | 画面上の表示の大きさ（ピクセル） |
| `uv0`（既定 `(0,0)`） | `ImVec2` | 画像の左上の UV |
| `uv1`（既定 `(1,1)`） | `ImVec2` | 画像の右下の UV |
| `tint_col` / `border_col`（旧版） | `ImVec4` | 色味・枠線（新しい版では別の関数・スタイルに） |

`Image` は、画像を表示するだけです。クリックできる画像は、`ImageButton`、または `Image` ＋ `IsItemClicked()` です。

```cpp
ImGui::Image((ImTextureID)(intptr_t)srv, ImVec2(64, 64));
if (ImGui::IsItemClicked()) OnClick();
if (ImGui::IsItemHovered()) ImGui::SetTooltip("クリックして選択");
```

### 画像ファイルを読み込む（stb_image）

画像ファイル（PNG・JPG）を、ピクセルに展開するのに、`stb_image.h`（ImGui のサンプルでも使われる、単一ヘッダ）を使います。

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
| `stbi_load(path, &w, &h, nullptr, 4)` | 画像を、RGBA（4 チャンネル）に展開（最後の `4` ＝ 強制的に 4 チャンネル） |
| `CreateTexture2D` | GPU のテクスチャを、作る |
| `CreateShaderResourceView` | シェーダー（ImGui の描画）から読むための、SRVを作る |
| テクスチャを `Release` | SRV が参照を保持するのでテクスチャ本体は、手放してよい（SRV を解放するときに、一緒に解放される） |
| `stbi_image_free` | ピクセルの一時領域を解放 |

ゲーム本体のテクスチャ読み込み（[メッシュとテクスチャ](../../3d/mesh-textures.md)）と、同じ仕組みです。ゲーム側で読み込んだテクスチャの SRV を、そのまま `ImGui::Image` に渡せます（アセットブラウザーなど）。

### 解放のタイミング

ImGui は、`ImGui::Render()` で、描画データを作り、`RenderDrawData` で実際に描画します。`Image` を呼んだ後、描画が終わるまで、SRV は生きている必要があります。

!!! warning "フレーム内で、SRV を解放しない"
    `Image` に渡した SRV を、同じフレームの描画前に `Release` すると、クラッシュします。テクスチャを入れ替えるときは、次のフレームまで、古いものを保持します。

## シーンビュー（ゲームの画面をウィンドウに出す） {#sceneview}

**エディタのようにゲームの 3D 画面を、ImGui のウィンドウの中**に出します。ゲームの描画をバックバッファではなく、レンダー ターゲット（テクスチャ）に描き、その SRV を `Image` で表示します。

<svg class="fig flow" viewBox="0 0 1027 112" role="img" aria-label="シーンビュー：ゲームの画面をテクスチャに描いて、ImGui のウィンドウの中に出す"><defs><marker id="fl66077" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">シーンビュー：ゲームの画面をテクスチャに描いて、ImGui のウィンドウの中に出す</text><line x1="141.0" y1="64.0" x2="199.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl66077)"/><text x="170.0" y="58.0" text-anchor="middle" style="font-size:12px">描く</text><line x1="470.0" y1="64.0" x2="528.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl66077)"/><text x="499.0" y="58.0" text-anchor="middle" style="font-size:12px">読む</text><line x1="610.0" y1="64.0" x2="668.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl66077)"/><text x="639.0" y="58.0" text-anchor="middle" style="font-size:12px">渡す</text><line x1="792.0" y1="64.0" x2="850.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl66077)"/><text x="821.0" y="58.0" text-anchor="middle" style="font-size:12px">表示</text><rect x="28.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="83.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲームの描画</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="202.0" y="44.0" width="265" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="334.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">レンダー ターゲット （テクスチャ）</text><circle cx="204.0" cy="46.0" r="10" fill="#2ea043"/><text x="204.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="531.0" y="44.0" width="76" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="569.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">SRV</text><circle cx="533.0" cy="46.0" r="10" fill="#e5a828"/><text x="533.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="671.0" y="44.0" width="118" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="730.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ImGui::Image</text><circle cx="673.0" cy="46.0" r="10" fill="#e5484d"/><text x="673.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="853.0" y="44.0" width="146" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="926.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">シーン ウィンドウ</text><circle cx="855.0" cy="46.0" r="10" fill="#e5484d"/><text x="855.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

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
| `BindFlags = RENDER_TARGET \| SHADER_RESOURCE` | 描き込める（レンダー ターゲット）し、読める（SRV） |
| `Resize` | ウィンドウの大きさが変わったら、作り直す |

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
| 1. ImGui でウィンドウの大きさを得る | `GetContentRegionAvail` |
| 2. レンダー ターゲットを、その大きさに | `Resize`（大きさが変わったときだけ） |
| 3. ゲームをレンダー ターゲットに描く | ゲームの描画（カメラの `aspect` も、この大きさに合わせる） |
| 4. バックバッファに戻し、ImGui を描く | `RenderDrawData` |

### 注意

| 注意 | 説明 |
| --- | --- |
| アスペクト比 | ウィンドウの縦横比をカメラの `aspect` に反映（[射影](../../3d/projection.md)） |
| ウィンドウの大きさが、0 | ウィンドウが折りたたまれたとき。`Resize` をスキップ |
| マウスの位置 | ゲーム内のクリック位置は、ウィンドウの左上を原点にして、画像の座標に変換（[ピッキング](../../3d/picking-raycast.md)） |
| ホバー・フォーカス | `IsWindowHovered()` / `IsWindowFocused()`で、ゲームの入力を受けるかを、判断 |
| ImGui のマウス占有 | `io.WantCaptureMouse` が `true` のときは、ゲームに入力を渡さない |

## 画像ボタン・アイコン

```cpp
if (ImGui::ImageButton("##play", (ImTextureID)(intptr_t)icon_play, ImVec2(24, 24))) {
  Play();
}
```

**`ImageButton`** は、画像がそのままボタンになります（第 1 引数の ID が必要。新しい版）。

| 方法 | 説明 |
| --- | --- |
| `ImageButton` | 画像のボタン。ツールバーのアイコンに |
| アイコン フォント | 画像ファイルを使わず、文字として、アイコンを出す（[フォント](fonts.md#icons)）。色・大きさを簡単に変えられる |

## UV とスプライトシート

**`uv0` / `uv1`** で、画像の一部だけを表示できます。スプライトシート（複数のアイコンを、1 枚の画像にまとめたもの）から、1 つを切り出すのに使います。

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
| UV は 0〜1 | 画像全体が、(0,0)〜(1,1) |
| DirectX は、左上が原点 | `uv0` が左上、`uv1` が右下 |
| 1 枚にまとめる利点 | テクスチャの数が減る（読み込み・メモリが少ない） |

## 描画の注意

| 注意 | 説明 |
| --- | --- |
| **ステートの保存** | `ImGui_ImplDX11_RenderDrawData` は、描画のステートを保存・復元する（自分のステートを壊さない） |
| ガンマ・色空間 | sRGB のテクスチャ（`_SRGB`） を渡すと色が薄く見えることがある。ImGui は、基本的にリニアでなく、そのままの値で表示するので、`UNORM`（非 sRGB） のほうが見た目がそのまま |
| 透明（アルファ） | RGBA の PNGの透明は、そのまま表示される |
| 大きな画像 | 表示サイズに縮小される。重い大画像は縮小版（サムネイル）を作る |
| 毎フレームの再作成 | テクスチャを毎フレーム作らない（読み込みは、1 回） |

## よくあるミス

??? failure "画像が、真っ黒・何も出ない"
    **SRV が `nullptr`**、`stbi_load` が失敗（パスが違う）、`BindFlags` に `SHADER_RESOURCE` がない、が考えられます。

??? failure "`ImGui::Image` にテクスチャそのもの（`ID3D11Texture2D*`）を渡している"
    SRV（`ID3D11ShaderResourceView*`）を渡します。

??? failure "フレーム内で、SRV を解放してクラッシュする"
    描画が終わるまで保持します。

??? failure "シーンビューが、ぼやける・伸びる"
    ウィンドウの大きさに合わせて、レンダー ターゲットを、作り直していません。

??? failure "シーンビューのクリックが、ゲームに届かない・ずれる"
    `WantCaptureMouse`、ウィンドウの原点からの座標変換を確認します。

??? failure "画像が、上下逆に出る"
    UV の向き（`uv0` と `uv1` の入れ替え）、または レンダー ターゲットの、Y の向きです。

??? failure "色が、暗い・薄い"
    sRGB の扱い（`_SRGB` の使用）を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ImGui は<strong>画像を持たず</strong>、`ImTextureID`（DX11 では SRV）を受け取って描く
    - [x] 表示は`ImGui::Image((ImTextureID)(intptr_t)srv, 大きさ, uv0, uv1)`
    - [x] 画像ファイルはstb_image で展開 → `CreateTexture2D` → SRV
    - [x] シーンビュー ＝ ゲームをレンダー ターゲットに描き、その SRV を `Image` で出す。ウィンドウの大きさに合わせて、作り直す
    - [x] `io.WantCaptureMouse` で、入力の取り合いを避ける
    - [x] SRV は、フレームの描画が終わるまで解放しない

## 関連ページ

- [Dear ImGui](index.md)
- [ドッキングとビューポート](docking.md)
- [日本語フォントとアイコン](fonts.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [射影](../../3d/projection.md)
- [ImGuizmo](imguizmo.md)

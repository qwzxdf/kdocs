---
title: Rasterizer State
tags:
  - DirectX
---

# Rasterizer State

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ラスタライザー ステート</strong>は、三角形を、<strong>ピクセルに、変換する</strong>段（ラスタライザー）の、設定です。「どちら向きの面を、表とするか」「裏面を、捨てるか」「塗りつぶすか、ワイヤフレームか」「深度に、バイアスを、掛けるか」「画面の外を、切るか」を、決めます。三角形が、見えないとき、まず、疑うのが、ここです。

!!! tip "ポイント"
    - 面の向きの、既定は、<strong>時計回り（CW）が表</strong>。このサイトの規約は、<strong>反時計回り（CCW）が表</strong>なので、`FrontCounterClockwise = TRUE`。
    - `CullMode`: `BACK`（裏を、捨てる、既定）、`FRONT`、`NONE`（両面）。
    - 作成は `CreateRasterizerState`、つなぐのは `RSSetState`。作ったステートは、使い回す。
    - シャドウ マップでは、`DepthBias` と `SlopeScaledDepthBias` で、影のにじみ・縞（シャドウ アクネ）を、抑える。
    - 既定のステート（`RSSetState(nullptr)`）は、`CullMode = BACK`、`FrontCounterClockwise = FALSE`。

## 作る

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.FillMode = D3D11_FILL_SOLID;                           // 塗りつぶし（WIREFRAME で、ワイヤフレーム）
desc.CullMode = D3D11_CULL_BACK;                            // 裏面を、捨てる
desc.FrontCounterClockwise = TRUE;                          // 反時計回りが表（このサイトの規約）
desc.DepthBias = 0;
desc.DepthBiasClamp = 0.0f;
desc.SlopeScaledDepthBias = 0.0f;
desc.DepthClipEnable = TRUE;                                // 近・遠クリップ面の外を、切る
desc.ScissorEnable = FALSE;
desc.MultisampleEnable = FALSE;
desc.AntialiasedLineEnable = FALSE;

Microsoft::WRL::ComPtr<ID3D11RasterizerState> state;
device->CreateRasterizerState(&desc, &state);
context->RSSetState(state.Get());
```

| メンバー | 内容 |
| --- | --- |
| `FillMode` | `SOLID`（塗りつぶし）、`WIREFRAME`（辺だけ） |
| `CullMode` | `NONE`（両面を描く）、`FRONT`（表を捨てる）、`BACK`（裏を捨てる） |
| `FrontCounterClockwise` | `TRUE` で、反時計回りが表 |
| `DepthBias` | 深度に、足す、整数のバイアス |
| `DepthBiasClamp` | バイアスの、上限 |
| `SlopeScaledDepthBias` | 面の、傾きに、比例した、バイアス |
| `DepthClipEnable` | 近・遠クリップを、有効にするか |
| `ScissorEnable` | シザー矩形を、有効にするか |
| `MultisampleEnable` | MSAA のとき、マルチサンプルの、四角形のエッジ処理 |
| `AntialiasedLineEnable` | 線の、アンチエイリアス |

## 面の向きと、カリング

三角形は、画面に、投影したとき、頂点の、並びが、<strong>時計回りか、反時計回りか</strong>で、表か裏かが、決まります。裏面を、捨てる（`CULL_BACK`）と、立体の、向こう側の面を、描かずに済み、ピクセル シェーダーの、負荷が、<strong>約半分</strong>になります。

```text
  反時計回り（CCW）を表とする（FrontCounterClockwise = TRUE）:
       A                    A → B → C が、反時計回りなら、表（見える）
      / \                   A → C → B（時計回り）なら、裏（捨てる）
     B───C
```

| 設定 | 表 | 裏を捨てる |
| --- | --- | --- |
| D3D11 の既定 | 時計回り | する（`BACK`） |
| このサイトの規約 | 反時計回り（`FrontCounterClockwise = TRUE`） | する（`BACK`） |

### カリングを、切る場面

| 場面 | `CullMode` |
| --- | --- |
| 普通の、閉じたメッシュ | `BACK` |
| 薄い板（草、旗、葉）、両面を、見せたい | `NONE` |
| シャドウ マップの描画 | `BACK`（影の、アクネを、減らす）か `FRONT`（前面を、捨てて、裏面を、描く方式） |
| 内側から、見る（部屋の、スカイボックス） | `FRONT`（または、頂点の並びを、反転） |
| ワイヤフレーム | `FillMode = WIREFRAME`、`CullMode = NONE` |

両面を、描く物（`NONE`）は、裏面の、法線が、逆向きになるので、ピクセル シェーダーで、`SV_IsFrontFace` を、使って、法線を、反転します。

```hlsl
float4 PSMain(VSOutput input, bool is_front : SV_IsFrontFace) : SV_Target {
  float3 normal = is_front ? input.normal : -input.normal;    // 裏面は、法線を反転
  ...
}
```

## 深度バイアス

シャドウ マップでは、光から見た、深度を、描き、後で、比較します。**同じ面の、深度を、比べると、数値誤差で、自分の影に、入ってしまう**（シャドウ アクネ）ので、描画時に、深度を、ずらします。

```cpp
D3D11_RASTERIZER_DESC shadow = {};
shadow.FillMode = D3D11_FILL_SOLID;
shadow.CullMode = D3D11_CULL_BACK;
shadow.FrontCounterClockwise = TRUE;
shadow.DepthBias = 1000;                                    // 深度の、最小単位に対する、倍数（整数）
shadow.SlopeScaledDepthBias = 2.0f;                         // 面が、光に、斜めなほど、大きくずらす
shadow.DepthBiasClamp = 0.0f;                               // 0 = 上限なし
shadow.DepthClipEnable = TRUE;
device->CreateRasterizerState(&shadow, &shadow_state);
```

`DepthBias` の、単位は、深度フォーマットに、依存します（`D32_FLOAT` と `D16_UNORM` で、同じ値でも、ずれる量が、違う）。値は、見ながら、調整します（[Shadow Bias](../../graphics/shadows/bias/index.md)）。バイアスが、大きすぎると、影が、物から、離れて見えます（ピーターパニング）。

## DepthClipEnable

<strong>DepthClipEnable = TRUE</strong>（既定）で、近・遠クリップ面の、外にある、ピクセルは、切られます。`FALSE` にすると、深度が、0〜1 の範囲に、クランプされ、<strong>切られません</strong>。

| 使いどころ | 内容 |
| --- | --- |
| カスケード シャドウ マップ | 光の近クリップ面の、手前の、影を、落とす物（光の、後ろの、物）を、切らずに、深度 0 に、固定して、描く |
| 無限遠の、深度 | 遠クリップ面で、切れないように、する |

## ワイヤフレーム

```cpp
D3D11_RASTERIZER_DESC wire = {};
wire.FillMode = D3D11_FILL_WIREFRAME;
wire.CullMode = D3D11_CULL_NONE;
wire.FrontCounterClockwise = TRUE;
wire.DepthClipEnable = TRUE;
device->CreateRasterizerState(&wire, &wireframe_state);
```

メッシュの、三角形の、構造を、確認するデバッグ表示に、使います。キーで、切り替える、デバッグ機能に、しておくと、便利です。

## シザー矩形

```cpp
desc.ScissorEnable = TRUE;
// 描画前: D3D11_RECT rect = {left, top, right, bottom};  context->RSSetScissorRects(1, &rect);
```

指定した、四角形の、外の、ピクセルを、捨てます（[Viewport](viewport.md)）。UI の、はみ出しを、切るのに、使います。

## ステートの、使い回し

ステートは、不変なので、起動時に、用途別に、作ります。

```cpp
struct RasterizerStates {
  ComPtr<ID3D11RasterizerState> solid;       // CULL_BACK、CCW が表
  ComPtr<ID3D11RasterizerState> two_sided;   // CULL_NONE（草、旗）
  ComPtr<ID3D11RasterizerState> wireframe;   // デバッグ
  ComPtr<ID3D11RasterizerState> shadow;      // 深度バイアスつき
};
```

## よくあるミス

??? failure "三角形が、見えない（裏面として、捨てられている）"
    `FrontCounterClockwise` が `FALSE`（既定の、時計回りが表）のまま、反時計回りの、メッシュを、描いている。`TRUE` にする。または、頂点の、順序を、反転する。

??? failure "草や、旗が、片側からしか、見えない"
    `CullMode = BACK`。薄い板は、`NONE`（両面）にして、裏面の、法線を、反転する。

??? failure "影が、縞模様（シャドウ アクネ）、または、物から、離れる（ピーターパニング）"
    `DepthBias`、`SlopeScaledDepthBias` が、小さすぎる、または、大きすぎる。調整する。

??? failure "モデルの、内側が、見えて、外側が、見えない（逆に見える）"
    座標系の、変換（鏡像）で、並びが、反転している。スケールが、負（ミラー）の、物は、カリングを、反転する、または、ステートを、切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ラスタライザー ステート ＝ 三角形 → ピクセルの、設定
    - [x] 規約は、反時計回りが表。`FrontCounterClockwise = TRUE`
    - [x] `CullMode`: 普通は `BACK`、両面は `NONE`、シャドウは `BACK` か `FRONT`
    - [x] シャドウ マップは、`DepthBias`・`SlopeScaledDepthBias` で、アクネを抑える
    - [x] `DepthClipEnable = FALSE` は、シャドウ（光の後ろの物）で使う
    - [x] 用途別に、作って、使い回す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Drawing a Triangle](triangle.md)
- [Viewport](viewport.md)
- [Depth-Stencil State](depth-stencil-state.md)
- [Shadow Bias](../../graphics/shadows/bias/index.md)
- [Microsoft Learn: ID3D11Device::CreateRasterizerState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createrasterizerstate)

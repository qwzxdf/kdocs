---
title: Rasterizer State
tags:
  - DirectX
---

# Rasterizer State

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ラスタライザー ステート</strong>は、三角形を <strong>ピクセルに変換する</strong>段（ラスタライザー）の、設定です。「どちら向きの面を表とするか」「裏面を、捨てるか」「塗りつぶすかワイヤフレームか」「深度に、バイアスを掛けるか」「画面の外を、切るか」を決めます。三角形が見えないときまず疑うのが、ここです。

!!! tip "ポイント"
    - 面の向きの既定は、<strong>時計回り（CW）が表</strong>。このサイトの規約は <strong>反時計回り（CCW）が表</strong>なので `FrontCounterClockwise = TRUE`。
    - `CullMode`: `BACK`（裏を捨てる既定）、`FRONT`、`NONE`（両面）。
    - 作成は `CreateRasterizerState`、つなぐのは `RSSetState`。作ったステートは使い回す。
    - シャドウ マップでは、`DepthBias` と `SlopeScaledDepthBias` で影のにじみ・縞（シャドウ アクネ）を、抑える。
    - 既定のステート（`RSSetState(nullptr)`）は `CullMode = BACK`、`FrontCounterClockwise = FALSE`。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

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
| `FrontCounterClockwise` | `TRUE` で反時計回りが表 |
| `DepthBias` | 深度に足す整数のバイアス |
| `DepthBiasClamp` | バイアスの上限 |
| `SlopeScaledDepthBias` | 面の傾きに比例した、バイアス |
| `DepthClipEnable` | 近・遠クリップを、有効にするか |
| `ScissorEnable` | シザー矩形を有効にするか |
| `MultisampleEnable` | MSAA のとき、マルチサンプルの四角形のエッジ処理 |
| `AntialiasedLineEnable` | 線のアンチエイリアス |

## 面の向きとカリング

三角形は画面に投影したとき頂点の並びが、<strong>時計回りか反時計回りか</strong>で、表か裏かが決まります。裏面を捨てる（`CULL_BACK`）と立体の向こう側の面を、描かずに済みピクセル シェーダーの負荷が、<strong>約半分</strong>になります。

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

### カリングを切る場面

| 場面 | `CullMode` |
| --- | --- |
| 普通の、閉じたメッシュ | `BACK` |
| 薄い板（草、旗、葉）、両面を見せたい | `NONE` |
| シャドウ マップの描画 | `BACK`（影の、アクネを減らす）か `FRONT`（前面を捨てて裏面を、描く方式） |
| 内側から見る（部屋のスカイボックス） | `FRONT`（または、頂点の並びを反転） |
| ワイヤフレーム | `FillMode = WIREFRAME`、`CullMode = NONE` |

両面を描く物（`NONE`）は裏面の法線が、逆向きになるのでピクセル シェーダーで `SV_IsFrontFace` を使って法線を、反転します。

```hlsl
float4 PSMain(VSOutput input, bool is_front : SV_IsFrontFace) : SV_Target {
  float3 normal = is_front ? input.normal : -input.normal;    // 裏面は、法線を反転
  ...
}
```

## 深度バイアス

シャドウ マップでは光から見た深度を描き後で、比較します。**同じ面の深度を比べると数値誤差で、自分の影に入ってしまう**（シャドウ アクネ）ので、描画時に深度をずらします。

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

`DepthBias` の単位は深度フォーマットに、依存します（`D32_FLOAT` と `D16_UNORM` で同じ値でも、ずれる量が違う）。値は見ながら調整します（[Shadow Bias](../../graphics/shadows/bias/index.md)）。バイアスが大きすぎると影が物から、離れて見えます（ピーターパニング）。

## DepthClipEnable

<strong>DepthClipEnable = TRUE</strong>（既定）で、近・遠クリップ面の外にあるピクセルは、切られます。`FALSE` にすると深度が 0〜1 の範囲に、クランプされ <strong>切られません</strong>。

| 使いどころ | 内容 |
| --- | --- |
| カスケード シャドウ マップ | 光の近クリップ面の手前の影を、落とす物（光の後ろの物）を切らずに、深度 0 に固定して描く |
| 無限遠の深度 | 遠クリップ面で、切れないようにする |

## ワイヤフレーム

```cpp
D3D11_RASTERIZER_DESC wire = {};
wire.FillMode = D3D11_FILL_WIREFRAME;
wire.CullMode = D3D11_CULL_NONE;
wire.FrontCounterClockwise = TRUE;
wire.DepthClipEnable = TRUE;
device->CreateRasterizerState(&wire, &wireframe_state);
```

メッシュの三角形の構造を確認するデバッグ表示に、使います。キーで切り替えるデバッグ機能に、しておくと便利です。

## シザー矩形

```cpp
desc.ScissorEnable = TRUE;
// 描画前: D3D11_RECT rect = {left, top, right, bottom};  context->RSSetScissorRects(1, &rect);
```

指定した四角形の外のピクセルを、捨てます（[Viewport](viewport.md)）。UI のはみ出しを切るのに使います。

## ステートの使い回し

ステートは不変なので起動時に、用途別に作ります。

```cpp
struct RasterizerStates {
  ComPtr<ID3D11RasterizerState> solid;       // CULL_BACK、CCW が表
  ComPtr<ID3D11RasterizerState> two_sided;   // CULL_NONE（草、旗）
  ComPtr<ID3D11RasterizerState> wireframe;   // デバッグ
  ComPtr<ID3D11RasterizerState> shadow;      // 深度バイアスつき
};
```

## よくあるミス

??? failure "三角形が、見えない（裏面として捨てられている）"
    `FrontCounterClockwise` が `FALSE`（既定の時計回りが表）のまま、反時計回りのメッシュを描いている。`TRUE` にする。または、頂点の順序を反転する。

??? failure "草や旗が、片側からしか見えない"
    `CullMode = BACK`。薄い板は `NONE`（両面）にして裏面の法線を、反転する。

??? failure "影が、縞模様（シャドウ アクネ）、または物から離れる（ピーターパニング）"
    `DepthBias`、`SlopeScaledDepthBias` が小さすぎるまたは大きすぎる。調整する。

??? failure "モデルの内側が見えて外側が、見えない（逆に見える）"
    座標系の変換（鏡像）で並びが、反転している。スケールが負（ミラー）の物は、カリングを反転するまたはステートを、切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ラスタライザー ステート ＝ 三角形 → ピクセルの設定
    - [x] 規約は反時計回りが表。`FrontCounterClockwise = TRUE`
    - [x] `CullMode`: 普通は `BACK`、両面は `NONE`、シャドウは `BACK` か `FRONT`
    - [x] シャドウ マップは、`DepthBias`・`SlopeScaledDepthBias` でアクネを抑える
    - [x] `DepthClipEnable = FALSE` はシャドウ（光の後ろの物）で使う
    - [x] 用途別に作って、使い回す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Drawing a Triangle](triangle.md)
- [Viewport](viewport.md)
- [Depth-Stencil State](depth-stencil-state.md)
- [Shadow Bias](../../graphics/shadows/bias/index.md)
- [Microsoft Learn: ID3D11Device::CreateRasterizerState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createrasterizerstate)

---
title: Blend State
tags:
  - 描画
---

# Blend State

ガラスや煙を描くと背景の色と混ざって見えます。この「混ぜ方」を決めるのが GPU のブレンド ステートです。通常のアルファ、加算、乗算で結果も描く順番への敏感さもまったく違います。設定を間違えると半透明が後ろの物を隠したり縁に黒い輪郭が出たりします。

<strong>半透明の描画は「これから描く色（ソース）」と「すでに画面にある色（デスティネーション）」を、式で混ぜることです</strong>。DirectX 11 のブレンド ステートは、その式の部品（ソースの係数、デスティネーションの係数、演算）を指定します。このページではブレンドの式、通常、加算、乗算、乗算済みアルファの特徴、順序への依存（数字つき）、深度の設定、動く C++ を説明します。

!!! tip "ポイント"
    - 通常は `SrcAlpha / InvSrcAlpha`、加算は `SrcAlpha / One`、乗算は `Zero / SrcColor` です。
    - 加算と乗算は描く順番に依存しないので、ソートが要りません。通常のアルファは依存します。
    - 半透明は深度テストをして、深度の書き込みはしません。
    - フィルタされたテクスチャの縁の黒い輪郭は、乗算済みアルファで避けられます。
    - レンダー ターゲットごとに別のブレンドを指定できます（`IndependentBlendEnable`）。

!!! info "このページを読む前に"
    - [Alpha Blending and Sorting](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ブレンドの式 {#formula}

```text
結果 = ソース × SrcBlend  [演算 BlendOp]  デスティネーション × DestBlend
```

`SrcBlend` はソース（これから描く色）に掛ける係数で、`SRC_ALPHA` や `ONE` をよく使います。`DestBlend` はデスティネーション（画面の色）に掛ける係数で、`INV_SRC_ALPHA` や `ONE` を使います。`BlendOp` は 2 つをどう組み合わせるかで、`ADD`（足す）、`MAX`、`MIN` があります。

<!-- fig:blend-modes:begin -->

<svg class="fig illust motion" data-fig="blend-modes" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-blend-modes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ブレンドの種類:同じ円を 3 つの混ぜ方で重ねる</text>
<text x="130" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">通常（アルファ）</text>
<rect x="30" y="90" width="50" height="170" fill="#e5484d"/>
<rect x="80" y="90" width="50" height="170" fill="#2ea043"/>
<rect x="130" y="90" width="50" height="170" fill="#2563eb"/>
<rect x="180" y="90" width="50" height="170" fill="#fde68a"/>
<rect x="30" y="90" width="200" height="170" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="130" cy="175" r="70" fill="#f97316" opacity="0" style="mix-blend-mode:normal"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000" values="0;0;0.6;0.6"/></circle>
<text x="130" y="292" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">背景と混ざる（α で）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="380" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">加算（光・炎）</text>
<rect x="280" y="90" width="50" height="170" fill="#e5484d"/>
<rect x="330" y="90" width="50" height="170" fill="#2ea043"/>
<rect x="380" y="90" width="50" height="170" fill="#2563eb"/>
<rect x="430" y="90" width="50" height="170" fill="#fde68a"/>
<rect x="280" y="90" width="200" height="170" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="380" cy="175" r="70" fill="#f97316" opacity="0" style="mix-blend-mode:screen"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000" values="0;0;1;1"/></circle>
<text x="380" y="292" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">明るくなる（足し算）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="630" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">乗算（影・色ガラス）</text>
<rect x="530" y="90" width="50" height="170" fill="#e5484d"/>
<rect x="580" y="90" width="50" height="170" fill="#2ea043"/>
<rect x="630" y="90" width="50" height="170" fill="#2563eb"/>
<rect x="680" y="90" width="50" height="170" fill="#fde68a"/>
<rect x="530" y="90" width="200" height="170" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="630" cy="175" r="70" fill="#8ec5ff" opacity="0" style="mix-blend-mode:multiply"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;1.0000" values="0;0;1;1"/></circle>
<text x="630" y="292" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">暗くなる（掛け算）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="30" y="336" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">通常:SrcAlpha / InvSrcAlpha、加算:One / One、乗算:Zero / SrcColor</text>
</svg>

<!-- fig:blend-modes:end -->

## 代表的なブレンド {#kinds}

### 通常のアルファ ブレンド

`結果 = ソース × α + デスティネーション × (1 − α)` でガラス、煙、フェードする物の標準です。`SrcBlend = SRC_ALPHA`、`DestBlend = INV_SRC_ALPHA` です。

### 加算ブレンド

`結果 = ソース × α + デスティネーション × 1` で火、光、魔法の輝きなど明るさを足していく表現です。`SrcBlend = SRC_ALPHA`（アルファを使わないなら `ONE`）、`DestBlend = ONE` です。重なるほど明るくなって白に近づきます。HDR ならブルームで光る表現につながります（[Bloom](../../postprocess/bloom/index.md)）。

### 乗算ブレンド

`結果 = ソース × デスティネーション` で色付きガラス、影、汚れのように背景を暗くする表現です。`SrcBlend = ZERO`、`DestBlend = SRC_COLOR` です。

### 乗算済みアルファ

`結果 = ソース（すでに α が掛かっている） + デスティネーション × (1 − α)` です。ソースにあらかじめアルファを掛けておく形で `SrcBlend = ONE`、`DestBlend = INV_SRC_ALPHA` です（[Premultiplied Alpha](premultiplied.md)）。

### 最大値

`BlendOp = MAX` で重なっても強い方だけを残します（[Trampled Grass](../../terrain/vegetation/trample.md)）。

## 順序への依存 {#order}

通常のアルファは描く順番で結果が変わります。赤（`(1, 0, 0)`、α = 0.5）と青（`(0, 0, 1)`、α = 0.5）を黒い背景に重ねて、計算しました。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="赤と青を逆の順番で重ねたときの色。通常のアルファは変わり、加算と乗算は同じ"><text x="14" y="22" class="fig-title">描く順番を入れ替えたときの結果（黒い背景、α = 0.5）</text>
<g stroke="#94a3b8" stroke-width="1.5"><rect x="110" y="50" width="110" height="70" rx="8" fill="#400080"/><rect x="250" y="50" width="110" height="70" rx="8" fill="#800040"/><rect x="420" y="50" width="110" height="70" rx="8" fill="#800080"/><rect x="560" y="50" width="110" height="70" rx="8" fill="#800080"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="165" y="140">赤 → 青</text><text x="165" y="158">(0.25, 0, 0.5)</text><text x="305" y="140">青 → 赤</text><text x="305" y="158">(0.5, 0, 0.25)</text><text x="235" y="44" style="font-weight:600">通常のアルファ: 順序で変わる</text>
<text x="475" y="140">赤 → 青</text><text x="475" y="158">(0.5, 0, 0.5)</text><text x="615" y="140">青 → 赤</text><text x="615" y="158">(0.5, 0, 0.5)</text><text x="545" y="44" style="font-weight:600">加算: 同じ</text></g>
<text x="360" y="204" text-anchor="middle" style="font-size:12px">乗算も同じ（(1, 0.5, 0.5) × (0.5, 1, 0.5) はどちらの順でも (0.5, 0.5, 0.25)）</text>
<text x="360" y="224" text-anchor="middle" style="font-size:12px">足し算も掛け算も交換できるので、加算と乗算はソートが要らない</text></svg>

通常のアルファは赤を先に描くと `(0.25, 0, 0.5)`、青を先に描くと `(0.5, 0, 0.25)` で手前に描いた色が強く出ます。加算はどちらの順でも `(0.5, 0, 0.5)` で同じです。乗算も `(1, 0.5, 0.5)` と `(0.5, 1, 0.5)` を掛けてどちらの順でも `(0.5, 0.5, 0.25)` になります。足し算も掛け算も交換できるからです。そのため、炎、光の粒、影はソートなしで描けることが多いです。通常のアルファの物（ガラス、煙）は奥から手前へソートします（[Sorting](sorting.md)）。

## 乗算済みアルファと縁の輪郭 {#premultiplied}

ストレートなアルファ（色にアルファが掛かっていない画像）のテクスチャをバイリニア フィルタで拡大すると、縁に黒い輪郭が出ることがあります。不透明な赤（`(1, 0, 0, 1)`）と透明な黒（`(0, 0, 0, 0)`）の境目を例にちょうど中間のサンプルを計算しました。バイリニア補間の結果は `(0.5, 0, 0, 0.5)` です。

白い背景に重ねるとストレートの式（`SRC_ALPHA / INV_SRC_ALPHA`）は `(0.5, 0, 0) × 0.5 + (1, 1, 1) × 0.5 = (0.75, 0.5, 0.5)` で、赤が暗く（くすんで）なります。本来の「50 % の赤」は `(1, 0.5, 0.5)` のはずです。乗算済みの式（`ONE / INV_SRC_ALPHA`）なら `(0.5, 0, 0) + (1, 1, 1) × 0.5 = (1, 0.5, 0.5)` で、正しい結果になります。

原因はストレートの画像で透明な画素の色（ここでは黒）が補間に混ざることです。乗算済みアルファでは色にアルファが掛かっているので、補間しても透明な画素は色の寄与が 0 のままです。これが縁の黒い輪郭を避けられる理由です。

## 深度の設定 {#depth}

半透明は深度テストは行って深度の書き込みはしないのが基本です。

- 深度テストを有効にすると、不透明な物の後ろにある半透明は描かれません。
- 深度の書き込みを無効にします。半透明が深度を書くとその後ろの半透明が隠れて、穴が開いたように見えます。

描く順番は不透明を描いて深度を書き半透明を描いて（深度テストのみ奥から手前へソート）、ポストプロセスです。

## 動く C++ {#cpp}

4 種類のブレンド ステートと深度のステートをまとめて作る関数です。

```cpp
#include <d3d11.h>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

// 1 つのレンダー ターゲットのブレンド設定を作る小さな関数
static D3D11_RENDER_TARGET_BLEND_DESC MakeBlend(D3D11_BLEND src, D3D11_BLEND dest, D3D11_BLEND_OP op) {
  D3D11_RENDER_TARGET_BLEND_DESC rt = {};
  rt.BlendEnable = TRUE;
  rt.SrcBlend = src;                        // ソース（これから描く色）に掛ける係数
  rt.DestBlend = dest;                      // デスティネーション（画面の色）に掛ける係数
  rt.BlendOp = op;
  rt.SrcBlendAlpha = D3D11_BLEND_ONE;       // アルファ チャンネルの合成: 通常は ONE / INV_SRC_ALPHA
  rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
  rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
  return rt;
}

struct TransparentStates {
  ComPtr<ID3D11BlendState> alpha, premultiplied, additive, multiply;
  ComPtr<ID3D11DepthStencilState> depth_test_only;   // 深度テストはするが、書き込まない
};

HRESULT CreateTransparentStates(ID3D11Device* device, TransparentStates* out) {
  const struct { D3D11_BLEND src, dest; ComPtr<ID3D11BlendState>* target; } kinds[] = {
      {D3D11_BLEND_SRC_ALPHA, D3D11_BLEND_INV_SRC_ALPHA, &out->alpha},       // C_s·α + C_d·(1−α)
      {D3D11_BLEND_ONE, D3D11_BLEND_INV_SRC_ALPHA, &out->premultiplied},     // C_s + C_d·(1−α)（C_s は α 掛け済み）
      {D3D11_BLEND_SRC_ALPHA, D3D11_BLEND_ONE, &out->additive},              // C_s·α + C_d
      {D3D11_BLEND_ZERO, D3D11_BLEND_SRC_COLOR, &out->multiply},             // C_d · C_s
  };
  for (const auto& k : kinds) {
    D3D11_BLEND_DESC desc = {};
    desc.RenderTarget[0] = MakeBlend(k.src, k.dest, D3D11_BLEND_OP_ADD);
    const HRESULT hr = device->CreateBlendState(&desc, k.target->GetAddressOf());
    if (FAILED(hr)) return hr;
  }
  D3D11_DEPTH_STENCIL_DESC ds = {};
  ds.DepthEnable = TRUE;                                  // 不透明な物の後ろは隠す
  ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;        // 半透明は深度を書かない
  ds.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
  return device->CreateDepthStencilState(&ds, out->depth_test_only.GetAddressOf());
}
```

アルファ チャンネルの合成は `ONE / INV_SRC_ALPHA` にしています。これで画面に残るアルファが重なりに応じて正しく累積します。使うときは描画の前に `context->OMSetBlendState(states.alpha.Get(), nullptr, 0xffffffff)` と `context->OMSetDepthStencilState(states.depth_test_only.Get(), 0)` を呼びます。

乗算済みアルファにするにはピクセル シェーダーで、出力の色にアルファを掛けます。

```hlsl
Texture2D<float4> g_tex : register(t0);
SamplerState g_linear_wrap : register(s0);

float4 PremultipliedPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float4 c = g_tex.Sample(g_linear_wrap, uv);        // ストレートなアルファのテクスチャ
  return float4(c.rgb * c.a, c.a);                    // 乗算済みにして返す（ONE / INV_SRC_ALPHA 用）
}
```

テクスチャを最初から乗算済みで保存しておけば、フィルタの段階で輪郭が出ません。シェーダーで掛ける方法はフィルタ後に掛けるので、輪郭が残ります。

!!! note "確かめた範囲"
    C++ は MSVC（`/W4`、`/c`）でコンパイルして警告もエラーも出ないことを確かめました（実行はしていません）。HLSL は `fxc`（`ps_5_0`）でコンパイルしました。順序への依存と縁の輪郭の数字は Python での計算です。GPU での描画は確認していません。

## 複数のレンダー ターゲット {#mrt}

レンダー ターゲットごとに別のブレンドを指定できます（`IndependentBlendEnable = TRUE`）。OIT の実装（[WBOIT](../oit/wboit.md)）で、2 つのターゲットに別々のブレンドを使います。1 つ目は加算（積算）で 2 つ目は乗算風（透過度）です。

## 比較 {#compare}

- アルファ（`SRC_ALPHA / INV_SRC_ALPHA`）はガラスやフェードに向きます。順序に依存します。
- 乗算済みアルファ（`ONE / INV_SRC_ALPHA`）は煙と光を 1 つのレイヤーで扱えます。順序に依存します。
- 加算（`SRC_ALPHA / ONE`）は火、光、魔法に向きます。順序に依存しません。
- 乗算（`ZERO / SRC_COLOR`）は色ガラスや影に向きます。順序に依存しません。
- 最大値（`MAX`）は重なっても強い方を残します。順序に依存しません。

## よくあるミス {#mistakes}

??? failure "半透明の物が後ろの物を隠して、穴が開いたように見える"
    原因は深度の書き込みが有効なことです。手前の半透明が深度を書くと奥の半透明が描かれなくなります。`DepthWriteMask = ZERO` にします。

??? failure "テクスチャの縁に黒い輪郭が出る"
    原因はストレートなアルファの画像をフィルタしてから合成していることです。透明な画素の色が補間に混ざります。乗算済みアルファの画像にして、`ONE / INV_SRC_ALPHA` で合成します。

??? failure "加算ブレンドの物が、背景を暗くしてしまう"
    原因は `DestBlend` を `INV_SRC_ALPHA` にしていることです。加算は `DestBlend = ONE` にして画面の色をそのまま残します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 通常、加算、乗算の 3 つを覚えます。加算と乗算は順序に依存しません。
    - [x] 半透明は深度テストをして、深度の書き込みはしません。
    - [x] 縁の輪郭は乗算済みアルファで避けられます。
    - [x] 通常のアルファは、奥から手前へソートします。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は式からの計算です。

- Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Smith, "Image Compositing Fundamentals", Microsoft Technical Memo 4, 1995（乗算済みアルファ）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（`SrcBlend`、`DestBlend`、`BlendOp`）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [Premultiplied Alpha](premultiplied.md)

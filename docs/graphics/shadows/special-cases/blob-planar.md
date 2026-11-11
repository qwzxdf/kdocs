---
title: Blob and Planar Projected Shadows
tags:
  - 描画
---

# Blob and Planar Projected Shadows

シャドウ マップは強力ですが、コストが高くバイアスやちらつきの調整も大変です。モバイル、遠くの小さな物、数百体の群衆にすべてシャドウ マップを使うのは現実的ではありません。それでも足元に影がないとキャラクターが地面から浮いて見えます。

<strong>もっと安い影の技法が 2 つあります</strong>。ブロブ シャドウは足元に丸く暗い板を置くだけです。平面投影シャドウは物体を光の向きで地面に押しつぶして、暗い単色で描きます。このページではブロブの作り方（高さによる変化）、平面投影行列の導出と検算（DirectXMath の `XMMatrixShadow` と一致を確認）、二重ブレンドの防止、使い分けを説明します。

!!! tip "ポイント"
    - ブロブは足元に丸くぼかした影の板を置きます。物が高く上がるほど薄く大きくします。
    - 平面投影は物体の頂点を光の向きに沿って地面の平面へ投影した形で描きます。
    - どちらも安いですが、地面が平らな場合の手法です。
    - 平面投影は三角形が重なる所が 2 回描かれて濃くなるので、ステンシルで 1 画素 1 回に制限します。
    - モバイル、遠くの小さな物、キャラクターの接地感の補助に使います。

!!! info "このページを読む前に"
    - [Special Cases](index.md)（このセクション全体の地図と読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

<!-- fig:blob-planar:begin -->

<svg class="fig illust motion" data-fig="blob-planar" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-blob-planar" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">簡易な影:ブロブ（丸い影）と、平面投影</text>
<text x="190" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ブロブ:高さで、大きさと濃さを変える</text>
<rect x="40" y="310" width="300" height="14" fill="#d6c7a1"/>
<ellipse cx="190" cy="316" rx="34" ry="8" fill="#000000" fill-opacity="0.6"><animate attributeName="rx" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.2500;0.4167;0.5833;0.7500;1.0000" values="34;34;34;60;34;34;34"/><animate attributeName="fill-opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.2500;0.4167;0.5833;0.7500;1.0000" values="0.6;0.6;0.6;0.18;0.6;0.6;0.6"/></ellipse>
<circle cx="190" cy="300" r="22" fill="#e5484d" stroke="#ffffff" stroke-width="2"><animate attributeName="cy" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.2500;0.4167;0.5833;0.7500;1.0000" values="300;300;300;140;300;300;300"/></circle>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">地面にいる:小さく濃い影<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2497;0.2500;1.0000" values="1;1;0;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ジャンプ…<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2497;0.2500;0.4163;0.4167;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高い:大きく薄い影<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4163;0.4167;0.5830;0.5833;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">着地:また小さく濃い<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5830;0.5833;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="570" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">平面投影:行列で、地面に押しつぶす</text>
<rect x="420" y="310" width="300" height="14" fill="#d6c7a1"/>
<polygon points="530,220 590,220 590,280 530,280" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<polygon points="0,0 0,0 0,0 0,0" fill="#000000" fill-opacity="0.5"><animate attributeName="points" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.3333;0.6667;0.9583;1.0000" values="0,0 0,0 0,0 0,0;0,0 0,0 0,0 0,0;542.35,310 696.36,310 696.36,316 542.35,316;542.35,310 696.36,310 696.36,316 542.35,316;415.45,310 575.88,310 575.88,316 415.45,316;415.45,310 575.88,310 575.88,316 415.45,316;415.45,310 575.88,310 575.88,316 415.45,316"/></polygon>
<circle cx="460" cy="110" r="12" fill="#e5aa28"><animate attributeName="cx" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.3333;0.6667;0.9583;1.0000" values="460;460;460;670;670;670"/></circle>
<text x="420" y="360" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">光の向きに沿って、物の頂点を地面へ投影した所が影<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="410" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">どちらもシャドウ マップなしで描ける、安い影。地面が平らな場合に有効（段差や他の物には落ちない）。</text>
</svg>

<!-- fig:blob-planar:end -->

## ブロブ シャドウ（丸い影） {#blob}

物の足元に丸くてぼんやりした暗い絵（ブロブ）を地面に貼るだけの最も簡単な影です。

```text
     ●  キャラクター
     │
   ░░▓▓░░     ← 足元の丸いブロブ影
 ━━━━━━━━━━━  地面
```

長所は軽いこと（四角形 1 枚）、ちらつかないこと接地感がしっかり出ることモバイルや低スペックで使えることです。短所は形が丸いだけで物の形にならないこと光の方向に依存せず真下にできること、地面が凸凹だと浮いて見えることほかの物に影が落ちないことです。

実装は地面に貼った四角形（デカール）のピクセル シェーダーで、中心からの距離で暗くします。物が地面から離れるほど薄く大きくします。

```hlsl
cbuffer BlobConstants : register(b0) {
  float4x4 g_view_proj;
  float3 g_blob_center;        // 足元の位置（ワールド）。地面に接する点
  float g_base_radius;         // 基本の半径（メートル）。例: 0.6
  float g_height_above_ground; // 物の地面からの高さ（メートル）。ジャンプ中に大きくなる
  float g_max_height;          // この高さで影が消える（メートル）。例: 3
  float g_base_opacity;        // 地面に接しているときの濃さ 0..1。例: 0.6
  float g_spread;              // 高いほど広がる量。例: 0.5
};

struct BlobVsOut {
  float4 pos : SV_Position;
  float2 uv : TEXCOORD0;
};

// 地面に寝かせた四角形（ストリップ 4 頂点）。高さに応じて半径を広げる
BlobVsOut BlobVS(uint vertex_id : SV_VertexID) {
  float2 corner = float2(vertex_id & 1, vertex_id >> 1) * 2.0 - 1.0;
  float h01 = saturate(g_height_above_ground / g_max_height);
  float radius = g_base_radius * (1.0 + g_spread * h01);               // 高いほど大きい
  float3 world = g_blob_center + float3(corner.x, 0.02, corner.y) * radius;   // 0.02: Z ファイティング避け
  BlobVsOut o;
  o.pos = mul(float4(world, 1.0), g_view_proj);
  o.uv = corner * 0.5 + 0.5;
  return o;
}

float4 BlobPS(BlobVsOut i) : SV_Target {
  float d = distance(i.uv, float2(0.5, 0.5)) * 2.0;                    // 中心 0、縁 1
  float alpha = saturate(1.0 - d);
  alpha *= alpha;                                                       // 縁をなだらかに（2 乗）
  float h01 = saturate(g_height_above_ground / g_max_height);
  float opacity = g_base_opacity * (1.0 - h01);                         // 高いほど薄い
  return float4(0, 0, 0, alpha * opacity);                              // アルファ ブレンドで地面に重ねる
}
```

地面に貼るので斜面や段差で浮かないように四角形を地形に投影すると、よくなります（デカール、[Terrain Decals and Roads](../../terrain/texturing/decals.md)）。足ごとにブロブを置くと歩く足元の接地が強調されます。ブロブと本格的な影を組み合わせて、近くは本格的に遠くはブロブにする（LOD）のも一般的です。

## 平面投影シャドウ {#planar}

物体の頂点を平面（地面）に投影して、影の形をそのまま描く方法です（Blinn、1988）。物の形になった影が平らな地面にできます。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="頂点を光の進む向きに沿って、地面の平面まで運ぶ。式は x' = x − (n·x + d)/(n·l) · l"><defs><marker id="bpA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">頂点を、光の向きに沿って地面へ運ぶ</text>
<line x1="40" y1="210" x2="680" y2="210" stroke="currentColor" stroke-width="2"/><text x="680" y="232" text-anchor="end" style="font-size:12px">地面（平面 n·x + d = 0）</text>
<circle cx="250" cy="80" r="6" fill="#4c8bf5"/><text x="258" y="74" style="font-size:12px;font-weight:600;fill:#4c8bf5">頂点 x</text>
<line x1="250" y1="80" x2="400" y2="205" stroke="#e5aa28" stroke-width="3" marker-end="url(#bpA)"/><text x="330" y="124" style="font-size:12px;font-weight:600;fill:#b7791f">光の進む向き l</text>
<circle cx="402" cy="210" r="6" fill="#e5484d"/><text x="410" y="230" style="font-size:12px;font-weight:600;fill:#e5484d">影の位置 x'</text>
<line x1="250" y1="80" x2="250" y2="210" stroke="#94a3b8" stroke-dasharray="4 4"/><text x="240" y="150" text-anchor="end" style="font-size:12px">高さ n·x + d</text>
<text x="470" y="80" style="font-size:13px;font-weight:600">x' = x − (n·x + d) / (n·l) · l</text><text x="470" y="104" style="font-size:12px">平面までの高さ ÷ 光の向きの「下向き成分」ぶん、l に沿って進む</text></svg>

頂点 `x` から光の進む向き `l` に沿って、平面 `n·x + d = 0` に届くまで進みます。進む距離は平面までの高さ `n·x + d` を光の向きの下向き成分 `n·l` で割った量です。

<div class="formula">x' = x − (n·x + d) / (n·l) · l</div>

行ベクトル × 行列の同次座標にするには、`x' = (n·l) x − l (n·x + d)` を `w' = n·l` で割ると考えて行列の成分を次のようにします。

```text
M[i][j] = (n·l) · δ_ij − n_i · l_j     （i, j = 0..2）
M[3][j] = −d · l_j                      （j = 0..2）
M[i][3] = 0                             （i = 0..2）
M[3][3] = n·l
```

DirectXMath の `XMMatrixShadow` と結果を比べました（MSVC で実行）。平面 `y = 0`、光の進む向き `(0.3, −0.8, 0.2)` で 3 つの頂点を投影したところ自分で導いた行列と `XMMatrixShadow` の結果は完全に一致しました（差は 0）。投影点の `y` は 0 で元の点との差は光の向きに平行でした（誤差は約 2 × 10⁻⁷）。

```cpp
#include <DirectXMath.h>

using namespace DirectX;

// 自分で導いた平面投影行列（行ベクトル × 行列）。平面: n·x + d = 0、l は光が進む向き
XMMATRIX PlanarShadow(XMFLOAT3 n, float d, XMFLOAT3 l) {
  const float nl = n.x * l.x + n.y * l.y + n.z * l.z;          // 光の向きの、法線方向の成分
  const float nv[3] = {n.x, n.y, n.z}, lv[3] = {l.x, l.y, l.z};
  XMFLOAT4X4 m = {};
  for (int i = 0; i < 3; ++i)
    for (int j = 0; j < 3; ++j) m.m[i][j] = (i == j ? nl : 0.0f) - nv[i] * lv[j];
  for (int j = 0; j < 3; ++j) m.m[3][j] = -d * lv[j];
  m.m[3][3] = nl;
  return XMLoadFloat4x4(&m);
}

// DirectXMath の関数でも同じ行列が得られる。第 2 引数は「物体から光へ向かう向き」（w = 0 なら平行光）
XMMATRIX PlanarShadowBuiltIn(XMFLOAT3 n, float d, XMFLOAT3 l) {
  return XMMatrixShadow(XMVectorSet(n.x, n.y, n.z, d), XMVectorSet(-l.x, -l.y, -l.z, 0.0f));
}
```

`XMMatrixShadow` の第 2 引数は光が進む向きの逆（物体から光へ向かう向き）です。このページのコードは `l`（光が進む向き）を符号反転して渡しています。

描き方は物を投影行列で変換して、もう一度描きます。色は半透明の黒です。

- 二重ブレンドの問題があります。物の三角形が重なる部分が 2 回描かれて、濃くなります（ムラ）。ステンシルで 1 画素 1 回に制限します。
- Z ファイティングがあります。影の平面が地面と同じ高さでちらつきます。少し持ち上げる（バイアス）か深度バイアスを使います。

```cpp
// （コンパイルしていない）二重ブレンドの防止: ステンシルが 0 の画素にだけ描き、描いたら 1 にする
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
ds.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
ds.StencilEnable = TRUE;
ds.StencilReadMask = ds.StencilWriteMask = 0xFF;
ds.FrontFace.StencilFunc = D3D11_COMPARISON_EQUAL;              // ステンシルが 0 のときだけ
ds.FrontFace.StencilPassOp = D3D11_STENCIL_OP_INCR_SAT;         // 描いたら 1 に増やす
ds.FrontFace.StencilFailOp = D3D11_STENCIL_OP_KEEP;
ds.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_KEEP;
ds.BackFace = ds.FrontFace;
device->CreateDepthStencilState(&ds, &planar_shadow_ds);
// 参照値 0 で設定する: context->OMSetDepthStencilState(planar_shadow_ds.Get(), 0);
```

長所は物の形の影が出ること光の方向に従うことシャドウ マップが不要なことです。古いゲーム機やモバイルでも使えます。短所は平らな地面にしか落ちないこと（階段、壁、ほかの物に落ちない）、影の縁が硬いこと（ぼかしが難しい）、物をもう一度描くコストがかかること自己影やほかの物への影が無いことです。

!!! note "確かめた範囲"
    平面投影行列は C++（MSVC `/W4`、DirectXMath）で自分で導いた行列と `XMMatrixShadow` が一致すること投影点が平面上にあって、光の向きに沿っていることを確かめました。HLSL は `fxc` で `BlobVS`（`vs_5_0`）と `BlobPS`（`ps_5_0`）をコンパイルして、エラーが出ないことを確かめました。ステンシルの C++ はコンパイルしていません。GPU での描画は確認していません。

## 使い分け {#choice}

- モバイルや低スペックではブロブ影を使います。最も安いです。
- キャラクターの接地感の補強にはブロブ影を使います。シャドウ マップと併用します。
- 平らな地面の物の形の影には平面投影を使います。
- 遠くの小さな物（群衆、車）にはブロブ影を使いシャドウ マップは省きます。
- 本格的なゲーム（PC、コンソール）ではシャドウ マップとコンタクト シャドウを使いブロブ影は補助にします。

## よくあるミス {#mistakes}

??? failure "段差のある地面で、平面投影の影が空中に浮く"
    原因は平面投影が 1 枚の平面を前提にしていることです。平らな地面でのみ使うかシャドウ マップに切り替えます。

??? failure "平面投影の影の重なった部分だけ濃い"
    原因は物の三角形が重なる部分が、2 回描かれていることです。ステンシルで 1 画素 1 回に制限します。

??? failure "ブロブ影が、地面に埋まって見えないまたはちらつく"
    原因は影の板が地面と同じ高さにあることです（Z ファイティング）。少し持ち上げるか深度バイアスを使います。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] ブロブは足元の丸い板です。高いほど薄く大きくします。
    - [x] 平面投影は `x' = x − (n·x + d)/(n·l) · l` で頂点を地面へ運びます。`XMMatrixShadow` と同じ行列になります。
    - [x] 平面投影の二重ブレンドは、ステンシルで防ぎます。
    - [x] どちらも平らな地面向きで、モバイルと遠景向きです。

## 参考 {#references}

このページは次の資料を読まずに書きました。平面投影行列は自分で導いて `XMMatrixShadow` との一致を実行して確かめました。

- Blinn, "Me and My (Fake) Shadow", IEEE Computer Graphics and Applications, Vol. 8, No. 1, 1988（平面への投影影）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Microsoft Learn, "XMMatrixShadow function (DirectXMath)"

## 関連ページ

- [Special Cases](index.md)
- [Distance Field Shadows](../sdf-shadows.md)
- [Contact Shadows](../contact-shadows.md)

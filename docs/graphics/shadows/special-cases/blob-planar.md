---
title: Blob and Planar Projected Shadows
tags:
  - 描画
---

# Blob and Planar Projected Shadows

<strong>シャドウ マップが重い・使えない環境（モバイル・遠くの小物）</strong>では、もっと安い影の技法を使います。ブロブ シャドウは足元に丸い暗い円を置くだけ、平面投影シャドウは物体を地面に押しつぶして黒く描く方法です。どちらも、柔らかさや正確さは劣りますが、安いです。このページではブロブ・平面投影の仕組みと使いどころを説明します。

!!! tip "ポイント"
    - ブロブ ＝ 足元に丸いぼかした影の板を置く。
    - 平面投影 ＝ 物体を光の向きで地面に投影した形で、黒く描く。
    - どちらも安いが、地面が平らな場合のみ。
    - モバイル・遠くの小さな物・キャラクターの補助の影に使う。

!!! info "このページを読む前に"
    - [Special Cases](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

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

## ブロブ シャドウ（丸い影）
<strong>足元に柔らかい丸い暗い画像</strong>（ブロブ）を地面に貼るだけの影です。シャドウ マップなしで最も安く、「地面に接している」感じを出せます。

| 項目 | 内容 |
| --- | --- |
| 実装 | 地面に丸いグラデーションの四角形（デカール）をキャラの足元に置く（デカール） |
| 変化 | 高さに応じて薄く・大きく（ジャンプ中は薄くぼける） |
| 利点 | 安い。モバイル・多数のキャラに向く |
| 欠点 | 形が丸いだけ。光の方向・物の形を反映しない。傾斜地で浮く |

ブロブ ＋ 本格的な影を組み合わせ、近くは本格、遠くはブロブのように切り替える（LOD）ことも一般的です。

## 平面投影シャドウ
<strong>物体のジオメトリを「地面の平面」に押し潰す</strong>行列をかけて描き、暗い単色で塗ります。

<div class="formula">平面 n·x + d = 0 へ、光の方向 L に沿って投影する行列（4×4）</div>

```cpp
XMVECTOR plane = XMVectorSet(0, 1, 0, 0);
XMVECTOR light = XMVectorSet(light_dir.x, light_dir.y, light_dir.z, 0);
XMMATRIX shadow_matrix = XMMatrixShadow(plane, XMVectorNegate(light));
```

| 項目 | 内容 |
| --- | --- |
| `XMMatrixShadow` | DirectXMath の関数。平面と光の方向から投影行列を作る |
| 描画 | 物体を `shadow_matrix` で変換して、黒（半透明）で描く |
| Z ファイティング対策 | 平面と同じ高さになるので、少しオフセット・ステンシルで二重描画を防ぐ |
| 利点 | 形が正確・シャドウ マップ不要 |
| 欠点 | 平らな床のみ。他の物への落とす影・自己影は不可。ハード エッジ |

古い手法ですが平らな床のゲーム（スポーツ・シンプルな 3D）では今でも有効です。

## シャドウ マップを使わない影

<strong>シャドウ マップ</strong>は 強力ですが、コストが高く画質の調整（バイアス、ちらつき）も大変です。用途によってはもっと簡単な方法で十分に見栄えのする影が作れます。

## ブロブ影（丸い影）

<strong>物の足元に丸くてぼんやりした、暗い絵</strong>（ブロブ）を地面に貼るだけの最も簡単な影です。

```text
     ●  キャラクター
     │
   ░░▓▓░░     ← 足元の、丸いブロブ影
 ━━━━━━━━━━━  地面
```

| 長所 | 短所 |
| --- | --- |
| 軽い（四角形 1 枚） | 形が丸い（物の形にならない） |
| ちらつかない安定 | 光の方向に依存しない（真下にできる） |
| 接地感がしっかり出る | 地面が凸凹だと浮いて見える |
| モバイル、低スペックで使える | 他の物に影が落ちない |

### 実装

```hlsl
// ブロブ影: 地面に貼った、四角形（デカール）の、ピクセル シェーダー。中心から、距離で、暗くする。
float4 main(float2 uv : TEXCOORD0) : SV_Target {
  float d = distance(uv, float2(0.5, 0.5)) * 2.0;            // 中心 0、縁 1
  float alpha = saturate(1.0 - d);
  alpha *= alpha;                                             // 縁をなだらかに（2 乗）
  return float4(0, 0, 0, alpha * g_shadow_opacity);          // アルファ ブレンドで、地面に重ねる
}
```

| 工夫 | 内容 |
| --- | --- |
| 高さで薄くする | 物が地面から離れる（ジャンプ）ほど薄く、広がる |
| 地面に沿わせる | 四角形を地面の形に投影（デカール、[Terrain Decals and Roads](../../terrain/texturing/decals.md)）。斜面でも浮かない |
| 複数（足ごと） | 足ごとに、ブロブを置くと歩く足元の接地が強調される |

## 平面への投影影（プラナー シャドウ）

<strong>物の頂点を平面（地面）に投影</strong>して、影の形をそのまま描く方法です（Blinn、1988）。物の形になった影が平らな地面にできます。

```text
 光
  ╲
    ╲     ●物
      ╲   │
 ━━━━━━━▓▓▓▓━━━  地面  ← 物の形を、地面に、投影した、影
```

光の方向と 平面の式から、投影行列を作ります。

```cpp
using namespace DirectX::SimpleMath;

// 平面 n·p + d = 0 に、光の方向 l（光が進む向き）で、投影する行列（左手系、行ベクトル）。
// 投影行列 = d·I − l·nᵀ  の形（頂点を同次座標で、平面上へ移す）。
Matrix PlanarShadowMatrix(const Vector3& plane_normal, float plane_d, const Vector3& light_dir) {
  const float dot = plane_normal.Dot(light_dir);
  Matrix m;
  m._11 = dot - light_dir.x * plane_normal.x * -1.0f;   // 実装の詳細は、行列の転置と符号に注意
  // （ここでは、概念を示す。実際には DirectX::XMMatrixShadow を使うと、簡単）
  return DirectX::XMMatrixShadow(DirectX::XMVectorSet(plane_normal.x, plane_normal.y, plane_normal.z, plane_d),
                                 DirectX::XMVectorSet(-light_dir.x, -light_dir.y, -light_dir.z, 0.0f));
}
```

`DirectX::XMMatrixShadow`（DirectXMath）が平面と光の位置（または方向）から、投影行列を作ってくれます。

| 要素 | 内容 |
| --- | --- |
| 描き方 | 物を投影行列で、変換してもう一度描く。色は半透明の黒 |
| 二重ブレンドの問題 | 物の、三角形が重なる部分が 2 回描かれ、濃くなる（ムラ）。ステンシルで 1 画素 1 回に制限する |
| Z ファイティング | 影の平面が地面と、同じ高さでチラつく。少し持ち上げる（バイアス）、または深度バイアス |

```cpp
// 二重ブレンドの防止: ステンシルが 0 の画素にだけ描き、描いたら、ステンシルを 1 にする。
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
ds.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
ds.StencilEnable = TRUE;
ds.StencilReadMask = ds.StencilWriteMask = 0xFF;
ds.FrontFace.StencilFunc = D3D11_COMPARISON_EQUAL;              // ステンシルが 0 のとき、だけ
ds.FrontFace.StencilPassOp = D3D11_STENCIL_OP_INCR_SAT;         // 描いたら、1 に増やす
ds.FrontFace.StencilFailOp = D3D11_STENCIL_OP_KEEP;
ds.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_KEEP;
ds.BackFace = ds.FrontFace;
device->CreateDepthStencilState(&ds, &planar_shadow_ds);
// 参照値 0 で設定する: context->OMSetDepthStencilState(planar_shadow_ds.Get(), 0);
```

| 長所 | 短所 |
| --- | --- |
| 物の形の影が出る | 平らな地面にしか、落ちない（階段、壁、他の物に落ちない） |
| 光の方向に従う | 影の縁が硬い（ぼかしが難しい） |
| シャドウ マップが不要 | 物をもう一度描く（コストがかかる） |
| 古いゲーム機、モバイルで使われる | 自己影、他の物への影が無い |

## 使い分け

| 状況 | 方法 |
| --- | --- |
| モバイル、低スペック | ブロブ影（最も安い） |
| キャラクターの接地感の補強 | ブロブ影（シャドウ マップと、併用） |
| 平らな地面の物の形の影 | プラナー シャドウ |
| 遠くの小さな物（群衆、車） | ブロブ影（シャドウ マップは、省く） |
| 本格的なゲーム（PC、コンソール） | シャドウ マップ + コンタクト シャドウ。ブロブ影は補助 |

## よくあるミス

??? failure "段差のある地面で、平面投影の影が空中に浮く"
    <strong>平らな地面でのみ使う</strong>、またはシャドウ マップに切り替え。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ブロブ・平面投影は、安い影
    - [x] 平らな地面向き。モバイル・遠景向き

## 参考

- Blinn, "Me and My (Fake) Shadow", IEEE Computer Graphics and Applications, Vol. 8, No. 1, 1988（平面への、投影影）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Microsoft Learn, "XMMatrixShadow function (DirectXMath)"

## 関連ページ

- [Special Cases](index.md)
- [Distance Field Shadows](../sdf-shadows.md)
- [Contact Shadows](../contact-shadows.md)

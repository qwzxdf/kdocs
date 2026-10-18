---
title: Froxels
tags:
  - 描画
---

# Froxels

<strong>froxel は、カメラの視錐台（frustum）を分けた、3D のボクセルです</strong>。<strong>画面に近い所は細かく、遠い所は粗くなる</strong>ので、見た目に効率が良いです。このページでは、froxel の構造を説明します。

!!! tip "ポイント"
    - froxel ＝ frustum ＋ voxel。
    - 画面の縦横に分割し、奥行きを対数的に分割。
    - 3D テクスチャ（例：160×90×64）で持つ。
    - 近くが細かいので、効率的。

<!-- fig:froxel-slices:begin -->

<svg class="fig illust motion" data-fig="froxel-slices" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-froxel-slices" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">froxel:視錐台を、奥行きに沿って、手前ほど細かく分ける</text>
<polygon points="372,380 408,380 690,90 90,90" fill="#eff6ff" stroke="#64748b" stroke-width="2"/>
<circle cx="390" cy="406" r="8" fill="#e5484d"/>
<text x="404" y="412" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">カメラ</text>
<line x1="372.0" y1="380.0" x2="408.0" y2="380.0" stroke="#64748b" stroke-width="2"/>
<line x1="348.5" y1="355.83" x2="431.5" y2="355.83" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="348.5;348.5;348.5;368.81;368.81;368.81"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="431.5;431.5;431.5;411.19;411.19;411.19"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="355.83;355.83;355.83;376.72;376.72;376.72"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="355.83;355.83;355.83;376.72;376.72;376.72"/></line>
<line x1="325.0" y1="331.67" x2="455.0" y2="331.67" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="325;325;325;364.58;364.58;364.58"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="455;455;455;415.42;415.42;415.42"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="331.67;331.67;331.67;372.37;372.37;372.37"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="331.67;331.67;331.67;372.37;372.37;372.37"/></line>
<line x1="301.5" y1="307.5" x2="478.5" y2="307.5" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="301.5;301.5;301.5;358.96;358.96;358.96"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="478.5;478.5;478.5;421.04;421.04;421.04"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="307.5;307.5;307.5;366.59;366.59;366.59"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="307.5;307.5;307.5;366.59;366.59;366.59"/></line>
<line x1="278.0" y1="283.33" x2="502.0" y2="283.33" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="278;278;278;351.5;351.5;351.5"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="502;502;502;428.5;428.5;428.5"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="283.33;283.33;283.33;358.91;358.91;358.91"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="283.33;283.33;283.33;358.91;358.91;358.91"/></line>
<line x1="254.5" y1="259.17" x2="525.5" y2="259.17" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="254.5;254.5;254.5;341.59;341.59;341.59"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="525.5;525.5;525.5;438.41;438.41;438.41"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="259.17;259.17;259.17;348.73;348.73;348.73"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="259.17;259.17;259.17;348.73;348.73;348.73"/></line>
<line x1="231.0" y1="235.0" x2="549.0" y2="235.0" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="231;231;231;328.44;328.44;328.44"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="549;549;549;451.56;451.56;451.56"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="235;235;235;335.21;335.21;335.21"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="235;235;235;335.21;335.21;335.21"/></line>
<line x1="207.5" y1="210.83" x2="572.5" y2="210.83" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="207.5;207.5;207.5;310.98;310.98;310.98"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="572.5;572.5;572.5;469.02;469.02;469.02"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="210.83;210.83;210.83;317.25;317.25;317.25"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="210.83;210.83;210.83;317.25;317.25;317.25"/></line>
<line x1="184.0" y1="186.67" x2="596.0" y2="186.67" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="184;184;184;287.81;287.81;287.81"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="596;596;596;492.19;492.19;492.19"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="186.67;186.67;186.67;293.42;293.42;293.42"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="186.67;186.67;186.67;293.42;293.42;293.42"/></line>
<line x1="160.5" y1="162.5" x2="619.5" y2="162.5" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="160.5;160.5;160.5;257.04;257.04;257.04"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="619.5;619.5;619.5;522.96;522.96;522.96"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="162.5;162.5;162.5;261.78;261.78;261.78"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="162.5;162.5;162.5;261.78;261.78;261.78"/></line>
<line x1="137.0" y1="138.33" x2="643.0" y2="138.33" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="137;137;137;216.2;216.2;216.2"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="643;643;643;563.8;563.8;563.8"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="138.33;138.33;138.33;219.78;219.78;219.78"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="138.33;138.33;138.33;219.78;219.78;219.78"/></line>
<line x1="113.5" y1="114.17" x2="666.5" y2="114.17" stroke="#64748b" stroke-width="2"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="113.5;113.5;113.5;161.98;161.98;161.98"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="666.5;666.5;666.5;618.02;618.02;618.02"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="114.17;114.17;114.17;164.02;164.02;164.02"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8400;1.0000" values="114.17;114.17;114.17;164.02;164.02;164.02"/></line>
<line x1="90.0" y1="90.0" x2="690.0" y2="90.0" stroke="#64748b" stroke-width="2"/>
<line x1="378.0" y1="380" x2="190.0" y2="90" stroke="#cbd5e1" stroke-width="1"/>
<line x1="384.0" y1="380" x2="290.0" y2="90" stroke="#cbd5e1" stroke-width="1"/>
<line x1="390.0" y1="380" x2="390.0" y2="90" stroke="#cbd5e1" stroke-width="1"/>
<line x1="396.0" y1="380" x2="490.0" y2="90" stroke="#cbd5e1" stroke-width="1"/>
<line x1="402.0" y1="380" x2="590.0" y2="90" stroke="#cbd5e1" stroke-width="1"/>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">奥行きを、等間隔に分けると:手前が粗すぎる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">手前を細かく、奥を粗くしていく…<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;0.5197;0.5200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">対数的に分けた froxel:近くが細かい（見た目に効率が良い）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5197;0.5200;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="424" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">画面の縦横に分け、奥行きに沿って分割した 3D のグリッド（上から見た断面）。各セルに、密度と光を持つ。</text>
</svg>

<!-- fig:froxel-slices:end -->

## froxel
<strong>froxel</strong>（frustum voxel）は、<strong>カメラの視錐台を画面の格子（X, Y）と奥行き（Z）で分割した 3D 格子</strong>です。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="froxel">
<text x="20" y="24" class="fig-title">froxel：視錐台を、画面に沿った 3D の格子に切る</text>
<polygon points="80,140 400,60 400,220" fill="#4c8bf5" fill-opacity="0.1" stroke="#4c8bf5" stroke-width="2"/>
<g stroke="currentColor" stroke-opacity="0.4">
<line x1="130" y1="127" x2="130" y2="153"/><line x1="190" y1="112" x2="190" y2="168"/><line x1="260" y1="95" x2="260" y2="185"/><line x1="340" y1="75" x2="340" y2="205"/><line x1="400" y1="60" x2="400" y2="220"/>
</g>
<circle cx="80" cy="140" r="6" fill="#e5484d"/><text x="60" y="164" style="font-size:12px">カメラ</text>
<text x="130" y="120" style="font-size:11px">近い：薄い</text><text x="320" y="62" style="font-size:11px">遠い：厚い</text>
<g transform="translate(470,50)">
<text x="0" y="0" style="font-size:12px;font-weight:700">画面方向の格子（幅×高さ）</text>
<g stroke="currentColor" stroke-opacity="0.4" fill="none"><rect x="0" y="14" width="240" height="135"/>
<line x1="60" y1="14" x2="60" y2="149"/><line x1="120" y1="14" x2="120" y2="149"/><line x1="180" y1="14" x2="180" y2="149"/>
<line x1="0" y1="48" x2="240" y2="48"/><line x1="0" y1="82" x2="240" y2="82"/><line x1="0" y1="116" x2="240" y2="116"/></g>
<rect x="120" y="48" width="60" height="34" fill="#e5aa28" fill-opacity="0.5"/>
<text x="0" y="176" style="font-size:12px">1 マス ＝ 画面の 8×8 ピクセルほど</text>
<text x="0" y="198" style="font-size:12px">奥行き方向に 64 枚ほどのスライス</text>
</g>
</svg>

| 項目 | 内容 |
| --- | --- |
| 解像度 | 160×90×64 程度（画面の 1/8 の解像度）。ピクセルを 1 つずつでなく、まとめて計算 |
| 形式 | 3D テクスチャ（`RGBA16F`：散乱光 RGB ＋ 密度） |
| 奥行きの割り当て | 近くを細かく（指数的）。`z = near * pow(far/near, slice/N)` |
| カメラに追従 | 視錐台と一緒に動く。画面の解像度に依存しない |

```hlsl
float SliceToDepth(float slice, float near_z, float far_z, float slice_count) {
  return near_z * pow(far_z / near_z, slice / slice_count);
}

float DepthToSlice(float depth, float near_z, float far_z, float slice_count) {
  return log(depth / near_z) / log(far_z / near_z) * slice_count;
}
```

### 奥行きの割り当ての理由

奥行き方向を指数的に割り当てるのは、画面上のセルの形を、なるべく正方形（立方体）に近づけるためです。画面の格子は、遠くへ行くほど、実際のワールド空間で大きくなります（透視投影）。奥行き方向を一様にすると、遠くのセルは「画面方向に広く、奥行き方向に薄い」平たい形になります。奥行きを遠くほど厚くすれば、セルの形が立方体に近くなり、どの距離でも均等な品質になります。

また、近くを細かくする理由は、近くのフォグの変化（光の筋の細かい構造など）は目につきやすい一方、遠くの変化は目につきにくいからです。たとえば、near が 0.1 m、far が 128 m（比率 1280）、64 スライスなら、最初のスライスは約 0.11 m、32 番目のスライスで約 3.6 m、最後が 128 m に達します。近くの数 m を、全体の半分のスライスで覆っていることになります。

### 3D テクスチャで持つ利点

3D テクスチャの形式で持つと、ハードウェアの三線形補間が使えます。ピクセルの位置 (u, v, スライス) で引くだけで、周囲 8 個のセルから自動で補間されます。また、コンピュート シェーダーでセルごとに並列に計算するのに向いています。

## froxel の、グリッドを、作る

<strong>froxel</strong> は、<strong>カメラの視錐台</strong>を、細かく分割した、3D グリッドです（frustum + voxel）。カメラから見た、画面の、横・縦と、奥行きで、セルを、並べます。ボクセル（立方体の、グリッド）と、違い、セルの、形が、遠いほど、大きい（視錐台は、遠くで、広がるため）。

```text
  カメラ ●
          ╲╲
           ╲ ╲      奥行き方向に、スライス（スライス = 奥行きの 1 段）
            ╲  ╲
             [z=0][z=1][z=2]...[z=63]
```

## 3D テクスチャで、持つ

<strong>3D テクスチャ</strong>に、<strong>各セルの、値</strong>を、書き込みます。

```cpp
// 160×90×64 の、3D テクスチャを、2 枚（散乱と、積分結果）作る。計算シェーダーが、書き込む。
D3D11_TEXTURE3D_DESC desc = {};
desc.Width = 160;
desc.Height = 90;
desc.Depth = 64;
desc.MipLevels = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;               // 散乱光（RGB）+ 消散（A）
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;   // 読む + 計算シェーダーで書く
device->CreateTexture3D(&desc, nullptr, &froxel_tex);
```

`R16G16B16A16_FLOAT` は、<strong>HDR の色</strong>（明るい光）を、<strong>収める</strong>ためです。`BIND_UNORDERED_ACCESS` は、計算シェーダーが、書き込むために、必要です。3D テクスチャの、1 つの値が、1 つの、froxelです。

## セル ↔ ワールド座標

<strong>セルの、番号</strong>から、<strong>ワールド位置</strong>を、求める変換が、すべての段階（密度、ライト、積分、適用）で、必要です。

```hlsl
// froxel の番号 (x, y, z) から、ワールド位置を求める。z は、スライス番号（小数も可）。
float3 FroxelToWorld(float3 froxel_id) {
  float2 uv = (froxel_id.xy + 0.5) / float2(160, 90);                    // 画面上の位置（0〜1）
  float view_depth = SliceToViewDepth(froxel_id.z / 64.0);              // スライス → カメラからの、奥行き（メートル）
  // 画面の位置と、奥行きから、ビュー空間の位置 → ワールド空間へ
  float2 ndc = uv * float2(2, -2) + float2(-1, 1);
  float3 view_pos = float3(ndc.x * view_depth / g_proj_x, ndc.y * view_depth / g_proj_y, -view_depth);   // 右手系: 前方が −Z
  return mul(float4(view_pos, 1.0), g_inv_view).xyz;
}
```

<strong>画面上の位置</strong>（`x`、`y`）と、<strong>奥行き</strong>（`z`）から、ビュー空間の位置を、作り、逆ビュー行列で、ワールドへ、戻します。奥行きの、割り当て（`SliceToViewDepth`）が、次の節です。

## 奥行きの、割り当て

<strong>奥行き方向</strong>は、<strong>均等に</strong>分割しません。近くは、細かく、遠くは、粗くします。近くの、霧の変化は、画面上で、大きく、遠くは、小さいためです。

```hlsl
// 奥行きの割り当て: 指数的に（近くを、細かく）。near から far まで、64 スライス。
float SliceToViewDepth(float slice01) {                                  // slice01: 0〜1
  // slice01 = 0 で near、1 で far。指数的に、広がる。
  return g_near * pow(g_far / g_near, slice01);
}
float ViewDepthToSlice(float view_depth) {
  return log(view_depth / g_near) / log(g_far / g_near);
}
```

<strong>対数</strong>（`log`）の、割り当てで、<strong>スライスの、厚さ</strong>が、距離に、比例します（近くは、薄く、遠くは、厚い）。画面上で、各スライスが、ほぼ、同じ、見た目の厚さに、なります。

| 割り当て | 内容 |
| --- | --- |
| 均等 | 簡単だが、近くが、粗く、縞が、目立つ |
| 指数（対数） | 近くを、細かく。標準 |
| べき乗（`slice²`） | 指数より、ゆるやか。近くを、細かく、簡単な、式 |

## 近・遠の、範囲

<strong>froxel</strong> は、<strong>カメラの、近くから、一定の、距離</strong>（数十〜数百メートル）までを、覆います。それより、遠くの、霧は、別の方法（高さフォグ、空気遠近法）で、補います。

| 範囲 | 方式 |
| --- | --- |
| 〜 64 m 〜 200 m（froxel の、範囲） | ボリューム フォグ |
| それより遠く | 空気遠近法（[Physically Based Aerial Perspective](../aerial-fog/physical.md)）、高さフォグ |

<strong>境目</strong>では、<strong>froxel の、最後のスライスの、値</strong>を、遠景の霧へ、フェードして、つなぎます。

## 解像度の、選び方

| 解像度 | セル数 | 品質 | コスト |
| --- | --- | --- | --- |
| 80×45×32 | 約 11 万 | 低（ぼやける、縞） | 最小 |
| 160×90×64 | 約 92 万 | 標準 | 中 |
| 320×180×128 | 約 740 万 | 高（細かい光の筋） | 重い |

<strong>画面の、解像度</strong>（1920×1080）の、<strong>1/12</strong>（160×90）が、標準的です。霧は、ゆるやかに変化するので、低解像度でも、十分です。時間方向の、平均（[Temporal Accumulation](temporal.md)）で、品質を、補います。

## よくあるミス

??? failure "奥行きの分割が粗く、層状の縞が見える"
    <strong>スライス数を増やす</strong>・<strong>ジッタ</strong>を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 視錐台を分けた、3D のグリッド

## 参考

- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Microsoft Learn, "D3D11_TEXTURE3D_DESC"（3D テクスチャ、`D3D11_BIND_UNORDERED_ACCESS`）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Volumetric Fog](index.md)
- [Step 1: Density](density.md)

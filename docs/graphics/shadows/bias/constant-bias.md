---
title: Constant Bias
tags:
  - 描画
---

# Constant Bias

シャドウ マップを初めて実装すると、地面や物の表面に縞模様の影が出ることがあります。自分の面に自分の影が落ちている（シャドウ アクネ）のです。この縞を消す最も簡単な方法が、比較する深度から一定の値を引くことです。1 行で書けて最初に試すべき方法ですが、面の傾きが大きいと足りず傾きの小さい面では大きすぎて影が浮いてしまうので、単独では不十分です。

<strong>定数バイアスは画素の深度から一定の値を引いてから、シャドウ マップと比べます</strong>。このページではなぜ必要になるかシェーダーで引く方法とハードウェアの `DepthBias`、射影の種類による効き方の違い値の決め方（ワールドの距離からの換算）、限界を説明します。

!!! tip "ポイント"
    - 定数バイアスは比較する深度に一定の値を足す（引く）ことです。例は 0.001 です。
    - 面の傾きに関係なく同じ値なので、斜めの面ではアクネ、正面では浮きが出ます。
    - 正射影（太陽）では深度が線形なので、値が扱いやすいです。透視投影では遠くで大きくなりすぎます。
    - 値はワールドの距離（例: 5 cm）から、深度の単位へ換算して決めると、シーンが変わっても直感を保てます。
    - 他の方式（傾き依存、法線オフセット）と組み合わせる前提で使います。

!!! info "このページを読む前に"
    - [Shadow Bias](index.md)（このセクション全体の地図と読む順番）

## なぜバイアスが要るのか {#why}

シャドウ マップは光から見た最も手前の面の深度をテクセルごとに 1 つだけ保存します。ところが、1 つのテクセルは実際の面の上ではある広がりを持ちます。面が光に対して傾いているとテクセルの端と端で、面の深度は違います。1 つの値で代表するとテクセルの範囲のうち半分の点は、本来の深度より奥の値を持ちます。その点を画素の本来の深度と比べると、画素の方が奥になって影と判定されます。

さらに、深度は有限のビット数で保存されるので、量子化の誤差もあります。このずれを吸収するために比較の前に画素の深度を少し手前へ動かします。これがバイアスです。

<!-- fig:bias-needed:begin -->

<svg class="fig illust motion" data-fig="bias-needed" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bias-needed" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">必要なバイアスは、面が斜めなほど増える。一定のバイアスでは足りない</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">必要なバイアス（シャドウ マップの 1 テクセル単位）</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">光と面の法線の角度 (度)</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="230.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">20</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">40</text>
<text x="550.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">60</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">80</text>
<path d="M70.0,270.0 L80.67,270.0 L91.33,270.0 L102.0,270.0 L112.67,270.0 L123.33,270.0 L134.0,270.0 L144.67,270.0 L155.33,270.0 L166.0,270.0 L176.67,270.0 L187.33,270.0 L198.0,270.0 L208.67,270.0 L219.33,270.0 L230.0,270.0 L240.67,270.0 L251.33,270.0 L262.0,270.0 L272.67,270.0 L283.33,270.0 L294.0,270.0 L304.67,270.0 L315.33,270.0 L326.0,270.0 L336.67,270.0 L347.33,270.0 L358.0,270.0 L368.67,270.0 L379.33,270.0 L390.0,270.0 L400.67,270.0 L411.33,270.0 L422.0,270.0 L432.67,270.0 L443.33,270.0 L454.0,270.0 L464.67,270.0 L475.33,270.0 L486.0,270.0 L496.67,270.0 L507.33,270.0 L518.0,270.0 L528.67,270.0 L539.33,270.0 L550.0,270.0 L560.67,270.0 L571.33,270.0 L582.0,270.0 L592.67,270.0 L603.33,270.0 L614.0,270.0 L624.67,270.0 L635.33,270.0 L646.0,270.0 L656.67,270.0 L667.33,270.0 L678.0,270.0 L688.67,270.0 L699.33,270.0 L710.0,270.0" fill="none" stroke="#64748b" stroke-width="3" opacity="1" stroke-dasharray="6 5"/>
<text x="598.0" y="260.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">一定のバイアス = 1</text>
<path d="M70.0,310.0 L76.4,309.44 L82.8,308.88 L89.2,308.32 L95.6,307.76 L102.0,307.2 L108.4,306.64 L114.8,306.08 L121.2,305.51 L127.6,304.95 L134.0,304.38 L140.4,303.81 L146.8,303.23 L153.2,302.66 L159.6,302.08 L166.0,301.5 L172.4,300.91 L178.8,300.32 L185.2,299.73 L191.6,299.13 L198.0,298.53 L204.4,297.92 L210.8,297.31 L217.2,296.69 L223.6,296.07 L230.0,295.44 L236.4,294.81 L242.8,294.16 L249.2,293.51 L255.6,292.86 L262.0,292.19 L268.4,291.52 L274.8,290.84 L281.2,290.14 L287.6,289.44 L294.0,288.73 L300.4,288.01 L306.8,287.28 L313.2,286.53 L319.6,285.78 L326.0,285.01 L332.4,284.22 L338.8,283.42 L345.2,282.61 L351.6,281.78 L358.0,280.94 L364.4,280.08 L370.8,279.2 L377.2,278.3 L383.6,277.38 L390.0,276.44 L396.4,275.47 L402.8,274.49 L409.2,273.47 L415.6,272.44 L422.0,271.37 L428.4,270.28 L434.8,269.15 L441.2,268.0 L447.6,266.8 L454.0,265.58 L460.4,264.31 L466.8,263.0 L473.2,261.65 L479.6,260.25 L486.0,258.8 L492.4,257.3 L498.8,255.75 L505.2,254.13 L511.6,252.45 L518.0,250.7 L524.4,248.87 L530.8,246.97 L537.2,244.98 L543.6,242.9 L550.0,240.72 L556.4,238.43 L562.8,236.02 L569.2,233.49 L575.6,230.81 L582.0,227.99 L588.4,225.0 L594.8,221.82 L601.2,218.44 L607.6,214.84 L614.0,211.0 L620.4,206.87 L626.8,202.44 L633.2,197.67 L639.6,192.5 L646.0,186.89 L652.4,180.78 L658.8,174.09 L665.2,166.74 L671.6,158.61 L678.0,149.57 L684.4,139.46 L690.8,128.07 L697.2,115.14 L703.6,100.31 L710.0,83.15" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<text x="486.0" y="246.8" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">必要な量 = tan θ</text>
<circle cx="70.0" cy="310.0" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0913;0.1027;0.1140;0.1253;0.1367;0.1480;0.1593;0.1707;0.1820;0.1933;0.2047;0.2160;0.2273;0.2387;0.2500;0.2613;0.2727;0.2840;0.2953;0.3067;0.3180;0.3293;0.3407;0.3520;0.3633;0.3747;0.3860;0.3973;0.4087;0.4200;0.4313;0.4427;0.4540;0.4653;0.4767;0.4880;0.4993;0.5107;0.5220;0.5333;0.5447;0.5560;0.5673;0.5787;0.5900;0.6013;0.6127;0.6240;0.6353;0.6467;0.6580;0.6693;0.6807;0.6920;0.7033;0.7147;0.7260;0.7373;0.7487;0.7600;1.0000" values="70;70;80.4;90.8;101.2;111.6;122;132.4;142.8;153.2;163.6;174;184.4;194.8;205.2;215.6;226;236.4;246.8;257.2;267.6;278;288.4;298.8;309.2;319.6;330;340.4;350.8;361.2;371.6;382;392.4;402.8;413.2;423.6;434;444.4;454.8;465.2;475.6;486;496.4;506.8;517.2;527.6;538;548.4;558.8;569.2;579.6;590;600.4;610.8;621.2;631.6;642;652.4;662.8;673.2;683.6;694;694"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0913;0.1027;0.1140;0.1253;0.1367;0.1480;0.1593;0.1707;0.1820;0.1933;0.2047;0.2160;0.2273;0.2387;0.2500;0.2613;0.2727;0.2840;0.2953;0.3067;0.3180;0.3293;0.3407;0.3520;0.3633;0.3747;0.3860;0.3973;0.4087;0.4200;0.4313;0.4427;0.4540;0.4653;0.4767;0.4880;0.4993;0.5107;0.5220;0.5333;0.5447;0.5560;0.5673;0.5787;0.5900;0.6013;0.6127;0.6240;0.6353;0.6467;0.6580;0.6693;0.6807;0.6920;0.7033;0.7147;0.7260;0.7373;0.7487;0.7600;1.0000" values="310;310;309.09;308.18;307.27;306.36;305.44;304.52;303.59;302.66;301.72;300.77;299.8;298.83;297.85;296.85;295.84;294.81;293.76;292.69;291.6;290.49;289.35;288.19;287;285.78;284.52;283.22;281.89;280.51;279.08;277.61;276.08;274.49;272.83;271.1;269.3;267.4;265.42;263.33;261.13;258.8;256.34;253.71;250.92;247.93;244.73;241.27;237.54;233.49;229.07;224.22;218.88;212.95;206.34;198.9;190.45;180.78;169.58;156.44;140.79;121.81;121.81"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が真上から: 必要なバイアスはほぼ 0<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2497;0.2500;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">45 度: ちょうど 1 テクセル(一定の 1 と交わる)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2497;0.2500;0.4197;0.4200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">60 度: 1.7 テクセル必要 → 足りない所に縞(アクネ)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4197;0.4200;0.5897;0.5900;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">浅い角度: 数テクセル必要。大きくすると影が離れる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5897;0.5900;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:bias-needed:end -->

## シェーダーで引く {#shader}

最も素直な方法は比較する深度から直接、定数を引くことです。

```hlsl
Texture2D<float> g_shadow_map : register(t0);
SamplerComparisonState g_shadow_sampler : register(s0);

cbuffer ShadowConstants : register(b0) {
  float4x4 g_world_to_light;
  float g_constant_bias;     // 正規化深度（0..1）での値。例: 0.001
  float3 _pad;
};

float ShadowConstantBias(float3 world_pos) {
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);
  // 比較する深度から定数を引く。比較は「画素の深度 <= テクセルの深度」で、1 = 光が当たる
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z - g_constant_bias);
}

float4 ConstantBiasPS(float3 world_pos : TEXCOORD0) : SV_Target {
  float lit = ShadowConstantBias(world_pos);
  return float4(lit, lit, lit, 1.0);
}
```

値の単位は正規化された深度（0〜1）です。射影の種類によって同じ値の意味が変わります。

正射影（太陽）では深度が線形です。バイアス 0.001 は深度の範囲（`light_far − light_near`）の 0.1 % の距離に相当します。範囲が 100 m なら 10 cm です。ワールドの距離で考えやすいのが利点です。

透視投影（スポットライト、点光源）では深度が非線形です。近くの精度が高く遠くが粗いので、同じ値でも近くと遠くでワールドの距離が違います。標準の深度を `d = far/(far − near) · (1 − near/z)` とすると `d` の `z` での微分は `far · near / ((far − near) · z²)` です。深度が `b` だけずれたときの視点距離 `Δz` は、`Δz = b · (far − near) · z² / (far · near)` です。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="透視投影で、深度バイアス 0.0001 のワールドでの大きさ。距離の 2 乗で大きくなる"><text x="14" y="22" class="fig-title">透視投影: 同じバイアス 0.0001 が、距離でこれだけ変わる</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/><line x1="60" y1="200" x2="60" y2="40" stroke="currentColor" stroke-width="1.5"/>
<g fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"><rect x="100" y="199" width="80" height="1"/><rect x="240" y="196" width="80" height="4"/><rect x="380" y="180" width="80" height="20"/><rect x="520" y="50" width="80" height="150" fill="rgba(229,72,77,0.25)" stroke="#e5484d"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="140" y="192">0.001 m</text><text x="280" y="190">0.01 m</text><text x="420" y="174">0.1 m</text><text x="560" y="44">2.5 m</text>
<text x="140" y="220">1 m</text><text x="280" y="220">3 m</text><text x="420" y="220">10 m</text><text x="560" y="220">50 m</text></g>
<text x="360" y="244" text-anchor="middle" style="font-size:12px">near = 0.1、far = 100。距離 z の 2 乗に比例する。遠くでは影が 2.5 m も浮く（縦軸は途中を縮めてある）</text></svg>

`near = 0.1`、`far = 100` で `b = 10⁻⁴` なら `z = 1 m` で約 0.001 m、`z = 10 m` で約 0.1 m、`z = 50 m` で約 2.5 m です。近くの影に合わせた値が遠くでは影を 2.5 m も浮かせます。透視投影では定数のバイアスは使いにくいのです。

## ハードウェアの深度バイアス {#hw}

シャドウ パスで深度を書き込むときに書く値へバイアスを足す方法もあります。ラスタライザー ステートの `DepthBias` です。

```cpp
// （コンパイルしていない）
D3D11_RASTERIZER_DESC rs = {};
rs.DepthBias = 8000;                  // 整数。最小の深度の刻み × この値
rs.DepthBiasClamp = 0.0f;
rs.SlopeScaledDepthBias = 0.0f;       // 傾き依存は、別のページ（Slope-Scale Bias）
device->CreateRasterizerState(&rs, &shadow_pass_rs);
```

深度の形式によって 1 単位の大きさが違います。

- 24 ビット固定小数点（`D24_UNORM`）では、バイアスは `DepthBias × r` で `r` は表現できる最小の正の値、つまり `1 / 2²⁴ ≒ 6 × 10⁻⁸` です。
- 32 ビット浮動小数点（`D32_FLOAT`）では、バイアスは `DepthBias × 2^(e − 23)` で `e` はプリミティブの最大の深度の指数です。深度によって刻みが違います。

`D32_FLOAT` では `DepthBias` の効きが深度の大きさに依存します。近くではごく小さく遠くでは大きく効きます。固定小数点のほうが一定で扱いやすいです。通常は、シェーダーで引く方式のほうが、値の意味がはっきりしています。

## 値の決め方 {#value}

ワールドの距離でバイアスを指定すると、直感的です。深度の範囲に換算します。

```hlsl
// 正射影: ワールドの距離（メートル）から、正規化深度のバイアスへ
float BiasFromWorldDistanceOrtho(float bias_world_meters, float light_near, float light_far) {
  return bias_world_meters / (light_far - light_near);
}

// 透視投影: 視点距離 z（メートル）でのバイアスを、正規化深度へ（z² に比例して大きくなるのを逆算）
float BiasForPerspective(float bias_world_meters, float z, float light_near, float light_far) {
  return bias_world_meters * light_far * light_near / ((light_far - light_near) * z * z);
}

// テクセルの大きさに比例させる: シャドウ マップの 1 テクセルがワールドで何メートルか
// 面の傾きで必要量が変わるが、基準としては、テクセルの 1〜2 倍が目安（一例）
float BiasFromTexelSize(float extent_meters, float resolution, float k) {
  float texel_world = extent_meters / resolution;
  return k * texel_world;
}
```

`DepthBias` の整数に直すには 24 ビット固定小数点なら正規化深度のバイアスを `2⁻²⁴` で割ります。範囲 100 m の正射影で、ワールドで 5 cm のバイアスなら正規化で `0.05 / 100 = 5 × 10⁻⁴` で、`DepthBias = 5 × 10⁻⁴ / 5.96 × 10⁻⁸ ≒ 8400` です。「数百〜数千」という目安は範囲が小さい（数十 m 以下）カスケードの場合です。

カスケードシャドウではカスケードごとに 1 テクセルの大きさが違います。遠いカスケードはシャドウ マップの 1 画素が大きいので、バイアスも大きく取ります。

```cpp
// （コンパイルしていない）カスケードごとにバイアスをスケールする（遠いカスケードほど大きく）
float BiasForCascade(float base_bias, float cascade_range, float cascade0_range) {
  return base_bias * (cascade_range / cascade0_range);
}
```

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で、`ShadowConstantBias` を使うピクセル シェーダーとバイアスの換算関数をコンパイルして、エラーが出ないことを確かめました。換算の数字は式からの手計算です。GPU での描画は確認していません。

## 定数バイアスの限界 {#limits}

定数バイアスだけでは面が光に対して斜めになるほど足りなくなります。光に正面（垂直）の面は必要なバイアスが小さく、斜め（45°）で中くらいほぼ平行（80° 以上）で大きくなります。定数ではどれかに合わせるとほかで破綻します。

- 正面の面に合わせて小さくすると、斜めの面でシャドウ アクネが出ます。
- 斜めの面に合わせて大きくすると、正面の面で影が浮いてピーター パンニングが出ます。

そこで、面の傾きに応じて変える傾き依存のバイアスが必要になります（[Slope-Scale Bias](slope-scale-bias.md)）。

## よくあるミス {#mistakes}

??? failure "斜めの面ではアクネが消えずバイアスを上げると正面が浮く"
    原因は定数だけで両立しようとしていることです。傾きに比例するバイアス（スロープ スケール）か法線に沿って位置をずらす法線オフセットを併用します。

??? failure "近くの影はよいのに、遠くで影が物から大きく浮く"
    原因は透視投影の深度が非線形なのに、定数を使っていることです。バイアスは距離の 2 乗に比例して、ワールドで大きくなります。視点距離からバイアスを換算するか正射影のシャドウ マップ（太陽）に限って定数を使います。

??? failure "`DepthBias` を同じ値にしたのに、深度の形式を変えたら影が変わった"
    原因は `D24_UNORM` と `D32_FLOAT` で、`DepthBias` の 1 単位の大きさが違うことです。深度の形式を変えたら値を計算し直します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 定数バイアスは比較する深度から一定の値を引きます。
    - [x] 正射影ならワールドの距離から換算して決めます。透視投影では距離の 2 乗で大きくなるので使いにくいです。
    - [x] 単独では斜めの面と正面の面を両立できません。傾き依存のバイアスと併用します。

## 参考 {#references}

このページは次の資料を読まずに書きました。透視投影のバイアスの式は深度の式を微分して自分で導きました。`DepthBias` の式は Direct3D の一般的な説明に基づく記述で、仕様の原文では確かめていません。

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978（シャドウ マップの原典）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）
- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）

## 関連ページ

- [Shadow Bias](index.md)
- [Slope-Scale Bias](slope-scale-bias.md)
- [Peter Panning](peter-panning.md)

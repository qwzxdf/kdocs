---
title: Fighting Noise
tags:
  - 描画
---

# Fighting Noise

<strong>画素あたり 1〜2 本のレイでは、間接光はノイズだらけ</strong>です。このノイズを時間蓄積と空間フィルタで消すのがデノイズです。このページではノイズの原因と、デノイズの方針を説明します。

!!! tip "ポイント"
    - ノイズの原因 ＝ サンプル数が少ない。
    - 時間蓄積：前フレームの結果と混ぜる。
    - 空間フィルタ：法線・深度が近い画素だけ平均。
    - ゴーストとぼやけが、トレードオフ。

!!! info "このページを読む前に"
    - [Ray-Traced GI](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ノイズとの戦い
<strong>画素あたり 1 本</strong>のレイでは、ノイズが多いです。

### 重要度サンプリング

サンプル数が足りないなら 寄与の大きい方向に、サンプルを多く割り当てるのが、ノイズを減らす王道です。これを重要度サンプリングと呼びます。

基本は余弦重み付きです。BRDF の余弦に従って方向を選べば、斜めの方向（寄与の小さい方向）にレイを無駄遣いしません。次に、NEE（Next Event Estimation）があります。レイがヒットした点でライトを直接サンプルして（シャドウ レイを光源に向けて飛ばす）、直接光を確実に拾う方法です。レイが偶然、小さな光源に当たるのを待つのでなく、光源を狙って飛ばすのでノイズが激減します。さらに、サンプルの並べ方にも工夫が使えます。ブルー ノイズを乱数として使うと、隣り合う画素のサンプルが偏らず、画面全体で誤差が均されます（[Noise Patterns](../../ao/filtering/noise-pattern.md)）。

### デノイズ

重要度サンプリングを使っても、1 画素 1 本のレイでは足りません。ノイズは後処理のデノイザで消します。主な手法は段階的に発展してきました。

最も基本の技術は時間蓄積です。前のフレームの結果を動きベクトルで再投影し、今のフレームと混ぜます（[Temporal Accumulation](../../ao/filtering/temporal.md)）。次に空間フィルタで法線と深度を手がかりに、同じ面の画素だけを平均してぼかします。この 2 つを組み合わせさらに「ノイズの大きさ（分散）」を推定して、ノイズが多い画素ほど強くぼかす方式が、SVGF（Spatiotemporal Variance-Guided Filtering、Schied ら 2017）です。分散ガイドのおかげで静止した部分はシャープに、ノイズの多い部分は大きくぼかす、という切り替えが自動でできます。

実用的な製品としては NVIDIA の NRD（ReBLUR・ReLAX）、AMD の FidelityFX Denoiser があります。オフライン向けの OIDN（Intel Open Image Denoise）は、ニューラル ネットワークでデノイズします。最近は DLSS Ray Reconstruction のように、ニューラル ネットワークでデノイズとアップスケールを同時に行う方式も出ています。

### ゴーストとぼやけのトレードオフ

デノイズではゴースト（残像）とぼやけの間で、取引が避けられません。履歴を強く使うとノイズは減りますが、動きに対して残像が出ます。履歴を弱くすると残像は減りますが、ノイズが残ります。履歴の妥当性を法線・深度・輝度の差で検証して、怪しい履歴は捨てるという工夫が不可欠です（[Temporal Accumulation](../../ao/filtering/temporal.md)）。

<!-- fig:mc-noise-samples:begin -->

<svg class="fig illust motion" data-fig="mc-noise-samples" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-mc-noise-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ノイズはサンプル数の平方根に反比例: 4 倍の本数で、ノイズは半分</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ノイズの大きさ 1/√N</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">1 ピクセルあたりのサンプル数 N</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<text x="198.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<text x="326.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">16</text>
<text x="454.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">64</text>
<text x="582.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">256</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1024</text>
<path d="M70.0,81.43 L76.4,89.21 L82.8,96.74 L89.2,104.0 L95.6,111.02 L102.0,117.8 L108.4,124.34 L114.8,130.67 L121.2,136.78 L127.6,142.68 L134.0,148.38 L140.4,153.88 L146.8,159.2 L153.2,164.34 L159.6,169.3 L166.0,174.09 L172.4,178.72 L178.8,183.19 L185.2,187.51 L191.6,191.68 L198.0,195.71 L204.4,199.61 L210.8,203.37 L217.2,207.0 L223.6,210.51 L230.0,213.9 L236.4,217.17 L242.8,220.33 L249.2,223.39 L255.6,226.34 L262.0,229.19 L268.4,231.94 L274.8,234.6 L281.2,237.17 L287.6,239.65 L294.0,242.05 L300.4,244.36 L306.8,246.6 L313.2,248.76 L319.6,250.84 L326.0,252.86 L332.4,254.8 L338.8,256.68 L345.2,258.5 L351.6,260.25 L358.0,261.95 L364.4,263.59 L370.8,265.17 L377.2,266.69 L383.6,268.17 L390.0,269.59 L396.4,270.97 L402.8,272.3 L409.2,273.58 L415.6,274.82 L422.0,276.02 L428.4,277.18 L434.8,278.3 L441.2,279.38 L447.6,280.42 L454.0,281.43 L460.4,282.4 L466.8,283.34 L473.2,284.25 L479.6,285.13 L486.0,285.97 L492.4,286.79 L498.8,287.58 L505.2,288.35 L511.6,289.08 L518.0,289.8 L524.4,290.49 L530.8,291.15 L537.2,291.79 L543.6,292.41 L550.0,293.01 L556.4,293.59 L562.8,294.15 L569.2,294.69 L575.6,295.21 L582.0,295.71 L588.4,296.2 L594.8,296.67 L601.2,297.12 L607.6,297.56 L614.0,297.99 L620.4,298.4 L626.8,298.79 L633.2,299.17 L639.6,299.54 L646.0,299.9 L652.4,300.24 L658.8,300.57 L665.2,300.9 L671.6,301.21 L678.0,301.51 L684.4,301.8 L690.8,302.07 L697.2,302.34 L703.6,302.61 L710.0,302.86" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<circle cx="70.0" cy="81.43" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="70;70;80.67;91.33;102;112.67;123.33;134;144.67;155.33;166;176.67;187.33;198;208.67;219.33;230;240.67;251.33;262;272.67;283.33;294;304.67;315.33;326;336.67;347.33;358;368.67;379.33;390;400.67;411.33;422;432.67;443.33;454;464.67;475.33;486;496.67;507.33;518;528.67;539.33;550;560.67;571.33;582;592.67;603.33;614;624.67;635.33;646;656.67;667.33;678;688.67;699.33;710;710"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="81.43;81.43;94.26;106.37;117.8;128.58;138.76;148.38;157.45;166.01;174.09;181.72;188.92;195.71;202.13;208.18;213.9;219.29;224.38;229.19;233.72;238;242.05;245.86;249.46;252.86;256.06;259.09;261.95;264.65;267.19;269.59;271.86;274;276.02;277.93;279.73;281.43;283.03;284.55;285.97;287.32;288.6;289.8;290.93;292;293.01;293.96;294.86;295.71;296.52;297.27;297.99;298.66;299.3;299.9;300.47;301;301.51;301.98;302.43;302.86;302.86"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1〜4 本: ノイズ 1 → 0.5<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2237;0.2240;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4〜16 本: 0.5 → 0.25<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2237;0.2240;0.3677;0.3680;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">16〜64 本: 0.25 → 0.13<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3677;0.3680;0.5117;0.5120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">64〜256 本: 0.13 → 0.06<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5117;0.5120;0.6557;0.6560;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">256〜1024 本: 0.06 → 0.03。ここまで増やしても 1/32<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6557;0.6560;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:mc-noise-samples:end -->

## レイを 1 本しか飛ばせない

<strong>リアルタイム</strong>の レイトレーシング GI では、1 画素あたり 1 本（多くて、数本）のレイしか飛ばせません。1 本のレイの結果はノイズが、大きい（ある画素は明るい壁に当たり隣は暗い影に、当たる）。ノイズを取り除く（デノイズ）ことが、リアルタイム GI のほぼすべてと、言っても過言ではありません。

## デノイズの基本方針

<strong>同じ場所の複数のサンプル</strong>を、集めて平均することでノイズを、減らします。集める方法は 2 つあります。

| 方法 | 内容 |
| --- | --- |
| 時間方向（時間蓄積） | 前のフレームの、同じ場所の結果を混ぜる。数十フレーム分のサンプルが集まる |
| 空間方向（空間フィルタ） | 隣の画素を、混ぜる（ぼかす）。法線・深度が近い画素だけ（エッジを、保つ） |

両方を組み合わせたのが SVGF（Schied ら、2017）に代表される時空間フィルタです。

## ① 時間蓄積

<strong>前のフレームの結果</strong>を 再投影（カメラの動きを、補正して前の画面の位置を求める）して、今フレームと混ぜます。

```hlsl
// 今フレームの、ノイジーな、結果と、前フレームの、蓄積済みの結果を、混ぜる（指数移動平均）。
float2 prev_uv = Reproject(position_world, g_prev_view_proj);            // 前フレームの、画面上の位置
float4 history = g_history.SampleLevel(g_linear_clamp, prev_uv, 0);       // rgb = 前の結果、a = 蓄積した、サンプル数

// 履歴が、有効か（物が、動いて、別の面を、見ていないか）を、法線・深度で、確かめる。
bool valid = all(prev_uv >= 0.0) && all(prev_uv <= 1.0)
          && abs(history_depth - current_depth) < depth_threshold
          && dot(history_normal, current_normal) > 0.9;
float sample_count = valid ? min(history.a + 1.0, 32.0) : 1.0;             // 有効なら、増やす（上限 32）。無効なら、リセット
float alpha = 1.0 / sample_count;                                           // サンプルが、多いほど、今フレームの、影響が、小さい
float3 blended = lerp(history.rgb, current_gi, alpha);
g_history_out[pixel] = float4(blended, sample_count);
```

蓄積したサンプル数を 覚えておき、混ぜる割合を `1 / サンプル数`にするとちょうど、平均（全サンプルの単純平均）に、なります。上限（32）を設けて古い履歴の影響を、薄れさせ光の変化に追従します。

### 履歴のリジェクト（拒否）

カメラ・物が動くと 前のフレームの、同じ画素が別の面になることがあります。履歴をそのまま使うとゴースト（残像）が、出ます。

| 判定 | 内容 |
| --- | --- |
| 画面の外 | 前のフレームの位置が、画面の外 → 履歴を捨てる |
| 深度の違い | 前と今の深度が、大きく違う → 別の物（遮蔽が、解除された） → 捨てる |
| 法線の違い | 法線が大きく違う → 別の面 → 捨てる |
| 物の ID（任意） | 動く物の、ID が違う → 捨てる |

履歴を捨てた画素は サンプル数が、1 に戻りノイズが目立ちます（数フレームでまた、蓄積される）。空間フィルタがその間のノイズを、隠します。

## ② 空間フィルタ：エッジを保つぼかし

<strong>隣の画素</strong>を 混ぜて、ノイズをぼかします。ただし、物のエッジ（法線・深度が違う画素）を越えて、混ぜるとにじむのでエッジで止める、バイラテラル フィルタ（[Bilateral Blur](../../ao/filtering/bilateral-blur.md)）を、使います。

### À-Trous ウェーブレット フィルタ

SVGF は À-Trous（「穴あき」）ウェーブレット フィルタを、使います。同じ小さな 5×5 のカーネルを間隔を、広げながら（1、2、4、8、16 画素おき）、複数回、適用します。少ない読み込みで広い範囲をぼかせます。

```hlsl
// À-Trous フィルタの 1 回（step: 画素の間隔。1, 2, 4, 8, 16 と、繰り返す）。
float3 ATrous(uint2 pixel, int step_size, float3 center_color, float3 center_normal, float center_depth, float sigma_l) {
  const float kKernel[3] = { 1.0, 2.0 / 3.0, 1.0 / 6.0 };               // 5 タップの、B スプライン カーネル
  float3 sum = 0.0;
  float weight_sum = 0.0;
  for (int dy = -2; dy <= 2; ++dy)
    for (int dx = -2; dx <= 2; ++dx) {
      uint2 q = pixel + int2(dx, dy) * step_size;                         // 間隔を、空けて、読む
      float3 color = g_color[q];
      float3 normal = g_normal[q];
      float depth = g_depth[q];

      // 3 つのエッジ停止関数: 法線、深度、輝度（色）が、近いほど、重みが大きい。
      float w_normal = pow(saturate(dot(center_normal, normal)), g_sigma_normal);
      float w_depth = exp(-abs(center_depth - depth) / (g_sigma_depth * length(float2(dx, dy)) * step_size + 1e-4));
      float w_lum = exp(-abs(Luminance(center_color) - Luminance(color)) / sigma_l);
      float w = kKernel[abs(dx)] * kKernel[abs(dy)] * w_normal * w_depth * w_lum;
      sum += color * w;
      weight_sum += w;
    }
  return sum / max(weight_sum, 1e-4);
}
```

5×5 の 25 タップを、間隔を広げて、5 回（1、2、4、8、16）、適用すると約 `(5 × 2⁴)` = 80 画素の幅を、ぼかせます（25 × 5 = 125 回の読み込みで）。普通の、大きなカーネル（81×81 = 6,561 回）より、はるかに少ないです。3 つのエッジ停止（法線、深度、輝度）がエッジを保ちます。

### 分散でフィルタの強さを、決める（SVGF の核心）

SVGF は 画素ごとの、分散（ノイズの大きさ）を推定し、ノイズが大きい画素ほど強くぼかします。

```hlsl
// 時間蓄積で、輝度の、平均と、2 乗の平均を、持つ → 分散 = E[x²] − E[x]²。
float variance = max(0.0, moments.y - moments.x * moments.x);
float sigma_l = g_sigma_luminance * sqrt(variance) + 1e-4;               // 分散が、大きい → 輝度の差を、許す（強く、ぼかす）
```

ノイズが大きい（分散が大きい）画素は、輝度の差をより許して、強くぼかしノイズが小さい画素は、弱くぼかして細部を保ちます。

## ③ ノイズを減らす工夫（入力側）

<strong>デノイザーに渡す前</strong>に 入力の、ノイズを減らす工夫も効果的です。

| 工夫 | 内容 |
| --- | --- |
| ブルー ノイズの乱数 | サンプル方向を、ブルー ノイズで選ぶ。ノイズの粒が均一でフィルタが、効きやすい（[Monte Carlo Integration](../theory/monte-carlo.md)） |
| 低食い違い量列 | Halton、Sobol、R2 など。偏りの少ないサンプル |
| 余弦重み・重点サンプリング | 寄与の、大きい方向を多めに（[Monte Carlo Integration](../theory/monte-carlo.md)） |
| 明るすぎるサンプルを切る（ファイアフライ対策） | 明るい光源に偶然、当たったサンプルが白い点（ファイアフライ）になる。上限でクランプ |
| 半分の解像度でレイ | 画素の半分にだけレイを飛ばし、アップサンプル |

```hlsl
// ファイアフライ対策: 1 サンプルの、明るさに、上限を、設ける。
float lum = Luminance(radiance);
radiance *= min(1.0, g_max_radiance / max(lum, 1e-4));                    // 上限を超えたら、比率で、下げる
```

## デノイズの限界

| 問題 | 内容 |
| --- | --- |
| ぼやけ | 強くぼかすと細かい、陰影（接触の影）が失われる |
| ゴースト・遅れ | 時間蓄積が、光の変化に遅れる（ライトが動いた、数フレーム後に反映） |
| 動く物のノイズ | 履歴を、捨てるので動く物の周りがノイズだらけになる |
| ちらつき | デノイザーの判断が、フレームごとに揺れる |

<strong>ノイズとぼやけ・遅れ</strong>は トレード オフです。ReSTIR（[ReSTIR GI](restir.md)）は入力の質を、上げることでデノイザーの負担を、減らします。

## よくあるミス

??? failure "動く光で、間接光が遅れて追いかけてくる"
    <strong>ブレンド率を上げる</strong>・履歴を拒否する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時間蓄積と空間フィルタで、ノイズを消す

## 参考

- Schied, Kaplanyan, Wyman, Patney, Chaitanya, Burgess, Liu, Dachsbacher, Lefohn, Salvi, "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017（SVGF）
- Schied, Peters, Dachsbacher, "Gradient Estimation for Real-Time Adaptive Temporal Filtering", High-Performance Graphics 2018（A-SVGF）
- Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018（SEED のハイブリッド レイトレーシング）
- Dammertz, Sewtz, Hanika, Lensch, "Edge-Avoiding À-Trous Wavelet Transform for Fast Global Illumination Filtering", High Performance Graphics 2010（À-Trous フィルタ）

## 関連ページ

- [Ray-Traced GI](index.md)
- [ReSTIR GI](restir.md)
- [AO Filtering](../../ao/filtering/index.md)

---
title: Soft Particles
tags:
  - 描画
---

# Soft Particles

<strong>パーティクルが地面や壁と交差する所で、硬い線が見えて不自然</strong>になります。<strong>シーンの深度を読んで近いほどアルファを弱める「ソフト パーティクル」</strong>で、なめらかに消せます。このページではソフト パーティクルの仕組みを説明します。

!!! tip "ポイント"
    - パーティクルの深度と、シーンの深度の差を求める。
    - 差が小さい（交差に近い）ほど、アルファを弱める。
    - 深度バッファをテクスチャとして読む必要がある。
    - 煙・炎・霧のパーティクルで、効果が大きい。

<!-- fig:soft-particles-depth:begin -->

<svg class="fig illust motion" data-fig="soft-particles-depth" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-soft-particles-depth" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ソフト パーティクル:地面に近い部分ほど、薄くして、交差の線を消す</text>
<rect x="40" y="250" width="700" height="14" fill="#d6c7a1"/>
<polygon points="260,90 300,90 520,250 480,250" fill="#94a3b8" fill-opacity="0.25" stroke="#64748b" stroke-width="2" stroke-dasharray="6 4"/>
<text x="180" y="110" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">パーティクルの板</text>
<text x="40" y="304" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">硬い（そのまま）</text>
<rect x="260.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="265.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="271.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="276.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="282.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="287.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="293.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="298.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="304.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="309.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="315.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="320.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="326.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="331.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="337.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="342.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="348.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="353.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="359.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="364.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="370.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="375.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="381.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="386.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="392.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="397.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="403.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="408.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="414.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="419.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="425.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="430.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="436.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="441.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="447.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="452.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="458.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="463.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="469.0" y="310" width="5.6" height="30" fill="#697d9b"/>
<rect x="474.5" y="310" width="5.6" height="30" fill="#697d9b"/>
<text x="40" y="354" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">ソフト（深度差でフェード）</text>
<rect x="260.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="265.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="271.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="276.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="282.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="287.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="293.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="298.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="304.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="309.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="315.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="320.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="326.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="331.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="337.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="342.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="348.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="353.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="359.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="364.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="370.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="375.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="381.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="386.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="392.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="397.5" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="403.0" y="360" width="5.6" height="30" fill="#697d9b"/>
<rect x="408.5" y="360" width="5.6" height="30" fill="#7486a2"/>
<rect x="414.0" y="360" width="5.6" height="30" fill="#7e90a9"/>
<rect x="419.5" y="360" width="5.6" height="30" fill="#8999b0"/>
<rect x="425.0" y="360" width="5.6" height="30" fill="#94a2b8"/>
<rect x="430.5" y="360" width="5.6" height="30" fill="#9fabbf"/>
<rect x="436.0" y="360" width="5.6" height="30" fill="#a9b5c6"/>
<rect x="441.5" y="360" width="5.6" height="30" fill="#b4becd"/>
<rect x="447.0" y="360" width="5.6" height="30" fill="#bfc7d4"/>
<rect x="452.5" y="360" width="5.6" height="30" fill="#c9d1db"/>
<rect x="458.0" y="360" width="5.6" height="30" fill="#d4dae2"/>
<rect x="463.5" y="360" width="5.6" height="30" fill="#dfe3ea"/>
<rect x="469.0" y="360" width="5.6" height="30" fill="#eaecf1"/>
<rect x="474.5" y="360" width="5.6" height="30" fill="#f4f6f8"/>
<text x="260" y="296" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">← 板の上側</text>
<text x="480" y="296" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">地面との交差 →</text>
<rect x="260" y="300" width="5.6" height="100" fill="none" stroke="#e5aa28" stroke-width="2.5"><animate attributeName="x" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800;0.0976;0.1152;0.1328;0.1504;0.1680;0.1856;0.2032;0.2208;0.2384;0.2560;0.2736;0.2912;0.3088;0.3264;0.3440;0.3616;0.3792;0.3968;0.4144;0.4320;0.4496;0.4672;0.4848;0.5024;0.5200;0.5376;0.5552;0.5728;0.5904;0.6080;0.6256;0.6432;0.6608;0.6784;0.6960;0.7136;0.7312;0.7488;0.7664" values="260;260;265.5;271;276.5;282;287.5;293;298.5;304;309.5;315;320.5;326;331.5;337;342.5;348;353.5;359;364.5;370;375.5;381;386.5;392;397.5;403;408.5;414;419.5;425;430.5;436;441.5;447;452.5;458;463.5;469;474.5"/></rect>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 1.00 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1149;0.1152;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.95 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1149;0.1152;0.1501;0.1504;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.89 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1501;0.1504;0.1853;0.1856;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.84 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1853;0.1856;0.2205;0.2208;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.79 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2205;0.2208;0.2557;0.2560;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.74 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2557;0.2560;0.2909;0.2912;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.68 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2909;0.2912;0.3261;0.3264;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.63 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3261;0.3264;0.3613;0.3616;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.58 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3613;0.3616;0.3965;0.3968;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.53 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3965;0.3968;0.4317;0.4320;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.47 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4317;0.4320;0.4669;0.4672;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.42 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4669;0.4672;0.5021;0.5024;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.37 → 不透明度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5021;0.5024;0.5373;0.5376;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.32 → 不透明度 0.90<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5373;0.5376;0.5725;0.5728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.26 → 不透明度 0.75<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5725;0.5728;0.6077;0.6080;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.21 → 不透明度 0.60<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6077;0.6080;0.6429;0.6432;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.16 → 不透明度 0.45<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6429;0.6432;0.6781;0.6784;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.11 → 不透明度 0.30<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6781;0.6784;0.7133;0.7136;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.05 → 不透明度 0.15<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7133;0.7136;0.7485;0.7488;1.0000" values="0;0;1;1;0;0"/></text>
<text x="540" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度差 0.00 → 不透明度 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7485;0.7488;0.7837;0.7840;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">シーンの深度と、板の深度の差を見て、不透明度を決める<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="540" y="360" text-anchor="start" style="font-size:12px;font-weight:500;fill:#e5484d">硬い:交差で不透明のまま → 線が見える</text>
<text x="540" y="382" text-anchor="start" style="font-size:12px;font-weight:500;fill:#2ea043">ソフト:交差に向けて 0 → 線が消える</text>
</svg>

<!-- fig:soft-particles-depth:end -->

## 深度の読み取り（ソフト パーティクル）
<strong>パーティクルの板</strong>が <strong>地面や壁と交差する所で、硬い線</strong>が出ます。シーンの深度を読んで近いほど透明にすると、なじみます（ソフト パーティクル）。

```hlsl
float scene_depth = LinearDepth(depth_texture.Load(int3(input.position.xy, 0)).r);
float particle_depth = LinearDepth(input.position.z);
float fade = saturate((scene_depth - particle_depth) / fade_distance);
color.a *= fade;
```

| 点 | 説明 |
| --- | --- |
| `scene_depth` | 不透明な物の深度（深度バッファを SRV として読む） |
| `particle_depth` | パーティクル自身の深度 |
| `fade_distance` | この距離で完全に不透明に |
| 要件 | 深度バッファを、読み取りと深度テストで同時に使えないので、深度のコピー（または読み取り専用 DSV）が要る |

## 問題：パーティクルが地面と、交差して線が見える

煙や霧のパーティクルは <strong>板（ビルボード）</strong>で、描かれます。板が <strong>地面や壁に突き刺さる</strong>と、板と地面の交差線がぱっきりと見えます。煙が地面に板が刺さっているように見えて、不自然です。

```text
 煙の板
     ╲
      ╲   ← 板が、地面に刺さっている
 ━━━━━━╲━━━━━ 地面
        ╲
         ← 交差した所に、くっきり線が出る
```

## ソフト パーティクル

<strong>ソフト パーティクル</strong>（Lorach、2007）は <strong>パーティクルの、深度</strong>と後ろにある物の深度の差が、小さい所（交差に近い所）でパーティクルを透明に、フェードさせる手法です。交差線が消え板が地面になめらかに、溶け込みます。

```text
アルファ = 元のアルファ × saturate( (シーン深度 − パーティクル深度) / フェード距離 )
```

| 深度の差 | アルファ |
| --- | --- |
| 0（交差している） | 0（透明） |
| フェード距離の半分 | 半分 |
| フェード距離以上 | 元のまま |

## 実装

深度バッファを <strong>シェーダー リソース</strong>として、読みます。パーティクルの描画では深度の書き込みは、無効なので <strong>同じ深度バッファを、読み取り専用の DSV と SRV の、両方</strong>で使えます（[Color by Water Depth](../../water/shading/depth-color.md)、深度の読み方）。

```hlsl
Texture2D<float> g_scene_depth : register(t0);

float4 main(PSInput input) : SV_Target {
  float4 color = g_particle_tex.Sample(g_linear_clamp, input.uv) * input.color;

  // ① 後ろにある、物の深度（視点深度）を、読む
  float scene_ndc = g_scene_depth.Load(int3(input.position.xy, 0));
  float scene_depth = LinearizeDepth(scene_ndc);

  // ② このパーティクルの、深度（視点深度）
  float particle_depth = LinearizeDepth(input.position.z);

  // ③ 差に応じて、アルファを、フェードさせる
  float fade = saturate((scene_depth - particle_depth) / g_soft_distance);
  color.a *= fade;
  return color;
}
```

| パラメーター | 目安 | 効果 |
| --- | --- | --- |
| `g_soft_distance` | 0.5〜2 m | フェードする、深度の範囲。大きいほど交差線の近くからゆっくり、透明になる |

ほとんどの煙や霧では <strong>パーティクルの、大きさの半分くらい</strong>のフェード距離が、使われます。

### 線形の深度で比べる

深度バッファの値は <strong>非線形</strong>（近くで、精度が高く遠くで粗い）です。<strong>差を取るとき</strong>は必ず線形の、視点深度に直してから引きます。

```hlsl
// 線形の視点深度に直す（通常の射影行列）。
float LinearizeDepth(float d) {
  return near_plane * far_plane / (far_plane - d * (far_plane - near_plane));
}
```

非線形のまま差を取ると <strong>遠くで、フェードが効かなくなったり</strong>、<strong>近くで効きすぎたり</strong>します。

## 逆方向：パーティクルが、カメラに近すぎる

パーティクルが <strong>カメラに近づきすぎる</strong>と、<strong>画面全体を覆う</strong>ほど大きくなり、ブレンドのコストが跳ね上がり、見た目もうるさいです。カメラに近いほどフェードアウトさせます。

```hlsl
float near_fade = saturate((particle_depth - near_fade_start) / near_fade_range);
color.a *= near_fade;
```

## 光るパーティクルへの応用

<strong>加算ブレンド</strong>のパーティクル（火花、光）でもソフト パーティクルは、<strong>有効</strong>です。フェードをアルファではなく色（明るさ）に掛けます（加算では、アルファが色を決めるため）。

```hlsl
// 加算ブレンド: 色そのものに、フェードを掛ける。
color.rgb *= fade;
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| 深度を読む | MSAA を、使っているとき深度は MSAA の深度。`Load` でサンプルを指定して読む（または、リゾルブした深度を使う） |
| 同じバッファの読み書き | 深度を、読み取り専用にする（書き込みを、無効にする）。同時に SRV で読む |
| 水と同じ原理 | 水面と地形が、交差する線を消す（[Shore Foam: Depth Difference](../../water/shore-foam/shore-depth.md)）。水の岸のアルファも同じ式 |
| 解像度 | パーティクルを、低解像度で描くときは深度も縮小して、読む（縮小する深度は最も近い値で、縮める） |

## よくあるミス

??? failure "煙が地面と交差して、硬い線が出る"
    <strong>ソフト パーティクル</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度の差でアルファを弱める
    - [x] 交差の硬い線が消える

## 参考

- Lorach, "Soft Particles", NVIDIA White Paper, 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（`SrcBlend`、`DestBlend`、`BlendOp`）
- Microsoft Learn, "Reading depth-stencil as shader resource"

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [Sorting](sorting.md)

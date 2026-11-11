---
title: Blur Pass Implementation
tags:
  - 描画
---

# Blur Pass Implementation

速度バッファができればモーション ブラーのパスは、「各画素の速度に沿って画像を複数サンプルして平均する」だけに見えます。ところが、これをそのままやると速い物体の輪郭がぷつっと切れたり静止した前景に背景の動きがにじんだり、サンプルが点の列に見えたりします。

<strong>速度に沿った平均をジッター（サンプル位置のずらし）と深度と速度による重み付けで補うのが標準です</strong>。このページでは基本のぼかしジッターで縞をノイズに変える方法（誤差を測った結果つき）、前景と背景の重み付け（McGuire らの方式）、サンプル数と最大長、完成形のシェーダー、コストを説明します。

!!! tip "ポイント"
    - ぼかしは画素の速度ベクトルに沿って、前後にサンプルして平均します。
    - サンプル数は 8〜16 です。少ないとサンプルが離散的に見えます（縞）。
    - サンプル位置を画素ごとにジッターすると、縞がノイズに変わります。TAA と併用するとノイズがさらにならされます。
    - 重み付き平均で手前の速い物は奥にかぶさり奥の速い物は、手前の遅い物にはにじみません。
    - 速度の長さには最大値を設けて、短い速度（0.5 画素未満）はスキップします。

!!! info "このページを読む前に"
    - [Motion Blur](index.md)（このセクション全体の地図と読む順番）

## 基本のぼかし {#basic}

最も素朴な実装は速度ベクトルの両側に等間隔でサンプルを置いて、平均します。

```hlsl
Texture2D<float4> g_scene_color : register(t0);
Texture2D<float2> g_velocity : register(t1);          // 画素の速度（UV 単位。シャッター角を掛けた後）
Texture2D<float2> g_neighbor_max : register(t2);      // タイルの近傍最大速度（UV 単位）
Texture2D<float> g_depth : register(t3);              // 視点深度（メートル）
SamplerState g_linear_clamp : register(s0);
SamplerState g_point_clamp : register(s1);

cbuffer BlurConstants : register(b0) {
  float2 g_resolution;       // 画面の幅・高さ（ピクセル）
  float g_max_blur_px;       // ブラーの最大長（ピクセル）。画面の高さの 3〜5 %。例: 40
  float g_depth_scale;       // 深度の比較のなだらかさ。例: 1.0（メートルあたり）
  uint g_sample_count;       // 例: 12
  float3 _pad;
};

float3 MotionBlurBasic(float2 uv, float2 velocity_uv, uint sample_count) {
  float3 sum = g_scene_color.SampleLevel(g_linear_clamp, uv, 0).rgb;
  [loop] for (uint i = 1; i < sample_count; ++i) {
    float t = float(i) / float(sample_count - 1) - 0.5;     // -0.5 .. +0.5。中心がその画素
    sum += g_scene_color.SampleLevel(g_linear_clamp, uv + velocity_uv * t, 0).rgb;
  }
  return sum / float(sample_count);
}
```

`t` は速度ベクトルの前後にサンプルを置くパラメータで、中心がその画素です。`velocity_uv` にはシャッター角を掛けた UV での移動量を入れます。サンプルが一直線に等間隔に並ぶので、サンプル数が少ないと点の列が見えます。

## ジッターで縞を消す {#jitter}

サンプルの位置を画素ごとに少しずらすと規則的な縞が、細かいノイズに変わって目立たなくなります。

```hlsl
// 画面上の位置から、決定的な 0..1 のノイズを作る（Interleaved Gradient Noise）
float InterleavedGradientNoise(float2 pixel) {
  return frac(52.9829189 * frac(dot(pixel, float2(0.06711056, 0.00583715))));
}

float3 MotionBlurJitter(float2 uv, float2 velocity_uv, uint sample_count, float noise) {
  float3 sum = 0.0;
  [loop] for (uint i = 0; i < sample_count; ++i) {
    float t = (float(i) + noise) / float(sample_count) - 0.5;   // 各区間の中で、ノイズぶんだけずらす
    sum += g_scene_color.SampleLevel(g_linear_clamp, uv + velocity_uv * t, 0).rgb;
  }
  return sum / float(sample_count);
}
```

ノイズにはインターリーブド グラディエント ノイズ（IGN）などを使います。ブルー ノイズが理想です。

効果を 1 次元のモデルで測りました。幅 9 画素の明るい帯が 37 画素ごとに並ぶ画像を 60 画素のブラーでぼかしました。512 サンプルの結果を正解として、サンプル数 `N` を変えて規則的な置き方とジッターの誤差（RMS）を比べました。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="サンプル数ごとの誤差。規則的な置き方とジッター。4 サンプルではジッターが半分、8 から 16 サンプルでは RMS は同程度で、ジッターは構造的な縞がノイズに変わる"><text x="14" y="22" class="fig-title">サンプル数と誤差（RMS。小さいほど良い。1 次元モデルの実測）</text>
<line x1="60" y1="210" x2="690" y2="210" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="90" y="52" width="50" height="158" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="146" y="129" width="50" height="81" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/>
<rect x="250" y="176" width="50" height="34" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="306" y="153" width="50" height="57" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/>
<rect x="410" y="187" width="50" height="23" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="466" y="181" width="50" height="29" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/>
<rect x="570" y="199" width="50" height="11" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="626" y="204" width="50" height="6" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="115" y="46">0.211</text><text x="171" y="123">0.108</text><text x="275" y="170">0.046</text><text x="331" y="147">0.075</text><text x="435" y="181">0.031</text><text x="491" y="175">0.039</text><text x="595" y="193">0.015</text><text x="651" y="198">0.008</text>
<text x="143" y="230">4 サンプル</text><text x="303" y="230">8</text><text x="463" y="230">16</text><text x="623" y="230">32</text></g>
<text x="360" y="256" text-anchor="middle" style="font-size:12px">左（赤）が規則的、右（青）がジッター。4 と 32 ではジッターが小さい。8 と 16 では RMS は同程度かジッターが大きい</text></svg>

4 サンプルでは規則的が 0.211 に対して、ジッターが 0.108 で半分でした。8 サンプルでは規則的が 0.046、ジッターが 0.075 でジッターの方が大きくなりました。16 サンプルでは 0.031 と 0.039 でした。32 サンプルでは 0.015 と 0.008 で、ジッターが半分です。

つまり、ジッターは RMS 誤差を常に下げるわけではありません。規則的な置き方の誤差は縞（低周波の構造）になって、目立ちます。ジッターは同じ程度の誤差を細かいノイズに変えます。縞のような低周波の誤差は 8 サンプルで 0.0235 から 0.019 に下がりました。さらに、TAA で 4 フレームを平均すると、8 サンプルのジッターは RMS が 0.042 まで下がって、規則的（0.046）を下回りました。この測定は周期的な模様と 1 次元のブラーという縞が出やすい条件のものです。実際のシーンでの違いはこれより小さいことがあります。

<!-- fig:motion-blur-jitter:begin -->

<svg class="fig illust motion" data-fig="motion-blur-jitter" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-motion-blur-jitter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">モーション ブラーのサンプル: 少ない数で等間隔に取ると、帯になる。ずらして取ると、ノイズになる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 64 画素。幅 4 の明るい棒が 1 フレームで 16 画素、右へ動く。流れた軌跡を 4 サンプルや 16 サンプルで描く</text>
<text x="60.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">4 サンプル・等間隔</text>
<rect x="60.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#ffffff"/></rect>
<rect x="72.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0682" values="#e5e7eb;#ffffff"/></rect>
<rect x="85.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#ffffff"/></rect>
<rect x="97.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0713" values="#e5e7eb;#ffffff"/></rect>
<rect x="110.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#e5e7eb;#ffffff"/></rect>
<rect x="122.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#ffffff"/></rect>
<rect x="135.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0760" values="#e5e7eb;#ffffff"/></rect>
<rect x="147.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0776" values="#e5e7eb;#ffffff"/></rect>
<rect x="160.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#ffffff"/></rect>
<rect x="172.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0807" values="#e5e7eb;#ffffff"/></rect>
<rect x="185.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0822" values="#e5e7eb;#ffffff"/></rect>
<rect x="197.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0838" values="#e5e7eb;#ffffff"/></rect>
<rect x="210.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#ffffff"/></rect>
<rect x="222.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0869" values="#e5e7eb;#ffffff"/></rect>
<rect x="235.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="247.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0900" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="260.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="272.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0931" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="285.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0947" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="297.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0962" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="310.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="322.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0993" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="335.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1009" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="347.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1024" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="360.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="372.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1056" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="385.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1071" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="397.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1087" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="410.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="422.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1118" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="435.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1133" values="#e5e7eb;#ffffff"/></rect>
<rect x="447.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1149" values="#e5e7eb;#ffffff"/></rect>
<rect x="460.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1164" values="#e5e7eb;#ffffff"/></rect>
<rect x="472.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1180" values="#e5e7eb;#ffffff"/></rect>
<rect x="485.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1196" values="#e5e7eb;#ffffff"/></rect>
<rect x="497.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1211" values="#e5e7eb;#ffffff"/></rect>
<rect x="510.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1227" values="#e5e7eb;#ffffff"/></rect>
<rect x="522.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1242" values="#e5e7eb;#ffffff"/></rect>
<rect x="535.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1258" values="#e5e7eb;#ffffff"/></rect>
<rect x="547.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1273" values="#e5e7eb;#ffffff"/></rect>
<rect x="560.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#ffffff"/></rect>
<rect x="572.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1304" values="#e5e7eb;#ffffff"/></rect>
<rect x="585.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1320" values="#e5e7eb;#ffffff"/></rect>
<rect x="597.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1336" values="#e5e7eb;#ffffff"/></rect>
<rect x="610.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1351" values="#e5e7eb;#ffffff"/></rect>
<rect x="622.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#e5e7eb;#ffffff"/></rect>
<rect x="635.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1382" values="#e5e7eb;#ffffff"/></rect>
<rect x="647.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1398" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#e5e7eb;#ffffff"/></rect>
<rect x="672.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1429" values="#e5e7eb;#ffffff"/></rect>
<rect x="685.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1444" values="#e5e7eb;#ffffff"/></rect>
<rect x="697.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1460" values="#e5e7eb;#ffffff"/></rect>
<rect x="710.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1476" values="#e5e7eb;#ffffff"/></rect>
<rect x="722.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1491" values="#e5e7eb;#ffffff"/></rect>
<rect x="735.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1507" values="#e5e7eb;#ffffff"/></rect>
<rect x="747.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1522" values="#e5e7eb;#ffffff"/></rect>
<rect x="760.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1538" values="#e5e7eb;#ffffff"/></rect>
<rect x="772.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1553" values="#e5e7eb;#ffffff"/></rect>
<rect x="785.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1569" values="#e5e7eb;#ffffff"/></rect>
<rect x="797.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1584" values="#e5e7eb;#ffffff"/></rect>
<rect x="810.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#ffffff"/></rect>
<rect x="822.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1616" values="#e5e7eb;#ffffff"/></rect>
<rect x="835.0" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1631" values="#e5e7eb;#ffffff"/></rect>
<rect x="847.5" y="112.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1647" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="112" width="800.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="0;0;1;1"/><text x="870.0" y="124" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">ずれ 0.008</text>
<text x="870.0" y="142" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">読み込み 4</text>
</g>
<text x="60.0" y="170" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">4 サンプル・ずらす(ジッター)</text>
<rect x="60.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2444" values="#e5e7eb;#ffffff"/></rect>
<rect x="72.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2460" values="#e5e7eb;#ffffff"/></rect>
<rect x="85.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2476" values="#e5e7eb;#ffffff"/></rect>
<rect x="97.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2491" values="#e5e7eb;#ffffff"/></rect>
<rect x="110.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#e5e7eb;#ffffff"/></rect>
<rect x="122.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2522" values="#e5e7eb;#ffffff"/></rect>
<rect x="135.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2538" values="#e5e7eb;#ffffff"/></rect>
<rect x="147.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2553" values="#e5e7eb;#ffffff"/></rect>
<rect x="160.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2569" values="#e5e7eb;#ffffff"/></rect>
<rect x="172.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2584" values="#e5e7eb;#ffffff"/></rect>
<rect x="185.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2600" values="#e5e7eb;#ffffff"/></rect>
<rect x="197.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2616" values="#e5e7eb;#ffffff"/></rect>
<rect x="210.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2631" values="#e5e7eb;#ffffff"/></rect>
<rect x="222.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2647" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="235.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2662" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="247.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2678" values="#e5e7eb;#eaeaea"/></rect>
<rect x="260.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="272.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2709" values="#e5e7eb;#a9a9a9"/></rect>
<rect x="285.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2724" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="297.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2740" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="310.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="322.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2771" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="335.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2787" values="#e5e7eb;#fafafa"/></rect>
<rect x="347.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2802" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="360.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="372.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2833" values="#e5e7eb;#808080"/></rect>
<rect x="385.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2849" values="#e5e7eb;#adadad"/></rect>
<rect x="397.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2864" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="410.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="422.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2896" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="435.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2911" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="447.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2927" values="#e5e7eb;#ffffff"/></rect>
<rect x="460.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#ffffff"/></rect>
<rect x="472.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2958" values="#e5e7eb;#ffffff"/></rect>
<rect x="485.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2973" values="#e5e7eb;#ffffff"/></rect>
<rect x="497.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2989" values="#e5e7eb;#ffffff"/></rect>
<rect x="510.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#e5e7eb;#ffffff"/></rect>
<rect x="522.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3020" values="#e5e7eb;#ffffff"/></rect>
<rect x="535.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3036" values="#e5e7eb;#ffffff"/></rect>
<rect x="547.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3051" values="#e5e7eb;#ffffff"/></rect>
<rect x="560.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3067" values="#e5e7eb;#ffffff"/></rect>
<rect x="572.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3082" values="#e5e7eb;#ffffff"/></rect>
<rect x="585.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3098" values="#e5e7eb;#ffffff"/></rect>
<rect x="597.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3113" values="#e5e7eb;#ffffff"/></rect>
<rect x="610.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3129" values="#e5e7eb;#ffffff"/></rect>
<rect x="622.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3144" values="#e5e7eb;#ffffff"/></rect>
<rect x="635.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3160" values="#e5e7eb;#ffffff"/></rect>
<rect x="647.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3176" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3191" values="#e5e7eb;#ffffff"/></rect>
<rect x="672.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3207" values="#e5e7eb;#ffffff"/></rect>
<rect x="685.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3222" values="#e5e7eb;#ffffff"/></rect>
<rect x="697.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3238" values="#e5e7eb;#ffffff"/></rect>
<rect x="710.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3253" values="#e5e7eb;#ffffff"/></rect>
<rect x="722.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3269" values="#e5e7eb;#ffffff"/></rect>
<rect x="735.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3284" values="#e5e7eb;#ffffff"/></rect>
<rect x="747.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3300" values="#e5e7eb;#ffffff"/></rect>
<rect x="760.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3316" values="#e5e7eb;#ffffff"/></rect>
<rect x="772.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3331" values="#e5e7eb;#ffffff"/></rect>
<rect x="785.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3347" values="#e5e7eb;#ffffff"/></rect>
<rect x="797.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3362" values="#e5e7eb;#ffffff"/></rect>
<rect x="810.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3378" values="#e5e7eb;#ffffff"/></rect>
<rect x="822.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3393" values="#e5e7eb;#ffffff"/></rect>
<rect x="835.0" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3409" values="#e5e7eb;#ffffff"/></rect>
<rect x="847.5" y="174.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3424" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="174" width="800.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/><text x="870.0" y="186" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">ずれ 0.021</text>
<text x="870.0" y="204" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">読み込み 4</text>
</g>
<text x="60.0" y="232" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">16 サンプル・等間隔</text>
<rect x="60.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4222" values="#e5e7eb;#ffffff"/></rect>
<rect x="72.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4238" values="#e5e7eb;#ffffff"/></rect>
<rect x="85.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4253" values="#e5e7eb;#ffffff"/></rect>
<rect x="97.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269" values="#e5e7eb;#ffffff"/></rect>
<rect x="110.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4284" values="#e5e7eb;#ffffff"/></rect>
<rect x="122.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4300" values="#e5e7eb;#ffffff"/></rect>
<rect x="135.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#e5e7eb;#ffffff"/></rect>
<rect x="147.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4331" values="#e5e7eb;#ffffff"/></rect>
<rect x="160.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4347" values="#e5e7eb;#ffffff"/></rect>
<rect x="172.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4362" values="#e5e7eb;#ffffff"/></rect>
<rect x="185.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4378" values="#e5e7eb;#ffffff"/></rect>
<rect x="197.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4393" values="#e5e7eb;#ffffff"/></rect>
<rect x="210.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4409" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="222.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4424" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="235.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4440" values="#e5e7eb;#d7d7d7"/></rect>
<rect x="247.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4456" values="#e5e7eb;#c7c7c7"/></rect>
<rect x="260.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4471" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="272.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4487" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="285.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4502" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="297.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4518" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="310.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4533" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="322.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4549" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="335.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4564" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="347.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4580" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="360.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4596" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="372.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4611" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="385.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4627" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="397.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4642" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="410.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4658" values="#e5e7eb;#c7c7c7"/></rect>
<rect x="422.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4673" values="#e5e7eb;#d7d7d7"/></rect>
<rect x="435.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="447.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4704" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="460.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#ffffff"/></rect>
<rect x="472.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4736" values="#e5e7eb;#ffffff"/></rect>
<rect x="485.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4751" values="#e5e7eb;#ffffff"/></rect>
<rect x="497.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4767" values="#e5e7eb;#ffffff"/></rect>
<rect x="510.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#ffffff"/></rect>
<rect x="522.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4798" values="#e5e7eb;#ffffff"/></rect>
<rect x="535.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4813" values="#e5e7eb;#ffffff"/></rect>
<rect x="547.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4829" values="#e5e7eb;#ffffff"/></rect>
<rect x="560.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#ffffff"/></rect>
<rect x="572.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4860" values="#e5e7eb;#ffffff"/></rect>
<rect x="585.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4876" values="#e5e7eb;#ffffff"/></rect>
<rect x="597.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4891" values="#e5e7eb;#ffffff"/></rect>
<rect x="610.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#ffffff"/></rect>
<rect x="622.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4922" values="#e5e7eb;#ffffff"/></rect>
<rect x="635.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4938" values="#e5e7eb;#ffffff"/></rect>
<rect x="647.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4953" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#ffffff"/></rect>
<rect x="672.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984" values="#e5e7eb;#ffffff"/></rect>
<rect x="685.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5000" values="#e5e7eb;#ffffff"/></rect>
<rect x="697.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5016" values="#e5e7eb;#ffffff"/></rect>
<rect x="710.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5031" values="#e5e7eb;#ffffff"/></rect>
<rect x="722.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5047" values="#e5e7eb;#ffffff"/></rect>
<rect x="735.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5062" values="#e5e7eb;#ffffff"/></rect>
<rect x="747.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5078" values="#e5e7eb;#ffffff"/></rect>
<rect x="760.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5093" values="#e5e7eb;#ffffff"/></rect>
<rect x="772.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5109" values="#e5e7eb;#ffffff"/></rect>
<rect x="785.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5124" values="#e5e7eb;#ffffff"/></rect>
<rect x="797.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140" values="#e5e7eb;#ffffff"/></rect>
<rect x="810.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5156" values="#e5e7eb;#ffffff"/></rect>
<rect x="822.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5171" values="#e5e7eb;#ffffff"/></rect>
<rect x="835.0" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5187" values="#e5e7eb;#ffffff"/></rect>
<rect x="847.5" y="236.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5202" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="236" width="800.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5109;0.5111;1.0000" values="0;0;1;1"/><text x="870.0" y="248" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ずれ 0.000</text>
<text x="870.0" y="266" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">読み込み 16</text>
</g>
<text x="60.0" y="294" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">正解(256 サンプル)</text>
<rect x="60.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6000" values="#e5e7eb;#ffffff"/></rect>
<rect x="72.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6016" values="#e5e7eb;#ffffff"/></rect>
<rect x="85.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6031" values="#e5e7eb;#ffffff"/></rect>
<rect x="97.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6047" values="#e5e7eb;#ffffff"/></rect>
<rect x="110.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6062" values="#e5e7eb;#ffffff"/></rect>
<rect x="122.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6078" values="#e5e7eb;#ffffff"/></rect>
<rect x="135.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6093" values="#e5e7eb;#ffffff"/></rect>
<rect x="147.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6109" values="#e5e7eb;#ffffff"/></rect>
<rect x="160.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6124" values="#e5e7eb;#ffffff"/></rect>
<rect x="172.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6140" values="#e5e7eb;#ffffff"/></rect>
<rect x="185.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6156" values="#e5e7eb;#ffffff"/></rect>
<rect x="197.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6171" values="#e5e7eb;#ffffff"/></rect>
<rect x="210.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6187" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="222.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6202" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="235.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6218" values="#e5e7eb;#d7d7d7"/></rect>
<rect x="247.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6233" values="#e5e7eb;#c7c7c7"/></rect>
<rect x="260.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6249" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="272.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6264" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="285.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6280" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="297.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="310.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6311" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="322.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6327" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="335.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6342" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="347.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6358" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="360.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6373" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="372.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6389" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="385.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6404" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="397.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6420" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="410.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6436" values="#e5e7eb;#c7c7c7"/></rect>
<rect x="422.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6451" values="#e5e7eb;#d7d7d7"/></rect>
<rect x="435.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6467" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="447.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6482" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="460.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6498" values="#e5e7eb;#ffffff"/></rect>
<rect x="472.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6513" values="#e5e7eb;#ffffff"/></rect>
<rect x="485.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6529" values="#e5e7eb;#ffffff"/></rect>
<rect x="497.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6544" values="#e5e7eb;#ffffff"/></rect>
<rect x="510.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6560" values="#e5e7eb;#ffffff"/></rect>
<rect x="522.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6576" values="#e5e7eb;#ffffff"/></rect>
<rect x="535.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6591" values="#e5e7eb;#ffffff"/></rect>
<rect x="547.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6607" values="#e5e7eb;#ffffff"/></rect>
<rect x="560.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6622" values="#e5e7eb;#ffffff"/></rect>
<rect x="572.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6638" values="#e5e7eb;#ffffff"/></rect>
<rect x="585.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6653" values="#e5e7eb;#ffffff"/></rect>
<rect x="597.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6669" values="#e5e7eb;#ffffff"/></rect>
<rect x="610.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6684" values="#e5e7eb;#ffffff"/></rect>
<rect x="622.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6700" values="#e5e7eb;#ffffff"/></rect>
<rect x="635.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6716" values="#e5e7eb;#ffffff"/></rect>
<rect x="647.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6731" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#ffffff"/></rect>
<rect x="672.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6762" values="#e5e7eb;#ffffff"/></rect>
<rect x="685.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6778" values="#e5e7eb;#ffffff"/></rect>
<rect x="697.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6793" values="#e5e7eb;#ffffff"/></rect>
<rect x="710.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#ffffff"/></rect>
<rect x="722.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6824" values="#e5e7eb;#ffffff"/></rect>
<rect x="735.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6840" values="#e5e7eb;#ffffff"/></rect>
<rect x="747.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6856" values="#e5e7eb;#ffffff"/></rect>
<rect x="760.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#ffffff"/></rect>
<rect x="772.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6887" values="#e5e7eb;#ffffff"/></rect>
<rect x="785.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6902" values="#e5e7eb;#ffffff"/></rect>
<rect x="797.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6918" values="#e5e7eb;#ffffff"/></rect>
<rect x="810.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#ffffff"/></rect>
<rect x="822.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6949" values="#e5e7eb;#ffffff"/></rect>
<rect x="835.0" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6964" values="#e5e7eb;#ffffff"/></rect>
<rect x="847.5" y="298.0" width="12.8" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6980" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="298" width="800.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6887;0.6889;1.0000" values="0;0;1;1"/><text x="870.0" y="310" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">ずれ 0.000</text>
<text x="870.0" y="328" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">読み込み 256</text>
</g>
<text x="40" y="400" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">読み込みの回数(1 画素あたり):</text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;0.4220;0.4222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">256<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7554;0.7556;1.0000" values="0;0;1;1"/><rect x="40" y="436" width="880" height="76" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="460" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">4 サンプル: 等間隔だと、流れが「4 つの棒」に見える(帯)。ずらすと、1 本の流れ + ノイズ</text>
<text x="56" y="483" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">ずれ: 等間隔 4 = 0.008 / ずらす 4 = 0.021 / 等間隔 16 = 0.000</text>
<text x="56" y="505" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ノイズは、TAA や、ぼかしで消せる。帯は、消えない。だから、ジッターを使う</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">動いた軌跡を画素ごとに、何点かサンプルして平均する<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">サンプルが少ないと、「離れた棒」が見える(帯)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7776;0.7778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ずらして取れば、帯が消えて、ノイズに変わる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7776;0.7778;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:motion-blur-jitter:end -->

## 前景と背景の問題 {#problem}

単純な平均では 2 つの破綻が起きます。

- 速い物体の輪郭の外（背景）は背景の画素の速度が 0 なので、ぼけません。物体の尾が輪郭でぷつっと切れます。
- 静止した前景の物の縁では背景の速い動きでぼかした色が、静止した前景にまでにじみます。

## 深度と速度による重み付け {#weights}

サンプルを集めるときそのサンプルが自分より手前か奥かサンプルの速度が自分の位置まで届くかで、重みを決めます（McGuire らの方法の考え方）。

```hlsl
// 手前なら「相手の速度が自分まで届く」、奥なら「自分の速度が相手まで届く」ときに、重みが大きい
float SampleWeight(float center_depth, float sample_depth,
                   float2 center_velocity_px, float2 sample_velocity_px,
                   float offset_length_px) {
  // サンプルが自分より奥なら 1、手前なら 0 に近づく。なだらかな境目で、ちらつきを避ける
  float depth_compare = saturate(0.5 + (sample_depth - center_depth) * g_depth_scale);
  // 速度が、そのサンプルの距離まで届くか（1 = 届く、0 = 届かない）
  float center_reach = saturate(1.0 - offset_length_px / max(length(center_velocity_px), 1e-4));
  float sample_reach = saturate(1.0 - offset_length_px / max(length(sample_velocity_px), 1e-4));
  float front = (1.0 - depth_compare) * sample_reach;   // 手前のサンプルが自分に被さる
  float back = depth_compare * center_reach;            // 自分の動きが奥の色を混ぜる
  return front + back;
}
```

`depth_compare` はサンプルが自分より奥か手前かを表します。`sample_reach` は手前のサンプルの速度が、自分の位置まで届くかです（手前の動く物が、自分にかぶさる）。`center_reach` は自分の速度が奥のサンプルまで届くかです（自分の動きが奥の色を混ぜる）。手前なら「相手の速度が届く」、奥なら「自分の速度が届く」ときに重みが大きくなります。

考え方は手前の動く物のブラーは奥の背景にかぶさるというものです。奥の物が動いていても手前の静止した物には、にじみません。

## 完成形のシェーダー {#shader}

近傍の最大速度（タイルの最大速度）で、サンプルの方向と長さを決めると、輪郭の外側にも尾が伸びます（[Tile Max Velocity](tile-max.md)）。速度の長さには最大値を設けて、短い速度はスキップします。

```hlsl
float2 LimitVelocityPx(float2 v_px) {
  float len = length(v_px);
  if (len < 0.5) return 0.0;                             // 0.5 画素未満はぼかさない
  return v_px * (min(len, g_max_blur_px) / len);        // 最大長で切る
}

float4 MotionBlurPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float3 center_color = g_scene_color.SampleLevel(g_linear_clamp, uv, 0).rgb;
  float center_depth = g_depth.SampleLevel(g_point_clamp, uv, 0);
  float2 center_velocity = LimitVelocityPx(g_velocity.SampleLevel(g_point_clamp, uv, 0) * g_resolution);
  // サンプルの方向と長さは、自分の速度ではなく、近傍の最大速度で決める（尾を輪郭の外へ伸ばす）
  float2 neighbor_velocity = LimitVelocityPx(g_neighbor_max.SampleLevel(g_point_clamp, uv, 0) * g_resolution);

  if (length(neighbor_velocity) < 0.5) return float4(center_color, 1.0);   // 近くに動きがなければ、そのまま

  float noise = InterleavedGradientNoise(pos.xy);
  float3 sum = center_color;
  float weight_sum = 1.0;
  [loop] for (uint i = 0; i < g_sample_count; ++i) {
    float t = (float(i) + noise) / float(g_sample_count) - 0.5;
    float2 offset_px = neighbor_velocity * t;
    float2 sample_uv = uv + offset_px / g_resolution;
    float sample_depth = g_depth.SampleLevel(g_point_clamp, sample_uv, 0);
    float2 sample_velocity = LimitVelocityPx(g_velocity.SampleLevel(g_point_clamp, sample_uv, 0) * g_resolution);
    float w = SampleWeight(center_depth, sample_depth, center_velocity, sample_velocity, length(offset_px));
    sum += g_scene_color.SampleLevel(g_linear_clamp, sample_uv, 0).rgb * w;
    weight_sum += w;
  }
  return float4(sum / weight_sum, 1.0);
}
```

サンプル数はジッターありなら 8 で足りることが多く、速い動きでは 16 まで増やします。最大ブラー長は画面の高さの 3〜5 % です。1080 の高さなら 32〜54 ピクセルです。最小速度は 0.5 ピクセルで、それ未満の画素はブラーをスキップします。

## コスト {#cost}

1920 × 1080 の全画素で 12 サンプルならサンプル（色、深度、速度の読み出し）は `1920 × 1080 × 12 ≒ 2500 万回` です。1 サンプルで 3 回のテクスチャ読み出しがあるので、約 7500 万回です。タイルの最大速度が 0.5 画素未満のタイルをスキップすれば、静止した場面ではほとんどが 0 になります。半解像度でぼかして合成時に境界に気をつければ、見た目はあまり変わらず読み出しが 4 分の 1 になります。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で `MotionBlurPS` とそこから呼ぶ関数をコンパイルして、エラーが出ないことを確かめました。誤差の数字は 1 次元モデルを Python で実装して測った値で、実際の 2 次元の画像のものではありません。GPU での描画は確認していません。

## 工夫のまとめ {#tips}

- 重み付き平均は輪郭のにじみとかぶりを自然にします。必須です。
- ブルー ノイズのジッターは少ないサンプルでなめらかにします。
- 近傍最大速度は尾の長さと方向に使います。
- 速度が小さい画素はスキップして、コストを減らします。
- TAA と併用するとノイズがさらにならされます。
- カメラの動きと物体の動きを同じ速度バッファで、一括処理します。

## よくあるミス {#mistakes}

??? failure "サンプルが点の列に見える（縞）"
    原因はサンプルが規則的に並んでいることです。画素ごとのジッターを入れて縞をノイズに変えます。TAA があるならフレームごとにノイズを変えます。

??? failure "静止した前景に背景の動きがにじむ"
    原因は深度と速度で重みを付けずに単純に平均していることです。`SampleWeight` のような重み付けを使います。

??? failure "速い物体の輪郭で、ぼかしが切れる"
    原因は自分の速度でサンプルを置いていることです。背景の画素は速度が 0 なので、尾が伸びません。近傍の最大速度を使います。

??? failure "サンプル数を増やしても、重いだけで効果が少ない"
    原因は規則的な置き方の縞が、サンプル数だけでは消えにくいことです。ジッターでノイズに変えるほうが、効きます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] ぼかしは速度に沿って前後にサンプルして平均します。
    - [x] 画素ごとのジッターで、縞をノイズに変えます。TAA と併用するとさらによくなります。
    - [x] 深度と速度の重み付けで、前景と背景の破綻を防ぎます。
    - [x] 近傍最大速度で、輪郭の外にも尾を伸ばします。
    - [x] 最大長で制限して、遅い画素はスキップします。

## 参考 {#references}

このページは次の資料を読まずに書きました。重みの式は McGuire らの方法の考え方を自分で書いたもので、原論文とは異なります。

- McGuire, Hennessy, Bukowski, Osman, "A Reconstruction Filter for Plausible Motion Blur", I3D 2012
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014
- Sousa, "Graphics Gems from CryENGINE 3", SIGGRAPH 2013

## 関連ページ

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Tile Max Velocity](tile-max.md)
- [Strength and TAA](strength-taa.md)

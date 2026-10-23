---
title: Blur Pass Implementation
tags:
  - 描画
---

# Blur Pass Implementation

<strong>速度バッファができたら、画素ごとに速度の向きへ、画像を複数サンプルして平均</strong>します。単純な線形ブラーは、速い物体の輪郭がぷつっと切れ、静止した前景に背景の動きがにじむなどの破綻を起こすので、深度と速度で重みを付けるのが標準です。このページでは、基本のぼかし・ジッターでバンディングを消す方法・前景と背景の重み付け（McGuire 方式）・サンプル数・コストを説明します。

!!! tip "ポイント"
    - ぼかし ＝ <strong>画素の速度ベクトルに沿って、前後にサンプルして平均</strong>。
    - サンプル数は<strong>8〜16</strong>。少ないとサンプルが離散的に見える（縞）。
    - サンプル位置を画素ごとにジッターすると、縞がノイズに変わる。
    - 重み付き平均：手前の速い物は奥にかぶさり、奥の速い物は手前の遅い物には、にじまない。
    - 速度の長さを最大値で制限し、短い速度（< 0.5 画素）はスキップ。
    - 半解像度やタイルでコストを下げる。

!!! info "このページを読む前に"
    - [Motion Blur](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 基本のぼかし

```hlsl
float3 MotionBlurBasic(float2 uv, float2 velocity_uv, int sample_count) {
  float3 sum = scene_color.SampleLevel(linear_clamp, uv, 0).rgb;
  [loop] for (int i = 1; i < sample_count; ++i) {
    float t = float(i) / float(sample_count - 1) - 0.5;
    float2 sample_uv = uv + velocity_uv * t;
    sum += scene_color.SampleLevel(linear_clamp, sample_uv, 0).rgb;
  }
  return sum / float(sample_count);
}
```

ぼかしのコードの要点です。`t`（−0.5〜+0.5）は、速度ベクトルの両側（前後）にサンプルを置くパラメータで、中心がその画素です。`velocity_uv` は、シャッター角を掛けた UV での移動量です。サンプル数は 8〜16 で、速い動きほど多く必要です。

<strong>線形ブラーの欠点</strong>：サンプルが一直線に並ぶので、サンプル数が少ないと、「点の列」が見える。輪郭がくっきり出ない。

## ジッターで縞を消す

<strong>サンプルの位置を画素ごとに少しずらす</strong>と、規則的な縞が細かいノイズに変わり、目立たなくなります。

```hlsl
float3 MotionBlurJitter(float2 uv, float2 velocity_uv, int sample_count, float noise) {
  float3 sum = 0;
  [loop] for (int i = 0; i < sample_count; ++i) {
    float t = (float(i) + noise) / float(sample_count) - 0.5;
    float2 sample_uv = uv + velocity_uv * t;
    sum += scene_color.SampleLevel(linear_clamp, sample_uv, 0).rgb;
  }
  return sum / float(sample_count);
}
```

ジッターのコードの要点です。`noise`（0〜1）には、インターリーブド グラディエント ノイズなどを使います（ブルー ノイズが理想です）。サンプルが 8 個でも、なめらかに見えます。TAA と併用して、フレームごとに `noise` を変えると、TAA が平均して、さらに滑らかになります。

<!-- fig:motion-blur-jitter:begin -->

<svg class="fig illust motion" data-fig="motion-blur-jitter" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-motion-blur-jitter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">モーション ブラーのサンプル: 少ない数で等間隔に取ると、帯になる。ずらして取ると、ノイズになる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 64 画素。幅 4 の明るい棒が、1 フレームで 16 画素、右へ動く。流れた軌跡を、4 サンプルや 16 サンプルで描く</text>
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
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">動いた軌跡を、画素ごとに、何点かサンプルして平均する<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">サンプルが少ないと、「離れた棒」が見える(帯)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7776;0.7778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ずらして取れば、帯が消えて、ノイズに変わる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7776;0.7778;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:motion-blur-jitter:end -->

## 前景と背景の問題

<strong>単純な平均では、次の破綻が起きます</strong>。

単純な平均では、2 つの破綻が起きます。速い物体の輪郭の外（背景）は、背景の画素の速度が 0 なので、ぼけず、物体の尾が輪郭でぷつっと切れます。静止した前景の物の縁では、背景の速い動きでぼかした色が、静止した前景にまでにじみます。

## 深度と速度による重み付け

<strong>サンプルを集めるとき</strong>、そのサンプルが自分より手前か奥か、サンプルの速度が自分の位置まで届くかで重みを決めます（McGuire らの方法）。

```hlsl
float SampleWeight(float center_depth, float sample_depth,
                   float2 center_velocity_px, float2 sample_velocity_px,
                   float offset_length_px) {
  float depth_compare = saturate(0.5 + (sample_depth - center_depth) * kDepthScale);
  float center_reach = saturate(1.0 - offset_length_px / max(length(center_velocity_px), 1e-4));
  float sample_reach = saturate(1.0 - offset_length_px / max(length(sample_velocity_px), 1e-4));
  float front = (1.0 - depth_compare) * sample_reach;
  float back = depth_compare * center_reach;
  return front + back;
}
```

| 点 | 説明 |
| --- | --- |
| `depth_compare` | サンプルが自分より奥（1 に近い）か手前（0 に近い）か |
| `sample_reach` | 手前のサンプルの速度が、自分の位置まで届くか（手前の動く物が自分にかぶさる） |
| `center_reach` | 自分の速度が奥のサンプルまで届くか（自分の動きが奥の色を混ぜる） |
| `front + back` | 手前なら「相手の速度が届く」、奥なら「自分の速度が届く」 |

考え方：手前の動く物のブラーは、奥の背景にかぶさる。奥の物が動いていても手前の静止した物にはにじまない。

```hlsl
float3 MotionBlurWeighted(float2 uv, int sample_count, float noise) {
  float center_depth = LinearDepth(uv);
  float2 center_velocity = velocity.SampleLevel(point_clamp, uv, 0).xy * resolution;
  float2 neighbor_velocity = neighbor_max.SampleLevel(point_clamp, uv, 0).xy * resolution;
  float3 sum = scene_color.SampleLevel(linear_clamp, uv, 0).rgb;
  float weight_sum = 1.0;
  [loop] for (int i = 0; i < sample_count; ++i) {
    float t = (float(i) + noise) / float(sample_count) - 0.5;
    float2 offset_px = neighbor_velocity * t;
    float2 sample_uv = uv + offset_px / resolution;
    float sample_depth = LinearDepth(sample_uv);
    float2 sample_velocity = velocity.SampleLevel(point_clamp, sample_uv, 0).xy * resolution;
    float w = SampleWeight(center_depth, sample_depth, center_velocity, sample_velocity, length(offset_px));
    sum += scene_color.SampleLevel(linear_clamp, sample_uv, 0).rgb * w;
    weight_sum += w;
  }
  return sum / weight_sum;
}
```

サンプルの方向と長さには、自分の速度ではなく、近傍の最大速度（`neighbor_velocity`）を使うことで輪郭の外側にも尾が伸びます（[Tile Max Velocity](tile-max.md)）。

## サンプル数と最大長

| 項目 | 目安 |
| --- | --- |
| サンプル数 | 8〜16（ジッターありなら 8 で足りる） |
| 最大ブラー長 | 画面の高さの 3〜5 %（それ以上の速度は切る） |
| 最小速度 | 0.5 画素未満の画素は、ブラーをスキップ |
| 解像度 | 半解像度でも見た目は大きく変わらない（合成時に境界に注意） |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 重み付き平均 | 輪郭のにじみ・かぶりを自然に（必須） |
| <strong>ジッター（ブルー ノイズ）</strong> | 少ないサンプルでなめらか |
| 近傍最大速度 | 尾の長さと方向に使う |
| 速度が小さい画素はスキップ | コスト削減 |
| TAA と併用 | ノイズをさらにならす |
| カメラ・物体を同じパスで | 速度バッファで一括処理 |

## よくあるミス

??? failure "サンプルが点の列に見える（縞）"
    <strong>画素ごとのジッター</strong>を入れる。

??? failure "静止した前景に、背景の動きがにじむ"
    深度と速度の重み付けを使う。

??? failure "速い物体の輪郭で、ぼかしが切れる"
    近傍の最大速度を使い、尾を輪郭の外へ伸ばす。

??? failure "サンプル数を増やしても、重いだけで効果が少ない"
    ジッターでノイズ化する方が効く。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ぼかし ＝ <strong>速度に沿って前後にサンプルして平均</strong>
    - [x] 画素ごとのジッターで縞をノイズに
    - [x] 深度と速度の重み付けで前景・背景の破綻を防ぐ
    - [x] 近傍最大速度で輪郭の外にも尾を伸ばす
    - [x] 最大長で制限、遅い画素はスキップ

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）

## 関連ページ

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Tile Max Velocity](tile-max.md)
- [Strength and TAA](strength-taa.md)

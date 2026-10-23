---
title: Lens Flare
tags:
  - 描画
---

# Lens Flare

<strong>太陽やライトのような、とても明るい光源がレンズに入る</strong>と、レンズの内部で光が何度も反射し、画面に「ゴースト（光の円）」「ハロー（輪）」「光芒（スターバースト）」が現れます。これがレンズ フレアで、SF・映画・夕暮れの太陽の演出に欠かせません。表現の好みの問題であれば高品質というわけではありません。このページでは、フレアの種類・画面空間でのゴースト生成・ハロー・光芒（スターバースト）・色と減衰・コストとオクルージョンを説明します。

!!! tip "ポイント"
    - レンズ フレア ＝ <strong>レンズ内の反射で、強い光源から出る、ゴースト・ハロー・光芒</strong>。
    - <strong>ゴースト</strong> ＝ 光源を、画面中心を挟んで反対側に、複数の円として並べる。
    - 画面空間の方法：ブルームの明るい部分を取り出し、反転・ずらしてサンプルする（光源の位置を知らなくてよい）。
    - ハロー ＝ 画面中心を軸にした、大きな輪。光芒 ＝ 絞りの羽根による筋。
    - 画面端のゴーストは弱める。色収差を付けると虹色でリアル。
    - 光源が隠れたら消えるよう、オクルージョンを考慮する。

!!! info "このページを読む前に"
    - [Lens Effects](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 要素

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="レンズ フレアの要素">
<text x="20" y="26" class="fig-title">フレアの要素：ゴーストは、画面中心を挟んで反対側に並ぶ</text>
<g transform="translate(40,52)">
<rect x="0" y="0" width="460" height="170" fill="#0f172a"/>
<circle cx="380" cy="40" r="16" fill="#fff7d1"/><text x="350" y="76" style="font-size:12px;fill:#fff">光源</text>
<line x1="380" y1="40" x2="80" y2="130" stroke="#fff" stroke-opacity="0.3" stroke-dasharray="4 3"/>
<circle cx="230" cy="85" r="4" fill="#fff"/>
<circle cx="300" cy="64" r="12" fill="#5fa8ff" fill-opacity="0.45"/><circle cx="215" cy="90" r="18" fill="#ffd27a" fill-opacity="0.4"/><circle cx="150" cy="108" r="26" fill="#ff8aa0" fill-opacity="0.3"/><circle cx="90" cy="125" r="14" fill="#8affc1" fill-opacity="0.4"/>
<circle cx="230" cy="85" r="85" fill="none" stroke="#fff" stroke-opacity="0.25" stroke-width="6"/>
<text x="6" y="164" style="font-size:12px;fill:#fff">画面中心（白い点）を軸に、反対側にゴースト</text>
</g>
<g font-size="13"><text x="530" y="90" style="font-weight:700">要素</text>
<text x="530" y="116">ゴースト：光源の像の円</text>
<text x="530" y="140">ハロー：中心を囲む輪</text>
<text x="530" y="164">光芒：光源から伸びる筋</text>
<text x="530" y="188">ストリーク：横に伸びる光</text></g>
</svg>

| 要素 | 内容 | 原因 |
| --- | --- | --- |
| ゴースト | 光源の像が画面中心を挟んで反対側に、複数の円として現れる | レンズ面での多重反射 |
| ハロー | 画面中心を中心にした、大きな輪 | レンズ構成の光学的な効果 |
| <strong>光芒（スターバースト）</strong> | 光源から放射状に伸びる筋（羽根の数 × 2 本など） | 絞りの羽根による回折 |
| ストリーク | 横に長く伸びる光 | アナモルフィック レンズ（映画的） |

## 画面空間のゴースト

<strong>ブルームで明るい部分を取り出した画像</strong>から、反転した位置を複数回サンプルして、ゴーストを作る方法です（光源の位置を別に知る必要がありません）。

```hlsl
float3 LensFlareGhosts(float2 uv, int ghost_count, float dispersal, float distortion) {
  float2 flipped_uv = 1.0 - uv;
  float2 ghost_vector = (0.5 - flipped_uv) * dispersal;

  float3 result = 0.0;
  [loop] for (int i = 0; i < ghost_count; ++i) {
    float2 offset = frac(flipped_uv + ghost_vector * float(i));
    float weight = length(0.5 - offset) / length(float2(0.5, 0.5));
    weight = pow(1.0 - weight, 10.0);
    result += bright_texture.SampleLevel(linear_clamp, offset, 0).rgb * weight;
  }
  return result;
}
```

| 点 | 説明 |
| --- | --- |
| `flipped_uv = 1 − uv` | 画面中心に対して、反転した位置 |
| `ghost_vector` | 反転位置から画面中心へ向かうベクトル。`dispersal` で間隔を調整 |
| `weight` | 画面の端のゴーストを弱める（中心付近が強い） |
| `bright_texture` | ブルームの明るい部分の抽出画像（半解像度） |
| `frac` | 画面の外へ出たら、反対側に折り返す |

<!-- fig:lens-flare-ghosts:begin -->

<svg class="fig illust motion" data-fig="lens-flare-ghosts" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lens-flare-ghosts" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">レンズ フレア(ゴースト): 光源から画面の中心を通る直線の上に、レンズの反射の像が、並ぶ</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">画面(16:9)の中の光源の位置が動くと、ゴーストの位置は、中心から見た対称の位置に動く。ゴーストの倍率 = −1.2, −0.6, 0.4, 0.9</text>
<rect x="30.0" y="100.0" width="640.0" height="360.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30.0" y="90.0" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">画面(中心から、光源・ゴーストの位置)</text>
<circle cx="350.0" cy="280.0" r="4" fill="#1f2937"/>
<line x1="30.0" y1="280.0" x2="670.0" y2="280.0" stroke="#e2e8f0" stroke-width="1.2"/>
<line x1="350.0" y1="100.0" x2="350.0" y2="460.0" stroke="#e2e8f0" stroke-width="1.2"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;1.0000" values="1;1;0;0"/><line x1="126.0" y1="199.0" x2="618.8" y2="377.2" stroke="#e5484d" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="618.8" cy="377.2" r="17.2" fill="#e5484d" fill-opacity="0.28" stroke="#e5484d" stroke-width="2"/>
<line x1="126.0" y1="199.0" x2="484.4" y2="328.6" stroke="#e5aa28" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="484.4" cy="328.6" r="13.6" fill="#e5aa28" fill-opacity="0.28" stroke="#e5aa28" stroke-width="2"/>
<line x1="126.0" y1="199.0" x2="260.4" y2="247.6" stroke="#2ea043" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="260.4" cy="247.6" r="12.4" fill="#2ea043" fill-opacity="0.28" stroke="#2ea043" stroke-width="2"/>
<line x1="126.0" y1="199.0" x2="148.4" y2="207.1" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="148.4" cy="207.1" r="15.4" fill="#2563eb" fill-opacity="0.28" stroke="#2563eb" stroke-width="2"/>
<circle cx="126.0" cy="199.0" r="11" fill="#e5aa28" stroke="#ffffff" stroke-width="2.5"/>
<text x="140.0" y="187.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">光源</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/><line x1="254.0" y1="244.0" x2="465.2" y2="323.2" stroke="#e5484d" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="465.2" cy="323.2" r="17.2" fill="#e5484d" fill-opacity="0.28" stroke="#e5484d" stroke-width="2"/>
<line x1="254.0" y1="244.0" x2="407.6" y2="301.6" stroke="#e5aa28" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="407.6" cy="301.6" r="13.6" fill="#e5aa28" fill-opacity="0.28" stroke="#e5aa28" stroke-width="2"/>
<line x1="254.0" y1="244.0" x2="311.6" y2="265.6" stroke="#2ea043" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="311.6" cy="265.6" r="12.4" fill="#2ea043" fill-opacity="0.28" stroke="#2ea043" stroke-width="2"/>
<line x1="254.0" y1="244.0" x2="263.6" y2="247.6" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="263.6" cy="247.6" r="15.4" fill="#2563eb" fill-opacity="0.28" stroke="#2563eb" stroke-width="2"/>
<circle cx="254.0" cy="244.0" r="11" fill="#e5aa28" stroke="#ffffff" stroke-width="2.5"/>
<text x="268.0" y="232.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">光源</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;0.6665;0.6667;1.0000" values="0;0;1;1;0;0"/><line x1="414.0" y1="325.0" x2="273.2" y2="226.0" stroke="#e5484d" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="273.2" cy="226.0" r="17.2" fill="#e5484d" fill-opacity="0.28" stroke="#e5484d" stroke-width="2"/>
<line x1="414.0" y1="325.0" x2="311.6" y2="253.0" stroke="#e5aa28" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="311.6" cy="253.0" r="13.6" fill="#e5aa28" fill-opacity="0.28" stroke="#e5aa28" stroke-width="2"/>
<line x1="414.0" y1="325.0" x2="375.6" y2="298.0" stroke="#2ea043" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="375.6" cy="298.0" r="12.4" fill="#2ea043" fill-opacity="0.28" stroke="#2ea043" stroke-width="2"/>
<line x1="414.0" y1="325.0" x2="407.6" y2="320.5" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="407.6" cy="320.5" r="15.4" fill="#2563eb" fill-opacity="0.28" stroke="#2563eb" stroke-width="2"/>
<circle cx="414.0" cy="325.0" r="11" fill="#e5aa28" stroke="#ffffff" stroke-width="2.5"/>
<text x="428.0" y="313.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">光源</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6665;0.6667;1.0000" values="0;0;1;1"/><line x1="558.0" y1="352.0" x2="100.4" y2="193.6" stroke="#e5484d" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="100.4" cy="193.6" r="17.2" fill="#e5484d" fill-opacity="0.28" stroke="#e5484d" stroke-width="2"/>
<line x1="558.0" y1="352.0" x2="225.2" y2="236.8" stroke="#e5aa28" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="225.2" cy="236.8" r="13.6" fill="#e5aa28" fill-opacity="0.28" stroke="#e5aa28" stroke-width="2"/>
<line x1="558.0" y1="352.0" x2="433.2" y2="308.8" stroke="#2ea043" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="433.2" cy="308.8" r="12.4" fill="#2ea043" fill-opacity="0.28" stroke="#2ea043" stroke-width="2"/>
<line x1="558.0" y1="352.0" x2="537.2" y2="344.8" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.7"/>
<circle cx="537.2" cy="344.8" r="15.4" fill="#2563eb" fill-opacity="0.28" stroke="#2563eb" stroke-width="2"/>
<circle cx="558.0" cy="352.0" r="11" fill="#e5aa28" stroke="#ffffff" stroke-width="2.5"/>
<text x="572.0" y="340.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">光源</text>
</g>
<rect x="690" y="100" width="240" height="360" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="690" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">ゴーストの位置</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;1.0000" values="1;1;0;0"/><text x="706" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">光源 (-0.70, 0.45)</text>
<text x="706" y="174" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">×-1.2 → (0.84, -0.54)</text>
<text x="706" y="210" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">×-0.6 → (0.42, -0.27)</text>
<text x="706" y="246" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">×+0.4 → (-0.28, 0.18)</text>
<text x="706" y="282" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">×+0.9 → (-0.63, 0.41)</text>
<text x="706" y="340" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">光源が中心から遠いほど、</text>
<text x="706" y="358" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ゴーストも、遠くに離れる</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/><text x="706" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">光源 (-0.30, 0.20)</text>
<text x="706" y="174" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">×-1.2 → (0.36, -0.24)</text>
<text x="706" y="210" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">×-0.6 → (0.18, -0.12)</text>
<text x="706" y="246" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">×+0.4 → (-0.12, 0.08)</text>
<text x="706" y="282" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">×+0.9 → (-0.27, 0.18)</text>
<text x="706" y="340" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">光源が中心から遠いほど、</text>
<text x="706" y="358" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ゴーストも、遠くに離れる</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;0.6665;0.6667;1.0000" values="0;0;1;1;0;0"/><text x="706" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">光源 (0.20, -0.25)</text>
<text x="706" y="174" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">×-1.2 → (-0.24, 0.30)</text>
<text x="706" y="210" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">×-0.6 → (-0.12, 0.15)</text>
<text x="706" y="246" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">×+0.4 → (0.08, -0.10)</text>
<text x="706" y="282" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">×+0.9 → (0.18, -0.23)</text>
<text x="706" y="340" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">光源が中心から遠いほど、</text>
<text x="706" y="358" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ゴーストも、遠くに離れる</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6665;0.6667;1.0000" values="0;0;1;1"/><text x="706" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">光源 (0.65, -0.40)</text>
<text x="706" y="174" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">×-1.2 → (-0.78, 0.48)</text>
<text x="706" y="210" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">×-0.6 → (-0.39, 0.24)</text>
<text x="706" y="246" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">×+0.4 → (0.26, -0.16)</text>
<text x="706" y="282" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">×+0.9 → (0.59, -0.36)</text>
<text x="706" y="340" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">光源が中心から遠いほど、</text>
<text x="706" y="358" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ゴーストも、遠くに離れる</text>
</g>
<text x="40" y="480" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">画面に入っているゴースト:</text>
<text x="240" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="240" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.2798;0.2800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;0.4798;0.4800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4798;0.4800;0.6798;0.6800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6798;0.6800;1.0000" values="0;0;1;1"/></text>
<text x="280" y="484" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">個(4 個中)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8443;0.8444;1.0000" values="0;0;1;1"/><rect x="480" y="470" width="450" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="494" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1e3a8a">光源が画面の端にあるほど、ゴーストが広く散る。中心では、全部が重なる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">レンズの中で光が反射して、光源の像が、何個か、ずれて写る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ゴーストは、光源の位置 × 倍率(負なら反対側)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8665;0.8667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">簡単な式で、位置が決まる。画面の端は、フェードで消す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:lens-flare-ghosts:end -->

## ハロー

<strong>画面中心を中心にした、大きな輪</strong>を足します。反転位置から、中心方向へ一定の長さだけ進んだ位置をサンプルします。

```hlsl
float3 LensFlareHalo(float2 uv, float halo_width) {
  float2 flipped_uv = 1.0 - uv;
  float2 direction = normalize(0.5 - flipped_uv);
  float2 halo_vector = direction * halo_width;
  float weight = length(0.5 - frac(flipped_uv + halo_vector)) / length(float2(0.5, 0.5));
  weight = pow(1.0 - weight, 5.0);
  return bright_texture.SampleLevel(linear_clamp, flipped_uv + halo_vector, 0).rgb * weight;
}
```

ハローのコードの要点です。`halo_width` は輪の半径で、0.4〜0.6 程度です。向きを正規化して、どの画素でも同じ長さにすると、輪になります。

## 色と色収差

<strong>ゴーストやハローに色（虹色）</strong>を付けるとリアルになります。

ゴーストやハローに色（虹色）を付けると、リアルになります。方法は 3 つです。ゴーストごとに色を変える（1 つ目は青、2 つ目は橙など）。色収差を付けて、R・G・B を少しずつずらしてサンプルする（[Chromatic Aberration](chromatic-aberration.md)）。画面中心からの距離で色を引く、グラデーションの 1D テクスチャを使う方法です。

```hlsl
float3 flare_color = color_gradient.SampleLevel(linear_clamp, float2(length(0.5 - offset) / 0.707, 0.5), 0).rgb;
result += bright * weight * flare_color;
```

## 光芒（スターバースト）

<strong>絞りの羽根の数に応じた、星形の筋</strong>です。テクスチャを光源の位置に貼るのが簡単です。

光芒は、絞りの羽根の数に応じた星形の筋で、テクスチャを光源の位置に貼る方法が簡単です。スターバースト テクスチャは、星形のテクスチャを画面中心からの角度で回して、ブルームに乗算します。ダート テクスチャは、レンズの汚れや傷のテクスチャを画面全体に重ね、ブルームの強さに乗算します（[Compositing and Intensity](../bloom/composite.md)）。光源の位置を投影して、スプライトを描く方法もあります。

```hlsl
float3 Starburst(float2 uv, float2 light_uv, Texture2D starburst_texture, float intensity) {
  float2 d = uv - light_uv;
  float angle = atan2(d.y, d.x);
  float2 star_uv = float2(angle / 6.28318530718 + 0.5, 0.5);
  return starburst_texture.SampleLevel(linear_wrap, star_uv, 0).rgb * intensity;
}
```

## 光源が隠れたとき

<strong>太陽が建物に隠れたのに、フレアが残る</strong>と不自然です。光源の可視性（オクルージョン）を考慮します。

| 方式 | 内容 |
| --- | --- |
| 画面空間（ブルーム抽出）なら自動 | 隠れた光源は画面で明るくない → フレアも出ない |
| 光源位置にスプライトを描く場合 | 光源位置の深度で可視性を判定（オクルージョン クエリ・深度の読み取り） |
| 画面外の光源 | 画面の外の太陽は、画面空間では抽出できない。別途（光源位置から）スプライト |
| 可視性のフェード | 見える面積の割合で強さを滑らかに |

## コスト

| 項目 | 目安 |
| --- | --- |
| ブルームの抽出画像を再利用 | 追加の抽出は不要 |
| ゴースト ＋ ハロー | 半解像度でサンプル 5〜10 回 → 軽い |
| スターバースト・ダート | テクスチャ 1〜2 枚 → 軽い |
| ぼかし | <strong>ゴーストを少しぼかすと、なめらか（半解像度なら、安い）</strong> |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| ブルームの画像を使い回す | 別の抽出を避ける |
| 半解像度で作る | コストを 1/4 |
| 端のゴーストを弱める | 中心付近が強い |
| 色収差・グラデーション | 虹色でリアル |
| かけすぎない | 控えめで光源が主役のまま |
| 光源の可視性を考慮 | 隠れたら消える |
| 強さを光源の明るさで | 強い光だけ、フレア |

## よくあるミス

??? failure "画面端にゴーストが出て、不自然に光る"
    <strong>端の重みを弱める</strong>（`weight = pow(1 − 距離, 10)`）。

??? failure "光源が隠れても、フレアが残る"
    可視性を考慮する。画面空間なら、自動で消える。

??? failure "画面全体がフレアで真っ白になる"
    強さ・閾値を下げる。明るい光源だけがフレアを出す。

??? failure "ゴーストがぎざぎざに見える"
    半解像度のぼかしを足す、バイリニアで滑らかに。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レンズ フレア ＝ <strong>強い光源から出る、ゴースト・ハロー・光芒</strong>
    - [x] 画面空間：ブルームの明るい部分を、反転・ずらしてサンプル
    - [x] ゴーストは、画面中心を挟んで反対側。端は弱める。色収差で虹色
    - [x] 光芒・ダートはテクスチャで
    - [x] 隠れた光源は消えるように。控えめに

## 参考

- Hullin et al., "Physically-Based Real-Time Lens Flare Rendering"（SIGGRAPH 2011）
- Chapman, "Pseudo Lens Flare"（john-chapman-graphics.blogspot.com, 2013）

## 関連ページ

- [Lens Effects](index.md)
- [Chromatic Aberration](chromatic-aberration.md)
- [Bloom](../bloom/index.md)
- [God Rays](../../atmosphere/god-rays/index.md)

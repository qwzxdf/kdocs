---
title: Steps 3 and 4: Integration and Application
tags:
  - 描画
---

# Steps 3 and 4: Integration and Application

**注入した光を、視線に沿って奥から手前へ足し合わせます（積分）**。**その結果を、シーンの色に合成（適用）します**。このページでは、**積分と適用**を説明します。

!!! tip "ポイント"
    - **奥行き方向に、散乱光を累積し、透過率も求める**。
    - **結果は、3D テクスチャ（累積済み）**。
    - **適用：シーンの色 × 透過率 ＋ 散乱光**。
    - **シーンの深度から、froxel の位置を引く**。

## ③ 積分
**視線に沿って、手前から奥へ光と透過率を累積します**。**奥行き方向（Z）にループ**し、**各 froxel の寄与を足します**。

<div class="formula">
累積光 += 透過率 × 散乱光 × (1 − exp(−消散 × 厚み)) / 消散<br>
透過率 *= exp(−消散 × 厚み)
</div>

```hlsl
[numthreads(8, 8, 1)]
void IntegrateCS(uint3 id : SV_DispatchThreadID) {
  float3 accumulated = 0;
  float transmittance = 1.0;

  for (uint z = 0; z < kSliceCount; ++z) {
    float4 data = scattering_volume[uint3(id.xy, z)];
    float3 scattering = data.rgb;
    float extinction = max(data.a, 1e-5);

    float thickness = SliceThickness(z);
    float slice_transmittance = exp(-extinction * thickness);
    float3 integrated = (scattering - scattering * slice_transmittance) / extinction;

    accumulated += integrated * transmittance;
    transmittance *= slice_transmittance;

    integrated_volume[uint3(id.xy, z)] = float4(accumulated, transmittance);
  }
}
```

積分のコードの要点です。スライスの厚みは奥ほど大きいので、厚みを考慮して積分を厳密にします。区間内の透過率を指数で厳密に扱うので（解析的な積分）、粗いステップでも安定します。結果は 3D テクスチャに保存し、各スライスまでの累積を適用時に、深度に応じた位置で引きます。1 つのスレッドが奥まで受け持ち、画面方向は並列、奥行き方向は順次処理です。

<!-- fig:fog-integrate:begin -->

<svg class="fig illust motion" data-fig="fog-integrate" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-fog-integrate" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">スライスを手前から奥へ累積する: 光は足され、透過率は掛けられる</text>
<rect x="90" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="90" y="160.0" width="46" height="0.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="113.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<rect x="140" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="140" y="154.0" width="46" height="6.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="163.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2</text>
<rect x="190" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="190" y="130.0" width="46" height="30.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="213.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">3</text>
<rect x="240" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="240" y="106.0" width="46" height="54.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="263.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<rect x="290" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="290" y="142.0" width="46" height="18.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="313.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">5</text>
<rect x="340" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="340" y="154.0" width="46" height="6.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="363.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">6</text>
<rect x="390" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="390" y="160.0" width="46" height="0.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="413.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">7</text>
<rect x="440" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="440" y="124.0" width="46" height="36.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="463.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">8</text>
<rect x="490" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="490" y="112.0" width="46" height="48.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="513.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">9</text>
<rect x="540" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="540" y="148.0" width="46" height="12.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="563.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">10</text>
<rect x="590" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="590" y="154.0" width="46" height="6.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="613.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">11</text>
<rect x="640" y="100" width="46" height="60" fill="#e0f2fe" stroke="#94a3b8" stroke-width="1"/>
<rect x="640" y="160.0" width="46" height="0.0" fill="#e5aa28" fill-opacity="0.8"/>
<text x="663.0" y="178" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">12</text>
<text x="90" y="92" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">各スライスの散乱光（橙の高さ）</text>
<rect x="90" y="215" width="600" height="140" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="240.0" y1="215" x2="240.0" y2="355" stroke="#e2e8f0" stroke-width="1"/>
<line x1="90" y1="250.0" x2="690" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="215" x2="390.0" y2="355" stroke="#e2e8f0" stroke-width="1"/>
<line x1="90" y1="285.0" x2="690" y2="285.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="540.0" y1="215" x2="540.0" y2="355" stroke="#e2e8f0" stroke-width="1"/>
<line x1="90" y1="320.0" x2="690" y2="320.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="90" y="207" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">累積した光（橙）／ 透過率（青）</text>
<path d="M0,0" fill="none" stroke="#e5aa28" stroke-width="4"><animate attributeName="d" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1296;0.1852;0.2407;0.2963;0.3519;0.4074;0.4630;0.5185;0.5741;0.6296;0.6852;0.7407;1.0000" values="M90.0,355.0 L140.0,355.0 L190.0,355.0 L240.0,355.0 L290.0,355.0 L340.0,355.0 L390.0,355.0 L440.0,355.0 L490.0,355.0 L540.0,355.0 L590.0,355.0 L640.0,355.0 L690.0,355.0;M90.0,355.0 L140.0,355.0 L190.0,355.0 L240.0,355.0 L290.0,355.0 L340.0,355.0 L390.0,355.0 L440.0,355.0 L490.0,355.0 L540.0,355.0 L590.0,355.0 L640.0,355.0 L690.0,355.0;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,346.03 L290.0,346.03 L340.0,346.03 L390.0,346.03 L440.0,346.03 L490.0,346.03 L540.0,346.03 L590.0,346.03 L640.0,346.03 L690.0,346.03;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,310.13 L340.0,310.13 L390.0,310.13 L440.0,310.13 L490.0,310.13 L540.0,310.13 L590.0,310.13 L640.0,310.13 L690.0,310.13;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,264.46 L390.0,264.46 L440.0,264.46 L490.0,264.46 L540.0,264.46 L590.0,264.46 L640.0,264.46 L690.0,264.46;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,253.51 L440.0,253.51 L490.0,253.51 L540.0,253.51 L590.0,253.51 L640.0,253.51 L690.0,253.51;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,250.52 L540.0,250.52 L590.0,250.52 L640.0,250.52 L690.0,250.52;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,250.52 L540.0,250.52 L590.0,250.52 L640.0,250.52 L690.0,250.52;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,237.55 L540.0,237.55 L590.0,237.55 L640.0,237.55 L690.0,237.55;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,237.55 L540.0,225.03 L590.0,225.03 L640.0,225.03 L690.0,225.03;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,237.55 L540.0,225.03 L590.0,222.66 L640.0,222.66 L690.0,222.66;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,237.55 L540.0,225.03 L590.0,222.66 L640.0,221.67 L690.0,221.67;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,237.55 L540.0,225.03 L590.0,222.66 L640.0,221.67 L690.0,221.67;M90.0,355.0 L140.0,355.0 L190.0,346.03 L240.0,310.13 L290.0,264.46 L340.0,253.51 L390.0,250.52 L440.0,250.52 L490.0,237.55 L540.0,225.03 L590.0,222.66 L640.0,221.67 L690.0,221.67"/></path>
<path d="M0,0" fill="none" stroke="#2563eb" stroke-width="4"><animate attributeName="d" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1296;0.1852;0.2407;0.2963;0.3519;0.4074;0.4630;0.5185;0.5741;0.6296;0.6852;0.7407;1.0000" values="M90.0,215.0 L140.0,228.32 L190.0,228.32 L240.0,228.32 L290.0,228.32 L340.0,228.32 L390.0,228.32 L440.0,228.32 L490.0,228.32 L540.0,228.32 L590.0,228.32 L640.0,228.32 L690.0,228.32;M90.0,215.0 L140.0,228.32 L190.0,228.32 L240.0,228.32 L290.0,228.32 L340.0,228.32 L390.0,228.32 L440.0,228.32 L490.0,228.32 L540.0,228.32 L590.0,228.32 L640.0,228.32 L690.0,228.32;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,245.97 L290.0,245.97 L340.0,245.97 L390.0,245.97 L440.0,245.97 L490.0,245.97 L540.0,245.97 L590.0,245.97 L640.0,245.97 L690.0,245.97;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,274.23 L340.0,274.23 L390.0,274.23 L440.0,274.23 L490.0,274.23 L540.0,274.23 L590.0,274.23 L640.0,274.23 L690.0,274.23;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,300.86 L390.0,300.86 L440.0,300.86 L490.0,300.86 L540.0,300.86 L590.0,300.86 L640.0,300.86 L690.0,300.86;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,312.83 L440.0,312.83 L490.0,312.83 L540.0,312.83 L590.0,312.83 L640.0,312.83 L690.0,312.83;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,318.71 L490.0,318.71 L540.0,318.71 L590.0,318.71 L640.0,318.71 L690.0,318.71;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,322.16 L490.0,322.16 L540.0,322.16 L590.0,322.16 L640.0,322.16 L690.0,322.16;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,322.16 L490.0,330.67 L540.0,330.67 L590.0,330.67 L640.0,330.67 L690.0,330.67;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,322.16 L490.0,330.67 L540.0,337.86 L590.0,337.86 L640.0,337.86 L690.0,337.86;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,322.16 L490.0,330.67 L540.0,337.86 L590.0,340.96 L640.0,340.96 L690.0,340.96;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,322.16 L490.0,330.67 L540.0,337.86 L590.0,340.96 L640.0,342.92 L690.0,342.92;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,322.16 L490.0,330.67 L540.0,337.86 L590.0,340.96 L640.0,342.92 L690.0,344.07;M90.0,215.0 L140.0,228.32 L190.0,245.97 L240.0,274.23 L290.0,300.86 L340.0,312.83 L390.0,318.71 L440.0,322.16 L490.0,330.67 L540.0,337.86 L590.0,340.96 L640.0,342.92 L690.0,344.07"/></path>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 1 まで: 累積光 0.00、透過率 0.90<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1293;0.1296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 2 まで: 累積光 0.08、透過率 0.78<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1293;0.1296;0.1849;0.1852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 3 まで: 累積光 0.42、透過率 0.58<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1849;0.1852;0.2404;0.2407;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 4 まで: 累積光 0.85、透過率 0.39<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2404;0.2407;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 5 まで: 累積光 0.95、透過率 0.30<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3516;0.3519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 6 まで: 累積光 0.98、透過率 0.26<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3516;0.3519;0.4071;0.4074;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 7 まで: 累積光 0.98、透過率 0.23<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4071;0.4074;0.4627;0.4630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 8 まで: 累積光 1.10、透過率 0.17<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4627;0.4630;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 9 まで: 累積光 1.22、透過率 0.12<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;0.5738;0.5741;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 10 まで: 累積光 1.24、透過率 0.10<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5738;0.5741;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 11 まで: 累積光 1.25、透過率 0.09<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;0.6849;0.6852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">スライス 12 まで: 累積光 1.25、透過率 0.08<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6849;0.6852;0.7404;0.7407;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="422" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">光 += 透過率 × (S − S·e^(−σΔz)) / σ　　透過率 ×= e^(−σΔz)</text>
</svg>

<!-- fig:fog-integrate:end -->

## ④ 適用
**不透明のシーンの色に積分結果を合成します**。**ピクセルの深度から、対応するスライスを求めて、3D テクスチャを引きます**。

```hlsl
float depth = LinearizeDepth(depth_texture.Sample(point_clamp, uv).r);
float slice = DepthToSlice(depth, kNear, kFar, kSliceCount);
float3 froxel_uvw = float3(uv, slice / kSliceCount);
float4 fog = integrated_volume.SampleLevel(linear_clamp, froxel_uvw, 0);

float3 final_color = scene_color * fog.a + fog.rgb;
```

適用のコードの要点です。`fog.a` は透過率で、シーンの色に掛けます。`fog.rgb` は散乱光で、足します。三線形補間で、froxel の粗さを滑らかにします。半透明の物体も、ピクセル シェーダーの中で同じ式を適用します。

### 積分式の導出

累積の式が、なぜこの形なのかを確認します。1 つのスライスの内側で、散乱光 S（単位長さあたりに散乱される光）と消散 σ が一定だとします。スライスの手前の端から距離 x の位置で散乱された光は、スライスの手前の端に届くまでに `exp(−σ x)` の割合に弱まります。スライス全体で足し合わせると、次の積分になります。

<div class="formula">∫₀^Δz S · exp(−σ x) dx = S · (1 − exp(−σ Δz)) / σ</div>

コードの `(scattering - scattering * slice_transmittance) / extinction` が、まさにこれです。この<strong>区間内の解析積分</strong>がポイントです。単純に `scattering * thickness` を足すだけでは、密度が高いときにエネルギーが保存されず、濃い霧で光が過剰になります（特に、スライスが厚い遠方）。解析積分なら、どんなに濃くても、光の量が上限（S / σ）を超えません。この定式化は、Hillaire の Frostbite の発表で広まりました。

スライス全体を手前から奥へ回し、それまでの透過率 `transmittance` を、現在のスライスの寄与に掛けてから足します。手前の濃い霧は、奥の光を隠すので、奥の寄与が手前の透過率で減衰します。この累積を、スライスごとに保存すれば、適用のときは、画素の深度に対応するスライスの値を 1 回引くだけで、「カメラからその距離までの全フォグ」が得られます。

## よくあるミス

??? failure "積分の結果が、手前の物にも霧がかかる"
    **物体の深度**で**積分の位置を引く**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **奥から累積して、深度で引いて合成**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Volumetric Fog](index.md)
- [光の注入](injection.md)
- [時間蓄積](temporal.md)

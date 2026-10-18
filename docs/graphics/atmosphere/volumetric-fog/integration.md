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

| 点 | 説明 |
| --- | --- |
| **厚みを考慮** | **スライスの厚みは奥ほど大きい**ので、**厚みで積分を厳密に**する |
| **解析的な積分** | **区間内の透過率を指数で厳密に**（粗いステップでも安定） |
| **結果を 3D テクスチャに保存** | **各スライスまでの累積**を保存し、**適用時に深度に応じた位置を引く** |
| **1 スレッドが奥まで** | **画面方向は並列、奥行き方向は順次** |

<!-- fig:fog-integrate:begin -->

<svg class="fig illust motion" data-fig="fog-integrate" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-fog-integrate" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">霧の積分: 手前の層から順に、「光が減った分」と「霧が足した光」を積み重ねる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 本の視線を、奥行き 16 枚のスライス(froxel)に分けて、前から順に積算する。霧の塊が、途中にある</text>
<rect x="30" y="96" width="900" height="150" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 各スライス(手前 → 奥)の、霧の濃さ</text>
<rect x="60.0" y="219.67" width="48.0" height="8.33" fill="#93c5fd" opacity="0.9"/>
<text x="84.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">0.6 m</text>
<rect x="111.5" y="219.66" width="48.0" height="8.34" fill="#93c5fd" opacity="0.9"/>
<text x="135.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">0.8 m</text>
<rect x="163.0" y="219.63" width="48.0" height="8.37" fill="#93c5fd" opacity="0.9"/>
<text x="187.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">1.1 m</text>
<rect x="214.5" y="219.57" width="48.0" height="8.43" fill="#93c5fd" opacity="0.9"/>
<text x="238.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">1.5 m</text>
<rect x="266.0" y="219.46" width="48.0" height="8.54" fill="#93c5fd" opacity="0.9"/>
<text x="290.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">2 m</text>
<rect x="317.5" y="219.19" width="48.0" height="8.81" fill="#93c5fd" opacity="0.9"/>
<text x="341.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">2.7 m</text>
<rect x="369.0" y="218.48" width="48.0" height="9.52" fill="#93c5fd" opacity="0.9"/>
<text x="393.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">3.6 m</text>
<rect x="420.5" y="216.32" width="48.0" height="11.68" fill="#93c5fd" opacity="0.9"/>
<text x="444.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">4.9 m</text>
<rect x="472.0" y="208.98" width="48.0" height="19.02" fill="#93c5fd" opacity="0.9"/>
<text x="496.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">6.7 m</text>
<rect x="523.5" y="185.33" width="48.0" height="42.67" fill="#93c5fd" opacity="0.9"/>
<text x="547.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">9 m</text>
<rect x="575.0" y="138.0" width="48.0" height="90.0" fill="#93c5fd" opacity="0.9"/>
<text x="599.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">12.2 m</text>
<rect x="626.5" y="147.96" width="48.0" height="80.04" fill="#93c5fd" opacity="0.9"/>
<text x="650.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">16.5 m</text>
<rect x="678.0" y="214.21" width="48.0" height="13.79" fill="#93c5fd" opacity="0.9"/>
<text x="702.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">22.4 m</text>
<rect x="729.5" y="219.74" width="48.0" height="8.26" fill="#93c5fd" opacity="0.9"/>
<text x="753.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">30.3 m</text>
<rect x="781.0" y="219.74" width="48.0" height="8.26" fill="#93c5fd" opacity="0.9"/>
<text x="805.0" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">41.1 m</text>
<rect x="832.5" y="219.74" width="48.0" height="8.26" fill="#93c5fd" opacity="0.9"/>
<text x="856.5" y="240" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">55.6 m</text>
<text x="40" y="126" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">棒 = そのスライスの霧の濃さ(中央が、霧の塊)。スライスの厚みは、奥ほど厚い</text>
<rect x="30" y="262" width="900" height="160" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="252" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 積算の途中経過(前から順に)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="0;0;1;1"/><rect x="60.0" y="300.07" width="23.0" height="99.93" fill="#c4b5fd" opacity="0.95"/>
<rect x="84.0" y="399.95" width="23.0" height="0.05" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1021;1.0000" values="0;0;1;1"/><rect x="111.5" y="300.17" width="23.0" height="99.83" fill="#c4b5fd" opacity="0.95"/>
<rect x="135.5" y="399.89" width="23.0" height="0.11" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1403;0.1404;1.0000" values="0;0;1;1"/><rect x="163.0" y="300.3" width="23.0" height="99.7" fill="#c4b5fd" opacity="0.95"/>
<rect x="187.0" y="399.81" width="23.0" height="0.19" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1786;0.1787;1.0000" values="0;0;1;1"/><rect x="214.5" y="300.48" width="23.0" height="99.52" fill="#c4b5fd" opacity="0.95"/>
<rect x="238.5" y="399.69" width="23.0" height="0.31" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2170;1.0000" values="0;0;1;1"/><rect x="266.0" y="300.72" width="23.0" height="99.28" fill="#c4b5fd" opacity="0.95"/>
<rect x="290.0" y="399.52" width="23.0" height="0.48" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;1.0000" values="0;0;1;1"/><rect x="317.5" y="301.07" width="23.0" height="98.93" fill="#c4b5fd" opacity="0.95"/>
<rect x="341.5" y="399.29" width="23.0" height="0.71" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2934;0.2936;1.0000" values="0;0;1;1"/><rect x="369.0" y="301.56" width="23.0" height="98.44" fill="#c4b5fd" opacity="0.95"/>
<rect x="393.0" y="398.94" width="23.0" height="1.06" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="0;0;1;1"/><rect x="420.5" y="302.38" width="23.0" height="97.62" fill="#c4b5fd" opacity="0.95"/>
<rect x="444.5" y="398.33" width="23.0" height="1.67" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3700;0.3702;1.0000" values="0;0;1;1"/><rect x="472.0" y="304.17" width="23.0" height="95.83" fill="#c4b5fd" opacity="0.95"/>
<rect x="496.0" y="396.89" width="23.0" height="3.11" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4083;0.4085;1.0000" values="0;0;1;1"/><rect x="523.5" y="309.4" width="23.0" height="90.6" fill="#c4b5fd" opacity="0.95"/>
<rect x="547.5" y="392.21" width="23.0" height="7.79" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4466;0.4468;1.0000" values="0;0;1;1"/><rect x="575.0" y="322.81" width="23.0" height="77.19" fill="#c4b5fd" opacity="0.95"/>
<rect x="599.0" y="379.01" width="23.0" height="20.99" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4849;0.4851;1.0000" values="0;0;1;1"/><rect x="626.5" y="336.36" width="23.0" height="63.64" fill="#c4b5fd" opacity="0.95"/>
<rect x="650.5" y="365.87" width="23.0" height="34.13" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5232;0.5234;1.0000" values="0;0;1;1"/><rect x="678.0" y="339.16" width="23.0" height="60.84" fill="#c4b5fd" opacity="0.95"/>
<rect x="702.0" y="363.72" width="23.0" height="36.28" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5615;0.5617;1.0000" values="0;0;1;1"/><rect x="729.5" y="341.34" width="23.0" height="58.66" fill="#c4b5fd" opacity="0.95"/>
<rect x="753.5" y="362.38" width="23.0" height="37.62" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/><rect x="781.0" y="344.17" width="23.0" height="55.83" fill="#c4b5fd" opacity="0.95"/>
<rect x="805.0" y="360.68" width="23.0" height="39.32" fill="#fcd34d" opacity="0.95"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6381;0.6383;1.0000" values="0;0;1;1"/><rect x="832.5" y="347.79" width="23.0" height="52.21" fill="#c4b5fd" opacity="0.95"/>
<rect x="856.5" y="358.51" width="23.0" height="41.49" fill="#fcd34d" opacity="0.95"/>
</g>
<circle cx="52" cy="284" r="6" fill="#c4b5fd"/>
<text x="62" y="288" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">残った光(透過率 T)</text>
<circle cx="203.39999999999998" cy="284" r="6" fill="#fcd34d"/>
<text x="213.39999999999998" y="288" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">集めた霧の光</text>
<text x="560" y="290" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">透過率:</text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1020;0.1021;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1021;0.1403;0.1404;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1403;0.1404;0.1786;0.1787;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1786;0.1787;0.2169;0.2170;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">99<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2170;0.2551;0.2553;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">99<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;0.2934;0.2936;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">98<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2934;0.2936;0.3317;0.3319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">98<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;0.3700;0.3702;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">96<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3700;0.3702;0.4083;0.4085;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">91<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4083;0.4085;0.4466;0.4468;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">77<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4466;0.4468;0.4849;0.4851;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">64<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4849;0.4851;0.5232;0.5234;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">61<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5232;0.5234;0.5615;0.5617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">59<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5615;0.5617;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">56<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;0.6381;0.6383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="640" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">52<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6381;0.6383;1.0000" values="0;0;1;1"/></text>
<text x="690" y="292" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">%</text>
<text x="730" y="290" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">霧の光:</text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1020;0.1021;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1021;0.1403;0.1404;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1403;0.1404;0.1786;0.1787;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1786;0.1787;0.2169;0.2170;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2170;0.2551;0.2553;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;0.2934;0.2936;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2934;0.2936;0.3317;0.3319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;0.3700;0.3702;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">3<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3700;0.3702;0.4083;0.4085;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4083;0.4085;0.4466;0.4468;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">21<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4466;0.4468;0.4849;0.4851;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">34<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4849;0.4851;0.5232;0.5234;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">36<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5232;0.5234;0.5615;0.5617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">38<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5615;0.5617;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">39<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;0.6381;0.6383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="805" y="292" text-anchor="start" style="font-size:22px;font-weight:700;fill:#b45309" opacity="0">41<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6381;0.6383;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7020;0.7021;1.0000" values="0;0;1;1"/><rect x="30" y="440" width="900" height="76" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="464" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">最終: 透過率 52%、霧の光 0.41。厚みを考えた式で、足し算より正確(差 0.03)</text>
<text x="46" y="488" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">3D テクスチャ 160×90×64 = 921,600 個で積算。画素ごとに 64 回進める方法は 132,710,400 回(約 144 倍)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">霧の中を進む光は、減る(吸収・散乱)ことと、足される(霧が光る)ことを同時に受ける<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">前のスライスから順に、T(残る光)を掛けて、霧の光を足す<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.7020;0.7021;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">積算は 1 回。以後、どの画素も、奥行きに応じて、結果を 1 回読むだけ<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7020;0.7021;1.0000;1.0000" values="0;0;1;1;0"/></text>
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

| 点 | 説明 |
| --- | --- |
| **`fog.a` ＝ 透過率** | **シーンの色にかける** |
| **`fog.rgb` ＝ 散乱光** | **足す** |
| **三線形補間** | **froxel の粗さを滑らかにする** |
| **半透明** | **半透明の物もピクセル シェーダー内で同じ式を適用** |

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

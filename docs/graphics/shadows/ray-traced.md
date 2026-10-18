---
title: Ray-Traced Shadows
tags:
  - 描画
---

# Ray-Traced Shadows

**シャドウ マップ**は、**光から見たシーンをいったん画像（深度）に写し**、そこから**近似**します。そのため、**解像度・バイアス・エイリアシング**の問題が付きまといます。**レイトレース影**は、**画素から光へ直接レイを飛ばし**、**途中で何かに当たるか**を、**ジオメトリそのもの**に対して調べる方式です。**シャドウ マップの問題が、根本から消え**、**面光源の半影**も**レイを光源の面上にばらまく**ことで、**物理的に正しく**作れます。**DXR**（DirectX Raytracing）に対応した GPU が必要です。

!!! tip "ポイント"
    - <strong>画素（ワールド位置）から、光へシャドウ レイ</strong>を 1 本。<strong>当たれば影、当たらなければ日向</strong>。
    - <strong>シャドウ マップなし</strong>：<strong>解像度・バイアス・ピーター パンニング・アクネが存在しない</strong>。
    - <strong>面光源の半影</strong>：<strong>光源の面上のランダムな点</strong>へ飛ばし、<strong>平均</strong>。<strong>接触硬化が正確</strong>。
    - 必要なもの：<strong>加速構造（BLAS・TLAS）</strong>・<strong>DXR 対応 GPU</strong>。
    - <strong>少ないレイ</strong>（画素あたり 1 本）＋<strong>デノイズ</strong>で<strong>リアルタイム</strong>に。
    - 最適化：<strong>Any-Hit 不要</strong>（<strong>当たった時点で終了</strong>）・<strong>RayQuery（インライン）</strong>。

## Principle {#原理}

画素の**ワールド位置 `P`** から、**光源への方向**へ**レイ**を飛ばします。**途中で何かに当たったら影**です。

光源の種類ごとに、レイの方向は次のように決めます。平行光（太陽）では、光の逆方向（`-L`）に飛ばします。光源の大きさ（視直径）を考慮して、方向を円錐内でランダムにずらします。点光源やスポットライトでは、ライトの位置へ向かう方向に飛ばし、光源の大きさ（半径）を考慮して、光源の球面上のランダムな点を狙います。矩形の面光源では、面上のランダムな点へ飛ばします。このランダムなずらしが、物理的に正しい半影を生みます。

**ランダムに方向をずらす**ことで、<strong>1 本ずつのレイは「影か日向か」の 0/1 だが平均すると半影（0〜1）</strong>になります。

### Shadow Test {#影の判定}

```hlsl
float TraceShadowRay(float3 origin, float3 direction, float t_max) {
  RayQuery<RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH |
           RAY_FLAG_SKIP_CLOSEST_HIT_SHADER> query;
  RayDesc ray;
  ray.Origin = origin;
  ray.Direction = direction;
  ray.TMin = 0.001;
  ray.TMax = t_max;
  query.TraceRayInline(scene_tlas, 0, 0xFF, ray);
  query.Proceed();
  return query.CommittedStatus() == COMMITTED_TRIANGLE_HIT ? 0.0 : 1.0;
}
```

| 点 | 説明 |
| --- | --- |
| **`ACCEPT_FIRST_HIT_AND_END_SEARCH`** | **最初に当たった時点で探索を終了**（**最も近いヒットを探す必要はない**）。**大幅に速い** |
| **`SKIP_CLOSEST_HIT_SHADER`** | シェーダーを呼ばない（**当たったか**だけ分かればよい） |
| **`TMin`** | **自己交差**（自分の面に当たる）を避ける、**小さなオフセット** |
| **`TMax`** | **光源までの距離**（点光源）。**それより先は見ない** |
| <strong>RayQuery（インライン）</strong> | **ピクセル/コンピュート シェーダーの中**から、**直接**レイを飛ばす（DXR 1.1） |

<!-- fig:rt-shadow-samples:begin -->

<svg class="fig illust motion" data-fig="rt-shadow-samples" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rt-shadow-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">レイトレースの影: 面積のある光に、影の光線を N 本飛ばして、割合で濃さを決める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 つの点から、光(幅 4)の上のでたらめな点へ N 本。遮られた本数の割合が影の濃さ。同じ点で何度もやって、ばらつきを見る</text>
<rect x="30" y="96" width="440" height="250" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 光・遮る板・受ける点(断面)</text>
<rect x="216.0" y="112.0" width="104.0" height="8" fill="#e5aa28"/>
<rect x="229.0" y="222.0" width="78.0" height="7" fill="#475569"/>
<line x1="60.0" y1="324.0" x2="450.0" y2="324.0" stroke="#94a3b8" stroke-width="3"/>
<circle cx="203.0" cy="324.0" r="7" fill="#1f2937"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;1.0000" values="1;1;0;0"/><line x1="203.0" y1="324.0" x2="244.58" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<text x="50" y="338" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">光線 1 本 → 届いた 1 本 → 光 1.00(正解 0.38)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;0.4398;0.4400;1.0000" values="0;0;1;1;0;0"/><line x1="203.0" y1="324.0" x2="244.7" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="280.59" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="251.83" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="265.98" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<text x="50" y="338" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">光線 4 本 → 届いた 2 本 → 光 0.50(正解 0.38)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4398;0.4400;0.6265;0.6267;1.0000" values="0;0;1;1;0;0"/><line x1="203.0" y1="324.0" x2="245.19" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="289.79" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="274.34" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="312.17" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="218.88" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="279.29" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="310.95" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="319.75" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="217.04" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="235.59" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="317.42" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="267.06" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="315.1" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="251.79" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="243.49" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="228.03" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<text x="50" y="338" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">光線 16 本 → 届いた 7 本 → 光 0.44(正解 0.38)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6265;0.6267;1.0000" values="0;0;1;1"/><line x1="203.0" y1="324.0" x2="247.12" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="222.58" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="260.41" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="288.96" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="217.88" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="267.86" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="278.69" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="317.19" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="260.55" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="314.37" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="294.42" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="253.64" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="303.59" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="219.26" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="239.3" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="266.78" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="285.87" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="298.09" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="221.54" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="235.75" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="233.89" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="245.41" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="283.42" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="313.32" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="231.42" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="245.19" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="286.08" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="283.13" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="263.75" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="294.57" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="228.74" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="247.94" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="256.64" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="238.76" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="295.37" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="219.47" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="240.04" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="232.49" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="260.04" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="262.51" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="280.79" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="225.86" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="300.0" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="271.79" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="270.41" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="217.99" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="299.67" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="254.41" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="304.04" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="240.33" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="266.6" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="248.35" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="228.72" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="305.03" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="242.6" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="281.67" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="293.13" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="268.15" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="303.11" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="283.14" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="280.88" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="311.29" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="223.94" y2="120.0" stroke="#2ea043" stroke-width="1.5" opacity="0.8"/>
<line x1="203.0" y1="324.0" x2="296.73" y2="120.0" stroke="#e5484d" stroke-width="1.5" opacity="0.8"/>
<text x="50" y="338" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">光線 64 本 → 届いた 26 本 → 光 0.41(正解 0.38)</text>
</g>
<rect x="500" y="96" width="430" height="250" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="500" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">② 同じ点で 200 回やったときの、ばらつき</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/><text x="520" y="158" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">1 本</text>
<rect x="590" y="140" width="260.0" height="26" fill="#e5484d" opacity="0.85"/>
<text x="858.0" y="159" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ばらつき 0.480</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2754;0.2756;1.0000" values="0;0;1;1"/><text x="520" y="208" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">4 本</text>
<rect x="590" y="190" width="124.05" height="26" fill="#e5484d" opacity="0.85"/>
<text x="722.0508681395614" y="209" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ばらつき 0.229</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4620;0.4622;1.0000" values="0;0;1;1"/><text x="520" y="258" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">16 本</text>
<rect x="590" y="240" width="64.91" height="26" fill="#e5484d" opacity="0.85"/>
<text x="662.9118643662416" y="259" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ばらつき 0.120</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6487;0.6489;1.0000" values="0;0;1;1"/><text x="520" y="308" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">64 本</text>
<rect x="590" y="290" width="32.65" height="26" fill="#e5484d" opacity="0.85"/>
<text x="630.6482897434265" y="309" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ばらつき 0.060</text>
</g>
<text x="40" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">影の光線の本数:</text>
<text x="190" y="388" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="190" y="388" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.2665;0.2667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="388" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;0.4532;0.4533;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="388" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4532;0.4533;0.6398;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="388" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">64<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6398;0.6400;1.0000" values="0;0;1;1"/></text>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">画面 1920×1080 での 1 フレームの光線:</text>
<text x="40" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">2,073,600<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.2665;0.2667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">8,294,400<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;0.4532;0.4533;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">33,177,600<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4532;0.4533;0.6398;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="452" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">132,710,400<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6398;0.6400;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8132;0.8133;1.0000" values="0;0;1;1"/><rect x="520" y="380" width="410" height="116" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="536" y="404" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">4 倍の本数で、ばらつきは約 半分(1/√N)</text>
<text x="536" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">1 本 0.480 → 64 本 0.060(約 8.0 分の 1)</text>
<text x="536" y="451" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">実際は 1 本で撮って、時間方向に重ねて(デノイズ)消す</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">面積のある光の影は、半影ができる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光の上の点を、ばらつかせて選び、遮られた割合を数える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8132;0.8133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">本数を増やすほど、きれい。でも、光線は、画素数に比例して増える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8132;0.8133;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:rt-shadow-samples:end -->

## Penumbra: Sampling an Area Light {#半影面光源のサンプリング}

**面光源**（有限の大きさ）の影を**物理的に正確**に作るには、**光源の面上にランダムな点**を選び、**そこへレイ**を飛ばします。

```hlsl
float3 SampleSunDirection(float3 sun_dir, float angular_radius, float2 xi) {
  float cos_theta = lerp(cos(angular_radius), 1.0, xi.x);
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  float phi = 2.0 * 3.14159265 * xi.y;
  float3 local_dir = float3(sin_theta * cos(phi), sin_theta * sin(phi), cos_theta);
  return TransformToBasis(local_dir, sun_dir);
}
```

太陽の方向のサンプルのコードの要点です。太陽の視直径（約 0.27 度の半角）の円錐内で、ランダムな方向を一様に選びます。`xi` は 2 つの乱数で、ブルー ノイズ・IGN・低食い違い列などを使います。`TransformToBasis` は、太陽方向を軸とした局所座標を、ワールドへ変換する関数です。

**1 画素あたり 1 本**のレイでは、**半影は、0 か 1 のノイズ**になります。**複数本を平均**するか、**デノイズ**して滑らかにします。

### Contact Hardening Is Exact {#接触硬化は正確}

**遮蔽物が近い**と**光源の面上のどの点へのレイも、同じ遮蔽物に当たる**ので、**影は鋭く**なります。**遮蔽物が離れる**と**光源の面上の点によって、当たる・当たらないが分かれ**、**ぼけます**。[PCSS](pcss.md)が近似した性質が**ここでは自然に再現**されます。

## Denoising {#デノイズ}

**1 画素 1 本**の**ノイズの多い影**を、**滑らかにする**には、**デノイズ**します。

| 方法 | 内容 |
| --- | --- |
| <strong>時間蓄積（TAA 的）</strong> | **前のフレームの結果**を**再投影**して、**混ぜる**（**カメラ・物の動き**に注意） |
| **空間フィルタ** | **バイラテラル／À-trous ウェーブレット**で、**法線・深度**を**手がかり**に**エッジを保って**ぼかす |
| **分散ガイド** | **画素の分散**を見て、**ノイズの多い所**ほど**強く**フィルタ |
| **専用デノイザ** | <strong>NVIDIA NRD（ReBLUR・SIGMA）</strong>、**AMD FidelityFX Denoiser** など。<strong>影専用（SIGMA）</strong>は、**半影**に最適化 |

**影専用のデノイザ**は、<strong>可視性（0〜1）</strong>を、<strong>距離（遮蔽物までの距離）</strong>とともに受け取り、**半影の幅**に応じて、**フィルタの強さ**を変えます。

## Acceleration Structures {#加速構造}

**レイトレース影**には、<strong>シーンの加速構造（BVH）</strong>が必要です。

加速構造は 2 層です。BLAS（Bottom-Level）は、メッシュごとの BVH で、三角形を含みます。TLAS（Top-Level）は、BLAS のインスタンスを、変換行列付きで並べた BVH です。更新については、動く物体は TLAS のインスタンス行列を更新し、変形する（スキニングされた）物は BLAS を再構築またはリフィットします。

**影に使う BLAS は、見た目より単純でよい**（**低ポリのプロキシ**）ことが多く、**メモリ・構築コスト**を減らせます。

## Hybrid Setup {#ハイブリッド構成}

**全画素をレイトレース**すると重いので、**シャドウ マップと併用**します。

| 構成 | 内容 |
| --- | --- |
| **主ライトだけ RT** | **太陽の影だけ**、レイトレース（**柔らかい影・正確な接触**） |
| **シャドウ マップ ＋ RT** | **シャドウ マップ**で**完全な影・完全な日向**を判断し、**半影の領域だけ RT**で精密に |
| **遠景はシャドウ マップ** | **近くだけ RT** |
| **品質設定で切り替え** | **RT 非対応 GPU は、シャドウ マップ**に |

**画面空間のマスク**（半影のありそうな画素）を作り、**その画素だけレイを飛ばす**と、**大幅に安く**なります。

## Cost {#コスト}

| 項目 | 内容 |
| --- | --- |
| **レイ数** | 画素 × ライト数 × 1〜数本 |
| **加速構造のコスト** | **構築・更新・メモリ** |
| **デノイズ** | **追加パス** |
| **ライトが多い** | **ライトごとにレイ**が必要。**重要なライト**に限る |

**ライトが多数**ある場合は、**ライトの重要度でサンプルするライトを 1 つ選ぶ**（**ReSTIR**・**重要度サンプリング**）手法があります。

## Comparison with Shadow Maps {#シャドウ-マップとの比較}

| 項目 | シャドウ マップ | レイトレース |
| --- | --- | --- |
| **精度** | 解像度・バイアスの影響 | **ジオメトリそのもの**。**正確** |
| **アーティファクト** | アクネ・ピーター パンニング・エイリアシング | **ほぼなし**（ノイズのみ） |
| **半影** | 近似（PCSS） | **物理的に正確** |
| **透過・アルファ テスト** | 扱いにくい | **Any-Hit シェーダー**で可能 |
| **必要な HW** | 不要 | **DXR 対応 GPU** |
| **コスト** | 中 | **大**（デノイズ込み） |
| **多数のライト** | 負荷が増える | **ライト数に比例** |

## Pros and Cons {#長所と短所}

| 長所 | 短所 |
| --- | --- |
| **シャドウ マップの問題が、全て消える** | **DXR 対応 GPU が必須** |
| **正確な半影・接触硬化** | **加速構造の維持**（メモリ・更新） |
| **シャドウ マップのレンダリング パスが不要** | **ノイズ ＋ デノイズ** |
| **アルファ テストの物（葉）も、正確** | **ライト数に比例**して重い |

## Common Mistakes {#よくあるミス}

??? failure "自己交差で、面が黒いノイズだらけ"
    **`TMin` を小さく設定**し、**レイの原点を法線方向にわずかにずらす**。

??? failure "Any-Hit 不要なのに、最も近いヒットを探していて、遅い"
    **`ACCEPT_FIRST_HIT_AND_END_SEARCH`** を指定します。

??? failure "デノイズなしで、1 本のレイでノイズだらけ"
    **時間蓄積・空間フィルタ・専用デノイザ**を使います。

??? failure "全ライトに、全画素でレイを飛ばして、重い"
    **主ライトだけ RT**・**マスクした画素のみ**にします。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] レイトレース影 ＝ <strong>画素から光へ、シャドウ レイを飛ばし、当たれば影</strong>
    - [x] <strong>シャドウ マップの問題（解像度・バイアス・アクネ）が、存在しない</strong>
    - [x] <strong>光源の面上にランダムにレイを飛ばして平均</strong> ＝ <strong>正確な半影・接触硬化</strong>
    - [x] <strong>最初のヒットで終了</strong>（<strong>ACCEPT_FIRST_HIT</strong>）で速くする。<strong>デノイズ</strong>が必須
    - [x] <strong>ハイブリッド</strong>（シャドウ マップ ＋ RT）が実用的。<strong>DXR 対応 GPU</strong>が必要

## References {#参考}

- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- NVIDIA, "Ray Tracing Gems"（シャドウ・デノイズの章）
- NVIDIA, "NRD (NVIDIA Real-Time Denoisers)"（SIGMA：影用デノイザ）

## Related Pages {#関連ページ}

- [Shadows](index.md)
- [PCSS](pcss.md)
- [RT 反射](../reflections/rt-reflections/index.md)
- [Distance Field Shadows](sdf-shadows.md)

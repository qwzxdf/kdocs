---
title: Prefiltering (Split-Sum)
tags:
  - 描画
---

# Prefiltering (Split-Sum)

<strong>粗い面の反射は周囲の広い範囲の光の平均</strong>になります。これを毎回ピクセルごとに計算するのは重すぎるので、粗さごとにキューブマップを事前にぼかして、ミップに入れておきます。Split-Sum 近似と呼ばれる、ほとんどのエンジンで使われる方式です。このページでは事前フィルタの考え方とミップの使い方を説明します。

!!! tip "ポイント"
    - 粗さ ＝ ミップ レベル（粗いほど、ぼけたミップ）。
    - 事前に GGX 分布で重み付けして、ぼかす。
    - もう 1 つの項（BRDF の積分）は、LUT に入れておく。
    - 実行時はミップ 1 回 ＋ LUT 1 回の読み出しだけ。

!!! info "このページを読む前に"
    - [Reflection Probes](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 粗さへの対応：事前フィルタ（Split-Sum）
粗い面の反射は <strong>BRDF の山の範囲の景色を、重み付きで平均</strong>したものでした（[Reflections](../index.md)）。これを表面ごとに実行時に計算するのは重いので、事前計算します。Epic の Karis が提案した Split-Sum 近似が、標準になっています。

### 式を 2 つに分ける

<div class="formula">∫ L_i · f_spec · cosθ dω　≈　( ∫ L_i · D · cosθ dω ) × ( ∫ f_spec · cosθ dω )</div>

2 つの項を順に説明します。第 1 項は事前フィルタした環境マップです。粗さごとに環境をぼかしたキューブマップ（のミップ）で、プローブごとに事前計算します。第 2 項は BRDF の積分（スケールとバイアス）で、`F0 · A + B` の形をしています。A と B は `n·v` と粗さから引く値で、BRDF LUT（2D テクスチャ）を1 つだけ事前計算しておけば、すべてのプローブで共有できます。

Karis が Unreal Engine 4 で提案した split-sum 近似（"Real Shading in Unreal Engine 4"、SIGGRAPH 2013）は、本来は 1 つの積分である鏡面反射を、環境光の項と BRDF の項に「分けて」近似することで、事前計算を可能にしました。この分割は厳密な等式ではなく、視線と法線と反射方向が一致する（`n = v = r`）という仮定を置いた近似ですが、見た目の誤差は小さく現代の PBR のほぼ標準になっています。

詳しい導出は[PBR](../../../3d/pbr.md)の IBL を参照してください。

<!-- fig:prefilter-mips:begin -->

<svg class="fig illust motion" data-fig="prefilter-mips" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-prefilter-mips" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">環境マップの事前フィルタ: 粗さごとに、あらかじめぼかしたものをミップに入れておく</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">2 次元(円)の空。太陽と空がある。粗さ 0・0.25・0.5・0.75・1 の 5 段で、ぼかし具合と、画素数を見る</text>
<rect x="30" y="96" width="580" height="330" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 反射の向きごとの明るさ(横軸 = 向き 0〜360°)</text>
<path d="M50.0,385.98 L52.89,385.35 L55.78,384.72 L58.67,384.1 L61.56,383.47 L64.44,382.85 L67.33,382.23 L70.22,381.62 L73.11,381.01 L76.0,380.41 L78.89,379.82 L81.78,379.23 L84.67,378.65 L87.56,378.08 L90.44,377.52 L93.33,376.97 L96.22,376.43 L99.11,375.9 L102.0,375.39 L104.89,374.89 L107.78,374.4 L110.67,373.92 L113.56,373.46 L116.44,373.02 L119.33,372.59 L122.22,372.17 L125.11,371.76 L128.0,371.23 L130.89,370.11 L133.78,366.74 L136.67,356.93 L139.56,333.53 L142.44,290.25 L145.33,230.9 L148.22,175.82 L151.11,152.86 L154.0,175.39 L156.89,230.04 L159.78,288.97 L162.67,331.82 L165.56,354.79 L168.44,364.18 L171.33,367.13 L174.22,367.83 L177.11,367.95 L180.0,367.96 L182.89,367.97 L185.78,368.01 L188.67,368.06 L191.56,368.14 L194.44,368.24 L197.33,368.36 L200.22,368.5 L203.11,368.66 L206.0,368.84 L208.89,369.05 L211.78,369.27 L214.67,369.52 L217.56,369.79 L220.44,370.07 L223.33,370.38 L226.22,370.7 L229.11,371.04 L232.0,371.4 L234.89,371.78 L237.78,372.18 L240.67,372.59 L243.56,373.02 L246.44,373.46 L249.33,373.92 L252.22,374.4 L255.11,374.89 L258.0,375.39 L260.89,375.9 L263.78,376.43 L266.67,376.97 L269.56,377.52 L272.44,378.08 L275.33,378.65 L278.22,379.23 L281.11,379.82 L284.0,380.41 L286.89,381.01 L289.78,381.62 L292.67,382.23 L295.56,382.84 L298.44,383.44 L301.33,384.0 L304.22,384.46 L307.11,384.69 L310.0,384.44 L312.89,382.69 L315.78,379.48 L318.67,374.14 L321.56,366.06 L324.44,355.05 L327.33,341.65 L330.22,327.32 L333.11,314.33 L336.0,305.2 L338.89,301.9 L341.78,305.2 L344.67,314.33 L347.56,327.32 L350.44,341.65 L353.33,355.05 L356.22,366.06 L359.11,374.14 L362.0,379.48 L364.89,382.69 L367.78,384.44 L370.67,385.31 L373.56,385.71 L376.44,385.88 L379.33,385.95 L382.22,385.97 L385.11,385.98 L388.0,385.98 L390.89,385.98 L393.78,385.98 L396.67,385.98 L399.56,385.98 L402.44,385.98 L405.33,385.98 L408.22,385.98 L411.11,385.98 L414.0,385.98 L416.89,385.98 L419.78,385.98 L422.67,385.98 L425.56,385.98 L428.44,385.98 L431.33,385.98 L434.22,385.98 L437.11,385.98 L440.0,385.98 L442.89,385.98 L445.78,385.98 L448.67,385.98 L451.56,385.98 L454.44,385.98 L457.33,385.98 L460.22,385.98 L463.11,385.98 L466.0,385.98 L468.89,385.98 L471.78,385.98 L474.67,385.98 L477.56,385.98 L480.44,385.98 L483.33,385.98 L486.22,385.98 L489.11,385.98 L492.0,385.98 L494.89,385.98 L497.78,385.98 L500.67,385.98 L503.56,385.98 L506.44,385.98 L509.33,385.98 L512.22,385.98 L515.11,385.98 L518.0,385.98 L520.89,385.98 L523.78,385.98 L526.67,385.98 L529.56,385.98 L532.44,385.98 L535.33,385.98 L538.22,385.98 L541.11,385.98 L544.0,385.98 L546.89,385.98 L549.78,385.98 L552.67,385.98 L555.56,385.98 L558.44,385.98 L561.33,385.98 L564.22,385.98 L567.11,385.98" fill="none" stroke="#64748b" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/></path>
<text x="590" y="150" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">粗さ 0.00: 最大 2.14<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/></text>
<path d="M50.0,385.3 L52.89,384.94 L55.78,384.5 L58.67,383.99 L61.56,383.43 L64.44,382.84 L67.33,382.24 L70.22,381.64 L73.11,381.03 L76.0,380.44 L78.89,379.85 L81.78,379.26 L84.67,378.68 L87.56,378.12 L90.44,377.56 L93.33,377.01 L96.22,376.48 L99.11,375.95 L102.0,375.44 L104.89,374.94 L107.78,374.44 L110.67,373.94 L113.56,373.4 L116.44,372.74 L119.33,371.78 L122.22,370.15 L125.11,367.25 L128.0,362.17 L130.89,353.79 L133.78,341.08 L136.67,323.6 L139.56,302.11 L142.44,278.93 L145.33,257.72 L148.22,242.66 L151.11,237.08 L154.0,242.23 L156.89,256.87 L159.78,277.65 L162.67,300.41 L165.56,321.47 L168.44,338.53 L171.33,350.82 L174.22,358.79 L177.11,363.46 L180.0,365.96 L182.89,367.18 L185.78,367.75 L188.67,368.03 L191.56,368.18 L194.44,368.31 L197.33,368.43 L200.22,368.58 L203.11,368.74 L206.0,368.92 L208.89,369.13 L211.78,369.35 L214.67,369.6 L217.56,369.86 L220.44,370.14 L223.33,370.45 L226.22,370.77 L229.11,371.11 L232.0,371.47 L234.89,371.85 L237.78,372.24 L240.67,372.65 L243.56,373.08 L246.44,373.52 L249.33,373.98 L252.22,374.45 L255.11,374.94 L258.0,375.44 L260.89,375.95 L263.78,376.48 L266.67,377.01 L269.56,377.56 L272.44,378.12 L275.33,378.68 L278.22,379.26 L281.11,379.84 L284.0,380.43 L286.89,381.01 L289.78,381.59 L292.67,382.13 L295.56,382.6 L298.44,382.93 L301.33,383.01 L304.22,382.67 L307.11,381.69 L310.0,379.81 L312.89,376.75 L315.78,372.28 L318.67,366.29 L321.56,358.87 L324.44,350.36 L327.33,341.43 L330.22,332.95 L333.11,325.91 L336.0,321.25 L338.89,319.61 L341.78,321.25 L344.67,325.91 L347.56,332.95 L350.44,341.44 L353.33,350.39 L356.22,358.92 L359.11,366.41 L362.0,372.51 L364.89,377.16 L367.78,380.49 L370.67,382.73 L373.56,384.15 L376.44,385.0 L379.33,385.48 L382.22,385.74 L385.11,385.87 L388.0,385.93 L390.89,385.96 L393.78,385.97 L396.67,385.98 L399.56,385.98 L402.44,385.98 L405.33,385.98 L408.22,385.98 L411.11,385.98 L414.0,385.98 L416.89,385.98 L419.78,385.98 L422.67,385.98 L425.56,385.98 L428.44,385.98 L431.33,385.98 L434.22,385.98 L437.11,385.98 L440.0,385.98 L442.89,385.98 L445.78,385.98 L448.67,385.98 L451.56,385.98 L454.44,385.98 L457.33,385.98 L460.22,385.98 L463.11,385.98 L466.0,385.98 L468.89,385.98 L471.78,385.98 L474.67,385.98 L477.56,385.98 L480.44,385.98 L483.33,385.98 L486.22,385.98 L489.11,385.98 L492.0,385.98 L494.89,385.98 L497.78,385.98 L500.67,385.98 L503.56,385.98 L506.44,385.98 L509.33,385.98 L512.22,385.98 L515.11,385.98 L518.0,385.98 L520.89,385.98 L523.78,385.98 L526.67,385.98 L529.56,385.98 L532.44,385.98 L535.33,385.98 L538.22,385.98 L541.11,385.98 L544.0,385.98 L546.89,385.98 L549.78,385.98 L552.67,385.97 L555.56,385.96 L558.44,385.93 L561.33,385.86 L564.22,385.75 L567.11,385.57" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1871;0.1872;1.0000" values="0;0;1;1"/></path>
<text x="590" y="172" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb" opacity="0">粗さ 0.25: 最大 1.44<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1871;0.1872;1.0000" values="0;0;1;1"/></text>
<path d="M50.0,384.38 L52.89,384.05 L55.78,383.69 L58.67,383.3 L61.56,382.87 L64.44,382.42 L67.33,381.93 L70.22,381.43 L73.11,380.9 L76.0,380.35 L78.89,379.78 L81.78,379.19 L84.67,378.55 L87.56,377.87 L90.44,377.11 L93.33,376.25 L96.22,375.25 L99.11,374.06 L102.0,372.61 L104.89,370.83 L107.78,368.65 L110.67,365.98 L113.56,362.78 L116.44,358.97 L119.33,354.54 L122.22,349.51 L125.11,343.94 L128.0,337.94 L130.89,331.71 L133.78,325.45 L136.67,319.43 L139.56,313.95 L142.44,309.28 L145.33,305.67 L148.22,303.34 L151.11,302.4 L154.0,302.92 L156.89,304.83 L159.78,308.02 L162.67,312.28 L165.56,317.35 L168.44,322.95 L171.33,328.8 L174.22,334.63 L177.11,340.23 L180.0,345.4 L182.89,350.04 L185.78,354.08 L188.67,357.51 L191.56,360.35 L194.44,362.64 L197.33,364.46 L200.22,365.89 L203.11,367.0 L206.0,367.87 L208.89,368.55 L211.78,369.1 L214.67,369.56 L217.56,369.96 L220.44,370.33 L223.33,370.69 L226.22,371.04 L229.11,371.4 L232.0,371.76 L234.89,372.14 L237.78,372.53 L240.67,372.93 L243.56,373.35 L246.44,373.78 L249.33,374.22 L252.22,374.68 L255.11,375.15 L258.0,375.62 L260.89,376.1 L263.78,376.58 L266.67,377.05 L269.56,377.51 L272.44,377.93 L275.33,378.3 L278.22,378.61 L281.11,378.82 L284.0,378.91 L286.89,378.84 L289.78,378.57 L292.67,378.06 L295.56,377.27 L298.44,376.17 L301.33,374.72 L304.22,372.91 L307.11,370.75 L310.0,368.26 L312.89,365.49 L315.78,362.53 L318.67,359.45 L321.56,356.4 L324.44,353.5 L327.33,350.88 L330.22,348.69 L333.11,347.03 L336.0,346.02 L338.89,345.7 L341.78,346.1 L344.67,347.2 L347.56,348.94 L350.44,351.24 L353.33,353.99 L356.22,357.05 L359.11,360.29 L362.0,363.58 L364.89,366.8 L367.78,369.86 L370.67,372.67 L373.56,375.19 L376.44,377.4 L379.33,379.27 L382.22,380.83 L385.11,382.1 L388.0,383.11 L390.89,383.89 L393.78,384.49 L396.67,384.94 L399.56,385.26 L402.44,385.5 L405.33,385.66 L408.22,385.77 L411.11,385.85 L414.0,385.9 L416.89,385.93 L419.78,385.95 L422.67,385.96 L425.56,385.97 L428.44,385.97 L431.33,385.98 L434.22,385.98 L437.11,385.98 L440.0,385.98 L442.89,385.98 L445.78,385.98 L448.67,385.98 L451.56,385.98 L454.44,385.98 L457.33,385.98 L460.22,385.98 L463.11,385.98 L466.0,385.98 L468.89,385.98 L471.78,385.98 L474.67,385.98 L477.56,385.98 L480.44,385.98 L483.33,385.98 L486.22,385.98 L489.11,385.98 L492.0,385.98 L494.89,385.98 L497.78,385.98 L500.67,385.98 L503.56,385.98 L506.44,385.98 L509.33,385.98 L512.22,385.98 L515.11,385.98 L518.0,385.98 L520.89,385.97 L523.78,385.97 L526.67,385.96 L529.56,385.96 L532.44,385.94 L535.33,385.93 L538.22,385.9 L541.11,385.87 L544.0,385.83 L546.89,385.77 L549.78,385.69 L552.67,385.59 L555.56,385.47 L558.44,385.32 L561.33,385.13 L564.22,384.92 L567.11,384.67" fill="none" stroke="#2ea043" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="0;0;1;1"/></path>
<text x="590" y="194" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">粗さ 0.50: 最大 0.90<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="0;0;1;1"/></text>
<path d="M50.0,382.08 L52.89,381.58 L55.78,381.02 L58.67,380.4 L61.56,379.72 L64.44,378.97 L67.33,378.14 L70.22,377.24 L73.11,376.24 L76.0,375.16 L78.89,373.98 L81.78,372.71 L84.67,371.34 L87.56,369.87 L90.44,368.31 L93.33,366.65 L96.22,364.9 L99.11,363.07 L102.0,361.17 L104.89,359.21 L107.78,357.2 L110.67,355.16 L113.56,353.11 L116.44,351.07 L119.33,349.06 L122.22,347.1 L125.11,345.22 L128.0,343.43 L130.89,341.77 L133.78,340.25 L136.67,338.9 L139.56,337.73 L142.44,336.76 L145.33,336.0 L148.22,335.46 L151.11,335.16 L154.0,335.08 L156.89,335.23 L159.78,335.6 L162.67,336.19 L165.56,336.98 L168.44,337.96 L171.33,339.11 L174.22,340.4 L177.11,341.82 L180.0,343.35 L182.89,344.96 L185.78,346.63 L188.67,348.34 L191.56,350.07 L194.44,351.79 L197.33,353.5 L200.22,355.17 L203.11,356.79 L206.0,358.36 L208.89,359.85 L211.78,361.27 L214.67,362.61 L217.56,363.87 L220.44,365.04 L223.33,366.12 L226.22,367.13 L229.11,368.04 L232.0,368.88 L234.89,369.64 L237.78,370.33 L240.67,370.94 L243.56,371.47 L246.44,371.94 L249.33,372.34 L252.22,372.67 L255.11,372.93 L258.0,373.13 L260.89,373.25 L263.78,373.31 L266.67,373.3 L269.56,373.22 L272.44,373.07 L275.33,372.84 L278.22,372.55 L281.11,372.2 L284.0,371.78 L286.89,371.29 L289.78,370.75 L292.67,370.17 L295.56,369.54 L298.44,368.87 L301.33,368.19 L304.22,367.49 L307.11,366.79 L310.0,366.1 L312.89,365.43 L315.78,364.81 L318.67,364.23 L321.56,363.72 L324.44,363.29 L327.33,362.94 L330.22,362.68 L333.11,362.53 L336.0,362.49 L338.89,362.56 L341.78,362.75 L344.67,363.05 L347.56,363.46 L350.44,363.98 L353.33,364.6 L356.22,365.32 L359.11,366.12 L362.0,366.99 L364.89,367.92 L367.78,368.9 L370.67,369.92 L373.56,370.95 L376.44,372.0 L379.33,373.05 L382.22,374.09 L385.11,375.1 L388.0,376.09 L390.89,377.03 L393.78,377.94 L396.67,378.79 L399.56,379.58 L402.44,380.32 L405.33,381.01 L408.22,381.63 L411.11,382.2 L414.0,382.71 L416.89,383.17 L419.78,383.58 L422.67,383.94 L425.56,384.26 L428.44,384.53 L431.33,384.77 L434.22,384.98 L437.11,385.15 L440.0,385.3 L442.89,385.42 L445.78,385.53 L448.67,385.61 L451.56,385.69 L454.44,385.74 L457.33,385.79 L460.22,385.83 L463.11,385.86 L466.0,385.88 L468.89,385.9 L471.78,385.92 L474.67,385.93 L477.56,385.93 L480.44,385.94 L483.33,385.94 L486.22,385.93 L489.11,385.93 L492.0,385.92 L494.89,385.91 L497.78,385.9 L500.67,385.89 L503.56,385.87 L506.44,385.84 L509.33,385.81 L512.22,385.78 L515.11,385.74 L518.0,385.69 L520.89,385.64 L523.78,385.58 L526.67,385.5 L529.56,385.42 L532.44,385.32 L535.33,385.21 L538.22,385.09 L541.11,384.95 L544.0,384.79 L546.89,384.6 L549.78,384.4 L552.67,384.17 L555.56,383.91 L558.44,383.62 L561.33,383.29 L564.22,382.93 L567.11,382.53" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4764;0.4766;1.0000" values="0;0;1;1"/></path>
<text x="590" y="216" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">粗さ 0.75: 最大 0.62<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4764;0.4766;1.0000" values="0;0;1;1"/></text>
<path d="M50.0,375.76 L52.89,375.09 L55.78,374.38 L58.67,373.66 L61.56,372.91 L64.44,372.13 L67.33,371.34 L70.22,370.53 L73.11,369.7 L76.0,368.86 L78.89,368.0 L81.78,367.13 L84.67,366.26 L87.56,365.38 L90.44,364.5 L93.33,363.62 L96.22,362.75 L99.11,361.89 L102.0,361.04 L104.89,360.2 L107.78,359.38 L110.67,358.59 L113.56,357.82 L116.44,357.08 L119.33,356.38 L122.22,355.71 L125.11,355.07 L128.0,354.48 L130.89,353.94 L133.78,353.44 L136.67,352.99 L139.56,352.59 L142.44,352.24 L145.33,351.95 L148.22,351.71 L151.11,351.52 L154.0,351.39 L156.89,351.32 L159.78,351.3 L162.67,351.33 L165.56,351.42 L168.44,351.55 L171.33,351.74 L174.22,351.98 L177.11,352.26 L180.0,352.58 L182.89,352.94 L185.78,353.34 L188.67,353.78 L191.56,354.24 L194.44,354.73 L197.33,355.24 L200.22,355.78 L203.11,356.33 L206.0,356.89 L208.89,357.46 L211.78,358.04 L214.67,358.62 L217.56,359.2 L220.44,359.77 L223.33,360.34 L226.22,360.89 L229.11,361.44 L232.0,361.96 L234.89,362.47 L237.78,362.96 L240.67,363.43 L243.56,363.88 L246.44,364.31 L249.33,364.71 L252.22,365.08 L255.11,365.43 L258.0,365.75 L260.89,366.05 L263.78,366.32 L266.67,366.57 L269.56,366.8 L272.44,367.0 L275.33,367.19 L278.22,367.35 L281.11,367.49 L284.0,367.62 L286.89,367.74 L289.78,367.84 L292.67,367.93 L295.56,368.01 L298.44,368.09 L301.33,368.16 L304.22,368.24 L307.11,368.31 L310.0,368.38 L312.89,368.46 L315.78,368.55 L318.67,368.64 L321.56,368.74 L324.44,368.86 L327.33,368.99 L330.22,369.13 L333.11,369.29 L336.0,369.46 L338.89,369.65 L341.78,369.85 L344.67,370.08 L347.56,370.32 L350.44,370.58 L353.33,370.86 L356.22,371.15 L359.11,371.47 L362.0,371.79 L364.89,372.13 L367.78,372.49 L370.67,372.86 L373.56,373.24 L376.44,373.63 L379.33,374.03 L382.22,374.44 L385.11,374.86 L388.0,375.28 L390.89,375.7 L393.78,376.12 L396.67,376.55 L399.56,376.97 L402.44,377.39 L405.33,377.8 L408.22,378.21 L411.11,378.62 L414.0,379.01 L416.89,379.39 L419.78,379.77 L422.67,380.13 L425.56,380.48 L428.44,380.82 L431.33,381.15 L434.22,381.46 L437.11,381.75 L440.0,382.03 L442.89,382.3 L445.78,382.55 L448.67,382.78 L451.56,383.0 L454.44,383.2 L457.33,383.38 L460.22,383.55 L463.11,383.7 L466.0,383.84 L468.89,383.96 L471.78,384.06 L474.67,384.14 L477.56,384.21 L480.44,384.26 L483.33,384.3 L486.22,384.32 L489.11,384.32 L492.0,384.3 L494.89,384.27 L497.78,384.22 L500.67,384.15 L503.56,384.06 L506.44,383.95 L509.33,383.83 L512.22,383.68 L515.11,383.52 L518.0,383.33 L520.89,383.12 L523.78,382.89 L526.67,382.64 L529.56,382.37 L532.44,382.07 L535.33,381.74 L538.22,381.39 L541.11,381.02 L544.0,380.61 L546.89,380.19 L549.78,379.73 L552.67,379.25 L555.56,378.74 L558.44,378.2 L561.33,377.63 L564.22,377.03 L567.11,376.41" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6211;0.6213;1.0000" values="0;0;1;1"/></path>
<text x="590" y="238" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">粗さ 1.00: 最大 0.49<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6211;0.6213;1.0000" values="0;0;1;1"/></text>
<rect x="640" y="96" width="290" height="330" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="640" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② ミップごとの大きさ</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/><rect x="660" y="130" width="150.0" height="26" fill="#64748b" opacity="0.85"/>
<text x="660" y="126" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">粗さ 0.00</text>
<text x="818.0" y="148" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">256×256 × 6 面</text>
<text x="660" y="172" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">6,144 KB(1 面に RGBA16F)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1871;0.1872;1.0000" values="0;0;1;1"/><rect x="660" y="186" width="75.0" height="26" fill="#2563eb" opacity="0.85"/>
<text x="660" y="182" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">粗さ 0.25</text>
<text x="743.0" y="204" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">128×128 × 6 面</text>
<text x="660" y="228" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">1,536 KB(1 面に RGBA16F)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="0;0;1;1"/><rect x="660" y="242" width="37.5" height="26" fill="#2ea043" opacity="0.85"/>
<text x="660" y="238" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">粗さ 0.50</text>
<text x="705.5" y="260" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">64×64 × 6 面</text>
<text x="660" y="284" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">384 KB(1 面に RGBA16F)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4764;0.4766;1.0000" values="0;0;1;1"/><rect x="660" y="298" width="18.75" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="660" y="294" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">粗さ 0.75</text>
<text x="686.75" y="316" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">32×32 × 6 面</text>
<text x="660" y="340" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">96 KB(1 面に RGBA16F)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6211;0.6213;1.0000" values="0;0;1;1"/><rect x="660" y="354" width="9.38" height="26" fill="#e5484d" opacity="0.85"/>
<text x="660" y="350" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">粗さ 1.00</text>
<text x="677.375" y="372" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">16×16 × 6 面</text>
<text x="660" y="396" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">24 KB(1 面に RGBA16F)</text>
</g>
<text x="40" y="452" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">合計のメモリ:</text>
<text x="180" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0551;0.0553;1.0000" values="1;1;0;0"/></text>
<text x="180" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">6,144<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0551;0.0553;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">7,680<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.3445;0.3447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">8,064<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3445;0.3447;0.4892;0.4894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">8,160<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4892;0.4894;0.6339;0.6340;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="456" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">8,184<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6339;0.6340;1.0000" values="0;0;1;1"/></text>
<text x="250" y="456" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">KB(1 つのプローブ)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7828;0.7830;1.0000" values="0;0;1;1"/><line x1="151.11" y1="140" x2="151.11" y2="410" stroke="#1f2937" stroke-width="2" stroke-dasharray="5 4"/>
<text x="159.11111111111111" y="132" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">反射の向き 70°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7956;0.7957;1.0000" values="0;0;1;1"/><rect x="330" y="436" width="600" height="74" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="346" y="460" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">粗さ 0.4 の読み出し: ミップ 1(0.25)と 2(0.50)を混ぜる</text>
<text x="346" y="483" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">1.44 × 0.40 + 0.90 × 0.60 = 1.11</text>
<text x="346" y="506" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">読み込みは 1〜2 回でよい(毎回ぼかさなくてよい)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ざらざらした面の反射は、広い範囲の平均。毎回計算すると重い<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">粗さごとに、前もってぼかした環境マップを作り、ミップに入れる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;0.7828;0.7830;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">使うときは、粗さに近い 2 つのミップを読んで混ぜるだけ<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7828;0.7830;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:prefilter-mips:end -->

### ミップ レベルの選び方

粗さが大きいほどぼけた（高いミップの）レベルを読みます。

```hlsl
float3 SpecularIBL(float3 N, float3 V, float3 albedo, float metallic, float roughness) {
  float3 R = reflect(-V, N);
  float mip = roughness * (max_mip - 1.0);
  float3 prefiltered = env_cube.SampleLevel(linear_sampler, R, mip).rgb;

  float n_dot_v = saturate(dot(N, V));
  float2 brdf = brdf_lut.Sample(linear_sampler, float2(n_dot_v, roughness)).rg;

  float3 F0 = lerp(0.04, albedo, metallic);
  return prefiltered * (F0 * brdf.x + brdf.y);
}
```

| 点 | 説明 |
| --- | --- |
| `mip = roughness × (最大ミップ)` | 粗さ 0 でミップ 0（くっきり）、粗さ 1 で最大のミップ（ぼんやり） |
| BRDF LUT | `n·v` と粗さを入力にした、2 値（スケール・バイアス）。プロジェクト全体で 1 枚 |
| `F0` | 非金属は約 0.04、金属はアルベド色 |
| ミップ間はトリリニア補間 | 滑らかに粗さが変わる |

### 事前フィルタの作り方

各ミップはその粗さの GGX 分布で、環境マップを重要度サンプリングして作ります。

各ミップはその粗さの GGX 分布で環境マップを重要度サンプリングして作ります。ミップ 0 は粗さ 0 で元のキューブマップそのものです。ミップ 1 以降は粗さを段階的に上げながら、GGX の重要度サンプリングで各テクセルを再計算します（コンピュート シェーダーやピクセル シェーダーで実行）。

重要度サンプリングは 分布の山の部分から多くサンプルする手法で、サンプル数を減らせます（[Stochastic SSR](../ssr-stochastic.md)で詳しく）。

## 粗さとぼかし

<strong>鏡面反射</strong>の 見た目は粗さで、変わります（[Diffuse and Specular](../../gi/theory/diffuse-specular.md)）。つるつるなら周りの景色がくっきり、ざらざらならぼんやり広い範囲が、混ざります。反射プローブのキューブマップを、そのまま引くと常にくっきり映り、粗い面でも鏡のようになって不自然です。粗さに応じたぼかしが必要です。

## ミップにぼかしを焼く

<strong>キューブマップのミップ</strong>を、粗さごとのぼかしとして使います。ミップ 0 が粗さ 0（くっきり）、高いミップが粗さが大きい（ぼやけ）に、対応するよう各ミップを事前に、ぼかして作ります（Kautz と McCool、2000。事前フィルタ環境マップ）。

```text
ミップ 0（128×128）: 粗さ 0.0  ← ほぼ、元の画像
ミップ 1（64×64）  : 粗さ 0.2
ミップ 2（32×32）  : 粗さ 0.4
ミップ 3（16×16）  : 粗さ 0.6
ミップ 4（8×8）    : 粗さ 0.8
ミップ 5（4×4）    : 粗さ 1.0  ← ほぼ、全方向の平均
```

通常のミップ（4 画素を、平均）では 粗さに対応する正しい、ぼかしにならないので GGX の、反射ローブに合わせたぼかしで、各ミップを作ります。

## 重点サンプリングでぼかす

<strong>各ミップの各テクセル</strong>（反射方向 `R` に、対応）について GGX の分布に従って、周りの方向をサンプルし環境マップを引いて、平均します。重点サンプリング（[Monte Carlo Integration](../../gi/theory/monte-carlo.md)）で、少ないサンプルでも正しいぼかしが、得られます。

```hlsl
// GGX の分布に従って、ハーフ ベクトル H をサンプルする（ローカル座標。z が法線）。
float3 ImportanceSampleGGX(float2 u, float roughness) {
  float a = roughness * roughness;                                      // 知覚的な粗さ → GGX の α
  float phi = 2.0 * 3.14159265 * u.x;
  float cos_theta = sqrt((1.0 - u.y) / (1.0 + (a * a - 1.0) * u.y));    // GGX の、逆累積分布
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  return float3(sin_theta * cos(phi), sin_theta * sin(phi), cos_theta);
}
```

GGX の法線分布に 比例した、確率でハーフ ベクトル `H` を、選びます（Walter ら 2007）。粗さが小さいほど `H` は法線の近くに集中し粗さが、大きいほど広がります。

```hlsl
// 事前フィルタ: 反射方向 R に対応する、1 テクセルを、GGX の重点サンプリングで、環境マップから、ぼかして作る。
float3 PrefilterEnvMap(float3 R, float roughness) {
  float3 N = R;                                  // 近似: 法線 = 反射方向 = 視線（Karis の、仮定）
  float3 V = R;
  const uint kSamples = 256;
  float3 sum = 0.0;
  float weight = 0.0;
  for (uint i = 0; i < kSamples; ++i) {
    float2 u = Hammersley(i, kSamples);                                  // 低食い違い量列
    float3 H = LocalToWorld(ImportanceSampleGGX(u, roughness), N);       // GGX に従った、ハーフ ベクトル
    float3 L = normalize(2.0 * dot(V, H) * H - V);                       // 反射: 光の方向
    float n_dot_l = saturate(dot(N, L));
    if (n_dot_l > 0.0) {
      sum += g_env.SampleLevel(g_linear_clamp, L, 0).rgb * n_dot_l;      // その方向の、環境の光（余弦で重みづけ）
      weight += n_dot_l;
    }
  }
  return sum / max(weight, 1e-4);
}
```

ハーフ ベクトル `H` を、サンプルし それで視線 `V` を、反射させた光の方向 `L` で、環境マップを引きます。余弦で重みづけして平均します。粗さごとに各ミップをこの関数で、焼きます（制作時、または起動時）。

!!! note "`N = V = R` の近似"
    実際の鏡面反射は 視線と法線が、別ですが 事前フィルタのキューブマップは、反射方向 `R` だけで引くので `N = V = R` と、仮定します（Karis、2013）。視線が面に斜めのとき実際の反射の、伸び（斜めから見ると反射が縦に、伸びる）は再現できません。これは既知の近似の限界です。

## 反射の式の分解：split-sum

<strong>鏡面反射の間接光</strong>は 環境の、光 `L_i` と BRDF の積を半球で、積分したものです。この積分を 2 つに分けて近似する、split-sum（Karis、2013）が標準です。

```text
∫ L_i(l) × f(l, v) × cosθ dl  ≈  ( 1/N Σ L_i(l_k) × cosθ_k / Σ cosθ_k )  ×  ( 1/N Σ f(l_k, v) × cosθ_k / pdf )
                                    └── ① 事前フィルタした環境マップ ──┘      └── ② BRDF の積分（LUT） ──┘
```

| 項 | 内容 | 事前計算 |
| --- | --- | --- |
| ① 環境光の積分 | 粗さごとに、ぼかした環境マップ（上の `PrefilterEnvMap`） | キューブマップの、ミップ（粗さ × 反射方向） |
| ② BRDF の積分 | 視線と法線の角度（`n·v`）と粗さの関数。2 つの数（`A`、`B`）にまとまる | 2D の、LUT（`n·v` × 粗さ。256×256 の `R16G16`） |

積を 2 つの積分の積に分ける（厳密には、正しくないが十分に近い）ことで、どちらも事前計算できます。

### BRDF の LUT

```hlsl
// BRDF の LUT: (n·v, roughness) → (A, B)。鏡面反射の、フレネルと、可視性を含めた、積分。
float2 IntegrateBRDF(float n_dot_v, float roughness) {
  float3 V = float3(sqrt(1.0 - n_dot_v * n_dot_v), 0.0, n_dot_v);        // 視線（ローカル座標。法線は +Z）
  float A = 0.0, B = 0.0;
  const uint kSamples = 1024;
  for (uint i = 0; i < kSamples; ++i) {
    float2 u = Hammersley(i, kSamples);
    float3 H = ImportanceSampleGGX(u, roughness);
    float3 L = 2.0 * dot(V, H) * H - V;
    float n_dot_l = saturate(L.z);
    float n_dot_h = saturate(H.z);
    float v_dot_h = saturate(dot(V, H));
    if (n_dot_l > 0.0) {
      float G = GeometrySmith(n_dot_v, n_dot_l, roughness);               // 幾何減衰（マスキング・シャドウイング）
      float G_vis = G * v_dot_h / (n_dot_h * n_dot_v);                    // 可視性項
      float Fc = pow(1.0 - v_dot_h, 5.0);                                 // フレネル（Schlick）の、可変部分
      A += (1.0 - Fc) * G_vis;                                            // F0 に掛かる係数
      B += Fc * G_vis;                                                    // F0 に関係しない、加算の係数
    }
  }
  return float2(A, B) / kSamples;
}
```

フレネルの Schlick 近似（`F = F0 + (1 − F0) × Fc`）を、`F0` に掛かる項とそうでない項に、分けて、`A`、`B` に積分します。実行時、`F0 × A + B` で BRDF の積分が得られます（[Water Fresnel](../../water/shading/fresnel.md) の、Schlick 近似と同じ）。

## 実行時の使い方

```hlsl
// 鏡面の間接光: 粗さに応じたミップで、反射方向を読み、split-sum の、BRDF の積分を掛ける。
float3 SpecularIBL(float3 N, float3 V, float3 f0, float roughness) {
  float3 R = reflect(-V, N);
  float n_dot_v = saturate(dot(N, V));
  float mip = roughness * (kEnvMipCount - 1);                              // 粗さ → ミップ
  float3 prefiltered = g_probe_cube.SampleLevel(g_linear_clamp, R, mip).rgb;
  float2 brdf = g_brdf_lut.SampleLevel(g_linear_clamp, float2(n_dot_v, roughness), 0).xy;
  return prefiltered * (f0 * brdf.x + brdf.y);
}
```

<strong>ミップの選択</strong>は 粗さに比例（`roughness × (ミップ数 − 1)`）が、標準的ですがミップ数、ミップごとの粗さの割り当ては、事前フィルタを作るときと同じ式に、そろえます。`SampleLevel` のミップは連続（小数）なので、トライリニアで 2 つのミップが、補間され粗さがなめらかに変わります。

## 注意点

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| ミップ間の継ぎ目（面の境目） | キューブマップの面の境目で、ぼかしが途切れる（ミップで特に目立つ） | シームレス キューブマップ（DirectX 11 は、標準でシームレス）、事前フィルタを全方向でサンプル |
| 粗さ 0（完全な鏡）でぼやける | ミップ 0 が、128×128。つるつるの面では解像度が足りない | 解像度を上げる（256×256）、または SSR / RT で補う |
| ファイアフライ（明るい点が、散らばる） | 明るい光源（太陽）が、少ないサンプルで拾われる | サンプル数を増やす、元のキューブマップのミップを読んで、サンプルする（フィルタード重点サンプリング）、明るさをクランプ |

## よくあるミス

??? failure "粗い面の反射が、鏡のようにくっきり"
    <strong>粗さに応じたミップ</strong>を選ぶ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 粗さごとに、事前にぼかす
    - [x] 実行時は、ミップと LUT を読むだけ

## 参考

- Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice（split-sum 近似）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice
- Kautz, McCool, "Approximation of Glossy Reflection with Prefiltered Environment Maps", Graphics Interface 2000
- Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）

## 関連ページ

- [Reflection Probes](index.md)
- [Parallax Correction](parallax.md)
- [Stochastic SSR](../ssr-stochastic.md)

---
title: Caustics
tags:
  - 描画
---

# Caustics

<strong>水面の波で光が集まり水底にゆらゆら揺れる光の模様ができます</strong>。アニメーションするテクスチャを光の方向から投影するのが手軽です。このページではコースティクスの作り方を説明します。

!!! tip "ポイント"
    - コースティクス ＝ 波で光が集まってできる模様。
    - テクスチャをアニメーションして、投影する。
    - 水深に応じて強さを変える。
    - 本格的には波の法線から光線を追う。

!!! info "このページを読む前に"
    - [Underwater Rendering](index.md)（このセクション全体の地図と、読む順番）

<!-- fig:caustics-rays:begin -->

<svg class="fig illust motion" data-fig="caustics-rays" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-caustics-rays" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">コースティクス: 波が光を集めて、水底に明るい線を作る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">真上から来る平行な光 48 本が波打つ水面で曲がり(n = 1.33)、水底の 1 マスに当たる。当たった本数 = 明るさ</text>
<rect x="30" y="96" width="900" height="250" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">水面(波)と、屈折した光線</text>
<rect x="60.0" y="330.0" width="840.0" height="14" fill="#94a3b8"/>
<text x="908.0" y="342.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">水底</text>
<text x="908.0" y="134.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">水面</text>
<rect x="60.0" y="130.0" width="840.0" height="200.0" fill="#bae6fd" opacity="0.35"/>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3331;0.3333;1.0000" values="1;1;0;0"/><path d="M60.0,110.0 L67.0,110.06 L74.0,110.25 L81.0,110.55 L88.0,110.98 L95.0,111.52 L102.0,112.18 L109.0,112.95 L116.0,113.82 L123.0,114.79 L130.0,115.86 L137.0,117.01 L144.0,118.24 L151.0,119.55 L158.0,120.92 L165.0,122.35 L172.0,123.82 L179.0,125.33 L186.0,126.87 L193.0,128.43 L200.0,130.0 L207.0,131.57 L214.0,133.13 L221.0,134.67 L228.0,136.18 L235.0,137.65 L242.0,139.08 L249.0,140.45 L256.0,141.76 L263.0,142.99 L270.0,144.14 L277.0,145.21 L284.0,146.18 L291.0,147.05 L298.0,147.82 L305.0,148.48 L312.0,149.02 L319.0,149.45 L326.0,149.75 L333.0,149.94 L340.0,150.0 L347.0,149.94 L354.0,149.75 L361.0,149.45 L368.0,149.02 L375.0,148.48 L382.0,147.82 L389.0,147.05 L396.0,146.18 L403.0,145.21 L410.0,144.14 L417.0,142.99 L424.0,141.76 L431.0,140.45 L438.0,139.08 L445.0,137.65 L452.0,136.18 L459.0,134.67 L466.0,133.13 L473.0,131.57 L480.0,130.0 L487.0,128.43 L494.0,126.87 L501.0,125.33 L508.0,123.82 L515.0,122.35 L522.0,120.92 L529.0,119.55 L536.0,118.24 L543.0,117.01 L550.0,115.86 L557.0,114.79 L564.0,113.82 L571.0,112.95 L578.0,112.18 L585.0,111.52 L592.0,110.98 L599.0,110.55 L606.0,110.25 L613.0,110.06 L620.0,110.0 L627.0,110.06 L634.0,110.25 L641.0,110.55 L648.0,110.98 L655.0,111.52 L662.0,112.18 L669.0,112.95 L676.0,113.82 L683.0,114.79 L690.0,115.86 L697.0,117.01 L704.0,118.24 L711.0,119.55 L718.0,120.92 L725.0,122.35 L732.0,123.82 L739.0,125.33 L746.0,126.87 L753.0,128.43 L760.0,130.0 L767.0,131.57 L774.0,133.13 L781.0,134.67 L788.0,136.18 L795.0,137.65 L802.0,139.08 L809.0,140.45 L816.0,141.76 L823.0,142.99 L830.0,144.14 L837.0,145.21 L844.0,146.18 L851.0,147.05 L858.0,147.82 L865.0,148.48 L872.0,149.02 L879.0,149.45 L886.0,149.75 L893.0,149.94 L900.0,150.0" fill="none" stroke="#2563eb" stroke-width="3"/>
<line x1="68.75" y1="110.1" x2="62.73" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="86.25" y1="110.86" x2="68.45" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="103.75" y1="112.36" x2="74.91" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="121.25" y1="114.54" x2="82.53" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="138.75" y1="117.31" x2="91.7" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="156.25" y1="120.57" x2="102.7" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="173.75" y1="124.19" x2="115.76" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="191.25" y1="128.04" x2="131.01" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="208.75" y1="131.96" x2="148.51" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="226.25" y1="135.81" x2="168.26" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="243.75" y1="139.43" x2="190.2" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="261.25" y1="142.69" x2="214.2" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="278.75" y1="145.46" x2="240.03" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="296.25" y1="147.64" x2="267.41" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="313.75" y1="149.14" x2="295.95" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="331.25" y1="149.9" x2="325.23" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="348.75" y1="149.9" x2="354.77" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="366.25" y1="149.14" x2="384.05" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="383.75" y1="147.64" x2="412.59" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="401.25" y1="145.46" x2="439.97" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="418.75" y1="142.69" x2="465.8" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="436.25" y1="139.43" x2="489.8" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="453.75" y1="135.81" x2="511.74" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="471.25" y1="131.96" x2="531.49" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="488.75" y1="128.04" x2="548.99" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="506.25" y1="124.19" x2="564.24" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="523.75" y1="120.57" x2="577.3" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="541.25" y1="117.31" x2="588.3" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="558.75" y1="114.54" x2="597.47" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="576.25" y1="112.36" x2="605.09" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="593.75" y1="110.86" x2="611.55" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="611.25" y1="110.1" x2="617.27" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="628.75" y1="110.1" x2="622.73" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="646.25" y1="110.86" x2="628.45" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="663.75" y1="112.36" x2="634.91" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="681.25" y1="114.54" x2="642.53" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="698.75" y1="117.31" x2="651.7" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="716.25" y1="120.57" x2="662.7" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="733.75" y1="124.19" x2="675.76" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="751.25" y1="128.04" x2="691.01" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="768.75" y1="131.96" x2="708.51" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="786.25" y1="135.81" x2="728.26" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="803.75" y1="139.43" x2="750.2" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="821.25" y1="142.69" x2="774.2" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="838.75" y1="145.46" x2="800.03" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="856.25" y1="147.64" x2="827.41" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="873.75" y1="149.14" x2="855.95" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="891.25" y1="149.9" x2="885.23" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3331;0.3333;0.6152;0.6154;1.0000" values="0;0;1;1;0;0"/><path d="M60.0,130.58 L67.0,132.15 L74.0,133.7 L81.0,135.23 L88.0,136.73 L95.0,138.19 L102.0,139.6 L109.0,140.94 L116.0,142.22 L123.0,143.43 L130.0,144.55 L137.0,145.58 L144.0,146.52 L151.0,147.35 L158.0,148.08 L165.0,148.69 L172.0,149.19 L179.0,149.58 L186.0,149.84 L193.0,149.98 L200.0,149.99 L207.0,149.88 L214.0,149.65 L221.0,149.3 L228.0,148.83 L235.0,148.25 L242.0,147.55 L249.0,146.74 L256.0,145.83 L263.0,144.82 L270.0,143.72 L277.0,142.54 L284.0,141.28 L291.0,139.95 L298.0,138.56 L305.0,137.11 L312.0,135.62 L319.0,134.1 L326.0,132.55 L333.0,130.99 L340.0,129.42 L347.0,127.85 L354.0,126.3 L361.0,124.77 L368.0,123.27 L375.0,121.81 L382.0,120.4 L389.0,119.06 L396.0,117.78 L403.0,116.57 L410.0,115.45 L417.0,114.42 L424.0,113.48 L431.0,112.65 L438.0,111.92 L445.0,111.31 L452.0,110.81 L459.0,110.42 L466.0,110.16 L473.0,110.02 L480.0,110.01 L487.0,110.12 L494.0,110.35 L501.0,110.7 L508.0,111.17 L515.0,111.75 L522.0,112.45 L529.0,113.26 L536.0,114.17 L543.0,115.18 L550.0,116.28 L557.0,117.46 L564.0,118.72 L571.0,120.05 L578.0,121.44 L585.0,122.89 L592.0,124.38 L599.0,125.9 L606.0,127.45 L613.0,129.01 L620.0,130.58 L627.0,132.15 L634.0,133.7 L641.0,135.23 L648.0,136.73 L655.0,138.19 L662.0,139.6 L669.0,140.94 L676.0,142.22 L683.0,143.43 L690.0,144.55 L697.0,145.58 L704.0,146.52 L711.0,147.35 L718.0,148.08 L725.0,148.69 L732.0,149.19 L739.0,149.58 L746.0,149.84 L753.0,149.98 L760.0,149.99 L767.0,149.88 L774.0,149.65 L781.0,149.3 L788.0,148.83 L795.0,148.25 L802.0,147.55 L809.0,146.74 L816.0,145.83 L823.0,144.82 L830.0,143.72 L837.0,142.54 L844.0,141.28 L851.0,139.95 L858.0,138.56 L865.0,137.11 L872.0,135.62 L879.0,134.1 L886.0,132.55 L893.0,130.99 L900.0,129.42" fill="none" stroke="#2563eb" stroke-width="3"/>
<line x1="68.75" y1="132.54" x2="8.7" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="86.25" y1="136.36" x2="28.79" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="103.75" y1="139.94" x2="51.05" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="121.25" y1="143.13" x2="75.33" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="138.75" y1="145.82" x2="101.41" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="156.25" y1="147.91" x2="128.98" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="173.75" y1="149.3" x2="157.67" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="191.25" y1="149.95" x2="187.02" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="208.75" y1="149.84" x2="216.55" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="226.25" y1="148.96" x2="245.75" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="243.75" y1="147.36" x2="274.15" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="261.25" y1="145.08" x2="301.31" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="278.75" y1="142.23" x2="326.89" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="296.25" y1="138.91" x2="350.59" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="313.75" y1="135.24" x2="372.22" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="331.25" y1="131.38" x2="391.64" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="348.75" y1="127.46" x2="408.8" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="366.25" y1="123.64" x2="423.71" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="383.75" y1="120.06" x2="436.45" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="401.25" y1="116.87" x2="447.17" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="418.75" y1="114.18" x2="456.09" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="436.25" y1="112.09" x2="463.52" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="453.75" y1="110.7" x2="469.83" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="471.25" y1="110.05" x2="475.48" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="488.75" y1="110.16" x2="480.95" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="506.25" y1="111.04" x2="486.75" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="523.75" y1="112.64" x2="493.35" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="541.25" y1="114.92" x2="501.19" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="558.75" y1="117.77" x2="510.61" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="576.25" y1="121.09" x2="521.91" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="593.75" y1="124.76" x2="535.28" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="611.25" y1="128.62" x2="550.86" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="628.75" y1="132.54" x2="568.7" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="646.25" y1="136.36" x2="588.79" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="663.75" y1="139.94" x2="611.05" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="681.25" y1="143.13" x2="635.33" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="698.75" y1="145.82" x2="661.41" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="716.25" y1="147.91" x2="688.98" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="733.75" y1="149.3" x2="717.67" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="751.25" y1="149.95" x2="747.02" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="768.75" y1="149.84" x2="776.55" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="786.25" y1="148.96" x2="805.75" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="803.75" y1="147.36" x2="834.15" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="821.25" y1="145.08" x2="861.31" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="838.75" y1="142.23" x2="886.89" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="856.25" y1="138.91" x2="910.59" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="873.75" y1="135.24" x2="932.22" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="891.25" y1="131.38" x2="951.64" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6152;0.6154;1.0000" values="0;0;1;1"/><path d="M60.0,149.97 L67.0,149.81 L74.0,149.54 L81.0,149.14 L88.0,148.63 L95.0,148.0 L102.0,147.26 L109.0,146.41 L116.0,145.47 L123.0,144.42 L130.0,143.29 L137.0,142.08 L144.0,140.79 L151.0,139.44 L158.0,138.02 L165.0,136.56 L172.0,135.06 L179.0,133.53 L186.0,131.97 L193.0,130.4 L200.0,128.83 L207.0,127.27 L214.0,125.72 L221.0,124.2 L228.0,122.72 L235.0,121.28 L242.0,119.9 L249.0,118.57 L256.0,117.32 L263.0,116.15 L270.0,115.06 L277.0,114.06 L284.0,113.16 L291.0,112.37 L298.0,111.68 L305.0,111.11 L312.0,110.65 L319.0,110.31 L326.0,110.1 L333.0,110.0 L340.0,110.03 L347.0,110.19 L354.0,110.46 L361.0,110.86 L368.0,111.37 L375.0,112.0 L382.0,112.74 L389.0,113.59 L396.0,114.53 L403.0,115.58 L410.0,116.71 L417.0,117.92 L424.0,119.21 L431.0,120.56 L438.0,121.98 L445.0,123.44 L452.0,124.94 L459.0,126.47 L466.0,128.03 L473.0,129.6 L480.0,131.17 L487.0,132.73 L494.0,134.28 L501.0,135.8 L508.0,137.28 L515.0,138.72 L522.0,140.1 L529.0,141.43 L536.0,142.68 L543.0,143.85 L550.0,144.94 L557.0,145.94 L564.0,146.84 L571.0,147.63 L578.0,148.32 L585.0,148.89 L592.0,149.35 L599.0,149.69 L606.0,149.9 L613.0,150.0 L620.0,149.97 L627.0,149.81 L634.0,149.54 L641.0,149.14 L648.0,148.63 L655.0,148.0 L662.0,147.26 L669.0,146.41 L676.0,145.47 L683.0,144.42 L690.0,143.29 L697.0,142.08 L704.0,140.79 L711.0,139.44 L718.0,138.02 L725.0,136.56 L732.0,135.06 L739.0,133.53 L746.0,131.97 L753.0,130.4 L760.0,128.83 L767.0,127.27 L774.0,125.72 L781.0,124.2 L788.0,122.72 L795.0,121.28 L802.0,119.9 L809.0,118.57 L816.0,117.32 L823.0,116.15 L830.0,115.06 L837.0,114.06 L844.0,113.16 L851.0,112.37 L858.0,111.68 L865.0,111.11 L872.0,110.65 L879.0,110.31 L886.0,110.1 L893.0,110.0 L900.0,110.03" fill="none" stroke="#2563eb" stroke-width="3"/>
<line x1="68.75" y1="149.76" x2="78.32" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="86.25" y1="148.77" x2="107.43" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="103.75" y1="147.06" x2="135.67" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="121.25" y1="144.69" x2="162.62" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="138.75" y1="141.76" x2="187.94" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="156.25" y1="138.38" x2="211.34" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="173.75" y1="134.68" x2="232.64" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="191.25" y1="130.8" x2="251.73" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="208.75" y1="126.88" x2="268.56" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="226.25" y1="123.09" x2="283.14" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="243.75" y1="119.56" x2="295.57" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="261.25" y1="116.43" x2="306.0" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="278.75" y1="113.83" x2="314.68" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="296.25" y1="111.84" x2="321.91" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="313.75" y1="110.55" x2="328.1" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="331.25" y1="110.02" x2="333.69" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="348.75" y1="110.24" x2="339.18" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="366.25" y1="111.23" x2="345.07" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="383.75" y1="112.94" x2="351.83" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="401.25" y1="115.31" x2="359.88" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="418.75" y1="118.24" x2="369.56" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="436.25" y1="121.62" x2="381.16" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="453.75" y1="125.32" x2="394.86" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="471.25" y1="129.2" x2="410.77" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="488.75" y1="133.12" x2="428.94" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="506.25" y1="136.91" x2="449.36" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="523.75" y1="140.44" x2="471.93" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="541.25" y1="143.57" x2="496.5" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="558.75" y1="146.17" x2="522.82" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="576.25" y1="148.16" x2="550.59" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="593.75" y1="149.45" x2="579.4" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="611.25" y1="149.98" x2="608.81" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="628.75" y1="149.76" x2="638.32" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="646.25" y1="148.77" x2="667.43" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="663.75" y1="147.06" x2="695.67" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="681.25" y1="144.69" x2="722.62" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="698.75" y1="141.76" x2="747.94" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="716.25" y1="138.38" x2="771.34" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="733.75" y1="134.68" x2="792.64" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="751.25" y1="130.8" x2="811.73" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="768.75" y1="126.88" x2="828.56" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="786.25" y1="123.09" x2="843.14" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="803.75" y1="119.56" x2="855.57" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="821.25" y1="116.43" x2="866.0" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="838.75" y1="113.83" x2="874.68" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="856.25" y1="111.84" x2="881.91" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="873.75" y1="110.55" x2="888.1" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
<line x1="891.25" y1="110.02" x2="893.69" y2="330.0" stroke="#fbbf24" stroke-width="1.2" opacity="0.8"/>
</g>
<rect x="30" y="366" width="900" height="130" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="356" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">水底の 1 マスあたりに当たった光線の本数(平らな水面なら、どこも 2 本)</text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3331;0.3333;1.0000" values="1;1;0;0"/><rect x="40.0" y="420" width="31.5" height="70" fill="#f6aa20"/>
<text x="55.75" y="417" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">5</text>
<rect x="77.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="93.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="115.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="130.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="152.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="168.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="190.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="205.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="227.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="243.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="265.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="280.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="302.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="318.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="340.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="355.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="377.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="393.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="415.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="430.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="452.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="468.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="490.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="505.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="527.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="543.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="565.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="580.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="602.5" y="420" width="31.5" height="70" fill="#f6aa20"/>
<text x="618.25" y="417" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">5</text>
<rect x="640.0" y="420" width="31.5" height="70" fill="#f6aa20"/>
<text x="655.75" y="417" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">5</text>
<rect x="677.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="693.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="715.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="730.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="752.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="768.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="790.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="805.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="827.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="843.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="865.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="880.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="902.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="918.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<text x="900" y="392" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d">最も明るい所: 5 本(平均の 2.5 倍)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3331;0.3333;0.6152;0.6154;1.0000" values="0;0;1;1;0;0"/><rect x="40.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="55.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="77.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="93.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="115.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="130.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="152.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="168.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="190.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="205.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="227.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="243.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="265.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="280.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="302.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="318.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="340.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="355.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="377.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="393.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="415.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="430.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="452.5" y="420" width="31.5" height="70" fill="#f6aa20"/>
<text x="468.25" y="417" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">5</text>
<rect x="490.0" y="420" width="31.5" height="70" fill="#f6aa20"/>
<text x="505.75" y="417" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">5</text>
<rect x="527.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="543.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="565.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="580.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="602.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="618.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="640.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="655.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="677.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="693.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="715.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="730.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="752.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="768.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="790.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="805.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="827.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="843.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="865.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="880.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="902.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="918.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<text x="900" y="392" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d">最も明るい所: 5 本(平均の 2.5 倍)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6152;0.6154;1.0000" values="0;0;1;1"/><rect x="40.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="55.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="77.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="93.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="115.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="130.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="152.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="168.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="190.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="205.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="227.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="243.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="265.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="280.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="302.5" y="406" width="31.5" height="84" fill="#f59e0b"/>
<text x="318.25" y="403" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">6</text>
<rect x="340.0" y="434" width="31.5" height="56" fill="#f8b635"/>
<text x="355.75" y="431" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">4</text>
<rect x="377.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="393.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="415.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="430.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="452.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="468.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="490.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="505.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="527.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="543.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="565.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="580.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="602.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="618.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="640.0" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="655.75" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="677.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="693.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="715.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="730.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="752.5" y="476" width="31.5" height="14" fill="#fcda75"/>
<text x="768.25" y="473" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">1</text>
<rect x="790.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="805.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="827.5" y="462" width="31.5" height="28" fill="#face60"/>
<text x="843.25" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="865.0" y="462" width="31.5" height="28" fill="#face60"/>
<text x="880.75" y="459" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">2</text>
<rect x="902.5" y="420" width="31.5" height="70" fill="#f6aa20"/>
<text x="918.25" y="417" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#92400e">5</text>
<text x="900" y="392" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d">最も明るい所: 6 本(平均の 3.0 倍)</text>
</g>
<line x1="40" y1="462.0" x2="930" y2="462.0" stroke="#2ea043" stroke-width="2" stroke-dasharray="6 5"/>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">波の斜面が光を曲げる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">時刻 1: 斜面が光を中央に寄せる所が明るい線になる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;0.3331;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">時刻 2: 波が動くと、明るい線も動く<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3331;0.3333;0.6152;0.6154;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">時刻 3: 本数が集まった所ほど明るい。これがコースティクス<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6152;0.6154;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:caustics-rays:end -->

## コースティクス
<strong>コースティクス</strong>は 波打つ水面がレンズのように光を集め、底に明るい網目模様ができる現象です。波の凹凸の形で光が集まる所と散る所ができます。

コースティクスの方式は 3 つです。アニメする模様のテクスチャは、ループするコースティクス模様をライトの方向から底に投影して足す定番の安い方法です。シミュレーションは水面の法線から屈折を計算し、底に落ちる光の集まりを求める重い正確な方法です。ヤコビアン風の近似は水面の法線のラプラシアン（凸凹）から、集光の強さを近似します。

### テクスチャを投影する

```hlsl
float3 light_space = mul(float4(world_position, 1), light_view_projection).xyz;
float2 caustics_uv = world_position.xz * caustics_scale;

float c1 = caustics_texture.Sample(linear_wrap, caustics_uv + time * float2(0.03, 0.02)).r;
float c2 = caustics_texture.Sample(linear_wrap, caustics_uv * 1.3 - time * float2(0.02, 0.03)).r;
float caustics = min(c1, c2);

float depth_fade = exp(-water_depth_at_point * caustics_falloff);
float3 lit = base_color + sun_color * caustics * depth_fade * n_dot_l;
```

| 点 | 説明 |
| --- | --- |
| 2 枚の `min` | 向きの違う 2 枚の暗い方を取ると、明るい線が細く交差してリアルな網目 |
| 水深で減衰 | 深い底ほど、光が届かず弱い |
| `n_dot_l` | 太陽に向いた面だけ（壁には弱く） |
| 水面より上は出さない | 水位より下の位置だけに投影 |
| ワールド座標の UV | カメラが動いても底に貼りつく（真上から投影が簡単） |

### 色収差で見栄えを上げる

コースティクスを RGB でわずかにずらして取ると、縁が虹色に光って、よりそれらしく見えます。

```hlsl
float r = caustics_texture.Sample(linear_wrap, caustics_uv + float2(0.002, 0)).r;
float g = caustics_texture.Sample(linear_wrap, caustics_uv).r;
float b = caustics_texture.Sample(linear_wrap, caustics_uv - float2(0.002, 0)).r;
float3 caustics_rgb = float3(r, g, b);
```

## コースティクスとは

水面の波は <strong>レンズのように光を屈折</strong>させます。屈折した光は 水底で集まる場所と、散る場所ができ明るい網目状の模様が揺れます。これがコースティクス（集光模様）です。プールの底でゆらゆら動く光の網が典型です。

```text
        太陽
       ↓ ↓ ↓ ↓ ↓ ↓
━━━━ ╲╱ ╲╱ ╲╱ ╲╱ ━━━━  ← 波のある水面（光が、曲がる）
     ↘ ↓ ↙   ↘ ↓ ↙
        ↘↓↙       ↘↓↙
    ──── 明るい ──── 暗い ──── 明るい ──   ← 水底（光が、集まった所が、明るい）
```

## 方法 1：アニメーションする、テクスチャを投影する

最も簡単な方法は <strong>コースティクスの模様をあらかじめ作ったテクスチャ</strong>を水底に投影してゆっくり動かすことです。

```hlsl
// 水底の、ライティングにコースティクスを足す。
float2 uv = world_pos.xz * caustic_scale;
// 2 枚を違う速さと、向きで、動かして、重ねる（周期が見えにくくなる）。
float c1 = g_caustic_tex.Sample(g_linear_wrap, uv + time * float2( 0.03, 0.02)).r;
float c2 = g_caustic_tex.Sample(g_linear_wrap, uv * 1.3 - time * float2(0.02, 0.03)).r;
float caustic = min(c1, c2);                                 // 小さい方を取る → 模様が細く、鋭くなる
float3 lit = sun_color * n_dot_l * (1.0 + caustic * caustic_strength);
```

| 項目 | 内容 |
| --- | --- |
| テクスチャ | タイルできる、コースティクスの画像。ゆっくり変化するアニメーション（フレームの、連続）も使える |
| 投影の向き | 太陽の方向。水底の傾きに関係なく真上から（または、太陽の向きで）投影する |
| `min` で重ねる | 2 枚の、暗い所が重なった所がさらに暗くなり、網の線が細く見える |
| 強さ | 水深とともに弱める（深いと光が届かない） |

### 水深で弱める

```hlsl
// 深さとともに、コースティクスを弱める（水の吸収）。
float3 caustic_color = sun_color * exp(-absorption * depth_below_surface) * caustic * caustic_strength;
```

コースティクスは 太陽光の模様なので 水に吸収されます。水深が深いと暗く青くなります（[Color by Water Depth](../shading/depth-color.md)）。

## 方法 2：波からリアルタイムに計算する

波の形（法線）から <strong>屈折した光が水底の、どこに届くか</strong>を計算し 光が集まる場所を数えることでコースティクスを計算できます（Guardado ら、2004、Wallace、2015）。

### 考え方

水面の 1 つの小さな面を通った光は屈折して 水底の別の大きさの面に当たります。

| 水底での面積 | 光の強さ |
| --- | --- |
| 水面の面積より小さい | 光が集まる → 明るい |
| 水面の面積より大きい | 光が広がる → 暗い |

```text
明るさ ∝ 水面での面積 / 水底での面積
```

### 実装（画面の微分を使う方法）

水面の各点から 屈折光を水底へ飛ばし、水底の位置の隣のピクセルとの差から、面積の変化を求めます。

```hlsl
// 水面の、頂点（または画素）から、屈折光が水底に当たる位置を求める。
float3 refracted = refract(-sun_dir, wave_normal, 1.0 / 1.33);
float t = (floor_height - world_pos.y) / refracted.y;           // 水底（y = floor_height）までの距離
float3 floor_pos = world_pos + refracted * t;                    // 水底の位置

// 隣のピクセルとの、水底の位置の差から、面積の変化を求める。
float3 dx = ddx(floor_pos);
float3 dy = ddy(floor_pos);
float new_area = length(cross(dx, dy));                           // 水底での面積
float3 ox = ddx(world_pos);
float3 oy = ddy(world_pos);
float old_area = length(cross(ox, oy));                           // 水面での面積

float caustic = old_area / max(new_area, 1e-5);                   // 面積が小さくなるほど、明るい
```

この計算を 水底に描く（水面から見て、水底の位置に書き込む）ことで、コースティクスの画像（テクスチャ）を作れます。そのテクスチャを水底や水中の物に投影して使います。

| 項目 | 内容 |
| --- | --- |
| 解像度 | 512×512〜1024×1024 のテクスチャ。カメラの周りの窓（円環バッファでもよい） |
| 精度 | 波の法線の精度に依存。高周波の波を使うほど模様が細かい |
| 水底の形 | 水底を平面と、仮定する簡易版が多い（実際の、起伏のある水底ではずれる） |
| 太陽以外の光 | 空からの光は、広い範囲から来るのでコースティクスは、出ない（ぼやける） |

## 方法の選び方

| 方法 | 見た目 | コスト | 向く場面 |
| --- | --- | --- | --- |
| 投影テクスチャ（事前に作った） | 動きが一定の、模様 | 小 | ほとんどのゲーム |
| 波からリアルタイムに計算 | 波と正確に連動 | 中 | 波が大きい海。見た目を重視 |

波の動きと連動しなくても <strong>多くの人は、気づきません</strong>。投影テクスチャで十分なことが、ほとんどです。

## 水の外に出る光

水の<strong>外</strong>にある 壁や船体にも、水面で反射した揺れる光の模様が映ります（水辺の壁に水の揺れが、映る）。同じコースティクスのテクスチャを水の近くの物に弱く投影すると水辺の、雰囲気が出ます。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 水面の外には出さない | コースティクスを水の中の物にだけ掛ける（水の上の地面に掛けない）。水位以下の物だけ |
| 影との関係 | 影の中は太陽が当たらない。コースティクスも影の中では消す（影の係数を掛ける） |
| 夜 | 太陽が無いので消える |
| 曇り | 太陽光が弱いので、弱める |

## よくあるミス

??? failure "水底の模様が動かない・単調"
    <strong>2 枚を逆向きに流して重ねる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 揺れる模様を光の方向から投影

## 参考

- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Wallace, "Rendering Realtime Caustics in WebGL", Medium, 2015（屈折した光の、面積の変化からコースティクスを作る）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Underwater Rendering](index.md)
- [Underwater God Rays](god-rays.md)

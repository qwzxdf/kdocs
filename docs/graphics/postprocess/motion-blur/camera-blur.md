---
title: Camera Motion Blur
tags:
  - 描画
---

# Camera Motion Blur

**カメラが動いたり回ったりすると、静止している背景全体が、流れるように見えます**。**カメラ モーション ブラー**は、**この背景の流れ**を**表現**する**ブラー**で、**コストが安く、スピード感への効果が大きい**ため、**最初に実装すべき**部分です。**必要なのは画素ごとの深度と前フレームのカメラ行列だけ**で、**動く物体の速度バッファを作らなくても実現**できます。このページでは、**深度から速度を再構成する方法・並進と回転の違い・注意点（動く物体・遠景）・より良いやり方**を説明します。

!!! tip "ポイント"
    - カメラ ブラー ＝ <strong>カメラの動きによる、静止した物の見かけの動き</strong>を<strong>ぼかしにする</strong>。
    - <strong>深度（ワールド位置を再構成）</strong>＋<strong>前フレームのカメラ行列</strong>で、<strong>各画素の速度が分かる</strong>。
    - <strong>回転</strong>は<strong>画面全体が同じ向きに流れる</strong>。<strong>並進</strong>は<strong>近い物ほど速く流れる（視差）</strong>。
    - <strong>動く物体には、カメラ速度は不正確</strong>（<strong>物体ブラー</strong>で上書き）。
    - <strong>遠景（深度が最奥）</strong>は<strong>回転の影響だけ</strong>。
    - <strong>ゲーム内のカット切り替え</strong>では<strong>速度を 0 に</strong>する。

<!-- fig:camera-blur:begin -->

<svg class="fig illust motion" data-fig="camera-blur" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-camera-blur" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="cb-clip-190"><rect x="20" y="100" width="340" height="240"/>
</clipPath>
<clipPath id="cb-clip-590"><rect x="420" y="100" width="340" height="240"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">カメラ ブラー:カメラの動きだけから、画面全体の速度が決まる</text>
<rect x="20" y="100" width="340" height="240" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<text x="190" y="88" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">前へ進む:中心から外へ、放射状（外ほど速い）</text>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><line x1="40" y1="120" x2="6.72" y2="97.81" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="6.72,97.81 15.59,98.92 11.16,105.58" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1023;0.1026;1.0000" values="0;0;1;1"/><line x1="40" y1="170" x2="2.05" y2="157.35" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="2.05,157.35 10.91,156.09 8.38,163.68" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1179;0.1183;1.0000" values="0;0;1;1"/><line x1="40" y1="220" x2="0.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="0.0,220.0 8.0,216.0 8.0,224.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="40" y1="270" x2="2.05" y2="282.65" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="2.05,282.65 8.38,276.32 10.91,283.91" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="40" y1="320" x2="6.72" y2="342.19" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="6.72,342.19 11.16,334.42 15.59,341.08" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1023;0.1026;1.0000" values="0;0;1;1"/><line x1="90" y1="120" x2="62.0" y2="92.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="62.0,92.0 70.49,94.83 64.83,100.49" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1179;0.1183;1.0000" values="0;0;1;1"/><line x1="90" y1="170" x2="62.0" y2="156.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="62.0,156.0 70.94,156.0 67.37,163.16" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="90" y1="220" x2="62.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="62.0,220.0 70.0,216.0 70.0,224.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="90" y1="270" x2="62.0" y2="284.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="62.0,284.0 67.37,276.84 70.94,284.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="90" y1="320" x2="62.0" y2="348.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="62.0,348.0 64.83,339.51 70.49,345.17" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1179;0.1183;1.0000" values="0;0;1;1"/><line x1="140" y1="120" x2="126.0" y2="92.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="126.0,92.0 133.16,97.37 126.0,100.94" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="140" y1="170" x2="126.0" y2="156.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="126.0,156.0 134.49,158.83 128.83,164.49" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="140" y1="220" x2="126.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="126.0,220.0 134.0,216.0 134.0,224.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="140" y1="270" x2="126.0" y2="284.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="126.0,284.0 128.83,275.51 134.49,281.17" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="140" y1="320" x2="126.0" y2="348.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="126.0,348.0 126.0,339.06 133.16,342.63" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="190" y1="120" x2="190.0" y2="92.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="190.0,92.0 194.0,100.0 186.0,100.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="190" y1="170" x2="190.0" y2="156.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="190.0,156.0 194.0,164.0 186.0,164.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="190" y1="270" x2="190.0" y2="284.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="190.0,284.0 186.0,276.0 194.0,276.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="190" y1="320" x2="190.0" y2="348.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="190.0,348.0 186.0,340.0 194.0,340.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="240" y1="120" x2="254.0" y2="92.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="254.0,92.0 254.0,100.94 246.84,97.37" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="240" y1="170" x2="254.0" y2="156.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="254.0,156.0 251.17,164.49 245.51,158.83" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="240" y1="220" x2="254.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="254.0,220.0 246.0,224.0 246.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="240" y1="270" x2="254.0" y2="284.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="254.0,284.0 245.51,281.17 251.17,275.51" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2118;0.2122;1.0000" values="0;0;1;1"/><line x1="240" y1="320" x2="254.0" y2="348.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="254.0,348.0 246.84,342.63 254.0,339.06" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="290" y1="120" x2="318.0" y2="92.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="318.0,92.0 315.17,100.49 309.51,94.83" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="290" y1="170" x2="318.0" y2="156.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="318.0,156.0 312.63,163.16 309.06,156.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="290" y1="220" x2="318.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="318.0,220.0 310.0,224.0 310.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2118;0.2122;1.0000" values="0;0;1;1"/><line x1="290" y1="270" x2="318.0" y2="284.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="318.0,284.0 309.06,284.0 312.63,276.84" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2275;0.2278;1.0000" values="0;0;1;1"/><line x1="290" y1="320" x2="318.0" y2="348.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="318.0,348.0 309.51,345.17 315.17,339.51" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="340" y1="120" x2="373.28" y2="97.81" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="373.28,97.81 368.84,105.58 364.41,98.92" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="340" y1="170" x2="377.95" y2="157.35" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="377.95,157.35 371.62,163.68 369.09,156.09" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2118;0.2122;1.0000" values="0;0;1;1"/><line x1="340" y1="220" x2="380.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="380.0,220.0 372.0,224.0 372.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2275;0.2278;1.0000" values="0;0;1;1"/><line x1="340" y1="270" x2="377.95" y2="282.65" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="377.95,282.65 369.09,283.91 371.62,276.32" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-190)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;1.0000" values="0;0;1;1"/><line x1="340" y1="320" x2="373.28" y2="342.19" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="373.28,342.19 364.41,341.08 368.84,334.42" fill="#2563eb"/>
</g>
<rect x="420" y="100" width="340" height="240" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<text x="590" y="88" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">横を向く:画面全体が、同じ向きに同じ速さ</text>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><line x1="440" y1="120" x2="468.0" y2="120.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="468.0,120.0 460.0,124.0 460.0,116.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1023;0.1026;1.0000" values="0;0;1;1"/><line x1="440" y1="170" x2="468.0" y2="170.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="468.0,170.0 460.0,174.0 460.0,166.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1179;0.1183;1.0000" values="0;0;1;1"/><line x1="440" y1="220" x2="468.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="468.0,220.0 460.0,224.0 460.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="440" y1="270" x2="468.0" y2="270.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="468.0,270.0 460.0,274.0 460.0,266.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="440" y1="320" x2="468.0" y2="320.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="468.0,320.0 460.0,324.0 460.0,316.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1023;0.1026;1.0000" values="0;0;1;1"/><line x1="490" y1="120" x2="518.0" y2="120.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="518.0,120.0 510.0,124.0 510.0,116.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1179;0.1183;1.0000" values="0;0;1;1"/><line x1="490" y1="170" x2="518.0" y2="170.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="518.0,170.0 510.0,174.0 510.0,166.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="490" y1="220" x2="518.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="518.0,220.0 510.0,224.0 510.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="490" y1="270" x2="518.0" y2="270.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="518.0,270.0 510.0,274.0 510.0,266.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="490" y1="320" x2="518.0" y2="320.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="518.0,320.0 510.0,324.0 510.0,316.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1179;0.1183;1.0000" values="0;0;1;1"/><line x1="540" y1="120" x2="568.0" y2="120.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="568.0,120.0 560.0,124.0 560.0,116.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="540" y1="170" x2="568.0" y2="170.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="568.0,170.0 560.0,174.0 560.0,166.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="540" y1="220" x2="568.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="568.0,220.0 560.0,224.0 560.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="540" y1="270" x2="568.0" y2="270.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="568.0,270.0 560.0,274.0 560.0,266.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="540" y1="320" x2="568.0" y2="320.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="568.0,320.0 560.0,324.0 560.0,316.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1336;0.1339;1.0000" values="0;0;1;1"/><line x1="590" y1="120" x2="618.0" y2="120.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="618.0,120.0 610.0,124.0 610.0,116.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="590" y1="170" x2="618.0" y2="170.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="618.0,170.0 610.0,174.0 610.0,166.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="590" y1="220" x2="618.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="618.0,220.0 610.0,224.0 610.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="590" y1="270" x2="618.0" y2="270.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="618.0,270.0 610.0,274.0 610.0,266.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="590" y1="320" x2="618.0" y2="320.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="618.0,320.0 610.0,324.0 610.0,316.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1492;0.1496;1.0000" values="0;0;1;1"/><line x1="640" y1="120" x2="668.0" y2="120.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="668.0,120.0 660.0,124.0 660.0,116.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="640" y1="170" x2="668.0" y2="170.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="668.0,170.0 660.0,174.0 660.0,166.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="640" y1="220" x2="668.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="668.0,220.0 660.0,224.0 660.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="640" y1="270" x2="668.0" y2="270.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="668.0,270.0 660.0,274.0 660.0,266.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2118;0.2122;1.0000" values="0;0;1;1"/><line x1="640" y1="320" x2="668.0" y2="320.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="668.0,320.0 660.0,324.0 660.0,316.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1649;0.1652;1.0000" values="0;0;1;1"/><line x1="690" y1="120" x2="718.0" y2="120.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="718.0,120.0 710.0,124.0 710.0,116.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="690" y1="170" x2="718.0" y2="170.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="718.0,170.0 710.0,174.0 710.0,166.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="690" y1="220" x2="718.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="718.0,220.0 710.0,224.0 710.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2118;0.2122;1.0000" values="0;0;1;1"/><line x1="690" y1="270" x2="718.0" y2="270.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="718.0,270.0 710.0,274.0 710.0,266.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2275;0.2278;1.0000" values="0;0;1;1"/><line x1="690" y1="320" x2="718.0" y2="320.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="718.0,320.0 710.0,324.0 710.0,316.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1805;0.1809;1.0000" values="0;0;1;1"/><line x1="740" y1="120" x2="768.0" y2="120.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="768.0,120.0 760.0,124.0 760.0,116.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1962;0.1965;1.0000" values="0;0;1;1"/><line x1="740" y1="170" x2="768.0" y2="170.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="768.0,170.0 760.0,174.0 760.0,166.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2118;0.2122;1.0000" values="0;0;1;1"/><line x1="740" y1="220" x2="768.0" y2="220.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="768.0,220.0 760.0,224.0 760.0,216.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2275;0.2278;1.0000" values="0;0;1;1"/><line x1="740" y1="270" x2="768.0" y2="270.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="768.0,270.0 760.0,274.0 760.0,266.0" fill="#2563eb"/>
</g>
<g opacity="0" clip-path="url(#cb-clip-590)"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;1.0000" values="0;0;1;1"/><line x1="740" y1="320" x2="768.0" y2="320.0" stroke="#2563eb" stroke-width="2.5"/>
<polygon points="768.0,320.0 760.0,324.0 760.0,316.0" fill="#2563eb"/>
</g>
<text x="40" y="380" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">物体の速度は使わず、深度から求めた位置を、前フレームのカメラ行列で投影し直して、差を取る。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="404" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">安く済むが、動く物体のブレは出ない（物体の動きは、速度バッファが必要）。</text>
</svg>

<!-- fig:camera-blur:end -->

## 並進と回転

**カメラの動きは、2 種類**あります。

| 動き | 画面での見え方 |
| --- | --- |
| <strong>回転（見回す）</strong> | **画面全体が同じ向きにほぼ同じ速さで流れる**（**距離に依らない**） |
| <strong>並進（歩く・走る・走行）</strong> | **近い物ほど速く、遠い物ほど遅く流れる**（**視差**）。**進行方向の中心から外へ放射状に広がる** |

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="カメラの動きと速度">
<text x="20" y="26" class="fig-title">回転は一様に流れ、前進は中心から放射状に流れる</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">回転（右を向く）</text>
<rect x="0" y="0" width="300" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<g stroke="#e5484d" stroke-width="2.5" marker-end="url(#cb-arrow)"><line x1="260" y1="30" x2="200" y2="30"/><line x1="260" y1="70" x2="200" y2="70"/><line x1="260" y1="110" x2="200" y2="110"/><line x1="140" y1="30" x2="80" y2="30"/><line x1="140" y1="70" x2="80" y2="70"/><line x1="140" y1="110" x2="80" y2="110"/></g>
<defs><marker id="cb-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#e5484d"/></marker></defs>
<text x="0" y="164" style="font-size:12px">どこも同じ向き・同じ大きさ</text>
</g>
<g transform="translate(420,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">並進（前に進む）</text>
<rect x="0" y="0" width="300" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="150" cy="70" r="4" fill="#2563eb"/>
<g stroke="#e5484d" stroke-width="2.5" marker-end="url(#cb-arrow)"><line x1="160" y1="65" x2="185" y2="52"/><line x1="140" y1="65" x2="115" y2="52"/><line x1="160" y1="75" x2="185" y2="88"/><line x1="140" y1="75" x2="115" y2="88"/><line x1="200" y1="50" x2="262" y2="14"/><line x1="100" y1="50" x2="38" y2="14"/><line x1="200" y1="90" x2="262" y2="126"/><line x1="100" y1="90" x2="38" y2="126"/></g>
<text x="0" y="164" style="font-size:12px">中心は動かず、外へ行くほど速い（近い物ほど速い）</text>
</g>
</svg>

## 深度から速度を作る

**画素の深度から、その点のワールド位置を再構成し**、**前フレームのカメラでその点がどこに見えていたか**を**計算**します。

```hlsl
float2 CameraVelocity(float2 uv, float depth) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  float4 clip = float4(ndc, depth, 1.0);
  float4 world = mul(clip, inverse_view_projection);
  world /= world.w;
  float4 previous_clip = mul(world, previous_view_projection);
  float2 previous_ndc = previous_clip.xy / previous_clip.w;
  float2 previous_uv = float2(previous_ndc.x * 0.5 + 0.5, 0.5 - previous_ndc.y * 0.5);
  return uv - previous_uv;
}
```

| 点 | 説明 |
| --- | --- |
| **`inverse_view_projection`** | **今フレームの逆行列**。**深度 → ワールド位置** |
| **`previous_view_projection`** | **前フレームのカメラ**。**ワールド位置 → 前の画面位置** |
| **`uv − previous_uv`** | **今 − 前**（<strong>[Velocity Buffer](velocity-buffer.md)と同じ定義</strong>） |
| **ジッター** | **両方の行列から、ジッターを除く** |

## 特徴と注意

| 項目 | 内容 |
| --- | --- |
| **安い** | **フルスクリーンで深度を 1 回読み、行列を 2 回掛けるだけ**。**物体の速度書き込み不要** |
| **動く物体は不正確** | **物体はカメラ以外にも自分で動く**。**物体の速度で上書き** |
| **遠景** | **深度が最奥（スカイ）は、回転の影響だけ**になる（**並進は無視**） |
| **カメラが速く回る** | **ブラーが強くなりすぎる**ので、**最大長で制限** |
| **ジャンプ・カット** | **カメラが瞬間移動したフレームは、前フレームの行列を今に置き換え、速度 0** |

## 速度の合成

**最終的な速度**は、**動く物体は速度バッファ、それ以外はカメラ速度**を**使います**。

```hlsl
float2 FinalVelocity(float2 uv, float depth) {
  float2 object_velocity = velocity_buffer.SampleLevel(point_clamp, uv, 0).xy;
  bool has_object_velocity = any(object_velocity != 0.0) || stencil_flag;
  return has_object_velocity ? object_velocity : CameraVelocity(uv, depth);
}
```

**ステンシル・専用ビットで、「速度を書いた画素」を区別**する**と**、<strong>「速度ぴったり 0 の動く物体」と「書かれていない画素」を、取り違えません</strong>。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **カメラ ブラーだけをまず実装** | **安く、効果が大きい** |
| **速度の最大長を制限** | **急回転でも画面が崩れない**（**画面高さの 3〜5 %**） |
| **カットで即リセット** | **前フレームの行列を今に** |
| **プレイヤーの武器・手を除外** | **カメラに固定された物は、カメラ ブラーを掛けない**（**ステンシル／マスク**） |
| **遠景は強さを弱める** | **空の流れが強すぎるのを防ぐ** |
| **シャッター角で強さを調整** | [Strength and TAA](strength-taa.md) |

## よくあるミス

??? failure "カメラに固定された武器まで、ブラーがかかる"
    **ビューモデルは、カメラと同じ動きなので、速度 0**。**マスクして除外**。

??? failure "カメラが瞬間移動したフレームで、画面全体が大きくぶれる"
    **カットや瞬間移動では、前フレームの行列を今の行列にして、速度を 0**。

??? failure "ブラーが強すぎて、酔う"
    **最大長・強さを抑える**。**オプションで切れる**ようにする。

??? failure "静止した物の速度が、ジッターでふるえる"
    **行列からジッターを除いて**速度を計算。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カメラ ブラー ＝ <strong>カメラの動きによる、静止物の見かけの動き</strong>を<strong>ぼかす</strong>
    - [x] <strong>深度 ＋ 前フレームのカメラ行列</strong>で<strong>速度を再構成</strong>
    - [x] <strong>回転は一様、並進は近い物ほど速い</strong>
    - [x] <strong>動く物体は、物体の速度で上書き</strong>
    - [x] <strong>カットで速度 0</strong>、<strong>最大長で制限</strong>

## 参考

- Rosado, "Motion Blur as a Post-Processing Effect"（GPU Gems 3）
- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）

## 関連ページ

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Object Motion Blur](object-blur.md)
- [Blur Pass Implementation](blur-pass.md)

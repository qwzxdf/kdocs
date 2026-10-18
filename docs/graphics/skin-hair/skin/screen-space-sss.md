---
title: Separable SSS
tags:
  - 描画
---

# Separable SSS

<strong>画面空間の SSS</strong>は、ライティングが終わった画像を、肌の画素だけ<strong>ぼかして</strong>、SSS を表現する方法です。UV 空間を使わず、画面に映っている画素だけを処理するので、軽く、実装も単純です。Jimenez らの "Separable Subsurface Scattering"（2015）は、ぼかしを縦横の 2 回の 1 次元処理に分け、実用的なコストで高品質な SSS を実現しました。現代のゲームの標準的な方法です。このページでは、考え方、カーネルの作り方、実装の注意点を説明します。

!!! tip "ポイント"
    - 拡散反射の画像を、肌の画素だけ、深度を考慮してぼかす。
    - ぼかしを<strong>横 → 縦の 2 パス</strong>に分ける（分離可能）。サンプルは 11〜25 個。
    - カーネルは、拡散プロファイルを、1 次元に積分した形。RGB ごとに別の重み。
    - ぼかしの幅は、画面上の距離でなく、実際の長さ。深度で補正する。
    - 鏡面反射はぼかさない。アルベドは、ぼかしの前に外す。

## 考え方

拡散近似の下では、肌の表面のある点の SSS の光は、周りの点のライティング結果に、距離に応じた重み R(r) を掛けて足したもの、つまり<strong>ぼかし</strong>でした。これを画面の画像に対して行います。

手順は、次のとおりです。

1. 通常どおり、シーンのライティングを行います。肌の画素に対しては、拡散反射と鏡面反射を、別々の画像に（またはアルファチャンネルに）書き出します。
2. 拡散反射の画像に、横方向のぼかしを、続いて縦方向のぼかしを掛けます。ぼかしを掛けるのは、ステンシルで印を付けた肌の画素だけです。
3. ぼかした拡散反射に、鏡面反射を足して、最終的な色にします。

分離可能であることは、この方法の鍵です。拡散プロファイルは、本来は 2 次元の円対称な関数なので、厳密には縦横に分解できません。しかし、Jimenez らは、<strong>プロファイルを 1 次元のカーネルに近似して、縦と横に 2 回掛ける</strong>ことで、見た目がほぼ変わらないことを示しました。サンプル数が N×N から 2N に減り、1080p でも 0.5〜1 ms ほどで収まります。

<!-- fig:sss-blur:begin -->

<svg class="fig illust motion" data-fig="sss-blur" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sss-blur" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">スクリーン スペース SSS: 赤だけ広く、青は狭くぼかすと、肌の「にじむ光」になる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素の肌に、細い白い光の線が当たる。色ごとに、ぼかす広さ(ガウス)を変える</text>
<text x="60.0" y="98" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">入力: 光の当たり方(細い線)</text>
<rect x="60.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="77.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="94.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="111.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="128.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="145.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="162.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="179.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="196.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="213.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="230.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="247.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="264.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="281.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="298.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="315.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="332.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="349.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="366.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="383.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="400.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="417.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="434.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="468.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="485.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="502.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="519.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="536.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="553.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="570.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="587.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="604.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="621.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="638.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="655.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="672.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="689.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="706.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="723.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="740.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="757.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="774.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="791.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="808.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="825.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="842.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="859.0" y="104.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#252525"/></rect>
<rect x="60.0" y="104" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="30" y="160" width="900" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">① 色ごとのぼかし(縦 = 明るさ)</text>
<path d="M68.5,295.16 L85.5,295.16 L102.5,295.16 L119.5,295.16 L136.5,295.16 L153.5,295.16 L170.5,295.16 L187.5,295.16 L204.5,295.16 L221.5,295.16 L238.5,295.03 L255.5,294.77 L272.5,294.39 L289.5,293.73 L306.5,292.67 L323.5,291.08 L340.5,288.88 L357.5,286.08 L374.5,282.81 L391.5,279.36 L408.5,276.16 L425.5,273.67 L442.5,272.31 L459.5,272.31 L476.5,273.67 L493.5,276.16 L510.5,279.36 L527.5,282.81 L544.5,286.08 L561.5,288.88 L578.5,291.08 L595.5,292.67 L612.5,293.73 L629.5,294.39 L646.5,294.77 L663.5,295.03 L680.5,295.16 L697.5,295.16 L714.5,295.16 L731.5,295.16 L748.5,295.16 L765.5,295.16 L782.5,295.16 L799.5,295.16 L816.5,295.16 L833.5,295.16 L850.5,295.16 L867.5,295.16" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="0;0;1;1"/></path>
<text x="860" y="196" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">R: ぼかす広さ σ = 4.0 画素<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="0;0;1;1"/></text>
<path d="M68.5,295.16 L85.5,295.16 L102.5,295.16 L119.5,295.16 L136.5,295.16 L153.5,295.16 L170.5,295.16 L187.5,295.16 L204.5,295.16 L221.5,295.16 L238.5,295.16 L255.5,295.16 L272.5,295.16 L289.5,295.16 L306.5,295.16 L323.5,295.16 L340.5,295.06 L357.5,294.52 L374.5,292.44 L391.5,286.56 L408.5,274.85 L425.5,259.2 L442.5,247.34 L459.5,247.34 L476.5,259.2 L493.5,274.85 L510.5,286.56 L527.5,292.44 L544.5,294.52 L561.5,295.06 L578.5,295.16 L595.5,295.16 L612.5,295.16 L629.5,295.16 L646.5,295.16 L663.5,295.16 L680.5,295.16 L697.5,295.16 L714.5,295.16 L731.5,295.16 L748.5,295.16 L765.5,295.16 L782.5,295.16 L799.5,295.16 L816.5,295.16 L833.5,295.16 L850.5,295.16 L867.5,295.16" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1844;0.1846;1.0000" values="0;0;1;1"/></path>
<text x="860" y="214" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">G: ぼかす広さ σ = 1.8 画素<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1844;0.1846;1.0000" values="0;0;1;1"/></text>
<path d="M68.5,295.16 L85.5,295.16 L102.5,295.16 L119.5,295.16 L136.5,295.16 L153.5,295.16 L170.5,295.16 L187.5,295.16 L204.5,295.16 L221.5,295.16 L238.5,295.16 L255.5,295.16 L272.5,295.16 L289.5,295.16 L306.5,295.16 L323.5,295.16 L340.5,295.16 L357.5,295.16 L374.5,295.16 L391.5,294.96 L408.5,290.6 L425.5,263.03 L442.5,215.89 L459.5,215.89 L476.5,263.03 L493.5,290.6 L510.5,294.96 L527.5,295.16 L544.5,295.16 L561.5,295.16 L578.5,295.16 L595.5,295.16 L612.5,295.16 L629.5,295.16 L646.5,295.16 L663.5,295.16 L680.5,295.16 L697.5,295.16 L714.5,295.16 L731.5,295.16 L748.5,295.16 L765.5,295.16 L782.5,295.16 L799.5,295.16 L816.5,295.16 L833.5,295.16 L850.5,295.16 L867.5,295.16" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3177;0.3179;1.0000" values="0;0;1;1"/></path>
<text x="860" y="232" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb" opacity="0">B: ぼかす広さ σ = 0.9 画素<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3177;0.3179;1.0000" values="0;0;1;1"/></text>
<text x="60.0" y="332" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">② 3 色を重ねた、肌の色</text>
<rect x="60.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4821" values="#e5e7eb;#36251f"/></rect>
<rect x="77.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#36251f"/></rect>
<rect x="94.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4851" values="#e5e7eb;#36251f"/></rect>
<rect x="111.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4867" values="#e5e7eb;#36251f"/></rect>
<rect x="128.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4882" values="#e5e7eb;#36251f"/></rect>
<rect x="145.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4897" values="#e5e7eb;#36251f"/></rect>
<rect x="162.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4913" values="#e5e7eb;#36251f"/></rect>
<rect x="179.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4928" values="#e5e7eb;#36251f"/></rect>
<rect x="196.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4944" values="#e5e7eb;#36251f"/></rect>
<rect x="213.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4959" values="#e5e7eb;#36251f"/></rect>
<rect x="230.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4974" values="#e5e7eb;#36251f"/></rect>
<rect x="247.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4990" values="#e5e7eb;#37251f"/></rect>
<rect x="264.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5005" values="#e5e7eb;#38251f"/></rect>
<rect x="281.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5021" values="#e5e7eb;#39251f"/></rect>
<rect x="298.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5036" values="#e5e7eb;#3c251f"/></rect>
<rect x="315.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5051" values="#e5e7eb;#40251f"/></rect>
<rect x="332.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5067" values="#e5e7eb;#46251f"/></rect>
<rect x="349.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5082" values="#e5e7eb;#4d261f"/></rect>
<rect x="366.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5097" values="#e5e7eb;#552a1f"/></rect>
<rect x="383.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5113" values="#e5e7eb;#5e341f"/></rect>
<rect x="400.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128" values="#e5e7eb;#664926"/></rect>
<rect x="417.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5144" values="#e5e7eb;#6d644f"/></rect>
<rect x="434.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5159" values="#e5e7eb;#707994"/></rect>
<rect x="451.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5174" values="#e5e7eb;#707994"/></rect>
<rect x="468.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5190" values="#e5e7eb;#6d644f"/></rect>
<rect x="485.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5205" values="#e5e7eb;#664926"/></rect>
<rect x="502.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5221" values="#e5e7eb;#5e341f"/></rect>
<rect x="519.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5236" values="#e5e7eb;#552a1f"/></rect>
<rect x="536.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5251" values="#e5e7eb;#4d261f"/></rect>
<rect x="553.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5267" values="#e5e7eb;#46251f"/></rect>
<rect x="570.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5282" values="#e5e7eb;#40251f"/></rect>
<rect x="587.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5297" values="#e5e7eb;#3c251f"/></rect>
<rect x="604.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5313" values="#e5e7eb;#39251f"/></rect>
<rect x="621.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5328" values="#e5e7eb;#38251f"/></rect>
<rect x="638.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5344" values="#e5e7eb;#37251f"/></rect>
<rect x="655.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5359" values="#e5e7eb;#36251f"/></rect>
<rect x="672.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5374" values="#e5e7eb;#36251f"/></rect>
<rect x="689.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5390" values="#e5e7eb;#36251f"/></rect>
<rect x="706.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5405" values="#e5e7eb;#36251f"/></rect>
<rect x="723.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5421" values="#e5e7eb;#36251f"/></rect>
<rect x="740.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5436" values="#e5e7eb;#36251f"/></rect>
<rect x="757.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5451" values="#e5e7eb;#36251f"/></rect>
<rect x="774.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5467" values="#e5e7eb;#36251f"/></rect>
<rect x="791.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5482" values="#e5e7eb;#36251f"/></rect>
<rect x="808.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5497" values="#e5e7eb;#36251f"/></rect>
<rect x="825.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5513" values="#e5e7eb;#36251f"/></rect>
<rect x="842.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5528" values="#e5e7eb;#36251f"/></rect>
<rect x="859.0" y="340.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5544" values="#e5e7eb;#36251f"/></rect>
<rect x="60.0" y="340" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4821" values="#e5e7eb;#2f201b"/></rect>
<rect x="77.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#2f201b"/></rect>
<rect x="94.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4851" values="#e5e7eb;#2f201b"/></rect>
<rect x="111.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4867" values="#e5e7eb;#2f201b"/></rect>
<rect x="128.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4882" values="#e5e7eb;#2f201b"/></rect>
<rect x="145.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4897" values="#e5e7eb;#2f201b"/></rect>
<rect x="162.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4913" values="#e5e7eb;#2f201b"/></rect>
<rect x="179.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4928" values="#e5e7eb;#2f201b"/></rect>
<rect x="196.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4944" values="#e5e7eb;#2f201b"/></rect>
<rect x="213.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4959" values="#e5e7eb;#2f201b"/></rect>
<rect x="230.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4974" values="#e5e7eb;#2f201b"/></rect>
<rect x="247.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4990" values="#e5e7eb;#2f201b"/></rect>
<rect x="264.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5005" values="#e5e7eb;#2f201b"/></rect>
<rect x="281.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5021" values="#e5e7eb;#2f201b"/></rect>
<rect x="298.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5036" values="#e5e7eb;#2f201b"/></rect>
<rect x="315.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5051" values="#e5e7eb;#2f201b"/></rect>
<rect x="332.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5067" values="#e5e7eb;#2f201b"/></rect>
<rect x="349.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5082" values="#e5e7eb;#2f201b"/></rect>
<rect x="366.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5097" values="#e5e7eb;#2f201b"/></rect>
<rect x="383.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5113" values="#e5e7eb;#2f201b"/></rect>
<rect x="400.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128" values="#e5e7eb;#2f201b"/></rect>
<rect x="417.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5144" values="#e5e7eb;#2f201b"/></rect>
<rect x="434.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5159" values="#e5e7eb;#b57d68"/></rect>
<rect x="451.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5174" values="#e5e7eb;#b57d68"/></rect>
<rect x="468.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5190" values="#e5e7eb;#2f201b"/></rect>
<rect x="485.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5205" values="#e5e7eb;#2f201b"/></rect>
<rect x="502.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5221" values="#e5e7eb;#2f201b"/></rect>
<rect x="519.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5236" values="#e5e7eb;#2f201b"/></rect>
<rect x="536.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5251" values="#e5e7eb;#2f201b"/></rect>
<rect x="553.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5267" values="#e5e7eb;#2f201b"/></rect>
<rect x="570.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5282" values="#e5e7eb;#2f201b"/></rect>
<rect x="587.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5297" values="#e5e7eb;#2f201b"/></rect>
<rect x="604.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5313" values="#e5e7eb;#2f201b"/></rect>
<rect x="621.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5328" values="#e5e7eb;#2f201b"/></rect>
<rect x="638.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5344" values="#e5e7eb;#2f201b"/></rect>
<rect x="655.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5359" values="#e5e7eb;#2f201b"/></rect>
<rect x="672.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5374" values="#e5e7eb;#2f201b"/></rect>
<rect x="689.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5390" values="#e5e7eb;#2f201b"/></rect>
<rect x="706.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5405" values="#e5e7eb;#2f201b"/></rect>
<rect x="723.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5421" values="#e5e7eb;#2f201b"/></rect>
<rect x="740.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5436" values="#e5e7eb;#2f201b"/></rect>
<rect x="757.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5451" values="#e5e7eb;#2f201b"/></rect>
<rect x="774.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5467" values="#e5e7eb;#2f201b"/></rect>
<rect x="791.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5482" values="#e5e7eb;#2f201b"/></rect>
<rect x="808.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5497" values="#e5e7eb;#2f201b"/></rect>
<rect x="825.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5513" values="#e5e7eb;#2f201b"/></rect>
<rect x="842.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5528" values="#e5e7eb;#2f201b"/></rect>
<rect x="859.0" y="366.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5544" values="#e5e7eb;#2f201b"/></rect>
<rect x="60.0" y="366" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="884.0" y="358" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">ぼかした</text>
<text x="884.0" y="384" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ぼかさない</text>
<rect x="30" y="412" width="900" height="98" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="402" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">③ 画面全体(1920×1080)でぼかすのに必要な読み込み(R の広さ σ=4.0、半径 12)</text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5967;0.5969;1.0000" values="0;0;1;1"/><text x="50" y="452" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">縦横 2 回に分ける(分離)</text>
<text x="50" y="476" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">1 画素あたり 50 回 → 画面全体で 103,680,000 回</text>
<text x="490" y="452" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">2 次元でそのまま</text>
<text x="490" y="476" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">1 画素あたり 625 回 → 画面全体で 1,296,000,000 回</text>
<text x="900" y="500" text-anchor="end" style="font-size:16px;font-weight:700;fill:#7c3aed">約 12 倍の差</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光は、肌の中で散らばって、少し離れた所から出てくる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">赤は広く、緑は中くらい、青は狭く、ぼかす<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;0.4818;0.4821;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">重ねると、光の線のまわりに、赤い にじみが残る<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4818;0.4821;0.5967;0.5969;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縦横に分けると、読み込みが桁違いに少なくなる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5967;0.5969;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sss-blur:end -->

## カーネルの作り方

1 次元のカーネルは、次のように作ります。まず、拡散プロファイル R(r)（2 次元の円対称）を、ある方向の 1 次元の断面へ<strong>積分</strong>して、1 次元の関数にします。プロファイルは RGB で別々なので、カーネルも RGB ごとに別の重みを持ちます。次に、カーネルを離散化します。中心を含めて N 個のサンプル（典型的には 11 個から 25 個）を、中心から外へ向かって、<strong>間隔を不均一に</strong>取ります。中心付近は細かく、外側は粗くします。プロファイルは中心が尖っているので、そこを細かく取るためです。各サンプルに、オフセット（中心からの距離）と、RGB の重みを割り当てます。最後に、重みの合計が、RGB ごとに 1 になるよう正規化します。

このカーネルは、あらかじめ（起動時に）計算しておき、定数バッファに入れて、シェーダーから使います。

```hlsl
struct KernelSample {
  float3 weight;
  float offset;
};
StructuredBuffer<KernelSample> kernel;

float4 SssBlur(float2 uv, float2 direction, float sss_width) {
  float4 center = diffuse_tex.SampleLevel(point_clamp, uv, 0);
  float depth = linear_depth_tex.SampleLevel(point_clamp, uv, 0);

  float2 step = direction * sss_width / depth;
  float3 sum = center.rgb * kernel[0].weight;
  for (int i = 1; i < kSampleCount; ++i) {
    float2 sample_uv = uv + kernel[i].offset * step;
    float3 color = diffuse_tex.SampleLevel(linear_clamp, sample_uv, 0).rgb;
    float sample_depth = linear_depth_tex.SampleLevel(point_clamp, sample_uv, 0);

    float s = saturate(300.0 * sss_width * abs(depth - sample_depth) / depth);
    color = lerp(color, center.rgb, s);
    sum += kernel[i].weight * color;
  }
  return float4(sum, center.a);
}
```

## 画面上の幅を、実際の長さに合わせる

SSS のぼけ幅は、<strong>物体の表面上の実際の長さ</strong>（mm）で決まります。画面上では、カメラから遠いほど、同じ長さが小さく映ります。そこで、ぼかしの画面上の幅を、<strong>深度で割って</strong>調整します。コードの `step = direction * sss_width / depth` がそれです。`sss_width` は、世界での広がり（人間の肌なら 1 cm 以下）を、射影の係数を含めて画面上の長さに変換した値で、近くの顔は大きく、遠くの顔は小さくなります。この補正を忘れると、カメラが引いたときに顔のぼけが大きくなりすぎます。

## 輪郭をまたがないための工夫

ぼかしは、<strong>別の面の画素まで混ぜてしまう</strong>と、不自然になります。たとえば、顔の輪郭の外側の背景や、髪、服の色が、肌に混ざってしまいます。コードの `s` の項は、中心の画素とサンプル点の<strong>深度の差が大きいとき、サンプルの色を中心の色に置き換える</strong>工夫です。深度が離れた（別の面の）サンプルは、使われなくなるので、輪郭をまたいだにじみが防げます。

さらに、ステンシルで肌の画素だけに印を付けておくと、肌以外の画素に対して、ぼかしのシェーダーが走りません。画面の大半が肌でないシーンでは、大きく節約できます。

## アルベドの扱い

もう 1 つの重要な注意が、<strong>アルベド（テクスチャの色）</strong>です。ライティングの結果にアルベドを掛けてからぼかすと、<strong>毛穴・そばかす・ほくろなどのテクスチャの細かい模様まで、ぼけてしまいます</strong>。実際の肌では、模様は、肌の表面にある（表皮の色素）ので、内部で散乱する光でぼけません。

そのため、アルベドは、ぼかしの<strong>前に外し</strong>（ライティングの結果をアルベドで割るか、そもそも掛けずに放射照度を保存する）、ぼかしの<strong>後に掛け直す</strong>のが正しい方法です。ただし、アルベドを完全に後だけで掛けると、肌の色が、散乱によって「色を変えながら」広がる効果（赤が広がる）を表せません。そこで、Jimenez らは、アルベドの平方根を、ぼかしの前後に半分ずつ掛ける折衷案を示しています。この方法は、毛穴などの詳細を残しながら、色の広がりも出せます。

## 品質の調整

いくつかのパラメータで、見た目を調整できます。

`sss_width` は、ぼかしの全体の広がりで、肌の SSS の強さを決めます。大きいほど、肌が柔らかく見えますが、大きすぎると顔がのっぺりします。`sss_strength` は、ぼかした結果と元の画像を混ぜる割合で、0 なら SSS なし、1 なら完全にぼかします。顔の部位ごとに強さを変えたいとき（頬は強く、鼻の頭は弱くなど）は、<strong>SSS の強度マスク</strong>のテクスチャを使います。耳や鼻、唇は強め、額や頬骨は弱めにすると、現実に近くなります。

## 軽量化

品質を保ちながらコストを減らす方法があります。サンプル数を減らす（25 個を 11 個や 7 個に）。ぼかしを半解像度で行う（顔が小さいキャラクターなど）。画面上で小さいキャラクターは、SSS を省略するか、サンプル数を減らす（LOD）。これらを使い分けると、1080p で 0.5 ms 程度に収まります。

## よくあるミス

??? failure "鏡面反射まで、一緒にぼけて、つやが消える"
    <strong>拡散反射と鏡面反射を、別の画像に書く</strong>。ぼかすのは拡散だけで、<strong>鏡面は後で足す</strong>。

??? failure "顔の輪郭で、背景の色が肌ににじむ"
    <strong>深度の差が大きいサンプルを、中心の色に置き換える</strong>（深度を考慮したぼかし）。

??? failure "カメラが引くと、顔のぼけが大きくなる"
    ぼかしの画面上の幅を<strong>深度で割って</strong>、実際の長さを一定にする。

??? failure "毛穴やそばかすまで、ぼけてしまう"
    <strong>アルベドを、ぼかしの前に外す</strong>（または、√アルベドを前後に掛ける）。

??? failure "横方向と縦方向で、ぼけ方が違って見える"
    <strong>画面のアスペクト比を考慮して</strong>、横と縦のステップ幅を揃える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 拡散反射を<strong>肌の画素だけ、深度を考慮して、横 → 縦にぼかす</strong>
    - [x] カーネルは<strong>プロファイルを 1 次元に積分</strong>。RGB ごとに別の重み
    - [x] ぼかしの幅は、深度で補正して、実際の長さに合わせる
    - [x] 鏡面はぼかさない。アルベドは前に外し、後に掛ける

## 参考

- Jimenez, Zsolnai, Jarabo, Freude, Auzinger, Wu, von der Pahlen, Wimmer, Gutierrez, "Separable Subsurface Scattering"（Computer Graphics Forum, 2015）
- Jimenez, Sundstedt, Gutierrez, "Screen-Space Perceptual Rendering of Human Skin"（ACM Transactions on Applied Perception, 2009）
- Golubev, "Efficient Screen-Space Subsurface Scattering Using Burley's Normalized Diffusion"（SIGGRAPH 2018 Advances in Real-Time Rendering）

## 関連ページ

- [Skin Overview](index.md)
- [Diffusion Profiles](diffusion-profile.md)
- [Pre-Integrated Skin Shading](pre-integrated.md)
- [Bilateral Blur](../../ao/filtering/bilateral-blur.md)

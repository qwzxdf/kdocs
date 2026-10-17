---
title: モーション ブラー
tags:
  - 描画
---

# モーション ブラー

**モーション ブラー**は、<strong>動いている物（またはカメラ）が、動いた方向に「にじむ・流れる」</strong>効果です。**実際のカメラは、シャッターが開いている間に物が動くので、その軌跡がぶれて写ります**。**ゲームの 1 フレームは「一瞬」を切り取った絵**なので**動きがカクカクに見えがち**ですが、**ブラーを足すと滑らかでスピード感のある動き**になります。このセクションでは、**速度バッファ・カメラのブラー・オブジェクトのブラー・ぼかしの実装・タイル最大速度・強さと TAA** を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - モーション ブラー ＝ <strong>各画素の動き（速度）に沿って、画像をぼかす</strong>。
    - <strong>速度バッファ</strong>が<strong>主役</strong>。<strong>画素ごとに前フレームから今フレームへの移動量を持つ</strong>。
    - <strong>カメラ ブラー</strong>（<strong>カメラの動きで背景全体が流れる</strong>）と<strong>オブジェクト ブラー</strong>（<strong>動く物体</strong>）に分けて考える。
    - <strong>ぼかしの強さ ＝ シャッター角</strong>（<strong>180° が標準</strong>）。
    - <strong>前景・背景の重み付け</strong>で<strong>速い物の輪郭が自然</strong>になる。
    - <strong>タイル最大速度</strong>で<strong>高速化</strong>。<strong>TAA と速度バッファを共有</strong>。

## 動きで見る

<!-- fig:motion-blur-shutter:begin -->

<svg class="fig illust motion" data-fig="motion-blur-shutter" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-motion-blur-shutter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">シャッター角:露光の間に動いた分だけが、ブレになる</text>
<rect x="60" y="90" width="640" height="24" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="80" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 フレームの時間（左 = 始め、右 = 終わり）</text>
<rect x="60" y="90" width="0.0001" height="24" fill="#e5aa28"><animate attributeName="width" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.1481;0.3333;0.4444;0.6296;0.7037;0.8519;1.0000" values="0;0;0;320;320;640;640;320;320"/></rect>
<line x1="60" y1="260" x2="700" y2="260" stroke="#cbd5e1" stroke-width="2"/>
<circle cx="100.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;0.3;0.3"/></circle>
<circle cx="140.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1787;0.1790;1.0000" values="0;0;0.3;0.3"/></circle>
<circle cx="180.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2096;0.2099;1.0000" values="0;0;0.3;0.3"/></circle>
<circle cx="220.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2404;0.2407;1.0000" values="0;0;0.3;0.3"/></circle>
<circle cx="260.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2713;0.2716;1.0000" values="0;0;0.3;0.3"/></circle>
<circle cx="300.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3022;0.3025;1.0000" values="0;0;0.3;0.3"/></circle>
<circle cx="340.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="0;0;0.3;0.3"/></circle>
<circle cx="380.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4750;0.4753;0.8269;0.8272;1.0000" values="0;0;0.3;0.3;0;0"/></circle>
<circle cx="420.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5059;0.5062;0.8022;0.8025;1.0000" values="0;0;0.3;0.3;0;0"/></circle>
<circle cx="460.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5367;0.5370;0.7775;0.7778;1.0000" values="0;0;0.3;0.3;0;0"/></circle>
<circle cx="500.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5676;0.5679;0.7528;0.7531;1.0000" values="0;0;0.3;0.3;0;0"/></circle>
<circle cx="540.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5985;0.5988;0.7281;0.7284;1.0000" values="0;0;0.3;0.3;0;0"/></circle>
<circle cx="580.0" cy="230" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;0.7034;0.7037;1.0000" values="0;0;0.3;0.3;0;0"/></circle>
<circle cx="100" cy="230" r="22" fill="#1f2937" stroke="#ffffff" stroke-width="2"/>
<rect x="100" y="208" width="0.0001" height="44" fill="#2563eb" fill-opacity="0.28"><animate attributeName="width" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.1481;0.3333;0.4444;0.6296;0.7037;0.8519;1.0000" values="0;0;0;240;240;480;480;240;240"/></rect>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">シャッター角 0°:ブレなし（球は 1 点）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;1.0000" values="1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">ブレが伸びていく… シャッター角 180°（標準）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;0.3849;0.3852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">180°:露光 = フレームの半分。映画の標準<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3849;0.3852;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">シャッター角 360°:最大。流れる長いブレ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;0.7034;0.7037;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">180° に戻す<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7034;0.7037;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="368" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ブレの長さ ＝ 速さ × 露光の長さ（シャッターが開いている間に動いた距離）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:motion-blur-shutter:end -->

## 全体の流れ

| 手順 | 内容 | ページ |
| --- | --- | --- |
| **① 速度を作る** | **画素ごとの移動ベクトル** | [速度バッファ](velocity-buffer.md) |
| **②a カメラの動き** | **深度と行列から、背景の速度** | [カメラのブラー](camera-blur.md) |
| **②b 物体の動き** | **動く物体・スキニングの速度** | [オブジェクトのブラー](object-blur.md) |
| **③ ぼかす** | **速度に沿って、サンプルを集める** | [ぼかしの実装](blur-pass.md) |
| **④ 高速化** | **タイルの最大速度で無駄を省く** | [タイル最大速度](tile-max.md) |
| **⑤ 設計** | **シャッター角・最大長・TAA との関係** | [強さと TAA](strength-taa.md) |

## 関連ページ

- [ポストプロセス](../index.md)
- [被写界深度](../dof/index.md)
- [アンチエイリアシング（TAA）](../antialiasing/taa.md)
- [露出](../tonemapping/exposure.md)

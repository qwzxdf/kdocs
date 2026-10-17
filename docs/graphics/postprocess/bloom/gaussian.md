---
title: Gaussian Blur
tags:
  - 描画
---

# Gaussian Blur

**ガウスぼかし**は、**画像処理でもっとも基本的なぼかし**で、**ブルームをはじめ、DOF・SSAO のぼかしなど**、**あらゆる所**で**使われます**。**中心が重く、離れるほど滑らかに軽くなる重み**で**周りを平均**するので、**自然でムラのないぼかし**になります。このページでは、**ガウス関数・分離可能性（横 → 縦の 2 パス）・バイリニアを使ったタップ数の半減・重みの作り方・カーネル サイズの決め方**を説明します。

!!! tip "ポイント"
    - ガウスぼかし ＝ <strong>ガウス関数（釣り鐘）の重みで周りの画素を平均する</strong>。
    - <strong>分離可能</strong>：<strong>2D の (2R+1)² タップを横 1D → 縦 1D の 2 パス（2×(2R+1) タップ）</strong>にできる。
    - <strong>バイリニア補間を利用</strong>すると、<strong>2 タップを 1 回の読み込みにまとめられ、タップ数が約半分</strong>になる。
    - <strong>σ（標準偏差）</strong>が<strong>ぼかしの強さ</strong>。<strong>カーネルの半径は 3σ 程度</strong>で十分。
    - <strong>重みは合計 1 に正規化</strong>（<strong>明るさを保つ</strong>）。
    - <strong>ブルームでは、縮小した画像にかける</strong>ので、<strong>小さなカーネル（5〜9 タップ）で済む</strong>。

## ガウス関数

<div class="formula">G(x) = (1 / (σ√(2π))) · exp( −x² / (2σ²) )</div>

**中心が最大で離れるほど急速に小さくなる**釣り鐘形です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="ガウス関数">
<text x="20" y="26" class="fig-title">ガウスの重み：σ が大きいほど、広く平らになる</text>
<line x1="80" y1="200" x2="700" y2="200" stroke="currentColor" stroke-opacity="0.5"/><line x1="390" y1="50" x2="390" y2="200" stroke="currentColor" stroke-opacity="0.3" stroke-dasharray="4 4"/>
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="80,198 150,196 220,185 280,150 330,100 370,66 390,60 410,66 450,100 500,150 560,185 630,196 700,198"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="80,199 150,198 220,196 280,190 330,178 370,168 390,166 410,168 450,178 500,190 560,196 630,198 700,199"/>
<text x="470" y="80" style="font-size:12px;fill:#2563eb">σ 小：中心に集中（弱いぼかし）</text>
<text x="470" y="150" style="font-size:12px;fill:#e5484d">σ 大：広く平ら（強いぼかし）</text>
<text x="390" y="224" text-anchor="middle" style="font-size:12px">中心からの距離 →</text>
</svg>

## 分離可能性

**2D のガウスは、横の 1D ガウス × 縦の 1D ガウス**に**分解できます**。**そこで、「横方向にぼかす」→「縦方向にぼかす」の 2 パス**に**分ける**と、**タップ数が大幅に減ります**。

| 方式 | 1 画素あたりのタップ数（半径 R） |
| --- | --- |
| **2D を直接** | <strong>(2R+1)²</strong>（R=8 で 289） |
| <strong>分離（横 → 縦）</strong> | <strong>2 × (2R+1)</strong>（R=8 で 34） |

<!-- fig:gaussian-separable:begin -->

<svg class="fig illust motion" data-fig="gaussian-separable" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gaussian-separable" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ガウスぼかしは「横 → 縦」に分けると、サンプルが激減する</text>
<text x="40" y="70" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">そのまま 2D</text>
<rect x="40" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="40" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="84" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="106" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="128" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="150" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="172" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="194" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="216" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="62" y="112" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.21;0.21"/></rect>
<rect x="84" y="112" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="106" y="112" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="128" y="112" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="150" y="112" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="172" y="112" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="194" y="112" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.21;0.21"/></rect>
<rect x="62" y="134" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="84" y="134" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.3;0.3"/></rect>
<rect x="106" y="134" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="128" y="134" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="150" y="134" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="172" y="134" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.3;0.3"/></rect>
<rect x="194" y="134" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="62" y="156" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="84" y="156" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="106" y="156" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.68;0.68"/></rect>
<rect x="128" y="156" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="150" y="156" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.68;0.68"/></rect>
<rect x="172" y="156" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="194" y="156" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="62" y="178" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="84" y="178" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="106" y="178" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="128" y="178" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></rect>
<rect x="150" y="178" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="172" y="178" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="194" y="178" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="62" y="200" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="84" y="200" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="106" y="200" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.68;0.68"/></rect>
<rect x="128" y="200" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="150" y="200" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.68;0.68"/></rect>
<rect x="172" y="200" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="194" y="200" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="62" y="222" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="84" y="222" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.3;0.3"/></rect>
<rect x="106" y="222" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="128" y="222" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="150" y="222" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.42;0.42"/></rect>
<rect x="172" y="222" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.3;0.3"/></rect>
<rect x="194" y="222" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="62" y="244" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.21;0.21"/></rect>
<rect x="84" y="244" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="106" y="244" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="128" y="244" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="150" y="244" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.26;0.26"/></rect>
<rect x="172" y="244" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.23;0.23"/></rect>
<rect x="194" y="244" width="21" height="21" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;0.21;0.21"/></rect>
<rect x="127" y="177" width="23" height="23" fill="none" stroke="#e5aa28" stroke-width="3"/>
<text x="40" y="314" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 49 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="290" y="70" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">① 横にぼかす</text>
<rect x="290" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="290" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="334" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="356" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="378" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="400" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="422" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="444" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="466" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="312" y="178" width="21" height="21" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="334" y="178" width="21" height="21" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="356" y="178" width="21" height="21" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="378" y="178" width="21" height="21" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/></rect>
<rect x="400" y="178" width="21" height="21" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="422" y="178" width="21" height="21" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="444" y="178" width="21" height="21" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="377" y="177" width="23" height="23" fill="none" stroke="#e5aa28" stroke-width="3"/>
<text x="290" y="314" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 7 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="540" y="70" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">② 縦にぼかす</text>
<rect x="540" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="90" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="112" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="134" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="156" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="178" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="200" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="222" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="244" width="21" height="21" fill="#f1f5f9"/>
<rect x="540" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="562" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="584" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="606" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="650" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="672" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="694" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="716" y="266" width="21" height="21" fill="#f1f5f9"/>
<rect x="628" y="112" width="21" height="21" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="628" y="134" width="21" height="21" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="628" y="156" width="21" height="21" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="628" y="178" width="21" height="21" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/></rect>
<rect x="628" y="200" width="21" height="21" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;0.82;0.82"/></rect>
<rect x="628" y="222" width="21" height="21" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;0.49;0.49"/></rect>
<rect x="628" y="244" width="21" height="21" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;0.28;0.28"/></rect>
<rect x="627" y="177" width="23" height="23" fill="none" stroke="#e5aa28" stroke-width="3"/>
<text x="540" y="314" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 7 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">R=3 のとき、そのままだと (2R+1)² = 49 回、分けると 2(2R+1) = 14 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6257;0.6261;1.0000" values="1;1;0;0"/></text>
<text x="40" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">R=8 なら 289 回 → 34 回（約 8 分の 1）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6257;0.6261;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gaussian-separable:end -->

## 実装（横方向と縦方向）

```hlsl
Texture2D src : register(t0);
SamplerState linear_clamp : register(s0);

cbuffer BlurConstants : register(b0) {
  float2 direction;
  float2 texel_size;
};

static const int kRadius = 4;
static const float kWeights[kRadius + 1] = { 0.2270270, 0.1945946, 0.1216216, 0.0540541, 0.0162162 };

float4 BlurMain(float4 position : SV_POSITION, float2 uv : TEXCOORD0) : SV_Target {
  float3 sum = src.SampleLevel(linear_clamp, uv, 0).rgb * kWeights[0];
  for (int i = 1; i <= kRadius; ++i) {
    float2 offset = direction * texel_size * i;
    sum += src.SampleLevel(linear_clamp, uv + offset, 0).rgb * kWeights[i];
    sum += src.SampleLevel(linear_clamp, uv - offset, 0).rgb * kWeights[i];
  }
  return float4(sum, 1.0);
}
```

| 点 | 説明 |
| --- | --- |
| **`direction`** | <strong>横なら (1, 0)、縦なら (0, 1)</strong>。**同じシェーダーを 2 回使う** |
| **`kWeights`** | **σ ≒ 2 の 9 タップ**（**中心 + 片側 4**）。**合計 1** |
| **中心だけ 1 回、左右は対称に足す** | **重みが左右対称なので、2 回読んで同じ重み** |

## バイリニアでタップ数を半分に

**隣り合う 2 画素をちょうど良い位置の 1 回のバイリニア読み込みで**まとめられます。**2 画素の重み w1, w2 と、位置 o1, o2 に対して**：

<div class="formula">
新しい重み = w1 + w2<br>
新しい位置 = (o1·w1 + o2·w2) / (w1 + w2)
</div>

| 元（9 タップ） | バイリニア利用（5 タップ） |
| --- | --- |
| **位置 0, ±1, ±2, ±3, ±4** | **位置 0, ±1.385, ±3.231** |
| **重み 0.227, 0.195, 0.122, 0.054, 0.016** | **重み 0.227, 0.316, 0.070** |

```hlsl
static const float kOffsets[3] = { 0.0, 1.3846153846, 3.2307692308 };
static const float kLinearWeights[3] = { 0.2270270270, 0.3162162162, 0.0702702703 };

float4 BlurLinear(float4 position : SV_POSITION, float2 uv : TEXCOORD0) : SV_Target {
  float3 sum = src.SampleLevel(linear_clamp, uv, 0).rgb * kLinearWeights[0];
  for (int i = 1; i < 3; ++i) {
    float2 offset = direction * texel_size * kOffsets[i];
    sum += src.SampleLevel(linear_clamp, uv + offset, 0).rgb * kLinearWeights[i];
    sum += src.SampleLevel(linear_clamp, uv - offset, 0).rgb * kLinearWeights[i];
  }
  return float4(sum, 1.0);
}
```

**9 タップが 5 回の読み込み**で**済みます**（**約 55 %**）。**ただし、精度（FP16 のフォーマット）やフィルタ可能なフォーマットが条件**です。

## σ とカーネル サイズ

| 項目 | 目安 |
| --- | --- |
| **半径 R** | **約 3σ**（**これ以降はほぼ 0**） |
| **σ の決め方** | **ぼかしたい広さ（画素）÷ 2〜3** |
| **正規化** | **重みの合計を 1 にする**（**明るさが変わらない**） |

**重みを作る**簡単な方法（C++）：

```cpp
std::vector<float> GaussianWeights(int radius, float sigma) {
  std::vector<float> w(radius + 1);
  float sum = 0.0f;
  for (int i = 0; i <= radius; ++i) {
    w[i] = std::exp(-(i * i) / (2.0f * sigma * sigma));
    sum += (i == 0) ? w[i] : 2.0f * w[i];
  }
  for (float& v : w) v /= sum;
  return w;
}
```

## ブルームでの使い方

<strong>ブルームでは縮小した画像（1/2〜1/64）に、小さなカーネル（5〜9 タップ）</strong>で**ぼかします**。**元の解像度では、広い範囲**になるので**ガウスの半径が小さくても、十分なにじみ**になります。

| 段 | 解像度 | カーネル |
| --- | --- | --- |
| **1/2** | **960×540** | **9 タップ** |
| **1/8** | **240×135** | **5〜9 タップ** |
| **1/32** | **60×34** | **5 タップ** |

**縮小とぼかしを同時に行う方式**が<strong>[Dual Filter](dual-filter.md)</strong> です。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **分離 ＋ バイリニアで読み込み** | **タップ数を最小に** |
| **共有メモリで読み込みを再利用**（コンピュート） | **隣接スレッドが同じ画素を何度も読むのを避ける** |
| **縮小した画像にかける** | **カーネルを小さくできる**（[ダウンサンプル](downsample.md)） |
| **ガンマ・HDR に注意** | **リニアな HDR 値でぼかす**（ガンマ空間でぼかすと暗くなる） |
| **端の処理** | **`clamp` で端を延ばす**（**黒が混ざらないように**） |

## よくあるミス

??? failure "ぼかしたら、画面全体が暗く（明るく）なった"
    **重みの合計が 1 でない**。**正規化**する。

??? failure "横と縦で、ぼかし具合が違う"
    **横・縦の `texel_size` が、幅・高さの逆数になっているか**を確認。**非正方形ピクセル**にも注意。

??? failure "画面の端が黒くにじむ"
    <strong>サンプラーを `clamp`（端を延ばす）</strong>にする。**`border`（黒）は使わない**。

??? failure "ガンマ空間（LDR）でぼかして、暗くなる"
    **リニアでぼかす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ガウス ＝ <strong>釣り鐘の重みで周りを平均</strong>。<strong>σ が強さ、半径は 3σ</strong>
    - [x] <strong>分離</strong>（横 → 縦の 2 パス）で<strong>タップ数が大幅に減る</strong>
    - [x] <strong>バイリニア利用</strong>で<strong>さらに約半分</strong>
    - [x] <strong>重みの合計は 1</strong>。<strong>端は clamp</strong>
    - [x] ブルームでは<strong>縮小した画像に、小さなカーネル</strong>

## 参考

- Rákos, "Efficient Gaussian blur with linear sampling"（2010）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Gonzalez & Woods, "Digital Image Processing"

## 関連ページ

- [Bloom](index.md)
- [Downsampling and the Mip Chain](downsample.md)
- [Dual Filter](dual-filter.md)
- [SSAO のぼかし](../../ao/filtering/index.md)

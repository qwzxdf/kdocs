---
title: Gradient Sky
tags:
  - 描画
---

# Gradient Sky

**空の色を、上と地平線で変えるだけの、最も簡単な方法**です。**軽く、制御しやすい**ので、**スタイライズされた作品や、モバイルで多用されます**。このページでは、**グラデーションの空**を説明します。

!!! tip "ポイント"
    - **天頂の色と、地平線の色を、視線の高さで補間**。
    - **太陽の周りを、明るくする**。
    - **とても軽い**。
    - **物理的には正確でない**。

## グラデーションの空
**もっとも簡単**なのは、**視線の仰角（上下の角度）で、地平線の色と天頂の色を混ぜる**方法です。

```hlsl
float3 GradientSky(float3 view_dir) {
  float elevation = saturate(view_dir.y);
  float t = pow(elevation, 0.5);
  float3 sky = lerp(horizon_color, zenith_color, t);

  float below = saturate(-view_dir.y * 4.0);
  return lerp(sky, ground_color, below);
}
```

| 点 | 説明 |
| --- | --- |
| **`pow(elevation, 0.5)`** | **地平線付近で色が急に変わる**（**天頂は広く青い**）。**空の見た目に近づく** |
| **地面の色** | <strong>地平線より下は、地面（暗い色）</strong>で**塞ぐ**（実際の地面が見えない場合） |
| **太陽の方向で色を寄せる** | **太陽のそばを明るく暖色にする**（下の「太陽」） |
| **時間帯のプリセット** | **朝・昼・夕・夜の色セットを補間** |

**グラデーションは、安く・調整しやすい**ですが**太陽の位置で色が変わる**（夕焼けで太陽の側だけ赤い）**といった表現は、手作業になります**。

<!-- fig:sky-gradient-day:begin -->

<svg class="fig illust motion" data-fig="sky-gradient-day" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sky-gradient-day" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">太陽の高さに合わせて、天頂と地平線の 2 色を入れ替える</text>
<rect x="140" y="70.0" width="500" height="27.0" fill="#2563eb"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#2563eb;#2563eb;#1e3a8a;#1e3a8a;#1e1b4b;#1e1b4b;#020617;#020617"/></rect>
<rect x="140" y="96.0" width="500" height="27.0" fill="#2b67ec"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#2b67ec;#2b67ec;#263d87;#263d87;#231d51;#231d51;#030718;#030718"/></rect>
<rect x="140" y="122.0" width="500" height="27.0" fill="#3570ed"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#3570ed;#3570ed;#354382;#354382;#2c215d;#2c215d;#050a1b;#050a1b"/></rect>
<rect x="140" y="148.0" width="500" height="27.0" fill="#437aef"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#437aef;#437aef;#494b7b;#494b7b;#39266c;#39266c;#070d1e;#070d1e"/></rect>
<rect x="140" y="174.0" width="500" height="27.0" fill="#5387f1"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#5387f1;#5387f1;#5f5473;#5f5473;#472c7e;#472c7e;#0a1022;#0a1022"/></rect>
<rect x="140" y="200.0" width="500" height="27.0" fill="#6595f3"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#6595f3;#6595f3;#7a5e6a;#7a5e6a;#573392;#573392;#0e1426;#0e1426"/></rect>
<rect x="140" y="226.0" width="500" height="27.0" fill="#79a4f5"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#79a4f5;#79a4f5;#966a60;#966a60;#693ba9;#693ba9;#11192b;#11192b"/></rect>
<rect x="140" y="252.0" width="500" height="27.0" fill="#8fb5f8"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#8fb5f8;#8fb5f8;#b67654;#b67654;#7d43c1;#7d43c1;#151e30;#151e30"/></rect>
<rect x="140" y="278.0" width="500" height="27.0" fill="#a6c8fb"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#a6c8fb;#a6c8fb;#d78449;#d78449;#924cdb;#924cdb;#192335;#192335"/></rect>
<rect x="140" y="304.0" width="500" height="27.0" fill="#bfdbfe"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.2897;0.3448;0.5103;0.5655;0.7310;1.0000" values="#bfdbfe;#bfdbfe;#fb923c;#fb923c;#a855f7;#a855f7;#1e293b;#1e293b"/></rect>
<rect x="140" y="70" width="500" height="260" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="652" y="84" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">天頂</text>
<text x="652" y="330" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">地平線</text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">空は、天頂色と地平線色の 2 色を混ぜるだけ<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">昼: 天頂は濃い青、地平線は薄い水色<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.2894;0.2897;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">夕方: 地平線がオレンジに<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2894;0.2897;0.5101;0.5103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">夕暮れ: 紫を経て暗くなる<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5101;0.5103;0.7308;0.7310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="375" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">夜: 天頂も地平線もほぼ黒<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7308;0.7310;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sky-gradient-day:end -->

## よくあるミス

??? failure "地平線に、色の帯（バンディング）が出る"
    **ディザ**を**加える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さで色を補間するだけ**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky Models](index.md)
- [Analytic Sky Models](analytic.md)

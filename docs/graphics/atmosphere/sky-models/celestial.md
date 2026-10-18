---
title: Sun, Moon and Stars
tags:
  - 描画
---

# Sun, Moon and Stars

**空には、太陽・月・星があります**。**太陽はディスク、月はテクスチャ付きの球、星は点の集まりで描きます**。このページでは、**天体の描き方**を説明します。

!!! tip "ポイント"
    - **太陽 ＝ 明るいディスク ＋ 光の拡がり**。
    - **月 ＝ 位相（満ち欠け）を持つ球**。
    - **星 ＝ キューブマップ、または点の集まり**。
    - **昼は、星が見えない（空の明るさに負ける）**。

## Sun, Moon, and Stars {#太陽月星}
**空の主役**は**太陽**です。

### The Sun Disk {#太陽の円盤}

**太陽は視線と太陽の方向の角度が小さい所だけ、非常に明るい円盤**です。**実際の太陽の見た目の大きさは、約 0.53°**（**半径 約 0.265°**）です。

```hlsl
float SunDisk(float3 view_dir, float3 sun_dir) {
  float cos_angle = dot(view_dir, sun_dir);
  float cos_radius = cos(radians(0.265));
  float edge = smoothstep(cos_radius - 0.00002, cos_radius, cos_angle);
  return edge * sun_intensity;
}
```

| 点 | 説明 |
| --- | --- |
| **角度を内積で** | **`acos` を避け、`cos` の値で比べる** |
| **縁を少し滑らかに** | **ジャギーを防ぐ**（**TAA で滑らかになる**） |
| **HDR の強度** | **昼の太陽は空の 1 万倍以上明るい**。**ブルームが光る** |
| <strong>周りのにじみ（コロナ）</strong> | **指数関数的に減る光を足す**：`exp(-angle * k)` |
| **大きすぎる太陽は不自然** | **誇張しすぎない** |

### Sunset Colors {#夕焼けの色}

**太陽が地平線に近づくと、光が大気を長く通る**ので、**青が散り尽くして、赤が残ります**。**太陽の色を高さに応じて変える**だけで、**夕焼けの雰囲気**が**出ます**。

```hlsl
float3 SunColor(float sun_height) {
  float t = saturate(sun_height * 4.0);
  return lerp(float3(1.0, 0.35, 0.1), float3(1.0, 0.95, 0.85), t);
}
```

**正確には大気の透過率（光学的厚さ）から求めます**（[Atmospheric Scattering](../scattering/index.md)）。

### Moon and Stars {#月と星}

| 要素 | 内容 |
| --- | --- |
| **月** | **太陽と同様に円盤**。**月の満ち欠けは、太陽の向きとの角度から、球の陰影で表す** |
| **星** | <strong>星空のキューブマップ（HDR）</strong>を**回して貼る**。**空が暗いほど見える**（**昼の明るさで消える**） |
| **夜空の明るさ** | **月明かり・星明かりを環境光に足す** |
| **またたき** | **星に時間でわずかな明滅** |

```hlsl
float3 stars = star_cubemap.Sample(linear_wrap, mul(view_dir, star_rotation)).rgb;
float night_factor = saturate(-sun_dir.y * 5.0);
float3 sky = day_sky + stars * night_factor;
```

<!-- fig:sun-arc:begin -->

<svg class="fig illust motion" data-fig="sun-arc" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sun-arc" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">時刻から太陽の向きを決める: 1 日で半円を描く</text>
<line x1="130" y1="300" x2="650" y2="300" stroke="#94a3b8" stroke-width="2"/>
<path d="M160,300 A230,230 0 0 1 620,300" fill="none" stroke="#e2e8f0" stroke-width="3" stroke-dasharray="6 6"/>
<circle cx="160" cy="300" r="16" fill="#e5aa28"><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.0833;0.0977;0.1121;0.1264;0.1408;0.1552;0.1695;0.1839;0.1983;0.2126;0.2270;0.2414;0.2557;0.2701;0.2845;0.2989;0.3132;0.3276;0.3420;0.3563;0.3707;0.3851;0.3994;0.4138;0.4282;0.4425;0.4569;0.4713;0.4856;0.5000;0.5144;0.5287;0.5431;0.5575;0.5718;0.5862;0.6006;0.6149;0.6293;0.6437;0.6580;0.6724;0.6868;0.7011;0.7155;0.7299;0.7443;0.7586;1.0000" values="160;160;160.492;161.968;164.419;167.837;172.206;177.508;183.719;190.814;198.762;207.529;217.077;227.365;238.35;249.985;262.219;275;288.274;301.983;316.069;330.472;345.129;359.979;374.957;390;405.043;420.021;434.871;449.528;463.931;478.017;491.726;505;517.781;530.015;541.65;552.635;562.923;572.471;581.238;589.186;596.281;602.492;607.794;612.163;615.581;618.032;619.508;620;620"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.0833;0.0977;0.1121;0.1264;0.1408;0.1552;0.1695;0.1839;0.1983;0.2126;0.2270;0.2414;0.2557;0.2701;0.2845;0.2989;0.3132;0.3276;0.3420;0.3563;0.3707;0.3851;0.3994;0.4138;0.4282;0.4425;0.4569;0.4713;0.4856;0.5000;0.5144;0.5287;0.5431;0.5575;0.5718;0.5862;0.6006;0.6149;0.6293;0.6437;0.6580;0.6724;0.6868;0.7011;0.7155;0.7299;0.7443;0.7586;1.0000" values="300;300;284.957;269.979;255.129;240.472;226.069;211.983;198.274;185;172.219;159.985;148.35;137.365;127.077;117.529;108.762;100.814;93.719;87.508;82.206;77.837;74.419;71.968;70.492;70;70.492;71.968;74.419;77.837;82.206;87.508;93.719;100.814;108.762;117.529;127.077;137.365;148.35;159.985;172.219;185;198.274;211.983;226.069;240.472;255.129;269.979;284.957;300;300"/></circle>
<circle cx="620" cy="300" r="12" fill="#94a3b8" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7721;0.7724;1.0000" values="0;0;1;1"/></circle>
<text x="160" y="322" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">日の出（東）</text>
<text x="620" y="322" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">日没（西）</text>
<text x="390" y="50" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">正午</text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">6 時: 地平線(長い影・赤い空)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.2066;0.2069;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">9 時: 昇る途中(影は西に長い)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2066;0.2069;0.3446;0.3448;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">12 時: 最も高い(影は最短)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.4825;0.4828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">15 時: 下がる途中<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;0.6204;0.6207;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">18 時: 地平線に沈む → 月が昇る<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;0.7583;0.7586;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:sun-arc:end -->

## Common Mistakes {#よくあるミス}

??? failure "昼なのに、星が透けて見える"
    **空の明るさに応じて、星を弱める**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **太陽・月・星を、それぞれに合う方法で**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Sky Models](index.md)
- [Day-Night Cycle](day-night.md)

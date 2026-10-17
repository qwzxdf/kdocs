---
title: Screen-Space Radial Blur
tags:
  - 描画
---

# Screen-Space Radial Blur

**太陽の画面上の位置から外側へ、画像を放射状にぼかして、光の筋を作る**のが**最も手軽**な方法です。**太陽が画面内にある時だけ使え、遮蔽物の形が筋に反映されます**。このページでは、**放射ぼかし**を説明します。

!!! tip "ポイント"
    - **明るい部分を抽出し、太陽の位置から放射状にぼかす**。
    - **遮蔽物の影が、筋として現れる**。
    - **太陽が画面外にあると、使えない**。
    - **サンプル数が少ないと、縞が出る**。

<!-- fig:radial-streak:begin -->

<svg class="fig illust motion" data-fig="radial-streak" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-radial-streak" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<filter id="rs-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="14"/>
</filter>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">放射ぼかし:各画素から太陽へ向かい、明るさを集める</text>
<rect x="40" y="80" width="700" height="260" fill="#7dd3fc" rx="6"/>
<circle cx="600" cy="130" r="48" fill="#fff7d6" fill-opacity="0.9" filter="url(#rs-glow)"/>
<circle cx="600" cy="130" r="20" fill="#fff7d6"/>
<rect x="300" y="160" width="40" height="180" fill="#14532d"/>
<rect x="370" y="210" width="22" height="130" fill="#14532d"/>
<rect x="460" y="140" width="36" height="200" fill="#14532d"/>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3446;0.3448;1.0000" values="0;0;1;1;0;0"/><circle cx="540" cy="300" r="8" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
<circle cx="546.0" cy="283.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="552.0" cy="266.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="558.0" cy="249.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="564.0" cy="232.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="570.0" cy="215.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="576.0" cy="198.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="582.0" cy="181.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="588.0" cy="164.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="594.0" cy="147.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="600.0" cy="130.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<line x1="540" y1="300" x2="600" y2="130" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">画素 A:太陽との間に、さえぎる物がない → 明るいサンプル 10 / 10</text>
<rect x="620" y="360" width="80" height="22" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.6204;0.6207;1.0000" values="0;0;1;1;0;0"/><circle cx="250" cy="310" r="8" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
<circle cx="285.0" cy="292.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="320.0" cy="274.0" r="4.5" fill="#0f172a" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="355.0" cy="256.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="390.0" cy="238.0" r="4.5" fill="#0f172a" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="425.0" cy="220.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="460.0" cy="202.0" r="4.5" fill="#0f172a" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="495.0" cy="184.0" r="4.5" fill="#0f172a" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="530.0" cy="166.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="565.0" cy="148.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="600.0" cy="130.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250" y1="310" x2="600" y2="130" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">画素 B:途中に木が 3 本ある → 明るいサンプル 6 / 10</text>
<rect x="620" y="360" width="80" height="22" fill="#cacaca" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;0.8963;0.8966;1.0000" values="0;0;1;1;0;0"/><circle cx="415" cy="325" r="8" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
<circle cx="433.5" cy="305.5" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="452.0" cy="286.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="470.5" cy="266.5" r="4.5" fill="#0f172a" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="489.0" cy="247.0" r="4.5" fill="#0f172a" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="507.5" cy="227.5" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="526.0" cy="208.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="544.5" cy="188.5" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="563.0" cy="169.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="581.5" cy="149.5" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<circle cx="600.0" cy="130.0" r="4.5" fill="#fde047" stroke="#ffffff" stroke-width="1.5"/>
<line x1="415" y1="325" x2="600" y2="130" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">画素 C:木が 1 本だけ手前にある → 明るいサンプル 8 / 10</text>
<rect x="620" y="360" width="80" height="22" fill="#e6e6e6" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<text x="40" y="404" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">サンプルが、空（明るい）なら +、木（暗い）なら 0。多いほど明るい筋。</text>
</svg>

<!-- fig:radial-streak:end -->

## 画面空間の放射ぼかし
**画面上の太陽の位置を中心に、各ピクセルから太陽へ向かう直線上の明るさを、何度かサンプルして足し合わせる**方法です。**簡単・安価で古くから使われています**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="放射ぼかし">
<text x="20" y="24" class="fig-title">放射ぼかし：各ピクセルから太陽に向かって、明るさを平均する</text>
<rect x="60" y="50" width="360" height="160" fill="#87ceeb" fill-opacity="0.2" stroke="currentColor" stroke-opacity="0.5"/>
<circle cx="360" cy="80" r="14" fill="#e5aa28"/>
<polygon points="120,210 160,100 190,210" fill="#333"/><polygon points="220,210 240,120 270,210" fill="#333"/>
<g stroke="#e5aa28" stroke-dasharray="4 3"><line x1="150" y1="180" x2="360" y2="80"/><line x1="250" y1="190" x2="360" y2="80"/></g>
<circle cx="150" cy="180" r="4" fill="#e5484d"/><circle cx="250" cy="190" r="4" fill="#e5484d"/>
<g font-size="12">
<text x="450" y="80" style="font-weight:700">手順</text>
<text x="450" y="104">① 太陽の画面上の位置を求める</text>
<text x="450" y="126">② 明るい所（空）を別の画像に抜き出す（物は黒）</text>
<text x="450" y="148">③ 各ピクセルから太陽へ向かう線上を、</text><text x="450" y="166">　 数十回サンプルして足す（減衰しながら）</text>
<text x="450" y="188">④ 元の絵に加算</text>
</g>
</svg>

```hlsl
float3 GodRays(float2 uv, float2 sun_uv) {
  float2 delta = (uv - sun_uv) * (density / kSampleCount);
  float2 sample_uv = uv;
  float illumination_decay = 1.0;
  float3 accumulated = 0;

  for (int i = 0; i < kSampleCount; ++i) {
    sample_uv -= delta;
    float3 sample_color = occlusion_texture.Sample(linear_clamp, sample_uv).rgb;
    sample_color *= illumination_decay * weight;
    accumulated += sample_color;
    illumination_decay *= decay;
  }
  return accumulated * exposure;
}
```

コードの要点です。`occlusion_texture` は、空の明るい部分だけが残り、物は黒くなる画像で、深度から作ります。`decay` は 0.95〜0.99 で、光源から遠いほど弱くします。`density` はぼかしの長さ（0.5〜1.0）です。サンプル数は 32〜100 で、半解像度で描くと軽くなります。欠点は、太陽が画面の外だと使えないこと、太陽の向きを見ていないと筋が消えること、空気の濃さや影の奥行きを表現できないことです。

### 原理

この方式は、Mitchell の GPU Gems 3 の記事 "Volumetric Light Scattering as a Post-Process"（2007）で広まりました。考え方は、「画面上で太陽に近い位置の明るさが、そこから伸びる光の筋の源である」ことです。まず、シーンを「太陽の明るさだけが残り、物体は黒いシルエット」になる画像（オクルージョン画像）に直します。次に、各ピクセルから太陽の画面位置へ向かう直線に沿って、この画像をサンプルして足します。太陽に近い方向の明るい部分（空）が、直線上にあれば、そのピクセルは明るくなります。物体のシルエットが直線上にあれば、その分は暗いままです。結果として、シルエットの背後から放射状に伸びる光の筋が出ます。

直線に沿ったサンプルは、太陽から遠ざかるほど弱める減衰（`decay`）を掛けて足します。この減衰が、光が遠くへ届くほど弱まる様子を表します。

### 制約の理由

この方式は、あくまで「画面の絵」を加工しているだけで、3D の空間を解いていません。そのため、太陽が画面外にあると、そもそも太陽の画面位置が定義できず、ぼかしの中心がなくなります。また、手前の物体と奥の物体は区別できず、すべてが同じ平面のシルエットとして扱われます。「霧の奥行き」も存在しません。これらの制約は、後の節で説明するシャドウ マップによる方式で解決されます。

**太陽が画面外のときにも自然にするため**、**太陽が画面に近いほど強く、離れると弱くする**フェードを**付けます**。

## よくあるミス

??? failure "太陽が画面外に出ると、光の筋が消える"
    **他の方式**に**切り替える**、または**フェード**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **太陽から放射状にぼかす。手軽だが制約あり**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [God Rays](index.md)
- [Gaussian Blur](../../postprocess/bloom/gaussian.md)

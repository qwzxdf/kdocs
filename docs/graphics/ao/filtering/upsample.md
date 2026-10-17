---
title: Upsampling
tags:
  - 描画
---

# Upsampling

**AO は、半解像度（または 1/4）で計算する**と**コストが大きく減ります**が、**フル解像度に戻すとき、単純な拡大では、エッジがにじみます**。**フル解像度の深度を見ながら、近い深度の低解像度サンプルだけを重く混ぜる「深度を考慮したアップサンプル」**が**必要**です。このページでは、**低解像度で計算する理由・深度を見るアップサンプル・実装**を説明します。

!!! tip "ポイント"
    - **低解像度で AO を計算**し、**コストを 1/4**。
    - **拡大時に、フル解像度の深度**と**低解像度の深度**を**比べ、近いものを重く**。
    - **単純なバイリニアは、エッジで AO がにじむ**。
    - **ジョイント バイラテラル アップサンプル**と呼ばれる。

## アップサンプル：低解像度から戻す
AO は<strong>低周波（なめらか）</strong>なので**半分や 1/4 の解像度**で計算して、**拡大**すると**コストを大きく減らせます**（[低解像度のエフェクト](../../../rendering/low-res-effects.md)）。しかし、**単純なバイリニア拡大**は、**境界でにじみます**。

<!-- fig:ao-upsample:begin -->

<svg class="fig illust motion" data-fig="ao-upsample" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ao-upsample" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">アップサンプル:低解像度の 4 点から、深度の近い点を重く混ぜる</text>
<rect x="190" y="110" width="300" height="240" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 3"/>
<circle cx="250" cy="160" r="26" fill="#9e9e9e" stroke="#475569" stroke-width="2"/>
<text x="250" y="165" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">A</text>
<text x="250" y="206" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">深度 0.30</text>
<circle cx="430" cy="160" r="26" fill="#a8a8a8" stroke="#475569" stroke-width="2"/>
<text x="430" y="165" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">B</text>
<text x="430" y="206" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">深度 0.30</text>
<circle cx="250" cy="300" r="26" fill="#949494" stroke="#475569" stroke-width="2"/>
<text x="250" y="305" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">C</text>
<text x="250" y="346" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#2563eb">深度 0.30</text>
<circle cx="430" cy="300" r="26" fill="#f9f9f9" stroke="#475569" stroke-width="2"/>
<text x="430" y="305" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">D</text>
<text x="430" y="346" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#60a5fa">深度 0.85</text>
<circle cx="380" cy="215" r="10" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="340" y="98" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">橙の点 = フル解像度の画素（深度 0.32）</text>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><line x1="380" y1="215" x2="250" y2="160" stroke="#2ea043" stroke-width="4.639183958275801" opacity="0.8"/>
<text x="250" y="124" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2ea043">重み 0.46</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;1.0000" values="0;0;1;1"/><line x1="380" y1="215" x2="430" y2="160" stroke="#2ea043" stroke-width="7.0" opacity="0.8"/>
<text x="430" y="124" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2ea043">重み 0.76</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;1.0000" values="0;0;1;1"/><line x1="380" y1="215" x2="250" y2="300" stroke="#2ea043" stroke-width="4.145353032672427" opacity="0.8"/>
<text x="250" y="264" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2ea043">重み 0.40</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;1.0000" values="0;0;1;1"/><line x1="380" y1="215" x2="430" y2="300" stroke="#e5484d" stroke-width="1.0" opacity="0.8"/>
<text x="430" y="264" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5484d">重み 0.00</text>
</g>
<rect x="520" y="140" width="100" height="50" fill="#bfbfbf" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;1.0000;1.0000" values="0;0;1;1;0"/></rect>
<rect x="520" y="250" width="100" height="50" fill="#a1a1a1" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6477;0.6480;1.0000;1.0000" values="0;0;1;1;0"/></rect>
<text x="520" y="130" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">距離だけの補間<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="520" y="240" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">距離 × 深度の近さ<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6477;0.6480;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="520" y="214" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">AO = 0.53<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="520" y="324" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">AO = 0.36（D に引きずられない）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6477;0.6480;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">低解像度の AO 4 点（A〜D）から、中央の画素の AO を求める。各点の重み = 距離 × 深度の近さ<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;1.0000" values="1;1;0;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">深度が違う D（奥）の重みは、ほぼ 0。境界がにじまない<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ao-upsample:end -->

### なぜ単純な拡大ではだめなのか

低解像度の AO 画像の 1 画素は、フル解像度の 2×2 画素（半分の解像度の場合）に対応します。単純なバイリニア補間で拡大すると、隣り合う低解像度画素の AO を、距離だけを手がかりに混ぜます。物体の輪郭では、隣り合う 2 つの低解像度画素が<strong>手前の物体と奥の背景</strong>のように別の面に乗っていることがあります。すると、背景の画素に、手前の物体の AO が混じり、物の輪郭にぼんやりした暗い縁やにじみが出ます。

AO はもともと低周波で、面の内側ではなめらかに変化するので、拡大自体は問題ありません。問題は<strong>面の境界をまたいで混ぜる</strong>ことだけです。

### ジョイント バイラテラル アップサンプル

この問題を解決するのが、「フル解像度の深度を手がかりにして、補間の重みを調整する」方法です。手がかり（深度）が、補間する対象（AO）とは別の画像から来るので、「ジョイント（共同）」バイラテラルと呼ばれます。

考え方は、次のとおりです。フル解像度の 1 画素について、その周囲の低解像度画素 4 つ（2×2）を見ます。それぞれの低解像度画素には、その場所の深度を覚えておきます（AO を計算したときの縮小した深度）。フル解像度の画素の深度に<strong>近い深度を持つ低解像度画素ほど</strong>、同じ面に乗っているはずなので、重みを大きくします。深度が大きく違う低解像度画素は、別の面なので、ほとんど無視します。

式にすると、各低解像度画素 i の重みは、普通のバイリニアの重みに、深度の近さを掛けたものになります。

<div class="formula">w_i = (バイリニアの重み) × 1 / (ε + |z_full − z_low_i|)　　AO = Σ w_i · AO_low_i / Σ w_i</div>

ε は 0 で割らないための小さな値です。深度の差が大きいほど重みが小さくなり、境界をまたいだ混ぜ方が自然に避けられます。

```hlsl
float UpsampleAO(float2 uv_full) {
  float z_full = LinearDepth(uv_full);
  float2 low_pos = uv_full * low_size - 0.5;
  float2 f = frac(low_pos);
  int2 base = int2(floor(low_pos));

  float sum = 0.0;
  float weight_sum = 0.0;
  [unroll] for (int y = 0; y < 2; ++y) {
    [unroll] for (int x = 0; x < 2; ++x) {
      int2 p = base + int2(x, y);
      float w = (x == 0 ? 1.0 - f.x : f.x) * (y == 0 ? 1.0 - f.y : f.y);
      w *= 1.0 / (0.001 + abs(z_full - low_depth_tex.Load(int3(p, 0)).r));
      sum += ao_low_tex.Load(int3(p, 0)).r * w;
      weight_sum += w;
    }
  }
  return sum / weight_sum;
}
```

### 実装で気をつけること

低解像度の深度を、<strong>AO を計算したときと同じもの</strong>で持っておく必要があります。縮小の方法（代表の 1 点を選ぶ、最小を取るなど）が違うと、重みが合わなくなります。

もう 1 つの方式として、<strong>最も深度が近い低解像度画素を 1 つだけ選ぶ</strong>方法もあります。境界のシャープさは最高ですが、面の内側でも選ばれる画素が切り替わる所で階段状の段差が出やすいです。重み付けで混ぜる方式のほうが、見た目が安定します。

### より良いやり方：法線も使う

深度が近くても向きの違う面（部屋の隅の壁と床）では、AO が急に変わります。深度に加えて<strong>法線の近さ</strong>も重みに掛ければ、隅の境界もよりきれいに守れます。また、2×2 でなく 3×3 の範囲を見ると、低解像度のサンプルが足りない場所（輪郭の細い所）を補えます。近年の実装は、アップサンプルを時間蓄積と一体にして、フル解像度のサンプルを少数だけ追加で撒く方式もあります（[Typical Pipeline](pipeline.md)）。

## よくあるミス

??? failure "バイリニアで拡大して、物の輪郭に暗いにじみが出る"
    **深度を見るアップサンプル**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **低解像度で計算 ＋ 深度を見て拡大**
    - [x] **エッジのにじみを防ぐ**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [AO Filtering](index.md)
- [Bilateral Blur](bilateral-blur.md)
- [Typical Pipeline](pipeline.md)

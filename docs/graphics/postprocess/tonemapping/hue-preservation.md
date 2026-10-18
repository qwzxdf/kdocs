---
title: Preserving Hue
tags:
  - 描画
---

# Preserving Hue

**トーンマップ曲線を、R・G・B に別々に掛けるか、輝度にだけ掛けるか**で**明るい色の見え方**が**大きく変わります**。**別々に掛けると彩度の高い明るい色の比率が崩れ、色相がずれます**。**輝度にだけ掛けると色相は保てますが派手な色が飽和しすぎます**。このページでは、**2 つの方式の違い・ハイブリッド・彩度の扱い・どう選ぶか**を説明します。

!!! tip "ポイント"
    - <strong>チャンネルごと</strong>：<strong>R・G・B に別々に曲線</strong>。<strong>フィルムの特性に近く、明部は白へ向かう</strong>。<strong>色相はずれる</strong>。
    - <strong>輝度ベース</strong>：<strong>輝度にだけ曲線を掛け、色の比率を保つ</strong>。<strong>色相は保つが鮮やかな明部が飽和しすぎる</strong>。
    - <strong>ハイブリッド</strong>：<strong>両者を混ぜる</strong>。<strong>ACES・AgX は内部で彩度・色相を調整</strong>している。
    - <strong>彩度</strong>：<strong>輝度が大きいほど、彩度を落とす</strong>のが<strong>自然な白への向かい方</strong>。
    - <strong>選び方</strong>：<strong>色の忠実さ → 輝度ベース寄り、映画的な絵 → チャンネルごと寄り</strong>。

<!-- fig:hue-preserve:begin -->

<svg class="fig illust motion" data-fig="hue-preserve" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hue-preserve" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">色相の保存:チャンネルごとに圧縮すると、明るい橙が、黄色く白っぽくなる</text>
<text x="60" y="96" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">チャンネルごと（色相が黄色い方へずれる・白くなる）</text>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><rect x="60" y="120" width="115" height="80" fill="#ba8a40" stroke="#94a3b8" stroke-width="1.5"/>
<text x="117" y="220" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2237;0.2240;1.0000" values="0;0;1;1"/><rect x="195" y="120" width="115" height="80" fill="#d4aa56" stroke="#94a3b8" stroke-width="1.5"/>
<text x="252" y="220" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3677;0.3680;1.0000" values="0;0;1;1"/><rect x="330" y="120" width="115" height="80" fill="#e6c871" stroke="#94a3b8" stroke-width="1.5"/>
<text x="387" y="220" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5117;0.5120;1.0000" values="0;0;1;1"/><rect x="465" y="120" width="115" height="80" fill="#f2de90" stroke="#94a3b8" stroke-width="1.5"/>
<text x="522" y="220" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×8</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6557;0.6560;1.0000" values="0;0;1;1"/><rect x="600" y="120" width="115" height="80" fill="#f8edb0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="657" y="220" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×16</text>
</g>
<text x="60" y="266" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">輝度で圧縮（色相を保つ）</text>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><rect x="60" y="290" width="115" height="80" fill="#d68537" stroke="#94a3b8" stroke-width="1.5"/>
<text x="117" y="390" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2237;0.2240;1.0000" values="0;0;1;1"/><rect x="195" y="290" width="115" height="80" fill="#ffa142" stroke="#94a3b8" stroke-width="1.5"/>
<text x="252" y="390" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3677;0.3680;1.0000" values="0;0;1;1"/><rect x="330" y="290" width="115" height="80" fill="#ffb84c" stroke="#94a3b8" stroke-width="1.5"/>
<text x="387" y="390" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5117;0.5120;1.0000" values="0;0;1;1"/><rect x="465" y="290" width="115" height="80" fill="#ffc953" stroke="#94a3b8" stroke-width="1.5"/>
<text x="522" y="390" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×8</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6557;0.6560;1.0000" values="0;0;1;1"/><rect x="600" y="290" width="115" height="80" fill="#ffd357" stroke="#94a3b8" stroke-width="1.5"/>
<text x="657" y="390" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">明るさ ×16</text>
</g>
<text x="60" y="56" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">同じ色（鮮やかな橙）を、明るさだけ 1・2・4・8・16 倍にして、トーン マップする<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="60" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">チャンネルごとの圧縮は、大きい成分ほど強く縮むので、色相がずれ、白に近づく。炎・爆発・ネオンで、色が抜ける原因になる。</text>
</svg>

<!-- fig:hue-preserve:end -->

## 違いを見る

**赤 (4.0, 0.5, 0.2) という、明るい赤橙**を**Reinhard** に**通す**と、次のようになります。

明るい赤橙 (4.0, 0.5, 0.2) を Reinhard に通した例です。入力は (4.0, 0.5, 0.2) です。チャンネルごとに各成分へ `x/(1+x)` を掛けると、結果は (0.80, 0.33, 0.17) になります。輝度ベースだと、輝度 L ≒ 1.2 を L/(1+L) ≒ 0.55 に圧縮し、色に比を掛けるので、結果が 1.0 を超えて飽和します。

**チャンネルごと**だと、**R の比率が下がって、G・B の比率が相対的に上がる**ため、**赤が少し黄色（橙）寄り**に見えます。**これがフィルムのような、明部の色の変化**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="色相の変化の比較">
<text x="20" y="26" class="fig-title">赤橙の光を、だんだん明るくしていくと</text>
<defs>
<linearGradient id="hp-ch" x1="0" x2="1"><stop offset="0" stop-color="#7a1d10"/><stop offset="0.4" stop-color="#e5602f"/><stop offset="0.75" stop-color="#ffb24a"/><stop offset="1" stop-color="#fff2c6"/></linearGradient>
<linearGradient id="hp-lum" x1="0" x2="1"><stop offset="0" stop-color="#7a1d10"/><stop offset="0.5" stop-color="#e5483a"/><stop offset="1" stop-color="#ff5a45"/></linearGradient>
<linearGradient id="hp-hy" x1="0" x2="1"><stop offset="0" stop-color="#7a1d10"/><stop offset="0.5" stop-color="#e5543a"/><stop offset="0.85" stop-color="#ff9a6a"/><stop offset="1" stop-color="#ffe9d6"/></linearGradient>
</defs>
<g font-size="13">
<text x="40" y="62" style="font-weight:700">チャンネルごと</text><rect x="40" y="70" width="500" height="26" fill="url(#hp-ch)"/><text x="560" y="88" style="font-size:10px">橙 → 黄 → 白（フィルム的、色相は変わる）</text>
<text x="40" y="126" style="font-weight:700">輝度ベース</text><rect x="40" y="134" width="500" height="26" fill="url(#hp-lum)"/><text x="560" y="152" style="font-size:10px">赤のまま（色相は保つが、白に届かず飽和）</text>
<text x="40" y="190" style="font-weight:700">ハイブリッド</text><rect x="40" y="198" width="500" height="18" fill="url(#hp-hy)"/><text x="560" y="212" style="font-size:12px">赤 → 淡い赤 → 白（自然）</text>
</g>
</svg>

## チャンネルごと

```hlsl
float3 TonemapPerChannel(float3 color) {
  return ACESNarkowicz(color);
}
```

チャンネルごとの長所は、明るい色が自然に白へ向かうこと、実装が簡単なこと、フィルムのような質感が出ることです。短所は、色相が変わること（青が紫に、赤が黄に）と、意図した色が強い光で変わること（エフェクト）です。

## 輝度ベース

```hlsl
float Luminance(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

float3 TonemapByLuminance(float3 color) {
  float l = Luminance(color);
  float mapped = Reinhard(float3(l, l, l)).x;
  return color * (mapped / max(l, 1e-4));
}
```

輝度ベースの長所は、色相が完全に保たれることと、意図した色のままになることです。短所は、彩度の高い明るい色が 1 を超えて飽和すること（最後に切ると色が濃すぎる）と、白に向かわないので眩しさが出にくいことです。

**1 を超える値の処理**が**課題**です。**飽和した成分を他の成分に分配**（**ガマット マッピング**）したり、**白へ混ぜたり**して**対処**します。

## ハイブリッド

**両者を混ぜる**のが**定番**です。

```hlsl
float3 TonemapHybrid(float3 color, float blend) {
  float3 per_channel = ACESNarkowicz(color);
  float l = Luminance(color);
  float l_mapped = Luminance(per_channel);
  float3 by_luminance = color * (l_mapped / max(l, 1e-4));
  return lerp(by_luminance, per_channel, blend);
}
```

`blend` の値による見た目です。0 なら色相を完全に保ちます（輝度ベース）。1 ならフィルム的になります（チャンネルごと）。0.3〜0.6 が、ほどよく自然です。

## 彩度を落として白へ向かわせる

**実際の光は非常に明るいと目やセンサーの飽和で白っぽく**見えます。**輝度が大きいほど彩度を落とす**と、**自然に白へ向かいます**。

```hlsl
float3 DesaturateHighlights(float3 color, float threshold, float strength) {
  float l = Luminance(color);
  float t = saturate((l - threshold) / threshold) * strength;
  return lerp(color, float3(l, l, l), t);
}
```

彩度を落とす方式のコードの要点です。`threshold` は、この輝度から彩度を落とし始める閾値です。`strength` は、どれだけ白へ向かうかを表します（0〜1）。トーンマップの前に、HDR のうちに行います。

**AgX・Tony McMapface は、こうした彩度の処理を曲線の設計に組み込んで**います。

## 選び方

優先することごとの選び方です。映画的でフィルムの質感を出したいなら、チャンネルごと（ACES・Hable）です。色の忠実さやエフェクトの色が大事なら、輝度ベース寄りのハイブリッドか AgX です。まず簡単にしたいなら、1 行で済むチャンネルごとです。色相の破綻を許さないなら、AgX・Tony McMapface・PBR Neutral を選びます。

## よくあるミス

??? failure "輝度ベースで、1 を超えた値をそのまま出力して、色が破綻する"
    **最後に `saturate`**、または**ガマット マッピング**（超えた分を他の成分へ分配）。

??? failure "輝度の係数を、BT.601（0.299, 0.587, 0.114）にしてしまう"
    **sRGB（Rec.709）の原色なら、`(0.2126, 0.7152, 0.0722)`**。

??? failure "彩度を落とす処理を、トーンマップの後で行って、効きが弱い"
    **HDR のうち（トーンマップの前）に**行う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>チャンネルごと</strong> ＝ <strong>フィルム的。色相がずれる</strong>
    - [x] <strong>輝度ベース</strong> ＝ <strong>色相を保つが、鮮やかな明部が飽和</strong>
    - [x] <strong>ハイブリッド</strong>（<strong>blend 0.3〜0.6</strong>）が<strong>実用的</strong>
    - [x] <strong>輝度が大きいほど彩度を落とす</strong>と<strong>自然に白へ</strong>
    - [x] <strong>輝度の係数は Rec.709</strong>（0.2126, 0.7152, 0.0722）

## 参考

- Troy Sobotka, "AgX"（色相の保持）
- Pharr, Jakob, Humphreys, "Physically Based Rendering"（色と輝度）
- Hart, "Tone Mapping with Hue Preservation"（解説）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Reinhard](reinhard.md)
- [ACES](aces.md)
- [AgX and Others](agx.md)

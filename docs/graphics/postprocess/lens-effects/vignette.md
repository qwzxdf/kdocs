---
title: Vignette
tags:
  - 描画
---

# Vignette

<strong>ビネット（周辺減光）</strong>は、**画面の周辺が中心より暗くなる**効果です。**実際のレンズでは、設計や絞り・フィルターの影響で周辺に届く光が減る**ために**起きます**。**視線を画面の中心に集める効果があり**、**映画風・夜・緊張した場面**で**よく使われます**。**実装はとても簡単**ですが、**かけすぎると周辺が見えずプレイしにくい**ので、**注意**が**必要**です。このページでは、**物理的な原因（cos⁴ の法則）・基本の式・形（円・楕円）・色付きのビネット・ゲームでの使い方**を説明します。

!!! tip "ポイント"
    - ビネット ＝ <strong>画面の周辺ほど暗くする</strong>。<strong>中心は変えない</strong>。
    - 物理的な原因 ＝ <strong>cos⁴θ の法則</strong>（<strong>光軸から離れた光ほど、角度の 4 乗で暗い</strong>）と<strong>レンズ・絞りの遮り（機械的ビネット）</strong>。
    - 実装 ＝ <strong>画面中心からの距離で、暗くする係数を `smoothstep` で決め、色に掛ける</strong>。
    - <strong>形</strong>は<strong>円・楕円・四角寄り</strong>。<strong>アスペクト比の補正</strong>が<strong>必要</strong>。
    - <strong>色付き（暗い赤・黒以外）</strong>のビネットも<strong>演出</strong>に<strong>使える</strong>。
    - <strong>強すぎない</strong>。<strong>周辺のゲーム情報が見づらくなる</strong>。<strong>設定で切れる</strong>。

## 起きる理由

**レンズの設計上、光軸（画面の中心）から離れた方向から来る光は、レンズの端で遮られたり、斜めに入る分だけ弱くなったりします**。

<div class="formula">周辺の明るさ = 中心の明るさ × cos⁴(θ)　（θ：光軸からの角度）</div>

ビネットの原因は 3 つあります。cos⁴ の法則（自然なビネット）は、角度 θ が大きいほど、光が 4 乗で弱まる現象です。機械的ビネットは、レンズ鏡筒・フィルター・絞りが斜めの光を遮ることで起きます。光学的ビネットは、レンズ内部の絞りが斜めの光を通しにくいことで起きます。

<svg class="fig illust" viewBox="0 0 780 210" role="img" aria-label="ビネット">
<text x="20" y="26" class="fig-title">ビネット：中心から離れるほど暗くなる</text>
<defs><radialGradient id="vg-g" cx="0.5" cy="0.5" r="0.7"><stop offset="0.4" stop-color="#fff7d1" stop-opacity="1"/><stop offset="1" stop-color="#000000" stop-opacity="0.85"/></radialGradient></defs>
<rect x="40" y="50" width="300" height="140" fill="#fff7d1" stroke="#94a3b8"/><text x="40" y="206" style="font-size:12px">ビネットなし</text>
<rect x="400" y="50" width="300" height="140" fill="#fff7d1" stroke="#94a3b8"/><rect x="400" y="50" width="300" height="140" fill="url(#vg-g)"/><text x="400" y="206" style="font-size:12px">ビネットあり：周辺が暗い</text>
</svg>

## 基本の式

```hlsl
float Vignette(float2 uv, float intensity, float smoothness, float roundness) {
  float2 d = (uv - 0.5) * float2(roundness, 1.0) * 2.0;
  float distance_from_center = length(d);
  return 1.0 - smoothstep(1.0 - intensity - smoothness, 1.0 - intensity, distance_from_center) * intensity;
}

float3 ApplyVignette(float3 color, float2 uv) {
  return color * Vignette(uv, kVignetteIntensity, kVignetteSmoothness, kRoundness);
}
```

コードの要点です。`d = (uv − 0.5) × 2` は、画面中心を原点に ±1 の座標にしたもので、角で約 1.4 です。`length(d)` は画面中心からの距離です。`smoothstep` は、暗くなり始める距離から暗くなりきる距離までを滑らかにします。`intensity` は周辺の暗さの強さ（0〜1）、`smoothness` は暗さの移り変わりの幅、`roundness` はアスペクト比の補正です。

<!-- fig:vignette-params:begin -->

<svg class="fig illust motion" data-fig="vignette-params" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vignette-params" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<radialGradient id="vg-std" cx="0.5" cy="0.5" r="0.55" gradientUnits="objectBoundingBox"><stop offset="0.45" stop-color="#000000" stop-opacity="0"/>
<stop offset="1.0" stop-color="#000000" stop-opacity="0.85"/>
</radialGradient>
<radialGradient id="vg-small" cx="0.5" cy="0.5" r="0.38" gradientUnits="objectBoundingBox"><stop offset="0.4" stop-color="#000000" stop-opacity="0"/>
<stop offset="1.0" stop-color="#000000" stop-opacity="0.85"/>
</radialGradient>
<radialGradient id="vg-large" cx="0.5" cy="0.5" r="0.85" gradientUnits="objectBoundingBox"><stop offset="0.5" stop-color="#000000" stop-opacity="0"/>
<stop offset="1.0" stop-color="#000000" stop-opacity="0.85"/>
</radialGradient>
<radialGradient id="vg-soft" cx="0.5" cy="0.5" r="0.6" gradientUnits="objectBoundingBox"><stop offset="0.02" stop-color="#000000" stop-opacity="0"/>
<stop offset="1.0" stop-color="#000000" stop-opacity="0.85"/>
</radialGradient>
<radialGradient id="vg-hard" cx="0.5" cy="0.5" r="0.55" gradientUnits="objectBoundingBox"><stop offset="0.78" stop-color="#000000" stop-opacity="0"/>
<stop offset="0.82" stop-color="#000000" stop-opacity="0.85"/>
</radialGradient>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ビネット:半径とやわらかさで、四隅の暗さが変わる</text>
<rect x="60" y="70" width="420" height="260" fill="#fde68a"/>
<rect x="60" y="220" width="420" height="110" fill="#86efac"/>
<rect x="100" y="150" width="90" height="120" fill="#fca5a5"/>
<rect x="310" y="130" width="110" height="140" fill="#93c5fd"/>
<circle cx="400" cy="115" r="26" fill="#ffffff"/>
<rect x="60" y="70" width="420" height="260" fill="url(#vg-std)" opacity="1"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0828;1.0000" values="1;1;0;0"/></rect>
<rect x="60" y="70" width="420" height="260" fill="url(#vg-small)" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0276;0.0552;0.2621;0.2897;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="60" y="70" width="420" height="260" fill="url(#vg-large)" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2345;0.2621;0.4690;0.4966;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="60" y="70" width="420" height="260" fill="url(#vg-std)" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4414;0.4690;0.5517;0.5793;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="60" y="70" width="420" height="260" fill="url(#vg-soft)" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5241;0.5517;0.7241;0.7517;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="60" y="70" width="420" height="260" fill="url(#vg-hard)" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6966;0.7241;0.8621;0.8897;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="60" y="70" width="420" height="260" fill="url(#vg-std)" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.8345;0.8621;1.0000" values="0;0;1;1"/></rect>
<rect x="60" y="70" width="420" height="260" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="510" y="120" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">標準の設定<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;1.0000" values="1;1;0;0"/></text>
<text x="510" y="120" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">半径を小さく<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.2618;0.2621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="120" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">半径を大きく<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2618;0.2621;0.4687;0.4690;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="120" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">標準に戻す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4687;0.4690;0.5514;0.5517;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="120" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">やわらかく（なだらか）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5514;0.5517;0.7239;0.7241;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="120" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">硬く（境目がくっきり）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7239;0.7241;0.8618;0.8621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="120" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">標準に戻す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.8618;0.8621;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="510" y="150" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">暗くなる範囲が中心へ広がる<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.2618;0.2621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="150" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">四隅だけが、わずかに暗い<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2618;0.2621;0.4687;0.4690;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="150" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">暗さが、なめらかに増える<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5514;0.5517;0.7239;0.7241;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="150" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">円の縁が見えてしまう（不自然）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7239;0.7241;0.8618;0.8621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="230" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">radius ＝ 暗くなり始める距離</text>
<text x="510" y="254" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">smoothness ＝ 暗さの変化のなだらかさ</text>
<text x="510" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#e5484d">強すぎると、画面の中心まで暗くなる</text>
</svg>

<!-- fig:vignette-params:end -->

### 物理的な cos⁴

**画面中心からの距離と視野角から、`cos⁴(θ)` で暗くする**と**自然なビネット**になります。

```hlsl
float NaturalVignette(float2 uv, float vertical_fov_radians, float aspect) {
  float2 d = (uv - 0.5) * 2.0;
  float2 tan_half = tan(vertical_fov_radians * 0.5) * float2(aspect, 1.0);
  float2 ray = d * tan_half;
  float cos_theta = rsqrt(1.0 + dot(ray, ray));
  float c2 = cos_theta * cos_theta;
  return c2 * c2;
}
```

物理版のコードの要点です。`tan(fov/2)` は、画面の端に対応する視線の傾きです。`cos θ = 1 / √(1 + tan²)` で、視線の角度の余弦を求めます。`cos⁴` が、物理的なビネットの係数です。

**広角（視野角が大きい）ほど、周辺が暗くなる**ことが**自然**に**再現**されます。

## 形

ビネットの形は 3 種類です。円形は、`roundness` を画面のアスペクト比にして真円にします。楕円（画面に沿う）は、`roundness` を 1 にして、画面の縦横比に沿った楕円にします。四角寄りは、距離に最大ノルム（`max(|x|, |y|)`）を使い、画面の四隅だけをほんのり暗くします。

```hlsl
float BoxVignette(float2 uv, float intensity, float smoothness) {
  float2 d = abs(uv - 0.5) * 2.0;
  float distance_from_center = max(d.x, d.y);
  return 1.0 - smoothstep(1.0 - intensity - smoothness, 1.0, distance_from_center) * intensity;
}
```

## 色付きのビネット

**黒だけでなく、色を付ける**と**演出**になります。

黒だけでなく、色を付けると演出になります。暗い赤は、体力が少ない・ダメージ・危険を表します。暗い青は、水中・夜・冷たさです。暗い緑は、毒やナイト ビジョンです。白（明るい縁）は、夢・回想・眩しさです。

```hlsl
float3 ColoredVignette(float3 color, float2 uv, float3 vignette_color) {
  float v = 1.0 - Vignette(uv, kVignetteIntensity, kVignetteSmoothness, kRoundness);
  return lerp(color, vignette_color, v);
}
```

## ゲームでの使い方

ゲームでの使い方です。映画風の常時使用では、ごく弱く（0.2〜0.3）かけます。夜や洞窟では強めにして、懐中電灯の円のようにします。体力が低いときは、赤いビネットを体力に応じて濃くします。狙いやズームでは、スコープ中に強いビネット（円）をかけます。会話やカットシーンでは、視線を中心に集めます。

## より良いやり方

より良いやり方を挙げます。`smoothstep` で滑らかにして、境が見えないようにします。アスペクト比を補正して、ウルトラワイドでも形が崩れないようにします。物理的な cos⁴ を使うと、視野角に応じた自然な暗さになります。色付きにして、体力や状態の演出に使います。トーンマップ後（LDR）で乗算し、見た目の明るさに直接かけます。色収差・グレイン・トーンマップと 1 パスに統合します。プレイしにくい人のために、オプションで切れるようにします。

## よくあるミス

??? failure "ビネットが強すぎて、周辺の敵や UI が見えない"
    <strong>控えめに（0.2〜0.3）</strong>、**オプションで調整**。

??? failure "ウルトラワイドで、ビネットが横に伸びて不自然"
    **アスペクト比を補正**。

??? failure "ビネットの境がはっきり見える"
    **`smoothness` を大きく**し、**`smoothstep`** を使う。

??? failure "UI まで暗くなる"
    **ビネットは UI の前に掛ける**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビネット ＝ <strong>画面の周辺ほど暗くする</strong>。<strong>視線を中心へ</strong>
    - [x] <strong>物理的な原因は cos⁴θ</strong>（と<strong>レンズの遮り</strong>）
    - [x] <strong>中心からの距離 ＋ `smoothstep`</strong> で<strong>簡単に実装</strong>。<strong>アスペクト比を補正</strong>
    - [x] <strong>色付き</strong>で<strong>体力・水中・毒</strong>などの<strong>演出</strong>
    - [x] <strong>控えめに</strong>。<strong>UI の前に設定で切れる</strong>

## 参考

- Wikipedia, "Vignetting"
- Pharr, Jakob, Humphreys, "Physically Based Rendering"（cos⁴ の法則）
- Unity, "Post-processing: Vignette"

## 関連ページ

- [Lens Effects](index.md)
- [Chromatic Aberration](chromatic-aberration.md)
- [Film Grain](film-grain.md)
- [Color Grading](../color-grading/index.md)

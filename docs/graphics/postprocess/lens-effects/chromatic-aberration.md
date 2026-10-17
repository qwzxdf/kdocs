---
title: Chromatic Aberration
tags:
  - 描画
---

# Chromatic Aberration

<strong>色収差（Chromatic Aberration）</strong>は、**レンズを通った光が波長（色）によって、わずかに違う位置に像を結ぶ**ために起きる**現象**です。**画面の端で物の輪郭が赤と青（または緑とマゼンタ）にずれて、にじんで見えます**。**カメラの欠点**ですが<strong>ゲームでは「ホラー・SF・ダメージ・サイバーパンク」</strong>などの**演出**として**使われます**。**高品質になるわけではなく、完全に好みの問題**です。このページでは、**起きる理由・基本の実装・分散（多サンプル）による高品質版・かけ方（どこに・どれくらい）・演出での使い方**を説明します。

!!! tip "ポイント"
    - 色収差 ＝ <strong>波長ごとに、屈折率が違い、赤・緑・青が少しずつずれて結像する</strong>。
    - <strong>画面の中心はほぼずれず、端ほど大きくずれる</strong>（<strong>距離の 2 乗に比例</strong>）。
    - 実装 ＝ <strong>R・G・B を中心から外へ（または逆に）ずらしてサンプル</strong>。
    - <strong>高品質版</strong>は<strong>多数のサンプルを、波長に応じてずらし、色に変換して積分</strong>する。
    - <strong>強さは 0.005〜0.02 程度</strong>。<strong>強すぎると画面が溶けて見え、酔う</strong>。
    - <strong>演出</strong>：<strong>被ダメージ・ワープ・ホラー・グリッチ</strong>。<strong>一時的に強くする</strong>。

## 起きる理由

**ガラスの屈折率は、光の波長で少し違います**（**青は強く曲がり、赤は弱く曲がる**）。**そのため、レンズに入った白い光は、色ごとに少しずつ違う場所に像を結びます**。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="色収差の原理">
<text x="20" y="26" class="fig-title">青は強く曲がり、赤は弱く曲がるので、結像する位置が違う</text>
<line x1="40" y1="120" x2="700" y2="120" stroke="currentColor" stroke-opacity="0.3" stroke-dasharray="4 3"/>
<ellipse cx="300" cy="120" rx="16" ry="70" fill="#e0f2fe" stroke="currentColor" stroke-width="3"/>
<text x="270" y="40" style="font-size:12px">レンズ</text>
<g stroke-width="2.5" fill="none"><line x1="40" y1="75" x2="300" y2="75" stroke="#94a3b8"/><line x1="40" y1="165" x2="300" y2="165" stroke="#94a3b8"/>
<line x1="300" y1="75" x2="470" y2="120" stroke="#2563eb"/><line x1="300" y1="165" x2="470" y2="120" stroke="#2563eb"/>
<line x1="300" y1="75" x2="560" y2="120" stroke="#2ea043"/><line x1="300" y1="165" x2="560" y2="120" stroke="#2ea043"/>
<line x1="300" y1="75" x2="640" y2="120" stroke="#e5484d"/><line x1="300" y1="165" x2="640" y2="120" stroke="#e5484d"/></g>
<circle cx="470" cy="120" r="4" fill="#2563eb"/><circle cx="560" cy="120" r="4" fill="#2ea043"/><circle cx="640" cy="120" r="4" fill="#e5484d"/>
<text x="446" y="146" style="font-size:12px;fill:#2563eb">青の焦点</text><text x="534" y="146" style="font-size:12px;fill:#2ea043">緑</text><text x="622" y="146" style="font-size:12px;fill:#e5484d">赤の焦点</text>
<text x="40" y="206" style="font-size:12px">センサーの位置では、色ごとに像の大きさ・位置がずれる → 端で色のにじみ</text>
</svg>

| 種類 | 内容 |
| --- | --- |
| **軸上色収差** | **色ごとにピントの位置が違う**（**ぼけた部分に色のにじみ**） |
| **倍率色収差** | **色ごとに像の倍率が違う**（**画面の端で輪郭が色ずれ**）。**ゲームで再現するのは、主にこれ** |

## 基本の実装

**緑を基準に赤と青を画面中心からの距離に応じて、逆方向にずらしてサンプル**します。

```hlsl
float3 ChromaticAberration(float2 uv, float intensity) {
  float2 center_offset = uv - 0.5;
  float distance_squared = dot(center_offset, center_offset);
  float2 shift = center_offset * distance_squared * intensity;

  float r = scene_color.SampleLevel(linear_clamp, uv + shift, 0).r;
  float g = scene_color.SampleLevel(linear_clamp, uv, 0).g;
  float b = scene_color.SampleLevel(linear_clamp, uv - shift, 0).b;
  return float3(r, g, b);
}
```

| 点 | 説明 |
| --- | --- |
| **`center_offset × distance_squared`** | **中心はほぼ 0、周辺で急に大きく**（**実際のレンズの特性に近い**） |
| **R と B を逆方向** | **緑を基準に赤は外へ青は内へ**（**縁取りの色の順序が現実に近い**） |
| **`intensity`** | <strong>強さ（0.005〜0.02）</strong> |

<!-- fig:chromatic-aberration-compare:begin -->

<svg class="fig illust motion" data-fig="chromatic-aberration-compare" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-chromatic-aberration-compare" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">intensity を上げると、端の縁が赤と青に割れる</text>
<rect x="40" y="70" width="700" height="190" fill="#000000" rx="6"/>
<g style="mix-blend-mode:screen"><rect x="91" y="100" width="18" height="130" fill="#ff0000"><animate attributeName="x" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.1739;0.2609;0.3652;0.4522;0.5217;0.6261;0.7478;0.8174;1.0000" values="91;91;91;85.2;85.2;91;91;73.6;73.6;91;91"/></rect>
<rect x="381.0" y="100" width="18" height="130" fill="#ff0000"/>
<rect x="671" y="100" width="18" height="130" fill="#ff0000"><animate attributeName="x" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.1739;0.2609;0.3652;0.4522;0.5217;0.6261;0.7478;0.8174;1.0000" values="671;671;671;676.8;676.8;671;671;688.4;688.4;671;671"/></rect>
</g>
<g style="mix-blend-mode:screen"><rect x="91" y="100" width="18" height="130" fill="#00ff00"/>
<rect x="381.0" y="100" width="18" height="130" fill="#00ff00"/>
<rect x="671" y="100" width="18" height="130" fill="#00ff00"/>
</g>
<g style="mix-blend-mode:screen"><rect x="91" y="100" width="18" height="130" fill="#0000ff"><animate attributeName="x" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.1739;0.2609;0.3652;0.4522;0.5217;0.6261;0.7478;0.8174;1.0000" values="91;91;91;96.8;96.8;91;91;108.4;108.4;91;91"/></rect>
<rect x="381.0" y="100" width="18" height="130" fill="#0000ff"/>
<rect x="671" y="100" width="18" height="130" fill="#0000ff"><animate attributeName="x" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.1739;0.2609;0.3652;0.4522;0.5217;0.6261;0.7478;0.8174;1.0000" values="671;671;671;665.2;665.2;671;671;653.6;653.6;671;671"/></rect>
</g>
<text x="100" y="282" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">左の端</text>
<text x="390.0" y="282" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">中心</text>
<text x="680" y="282" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">右の端</text>
<text x="40" y="320" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">強さ 0:ずれなし<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2170;0.2174;1.0000" values="1;1;0;0"/></text>
<text x="40" y="320" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">強さ 0.02（ちょうどよい）:端の縁にわずかな色ずれ<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2170;0.2174;0.4083;0.4087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="320" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">強さ 0:ずれなし<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4083;0.4087;0.5736;0.5739;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="320" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">強さ 0.06（やりすぎ）:端で赤と青がはっきり分かれる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;0.7823;0.7826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="320" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">強さ 0:ずれなし<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7823;0.7826;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="346" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ずれの量 ＝ 中心からの距離 × 強さ（中心は、いつもずれない）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:chromatic-aberration-compare:end -->

## 高品質版：多サンプル

**3 チャンネルだけをずらす**と、**縁取りが赤と青の 2 色で、くっきり段になります**。**実際のレンズでは、波長ごとに連続的にずれる**ので、**縁取りが虹のように滑らか**です。

```hlsl
float3 ChromaticAberrationSpectral(float2 uv, float intensity) {
  float2 center_offset = uv - 0.5;
  float distance_squared = dot(center_offset, center_offset);
  float3 sum = 0;
  float3 weight_sum = 0;
  const int kSamples = 8;
  for (int i = 0; i < kSamples; ++i) {
    float t = i / (kSamples - 1.0);
    float2 shift = center_offset * distance_squared * intensity * (t * 2.0 - 1.0);
    float3 wavelength_weight = float3(saturate(1.0 - 2.0 * t), 1.0 - abs(2.0 * t - 1.0), saturate(2.0 * t - 1.0));
    sum += scene_color.SampleLevel(linear_clamp, uv + shift, 0).rgb * wavelength_weight;
    weight_sum += wavelength_weight;
  }
  return sum / weight_sum;
}
```

| 点 | 説明 |
| --- | --- |
| **`t`** | <strong>波長（0 ＝ 青側、1 ＝ 赤側）</strong> |
| **`wavelength_weight`** | **その波長が、RGB のどれに寄与するか**（**簡易的な波長 → 色の変換**） |
| **サンプル数** | **8 程度**。**多いほど虹が滑らか** |
| **正規化** | **重みの合計で割る**（**明るさを保つ**） |

## 使い方

| 設定 | 内容 |
| --- | --- |
| **強さ** | <strong>控えめ（0.005〜0.01）</strong>で、**カメラらしさ**。**強め（0.02〜0.05）で、演出** |
| **範囲** | **画面全体**に**距離の 2 乗**で。**中心はほぼ無効** |
| **向き** | **画面中心から放射状**（**倍率色収差**） |
| **順序** | <strong>トーンマップ後（LDR）</strong>に**かける** |

### 演出での使い方

| 場面 | 使い方 |
| --- | --- |
| **ダメージを受けた** | <strong>一瞬、強い色収差（0.03〜0.05）</strong> → **すぐ戻す** |
| **ワープ・加速** | **強度を速度に比例** |
| **ホラー・幻覚** | <strong>不安定に揺らす（時間でノイズ）</strong> |
| **グリッチ** | **横方向だけ、大きくずらす** |
| **サイバーパンク** | **常時、控えめにかける** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **距離の 2 乗でずらす** | <strong>中心がくっきり、端でにじむ（自然）</strong> |
| **多サンプルで虹のように** | <strong>高品質（コストに余裕があれば）</strong> |
| **LDR でトーンマップ後に** | **見た目の色にかける** |
| **他のパスと統合** | **ビネット・グレイン・トーンマップと 1 パス** |
| **オプションで切れる／強さ調整** | **酔いやすい人・アクセシビリティ** |
| **UI の前に** | **文字が色ずれしない** |

## よくあるミス

??? failure "強くしすぎて、画面が溶けて見え、酔う"
    **0.005〜0.02**。**オプションで調整**できるように。

??? failure "画面中心まで色がずれて、全体がぼやける"
    **距離の 2 乗**をかけ、**中心は 0 に近く**する。

??? failure "UI の文字まで色ずれして、読みにくい"
    **UI は色収差の後に描く**。

??? failure "縁取りが赤と青の 2 色だけで、安っぽい"
    **多サンプル（スペクトル）版**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 色収差 ＝ <strong>波長ごとに屈折が違い、画面の端で赤・緑・青がずれる</strong>
    - [x] 実装 ＝ <strong>緑を基準に、赤・青を中心から逆方向へずらす</strong>。<strong>距離の 2 乗</strong>
    - [x] <strong>多サンプル（波長）</strong>で<strong>虹のように滑らか</strong>
    - [x] <strong>控えめに（0.005〜0.02）</strong>。<strong>演出では一時的に強く</strong>
    - [x] <strong>表現の好み</strong>。<strong>設定で切れるように</strong>

## 参考

- Wikipedia, "Chromatic aberration"
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Pharr, Jakob, Humphreys, "Physically Based Rendering"（レンズのモデル）

## 関連ページ

- [Lens Effects](index.md)
- [Vignette](vignette.md)
- [Film Grain](film-grain.md)
- [被写界深度](../dof/index.md)

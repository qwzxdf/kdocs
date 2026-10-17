---
title: ビネット
tags:
  - 描画
---

# ビネット

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

| 原因 | 内容 |
| --- | --- |
| <strong>cos⁴ の法則（自然なビネット）</strong> | **角度 θ が大きいほど、光が 4 乗で弱まる** |
| **機械的ビネット** | **レンズ鏡筒・フィルター・絞りが斜めの光を遮る** |
| **光学的ビネット** | **レンズ内部の絞りが斜めの光を通しにくい** |

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

| 点 | 説明 |
| --- | --- |
| **`d = (uv − 0.5) × 2`** | **画面中心を原点に±1 の座標**（**角で約 1.4**） |
| **`length(d)`** | **画面中心からの距離** |
| **`smoothstep`** | **暗くなり始める距離〜暗くなりきる距離を、滑らかに** |
| **`intensity`** | <strong>周辺の暗さの強さ（0〜1）</strong> |
| **`smoothness`** | **暗さの移り変わりの幅** |
| **`roundness`** | **アスペクト比の補正**。**1 で画面の縦横比に沿った楕円、画面の高さで円なら調整** |

<!-- fig:vignette-params:begin -->
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

| 点 | 説明 |
| --- | --- |
| **`tan(fov/2)`** | **画面の端に対応する、視線の傾き** |
| **`cos θ = 1 / √(1 + tan²)`** | **視線の角度の余弦** |
| **`cos⁴`** | **物理的なビネットの係数** |

**広角（視野角が大きい）ほど、周辺が暗くなる**ことが**自然**に**再現**されます。

## 形

| 形 | 内容 |
| --- | --- |
| **円形** | **`roundness`＝ 画面のアスペクト比で、真円** |
| <strong>楕円（画面に沿う）</strong> | **`roundness` ＝ 1 で、画面の縦横比に沿った楕円** |
| **四角寄り** | **距離に最大ノルム（`max(|x|, |y|)`）を使う**（**画面の四隅だけをほんのり暗く**） |

```hlsl
float BoxVignette(float2 uv, float intensity, float smoothness) {
  float2 d = abs(uv - 0.5) * 2.0;
  float distance_from_center = max(d.x, d.y);
  return 1.0 - smoothstep(1.0 - intensity - smoothness, 1.0, distance_from_center) * intensity;
}
```

## 色付きのビネット

**黒だけでなく、色を付ける**と**演出**になります。

| 色 | 演出 |
| --- | --- |
| **暗い赤** | **体力が少ない・ダメージ・危険** |
| **暗い青** | **水中・夜・冷たさ** |
| **暗い緑** | **毒・ナイト ビジョン** |
| <strong>白（明るい縁）</strong> | **夢・回想・眩しさ** |

```hlsl
float3 ColoredVignette(float3 color, float2 uv, float3 vignette_color) {
  float v = 1.0 - Vignette(uv, kVignetteIntensity, kVignetteSmoothness, kRoundness);
  return lerp(color, vignette_color, v);
}
```

## ゲームでの使い方

| 場面 | 使い方 |
| --- | --- |
| **映画風の常時** | <strong>ごく弱く（0.2〜0.3）</strong> |
| **夜・洞窟** | **強め**（**懐中電灯の円のような**） |
| **体力が低い** | **赤いビネットを体力に応じて濃く** |
| **狙い・ズーム** | <strong>スコープ中は強いビネット（円）</strong> |
| **会話・カットシーン** | **視線を中心に集める** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **`smoothstep` で滑らかに** | **境が見えない** |
| **アスペクト比を補正** | **ウルトラワイドでも形が崩れない** |
| **物理的な cos⁴** | **視野角に応じた、自然な暗さ** |
| **色付きにして演出に使う** | **体力・状態** |
| **トーンマップ後（LDR）で乗算** | **見た目の明るさに直接** |
| **他のパスと統合** | **色収差・グレイン・トーンマップと 1 パス** |
| **オプションで切れる** | **プレイしにくい人のため** |

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

- [レンズ効果](index.md)
- [色収差](chromatic-aberration.md)
- [フィルム グレイン](film-grain.md)
- [カラー グレーディング](../color-grading/index.md)

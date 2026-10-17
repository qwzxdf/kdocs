---
title: ポスタライズとハーフトーン
tags:
  - 描画
---

# ポスタライズとハーフトーン

**ポスタライズ**は、**色の段階（階調）を減らして、ポスターのように平らな色の面にする**表現です。**ハーフトーンは、網点（ドット）の大きさで濃淡を表す、漫画・印刷のような表現**です。**どちらも、3D の絵を「イラスト・漫画・印刷物」の質感に近づける**ための**後処理**で、**セル シェーディングや輪郭線と組み合わせて、画風を作ります**。**写実的な品質とは別の軸の、好みの表現**です。このページでは、**ポスタライズの式・色数・ディザリングとの組み合わせ・ハーフトーンの網点・クロスハッチ（線の濃淡）・使いどころ**を説明します。

!!! tip "ポイント"
    - ポスタライズ ＝ <strong>各チャンネルを、N 段階に丸める</strong>（<strong>`floor(c × N) / N`</strong>）。<strong>色の面が平らに</strong>。
    - <strong>輝度だけを丸める</strong>と<strong>色相を保てる</strong>。
    - <strong>ハーフトーン</strong> ＝ <strong>明るさに応じた大きさの円（網点）</strong>を、<strong>格子状に並べる</strong>。<strong>角度を付ける</strong>と<strong>漫画風</strong>。
    - <strong>クロスハッチ</strong> ＝ <strong>線の本数で濃淡</strong>（<strong>ペン画・版画風</strong>）。
    - <strong>丸めの境は、ちらつきやすい</strong>。<strong>TAA・ディザリングで抑える</strong>。
    - <strong>どれも画風の選択</strong>。<strong>写実的な絵を良くする技法ではない</strong>。

## ポスタライズ

**色の連続的な階調**を**少ない段階に丸めます**。

<div class="formula">c' = floor( c × N ) / N　（N：段階数）</div>

```hlsl
float3 Posterize(float3 color, float levels) {
  return floor(color * levels + 0.5) / levels;
}
```

| 段階数 N | 見た目 |
| --- | --- |
| **2** | **白黒・極端なポスター** |
| **4〜6** | **ポスター・グラフィック的** |
| **8〜16** | <strong>控えめ（バンディングが目立ち始める）</strong> |

<svg class="fig illust" viewBox="0 0 780 210" role="img" aria-label="ポスタライズ">
<text x="20" y="26" class="fig-title">滑らかなグラデーションを、数段階の面に</text>
<defs><linearGradient id="ph-g" x1="0" x2="1"><stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#fde68a"/></linearGradient></defs>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:12px">元（滑らか）</text><rect x="0" y="0" width="680" height="30" fill="url(#ph-g)"/>
<text x="0" y="52" style="font-size:12px">4 段階</text>
<g><rect x="0" y="60" width="170" height="30" fill="#1e293b"/><rect x="170" y="60" width="170" height="30" fill="#5b5361"/><rect x="340" y="60" width="170" height="30" fill="#b09c78"/><rect x="510" y="60" width="170" height="30" fill="#fde68a"/></g>
<text x="0" y="112" style="font-size:12px">2 段階</text>
<g><rect x="0" y="120" width="340" height="30" fill="#1e293b"/><rect x="340" y="120" width="340" height="30" fill="#fde68a"/></g>
</g>
</svg>

### 輝度だけ丸める

**RGB 別々に丸めると、色相がずれます**（**例：茶色が緑や赤に分かれる**）。**輝度だけを丸め、色の比率を保つ**方が**色の自然さが保たれます**。

```hlsl
float3 PosterizeLuma(float3 color, float levels) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float quantized = floor(luma * levels + 0.5) / levels;
  return color * (quantized / max(luma, 1e-4));
}
```

| 方式 | 見た目 |
| --- | --- |
| **RGB 別々** | **カラフルでグラフィック的**（**色がずれる**） |
| **輝度だけ** | **色味は保ち、陰影だけ段階化**（**セル シェーディングに近い**） |

## ディザリングと組み合わせる

**丸めるだけだと段の境がくっきりします**。**丸める前にノイズやパターン（ディザ）を足す**と**境が模様のように混ざります**（**古いゲーム機・版画風**）。

```hlsl
float3 PosterizeDithered(float3 color, float levels, float2 pixel_position) {
  float dither = Bayer4x4(pixel_position) - 0.5;
  return floor(color * levels + 0.5 + dither) / levels;
}
```

| ディザ | 見た目 |
| --- | --- |
| <strong>ベイヤー（規則的）</strong> | **レトロ・格子状の模様** |
| **ブルー ノイズ** | **自然な粒状** |
| **なし** | **平らな色の面** |

## ハーフトーン（網点）

**印刷・漫画の網点**は**明るさに応じた大きさの円を、格子状に並べて濃淡を表します**。

| 要素 | 内容 |
| --- | --- |
| **格子** | **等間隔の点の配置**（**傾けると漫画風**） |
| **点の大きさ** | **暗いほど大きく、明るいほど小さい** |
| **角度** | **45°（白黒）が標準**。**カラーは色ごとに別の角度**（**CMYK の網点**） |

```hlsl
float Halftone(float2 pixel_position, float luminance, float cell_size, float angle) {
  float s = sin(angle);
  float c = cos(angle);
  float2 rotated = float2(c * pixel_position.x - s * pixel_position.y, s * pixel_position.x + c * pixel_position.y);
  float2 cell = frac(rotated / cell_size) - 0.5;
  float distance_from_center = length(cell);
  float radius = sqrt(1.0 - luminance) * 0.7;
  return smoothstep(radius + 0.05, radius - 0.05, distance_from_center);
}
```

| 点 | 説明 |
| --- | --- |
| **`rotated / cell_size`** | **傾けた格子のセル座標** |
| **`frac − 0.5`** | **セルの中心を原点に** |
| **`radius = √(1 − 輝度) × 0.7`** | **暗いほど、円が大きい**（**面積が明るさに比例するよう√**） |
| **`smoothstep`** | <strong>円の縁を少しぼかす（ジャギー防止）</strong> |

<!-- fig:halftone-dots:begin -->
<!-- fig:halftone-dots:end -->

### カラーのハーフトーン

**CMYK の 4 色**を**別々の角度**で**重ねる**と、**印刷物のような、カラーの網点**になります。

| インク | 角度 |
| --- | --- |
| <strong>C（シアン）</strong> | **15°** |
| <strong>M（マゼンタ）</strong> | **75°** |
| <strong>Y（イエロー）</strong> | **0°** |
| <strong>K（黒）</strong> | **45°** |

**角度をずらす**ことで**モアレ（干渉縞）を避けます**。

## クロスハッチ（線の濃淡）

**線の本数と向きで濃淡**を**表す**のが**クロスハッチ**で、<strong>ペン画・版画・ゲーム「オブラ・ディン号の帰還」</strong>の**ような絵**になります。

| 明るさ | 線 |
| --- | --- |
| **明るい** | <strong>線なし（白）</strong> |
| **やや暗い** | **斜線 1 方向** |
| **暗い** | <strong>斜線 2 方向（交差）</strong> |
| **とても暗い** | **さらに別の方向を重ねる** |

```hlsl
float Hatch(float2 pixel_position, float luminance) {
  float2 p = pixel_position / kHatchSpacing;
  float line1 = step(0.5, frac(p.x + p.y)) * step(luminance, 0.8);
  float line2 = step(0.5, frac(p.x - p.y)) * step(luminance, 0.55);
  float line3 = step(0.5, frac(p.x)) * step(luminance, 0.3);
  return 1.0 - max(line1, max(line2, line3));
}
```

**画面に固定した網点・線**は<strong>カメラが動くと、「画面に張り付いた模様」</strong>に**見えます**（**シャワー ドア効果**）。**物体の表面（UV やワールド座標）に貼る**と**物体と一緒に動いて自然**です（**トゥーン レンダリングの手法の 1 つ**）。

## 使いどころ

| 表現 | 使い方 |
| --- | --- |
| **ポスタライズ** | **グラフィック ノベル・ポスター風・夢のシーン・回想** |
| **ハーフトーン** | **漫画風・印刷物風・コミック調のゲーム** |
| **クロスハッチ** | **ペン画・版画・ノワール** |
| **ディザ付きポスタライズ** | **古いゲーム機風・レトロ・Pixel Art 風** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **輝度だけ丸める** | **色相が保たれる** |
| **ディザで段の境を混ぜる** | **レトロ・版画風** |
| **網点・線を物体表面に貼る** | **画面に張り付いて見える違和感を避ける** |
| **TAA と相性に注意** | **細かい網点は、TAA でぼけ・モアレ** |
| **強さを時間で切り替える** | **回想・特殊状態** |
| **輪郭線・セルと組み合わせる** | **統一した画風に** |

## よくあるミス

??? failure "RGB 別々にポスタライズして、色相がずれる"
    **輝度だけを丸める**。

??? failure "網点が、画面に張り付いて見える"
    **物体表面（UV・ワールド）に貼る**。

??? failure "細かい網点が、モアレになる"
    **セルの大きさを大きく**、**解像度に合わせる**、**TAA の影響を確認**。

??? failure "段の境がちらつく"
    **丸める前に軽くぼかす**、**TAA**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ポスタライズ ＝ <strong>色の階調を N 段階に丸める</strong>。<strong>輝度だけ丸めると色相を保てる</strong>
    - [x] <strong>ディザ</strong>と組み合わせて<strong>レトロ・版画風</strong>
    - [x] ハーフトーン ＝ <strong>明るさに応じた大きさの網点を、傾けた格子に並べる</strong>
    - [x] <strong>クロスハッチ</strong> ＝ <strong>線の本数で濃淡</strong>
    - [x] <strong>画面固定の模様に注意</strong>。<strong>画風の選択</strong>（<strong>好みの問題</strong>）

## 参考

- Praun et al., "Real-Time Hatching"（SIGGRAPH 2001）
- Lake et al., "Stylized Rendering Techniques for Scalable Real-Time 3D Animation"（NPAR 2000）
- Pope, "Return of the Obra Dinn" 開発日誌（TIGSource, ディザリングの解説）

## 関連ページ

- [輪郭線・トゥーン](index.md)
- [セル シェーディング](cel-shading.md)
- [背面法の輪郭線](outline-hull.md)
- [フィルム グレイン](../lens-effects/film-grain.md)

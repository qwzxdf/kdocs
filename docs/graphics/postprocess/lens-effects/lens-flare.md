---
title: レンズ フレア
tags:
  - 描画
---

# レンズ フレア

**太陽やライトのような、とても明るい光源がレンズに入る**と、<strong>レンズの内部で光が何度も反射し、画面に「ゴースト（光の円）」「ハロー（輪）」「光芒（スターバースト）」</strong>が**現れます**。**これがレンズ フレア**で、**SF・映画・夕暮れの太陽**の**演出**に**欠かせません**。**表現の好みの問題**で**あれば高品質というわけではありません**。このページでは、**フレアの種類・画面空間でのゴースト生成・ハロー・光芒（スターバースト）・色と減衰・コストとオクルージョン**を説明します。

!!! tip "ポイント"
    - レンズ フレア ＝ <strong>レンズ内の反射で、強い光源から出る、ゴースト・ハロー・光芒</strong>。
    - <strong>ゴースト</strong> ＝ <strong>光源を、画面中心を挟んで反対側に、複数の円として並べる</strong>。
    - <strong>画面空間の方法</strong>：<strong>ブルームの明るい部分を取り出し、反転・ずらしてサンプル</strong>する（<strong>光源の位置を知らなくてよい</strong>）。
    - <strong>ハロー</strong> ＝ <strong>画面中心を軸にした、大きな輪</strong>。<strong>光芒</strong> ＝ <strong>絞りの羽根による筋</strong>。
    - <strong>画面端のゴーストは弱める</strong>。<strong>色収差を付ける</strong>と<strong>虹色でリアル</strong>。
    - <strong>光源が隠れたら消える</strong>よう、<strong>オクルージョン</strong>を考慮する。

## 要素

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="レンズ フレアの要素">
<text x="20" y="26" class="fig-title">フレアの要素：ゴーストは、画面中心を挟んで反対側に並ぶ</text>
<g transform="translate(40,52)">
<rect x="0" y="0" width="460" height="170" fill="#0f172a"/>
<circle cx="380" cy="40" r="16" fill="#fff7d1"/><text x="350" y="76" style="font-size:12px;fill:#fff">光源</text>
<line x1="380" y1="40" x2="80" y2="130" stroke="#fff" stroke-opacity="0.3" stroke-dasharray="4 3"/>
<circle cx="230" cy="85" r="4" fill="#fff"/>
<circle cx="300" cy="64" r="12" fill="#5fa8ff" fill-opacity="0.45"/><circle cx="215" cy="90" r="18" fill="#ffd27a" fill-opacity="0.4"/><circle cx="150" cy="108" r="26" fill="#ff8aa0" fill-opacity="0.3"/><circle cx="90" cy="125" r="14" fill="#8affc1" fill-opacity="0.4"/>
<circle cx="230" cy="85" r="85" fill="none" stroke="#fff" stroke-opacity="0.25" stroke-width="6"/>
<text x="6" y="164" style="font-size:12px;fill:#fff">画面中心（白い点）を軸に、反対側にゴースト</text>
</g>
<g font-size="13"><text x="530" y="90" style="font-weight:700">要素</text>
<text x="530" y="116">ゴースト：光源の像の円</text>
<text x="530" y="140">ハロー：中心を囲む輪</text>
<text x="530" y="164">光芒：光源から伸びる筋</text>
<text x="530" y="188">ストリーク：横に伸びる光</text></g>
</svg>

| 要素 | 内容 | 原因 |
| --- | --- | --- |
| **ゴースト** | **光源の像が画面中心を挟んで反対側に、複数の円として現れる** | **レンズ面での多重反射** |
| **ハロー** | **画面中心を中心にした、大きな輪** | **レンズ構成の光学的な効果** |
| <strong>光芒（スターバースト）</strong> | **光源から放射状に伸びる筋**（**羽根の数 × 2 本**など） | **絞りの羽根による回折** |
| **ストリーク** | **横に長く伸びる光** | **アナモルフィック レンズ**（**映画的**） |

## 画面空間のゴースト

**ブルームで明るい部分を取り出した画像**から、**反転した位置を複数回サンプルして、ゴーストを作る**方法です（**光源の位置を別に知る必要がありません**）。

```hlsl
float3 LensFlareGhosts(float2 uv, int ghost_count, float dispersal, float distortion) {
  float2 flipped_uv = 1.0 - uv;
  float2 ghost_vector = (0.5 - flipped_uv) * dispersal;

  float3 result = 0.0;
  [loop] for (int i = 0; i < ghost_count; ++i) {
    float2 offset = frac(flipped_uv + ghost_vector * float(i));
    float weight = length(0.5 - offset) / length(float2(0.5, 0.5));
    weight = pow(1.0 - weight, 10.0);
    result += bright_texture.SampleLevel(linear_clamp, offset, 0).rgb * weight;
  }
  return result;
}
```

| 点 | 説明 |
| --- | --- |
| **`flipped_uv = 1 − uv`** | **画面中心に対して、反転した位置** |
| **`ghost_vector`** | **反転位置から画面中心へ向かうベクトル**。**`dispersal` で間隔を調整** |
| **`weight`** | **画面の端のゴーストを弱める**（**中心付近が強い**） |
| **`bright_texture`** | **ブルームの明るい部分の抽出画像**（**半解像度**） |
| **`frac`** | **画面の外へ出たら、反対側に折り返す** |

<!-- fig:lens-flare-ghosts:begin -->

<svg class="fig illust motion" data-fig="lens-flare-ghosts" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lens-flare-ghosts" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="lf-clip"><rect x="40" y="60" width="700" height="300" rx="6"/>
</clipPath>
<filter id="lf-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5"/>
</filter>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">画面空間のゴースト:光源の像が、画面の中心を通る線上に並ぶ</text>
<rect x="40" y="60" width="700" height="300" fill="#0b1224" rx="6"/>
<circle cx="390.0" cy="210.0" r="4" fill="#64748b"/>
<text x="398.0" y="202.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">画面の中心</text>
<line x1="130" y1="120" x2="650.0" y2="300.0" stroke="#334155" stroke-width="1.5" stroke-dasharray="4 4"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="130;130;340;600;660;660"/><animate attributeName="y1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="120;120;180;150;290;290"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="650;650;440;180;120;120"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="300;300;240;270;130;130"/></line>
<circle cx="130" cy="120" r="14" fill="#fff7d6" filter="url(#lf-glow)"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="130;130;340;600;660;660"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="120;120;180;150;290;290"/></circle>
<circle cx="130" cy="120" r="6" fill="#ffffff"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="130;130;340;600;660;660"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="120;120;180;150;290;290"/></circle>
<circle cx="234.0" cy="156.0" r="24" fill="none" stroke="#7dd3fc" stroke-width="4" opacity="0.8" clip-path="url(#lf-clip)"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="234;234;360;516;552;552"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="156;156;192;174;258;258"/></circle>
<circle cx="481.0" cy="241.5" r="40" fill="none" stroke="#fbbf24" stroke-width="4" opacity="0.8" clip-path="url(#lf-clip)"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="481;481;407.5;316.5;295.5;295.5"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="241.5;241.5;220.5;231;182;182"/></circle>
<circle cx="572.0" cy="273.0" r="18" fill="none" stroke="#a78bfa" stroke-width="4" opacity="0.8" clip-path="url(#lf-clip)"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="572;572;425;243;201;201"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="273;273;231;252;154;154"/></circle>
<circle cx="754.0" cy="336.0" r="32" fill="none" stroke="#86efac" stroke-width="4" opacity="0.8" clip-path="url(#lf-clip)"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="754;754;460;96;12;12"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="336;336;252;294;98;98"/></circle>
<circle cx="910.0" cy="390.0" r="14" fill="none" stroke="#f472b6" stroke-width="4" opacity="0.8" clip-path="url(#lf-clip)"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="910;910;490;-30;-150;-150"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2800;0.5200;0.8000;1.0000" values="390;390;270;330;50;50"/></circle>
<text x="40" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ゴースト位置 ＝ 中心 − (光源 − 中心) × 係数。係数がマイナスなら光源側、プラスなら反対側にできる。<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:lens-flare-ghosts:end -->

## ハロー

**画面中心を中心にした、大きな輪**を**足し**ます。**反転位置から、中心方向へ一定の長さだけ進んだ位置をサンプル**します。

```hlsl
float3 LensFlareHalo(float2 uv, float halo_width) {
  float2 flipped_uv = 1.0 - uv;
  float2 direction = normalize(0.5 - flipped_uv);
  float2 halo_vector = direction * halo_width;
  float weight = length(0.5 - frac(flipped_uv + halo_vector)) / length(float2(0.5, 0.5));
  weight = pow(1.0 - weight, 5.0);
  return bright_texture.SampleLevel(linear_clamp, flipped_uv + halo_vector, 0).rgb * weight;
}
```

| 点 | 説明 |
| --- | --- |
| **`halo_width`** | **輪の半径**（**0.4〜0.6 程度**） |
| **向きを正規化** | **どの画素でも同じ長さ**（**輪になる**） |

## 色と色収差

<strong>ゴーストやハローに色（虹色）</strong>を**付ける**と**リアルになります**。

| 方法 | 内容 |
| --- | --- |
| **ゴーストごとに色を変える** | **1 つ目は青、2 つ目は橙…** |
| **色収差を付ける** | **R・G・B を少しずつずらしてサンプル**（[色収差](chromatic-aberration.md)） |
| **グラデーション テクスチャ** | **画面中心からの距離で色を引く 1D テクスチャ** |

```hlsl
float3 flare_color = color_gradient.SampleLevel(linear_clamp, float2(length(0.5 - offset) / 0.707, 0.5), 0).rgb;
result += bright * weight * flare_color;
```

## 光芒（スターバースト）

**絞りの羽根の数に応じた、星形の筋**です。**テクスチャを光源の位置に貼る**のが**簡単**です。

| 方法 | 内容 |
| --- | --- |
| **スターバースト テクスチャ** | **星形のテクスチャを画面中心からの角度で回して、ブルームに乗算** |
| **ダート テクスチャ** | **レンズの汚れ・傷のテクスチャを画面全体に重ね、ブルームの強さに乗算**（[合成と強さ](../bloom/composite.md)） |
| **光源位置にスプライト** | **光源の位置を投影して、スプライトを描く** |

```hlsl
float3 Starburst(float2 uv, float2 light_uv, Texture2D starburst_texture, float intensity) {
  float2 d = uv - light_uv;
  float angle = atan2(d.y, d.x);
  float2 star_uv = float2(angle / 6.28318530718 + 0.5, 0.5);
  return starburst_texture.SampleLevel(linear_wrap, star_uv, 0).rgb * intensity;
}
```

## 光源が隠れたとき

**太陽が建物に隠れたのに、フレアが残る**と**不自然**です。<strong>光源の可視性（オクルージョン）</strong>を**考慮**します。

| 方式 | 内容 |
| --- | --- |
| **画面空間（ブルーム抽出）なら自動** | **隠れた光源は画面で明るくない → フレアも出ない** |
| **光源位置にスプライトを描く場合** | **光源位置の深度で可視性を判定**（**オクルージョン クエリ・深度の読み取り**） |
| **画面外の光源** | **画面の外の太陽は、画面空間では抽出できない**。**別途（光源位置から）スプライト** |
| **可視性のフェード** | **見える面積の割合で強さを滑らかに** |

## コスト

| 項目 | 目安 |
| --- | --- |
| **ブルームの抽出画像を再利用** | **追加の抽出は不要** |
| **ゴースト ＋ ハロー** | **半解像度でサンプル 5〜10 回 → 軽い** |
| **スターバースト・ダート** | **テクスチャ 1〜2 枚 → 軽い** |
| **ぼかし** | <strong>ゴーストを少しぼかすと、なめらか（半解像度なら、安い）</strong> |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **ブルームの画像を使い回す** | **別の抽出を避ける** |
| **半解像度で作る** | **コストを 1/4** |
| **端のゴーストを弱める** | **中心付近が強い** |
| **色収差・グラデーション** | **虹色でリアル** |
| **かけすぎない** | **控えめで光源が主役のまま** |
| **光源の可視性を考慮** | **隠れたら消える** |
| **強さを光源の明るさで** | **強い光だけ、フレア** |

## よくあるミス

??? failure "画面端にゴーストが出て、不自然に光る"
    **端の重みを弱める**（`weight = pow(1 − 距離, 10)`）。

??? failure "光源が隠れても、フレアが残る"
    **可視性を考慮**する。**画面空間なら、自動で消える**。

??? failure "画面全体がフレアで真っ白になる"
    **強さ・閾値を下げる**。**明るい光源だけがフレアを出す**。

??? failure "ゴーストがぎざぎざに見える"
    **半解像度のぼかし**を足す、**バイリニアで滑らかに**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レンズ フレア ＝ <strong>強い光源から出る、ゴースト・ハロー・光芒</strong>
    - [x] <strong>画面空間</strong>：<strong>ブルームの明るい部分を、反転・ずらしてサンプル</strong>
    - [x] <strong>ゴーストは、画面中心を挟んで反対側</strong>。<strong>端は弱める</strong>。<strong>色収差で虹色</strong>
    - [x] <strong>光芒・ダート</strong>は<strong>テクスチャ</strong>で
    - [x] <strong>隠れた光源は消える</strong>ように。<strong>控えめに</strong>

## 参考

- Hullin et al., "Physically-Based Real-Time Lens Flare Rendering"（SIGGRAPH 2011）
- Chapman, "Pseudo Lens Flare"（john-chapman-graphics.blogspot.com, 2013）

## 関連ページ

- [レンズ効果](index.md)
- [色収差](chromatic-aberration.md)
- [ブルーム](../bloom/index.md)
- [光の筋](../../atmosphere/god-rays/index.md)

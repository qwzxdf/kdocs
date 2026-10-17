---
title: 光の筋
tags:
  - 描画
---

# 光の筋

**木の葉の隙間や雲の切れ間、窓から差し込む光の柱**を**ゴッド レイ**（光の筋、クレパスキュラー レイ）と呼びます。**空気中の粒が光を散らすため、光が通る道筋が見える**現象です。このページでは、**光の筋の原理・画面空間の放射ぼかし（安い方法）・シャドウ マップを使ったレイマーチ（正確な方法）・メッシュで作る光の柱・使い分け**を説明します。

!!! tip "ポイント"
    - 光の筋 ＝ <strong>空気中の粒が、光の通り道を光らせる</strong>。<strong>影があって初めて見える</strong>。
    - <strong>放射ぼかし</strong>：<strong>画面上で光源から外向きに明るさを引き伸ばす</strong>。<strong>安く簡単。光源が画面内にあるときだけ</strong>。
    - <strong>レイマーチ</strong>：<strong>視線に沿って歩き、各点でシャドウ マップを引く</strong>。<strong>正確。ボリューメトリック フォグの一種</strong>。
    - <strong>メッシュ</strong>：<strong>光の柱の形の半透明メッシュ</strong>を<strong>加算</strong>で描く。<strong>固定の光源向き</strong>。
    - <strong>ジッターと時間蓄積</strong>で<strong>少ないステップでも縞が出ない</strong>。
    - <strong>太陽の方向を見ると強く</strong>見える（<strong>前方散乱</strong>）。

## 光の筋が見える理由

**光は空気中を通っても何もなければ見えません**。**粒（ほこり・水蒸気）があると光が散らされて、視線の方向に光が飛んできます**。**途中に影を作る物があると、影の部分では光が通らないので、光る部分と暗い部分が筋になります**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="光の筋の原理">
<text x="20" y="24" class="fig-title">遮る物があるから、光の部分と暗い部分の「筋」ができる</text>
<circle cx="120" cy="50" r="16" fill="#e5aa28"/><text x="100" y="86" style="font-size:12px">太陽</text>
<g stroke="#e5aa28" stroke-width="2"><line x1="120" y1="66" x2="210" y2="170"/><line x1="130" y1="64" x2="300" y2="170"/><line x1="140" y1="62" x2="400" y2="170"/><line x1="150" y1="60" x2="500" y2="170"/><line x1="160" y1="58" x2="600" y2="170"/></g>
<rect x="190" y="106" width="40" height="40" fill="#555"/><rect x="330" y="96" width="40" height="40" fill="#555"/>
<text x="196" y="130" style="font-size:11px;fill:#fff">遮る物</text>
<g fill="#e5aa28" fill-opacity="0.22"><polygon points="230,146 330,170 280,170 235,155"/><polygon points="370,136 470,170 410,170 370,142"/></g>
<line x1="40" y1="170" x2="740" y2="170" stroke="currentColor" stroke-opacity="0.5" stroke-width="2"/>
<circle cx="680" cy="150" r="6" fill="#e5484d"/><text x="640" y="190" style="font-size:12px">カメラ</text>
<text x="360" y="220" style="font-size:12px">暗い帯：遮られた所（光が通らない）　明るい帯：光が通る所</text>
</svg>

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

| 点 | 説明 |
| --- | --- |
| **`occlusion_texture`** | **空の明るい部分だけが残り、物は黒**の画像（深度から作る） |
| **`decay`** | **0.95〜0.99**。**光源から遠いほど弱くする** |
| **`density`** | **ぼかしの長さ**（0.5〜1.0） |
| **サンプル数** | **32〜100**。**半解像度で描く**と**軽い** |
| **欠点** | **太陽が画面の外だと使えない**。**太陽の向きを見ていないと、筋が消える**。**空気の濃さ・影の奥行きは表現できない** |

**太陽が画面外のときにも自然にするため**、**太陽が画面に近いほど強く、離れると弱くする**フェードを**付けます**。

## シャドウ マップでレイマーチ

**正確な方法**は**視線に沿ってサンプル点を歩き、各点が日向か日陰かをシャドウ マップで判定して、日向の点の寄与を足す**ことです。**ボリューメトリック フォグ（[ボリューメトリック フォグ](volumetric-fog.md)）と同じ原理**です。

```hlsl
float3 VolumetricGodRays(float3 camera_pos, float3 pixel_world_pos, float2 pixel_coord) {
  float3 ray = pixel_world_pos - camera_pos;
  float ray_length = min(length(ray), kMaxDistance);
  float3 ray_dir = normalize(ray);

  float step_length = ray_length / kStepCount;
  float jitter = InterleavedGradientNoise(pixel_coord);
  float cos_theta = dot(ray_dir, -sun_direction);
  float phase = HenyeyGreenstein(cos_theta, 0.7);

  float3 accumulated = 0;
  for (int i = 0; i < kStepCount; ++i) {
    float3 p = camera_pos + ray_dir * (i + jitter) * step_length;
    float shadow = SampleCascadeShadow(p);
    float height_density = fog_density * exp(-height_falloff * (p.y - fog_base));
    accumulated += shadow * height_density * phase * step_length;
  }
  return accumulated * sun_color;
}
```

| 点 | 説明 |
| --- | --- |
| **ステップ数** | **16〜64 回**。**少ないとジッターのノイズ**が出る |
| **ジッター** | **開始位置をずらして縞を消す**（ブルー ノイズ。**時間蓄積で平均**） |
| **`phase`** | **太陽の方を見ると光が強い**（前方散乱） |
| **密度** | **一様な霧、または高さフォグ**。**ノイズで濃淡**を付けると、**揺らぐ光の筋** |
| **範囲** | **カメラ近くだけ**で十分（**遠くは距離フォグ**） |
| **半解像度で描く** | **ぼかし＋アップサンプリング**で**軽く** |

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="レイマーチの光の筋">
<text x="20" y="24" class="fig-title">視線上の各点が、日向か日陰かを数える</text>
<polygon points="260,70 400,70 420,190 240,190" fill="#555" fill-opacity="0.35" stroke="#555"/>
<text x="290" y="150" style="font-size:12px">影の領域</text>
<circle cx="80" cy="200" r="6" fill="#e5484d"/><text x="50" y="224" style="font-size:12px">カメラ</text>
<line x1="80" y1="200" x2="700" y2="90" stroke="currentColor" stroke-width="2"/>
<g><circle cx="160" cy="186" r="4" fill="#e5aa28"/><circle cx="240" cy="172" r="4" fill="#e5aa28"/><circle cx="320" cy="158" r="4" fill="#555"/><circle cx="400" cy="144" r="4" fill="#555"/><circle cx="480" cy="130" r="4" fill="#e5aa28"/><circle cx="560" cy="116" r="4" fill="#e5aa28"/><circle cx="640" cy="102" r="4" fill="#e5aa28"/></g>
<text x="440" y="210" style="font-size:12px;fill:#e5aa28">黄 ＝ 日向（光が足される）</text>
<text x="440" y="228" style="font-size:12px">灰 ＝ 日陰（足されない）</text>
</svg>

## ボリュームを使う方法

**ボリューメトリック フォグ**（[ボリューメトリック フォグ](volumetric-fog.md)）を**使っていれば、光の筋は自動で出ます**。**froxel に太陽光とシャドウを注入**しているため、**影による筋が自然に現れます**。**別途レイマーチを用意する必要はありません**。

| 状況 | おすすめ |
| --- | --- |
| **ボリューメトリック フォグを使っている** | <strong>それを使う（自動）</strong> |
| **光の筋だけ欲しい** | **シャドウ マップのレイマーチ** |
| **とにかく軽く** | **放射ぼかし** |
| **固定の窓の光** | **メッシュの光の柱** |

## メッシュで光の柱を作る

<strong>固定された光の柱（窓から差す光、洞窟の天井の穴）</strong>は、**半透明メッシュ**で**作れます**。

| 工夫 | 内容 |
| --- | --- |
| **形** | **光が通る形の錐台や箱のメッシュ** |
| **加算ブレンド** | **背景に足して光らせる** |
| **フレネル風の縁** | **視線と面の角度で縁を薄く**（輪郭を消す） |
| **深度フェード** | **床・壁との交差部を薄く**（ハードな線を消す） |
| **ノイズ・流れ** | **テクスチャを流して、ほこりの揺らぎ** |
| **カメラが近づくと薄く** | **近すぎるとフェードアウト** |

```hlsl
float edge_fade = pow(saturate(abs(dot(normal, view_dir))), 2.0);
float depth_fade = saturate((scene_depth - pixel_depth) / fade_distance);
float near_fade = saturate((pixel_depth - near_fade_start) / near_fade_range);
float dust = dust_texture.Sample(linear_wrap, uv + time * 0.02).r;
float alpha = edge_fade * depth_fade * near_fade * (0.7 + 0.3 * dust) * intensity;
return float4(light_color * alpha, 0);
```

## 水中の光の筋

**水中の光の筋**は、**同じ原理**で**コースティクスで揺らぎが付く**のが**特徴**です（[水中の表現](../water/underwater.md)）。

## 見た目の調整

| パラメータ | 影響 |
| --- | --- |
| **霧の密度** | **濃いほど光の筋が強い** |
| **位相関数の g** | **大きいほど、太陽の方向でだけ見える** |
| **光の強さ** | **HDR で強く、ブルームで光らせる** |
| **色** | **朝夕は暖色、昼は白、水中は青緑** |
| **ノイズ・風** | **揺らぎを足す** |
| **カメラが太陽側へ向くとき強く** | **前方散乱** |

## よくあるミス

??? failure "光の筋が一面にべったり出て、筋に見えない"
    **影（シャドウ マップ）が反映されていない**。**日向と日陰の差**が**筋**になる。

??? failure "放射ぼかしの筋が、太陽が画面外になると急に消える"
    **画面外でもフェードで滑らかに**弱める。**またはレイマーチに切り替える**。

??? failure "レイマーチで縞模様（バンディング）が出る"
    **ジッターと時間蓄積**を入れる。**ステップ数を増やす**。

??? failure "光の柱メッシュの輪郭がはっきり見えて、安っぽい"
    **縁のフェード・深度フェード・ノイズ**を加える。

??? failure "光の筋の計算が重い"
    **半解像度で描き、アップサンプル**する。**範囲を近距離に限定**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 光の筋 ＝ <strong>空気中の粒が光の通り道を光らせる</strong>。<strong>影があって初めて筋になる</strong>
    - [x] <strong>放射ぼかし</strong> ＝ <strong>安い。太陽が画面内のときだけ</strong>
    - [x] <strong>シャドウ マップのレイマーチ</strong> ＝ <strong>正確。ジッター＋時間蓄積</strong>
    - [x] <strong>ボリューメトリック フォグ</strong>があれば<strong>自動で出る</strong>
    - [x] <strong>固定の光の柱</strong>は<strong>加算メッシュ</strong>

## 参考

- Mitchell, "Light Shafts: Rendering Shadows in Participating Media"（GDC 2004）
- Mitchell, "Volumetric Light Scattering as a Post-Process"（GPU Gems 3）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）

## 関連ページ

- [空と大気](index.md)
- [ボリューメトリック フォグ](volumetric-fog.md)
- [雲](clouds.md)
- [水中の表現](../water/underwater.md)
- [影](../shadows/index.md)

---
title: Underwater Fog
tags:
  - 描画
---

# Underwater Fog

水に潜ると遠くの物は見えず近くの物は色が青緑に染まります。空気中の霧と同じように見えますが、違いがあります。空気中の霧は色に関係なく同じ割合で遠くを霞ませます。水は赤をすぐに吸い取り青を遠くまで通します。

<strong>水中の霧は空気中の霧と同じ式で書けますが、吸収の強さが色（RGB）ごとに違います</strong>。このページでは色ごとの減衰（数字つき）、全画面の霧のシェーダー、水の色と深さ光源の色、遠景の扱い濁った水の違いを説明します。

!!! tip "ポイント"
    - 透過率は `T = exp(−σ · d)` で、`σ` は RGB ごとの吸収係数です。赤が先に消えて遠くは青緑になります。
    - `σ = (0.45, 0.07, 0.03)` なら透過率が 5 % になる距離は、赤で約 6.7 m、緑で約 43 m、青で約 100 m です。
    - 距離は深度から求めた視線に沿った距離です。水面の外に出る物では水中を通る分だけを使います。
    - 水の色は深いほど暗くします。太陽光が深さとともに減るからです。
    - 空は水の色で塗ります。水面の向こうは見えません。

!!! info "このページを読む前に"
    - [Underwater Rendering](index.md)（このセクション全体の地図と、読む順番）

## 水中の霧 {#fog}

水中では遠くの物ほど水の色に近づきます。地上のフォグと同じ構造ですが、吸収が色ごとに違います。

<div class="formula">T = exp( −σ · d )　（σ: 吸収係数（RGB）、d: カメラから物までの距離）</div>

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="水中の霧">
<text x="20" y="24" class="fig-title">水中の霧：距離とともに、赤 → 緑 → 青の順に消える</text>
<line x1="80" y1="170" x2="720" y2="170" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="170" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="80,52 160,100 240,132 320,150 400,160 560,167 720,169"/>
<polyline fill="none" stroke="#2ea043" stroke-width="3" points="80,52 160,60 240,70 320,82 400,95 560,120 720,140"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="3" points="80,52 160,55 240,58 320,63 400,69 560,80 720,98"/>
<text x="720" y="192" text-anchor="end" style="font-size:12px">距離 d →</text>
<text x="86" y="44" style="font-size:12px">残る光の割合 T</text>
<text x="170" y="118" style="font-size:12px;fill:#e5484d">赤（すぐ消える）</text>
<text x="420" y="110" style="font-size:12px;fill:#2ea043">緑</text>
<text x="420" y="64" style="font-size:12px;fill:#4c8bf5">青（最後まで残る）</text>
</svg>

水の中は光が吸収と散乱ですぐに減ります。遠くの物が見えず色が青緑に染まる様子は、霧と同じ式で表現できます。

## 色ごとの減衰 {#channels}

水中の霧の式は次のとおりです。

```text
透過率 T = exp(−absorption × distance)               （RGB ごと）
結果 = 元の色 × T + 水の色 × (1 − T)
```

吸収係数 `(0.45, 0.07, 0.03)`（1/m）で計算しました（[Color by Water Depth](../shading/depth-color.md)）。

- 0 m では赤、緑、青とも 100 % で元の色のままです。
- 3 m では赤が 26 %、緑が 81 %、青が 91 % です。赤がほぼ消えます。
- 10 m では赤が 1 %、緑が 50 %、青が 74 % です。青緑に見えます。
- 30 m では赤が 0 %、緑が 12 %、青が 41 % です。暗い青になります。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="距離に対する透過率。赤は急に、緑はゆっくり、青はさらにゆっくり減る"><text x="14" y="22" class="fig-title">距離と透過率（σ = 0.45, 0.07, 0.03）</text>
<line x1="70" y1="190" x2="670" y2="190" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="190" x2="70" y2="40" stroke="currentColor" stroke-width="1.5"/>
<text x="62" y="54" text-anchor="end" style="font-size:12px">1</text><text x="62" y="194" text-anchor="end" style="font-size:12px">0</text><text x="670" y="212" text-anchor="end" style="font-size:12px">距離 d（メートル）0 〜 60</text>
<path d="M70.0,50.0 L80.0,100.7 L90.0,133.1 L100.0,153.7 L110.0,166.9 L120.0,175.2 L130.0,180.6 L140.0,184.0 L150.0,186.2 L160.0,187.6 L170.0,188.4 L180.0,189.0 L190.0,189.4 L200.0,189.6 L210.0,189.7 L220.0,189.8 L230.0,189.9 L240.0,189.9 L250.0,190.0 L260.0,190.0 L270.0,190.0 L280.0,190.0 L290.0,190.0 L300.0,190.0 L310.0,190.0 L320.0,190.0 L330.0,190.0 L340.0,190.0 L350.0,190.0 L360.0,190.0 L370.0,190.0 L380.0,190.0 L390.0,190.0 L400.0,190.0 L410.0,190.0 L420.0,190.0 L430.0,190.0 L440.0,190.0 L450.0,190.0 L460.0,190.0 L470.0,190.0 L480.0,190.0 L490.0,190.0 L500.0,190.0 L510.0,190.0 L520.0,190.0 L530.0,190.0 L540.0,190.0 L550.0,190.0 L560.0,190.0 L570.0,190.0 L580.0,190.0 L590.0,190.0 L600.0,190.0 L610.0,190.0 L620.0,190.0 L630.0,190.0 L640.0,190.0 L650.0,190.0 L660.0,190.0 L670.0,190.0" fill="none" stroke="#e5484d" stroke-width="3.5"/><path d="M70.0,50.0 L80.0,59.5 L90.0,68.3 L100.0,76.5 L110.0,84.2 L120.0,91.3 L130.0,98.0 L140.0,104.2 L150.0,110.0 L160.0,115.4 L170.0,120.5 L180.0,125.2 L190.0,129.6 L200.0,133.6 L210.0,137.5 L220.0,141.0 L230.0,144.3 L240.0,147.4 L250.0,150.3 L260.0,153.0 L270.0,155.5 L280.0,157.8 L290.0,160.0 L300.0,162.0 L310.0,163.9 L320.0,165.7 L330.0,167.3 L340.0,168.8 L350.0,170.3 L360.0,171.6 L370.0,172.9 L380.0,174.0 L390.0,175.1 L400.0,176.1 L410.0,177.0 L420.0,177.9 L430.0,178.7 L440.0,179.5 L450.0,180.2 L460.0,180.9 L470.0,181.5 L480.0,182.1 L490.0,182.6 L500.0,183.1 L510.0,183.6 L520.0,184.0 L530.0,184.4 L540.0,184.8 L550.0,185.1 L560.0,185.5 L570.0,185.8 L580.0,186.1 L590.0,186.3 L600.0,186.6 L610.0,186.8 L620.0,187.0 L630.0,187.2 L640.0,187.4 L650.0,187.6 L660.0,187.7 L670.0,187.9" fill="none" stroke="#3ca05a" stroke-width="3.5"/><path d="M70.0,50.0 L80.0,54.1 L90.0,58.2 L100.0,62.0 L110.0,65.8 L120.0,69.5 L130.0,73.1 L140.0,76.5 L150.0,79.9 L160.0,83.1 L170.0,86.3 L180.0,89.4 L190.0,92.3 L200.0,95.2 L210.0,98.0 L220.0,100.7 L230.0,103.4 L240.0,105.9 L250.0,108.4 L260.0,110.8 L270.0,113.2 L280.0,115.4 L290.0,117.6 L300.0,119.8 L310.0,121.9 L320.0,123.9 L330.0,125.8 L340.0,127.7 L350.0,129.6 L360.0,131.3 L370.0,133.1 L380.0,134.8 L390.0,136.4 L400.0,138.0 L410.0,139.5 L420.0,141.0 L430.0,142.5 L440.0,143.9 L450.0,145.2 L460.0,146.5 L470.0,147.8 L480.0,149.1 L490.0,150.3 L500.0,151.5 L510.0,152.6 L520.0,153.7 L530.0,154.8 L540.0,155.8 L550.0,156.8 L560.0,157.8 L570.0,158.8 L580.0,159.7 L590.0,160.6 L600.0,161.5 L610.0,162.3 L620.0,163.1 L630.0,163.9 L640.0,164.7 L650.0,165.4 L660.0,166.2 L670.0,166.9" fill="none" stroke="#4c8bf5" stroke-width="3.5"/>
<text x="130" y="100" style="font-size:12px;font-weight:600;fill:#e5484d">赤（5 % で約 6.7 m）</text><text x="260" y="120" style="font-size:12px;font-weight:600;fill:#3ca05a">緑（約 43 m）</text><text x="400" y="80" style="font-size:12px;font-weight:600;fill:#4c8bf5">青（約 100 m）</text>
<text x="360" y="246" text-anchor="middle" style="font-size:12px">赤はすぐ消え、青は遠くまで残る。空気中の霧は、3 つの曲線が同じ</text></svg>

透過率が 5 % になる距離は `ln(20) / σ` です。赤で 6.7 m、緑で 42.8 m、青で 99.9 m です。水中で赤い物が数メートルで黒く見えるのは、このためです。空気中の霧の式（[Fog Equations](../../atmosphere/aerial-fog/fog-equation.md)）と形は同じですが、係数が RGB で違います。

## 全画面で適用する {#postprocess}

カメラが水の中にあるとき画面全体に霧をかけます。ポストプロセスで画素ごとの距離（深度バッファから）を使います。

```hlsl
Texture2D<float4> g_scene : register(t0);
Texture2D<float> g_depth : register(t1);              // 視点深度（メートル）。リニアに直したもの
SamplerState g_linear_clamp : register(s0);
SamplerState g_point_clamp : register(s1);

cbuffer UnderwaterFogConstants : register(b0) {
  float4x4 g_inv_view_proj;
  float3 g_camera_position;
  float g_water_surface_y;   // 水面の高さ（ワールド y）
  float3 g_absorption;       // 吸収係数（RGB, 1/m）。例: (0.45, 0.07, 0.03)
  float g_far_depth;         // この値以上の深度は空とみなす（メートル）
  float3 g_deep_color;       // 深い水の色。例: (0.02, 0.1, 0.2)
  float _pad;
};

float4 UnderwaterFogPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float depth = g_depth.SampleLevel(g_point_clamp, uv, 0);
  // 視線方向（ワールド）。遠い面の点を逆変換して作る
  float4 far_w = mul(float4(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0, 1.0, 1.0), g_inv_view_proj);
  float3 ray_dir = normalize(far_w.xyz / far_w.w - g_camera_position);
  // 視点深度 → 視線に沿った距離。視点深度はカメラの前方向の成分なので、1/cosθ を掛ける（簡略化: 画面中央との角度）
  float3 cam_forward = normalize(mul(float4(0, 0, 1, 1), g_inv_view_proj).xyz / mul(float4(0, 0, 1, 1), g_inv_view_proj).w - g_camera_position);
  float distance_to_pixel = depth / max(dot(ray_dir, cam_forward), 0.1);

  // 視線が水面から出るなら、水中を通るのは水面までの距離だけ（水面の外の物に、水中の霧をかけない）
  float t_surface = (ray_dir.y > 1e-4) ? (g_water_surface_y - g_camera_position.y) / ray_dir.y : 1e9;
  float water_distance = min(distance_to_pixel, max(t_surface, 0.0));

  float3 scene = g_scene.SampleLevel(g_linear_clamp, uv, 0).rgb;
  float3 T = exp(-g_absorption * water_distance);                    // RGB ごとの透過率

  // 水の色: カメラの深さに応じて暗くする（太陽光が届かなくなる）
  float camera_depth = max(g_water_surface_y - g_camera_position.y, 0.0);
  float3 sun_at_camera = exp(-g_absorption * camera_depth);
  float3 water_color = g_deep_color * (0.2 + 0.8 * sun_at_camera.b);   // 青の残り具合で明るさを決める

  // 空（深度が最大の画素）は、水の色で塗る。水面の向こうは見えない
  if (depth >= g_far_depth) return float4(water_color, 1.0);
  return float4(scene * T + water_color * (1.0 - T), 1.0);
}
```

`t_surface` は視線が上向きなら水面までの距離です。物が水面より上にあるとき `min` で、水中を通る分だけを使います。水面の外の物には水中の霧が水面より先でかからないようにします。

水面を見上げたときの描画は別に扱います（[The Underside of the Surface and Crossing It](surface-back.md)）。水中の遠い物は距離が大きいほど水の色に近づきます。

### 水の色と深さ

水中の水の色は深くなるほど暗くなります。太陽の光が深さとともに減るためです。`sun_at_camera` はカメラの深さまで届く太陽光の割合で、青が最後まで残るので青の成分で明るさを決めています。水面の近くでは明るい青緑で 10 m で暗い青、50 m でほぼ真っ暗、200 m では太陽光が届かず真っ暗です。吸収係数の青 0.03 なら青の太陽光は、深さ 100 m で 5 % まで減ります。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で、`UnderwaterFogPS` をコンパイルしてエラーが出ないことを確かめました。透過率の数字と曲線は式からの計算（Python）です。深度から距離への変換は簡略化しています。GPU での描画は確認していません。

## 光源の色も変わる {#lights}

水中の物をライティングするとき光が水の中を通ってくる間に吸収されます。

- 太陽光は水面から物までの深さに応じて、赤から消えます。
- 環境光（空の光）も同様に全体に暗く青くなります。
- 水中のライト（懐中電灯、ランプ）は光源から物までの距離に応じて吸収されます。近くでは白く遠くでは青緑になります。

```hlsl
// 太陽光を、水面から物までの深さ d で減衰させる
float3 SunUnderwater(float3 sun_color, float3 absorption, float depth_below_surface) {
  return sun_color * exp(-absorption * depth_below_surface);
}
```

## 水中の遠景の扱い {#far}

遠くの地形や物を描くとき空気中の大気（空気遠近法）は、水中では使いません。水の霧で置き換えます。空気中では大気の霧（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)）、水中ではこのページの霧、水面をまたぐ場合は水面の高さで霧を切り替えます。水中では視界が短くなるので遠景の描画は早めに打ち切って、コストを減らせます。

## 濁り: 吸収と散乱 {#turbid}

澄んだ海では吸収が主です。濁った水（泥、プランクトン）では散乱が強く、光が水中であらゆる方向に散って、視界がさらに短くなります。霧のようなもやが見えます。

- 澄んだ海は吸収が小さく（赤だけ強い）、散乱がごく小さいので青く遠くまで見えます。
- 湖は吸収も散乱も中くらいで、緑がかった少しもやっとした見た目です。
- 濁った川は吸収も散乱も大きく、茶色のもやで数メートルしか見えません。

濁った水では `water_color` を明るく不透明に近くして、吸収係数を大きくします。霧のような見た目になります。

## よくあるミス {#mistakes}

??? failure "水中なのに、遠くまでくっきり見える"
    原因は距離フォグがかかっていないことです。`exp(−σ · d)` を RGB ごとの吸収係数で計算して、水の色と混ぜます。

??? failure "遠くが、赤くなるまたは色が地上のままになる"
    原因は吸収係数を RGB で同じ値にしていることです。赤を大きく青を小さくします。

??? failure "水面の外にある物（山、空）まで水中の霧で青くなる"
    原因はカメラから物までの全距離に水中の霧をかけていることです。視線が水面から出るなら水面までの距離だけを使います。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 透過率は `exp(−σ · d)` で、`σ` を RGB で変えます。赤が先に消えます。
    - [x] `σ = (0.45, 0.07, 0.03)` なら 5 % になる距離は、赤で約 6.7 m、青で約 100 m です。
    - [x] 水面の外に出る視線は、水中を通る分だけに霧をかけます。
    - [x] 水の色は深いほど暗くします。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は式からの計算です。吸収係数は一例です。

- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997
- Jerlov, "Marine Optics", Elsevier, 1976
- Gordon, Brown, Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics, Vol. 14, No. 2, 1975
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Underwater Rendering](index.md)
- [Color by Water Depth](../shading/depth-color.md)
- [Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)

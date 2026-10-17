---
title: 水のシェーディング
tags:
  - 描画
---

# 水のシェーディング

<strong>水面の「色」</strong>を、**どう決めるか**です。**水面の色は、「反射した光」と「水の中を通ってきた光」の足し算**です。**どちらがどれだけ見えるかはフレネルで決まり**、**水の中を通った光の色は、水深（光が水を通る距離）で決まります**。このページでは、**フレネル・水深による吸収（Beer の法則）・屈折の歪み・スペキュラ・散乱（SSS 風の色）・合成の全体像**を説明します。

!!! tip "ポイント"
    - 水面の色 ＝ <strong>反射 × F</strong> ＋ <strong>水中を通った光 × (1 − F)</strong>。<strong>F はフレネル</strong>。
    - <strong>真上から見ると透けて底が見え</strong>、<strong>浅い角度で見ると空を映す鏡</strong>になる。
    - <strong>水中の光は、距離に応じて指数的に減る</strong>（<strong>Beer の法則</strong>）。<strong>赤が最初に消え、青が最後まで残る</strong>。
    - <strong>水深</strong> ＝ <strong>水面の深度と、不透明の深度の差</strong>（[屈折](../translucency/refraction.md)）。
    - <strong>屈折</strong>は<strong>法線で UV をずらして</strong>背景を読む。<strong>水面より手前の物を読まない</strong>ように注意。
    - <strong>スペキュラ</strong>は<strong>太陽の反射</strong>。<strong>法線マップの細かさ</strong>で<strong>きらめく</strong>。

## 水面で何が起きているか

**光が水面に当たると一部は反射し、残りは水の中へ屈折して入ります**。**水の中では吸収と散乱を受けながら進み**、**底や水中の物で跳ね返り**、**再び水面を通って目に入ります**。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="水面で起きること">
<text x="20" y="24" class="fig-title">水面で起きること：反射 ＋ 水中を通ってきた光</text>
<rect x="40" y="130" width="700" height="150" fill="#4c8bf5" fill-opacity="0.18"/>
<line x1="40" y1="130" x2="740" y2="130" stroke="#4c8bf5" stroke-width="3"/>
<line x1="150" y1="40" x2="330" y2="130" stroke="#e5aa28" stroke-width="3"/>
<polygon points="330,130 316,116 308,128" fill="#e5aa28" transform="translate(0,0)" opacity="0"/>
<line x1="330" y1="130" x2="500" y2="45" stroke="#e5484d" stroke-width="3"/>
<text x="505" y="52" style="font-size:13px">反射（F）</text>
<line x1="330" y1="130" x2="400" y2="250" stroke="#2ea043" stroke-width="3"/>
<text x="408" y="248" style="font-size:13px">屈折して水中へ（1 − F）</text>
<line x1="400" y1="250" x2="640" y2="250" stroke="currentColor" stroke-opacity="0.5" stroke-width="2"/>
<text x="470" y="270" style="font-size:12px">底で跳ね返る</text>
<line x1="640" y1="250" x2="560" y2="130" stroke="#2ea043" stroke-width="3" stroke-dasharray="6 4"/>
<line x1="560" y1="130" x2="640" y2="40" stroke="#2ea043" stroke-width="3" stroke-dasharray="6 4"/>
<text x="648" y="44" style="font-size:13px">目へ</text>
<text x="100" y="68" style="font-size:13px">太陽</text>
<line x1="330" y1="130" x2="330" y2="60" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
<text x="338" y="76" style="font-size:12px">法線</text>
</svg>

| 成分 | 内容 |
| --- | --- |
| **反射** | **空・周囲の景色**を映す（[反射](../reflections/index.md)） |
| **屈折＋透過** | **水中の物・底**が透けて見える（歪む） |
| **吸収** | **水を通る距離に応じて、色が変わり暗くなる** |
| **散乱** | **水中の粒子で光が散らばり、水自体が青緑に光る** |
| **スペキュラ** | **太陽・光源の鋭い反射** |

## フレネル

**フレネル**は、<strong>「見る角度が浅いほど、反射が強くなる」</strong>という現象です。**水面に真上から（垂直に）近い角度で見ると反射は約 2 %** で**ほとんどが透過**します。**水平に近い角度で見ると、反射は 100 % に近づき**、**鏡のように**なります。

<div class="formula">F(θ) = F₀ + (1 − F₀) · (1 − cos θ)⁵　（Schlick 近似、水の F₀ ≈ 0.02）</div>

| 記号 | 意味 |
| --- | --- |
| **θ** | **視線と法線のなす角**（`cos θ = dot(N, V)`） |
| **F₀** | **真上から見たときの反射率**。**水は約 0.02**（屈折率 1.33 から求まる） |
| **F** | **反射の割合**（0〜1）。**透過は 1 − F** |

**屈折率 n から F₀ を求める式**です。

<div class="formula">F₀ = ((n₁ − n₂) / (n₁ + n₂))²　（空気 n₁ = 1.0、水 n₂ = 1.33 → F₀ ≈ 0.02）</div>

```hlsl
float Fresnel(float3 normal, float3 view_dir) {
  float cos_theta = saturate(dot(normal, view_dir));
  const float kF0 = 0.02;
  return kF0 + (1.0 - kF0) * pow(1.0 - cos_theta, 5.0);
}
```

<strong>`view_dir` は、「水面から目へ向かう向き」</strong>（正規化済み）です。**向きを逆にすると、`cos θ` の符号が変わる**ので**注意**します。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="フレネルのグラフ">
<text x="20" y="24" class="fig-title">フレネル：見る角度で、反射の割合が変わる（水：F₀ = 0.02）</text>
<line x1="80" y1="220" x2="720" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="3" points="80,216 160,215 240,213 320,210 400,205 480,196 560,180 620,155 670,110 700,70 720,52"/>
<text x="84" y="44" style="font-size:12px">F（反射の割合）</text>
<text x="76" y="238" style="font-size:12px" text-anchor="end">0</text>
<text x="86" y="240" style="font-size:12px">真上から見る（θ = 0°）</text>
<text x="720" y="240" style="font-size:12px" text-anchor="end">水平に近い（θ → 90°）</text>
<text x="420" y="150" style="font-size:13px">ほとんど変わらない</text>
<text x="560" y="100" style="font-size:13px">急に反射が増える</text>
<line x1="90" y1="52" x2="720" y2="52" stroke="#e5484d" stroke-opacity="0.5" stroke-dasharray="4 4"/>
<text x="400" y="46" style="font-size:12px;fill:#e5484d">F = 1（完全な鏡）</text>
</svg>

**水面の見た目の大半は、この 1 つの式で決まります**。**足元の水は透けて底が見え**、**遠くの水は空を映す**のは、**フレネルのため**です。

## 水深による色（Beer の法則）

**光が水の中を距離 d だけ進むと、強さは指数関数的に減ります**（**Beer–Lambert の法則**）。**吸収の強さは色（波長）ごとに違い**、**水は赤を強く吸収し、青をあまり吸収しません**。**そのため、深くなるほど青緑に変わります**。

<div class="formula">透過率 T = exp( −σ · d )　（σ：色ごとの吸収係数、d：水中を通った距離）</div>

| 記号 | 意味 |
| --- | --- |
| <strong>σ（RGB）</strong> | **吸収係数**。**水は赤が大きく、青が小さい**（例：(0.45, 0.07, 0.03) /m） |
| **d** | **光が水中を通った距離** |
| **T** | **残る光の割合**。**色ごとに違う** |

```hlsl
float3 absorption = float3(0.45, 0.07, 0.03);
float3 transmittance = exp(-absorption * water_depth);
float3 refracted_color = scene_color * transmittance + deep_color * (1.0 - transmittance);
```

| 点 | 説明 |
| --- | --- |
| **`scene_color * transmittance`** | **底の色が水を通って減った分** |
| **`deep_color * (1 − T)`** | **減った分を水自身の色で置き換える<strong>（</strong>散乱で光る水の色**） |
| **浅い所** | **T ≈ 1**。**底がはっきり見える** |
| **深い所** | **T ≈ 0**。**水自身の色（深い青）だけ** |

### 水深の求め方

**水深**は**不透明な物の深度（水の後ろにある底）と、水面の深度の差**です（[屈折](../translucency/refraction.md)）。

```hlsl
float scene_depth = LinearizeDepth(depth_texture.Sample(point_clamp, screen_uv).r);
float surface_depth = LinearizeDepth(input.position.z);
float water_depth = max(scene_depth - surface_depth, 0.0);
```

| 注意 | 内容 |
| --- | --- |
| **視線方向の距離** | **深度の差は視線に沿った距離ではなく、カメラの前方（Z）方向の差**。**斜めから見るほど、実際の水中の距離は長い**ので、**`/ dot(V, 前方)`** のような補正をすることもある |
| **ワールド座標で求める** | **底のワールド位置を再構築し、水面との距離を直接測る**ほうが**正確** |
| **垂直の水深** | **泡や岸辺の判定には、垂直方向の深さ**（ワールドの Y の差）を使う |

## 屈折の歪み

**水面の法線は波で傾く**ので、**水中の物は歪んで見えます**。**法線の XZ 成分で背景を読む UV をずらします**。

```hlsl
float2 distortion = wave_normal.xz * distortion_strength;
float2 refract_uv = screen_uv + distortion;

float scene_depth_at_uv = LinearizeDepth(depth_texture.Sample(point_clamp, refract_uv).r);
if (scene_depth_at_uv < surface_depth) {
  refract_uv = screen_uv;
}

float3 scene_color = scene_copy.Sample(linear_clamp, refract_uv).rgb;
```

| 点 | 説明 |
| --- | --- |
| **`distortion_strength`** | **0.02 程度**。**大きすぎると不自然** |
| **深度の再確認** | **ずらした先が水面より手前（水の外にある物）なら、ずらさない**。**手前の物が水の中に引きずられて見える**失敗を防ぐ |
| **距離で弱める** | **遠くの水は歪みを減らす**（**ちらつき防止**） |
| **水深で強める** | **深いほど、歪みが大きい**（**浅い所はほとんど歪まない**） |

## スペキュラ（太陽の反射）

**太陽が水面に映ると細かい波ごとに小さな反射が散らばって見えます**（**グリント**）。**法線マップの細かい法線**で、**Blinn–Phong・GGX のスペキュラ**を**計算**します。

```hlsl
float3 half_vector = normalize(light_dir + view_dir);
float n_dot_h = saturate(dot(normal, half_vector));
float specular = pow(n_dot_h, shininess) * sun_intensity;
```

| 点 | 説明 |
| --- | --- |
| **高い `shininess`** | **水面は滑らかなので鋭いハイライト**（例：256 以上） |
| **GGX を使う** | **PBR の規約と揃える**（[PBR](../../3d/pbr.md)）。**粗さ（roughness）を小さく** |
| **HDR で出す** | **太陽の反射は非常に明るい**。**ブルームで光る**（[ブルーム](../postprocess/index.md)） |
| **ちらつき対策** | **細かい法線は距離でぼかす**（**粗さを距離で上げる**）。**さもないと遠くがチカチカする** |

## 反射

**反射はフレネルの F で重みを付けて合成**します。**反射の取り方は、状況で選びます**。

| 方式 | 内容 |
| --- | --- |
| <strong>環境マップ（キューブ）</strong> | **安い**。**空や遠景だけ**。**近くの物は映らない** |
| **平面反射** | **水面は平らなので鏡像用にもう一度描く**。**正確だが重い**（[平面反射](../reflections/index.md)） |
| **SSR** | **画面内の物を映す**。**画面外は環境マップに落とす** |
| **レイトレ反射** | **最も正確**。**重い** |

**波で法線が傾く**ので**反射ベクトルを法線から作り**、**平面反射なら、法線の XZ で UV をずらして歪ませます**。

```hlsl
float3 reflect_dir = reflect(-view_dir, normal);
float3 reflection = environment.SampleLevel(linear_clamp, reflect_dir, 0).rgb;
```

## 散乱の色（SSS 風）

**波頭に光が透けて、明るい青緑に光って見える**ことがあります（**太陽を背にして波を見たとき**）。**波の高い所ほど、水が薄く、光が通り抜ける**ためです。

```hlsl
float wave_height_factor = saturate(height_offset / max_wave_height);
float sun_behind = pow(saturate(dot(view_dir, -light_dir)), 4.0);
float3 scatter = scatter_color * wave_height_factor * sun_behind * sun_intensity;
```

| 点 | 説明 |
| --- | --- |
| **波の高さ** | **波頂ほど強い** |
| **太陽の向き** | **太陽が水面の向こう（視線と反対）にあるとき強い** |
| **色** | **明るい青緑**（例：(0.1, 0.5, 0.45)） |

## 合成の全体像

```hlsl
float3 N = ComputeNormal(input);
float3 V = normalize(camera_position - input.world_position);

float fresnel = Fresnel(N, V);

float3 reflection = SampleReflection(N, V);

float3 refracted = SampleRefraction(N, screen_uv, water_depth);

float3 color = lerp(refracted, reflection, fresnel);
color += specular + scatter + foam;
```

| 手順 | 内容 |
| --- | --- |
| **① 法線** | **波の法線 ＋ 細かい法線マップ**（[波のジオメトリ](waves.md)） |
| **② フレネル** | **反射と透過の割合** |
| **③ 屈折の色** | **歪ませた背景 ＋ 深度による吸収** |
| **④ 反射の色** | **環境マップ・SSR・平面反射** |
| **⑤ 混ぜる** | **`lerp(屈折, 反射, F)`** |
| **⑥ 足す** | **スペキュラ・散乱・泡**（[岸辺と泡](shore-foam.md)） |

## 水の色のパラメータ

| パラメータ | 内容 |
| --- | --- |
| **浅い水の色** | **明るい青緑**（岸辺・白い砂の上） |
| **深い水の色** | **濃い青**（沖） |
| **吸収係数 σ** | **RGB ごと**。**値を大きくすると浅いうちに濃い色** |
| **透明度の距離** | **底が見える深さ**。**σ で調整** |
| **屈折の強さ** | **歪みの大きさ** |
| **スペキュラの鋭さ** | **ハイライトの広がり** |
| **泡の色・量** | **岸辺・波頂の泡** |

**場所ごとに（湖・海・沼）変えられるよう、パラメータはマテリアルとして持つ**のが**扱いやすい**です。

## よくあるミス

??? failure "フレネルの向きを逆にして、足元が鏡になる"
    **`view_dir` は、水面から目へ向かう向き**。**`dot(N, V)` が 1 に近い（真上から見る）とき、反射が弱くなる**はず。

??? failure "水面より手前の物が、屈折で水中に引きずられる"
    **ずらした UV の深度が、水面より手前なら、ずらさない**。

??? failure "深度の差を、そのまま水の距離にして、斜めから見ると色が薄い"
    **斜めから見るほど、水中を通る距離は長い**。**視線方向の距離に補正する**。

??? failure "吸収を RGB 同じにして、色が付かない"
    **赤を強く、青を弱く吸収させる**。

??? failure "遠くの水が、チカチカする"
    <strong>細かい法線・スペキュラを距離でぼかす（粗さを上げる）</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 水面の色 ＝ <strong>反射 × F ＋ 屈折した色 × (1 − F)</strong>。<strong>F はフレネル</strong>（<strong>F₀ ≈ 0.02</strong>）
    - [x] <strong>水中の光は距離で指数的に減る</strong>（<strong>Beer の法則</strong>）。<strong>赤が最初に消える</strong>
    - [x] <strong>水深 ＝ 不透明の深度と水面の深度の差</strong>。<strong>斜めは補正</strong>
    - [x] <strong>屈折</strong>は<strong>法線で UV をずらす</strong>。<strong>手前の物を巻き込まない</strong>
    - [x] <strong>スペキュラ ＋ 散乱 ＋ 泡</strong>を<strong>足して仕上げる</strong>

## 参考

- Schlick, "An Inexpensive BRDF Model for Physically-based Rendering"（1994、フレネルの近似）
- Sousa, "Rendering Water in Crysis"（GPU Gems 2）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水](index.md)
- [波のジオメトリ](waves.md)
- [岸辺と泡](shore-foam.md)
- [屈折とガラス](../translucency/refraction.md)
- [反射](../reflections/index.md)

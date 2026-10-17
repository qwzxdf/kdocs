---
title: 水中の表現
tags:
  - 描画
---

# 水中の表現

**カメラが水面の下に入ったとき**、**そして水面の下の底を見上げるとき**の**表現**です。**水の中は遠くが青く霞み、光の筋が差し、底に光の網目（コースティクス）が揺れます**。このページでは、**水中の判定・水中の霧（吸収と散乱）・コースティクス・光の筋（ゴッド レイ）・水面の裏側・水面をまたぐときの処理**を説明します。

!!! tip "ポイント"
    - 水中の霧 ＝ <strong>距離に応じて、指数的に色が水の色に近づく</strong>（<strong>Beer の法則</strong>）。<strong>赤から消える</strong>。
    - <strong>コースティクス</strong> ＝ <strong>水面の凹凸で光が集まってできる、底の明暗の網目</strong>。<strong>動くテクスチャを投影して足す</strong>。
    - <strong>光の筋</strong> ＝ <strong>水中の粒子に当たる光</strong>。<strong>レイマーチ</strong>か、<strong>ビルボード</strong>で作る。
    - <strong>水面の裏側</strong>は、<strong>全反射</strong>が起きる（<strong>臨界角より浅い角度で見上げると、鏡</strong>）。
    - <strong>水面をまたぐ</strong>とき、<strong>画面の上半分と下半分を、別に処理</strong>する。
    - <strong>水中は色が「画面全体」に掛かる</strong>ので<strong>ポストプロセス</strong>で足すと**簡単**。

## 水中かどうかを決める

**カメラが水面より下か**を**判定**します。

```hlsl
bool underwater = camera_position.y < WaterHeightAt(camera_position.xz, time);
```

| 点 | 説明 |
| --- | --- |
| **波の高さを含める** | **平均水位ではなく、そこの水面の高さ**で判定 |
| **ポストプロセスの切り替え** | **水中なら、水中のフォグ・色補正を掛ける** |
| **水面の描き方** | **水中から見る水面は、裏面を描く**（**カリングを切るか、裏面用のシェーダー**） |

## 水中の霧

**水中では遠くの物ほど、水の色に近づきます**。**地上のフォグと同じ構造**ですが、**吸収が色ごとに違う**のが**特徴**です。

<div class="formula">T = exp( −σ · d )　（σ：吸収係数（RGB）、d：カメラから物までの距離）</div>

```hlsl
float3 absorption = float3(0.45, 0.07, 0.03);
float3 transmittance = exp(-absorption * distance_to_pixel);
float3 scattered = water_color * (1.0 - transmittance);
float3 final_color = scene_color * transmittance + scattered;
```

| 点 | 説明 |
| --- | --- |
| **赤が先に消える** | **遠くは青緑**になる |
| **`distance_to_pixel`** | **深度から求めた、カメラからの距離**（水面を通る分も含む） |
| **水深で明るさを変える** | **深いほど暗い**（**太陽光が届かない**）。**`exp(−k · depth)`** |
| **空は水の色** | **空の部分は遠距離扱いで水の色になる** |

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

## コースティクス

**コースティクス**は、**波打つ水面がレンズのように光を集め、底に明るい網目模様ができる**現象です。**波の凹凸の形で光が集まる所と散る所ができます**。

| 方式 | 内容 |
| --- | --- |
| **アニメする模様のテクスチャ** | **ループするコースティクス模様を、ライトの方向から底に投影**して**足す**。**安い・定番** |
| **シミュレーション** | **水面の法線から屈折を計算**し、**底に落ちる光の集まりを求める**（**重い・正確**） |
| **ヤコビアン風の近似** | **水面の法線のラプラシアン**（凸凹）から、**集光の強さを近似** |

### テクスチャを投影する

```hlsl
float3 light_space = mul(float4(world_position, 1), light_view_projection).xyz;
float2 caustics_uv = world_position.xz * caustics_scale;

float c1 = caustics_texture.Sample(linear_wrap, caustics_uv + time * float2(0.03, 0.02)).r;
float c2 = caustics_texture.Sample(linear_wrap, caustics_uv * 1.3 - time * float2(0.02, 0.03)).r;
float caustics = min(c1, c2);

float depth_fade = exp(-water_depth_at_point * caustics_falloff);
float3 lit = base_color + sun_color * caustics * depth_fade * n_dot_l;
```

| 点 | 説明 |
| --- | --- |
| **2 枚の `min`** | **向きの違う 2 枚の暗い方を取る**と、**明るい線が細く交差して、リアルな網目** |
| **水深で減衰** | **深い底ほど、光が届かず、弱い** |
| **`n_dot_l`** | **太陽に向いた面だけ**（**壁には弱く**） |
| **水面より上は出さない** | **水位より下の位置だけに投影** |
| **ワールド座標の UV** | **カメラが動いても底に貼りつく**（**真上から投影**が簡単） |

### 色収差で見栄えを上げる

**コースティクスを、RGB でわずかにずらして取る**と、**縁が虹色に光って**、**よりそれらしく**見えます。

```hlsl
float r = caustics_texture.Sample(linear_wrap, caustics_uv + float2(0.002, 0)).r;
float g = caustics_texture.Sample(linear_wrap, caustics_uv).r;
float b = caustics_texture.Sample(linear_wrap, caustics_uv - float2(0.002, 0)).r;
float3 caustics_rgb = float3(r, g, b);
```

## 光の筋（ゴッド レイ）

**水中に差し込む光の柱**です。**水中の粒子が光を散らして見える**ことで**生じます**。

| 方式 | 内容 |
| --- | --- |
| <strong>レイマーチ（ボリューム）</strong> | **視線に沿って進み、光が当たる点を数える**。**シャドウ マップで光が届くか判定** |
| **ポストプロセスの放射ぼかし** | **画面上で光源から放射状にぼかす**（安い） |
| <strong>ビルボード（メッシュ）</strong> | **光の筋の形をした半透明メッシュ**を、**加算で描く** |

**レイマーチの基本形**です。

```hlsl
float3 ray_origin = camera_position;
float3 ray_dir = normalize(world_position - camera_position);
float ray_length = distance_to_pixel;

float step_length = ray_length / kStepCount;
float jitter = InterleavedGradientNoise(input.position.xy);
float3 accumulated = 0;

for (int i = 0; i < kStepCount; ++i) {
  float3 sample_position = ray_origin + ray_dir * (i + jitter) * step_length;
  float shadow = SampleShadowMap(sample_position);
  float caustics = SampleCaustics(sample_position);
  float transmittance = exp(-density * (i + jitter) * step_length);
  accumulated += sun_color * shadow * caustics * transmittance * step_length;
}
```

| 点 | 説明 |
| --- | --- |
| **ジッター** | **開始位置をずらしてノイズ化**し、**少ない段数でも縞が出ない** |
| **シャドウ マップ** | **水面を通った光の柱は、物の影で切れる** |
| **コースティクス** | **光の筋が波の形で揺れる**（水面のうねりに応じて明暗） |
| **透過率** | **遠くほど減衰** |

## 水面の裏側

**水中から水面を見上げる**と、**水面は「鏡」と「窓」の両方**になります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="水中から見上げる窓">
<text x="20" y="24" class="fig-title">水中から見上げる：臨界角の内側だけ空が見え、外側は全反射</text>
<rect x="40" y="110" width="700" height="130" fill="#4c8bf5" fill-opacity="0.2"/>
<line x1="40" y1="110" x2="740" y2="110" stroke="#4c8bf5" stroke-width="3"/>
<circle cx="390" cy="225" r="7" fill="#e5484d"/>
<text x="402" y="230" style="font-size:12px">カメラ</text>
<line x1="390" y1="225" x2="390" y2="110" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
<line x1="390" y1="225" x2="505" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="390" y1="225" x2="275" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="505" y1="110" x2="610" y2="60" stroke="#2ea043" stroke-width="3"/>
<line x1="275" y1="110" x2="170" y2="60" stroke="#2ea043" stroke-width="3"/>
<text x="612" y="62" style="font-size:12px">空が見える</text>
<line x1="390" y1="225" x2="610" y2="110" stroke="#e5aa28" stroke-width="3"/>
<line x1="610" y1="110" x2="690" y2="215" stroke="#e5aa28" stroke-width="3"/>
<text x="600" y="172" style="font-size:12px">全反射</text>
<text x="400" y="170" style="font-size:12px">臨界角 約 49°</text>
</svg>

**水から空気へ出る光は、臨界角（約 49°）より浅い角度だと屈折せずに全反射**します。

<div class="formula">臨界角 θc = asin( n₂ / n₁ ) = asin( 1.0 / 1.33 ) ≈ 48.8°</div>

| 範囲 | 見え方 |
| --- | --- |
| <strong>真上に近い（円の内側）</strong> | **空が見える**（**窓**）。**空は円形に縮んで見える**（スネルの窓） |
| **円の外側** | **全反射**：**水中の景色が水面に鏡のように映る** |

```hlsl
float3 refracted = refract(-view_dir, -normal, 1.33 / 1.0);
bool total_internal_reflection = dot(refracted, refracted) < 0.001;

float3 color = total_internal_reflection
             ? SampleUnderwaterReflection(reflect(-view_dir, -normal))
             : SampleSky(refracted);
```

| 点 | 説明 |
| --- | --- |
| **`refract` の戻り値が 0** | **全反射**（屈折できない） |
| **法線を反転** | **水中側から見るので法線の向きを逆に** |
| **水面の下側のシェーディング** | **フレネルは水中側の屈折率で計算** |

## 水面をまたぐ処理

**水面ぎりぎりにカメラがあるとき、画面の上半分は水の外、下半分は水の中**になります。

| 工夫 | 内容 |
| --- | --- |
| **近い面を塞ぐ** | **カメラ前方の水面に細い帯**（水中のフォグ色）**を描き、境目の隙間をなくす** |
| **水位線の描画** | **ポストプロセスで水位の画面上の位置を求め、上下で別の処理** |
| **体積の判定** | **水のボリューム（メッシュ）を描き、前面・裏面で内外を決める** |
| **遷移** | **水に入る瞬間は、フェードで急変を隠す** |

## 水中の他の要素

| 要素 | 内容 |
| --- | --- |
| **視界** | **水中の霧で見える距離を制限** |
| **ゆらぎ** | **画面全体を法線の動きで少し歪ませる**（[ポストプロセス](../postprocess/index.md)） |
| **泡の粒子** | **ゆっくり上がる泡**（パーティクル） |
| **マリン スノー** | **漂う小さな粒**（ほこり）。**奥行き感が出る** |
| **音** | **ローパス フィルタ**（こもった音） |
| **色補正** | **青緑に寄せる** |

## よくあるミス

??? failure "水中の霧を、赤・緑・青で同じ減衰にして、灰色になる"
    <strong>吸収係数を色ごとに変える（赤を強く）</strong>。

??? failure "コースティクスが、水面より上の壁にも出る"
    **水位より下だけに投影する**。

??? failure "水中から見た水面が、真っ黒になる"
    **裏面を描いていない**。**カリングを切り**、**法線を反転**して**全反射を計算**する。

??? failure "水面ぎりぎりで、画面に隙間ができる"
    **カメラ前に細い帯を描く**か、**ポストプロセスで水位線を処理**する。

??? failure "光の筋が、縞模様になる"
    **開始位置をジッターして、段数を増やすか、時間方向に平均**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 水中の霧 ＝ <strong>Beer の法則</strong>。<strong>距離で指数的に水の色へ</strong>。<strong>赤から消える</strong>
    - [x] <strong>コースティクス</strong>は<strong>動く網目の模様を、底に投影</strong>して足す。<strong>2 枚の min</strong>
    - [x] <strong>光の筋</strong>は<strong>レイマーチ（シャドウ マップ付き）</strong>、<strong>ジッターで縞を消す</strong>
    - [x] <strong>水面の裏側</strong>は<strong>臨界角（約 49°）の窓</strong>。<strong>外側は全反射</strong>
    - [x] <strong>水面をまたぐ</strong>ときは<strong>隙間を塞ぎ</strong>、<strong>上下で処理を分ける</strong>

## 参考

- Sousa, "Rendering Water in Crysis"（GPU Gems 2）
- Guardado & Sánchez-Crespo, "Rendering Water Caustics"（GPU Gems 1）
- Fiorini et al., "Crest: Ocean System"（Unity のオープン ソース）

## 関連ページ

- [水](index.md)
- [波のジオメトリ](waves.md)
- [水のシェーディング](shading.md)
- [波紋と水面のインタラクション](interaction.md)
- [屈折とガラス](../translucency/refraction.md)

---
title: Scattering Color (SSS-Like)
tags:
  - 描画
---

# Scattering Color (SSS-Like)

夕方の海で波の向こうに太陽があるとき波の頂が明るい緑色に透けて光ります。水面を不透明な面として描くとこの透け感は出ません。水は光が内側へ入って散らされて、また出てくるからです。

<strong>水の色は吸収されて減った光と水の中で後ろへ散乱して戻ってくる光の足し算です</strong>。波の頂では水の層が薄いので背後の太陽光が通り抜けて、明るい青緑に透けます。このページでは水の色の式（Gordon ら）、波頭の透け感（SSS 風の近似）、浅瀬の散乱、入れすぎないための調整を説明します。

!!! tip "ポイント"
    - 水の色は吸収 `a` と後方散乱 `b_b` から、`R ≈ 0.33 × b_b / (a + b_b)` で近似できます。
    - 海が青いのは赤が吸収されて、青の吸収が最小で後方散乱で青が返るためです。
    - 波頭の透け感は波の高さ太陽が視線の向こう側にあるかの 2 つの積で足します。
    - 足し算なので入れすぎると、水面全体が発光して見えます。
    - 浅瀬は水の散乱の色と底の色が混ざります。白い砂の上は明るい水色です。

!!! info "このページを読む前に"
    - [Water Shading](index.md)（このセクション全体の地図と読む順番）
    - [Color by Water Depth](depth-color.md)（深さによる吸収で色が変わる仕組み）

## 水の色はどこから来るのか {#origin}

水を通して見える色は底から来る光が減ったものと水自体から返ってくる光の足し算です。後者は水の中で光が散乱して目に届く光です。この光が水の色を作っています。

- 吸収は光が水に吸い取られることです。赤が先に消えます。係数 `a`（1/m）で表します。
- 散乱は光が水の中で向きを変えることです。係数 `b`（1/m）で表します。
- 後方散乱は散乱のうち来た方向へ戻る成分です。係数 `b_b` で目に届く光の源です。

海が青く見えるのは赤が吸収され青い光が後方散乱で返ってくるためです。

## 水の色を計算する {#color}

Gordon ら（1975）は深い水の水面から出てくる光の割合を吸収と後方散乱から、次の式で近似しました。

```text
R ≈ f × b_b / (a + b_b)         f ≈ 0.33
```

`R` は入ってきた光の何割が水面から戻ってくるかを表します（体積反射率）。式を計算して確かめます。吸収が色ごとに違うので `R` も色ごとに違います。

- 澄んだ海（`a = (0.45, 0.07, 0.03)` 1/m、`b_b = 0.005`）では `R = (0.0036, 0.022, 0.047)` です。赤が緑の約 6 分の 1、青の約 13 分の 1 しか戻らないので、青っぽくなります。
- 濁った緑の湖（`a = (0.8, 0.3, 0.3)`、`b_b = 0.02`）では `R = (0.008, 0.021, 0.021)` です。緑と青が同じ程度に戻って青緑になります。

`b_b` が `a` に比べて小さいので、`R` は小さい値です。海が暗いのが普通だからです。`b_b` を 0.002 に下げると、同じ澄んだ海で `R = (0.0015, 0.0092, 0.021)` で青の戻りが半分以下になって、さらに暗くなります。`a` の値は一例で実際の水質（Jerlov の分類など）で違います。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="澄んだ海と濁った湖の体積反射率 R の RGB 値。海は青が強く、湖は緑と青が同じ"><text x="14" y="22" class="fig-title">体積反射率 R（式から計算した値）</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="100" y="188" width="50" height="12" fill="rgba(229,72,77,0.35)" stroke="#e5484d"/><rect x="160" y="118" width="50" height="82" fill="rgba(60,160,90,0.35)" stroke="#3ca05a"/><rect x="220" y="23" width="50" height="177" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5"/>
<rect x="400" y="170" width="50" height="30" fill="rgba(229,72,77,0.35)" stroke="#e5484d"/><rect x="460" y="122" width="50" height="78" fill="rgba(60,160,90,0.35)" stroke="#3ca05a"/><rect x="520" y="122" width="50" height="78" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="125" y="182">0.0036</text><text x="185" y="112">0.022</text><text x="245" y="17">0.047</text><text x="425" y="164">0.008</text><text x="485" y="116">0.021</text><text x="545" y="116">0.021</text>
<text x="185" y="222" style="font-weight:600">澄んだ海（青が強い）</text><text x="485" y="222" style="font-weight:600">濁った緑の湖（緑と青が同じ）</text></g>
<text x="360" y="250" text-anchor="middle" style="font-size:12px">左から R（赤）、G（緑）、B（青）。どちらも小さい値で、水は基本的に暗い</text></svg>

HLSL では次のように書けます。

```hlsl
// 深い水の色（体積反射率）。吸収 a（RGB）と後方散乱 bb（スカラー）から計算する
float3 DeepWaterColor(float3 absorption, float backscatter, float3 incident_light) {
  float3 R = 0.33 * backscatter / (absorption + backscatter);
  return incident_light * R;
}
```

`incident_light` は水面に降り注ぐ光（空の光と太陽光）です。昼と夜、晴れと曇りで水の色も変わります。

```hlsl
// 水面に降り注ぐ光 = 空の光 + 太陽光
float3 WaterIrradiance(float3 sky_irradiance, float3 sun_color, float3 sun_dir) {
  return sky_irradiance + sun_color * saturate(sun_dir.y);
}
```

`sun_dir.y` は太陽の高さの正弦で太陽が水平線の下なら太陽光は 0 になります。

## 波頭が透けて光る {#crest}

太陽を背にして波を見ると（太陽が波の向こう側にあるとき）、波頭が明るい青緑に光って見えます。波頭では水の層が薄く背後から来た太陽光が水を通り抜けて、目に届くためです。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="波頭の断面。背後から来た太陽光が薄い波頭を通り抜けてカメラに届く"><defs><marker id="swA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">波頭は、薄いので、背後の光が通り抜ける</text>
<path d="M40,220 C120,220 170,200 220,160 C250,130 280,100 300,90 C320,86 340,96 360,130 C390,180 440,220 520,222 L680,222 L680,250 L40,250 Z" fill="rgba(76,139,245,0.3)" stroke="#4c8bf5" stroke-width="2.5"/>
<path d="M270,118 C285,104 300,98 312,100 C325,104 335,114 345,130" fill="none" stroke="#3ca05a" stroke-width="6" opacity="0.8"/><text x="330" y="84" style="font-size:12px;fill:#3ca05a;font-weight:600">薄い波頭（緑に透ける）</text>
<g stroke="#e5aa28" stroke-width="3" marker-end="url(#swA)"><line x1="80" y1="60" x2="268" y2="124"/><line x1="100" y1="40" x2="290" y2="106"/></g><text x="60" y="36" style="font-size:12px;font-weight:600;fill:#b7791f">太陽（波の向こう側）</text>
<line x1="320" y1="104" x2="610" y2="170" stroke="currentColor" stroke-width="2.5" marker-end="url(#swA)"/><text x="620" y="176" style="font-size:12px;font-weight:600">カメラ</text>
<text x="360" y="262" text-anchor="middle" style="font-size:12px">視線と太陽が反対向き（view_dir · −sun_dir が大きい）で、波が高い所ほど強く光る</text></svg>

簡単な近似は次のとおりです。波の高さと太陽が視線の向こう側にあるかを掛け合わせます。

```hlsl
Texture2D<float4> g_scene_refraction : register(t0);   // 屈折で読んだ背景の色（底など）
SamplerState g_linear_clamp : register(s0);

cbuffer WaterConstants : register(b0) {
  float3 g_absorption;       // 吸収 a（RGB, 1/m）。例: (0.45, 0.07, 0.03)
  float g_backscatter;       // b_b。例: 0.005
  float3 g_sky_irradiance;   // 空の光（明るさ）
  float g_sss_height_start;  // 透け感が出始める波の高さ（メートル）。例: 0.5
  float3 g_sun_color;
  float g_sss_height_range;  // 出始めてから最大までの高さ（メートル）。例: 1.0
  float3 g_sun_dir;          // 太陽へ向かう単位ベクトル
  float g_sss_power;         // 太陽が向こう側のときの絞り。例: 4
  float3 g_scatter_color;    // 薄い水を通る光の色。明るい青緑。例: (0.1, 0.5, 0.45)
  float g_sss_strength;      // 全体の強さ。例: 0.5
};

// 波頭の透過光（SSS 風）
float3 WaveCrestScatter(float wave_height, float3 view_dir) {
  // 波の高さ: 高い波頭ほど 1。start から range で 0 → 1
  float height_factor = saturate((wave_height - g_sss_height_start) / g_sss_height_range);
  // 太陽が視線の向こう側にあるときだけ強い。view_dir はカメラから水面へ向かう向き
  float sun_behind = pow(saturate(dot(view_dir, g_sun_dir)), g_sss_power);
  return g_scatter_color * height_factor * sun_behind * g_sun_color * g_sss_strength;
}
```

`view_dir` はカメラから水面へ向かう向きで `g_sun_dir` は、太陽へ向かう向きです。太陽がカメラの向こう側（視線の先）にあるとき `dot(view_dir, g_sun_dir)` が 1 に近づきます。`pow` の指数が大きいほど太陽の真正面だけに絞れます。指数 4 で半分の強さになる角度は約 33° です（`cos⁴θ = 0.5` から）。指数を 8 にすると約 23.5°、16 で約 17° です。

波の高さは波の頂点の高さ（または波の傾きが大きい場所）を使います。波が大きい（荒れた）日ほど強く出ます。

水面全体の色は水の色（深い水）と波頭の透け感と屈折で見える背景をまとめて組み立てます。

```hlsl
float4 WaterScatterPS(float4 pos : SV_Position, float3 world_pos : TEXCOORD0,
                      float wave_height : TEXCOORD1, float2 refract_uv : TEXCOORD2,
                      float3 view_dir : TEXCOORD3) : SV_Target {
  // ① 水自身の色（深い水の、後方散乱）
  float3 irradiance = g_sky_irradiance + g_sun_color * saturate(g_sun_dir.y);
  float3 water_color = DeepWaterColor(g_absorption, g_backscatter, irradiance / 3.14159265);

  // ② 屈折で見える背景（底など）。ここでは単純に、水の色と混ぜる
  float3 background = g_scene_refraction.SampleLevel(g_linear_clamp, refract_uv, 0).rgb;
  float3 base = lerp(water_color, background, 0.5);                // 0.5 は混ぜ方の一例

  // ③ 波頭の透け感を足す（足し算なので、入れすぎない）
  float3 crest = WaveCrestScatter(wave_height, normalize(view_dir));
  return float4(base + crest, 1.0);
}
```

!!! warning "入れすぎると水が発光する"
    波頭の項は足し算です。強くしすぎると水面全体がぼんやり光って見えます。波頭の一部だけがほんのり光る程度に抑えます。`g_sss_strength` を 0.5 程度から始めて `height_factor` で、波頭に限ります。

## 浅瀬の散乱 {#shallow}

浅い場所の水の色は水の散乱の色と底の色の混ざったものです。底の色が白い砂だと散乱した光が明るく、水が鮮やかな水色になります。暗い岩や泥の上は暗い濃い色（北の海や沼の見え方）になり緑の藻が底にあると、緑がかった色になります。

底の色は屈折で底のテクスチャを読んで、水の色と混ぜるとこの違いが自然に出ます（[Color by Water Depth](depth-color.md)）。深さが増えるほど底の色の割合が減って、水の色（`R`）の割合が増えます。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で `WaterScatterPS` とそこから呼ぶ関数をコンパイルして、エラーが出ないことを確かめました。`R` の値と角度は式からの計算（Python）です。係数 `a`、`b_b` は例示の数字で実際の水質で測った値ではありません。GPU での描画は確認していません。

## よくあるミス {#mistakes}

??? failure "水がぼんやり光って見える"
    原因は波頭の項が強すぎることです。足し算なので水面全体が発光して見えます。`g_sss_strength` を下げて `height_factor` で波頭に限ります。

??? failure "太陽と反対側（太陽を背にしたとき）に透け感が出る"
    原因は `view_dir` の向きを逆にしていることです。カメラから水面へ向かう向きと太陽へ向かう向きの内積が、1 に近いときが太陽が視線の向こう側にあるときです。向きの約束を確認します。

??? failure "海がいつも真っ黒、または明るすぎる"
    原因は `b_b` の値か入射光の単位が合っていないことです。`R` は 0.01 から 0.05 程度の小さい値です。入射光の明るさ（空と太陽の合計）が、`R` を掛けたあとに目に見える明るさになっているか確認します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 水の色は `R ≈ 0.33 × b_b / (a + b_b)` と入射光の積で、赤が吸収されて青が返ります。
    - [x] 波頭の透け感は波の高さと太陽が視線の向こう側にあるか、の積で足します。
    - [x] 足し算なので、入れすぎると水面が発光します。
    - [x] 浅瀬は底の色と水の色を深さで混ぜます。

## 参考 {#references}

このページは次の資料を読まずに書きました。式は Gordon らの近似の一般的な形を書いたもので、`R` の値はその式に例示の係数を入れて計算した値です。

- Gordon, Brown, Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics, Vol. 14, No. 2, 1975（水中の散乱と吸収から水の色を求める式）
- Jerlov, "Marine Optics", Elsevier, 1976（海水の水質の分類 Jerlov water types）
- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997（純水の吸収係数の測定値）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes

## 関連ページ

- [Water Shading](index.md)
- [Color by Water Depth](depth-color.md)

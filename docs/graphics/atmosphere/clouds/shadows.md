---
title: Cloud Shadows
tags:
  - 描画
---

# Cloud Shadows

晴れた日に丘の上から見渡すと雲の影が地面の上をゆっくり流れていきます。この影があるだけで風景に広さと動きが出ます。雲だけが描かれていて地面が一様に日向のままだと雲が絵に貼りついているように見えます。

<strong>雲の影は太陽の方向から雲を見たときの透過率を低解像度のテクスチャ（影マップ）に描いておき、地面の太陽光に掛けて作ります</strong>。このページでは影マップの座標、雲の層を貫く積分、地面での引き方、簡易な天気マップ方式、霧への適用、太陽が低いときの注意を説明します。

!!! tip "ポイント"
    - 雲の透過率 `exp(−光学的厚さ)` を太陽に垂直な平面の 2D テクスチャに描きます。
    - 地面のシェーディングで、その影マップを引いて太陽光に掛けます。通常のシャドウ マップと掛け合わせます。
    - 影は柔らかくゆっくり動くので、512×512 程度の低解像度で足ります。更新も数フレームに 1 回で十分です。
    - 太陽が低いと影は雲の真下から大きくずれます。影マップの範囲が足りなくなります。
    - 同じ影マップを霧の光の注入にも使うと雲の下で霧が暗くなります。

!!! info "このページを読む前に"
    - [Clouds](index.md)（このセクション全体の地図と読む順番）

## 雲の影が必要な理由 {#why}

雲は地面と他の雲に影を落とします。地面への影は地面の各点から太陽へ向かって雲の層を貫く線を引きその線上の雲の密度を足し合わせれば、求まります。この足し算を地面のピクセルごとにやると重いので、先にまとめて影マップへ描いておき地面では引くだけにします。

雲の自己影（雲同士の影）は雲を描くときの光のマーチで扱います。この影マップは地面とボリューム フォグ向けです。

## 影マップを描く {#map}

太陽の方向を軸にした正射影で、カメラの周りの地面を覆う範囲を決めます。範囲内の各テクセルから太陽に向かって雲の層を貫く線を引いて、層の入口から出口までの密度を積分します。その透過率をテクスチャに保存します。

<svg class="fig flow" viewBox="0 0 720 290" role="img" aria-label="地面の点から太陽の向きに雲の層を貫く線を引き、光学的厚さを積分する。低い太陽では影が大きくずれる"><defs><marker id="cwA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">地面の点から、太陽へ向かって雲の層を貫く</text>
<rect x="40" y="70" width="640" height="56" fill="rgba(148,163,184,0.25)" stroke="#94a3b8"/><text x="660" y="62" text-anchor="end" style="font-size:12px">雲の層（高さ h0〜h1）</text>
<line x1="40" y1="240" x2="680" y2="240" stroke="currentColor" stroke-width="2"/><text x="660" y="262" text-anchor="end" style="font-size:12px">地面</text>
<circle cx="250" cy="240" r="5" fill="#e5484d"/><text x="250" y="258" text-anchor="middle" style="font-size:12px;font-weight:600">地面の点 P</text>
<line x1="250" y1="240" x2="470" y2="40" stroke="#e5aa28" stroke-width="3" marker-end="url(#cwA)"/><text x="480" y="46" style="font-size:12px;font-weight:600">太陽へ</text>
<line x1="250" y1="240" x2="250" y2="126" stroke="#94a3b8" stroke-dasharray="4 4"/>
<line x1="345" y1="126" x2="395" y2="70" stroke="#4c8bf5" stroke-width="6"/><text x="405" y="108" style="font-size:12px;fill:#4c8bf5;font-weight:600">この区間の密度を積分</text>
<line x1="250" y1="270" x2="345" y2="270" stroke="currentColor" stroke-width="1.5" marker-end="url(#cwA)"/><text x="300" y="284" text-anchor="middle" style="font-size:12px">水平のずれ = h / tan(仰角)</text></svg>

雲の層を高さ `h0` から `h1` の平らな板として扱うと地面の点 `P` から太陽へ向かう線が板に入る距離と出る距離は、太陽の向きの y 成分で決まります。`t0 = (h0 − P.y) / sun.y`、`t1 = (h1 − P.y) / sun.y` です。`sun.y` は太陽が水平線に近いほど小さくなります。

水平方向のずれは数字で見積もれます。雲の底が高さ 2000 m にあるとき太陽の仰角が 30° なら影は雲の真下から `2000 / tan 30° ≒ 3460 m` ずれます。仰角が 10° なら `2000 / tan 10° ≒ 11.3 km` です。朝夕は影の位置が雲から遠く離れます。影マップの範囲（カメラの周りの数 km）には、この距離のぶんだけ余裕を持たせます。

まず、定数とテクスチャです。影マップの座標系は太陽の向きに垂直な平面に基底ベクトルで作ります。

```hlsl
Texture3D<float> g_cloud_noise : register(t0);      // 雲の密度の基本形（低周波の 3D ノイズ）
Texture2D<float> g_weather_map : register(t1);      // カバレッジ（0..1）。雲の有無
SamplerState g_linear_wrap : register(s0);
SamplerState g_linear_clamp : register(s1);
RWTexture2D<float> g_cloud_shadow_map : register(u0);

cbuffer CloudShadowConstants : register(b0) {
  float3 g_sun_dir;            // 太陽へ向かう単位ベクトル
  float g_cloud_h0;            // 雲の底の高さ（メートル）。例: 2000
  float3 g_shadow_right;       // 影マップの右方向（太陽に垂直な単位ベクトル）
  float g_cloud_h1;            // 雲の天井の高さ（メートル）。例: 4000
  float3 g_shadow_up;          // 影マップの上方向（太陽に垂直な単位ベクトル）
  float g_extinction;          // 消散係数（1/メートル）。例: 0.002
  float3 g_shadow_center;      // 影マップの中心（カメラの下の地面。ワールド位置）
  float g_shadow_extent;       // 影マップが覆う 1 辺（メートル）。例: 8192
  float2 g_weather_scale;      // 天気マップの UV へのスケール（1/メートル）
  float g_time;                // 雲の流れ用
  uint g_shadow_size;          // 影マップの 1 辺（テクセル）。例: 512
};
```

次に、影マップを描く計算シェーダーです。

```hlsl
// 雲の密度を、安く求める（細部のノイズは使わない。影はぼんやりしているので十分）
float CloudDensityCheap(float3 p) {
  float2 weather_uv = p.xz * g_weather_scale + g_time * 0.0002;
  float coverage = g_weather_map.SampleLevel(g_linear_wrap, weather_uv, 0);
  float shape = g_cloud_noise.SampleLevel(g_linear_wrap, p * 0.0004, 0);
  // 層の中の高さの割合。底と天井で、密度を落とす（足した処理: 丸みの近似）
  float h = saturate((p.y - g_cloud_h0) / (g_cloud_h1 - g_cloud_h0));
  float profile = saturate(4.0 * h * (1.0 - h));
  return saturate(coverage * shape * profile * 2.0 - 0.2);
}

[numthreads(8, 8, 1)]
void CloudShadowMapCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_shadow_size)) return;

  // 影マップのテクセル → 太陽に垂直な平面上の点（地面の高さに置く）
  float2 uv = (float2(id.xy) + 0.5) / g_shadow_size - 0.5;         // -0.5 .. +0.5
  float3 plane_pos = g_shadow_center + (g_shadow_right * uv.x + g_shadow_up * uv.y) * g_shadow_extent;

  // この点から太陽へ向かって、雲の層に入る距離と出る距離（平らな板として扱う）
  float sun_y = max(g_sun_dir.y, 0.05);                            // 足した: 水平に近い太陽の暴走を防ぐ
  float t0 = (g_cloud_h0 - plane_pos.y) / sun_y;
  float t1 = (g_cloud_h1 - plane_pos.y) / sun_y;

  const int kSteps = 16;
  float step_len = (t1 - t0) / kSteps;
  float optical_depth = 0.0;
  for (int i = 0; i < kSteps; ++i) {
    float3 p = plane_pos + g_sun_dir * (t0 + (i + 0.5) * step_len);
    optical_depth += CloudDensityCheap(p) * g_extinction * step_len;
  }
  g_cloud_shadow_map[id.xy] = exp(-optical_depth);                  // 透過率（1 = 影なし、0 = 完全な影）
}
```

`CloudDensityCheap` は雲を描くときの密度の安い版です。影はぼんやりしているので細部のノイズを省いても、見た目はほぼ変わりません。`exp(-optical_depth)` が透過率で 1 なら光がそのまま地面に届いて、0 なら雲に遮られます。

数字で確かめます。512 × 512 のテクセルに 16 ステップなら 1 回の更新で `512 × 512 × 16 ≒ 420 万回` の密度計算です。範囲が 8192 m なら 1 テクセルが 16 m で、雲の影の柔らかさには十分です。雲はゆっくり動くので 4 フレームに 1 回の更新で、1 フレーム当たり約 100 万回に減ります。

## 地面で引く {#lookup}

地面のライティングではピクセルのワールド位置を影マップの座標へ変換して、透過率を引きます。変換は描くときと同じ基底でそろえます。

```hlsl
Texture2D<float> g_shadow_map_sample : register(t2);     // 描いた影マップ（SRV）
Texture2D<float> g_sun_shadow_map : register(t3);        // 通常のシャドウ マップ
SamplerComparisonState g_shadow_sampler : register(s2);

cbuffer GroundConstants : register(b1) {
  float3 g_sun_color;
  float g_min_transmittance;   // 影の下限。例: 0.3（暗くなりすぎない）
  float4x4 g_world_to_light;
};

float CloudShadow(float3 world_pos) {
  // 地面の点を、太陽に垂直な平面へ投影して、影マップの UV にする
  float3 rel = world_pos - g_shadow_center;
  float2 uv = float2(dot(rel, g_shadow_right), dot(rel, g_shadow_up)) / g_shadow_extent + 0.5;
  if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;                  // 足した: 範囲外は影なし
  float t = g_shadow_map_sample.SampleLevel(g_linear_clamp, uv, 0);
  return max(t, g_min_transmittance);                              // 下限で、暗くなりすぎを防ぐ
}

float4 GroundSunPS(float3 world_pos : TEXCOORD0, float3 normal : TEXCOORD1) : SV_Target {
  // 通常のシャドウ マップ（地面の物体が落とす影）
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float2 suv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);
  float object_shadow = g_sun_shadow_map.SampleCmpLevelZero(g_shadow_sampler, suv, ndc.z - 0.001);

  // 雲の影と、物体の影は独立した遮蔽なので、掛け算で重ねる
  float3 sun = g_sun_color * CloudShadow(world_pos) * object_shadow;
  float ndotl = saturate(dot(normalize(normal), g_sun_dir));
  return float4(sun * ndotl, 1.0);
}
```

雲の影と物体の影は独立した遮蔽なので、確率の積と同じく掛け算で重ねます。雲の下では太陽の光が弱まって、地面が暗くなります。

`g_min_transmittance` は影の濃さの下限です。雲の影は実際は柔らかく薄いものです。完全に 0 にすると暗すぎて不自然なので、0.3 程度を下限にします。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="雲底の高さ 2000 m での、太陽の仰角と影の水平ずれ"><text x="14" y="22" class="fig-title">太陽の仰角と、影の水平ずれ（雲底 2000 m）</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/><line x1="60" y1="200" x2="60" y2="40" stroke="currentColor" stroke-width="1.5"/>
<g fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"><rect x="90" y="199" width="70" height="1"/><rect x="200" y="184" width="70" height="16"/><rect x="310" y="173" width="70" height="27"/><rect x="420" y="153" width="70" height="47"/><rect x="530" y="46" width="70" height="154" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="125" y="190">0</text><text x="235" y="178">約 1.15</text><text x="345" y="167">2.0</text><text x="455" y="147">約 3.5</text><text x="565" y="40">約 11.3</text>
<text x="125" y="220">90°</text><text x="235" y="220">60°</text><text x="345" y="220">45°</text><text x="455" y="220">30°</text><text x="565" y="220">10°</text></g>
<text x="360" y="244" text-anchor="middle" style="font-size:12px">水平ずれ（km）= 2000 m ÷ tan(仰角)。低い太陽ほど急に大きくなる。90° は真下で 0（図は目盛りを切ってある）</text></svg>

## 簡易な方法: 天気マップを直接引く {#weather}

影マップを作らずに天気マップのカバレッジをそのまま影の濃さに使う方法があります。雲の高さのぶんだけ太陽の向きに位置をずらして、天気マップを読みます。

```hlsl
float WeatherMapShadow(float3 world_pos) {
  // 雲の層が地面の上空にあるので、影は太陽と反対の向きにずれる
  float2 shift = g_sun_dir.xz * (g_cloud_h0 / max(g_sun_dir.y, 0.1));
  float2 shadow_uv = (world_pos.xz + shift) * g_weather_scale;
  float coverage = g_weather_map.SampleLevel(g_linear_wrap, shadow_uv, 0);
  return 1.0 - coverage * 0.7;                // 0.7 は影の強さの一例
}
```

計算はテクスチャ読み出し 1 回だけで、軽いです。雲の厚みの細かい濃淡は出ません。影マップ方式は雲の実際の密度を反映するので、精度が高く更新に少しコストがかかります。天気マップ方式は精度が低く（カバレッジだけ）、コストは最小です。

## 霧にも使う {#fog}

霧や大気のライティングにも同じ雲の影を使います。雲の下で霧が暗くなって雲の隙間から差す光の筋（[God Rays](../god-rays/index.md)）が出ます。地面と霧が同じ影マップを使うので、ずれがありません。

```hlsl
// ボリューム フォグの、太陽の光の注入で、雲の影も掛ける（セルごとに呼ぶ）
float3 InjectSunLight(float3 cell_world_pos, float shadow_map_visibility) {
  return g_sun_color * shadow_map_visibility * CloudShadow(cell_world_pos);
}
```

!!! note "確かめた範囲"
    HLSL は `fxc` で、`CloudShadowMapCS`（`cs_5_0`）、`GroundSunPS`（`ps_5_0`）と天気マップ方式の関数をコンパイルして、エラーが出ないことを確かめました。数字は式からの手計算です。GPU での描画は確認していません。

## 注意点 {#notes}

- 雲が風で動くと影マップも変わります。更新を間引くと影がカクカクします。前の影マップと補間してなめらかにします。
- 太陽の角度が浅い朝夕は影が長く伸びます。影マップの範囲が足りなくなるので、範囲を広げるかカスケードにします。
- 雲の影の濃さは柔らかく薄い方が自然です。透過率の下限を設けます。
- 地面と霧で同じ影マップを使って、ずれがないようにします。

## よくあるミス {#mistakes}

??? failure "雲の影が地面に落ちない"
    原因は影マップを作っていないか地面のシェーダーで引いていないことです。影マップを描いて地面の太陽光に透過率を掛けます。

??? failure "雲の影が、雲の真下にしか出ない（朝夕に合わない）"
    原因は太陽の向きに位置をずらしていないことです。雲の高さのぶんだけ太陽の向きにずれます。仰角 10° で雲底 2000 m なら約 11 km もずれます。

??? failure "雲の影の下が真っ暗になる"
    原因は透過率の下限がないことです。影は柔らかく薄いものなので下限（0.3 程度）を設けて、環境光も残します。

??? failure "雲の動きに合わせて、影がカクカク動く"
    原因は影マップの更新を間引いたのに、補間していないことです。前の影マップと新しい影マップの間をフレームごとに補間します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 雲の透過率を太陽に垂直な平面の影マップに描いて、地面の太陽光に掛けます。
    - [x] 解像度は 512×512 程度で、数フレームに 1 回の更新で足ります。
    - [x] 太陽が低いと影は雲の真下から大きくずれます。仰角 10° で雲底 2000 m なら約 11 km です。
    - [x] 地面と霧で、同じ影マップを使います。

## 参考 {#references}

このページは次の資料を読まずに書きました。式と HLSL は自分で書いたもので、`fxc` でのコンパイルまで確かめています。

- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Clouds](index.md)
- [Cascaded Shadow Maps (CSM)](../../shadows/cascaded.md)

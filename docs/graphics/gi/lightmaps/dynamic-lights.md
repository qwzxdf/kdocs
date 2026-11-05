---
title: Lightmaps and Dynamic Lights
tags:
  - 描画
---

# Lightmaps and Dynamic Lights

ライトマップに焼いた光は焼いた時点で固定です。部屋の照明を消す懐中電灯を点けるキャラクターの影が壁に落ちるといったゲームの動きは、焼いた光だけでは出せません。そこで、ライトごとに「何を焼いて何を実行時に計算するか」を決めます。決めるのはライトのモードです。ベイク、動的、ミックスの 3 つがありミックスはさらに影の扱いで細かく分かれます。このページでは Unity のマニュアルの表に沿って、モードごとに何が焼かれ何が実行時に計算されるかを整理し、各モードの HLSL、シャドウマスクの 4 チャンネル制限、照明のオン・オフのコストを数字と一緒に説明します。

!!! tip "ポイント"
    - ライトのモードは 3 つ。ベイク（全部焼く）、動的（全部実行時）、ミックス（間接光は焼き直接光は実行時）。
    - ミックスの影の扱いは 4 通り。Baked Indirect、Shadowmask、Distance Shadowmask、Subtractive。
    - シャドウマスクは 1 テクセルに最大 4 本のライトの影を持つ。5 本目からは焼かれる。
    - 同じライトを焼いたものと実行時の両方で足さない。モードは 1 つに決める。
    - 照明のオン・オフはライトマップの 2 セット持ちかライトごとのライトマップに分けて足す。

!!! info "このページを読む前に"
    - [Lightmaps](index.md)（このセクション全体の地図と読む順番）

## 読んだ資料 {#sources}

- Unity のマニュアルの Mixed Light と Lighting Mode のページ（docs.unity.com）。取得した要約を読みました。ページの全文は読めていません。ここに書く Unity の数字（4 チャンネル、各モードの焼く内容）はその要約の範囲です。
- Iwanicki, Sloan, "Precomputed Lighting in Call of Duty: Infinite Warfare"（SIGGRAPH 2017）と、Iwanicki の "Lighting Technology of The Last of Us"（2013）は、読んでいません。

ほかのエンジンでも似た仕組みを持ちますが、このページの用語と数字は Unity のものです。

## ライトの 3 つのモード {#modes}

エンジンではライトごとにモードを選びます。

- **ベイク**: 直接光と間接光をライトマップに焼きます。実行時には何も計算しません。動かない部屋の照明や街灯に使います。
- **動的（リアルタイム）**: 何も焼かず直接光と影を実行時に計算します。懐中電灯、爆発、プレイヤーが触れるライトに使います。
- **ミックス**: 間接光は焼き直接光は実行時に計算します。太陽のように動かないが動く物体と連動した影を出したいライトに使います。

ミックスは実行時のライトと同じコストがかかります。Unity のマニュアルは焼きの結果がない場合（Baked Global Illumination を無効にした場合）、ミックスのライトがリアルタイムとして振る舞うと書いています。

<svg class="fig flow" viewBox="0 0 620 190" role="img" aria-label="3 つのライト モード"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">3 つのモードで、焼くもの(青)と、実行時に計算するもの(黄)</text><text x="10" y="62" text-anchor="start" font-size="12" fill="currentColor">ベイク</text><rect x="100" y="34" width="150" height="40" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="175.0" y="58.0" text-anchor="middle" font-size="11" fill="currentColor">間接光(焼き)</text><rect x="260" y="34" width="150" height="40" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="335.0" y="58.0" text-anchor="middle" font-size="11" fill="currentColor">直接光(焼き)</text><rect x="420" y="34" width="150" height="40" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="495.0" y="58.0" text-anchor="middle" font-size="11" fill="currentColor">影(焼き)</text><text x="10" y="112" text-anchor="start" font-size="12" fill="currentColor">動的</text><rect x="100" y="84" width="150" height="40" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="175.0" y="108.0" text-anchor="middle" font-size="11" fill="currentColor">間接光(実行時)</text><rect x="260" y="84" width="150" height="40" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="335.0" y="108.0" text-anchor="middle" font-size="11" fill="currentColor">直接光(実行時)</text><rect x="420" y="84" width="150" height="40" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="495.0" y="108.0" text-anchor="middle" font-size="11" fill="currentColor">影(実行時)</text><text x="10" y="162" text-anchor="start" font-size="12" fill="currentColor">ミックス</text><rect x="100" y="134" width="150" height="40" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="175.0" y="158.0" text-anchor="middle" font-size="11" fill="currentColor">間接光(焼き)</text><rect x="260" y="134" width="150" height="40" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="335.0" y="158.0" text-anchor="middle" font-size="11" fill="currentColor">直接光(実行時)</text><rect x="420" y="134" width="150" height="40" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="495.0" y="158.0" text-anchor="middle" font-size="11" fill="currentColor">影(実行時)</text></svg>

## ミックスのライティング モード {#lighting-mode}

ミックスのライトの扱いはシーン全体のライティング モードで決まります。Unity のマニュアルは見た目の質の高い順に 4 つを挙げています。

| 項目 | Baked Indirect | Shadowmask | Distance Shadowmask | Subtractive |
| --- | --- | --- | --- | --- |
| 直接光 | 実行時 | 実行時 | 実行時 | 動く物は実行時、静的は焼き |
| 間接光 | 焼き | 焼き | 焼き | 焼き |
| 動く物の影 | 実行時 | 実行時 | 実行時 | 実行時（最も強い平行光 1 つだけ） |
| 静的な物の影（影の距離まで） | 実行時 | 焼き（1 つの面に最大 4 本） | 実行時 | 焼き |
| 静的な物の影（影の距離の外） | なし | 焼き（最大 4 本） | 焼き（最大 4 本） | 焼き |

Baked Indirect は静的な物の影も実行時に出すので、見た目はよいが影の距離の外では影が消えます。Shadowmask は静的な物の影を焼いておくので、影の距離の外でも影が出て実行時の影は動く物だけで済みます。Distance Shadowmask は、影の距離の内側では実行時の影を使い外側では焼いた影を使うので、最も品質が高く最も重いです。Subtractive は直接光と影までライトマップに焼き動く物の影だけを引き算で足します。最も軽いが品質は低く低性能のハードウェアやセルシェーディングのような様式化に向きます。

Subtractive では実行時の影と焼いた影がうまく混ざらないことがあります。マニュアルは影の色（Realtime Shadow Color）を調整して混ぜ方を整えるよう勧めています。

## シャドウマスクの 4 チャンネル制限 {#shadowmask}

シャドウマスクはライトマップと同じ UV、同じ解像度のテクスチャで 1 テクセルに最大 4 本のライトの影を持ちます（RGBA のチャンネルごとに 1 本）。重なるライトが 5 本以上あると、残りは焼きに回されます（マニュアルの記述）。

C++ で 200 m × 200 m の範囲に半径 15 m のライトをランダムに置き、重なるライトどうしを別のチャンネルに割り当てる貪欲な彩色で、焼きに回る本数を見積もりました。

<svg class="fig flow" viewBox="0 0 660 226" role="img" aria-label="シャドウマスクのチャンネル不足"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">ライトの数ごとの、焼きに回る本数(青: 焼きに回る本数、灰: 1 点で重なる最大数)</text><line x1="60" y1="184" x2="620" y2="184" stroke="#94a3b8"/><rect x="80" y="184.0" width="34" height="1.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="97" y="180.0" text-anchor="middle" font-size="10" fill="currentColor">0</text><rect x="118" y="182.5" width="34" height="1.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="135" y="178.5" text-anchor="middle" font-size="10" fill="currentColor">3</text><text x="116" y="200" text-anchor="middle" font-size="11" fill="currentColor">20 本</text><rect x="186" y="182.0" width="34" height="2.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="203" y="178.0" text-anchor="middle" font-size="10" fill="currentColor">4</text><rect x="224" y="181.5" width="34" height="2.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="241" y="177.5" text-anchor="middle" font-size="10" fill="currentColor">5</text><text x="222" y="200" text-anchor="middle" font-size="11" fill="currentColor">50 本</text><rect x="292" y="174.0" width="34" height="10.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="309" y="170.0" text-anchor="middle" font-size="10" fill="currentColor">20</text><rect x="330" y="181.0" width="34" height="3.0" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="347" y="177.0" text-anchor="middle" font-size="10" fill="currentColor">6</text><text x="328" y="200" text-anchor="middle" font-size="11" fill="currentColor">100 本</text><rect x="398" y="132.5" width="34" height="51.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="415" y="128.5" text-anchor="middle" font-size="10" fill="currentColor">103</text><rect x="436" y="178.5" width="34" height="5.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="453" y="174.5" text-anchor="middle" font-size="10" fill="currentColor">11</text><text x="434" y="200" text-anchor="middle" font-size="11" fill="currentColor">200 本</text><rect x="504" y="43.0" width="34" height="141.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="521" y="39.0" text-anchor="middle" font-size="10" fill="currentColor">282</text><rect x="542" y="175.5" width="34" height="8.5" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="559" y="171.5" text-anchor="middle" font-size="10" fill="currentColor">17</text><text x="540" y="200" text-anchor="middle" font-size="11" fill="currentColor">400 本</text></svg>

ライトが 20 本なら 1 点で重なるライトは最大 3 本で、すべて 4 チャンネルに収まります。50 本では最大 5 本重なる点があり 4 本が焼きに回ります。200 本では最大 11 本が重なり 103 本が焼きに回りました。貪欲な割り当ては最適ではないので、実際のエンジンの割り当てより多めに出ます。ただし、重なりが 4 を超える点があれば、少なくとも 1 本は必ず焼きに回ります。

シャドウマスクのメモリはライトマップと同じ大きさです。2048² の RGBA8 なら 16 MiB（非圧縮）です。ライトの置き方を考えるときは重なりが 4 を超えないよう影響範囲を絞ります。

## 描画の組み合わせ {#shading}

モードごとの合成を HLSL に書きました。

```hlsl
// ライトマップと動的なライトの組み合わせ方（ライトのモードごとの描画）。
//   モード 0 ベイク        : 直接光 + 間接光を焼いた。実行時は何も足さない。
//   モード 1 動的          : 何も焼かない。実行時に直接光（影つき）。
//   モード 2 ミックス・間接: 間接光だけを焼いた。直接光と影は実行時（Unity の Baked Indirect）。
//   モード 3 シャドウマスク: 間接光を焼き、静的な影を別チャンネルに焼いた。影の距離で実行時の影と焼いた影を切り替える。
//   モード 4 減算          : 直接光 + 影までライトマップに焼いた。動く物の影は、実行時に引き算で足す（Unity の Subtractive）。
// モードの定義と、どのモードで何が焼かれるかは、Unity のマニュアル（Lighting Mode の表）に沿う。
// 式は、考え方（二重に足さない、実行時の影と焼いた影を距離で混ぜる、影の分を引く）を、このページが HLSL に書いたもの。

Texture2D<float4> g_lightmap : register(t0);            // 焼いたライトマップ（rgb = 光、モードで中身が違う）
Texture2D<float4> g_shadowmask : register(t1);          // シャドウマスク（rgba = 最大 4 本のライトの影）
Texture2D<float> g_realtime_shadow : register(t2);      // 実行時のシャドウ マップの結果（この画素の可視性）
Texture2D<float4> g_lightmap_on : register(t3);         // 照明のオン用のライトマップ
Texture2D<float4> g_lightmap_off : register(t4);        // オフ用のライトマップ
SamplerState g_linear_clamp : register(s0);

cbuffer LightModeCB : register(b0) {
  int g_mode;                    // 上のモード番号
  int g_mask_channel;            // このライトが使うシャドウマスクのチャンネル（0〜3。-1 はなし）
  float g_shadow_distance;       // 実行時の影を引く最大の距離 [m]
  float g_shadow_fade_width;     // 距離でのフェードの幅 [m]
  float3 g_light_dir;            // ライトへ向かう単位ベクトル
  float g_switch;                // 照明のオン・オフの混ぜる割合（0 = オフ、1 = オン）
  float3 g_light_color;          // ライトの色 × 強さ（直接光）
  float g_pad0;
  float3 g_realtime_shadow_color;// 減算モードで、影の部分に足す色（Unity の Realtime Shadow Color に相当）
  float g_pad1;
};

struct PSInput {
  float4 position : SV_Position;
  float3 world_position : TEXCOORD0;
  float3 world_normal : NORMAL;
  float2 uv : TEXCOORD1;
  float2 lightmap_uv : TEXCOORD2;     // UV2
  float eye_distance : TEXCOORD3;     // カメラからの距離 [m]
};

// ================= 部品 =================

// 距離でのフェードの重み。0 = 実行時の影、1 = 焼いた影。影の距離の手前の fade_width から、smoothstep で切り替える。
float BakedShadowWeight(float eye_distance) {
  float t = saturate((eye_distance - (g_shadow_distance - g_shadow_fade_width)) / g_shadow_fade_width);
  return t * t * (3.0 - 2.0 * t);
}

// シャドウマスクの可視性。チャンネル c の値（1 = 日向、0 = 影）。
float ShadowmaskVisibility(float2 lightmap_uv, int channel) {
  float4 mask = g_shadowmask.SampleLevel(g_linear_clamp, lightmap_uv, 0);
  // チャンネルの選び方: 配列の添字で選べないので、内積で取り出す。
  float4 select = float4(channel == 0, channel == 1, channel == 2, channel == 3);
  return dot(mask, select);
}

// ================= モード別の合成 =================

float3 ShadeByMode(PSInput input, float3 albedo, float3 n) {
  float n_dot_l = saturate(dot(n, g_light_dir));
  float3 lightmap = g_lightmap.SampleLevel(g_linear_clamp, input.lightmap_uv, 0).rgb;
  float realtime = g_realtime_shadow.Load(int3(input.position.xy, 0));    // 実行時の影（この画素の可視性）

  float3 light = 0;
  if (g_mode == 0) {
    // ベイク: 焼いた光だけ。実行時のライトは、この物体に足さない（二重に足さない）。
    light = lightmap;
  } else if (g_mode == 1) {
    // 動的: 直接光 + 影だけ。間接光はない（足すなら別にアンビエント）。
    light = g_light_color * n_dot_l * realtime;
  } else if (g_mode == 2) {
    // ミックス・間接のみ: 焼いたのは間接光だけ。直接光 + 実行時の影を足す。
    light = lightmap + g_light_color * n_dot_l * realtime;
  } else if (g_mode == 3) {
    // シャドウマスク: 影の距離の内側は実行時の影、外側は焼いた影。間は smoothstep で混ぜる。
    float baked = ShadowmaskVisibility(input.lightmap_uv, g_mask_channel);
    float w = BakedShadowWeight(input.eye_distance);
    float visibility = lerp(realtime, baked, w);
    // 動く物（焼かれていない）は、焼いた影を持たない。静的な面だけ、実行時の影と焼いた影の「小さいほう」を取る手もある。
    light = lightmap + g_light_color * n_dot_l * visibility;
  } else {
    // 減算: ライトマップが、直接光 + 影 + 間接光を持つ。動く物の影の分だけ、直接光を引く。
    float3 direct = g_light_color * n_dot_l;                              // この画素の直接光の大きさ
    float3 subtracted = lightmap - direct * (1.0 - realtime);             // 影になるぶん（1 - 可視性）を引く
    // 引きすぎて、影の色より暗くならないようにする（引きすぎると真っ黒になる）。
    light = max(subtracted, g_realtime_shadow_color);
  }
  return albedo * light;
}
```

- **ベイク**: ライトマップの値をそのまま使います。実行時のライトを足すと二重になります。
- **動的**: 直接光と影だけで、間接光がありません。足すなら別にアンビエントを足します。
- **ミックス（間接のみ）**: ライトマップは間接光です。直接光と実行時の影を足します。
- **シャドウマスク**: 影の距離の内側は実行時の影、外側は焼いた影でその間を smoothstep で混ぜます。
- **減算**: ライトマップには、影つきの直接光が入っています。動く物の影になるぶん（1 − 可視性）の直接光を引き影の色を下限にして、引きすぎを防ぎます。

距離のブレンドを数えると影の距離が 50 m、フェードの幅が 10 m のとき 40 m までは実行時の影が 100 %、45 m で 50 % ずつ 50 m 以降は焼いた影が 100 % です。

<svg class="fig flow" viewBox="0 0 620 196" role="img" aria-label="距離ブレンドの重み"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">シャドウマスクの距離ブレンド(影の距離 50 m、幅 10 m)</text><line x1="60" y1="154" x2="560" y2="154" stroke="#94a3b8"/><line x1="60" y1="34" x2="60" y2="154" stroke="#94a3b8"/><polyline points="60.0,154.0 67.1,154.0 74.3,154.0 81.4,154.0 88.6,154.0 95.7,154.0 102.9,154.0 110.0,154.0 117.1,154.0 124.3,154.0 131.4,154.0 138.6,154.0 145.7,154.0 152.9,154.0 160.0,154.0 167.1,154.0 174.3,154.0 181.4,154.0 188.6,154.0 195.7,154.0 202.9,154.0 210.0,154.0 217.1,154.0 224.3,154.0 231.4,154.0 238.6,154.0 245.7,154.0 252.9,154.0 260.0,154.0 267.1,154.0 274.3,154.0 281.4,154.0 288.6,154.0 295.7,154.0 302.9,154.0 310.0,154.0 317.1,154.0 324.3,154.0 331.4,154.0 338.6,154.0 345.7,154.0 352.9,150.6 360.0,141.5 367.1,128.1 374.3,111.8 381.4,94.0 388.6,76.2 395.7,59.9 402.9,46.5 410.0,37.4 417.1,34.0 424.3,34.0 431.4,34.0 438.6,34.0 445.7,34.0 452.9,34.0 460.0,34.0 467.1,34.0 474.3,34.0 481.4,34.0 488.6,34.0 495.7,34.0 502.9,34.0 510.0,34.0 517.1,34.0 524.3,34.0 531.4,34.0 538.6,34.0 545.7,34.0 552.9,34.0 560.0,34.0" fill="none" stroke="#4c8bf5" stroke-width="2.5"/><text x="474.28571428571433" y="28" text-anchor="middle" font-size="11" fill="currentColor">焼いた影</text><polyline points="60.0,34.0 67.1,34.0 74.3,34.0 81.4,34.0 88.6,34.0 95.7,34.0 102.9,34.0 110.0,34.0 117.1,34.0 124.3,34.0 131.4,34.0 138.6,34.0 145.7,34.0 152.9,34.0 160.0,34.0 167.1,34.0 174.3,34.0 181.4,34.0 188.6,34.0 195.7,34.0 202.9,34.0 210.0,34.0 217.1,34.0 224.3,34.0 231.4,34.0 238.6,34.0 245.7,34.0 252.9,34.0 260.0,34.0 267.1,34.0 274.3,34.0 281.4,34.0 288.6,34.0 295.7,34.0 302.9,34.0 310.0,34.0 317.1,34.0 324.3,34.0 331.4,34.0 338.6,34.0 345.7,34.0 352.9,37.4 360.0,46.5 367.1,59.9 374.3,76.2 381.4,94.0 388.6,111.8 395.7,128.1 402.9,141.5 410.0,150.6 417.1,154.0 424.3,154.0 431.4,154.0 438.6,154.0 445.7,154.0 452.9,154.0 460.0,154.0 467.1,154.0 474.3,154.0 481.4,154.0 488.6,154.0 495.7,154.0 502.9,154.0 510.0,154.0 517.1,154.0 524.3,154.0 531.4,154.0 538.6,154.0 545.7,154.0 552.9,154.0 560.0,154.0" fill="none" stroke="#e5aa28" stroke-width="2.5"/><text x="145.71428571428572" y="28" text-anchor="middle" font-size="11" fill="currentColor">実行時の影</text><text x="60.0" y="170" text-anchor="middle" font-size="10" fill="currentColor">0 m</text><text x="202.85714285714286" y="170" text-anchor="middle" font-size="10" fill="currentColor">20 m</text><text x="345.7142857142857" y="170" text-anchor="middle" font-size="10" fill="currentColor">40 m</text><text x="417.14285714285717" y="170" text-anchor="middle" font-size="10" fill="currentColor">50 m</text><text x="560.0" y="170" text-anchor="middle" font-size="10" fill="currentColor">70 m</text></svg>

## 照明のオン・オフ {#switch}

ライトマップの光は消せません。部屋の照明を消すような仕掛けには 3 つの方法があります。

- **動的にする**: オン・オフはできるが、間接光が出ません。簡易なアンビエントを足すと自然になります。
- **ライトマップを 2 セット持つ**: オン用とオフ用を焼き切り替えるか、補間します。メモリが 2 倍になります。
- **ライトごとのライトマップに分ける**: ライトごとに別のライトマップを焼き、実行時にオン・オフの強さを掛けて足し合わせます。メモリがライトの数に比例します。

C++ で数えると 2048² を BC7（1 バイト/テクセル）で持つ 1 セットは 4 MiB です。オン・オフするライトが 4 本ならライトごとの方式は 16 MiB、8 本で 32 MiB、16 本で 64 MiB です。2 セット持ちを組み合わせで考えると（N 本が独立にオン・オフ）、`2^N` 通りになり N = 8 で 256 セット、N = 16 で 65,536 セットです。組み合わせでは現実的ではないので、独立したライトはライトごとの方式に分けます。

```hlsl
// ================= 照明のオン・オフ =================

// オン用とオフ用の 2 セットのライトマップを、g_switch で混ぜる。スイッチを、滑らかに切り替える（アニメーション）。
// 2 セットのメモリが要る。ライトが N 本なら、組み合わせは 2^N 通りになるので、ライトごとのライトマップに分ける。
float3 LightmapWithSwitch(float2 lightmap_uv) {
  float3 on = g_lightmap_on.SampleLevel(g_linear_clamp, lightmap_uv, 0).rgb;
  float3 off = g_lightmap_off.SampleLevel(g_linear_clamp, lightmap_uv, 0).rgb;
  return lerp(off, on, g_switch);
}

// ライトごとのライトマップを足し合わせる場合: 各ライトが焼いた寄与に、ライトごとの強さ（オン・オフ、明滅）を掛けて足す。
StructuredBuffer<float> g_light_gain : register(t5);           // ライトごとの強さ（0〜1）
Texture2DArray<float4> g_per_light_lightmaps : register(t6);   // ライトごとのライトマップ（配列）

float3 PerLightLightmaps(float2 lightmap_uv, uint light_count) {
  float3 sum = 0;
  for (uint i = 0; i < light_count; ++i) {
    float gain = g_light_gain[i];
    if (gain <= 0.0) continue;                                  // オフのライトは、読み込みも省く
    sum += gain * g_per_light_lightmaps.SampleLevel(g_linear_clamp, float3(lightmap_uv, i), 0).rgb;
  }
  return sum;
}

// ================= 画素シェーダー =================

Texture2D<float4> g_albedo_tex : register(t7);
uint g_per_light_count;

float4 LightModePS(PSInput input) : SV_Target {
  float3 albedo = g_albedo_tex.Sample(g_linear_clamp, input.uv).rgb;
  float3 n = normalize(input.world_normal);
  return float4(ShadeByMode(input, albedo, n), 1.0);
}

// オン・オフ用の入口（上のモードと別に、照明のスイッチがある面で使う）。
float4 SwitchPS(PSInput input) : SV_Target {
  float3 albedo = g_albedo_tex.Sample(g_linear_clamp, input.uv).rgb;
  float3 baked = LightmapWithSwitch(input.lightmap_uv) + PerLightLightmaps(input.lightmap_uv, g_per_light_count);
  return float4(albedo * baked, 1.0);
}
```

`LightmapWithSwitch` は 2 セットを `g_switch` で混ぜます。スイッチを滑らかに切り替えるアニメーションができます。`PerLightLightmaps` はライトごとのライトマップを強さを掛けて足します。強さが 0 のライトは読み込みも省いています。

## 動的なライトの問題 {#problems}

- **動的な光の間接光が無い**: 動くライトの反射光は、ライトマップに含まれません。プローブ GI の動的更新（[Dynamic Updates](../probes/dynamic-update.md)）、DDGI、または簡易なアンビエントを動くライトの周りに足して補います。
- **二重に足される**: ライトをベイクにも動的にも設定すると、二重に照らされます。ライトのモードを 1 つにします。
- **静的なライトのオン・オフができない**: 上の「照明のオン・オフ」の方法を使います。

## 太陽（動かない場合）{#sun}

太陽が固定（時間が止まっている）なら太陽の光もライトマップに焼けます。昼夜が変わるなら太陽は動的です（[Day-Night Cycle](../../atmosphere/sky-models/day-night.md)）。ライトマップは時間帯ごとに複数セットを焼いて補間するかプローブ GI の動的更新を使います。

## 長所と短所 {#pros-cons}

- 長所: 実行時のコストがほぼゼロ（ベイク）、高品質（オフラインの正確な計算）、モバイルでも使えるノイズがなくソフト シャドウもきれいシェーダーが簡単。
- 短所: 静的な物だけ（動く物と動くライトを反映できない）、メモリがかかる（ライトマップ アトラス）、変更のたびに再ベイクが必要、UV2 の準備（歪みマージン、密度）が要る。

実際の現場ではイテレーションの遅さが最大の問題になります。ライトの位置を少し動かすたびに数十分から数時間のベイクが必要では、アーティストの作業が止まります。最近のエンジンは GPU ベイクや低解像度のプレビュー ベイクで、この待ち時間を縮めています。

## 数字を出す C++ {#cpp}

シャドウマスクの 4 チャンネル制限、ライトマップのメモリ、ライトごとのライトマップのコスト、距離ブレンドの重みを数えた C++ です。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。HLSL は `fxc`（ps_5_0）でコンパイルして確かめました。実行して絵は確かめていません。

```cpp
// ライトのモードごとの数字を出す。
//  1. シャドウマスクの 4 チャンネル制限: 重なるライトが多いとき、何本が焼きに回されるか（貪欲な彩色で見積もる）
//  2. ライトマップのメモリと、ライトのオン・オフ（2 セル / ライトごと）の増え方
//  3. シャドウマスクの距離ブレンドの重み
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <random>
#include <vector>

namespace {
struct Light { double x, y, r; };

// 2 つのライトの影響範囲が重なるか。
bool Overlap(const Light& a, const Light& b) { return std::hypot(a.x - b.x, a.y - b.y) < a.r + b.r; }
}  // namespace

int main() {
  std::mt19937_64 rng(2026);
  std::uniform_real_distribution<double> pos(0.0, 200.0);

  std::printf("== シャドウマスクの 4 チャンネル制限（200 m x 200 m、ライトの半径 15 m）==\n");
  std::printf("ライト数  1 点で重なる最大数  貪欲な彩色で 4 チャンネルに収まらず、焼きに回る数\n");
  for (int n : {20, 50, 100, 200, 400}) {
    std::vector<Light> lights;
    for (int i = 0; i < n; ++i) lights.push_back({pos(rng), pos(rng), 15.0});

    // 1 点で重なるライトの最大数（1 m 格子で調べる）。
    int max_overlap = 0;
    for (double y = 0; y <= 200; y += 1.0) {
      for (double x = 0; x <= 200; x += 1.0) {
        int c = 0;
        for (const Light& l : lights) c += std::hypot(l.x - x, l.y - y) < l.r;
        max_overlap = std::max(max_overlap, c);
      }
    }

    // チャンネルの割り当て: 重なるライトどうしは、別のチャンネルにする。順に貪欲に割り当て、
    // 4 つとも使われていたら、そのライトは影を焼きに回す（実行時の影は持たない）。
    std::vector<int> channel(n, -1);
    int overflow = 0;
    for (int i = 0; i < n; ++i) {
      bool used[4] = {false, false, false, false};
      for (int j = 0; j < i; ++j) {
        if (channel[j] >= 0 && Overlap(lights[i], lights[j])) used[channel[j]] = true;
      }
      for (int c = 0; c < 4; ++c) {
        if (!used[c]) { channel[i] = c; break; }
      }
      if (channel[i] < 0) ++overflow;
    }
    std::printf("%6d   %12d            %6d\n", n, max_overlap, overflow);
  }

  std::printf("\n== ライトマップのメモリ（1 セット）==\n");
  std::printf("サイズ     RGBA8(4 B)   BC7(1 B)     シャドウマスク(同じ大きさ、RGBA8)\n");
  for (int size : {1024, 2048, 4096}) {
    const double texels = static_cast<double>(size) * size;
    std::printf("%4d^2    %7.1f MiB   %6.1f MiB   %7.1f MiB\n", size, texels * 4 / 1048576, texels / 1048576,
                texels * 4 / 1048576);
  }
  std::printf("\n== ライトのオン・オフをライトマップで持つ場合（2048^2、BC7）==\n");
  const double one = 2048.0 * 2048 / 1048576;
  for (int lights : {1, 4, 8, 16}) {
    std::printf("オン・オフを持つライト %2d 本: ライトごとのライトマップ %5.1f MiB、2^N 通りの組み合わせなら %8.0f セット\n", lights,
                lights * one, std::pow(2.0, lights));
  }

  std::printf("\n== シャドウマスクの距離ブレンド（影の距離 50 m、フェードの幅 10 m）==\n");
  std::printf("距離[m]  実行時の影の重み  焼いた影の重み\n");
  for (double d : {0.0, 30.0, 40.0, 45.0, 50.0, 60.0}) {
    const double fade = std::clamp((d - 40.0) / 10.0, 0.0, 1.0);       // 40 m から 50 m で 0 → 1
    const double w = fade * fade * (3 - 2 * fade);                       // smoothstep
    std::printf("%6.0f      %5.2f            %5.2f\n", d, 1.0 - w, w);
  }
  return 0;
}
```

```text title="実行結果"
== シャドウマスクの 4 チャンネル制限（200 m x 200 m、ライトの半径 15 m）==
ライト数  1 点で重なる最大数  貪欲な彩色で 4 チャンネルに収まらず、焼きに回る数
    20              3                 0
    50              5                 4
   100              6                20
   200             11               103
   400             17               282
```

```text title="実行結果（続き）"
== ライトマップのメモリ（1 セット）==
サイズ     RGBA8(4 B)   BC7(1 B)     シャドウマスク(同じ大きさ、RGBA8)
1024^2        4.0 MiB      1.0 MiB       4.0 MiB
2048^2       16.0 MiB      4.0 MiB      16.0 MiB
4096^2       64.0 MiB     16.0 MiB      64.0 MiB
```

```text title="実行結果（続き）"
== ライトのオン・オフをライトマップで持つ場合（2048^2、BC7）==
オン・オフを持つライト  1 本: ライトごとのライトマップ   4.0 MiB、2^N 通りの組み合わせなら        2 セット
オン・オフを持つライト  4 本: ライトごとのライトマップ  16.0 MiB、2^N 通りの組み合わせなら       16 セット
オン・オフを持つライト  8 本: ライトごとのライトマップ  32.0 MiB、2^N 通りの組み合わせなら      256 セット
オン・オフを持つライト 16 本: ライトごとのライトマップ  64.0 MiB、2^N 通りの組み合わせなら    65536 セット
```

```text title="実行結果（続き）"
== シャドウマスクの距離ブレンド（影の距離 50 m、フェードの幅 10 m）==
距離[m]  実行時の影の重み  焼いた影の重み
     0       1.00             0.00
    30       1.00             0.00
    40       1.00             0.00
    45       0.50             0.50
    50       0.00             1.00
    60       0.00             1.00
```

## よくあるミス

??? failure "ベイク済みのライトが二重に効いて、明るすぎる"
    ライトをベイクにも動的にも設定している。ライトのモードを 1 つにして、ベイク済みのライトは実行時の計算から外す。

??? failure "シャドウマスクで、一部のライトの影だけが出ない"
    重なるライトが 4 本を超えて、焼きに回された。ライトの影響範囲を絞るか重要でないライトを動的や影なしにする。

??? failure "Subtractive で、動く物の影が真っ黒になる"
    引きすぎている。影の色（下限）を設定して `max` で下に切る。

??? failure "影の距離の境目で、影が急に切り替わる"
    実行時の影と焼いた影を距離で混ぜていない。影の距離の手前から `smoothstep` でフェードさせる。

??? failure "照明を消しても、部屋が明るいまま"
    ライトマップに焼いた光は消せない。オン・オフするライトは動的にするかライトごとのライトマップに分ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 静的はベイク、動的はリアルタイム、ミックスは間接を焼いて直接を実行時。
    - [x] 二重に足さない。ライトのモードは 1 つ。
    - [x] シャドウマスクは 1 テクセル 4 本まで。重なりを絞る。
    - [x] 影の距離の内外は、smoothstep で混ぜる。
    - [x] 照明のオン・オフは、ライトごとのライトマップが現実的。

## 参考

- Unity Documentation, "Mixed Lights" と "Lighting Mode"（docs.unity.com）。要約を取得して読んだ。全文は読んでいない。
- Michał Iwanicki, Peter-Pike Sloan, "Precomputed Lighting in Call of Duty: Infinite Warfare", SIGGRAPH 2017, Advances in Real-Time Rendering in Games（読んでいない）
- Michał Iwanicki, "Lighting Technology of The Last of Us", SIGGRAPH 2013（取得できず、読んでいない）

## 関連ページ

- [Lightmaps](index.md)
- [GI Comparison](../comparison.md)
- [Probe GI](../probes/index.md)
- [Specular and Dynamic Objects](dynamic-objects.md)

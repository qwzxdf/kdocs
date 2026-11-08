---
title: God Rays in Air and Water
tags:
  - 描画
---

# God Rays in Air and Water

空気中のゴッド レイの作り方（[God Rays](index.md)）は、水中でもほとんどそのまま使えます。ところが、空気中の設定のまま水に潜ると、光の筋が白くて長く伸びてしまい水の中に見えません。違うのは光の色と減衰、光の向き波による揺れの 3 点です。このページでは空気中との違いを数字で整理して、色と減衰、光の向きを求めるコードを示します。

水中の光の筋そのものの作り方（放射状ブラー・シャドウ マップのレイマーチ・メッシュ）は、水のセクションの [Underwater God Rays](../../water/underwater/god-rays.md) にまとめています。

!!! tip "ポイント"
    - 水中では赤から先に吸収されるので、光の筋は青緑になります。
    - 光は 2 回減衰します。太陽から点まで点からカメラまでです。どちらも Beer の法則で表せます。
    - 水面で屈折するので、光は真下に近い向きになります。水中の光の向きは水面に対して最大でも約 48.6° しか鉛直からずれません。
    - 作り方の詳細は [Underwater God Rays](../../water/underwater/god-rays.md) にあります。

!!! info "このページを読む前に"
    - [God Rays](index.md)（このセクション全体の地図と読む順番）

## 空気中との違い

空気中と水中の違いは 5 つの観点で比べられます。

| 項目 | 空気中 | 水中 |
| --- | --- | --- |
| 光の色 | 太陽の色（白、橙） | 青緑（赤が吸収される） |
| 減衰 | ゆるやか（数 km） | 急（数十 m で消える） |
| 揺れ | ほぼなし（霧のゆらぎ） | 波による強い揺れ（コースティクス） |
| 光の向き | 太陽の方向 | 屈折して真下に近づく |
| 見える距離 | 長い | 短い（濁りで数 m〜数十 m） |

どれも光の筋を作るアルゴリズムは変えずパラメーターと光の向きを変えるだけで表せます。特に、光の色と減衰が見た目の印象を一番大きく変えます。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="水中の光の筋が2回減衰する様子">
<defs><marker id="uwA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="14" y="22" class="fig-title">水中の光は 2 回減衰する</text>
<rect x="20" y="60" width="600" height="180" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-width="1"/>
<line x1="20" y1="60" x2="620" y2="60" stroke="currentColor" stroke-width="2"/>
<text x="26" y="52" style="font-size:12px">水面</text>
<circle cx="90" cy="30" r="12" fill="rgba(229,170,40,0.6)" stroke="currentColor"/>
<g stroke="currentColor" stroke-width="2" fill="none" marker-end="url(#uwA)">
<line x1="100" y1="42" x2="270" y2="190"/>
<line x1="280" y1="192" x2="520" y2="190"/>
</g>
<circle cx="275" cy="191" r="6" fill="rgba(229,170,40,0.8)" stroke="currentColor"/>
<rect x="525" y="170" width="70" height="40" rx="6" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="560" y="190" text-anchor="middle" dominant-baseline="central" style="font-size:13px">カメラ</text>
<text x="120" y="130" style="font-size:12px">① 太陽 → 点: exp(−a · 深さ)</text>
<text x="300" y="176" style="font-size:12px">② 点 → カメラ: exp(−a · 距離)</text>
<text x="40" y="228" style="font-size:12px">a は色（RGB）ごとに違う吸収係数。赤の a が大きいので、深く遠いほど青緑になる</text>
</svg>

## 色と減衰

水中の光の筋の色は水面からの深さに応じて、赤から順に吸収されて決まります。浅い所は明るい青緑、深くなるほど暗い青になります。点から見る側でもカメラまでの距離に応じてまた吸収されます。

```hlsl
cbuffer WaterCB : register(b0) {
  float3 g_sun_color;     // 水面に届く太陽光(リニア RGB)
  float pad0;             // 16 バイト境界にそろえる詰め物
  float3 g_absorption;    // 吸収係数(1/m、RGB)。赤が大きく、青が小さい
  float g_eta;            // 水の屈折率 n_water / n_air。約 1.333
  float3 g_sun_dir;       // 太陽へ向かう単位ベクトル(Y 上、ワールド空間)
  float pad1;             // 詰め物
};

// 水中の光の筋: 水面からの深さと、カメラまでの距離の両方で減衰させる。
float3 UnderwaterSunColor(float depth, float dist) {
  float3 sun_at_depth = g_sun_color * exp(-g_absorption * depth);   // 水面 → この点(太陽の光)
  float3 to_camera = exp(-g_absorption * dist);                     // この点 → カメラ(散乱した光)
  return sun_at_depth * to_camera;                                  // 2 回の減衰を掛ける
}
```

`exp(-a × 距離)` は Beer の法則による透過率です。`a` は吸収係数で単位は 1/m です。色ごとに値が違うので `float3` で持ちます。`depth` と `dist` の単位は m にそろえます。ゲームの 1 単位が 1 m でないときは、m に換算してから渡します。

### 数字で追う

吸収係数を赤 0.35、緑 0.05、青 0.01（1/m）とします。これは説明のための一例で実際の水の値ではありません（Pope と Fry の純水の測定を読んでいないので、この値の根拠は示せません）。濁った水ではすべての値がずっと大きくなります。

深さ 5 m の点を 10 m 離れたカメラが見るとします。太陽から点まで 5 m、点からカメラまで 10 m で、合計 15 m 分の吸収を受けます。

1. 赤は exp(−0.35 × 15) ≒ 0.005 です。ほとんど届きません。
2. 緑は exp(−0.05 × 15) ≒ 0.47 です。半分近く残ります。
3. 青は exp(−0.01 × 15) ≒ 0.86 です。ほぼ残ります。

結果は (0.005, 0.47, 0.86) で、赤がほぼ 0 になり青緑の光の筋になります。深さが 1 m、カメラまで 2 m なら(0.35, 0.86, 0.97) で、赤がまだ 3 割ほど残るので、浅い所は白に近い明るい色です。

赤が 1/10 になる距離は ln(10) ÷ 0.35 ≒ 6.6 m です。緑は ln(10) ÷ 0.05 ≒ 46 m、青は ln(10) ÷ 0.01 ≒ 230 m です。赤が 7 m 足らずで消える一方、青は数百 m 届くという関係が、水中が青く見える理由です。

## 光の向き

水中の光の向きは空気中の太陽の方向とは違います。光は水面で屈折し鉛直に近づく向きに曲がります。

```hlsl
// 水中の光の向き(太陽へ向かう単位ベクトル)。足した: refract で水面の法線 (0,1,0) を使う。
float3 UnderwaterSunDir() {
  float3 incident = -g_sun_dir;                                          // 光が進む向き(太陽 → 水面)
  float3 refracted = refract(incident, float3(0, 1, 0), 1.0 / g_eta);   // 空気 → 水の屈折
  return -normalize(refracted);                                          // 水中で、太陽へ向かう向き
}
```

`refract` の第 3 引数は入射側の屈折率を出射側で割った値です。空気から水に入るので 1 ÷ 1.333 です。逆にすると、光が水面で全反射する式になって、`refract` が 0 ベクトルを返し真っ黒になります。

数字で見ます。水の屈折率 1.333 のとき水面すれすれ（太陽の高度 0°）から入る光でも、水中では鉛直から asin(1 ÷ 1.333) ≒ 48.6° までしか傾きません。これが水中の最大の傾きです。太陽高度 30° なら鉛直から約 40.5°、60° なら約 22.0°、真上に近い 89° なら約 0.75° です。

つまり、地平線に近い太陽でも水中の光の筋はかなり立って見えます。空気中の夕日のような水平に近い光の筋は、水中にはありません。

## 波による揺れ

水面が波立つと水中の光の筋は揺れます。水面の法線が変わると屈折の向きが変わるからです。揺れた光が水底に当たったものが、コースティクスです。揺れる筋の作り方は [Underwater God Rays](../../water/underwater/god-rays.md) で扱います。

## よくあるミス

??? failure "水中の光の筋が、空気中と同じ色に見える"
    吸収を入れていません。`exp(-g_absorption * 距離)` を太陽から点まで点からカメラまでの両方に掛けます。片方だけだと深さか距離のどちらかで色が変わらなくなります。

??? failure "`refract` の屈折率の比を逆にして、光の向きが真っ黒になる"
    空気から水へは `1 / 1.333` です。逆にすると全反射の条件になり `refract` が 0 ベクトルを返します。`normalize` が NaN を作って画面に黒い斑点が出ます。

??? failure "吸収係数の単位が合わず光の筋が一瞬で消えるまたは全く減衰しない"
    `a` は 1/m の単位です。ゲームの 1 単位が 1 m でなければ、深さと距離を m に換算します。cm で渡すと係数が 100 倍のずれになります。

## 確かめたこと

- HLSL を `fxc`（`ps_5_0`）でコンパイルして、エラーが出ないことを確かめました。
- 数字（透過率、10 分の 1 になる距離、屈折の角度）は Python で計算した値です。
- GPU では動かしておらず描画結果は見ていません。吸収係数は説明のための一例です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空気中との違いは、色と減衰・光の向き・波の揺れの 3 つです。
    - [x] 光は 2 回減衰します。吸収係数は色ごとに持ち赤が先に消えます。
    - [x] 水中の光の向きは、屈折で鉛直から最大約 48.6° までです。

## 参考

このページは次の資料を読まずに書きました。内容は一般に知られている説明と手元で計算した数字に基づいています。

- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004。未読。
- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004。未読。
- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997。未読。
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）。未読。

## 関連ページ

- [God Rays](index.md)
- [Underwater God Rays](../../water/underwater/god-rays.md)

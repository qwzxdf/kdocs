---
title: GI Comparison
tags:
  - 描画
---

# GI Comparison

ライトマップ、ライト プローブ、SSGI、ボクセル GI、DDGI、レイトレ GI。間接光の手法はたくさんありどれも万能ではありません。ライトマップは最高品質で最も軽いのに、光が動くと使えません。SSGI は光が動いても使えますが、画面に映っていない光を拾えません。そのため実際のゲームは複数の手法を物の種類ごとに割り当てて、重ねて使います。

このページは GI の手法を横に並べて、画面の明るさの中で GI がどこを担当するかを見るためのページです。表で全方式を比べメモリを数字で見積もり直接光・間接光・AO・反射を 1 つの式に合計する HLSL を載せます。動的 GI の中での選び方は [Choosing a Method](rt-gi/choosing.md) に任せます。

!!! tip "ポイント"
    静的なシーンはライトマップとプローブが最も安く高品質です。動的なシーンは RT を前提にできるかで DDGI や ReSTIR GI と、Lumen 型やプローブの更新に分かれます。SSGI は単独で使わず近距離の補助にします。間接光の拡散は低周波なので粗い保存で足り細かい接触の暗さは AO が受け持ちます。鏡面の間接光は反射の手法に任せます。GI と AO と反射はまとめて設計します。

!!! info "このページを読む前に"
    - [Global Illumination (GI)](index.md)（このセクション全体の地図と、読む順番）

## 全方式の比較

次の表は全方式を観点ごとに並べた引く用の一覧です。各方式の仕組みはそれぞれのページにあります。

| 方式 | 動くライト | 動く物 | 画面外 | ノイズ | 実行コスト | 事前計算 | 必要な HW |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [ライトマップ](lightmaps/index.md) | ✕ | ✕（背景のみ） | ○ | なし | 極小 | 必要（重い） | なし |
| ベイク済みプローブ | ✕ | ○（受ける側） | ○ | なし | 極小 | 必要 | なし |
| [SSGI](ssgi.md) | ○ | ○ | ✕ | あり（大） | 中 | なし | なし |
| [ボクセル GI](voxel-gi.md) | ○ | ○ | ○ | 少ない | 大 | なし | 中程度 |
| [DDGI](ddgi.md) | ○ | ○ | ○ | 小（蓄積） | 中 | なし | DXR |
| [ReSTIR GI](restir.md) | ○ | ○ | ○ | あり | 大 | なし | DXR |
| [Lumen 型](lumen.md) | ○ | ○ | ○ | 小〜中 | 大 | メッシュ SDF | 中程度 |
| [Radiance Cascades](rt-gi/radiance-cascades.md) | ○ | ○ | ○ | なし | 中 | なし | なし（2D） |

ライトマップは動くライトにも動く物にも対応できませんが、ノイズがなく実行時のコストはテクスチャを引くだけです。代償はベイクに時間がかかることと光を変えるたびにやり直すことです。ベイク済みのプローブは動く物にも当たりますが、光は固定です。

SSGI、ボクセル GI、DDGI、ReSTIR GI、Lumen 型は事前計算なしで光が動きます。差は画面外の扱いとコストと必要なハードウェアに出ます。

## 物の種類ごとの出どころ

実際のゲームは 1 つの方式ですべてをまかなわず物の種類ごとに間接光の出どころを分けます。

<svg class="fig flow" viewBox="0 0 680 250" role="img" aria-label="静的な背景はライトマップ、動く物はプローブ、動くライトは直接光だけ"><defs><marker id="gcB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">物の種類ごとの、間接光の出どころ</text><rect x="14" y="40" width="230" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="129.0" y="61.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">静的な背景</text><line x1="244" y1="61" x2="300" y2="61" stroke="currentColor" stroke-width="2" marker-end="url(#gcB)"/><rect x="300" y="40" width="360" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="480.0" y="61.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ライトマップ（最高品質）</text><rect x="14" y="92" width="230" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="129.0" y="113.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">動く物・キャラ</text><line x1="244" y1="113" x2="300" y2="113" stroke="currentColor" stroke-width="2" marker-end="url(#gcB)"/><rect x="300" y="92" width="360" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="480.0" y="113.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ライト プローブ（ライトマップと揃える）</text><rect x="14" y="144" width="230" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="129.0" y="165.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">動くライト（懐中電灯・爆発）</text><line x1="244" y1="165" x2="300" y2="165" stroke="currentColor" stroke-width="2" marker-end="url(#gcB)"/><rect x="300" y="144" width="360" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="480.0" y="165.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">直接光だけ。間接光は無視かフェイク</text><rect x="14" y="196" width="230" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="129.0" y="217.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">昼夜が変わる世界</text><line x1="244" y1="217" x2="300" y2="217" stroke="currentColor" stroke-width="2" marker-end="url(#gcB)"/><rect x="300" y="196" width="360" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="480.0" y="217.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">動的 GI（DDGI・Lumen 型など）</text></svg>

静的な背景はライトマップにします。最高品質でランタイムのコストはほぼ 0 です。動く物体とキャラクターはライト プローブから受けます。このとき、ライトマップと明るさがそろうようにプローブはライトマップと同じライティングでベイクします。そろっていないと動く物だけ浮いて見えます。

動くライト（懐中電灯・爆発）は直接光だけにして、間接光は無視するかフェイクにします。昼夜が変わる世界では動的 GI が必要です。

## 数字で見積もる

方式のメモリを掛け算で見ます。

ライトマップは 4096 × 4096 = 16,777,216 テクセルです。BC6H（1 テクセル 1 バイト）なら 16 MiB、RGBA16F（8 バイト）のままなら 128 MiB で、圧縮の有無で 8 倍の差が出ます。シーン全体のライトマップはこの数枚から数十枚になります。

ライト プローブは 64 × 64 × 16 = 65,536 個の格子で、SH の L2（RGB で 27 係数）を 16 ビット（2 バイト）で持てば約 3.4 MiB です。32 ビットなら約 6.8 MiB、L1（12 係数）の 16 ビットなら約 1.5 MiB です。プローブはライトマップに比べて桁違いに小さいことが分かります。

ボクセル GI は 128³ = 2,097,152 ボクセルに RGBA16F（8 バイト）で 16 MiB です。1 方向の値だけの見積もりで、実際は方向別の値を持つ構成が多く、さらに大きくなります。

どの値も 1 つの構成の一例です。解像度とフォーマットを変えると大きく変わるので、自分の設計で掛け算してください。

## 画面の明るさを合計する

画面の明るさは複数の要素の合計です。次の図はどこにどの項を掛けるかを示します。

<svg class="fig flow" viewBox="0 0 680 270" role="img" aria-label="画面の明るさは、直接光、間接拡散、間接鏡面、発光の合計"><defs><marker id="gcA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">画面の明るさ ＝ 4 つの合計（どこに何を掛けるか）</text><rect x="12" y="50" width="150" height="66" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="87.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">直接光</text><text x="87.0" y="92.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">× 影</text><text x="87" y="138" text-anchor="middle" style="font-size:11px">Shadows</text><text x="172" y="88" text-anchor="middle" style="font-size:18px;font-weight:700">+</text><rect x="179" y="50" width="150" height="66" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="254.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">間接拡散</text><text x="254.0" y="92.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">× albedo × AO</text><text x="254" y="138" text-anchor="middle" style="font-size:11px">GI（このページ）</text><text x="339" y="88" text-anchor="middle" style="font-size:18px;font-weight:700">+</text><rect x="346" y="50" width="150" height="66" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="421.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">間接鏡面</text><text x="421.0" y="92.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">× 反射色 × スペキュラ遮蔽</text><text x="421" y="138" text-anchor="middle" style="font-size:11px">Reflections</text><text x="506" y="88" text-anchor="middle" style="font-size:18px;font-weight:700">+</text><rect x="513" y="50" width="150" height="66" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="588.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">発光</text><text x="588.0" y="92.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">そのまま</text><text x="588" y="138" text-anchor="middle" style="font-size:11px">エミッシブ</text><rect x="180" y="170" width="320" height="50" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="340.0" y="195.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">最終の色</text><line x1="87" y1="148" x2="340" y2="170" stroke="currentColor" stroke-width="1.5" marker-end="url(#gcA)"/><line x1="254" y1="148" x2="340" y2="170" stroke="currentColor" stroke-width="1.5" marker-end="url(#gcA)"/><line x1="421" y1="148" x2="340" y2="170" stroke="currentColor" stroke-width="1.5" marker-end="url(#gcA)"/><line x1="588" y1="148" x2="340" y2="170" stroke="currentColor" stroke-width="1.5" marker-end="url(#gcA)"/><text x="14" y="250" style="font-size:12px">AO は間接拡散にだけ。直接光に掛けると、影のパスと二重になる。</text></svg>

直接光は影をかけます。間接拡散光には albedo と AO を掛けます。間接鏡面光には反射の色とスペキュラ遮蔽を掛けます。発光はそのまま足します。AO は間接拡散にだけ掛け直接光には掛けません（[AO Artifacts](../ao/artifacts/index.md)）。

### 合計する HLSL

次のコードはこの合計を行うピクセル シェーダーです。間接拡散の出どころ（ライトマップ、動的 GI、アンビエント）を信頼度で重ねデバッグ用に 4 つの表示を切り替えられます。`fxc`（`ps_5_0`）で 5 つの `DEBUG_VIEW` すべてを警告なしでコンパイルして確かめました。実行はしていません。

```hlsl
// gi_compose.hlsl : 直接光 + 間接拡散 + 間接鏡面 + 発光 を合計する（ライティング パスの末尾）。
// DEBUG_VIEW: 0=通常 1=間接拡散だけ 2=AO だけ 3=間接鏡面だけ 4=GI の出どころ（色分け）
#ifndef DEBUG_VIEW
#define DEBUG_VIEW 0
#endif

Texture2D<float4> g_lightmap   : register(t0);  // ベイク済みのライトマップ（静的な背景）。a = 有効なら 1
Texture3D<float4> g_dyn_gi     : register(t1);  // 動的 GI（ボクセル / プローブの格子）から引いた放射照度。a = 信頼度
Texture2D<float>  g_ao         : register(t2);  // 画面空間 AO（1 = 遮蔽なし）
SamplerState g_linear          : register(s0);

cbuffer LightingParams : register(b0) {
  float3 g_sky_ambient;      // 最低限の環境光（真っ黒を避ける）。小さな値にする
  float  g_ao_strength;      // AO を間接拡散へ掛ける強さ。0〜1
  float3 g_grid_origin;      // 動的 GI の格子の原点（ワールド）
  float  g_grid_cell;        // 格子 1 マスの大きさ（ワールド単位）
};

struct Surface {
  float3 position;           // ワールド位置
  float3 albedo;             // 拡散反射率 0〜1
  float3 specular_color;     // 鏡面の反射色（F0 × BRDF の積分は反射側で掛け済みとする）
  float  n_dot_v;
  float  roughness;
  float2 lightmap_uv;        // UV2。動く物は無効（lightmap の a = 0）
  float3 emissive;
};
```

入力はライトマップ、動的 GI の格子、AO の 3 枚です。ライトマップと動的 GI はアルファに「この値を信頼してよいか」を持たせます。ライトマップは UV2 の外や動く物で 0、動的 GI は格子の外で 0 にします。こうすると出どころの切り替えを `if` ではなく `lerp` で書けます。`g_sky_ambient` はどの出どころも効かない場所で真っ黒にならないための最低値で、大きくしすぎると全体が白っぽくなります。

```hlsl
// スペキュラ遮蔽（Lagarde and de Rousiers 2014）。AO と同じ値を、鏡面用に直したもの。
float SpecularOcclusion(float n_dot_v, float ao, float roughness) {
  return saturate(pow(max(n_dot_v + ao, 0.0), exp2(-16.0 * roughness - 1.0)) - 1.0 + ao);
}

// 間接拡散の出どころを決める。静的ならライトマップ、動的なら格子。足りない分はアンビエント。
float3 IndirectDiffuse(Surface s, out float3 source_color) {
  float4 lm = g_lightmap.SampleLevel(g_linear, s.lightmap_uv, 0);
  float3 uvw = (s.position - g_grid_origin) / (g_grid_cell * 64.0);   // 64 マス四方の格子と仮定（一例）
  float4 dyn = g_dyn_gi.SampleLevel(g_linear, uvw, 0);

  float3 irradiance = g_sky_ambient;                       // 最後の砦: 何も無いときの最低値
  source_color = float3(0.5, 0.5, 0.5);                    // デバッグ用: 灰 = アンビエント
  irradiance = lerp(irradiance, dyn.rgb, dyn.a);           // 動的 GI を信頼度で重ねる
  source_color = lerp(source_color, float3(0.2, 0.8, 0.2), dyn.a);  // 緑 = 動的 GI
  irradiance = lerp(irradiance, lm.rgb, lm.a);             // 静的はライトマップが最優先（二重に足さない）
  source_color = lerp(source_color, float3(0.2, 0.4, 1.0), lm.a);   // 青 = ライトマップ
  return irradiance;
}
```

`IndirectDiffuse` は下から順にアンビエント、動的 GI、ライトマップを重ねます。ライトマップを最後に重ねるのは、静的な背景ではライトマップが最も正確で、動的 GI を足すと二重に明るくなるからです。足し算ではなく `lerp` にしているのが、二重掛けを防ぐ肝です。`source_color` はどの出どころが効いているかを色で見るためのデバッグ用の出力です。

`pow` の底を `max(…, 0.0)` で包むのは `fxc` が「底が負になりうる」と警告するためです（足した処理）。`n_dot_v` が 0 以上、`ao` が 0 以上なら底は負になりません。

```hlsl
float4 main(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  Surface s;
  s.position = float3(0, 0, 0);          // 実際は G バッファから再構成する
  s.albedo = float3(0.5, 0.5, 0.5);
  s.specular_color = float3(0.04, 0.04, 0.04);
  s.n_dot_v = 1.0;
  s.roughness = 0.5;
  s.lightmap_uv = uv;
  s.emissive = float3(0, 0, 0);

  float3 direct = float3(0, 0, 0);        // 直接光 × 影は別のパスで計算済みとする
  float3 indirect_specular = float3(0, 0, 0);  // 反射の合成結果（Reflection Comparison）

  float ao = lerp(1.0, g_ao.SampleLevel(g_linear, uv, 0), g_ao_strength);
  float3 source;
  float3 indirect_diffuse = IndirectDiffuse(s, source);

  // AO は間接拡散にだけ掛ける。直接光には掛けない（直接光の影は影のパスの仕事）。
  float3 diffuse_term = indirect_diffuse * s.albedo * ao;
  // 鏡面の間接光には、AO ではなくスペキュラ遮蔽を掛ける。
  float3 specular_term = indirect_specular * s.specular_color * SpecularOcclusion(s.n_dot_v, ao, s.roughness);

#if DEBUG_VIEW == 1
  return float4(indirect_diffuse * s.albedo, 1);   // AO も直接光も除く: 間接拡散の純粋な量
#elif DEBUG_VIEW == 2
  return float4(ao.xxx, 1);
#elif DEBUG_VIEW == 3
  return float4(indirect_specular, 1);
#elif DEBUG_VIEW == 4
  return float4(source, 1);                        // 青 = ライトマップ、緑 = 動的 GI、灰 = アンビエント
#else
  return float4(direct + diffuse_term + specular_term + s.emissive, 1);
#endif
}
```

`main` は確認用のダミー入力で `Surface` を作っています。実際は G バッファから再構成します。`g_ao_strength` で AO の効きを調整できるようにしておくと AO が強すぎる場面を設定だけで直せます。最後の `return` は通常時が 4 項の合計、デバッグ時が一部の項だけの表示です。デバッグ表示を用意しておくのは、GI のバグは直接光に混ざると見分けにくく、間接光だけを見ないと原因が分からないからです。

## 組み合わせの例

### 静的と動的の混合

静的な背景はライトマップ、動く物はライト プローブ、動くライトは直接光だけ接触部の暗さは [AO](../ao/index.md)、鏡面の間接光は反射プローブと SSR（[Reflections](../reflections/index.md)）です。

### 動的 GI の階層

Lumen 型の動的 GI は距離で手法を分けます。ごく近距離は画面空間のトレース、中距離は距離場のトレースとサーフェス キャッシュ、遠距離は世界空間の粗いプローブです。ノイズは時間蓄積と空間フィルタで減らします。

### 動的 GI の選び方

動的 GI の中でどれを選ぶかは [Choosing a Method](rt-gi/choosing.md) にまとめてあります。このページの表と合わせて使ってください。

## デバッグ

症状から原因を探すときは上の `DEBUG_VIEW` で間接光だけ AO だけ出どころだけを順に見ます。

- 暗い部屋が真っ黒: 間接光が効いていません。出どころの色分けで灰（アンビエントだけ）ならライトマップか動的 GI のアルファが 0 です。アンビエントの最低値も確認します。
- 壁越しに光が漏れる: プローブの可視性、配置、ボクセルの解像度、壁の厚みが原因です。壁が格子 1 マスより薄いと両側の値が混ざります。
- 動く物体だけ背景と明るさが違う: プローブとライトマップのライティングがそろっていません。同じ光でベイクし直します。
- 画面端で間接光が変わる: SSGI が画面外を拾えないためです。ベースの GI へのフォールバックを足します。
- ノイズやちらつき: 時間蓄積の履歴が捨てられているかデノイズが弱すぎます。
- ライトを動かしても反応しない: ベイク済みの GI は固定です。動的な方式が必要です。
- 間接光が二重に効いている: ライトマップと動的 GI の重複、または AO の二重掛けです。出どころの色分けで青と緑が同じ場所で重なっていないか確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 静的はライトマップとプローブ。動的は RT の有無で選ぶ
    - [x] SSGI は補助。単独では画面外で不安定
    - [x] AO は間接拡散にスペキュラ遮蔽は間接鏡面に掛ける
    - [x] 出どころの切り替えは、足し算ではなく lerp で二重掛けを防ぐ
    - [x] 間接光だけを見るデバッグ表示を用意する

## 参考

このページは同じセクションの各ページ（Lightmaps、Probe GI、SSGI、Voxel GI、DDGI、ReSTIR、Lumen and Nanite）と AO と反射のセクションをもとにまとめたものです。次の資料はこのページを書くために読み直していません。メモリの見積もりと HLSL の構成は、このページで決めた一例です。

- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018.（大域照明の章）
- Daniel Wright, Krzysztof Narkowicz, Patrick Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games.
- Zander Majercik, Jean-Philippe Guertin, Derek Nowrouzezahrai, Morgan McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019.（DDGI）
- Cyril Crassin, Fabrice Neyret, Miguel Sainz, Simon Green, Elmar Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011).
- Yaobin Ouyang, Shiqiu Liu, Markus Kettunen, Matt Pharr, Jacopo Pantaleoni, "ReSTIR GI: Path Resampling for Real-Time Path Tracing", Computer Graphics Forum (High-Performance Graphics 2021).
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014.（スペキュラ遮蔽）

## 関連ページ

- [Global Illumination (GI)](index.md)
- [Lightmaps](lightmaps/index.md)
- [Probe GI](probes/index.md)
- [DDGI](ddgi.md)
- [Choosing a Method](rt-gi/choosing.md)
- [AO](../ao/index.md)
- [Reflections](../reflections/index.md)

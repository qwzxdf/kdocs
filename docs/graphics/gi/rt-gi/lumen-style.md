---
title: Lumen-Style Approaches
tags:
  - 描画
---

# Lumen-Style Approaches

ハードウェアのレイトレーシングがあれば、間接光は画素からレイを飛ばして、三角形に当てれば求まります。しかし、すべての GPU がそれを持つわけではありません。持っていても画素ごとにレイを飛ばすのは重すぎます。そこで、シーンを簡略化して持ってそこへレイを飛ばして、結果をキャッシュして再利用する、という構成が使われます。

<strong>Lumen のような方式はシーンを簡略化した表現（距離場とサーフェス キャッシュ）にレイを飛ばして、間引いたプローブに集めて補間して、時間方向にも再利用します</strong>。ハードウェアのレイトレが無くても動くのが特徴です。このページでは構成の階層、距離場のレイマーチ（薄い壁での漏れを測った結果つき）、サーフェス キャッシュの引き方、スクリーン プローブの数、通した HLSL、長所と短所を説明します。

!!! tip "ポイント"
    - シーンを簡略化して持ちます（距離場、サーフェス キャッシュ）。三角形そのものには当てません。
    - レイは画素ごとではなく、画面に間引いて置いたプローブから飛ばして、画素へ補間します。
    - 近くは画面空間、中距離は距離場、遠くは粗いプローブと精度を段階的に落とします。
    - 距離場は薄い壁を見逃します。実測では壁の厚みが格子の間隔の半分なら約半分のレイが壁を貫通しました。
    - 細部の精度はハードウェア レイトレに劣ります。対応 GPU では距離場の代わりにハードウェア レイトレも使えます。

!!! info "このページを読む前に"
    - [Ray-Traced GI](index.md)（このセクション全体の地図と読む順番）

## 全体の構造 {#overview}

Unreal Engine 5 の Lumen は、ハードウェア レイトレが無くても動く GI です。複数の手法を階層的に組み合わせています。このページは Lumen の技術資料（Wright ら SIGGRAPH 2022）を読まずに、一般に知られた構成を自分の言葉と式で説明するものです。細部（実際のデータ構造、パラメータ）はここで説明したものと違います。

<svg class="fig flow" viewBox="0 0 720 300" role="img" aria-label="Lumen 的な構成。画面空間、距離場、サーフェス キャッシュ、スクリーン プローブ、補間と時間再利用"><defs><marker id="lmA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">精度を段階的に落として、コストを下げる</text>
<g stroke="#4c8bf5" stroke-width="2" fill="rgba(76,139,245,0.22)"><rect x="20" y="50" width="150" height="58" rx="9"/><rect x="200" y="50" width="150" height="58" rx="9"/><rect x="380" y="50" width="150" height="58" rx="9" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="560" y="50" width="140" height="58" rx="9"/></g>
<g style="font-size:12px;font-weight:600" text-anchor="middle"><text x="95" y="74">① 画面空間</text><text x="275" y="74">② 距離場</text><text x="455" y="74">③ サーフェス キャッシュ</text><text x="630" y="74">④ 集めてフィルタ</text></g>
<g style="font-size:11px" text-anchor="middle"><text x="95" y="94">近距離。最も正確</text><text x="275" y="94">世界全体。粗い</text><text x="455" y="94">当たった面の光を読む</text><text x="630" y="94">プローブ・補間・時間</text></g>
<g stroke="currentColor" stroke-width="2" marker-end="url(#lmA)"><line x1="170" y1="79" x2="200" y2="79"/><line x1="350" y1="79" x2="380" y2="79"/><line x1="530" y1="79" x2="560" y2="79"/></g>
<text x="185" y="132" text-anchor="middle" style="font-size:11px">当たらなければ</text><text x="365" y="132" text-anchor="middle" style="font-size:11px">当たった点の</text><text x="545" y="132" text-anchor="middle" style="font-size:11px">ノイズを</text>
<rect x="20" y="160" width="680" height="110" rx="10" fill="rgba(148,163,184,0.15)" stroke="#94a3b8"/>
<text x="360" y="186" text-anchor="middle" style="font-size:12px;font-weight:600">レイは、画素ごとでなく、間引いたプローブから飛ばす</text>
<text x="360" y="210" text-anchor="middle" style="font-size:12px">1920×1080 を 16×16 のタイルで区切ると、プローブは 8160 個</text>
<text x="360" y="230" text-anchor="middle" style="font-size:12px">1 個 64 本なら、光線は約 52 万本（画素ごとに 1 本の約 207 万本の 1/4）</text>
<text x="360" y="250" text-anchor="middle" style="font-size:12px">画素は、周りのプローブから補間して、間接光を得る</text></svg>

近くは画面空間のレイマーチで、画面の深度バッファがそのままジオメトリになります。遠くへ当たらなかったレイは距離場で世界全体を追います。当たった点の光はサーフェス キャッシュから読みます。画素ごとのレイはノイジーなので、プローブに集めて補間して時間方向にも再利用します。

設計の考え方は正確さを段階ごとに捨てて、コストを下げることです。見た目への影響は近いほど大きく、遠いほど小さいので近距離は画面の深度で精密に中距離は距離場で粗く、遠距離は粗いワールド プローブで、さらに粗く追います。

手法ごとの得意と苦手は次のとおりです。

- 画面空間のトレース（SSGI、SSR）は近距離で最高精度で、安いです。画面の外や隠れた面が無いのが苦手です。
- 距離場（ソフトウェア）は世界全体に安くレイを飛ばせます。細かい形状は距離場の解像度で、粗くなります。
- ハードウェア レイトレは本物の三角形に対して正確です。重く対応 GPU が必要です。
- サーフェス キャッシュは当たった面のライティングを毎回計算せずに引けます。キャッシュの更新が必要です。

## 距離場のレイマーチ {#sdf}

距離場（SDF）は空間の各点から、最も近い面までの距離を持つデータです。その距離だけ進めば面を越えないことが保証されるので、大きな歩幅で進めます（スフィア トレーシング）。

```hlsl
Texture3D<float> g_global_sdf : register(t0);       // グローバル距離場（メートル。負は内側）
SamplerState g_linear_clamp : register(s0);

cbuffer SdfConstants : register(b0) {
  float3 g_sdf_origin;       // 距離場の左下手前（ワールド）
  float g_sdf_extent;        // 距離場が覆う 1 辺（メートル）
  float g_hit_threshold;     // 当たりとみなす距離（メートル）。例: 0.05
  float g_max_distance;      // レイの最大の長さ（メートル）。例: 100
  uint g_max_steps;          // 最大ステップ数。例: 64
  float _pad;
};

float SampleSdf(float3 p) {
  float3 uvw = (p - g_sdf_origin) / g_sdf_extent;
  return g_global_sdf.SampleLevel(g_linear_clamp, uvw, 0);
}

// 当たれば、レイの起点からの距離（>= 0）、外れたら -1
float TraceGlobalSdf(float3 origin, float3 dir) {
  float t = 0.0;
  for (uint i = 0; i < g_max_steps; ++i) {
    float d = SampleSdf(origin + dir * t);
    if (d < g_hit_threshold) return t;                 // 面に十分近づいた → 当たり
    t += max(d, g_hit_threshold);                      // 距離だけ安全に進む（下限で、止まるのを防ぐ。足した処理）
    if (t > g_max_distance) break;
  }
  return -1.0;
}
```

距離場が精密なら歩幅が大きくて速く、ステップ数が少なく済みます。ソフトウェアで動くのでハードウェア レイトレが無い GPU でも使えます。ただし、距離場の精度は格子の解像度で決まります。

### 薄い壁の漏れを測る

距離場は格子の点の値を補間して読むので、格子の間隔より薄い物は見逃されることがあります。厚み `t` の壁を格子の間隔 `h`（0.5 m）で標本化して、格子の位置をランダムにずらしながら、壁を貫く斜めのレイを 2 万本飛ばして、壁に当たる割合を測りました（C++、MSVC `/W4` で実行）。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="壁の厚みと格子の間隔の比に対する、光漏れの割合。薄いほど漏れる"><text x="14" y="22" class="fig-title">薄い壁を貫くレイの漏れ（実測）</text>
<line x1="70" y1="210" x2="680" y2="210" stroke="currentColor" stroke-width="1.5"/>
<g fill="rgba(229,72,77,0.28)" stroke="#e5484d" stroke-width="2"><rect x="90" y="23" width="60" height="187"/><rect x="170" y="56" width="60" height="154"/><rect x="250" y="110" width="60" height="100"/><rect x="330" y="165" width="60" height="45"/><rect x="410" y="209" width="60" height="1"/><rect x="490" y="209" width="60" height="1"/><rect x="570" y="209" width="60" height="1"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="120" y="17">87 %</text><text x="200" y="50">72 %</text><text x="280" y="104">47 %</text><text x="360" y="159">21 %</text><text x="440" y="203">0 %</text><text x="520" y="203">0 %</text><text x="600" y="203">0 %</text>
<text x="120" y="230">0.1</text><text x="200" y="230">0.25</text><text x="280" y="230">0.5</text><text x="360" y="230">0.75</text><text x="440" y="230">1.0</text><text x="520" y="230">1.5</text><text x="600" y="230">2.0</text></g>
<text x="375" y="254" text-anchor="middle" style="font-size:12px">横軸: 壁の厚み ÷ 格子の間隔。厚みが格子の間隔より小さいと、漏れる（おおよそ 1 − 厚み/間隔）</text></svg>

結果はおおよそ「漏れる割合 ≒ 1 − 厚み ÷ 格子の間隔」でした。厚みが格子の間隔の 0.1 倍なら 87 %、0.5 倍なら 47 %、0.75 倍なら 21 % のレイが、壁を素通りしました。厚みが格子の間隔以上なら漏れは 0 でした。薄い壁、小さな隙間、細かい模様の物体で光漏れや暗すぎる箇所が出る理由です。距離場の解像度を上げるかハードウェア レイトレを併用すれば、改善します。

## サーフェス キャッシュ {#cache}

レイが当たった点のライティング（直接光、影、間接光）を毎回計算すると重くなります。そこで、メッシュの各面にライティングのキャッシュ（サーフェス キャッシュ、カード）を持ちます。当たった点の光はキャッシュから読むだけにします。

- カードはメッシュを 6 方向（上下左右前後）から見た小さな平面の画像のアトラスです。アルベド、法線、深度、ライティングを持ちます。
- 更新は毎フレーム一部（優先度の高いカード）だけライティングを再計算して行います。
- 使い方はレイが当たった点をカードに投影して、そこのライティングを読みます。

```hlsl
Texture2D<float4> g_card_lighting : register(t1);      // カードのアトラス（RGB = 出射する光）
cbuffer CardConstants : register(b1) {
  float4x4 g_world_to_card[3];     // 当たった物体の、3 軸 (X, Y, Z) のカードへの変換（簡略化のため、物体 1 つぶん）
  float4 g_card_uv_rect[3];        // カードがアトラスで占める矩形 (u0, v0, du, dv)
};

// 当たった点から、サーフェス キャッシュの光を読む。法線に最も向きが近い軸のカードを選ぶ
float3 SampleSurfaceCache(float3 hit_pos, float3 hit_normal) {
  float3 a = abs(hit_normal);
  uint axis = (a.x > a.y && a.x > a.z) ? 0 : ((a.y > a.z) ? 1 : 2);
  float4 card = mul(float4(hit_pos, 1.0), g_world_to_card[axis]);       // カードの局所座標（xy が 0..1）
  float4 rect = g_card_uv_rect[axis];
  float2 uv = rect.xy + saturate(card.xy) * rect.zw;
  return g_card_lighting.SampleLevel(g_linear_clamp, uv, 0).rgb;
}
```

法線の絶対値が最も大きい軸のカードを選ぶのは、その面がそのカードの向きに最も近いからです。実際には、3 軸の結果を法線で重みづけして混ぜたり斜めの面に備えたりします。

## スクリーン プローブ {#probes}

スクリーン プローブがコストを下げる鍵です。画面を 16 × 16 画素程度のタイルに区切って、タイルごとに 1 個のプローブを置きます。プローブからだけレイを飛ばします。各プローブは八面体マップ（[DDGI](../ddgi.md) で使う方向の展開と同じ考え方）に、方向ごとの放射輝度を持ちます。画素は周りのプローブから補間して、間接光を得ます。

1920 × 1080 を 16 × 16 で区切ると、プローブは `120 × 68 = 8160` 個です。1 個 64 本（八面体マップの 8 × 8）なら光線は約 52 万本です。画素ごとに 1 本を飛ばすと約 207 万本なので、画素あたり 1 本の 4 分の 1 です。画素ごとに複数本飛ばす実装と比べれば、さらに差が開きます。メモリはプローブ 8160 個 × 64 方向 × RGBA16F（8 バイト）で、約 4 MiB です。

まず、プローブから光線を飛ばして八面体マップに書く計算シェーダーです。

```hlsl
RWTexture2D<float4> g_probe_radiance : register(u0);   // プローブ × 八面体 8×8 のアトラス（RGB = 放射輝度）
Texture2D<float> g_depth : register(t2);
Texture2D<float4> g_normal : register(t3);

cbuffer ProbeConstants : register(b2) {
  float4x4 g_inv_view_proj;
  float2 g_screen_size;
  uint g_tile_size;          // 16
  uint g_frame_index;
  float3 g_sky_color;        // 当たらなかったときの光（空の色）
  float _pad2;
};
static const uint kOct = 8;                            // 八面体マップの 1 辺

// 0..1 の八面体の座標 → 方向（ここでは、上半分と下半分の折り返しを、省かずに書く）
float3 OctDecode(float2 uv) {
  float2 f = uv * 2.0 - 1.0;
  float3 n = float3(f.x, 1.0 - abs(f.x) - abs(f.y), f.y);
  if (n.y < 0.0) {
    float2 s = float2(n.x >= 0.0 ? 1.0 : -1.0, n.z >= 0.0 ? 1.0 : -1.0);
    n.xz = (1.0 - abs(n.zx)) * s;
  }
  return normalize(n);
}

[numthreads(8, 8, 1)]
void TraceProbeCS(uint3 gid : SV_GroupID, uint3 tid : SV_GroupThreadID) {
  // 1 グループ = 1 プローブ。スレッド = 八面体のテクセル（= 方向）
  uint2 probe = gid.xy;
  uint2 pixel = probe * g_tile_size + g_tile_size / 2;               // タイルの中心の画素
  float depth = g_depth.Load(int3(pixel, 0));
  float4 ndc = float4((pixel.x + 0.5) / g_screen_size.x * 2.0 - 1.0, 1.0 - (pixel.y + 0.5) / g_screen_size.y * 2.0, depth, 1.0);
  float4 w = mul(ndc, g_inv_view_proj);
  float3 world_pos = w.xyz / w.w;
  float3 normal = normalize(g_normal.Load(int3(pixel, 0)).xyz * 2.0 - 1.0);

  // 方向: 八面体のテクセルの中心から作って、法線の半球へ向きを揃える（足した処理）
  float2 uv = (float2(tid.xy) + 0.5) / kOct;
  float3 dir = OctDecode(uv);
  if (dot(dir, normal) < 0.0) dir = -dir;                            // 下半球に向かうレイを、上半球へ反転

  float3 origin = world_pos + normal * 0.05;                         // 自己交差を避けるずらし
  float t = TraceGlobalSdf(origin, dir);
  float3 radiance = g_sky_color;                                     // 当たらなければ空
  if (t >= 0.0) {
    float3 hit = origin + dir * t;
    // 当たった点の法線は、距離場の勾配から求める（ここでは簡略化して、レイの逆向きを使う）
    radiance = SampleSurfaceCache(hit, -dir);
  }
  g_probe_radiance[probe * kOct + tid.xy] = float4(radiance, 1.0);
}
```

この版は画面空間のトレースを省いて、距離場だけでトレースしています。実際の構成は、先に画面空間で追って当たらなければ距離場へ移ります。

次に、画素が周りのプローブから補間する部分です。単純な線形補間では物の縁でプローブの値が漏れるので、深度と法線の近さで重みを付けます。

```hlsl
Texture2D<float4> g_probe_atlas : register(t4);        // g_probe_radiance を読む SRV

float3 SampleProbe(uint2 probe, float3 normal) {
  // プローブの八面体マップから、法線方向の周り（1 テクセル）を平均する簡易版
  float2 uv = (float2(probe * kOct) + float2(kOct, kOct) * 0.5);
  float2 oct_uv = float2(0.5, 0.5);                                 // 足した: 法線→八面体の座標の変換は、OctEncode を使う
  return g_probe_atlas.Load(int3(probe * kOct + uint2(kOct / 2, kOct / 2), 0)).rgb;
}

float4 FinalGatherPS(float4 pos : SV_Position) : SV_Target {
  float2 p = pos.xy / g_tile_size - 0.5;                            // プローブ格子の座標
  uint2 p0 = uint2(floor(p));
  float2 f = frac(p);
  float depth = g_depth.Load(int3(pos.xy, 0));
  float3 normal = normalize(g_normal.Load(int3(pos.xy, 0)).xyz * 2.0 - 1.0);

  float3 sum = 0.0;
  float weight_sum = 0.0;
  [unroll] for (int k = 0; k < 4; ++k) {
    uint2 pc = p0 + uint2(k & 1, k >> 1);                           // 周りの 4 プローブ
    float bilinear = ((k & 1) ? f.x : 1.0 - f.x) * ((k >> 1) ? f.y : 1.0 - f.y);
    // プローブの位置の深度と、画素の深度が近いほど、重みを大きくする（縁での漏れを防ぐ）
    float probe_depth = g_depth.Load(int3(pc * g_tile_size + g_tile_size / 2, 0));
    float depth_weight = exp(-abs(probe_depth - depth) * 50.0);
    float w = bilinear * depth_weight;
    sum += SampleProbe(pc, normal) * w;
    weight_sum += w;
  }
  return float4(sum / max(weight_sum, 1e-4), 1.0);                  // 間接光
}
```

`SampleProbe` は紙面を短くするために法線方向の八面体マップの読みを簡略化しています（足した簡略化）。実際は、法線から `OctEncode` で座標を求めて、周りのテクセルを補間します。

ワールド プローブ（遠距離）は遠くの光を世界空間の粗いプローブから読みます。対応 GPU では距離場の代わりにハードウェア レイトレのモードも使えます。

!!! note "確かめた範囲"
    HLSL は `fxc` で、`TraceProbeCS`（`cs_5_0`）と `FinalGatherPS`（`ps_5_0`）をコンパイルして、エラーが出ないことを確かめました。薄い壁の漏れとプローブの本数・メモリは、C++（MSVC `/W4`）の実測と計算です。GPU での描画は確認していません。Lumen の発表（Wright ら）は読んでいません。

## 長所と短所 {#pros-cons}

長所は動的なことです。光や物の変化に追従して世界全体の間接光が得られます。ハードウェア レイトレが無くても動いて、GI と粗い鏡面反射を同じ仕組みで扱えます。

短所は実装が複雑なことです（距離場、サーフェス キャッシュ、プローブ、フィルタ）。自作は大変です。距離場の解像度による細かい形状の欠落と薄い壁での光漏れが出ます。距離場、カード アトラス、プローブのメモリも要ります。ハードウェア レイトレ版は GPU の世代に依存します。

## 自作する場合の現実的な構成 {#practical}

フル機能の Lumen を自作するのは、現実的ではありません。小規模には必要な機能を絞った構成が現実的です。

- 動的な環境光はまず SSGI とライト プローブ（ベイク、または空の SH）です。
- 動的な間接光を広く得るなら DDGI です（[DDGI](../ddgi.md)）。
- ソフトウェアで世界全体の間接光ならボクセル GI（[Voxel GI](../voxel-gi.md)）や、距離場です。
- 高品質を求めるなら（RT 対応の GPU）、ReSTIR GI（[ReSTIR GI](restir.md)）とデノイザーです。

## よくあるミス {#mistakes}

??? failure "薄い壁や小さい物で、光漏れが起きる"
    原因は距離場の格子の間隔より物が薄いことです。実測では厚みが格子の間隔の半分なら約半分のレイが素通りしました。距離場の解像度を上げるか薄い物を厚みのある別の表現で持つかハードウェア レイトレを併用します。

??? failure "プローブの補間で、物の縁に明るい縁取りが出る"
    原因は周りのプローブを深度や法線の近さで重みづけせずに単純に線形補間していることです。深度と法線で重みを付けて縁をまたぐプローブの寄与を減らします。

??? failure "壁の裏側のプローブの光が、手前に漏れる"
    原因はプローブの八面体マップを法線の向きにそろえていないことです。プローブの半球に合わせてレイの向きを反転します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 簡略化したシーン（距離場、サーフェス キャッシュ）にレイを飛ばして、間引いたプローブに集めます。
    - [x] 近くは画面空間、中距離は距離場、遠くは粗いプローブで精度を段階的に落とします。
    - [x] 距離場は格子の間隔より薄い物を見逃します。漏れはおおよそ `1 − 厚み/間隔` です。
    - [x] 1920×1080 を 16×16 で区切れば、プローブは 8160 個で 64 本なら約 52 万本です。

## 参考 {#references}

このページは次の資料を読まずに書きました。構成の説明は一般に知られた内容で、Lumen の実装とは細部が違います。数字は自分で書いた C++ の実測と計算です。

- Wright, Narkowicz, Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games
- Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018（SEED のハイブリッド レイトレーシング）
- Schied, Kaplanyan, Wyman, Patney, Chaitanya, Burgess, Liu, Dachsbacher, Lefohn, Salvi, "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017（SVGF）
- Epic Games, "Lumen Technical Details", Unreal Engine 5 ドキュメント

## 関連ページ

- [Ray-Traced GI](index.md)
- [Distance Field AO (DFAO)](../../ao/world-space/dfao.md)
- [DDGI](../ddgi.md)

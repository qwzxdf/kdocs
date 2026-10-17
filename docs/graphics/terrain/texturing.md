---
title: 地形のテクスチャ
tags:
  - 描画
---

# 地形のテクスチャ

**広大な地形全体を、1 枚の巨大なテクスチャで覆う**と、**メモリが足りず、近づくとぼやけます**。そこで**小さな繰り返しテクスチャ（草・土・岩・雪）を何種類か用意**し、**場所ごとの重み（スプラット マップ）で混ぜる**のが**定番**です。このページでは、**スプラット マッピング・高さによるブレンド・急斜面のトライプラナー・タイルの繰り返しを隠す方法・仮想テクスチャ**を説明します。

!!! tip "ポイント"
    - 地面 ＝ <strong>数種類の繰り返しテクスチャを、重みマップ（スプラット）で混ぜる</strong>。
    - 重みは<strong>合計 1</strong>。<strong>RGBA の 4 チャンネルで、4 種類</strong>。<strong>それ以上はマップを複数枚</strong>。
    - 単純な線形ブレンドは<strong>境目がぼやける</strong>。<strong>高さ（凹凸）を使ったブレンド</strong>で<strong>境が自然</strong>に。
    - <strong>急斜面は、XZ の投影だと引き伸ばされる</strong>。<strong>トライプラナー</strong>（<strong>3 方向から投影して混ぜる</strong>）で<strong>解決</strong>。
    - <strong>繰り返しは目立つ</strong>：<strong>2 つのスケールを重ねる・タイルを回転する</strong>などで<strong>隠す</strong>。
    - <strong>仮想テクスチャ</strong>は<strong>見える所だけ、必要な解像度で読み込む</strong>。

## スプラット マッピング

**スプラット マップ**は、**各位置で「どのテクスチャをどれだけ使うか」を表す重みテクスチャ**です。**RGBA の 4 チャンネルで 4 種類**を**扱います**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="スプラット マッピング">
<text x="20" y="24" class="fig-title">スプラット マッピング：重みマップで、複数の地面テクスチャを混ぜる</text>
<rect x="40" y="60" width="140" height="100" fill="#2ea043" fill-opacity="0.5" stroke="currentColor" stroke-opacity="0.5"/>
<rect x="190" y="60" width="140" height="100" fill="#a0763c" fill-opacity="0.6" stroke="currentColor" stroke-opacity="0.5"/>
<rect x="340" y="60" width="140" height="100" fill="#8a8a8a" fill-opacity="0.6" stroke="currentColor" stroke-opacity="0.5"/>
<rect x="490" y="60" width="140" height="100" fill="#f0f4f8" fill-opacity="0.8" stroke="currentColor" stroke-opacity="0.5"/>
<text x="110" y="180" text-anchor="middle" style="font-size:12px">草（R）</text>
<text x="260" y="180" text-anchor="middle" style="font-size:12px">土（G）</text>
<text x="410" y="180" text-anchor="middle" style="font-size:12px">岩（B）</text>
<text x="560" y="180" text-anchor="middle" style="font-size:12px">雪（A）</text>
<text x="400" y="52" text-anchor="middle" style="font-size:12px">繰り返しテクスチャ</text>
<text x="700" y="100" text-anchor="middle" style="font-size:13px">× 重み</text>
<text x="700" y="124" text-anchor="middle" style="font-size:13px">（スプラット）</text>
<text x="700" y="148" text-anchor="middle" style="font-size:13px">＝ 地面の色</text>
</svg>

```hlsl
Texture2D<float4> splat_map : register(t0);
Texture2DArray<float4> albedo_array : register(t1);
Texture2DArray<float4> normal_array : register(t2);

float4 weights = splat_map.Sample(linear_clamp, terrain_uv);
weights /= (weights.r + weights.g + weights.b + weights.a + 1e-5);

float2 tile_uv = world_position.xz * tile_scale;
float3 color = 0;
float3 normal_ts = 0;
for (int i = 0; i < 4; ++i) {
  float3 uvw = float3(tile_uv, i);
  color += albedo_array.Sample(linear_wrap, uvw).rgb * weights[i];
  normal_ts += (normal_array.Sample(linear_wrap, uvw).xyz * 2.0 - 1.0) * weights[i];
}
normal_ts = normalize(normal_ts);
```

| 点 | 説明 |
| --- | --- |
| **スプラット マップは地形全体** | **解像度は高さマップと同程度かそれ以上**。**低解像度だと境目がぼやける** |
| **テクスチャ配列** | **層ごとに別のテクスチャを持たず、`Texture2DArray` にまとめる**（**スロットを節約**） |
| **重みの正規化** | **合計を 1 にする**（**暗くなる・明るくなる**のを防ぐ） |
| **タイルの UV** | **ワールド座標 × スケール**。**メッシュの UV に依らず、継ぎ目が出ない** |
| **層数が多い** | **スプラット マップを複数枚にして、重みの大きい上位 4 つだけ読む** |
| **法線・粗さも混ぜる** | **アルベドだけでなく、法線・粗さ・AO も同じ重みで** |

## 重みを決める

| 方法 | 内容 |
| --- | --- |
| **手描き** | **地形エディタでブラシで塗る** |
| **ルールで自動** | **高さ・傾きから決める**（下の表） |
| **侵食の結果から** | **堆積した所は土・砂、削られた所は岩**（[地形の生成](generation.md)） |

| 条件 | 地面 |
| --- | --- |
| **傾きが緩やか・低い** | **草** |
| **傾きが急** | **岩** |
| **高い所** | **雪** |
| **水の近く** | **砂・泥** |

```hlsl
float slope = 1.0 - saturate(normal.y);
float rock = smoothstep(0.35, 0.55, slope);
float snow = smoothstep(snow_line, snow_line + 20.0, world_position.y) * (1.0 - rock);
float grass = (1.0 - rock) * (1.0 - snow);
```

**ルールで基礎を作り、手描きの重みを足して調整する**のが**実用的**です。

## 高さによるブレンド

**重みの線形ブレンドは、境目がぼんやり混ざって不自然**です。**実際の地面は、「石の隙間に土が入り込む」ように凹凸に沿って境ができます**。**各テクスチャの高さ（ハイトマップ）を足し込んでから、一番高い層を優先**すると**自然な境目**になります。

```hlsl
float4 heights = float4(
  height_array.Sample(linear_wrap, float3(tile_uv, 0)).r,
  height_array.Sample(linear_wrap, float3(tile_uv, 1)).r,
  height_array.Sample(linear_wrap, float3(tile_uv, 2)).r,
  height_array.Sample(linear_wrap, float3(tile_uv, 3)).r);

float4 blended = weights + heights * height_strength;
float max_value = max(max(blended.r, blended.g), max(blended.b, blended.a)) - blend_depth;
float4 final_weights = max(blended - max_value, 0.0);
final_weights /= (final_weights.r + final_weights.g + final_weights.b + final_weights.a);
```

| 点 | 説明 |
| --- | --- |
| **`blend_depth`** | **境目の幅**（0.1 程度）。**小さいと鋭く、大きいとぼやける** |
| **高い層が勝つ** | **凸な所が先に現れ、凹んだ所に他の層が残る** |
| **ハイトマップが必要** | **テクスチャごとに高さのチャンネルを用意**（**法線マップのアルファなどに詰める**） |

## トライプラナー

**XZ 平面に投影する UV は、急斜面や崖でテクスチャが縦に引き伸ばされます**。**X・Y・Z の 3 方向から投影した 3 枚を、法線の向きで混ぜる**のが**トライプラナー マッピング**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="トライプラナー">
<text x="20" y="24" class="fig-title">トライプラナー：面の向きに応じて、3 方向の投影を混ぜる</text>
<polyline fill="#a0763c" fill-opacity="0.3" stroke="currentColor" stroke-opacity="0.7" stroke-width="2" points="60,190 220,190 300,70 440,70 520,190 720,190"/>
<g stroke="#4c8bf5" stroke-width="2"><line x1="120" y1="40" x2="120" y2="190"/><line x1="160" y1="40" x2="160" y2="190"/><line x1="200" y1="40" x2="200" y2="190"/></g>
<text x="60" y="34" style="font-size:12px;fill:#4c8bf5">上から投影：平らな所は良い</text>
<g stroke="#e5484d" stroke-width="2"><line x1="260" y1="110" x2="320" y2="110" /><line x1="262" y1="140" x2="320" y2="140"/></g>
<text x="330" y="150" style="font-size:12px;fill:#e5484d">崖は上から投影すると引き伸ばされる</text>
<g stroke="#2ea043" stroke-width="2"><line x1="420" y1="95" x2="470" y2="95" stroke-dasharray="3 3"/><line x1="440" y1="130" x2="490" y2="130" stroke-dasharray="3 3"/></g>
<text x="450" y="64" style="font-size:12px;fill:#2ea043">横から投影すれば良い</text>
</svg>

```hlsl
float3 TriplanarWeights(float3 normal, float sharpness) {
  float3 w = pow(abs(normal), sharpness);
  return w / (w.x + w.y + w.z);
}

float3 Triplanar(Texture2D tex, float3 world_position, float3 normal, float scale) {
  float3 w = TriplanarWeights(normal, 4.0);
  float3 x = tex.Sample(linear_wrap, world_position.zy * scale).rgb;
  float3 y = tex.Sample(linear_wrap, world_position.xz * scale).rgb;
  float3 z = tex.Sample(linear_wrap, world_position.xy * scale).rgb;
  return x * w.x + y * w.y + z * w.z;
}
```

| 点 | 説明 |
| --- | --- |
| **サンプル数が 3 倍** | **3 方向から 1 回ずつ読む**ので**重い**。**急斜面（岩）の層だけに使う** |
| **`sharpness`** | **大きいほど、方向の切り替えが鋭い** |
| **法線マップも要注意** | **接線空間でなくワールド空間の法線に直す**（**投影ごとに軸を入れ替えて、法線を戻す**） |
| **傾きで使い分け** | **平らな所は 1 方向（安い）、急な所だけ 3 方向** |

## 繰り返し（タイリング）を隠す

**繰り返しテクスチャは、広い範囲に貼ると同じ模様の並びが目立ちます**。

| 工夫 | 内容 |
| --- | --- |
| **2 つのスケールを重ねる** | **大きさの違う 2 枚を混ぜる**（**周期がずれる**） |
| **近景・遠景のスケール** | **距離で細かいタイルと大きなタイルを切り替える** |
| **タイルごとにランダムに回す** | **セルごとに回転・オフセットを変える**（**ハッシュで決める**）。**境でブレンド** |
| **マクロ バリエーション** | **低周波のノイズで色を少しずらす** |
| **ディテール テクスチャ** | **近づいたときだけ、細かい模様を重ねる** |

```hlsl
float2 uv_near = world_position.xz * 0.5;
float2 uv_far = world_position.xz * 0.043;
float3 near_color = albedo.Sample(linear_wrap, uv_near).rgb;
float3 far_color = albedo.Sample(linear_wrap, uv_far).rgb;
float3 color = near_color * far_color * 2.0;
```

**2 枚を掛けて 2 倍**にすると、**平均の明るさが保たれます**。

## 異方性フィルタリング

**斜めから見る地面**は、**テクスチャが縦に潰れる**ので、**ぼやけます**。<strong>異方性フィルタリング（16x など）</strong>を**有効**にすると**遠くの地面もくっきり**します。**地形ではほぼ必須**です。

## 仮想テクスチャ

**地形全体に固有のテクスチャを描きたい**（**手描きの道・足跡・建物の跡**）とき、<strong>巨大なテクスチャ（例：128K×128K）</strong>が**必要**になりますが**メモリに全部は載せられません**。**仮想テクスチャ**（**Sparse Virtual Texture**）は、**見える部分を必要な解像度でタイル単位に読み込み**ます。

| 要素 | 内容 |
| --- | --- |
| **タイル** | **テクスチャを、128×128 などのページに分割** |
| **フィードバック パス** | **画面の各ピクセルがどのページ・ミップを必要とするかを書き出す** |
| **ページ テーブル** | **仮想アドレスから、物理テクスチャ（キャッシュ）の位置へ** |
| **キャッシュ** | **物理テクスチャに読み込んだタイルを置く**（**LRU で入れ替え**） |
| **読み込み** | **足りないタイルをディスクから読み、必要なら生成** |

<strong>ランタイム仮想テクスチャ（RVT）</strong>は、**スプラットのブレンド結果を、タイルとしてキャッシュ**します。**毎ピクセルのスプラット計算が、キャッシュの読み出し 1 回になり**、**描画が軽くなります**。

| 利点 | 欠点 |
| --- | --- |
| **ピクセルごとの合成を省略** | **仕組みが複雑** |
| **地形全体の巨大な固有テクスチャ** | <strong>フィードバックの遅延で、一瞬ぼやける（ポップイン）</strong> |
| **デカールを焼き込める** | **メモリの管理が必要** |

## 地形のデカールと道

| 要素 | 内容 |
| --- | --- |
| **道・小道** | **スプラット マップにスプライン沿いに塗る** |
| **足跡・タイヤの跡** | **スプラット／デカールに描き込む** |
| **焼け跡・血痕** | **デカール**を**投影** |
| **整地** | **高さマップも同時に整える** |

## よくあるミス

??? failure "重みの合計が 1 でなく、地面が暗くなる／明るくなる"
    **重みを正規化する**。

??? failure "崖のテクスチャが縦に伸びる"
    **急斜面はトライプラナー**で**投影**する。

??? failure "法線マップを、トライプラナーでそのまま混ぜて、光り方が崩れる"
    **ワールド空間の法線に直してから混ぜる**。**投影ごとに軸を入れ替える**。

??? failure "遠くで、タイルの繰り返しが目立つ"
    **2 つのスケールを重ねる**。**マクロ バリエーション**を足す。

??? failure "遠くの地面がぼやける"
    **異方性フィルタリングを有効**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 地面 ＝ <strong>繰り返しテクスチャを、スプラット マップの重みで混ぜる</strong>。<strong>重みは正規化</strong>
    - [x] <strong>高さ（ハイトマップ）を使うブレンド</strong>で<strong>境が自然</strong>
    - [x] <strong>急斜面はトライプラナー</strong>。<strong>法線は軸に注意</strong>
    - [x] <strong>繰り返しは、2 スケールの重ねとバリエーションで隠す</strong>
    - [x] <strong>仮想テクスチャ</strong>は<strong>見える所だけ、必要な解像度で</strong>

## 参考

- Barrett, "Sparse Virtual Textures"（GDC 2008）
- van Waveren, "id Tech 5 Challenges: From Texture Virtualization to Massive Parallelization"（2009）
- Mikkelsen, "Practical Real-Time Hex-Tiling"（JCGT 2022）

## 関連ページ

- [地形](index.md)
- [高さマップとメッシュ](heightmap-mesh.md)
- [草と木](vegetation.md)
- [地形の生成](generation.md)

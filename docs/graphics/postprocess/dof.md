---
title: 被写界深度（DOF）
tags:
  - 描画
---

# 被写界深度（DOF）

**カメラ**は**ピントを合わせた距離の物だけがシャープ**で、**手前や奥はぼやけます**。これが**被写界深度**（Depth of Field、DOF）です。**ゲームのカメラは、ピンホールカメラ**（全部にピントが合う）なので**ぼかしを後から加えて**、**写真・映画的な奥行きと視線の誘導**を作ります。<strong>ボケの量は距離から計算できます（錯乱円）</strong>。このページでは、**ボケの物理（錯乱円）・ぼかしの実装（ギャザー／スキャッター）・前景と背景の扱い・ボケの形・コスト**を説明します。

!!! tip "ポイント"
    - ボケの大きさ ＝ <strong>錯乱円（Circle of Confusion、CoC）</strong>。<strong>ピント面から離れるほど大きい</strong>。
    - CoC は<strong>焦点距離・絞り（F 値）・ピント距離・被写体距離</strong>から<strong>式で出せる</strong>。
    - 実装の核は<strong>「CoC に応じた半径で、周りをぼかす」</strong>。<strong>背景（奥）</strong>と<strong>前景（手前）</strong>で<strong>扱いが違う</strong>。
    - <strong>ギャザー</strong>（周りを集める）は<strong>簡単</strong>、<strong>スキャッター</strong>（明るい点をスプライトで広げる）は<strong>ボケの形が綺麗</strong>。
    - <strong>ボケの形（絞りの羽根）</strong>は<strong>ポイント サンプルの配置</strong>で決まる。
    - <strong>前景のぼけ</strong>が<strong>鮮明な背景に、にじみ出す</strong>ようにするのが<strong>難しい点</strong>。

## 錯乱円（CoC）

**レンズがピント面にない点を撮る**と、<strong>像が点ではなく「円」</strong>になります。この円が**錯乱円**で**ボケの大きさ**を決めます。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="錯乱円">
<text x="20" y="24" class="fig-title">ピント面にない点は、センサー上で円（錯乱円）になる</text>
<line x1="60" y1="130" x2="720" y2="130" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/>
<line x1="330" y1="60" x2="330" y2="200" stroke="currentColor" stroke-width="4"/><text x="300" y="52" style="font-size:12px">レンズ</text>
<circle cx="80" cy="130" r="6" fill="rgba(229,170,40,0.9)" stroke="currentColor" stroke-width="2"/><text x="40" y="156" style="font-size:12px">物体（ピント外）</text>
<line x1="80" y1="130" x2="330" y2="82" stroke="currentColor"/><line x1="80" y1="130" x2="330" y2="178" stroke="currentColor"/>
<line x1="330" y1="82" x2="560" y2="130" stroke="currentColor"/><line x1="330" y1="178" x2="560" y2="130" stroke="currentColor"/>
<line x1="640" y1="70" x2="640" y2="190" stroke="currentColor" stroke-width="3"/><text x="610" y="62" style="font-size:12px">センサー</text>
<line x1="330" y1="82" x2="640" y2="104" stroke="currentColor" stroke-dasharray="2 3" opacity="0.6"/><line x1="330" y1="178" x2="640" y2="156" stroke="currentColor" stroke-dasharray="2 3" opacity="0.6"/>
<line x1="650" y1="104" x2="650" y2="156" stroke="#e5484d" stroke-width="3"/><text x="660" y="134" style="font-size:12px;fill:#e5484d;font-weight:700">錯乱円（CoC）</text>
<text x="300" y="226" style="font-size:12px">ピント面の像はセンサーの手前 → センサー上では広がる</text>
</svg>

**薄いレンズの式**から、**CoC の直径**（**センサー上の長さ**）が**導けます**。

<div class="formula">CoC = A · |S₂ − S₁| / S₂ · f / (S₁ − f)　（A = f / N）</div>

| 記号 | 意味 |
| --- | --- |
| **f** | **焦点距離**（例：50 mm） |
| **N** | **F 値**（絞り）。<strong>小さいほど開放（ボケが大きい）</strong> |
| **A = f / N** | **絞りの口径** |
| **S₁** | **ピントを合わせた距離** |
| **S₂** | **被写体の距離** |

| 要因 | ボケの大きさへの影響 |
| --- | --- |
| <strong>絞りを開く（F 値を小さく）</strong> | **大きくなる** |
| <strong>焦点距離を長く（望遠）</strong> | **大きくなる** |
| **被写体を近づける** | **大きくなる** |
| **ピント面から離れる** | **大きくなる**（**背景は無限遠で飽和**） |

### HLSL

```hlsl
cbuffer DofConstants : register(b0) {
  float focal_length;
  float f_number;
  float focus_distance;
  float sensor_height;
  float image_height_in_pixels;
  float max_coc_in_pixels;
  float2 padding;
};

float CircleOfConfusion(float linear_depth) {
  float aperture = focal_length / f_number;
  float coc = aperture * abs(linear_depth - focus_distance) / linear_depth *
              focal_length / (focus_distance - focal_length);
  return coc;
}

float SignedCocPixels(float linear_depth) {
  float coc = CircleOfConfusion(linear_depth);
  float pixels = coc / sensor_height * image_height_in_pixels;
  float sign_value = linear_depth < focus_distance ? -1.0 : 1.0;
  return sign_value * min(pixels, max_coc_in_pixels);
}
```

| 点 | 説明 |
| --- | --- |
| **`linear_depth`** | **カメラからの線形な距離**（ビュー空間の z）。**非線形の深度バッファの値は、不可** |
| **符号** | **前景（ピントより手前）は負、背景（奥）は正**。**前景と背景を区別して扱う**ため |
| **センサー高さで割って、画素数に** | **物理量（mm）を、画像の画素数**に**換算** |
| **`max_coc_in_pixels`** | <strong>ボケの最大半径（画素）</strong>。**コストの上限**を決める（例：20〜50 画素） |

**アーティスト向け**には、<strong>物理式ではなく、「ピント距離・ピント範囲・ぼかしの強さ」</strong>の**簡易パラメータ**で、**CoC を作る**のも**一般的**です。

```hlsl
float SimpleCoc(float linear_depth, float focus, float range, float scale) {
  float d = linear_depth - focus;
  float t = saturate(abs(d) / range);
  return sign(d) * t * scale;
}
```

## ギャザー（Gather）方式

**各画素が周りを見て、集める**方式です。**画素ごとに自分の CoC の半径内**の**サンプルを集めて平均**します。

```hlsl
float3 GatherBlur(float2 uv, float center_coc_pixels, float2 texel_size) {
  float radius = abs(center_coc_pixels);
  if (radius < 0.5) return scene_color.SampleLevel(linear_sampler, uv, 0).rgb;

  float3 sum = 0.0;
  float weight_sum = 0.0;
  [loop] for (int i = 0; i < kSampleCount; ++i) {
    float2 offset = kDiskSamples[i] * radius * texel_size;
    float3 color = scene_color.SampleLevel(linear_sampler, uv + offset, 0).rgb;
    float sample_coc = abs(coc_texture.SampleLevel(linear_sampler, uv + offset, 0).r);
    float weight = saturate(sample_coc - length(kDiskSamples[i] * radius) + 1.0);
    sum += color * weight;
    weight_sum += weight;
  }
  return sum / max(weight_sum, 1e-4);
}
```

| 点 | 説明 |
| --- | --- |
| **`kDiskSamples`** | **円盤状に分布した、サンプルの方向**（**ボケの形**を決める。後述） |
| **重み `weight`** | **サンプル画素の CoC が、そこまで届くか**で決める。**ピントが合った（CoC が小さい）画素を周りのボケに混ぜない**（**輪郭のにじみ防止**） |
| **前景の扱い** | **自分の CoC だけでなく、周りの CoC も影響する**必要がある（**後述**） |

**サンプル数が多い**ほど**綺麗**ですが、**画素ごとのコスト**が**重い**です。**半解像度**で**処理**するのが**一般的**です。

## スキャッター（Scatter）方式

**各画素を、CoC の大きさの「スプライト（四角形）」として描き**、**ボケの形のテクスチャで、広げて加算**する方式です。<strong>明るい光の点が絞りの形（円・六角形）のボケ（ボケ玉）</strong>になる、**映画的な見た目**が**得られます**。

| 項目 | ギャザー | スキャッター |
| --- | --- | --- |
| **処理** | **各画素が周りを集める** | **各画素が周りへ広がる** |
| <strong>ボケ玉（明るい点の円形ボケ）</strong> | **サンプル数が足りないと、粗い** | **綺麗** |
| **ボケの形** | **サンプル配置で近似** | **テクスチャで自由** |
| **コスト** | **画素数 × サンプル数** | **画素数 × スプライトの面積**（**大きい CoC で非常に重い**） |
| **前景・背景** | **扱いやすい** | **ソート・オーバードロー**が**問題** |

**現代のゲーム**は、**ギャザーが中心**で**ボケ玉が重要な場面だけ**、**明るい画素を抽出して、スプライトで描く**（**スキャッターのハイブリッド**）ことが**多い**です。

## 前景と背景

**背景のボケ**は**ピントの合った前の物に、にじみ出してはいけません**（**輪郭が背景色で汚れる**）。**前景のボケ**は**逆に後ろの鮮明な背景の上に、にじみ出さなければ不自然**です。

| 領域 | 扱い |
| --- | --- |
| <strong>背景（奥）</strong> | **ギャザー**で**ぼかす**。**自分より手前の鮮明な画素は、混ぜない**（**CoC による重み**） |
| <strong>前景（手前）</strong> | **周りの画素ににじみ出す**。**自分の CoC の範囲に、他の画素を巻き込む**ので、<strong>周辺の最大 CoC を使う（前景のタイル）</strong> |
| **ピント面** | **シャープ**のまま |

### 前景と背景を分けて処理

**前景と背景を別のレイヤー**として**ぼかし**、**最後に合成**する構成です。

| 手順 | 内容 |
| --- | --- |
| **① CoC 画像を作る** | **深度から、符号付き CoC** を**計算** |
| **② 前景・背景に分離** | **CoC の符号**で**分ける** |
| **③ それぞれぼかす** | **背景は重み付きギャザー**・**前景は広げてぼかす** |
| **④ 合成** | **ピント面 → 背景 → 前景**の順に**重ねる** |

### 近傍の最大 CoC（タイル）

**前景のボケがどこまで広がるか**を知るため、**画面を小さなタイル（例：16×16）に分け**、**各タイルの最大の前景 CoC**を**求めます**。**その範囲の画素**は、**前景のボケの影響**を**受けうる**ので、**ぼかしの対象にします**。

```hlsl
groupshared float s_min_coc[256];

[numthreads(16, 16, 1)]
void TileMaxCoc(uint3 id : SV_DispatchThreadID, uint3 group_id : SV_GroupID,
                uint group_index : SV_GroupIndex) {
  float coc = coc_texture.Load(int3(id.xy, 0)).r;
  s_min_coc[group_index] = coc;
  GroupMemoryBarrierWithGroupSync();

  for (uint stride = 128; stride > 0; stride >>= 1) {
    if (group_index < stride) {
      s_min_coc[group_index] = min(s_min_coc[group_index], s_min_coc[group_index + stride]);
    }
    GroupMemoryBarrierWithGroupSync();
  }

  if (group_index == 0) tile_coc[group_id.xy] = s_min_coc[0];
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`min`（符号付き CoC）</strong> | **前景は負**なので**最小値 ＝ 最も大きい前景ボケ** |
| **並列リダクション** | **共有メモリで半分ずつ畳み込む** |
| **利用** | **前景のぼかしを行う画素の範囲**・**サンプル半径の上限**の決定 |

## ボケの形（ボケ味）

**カメラの絞りは、数枚の羽根で多角形の穴**を作ります。**明るい点のボケ**は、**その形**になります。

| 絞り | ボケ玉の形 |
| --- | --- |
| <strong>丸い（羽根が多い・開放）</strong> | **円形** |
| **羽根が少ない** | **多角形**（六角形・八角形） |
| <strong>シネマ レンズ（アナモルフィック）</strong> | **縦長の楕円** |

**ギャザーのサンプル配置**を、**その形に分布**させます。

| 配置 | 形 |
| --- | --- |
| <strong>ポワソン円盤 / 螺旋（ヴォーゲル）</strong> | **円形** |
| **正多角形内の分布** | **多角形** |
| **楕円にスケール** | **アナモルフィック** |

### ヴォーゲル螺旋

**円盤をほぼ均一に覆う**、**簡単なサンプル配置**です。

```hlsl
float2 VogelDisk(int index, int count, float phi) {
  const float kGoldenAngle = 2.39996323;
  float r = sqrt(index + 0.5) / sqrt(count);
  float theta = index * kGoldenAngle + phi;
  return float2(cos(theta), sin(theta)) * r;
}
```

| 点 | 説明 |
| --- | --- |
| **`kGoldenAngle`** | **黄金角**（約 137.5 度）。**サンプルが重ならず、均一**に並ぶ |
| **`phi`** | **画素ごとの回転**（<strong>ノイズ（IGN）</strong>）。**縞をノイズに変える**（[PCF](../shadows/pcf.md)と同じ） |

## 最適化

| 工夫 | 内容 |
| --- | --- |
| **半解像度で処理** | **ぼかしは半解像度で十分**（**ぼけた画像は低解像度でも違いが目立たない**）。**コスト 1/4** |
| **CoC が小さい画素は、スキップ** | **ピントが合った範囲は、何もしない**（**タイルで判定**） |
| **分離可能な近似** | **円形ボケを複数の分離ガウスの組み合わせ**で**近似**（**サンプル数を大幅に削減**） |
| **サンプル数を、CoC に応じて変える** | **大きいボケは多く、小さいボケは少なく** |
| **TAA との併用** | **サンプルを少なく**し、**TAA で平滑化** |
| **ブルームとの順序** | **DOF はブルームの前**（**ボケ玉がにじむ**）。**HDR のまま** |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **映画的な奥行き・視線誘導** | **コスト**（特に大きなボケ） |
| **ボケ玉・ボケ味で画面の質感が上がる** | **前景・背景の境界**で**アーティファクト**（にじみ・ハロー） |
| **ゲームプレイで注目点を強調**できる | **画面空間なので半透明・隠れた物のボケが不正確** |

## よくあるミス

??? failure "非線形の深度から CoC を計算して、ボケの量がおかしい"
    **ビュー空間の線形な距離**で計算する。

??? failure "背景のぼかしが、ピントの合った前の物に、にじみ出す"
    **ギャザーの重みにサンプル側の CoC**を**考慮**する。

??? failure "前景のボケが、背景の上にかぶらず、輪郭が鋭いまま"
    **前景を別レイヤーで広げる**・**タイルの最大 CoC を使う**。

??? failure "ボケの最大半径を無制限にして、フレーム時間が不安定"
    **`max_coc_in_pixels`** で**上限**を設ける。

??? failure "DOF を、トーンマップの後（LDR）で行って、ボケ玉が暗くなる"
    **HDR のまま**行う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DOF ＝ <strong>ピント面から離れるほど、ぼやける</strong>。<strong>ボケの大きさ ＝ 錯乱円（CoC）</strong>
    - [x] CoC は<strong>焦点距離・F 値・ピント距離・被写体距離</strong>から<strong>式で出せる</strong>（<strong>線形な距離</strong>で計算）
    - [x] <strong>ギャザー</strong>（周りを集める）が<strong>主流</strong>。<strong>スキャッター</strong>は<strong>ボケ玉が綺麗</strong>だが<strong>重い</strong>
    - [x] <strong>背景は、ピントの合った物ににじませない</strong>。<strong>前景は背景にかぶせる</strong>（<strong>タイルの最大 CoC</strong>）
    - [x] <strong>半解像度・CoC 小はスキップ</strong>で<strong>軽く</strong>。<strong>HDR でブルームの前</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018、DICE／Frostbite の DOF）
- Gotanda et al., "Real-Time Rendering of Physically Based Optical Effects in Theory and Practice"（SIGGRAPH 2015）

## 関連ページ

- [ポストプロセス](index.md)
- [ブルーム](bloom.md)
- [モーション ブラー](motion-blur.md)
- [PCF（ポワソン円盤）](../shadows/pcf.md)

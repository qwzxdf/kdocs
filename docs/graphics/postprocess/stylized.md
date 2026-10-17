---
title: 輪郭線・トゥーン
tags:
  - 描画
---

# 輪郭線・トゥーン

**写実的ではなく、イラスト・アニメのような見た目**を目指す**スタイライズド レンダリング**（NPR、Non-Photorealistic Rendering）でも**ポストプロセスは大活躍**します。<strong>輪郭線（アウトライン）</strong>・<strong>セル シェーディング（トゥーン）</strong>・**ポスタライズ**・**ハーフトーン**など。このページでは、<strong>輪郭線の主な 3 方式（背面法・画面空間エッジ検出・Sobel）</strong>、<strong>トゥーン シェーディング（階調化）</strong>、**ポスタライズ**を**原理と実装**で説明します。

!!! tip "ポイント"
    - <strong>輪郭線</strong>は<strong>深度・法線・ID の「急な変化」</strong>を<strong>検出して描く</strong>（<strong>画面空間エッジ検出</strong>）。
    - <strong>背面法（Inverted Hull）</strong>：<strong>メッシュを法線方向に膨らませて、裏面だけ黒く描く</strong>。<strong>太さがワールド空間</strong>で決まる。
    - <strong>Sobel / Roberts Cross</strong>：<strong>隣接画素の差分</strong>から<strong>エッジの強さ</strong>。
    - <strong>トゥーン</strong>：<strong>連続した陰影（N·L）を、少数の階調にまとめる</strong>（<strong>しきい値・ランプ テクスチャ</strong>）。
    - <strong>ポスタライズ</strong>：<strong>色の階調数を減らす</strong>。
    - <strong>線の太さ・距離による変化</strong>が<strong>見た目の質</strong>を決める。

## 輪郭線の方式

| 方式 | 原理 | 長所 | 短所 |
| --- | --- | --- | --- |
| <strong>背面法（Inverted Hull）</strong> | **メッシュを法線方向に膨らませた裏面**を**黒で描く** | **安い**。<strong>線の太さが一定（ワールド空間）</strong>。**線の形が整っている** | **鋭角・分離したメッシュで線が途切れる**。**内側の線（折り目）は出ない** |
| **画面空間エッジ検出** | **深度・法線・ID の画像から、エッジを検出** | **内側の線（折り目）も出る**。**メッシュに依存しない** | <strong>線の太さが画面空間（距離で変わる）</strong>。**検出の調整** |
| **ジオメトリで線を生成** | **シルエット辺をジオメトリとして描く** | **高品質**（線をスタイライズできる） | **実装が複雑**。**コスト** |

## 背面法（Inverted Hull）

**メッシュを 2 回描く**簡単な方法です。**1 回目は通常**に、**2 回目は頂点を法線方向に少し押し出し**、<strong>表面をカリング（裏面だけ描く）</strong>して、<strong>黒（輪郭線の色）</strong>で塗ります。<strong>膨らんだ裏面の「はみ出し」</strong>が、**輪郭線**として**見えます**。

```hlsl
cbuffer OutlineConstants : register(b1) {
  float outline_width;
  float3 outline_color;
};

VsOutput OutlineVS(float3 position : POSITION, float3 normal : NORMAL) {
  float4 world_position = mul(float4(position, 1.0), world);
  float3 world_normal = normalize(mul(normal, (float3x3)world));
  world_position.xyz += world_normal * outline_width;

  VsOutput output;
  output.position = mul(world_position, view_projection);
  return output;
}

float4 OutlinePS() : SV_Target {
  return float4(outline_color, 1.0);
}
```

| 点 | 説明 |
| --- | --- |
| **ラスタライザー** | <strong>前面カリング（`CullMode = FRONT`）</strong>で、**裏面だけ描く**。**左手系・時計回り前面**（このサイトの標準）の**メッシュ**では、**`D3D11_CULL_FRONT`** |
| **法線で押し出す** | **ワールド空間の法線方向**に**`outline_width`** 分**膨らませる**。**線の太さがワールド単位** |
| **欠点：頂点の分離** | <strong>ハード エッジ（法線が面ごとに違う）</strong>で**頂点が分かれていると**、**押し出しで隙間が空いて**、**線が途切れる**。**スムーズな法線を別に持つ**（**頂点カラーや UV2 に格納**） |
| **距離による太さ** | **距離に応じて、`outline_width` を調整**（**遠くで細く／画面上の太さを一定に**） |

### 画面上の太さを一定にする

**カメラからの距離に比例して押し出し量を増やす**と、**画面上の線の太さが一定**になります。

```hlsl
float4 clip = mul(world_position, view_projection);
float distance_scale = clip.w;
world_position.xyz += world_normal * outline_width * distance_scale;
```

## 画面空間エッジ検出

<strong>完成した画像（深度・法線・ID）</strong>から、<strong>エッジ（急な変化）</strong>を**検出**します。

### 深度によるエッジ

**隣接する画素の深度の差**が**大きい**ところは、<strong>物体の境界（シルエット）</strong>です。

```hlsl
float DepthEdge(float2 uv, float2 texel_size, float threshold) {
  float center = LinearDepth(depth_texture.SampleLevel(point_sampler, uv, 0).r);
  float left = LinearDepth(depth_texture.SampleLevel(point_sampler, uv + float2(-1, 0) * texel_size, 0).r);
  float right = LinearDepth(depth_texture.SampleLevel(point_sampler, uv + float2(1, 0) * texel_size, 0).r);
  float up = LinearDepth(depth_texture.SampleLevel(point_sampler, uv + float2(0, -1) * texel_size, 0).r);
  float down = LinearDepth(depth_texture.SampleLevel(point_sampler, uv + float2(0, 1) * texel_size, 0).r);

  float difference = abs(left - center) + abs(right - center) + abs(up - center) + abs(down - center);
  return step(threshold * center, difference);
}
```

| 点 | 説明 |
| --- | --- |
| **線形な深度** | **非線形の深度では、遠くで差が小さすぎる**。**線形に変換** |
| **`threshold * center`** | **距離に比例した、しきい値<strong>（</strong>遠くの物も同じ見た目**で線が出る） |
| **欠点** | **面が斜めにカメラに向く**と**深度の差が大きくなり、面の中に線が出る**（**誤検出**）。**法線も併用して補う** |

### 法線によるエッジ

**法線の向きが大きく変わる所**（**折り目・硬い角**）は、**輪郭線**を**描きたい**場所です。

```hlsl
float NormalEdge(float2 uv, float2 texel_size, float threshold) {
  float3 center = normal_texture.SampleLevel(point_sampler, uv, 0).xyz * 2.0 - 1.0;
  float3 left = normal_texture.SampleLevel(point_sampler, uv + float2(-1, 0) * texel_size, 0).xyz * 2.0 - 1.0;
  float3 right = normal_texture.SampleLevel(point_sampler, uv + float2(1, 0) * texel_size, 0).xyz * 2.0 - 1.0;
  float3 up = normal_texture.SampleLevel(point_sampler, uv + float2(0, -1) * texel_size, 0).xyz * 2.0 - 1.0;
  float3 down = normal_texture.SampleLevel(point_sampler, uv + float2(0, 1) * texel_size, 0).xyz * 2.0 - 1.0;

  float difference = (1.0 - dot(center, left)) + (1.0 - dot(center, right)) +
                     (1.0 - dot(center, up)) + (1.0 - dot(center, down));
  return step(threshold, difference);
}
```

| 点 | 説明 |
| --- | --- |
| **法線バッファ** | **G バッファ**から**得る**、または**専用に描く** |
| **`1 - dot(a, b)`** | **向きの違い**（**同じ向きで 0、直角で 1**） |
| **用途** | **折り目・内側の線**（深度では取れない） |

### ID によるエッジ

<strong>オブジェクト ID（またはマテリアル ID）</strong>を**画像に描き**、**隣接画素で ID が違う**所を**線**にします。**物体の境界を確実に**、**任意の形**で**検出**できます（**深度や法線の誤検出がない**）。

### Sobel フィルタ

**3×3 の近傍**から、<strong>勾配（エッジの強さ）</strong>を**計算**する、**古典的なフィルタ**です。

```hlsl
float Sobel(Texture2D<float> source, float2 uv, float2 texel_size) {
  float tl = source.SampleLevel(point_sampler, uv + float2(-1, -1) * texel_size, 0);
  float t = source.SampleLevel(point_sampler, uv + float2(0, -1) * texel_size, 0);
  float tr = source.SampleLevel(point_sampler, uv + float2(1, -1) * texel_size, 0);
  float l = source.SampleLevel(point_sampler, uv + float2(-1, 0) * texel_size, 0);
  float r = source.SampleLevel(point_sampler, uv + float2(1, 0) * texel_size, 0);
  float bl = source.SampleLevel(point_sampler, uv + float2(-1, 1) * texel_size, 0);
  float b = source.SampleLevel(point_sampler, uv + float2(0, 1) * texel_size, 0);
  float br = source.SampleLevel(point_sampler, uv + float2(1, 1) * texel_size, 0);

  float gx = -tl - 2.0 * l - bl + tr + 2.0 * r + br;
  float gy = -tl - 2.0 * t - tr + bl + 2.0 * b + br;
  return sqrt(gx * gx + gy * gy);
}
```

| 点 | 説明 |
| --- | --- |
| **`gx`・`gy`** | **水平・垂直方向の勾配**（**Sobel カーネル**） |
| **`sqrt(gx² + gy²)`** | **勾配の大きさ**＝**エッジの強さ** |
| **Roberts Cross** | **2×2 の対角差分**。**軽い**が**ノイズに敏感** |

### 線の太さ

**画面空間のエッジ検出**で、**線を太くする**には、**サンプル間隔（オフセット）を大きく**します。

```hlsl
float2 offset = texel_size * line_width;
```

**距離に応じて太さを変える**ことで、<strong>遠景で線が潰れる（太すぎ）</strong>のを**防ぎます**。

## トゥーン シェーディング（セル シェーディング）

<strong>滑らかな陰影を少数の階調（2〜4 段）</strong>に**まとめて**、**セル画のような見た目**にします。

### しきい値による階調化

```hlsl
float ToonShade(float n_dot_l, float threshold, float smoothness) {
  return smoothstep(threshold - smoothness, threshold + smoothness, n_dot_l);
}

float3 ToonLighting(float3 albedo, float3 shadow_color, float n_dot_l) {
  float lit = ToonShade(n_dot_l, 0.5, 0.01);
  return lerp(albedo * shadow_color, albedo, lit);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`smoothstep`（狭い幅）</strong> | **明暗の境界をほぼ段差**に。**少しだけ滑らかにして、ジャギーを避ける** |
| **`shadow_color`** | **影の部分の色味**（**暗くするだけでなく、色相をずらす**と**絵として良い**） |
| **階調数** | <strong>2 段（明・暗）</strong>が**基本**。<strong>3 段（ハイライト・明・暗）</strong> |

### ランプ テクスチャ

**N·L（0〜1）を、1D のテクスチャ（ランプ）の座標**にして、**階調の色**を**引きます**。**アーティストがランプの絵で階調・色を直接調整**できます。

```hlsl
float3 ramp_color = ramp_texture.Sample(linear_clamp, float2(n_dot_l * 0.5 + 0.5, 0.5)).rgb;
float3 result = albedo * ramp_color;
```

### スペキュラ・リムライト

| 要素 | 内容 |
| --- | --- |
| **トゥーン スペキュラ** | **スペキュラもしきい値で 2 値化**（**くっきりしたハイライト**） |
| **リムライト** | <strong>視線と法線が直角に近い所（縁）</strong>を**明るく**する。**`pow(1 - dot(N, V), p)`**。**輪郭を強調** |

## ポスタライズ

**色の階調数を減らす**エフェクトです（**ポップ アート・ゲームボーイ風**）。

```hlsl
float3 Posterize(float3 color, float levels) {
  return floor(color * levels) / (levels - 1.0);
}
```

| 点 | 説明 |
| --- | --- |
| **`levels`** | **各チャンネルの階調数**（例：4） |
| **LDR で** | **トーンマップ後**に**適用** |
| **ディザリングとの併用** | **階調を減らした分をディザ（ノイズ）で補う**と**レトロな見た目** |

## ハーフトーン

<strong>網点（ドット）</strong>で**陰影を表現**する、**漫画・印刷風**の効果です。**明るさに応じて、ドットの大きさを変え**ます。

```hlsl
float Halftone(float2 pixel, float luminance, float dot_size) {
  float2 grid = frac(pixel / dot_size) - 0.5;
  float distance_from_center = length(grid);
  float radius = sqrt(1.0 - luminance) * 0.7;
  return step(distance_from_center, radius);
}
```

## アウトラインの色・演出

| 手法 | 内容 |
| --- | --- |
| **黒の一定色** | **基本** |
| **物体の色を暗くした色** | **自然な見た目**（**輪郭線の色が物体のアルベドから決まる**） |
| **線の強弱** | **距離・太さ・角度で線の濃さを変える**（**手描き風**） |
| **ノイズで揺らす** | **線を少し揺らして**、**手描き感** |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **アニメ・イラスト風の独自の見た目** | **背面法はハード エッジで途切れる** |
| **画面空間のエッジは、メッシュに非依存** | <strong>画面空間のエッジは、誤検出（斜面・遠景）</strong>の**調整が難しい** |
| **ポスト処理なので既存パイプラインに足せる** | **線の太さが距離・解像度で変わる** |

## よくあるミス

??? failure "背面法で、ハード エッジの頂点が分かれて、押し出しで線が途切れる"
    <strong>スムーズな法線を別チャンネル（頂点カラー・UV2）</strong>に持つ。

??? failure "非線形の深度で、エッジ検出して、遠くで線が出ない／近くで出すぎる"
    **線形深度**で検出し、**距離に比例したしきい値**。

??? failure "深度だけでエッジを取り、傾いた面の中に線が出る"
    **法線・ID も併用**する。

??? failure "トゥーンの境界が、ギザギザ（エイリアシング）になる"
    **`smoothstep` で、わずかに滑らかに**（`fwidth` で画素幅に合わせる）。

??? failure "背面法のカリング設定が逆で、表面が黒くなる"
    **前面カリング**にする（**メッシュの巻き方向・座標系に注意**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 輪郭線は<strong>背面法（安い・ワールド空間の太さ）</strong>と<strong>画面空間エッジ検出（深度・法線・ID・Sobel）</strong>
    - [x] <strong>背面法</strong>は<strong>ハード エッジで途切れる</strong>ので<strong>スムーズ法線を別に持つ</strong>
    - [x] <strong>画面空間</strong>は<strong>線形深度・距離比例のしきい値</strong>。<strong>法線・ID で補う</strong>
    - [x] <strong>トゥーン</strong> ＝ <strong>N·L を、しきい値・ランプで少数の階調に</strong>。<strong>影の色相をずらす</strong>
    - [x] <strong>ポスタライズ・ハーフトーン</strong>で<strong>レトロ・漫画風</strong>

## 参考

- Saito, Takahashi, "Comprehensible Rendering of 3-D Shapes"（SIGGRAPH 1990）
- 西川, "GUILTY GEAR Xrd の作り方"（CEDEC 2015）／ 石川ほか、トゥーン レンダリング
- Decaudin, "Cartoon-Looking Rendering of 3D-Scenes"（1996）

## 関連ページ

- [ポストプロセス](index.md)
- [ブルーム](bloom.md)
- [カラー グレーディング](color-grading.md)

---
title: 画面空間のエッジ検出
tags:
  - 描画
---

# 画面空間のエッジ検出

**背面法はモデルの外側の輪郭しか出ません**。**モデルの内側の折り目（鼻・袖・服のしわの境）や、物体どうしの境の線も出したい**場合は、**画面の画像（深度・法線・ID）から、「値が大きく変わる場所」を検出して線にする**、**画面空間のエッジ検出**を使います。**どんな形状でも後処理で線を引ける**ので**柔軟**ですが、**線の太さの制御や細部のちらつき**に**注意**が**必要**です。このページでは、**深度・法線・ID による検出・Sobel フィルタ・線の太さ・ちらつきの抑制・色の付け方**を説明します。

!!! tip "ポイント"
    - エッジ検出 ＝ <strong>隣り合う画素の、深度・法線・ID の差が大きい所を線にする</strong>。
    - <strong>深度</strong>：<strong>物体の輪郭・前後関係の境</strong>。<strong>法線</strong>：<strong>折り目・面の向きが変わる所</strong>。<strong>ID</strong>：<strong>物体・材質の境</strong>。
    - 3 つを<strong>組み合わせる</strong>と<strong>内側の線も外側の線も出る</strong>。
    - <strong>Sobel フィルタ</strong>が<strong>標準</strong>。<strong>勾配の大きさで線の強さ</strong>を決める。
    - <strong>線の太さ</strong>は<strong>サンプル間隔</strong>で調整する。<strong>距離で補正</strong>。
    - <strong>斜めの面で深度の差が出て、不要な線</strong>が出る → <strong>深度勾配で補正</strong>。

## 3 つの検出

**検出に使う画像**は、**不透明パスの出力**（**深度バッファ・法線バッファ・ID バッファ**）です。

| 入力 | 検出される線 | 弱点 |
| --- | --- | --- |
| **深度** | **物体の外側の輪郭・手前と奥の境** | **同じ深度の折り目は出ない・斜めの面で誤検出** |
| **法線** | <strong>折り目・面の向きの境（内側の線）</strong> | **滑らかな面の境は出ない・法線マップの細かい凹凸で、ノイズ** |
| <strong>ID（材質・物体）</strong> | **材質・物体どうしの境** | **ID バッファが別途必要** |

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="エッジ検出の入力">
<text x="20" y="26" class="fig-title">深度・法線・ID から、それぞれ違う線が取れる</text>
<g font-size="12">
<g transform="translate(40,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><circle cx="100" cy="66" r="42" fill="#cbd5e1"/><circle cx="100" cy="66" r="42" fill="none" stroke="#111827" stroke-width="4"/><text x="0" y="152">深度：外側の輪郭</text></g>
<g transform="translate(290,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><rect x="50" y="30" width="100" height="76" fill="#e2e8f0"/><line x1="100" y1="30" x2="100" y2="106" stroke="#111827" stroke-width="4"/><line x1="50" y1="68" x2="150" y2="68" stroke="#111827" stroke-width="4"/><text x="0" y="152">法線：内側の折り目</text></g>
<g transform="translate(540,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><rect x="30" y="30" width="70" height="76" fill="#fecaca"/><rect x="100" y="30" width="70" height="76" fill="#bfdbfe"/><line x1="100" y1="30" x2="100" y2="106" stroke="#111827" stroke-width="4"/><text x="0" y="152">ID：物体・材質の境</text></g>
</g>
</svg>

## Sobel フィルタ

<strong>画像の勾配（変化の大きさ）</strong>を**測る標準的な方法**が**Sobel フィルタ**です。**周囲 3×3 の画素に、重みを掛けて、縦・横の勾配を求めます**。

```hlsl
float Sobel(Texture2D<float> source, float2 uv, float2 texel) {
  float tl = source.SampleLevel(point_clamp, uv + texel * float2(-1, -1), 0);
  float t  = source.SampleLevel(point_clamp, uv + texel * float2( 0, -1), 0);
  float tr = source.SampleLevel(point_clamp, uv + texel * float2( 1, -1), 0);
  float l  = source.SampleLevel(point_clamp, uv + texel * float2(-1,  0), 0);
  float r  = source.SampleLevel(point_clamp, uv + texel * float2( 1,  0), 0);
  float bl = source.SampleLevel(point_clamp, uv + texel * float2(-1,  1), 0);
  float b  = source.SampleLevel(point_clamp, uv + texel * float2( 0,  1), 0);
  float br = source.SampleLevel(point_clamp, uv + texel * float2( 1,  1), 0);
  float gx = (tr + 2.0 * r + br) - (tl + 2.0 * l + bl);
  float gy = (bl + 2.0 * b + br) - (tl + 2.0 * t + tr);
  return sqrt(gx * gx + gy * gy);
}
```

| 点 | 説明 |
| --- | --- |
| **`gx`・`gy`** | **横方向・縦方向の勾配**（**重み 1・2・1**） |
| **`sqrt(gx² + gy²)`** | **勾配の大きさ**（**エッジの強さ**） |
| **しきい値で 2 値化** | **`step(threshold, 強さ)` で、線あり・なし** |
| **簡易版** | **上下左右の 4 点だけの差（Roberts Cross など）も使える** |

<!-- fig:outline-edge-detect:begin -->
<!-- fig:outline-edge-detect:end -->

## 深度によるエッジ

**線形化した深度**に**Sobel を適用**し、**差が一定以上の所を線**に**します**。

```hlsl
float DepthEdge(float2 uv) {
  float center = LinearDepth(uv);
  float edge = Sobel(linear_depth, uv, texel);
  float threshold = kDepthThreshold * center;
  return step(threshold, edge);
}
```

| 点 | 説明 |
| --- | --- |
| **線形な深度を使う** | **非線形な深度では、遠くで差が出ない** |
| **しきい値を深度に比例** | **遠い物体ほど、深度の差が大きく出るので、補正する** |
| **斜めの面の誤検出** | <strong>地面のような、斜めの面は隣の画素で深度が少し違う（勾配）</strong> → **深度の勾配を法線から予測して、差し引く** |

### 斜めの面の誤検出の対策

**斜めの面では隣の画素との深度の差が、自然に生じます**（**エッジではない**）。**法線と視線の角度**から、**その差の予想値**を**求め、予想を超える差だけをエッジ**とします。

```hlsl
float DepthEdgeCorrected(float2 uv, float3 normal, float3 view_dir) {
  float center = LinearDepth(uv);
  float cos_angle = abs(dot(normal, view_dir));
  float expected_difference = center * texel_world_size / max(cos_angle, 0.05);
  float edge = Sobel(linear_depth, uv, texel);
  return step(expected_difference * kSlopeScale + kBias, edge);
}
```

## 法線によるエッジ

**隣り合う法線の差（内積）が小さい所**が**折り目**です。

```hlsl
float NormalEdge(float2 uv) {
  float3 n = normal_buffer.SampleLevel(point_clamp, uv, 0).xyz * 2.0 - 1.0;
  float3 n_r = normal_buffer.SampleLevel(point_clamp, uv + float2(texel.x, 0), 0).xyz * 2.0 - 1.0;
  float3 n_b = normal_buffer.SampleLevel(point_clamp, uv + float2(0, texel.y), 0).xyz * 2.0 - 1.0;
  float d = (1.0 - dot(n, n_r)) + (1.0 - dot(n, n_b));
  return step(kNormalThreshold, d);
}
```

| 点 | 説明 |
| --- | --- |
| **`1 − dot(n, n_neighbor)`** | **同じ向きなら 0、直角で 1** |
| **法線マップの影響** | **細かい凹凸の法線マップが入ると、ノイズ**。**ジオメトリの法線（法線マップなし）を別に使う** |

## ID によるエッジ

**物体 ID・材質 ID を画素ごとに別のバッファへ書き**、**隣と ID が違えば線**とします。

| 用途 | 内容 |
| --- | --- |
| **物体どうしの境** | **キャラクターと背景の境・キャラ同士の境** |
| **材質の境** | **髪と肌・服と肌** |
| **選択した物体の強調** | <strong>選択された ID だけ輪郭を出す（ハイライト）</strong> |

```hlsl
float IdEdge(float2 uv) {
  uint id = id_buffer.Load(int3(uv * resolution, 0));
  uint id_r = id_buffer.Load(int3(uv * resolution + int2(1, 0), 0));
  uint id_b = id_buffer.Load(int3(uv * resolution + int2(0, 1), 0));
  return (id != id_r || id != id_b) ? 1.0 : 0.0;
}
```

## 線の太さ

| 方法 | 内容 |
| --- | --- |
| **サンプル間隔を広げる** | **`texel × 2` など、隣より離れた画素と比べる**と、**線が太くなる** |
| **距離による補正** | <strong>遠くで間隔を狭める（細く）</strong>・**近くで広げる** |
| **複数の間隔を混ぜる** | **細い線 ＋ 太い線で強弱** |
| **ぼかしで太く** | **検出後に軽くぼかして太くする** |

**注意**：**間隔を広げると離れた 2 点の差を見るので、細かい形状の線が出にくく**なります。

## ちらつきと安定

**画面空間のエッジは、カメラが動くと検出される画素が変わり、線がちらつく**ことが**あります**。

| 対策 | 内容 |
| --- | --- |
| **TAA で平均** | **TAA の後に線を引く**のではなく、**線を引いてから TAA** で**滑らかに** |
| <strong>しきい値にソフトな境（`smoothstep`）</strong> | **線の強さが連続的に変わる** |
| **アンチエイリアス済みの深度・法線から検出** | **ジャギーが少ない** |
| **線をジオメトリ側（背面法）で出す部分を併用** | **外側の輪郭は背面法で安定** |

## 色の付け方

| 方法 | 内容 |
| --- | --- |
| **黒** | **標準** |
| **元の色の暗い版** | <strong>柔らかい絵（線が浮かない）</strong> |
| **材質ごとの色** | **肌は赤っぽい、髪は暗い** |
| **深度でフェード** | **遠くの線を薄く** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **深度・法線・ID を組み合わせる** | **内側・外側の線を両方** |
| **斜めの面の補正** | **地面の誤検出を防ぐ** |
| <strong>ジオメトリの法線（法線マップなし）</strong> | **細かい凹凸でノイズが出ない** |
| **TAA を併用** | **ちらつきを抑える** |
| **背面法と併用** | **外側は背面法、内側は画面空間** |
| **線の強さを `smoothstep`** | **滑らか** |

## よくあるミス

??? failure "地面（斜めの面）に、縞のような線が出る"
    **深度の勾配補正**を入れる。

??? failure "法線マップのせいで、細かい線がうるさい"
    **法線マップを含まない、ジオメトリの法線**を別に書く。

??? failure "遠くで線が太く、近くで細い"
    **距離でサンプル間隔を補正**する。

??? failure "動くと線がちらつく"
    **`smoothstep` で滑らかに**、**TAA を併用**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 画面空間エッジ ＝ <strong>隣の画素との、深度・法線・ID の差が大きい所を線にする</strong>
    - [x] <strong>深度は外側の輪郭、法線は内側の折り目、ID は物体・材質の境</strong>
    - [x] <strong>Sobel フィルタ</strong>で<strong>勾配の大きさ</strong>を測る
    - [x] <strong>斜めの面の誤検出</strong>は<strong>深度勾配の補正</strong>で防ぐ
    - [x] <strong>背面法と併用</strong>。<strong>TAA でちらつきを抑える</strong>

## 参考

- Saito & Takahashi, "Comprehensible Rendering of 3-D Shapes"（SIGGRAPH 1990）
- Decaudin, "Cartoon-Looking Rendering of 3D-Scenes"（1996）
- Vergne et al., "Apparent Relief"（SIGGRAPH 2011）

## 関連ページ

- [輪郭線・トゥーン](index.md)
- [背面法の輪郭線](outline-hull.md)
- [セル シェーディング](cel-shading.md)
- [TAA](../antialiasing/taa.md)

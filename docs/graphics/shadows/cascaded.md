---
title: カスケード シャドウ マップ
tags:
  - 描画
---

# カスケード シャドウ マップ

**広い屋外**で太陽の影を、**1 枚のシャドウ マップ**で覆うと、<strong>画面の近くの影が粗く（ギザギザ）</strong>なります。**カメラの近くは、細かく**、**遠くは粗くて十分**なのに**マップが全体を均等に覆っている**からです（遠近エイリアシング）。**カスケード シャドウ マップ**（CSM、Cascaded Shadow Maps）は、**カメラの視錐台を奥行き方向に複数に分割**し、**分割ごとに別のシャドウ マップ**を用意します。**近い範囲ほど、小さな領域を細かく**、**遠い範囲は広い領域を粗く**覆うので、**画面でほぼ一定の細かさ**の影になります。**屋外の太陽の影の標準的な方式**です。

!!! tip "ポイント"
    - 視錐台を<strong>奥行きで N 個（3〜4）に分割</strong>。<strong>各分割（カスケード）に、シャドウ マップ</strong>を 1 枚。
    - <strong>分割の位置</strong>は、<strong>対数と一様の中間（PSSM）</strong>で決める。
    - 各カスケードの<strong>光の正射影</strong>は、その分割を<strong>ちょうど覆う</strong>ように決める。<strong>球で包むと回転に強く安定</strong>。
    - <strong>テクセルのスナップ</strong>で、カメラが動いても影の縁がちらつかない。
    - 描画時、<strong>画素の深度から、カスケードを選ぶ</strong>。<strong>境目はブレンド</strong>する。
    - <strong>影を落とす物は、視錐台の外</strong>（光に近い側）にもある。<strong>範囲を光の方向に広げる</strong>。

## 遠近エイリアシングの解消

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="カスケード">
<text x="20" y="24" class="fig-title">視錐台を奥行きで分割し、近いほど小さな範囲を同じ解像度で覆う（真上から見た図）</text>
<circle cx="70" cy="160" r="8" fill="currentColor"/><text x="50" y="186" style="font-size:12px">カメラ</text>
<polygon points="70,160 700,50 700,270" fill="rgba(76,139,245,0.1)" stroke="currentColor" stroke-width="2"/>
<line x1="170" y1="143" x2="170" y2="177" stroke="currentColor" stroke-dasharray="4 3"/><line x1="320" y1="122" x2="320" y2="198" stroke="currentColor" stroke-dasharray="4 3"/><line x1="500" y1="92" x2="500" y2="228" stroke="currentColor" stroke-dasharray="4 3"/>
<rect x="72" y="140" width="98" height="40" fill="rgba(46,160,67,0.3)"/><rect x="170" y="115" width="150" height="90" fill="rgba(229,170,40,0.25)"/><rect x="320" y="80" width="180" height="160" fill="rgba(229,72,77,0.2)"/><rect x="500" y="50" width="200" height="220" fill="rgba(150,100,230,0.18)"/>
<text x="84" y="132" style="font-size:12px">カスケード 0（最も細かい）</text>
<text x="190" y="108" style="font-size:12px">カスケード 1</text><text x="350" y="72" style="font-size:12px">カスケード 2</text><text x="540" y="44" style="font-size:12px">カスケード 3（最も粗い）</text>
<text x="20" y="292" style="font-size:12px">同じ解像度（例：2048²）の影の地図が、近い範囲ほど狭い領域を覆う → 画面での影の細かさが、距離によらず、ほぼ一定</text>
</svg>

| 項目 | 1 枚のシャドウ マップ | カスケード |
| --- | --- | --- |
| **近い影** | **粗い**（広い範囲を均等に） | **細かい**（狭い範囲） |
| **遠い影** | 無駄に細かい | 粗い（広い範囲） |
| **メモリ** | 1 枚 | **N 枚**（解像度は各 1024〜4096） |
| **描画コスト** | 1 回 | **N 回**（シーンを、N 回描く） |

## 分割の決め方

**視錐台の近クリップ面 `n` から遠クリップ面 `f`** までを、N 個に分けます。**一様**に分けると**近くの細かさが足りず**、**対数**で分けると**近くが極端に狭く**なります。**中間**（**PSSM**、Parallel-Split Shadow Maps）が、実用的です。

<div class="formula">C_i = λ · n · (f / n)^(i/N) + (1 − λ) · ( n + (i/N) · (f − n) )　（i = 1 … N）</div>

| 記号 | 意味 |
| --- | --- |
| **C_i** | i 番目の分割の**奥側の境界**（カメラからの距離） |
| **λ** | 0 で一様、1 で対数。**0.5〜0.9 程度** |
| **n・f** | 近・遠クリップ面（**影を描く最大距離を、f の代わりに**短めに設定することが多い） |

```cpp
std::array<float, kCascadeCount + 1> SplitDistances(float n, float f, float lambda) {
  std::array<float, kCascadeCount + 1> splits;
  splits[0] = n;
  for (int i = 1; i <= kCascadeCount; ++i) {
    float t = static_cast<float>(i) / kCascadeCount;
    float log_split = n * std::pow(f / n, t);
    float uniform_split = n + (f - n) * t;
    splits[i] = lambda * log_split + (1.0f - lambda) * uniform_split;
  }
  return splits;
}
```

**影の最大距離**（`f`）は、**遠クリップ面より短く**します（**遠すぎる影は見えないので描画しない**）。**100〜300 m**程度が、多くのゲームの設定です。

## 各カスケードの光の射影

**各分割の視錐台**（8 つの角）を、**光の視点から、ちょうど覆う正射影**を作ります。

| 方法 | 内容 |
| --- | --- |
| **AABB でフィット** | 分割の 8 つの角を**光空間に変換**し、**最小の AABB**で包む。**小さく、効率的**だが**カメラが回転すると、AABB の大きさが変わり、影がちらつく** |
| **球でフィット** | 分割の 8 つの角を**包む最小の球**を求め、**球の直径**を**正射影の大きさ**にする。**回転しても大きさが変わらない**ので、**安定**。<strong>やや無駄（解像度が少し下がる）</strong> |

**安定性**を優先して、**球でのフィット**が実用的です。

```cpp
Vector3 center = Vector3::Zero;
for (const auto& corner : frustum_corners) center += corner;
center /= 8.0f;

float radius = 0.0f;
for (const auto& corner : frustum_corners) radius = std::max(radius, (corner - center).Length());
radius = std::ceil(radius * 16.0f) / 16.0f;
```

| 点 | 説明 |
| --- | --- |
| **`radius` の切り上げ** | **わずかなカメラの動きで、半径が変わらない**ように、**粗い刻み**で丸める（ちらつき防止） |
| **中心** | 分割の視錐台の中心（8 角の平均）。光空間の位置合わせは次節 |

## テクセルのスナップ

カメラが動くと**シャドウ マップの範囲**も動きます。**範囲の位置がテクセルの境界とずれていく**と**影の縁がちらちらと揺れます**（テクセルをまたぐたびに、サンプルの位置が変わる）。**範囲の位置をテクセル単位に揃える**（スナップ）と、**縁が動かず**、**ちらつきが止まります**。

```cpp
float texel_size = (radius * 2.0f) / shadow_resolution;

Vector3 center_ls = Vector3::Transform(center, light_view);
center_ls.x = std::floor(center_ls.x / texel_size) * texel_size;
center_ls.y = std::floor(center_ls.y / texel_size) * texel_size;
Vector3 snapped_center = Vector3::Transform(center_ls, light_view.Invert());
```

| 手順 | 内容 |
| --- | --- |
| **① 光空間に変換** | 中心を光のビュー空間へ |
| **② テクセルの大きさで、丸める** | x・y を、`texel_size` の倍数に揃える |
| **③ 元の空間へ戻す** | 揃えた中心から、射影行列を作る |

**回転に強い（球でのフィット）と、スナップ**を併用します。

## 深度範囲：視錐台の外の遮蔽物

**影を落とす物体**は、<strong>視錐台の外（光に近い側）</strong>にもあります。**視錐台の中だけ**を覆う正射影では、**その物体がシャドウ マップに入らず**、**影が欠けます**。

| 方法 | 内容 |
| --- | --- |
| **光の方向に範囲を延ばす** | 正射影の**近クリップ面を、光に近い側**へ。<strong>影を落とす物体（カスケードの外）</strong>も含める |
| <strong>深度クランプ（Pancaking）</strong> | **近クリップ面より手前の物体**を、**近クリップ面に押し付けて**描く（`DepthClipEnable = FALSE`）。**近クリップ面を狭く**でき、**深度の精度が上がる**。ただし、**物体がクリップ面に**押し付けられる |
| **影を落とす物体の AABB で決める** | シーン全体の影を落とす物体を**光空間で**包んで近クリップ面を決める |

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.DepthClipEnable = FALSE;
```

**深度クランプ**で**シャドウ マップの深度範囲**を、**その分割に必要な分だけ**にできます。

## カスケードの選択

描画時、**各画素のカメラからの深度**（**ビュー空間の z**）を、**分割の境界と比べ**、**どのカスケードを使うか**を決めます。

```hlsl
int SelectCascade(float view_depth) {
  int cascade = 0;
  [unroll] for (int i = 0; i < kCascadeCount - 1; ++i) {
    cascade += (view_depth > cascade_splits[i]) ? 1 : 0;
  }
  return cascade;
}
```

| 方式 | 内容 |
| --- | --- |
| **深度で選ぶ** | `view_depth` と分割の距離を比べる。簡単 |
| **シャドウ マップの範囲で選ぶ** | **各カスケードの uv が、範囲内（0〜1）に入るか**を細かい順に調べ、**入った最初**のものを使う。**範囲を安全に使う**（ブレンドと相性が良い） |

### シャドウ マップを選んで引く

```hlsl
float CascadeShadow(float3 world_pos, float view_depth) {
  int c = SelectCascade(view_depth);
  float4 light_clip = mul(float4(world_pos, 1.0), cascade_view_projection[c]);
  float3 ndc = light_clip.xyz / light_clip.w;
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  return shadow_array.SampleCmpLevelZero(shadow_sampler, float3(uv, c), ndc.z - bias);
}
```

**カスケードはテクスチャ配列**（`Texture2DArray`）に入れると**インデックスで切り替え**られて便利です（**1 つの SRV**）。

## カスケード間のブレンド

**カスケードの境界**で**シャドウ マップが切り替わる**と、<strong>解像度の違い（ぼけの違い）</strong>により、**影が突然、変わって見え**ます。**境界の近く**で**隣のカスケードと混ぜます**。

| 方法 | 内容 |
| --- | --- |
| **境界の手前でブレンド** | **カスケードの奥側 10% 程度**で、**次のカスケード**の結果と、`lerp` |
| **uv の端でブレンド** | シャドウ マップの端（uv が 0 や 1 に近い）で、**次の粗いカスケード**へ |

```hlsl
float shadow = CascadeShadow(world_pos, c);
float blend = saturate((view_depth - blend_start[c]) / blend_width[c]);
if (blend > 0.0) {
  shadow = lerp(shadow, CascadeShadow(world_pos, c + 1), blend);
}
```

**ブレンドは境界の画素だけ**で、**2 回サンプルする**ので、**わずかにコストが増えます**。

## 最大距離でのフェード

**影の最大距離**を超えた先は、**影なし**になります。**突然、影が消える**と目立つので、**最大距離の手前でフェード**します。

```hlsl
float fade = saturate((max_shadow_distance - view_depth) / fade_length);
shadow = lerp(1.0, shadow, fade);
```

## カスケードごとの調整

| 項目 | 内容 |
| --- | --- |
| **バイアス** | **テクセルの大きさ**が違うので、**カスケードごとに**調整（[バイアス](bias.md)）。**ワールド単位のテクセル サイズ**に比例させる |
| **PCF のぼけの幅** | **カスケードで、1 テクセルの大きさが違う**ので、**カーネルをスケール**して、**ワールドでの幅をそろえる** |
| **LOD・カリング** | **遠いカスケード**は、**低い LOD**・**小さい物を省く** |
| **更新頻度** | **遠いカスケード**は、**数フレームに 1 回**更新（[影のコスト](../../rendering/shadows.md)） |

## カスケードごとのカリング

各カスケードは、<strong>別の視錐台（光の正射影）</strong>で、シーンを描きます。**カスケードごとに視錐台カリング**を行い、**そのカスケードに入る物体だけ**を描きます。

| 最適化 | 内容 |
| --- | --- |
| **カスケードごとのカリング** | **そのカスケードの箱**に入る物体だけ |
| **小さい物の除外** | **遠いカスケードでは、小さな物体**を影から外す |
| **インスタンシング・GPU Driven** | カスケードごとの描画を、**まとめて**（[GPU Driven](../../rendering/gpu-driven.md)） |
| **1 回の描画で全カスケード** | **ジオメトリ シェーダー**や、**ビュー インスタンシング**で、1 回のドローで複数のカスケードへ。ただし、**効果は環境による** |

## 設計のパラメータ

| パラメータ | 目安 |
| --- | --- |
| **カスケード数** | 3〜4（モバイルは 1〜2） |
| <strong>解像度（各）</strong> | 1024〜2048（高品質は 4096） |
| **最大距離** | 100〜300 m |
| <strong>λ（分割の混合）</strong> | 0.5〜0.9 |
| **ブレンド幅** | 各カスケードの 5〜10% |
| **フォーマット** | D32_FLOAT（または D16 で帯域を半分に） |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **画面全体でほぼ一定の影の細かさ** | **N 回、シーンを描く**（コスト・メモリが N 倍） |
| **屋外の太陽に最適** | **境界のアーティファクト**（ブレンドで軽減） |
| **実装が標準的で資料が豊富** | **ちらつき対策**（スナップ・球フィット）が要る |
| **PCF などとそのまま組み合わせられる** | **遠くは粗い**（距離の限界） |

## よくあるミス

??? failure "カメラが動くと、影の縁がちらちらする"
    **テクセルのスナップ**と**球でのフィット**を入れます。

??? failure "近くの影が粗く、遠くが無駄に細かい"
    **カスケード**に分割します。**λ** で近くを細かく。

??? failure "カスケードの境目で、影が突然変わる"
    **境界でブレンド**します。

??? failure "視錐台の外にある、影を落とす物体の影が欠ける"
    **近クリップ面を光の方向に延ばす**か、**深度クランプ**を使います。

??? failure "バイアスを、全カスケードで同じにして、遠いカスケードでアクネ・近いカスケードで浮く"
    **テクセルの大きさに比例**させます。

??? failure "全カスケードを、毎フレーム フル品質で描いて、重い"
    **遠いカスケードは、更新頻度・LOD・カリング**で軽くします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CSM ＝ <strong>視錐台を奥行きで分割し、分割ごとにシャドウ マップ</strong>。<strong>近いほど、細かい</strong>
    - [x] 分割は<strong>対数と一様の中間（PSSM、λ）</strong>。<strong>影の最大距離</strong>を決める
    - [x] 各カスケードの射影は、<strong>分割を覆う球（安定）</strong>。<strong>テクセルのスナップ</strong>でちらつきを止める
    - [x] <strong>視錐台の外の遮蔽物</strong>のため、<strong>光の方向に範囲を延ばす（深度クランプ）</strong>
    - [x] <strong>境界はブレンド</strong>、<strong>最大距離はフェード</strong>、<strong>カスケードごとにバイアス・PCF を調整</strong>

## 参考

- Dimitrov, "Cascaded Shadow Maps"（NVIDIA 2007）
- Zhang et al., "Parallel-Split Shadow Maps for Large-scale Virtual Environments"（VRCIA 2006）
- Microsoft, "Cascaded Shadow Maps"（DirectX ドキュメント）

## 関連ページ

- [影](index.md)
- [シャドウ マップの基礎](shadow-map-basics.md)
- [バイアス](bias.md)
- [PCF](pcf.md)
- [影のコスト（最適化）](../../rendering/shadows.md)
- [視錐台](../../3d/projection.md)

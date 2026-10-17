---
title: リフレクション プローブ
tags:
  - 描画
---

# リフレクション プローブ

**リフレクション プローブ**（Reflection Probe）は、**空間のある 1 点から、全方向を撮った写真**（**キューブマップ**）を、**あらかじめ作っておき**、反射の景色として使う方式です。**どんな形の面にも安く、ぼけた反射**を付けられるので、**PBR の IBL（画像ベース ライティング）の鏡面項**の基本になっています。このページでは、**キューブマップの作り方・粗さへの対応（事前フィルタ）・視差の補正・複数のプローブの混ぜ方**を、順に説明します。

!!! tip "ポイント"
    - プローブ ＝ <strong>ある点から見た、全方向の景色のキューブマップ</strong>。<strong>反射方向 R で引くだけ</strong>。
    - 粗さに応じた反射は、<strong>事前に粗さごとにぼかしたミップ</strong>を持っておく（<strong>事前フィルタ</strong>）。
    - 反射は<strong>プローブの位置から見た景色</strong>。<strong>面とプローブの位置がずれると、映り込みがずれる</strong>（視差）。<strong>視差補正</strong>が必要。
    - 補正は<strong>プローブが写す範囲を「箱・球」で近似</strong>して、<strong>反射レイとその箱の交点</strong>から引き直す。
    - <strong>複数のプローブ</strong>を<strong>距離や影響範囲で混ぜる</strong>。
    - 動的なシーンには<strong>更新（再撮影）</strong>が必要。<strong>静的な背景向き</strong>。

## 発想

反射は、「**反射方向 R に何が見えるか**」です。**R 方向の景色**を**シーンから、その場で求める**のは大変です（レイトレ・SSR）。**空間の 1 点（プローブの位置）から見た景色**を**あらかじめ写真に撮って**おけば、**R 方向のピクセルを読むだけ**で済みます。

| 項目 | 内容 |
| --- | --- |
| **撮影** | プローブの位置から、**6 方向**（上下左右前後）を描き、**キューブマップ**に保存 |
| **使用** | 表面の反射方向 R で、キューブマップを引く（`cube.Sample(sampler, R)`） |
| **粗さ** | 粗さに応じて、**ぼかしたミップ**を引く（次節） |

## キューブマップの作成

| 手順 | 内容 |
| --- | --- |
| **① 位置を決める** | 部屋の中央、広場の中央など。**反射が映る面の近く** |
| **② 6 面を描く** | 90 度の視野角で**+X, −X, +Y, −Y, +Z, −Z** の 6 方向を、HDR で描く |
| <strong>③ ミップを作る（事前フィルタ）</strong> | **粗さごとに反射のぼけ**を事前計算 |
| **④ 保存** | ベイク（事前）または実行時に更新 |

<strong>HDR（浮動小数点）</strong>で保存します。**太陽や光源の明るさ**が**反射のハイライト**に効くためです。

## 粗さへの対応：事前フィルタ（Split-Sum）

粗い面の反射は、**BRDF の山の範囲の景色を、重み付きで平均**したものでした（[反射](index.md)）。これを**表面ごとに実行時に計算するのは重い**ので、**事前計算**します。Epic の Karis が提案した **Split-Sum 近似**が、標準になっています。

### 式を 2 つに分ける

<div class="formula">∫ L_i · f_spec · cosθ dω　≈　( ∫ L_i · D · cosθ dω ) × ( ∫ f_spec · cosθ dω )</div>

| 項 | 内容 | 事前計算 |
| --- | --- | --- |
| **第 1 項：事前フィルタした環境マップ** | **粗さごとに環境をぼかした**キューブマップ（ミップ） | プローブごとに（キューブマップのミップとして） |
| <strong>第 2 項：BRDF の積分（スケールとバイアス）</strong> | `F0 · A + B`（A・B は、`n·v` と粗さから引く） | **BRDF LUT**（2D テクスチャ）を、1 つだけ事前計算 |

詳しい導出は、[PBR](../../3d/pbr.md)の IBL を参照してください。

### ミップ レベルの選び方

**粗さが大きいほど、ぼけた（高いミップの）レベル**を読みます。

```hlsl
float3 SpecularIBL(float3 N, float3 V, float3 albedo, float metallic, float roughness) {
  float3 R = reflect(-V, N);
  float mip = roughness * (max_mip - 1.0);
  float3 prefiltered = env_cube.SampleLevel(linear_sampler, R, mip).rgb;

  float n_dot_v = saturate(dot(N, V));
  float2 brdf = brdf_lut.Sample(linear_sampler, float2(n_dot_v, roughness)).rg;

  float3 F0 = lerp(0.04, albedo, metallic);
  return prefiltered * (F0 * brdf.x + brdf.y);
}
```

| 点 | 説明 |
| --- | --- |
| **`mip = roughness × (最大ミップ)`** | 粗さ 0 でミップ 0（くっきり）、粗さ 1 で最大のミップ（ぼんやり） |
| **BRDF LUT** | `n·v` と粗さを入力にした、2 値（スケール・バイアス）。**プロジェクト全体で 1 枚** |
| **`F0`** | 非金属は約 0.04、金属はアルベド色 |
| **ミップ間はトリリニア補間** | 滑らかに粗さが変わる |

### 事前フィルタの作り方

**各ミップ**は**その粗さの GGX 分布**で、**環境マップを重要度サンプリング**して作ります。

| ミップ | 粗さ | 作り方 |
| --- | --- | --- |
| **0** | 0 | 元のキューブマップ |
| **1〜N** | 粗さを段階的に上げる | **GGX の重要度サンプリング**で、各テクセルを再計算（コンピュート・ピクセルシェーダー） |

**重要度サンプリング**は、**分布の山の部分から多くサンプル**する手法で、**サンプル数を減らせます**（[確率的 SSR](ssr-stochastic.md)で詳しく）。

## 視差の問題と補正

### 視差の問題

プローブは、**1 点（プローブの位置）から見た景色**です。**面とプローブの位置が離れている**と、**面から見た景色とプローブから見た景色が、ずれます**。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="視差の問題">
<text x="20" y="24" class="fig-title">プローブの位置と、反射する面の位置が違うと、映り込みがずれる</text>
<rect x="50" y="50" width="680" height="220" fill="rgba(150,150,150,0.1)" stroke="currentColor" stroke-width="2"/><text x="60" y="68" style="font-size:12px">部屋（壁）</text>
<circle cx="390" cy="160" r="7" fill="#2ea043"/><text x="364" y="184" style="font-size:12px;fill:#2ea043;font-weight:700">プローブ</text>
<line x1="150" y1="250" x2="330" y2="250" stroke="currentColor" stroke-width="5"/><text x="180" y="270" style="font-size:12px">床の面（反射する）</text>
<circle cx="250" cy="250" r="6" fill="currentColor"/><text x="240" y="238" style="font-size:12px">p</text>
<line x1="250" y1="250" x2="500" y2="110" stroke="#e5484d" stroke-width="2.5"/><text x="500" y="104" style="font-size:12px;fill:#e5484d;font-weight:700">本当の反射が当たる壁</text>
<line x1="390" y1="160" x2="640" y2="20" stroke="#4c8bf5" stroke-width="2" stroke-dasharray="5 3"/><text x="520" y="62" style="font-size:12px;fill:#4c8bf5;font-weight:700">プローブから R 方向に引くと…</text>
<text x="420" y="290" style="font-size:12px">→ 実際より、遠く（別の場所）の景色が映ってしまう</text>
</svg>

特に**平らな床**で**壁との境が実際より遠くに映る**・**物が宙に浮いて見える**といった症状が出ます。

### 視差補正：プローブの範囲を箱で近似する

**プローブが写している範囲（部屋）を、箱（または球）で近似**します。**反射レイ**を**表面の位置 p から R 方向に飛ばして、箱と交差する点 H** を求めます。**プローブの位置から H への方向**で、キューブマップを引きます。

<div class="formula">H = p + R · t　（レイと箱の交点）、　引く方向 R′ = H − probe_pos</div>

**表面の位置 p から**、<strong>本当に当たる壁（H）</strong>を求めて、そこを**プローブから見た方向**で引き直すので、**視差のずれが補正されます**。

### 箱（AABB）との交差

```hlsl
float3 BoxProjection(float3 world_pos, float3 R, float3 probe_pos,
                     float3 box_min, float3 box_max) {
  float3 first_plane = (box_max - world_pos) / R;
  float3 second_plane = (box_min - world_pos) / R;
  float3 furthest = max(first_plane, second_plane);
  float distance = min(min(furthest.x, furthest.y), furthest.z);
  float3 hit = world_pos + R * distance;
  return hit - probe_pos;
}
```

| 点 | 説明 |
| --- | --- |
| **`(box_max − pos) / R`・`(box_min − pos) / R`** | 3 軸の箱の面までの距離（レイが各面に当たる t） |
| **`max(first, second)`** | **前向き（レイが進む側）の面**を選ぶ |
| **`min(…x, y, z)`** | **最初に当たる**面（箱の内側からの出口） |
| **戻り値** | プローブから見た方向（正規化はサンプラーが不要） |

!!! note "箱の範囲の決め方"
    **プローブが写す範囲**（影響範囲）を、**部屋の大きさに合わせた箱**にします。**箱が実際の壁と合っているほど**、補正が正確です。**合っていないと補正が逆効果**になることもあります。

### 視差補正の限界

| 限界 | 説明 |
| --- | --- |
| **箱の近似** | **部屋の中の家具・物体は箱の壁として扱われる** → **家具の反射は、壁の位置に映る** |
| **プローブ位置の物陰** | プローブから見えなかった所（家具の裏）は、撮れていない |
| **不規則な形の部屋** | 箱で表せない部屋では、**補正が合わない** |
| **動く物** | プローブには映らない（動的な更新が必要） |

## 複数のプローブを混ぜる

**1 つのプローブ**では、**広いシーンをカバーできません**。**場所ごとに複数のプローブ**を置き、**表面の位置に応じて、混ぜます**。

| 方式 | 内容 |
| --- | --- |
| <strong>影響範囲（ボリューム）</strong> | 各プローブに**影響範囲の箱**。**範囲内の表面にだけ**使う |
| **ブレンド** | **範囲が重なる所**は、**距離・重み**で複数のプローブを混ぜる |
| **ブレンド距離** | 範囲の端で**徐々に弱める**（突然切り替わらないように） |
| **優先度** | 小さいプローブ（部屋の中）を、大きいプローブ（外）より優先 |
| **グローバル プローブ** | **シーン全体**（空・遠景）を覆う、粗いプローブ。**フォールバック** |

```hlsl
float3 BlendedReflection(float3 pos, float3 R, float roughness) {
  float3 result = 0;
  float total_weight = 0;
  for (int i = 0; i < probe_count_in_cell; ++i) {
    Probe p = probes[probe_indices[i]];
    float w = ProbeWeight(p, pos);
    if (w <= 0.0) continue;
    float3 dir = BoxProjection(pos, R, p.position, p.box_min, p.box_max);
    result += p.cube.SampleLevel(sampler, dir, roughness * max_mip).rgb * w;
    total_weight += w;
  }
  return result / max(total_weight, 1e-4);
}
```

<strong>クラスタード（セル分割）</strong>で、各セルに影響するプローブを**事前に絞り込む**と、速くなります（[Tiled と Clustered](../../rendering/light-culling.md)のライトと同じ構造）。

## ベイクと動的更新

| 方式 | 内容 | 向く場面 |
| --- | --- | --- |
| **事前ベイク** | ビルド時に撮影・フィルタ。**実行時のコストなし** | **静的な背景** |
| **実行時に更新** | 実行中に、**6 面を描き直す**（1 フレームに 1 面ずつ分散、など） | 時間帯が変わる・動く物が映る場合 |
| <strong>リアルタイム（毎フレーム）</strong> | 非常に重い。**車のミラー・重要な 1 箇所**だけ | 限定的 |

**事前フィルタ**（ミップの作成）は、**ベイクなら事前、動的なら、コンピュート シェーダーで毎回**行います。**コストが大きい**ので**更新頻度を下げる**のが普通です。

## 空（スカイボックス）との関係

<strong>屋外の遠い景色（空）</strong>は、**プローブの視差を気にしなくてよい**（無限遠）ので<strong>グローバルなプローブ（スカイ）</strong>として、**全シーンに適用**します。**近くの建物・地面**は**ローカル プローブ**で補います。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **安い**（キューブマップを引くだけ） | **位置が 1 点**。視差・詳細なずれ |
| **あらゆる形の面**に使える | **動く物・変化するシーン**を映せない（更新が必要） |
| **粗さに対応**（ミップ） | **自己反射**（そこにあるはずの物がプローブに写っている） |
| **画面外の景色も映る** | **接地の細かい反射**（足元の映り込み）が、出ない |

## SSR と組み合わせる

**プローブは遠くの粗い反射**、**SSR は近くの細かい映り込み**が得意です。**組み合わせる**のが一般的です（[SSR のフォールバックと合成](ssr-fallback.md)）。

| 距離・粗さ | 向く方式 |
| --- | --- |
| **遠景・粗い反射** | プローブ |
| **近く・細かい反射**（足元・接地） | SSR |
| <strong>平面（水面・鏡）</strong> | 平面反射 |

## よくあるミス

??? failure "視差補正をせず、床の反射で壁が宙に浮く"
    **箱による視差補正**を入れます。

??? failure "プローブの箱が、実際の部屋の大きさと合っておらず、反射がゆがむ"
    **部屋にぴったり**の箱にします。

??? failure "LDR（8 ビット）でキューブマップを保存して、ハイライトが弱い"
    <strong>HDR（浮動小数点）</strong>で保存します。

??? failure "事前フィルタ（ミップ）を作らず、粗い面がくっきり映る"
    **粗さごとのぼかしたミップ**を作ります。

??? failure "プローブ自身（反射する物体）が、プローブに写り込んで自分の反射を見ている"
    撮影時に**自分自身を除外**します。

??? failure "プローブの切り替えが、突然で目立つ"
    **ブレンド距離**で徐々に混ぜます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プローブ ＝ <strong>1 点から見た全方向のキューブマップ</strong>。<strong>反射方向 R で引く</strong>
    - [x] <strong>粗さ</strong>は<strong>事前フィルタしたミップ ＋ BRDF LUT</strong>（Split-Sum）
    - [x] <strong>視差</strong>は<strong>箱への投影（視差補正）</strong>で補正。<strong>箱は部屋に合わせる</strong>
    - [x] <strong>複数のプローブは、影響範囲とブレンドで混ぜる</strong>
    - [x] <strong>安いが位置が 1 点・動かない</strong>。<strong>SSR・平面反射と組み合わせる</strong>

## 参考

- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013 Course、Split-Sum 近似）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering"（視差補正・プローブ ブレンド）

## 関連ページ

- [反射](index.md)
- [SSR の基礎](ssr-basics.md)
- [SSR のフォールバックと合成](ssr-fallback.md)
- [PBR](../../3d/pbr.md)
- [Tiled と Clustered](../../rendering/light-culling.md)

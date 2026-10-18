---
title: Shadows for Many Lights
tags:
  - 描画
---

# Shadows for Many Lights

**影を持つライトが数十個になる**と、**すべてにシャドウ マップを作ると、フレームが破綻**します。**そこで、シャドウ マップを 1 枚の大きなアトラスにまとめ、画面上の大きさに応じて解像度を配分し、静止したライトの影はキャッシュ**します。このページでは、**アトラス・解像度の割り当て・キャッシュ・影付きライトの描画・バイアスと精度**を説明します。

!!! tip "ポイント"
    - **シャドウ マップを、大きなアトラスにまとめて管理**する。
    - **画面上で大きい・近いライトに、大きな解像度**を割り当てる。
    - **静止したライトと静止した物の影は、キャッシュして、毎フレーム描かない**。
    - **影を持つライトの数に、上限**を設ける。

<!-- fig:many-lights-cache:begin -->

<svg class="fig illust motion" data-fig="many-lights-cache" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-many-lights-cache" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">多数のライトの影:毎フレーム、少しずつ更新して、予算に収める</text>
<rect x="50" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="100.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 1</text>
<text x="100.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="164" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.1292;0.1917;0.2542;0.3167;0.3792;0.4417;0.5042;0.5667;0.6292;0.6917;0.7542;0.8167;0.8792" values="#e0f2fe;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<text x="214.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 2</text>
<text x="214.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">動く</text>
<rect x="278" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="328.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 3</text>
<text x="328.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="392" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="442.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 4</text>
<text x="442.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="506" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="556.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 5</text>
<text x="556.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="620" y="100" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="670.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 6</text>
<text x="670.0" y="152" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="50" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="100.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 7</text>
<text x="100.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="164" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="214.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 8</text>
<text x="214.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="278" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.1292;0.1917;0.2542;0.3167;0.3792;0.4417;0.5042;0.5667;0.6292;0.6917;0.7542;0.8167;0.8792" values="#e0f2fe;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<text x="328.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 9</text>
<text x="328.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">動く</text>
<rect x="392" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="442.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 10</text>
<text x="442.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="506" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="556.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 11</text>
<text x="556.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="620" y="204" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="670.0" y="232" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 12</text>
<text x="670.0" y="256" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="50" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="100.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 13</text>
<text x="100.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="164" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="214.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 14</text>
<text x="214.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="278" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"><animate attributeName="fill" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.1292;0.1917;0.2542;0.3167;0.3792;0.4417;0.5042;0.5667;0.6292;0.6917;0.7542;0.8167;0.8792" values="#e0f2fe;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<text x="328.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 15</text>
<text x="328.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">動く</text>
<rect x="392" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="442.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 16</text>
<text x="442.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="506" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="556.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 17</text>
<text x="556.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<rect x="620" y="308" width="100" height="90" rx="8" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>
<text x="670.0" y="336" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ライト 18</text>
<text x="670.0" y="360" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">静止</text>
<text x="50" y="66" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">黄色 = このフレームで、シャドウ マップを描き直したライト。他は、前のフレームの結果を使い回す<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="50" y="366" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">動くライト（赤い文字）は、毎フレーム更新。静止したライトは、順番に（ラウンド ロビン）、数個ずつ更新する。</text>
<text x="50" y="390" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 フレームに描くシャドウ マップの数に、上限を決める → コストが一定になる。</text>
</svg>

<!-- fig:many-lights-cache:end -->

## 多数のライトの影
**ライトが多い**ほど、**影の計算がすぐに破綻**します。

ライトが増えると、3 つのコストが同時に膨らみます。描画回数は、点光源が 6 回、スポットが 1 回で、ライトごとに掛かります。メモリは、キューブ 1 つ（1024²×6 面）が約 24 MB（D32）なので、数十個で数百 MB になります。フィルタのコストは、画素ごとに、影付きのライトの数だけサンプルが必要です。

### 管理の方法

| 方法 | 内容 |
| --- | --- |
| **影付きライトの数を制限** | **重要なライトだけ**影付き（例：画面の近く・大きい・明るい） |
| **優先度付け** | **画面上の大きさ・明るさ・距離**で**スコア**を付け、**上位 N 個**だけに影 |
| **アトラス** | **1 枚の大きなテクスチャ**に、**複数のシャドウ マップ**を**敷き詰める**。**ライトごとに解像度を可変**（近いライトは大きく） |
| **解像度の可変** | **画面上で小さいライト**は、**低い解像度** |
| **更新頻度** | **静的なライト・静的な物**は**キャッシュ**し、**動く物が入ったときだけ更新** |
| **遠方・画面外の除外** | **視錐台の外・遠いライト**は**描かない** |

### シャドウ マップのキャッシュ

**静的なシーンのシャドウ マップ**は、**一度描いた結果を再利用**できます。

キャッシュの戦略です。静的なジオメトリの影はキャッシュし、動的な物の影だけを毎フレーム上書き（または合成）します。動かないライトは、ライトが動いたときだけ再生成し、そうでなければ再描画しません。動く物のいる範囲だけを部分的に更新するダーティ領域の管理もあります。

**2 枚**（静的用・動的用）を**持ち、画素ごとに両方を引いて、小さい方（より暗い方）を取る**方法もあります。

## 影のあるライトの描画での使い方
**ライティング**の段階で**ライトごとの影の係数**を、**そのライトの寄与に掛けます**。

```hlsl
float shadow = SpotShadow(world_pos, light_index);
float3 lit = EvaluateLight(light, surface) * shadow;
```

**クラスター ライティング**・**タイル ベース**と組み合わせると、**影付きライトの情報**を**ライト リストに含めて、引けるようにします**（[ライト カリング](../../../rendering/light-culling.md)）。

## バイアスと精度
バイアスと精度の注意点です。透視投影の深度は非線形で、近くに集中して遠くで精度が不足します。近クリップ面を大きく、遠クリップ面を短くして精度を保ちます。バイアスは距離によって必要な量が変わるので、ワールド単位の法線オフセットが扱いやすいです（[Shadow Bias](../bias/index.md)）。Reversed-Z は、シャドウ マップにも有効です（浮動小数点の深度）。

## 問題：影を落とす光は、数に限りがある

光が、**100 個**あっても、**すべてに、シャドウ マップを、作る**ことは、できません（点光源 1 つで、シーンを、6 回、描く）。**どの光に、影を、与えるか**、**どう効率よく、作るか**を、設計する必要があります。

## 影を、落とす光を、選ぶ

| 基準 | 内容 |
| --- | --- |
| **画面に、映っている** | 視錐台の外にある光（光の、範囲球が、視錐台と、交わらない）は、**影を、作らない** |
| **画面上の、大きさ** | 光が、画面に、**大きく**映る（近い、明るい光）ほど、**優先** |
| **明るさ** | 暗い光は、影が、見えない。**影を、省く** |
| **距離** | **遠い光**は、影が、細かく見えない。**影なし**、または、**低解像度** |
| **重要さ** | ゲームの、**演出上、重要な光**（プレイヤーの懐中電灯、重要な、ランプ）は、**優先** |

```cpp
// 光ごとに、「影の優先度」を、計算して、上位 N 個だけ、影を作る。
float ShadowPriority(const Light& light, const Camera& camera) {
  const float dist = Distance(light.position, camera.position);
  if (dist > light.range + camera.far_plane) return 0.0f;
  if (!camera.frustum.Intersects(Sphere{light.position, light.range})) return 0.0f;
  // 画面上の、おおよその大きさ（半径 / 距離）× 明るさ
  const float screen_size = light.range / std::max(dist, 1.0f);
  return screen_size * light.intensity * light.importance;
}

// 優先度の高い順に、N 個（8 個など）を選んで、シャドウ マップを割り当てる。
std::sort(lights.begin(), lights.end(), [&](auto& a, auto& b) { return a.priority > b.priority; });
for (int i = 0; i < std::min<int>(kMaxShadowLights, lights.size()); ++i) lights[i].shadow_slot = i;
```

## シャドウ マップを、アトラスに

影を、落とす、光が、複数あるとき、シャドウ マップを、**1 枚の大きなテクスチャ（アトラス）**に、**まとめます**。ライトごとに、テクスチャを、**バインドし直す**必要が、なくなります。

```text
┌──────────┬──────┬──────┐
│          │ 光 2 │ 光 3 │
│  光 1     ├──────┼──────┤
│ (2048²)  │ 光 4 │ 光 5 │
│          │ (512²)│(512²)│
└──────────┴──────┴──────┘
   4096×4096 のアトラスに、解像度の違う、シャドウ マップを、詰める
```

| 利点 | 内容 |
| --- | --- |
| **1 つのテクスチャ** | シェーダーに、渡す、リソースが、1 つ |
| **解像度を、光ごとに、変えられる** | 画面上で、大きい光は、**大きなタイル**。小さい光は、**小さなタイル** |

各光の、**アトラス内の、位置と大きさ**（`offset`、`scale`）を、**定数バッファ**に、持たせ、**UV を、変換**して、読みます。

```hlsl
struct ShadowTile { float4 uv_scale_offset; };      // xy = スケール、zw = オフセット（アトラス内の位置）
StructuredBuffer<ShadowTile> g_tiles : register(t10);

float SampleShadowAtlas(uint tile_index, float2 local_uv, float depth) {
  ShadowTile t = g_tiles[tile_index];
  float2 atlas_uv = local_uv * t.uv_scale_offset.xy + t.uv_scale_offset.zw;
  return g_shadow_atlas.SampleCmpLevelZero(g_shadow_sampler, atlas_uv, depth);
}
```

**タイルの境界**では、**PCF が、隣のタイルを、読んで**しまうので、**タイルの縁に、余白**を設け、**UV を、余白の内側に、クランプ**します。

## 描画の、頻度を、減らす

**すべての光の影を、毎フレーム、更新**する必要は、ありません。

| 光の種類 | 更新 |
| --- | --- |
| **静止した光 + 静止した物** | **一度作って、保存**（キャッシュ）。**更新しない** |
| **静止した光 + 動く物** | **静止した物の、シャドウ マップ**を、キャッシュし、**動く物だけ**を、毎フレーム、描き足す（2 枚を、合成） |
| **動く光** | 毎フレーム更新（重い）。**数を、制限** |
| **遠い光** | **数フレームに 1 回**（影が、少し、遅れても、気づかない） |

### 静止物のキャッシュ

```text
キャッシュ（起動時、または、変更時に 1 回）:  静止した物だけを、深度に描く → static_shadow_map
毎フレーム:  static_shadow_map を、コピー → dynamic_shadow_map に、動く物を、描き足す（深度テストで、手前が、勝つ）
```

```cpp
// 静止物の影のキャッシュを、毎フレームの、シャドウ マップに、コピーしてから、動く物を、描き足す。
context->CopyResource(shadow_map.Get(), static_shadow_cache.Get());     // 静止物の深度を、コピー
context->OMSetRenderTargets(0, nullptr, shadow_dsv.Get());
// ここでは、Clear しない（コピーした深度を、残したまま、動く物を、重ねて描く）
DrawDynamicShadowCasters();
```

**動く物が、少なければ**、**シャドウ パスが、劇的に、軽くなります**。

## ライトの、種類による、判断

| 光 | 影の扱い |
| --- | --- |
| **太陽**（1 つ） | CSM、毎フレーム更新（[CSM](../cascaded.md)） |
| **プレイヤーの、懐中電灯** | **スポットライト**の、影。毎フレーム更新。高解像度 |
| **近くの、点光源**（数個） | キューブマップ。静止物は、キャッシュ |
| **遠くの、点光源**（多数） | **影なし**（または、低解像度、更新を、間引く） |
| **小さな、装飾の光**（ろうそく） | **影なし**。コンタクト シャドウで、補う（[Contact Shadows](../contact-shadows.md)） |

## 影なしの光に、影の、効果を

影を、落とさない、光でも、**暗さの、手がかり**が、欲しい場面があります。

| 方法 | 内容 |
| --- | --- |
| **コンタクト シャドウ** | 画面空間で、**短い距離**の、影を作る（[Contact Shadows](../contact-shadows.md)） |
| **AO**（アンビエント オクルージョン） | 物の、隙間・接触部分を、暗くする（[AO](../../ao/index.md)） |
| **距離フィールドの、影** | 全体に、**安く**、ソフトな影（[Distance Field Shadows](../sdf-shadows.md)） |

## クラスタード シェーディングとの、関係

数百の光を、**画面の、小さな領域（クラスター）**ごとに、**影響する光を、絞って**、シェーディングする方法です（Olsson ら、2012）。**影を、落とす光**は、**クラスターごとの、光のリスト**の中で、**影のアトラスの、タイル番号**を、持ちます。

```hlsl
// クラスターの、光のリストを、走査して、影つきの光だけ、シャドウ マップを読む。
for (uint i = 0; i < light_count_in_cluster; ++i) {
  Light light = g_lights[light_indices[i]];
  float shadow = 1.0;
  if (light.shadow_tile >= 0) shadow = SampleLightShadow(light, world_pos, normal);
  color += ShadeLight(light, ...) * shadow;
}
```

## よくあるミス

??? failure "影付きライトの数が増えて、フレーム時間が増える一方"
    **影付きライトの数に上限・距離で影を切る・キャッシュ**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **アトラスで管理・解像度を配分・キャッシュ**
    - [x] **影付きライトの数を制限**

## 参考

- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012
- Harada, McKee, Yang, "Forward+: Bringing Deferred Lighting to the Next Level", Eurographics 2012 Short Papers
- Brabec, Annen, Seidel, "Shadow Mapping for Hemispherical and Omnidirectional Light Sources", Advances in Modelling, Animation and Rendering (Computer Graphics International 2002)（放物面マッピング）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Virtual Shadow Maps](../virtual-shadow-maps.md)
- [Tiled と Clustered](../../../rendering/light-culling.md)

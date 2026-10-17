---
title: 草と木
tags:
  - 描画
---

# 草と木

**地形の上の植生**（草・低木・木）は、**数が桁違いに多い**です。**1 km 四方に草を 100 万本**置くことも**普通**です。1 本ずつ描画命令を出すのは**無理**なので、**インスタンシングで一括描画**し、**カリングと LOD で数を減らし**、**風で揺らします**。このページでは、**配置・インスタンシング・カリング・草の形（ビルボードと草の葉）・風・木の LOD（インポスター）・半透明の問題**を説明します。

!!! tip "ポイント"
    - 大量の植生 ＝ <strong>インスタンシング</strong>（<strong>1 回の描画命令で数千〜数万本</strong>）。
    - 配置は<strong>ノイズ・密度マップ</strong>から<strong>決定的に生成</strong>（<strong>セルごとにハッシュ</strong>）。<strong>メモリに全部持たない</strong>。
    - <strong>カリング</strong>：<strong>視錐台＋距離</strong>。<strong>GPU（コンピュート）でやる</strong>と<strong>速い</strong>。
    - 草 ＝ <strong>数枚の板ポリ（クロス）か、1 本ずつの細い葉</strong>。<strong>遠くは減らす・密度を下げる</strong>。
    - 風 ＝ <strong>頂点シェーダーで揺らす</strong>。<strong>根元は固定、先端ほど大きく</strong>。
    - 木 ＝ <strong>LOD</strong>。<strong>遠くは板（ビルボード／インポスター）に置き換え</strong>。
    - <strong>葉の半透明</strong>は<strong>アルファ テスト＋ A2C</strong>（[半透明](../translucency/alpha-test/index.md)）。

## 配置

**植生の位置**は**何を元に決めるか**です。

| 方法 | 内容 |
| --- | --- |
| **手で置く** | **エディタで 1 本ずつ**。**主役の木・目立つ物** |
| **ブラシで散布** | **範囲に密度を指定してランダムに配置**（**保存は位置のリスト**） |
| **ルールで自動** | **地形の高さ・傾き・スプラット マップ・ノイズ**から**決定的に生成** |
| **GPU 生成** | **カメラ周りのセルについて、コンピュートで毎フレーム生成**（**保存が不要**） |

**GPU 生成の草**は、**ワールドを小さなセル（例：1 m）に区切り**、**セルのハッシュから、乱数で位置・向き・大きさを決めます**。**同じセルは毎回同じ結果になる**ので、**保存が要りません**。

```hlsl
uint HashCell(int2 cell) {
  uint h = uint(cell.x) * 73856093u ^ uint(cell.y) * 19349663u;
  h ^= h >> 13;
  h *= 0x5bd1e995u;
  h ^= h >> 15;
  return h;
}

float Random01(inout uint state) {
  state = state * 1664525u + 1013904223u;
  return float(state >> 8) / 16777216.0;
}

[numthreads(8, 8, 1)]
void GenerateGrass(uint3 id : SV_DispatchThreadID) {
  int2 cell = camera_cell + int2(id.xy) - kHalfCells;
  uint state = HashCell(cell);

  float2 offset = float2(Random01(state), Random01(state));
  float2 xz = (float2(cell) + offset) * cell_size;
  float density = density_map.SampleLevel(linear_clamp, WorldToUV(xz), 0).r;
  if (Random01(state) > density) return;

  float height = SampleTerrainHeight(xz);
  float rotation = Random01(state) * 6.2831853;
  float scale = lerp(0.7, 1.3, Random01(state));
  AppendInstance(float3(xz.x, height, xz.y), rotation, scale);
}
```

| 点 | 説明 |
| --- | --- |
| **セルのハッシュ** | **同じセルは毎フレーム同じ位置**（**揺れない・点滅しない**） |
| **密度マップ** | **スプラット マップの「草」の重み**などで**草が生える所だけ** |
| **カメラ周りのセルだけ** | **遠くのセルは生成しない** |
| **`AppendInstance`** | **`AppendStructuredBuffer`**に書く。**後で `DrawIndexedInstancedIndirect`** |

## インスタンシング

**同じメッシュを位置・向き・大きさだけ変えて、大量に描く**のが**インスタンシング**です。

| 方式 | 内容 |
| --- | --- |
| **`DrawIndexedInstanced`** | **インスタンス数を指定**。**インスタンスごとのデータは、頂点バッファか StructuredBuffer** |
| **`DrawIndexedInstancedIndirect`** | **インスタンス数を GPU が決める**（**カリング結果をそのまま**）。**CPU 待ちが無い** |
| **インスタンス データ** | **位置（float3）・回転（1 つの角度）・スケール・色の個体差**など。**16〜32 バイト** |

```hlsl
struct GrassInstance {
  float3 position;
  float rotation;
  float scale;
  float color_variation;
  float2 padding;
};

StructuredBuffer<GrassInstance> instances : register(t0);

VSOutput VSMain(VSInput input, uint instance_id : SV_InstanceID) {
  GrassInstance instance = instances[instance_id];
  float s = sin(instance.rotation);
  float c = cos(instance.rotation);
  float3 local = input.position * instance.scale;
  float3 rotated = float3(local.x * c + local.z * s, local.y, -local.x * s + local.z * c);
  float3 world = rotated + instance.position;

  VSOutput output;
  output.position = mul(float4(world, 1), view_projection);
  output.color_variation = instance.color_variation;
  return output;
}
```

**1 つの描画命令にまとめる**ので、**CPU の負担が小さく**、**GPU も効率的**です。**メッシュ（ポリゴン数）が小さい**ほど、**インスタンシングの効果が大きい**です。

## カリング

**画面に映らない・遠すぎる植生は、描きません**。

| 種類 | 内容 |
| --- | --- |
| **距離カリング** | **一定距離より遠い物は描かない**（**草は 50〜100 m 程度**）。**フェードで消す** |
| **視錐台カリング** | **視錐台の外を捨てる** |
| **オクルージョン カリング** | **山や建物の裏は捨てる**（**Hi-Z**） |
| **密度の距離減衰** | **遠いほど、間引く**（**一部の草だけ描き、残りを太くする**） |

**コンピュート シェーダーで全インスタンスを判定**し、**生き残ったものを別バッファに詰め**ます。

```hlsl
[numthreads(64, 1, 1)]
void CullInstances(uint3 id : SV_DispatchThreadID) {
  if (id.x >= instance_count) return;
  GrassInstance instance = all_instances[id.x];
  float distance_to_camera = distance(instance.position, camera_position);
  if (distance_to_camera > max_distance) return;
  if (!SphereInFrustum(instance.position, instance.scale * radius)) return;
  uint index;
  visible_count.InterlockedAdd(0, 1, index);
  visible_instances[index] = instance;
}
```

詳しい構成は、[GPU Driven](../../rendering/index.md) と同じ考え方です。

## 草の形

**草は細い葉が大量に生えている**ので、**ポリゴンを工夫**します。

| 方式 | 内容 |
| --- | --- |
| <strong>クロス板（板ポリを十字）</strong> | **草の絵を貼った板を 2 枚、十字に交差**。**簡単・古典的** |
| **3 枚〜の房** | **3〜5 本の葉の板を扇状に**。**ポリゴンは 6〜10 枚** |
| **1 本ずつの葉** | <strong>細長い三角形の帯（3〜7 セグメント）</strong>を**1 本ずつ**。**曲げて、風で揺らせる**。**距離で本数を減らす** |
| **ビルボード** | **常にカメラを向く**。**遠景用**（**回転しても形が崩れない草原の塊**） |

**1 本ずつの葉**は、**頂点が先端ほど細く、少し曲がっている**メッシュです。**インスタンスごとに高さ・曲がり・色を変える**と**自然**です。

```hlsl
float bend = instance.bend * pow(input.height_t, 2.0);
local.x += bend;
local.y *= lerp(1.0, 0.9, bend);
```

| 点 | 説明 |
| --- | --- |
| **`height_t`** | **葉の根元 0、先端 1** |
| **二乗で曲げる** | **先端ほど大きく曲がる**（**根元は動かない**） |
| **根元の色を暗く** | **地面との馴染み・AO の代わり**。**先端を明るく** |
| **地形の色に合わせる** | **草の根元の色を地形のテクスチャの色から取る**と、**境目が消える** |

## 風

**風で揺れる草・木は画面に動きと生気**を**与えます**。**頂点シェーダーで頂点をずらす**のが**基本**です。

<svg class="fig illust motion" data-fig="grass-wind" viewBox="0 0 780 200" role="img" aria-label="風で揺れる草">
<text x="20" y="24" class="fig-title">風：根元は動かず、先端ほど大きく揺れる</text>
<line x1="40" y1="170" x2="740" y2="170" stroke="currentColor" stroke-opacity="0.4"/>
<g stroke="#2ea043" stroke-width="5" fill="none" stroke-linecap="round">
<path d="M120,170 Q120,110 120,60"><animate attributeName="d" values="M120,170 Q120,110 120,60;M120,170 Q125,110 150,62;M120,170 Q120,110 120,60;M120,170 Q115,110 95,64;M120,170 Q120,110 120,60" dur="3s" repeatCount="indefinite"/></path>
<path d="M300,170 Q300,115 300,70"><animate attributeName="d" values="M300,170 Q300,115 300,70;M300,170 Q305,115 328,72;M300,170 Q300,115 300,70;M300,170 Q295,115 275,74;M300,170 Q300,115 300,70" dur="3s" begin="0.4s" repeatCount="indefinite"/></path>
<path d="M480,170 Q480,105 480,50"><animate attributeName="d" values="M480,170 Q480,105 480,50;M480,170 Q486,105 512,54;M480,170 Q480,105 480,50;M480,170 Q474,105 452,56;M480,170 Q480,105 480,50" dur="3s" begin="0.8s" repeatCount="indefinite"/></path>
<path d="M660,170 Q660,112 660,66"><animate attributeName="d" values="M660,170 Q660,112 660,66;M660,170 Q665,112 688,68;M660,170 Q660,112 660,66;M660,170 Q655,112 636,70;M660,170 Q660,112 660,66" dur="3s" begin="1.2s" repeatCount="indefinite"/></path>
</g>
</svg>

```hlsl
float3 ApplyWind(float3 world_position, float height_t, float2 wind_direction, float wind_strength, float time) {
  float phase = dot(world_position.xz, wind_direction) * 0.4 + time * 2.0;
  float sway = sin(phase) + 0.5 * sin(phase * 2.3 + 1.7);
  float amount = height_t * height_t * wind_strength * sway;
  return world_position + float3(wind_direction.x, 0, wind_direction.y) * amount;
}
```

| 点 | 説明 |
| --- | --- |
| **位置に応じた位相** | **場所ごとにずらす**と**風が波のように草原を渡る** |
| **周波数の違う波を足す** | **単調でなくなる** |
| **`height_t²`** | **根元は動かず、先端が大きく動く** |
| **風のテクスチャ** | **風の強さ・向きをスクロールするノイズのテクスチャ**で**与える**（**突風が移動する**） |
| **木の揺れ** | **幹はゆっくり大きく、枝は中くらい、葉は細かく速く**の**3 層** |

**頂点カラーに揺れの強さ（幹 0・先端 1）を焼いておく**と**美術側で調整**できます。

## 踏まれる草

**キャラクターが歩くと草が倒れる**表現です。**キャラクターの位置をシェーダーに渡し、近い草を押しのけます**。

```hlsl
float3 away = world_position - character_position;
float influence = saturate(1.0 - length(away.xz) / push_radius);
world_position.xz += normalize(away.xz) * influence * push_strength * height_t;
world_position.y -= influence * push_strength * height_t;
```

**複数の物を扱うなら、物の位置を高さマップ風のテクスチャに描き、それを草が読む**（[波紋のブラシ](../water/interaction.md)と同じ）のが**スケールします**。

## 木

**木はポリゴンが多く（数万）、枚数も多い**ので、**LOD が重要**です。

| LOD | 内容 |
| --- | --- |
| <strong>LOD 0（近景）</strong> | <strong>幹・枝の 3D モデル ＋ 葉のカード（板に葉の絵）</strong> |
| **LOD 1〜2** | **枝を減らす・葉のカードを統合** |
| <strong>インポスター（遠景）</strong> | **木を数方向から撮った絵（板ポリ）に置き換え**。**カメラの向きに応じて、絵を切り替える／混ぜる** |
| <strong>ビルボード（最遠）</strong> | **1 枚の板** |

**インポスター**は、**事前に木を複数の視点（例：8×8 = 64 方向）から撮影**し、**アトラスに並べます**。**描画時はカメラに最も近い方向の絵を選び、板に貼ります**。**法線・深度もアトラスに持つと、ライティングも正しく**なります。

| 点 | 説明 |
| --- | --- |
| **LOD の切り替え** | <strong>ディザリング（市松のフェード）</strong>で、**ポップを隠す**（[半透明](../translucency/alpha-test/index.md)） |
| **葉のカード** | **1 枚に複数の葉を描いた板**。**アルファ テスト** |
| **幹と葉でマテリアルを分ける** | **幹は不透明、葉はアルファ テスト** |
| **影** | **影の LOD は、描画より粗くする**（[影](../shadows/index.md)） |

## 半透明の問題

**草と葉はアルファ テスト（切り抜き）で描きます**。**半透明ブレンドは、ソートが要るので不向き**です。

| 問題 | 対策 |
| --- | --- |
| **ジャギー** | **A2C（Alpha To Coverage）＋ MSAA**。**または TAA で滑らかに** |
| **遠くで草が痩せる** | **ミップでアルファが薄まる**。**ミップごとにアルファを補正**（[アルファ テスト](../translucency/alpha-test/index.md)） |
| **裏面が暗い／明るい** | **両面描画で裏面の法線を反転**。**葉の透過光を足す** |

## ライティング

| 要素 | 内容 |
| --- | --- |
| **法線** | **草の法線を地形の法線に寄せる**と**草原が面として一様に照らされ、ごちゃつかない** |
| **透過光** | **葉は光を通す**。**太陽が背後にあると明るい** |
| **AO** | **根元を暗く**（高さで）。**木の内側も暗く** |
| **影** | **草は影を落とさない・受けるだけ**にして、**軽くする** |

## よくあるミス

??? failure "草の位置が毎フレーム変わって、ちらつく"
    **セルのハッシュなど、決定的な乱数**を使う。**時間で乱数を変えない**。

??? failure "遠くの草が痩せて消える"
    **アルファのミップを補正**し、**遠くは密度を落として、1 本を太くする**。

??? failure "草が全部同じ向き・同じ高さで人工的"
    **回転・スケール・色を個体ごとにずらす**。

??? failure "風で根元まで動いて、地面から浮く"
    **揺れの強さを根元 0・先端 1 にする**（`height_t²`）。

??? failure "木の LOD が切り替わるとき、ポップする"
    **ディザリングのフェード**で**切り替える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大量の植生 ＝ <strong>インスタンシング</strong>。<strong>配置はセルのハッシュで決定的に</strong>
    - [x] <strong>カリング</strong>は<strong>距離＋視錐台</strong>（<strong>GPU で</strong>）。<strong>遠くは密度を落とす</strong>
    - [x] 草 ＝ <strong>クロス板 or 1 本ずつの葉</strong>。<strong>個体差</strong>を付ける
    - [x] 風 ＝ <strong>位相をずらした波、根元固定</strong>
    - [x] 木 ＝ <strong>LOD とインポスター</strong>。<strong>切り替えはディザ</strong>
    - [x] 葉の透明 ＝ <strong>アルファ テスト ＋ A2C</strong>

## 参考

- Wang, "Rendering Grass in Real-Time with Dynamic Lighting"（GPU Gems 系）
- Pelzer, "Rendering Countless Blades of Waving Grass"（GPU Gems 1）
- Sousa, "Vegetation Procedural Animation and Shading in Crysis"（GPU Gems 3）
- Jahrmann & Wimmer, "Interactive Grass Rendering Using Real-Time Tessellation"

## 関連ページ

- [地形](index.md)
- [地形のテクスチャ](texturing.md)
- [アルファ テスト](../translucency/alpha-test/index.md)
- [波紋と水面のインタラクション](../water/interaction.md)

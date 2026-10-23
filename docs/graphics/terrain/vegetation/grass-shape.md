---
title: Grass Shape
tags:
  - 描画
---

# Grass Shape

<strong>草は細長い板ポリを数枚、交差させて作るのが基本</strong>です。1 枚の草を少ない頂点でそれらしく見せる工夫が要ります。このページでは草の形を説明します。

!!! tip "ポイント"
    - 板ポリを十字に交差させる。
    - 1 本ずつ曲げた細いメッシュにする方法もある。
    - 頂点カラーで風の効き方（根元は動かない）を指定。
    - テクスチャで葉の形を切り抜く。

!!! info "このページを読む前に"
    - [Vegetation](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 草の形
<strong>草は細い葉が大量に生えている</strong>ので、ポリゴンを工夫します。

| 方式 | 内容 |
| --- | --- |
| クロス板（板ポリを十字） | 草の絵を貼った板を 2 枚、十字に交差。簡単・古典的 |
| 3 枚〜の房 | 3〜5 本の葉の板を扇状に。ポリゴンは 6〜10 枚 |
| 1 本ずつの葉 | 細長い三角形の帯（3〜7 セグメント）を1 本ずつ。曲げて風で揺らせる。距離で本数を減らす |
| ビルボード | 常にカメラを向く。遠景用（回転しても形が崩れない草原の塊） |

1 本ずつの葉は 頂点が先端ほど細く、少し曲がっているメッシュです。インスタンスごとに高さ・曲がり・色を変えると自然です。

```hlsl
float bend = instance.bend * pow(input.height_t, 2.0);
local.x += bend;
local.y *= lerp(1.0, 0.9, bend);
```

| 点 | 説明 |
| --- | --- |
| `height_t` | 葉の根元 0、先端 1 |
| 二乗で曲げる | 先端ほど大きく曲がる（根元は動かない） |
| 根元の色を暗く | 地面との馴染み・AO の代わり。先端を明るく |
| 地形の色に合わせる | 草の根元の色を地形のテクスチャの色から取ると、境目が消える |

## 草 1 本をどう作るか

草は <strong>数が多い</strong>（1 平方メートルに、数百本）ので 1 本あたりの、三角形の数がすべてを決めます。1 本を 3 枚の三角形で作ると、100 万本で 300 万三角形です。

| 方式 | 三角形 / 本 | 見た目 | 風の表現 |
| --- | --- | --- | --- |
| クロス板（十字に交差した 2 枚、絵を貼る） | 4 | 密集した草むらに見える。横から見ると板 | 先端を揺らせる |
| 房（3〜5 本の葉を扇形に） | 6〜10 | 近景でも、まずまず | 房全体が揺れる |
| 1 本ずつの葉（細い帯） | 3〜14 | 近景で、1 本ずつ見える | 1 本ごとに、曲がる |
| ビルボード | 2 | 遠景用 | 動かない |

## 葉 1 本のメッシュ

1 本の葉は <strong>根元から先端へ向かう、細い帯</strong>です。帯を数段に分けて 根元は太く、先端は細くします。

```text
先端   ▲        ← 頂点 1 つ（三角形）
      ╱ ╲
     ╱───╲      ← セグメント 3（幅 小）
    │     │
    │─────│     ← セグメント 2
    │     │
    │─────│     ← セグメント 1
    │     │
根元 └─────┘     ← セグメント 0（幅 大）
```

| セグメント数 | 頂点数 | 三角形 | 用途 |
| --- | --- | --- | --- |
| 1 | 3 | 1 | 遠景（三角形 1 枚の、葉） |
| 3 | 7 | 5 | 中景 |
| 5 | 11 | 9 | 近景 |
| 7 | 15 | 13 | 最近景（曲がりが、なめらか） |

距離に応じて セグメント数が、違うメッシュに切り替えます。遠景では三角形 1 枚でも画面上では、細い線にしか見えません。

### 頂点の位置の決め方

頂点は 根元から先端への高さ `t`（0〜1）と、左右（−1、+1）で決まります。

```hlsl
// 葉の頂点を、シェーダーの中で、組み立てる（頂点バッファを持たない方法）。
// vertex_id から、段（level）と、左右（side）を取り出す。
static const int kSegments = 5;

float3 BladeVertex(uint vertex_id, float width, float height, float bend) {
  uint level = vertex_id / 2;                 // 0 〜 kSegments
  float side = (vertex_id & 1) ? 1.0 : -1.0;
  float t = float(level) / kSegments;

  // 幅: 根元で太く、先端で細く
  float w = width * (1.0 - t * t);
  // 曲がり: 先端ほど、前へ倒れる（二次曲線）
  float forward = bend * t * t * height;
  float up = height * (t - 0.5 * bend * bend * t * t * t);   // 曲がった分だけ、少し低くなる

  return float3(side * w * 0.5, up, forward);
}
```

曲がりを 2 次以上の曲線（`t²`）にすると、根元はまっすぐ立ち先端だけが、しなる、草らしい形になります。

## 頂点シェーダーで組み立てる

草を <strong>頂点バッファのメッシュにしない</strong>方法も、あります。インスタンスごとのパラメーター（位置、向き高さ曲がり）から頂点シェーダーが直接、頂点を計算します。

| 項目 | 内容 |
| --- | --- |
| 頂点バッファ | 不要（`SV_VertexID` だけ使う）。インデックス バッファも規則的なので、定数で組める |
| インスタンス | 位置、向き高さ曲がり色のばらつき |
| 利点 | LOD ごとに、頂点数が違うメッシュを頂点バッファの切り替えなしで、`DrawInstanced(頂点数, インスタンス数)` で描ける |

```cpp
// 頂点バッファなしで描く。頂点数は、段数から決まる。
context->IASetInputLayout(nullptr);
context->IASetVertexBuffers(0, 0, nullptr, nullptr, nullptr);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLESTRIP);   // 帯は、ストリップで表現できる
const UINT vertices_per_blade = (kSegments + 1) * 2 + 1;                   // 先端は、1 つ追加
context->DrawInstanced(vertices_per_blade, instance_count, 0, 0);
```

三角形ストリップは 帯（左右の頂点を、交互に並べる）と相性が良いです。

## 向きとカメラ

葉は <strong>ただの帯</strong>なので 横から見ると、細い線になります（帯の幅の方向と視線が、垂直のとき厚みがゼロ）。見えなくなる問題の対策を示します。

| 問題 | 対策 |
| --- | --- |
| 帯を真横から見ると消える | カメラの向きに、少しだけ帯を回す（ビルボード的に、幅の向きを視線に垂直に近づける）。ただし、全部を向けると不自然 |
| 帯の裏面が描かれない | カリングを、無効にして両面を描く。裏面の法線は反転する |
| 近づくと帯が細すぎる | 幅に、最小値を持たせる。遠くでは幅を少し太くする（細すぎると、エイリアシングで消える） |

```hlsl
// 視線に応じて、帯の幅を、少しだけ、広げる（真横から見ても、消えないように）。
float3 view_dir = normalize(camera_position - world_pos);
float side_on = 1.0 - abs(dot(view_dir, blade_normal));   // 真横から見るほど 1
world_pos += blade_right * side * side_on * thicken_amount;
```

## 色

草の色の <strong>ばらつき</strong>と 根元の暗さが、見た目の半分を決めます。

| 要素 | 内容 |
| --- | --- |
| 根元の色 | 暗く地形のテクスチャの色に、合わせる。境目が消える（地形との馴染み） |
| 先端の色 | 明るい。高さ `t` で補間 |
| 本ごとのばらつき | 位置から、決定的な乱数で色相と明度を少しずらす |
| 地面の色を拾う | 草の根元の位置で、地形のカラー マップを読み草の色に、混ぜる |

```hlsl
float3 root_color = terrain_albedo.SampleLevel(g_linear_clamp, terrain_uv, 0).rgb * 0.5;  // 地面の色を、暗くして
float3 tip_color = lerp(root_color, float3(0.55, 0.75, 0.25), 0.8);                        // 先端は、明るい緑
float3 color = lerp(root_color, tip_color, t) * (0.9 + 0.2 * instance_random);             // 1 本ずつの、ばらつき
```

## 近年の実装例

Wohllaib（2021）は、『Ghost of Tsushima』の草を、<strong>1 本ずつの葉を計算シェーダーで、曲線として生成</strong>し描画する方法を、紹介しています。数百万本の草を GPU 上で、LOD ごとに頂点数を変えて、描いています。

| 項目 | 内容 |
| --- | --- |
| 葉の形 | ベジェ曲線（曲がった線）に沿って、帯を作る |
| LOD | 距離に応じて、頂点数を減らす。遠くは少ない頂点で細く |
| 風 | 葉の曲線の制御点を、風で動かす |
| 地形との馴染み | 草の色を、地形の色から取り根元で境目を消す |

詳細は GDC の発表を参照してください。ここでは、「1 本ずつの葉を曲線として扱い、LOD で頂点数を変える」という、考え方を押さえてください。

## よくあるミス

??? failure "草が、横から見ると板に見える"
    <strong>複数枚を交差</strong>させる・向きをカメラに合わせる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 板ポリの交差と、切り抜きテクスチャ

## 参考

- Pelzer, "Rendering Countless Blades of Waving Grass", GPU Gems, Chapter 7, 2004（草の板ポリ、風、クロス ブレンド）
- Wohllaib, "Procedural Grass in Ghost of Tsushima", Game Developers Conference 2021
- Boulanger, Pattanaik, Bouatouch, "Rendering Grass in Real Time with Dynamic Lighting", IEEE Computer Graphics and Applications, Vol. 29, No. 1, 2009
- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）

## 関連ページ

- [Vegetation](index.md)
- [Wind](wind.md)

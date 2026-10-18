---
title: Editing Heightmaps
tags:
  - 描画
---

# Editing Heightmaps

<strong>地形を作るには、高さマップを、ブラシで盛ったり削ったりして、編集します</strong>。このページでは、<strong>編集の方法と保存</strong>を説明します。

!!! tip "ポイント"
    - ブラシで高さを上げ下げ・平らにならす。
    - 編集した範囲だけ、メッシュ・法線を更新する。
    - 高さマップは、16bit で保存。
    - 元に戻せる（アンドゥ）ように、差分を記録する。

## 高さマップの編集
| 方法 | 内容 |
| --- | --- |
| ブラシで盛る・削る | 高さマップに丸いブラシを加算・減算 |
| 平らにする・均す | 平均を取って、段差をならす |
| <strong>ステップ（段丘）</strong> | 高さを丸めて、段々にする |
| 道・建物の整地 | 指定範囲を一定の高さに合わせる（スプライン沿いに整地） |
| ランタイムの変形 | 爆発で穴が開くなど。高さマップを書き換え、法線・当たり判定も更新 |

## ブラシの考え方

高さマップの編集は、<strong>ブラシの範囲の画素に、ブラシの形の、重みを掛けて、高さを、変える</strong>操作です。

| ブラシ | 高さの変え方 |
| --- | --- |
| 盛る（Raise） | `h += strength × falloff` |
| 削る（Lower） | `h -= strength × falloff` |
| 平らにする（Flatten） | `h = lerp(h, target, strength × falloff)`（`target` は、クリックした場所の高さ） |
| ならす（Smooth） | `h = lerp(h, 周りの平均, strength × falloff)` |
| 設定した高さにする（Set Height） | `h = lerp(h, 指定の高さ, falloff)` |
| ノイズ | `h += noise(p) × strength × falloff` |
| 段丘（Terrace） | 高さを、階段状に丸める |

`falloff` は、ブラシの中心から、縁へ向かって、1 から 0 へ、減る重みです。

```hlsl
// 中心 1、縁 0 の、なめらかな重み。
float Falloff(float dist, float radius, float hardness) {
  float t = saturate(dist / radius);
  // hardness が 1 に近いほど、縁が鋭い
  return 1.0 - smoothstep(hardness, 1.0, t);
}
```

## 計算シェーダーで、ブラシを適用する

CPU で、高さマップを書き換えて、毎フレーム、GPU に転送するのは、重いです。<strong>ブラシも、GPU の計算シェーダーで、適用</strong>します。

```hlsl
RWTexture2D<float> g_height : register(u0);          // R32_FLOAT（編集中は精度が必要）
```

高さマップは、`R32_FLOAT` の、UAV にします。編集を、重ねると、誤差が、たまるので、16 ビットでは、足りず、32 ビットの、浮動小数が、必要です。

```hlsl
cbuffer BrushCB : register(b0) {
  float2 brush_center;     // ブラシの中心（高さマップの画素座標）
  float brush_radius;      // 画素
  float brush_strength;    // 1 回に変える量（メートル）
  float hardness;
  int mode;                // 0=盛る 1=削る 2=ならす 3=平らにする
  float flatten_target;
  float dt;
};
```

ブラシの、設定です。中心、半径、強さ、硬さ、モード（盛る、削る、ならす、平らにする）を、定数バッファで、渡します。`dt` を、強さに、掛けるので、フレームレートが、違っても、同じ速さで、編集できます。

```hlsl
[numthreads(8, 8, 1)]
void main(uint3 id : SV_DispatchThreadID) {
  float2 p = float2(id.xy);
  float d = distance(p, brush_center);
  if (d > brush_radius) return;                       // ブラシの外は、何もしない
```

ブラシの、範囲の画素だけが、処理します。外側は、何もしないので、画面全体を、ディスパッチしても、範囲外は、すぐ終わります。

```hlsl
  float w = Falloff(d, brush_radius, hardness) * brush_strength * dt;
  float h = g_height[id.xy];
```

ブラシの、中心からの、距離に、応じた、重み `w` を、求めます。`Falloff` は、中心で 1、縁で 0 に、なる、関数で、`hardness` が、縁の、柔らかさを、決めます。

```hlsl
  if (mode == 0) h += w;
  else if (mode == 1) h -= w;
  else if (mode == 3) h = lerp(h, flatten_target, saturate(w));
  else {
    // ならす: 周りの 8 画素の平均へ寄せる
    float sum = 0.0;
    for (int j = -1; j <= 1; ++j)
      for (int i = -1; i <= 1; ++i) sum += g_height[id.xy + int2(i, j)];
    h = lerp(h, sum / 9.0, saturate(w));
  }
```

モードごとに、高さを、更新します。盛る、削るは、`w` を、足し引きするだけです。平らにするは、目標の高さに、寄せ、ならすは、周りの 9 画素の、平均に、寄せます。

```hlsl
  g_height[id.xy] = h;
}
```

```cpp
// ブラシの範囲を覆う、最小のスレッド グループだけを、ディスパッチする。
const int r = int(brush_radius) + 1;
const int x0 = std::max(0, int(center.x) - r), y0 = std::max(0, int(center.y) - r);
// シェーダー側は、id にオフセットを足して使う（ここでは、省略）
context->Dispatch((2 * r + 7) / 8, (2 * r + 7) / 8, 1);
```

!!! warning "「ならす」は、読み書きが同じテクスチャだと、結果が、順序に依存する"
    「ならす」ブラシは、<strong>周りの画素を読んで、自分に書く</strong>ので、同じテクスチャへ書くと、<strong>すでに書き換えた画素を、読むことがあります</strong>（順序が決まっていない）。ならしを、正確にやるときは、ピンポン（別のテクスチャに、書き出して、コピーして戻す）にします。

## 編集した範囲だけを、更新する

高さを書き換えたら、<strong>それに依存する、すべてのデータ</strong>を、更新する必要があります。ただし、<strong>編集した範囲だけ</strong>でかまいません。

| 依存するデータ | 更新方法 |
| --- | --- |
| ミップ | 編集した範囲の、ミップだけ、作り直す（[Heightmap LOD (Mips)](../lod/height-mip.md)） |
| 法線マップ | 編集範囲 + 1 画素の外側を、再計算する（法線は、隣の高さに依存するため） |
| チャンクの AABB | 編集範囲に、触れたチャンクの、最小・最大を、再計算する |
| 四分木のノード（CDLOD） | 影響する、ノードの最小・最大を、根まで、更新する |
| 物理の高さ場 | 当たり判定の、高さデータを、更新する |
| 配置（植生） | 高さが変わった範囲の、草・木を、置き直す |

```cpp
// 編集した範囲（ダーティ矩形）を、記録して、まとめて更新する。
struct DirtyRect { int x0, y0, x1, y1; };

void MarkDirty(DirtyRect& d, int x0, int y0, int x1, int y1) {
  d.x0 = std::min(d.x0, x0); d.y0 = std::min(d.y0, y0);
  d.x1 = std::max(d.x1, x1); d.y1 = std::max(d.y1, y1);
}

// フレームの終わりに、1 回だけ、まとめて更新する。
if (dirty.x1 >= dirty.x0) {
  const DirtyRect r = {dirty.x0 - 1, dirty.y0 - 1, dirty.x1 + 1, dirty.y1 + 1};  // 法線のため、1 画素広げる
  RecomputeNormals(r);
  RebuildMips(r);
  UpdateChunkBounds(r);
  UpdatePhysicsHeights(r);
  dirty = EmptyRect();
}
```

編集中は、<strong>ブラシを動かすたびに、全部更新する必要はなく</strong>、フレームの最後に、1 回まとめれば、十分です。

## 精度

| 項目 | 内容 |
| --- | --- |
| 編集中の形式 | `R32_FLOAT`。ブラシの 1 回の変化量は、非常に小さい（0.01 m 以下）。16 ビットだと、変化が、丸められて、消える |
| 保存の形式 | `R16_UNORM`。編集が終わったら、変換する |
| 誤差の蓄積 | 何度も、ならすと、高さが、少しずつ、変化する。保存前に、不要な、ならしを、しない |

## 元に戻す（アンドゥ）

地形の編集は、<strong>数十回〜数百回のブラシ</strong>を、繰り返します。アンドゥは、必須です。ただし、<strong>高さマップ全体を、毎回コピーすると、メモリが足りません</strong>。

| 方法 | 内容 |
| --- | --- |
| タイルの差分 | 編集で、変わったタイル（64×64 画素など）だけを、変更前の値で保存する。アンドゥは、保存したタイルを、書き戻す |
| ストローク単位 | マウスを押してから離すまでを、1 回の操作として、まとめる（細かい、1 フレームごとの変更では、ない） |
| 圧縮 | 差分は、変わっていない部分が多い。圧縮して保存する |

```cpp
struct UndoEntry {
  struct Tile { int tx, ty; std::vector<float> before; };
  std::vector<Tile> tiles;                  // 変更された、タイルの、変更前の値
};

// ブラシで、タイルに、初めて触れる前に、そのタイルの内容を、保存する。
void SaveTileBeforeEdit(UndoEntry& e, const HeightMap& h, int tx, int ty) {
  for (const auto& t : e.tiles) if (t.tx == tx && t.ty == ty) return;   // すでに、保存済み
  e.tiles.push_back({tx, ty, h.CopyTile(tx, ty)});
}
```

## ゲーム中の変形（ランタイム）

爆発の穴、掘削、建物の整地など、<strong>ゲーム中に、地形を、変形させる</strong>場合も、同じ仕組みです。ただし、次の点が、違います。

| 項目 | 内容 |
| --- | --- |
| 速さ | 1 フレームの中で、終わらせる（ブラシの適用は、軽い） |
| 同期 | 物理（当たり判定）と、見た目が、同じ高さデータを、見ていること |
| ネットワーク | 変形の、コマンド（位置・半径・強さ）を、送る。高さマップは、送らない（決定的に、同じ結果にする） |
| 保存 | セーブ データには、元の地形からの、差分（編集コマンドの列、または、変更タイル）を、保存する |

## よくあるミス

??? failure "編集のたびに、全体を再生成して遅い"
    <strong>編集した範囲だけ更新</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲だけ更新して、軽く編集

## 参考

- Št'ava, Beneš, Brisbin, Křivánek, "Interactive Terrain Modeling Using Hydraulic Erosion", Symposium on Computer Animation 2008
- Galin, Guérin, Peytavie, Cordonnier, Cani, Beneš, Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）
- Jolt Physics, "HeightFieldShape" ドキュメント（物理エンジンでの、高さ場の扱い）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [Terrain Generation](../generation/index.md)

---
title: Trees
tags:
  - 描画
---

# Trees

<strong>木は、近くは詳細なメッシュ、遠くは簡易なメッシュやビルボード</strong>にして、<strong>LOD で負荷を下げます</strong>。このページでは、木の描画を説明します。

!!! tip "ポイント"
    - 近く：幹と枝のメッシュ ＋ 葉のカード。
    - 中距離：簡易メッシュ。
    - 遠く：ビルボード（板に木の絵）。
    - LOD の切り替えは、ディザでなめらかに。

## 木
<strong>木はポリゴンが多く（数万）、枚数も多い</strong>ので、<strong>LOD が重要</strong>です。

| LOD | 内容 |
| --- | --- |
| <strong>LOD 0（近景）</strong> | <strong>幹・枝の 3D モデル ＋ 葉のカード（板に葉の絵）</strong> |
| LOD 1〜2 | 枝を減らす・葉のカードを統合 |
| <strong>インポスター（遠景）</strong> | 木を数方向から撮った絵（板ポリ）に置き換え。カメラの向きに応じて、絵を切り替える／混ぜる |
| <strong>ビルボード（最遠）</strong> | 1 枚の板 |

<strong>インポスター</strong>は、<strong>事前に木を複数の視点（例：8×8 = 64 方向）から撮影</strong>し、アトラスに並べます。描画時はカメラに最も近い方向の絵を選び、板に貼ります。法線・深度もアトラスに持つと、ライティングも正しくなります。

| 点 | 説明 |
| --- | --- |
| LOD の切り替え | <strong>ディザリング（市松のフェード）</strong>で、ポップを隠す（[Alpha Testing](../../translucency/alpha-test/index.md)） |
| 葉のカード | 1 枚に複数の葉を描いた板。アルファ テスト |
| 幹と葉でマテリアルを分ける | 幹は不透明、葉はアルファ テスト |
| 影 | 影の LOD は、描画より粗くする（[Shadows](../../shadows/index.md)） |

## 木は、どう作られるか

木の 3D モデルは、<strong>手で作る</strong>場合と、<strong>ルールから、自動生成する</strong>場合があります。

| 方法 | 内容 |
| --- | --- |
| 手作り（DCC ツール） | アーティストが、幹、枝、葉を、モデリングする。品質は、高いが、手間がかかる |
| 木の専用ツール | 樹種ごとの、パラメーターから、木を生成する。パラメーターを変えて、同じ種類の、別の木を、たくさん作れる |
| 手続き的な生成（L システムなど） | ルール（枝分かれの規則）を、繰り返し適用して、枝を生やす |

自動生成の、基礎は、<strong>L システム</strong>（Prusinkiewicz と Lindenmayer、1990）と、<strong>Weber と Penn の、パラメトリックな木</strong>（1995）です。

### Weber と Penn の、考え方

1 本の木を、<strong>少数のパラメーターで</strong>記述します。

| パラメーター | 内容 |
| --- | --- |
| 枝の分かれる、数 | 幹から、何本の枝が出るか |
| 枝の長さ・太さの、減り方 | 先へ行くほど、短く、細く |
| 枝の、曲がり・ねじれ | 枝が、どのくらい、まっすぐでないか |
| 枝の、角度 | 幹から、どの角度で分かれるか |
| ランダムさ | 個体ごとの、ばらつき |

パラメーターを変えると、<strong>松、オーク、柳</strong>など、違う樹種が、生成できます。1 本の定義から、<strong>ランダムなバリエーション</strong>を、いくつも作れるので、同じ木が並ぶ問題が、軽減されます。

## 木を構成する、部品

| 部品 | 形 | 素材 |
| --- | --- | --- |
| 幹・太い枝 | メッシュ（円柱を、曲げたもの） | 不透明（木の皮のテクスチャ） |
| 細い枝 | メッシュ、または、板 | アルファ テスト |
| 葉 | カード（板に、葉の房の絵） | アルファ テスト、透過（[Foliage Translucency](translucency.md)） |

葉を、1 枚ずつ、3D モデルにすると、<strong>数十万ポリゴン</strong>になります。<strong>葉の房を、1 枚の板に描いて、並べる</strong>（カード）ことで、数千ポリゴンに、収めます。

## LOD

木は、1 本が、<strong>数万ポリゴン</strong>で、森では、数万本です。LOD が、<strong>必須</strong>です。

| LOD | 距離 | 内容 | 三角形（目安） |
| --- | --- | --- | --- |
| 0 | 〜30 m | 幹・枝の、完全なメッシュ ＋ 葉のカード | 20,000〜50,000 |
| 1 | 30〜80 m | 細い枝を減らす。葉のカードを、統合 | 5,000〜10,000 |
| 2 | 80〜200 m | 幹と、主な枝だけ。葉は、大きなカードに | 1,000〜3,000 |
| インポスター | 200 m〜 | 数方向から撮った絵を、板に貼る | 2（板 1 枚） |
| ビルボード | 最遠 | 1 枚の絵（常に、カメラを向く） | 2 |

### LOD の切り替えを、隠す

LOD が、切り替わる瞬間に、<strong>ポップ</strong>が起きます。隠すには、<strong>ディザ フェード</strong>を使います。

```hlsl
// ディザ フェード: 2 つの LOD を、市松状のパターンで、混ぜて切り替える。
// fade が 0 → 1 に動くと、LOD A が、少しずつ、消えて、LOD B が現れる。
void ApplyDitherFade(float4 screen_pos, float fade) {
  // 4×4 のベイヤー行列（0〜15）から、しきい値を作る
  static const float bayer[16] = {
     0, 8, 2,10,  12, 4,14, 6,  3,11, 1, 9,  15, 7,13, 5};
  uint2 p = uint2(screen_pos.xy) & 3;
  float threshold = (bayer[p.y * 4 + p.x] + 0.5) / 16.0;
  clip(fade - threshold);        // fade が threshold 未満の画素は、捨てる（LOD A の側）
}
// LOD B には、逆（1 - fade）を渡す。
```

2 つの LOD を、<strong>同時に、描く</strong>期間が、必要です。コストは、増えますが、切り替えの、見た目が、大きく、改善します（[Dithered Transparency](../../translucency/alpha-test/dither.md)）。

## インポスター

<strong>インポスター（imposter）</strong>は、<strong>3D の木を、事前に、複数の方向から撮影した絵</strong>を、板に貼って、木の代わりに、描く手法です。

### 作り方

| 手順 | 内容 |
| --- | --- |
| ① 撮影 | 木を、周りの、決まった方向（例：8×8 = 64 方向）から、撮影する。色、法線、深度を、それぞれ、記録する |
| ② アトラス | 撮影した絵を、1 枚の大きなテクスチャ（アトラス）に、並べる |
| ③ 実行時 | カメラの向きに、最も近い撮影方向の、絵を、板に貼って描く |

### 方向の、決め方（8 面体マッピング）

撮影する方向を、<strong>球面上に</strong>、均等に並べたいとき、<strong>8 面体（正八面体）マッピング</strong>が、使われます。球面を、正方形に展開する方法で、格子状に、均等な方向を、取れます（Brucks、2018）。

```text
方向 (x, y, z) → 正方形上の座標 (u, v)      ← 8 面体マッピング（球面 ↔ 正方形）
 u, v を、N×N の格子に、離散化          → 撮影する方向の、番号
```

### 実行時：3 枚の絵を、混ぜる

カメラが、<strong>撮影方向の、間</strong>を向いているとき、1 枚の絵だけだと、<strong>ポップ</strong>が起きます（絵が、切り替わる瞬間）。そこで、近い、3 つの方向の絵を、重みつきで、混ぜます。

```hlsl
// インポスターの、ピクセル シェーダー（概略）。
float4 ImposterPS(float2 uv : TEXCOORD0, float3 view_dir_local : TEXCOORD1) : SV_Target {
  // ① カメラの向きを、8 面体マッピングの、座標に変える
  float2 grid = OctEncode(normalize(view_dir_local)) * (kGridSize - 1);
  float2 cell = floor(grid);
  float2 f = frac(grid);

  // ② 近い 3 つの方向（格子の三角形）を選ぶ。重みは、重心座標
  float2 c0 = cell, c1 = cell + float2(1, 0), c2 = cell + float2(0, 1), c3 = cell + float2(1, 1);
  bool upper = (f.x + f.y) > 1.0;
  float3 w = upper ? float3(1.0 - f.y, 1.0 - f.x, f.x + f.y - 1.0)
                   : float3(1.0 - f.x - f.y, f.x, f.y);
  float2 a = upper ? c3 : c0, b = upper ? c2 : c1, c = upper ? c1 : c2;

  // ③ 3 枚の、アトラスの絵を、読んで、混ぜる
  float4 col = SampleAtlas(a, uv) * w.x + SampleAtlas(b, uv) * w.y + SampleAtlas(c, uv) * w.z;
  clip(col.a - 0.5);
  return col;
}
```

| 項目 | 内容 |
| --- | --- |
| 方向の数 | 8×8（64 枚）が、一般的。多いほど、滑らかだが、アトラスが、大きい（例：2048×2048 に 64 枚 ＝ 1 枚 256×256） |
| 深度・法線 | 色だけでなく、法線と深度も、撮影しておくと、ライティングと、地面との、接点（深度のオフセット）が、正しくなる |
| 距離の、切り替え | LOD 2 から、インポスターへ、ディザ フェードで、切り替える |
| 向き | 地面に垂直な軸で、回転する（木は、地面に、立っているため）。真上から見る場合を、除いて、縦の軸だけで、回す、簡易版も、ある |

簡易版は、<strong>横方向の、数方向（8 方向）だけ</strong>を、撮影します。真上や真下から見ない、地上のゲームでは、十分です。

## ビルボード（最遠）

最も遠い木は、<strong>カメラを、常に向いた、板 1 枚</strong>に、します。<strong>1 方向の絵</strong>だけで、回転で、形が崩れないよう、ほぼ、シルエットだけが、分かる程度です。

| 距離 | 見え方 |
| --- | --- |
| 500 m〜 | 数画素の、緑のかたまり。詳細は、不要 |
| 1 km〜 | 木を 1 本ずつ、描かず、森の、色の塊として、地形のテクスチャに、含める |

## 影

| LOD | 影への、扱い |
| --- | --- |
| 近い木 | 完全なメッシュで、影を落とす。葉は、アルファ テストで切り抜く |
| 中くらい | 影用の、簡略な LOD（描画より、粗い）を使う |
| 遠い木 | 影を落とさない。または、インポスターで、影も、近似する |

影の描画は、<strong>カメラの描画と、別の距離で、LOD を、決めて</strong>かまいません（影は、粗くても、気づかれにくい）。

## よくあるミス

??? failure "LOD が切り替わる時、木がポップする"
    <strong>ディザ フェード</strong>で<strong>切り替える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 近くは詳細、遠くはビルボード

## 参考

- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）
- Weber, Penn, "Creation and Rendering of Realistic Trees", SIGGRAPH 1995
- Prusinkiewicz, Lindenmayer, "The Algorithmic Beauty of Plants", Springer, 1990（L システム）
- Décoret, Durand, Sillion, Dorsey, "Billboard Clouds for Extreme Model Simplification", ACM Transactions on Graphics (SIGGRAPH 2003)
- Brucks, "Octahedral Impostors", 2018（8 面体のマッピングを使った、インポスターの作り方）

## 関連ページ

- [Vegetation](index.md)
- [Dithered Transparency](../../translucency/alpha-test/dither.md)

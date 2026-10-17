---
title: SSGI
tags:
  - 描画
---

# SSGI

**SSGI**（Screen-Space Global Illumination、画面空間 GI）は、<strong>[SSAO](../ao/ssao-hemisphere.md) と同じ発想</strong>を、<strong>「暗さ」だけでなく「光（色）」にまで広げた</strong>ものです。**画素の周りの半球にレイを飛ばし**（深度バッファ上で）、<strong>当たった画素の「色（その画素の出射光）」</strong>を、**間接光として集めます**。**事前計算が不要**で**動く物・動くライト**も**自動的に反映**されます。ただし、**画面に映っているものしか見えない**という**画面空間の限界**があります。

!!! tip "ポイント"
    - <strong>画素から半球方向にレイ</strong>を飛ばし（<strong>深度バッファ上</strong>）、<strong>当たった点の色</strong>を<strong>間接光</strong>として<strong>平均</strong>。
    - <strong>SSAO は「遮られた量」</strong>、<strong>SSGI は「当たった先の色」</strong>。
    - <strong>前フレームの最終画像（ライティング済み）</strong>を<strong>光源として使う</strong>と<strong>多バウンス</strong>が<strong>ほぼ無料</strong>で得られる。
    - <strong>少ないレイ ＋ ノイズ ＋ デノイズ（時間・空間）</strong>が<strong>必須</strong>。
    - 限界：<strong>画面外・裏側・隠れた面</strong>は<strong>見えない</strong>。<strong>画面端でゲインが変わる</strong>。
    - <strong>他の GI（プローブ等）の補助</strong>として、<strong>近距離の細かい間接光</strong>を足す使い方が多い。

## 原理

**SSAO**は<strong>半球に飛ばしたレイが「遮られたか」</strong>だけを見ました。**SSGI**は<strong>レイが当たった画素の「光（色）」</strong>を**読みます**。

| 項目 | SSAO | SSGI |
| --- | --- | --- |
| **レイの結果** | <strong>遮られた（0/1）</strong> | <strong>当たった点の色（RGB）</strong> |
| **出力** | <strong>暗さ（スカラー）</strong> | <strong>間接光（RGB）</strong> |
| **色の効果** | なし | **カラー ブリーディング** |

### 手順

| 手順 | 内容 |
| --- | --- |
| **① サンプル方向の生成** | **画素の法線**を中心とする**半球**で、**余弦重み付き**のランダムな方向 |
| **② 画面空間のレイマーチ** | **深度バッファ**上で**レイを進める**（[SSR](../reflections/ssr-basics/index.md) や [Hi-Z](../reflections/ssr-hiz.md) と同じ） |
| **③ ヒット判定** | **レイの深度が深度バッファの奥に入った**ら、**ヒット** |
| **④ 色を読む** | **ヒット画素の出射光**（**前フレームの最終色**）を**読む** |
| **⑤ 平均** | **全レイの色を平均**して、**間接光** |

```hlsl
float3 SSGI(float3 view_pos, float3 view_normal, float2 pixel) {
  float3 sum = 0.0;
  [loop] for (int i = 0; i < kRayCount; ++i) {
    float3 dir = CosineSampleHemisphere(view_normal, Hash(pixel, i));
    float2 hit_uv;
    float hit_depth;
    if (ScreenSpaceTrace(view_pos, dir, hit_uv, hit_depth)) {
      float3 radiance = prev_frame_color.SampleLevel(linear_sampler, hit_uv, 0).rgb;
      sum += radiance;
    }
  }
  return sum / kRayCount;
}
```

| 点 | 説明 |
| --- | --- |
| **`prev_frame_color`** | **前フレームの最終的な画像**（ライティング済み・ポストプロセス前）。**間接光も含んでいる**ので、**多バウンス**になる |
| **余弦重み付きサンプル** | **`(n·ω)/pdf` が定数**になり、**単純な平均** |
| **`ScreenSpaceTrace`** | **画面空間のレイマーチ**（[SSR](../reflections/ssr-basics/index.md)・[Hi-Z トレース](../reflections/ssr-hiz.md)） |

## 多バウンスの得かた

**前フレームの最終画像に、前フレームの SSGI の結果が含まれている**ので、**フレームを重ねるごとに**、**バウンスが増える**ように見えます。

| 項目 | 内容 |
| --- | --- |
| **1 バウンス** | **現在のフレームの直接光だけ**を読む場合 |
| <strong>多バウンス（無料）</strong> | **前フレームの最終画像**（間接光を含む）を読む。**フレームごとに、1 バウンスずつ蓄積** |
| **注意** | **ゲインが 1 を超える**と、<strong>発散（明るくなり続ける）</strong>。**減衰**させる |

## ノイズとデノイズ

**画素あたり 1〜数本**のレイでは、**ノイズ**が**非常に目立ちます**。

| 手法 | 内容 |
| --- | --- |
| **時間蓄積** | **前フレームの結果**を**再投影**して**混ぜる**（**動きのベクトル**が必要） |
| **空間フィルタ** | **バイラテラル・À-trous**で**法線・深度**を**手がかり**に**エッジを保ってぼかす** |
| **半分の解像度** | **半解像度で計算**し、**バイラテラル アップサンプル** |
| **ブルー ノイズ** | **ノイズの質を良く**する（**ブルー ノイズ・IGN**） |
| **TAA との併用** | **TAA が時間方向の平均**を取る |

**ノイズが大きい**ので**時間蓄積と空間フィルタ**の**組み合わせ**が、**ほぼ必須**です。

## 画面空間の限界

| 限界 | 内容 |
| --- | --- |
| **画面外の光源・面** | **見えない**ので**間接光に寄与しない**。**カメラの向きで明るさが変わる** |
| **隠れた面の裏側** | **深度バッファは、一番手前の面だけ**。**裏側・遮蔽物の向こう**は**不明** |
| **画面端** | **サンプルが画面外へ出る**ので**端で暗くなる**（**フェード**が必要） |
| **厚み** | **薄い物の背後**を**通過**できない／**遠くの面の手前を、誤ってヒット** |
| **視点依存** | **カメラを動かすと間接光が変わって見える**（**破綻**） |

**そのため、SSGI 単体で安定した GI にはなりません**。**プローブやライトマップなどの、ベースの GI**に**近距離の細かい間接光・カラー ブリーディングを足す**使い方が、一般的です。

## コストと工夫

| 項目 | 内容 |
| --- | --- |
| **レイ数** | **画素あたり 1〜4 本**。**多いほど、きれい・重い** |
| **レイの距離** | **短い**ほど安い（**近距離のみ**） |
| **半解像度** | **計算量を 1/4** |
| **Hi-Z トレース** | **遠くまで少ないステップ**で |
| **法線・深度の事前フィルタ** | **ノイズ低減**に有利 |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **事前計算が不要**（動く物・動くライトを反映） | **画面にあるものしか見えない** |
| **実装が比較的簡単**（SSAO・SSR の拡張） | **ノイズ・デノイズが必須** |
| **カラー ブリーディングが出る** | **視点依存**（カメラで変わる） |
| **多バウンスがほぼ無料** | **画面外の光源が効かない** |
| **他の GI の補助**として良い | **単独では安定しない** |

## よくあるミス

??? failure "画面端で、間接光が急に暗くなる"
    **画面端付近をフェード**させる・**ベースの GI にフォールバック**します。

??? failure "前フレームの色を、再投影せずに読んで動くとずれる"
    **動きのベクトル**で**再投影**します。

??? failure "前フレーム色を、減衰なしで読み続けて、発散して明るくなる"
    **減衰**（1 未満）を掛けます。

??? failure "ノイズが残って、チラつく"
    **時間蓄積 ＋ 空間フィルタ**を強め、**ブルー ノイズ**を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSGI ＝ <strong>SSAO の拡張</strong>。<strong>半球レイが当たった画素の「色」</strong>を、<strong>間接光</strong>として集める
    - [x] <strong>前フレームの最終画像</strong>を光源にすると、<strong>多バウンスがほぼ無料</strong>
    - [x] <strong>少ないレイ ＋ 時間・空間デノイズ</strong>が<strong>必須</strong>
    - [x] <strong>画面外・裏側は見えない</strong>。<strong>視点依存</strong>。<strong>単独は不安定</strong>
    - [x] <strong>ベースの GI ＋ SSGI（近距離の補助）</strong>が、実用的

## 参考

- Ritschel, Grosch, Seidel, "Approximating Dynamic Global Illumination in Image Space"（I3D 2009）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015、レイ再利用の手法）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（GTAO）

## 関連ページ

- [間接光（GI）](index.md)
- [GI の理論](theory.md)
- [SSAO](../ao/ssao-hemisphere.md)
- [SSR の基礎](../reflections/ssr-basics/index.md)
- [Hi-Z トレース](../reflections/ssr-hiz.md)
- [AO のフィルタ](../ao/filtering/index.md)

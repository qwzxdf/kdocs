---
title: Water Reflection
tags:
  - 描画
---

# Water Reflection

<strong>水面には空や周囲の景色が映ります</strong>。空は環境マップで安く、周囲の物は SSR や平面反射で映します。このページでは水の反射の手法と、使い分けを説明します。

!!! tip "ポイント"
    - 空は環境マップ（キューブマップ）。
    - 周囲の物は SSR・平面反射。
    - 法線で反射方向をずらして、波の歪みを出す。
    - フォールバックの順：SSR → 平面反射 → 環境マップ。

!!! info "このページを読む前に"
    - [Water Shading](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 反射
<strong>反射はフレネルの F で重みを付けて合成</strong>します。反射の取り方は状況で選びます。

| 方式 | 内容 |
| --- | --- |
| 環境マップ（キューブ） | 安い。空や遠景だけ。近くの物は映らない |
| 平面反射 | 水面は平らなので鏡像用にもう一度描く。正確だが重い（[Reflections](../../reflections/index.md)） |
| SSR | 画面内の物を映す。画面外は環境マップに落とす |
| レイトレ反射 | 最も正確。重い |

波で法線が傾くので反射ベクトルを法線から作り、平面反射なら法線の XZ で UV をずらして歪ませます。

```hlsl
float3 reflect_dir = reflect(-view_dir, normal);
float3 reflection = environment.SampleLevel(linear_clamp, reflect_dir, 0).rgb;
```

### 組み合わせ方

実際のゲームではこれらを重ねます。基本は環境マップで空と遠景を安定して映します。その上に SSR を足して近くの岸辺や船、橋の映り込みを出します。SSR が当たらなかった画素（画面外や画面端）は、環境マップにフェードで戻します（[SSR Fallback and Compositing](../../reflections/ssr-fallback.md)）。湖や池のように水面が完全に平らな場合は、平面反射が品質で勝ります。波のある海は法線が場所ごとに違い、反射方向がバラバラになるので、平面反射の鏡像を波の法線の XZ 成分で歪ませて使います。

反射の強さはフレネルで決まります（[Water Fresnel](fresnel.md)）。真上から見るとほとんど反射せず、斜めから見るほど鏡に近づくので、反射の質が目立つのは遠くの水面です。遠くの水面は法線が細かく揺れてちらつきやすいため、距離に応じて法線を平らにする（粗さを上げる）処理を入れます。

## 反射の取り方

水面には <strong>空、雲、遠くの山、近くの建物</strong>が映ります。映す方法を状況に合わせて選び、重ねます。

| 方法 | 映るもの | コスト | 弱点 |
| --- | --- | --- | --- |
| 環境マップ（キューブマップ） | 空、遠景 | 小 | 近くの物（船、岸の建物）が映らない |
| 平面反射 | 水面の上にある、すべて | 大（シーンをもう一度描く） | 波で乱れた反射が、作れない（ごまかす） |
| SSR | 画面に映っているもの | 中 | 画面の外が、映らない。水平に近い視線で画面の端から、反射が消える |
| レイトレーシング | すべて | 大 | 対応する GPU が必要 |

## 重ね方：フォールバック

実際のゲームでは <strong>1 つだけでは足りない</strong>ので、重ねます。

```text
   平面反射 or SSR   （近くの物。画面内の物）
        ↓ 失敗した（映っていない）ピクセルは
   環境マップ         （空、遠景。必ず映る）
```

| 順 | 方法 | 決め方 |
| --- | --- | --- |
| 1 | SSR（または平面反射） | 反射レイが、画面の中の物に当たったら使う。当たらなければ次へ |
| 2 | 環境マップ（空） | SSR が、当たらなかったとき |

```hlsl
float3 reflect_dir = reflect(-view_dir, normal);

// ① SSR（当たった場合のみ、色と、信頼度（0〜1）を返す）
float4 ssr = TraceScreenSpaceReflection(world_pos, reflect_dir);   // rgb = 色、a = 信頼度

// ② 環境マップ（空）
float3 sky = g_sky_cube.SampleLevel(g_linear_clamp, reflect_dir, roughness_mip).rgb;

// ③ 重ねる
float3 reflection = lerp(sky, ssr.rgb, ssr.a);
```

SSR の詳細は[Reflections](../../reflections/index.md) の、SSR のページを参照してください。

## 反射方向の作り方

反射の方向は <strong>波の法線</strong>から、計算します（`reflect(−V, N)`）。波で法線が傾くので 反射が揺れて、歪みます。

```hlsl
float3 reflect_dir = reflect(-view_dir, wave_normal);
```

### 地平線の下を向く反射

波の法線が 視線の方向に傾きすぎると、反射の向きが 水面の下を向くことがあります。空が映る環境マップの下半分（地面）を読むことになり黒や、不自然な色が出ます。

```hlsl
// 反射の向きが、地平線の下に向いたときは、水平に近い向きへ、押し戻す。
reflect_dir.y = max(reflect_dir.y, 0.02);
reflect_dir = normalize(reflect_dir);
```

遠くの水面ほど起きやすいです（視線が、水平に近く法線の少しの傾きで反射が、下を向く）。遠くでは波の法線を弱めて、反射の向きを安定させます（[Computing Normals](../waves/normals.md)）。

## 平面反射

水面は <strong>ほぼ平ら</strong>です。水面を鏡としてカメラを水面の反対側に置いた、仮想のカメラでシーンをもう一度描くと、正確な反射が得られます。

```text
 実際のカメラ ●
                 ╲
 ━━━━━━━━━━━━━━━━ 水面（y = h）
                 ╱
 鏡像のカメラ  ●   ← 水面について、反対側
```

```cpp
// 水面 (y = h) に対する、鏡像のカメラ。
float3 MirroredPosition(float3 p, float water_height) {
  return {p.x, 2.0f * water_height - p.y, p.z};
}
// 鏡像カメラの視線方向の y 成分も、反転する。
// 水面より下にある物を、描かないよう、斜めクリップ面（水面）を、設定する。
```

| 項目 | 内容 |
| --- | --- |
| 描く範囲 | 水面より上にある物だけ。水面で斜めにクリップする（水面より下を、映さない） |
| 解像度 | 画面の半分程度に、下げる（反射はぼやけてよい） |
| 描くもの | 遠景（空、山）と重要な近景だけに絞る。全シーンを描くと描画が 2 倍に近くなる |
| 波での歪み | 反射のテクスチャを読むときに、波の法線の `xz` で UV をずらす |

```hlsl
// 平面反射のテクスチャを、波の法線で歪ませて読む。
float2 reflect_uv = screen_uv + wave_normal.xz * distortion_strength;
reflect_uv.x = 1.0 - reflect_uv.x;                         // 鏡像なので、左右を反転する（実装による）
float3 reflection = g_planar_reflection.Sample(g_linear_clamp, reflect_uv).rgb;
```

平面反射は 水面が平ら（波が小さい）ときに、最も正確です。波が大きい海では歪みが大きく、ごまかしになります。小さな池、プール、湖に向きます。

## 空の反射

空は <strong>環境マップ</strong>（キューブマップ）で、映すのが基本です。昼と夜、天候の変化に合わせて 環境マップを、更新します。

| 方法 | 内容 |
| --- | --- |
| 事前のキューブマップ | 昼・夜・夕方の、キューブマップを用意して時間帯で、混ぜる |
| 大気からリアルタイムに生成 | [Atmosphere Model](../../atmosphere/scattering/atmosphere-model.md) の結果を、キューブマップに描いて使う |
| 大気の LUT を直接引く | 反射ベクトルから、空の色を LUT から読む。キューブマップが要らない |

粗さがあるとき（細かい波のばらつき）は、キューブマップのミップ（ぼかした版）を、読みます。`SampleLevel` で粗さに応じたミップを選びます（[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)）。

## 合成

反射の強さは <strong>フレネル</strong>で決まります（[Water Fresnel](fresnel.md)）。

```hlsl
float F = FresnelSchlick(saturate(dot(wave_normal, view_dir)), 0.02);
float3 color = lerp(refraction, reflection, F);
```

真上から見ると `F ≈ 0.02` で 反射は、ほぼ見えません。遠くを見るほど `F` が大きく 反射が、支配的になります。

## よくあるミス

??? failure "水面の反射が、画面の端で途切れる"
    <strong>環境マップへフォールバック</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空は環境マップ、周囲は SSR か平面反射

## 参考

- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games（水の描画、平面反射と屈折のコピー）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（反射と、フレネルの扱い）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（フレネル、屈折、スネルの法則）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes

## 関連ページ

- [Water Shading](index.md)
- [Reflections](../../reflections/index.md)
- [Planar Reflections](../../reflections/planar.md)

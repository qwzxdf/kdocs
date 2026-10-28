---
title: Wakes and Collisions
tags:
  - 描画
---

# Wakes and Collisions

<strong>船の後ろや物が水に当たった所には、泡の筋（航跡）ができます</strong>。物の位置を泡のバッファに書き込むことで、表現できます。このページでは航跡と衝突の泡を説明します。

!!! tip "ポイント"
    - 物が通った位置に泡を書き込む。
    - 書き込みはバッファを描く（スプラット）。
    - 履歴でゆっくり消える。
    - 速さに応じて強さを変える。

!!! info "このページを読む前に"
    - [Shore Foam](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 航跡と衝突
<strong>船や泳ぐキャラクターの後ろ</strong>には泡の筋が残ります。

航跡の作り方は 3 つです。ブラシで泡の履歴に描く方法は、物の位置に丸い点を描き込みます（[Water Interaction](../interaction/index.md)）。パーティクルでしぶきを出す方法もあります。水中の物の深度を使う方法は岸辺と同じ深度差で、杭の周りに自動で輪を出します。

## 航跡の形（ケルビン波）

船が水面を進むと <strong>V 字形の、波の模様</strong>ができます。ケルビン卿が理論的に示した形で、ケルビン波と呼ばれます。

```text
              船
       ╲      ●      ╱
         ╲   ↑ ↑   ╱         ← 発散波（V 字の、外側）
           ╲     ╱
            ╲   ╱  ← 横波（V 字の、内側の、横縞）
             ╲ ╱
              ·
```

| 項目 | 内容 |
| --- | --- |
| V 字の開き角 | 船の進行方向から、約 19.47°（片側）。船の速さに依存しない |
| 構成 | 船の進行方向に垂直な横波と斜めに広がる発散波 |
| 泡 | 船の真後ろに白い泡の帯（スクリュー、船体の乱れ） |

19.47° という値は船の速さに、無関係で水の分散関係から決まります（`sin⁻¹(1/3)`）。ゲームでは V 字の見た目を作るだけならこの角度の 2 本の線を描くだけで十分です。

## 作る方法

| 方法 | 内容 | 向く場面 |
| --- | --- | --- |
| 泡の履歴に船の軌跡を描く | 船の位置に泡を毎フレーム描き込む。軌跡が履歴として残り泡が広がって、消える（[Persistent Foam](foam-history.md)） | 基本。どんな船でも |
| 航跡のメッシュ | 船の後ろに、V 字形のリボン（帯）を置く。テクスチャで波と泡を描く | 大きな船。決まった形の航跡 |
| 波のシミュレーション | 船が水面を押す。波が自然に V 字形になる（[Applying a Height Map to the Surface](../interaction/apply-height.md)） | 静かな水面。小さな船、泳ぐ人 |
| パーティクル | 船首のしぶき船尾の、泡 | 補助として併用 |

## 方法 1：泡の履歴に軌跡を描く

船の <strong>水面に触れている船体</strong>の位置に 泡を描き込みます（[Writing Object Contacts](../interaction/contact.md) の、方法 2 を応用）。

```hlsl
// 船の底を上から見下ろして描く。水面より下の部分に泡を書く。
float4 WakePS(PSInput input) : SV_Target {
  float depth_below = water_height - input.world_position.y;
  if (depth_below <= 0.0) discard;
  // 船の速さに応じて、泡の強さを決める（止まっている船は、泡が出ない）
  float foam = saturate(ship_speed / max_speed) * wake_strength;
  return float4(foam, 0, 0, 1);
}
```

船が進むたびに泡が描き込まれ、軌跡が残ります。履歴の 減衰と広がりで後ろに行くほど、広がって薄くなる航跡が自然にできます。

| パラメーター | 内容 |
| --- | --- |
| 泡の強さ | 船の速さに比例。速いほど泡が濃い |
| 減衰 | 遅い（5〜10 秒）。軌跡が長く残る |
| 広がり（ぼかし） | 少し。航跡が後ろで広がる |

## 方法 2：航跡のメッシュ

船の後ろに <strong>V 字のリボンを置いて、アニメーション</strong>させます。

```text
上から見た、リボンのメッシュ:

  ╲                ╱
   ╲              ╱           各頂点に、船からの、距離（0〜1）を持たせる。
    ╲            ╱            距離に応じて、リボンが、広がり、薄くなる。
     ╲          ╱
      ╲___●___╱
```

```hlsl
// リボンの、頂点シェーダー: 船からの距離で、幅を広げる。
float t = input.distance_from_ship;                  // 0（船尾）〜 1（遠い）
float width = lerp(ship_width, ship_width * 8.0, t);
world_pos += side_vector * input.side * width;       // side: −1（左）〜 +1（右）
```

```hlsl
// ピクセル シェーダー: 距離で薄くし、V 字の縁と、中央の泡の帯をテクスチャで描く。
float fade = 1.0 - smoothstep(0.0, 1.0, t);
float foam_pattern = g_wake_tex.Sample(g_linear_wrap, float2(input.side * 0.5 + 0.5, t * 8.0 - time * 0.5)).r;
float alpha = foam_pattern * fade * wake_strength;
```

方法 1 に比べて 形を制御しやすいですが 船が曲がるとリボンも船の軌跡に沿って、曲げる必要があり実装が増えます（船の過去の位置をリストで持ちそこへリボンを並べる）。

## 船首の波とスプレー

船首は水を <strong>押しのけて</strong>、船首波（バウ ウェーブ）と、しぶきを作ります。

| 要素 | 方法 |
| --- | --- |
| 船首波 | 船首の位置に強い、押し込みを波のシミュレーションに加える（[Applying a Height Map to the Surface](../interaction/apply-height.md)） |
| しぶき | 船首でパーティクルを出す。速さに応じた数と向き |
| 泡 | 船首から船体の側面に沿って泡を描く（方法 1） |

## 衝突と水しぶき

物が水に <strong>落ちたりぶつかったり</strong>したときは、一瞬の波紋と泡が出ます。

```cpp
// 水に入った瞬間: 波紋 + 泡 + しぶき（3 つを同時に）。
void OnEnterWater(const float3& pos, float speed) {
  AddImpulse(pos.xz, radius, -speed * 0.02f);        // 波紋
  AddFoam(pos.xz, radius * 1.5f, saturate(speed / 10.0f));   // 泡を履歴に描く
  SpawnSplash(pos, speed);                           // しぶき
}
```

波紋は 広がって消える、泡は ゆっくり消える、しぶきは落ちてまた水面に小さな波紋を作ります。この 3 つの時間スケールの違いが、水に落ちた感じを作ります。

## 水の中の航跡

船が <strong>スクリュー</strong>を回すと 水中に泡の、柱ができます。水面から水中に向かって泡のパーティクルを出すと、水中から航跡が見えます（[Underwater Rendering](../underwater/index.md)）。

## よくあるミス

??? failure "船が通っても、泡の筋が出ない"
    <strong>物の位置を泡のバッファに書き込む</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 通った所に書き込んで、ゆっくり消す

## 参考

- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）
- Jensen, Golias, "Deep-Water Animation and Rendering", Gamasutra, 2001（海の描画。泡、波頭）
- Thomson (Lord Kelvin), "On Ship Waves", Proceedings of the Institution of Mechanical Engineers, 1887（ケルビン波の原典）

## 関連ページ

- [Shore Foam](index.md)
- [Water Interaction](../interaction/index.md)

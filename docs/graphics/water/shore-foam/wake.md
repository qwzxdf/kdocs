---
title: Wakes and Collisions
tags:
  - 描画
---

# Wakes and Collisions

**船の後ろや、物が水に当たった所には、泡の筋（航跡）ができます**。**物の位置を、泡のバッファに書き込む**ことで、**表現**できます。このページでは、**航跡と衝突の泡**を説明します。

!!! tip "ポイント"
    - **物が通った位置に、泡を書き込む**。
    - **書き込みは、バッファを描く（スプラット）**。
    - **履歴で、ゆっくり消える**。
    - **速さに応じて、強さを変える**。

## 航跡と衝突
**船や泳ぐキャラクターの後ろ**には**泡の筋**が**残ります**。

航跡の作り方は 3 つです。ブラシで泡の履歴に描く方法は、物の位置に丸い点を描き込みます（[Water Interaction](../interaction/index.md)）。パーティクルでしぶきを出す方法もあります。水中の物の深度を使う方法は、岸辺と同じ深度差で、杭の周りに自動で輪を出します。

## 航跡の形（ケルビン波）

船が、水面を進むと、**V 字形の、波の模様**が、できます。**ケルビン卿**が、理論的に、示した形で、**ケルビン波**と呼ばれます。

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
| V 字の、開き角 | 船の進行方向から、約 **19.47°**（片側）。**船の速さに、依存しない** |
| 構成 | 船の進行方向に、垂直な**横波**と、斜めに広がる**発散波** |
| 泡 | 船の真後ろに、**白い泡の帯**（スクリュー、船体の、乱れ） |

**19.47° という値は、船の速さに、無関係**で、水の分散関係から、決まります（`sin⁻¹(1/3)`）。ゲームでは、**V 字の、見た目**を、作るだけなら、この角度の、**2 本の線**を、描くだけで、十分です。

## 作る方法

| 方法 | 内容 | 向く場面 |
| --- | --- | --- |
| 泡の履歴に、**船の軌跡を描く** | 船の位置に、泡を、毎フレーム描き込む。**軌跡**が、履歴として、残り、泡が、広がって、消える（[Persistent Foam](foam-history.md)） | 基本。どんな船でも |
| **航跡のメッシュ** | 船の後ろに、**V 字形の、リボン（帯）**を、置く。テクスチャで、波と泡を、描く | 大きな船。決まった形の、航跡 |
| 波の、シミュレーション | 船が、水面を、押す。波が、**自然に、V 字形**になる（[Applying a Height Map to the Surface](../interaction/apply-height.md)） | 静かな、水面。小さな船、泳ぐ人 |
| パーティクル | 船首の、しぶき、船尾の、泡 | 補助として、併用 |

## 方法 1：泡の履歴に、軌跡を描く

船の、**水面に触れている、船体**の位置に、**泡を、描き込み**ます（[Writing Object Contacts](../interaction/contact.md) の、方法 2 を、応用）。

```hlsl
// 船の底を、上から見下ろして描く。水面より下の部分に、泡を、書く。
float4 WakePS(PSInput input) : SV_Target {
  float depth_below = water_height - input.world_position.y;
  if (depth_below <= 0.0) discard;
  // 船の速さに応じて、泡の強さを決める（止まっている船は、泡が出ない）
  float foam = saturate(ship_speed / max_speed) * wake_strength;
  return float4(foam, 0, 0, 1);
}
```

船が、進むたびに、泡が、描き込まれ、**軌跡**が、残ります。履歴の、**減衰と、広がり**で、**後ろに行くほど、広がって、薄くなる**航跡が、自然にできます。

| パラメーター | 内容 |
| --- | --- |
| 泡の強さ | 船の**速さ**に、比例。速いほど、泡が、濃い |
| 減衰 | 遅い（5〜10 秒）。軌跡が、長く、残る |
| 広がり（ぼかし） | 少し。航跡が、後ろで、**広がる** |

## 方法 2：航跡のメッシュ

船の後ろに、**V 字の、リボンを、置いて、アニメーション**させます。

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
// ピクセル シェーダー: 距離で薄くし、V 字の縁と、中央の泡の帯を、テクスチャで描く。
float fade = 1.0 - smoothstep(0.0, 1.0, t);
float foam_pattern = g_wake_tex.Sample(g_linear_wrap, float2(input.side * 0.5 + 0.5, t * 8.0 - time * 0.5)).r;
float alpha = foam_pattern * fade * wake_strength;
```

方法 1 に比べて、**形を、制御しやすい**ですが、**船が、曲がる**と、リボンも、船の軌跡に沿って、**曲げる**必要があり、実装が、増えます（船の過去の位置を、リストで持ち、そこへリボンを、並べる）。

## 船首の波と、スプレー

船首は、水を、**押しのけて**、**船首波**（バウ ウェーブ）と、**しぶき**を、作ります。

| 要素 | 方法 |
| --- | --- |
| 船首波 | 船首の位置に、**強い、押し込み**を、波のシミュレーションに加える（[Applying a Height Map to the Surface](../interaction/apply-height.md)） |
| しぶき | 船首で、**パーティクル**を、出す。速さに応じた、数と、向き |
| 泡 | 船首から、船体の側面に沿って、泡を、描く（方法 1） |

## 衝突と、水しぶき

物が、水に、**落ちたり、ぶつかったり**したときは、**一瞬の、波紋と、泡**が、出ます。

```cpp
// 水に入った瞬間: 波紋 + 泡 + しぶき（3 つを同時に）。
void OnEnterWater(const float3& pos, float speed) {
  AddImpulse(pos.xz, radius, -speed * 0.02f);        // 波紋
  AddFoam(pos.xz, radius * 1.5f, saturate(speed / 10.0f));   // 泡を、履歴に描く
  SpawnSplash(pos, speed);                           // しぶき
}
```

波紋は、**広がって消える**、泡は、**ゆっくり消える**、しぶきは、**落ちて、また、水面に、小さな波紋**を、作ります。この、**3 つの、時間スケールの違い**が、水に落ちた感じを、作ります。

## 水の中の、航跡

船が、**スクリュー**を、回すと、**水中に、泡の、柱**ができます。水面から、**水中に向かって、泡の、パーティクル**を出すと、**水中から、航跡**が見えます（[Underwater Rendering](../underwater/index.md)）。

## よくあるミス

??? failure "船が通っても、泡の筋が出ない"
    **物の位置を、泡のバッファに書き込む**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **通った所に書き込んで、ゆっくり消す**

## 参考

- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）
- Jensen, Golias, "Deep-Water Animation and Rendering", Gamasutra, 2001（海の描画。泡、波頭）
- Thomson (Lord Kelvin), "On Ship Waves", Proceedings of the Institution of Mechanical Engineers, 1887（ケルビン波の原典）

## 関連ページ

- [Shore Foam](index.md)
- [Water Interaction](../interaction/index.md)

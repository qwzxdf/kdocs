---
title: Other Underwater Elements
tags:
  - 描画
---

# Other Underwater Elements

<strong>水中の雰囲気は、霧や光だけでなく、粒子・色補正・音でも作れます</strong>。このページでは、<strong>水中の他の要素</strong>を説明します。

!!! tip "ポイント"
    - 浮遊する粒子（マリン スノー）で、深さの感じを出す。
    - 色補正で、全体を青緑に寄せる。
    - 音を、こもらせる（ローパス フィルタ）。
    - 画面の端を少し歪ませると、水中らしい。

## 水中の他の要素
| 要素 | 内容 |
| --- | --- |
| 視界 | 水中の霧で見える距離を制限 |
| ゆらぎ | 画面全体を法線の動きで少し歪ませる（[Post-Processing](../../postprocess/index.md)） |
| 泡の粒子 | ゆっくり上がる泡（パーティクル） |
| マリン スノー | 漂う小さな粒（ほこり）。奥行き感が出る |
| 音 | ローパス フィルタ（こもった音） |
| 色補正 | 青緑に寄せる |

## 水中らしさを、作る、小さな要素

霧と、コースティクス、光の筋に加えて、<strong>小さな、要素</strong>を足すと、<strong>水中の、雰囲気</strong>が、大きく、変わります。

## 浮遊粒子（マリン スノー）

水中には、<strong>細かい粒子</strong>（プランクトンの死骸、泥、微生物）が、<strong>ゆっくり</strong>漂っています。カメラの周りに、小さな、白い点を、ゆっくり動かすだけで、水中にいる感じが、出ます。

| 項目 | 内容 |
| --- | --- |
| 数 | 数百〜数千個 |
| 大きさ | 小さい（数ピクセル）。奥にあるほど、小さく |
| 動き | ゆっくり、漂い、ゆっくり沈む。水流（フロー マップ）があれば、流れに乗る |
| 範囲 | カメラの周りの、箱の中。箱の外に出た粒子は、反対側へ戻す（ループ） |
| ライティング | 光の筋の中で、明るく光る（散乱）。影の中は、暗い |
| 描画 | 加算ブレンド、またはアルファ ブレンドの、小さな板（ビルボード） |

```hlsl
// 粒子: カメラの周りの箱の中に、ループさせる（箱の外に出ると、反対側に出る）。
float3 pos = initial_position + velocity * time;
pos = camera_position + fmod(pos - camera_position + box_size * 0.5, box_size) - box_size * 0.5;
```

<strong>カメラの周りの箱の中だけ</strong>に、粒子を置き、<strong>箱の外に出た粒子は、反対側から、再登場</strong>させると、数百個で、無限に広がる、粒子の海に見えます。

## 泡（気泡）

| 種類 | 内容 |
| --- | --- |
| 吐いた息（ダイバー） | プレイヤーの、口から、大きな泡が、上昇する。だんだん、大きくなる（水圧が下がる） |
| 水に落ちた、物の泡 | 水に入った瞬間、多数の、小さな泡。数秒で、水面へ上がる |
| スクリュー、物の動き | 船のスクリューの後ろに、泡の帯 |
| 火山、熱水 | 地面から、泡が、立ち上る |

泡は、<strong>パーティクル</strong>で、表現します。<strong>上に向かって、上昇し、ゆらゆら揺れ</strong>、水面で、消えるように、します。

| パラメーター | 目安 |
| --- | --- |
| 上昇速度 | 0.2〜0.5 m/s |
| 揺れ | 左右に、小さな、サイン波 |
| 寿命 | 水面に着くまで（または、固定の時間） |
| 見た目 | 半透明の、丸。縁が、明るく、中心が、透ける。小さな、ハイライト |

## 水の動き（ゆらぎ）

水中では、<strong>水の流れ</strong>で、<strong>海藻が、ゆらゆら揺れ</strong>、物が、わずかに、漂います。

| 要素 | 方法 |
| --- | --- |
| 海藻、サンゴ | 頂点シェーダーで、ゆっくりした、揺れ（[Wind](../../terrain/vegetation/wind.md) と、同じ方法を、ゆっくり、大きな、波長で） |
| 魚の群れ | ボイド（群れの、アルゴリズム）で、動かす。GPU で、数千匹 |
| 浮かぶごみ | 水の流れに、沿って、ゆっくり動かす |

水中の動きは、<strong>空気中より、はるかに、ゆっくり</strong>で、<strong>周期も、長い</strong>。同じ式でも、速さの係数を、小さくします。

## 画面の、歪み（水中のレンズ効果）

カメラが、水の中に入ると、<strong>画面全体が、ゆらゆらと、歪んで</strong>見えます（光が、波打つ水の中を、通るため。マスクを、通して見るときも、歪む）。

```hlsl
// ポストプロセス: 画面を、ゆっくり歪ませる。
float2 wobble = float2(
    sin(uv.y * 20.0 + time * 1.5),
    cos(uv.x * 20.0 + time * 1.2)) * 0.002;           // ごく小さく（0.002 程度）
float3 color = g_scene.Sample(g_linear_clamp, uv + wobble).rgb;
```

歪みは、<strong>ごく、わずか</strong>にします。強すぎると、<strong>酔います</strong>。

## 色補正

水中は、全体の、<strong>色味</strong>が、変わります。

| 要素 | 変更 |
| --- | --- |
| 彩度 | 下げる（赤が失われ、全体が、青緑に偏る） |
| コントラスト | 下げる（霧で、コントラストが落ちる） |
| 色相 | 青緑に、寄せる（カラー グレーディング、[Color Grading](../../postprocess/color-grading/index.md)） |
| 周辺減光 | 強める（暗い、閉じた視界の印象） |
| 被写界深度 | 遠くを、ぼかす（水の濁りで、遠くが、ぼやける） |

水に入った瞬間に、カラー グレーディングの、<strong>LUT を、切り替える</strong>（または、補間する）と、<strong>水の中に入った</strong>ことが、はっきり伝わります。

## 音

見た目だけでなく、<strong>音</strong>も、水中の、<strong>雰囲気</strong>を、大きく変えます。

| 要素 | 変更 |
| --- | --- |
| 周波数 | 高音を、カットする（ローパス フィルタ）。水中では、こもった音になる |
| 反響 | 音が、ぼやけて、遠くまで届く |
| 環境音 | 水の、ごぼごぼ、という低音。泡の音 |
| 水面の、上の音 | 小さく、こもって聞こえる（逆に、水面の上から、水中の音は、ほぼ聞こえない） |

水に入る、<strong>境目</strong>で、<strong>フィルタを、なめらかに、切り替える</strong>と、水中に入った感じが、出ます。

## 水に入った、瞬間と、出る瞬間

| 瞬間 | 演出 |
| --- | --- |
| 水に、入る | 水しぶき、泡、画面の、水滴、音の、フィルタ、霧と、色補正の、切り替え（数フレームで、補間） |
| 水から、出る | 画面を、水が、流れ落ちる（レンズの水滴）、音が、元に戻る、霧と色補正が、元に戻る |

<strong>瞬間的に、切り替える</strong>と、不自然です。<strong>水面を、またぐ間</strong>（0.2〜0.5 秒）で、補間します（[The Underside of the Surface and Crossing It](surface-back.md)）。

## よくあるミス

??? failure "水中なのに、地上と同じ雰囲気"
    <strong>粒子・色補正・音</strong>も<strong>切り替える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 粒子・色・音も、水中用に切り替える

## 参考

- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Reynolds, "Flocks, Herds, and Schools: A Distributed Behavioral Model", SIGGRAPH 1987（ボイド（群れ）の原典）

## 関連ページ

- [Underwater Rendering](index.md)
- [Color Grading](../../postprocess/color-grading/index.md)

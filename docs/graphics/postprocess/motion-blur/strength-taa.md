---
title: 強さと TAA
tags:
  - 描画
---

# 強さと TAA

**モーション ブラーは、「かければ良い」ものではありません**。**強すぎると酔い、画面が見づらく、弱すぎると効果が分からない**ので、**強さの設計**が**重要**です。また、**TAA は同じ速度バッファを使い、時間方向の平均なのでモーション ブラーと見た目が混ざり、順序・ジッター・ゴーストに注意**が必要です。このページでは、**シャッター角と強さの決め方・フレームレートの補正・最大長・対象の除外・TAA との関係・オプション設計**を説明します。

!!! tip "ポイント"
    - 強さ ＝ <strong>シャッター角</strong>。<strong>180° が標準</strong>（<strong>1 フレーム時間の半分、シャッターが開いている想定</strong>）。
    - <strong>ブラー長 ＝ 速度 × (シャッター角 / 360°)</strong>。<strong>フレームレートに依存しない設計</strong>にする。
    - <strong>最大ブラー長</strong>（<strong>画面高さの 3〜5 %</strong>）で<strong>制限</strong>。<strong>酔い・破綻の防止</strong>。
    - <strong>武器・UI・遠景</strong>など<strong>除外</strong>すべき対象がある。
    - <strong>TAA と速度バッファを共有</strong>。<strong>ジッターを速度に混ぜない</strong>。
    - <strong>好みが分かれる</strong>ので、<strong>設定でオフにできる</strong>ようにする。

## シャッター角

<strong>実際のカメラ（映画）</strong>では、**1 フレームの時間のうち、シャッターが開いている割合**を<strong>「シャッター角」</strong>で**表します**。**180° なら、フレーム時間の半分**が**開いています**。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="シャッター角">
<text x="20" y="26" class="fig-title">シャッター角が大きいほど、軌跡（ブラー）が長い</text>
<g font-size="13">
<text x="40" y="70" style="font-weight:700">90°（弱い）</text><rect x="160" y="52" width="40" height="22" fill="#2563eb" fill-opacity="0.8"/><rect x="200" y="52" width="40" height="22" fill="#2563eb" fill-opacity="0.35"/>
<text x="40" y="120" style="font-weight:700">180°（標準）</text><rect x="160" y="102" width="40" height="22" fill="#2563eb" fill-opacity="0.8"/><rect x="200" y="102" width="80" height="22" fill="#2563eb" fill-opacity="0.35"/>
<text x="40" y="170" style="font-weight:700">360°（最大）</text><rect x="160" y="152" width="40" height="22" fill="#2563eb" fill-opacity="0.8"/><rect x="200" y="152" width="160" height="22" fill="#2563eb" fill-opacity="0.35"/>
<text x="420" y="80">物体が 1 フレームで動く距離 ＝ 濃い四角の幅</text>
<text x="420" y="104">ブラー長 ＝ 動く距離 × (角度 / 360°)</text>
<text x="420" y="128">ゲームの標準は 180° 前後（0.5）</text>
</g>
</svg>

<div class="formula">ブラー長 ＝ 速度（1 フレームの移動量）× ( シャッター角 / 360° )</div>

| シャッター角 | 見た目 |
| --- | --- |
| **90°** | **控えめ**（**スポーティな、くっきり**） |
| **180°** | **標準的**（**映画の見た目**） |
| **270°〜360°** | **強い**（**夢のような、流れる動き**） |

## フレームレートの補正

**速度バッファの速度**は<strong>「前フレームからの移動量」</strong>なので**フレームレートが違うと、同じ動きでも速度が違います**（**30 FPS は 60 FPS の 2 倍の移動量**）。**そのままブラーにすると、低 FPS でブラーが長くなりすぎます**。**実際のカメラは「時間」で決まる**ので**ブラー長 ＝ 速度 ÷ フレーム時間 × シャッター時間**で**一定にする**のが**理想**です。

```hlsl
float2 ScaleVelocity(float2 velocity_per_frame, float delta_time, float shutter_seconds) {
  float2 velocity_per_second = velocity_per_frame / max(delta_time, 1e-4);
  return velocity_per_second * shutter_seconds;
}
```

| 点 | 説明 |
| --- | --- |
| **`shutter_seconds`** | **例：1/120 秒**（**フレームレートに依らず固定**） |
| **効果** | **30 FPS でも 144 FPS でも、同じ長さのブラー** |
| **注意** | **低 FPS ではブラーが画面に対し短くなり、動きが粗く見える**。**用途で選ぶ** |

**もう 1 つの考え方**は、<strong>「シャッター角を固定」</strong>（**常にフレーム時間の割合**）です。**どちらが良いかは、ゲームの見せ方**で**決めます**。

## 最大ブラー長

<strong>極端に速い動き（急旋回・瞬間移動）</strong>で、**ブラーが画面の広い範囲に伸びると、画面が崩れ・酔います**。

| 項目 | 目安 |
| --- | --- |
| **最大ブラー長** | **画面の高さの 3〜5 %** |
| **最小** | **0.5 画素未満はスキップ** |
| **タイル サイズ** | **最大ブラー長に合わせる**（[タイル最大速度](tile-max.md)） |

## 対象の除外

**ブラーを掛けない方が良い物**があります。

| 対象 | 理由 |
| --- | --- |
| <strong>プレイヤーの武器・手（ビューモデル）</strong> | **カメラに固定され、ブラーが不自然** |
| **UI** | **ポストプロセスの後に描く** |
| <strong>遠景（空）</strong> | **カメラ回転で空全体が流れすぎる** |
| **小さい物体** | **ブラーが見えず、コストだけ** |
| **カット・瞬間移動の直後** | **速度が壊れている** |

## TAA との関係

**TAA は速度バッファ（動きのベクトル）で、前フレームの結果を再投影**するので、**モーション ブラーと速度バッファを共有**します。

| 点 | 内容 |
| --- | --- |
| **順序** | **TAA の後にブラー**（または**前**）。**エンジンによる** |
| **ジッター** | **速度から、TAA のジッターを除く**（**除かないと静止した物が、ブラーやゴーストでぶれる**） |
| **ゴースト** | **ブラーで混ざった色は、TAA の履歴の妥当性を下げる**ので、**履歴を拒否する判定に注意** |
| **見た目の混ざり** | **TAA 自体が時間平均なので、ブラーを強くしすぎると、二重にぼける** |
| **ノイズ（ジッター）の相乗効果** | **ブラーのサンプル ノイズを、TAA が平均して、滑らかに** |

<!-- fig:motion-blur-vs-taa:begin -->
<!-- fig:motion-blur-vs-taa:end -->

## 設定項目の設計

| 項目 | 内容 |
| --- | --- |
| **ON / OFF** | **酔いやすい人のため、必ず切れるように** |
| <strong>強さ（スライダー）</strong> | **シャッター角を、0〜360° の範囲で** |
| **カメラ / オブジェクトを別々に** | **カメラ ブラーだけオン**など |
| **品質** | **サンプル数・半解像度** |

**モーション ブラーは、好き嫌いが分かれます**。**デフォルトは控えめ**にして、**ユーザーが調整できる**ようにします。

## よくあるミス

??? failure "低 FPS でブラーが長すぎる、高 FPS で短すぎる"
    **フレーム時間で補正**する（`速度 ÷ dt × シャッター時間`）。

??? failure "強すぎて酔う・見づらい"
    **最大ブラー長で制限**、**デフォルトは控えめ**、**オプションで OFF**。

??? failure "静止した物が、TAA とブラーでぶれる"
    **ジッターを速度から除く**。

??? failure "武器・UI までぼける"
    **ビューモデル・UI を除外**（**マスク・描画順**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 強さ ＝ <strong>シャッター角</strong>（<strong>180° が標準</strong>）。<strong>ブラー長 ＝ 速度 × 角度/360°</strong>
    - [x] <strong>フレーム時間で補正</strong>して<strong>FPS に依らない</strong>見た目に
    - [x] <strong>最大ブラー長（画面高さの 3〜5 %）</strong>で<strong>制限</strong>
    - [x] <strong>武器・UI・遠景は除外</strong>
    - [x] <strong>TAA と速度バッファを共有</strong>。<strong>ジッターを引く</strong>。<strong>設定で切れるように</strong>

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）

## 関連ページ

- [モーション ブラー](index.md)
- [ぼかしの実装](blur-pass.md)
- [TAA](../antialiasing/taa.md)
- [速度バッファ](velocity-buffer.md)

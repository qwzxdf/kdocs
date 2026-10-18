---
title: Strength and TAA
tags:
  - 描画
---

# Strength and TAA

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

シャッター角と見た目の関係です。90° は控えめで、スポーティでくっきりした動きになります。180° は標準的で、映画の見た目です。270°〜360° は強く、夢のような流れる動きになります。

## フレームレートの補正

**速度バッファの速度**は<strong>「前フレームからの移動量」</strong>なので**フレームレートが違うと、同じ動きでも速度が違います**（**30 FPS は 60 FPS の 2 倍の移動量**）。**そのままブラーにすると、低 FPS でブラーが長くなりすぎます**。**実際のカメラは「時間」で決まる**ので**ブラー長 ＝ 速度 ÷ フレーム時間 × シャッター時間**で**一定にする**のが**理想**です。

```hlsl
float2 ScaleVelocity(float2 velocity_per_frame, float delta_time, float shutter_seconds) {
  float2 velocity_per_second = velocity_per_frame / max(delta_time, 1e-4);
  return velocity_per_second * shutter_seconds;
}
```

時間固定のシャッターのコードの要点です。`shutter_seconds` は、例えば 1/120 秒で、フレームレートに依らず固定です。効果として、30 FPS でも 144 FPS でも同じ長さのブラーになります。ただし、低 FPS ではブラーが画面に対して短くなり、動きが粗く見えるので、用途で選びます。

**もう 1 つの考え方**は、<strong>「シャッター角を固定」</strong>（**常にフレーム時間の割合**）です。**どちらが良いかは、ゲームの見せ方**で**決めます**。

## 最大ブラー長

<strong>極端に速い動き（急旋回・瞬間移動）</strong>で、**ブラーが画面の広い範囲に伸びると、画面が崩れ・酔います**。

極端に速い動き（急旋回・瞬間移動）では、ブラーが画面の広い範囲に伸びて、画面が崩れ、酔います。最大ブラー長は画面の高さの 3〜5 %、最小は 0.5 画素未満をスキップ、タイル サイズは最大ブラー長に合わせます（[Tile Max Velocity](tile-max.md)）。

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

<svg class="fig illust motion" data-fig="motion-blur-vs-taa" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-motion-blur-vs-taa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">モーション ブラーと TAA: TAA は、動きに合わせて前の色を使い、くっきり保つ。ブラーは、動きの跡を、わざとぼかす</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">棒(幅 4)が右へ動く。速さ 4・8・16・32 画素 / フレーム。見た目の流れの長さと、TAA で、履歴を使いすぎたときの残像を比べる</text>
<rect x="30" y="96" width="900" height="250" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 速さごとの、跡の長さ(画素)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><text x="50" y="152" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">速さ 4</text>
<rect x="140" y="138" width="3" height="16" fill="#2ea043" opacity="0.85"/>
<text x="149.20689655172413" y="151" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ブラー(シャッター 1/2): 2 画素</text>
<rect x="140" y="158" width="70.0" height="16" fill="#e5484d" opacity="0.85"/>
<text x="218.0" y="171" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">履歴の残像(α=0.1、5% まで): 116 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;1.0000" values="0;0;1;1"/><text x="50" y="204" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">速さ 8</text>
<rect x="140" y="190" width="3" height="16" fill="#2ea043" opacity="0.85"/>
<text x="150.41379310344828" y="203" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ブラー(シャッター 1/2): 4 画素</text>
<rect x="140" y="210" width="140.0" height="16" fill="#e5484d" opacity="0.85"/>
<text x="288.0" y="223" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">履歴の残像(α=0.1、5% まで): 232 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4398;0.4400;1.0000" values="0;0;1;1"/><text x="50" y="256" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">速さ 16</text>
<rect x="140" y="242" width="4.83" height="16" fill="#2ea043" opacity="0.85"/>
<text x="152.82758620689654" y="255" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ブラー(シャッター 1/2): 8 画素</text>
<rect x="140" y="262" width="280.0" height="16" fill="#e5484d" opacity="0.85"/>
<text x="428.0" y="275" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">履歴の残像(α=0.1、5% まで): 464 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6265;0.6267;1.0000" values="0;0;1;1"/><text x="50" y="308" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">速さ 32</text>
<rect x="140" y="294" width="9.66" height="16" fill="#2ea043" opacity="0.85"/>
<text x="157.6551724137931" y="307" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ブラー(シャッター 1/2): 16 画素</text>
<rect x="140" y="314" width="560.0" height="16" fill="#e5484d" opacity="0.85"/>
<text x="140" y="327" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">履歴の残像(α=0.1、5% まで): 928 画素</text>
</g>
<rect x="30" y="366" width="900" height="110" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="356" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 使い分け</text>
<text x="50" y="406" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">TAA(再投影つき)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8265;0.8267;1.0000" values="0;0;1;1"/></text>
<text x="260" y="406" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">動きの分だけ履歴の位置をずらして使う → 棒は、くっきり。ぼけない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8265;0.8267;1.0000" values="0;0;1;1"/></text>
<text x="50" y="430" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">モーション ブラー<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8798;0.8800;1.0000" values="0;0;1;1"/></text>
<text x="260" y="430" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">動きの跡を、わざとぼかす → 速さが「見える」。映像らしさ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8798;0.8800;1.0000" values="0;0;1;1"/></text>
<text x="50" y="454" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">TAA の履歴を再投影しない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9332;0.9333;1.0000" values="0;0;1;1"/></text>
<text x="260" y="454" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">跡が 928 画素も残る → ゴースト(悪い)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.9332;0.9333;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">動く物は、TAA でも、ブラーでも、見た目が変わる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ブラーは、速さに比例して長くなる(意図した効果)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8132;0.8133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">TAA の残像は、バグ。両方を使うときは、ブラーを先に、TAA を後に<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8132;0.8133;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

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

- [Motion Blur](index.md)
- [Blur Pass Implementation](blur-pass.md)
- [TAA](../antialiasing/taa.md)
- [Velocity Buffer](velocity-buffer.md)

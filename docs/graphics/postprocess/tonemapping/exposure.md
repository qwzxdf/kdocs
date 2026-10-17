---
title: 露出
tags:
  - 描画
---

# 露出

**露出**は、**HDR の光の量に掛ける倍率**です。**カメラで言う「絞り・シャッター速度・ISO 感度」をまとめた 1 つの数**で、**画面全体の明るさ**を決めます。**トーンマップの前に掛ける**ので、**同じ光景でも露出で「明るい昼」にも「暗い夜」にも見えます**。このページでは、**EV（露出値）・カメラの 3 要素・EV100 による物理ベースの露出・露出補正・露出の決め方**を説明します。

!!! tip "ポイント"
    - 露出後の値 ＝ <strong>HDR の輝度 × 倍率</strong>。<strong>トーンマップの前に掛ける</strong>。
    - <strong>EV</strong> は<strong>2 の冪で表す指標</strong>。<strong>EV が 1 上がるごとに、光の量は半分（暗く）</strong>。<strong>1 EV ＝ 1 ストップ</strong>。
    - カメラの<strong>絞り・シャッター・ISO</strong>は<strong>どれも光の量を 2 倍・半分にできる</strong>。<strong>ゲームでは 1 つの倍率にまとめる</strong>。
    - <strong>EV100</strong> は <strong>ISO 100 を基準にした EV</strong>。<strong>物理ベース（PBR）の光の単位</strong>と<strong>相性が良い</strong>。
    - <strong>露出補正</strong> ＝ <strong>自動露出の結果に足す EV のずれ</strong>。<strong>アーティストの調整</strong>。
    - 露出が<strong>合っていない</strong>と、<strong>明部が真っ白に飛ぶ</strong>か、<strong>暗部が真っ黒に潰れる</strong>。

<!-- fig:exposure-ev:begin -->

<svg class="fig illust motion" data-fig="exposure-ev" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-exposure-ev" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">露出（EV）:+1 EV で光の量が 2 倍、−1 EV で半分</text>
<rect x="70" y="110" width="130" height="100" fill="#414141" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.1379;0.3448;0.4483;0.6552;0.7586;0.8621;1.0000" values="#414141;#414141;#414141;#a8a8a8;#a8a8a8;#191919;#191919;#414141;#414141"/></rect>
<text x="135" y="100" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">暗い物(0.05)</text>
<rect x="235" y="110" width="130" height="100" fill="#757575" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.1379;0.3448;0.4483;0.6552;0.7586;0.8621;1.0000" values="#757575;#757575;#757575;#ffffff;#ffffff;#2d2d2d;#2d2d2d;#757575;#757575"/></rect>
<text x="300" y="100" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">中間の物(0.18)</text>
<rect x="400" y="110" width="130" height="100" fill="#cacaca" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.1379;0.3448;0.4483;0.6552;0.7586;0.8621;1.0000" values="#cacaca;#cacaca;#cacaca;#ffffff;#ffffff;#4f4f4f;#4f4f4f;#cacaca;#cacaca"/></rect>
<text x="465" y="100" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">明るい物(0.6)</text>
<rect x="565" y="110" width="130" height="100" fill="#ffffff" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.1379;0.3448;0.4483;0.6552;0.7586;0.8621;1.0000" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#a3a3a3;#a3a3a3;#ffffff;#ffffff"/></rect>
<text x="630" y="100" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">光源(3.0)</text>
<rect x="90" y="290" width="600" height="12" rx="6" fill="#e2e8f0"/>
<rect x="89.0" y="284" width="2" height="24" fill="#64748b"/>
<text x="90.0" y="326" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">-3 EV</text>
<rect x="189.0" y="284" width="2" height="24" fill="#64748b"/>
<text x="190.0" y="326" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">-2 EV</text>
<rect x="289.0" y="284" width="2" height="24" fill="#64748b"/>
<text x="290.0" y="326" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">-1 EV</text>
<rect x="389.0" y="284" width="2" height="24" fill="#64748b"/>
<text x="390.0" y="326" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">0 EV</text>
<rect x="489.0" y="284" width="2" height="24" fill="#64748b"/>
<text x="490.0" y="326" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">+1 EV</text>
<rect x="589.0" y="284" width="2" height="24" fill="#64748b"/>
<text x="590.0" y="326" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">+2 EV</text>
<rect x="689.0" y="284" width="2" height="24" fill="#64748b"/>
<text x="690.0" y="326" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">+3 EV</text>
<circle cx="390.0" cy="296" r="11" fill="#2563eb" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.1379;0.3448;0.4483;0.6552;0.7586;0.8621;1.0000" values="390;390;390;690;690;90;90;390;390"/></circle>
<text x="90" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">露出 0 EV:中間の物が、中間の灰色<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1377;0.1379;1.0000" values="1;1;0;0"/></text>
<text x="90" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">露出を上げる…<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1377;0.1379;0.3446;0.3448;1.0000" values="0;0;1;1;0;0"/></text>
<text x="90" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">+3 EV（8 倍）:明るい物が白飛び<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.4480;0.4483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="90" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">露出を下げる…<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4480;0.4483;0.6549;0.6552;1.0000" values="0;0;1;1;0;0"/></text>
<text x="90" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">−3 EV（1/8）:暗い物が真っ黒（つぶれる）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6549;0.6552;0.7583;0.7586;1.0000" values="0;0;1;1;0;0"/></text>
<text x="90" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">0 EV に戻す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7583;0.7586;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:exposure-ev:end -->

## なぜ露出が要るのか

**HDR の値は、「光の絶対量」に近い**ので**幅が非常に広い**です。**ディスプレイに映せるのは 0〜1 だけ**なので、**どの範囲を 0〜1 に割り当てるか**を**先に決める**必要があります。**これが露出**です。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="露出で範囲を選ぶ">
<text x="20" y="26" class="fig-title">露出 ＝ 広い明るさの中から、見せたい範囲を選んで、0〜1 に合わせる</text>
<defs><linearGradient id="ex-g" x1="0" x2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#fff7d1"/></linearGradient></defs>
<rect x="40" y="60" width="700" height="34" fill="url(#ex-g)" stroke="#94a3b8"/>
<g font-size="12"><text x="40" y="112">0.01（暗い部屋）</text><text x="250" y="112">1</text><text x="400" y="112">100</text><text x="540" y="112">10,000</text><text x="700" y="112">100,000（太陽）</text></g>
<rect x="170" y="130" width="140" height="22" rx="4" fill="#2563eb" fill-opacity="0.35" stroke="#2563eb" stroke-width="2"/>
<text x="240" y="170" text-anchor="middle" style="font-size:13px;fill:#2563eb">夜の屋内を撮る露出</text>
<rect x="400" y="130" width="200" height="22" rx="4" fill="#e5484d" fill-opacity="0.3" stroke="#e5484d" stroke-width="2"/>
<text x="500" y="170" text-anchor="middle" style="font-size:13px;fill:#e5484d">晴天の屋外を撮る露出</text>
<text x="40" y="214" style="font-size:13px">選んだ範囲の外は、暗い側は真っ黒に潰れ、明るい側は真っ白に飛ぶ。</text>
<text x="40" y="236" style="font-size:13px">屋内から屋外へ出ると、見える範囲を切り替える（＝露出を変える）必要がある。</text>
</svg>

## EV（露出値）

<div class="formula">露出後の値 = 輝度 × 2^(−EV)　（EV が大きいほど暗くなる）</div>

| EV の差 | 光の量 | たとえ |
| --- | --- | --- |
| **+1 EV** | **半分** | **1 段暗くする**（絞りを 1 段絞る） |
| **−1 EV** | **2 倍** | **1 段明るくする** |
| **+3 EV** | **1/8** | **かなり暗く** |
| **差が 0** | **そのまま** | — |

<strong>「1 段（ストップ）」で 2 倍・半分</strong>という**単位**は、**人間の明るさの感じ方が対数的**であることに合っています。**EV が等間隔なら、見た目の明るさもほぼ等間隔に変わります**。

## カメラの 3 つの要素

**実際のカメラは、3 つの要素で光の量を決めます**。**どれも「1 段」変えると光が 2 倍・半分**になります。

| 要素 | 内容 | 副作用 |
| --- | --- | --- |
| <strong>絞り（F 値）</strong> | **レンズの穴の大きさ**。**F が小さいほど明るい** | **被写界深度**が変わる（開けるとボケる） |
| **シャッター速度** | **光を取り込む時間**。**長いほど明るい** | **モーション ブラー**が変わる（遅いとブレる） |
| **ISO 感度** | **センサーの増幅率**。**高いほど明るい** | **ノイズ**が増える |

<div class="formula">EV = log₂( F² / t ) − log₂( ISO / 100 )　（F：F 値、t：シャッター秒、ISO：感度）</div>

**ゲームではこれを 1 つの倍率にまとめます**。**絞りは DOF**（[被写界深度](../dof/index.md)）、**シャッターはモーション ブラー**（[モーション ブラー](../motion-blur/index.md)）と**別に決める**ことも多く、**露出としては合計の EV だけ使います**。

## EV100 と物理ベースの露出

**EV100** は、**ISO 100 に換算した EV** です。**絞り・シャッターの組み合わせが違っても、同じ EV100 なら、同じ明るさ**になります。

```hlsl
float ExposureFromEV100(float ev100) {
  float max_luminance = 1.2 * exp2(ev100);
  return 1.0 / max_luminance;
}

float3 ApplyExposure(float3 hdr_color, float ev100) {
  return hdr_color * ExposureFromEV100(ev100);
}
```

| 点 | 説明 |
| --- | --- |
| **`1.2 * exp2(ev100)`** | **この輝度のとき、ちょうど 1（真っ白）になる<strong>（飽和輝度）。</strong>1.2 はカメラの標準的な係数** |
| **`1.0 / …`** | **その逆数を倍率にする**（輝度 × 倍率 ＝ 0〜1 付近になる） |
| **単位をそろえる** | **ライトの強さ（ルクス・カンデラ）を物理値**にすると**露出とセットで**明るさが**一貫** |

### 典型的な EV100

| 状況 | EV100 |
| --- | --- |
| <strong>晴天の屋外（日向）</strong> | **約 15** |
| **曇り** | **約 12** |
| **明るい室内** | **約 7〜8** |
| **暗い室内** | **約 4〜5** |
| <strong>夜景（街灯）</strong> | **約 0〜3** |
| **星明かり** | **約 −3〜−5** |

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="EV100 の目盛り">
<text x="20" y="26" class="fig-title">EV100 の目盛り：1 つ違うごとに、光の量が 2 倍</text>
<line x1="40" y1="100" x2="740" y2="100" stroke="currentColor" stroke-width="2"/>
<g font-size="12" text-anchor="middle">
<line x1="60" y1="92" x2="60" y2="108" stroke="currentColor"/><text x="60" y="126">−3</text><text x="60" y="146" style="font-size:11px">星明かり</text>
<line x1="170" y1="92" x2="170" y2="108" stroke="currentColor"/><text x="170" y="126">2</text><text x="170" y="146" style="font-size:11px">夜景</text>
<line x1="290" y1="92" x2="290" y2="108" stroke="currentColor"/><text x="290" y="126">5</text><text x="290" y="146" style="font-size:11px">暗い室内</text>
<line x1="410" y1="92" x2="410" y2="108" stroke="currentColor"/><text x="410" y="126">8</text><text x="410" y="146" style="font-size:11px">明るい室内</text>
<line x1="540" y1="92" x2="540" y2="108" stroke="currentColor"/><text x="540" y="126">12</text><text x="540" y="146" style="font-size:11px">曇り</text>
<line x1="680" y1="92" x2="680" y2="108" stroke="currentColor"/><text x="680" y="126">15</text><text x="680" y="146" style="font-size:11px">晴天の屋外</text>
</g>
<text x="40" y="60" style="font-size:13px">暗い ←　　　　　　　　　　　　　　　　　　　　　　　　　　　　　→ 明るい（EV100 が大きいほど、倍率は小さい＝暗く映す）</text>
</svg>

## 露出補正

**自動露出が決めた EV に、手で EV を足す**のが**露出補正**です。**画作りの意図**（**ここは少し暗く、雰囲気を出す**）を**反映**できます。

```hlsl
float finalEV100 = autoEV100 + exposure_compensation;
```

| 用途 | 例 |
| --- | --- |
| **ステージごとの調整** | **ホラー ステージは −1、砂漠は +0.5** |
| **イベント演出** | **爆発の瞬間だけ −2 してまぶしさを演出** |
| **ユーザー設定** | **明るさ（ガンマ）スライダー** |

## ゲームでの露出の決め方

| 方式 | 内容 | 向く場面 |
| --- | --- | --- |
| **固定の EV** | **ステージごとに決めた値** | **室内のみ・明るさが一定のゲーム** |
| **エリアごとの EV** | **ボリュームで EV を指定し、境で補間** | **屋内外が混在するゲーム** |
| **自動露出** | **画面の明るさから毎フレーム決める**（[自動露出](auto-exposure.md)） | **明るさが大きく変わるゲーム** |
| **自動 ＋ 補正 ＋ 範囲制限** | **自動の結果に補正を足し、最小・最大 EV を決める** | **多くのゲームの標準** |

## よくあるミス

??? failure "露出をトーンマップの後に掛けて、明るさが調整できない"
    **露出は HDR のリニア値に、トーンマップの前**に掛ける。

??? failure "EV の符号を逆にして、明るくしたつもりが暗くなる"
    **EV が大きいほど暗い**（`× 2^(−EV)`）。**明るくしたいなら EV を下げる**。

??? failure "ライトの強さがバラバラで、露出を変えるとあるものだけ飛ぶ"
    **ライトを物理単位にそろえる**。**オブジェクトごとの強さの「調整」を露出で隠さない**。

??? failure "屋内と屋外の境で、画面が急に明るく・暗くなる"
    **露出を境でゆっくり補間**する（[自動露出](auto-exposure.md)の時間追従）。

??? failure "絞り・シャッターの値をそのまま倍率に使って、DOF やブレとぶつかる"
    **露出（明るさ）と、DOF・ブレ（見た目の効果）は、別に設計する**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 露出 ＝ <strong>HDR に掛ける倍率</strong>。<strong>トーンマップの前</strong>に掛ける
    - [x] <strong>EV が 1 増えると光は半分</strong>。<strong>`× 2^(−EV)`</strong>
    - [x] カメラの<strong>絞り・シャッター・ISO</strong>は<strong>どれも 1 段で 2 倍</strong>。<strong>ゲームでは 1 つの倍率にまとめる</strong>
    - [x] <strong>EV100</strong>（ISO 100 基準）と<strong>物理単位のライト</strong>で<strong>明るさが一貫</strong>
    - [x] <strong>露出補正</strong>は<strong>自動露出に足す EV</strong>

## 参考

- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering"（SIGGRAPH 2014、EV100 と露出）
- ISO 2720:1974, "General Purpose Photographic Exposure Meters"
- Hoffman, "Physically Based Shading in Theory and Practice"（SIGGRAPH Course）

## 関連ページ

- [トーンマッピングと露出](index.md)
- [自動露出](auto-exposure.md)
- [Reinhard](reinhard.md)
- [被写界深度](../dof/index.md)
- [PBR](../../../3d/pbr.md)

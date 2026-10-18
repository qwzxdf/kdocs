---
title: VSM, ESM and MSM
tags:
  - 描画
---

# VSM, ESM and MSM

**通常のシャドウ マップは、深度を比べる「0 か 1」の判定**なので、**そのままぼかす（フィルタする）と、深度の平均になってしまい、正しい影になりません**。**VSM 系は、深度でなく「深度の統計（平均と二乗の平均）」を保存**し、**統計から「影の割合」を計算する**ことで、**シャドウ マップ自体をフィルタ（ぼかし）できます**。**柔らかい影が安く得られる**反面、**光漏れ**という**独特の欠点**があります。このセクションでは、**VSM の仕組み・光漏れ・ESM・EVSM・MSM・比較**を、**1 つずつ別のページ**で説明します。

## 発想：深度でなく、統計を保存する
PCF が**平均できない**理由は、**深度を平均してから比べると、誤る**ことでした。VSM は<strong>「ある範囲の深度の分布」</strong>を、**平均 μ と 2 乗平均**の 2 つの数で、**保存**します。**これらは平均（ぼかし）しても意味が保たれる**量です。

保存する量は 2 つです。M₁ = E[z] は深度の平均、M₂ = E[z²] は深度の 2 乗の平均です。この 2 つから、分散 σ² = M₂ − M₁² が求まります。

**分散** は次のとおりです。

<div class="formula">σ² = M₂ − M₁²</div>

シャドウ マップに**深度 z と z² を書き**、<strong>ぼかし（平均）</strong>をすれば、**範囲の M₁・M₂** が得られます。**ぼかしても統計としての意味が保たれる**のがポイントです。

<!-- fig:vsm-chebyshev:begin -->

<svg class="fig illust motion" data-fig="vsm-chebyshev" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vsm-chebyshev" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">分散シャドウ マップ(VSM): 深度の平均と分散だけ覚えて、チェビシェフの不等式で「光が届く割合の上限」を出す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">フィルター範囲の 16 サンプルの深度が、手前の物(0.4)6 個と、奥の地面(0.8)10 個。受ける点の深度 t を 0.2 → 1.0 に動かす</text>
<rect x="30" y="96" width="480" height="170" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 16 個のサンプルの深度(棒 = 1 個)</text>
<rect x="48" y="206.0" width="22" height="44.0" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="75" y="206.0" width="22" height="44.0" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="102" y="206.0" width="22" height="44.0" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="129" y="206.0" width="22" height="44.0" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="156" y="206.0" width="22" height="44.0" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="183" y="206.0" width="22" height="44.0" fill="#fca5a5" stroke="#64748b" stroke-width="1"/>
<rect x="210" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="237" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="264" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="291" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="318" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="345" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="372" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="399" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="426" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<rect x="453" y="162.0" width="22" height="88.0" fill="#93c5fd" stroke="#64748b" stroke-width="1"/>
<text x="48" y="118" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">赤 = 手前の物(深度 0.4)、青 = 奥の地面(0.8)</text>
<line x1="40" y1="178.5" x2="490" y2="178.5" stroke="#2ea043" stroke-width="2.5" stroke-dasharray="6 5"/>
<text x="488" y="172.5" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043">平均 μ = 0.650</text>
<rect x="540" y="96" width="390" height="170" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="540" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 覚えておく値は、たった 2 つ</text>
<text x="560" y="130" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">平均(深度の平均)</text>
<text x="560" y="150" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">μ = 0.650</text>
<text x="560" y="170" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">2 乗の平均 − 平均の 2 乗</text>
<text x="560" y="190" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">分散 σ² = 0.0375</text>
<text x="560" y="210" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">保存するもの</text>
<text x="560" y="230" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">(深度, 深度²) の 2 枚</text>
<rect x="30" y="290" width="900" height="190" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="280" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">③ 受ける点の深度 t を動かしたときの、光が届く割合</text>
<path d="M70.0,304.0 L90.5,304.0 L111.0,304.0 L131.5,304.0 L152.0,304.0 L172.5,304.0 L193.0,304.0 L213.5,304.0 L234.0,304.0 L254.5,304.0 L275.0,304.0 L295.5,360.25 L316.0,360.25 L336.5,360.25 L357.0,360.25 L377.5,360.25 L398.0,360.25 L418.5,360.25 L439.0,360.25 L459.5,360.25 L480.0,360.25 L500.5,360.25 L521.0,360.25 L541.5,360.25 L562.0,360.25 L582.5,360.25 L603.0,360.25 L623.5,360.25 L644.0,360.25 L664.5,360.25 L685.0,360.25 L705.5,454.0 L726.0,454.0 L746.5,454.0 L767.0,454.0 L787.5,454.0 L808.0,454.0 L828.5,454.0 L849.0,454.0 L869.5,454.0 L890.0,454.0" fill="none" stroke="#2ea043" stroke-width="3.5"/>
<path d="M70.0,304.0 L90.5,304.0 L111.0,304.0 L131.5,304.0 L152.0,304.0 L172.5,304.0 L193.0,304.0 L213.5,304.0 L234.0,304.0 L254.5,304.0 L275.0,304.0 L295.5,304.0 L316.0,304.0 L336.5,304.0 L357.0,304.0 L377.5,304.0 L398.0,304.0 L418.5,304.0 L439.0,304.0 L459.5,304.0 L480.0,304.0 L500.5,304.0 L521.0,304.0 L541.5,304.4 L562.0,307.52 L582.5,313.38 L603.0,321.33 L623.5,330.64 L644.0,340.59 L664.5,350.6 L685.0,360.25 L705.5,369.29 L726.0,377.57 L746.5,385.07 L767.0,391.78 L787.5,397.75 L808.0,403.05 L828.5,407.74 L849.0,411.9 L869.5,415.58 L890.0,418.84" fill="none" stroke="#e5484d" stroke-width="3.5" stroke-dasharray="7 5"/>
<circle cx="86" cy="468" r="6" fill="#2ea043"/>
<text x="96" y="472" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">正解(深度の分布をそのまま数える)</text>
<circle cx="305.79999999999995" cy="468" r="6" fill="#e5484d"/>
<text x="315.79999999999995" y="472" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">VSM(平均と分散から、チェビシェフ)</text>
<circle cx="70.0" cy="304.0" r="6" fill="#2ea043"><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0806;0.0944;0.1083;0.1222;0.1361;0.1500;0.1639;0.1778;0.1917;0.2056;0.2194;0.2333;0.2472;0.2611;0.2750;0.2889;0.3028;0.3167;0.3306;0.3444;0.3583;0.3722;0.3861;0.4000;0.4139;0.4278;0.4417;0.4556;0.4694;0.4833;0.4972;0.5111;0.5250;0.5389;0.5528;0.5667;0.5806;0.5944;0.6083;0.6222;1.0000" values="70;70;90.5;111;131.5;152;172.5;193;213.5;234;254.5;275;295.5;316;336.5;357;377.5;398;418.5;439;459.5;480;500.5;521;541.5;562;582.5;603;623.5;644;664.5;685;705.5;726;746.5;767;787.5;808;828.5;849;869.5;890;890"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0806;0.0944;0.1083;0.1222;0.1361;0.1500;0.1639;0.1778;0.1917;0.2056;0.2194;0.2333;0.2472;0.2611;0.2750;0.2889;0.3028;0.3167;0.3306;0.3444;0.3583;0.3722;0.3861;0.4000;0.4139;0.4278;0.4417;0.4556;0.4694;0.4833;0.4972;0.5111;0.5250;0.5389;0.5528;0.5667;0.5806;0.5944;0.6083;0.6222;1.0000" values="304;304;304;304;304;304;304;304;304;304;304;304;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;360.25;454;454;454;454;454;454;454;454;454;454;454"/></circle>
<circle cx="70.0" cy="304.0" r="6" fill="#e5484d"><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0806;0.0944;0.1083;0.1222;0.1361;0.1500;0.1639;0.1778;0.1917;0.2056;0.2194;0.2333;0.2472;0.2611;0.2750;0.2889;0.3028;0.3167;0.3306;0.3444;0.3583;0.3722;0.3861;0.4000;0.4139;0.4278;0.4417;0.4556;0.4694;0.4833;0.4972;0.5111;0.5250;0.5389;0.5528;0.5667;0.5806;0.5944;0.6083;0.6222;1.0000" values="70;70;90.5;111;131.5;152;172.5;193;213.5;234;254.5;275;295.5;316;336.5;357;377.5;398;418.5;439;459.5;480;500.5;521;541.5;562;582.5;603;623.5;644;664.5;685;705.5;726;746.5;767;787.5;808;828.5;849;869.5;890;890"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0806;0.0944;0.1083;0.1222;0.1361;0.1500;0.1639;0.1778;0.1917;0.2056;0.2194;0.2333;0.2472;0.2611;0.2750;0.2889;0.3028;0.3167;0.3306;0.3444;0.3583;0.3722;0.3861;0.4000;0.4139;0.4278;0.4417;0.4556;0.4694;0.4833;0.4972;0.5111;0.5250;0.5389;0.5528;0.5667;0.5806;0.5944;0.6083;0.6222;1.0000" values="304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304;304.4;307.52;313.38;321.33;330.64;340.59;350.6;360.25;369.29;377.57;385.07;391.78;397.75;403.05;407.74;411.9;415.58;418.84;418.84"/></circle>
<text x="70" y="500" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">受ける点が、手前の物より手前(t ≤ μ)なら、無条件で光が届く<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="70" y="500" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">t が 0.4 〜 0.8: 正解は 0.625(奥の 10 個だけ届く)、VSM は それ以上の値(上限)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2887;0.2889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="500" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">t &gt; 0.8: 全部の深度より奥 → 正解は 0、VSM は 小さいが 0 ではない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;0.6220;0.6222;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6665;0.6667;1.0000" values="0;0;1;1"/><rect x="540" y="96" width="390" height="170" rx="12" fill="#fef2f2" stroke="#e5484d" stroke-width="2.5"/>
<text x="556" y="120" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">VSM は、上限なので、</text>
<text x="556" y="144" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">本当より明るくなる側にずれる</text>
<text x="556" y="168" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">最大のずれ 0.56</text>
<text x="556" y="192" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">(光が漏れる = ライト ブリーディング)</text>
</g>
</svg>

<!-- fig:vsm-chebyshev:end -->

## 影の割合：チェビシェフの不等式
受け手の深度を `t` とします。**範囲の深度の分布**（平均 μ・分散 σ²）から、<strong>「t より、奥にある深度の割合」</strong>＝**日向の割合**を**見積もります**。**正確な分布は分からない**ので、**チェビシェフの（片側）不等式**で**上限**を使います。

<div class="formula">t ≤ μ のとき：日向 = 1　、　t &gt; μ のとき：p_max(t) = σ² / (σ² + (t − μ)²)</div>

チェビシェフの不等式による判定は、2 つの場合に分かれます。t ≤ μ（受け手が平均より手前）なら、完全に日向です。t > μ（受け手が平均より奥）なら、遮蔽物がある可能性があり、日向の割合の上限が `p_max` で与えられます。

`p_max` は、**t が μ に近いほど 1 に近く、離れるほど 0 に近づきます**。**分散が大きい**（深度がばらついている＝**エッジの近く**）ほど、<strong>半影（中間の値）</strong>が出ます。

```hlsl
float ChebyshevUpperBound(float2 moments, float t) {
  float mean = moments.x;
  float variance = max(moments.y - mean * mean, kMinVariance);
  float d = t - mean;
  float p_max = variance / (variance + d * d);
  return (t <= mean) ? 1.0 : p_max;
}
```

コードの要点です。`kMinVariance` は、分散が 0（平らな面）のとき、0 除算やアクネにならないようにする下限で、バイアスの代わりになります。`t ≤ mean` なら完全に日向です。戻り値は日向の割合（上限）で、影の濃さは `1 − 日向` です。

## 手順
VSM の処理は 3 段階です。深度でなく (z, z²) をピクセル シェーダーで書き込みます（浮動小数点の 2 チャンネル）。次に、分離可能なガウス ブラーや、ミップ・異方性フィルタでぼかします。最後に、受け手の深度でぼかされたモーメントを引き、チェビシェフで日向の割合を求めます。

```hlsl
float2 WriteMoments(float depth) {
  float dx = ddx(depth);
  float dy = ddy(depth);
  float moment2 = depth * depth + 0.25 * (dx * dx + dy * dy);
  return float2(depth, moment2);
}
```

コードの要点です。`ddx・ddy` の項は、面の傾きによる深度の分散を `M₂` に足すもので、傾いた面でもアクネが出ません（バイアスの代わり）。フォーマットは `R32G32_FLOAT` にします。精度が大事で、16 ビットでは足りないことが多いです。ぼかしは、シャドウ マップに分離したガウス ブラーをかけ、ミップを作って遠くを粗くすることもできます。

### 利点：フィルタが安い

| フィルタ | PCF | VSM |
| --- | --- | --- |
| **広いソフトネス** | サンプルを**増やす**（重い） | **ぼかして**おくだけ（シャドウ マップ全体に、1 回）。**画素あたりは、1 サンプル** |
| **ミップ・異方性** | **使えない** | **使える**（遠くの影を安く滑らか） |
| **MSAA** | 難しい | **使える** |
| **アクネ** | バイアスが必要 | **出にくい**（面の傾きが分散に入る） |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Light Bleeding](light-bleeding.md) | VSM の最大の弱点と、対策 |
| [ESM](esm.md) | 指数で深度をゆがめる、簡単な改良 |
| [EVSM](evsm.md) | 指数と VSM を組み合わせる |
| [MSM](msm.md) | 高次のモーメントで、光漏れを抑える |
| [Comparison with PCF](comparison.md) | VSM 系の比較・PCF との選び方 |

## 通常の、シャドウ マップの、弱点

通常のシャドウ マップは、**「画素の深度」と「保存された深度」を、比較**して、**0 か 1** を、返します。この結果は、**フィルタ（ぼかし）**が、**かけられません**（**深度を、ぼかしてから**比べると、**間違った影**になる）。**PCF**は、**複数回、比較**して、平均しますが、**1 画素あたり、数十回の、読み込み**が、必要で、**重い**です。

**フィルタ可能な、シャドウ マップ**は、**深度を、ぼかして**から、**比較**できる、**表現**に、変えます。**ぼかしは、シャドウ マップに**、**1 回だけ**かけ、**シェーダーでは、1 回の、読み込み**で、**なめらかな影**が、得られます。

| 手法 | 保存するもの | ぼかしの、可否 |
| --- | --- | --- |
| 通常 | 深度 `z` | **ぼかせない**（比較結果の、平均が、必要） |
| **VSM**（Variance） | 深度の、**平均**と**2 乗の平均**（分散を、求めるため） | **ぼかせる**（ガウスぼかし、ミップ、異方性フィルタ） |
| **ESM**（Exponential） | `exp(c × z)` | **ぼかせる** |
| **EVSM** | `exp(c × z)` の、**平均と、2 乗の平均** + `exp(−c × z)` | **ぼかせる**。光漏れを、減らす |
| **MSM**（Moment） | 深度の、**4 つのモーメント**（`z`、`z²`、`z³`、`z⁴`） | **ぼかせる**。光漏れが、少ない |

## 共通の、利点

| 利点 | 内容 |
| --- | --- |
| **ぼかしを、安く** | シャドウ マップに、**ガウスぼかし**をかけるだけで、**柔らかい影**。1 画素あたり、**シェーダーで、1 回の読み込み** |
| **ミップマップ、異方性フィルタ** | **シャドウ マップに、ミップ**を、作れる。**遠くの影**の、**エイリアシング**が、減る |
| **影の、ハードウェア フィルタリング** | テクスチャの、**バイリニア**、**トライリニア**、**異方性**が、**そのまま、使える** |
| **バイアスが、小さい** | 比較は、確率的な、推定なので、**自己影が、出にくい** |

## 共通の、欠点

| 欠点 | 内容 |
| --- | --- |
| **光漏れ**（light bleeding） | **影の中**に、**明るい、斑点**が、出る。**重なる、遮蔽物**で、起きやすい（[Light Bleeding](light-bleeding.md)） |
| **メモリが、増える** | 深度 1 値ではなく、**2〜4 値**（`R32G32`、`R32G32B32A32`）を、保存する |
| **精度** | 浮動小数点の、精度が、**必要**（16 ビットでは、足りないことがある） |
| **シャドウ パスが、重い** | 深度を、**値の、変換**して、書き出す（ピクセル シェーダーが、必要） |

## 手法の、選び方

| 優先すること | 手法 |
| --- | --- |
| まず、フィルタ可能に（シンプル） | **VSM**（[VSM](#vsm)）。光漏れが、許容できる場面（遮蔽物が、単純） |
| 光漏れを、減らしたい | **EVSM**（[EVSM](evsm.md)）、**MSM**（[MSM](msm.md)） |
| 実装を、軽く（1 チャンネル） | **ESM**（[ESM](esm.md)）。遮蔽物と、受け手が、**離れている**場面（**光漏れ・影の、薄れ**が、出る） |
| PCF で、足りる | **VSM 系は、使わない**。PCF のほうが、**光漏れがなく**、**確実** |

近年は、**PCF と、ブルー ノイズ、TAA**（[PCF](../pcf.md)）、**ハードウェア レイトレーシング**で、**柔らかい影**を、得る方向に、移っています。VSM 系は、**特定の、場面**（特に、カスケードの、フィルタ、**ぼかしの、広い影**）で、**使われます**。

## VSM（分散シャドウ マップ） {#vsm}

Donnelly と Lauritzen（2006）の、**VSM**は、**シャドウ マップに、深度 `z` と、深度の 2 乗 `z²`** を、保存します。

```hlsl
// シャドウ パス: 深度と、深度の 2 乗を、書き出す（R32G32_FLOAT のレンダー ターゲット）。
float2 main(float4 pos : SV_Position) : SV_Target {
  float z = pos.z;                           // 0〜1 の深度（正射影では線形）
  float dx = ddx(z), dy = ddy(z);
  float moment2 = z * z + 0.25 * (dx * dx + dy * dy);       // 画素内の、深度の変化を、2 乗の項に加える
  return float2(z, moment2);
}
```

```hlsl
// メイン パス: ぼかした、2 つのモーメントから、チェビシェフの不等式で、光が当たる確率の、上限を求める。
float ChebyshevUpperBound(float2 moments, float t) {
  float mean = moments.x;                    // E[z]
  float variance = max(moments.y - mean * mean, 1e-5);       // E[z²] − E[z]²
  float d = t - mean;
  float p_max = variance / (variance + d * d);                // チェビシェフの不等式
  return (t <= mean) ? 1.0 : p_max;                           // 手前なら、完全に光が当たる
}

float lit = ChebyshevUpperBound(g_shadow_vsm.SampleLevel(g_linear_clamp, uv, 0).xy, depth);
```

**考え方**：シャドウ マップの、1 画素（ぼかした後は、周りの、複数の画素）に、**深度の分布**（平均 `μ` と、分散 `σ²`）が、**入っている**。**画素の深度 `t` が、`μ` より、遠い**とき、**「`t` より、手前に、遮蔽物がある確率」**の、**上限**を、**チェビシェフの不等式**で、**求めます**。

```text
P(z ≥ t) ≤ σ² / (σ² + (t − μ)²)             （t > μ のとき）
```

これが、**光が、当たる確率の、上限**で、**影の、なめらかさ**に、使います。

## よくあるミス

??? failure "VSM の影の中に、光が漏れて、白い筋が出る"
    **光漏れ**。**[Light Bleeding](light-bleeding.md)の対策**（**しきい値で絞る**・**EVSM・MSM**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **VSM は、深度の統計を保存して、フィルタ可能にする**
    - [x] **柔らかい影が安いが、光漏れがある**

## 参考

- Donnelly, Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games 2006
- Annen, Mertens, Seidel, Eisemann, Durand, "Exponential Shadow Maps", Graphics Interface 2008
- Lauritzen, McGuire, "Layered Variance Shadow Maps", Graphics Interface 2008（光漏れの、軽減）
- Peters, Klein, "Moment Shadow Mapping", Symposium on Interactive 3D Graphics and Games 2015
- Lauritzen, "Summed-Area Variance Shadow Maps", GPU Gems 3, Chapter 8, 2007

## 関連ページ

- [Shadows](../index.md)
- [PCF](../pcf.md)
- [Light Bleeding](light-bleeding.md)

---
title: Noise, Banding and Flicker
tags:
  - 描画
---

# Noise, Banding and Flicker

<strong>AO は、ノイズが残る・縞（バンディング）が見える・ちらつく</strong>ことが<strong>あります</strong>。サンプル数・ノイズ パターン・フィルタ・時間蓄積の設定で変わります。このページでは、ノイズ・バンディング・ちらつき・残像の原因と対策を説明します。

!!! tip "ポイント"
    - ノイズ ＝ サンプル不足。フィルタ・時間蓄積で消す。
    - バンディング ＝ ノイズ無しの規則的パターン。画素ごとに回転。
    - ちらつき ＝ フレームごとの不安定。時間蓄積・ノイズの安定化。
    - 残像（ゴースト）＝ 時間蓄積の履歴が合わない。履歴の拒否。

!!! info "このページを読む前に"
    - [AO Artifacts](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ノイズ・バンディング

### ざらざらしたノイズ

SSAO の積分はモンテカルロ法です。画素ごとにサンプルを 8〜16 個しか撒かないので、結果は<strong>真の値のまわりでばらつく</strong>のが当然です。サンプル数 N に対して、ばらつきの大きさは 1/√N でしか減りません。サンプルを 4 倍にして、やっとノイズが半分です。そのため、実際のゲームは「サンプルは少なく、ノイズは後でぼかして消す」という設計になっています（[AO Filtering](../filtering/index.md)）。

### 規則的な縞（バンディング）

全画素が同じ向きのサンプル パターンを使うと、ノイズは出ませんが、<strong>同じ向きの誤差が、面全体で揃って</strong>縞や段として見えます。人間の目は、ランダムなノイズより規則的な模様に敏感です。そこで、画素ごとにサンプル パターンを回転させて、<strong>誤差を乱数のようにばらまきます</strong>。縞はノイズに変わり、ノイズはブラーで消せます。つまり、バンディング対策は「ノイズを意図して足し、後で消す」という二段構えです（[Noise Patterns](../filtering/noise-pattern.md)）。

ここで、ブラーの大きさとノイズの繰り返し周期は合わせます。4×4 のタイルで回転パターンを敷き詰めたなら、4×4 のブラーで、タイル 1 つ分の画素を平均すれば、パターンの全方向が混ざって消えます。周期が合っていないと、タイルの境目がうっすら残ります。

ホワイト ノイズは低周波の成分を含むため、ぼかしても大きな斑が残ります。<strong>IGN（Interleaved Gradient Noise）やブルー ノイズ</strong>は低周波が少なく、同じぼかしでもきれいに消えます。

## ちらつきと残像

### 静止していてもちらつく

時間蓄積（[Temporal Accumulation](../filtering/temporal.md)）は、毎フレームノイズのパターンを変えて、過去の結果と混ぜることでサンプルを増やす方法です。混ぜる割合 α が大きい（新しい結果を重視する）と、ノイズが十分に平均されず、ちらつきとして見えます。α を下げる（履歴を重視する）か、フレームあたりのサンプルを増やします。ただし α を下げすぎると、次の残像の問題が強くなります。

### カメラが動くとちらつく

深度そのものがフレームごとに揺れる場合です。低解像度の深度を使っていたり、深度のミップが平均で作られていたりすると、1 画素動くだけで値が大きく変わります。フル解像度の深度を使う（HBAO+ の方針）か、ミップを代表の 1 点で作る（[SAO](../sao.md)）と安定します。

### 動く物体に残像（ゴースト）

時間蓄積は、<strong>「前のフレームの同じ場所の値」</strong>を再利用します。動く物体は、前のフレームでは別の場所にあったので、動きベクトルで位置を合わせます。動きベクトルが不正確、または前に隠れていた場所が現れた（ディスオクルージョン）と、履歴が間違った値になり、残像として尾を引きます。

対策は、履歴を<strong>疑う</strong>ことです。前フレームの深度・法線と今のフレームの値を比べて、大きく違えば履歴を捨てます。履歴を捨てた画素はサンプル数が足りないので、そこだけ空間フィルタ（ブラー）を強めてノイズを抑えます。

### より良いやり方

ノイズとちらつきを根本から減らす道具は 2 つあります。1 つは、<strong>空間時間フィルタ</strong>（履歴の分散を見て、ブラーの強さを画素ごとに決める SVGF などの考え方）です。もう 1 つは、<strong>低ディスクレパンシー列</strong>（Halton や R2 列）で、毎フレームのサンプル位置を「均等に埋まるように」ずらすことで、時間蓄積の収束を早めます。どちらも、AO だけでなく SSR・GI・影のノイズ除去にも共通して使えます。

<!-- fig:blur-noise:begin -->

<svg class="fig illust motion" data-fig="blur-noise" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-blur-noise" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ぼかす範囲を広げると、ノイズは 1/(2r+1) に減る(代わりにボケる)</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ノイズの大きさ（ぼかさない時 = 1）</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">ぼかす半径 r（画素）</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="150.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<text x="230.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2</text>
<text x="310.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">3</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<text x="470.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">5</text>
<text x="550.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">6</text>
<text x="630.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">7</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">8</text>
<path d="M70.0,81.43 L78.0,119.52 L86.0,146.73 L94.0,167.14 L102.0,183.02 L110.0,195.71 L118.0,206.1 L126.0,214.76 L134.0,222.09 L142.0,228.37 L150.0,233.81 L158.0,238.57 L166.0,242.77 L174.0,246.51 L182.0,249.85 L190.0,252.86 L198.0,255.58 L206.0,258.05 L214.0,260.31 L222.0,262.38 L230.0,264.29 L238.0,266.04 L246.0,267.67 L254.0,269.18 L262.0,270.59 L270.0,271.9 L278.0,273.13 L286.0,274.29 L294.0,275.37 L302.0,276.39 L310.0,277.35 L318.0,278.25 L326.0,279.11 L334.0,279.92 L342.0,280.7 L350.0,281.43 L358.0,282.13 L366.0,282.79 L374.0,283.42 L382.0,284.03 L390.0,284.6 L398.0,285.16 L406.0,285.68 L414.0,286.19 L422.0,286.68 L430.0,287.14 L438.0,287.59 L446.0,288.02 L454.0,288.44 L462.0,288.84 L470.0,289.22 L478.0,289.59 L486.0,289.95 L494.0,290.3 L502.0,290.63 L510.0,290.95 L518.0,291.26 L526.0,291.57 L534.0,291.86 L542.0,292.14 L550.0,292.42 L558.0,292.68 L566.0,292.94 L574.0,293.19 L582.0,293.44 L590.0,293.67 L598.0,293.9 L606.0,294.13 L614.0,294.34 L622.0,294.56 L630.0,294.76 L638.0,294.96 L646.0,295.16 L654.0,295.35 L662.0,295.53 L670.0,295.71 L678.0,295.89 L686.0,296.06 L694.0,296.23 L702.0,296.39 L710.0,296.55" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<circle cx="70.0" cy="81.43" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0950;0.1100;0.1250;0.1400;0.1550;0.1700;0.1850;0.2000;0.2150;0.2300;0.2450;0.2600;0.2750;0.2900;0.3050;0.3200;0.3350;0.3500;0.3650;0.3800;0.3950;0.4100;0.4250;0.4400;0.4550;0.4700;0.4850;0.5000;0.5150;0.5300;0.5450;0.5600;0.5750;0.5900;0.6050;0.6200;0.6350;0.6500;0.6650;0.6800;0.6950;0.7100;0.7250;0.7400;0.7550;0.7700;0.7850;0.8000;1.0000" values="70;70;83.33;96.67;110;123.33;136.67;150;163.33;176.67;190;203.33;216.67;230;243.33;256.67;270;283.33;296.67;310;323.33;336.67;350;363.33;376.67;390;403.33;416.67;430;443.33;456.67;470;483.33;496.67;510;523.33;536.67;550;563.33;576.67;590;603.33;616.67;630;643.33;656.67;670;683.33;696.67;710;710"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0950;0.1100;0.1250;0.1400;0.1550;0.1700;0.1850;0.2000;0.2150;0.2300;0.2450;0.2600;0.2750;0.2900;0.3050;0.3200;0.3350;0.3500;0.3650;0.3800;0.3950;0.4100;0.4250;0.4400;0.4550;0.4700;0.4850;0.5000;0.5150;0.5300;0.5450;0.5600;0.5750;0.5900;0.6050;0.6200;0.6350;0.6500;0.6650;0.6800;0.6950;0.7100;0.7250;0.7400;0.7550;0.7700;0.7850;0.8000;1.0000" values="81.43;81.43;138.57;172.86;195.71;212.04;224.29;233.81;241.43;247.66;252.86;257.25;261.02;264.29;267.14;269.66;271.9;273.91;275.71;277.35;278.83;280.19;281.43;282.57;283.63;284.6;285.51;286.35;287.14;287.88;288.57;289.22;289.83;290.41;290.95;291.47;291.95;292.42;292.86;293.28;293.67;294.05;294.42;294.76;295.09;295.41;295.71;296.01;296.29;296.55;296.55"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">r = 0: ぼかさない。ノイズ 1<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2597;0.2600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">r = 2（5×5 の平均）: ノイズ 0.2 まで下がる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2597;0.2600;0.4397;0.4400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">r = 4（9×9）: 0.11。ただし輪郭がボケ始める<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4397;0.4400;0.6197;0.6200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">だから輪郭を保つ、深度を見るぼかしを使う<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6197;0.6200;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:blur-noise:end -->

## よくあるミス

??? failure "動くとちらつく"
    <strong>時間蓄積の履歴拒否・ブレンド率・ノイズの安定化</strong>を確認。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ノイズ・バンディング・ちらつきは、フィルタと時間蓄積で対処

## 参考

- Georgiev, Fajardo, "Blue-Noise Dithered Sampling", SIGGRAPH 2016 Talks
- Heitz, Belcour, Ostromoukhov, Coeurjolly, Iehl, "A Low-Discrepancy Sampler that Distributes Monte Carlo Errors as a Blue Noise in Screen Space", SIGGRAPH 2019 Talks
- Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（時間蓄積・履歴のクランプ）
- Salvi, "An Excursion in Temporal Supersampling", GDC 2016（分散クリッピング）

## 関連ページ

- [AO Artifacts](index.md)
- [AO Filtering](../filtering/index.md)
- [Temporal Accumulation](../filtering/temporal.md)

---
title: Temporal Accumulation
tags:
  - 描画
---

# Temporal Accumulation

<strong>1 フレームのサンプル数が少なくても、毎フレーム違うサンプルで計算して、過去のフレームの結果と混ぜれば、時間をかけて、サンプルが蓄積されます</strong>。これが時間蓄積です。カメラや物が動くと、過去の結果は位置がずれるので、速度（動きのベクトル）で再投影し、合わなければ捨てます。このページでは、再投影・履歴の拒否・ブレンド率・ゴースト対策を説明します。

!!! tip "ポイント"
    - 毎フレーム違うサンプル ＋ 前フレームの結果と混ぜる＝サンプルが蓄積する。
    - 速度バッファで、前フレームの位置を求める（[Velocity Buffer](../../postprocess/motion-blur/velocity-buffer.md)）。
    - 深度・法線が合わない履歴は拒否（ゴースト対策）。
    - ブレンド率は 0.05〜0.1（履歴 90〜95 %）。

!!! info "このページを読む前に"
    - [AO Filtering](index.md)（このセクション全体の地図と、読む順番）

## 時間蓄積とは

AO を毎フレーム 8 サンプルで計算し、前のフレームの結果と平均すれば、数フレームで実質的に数十サンプルを使ったのと同じ精度になります。これが時間蓄積です。[TAA](../../postprocess/antialiasing/taa.md) と全く同じ発想で、サンプルを空間（1 画素の中）でなく時間（複数フレーム）に分散させて集めます。

静止しているなら、前のフレームの同じ画素の値をそのまま使えます。難しいのは<strong>動くとき</strong>です。カメラが動けば、画面上の同じ場所に映る物が変わります。前のフレームの同じ画素ではなく、「今映っている点が前のフレームでは画面のどこにあったか」を調べ、その位置の値を読む必要があります。これが再投影です。

## 手順

<!-- fig:temporal-converge:begin -->

<svg class="fig illust motion" data-fig="temporal-converge" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-temporal-converge" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">時間蓄積(AO): 毎フレーム 4 サンプルだけでも、前のフレームと混ぜれば、ノイズが減っていく</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">真の AO = 0.6 の画素。毎フレームの推定は 4 サンプルの平均。混ぜる割合 α を 1.0(蓄積なし)/ 0.2 / 0.1 に変えて、400 画素の、ばらつきを測る</text>
<rect x="30" y="96" width="700" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 画素ごとのばらつき(標準偏差)</text>
<path d="M70.0,176.96 L86.41,144.21 L102.82,150.9 L119.23,147.5 L135.64,147.28 L152.05,144.86 L168.46,154.81 L184.87,144.08 L201.28,149.16 L217.69,149.46 L234.1,146.46 L250.51,168.37 L266.92,143.44 L283.33,147.7 L299.74,151.01 L316.15,154.88 L332.56,151.48 L348.97,147.28 L365.38,153.8 L381.79,149.73 L398.21,153.67 L414.62,150.06 L431.03,141.95 L447.44,147.33 L463.85,146.98 L480.26,152.49 L496.67,147.56 L513.08,148.79 L529.49,148.74 L545.9,146.46 L562.31,140.07 L578.72,153.51 L595.13,148.64 L611.54,149.21 L627.95,150.06 L644.36,146.41 L660.77,145.06 L677.18,148.84 L693.59,150.56 L710.0,152.66" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="0;0;1;1"/></path>
<text x="706.0" y="144.66471444906418" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">α = 1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,176.96 L86.41,208.32 L102.82,221.94 L119.23,240.3 L135.64,252.88 L152.05,261.01 L168.46,270.33 L184.87,273.24 L201.28,273.58 L217.69,277.53 L234.1,279.87 L250.51,283.7 L266.92,283.61 L283.33,284.83 L299.74,285.65 L316.15,287.53 L332.56,285.46 L348.97,281.34 L365.38,281.99 L381.79,281.86 L398.21,282.56 L414.62,285.08 L431.03,283.04 L447.44,283.62 L463.85,283.7 L480.26,283.3 L496.67,284.1 L513.08,284.82 L529.49,283.51 L545.9,284.27 L562.31,282.84 L578.72,282.53 L595.13,286.24 L611.54,283.43 L627.95,281.08 L644.36,282.11 L660.77,281.83 L677.18,283.31 L693.59,283.27 L710.0,286.07" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2126;0.2128;1.0000" values="0;0;1;1"/></path>
<text x="706.0" y="278.07418909249407" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">α = 0.2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2126;0.2128;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,176.96 L86.41,194.32 L102.82,204.21 L119.23,217.35 L135.64,228.49 L152.05,238.28 L168.46,248.22 L184.87,256.2 L201.28,260.71 L217.69,266.79 L234.1,272.94 L250.51,278.63 L266.92,282.45 L283.33,286.4 L299.74,289.34 L316.15,293.08 L332.56,294.71 L348.97,294.97 L365.38,296.8 L381.79,297.92 L398.21,299.04 L414.62,300.77 L431.03,300.09 L447.44,301.17 L463.85,302.05 L480.26,302.84 L496.67,303.73 L513.08,304.6 L529.49,304.68 L545.9,304.92 L562.31,304.11 L578.72,303.83 L595.13,305.34 L611.54,304.62 L627.95,303.02 L644.36,303.28 L660.77,303.29 L677.18,303.83 L693.59,303.85 L710.0,304.52" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3617;1.0000" values="0;0;1;1"/></path>
<text x="706.0" y="296.52276948343746" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">α = 0.1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3617;1.0000" values="0;0;1;1"/></text>
<text x="710.0" y="366" text-anchor="end" style="font-size:11px;font-weight:500;fill:#64748b">経過フレーム</text>
<rect x="750" y="96" width="180" height="280" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="750" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">40 フレーム後のばらつき</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1062;0.1064;1.0000" values="0;0;1;1"/><text x="766" y="150" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">α = 1</text>
<text x="766" y="178" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d">0.240</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;1.0000" values="0;0;1;1"/><text x="766" y="220" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">α = 0.2</text>
<text x="766" y="248" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5aa28">0.078</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4041;0.4043;1.0000" values="0;0;1;1"/><text x="766" y="290" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">α = 0.1</text>
<text x="766" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043">0.055</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">ばらつき(×1000):</text>
<text x="200" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1062;0.1064;1.0000" values="1;1;0;0"/></text>
<text x="200" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">240<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1062;0.1064;0.2551;0.2553;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">78<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2551;0.2553;0.4041;0.4043;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">55<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4041;0.4043;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5530;0.5532;1.0000" values="0;0;1;1"/><rect x="40" y="440" width="880" height="80" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="464" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">α = 0.1 で、ばらつきは α = 1(蓄積なし)の 23%(約 4.3 分の 1)</text>
<text x="56" y="488" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">理論: ばらつき ∝ √(α ÷ (2 − α))。α が小さいほど、静止しているときは、きれい</text>
<text x="56" y="510" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">代わりに、動くと、残像が長い(ゴースト)。α は、動きに応じて変える</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">毎フレームの AO は、少ないサンプルで、ノイズが大きい<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">前のフレームの結果を混ぜると、ノイズが平均化されて減る<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.5530;0.5532;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ただし、動く物には、ゴーストが出る<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5530;0.5532;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:temporal-converge:end -->

### ① 再投影

今の画素の点が前のフレームで画面のどこにあったかを求めます。方法は 2 つあります。

* <strong>動きベクトル（速度バッファ）</strong>を使う。画素ごとに「前のフレームでの位置との差」が書かれていて、物体の動きも含めて扱えます（[Velocity Buffer](../../postprocess/motion-blur/velocity-buffer.md)）。
* 深度とカメラ行列から求める。今の深度で点のワールド位置を復元し、前フレームのビュー射影行列で変換します。カメラの動きだけに対応し、動く物体には使えません。

### ② 履歴を読む

求めた位置から、前フレームの AO を読みます。位置が画素の中心にぴったり合うことはないので、バイリニアで補間して読みます。補間はわずかなボケを生むため、毎フレーム繰り返すと次第に広がります（TAA と同じ問題で、鮮明さを保ちたい場合は、バイキュービックで読みます）。

### ③ 履歴の検証

読んだ履歴が今の点と同じ面の値かを確かめます。動いた物体の背後から現れた場所は、前のフレームでは別の物体が映っていたので、その履歴は無関係です。前フレームの深度・法線と今のそれを比べ、違いが大きければ履歴を捨てます。

### ④ 混ぜる

<div class="formula">AO = lerp(履歴, 今の結果, α)</div>

α が小さいほど履歴を重視して滑らかになりますが、変化への追従が遅れます。0.05〜0.2 が目安です。

```hlsl
float TemporalAO(float2 uv, float current_ao) {
  float2 history_uv = Reproject(uv);
  float history_ao = history_tex.SampleLevel(linear_sampler, history_uv, 0).r;
  float history_z = history_depth_tex.SampleLevel(point_sampler, history_uv, 0).r;

  float depth_diff = abs(LinearDepth(uv) - history_z) / LinearDepth(uv);
  bool valid = all(saturate(history_uv) == history_uv) && depth_diff < 0.05;

  float alpha = valid ? 0.1 : 1.0;
  return lerp(history_ao, current_ao, alpha);
}
```

このコードのポイントは次のとおりです。再投影した位置が画面の外（0〜1 の外）なら履歴はないので α = 1（今の結果だけ）にします。深度の差は、相対値で比べます。遠い所は、絶対値で比べると誤差に埋もれるからです。

### 履歴の長さに応じた α

固定の α の代わりに、履歴の長さ n（何フレーム分溜まっているか）を数えて α = 1/(n+1) にする方法があります。これは単純平均と同じで、n が小さい（履歴が新しい）うちは今の結果を大きく取り込み、n が大きくなるほど履歴を重視します。履歴が捨てられたら n を 0 に戻します。α を下限（たとえば 0.05）で止めれば、長く溜めても追従性が残ります。起動直後や、物が現れた直後でも素早く収束するのが利点です。

## ゴーストとその対策

時間蓄積の最大の弱点は<strong>ゴースト</strong>です。動く物体の跡に前の位置の AO が残像のように残ります。

主な対策を状況別に整理します。

動く物体には、動きベクトルで再投影するのが基本です。動きベクトルがなければ、深度と法線の差で履歴を拒否して、尾を引かないようにします。カメラが急に切り替わったときは、履歴を全部捨てます。履歴が捨てられた画素は、サンプル数が足りずノイズが目立つので、その画素だけ空間フィルタを強めるとよいでしょう。ライトの変化には、AO はライトに依存しないので影響を受けません。形が変わるとき（ドアが開く、物が動く）だけが問題です。

## 分散のクランプ

最後に、一歩進んだ工夫です。TAA の<strong>近傍クランプ</strong>と同じように、今のフレームの周囲の画素の最小値・最大値（あるいは平均と分散）を求め、履歴の値をその範囲に収めます。範囲から外れた履歴は、今のフレームの状況と明らかに合わないので、「古い値の暴走」だと見なして範囲の端まで引き戻します。ゴーストの多くをこれで抑えられます。AO は 1 チャンネルのスカラーなので、実装は簡単です。

## よくあるミス

??? failure "動く物の後ろに、AO の残像（ゴースト）が出る"
    <strong>深度・法線で、履歴を拒否</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 毎フレーム違うサンプルを時間で蓄積
    - [x] 履歴の拒否で、ゴーストを防ぐ

## 参考

- Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（時間蓄積・履歴のクランプ）
- Salvi, "An Excursion in Temporal Supersampling", GDC 2016（分散クリッピング）
- Schied et al., "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice

## 関連ページ

- [AO Filtering](index.md)
- [Noise Patterns](noise-pattern.md)
- [TAA](../../postprocess/antialiasing/taa.md)

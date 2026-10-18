---
title: Fireflies (Karis Average)
tags:
  - 描画
---

# Fireflies (Karis Average)

<strong>ブルームを動かすと小さくて非常に明るい点（スペキュラのハイライト・小さな光源）が、画面の隅々で「ぴかぴか」と点滅</strong>することがあります。これを<strong>ファイアフライ（蛍）</strong>と呼びます。<strong>原因は極端に明るい 1 画素が、縮小のたびに周りの数画素分の平均に混ざり、強い光が画素の位置次第で出たり消えたりする</strong>からです。対策が Karis Average（Brian Karis）で、明るい画素の重みを下げて平均します。このページでは、ちらつきの原因・Karis Average の式・どの段に使うか・クランプ・より良いやり方を説明します。

!!! tip "ポイント"
    - ファイアフライ ＝ <strong>極端に明るい小さな点が、縮小でちらつくブルーム</strong>。
    - 原因 ＝ <strong>HDR の値が非常に大きい 1 画素が、平均に混ざる量が位置で変わる</strong>。
    - 対策 ＝ <strong>Karis Average</strong>：<strong>各サンプルの重みを `1 / (1 + 輝度)`</strong> にして、<strong>明るい画素の影響を抑える</strong>。
    - <strong>最初の縮小（1 段目）だけ</strong>に使えば<strong>十分</strong>。<strong>それ以降は普通の平均</strong>。
    - <strong>輝度のクランプ</strong>（上限を決める）も<strong>併用</strong>できる。
    - <strong>TAA</strong> があれば<strong>さらに安定</strong>する。

## ちらつきの原因

<strong>縮小は「周りの画素を平均して 1 画素にする」</strong>処理です。<strong>ここにとても明るい（例：値 1000）画素が 1 つ混ざる</strong>と、<strong>平均の値がその 1 画素に支配されます</strong>。画面が少し動くとこの明るい画素がどの縮小画素に混ざるかが変わり、ある縮小画素は 1000 ÷ 4 = 250、次のフレームは別の画素に移って 0——<strong>これが「ぴかぴか」</strong>です。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="ファイアフライの原因">
<text x="20" y="26" class="fig-title">非常に明るい 1 画素が、縮小の平均を支配する</text>
<g transform="translate(40,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">フレーム 1</text>
<g stroke="#94a3b8" fill="#f1f5f9"><rect x="0" y="0" width="40" height="40"/><rect x="40" y="0" width="40" height="40"/><rect x="0" y="40" width="40" height="40"/><rect x="40" y="40" width="40" height="40"/></g>
<rect x="0" y="0" width="40" height="40" fill="#f59e0b"/><text x="20" y="26" text-anchor="middle" style="font-size:12px;font-weight:700">1000</text>
<text x="100" y="26" style="font-size:12px">平均 ＝ 250</text>
<text x="0" y="104" style="font-size:12px">縮小画素は明るく光る</text>
</g>
<g transform="translate(300,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">フレーム 2（少し動いた）</text>
<g stroke="#94a3b8" fill="#f1f5f9"><rect x="0" y="0" width="40" height="40"/><rect x="40" y="0" width="40" height="40"/><rect x="0" y="40" width="40" height="40"/><rect x="40" y="40" width="40" height="40"/></g>
<text x="100" y="26" style="font-size:12px">明るい画素が、別の縮小画素へ</text>
<text x="100" y="48" style="font-size:12px">この縮小画素の平均 ＝ 0</text>
<text x="0" y="104" style="font-size:12px">光が消える → ちらつく</text>
</g>
<text x="40" y="206" style="font-size:13px">1 画素の値が大きすぎるので、平均に混ざる・混ざらないで、結果が極端に変わる。</text>
<text x="40" y="228" style="font-size:13px">対策は、明るい画素の「重み」を下げて、平均への影響を小さくすること。</text>
</svg>

## Karis Average

<strong>サンプルごとに輝度に応じた重みを付けて、加重平均</strong>します。

<div class="formula">重み w = 1 / (1 + 輝度)　、　平均 = Σ (w · 色) / Σ w</div>

```hlsl
float KarisWeight(float3 color) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return 1.0 / (1.0 + luma);
}

float3 KarisAverage(float3 a, float3 b, float3 c, float3 d) {
  float wa = KarisWeight(a);
  float wb = KarisWeight(b);
  float wc = KarisWeight(c);
  float wd = KarisWeight(d);
  return (a * wa + b * wb + c * wc + d * wd) / (wa + wb + wc + wd);
}
```

コードの要点です。`1 / (1 + 輝度)` の重みは、輝度 1000 のサンプルなら約 0.001、暗いサンプルなら約 1 になります。加重平均なので、重みの合計で割り、全体の明るさは保たれます（明るい点の寄与だけが小さくなります）。結果として、明るい 1 画素が平均を支配せず、ちらつきません。

この重み付けは、Karis Average と呼ばれ、Jimenez の SIGGRAPH 2014 の発表で広く知られるようになりました。

<!-- fig:karis-fireflies:begin -->

<svg class="fig illust motion" data-fig="karis-fireflies" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-karis-fireflies" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ホタル(ちらつく光の点): 1 画素だけ極端に明るいと、縮小で何倍にも広がる。Karis 平均で、明るさに応じて重みを下げる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 32 画素に、極端に明るい 1 画素(1000)がある。縮小を 3 段くり返して、ふつうの平均と Karis 平均の差を見る</text>
<text x="40" y="102" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">ふつうの平均</text>
<rect x="190.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#0f172a;#232a36"/></rect>
<rect x="208.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#0f172a;#232a36"/></rect>
<rect x="226.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#232a36"/></rect>
<rect x="244.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#232a36"/></rect>
<rect x="262.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#232a36"/></rect>
<rect x="280.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#232a36"/></rect>
<rect x="298.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#232a36"/></rect>
<rect x="316.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#232a36"/></rect>
<rect x="352.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0823" values="#0f172a;#232a36"/></rect>
<rect x="370.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#232a36"/></rect>
<rect x="388.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0851" values="#0f172a;#232a36"/></rect>
<rect x="406.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#232a36"/></rect>
<rect x="424.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0879" values="#0f172a;#fff4b8"/></rect>
<rect x="442.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#232a36"/></rect>
<rect x="460.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#0f172a;#232a36"/></rect>
<rect x="478.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#232a36"/></rect>
<rect x="496.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0935" values="#0f172a;#232a36"/></rect>
<rect x="514.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#232a36"/></rect>
<rect x="532.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963" values="#0f172a;#232a36"/></rect>
<rect x="550.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#232a36"/></rect>
<rect x="568.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0991" values="#0f172a;#232a36"/></rect>
<rect x="586.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#232a36"/></rect>
<rect x="604.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1019" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#232a36"/></rect>
<rect x="640.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047" values="#0f172a;#232a36"/></rect>
<rect x="658.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#232a36"/></rect>
<rect x="676.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#0f172a;#232a36"/></rect>
<rect x="694.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#232a36"/></rect>
<rect x="712.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#0f172a;#232a36"/></rect>
<rect x="730.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#232a36"/></rect>
<rect x="748.0" y="110.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1130" values="#0f172a;#232a36"/></rect>
<rect x="190" y="110" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="124" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 0(32 画素)</text>
<text x="790" y="124" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">最大 1000.0</text>
<rect x="190.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1488" values="#0f172a;#232a36"/></rect>
<rect x="226.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1516" values="#0f172a;#232a36"/></rect>
<rect x="262.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1544" values="#0f172a;#232a36"/></rect>
<rect x="298.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1572" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#0f172a;#232a36"/></rect>
<rect x="370.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1628" values="#0f172a;#232a36"/></rect>
<rect x="406.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1656" values="#0f172a;#e7deaa"/></rect>
<rect x="442.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1684" values="#0f172a;#232a36"/></rect>
<rect x="478.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1712" values="#0f172a;#232a36"/></rect>
<rect x="514.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1740" values="#0f172a;#232a36"/></rect>
<rect x="550.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1767" values="#0f172a;#232a36"/></rect>
<rect x="586.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1795" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1823" values="#0f172a;#232a36"/></rect>
<rect x="658.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#0f172a;#232a36"/></rect>
<rect x="694.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1879" values="#0f172a;#232a36"/></rect>
<rect x="730.0" y="144.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1907" values="#0f172a;#232a36"/></rect>
<rect x="190" y="144" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="158" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 1(16 画素)</text>
<text x="790" y="158" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">最大 500.4</text>
<rect x="190.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2279" values="#0f172a;#232a36"/></rect>
<rect x="262.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2335" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2391" values="#0f172a;#232a36"/></rect>
<rect x="406.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2447" values="#0f172a;#cfc89c"/></rect>
<rect x="478.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2502" values="#0f172a;#232a36"/></rect>
<rect x="550.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2614" values="#0f172a;#232a36"/></rect>
<rect x="694.0" y="178.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2670" values="#0f172a;#232a36"/></rect>
<rect x="190" y="178" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="192" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 2(8 画素)</text>
<text x="790" y="192" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">最大 250.6</text>
<rect x="190.0" y="212.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3070" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="212.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3181" values="#0f172a;#b7b28e"/></rect>
<rect x="478.0" y="212.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3293" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="212.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3405" values="#0f172a;#232a36"/></rect>
<rect x="190" y="212" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="226" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 3(4 画素)</text>
<text x="790" y="226" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">最大 125.7</text>
<text x="40" y="266" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">Karis 平均(明るい画素の重みを下げる)</text>
<rect x="190.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#0f172a;#232a36"/></rect>
<rect x="208.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#0f172a;#232a36"/></rect>
<rect x="226.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#232a36"/></rect>
<rect x="244.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#232a36"/></rect>
<rect x="262.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#232a36"/></rect>
<rect x="280.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#232a36"/></rect>
<rect x="298.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#232a36"/></rect>
<rect x="316.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#232a36"/></rect>
<rect x="352.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0823" values="#0f172a;#232a36"/></rect>
<rect x="370.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#232a36"/></rect>
<rect x="388.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0851" values="#0f172a;#232a36"/></rect>
<rect x="406.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#232a36"/></rect>
<rect x="424.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0879" values="#0f172a;#fff4b8"/></rect>
<rect x="442.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#232a36"/></rect>
<rect x="460.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#0f172a;#232a36"/></rect>
<rect x="478.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#232a36"/></rect>
<rect x="496.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0935" values="#0f172a;#232a36"/></rect>
<rect x="514.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#232a36"/></rect>
<rect x="532.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963" values="#0f172a;#232a36"/></rect>
<rect x="550.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#232a36"/></rect>
<rect x="568.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0991" values="#0f172a;#232a36"/></rect>
<rect x="586.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#232a36"/></rect>
<rect x="604.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1019" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#232a36"/></rect>
<rect x="640.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047" values="#0f172a;#232a36"/></rect>
<rect x="658.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#232a36"/></rect>
<rect x="676.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#0f172a;#232a36"/></rect>
<rect x="694.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#232a36"/></rect>
<rect x="712.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#0f172a;#232a36"/></rect>
<rect x="730.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#232a36"/></rect>
<rect x="748.0" y="274.0" width="18.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1130" values="#0f172a;#232a36"/></rect>
<rect x="190" y="274" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="288" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 0(32 画素)</text>
<text x="790" y="288" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">最大 1000.0</text>
<rect x="190.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1488" values="#0f172a;#232a36"/></rect>
<rect x="226.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1516" values="#0f172a;#232a36"/></rect>
<rect x="262.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1544" values="#0f172a;#232a36"/></rect>
<rect x="298.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1572" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#0f172a;#232a36"/></rect>
<rect x="370.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1628" values="#0f172a;#232a36"/></rect>
<rect x="406.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1656" values="#0f172a;#545653"/></rect>
<rect x="442.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1684" values="#0f172a;#232a36"/></rect>
<rect x="478.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1712" values="#0f172a;#232a36"/></rect>
<rect x="514.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1740" values="#0f172a;#232a36"/></rect>
<rect x="550.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1767" values="#0f172a;#232a36"/></rect>
<rect x="586.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1795" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1823" values="#0f172a;#232a36"/></rect>
<rect x="658.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1851" values="#0f172a;#232a36"/></rect>
<rect x="694.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1879" values="#0f172a;#232a36"/></rect>
<rect x="730.0" y="308.0" width="36.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1907" values="#0f172a;#232a36"/></rect>
<rect x="190" y="308" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="322" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 1(16 画素)</text>
<text x="790" y="322" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">最大 6.2</text>
<rect x="190.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2279" values="#0f172a;#232a36"/></rect>
<rect x="262.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2335" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2391" values="#0f172a;#232a36"/></rect>
<rect x="406.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2447" values="#0f172a;#3c4044"/></rect>
<rect x="478.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2502" values="#0f172a;#232a36"/></rect>
<rect x="550.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2614" values="#0f172a;#232a36"/></rect>
<rect x="694.0" y="342.0" width="72.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2670" values="#0f172a;#232a36"/></rect>
<rect x="190" y="342" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="356" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 2(8 画素)</text>
<text x="790" y="356" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">最大 2.6</text>
<rect x="190.0" y="376.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3070" values="#0f172a;#232a36"/></rect>
<rect x="334.0" y="376.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3181" values="#0f172a;#30353d"/></rect>
<rect x="478.0" y="376.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3293" values="#0f172a;#232a36"/></rect>
<rect x="622.0" y="376.0" width="144.3" height="22.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3405" values="#0f172a;#232a36"/></rect>
<rect x="190" y="376" width="576.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="180" y="390" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">段 3(4 画素)</text>
<text x="790" y="390" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">最大 1.6</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4556;0.4558;1.0000" values="0;0;1;1"/><rect x="40" y="430" width="880" height="76" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="454" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">段 3 の最大: ふつう 125.7 / Karis 1.6(79 倍の差)</text>
<text x="56" y="478" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">ふつうの平均は、1 画素の光が、縮小のたびに半分に広がるだけで、ほぼ消えない → ぼかした後に、大きな光の塊が出て、ちらつく</text>
<text x="56" y="499" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">Karis 平均は、重み 1 ÷ (1 + 輝度)で、極端に明るい画素の影響を小さくする</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ゲームでは、小さくて、とても明るい反射(ハイライト)がある<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縮小の平均で、1 画素の強い光が、広い範囲に混ざる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.4556;0.4558;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">重みを付けると、その影響が小さくなり、ちらつきが抑えられる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4556;0.4558;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:karis-fireflies:end -->

## 13 タップ ダウンサンプルに組み込む

<strong>13 タップの縮小</strong>（[ダウンサンプル](downsample.md)）では、<strong>5 つの 2×2 ボックス（中央 1・四隅 4）それぞれに Karis 重みを掛けて平均</strong>します。

```hlsl
float3 Downsample13Karis(Texture2D src, SamplerState linear_clamp, float2 uv, float2 texel) {
  float3 a = src.SampleLevel(linear_clamp, uv + texel * float2(-2, -2), 0).rgb;
  float3 b = src.SampleLevel(linear_clamp, uv + texel * float2( 0, -2), 0).rgb;
  float3 c = src.SampleLevel(linear_clamp, uv + texel * float2( 2, -2), 0).rgb;
  float3 d = src.SampleLevel(linear_clamp, uv + texel * float2(-2,  0), 0).rgb;
  float3 e = src.SampleLevel(linear_clamp, uv, 0).rgb;
  float3 f = src.SampleLevel(linear_clamp, uv + texel * float2( 2,  0), 0).rgb;
  float3 g = src.SampleLevel(linear_clamp, uv + texel * float2(-2,  2), 0).rgb;
  float3 h = src.SampleLevel(linear_clamp, uv + texel * float2( 0,  2), 0).rgb;
  float3 i = src.SampleLevel(linear_clamp, uv + texel * float2( 2,  2), 0).rgb;
  float3 j = src.SampleLevel(linear_clamp, uv + texel * float2(-1, -1), 0).rgb;
  float3 k = src.SampleLevel(linear_clamp, uv + texel * float2( 1, -1), 0).rgb;
  float3 l = src.SampleLevel(linear_clamp, uv + texel * float2(-1,  1), 0).rgb;
  float3 m = src.SampleLevel(linear_clamp, uv + texel * float2( 1,  1), 0).rgb;

  float3 group_center = KarisAverage(j, k, l, m);
  float3 group_a = KarisAverage(a, b, d, e);
  float3 group_b = KarisAverage(b, c, e, f);
  float3 group_c = KarisAverage(d, e, g, h);
  float3 group_d = KarisAverage(e, f, h, i);
  return group_center * 0.5 + (group_a + group_b + group_c + group_d) * 0.125;
}
```

<strong>各グループの Karis 平均を、通常のボックス平均の代わりに使う</strong>だけです。

## 最初の段だけに使う

<strong>Karis Average は、重みが輝度で変わるので、すべての段に使う</strong>と<strong>広いにじみまで明るい部分が弱くなりすぎます</strong>。ちらつきの原因は、最初の縮小（元の高解像度 → 1/2）で極端な値が混ざることなので、最初の 1 段だけに使い、2 段目以降は普通の平均にします。

Karis Average は、重みが輝度で変わるので、すべての段に使うと、広いにじみまで明るい部分が弱くなりすぎます。ちらつきの原因は最初の縮小（元の高解像度から 1/2）なので、1 段目だけ Karis Average（13 タップ）を使い、2 段目以降は通常の平均（4 タップのバイリニア）にします。

## 輝度のクランプ

<strong>もう 1 つの対策</strong>は、<strong>輝度の上限（クランプ）</strong>です。<strong>ブルームに入れる明るさを、たとえば 10 まで</strong>に切ると、極端な値が混ざらず、ちらつきが減ります。

```hlsl
float3 ClampBloomInput(float3 color, float max_luma) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return color * min(1.0, max_luma / max(luma, 1e-4));
}
```

| 方式 | 長所 | 短所 |
| --- | --- | --- |
| Karis Average | 明るさを保ちつつ、ちらつきを消す | 13 タップのコスト増 |
| クランプ | 簡単・安い | 非常に明るい光源が弱くなる（太陽が控えめなブルーム） |
| 併用 | 安定する | 調整項目が増える |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 1 段目だけ Karis | コストを抑え、にじみの広がりを保つ |
| クランプを併用 | 極端な値（太陽・爆発）は上限を決める |
| TAA で時間方向に安定 | 残るちらつきを時間蓄積でなだらかに（[TAA](../antialiasing/taa.md)） |
| スペキュラ側で抑える | ライティングの段階で極端なハイライトを抑える（スペキュラ エイリアシングの対策） |
| ブルームの入力を半解像度に | 最初から 1/2 で作ると、元の高解像度の極端な点が、混ざりにくい |

## よくあるミス

??? failure "ブルームを動かすと、小さな光がぴかぴかする"
    <strong>ファイアフライ</strong>。<strong>最初の縮小に Karis Average</strong>、または輝度クランプ。

??? failure "全段に Karis を使って、にじみが弱く暗い"
    <strong>1 段目だけ</strong>に使う。

??? failure "重みの合計で割り忘れて、全体が暗くなる"
    <strong>`Σ(w·色) / Σw`</strong>。<strong>必ず重みの合計で割る</strong>。

??? failure "クランプを強くしすぎて、太陽が光らない"
    <strong>上限を上げる</strong>、または<strong>Karis に切り替える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイアフライ ＝ <strong>極端に明るい小さな点が、縮小でちらつく</strong>
    - [x] <strong>Karis Average</strong> ＝ <strong>重み `1/(1+輝度)` の加重平均</strong>。<strong>明るさを保ちつつ、ちらつきを消す</strong>
    - [x] <strong>最初の縮小（1 段目）だけ</strong>に使う
    - [x] <strong>輝度クランプ</strong>も併用できる
    - [x] <strong>TAA</strong> で<strong>さらに安定</strong>

## 参考

- Brian Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013 Course）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）

## 関連ページ

- [Bloom](index.md)
- [Downsampling and the Mip Chain](downsample.md)
- [Dual Filter](dual-filter.md)
- [Compositing and Intensity](composite.md)

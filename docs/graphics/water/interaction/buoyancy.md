---
title: Buoyancy and Reaction
tags:
  - 描画
---

# Buoyancy and Reaction

<strong>物が水に浮くには浮力が必要</strong>で、<strong>水の側も物から押されて動きます</strong>。このページでは浮力の計算と水への反作用を説明します。

!!! tip "ポイント"
    - 浮力 ＝ 水に沈んだ体積に比例した、上向きの力。
    - 物体の数点で水深を求めて、力を加える。
    - 水の抵抗（ダンピング）で、揺れが収まる。
    - 物が水を押す反作用は、高さマップに書く。

## 浮力と水への反作用
<strong>水面と物の相互作用は見た目だけでなく、物理にも影響します</strong>。

相互作用の物理の要素です。浮力は水に浸かった体積に比例します（[Water Waves](../waves/index.md)）。抵抗は水中を動く物が速さに比例して減速する効果です。波紋の起点は物理エンジンの接触や速度から、ブラシの強さを決めます。

<!-- fig:buoyancy-draft:begin -->

<svg class="fig illust motion" data-fig="buoyancy-draft" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-buoyancy-draft" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">浮力は沈んだ体積に比例し、重さと釣り合う深さで止まる</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">力（重さ = 1 とする）</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">沈んでいる深さ ÷ 箱の高さ</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="230.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.25</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.5</text>
<text x="550.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.75</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<path d="M70.0,138.57 L80.67,138.57 L91.33,138.57 L102.0,138.57 L112.67,138.57 L123.33,138.57 L134.0,138.57 L144.67,138.57 L155.33,138.57 L166.0,138.57 L176.67,138.57 L187.33,138.57 L198.0,138.57 L208.67,138.57 L219.33,138.57 L230.0,138.57 L240.67,138.57 L251.33,138.57 L262.0,138.57 L272.67,138.57 L283.33,138.57 L294.0,138.57 L304.67,138.57 L315.33,138.57 L326.0,138.57 L336.67,138.57 L347.33,138.57 L358.0,138.57 L368.67,138.57 L379.33,138.57 L390.0,138.57 L400.67,138.57 L411.33,138.57 L422.0,138.57 L432.67,138.57 L443.33,138.57 L454.0,138.57 L464.67,138.57 L475.33,138.57 L486.0,138.57 L496.67,138.57 L507.33,138.57 L518.0,138.57 L528.67,138.57 L539.33,138.57 L550.0,138.57 L560.67,138.57 L571.33,138.57 L582.0,138.57 L592.67,138.57 L603.33,138.57 L614.0,138.57 L624.67,138.57 L635.33,138.57 L646.0,138.57 L656.67,138.57 L667.33,138.57 L678.0,138.57 L688.67,138.57 L699.33,138.57 L710.0,138.57" fill="none" stroke="#e5484d" stroke-width="3" opacity="1" stroke-dasharray="6 5"/>
<text x="82.8" y="128.57" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">重さ（下向き）</text>
<path d="M70.0,310.0 L78.0,306.43 L86.0,302.86 L94.0,299.29 L102.0,295.71 L110.0,292.14 L118.0,288.57 L126.0,285.0 L134.0,281.43 L142.0,277.86 L150.0,274.29 L158.0,270.71 L166.0,267.14 L174.0,263.57 L182.0,260.0 L190.0,256.43 L198.0,252.86 L206.0,249.29 L214.0,245.71 L222.0,242.14 L230.0,238.57 L238.0,235.0 L246.0,231.43 L254.0,227.86 L262.0,224.29 L270.0,220.71 L278.0,217.14 L286.0,213.57 L294.0,210.0 L302.0,206.43 L310.0,202.86 L318.0,199.29 L326.0,195.71 L334.0,192.14 L342.0,188.57 L350.0,185.0 L358.0,181.43 L366.0,177.86 L374.0,174.29 L382.0,170.71 L390.0,167.14 L398.0,163.57 L406.0,160.0 L414.0,156.43 L422.0,152.86 L430.0,149.29 L438.0,145.71 L446.0,142.14 L454.0,138.57 L462.0,135.0 L470.0,131.43 L478.0,127.86 L486.0,124.29 L494.0,120.71 L502.0,117.14 L510.0,113.57 L518.0,110.0 L526.0,106.43 L534.0,102.86 L542.0,99.29 L550.0,95.71 L558.0,92.14 L566.0,88.57 L574.0,85.0 L582.0,81.43 L590.0,77.86 L598.0,74.29 L606.0,70.71 L614.0,70.0 L622.0,70.0 L630.0,70.0 L638.0,70.0 L646.0,70.0 L654.0,70.0 L662.0,70.0 L670.0,70.0 L678.0,70.0 L686.0,70.0 L694.0,70.0 L702.0,70.0 L710.0,70.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<text x="166.0" y="253.14" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">浮力（上向き）</text>
<circle cx="70.0" cy="310.0" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0917;0.1033;0.1150;0.1267;0.1383;0.1500;0.1617;0.1733;0.1850;0.1967;0.2083;0.2200;0.2317;0.2433;0.2550;0.2667;0.2783;0.2900;0.3017;0.3133;0.3250;0.3367;0.3483;0.3600;0.3717;0.3833;0.3950;0.4067;0.4183;0.4300;0.4417;0.4533;0.4650;0.4767;0.4883;0.5000;0.5117;0.5233;0.5350;0.5467;0.5583;0.5700;0.5817;0.5933;0.6050;0.6167;0.6283;0.6400;1.0000" values="70;70;78;86;94;102;110;118;126;134;142;150;158;166;174;182;190;198;206;214;222;230;238;246;254;262;270;278;286;294;302;310;318;326;334;342;350;358;366;374;382;390;398;406;414;422;430;438;446;454;454"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0917;0.1033;0.1150;0.1267;0.1383;0.1500;0.1617;0.1733;0.1850;0.1967;0.2083;0.2200;0.2317;0.2433;0.2550;0.2667;0.2783;0.2900;0.3017;0.3133;0.3250;0.3367;0.3483;0.3600;0.3717;0.3833;0.3950;0.4067;0.4183;0.4300;0.4417;0.4533;0.4650;0.4767;0.4883;0.5000;0.5117;0.5233;0.5350;0.5467;0.5583;0.5700;0.5817;0.5933;0.6050;0.6167;0.6283;0.6400;1.0000" values="310;310;306.43;302.86;299.29;295.71;292.14;288.57;285;281.43;277.86;274.29;270.71;267.14;263.57;260;256.43;252.86;249.29;245.71;242.14;238.57;235;231.43;227.86;224.29;220.71;217.14;213.57;210;206.43;202.86;199.29;195.71;192.14;188.57;185;181.43;177.86;174.29;170.71;167.14;163.57;160;156.43;152.86;149.29;145.71;142.14;138.57;138.57"/></circle>
<circle cx="454.0" cy="138.57" r="10" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;1.0000" values="0;0;1;1"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">箱の密度が、水の 0.6 倍だとする<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">沈めるほど、押し返す力が増える<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3197;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">浮力 &lt; 重さ: まだ沈む<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.6397;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深さ 0.6 で浮力 = 重さ → 釣り合って止まる(緑の丸)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:buoyancy-draft:end -->

## 浮力と反作用

水と物の相互作用は <strong>2 方向</strong>です。

| 方向 | 内容 |
| --- | --- |
| 水 → 物 | 浮力、抵抗、波に押される力。物の動きを決める |
| 物 → 水 | 押しのけた水が、波になる。波紋、航跡、しぶき。水面の見た目を変える |

## 浮力の物理

<strong>アルキメデスの原理</strong>：<strong>物が押しのけた水の重さ</strong>だけ、上向きの力を受けます。

```text
F_buoyancy = ρ × g × V_submerged             ρ: 水の密度（1000 kg/m³）、V: 水に沈んでいる体積
```

| 状況 | 浮力 | 結果 |
| --- | --- | --- |
| 沈んでいる体積が小さい | 小さい | 物が重力で、沈む |
| 沈んでいる体積が増える | 増える | 重力と、釣り合う深さで止まる（浮く） |
| 完全に沈んだ | 最大（`ρ g V`） | 物の重さが、これより軽ければ浮き上がる |

浮力が <strong>重力と釣り合う</strong>喫水（沈む深さ）が、<strong>自然に浮く高さ</strong>です。物の密度が水より小さいと一部が、水面の上に出て浮きます。

## 実装：沈んだ体積を近似する

正確な沈んだ体積の計算は <strong>水面の高さと、物の形状の交差</strong>が必要で重いです。実用的な近似を示します。

### ① 点サンプリング（簡単）

物の複数の点（浮力点）で水面の高さを調べ、<strong>各点が受け持つ体積の沈んだ割合</strong>を、浮力に変えます（[Floating Objects](../waves/floating.md)）。

### ② 箱で近似

物を <strong>箱</strong>とみなして <strong>水面と箱の、交差から沈んだ体積</strong>を求めます。

```cpp
// 箱（軸に沿った、水平な箱とみなす）の、沈んだ高さから、体積を求める。
float SubmergedVolume(float box_bottom_y, float box_height, float width, float depth, float water_y) {
  const float submerged_h = std::clamp(water_y - box_bottom_y, 0.0f, box_height);
  return submerged_h * width * depth;
}
```

波の高さが <strong>箱の下で均一でない</strong>ので箱を、<strong>水平方向にいくつかのマスに分けて</strong>、マスごとに水面の高さを調べると傾いた、水面にも対応できます。

### ③ 三角形ごと（Kerner の方法）

船体を <strong>三角形のメッシュ</strong>として、扱います。<strong>水面の下にある三角形</strong>をすべて集め、各三角形に次の力をかけます。

| 力 | 計算 |
| --- | --- |
| 静水圧（浮力） | `ρ g × (水面からの深さ) × 面積 × (−法線)`。深い所ほど強く法線の向きに押す |
| 粘性抵抗 | 三角形の位置での、水に対する相対速度に比例した、摩擦 |
| 圧力抗力 | 進行方向を向く、三角形が水を押しのける力 |
| スラミング | 面が水面へ、勢いよく入ったときの衝撃 |

三角形ごとの静水圧を足し合わせると、<strong>浮力と船体の傾きを戻そうとする力（復元力）</strong>が、<strong>自然に</strong>出ます。点サンプリングより重いですが、船の揺れがはるかにもっともらしくなります（Kerner、2015）。

## 抵抗で安定させる

浮力だけだと物は <strong>上下に跳ね続けます</strong>。<strong>抵抗</strong>（速度に比例して動きを遅くする力）を加えて揺れを、収束させます。

```cpp
// 水の中の物には、速度に比例した、抵抗をかける。沈んでいる割合に応じて、強くする。
float3 drag = -body.velocity * linear_drag * submerged_ratio;
float3 angular_drag = -body.angular_velocity * angular_drag_coeff * submerged_ratio;
body.ApplyForce(drag);
body.ApplyTorque(angular_drag);
```

| 抵抗 | 効果 |
| --- | --- |
| 小さい | いつまでもゆらゆら揺れる |
| 大きい | すぐに止まる。重たい動きにくい物に見える |

## 水面に反作用を返す

物が水を押しのけると <strong>波</strong>が出ます。物の <strong>速さと水面への侵入量</strong>に応じて波紋を、起こします（[Writing Object Contacts](contact.md)）。

| 状況 | 起こす波 |
| --- | --- |
| 物が水面に落ちる | 落ちた位置に強い、1 回の波紋（スプラッシュ） |
| 物が水面を進む | 進む軌跡に、連続した弱い波紋（航跡） |
| 物が浮いて揺れる | 揺れの、強さに応じた小さな波紋 |

## 注意点

| 項目 | 内容 |
| --- | --- |
| 物理エンジンとの連携 | 浮力は、物理エンジンの外力として毎ステップ、かける（`ApplyForceAtPoint`） |
| 固定ステップ | 浮力の計算は、物理の固定ステップで行う。フレームレートに依存させない |
| 水面の高さの取得 | GPU と、同じ波の式。時間をそろえる（[Floating Objects](../waves/floating.md)） |
| 発振 | 浮力が強い質量が軽い、ステップが粗いと物理が不安定になる。抵抗で抑える |
| 水の流れ | 川では流れの速度を、水の速度として相対速度に使う。物が流される |

## よくあるミス

??? failure "物が、水の上で跳ね続ける"
    <strong>ダンピング</strong>を<strong>加える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 沈んだ体積に応じた力で浮かせる

## 参考

- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015
- Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）
- Catto, "Understanding Constraints" など、Box2D / 物理エンジンの、固定ステップのドキュメント

## 関連ページ

- [Water Interaction](index.md)
- [Floating Objects](../waves/floating.md)

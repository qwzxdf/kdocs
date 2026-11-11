---
title: Buoyancy and Reaction
tags:
  - 描画
---

# Buoyancy and Reaction

水に箱を落とすと少し沈んで跳ね返って、揺れながら浮かびます。この動きを作るには水面の高さを見て、物に上向きの力を加える必要があります。ところが、力を加えるだけだと物はいつまでも上下に揺れ続けます。さらに、物が水を押しのけると水の側にも波が立ちます。

<strong>水と物の相互作用は 2 方向です</strong>。水から物へは浮力、抵抗、波に押される力が働きます。物から水へは押しのけた水が波紋や航跡になります。このページでは浮力の式、沈んだ体積の近似、抵抗で揺れを収める方法（シミュレーションで測った周期と収まる時間つき）、水面への反作用、物理エンジンとの連携の注意を説明します。

!!! tip "ポイント"
    - 浮力は水に沈んだ体積に比例した上向きの力です（`ρ g V`）。重力と釣り合う深さで止まります。
    - 物体の数点で水面を調べて、点ごとに力を加えると傾きを戻す力も出ます。
    - 抵抗がないと揺れは収まりません。抵抗は沈んでいる割合に応じて、強くします。
    - 小さな揺れの周期は `2π sqrt(m / (ρ g A))` で、測った値と一致しました。
    - 物が水を押す反作用は高さマップに波紋として書き込みます。

!!! info "このページを読む前に"
    - [Water Interaction](index.md)（このセクション全体の地図と、読む順番）

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
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">箱の密度が水の 0.6 倍だとする<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">沈めるほど、押し返す力が増える<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3197;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">浮力 &lt; 重さ: まだ沈む<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.6397;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深さ 0.6 で浮力 = 重さ → 釣り合って止まる(緑の丸)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:buoyancy-draft:end -->

## 浮力の物理 {#physics}

アルキメデスの原理で物は押しのけた水の重さだけ上向きの力を受けます。

```text
F_buoyancy = ρ × g × V_submerged             ρ: 水の密度（1000 kg/m³）、V: 水に沈んでいる体積
```

沈んでいる体積が小さいうちは浮力が小さくて、物は重力で沈みます。沈む体積が増えると浮力も増えて、重力と釣り合う深さで止まります。完全に沈むと浮力が最大の `ρ g V` になります。物の重さがこれより軽ければ浮き上がります。

重力と釣り合う深さ（喫水）は水平な箱なら質量 `m`、底面積 `A` で `m / (ρ A)` です。質量 600 kg、底面積 1 m² の箱なら `600 / (1000 × 1) = 0.6 m` です。物の密度が水より小さいと一部が水面の上に出て、浮きます。

## 沈んだ体積を近似する {#volume}

正確な沈んだ体積の計算は水面の高さと物の形状の交差が必要で、重くなります。実用的な近似が 3 つあります。

### 点サンプリング

物の複数の点（浮力点）で水面の高さを調べて、各点が受け持つ体積の沈んだ割合を浮力に変えます（[Floating Objects](../waves/floating.md)）。簡単で傾きを戻す力も点の位置の違いから出ます。

### 箱で近似

物を箱とみなして水面と箱の交差から沈んだ体積を求めます。

```cpp
// 箱（軸に沿った水平な箱とみなす）の、沈んだ高さから体積を求める（コンパイルしていない）
float SubmergedVolume(float box_bottom_y, float box_height, float width, float depth, float water_y) {
  const float submerged_h = std::clamp(water_y - box_bottom_y, 0.0f, box_height);
  return submerged_h * width * depth;
}
```

波の高さが箱の下で均一でないので、箱を水平方向にいくつかのマスに分けて、マスごとに水面の高さを調べると、傾いた水面にも対応できます。

### 三角形ごと（Kerner の方法）

船体を三角形のメッシュとして扱います。水面の下にある三角形を集めて、各三角形に次の力をかけます。このページでは Kerner の記事を読んでいないので、内容は一般的な説明にとどめます。

- 静水圧（浮力）は `ρ g × (水面からの深さ) × 面積 × (−法線)` で深い所ほど強く、法線の向きに押します。
- 粘性抵抗は三角形の位置での水に対する相対速度に比例した摩擦です。
- 圧力抗力は進行方向を向く三角形が、水を押しのける力です。
- スラミングは面が水面へ勢いよく入ったときの衝撃です。

三角形ごとの静水圧を足し合わせると浮力と船体の傾きを戻そうとする力（復元力）が自然に出ます。点サンプリングより重いですが、船の揺れがもっともらしくなります。

## 抵抗で安定させる {#drag}

浮力だけだと物は上下に跳ね続けます。小さな揺れの周期は浮力がばねのように働くことから決まります。ばね定数は `k = ρ g A` で周期は次のとおりです。

<div class="formula">T = 2π · sqrt( m / (ρ g A) )</div>

質量 600 kg、底面積 1 m² なら `T = 2π × sqrt(600 / 9810) ≒ 1.554 s` です。抵抗（速度に比例して動きを遅くする力）を加えて、揺れを収束させます。次のシミュレーションで確かめました。

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

// 水平な箱（幅 w × 奥行き d × 高さ h）の上下運動だけを、半陰的オイラー法で解く。
// 浮力 = ρ g × 沈んだ体積、抵抗 = -c v × 沈んだ割合。水面は y = 0。
struct Result { double period; double draft; double settle_time; bool exploded; };

Result Simulate(double mass, double linear_drag, double dt, double t_end) {
  const double rho = 1000.0, g = 9.81, w = 1.0, d = 1.0, h = 10.0;
  double y = -mass / (rho * w * d) + 0.1;    // 釣り合いの位置から 10 cm 持ち上げて放す（小さな振動にする）
  double v = 0.0;
  const double equilibrium = mass / (rho * w * d);       // 釣り合う喫水（箱の底が -喫水）
  Result r{0, equilibrium, -1, false};
  double prev_v = 0, last_cross = -1;
  std::vector<double> periods;
  for (double t = 0; t < t_end; t += dt) {
    const double submerged_h = std::clamp(-y, 0.0, h);    // 沈んだ高さ
    const double submerged_ratio = submerged_h / h;
    const double buoyancy = rho * g * submerged_h * w * d;
    const double drag = -linear_drag * v * submerged_ratio;
    const double a = (buoyancy + drag - mass * g) / mass;
    v += a * dt;                                          // 半陰的オイラー: 先に速度を更新して
    y += v * dt;                                          // 更新した速度で位置を進める
    if (!std::isfinite(y) || std::fabs(y) > 1e6) { r.exploded = true; break; }
    // 速度が負から正へ変わる時刻（振動の最下点）の間隔を周期とする
    if (prev_v < 0 && v >= 0) {
      if (last_cross >= 0) periods.push_back(t - last_cross);
      last_cross = t;
    }
    prev_v = v;
    if (r.settle_time < 0 && std::fabs(-y - equilibrium) < 0.01 * equilibrium && std::fabs(v) < 0.01) r.settle_time = t;
  }
  if (!periods.empty()) r.period = periods[0];
  return r;
}
```

箱の高さを 10 m にして、完全に沈む場合の頭打ちを避けています。MSVC（`/W4`）でコンパイルして実行しました。質量 600 kg で 60 fps（`dt = 1/60`）で、60 秒間を調べた結果は次のとおりです。

- 抵抗 0 のとき周期は 1.550 秒で、理論の 1.554 秒と一致しました。60 秒たっても収まりません。
- 抵抗 200 のときも周期は 1.550 秒で、60 秒では収まりませんでした。
- 抵抗 1000 のとき約 55 秒で、喫水の誤差 1 % 以内に収まりました。
- 抵抗 3000 のとき約 18.5 秒で収まりました。

抵抗に「沈んだ割合」を掛けているので、実効的な抵抗は数字よりずっと小さくなります（ここでは、箱の高さ 10 m に対して、沈んだ割合は約 0.06 です）。抵抗が小さいといつまでも揺れて、大きいとすぐに止まって重くて動きにくい物に見えます。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="抵抗の大きさごとの、揺れが収まるまでの時間。0 と 200 は 60 秒で収まらず、1000 で 55 秒、3000 で 18.5 秒"><text x="14" y="22" class="fig-title">抵抗と、揺れが収まるまでの時間（質量 600 kg、実測）</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="100" y="40" width="90" height="160" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="250" y="40" width="90" height="160" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="400" y="52" width="90" height="148" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="550" y="150" width="90" height="50" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="145" y="34">60 秒でも未収束</text><text x="295" y="34">60 秒でも未収束</text><text x="445" y="46">約 55 秒</text><text x="595" y="144">約 18.5 秒</text>
<text x="145" y="220">抵抗 0</text><text x="295" y="220">200</text><text x="445" y="220">1000</text><text x="595" y="220">3000</text></g>
<text x="360" y="244" text-anchor="middle" style="font-size:12px">周期はどれも 1.550 秒（理論 1.554 秒）。抵抗は、周期ではなく、収まる速さを決める</text></svg>

水中の物には速度に比例した抵抗をかけます。沈んでいる割合に応じて強くします。

```cpp
// （コンパイルしていない）水の中の物に、速度に比例した抵抗をかける。沈んだ割合で強くする
float3 drag = -body.velocity * linear_drag * submerged_ratio;
float3 angular_drag = -body.angular_velocity * angular_drag_coeff * submerged_ratio;
body.ApplyForce(drag);
body.ApplyTorque(angular_drag);
```

## 水面に反作用を返す {#reaction}

物が水を押しのけると波が出ます。物の速さと水面への侵入量に応じて、波紋を起こします（[Writing Object Contacts](contact.md)）。

- 物が水面に落ちたら落ちた位置に強い 1 回の波紋（スプラッシュ）を作ります。
- 物が水面を進んだら軌跡に連続した弱い波紋（航跡）を作ります。
- 物が浮いて揺れたら揺れの強さに応じた小さな波紋を作ります。

## 物理エンジンとの連携 {#engine}

浮力は物理エンジンの外力として、毎ステップかけます（`ApplyForceAtPoint`）。浮力の計算は物理の固定ステップで行います。フレームレートに依存させません。水面の高さは GPU と同じ波の式で求めて、時間をそろえます（[Floating Objects](../waves/floating.md)）。

浮力が強くて質量が軽くステップが粗いと物理が不安定になります。ばねの角周波数は `ω = sqrt(ρ g A / m)` で陽的な時間積分は、おおよそ `ω · dt < 2` が安定の目安です。たとえば、質量 2 kg、底面積 1 m² なら `ω = 70 rad/s` で、60 fps（`dt = 1/60`）では `ω · dt = 1.17` ですが、質量 0.5 kg なら `ω · dt = 2.33` で、目安を超えます。上のシミュレーションでは箱が水面から出ると力が 0 になるので、発散せずに頭打ちになりました。実際の物理エンジンでは軽い物はステップを細かくするか抵抗で抑えます。

川では流れの速度を水の速度として、相対速度に使います。物が流されます。

!!! note "確かめた範囲"
    C++ のシミュレーションは、MSVC（`/W4`）でコンパイルして実行しました。周期と収まる時間はその実行結果です。箱の上下運動 1 次元だけで、傾きや点サンプリングは調べていません。`ω · dt` の目安は一般的なもので発散は再現していません。三角形ごとの方法は Kerner の記事を読んでいません。GPU での描画は確認していません。

## よくあるミス {#mistakes}

??? failure "物が水の上で跳ね続ける"
    原因は抵抗（ダンピング）がないことです。浮力はばねのように働くので抵抗がないと揺れが収まりません。速度に比例する抵抗を沈んでいる割合に応じて加えます。

??? failure "浮力が、フレームレートで変わる"
    原因は浮力を描画のフレームごとにかけていることです。物理の固定ステップで毎ステップかけます。

??? failure "軽い物が、水面で暴れて飛んでいく"
    原因は `ω · dt` が大きすぎることです。軽い物はばねが強く効くのでステップを細かくするか抵抗を強めます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 浮力は `ρ g V` で、重力と釣り合う喫水で止まります。600 kg、1 m² の箱なら 0.6 m です。
    - [x] 抵抗がないと揺れが収まりません。小さな揺れの周期は `2π sqrt(m / (ρ g A))` です。
    - [x] 物の押しのけは波紋として、高さマップに書き込みます。
    - [x] 浮力は物理の固定ステップで、毎ステップかけます。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は自分で書いた C++ のシミュレーションの実測と式からの計算です。

- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015
- Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と波頭の折れ）
- Catto, "Understanding Constraints" など、Box2D / 物理エンジンの固定ステップのドキュメント

## 関連ページ

- [Water Interaction](index.md)
- [Floating Objects](../waves/floating.md)

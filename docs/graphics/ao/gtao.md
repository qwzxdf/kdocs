---
title: GTAO
tags:
  - 描画
---

# GTAO

<strong>GTAO</strong>（Ground Truth Ambient Occlusion）は、2016 年に Jimenez らが発表した方式です。「<strong>正解（グラウンド トゥルース）に近い AO をリアルタイムで</strong>」を目指し、これまでの SSAO が省略していた、コサイン重みを正しく積分しました。HBAO と同じ「地平線を探す」考え方ですが積分の内側を解析的に解く式を導き、少ない方向数でレイトレース AO に近い結果を出します。さらにマルチ バウンスの近似・ベント法線・スペキュラ遮蔽も同じ枠組みで扱います。

!!! tip "ポイント"
    - 画素ごとに<strong>1〜数本の「スライス」</strong>（視線を含む平面）を取り、<strong>各スライスで両側の地平線 h1・h2</strong>を探す。
    - <strong>コサイン重み付きの積分を、閉じた式</strong>で解く：<strong>`â(h1, h2, γ)`</strong>。<strong>γ はスライスに投影した法線の角度</strong>。
    - <strong>面の表側（法線を中心とした半円）に、地平線を丸める</strong>（クランプ）。
    - <strong>投影した法線の長さ</strong>が、スライスの重み（外側の積分）。
    - <strong>時間方向</strong>にスライスの向きを回して、<strong>少ない方向数でも</strong>収束させる。
    - <strong>マルチ バウンス</strong>（間接光の回り込み）の近似、<strong>ベント法線</strong>、<strong>スペキュラ遮蔽</strong>が付く。

## HBAO からの改良

HBAO と GTAO は、どちらも「地平線を探す」方式ですが、積分の扱いが違います。HBAO は<strong>立体角の割合</strong>を積分し、コサイン重みを省略していました。GTAO はコサイン重みを含めて、正しい AO の積分を行います。そのため、スライスごとに法線をスライス平面へ<strong>投影</strong>し、投影された法線の長さを、そのスライスの重みにします。

内側の積分も違います。HBAO は `sin h − sin t` でしたが、GTAO は、コサイン重みを含めた<strong>閉じた式</strong> `â(h1, h2, γ)` を使います。地平線の探し方も、HBAO は片側に歩くだけですが、GTAO は両側（±）に歩いて、h1 と h2 の 2 つを求めます。さらに GTAO は、マルチ バウンスの近似、ベント法線、スペキュラ遮蔽を同じ枠組みで扱い、薄い物体のための簡単なヒューリスティックも持っています。

!!! info "ここで使われる「積分」を、やさしく言うと"
    GTAO も、HBAO と同じく、<strong>断面ごとに、仰角（地平線）を 2 つ探して、見えている割合を、式で出す</strong>方式です。違いは、<strong>足すときの重み</strong>です。

    - AO では、真上に近い方向ほど、重く足す（コサイン重み）のが正しい。
    - HBAO は、この重みを、省略した式を使っていた。
    - GTAO は、コサイン重みも含めて、<strong>正確に積分した式</strong>（下の `â`）を使う。

    断面の中で、方向を刻まずに済むのは、コサインの積分が、サインや、コサインの式に、なるからです。仰角が 2 つ分かれば、式 1 回で、答えが出ます。断面を何枚も、平均するのは、HBAO と同じです。

    <strong>数式を使わない、くわしい説明</strong>は [Integrals and Elevation Angles in Plain Words](theory/integral-intuition.md) です。

## 理論：スライスに分けた積分

[理論](theory/index.md)の AO は次の積分でした。

<div class="formula">AO = (1/π) ∫_{Ω} V(ω) (n·ω) dω</div>

GTAO は<strong>視線ベクトル v を含む平面（スライス）</strong>に半球を分けます。スライスの向きを φ（0〜π）で表します。<strong>各スライスの中で仰角の積分を解析的に</strong>行い、<strong>φ について積分</strong>します。

<div class="formula">AO(x) = (1/π) ∫₀^π ∫_{−π/2}^{π/2} V(φ, θ) · |sin θ| · cos(…)  dθ dφ　→　(1/π) ∫₀^π ‖n_p‖ · â(h₁(φ), h₂(φ), γ(φ)) dφ</div>

| 記号 | 意味 |
| --- | --- |
| v | 視線ベクトル（画素から、カメラへ向かう単位ベクトル） |
| φ | スライスの向き（画面上の方向の角度） |
| n_p | 法線 n をスライスの平面に投影したベクトル。‖n_p‖ はその長さ |
| γ | 視線 v と投影した法線 n_p の間の角度 |
| h₁, h₂ | スライスの中での両側の地平線の角度（v を基準に測る。h₁ は負側、h₂ は正側） |
| <strong>â(h₁, h₂, γ)</strong> | スライス内のコサイン重み付き可視性（閉じた式） |

<strong>ポイント</strong>：`‖n_p‖ â(…)` は、<strong>1 つのスライスが、AO に寄与する量</strong>です。法線がスライス平面から外を向いている（`‖n_p‖` が小さい）スライスは寄与が小さくなります。この重みがコサイン重みを正しく反映しています。

<!-- fig:gtao-visibility:begin -->

<svg class="fig illust motion" data-fig="gtao-visibility" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gtao-visibility" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">GTAO の可視性: 1 つの断面で、地平線の角度 h1・h2 から、cos 重み付きの「見える割合」を、式で一発で求める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">面の法線が、視線方向から n だけ傾いている。地平線の角度(h1 = 左、h2 = 右)を、式と、細かい数値積分で比べる</text>
<rect x="30" y="96" width="700" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 見える割合 V(h1 = h2 = h、法線の傾き n = 0°, 25°, 50°)</text>
<path d="M70.0,350.0 L80.67,349.84 L91.33,349.37 L102.0,348.58 L112.67,347.49 L123.33,346.08 L134.0,344.37 L144.67,342.36 L155.33,340.06 L166.0,337.47 L176.67,334.59 L187.33,331.45 L198.0,328.04 L208.67,324.37 L219.33,320.46 L230.0,316.32 L240.67,311.95 L251.33,307.37 L262.0,302.6 L272.67,297.63 L283.33,292.5 L294.0,287.21 L304.67,281.77 L315.33,276.21 L326.0,270.54 L336.67,264.76 L347.33,258.91 L358.0,252.99 L368.67,247.02 L379.33,241.02 L390.0,235.0 L400.67,228.98 L411.33,222.98 L422.0,217.01 L432.67,211.09 L443.33,205.24 L454.0,199.46 L464.67,193.79 L475.33,188.23 L486.0,182.79 L496.67,177.5 L507.33,172.37 L518.0,167.4 L528.67,162.63 L539.33,158.05 L550.0,153.68 L560.67,149.54 L571.33,145.63 L582.0,141.96 L592.67,138.55 L603.33,135.41 L614.0,132.53 L624.67,129.94 L635.33,127.64 L646.0,125.63 L656.67,123.92 L667.33,122.51 L678.0,121.42 L688.67,120.63 L699.33,120.16 L710.0,120.0" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<text x="705.9999999999999" y="112.0" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">n = 0°<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,350.0 L80.67,349.86 L91.33,349.43 L102.0,348.72 L112.67,347.72 L123.33,346.45 L134.0,344.9 L144.67,343.08 L155.33,340.99 L166.0,338.64 L176.67,336.04 L187.33,333.19 L198.0,330.09 L208.67,326.77 L219.33,323.23 L230.0,319.47 L240.67,315.52 L251.33,311.37 L262.0,307.04 L272.67,302.54 L283.33,297.89 L294.0,293.09 L304.67,288.17 L315.33,283.13 L326.0,277.98 L336.67,272.75 L347.33,267.44 L358.0,262.08 L368.67,256.67 L379.33,251.23 L390.0,245.77 L400.67,240.32 L411.33,234.88 L422.0,229.47 L432.67,224.1 L443.33,218.8 L454.0,213.57 L464.67,208.42 L475.33,203.38 L486.0,198.46 L496.67,193.66 L507.33,189.01 L518.0,184.51 L528.67,180.18 L539.33,176.0 L550.0,171.88 L560.67,167.8 L571.33,163.79 L582.0,159.85 L592.67,155.98 L603.33,152.2 L614.0,148.51 L624.67,144.91 L635.33,141.42 L646.0,138.04 L656.67,134.77 L667.33,131.62 L678.0,128.6 L688.67,125.71 L699.33,122.96 L710.0,120.34" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;1.0000" values="0;0;1;1"/></path>
<text x="705.9999999999999" y="112.34297856058319" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">n = 25°<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,350.0 L80.67,349.9 L91.33,349.6 L102.0,349.09 L112.67,348.38 L123.33,347.48 L134.0,346.38 L144.67,345.09 L155.33,343.61 L166.0,341.94 L176.67,340.1 L187.33,338.07 L198.0,335.88 L208.67,333.53 L219.33,331.01 L230.0,328.35 L240.67,325.54 L251.33,322.6 L262.0,319.53 L272.67,316.34 L283.33,313.04 L294.0,309.64 L304.67,306.15 L315.33,302.57 L326.0,298.92 L336.67,295.21 L347.33,291.45 L358.0,287.64 L368.67,283.71 L379.33,279.66 L390.0,275.48 L400.67,271.18 L411.33,266.76 L422.0,262.24 L432.67,257.61 L443.33,252.88 L454.0,248.06 L464.67,243.16 L475.33,238.19 L486.0,233.14 L496.67,228.03 L507.33,222.87 L518.0,217.67 L528.67,212.42 L539.33,207.15 L550.0,201.85 L560.67,196.54 L571.33,191.22 L582.0,185.91 L592.67,180.6 L603.33,175.32 L614.0,170.06 L624.67,164.84 L635.33,159.67 L646.0,154.54 L656.67,149.47 L667.33,144.47 L678.0,139.55 L688.67,134.7 L699.33,129.94 L710.0,125.28" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/></path>
<text x="705.9999999999999" y="117.28136271515862" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">n = 50°<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/></text>
<text x="70.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0°</text>
<text x="283.3333333333333" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">30°</text>
<text x="496.66666666666663" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">60°</text>
<text x="710.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">90°</text>
<text x="710.0" y="366" text-anchor="end" style="font-size:11px;font-weight:500;fill:#64748b">地平線の角度 h(法線から測る)</text>
<circle cx="496.67" cy="177.5" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="0;0;1;1"/></circle>
<circle cx="496.67" cy="193.66" r="6" fill="#e5aa28" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;1.0000" values="0;0;1;1"/></circle>
<circle cx="496.67" cy="228.03" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3776;0.3778;1.0000" values="0;0;1;1"/></circle>
<rect x="750" y="96" width="180" height="280" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="750" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">h = 60° のとき</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="0;0;1;1"/><text x="766" y="150" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">n = 0°</text>
<text x="766" y="178" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043">V = 0.750</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;1.0000" values="0;0;1;1"/><text x="766" y="220" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">n = 25°</text>
<text x="766" y="248" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5aa28">V = 0.680</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3776;0.3778;1.0000" values="0;0;1;1"/><text x="766" y="290" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">n = 50°</text>
<text x="766" y="318" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d">V = 0.530</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">式の読み込み回数(地平線を探した後):</text>
<text x="40" y="438" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb" opacity="0">式は 1 回(三角関数のみ)。数値積分なら、角度を 4000 等分(= 4000 回)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;1.0000" values="0;0;1;1"/></text>
<text x="340" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="340" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4,000<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="340" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5109;0.5111;1.0000" values="0;0;1;1"/><rect x="40" y="456" width="880" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="480" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1e3a8a">全方向が空(h = 90°、n = 0)で V = 1.00、完全にふさがる(h = 0)と V = 0。法線が傾くほど、見える割合は、変わる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">断面で、見える角度の範囲(地平線)が決まる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">cos 重みの積分は、閉じた式になるので、数値積分が要らない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.5109;0.5111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">式 1 回で、見える割合が決まる(GTAO の核心)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5109;0.5111;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gtao-visibility:end -->

### 内側の積分の式

地平線 h₁・h₂ が<strong>法線を中心にした、cos の半円</strong>にクランプされたあとの、スライス内の可視性は、次の式です。

<div class="formula">â(h₁, h₂, γ) = ¼ ( −cos(2h₁ − γ) + cos γ + 2 h₁ sin γ ) + ¼ ( −cos(2h₂ − γ) + cos γ + 2 h₂ sin γ )</div>

| 項 | 意味 |
| --- | --- |
| h₁・h₂ | 地平線の角度（v からの角度） |
| γ | 法線の方向（v からの角度） |
| <strong>cos(2h − γ)</strong> | コサイン重みを角度で積分した結果に現れる項 |

この式は、「<strong>h から法線の方向まで、`cos(角度 − γ)` を積分する</strong>」ことを`∫ cos x · …` として解いたものです。<strong>サンプルで数える代わりに、地平線 2 つの角度を入れるだけで、積分が出る</strong>のが、GTAO の核心です。

### 地平線のクランプ

<strong>法線から ±90 度</strong>より外は、<strong>コサイン重みが 0</strong>（面の裏側）です。地平線が法線の半円の外に出ないように、丸めます。

<div class="formula">h₁ ← γ + max(h₁ − γ, −π/2)、　h₂ ← γ + min(h₂ − γ, +π/2)</div>

## 地平線の探し方

各スライスで、両側（＋方向と −方向）に深度バッファを歩きます。角度をそのまま測らず「コサイン」で扱うと、`acos` を毎ステップ呼ばずに済み、計算が安く済みます。

手順は次のとおりです。まず、φ から画面上の方向 `dir` を決めます（ビュー空間では `(dir, 0)`）。次に、`+dir` と `−dir` の両側に数ステップ（8〜12）歩きます。ステップ幅は、半径を画面の大きさに直して、ステップ数で割った値です。遠いほど幅を広げる（べき乗で間隔を取る）と、近くのサンプルが密になり、近い遮蔽物をよく拾えます。各サンプルの位置 S について、視線ベクトル v との角度の cos を `dot(normalize(S − P), v)` で求めます。地平線の cos を、この値の<strong>最大</strong>（角度が最小、つまり最も高く見える遮蔽）で更新します。最後に、`h₁ = −acos(cos₁)`、`h₂ = acos(cos₂)` で角度に戻します。

距離の減衰は、地平線の cos を、遠いサンプルほど −1（遮蔽なし）に近づける形で入れます。遠い遮蔽物が、地平線を押し上げる力が弱まる、ということです。

```hlsl
float falloff = saturate((radius_dist - dist) * falloff_mul + falloff_add);
horizon_cos = max(horizon_cos, lerp(low_horizon_cos, shc, falloff));
```

## 1 つのスライスの計算

```hlsl
float SliceVisibility(float3 p, float3 v, float3 n, float2 dir, float2 h_cos) {
  float3 dir3 = float3(dir.x, -dir.y, 0.0);
  float3 axis = normalize(cross(dir3, v));
  float3 ortho_dir = dir3 - dot(dir3, v) * v;

  float3 proj_n = n - axis * dot(n, axis);
  float proj_n_len = length(proj_n);
  float cos_n = saturate(dot(proj_n, v) / max(proj_n_len, 1e-5));
  float n_angle = -sign(dot(proj_n, ortho_dir)) * acos(cos_n);

  float h1 = -acos(clamp(h_cos.x, -1.0, 1.0));
  float h2 = acos(clamp(h_cos.y, -1.0, 1.0));

  h1 = n_angle + max(h1 - n_angle, -1.5707963);
  h2 = n_angle + min(h2 - n_angle, 1.5707963);

  float sin_n = sin(n_angle);
  float v1 = (cos_n + 2.0 * h1 * sin_n - cos(2.0 * h1 - n_angle));
  float v2 = (cos_n + 2.0 * h2 * sin_n - cos(2.0 * h2 - n_angle));
  return proj_n_len * (v1 + v2) * 0.25;
}
```

| 点 | 説明 |
| --- | --- |
| `axis` | スライス平面の法線（`dir` と `v` の外積） |
| `proj_n` | 法線をスライス平面に投影（`axis` 成分を引く） |
| `n_angle` | `v` と `proj_n` の間の角度（符号つき） |
| クランプ | 地平線を法線の ±90 度に丸める |
| 戻り値 | `‖proj_n‖ · â(h₁, h₂, n_angle)`。スライスごとの可視性 |

<strong>最終的な AO は、スライスの可視性の平均</strong>です。

<div class="formula">visibility = (1 / スライス数) · Σ SliceVisibility</div>

!!! note "実装の参考"
    Intel の <strong>XeGTAO</strong>（GameTechDev/XeGTAO）は、GTAO の実装を、<strong>HLSL の完全なコード</strong>として公開しています。パラメータの意味・ノイズ・時間蓄積・ベント法線まで含んでおり、自分で実装する際の最もよい参考資料です。

## スライスの数とノイズ

画素あたりのスライス数は、1〜2 本です（リアルタイムでは、これが限界です）。これでどうやって収束させるのでしょうか。答えは、<strong>空間と時間の両方に分散させる</strong>ことです。

画素ごとにスライスの向きを変え、空間的にノイズに変えます（4×4 や IGN など。[Noise Patterns](filtering/noise-pattern.md)）。さらに、フレームごとにスライスの向きを回して、時間的にも別の向きを見ます。ステップの位置にもジッターを足します。そして、バイラテラル ブラーと時間蓄積で、これらのノイズを平均します。実質、毎画素で数十本のスライスを使ったのと同じ結果になります。

GTAO が実用的な速さで動くのは、この<strong>時間蓄積</strong>のおかげです。1 フレームの結果は非常に粗いものですが、数フレームを重ねるときれいになります（[Temporal Accumulation](filtering/temporal.md)）。

## 薄い物体への対策

スクリーン空間では、手前の物体の「厚み」が分かりません。深度バッファが示すのは、面の手前側だけです。薄い柱の後ろにある面は、柱が無限に厚いとみなされ、必要以上に暗くなります（[Screen Edges and Thin Objects](artifacts/edge-thin.md)）。

GTAO の論文は、簡単なヒューリスティックを提案しています。「物体は手前の面から、奥へ一定の厚みしかない」と仮定して、<strong>遠い遮蔽物による地平線の更新を弱める</strong>方法です。これで、薄い物の後ろが暗くなりすぎるのを防げます。ほかの選択肢は、距離の減衰を強めに掛けること、あるいは（高コストですが）手前の面とその裏の面の 2 枚の深度を持つことです。実装は XeGTAO などを参照してください。

## マルチ バウンス：回り込みの近似

AO は、「<strong>遮蔽された方向は、真っ暗</strong>」と考えます。しかし、現実には<strong>遮蔽物の表面で光が反射して、そこそこ明るい</strong>です（間接光の、2 回目以降の反射＝マルチ バウンス）。明るい色の部屋の隅が真っ黒になるのは、不自然です。

GTAO は<strong>アルベドに応じて、AO の値を明るく戻す</strong>、<strong>簡単な近似式</strong>を提案しています。

<div class="formula">A_mb = max( A , ((A · a + b) · A + c) · A )　、　a = 2.0404·ρ − 0.3324、　b = −4.7951·ρ + 0.6417、　c = 2.7552·ρ + 0.6903</div>

| 記号 | 意味 |
| --- | --- |
| A | もとの AO（0〜1） |
| ρ | 表面のアルベド（0〜1、通常はグレースケール化したもの） |
| A_mb | マルチ バウンスを考慮した AO |

```hlsl
float3 MultiBounce(float ao, float3 albedo) {
  float3 a = 2.0404 * albedo - 0.3324;
  float3 b = -4.7951 * albedo + 0.6417;
  float3 c = 2.7552 * albedo + 0.6903;
  return max(ao, ((ao * a + b) * ao + c) * ao);
}
```

<strong>明るい色</strong>（ρ が大きい）ほど、<strong>AO が持ち上がり</strong>、暗い色ではほぼそのままです。色ごと（RGB）に計算すると赤い壁の隅が赤く照らされる効果も出ます。

## ベント法線とスペキュラ遮蔽

### ベント法線

可視な範囲の平均の方向を、<strong>ベント法線</strong>（bent normal）と呼びます。普通の法線は面が向いている方向ですが、ベント法線は<strong>空が見えている方向</strong>を向きます。

拡散の環境光（IBL）では、法線の代わりにベント法線で環境マップを引くと、遮られた方向の光を拾わなくなります。また、スペキュラ遮蔽では、可視円錐の向きとして使います。GTAO では、スライスごとの可視な範囲の中心から、ベント法線を作れます。

### スペキュラ遮蔽

AO は拡散（ざらっとした反射）に掛けるものです。鏡面反射にも遮蔽があります。隅の見えないはずの所に、環境マップの反射が見えてしまう破綻です。これを<strong>スペキュラ遮蔽</strong>で弱めます。

厳密には、可視円錐（AO の大きさとベント法線の向きで決まる）と、反射の円錐（粗さと反射方向で決まる）が、どれだけ重なるかを求めます。簡易な近似として、AO・粗さ・`n·v` から直接求める式があります。

```hlsl
float SpecularOcclusion(float n_dot_v, float ao, float roughness) {
  return saturate(pow(n_dot_v + ao, exp2(-16.0 * roughness - 1.0)) - 1.0 + ao);
}
```

粗さが低い（鏡面に近い）ほど AO の影響を弱くし、粗いほど AO に近づけます。Lagarde による、広く使われている近似です。

## GTAO の位置づけ

精度の面では、コサイン重みが正確で積分が解析的なので、レイトレース AO に近い結果が出ます。コストは、スライス 1〜2 本 × 両側のステップ 8〜12 で、時間蓄積が前提です。入力は深度と（あれば）法線で、深度から復元もできます。マルチ バウンス・ベント法線・スペキュラ遮蔽も付いてきます。実装は XeGTAO が公開されており、主要なエンジンが GTAO 系を採用または提供しています。

## 弱点

スクリーン空間の限界（画面外・隠れた物・薄い物）は残り、薄い物はヒューリスティックで軽減するだけです。ノイズと時間蓄積に依存するので、動きの速い場面ではゴースト（残像）やちらつきが出ることがあります。角度・クランプ・符号の管理が細かく、実装は複雑です。画素 × スライス × 両側のステップという、ステップのコストもかかります。

## より良いやり方

GTAO を超える精度が必要なら、レイトレース AO に切り替えます（[RTAO](world-space/rtao.md)）。ハードウェアのレイトレーシングが使える環境では、画面外や薄い物の問題が根本的に消えます。そうでない環境では、GTAO を基本として、画面に映らない大きな遮蔽は、距離場 AO や、焼き込んだ AO で補うのが現実的です（[World-Space AO Comparison](world-space/comparison.md)）。

## よくあるミス

??? failure "地平線のクランプを忘れて、面の裏側の遮蔽が効く"
    `h₁, h₂` を法線の ±90 度に丸めます。

??? failure "法線をスライスに投影せず、重みを掛けない"
    `‖n_p‖`（投影した法線の長さ）が、スライスの重みです。

??? failure "1 フレームの結果をそのまま使って、ノイズだらけ"
    <strong>ブラーと時間蓄積</strong>が前提です（[フィルタ](filtering/index.md)）。

??? failure "マルチ バウンスを、グレーのアルベドで色付きの壁に掛けて、色味が失われる"
    <strong>色ごと（RGB）</strong>に計算すると色の回り込みが出ます。

??? failure "スペキュラ遮蔽を入れず、隅に環境マップの反射が、まぶしく映る"
    スペキュラ遮蔽を足します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GTAO ＝ <strong>コサイン重みを正しく積分する、地平線ベースの AO</strong>
    - [x] <strong>スライスごとに、両側の地平線 h₁・h₂ を探し</strong>、<strong>`‖n_p‖ · â(h₁, h₂, γ)`</strong> を平均
    - [x] <strong>地平線を法線の ±90 度にクランプ</strong>。内側の積分は<strong>閉じた式</strong>
    - [x] <strong>時間・空間でスライスの向きを変え</strong>、ブラーと時間蓄積で収束
    - [x] <strong>マルチ バウンス・ベント法線・スペキュラ遮蔽</strong>も扱える

## 参考

- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Intel, XeGTAO（GitHub: GameTechDev/XeGTAO、GTAO の、HLSL 実装）
- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（スペキュラ オクルージョン）

## 関連ページ

- [Ambient Occlusion (AO)](index.md)
- [HBAO](hbao.md)
- [AO Filtering](filtering/index.md)
- [AO Comparison](comparison.md)
- [PBR](../../3d/pbr.md)

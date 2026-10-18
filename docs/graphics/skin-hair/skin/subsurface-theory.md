---
title: Subsurface Scattering
tags:
  - 描画
---

# Subsurface Scattering

<strong>次表面散乱</strong>（Subsurface Scattering、SSS）は光が物体の内部に入り散らばり <strong>入った点とは別の点から出てくる</strong>現象です。肌・大理石・ろうそく・牛乳・葉・ジェイドなど半透明の物体で起きます。ふつうの BRDF は「光は入った点から出る」と仮定しますが、SSS はその仮定を外します。このページでは SSS を表す BSSRDF という考え方と現実的な計算の基になる拡散近似と双極子モデルを、順に説明します。

!!! tip "ポイント"
    - BRDF は「入る点＝出る点」。BSSRDF は「入る点と出る点が違ってよい」。
    - 内部の光は何度も散乱して拡散する。拡散近似なら出る点と入る点の距離 r だけの関数 R(r) で書ける。
    - R(r) を<strong>拡散プロファイル</strong>と呼ぶ。中心が高くすそ野が長い形。色ごとに違う（赤が最も広い）。
    - 双極子モデル（Jensen 2001）が、実用の出発点。吸収係数と散乱係数から R(r) を計算できる。
    - リアルタイムでは R(r) をガウスの和で近似して、ぼかしで実装する。

## BRDF から BSSRDF へ

まず、ふつうの反射の式を思い出します。ある点 x に入る光 L_i(ω_i) が、BRDF f_r で反射されて、視線方向 ω_o に出ていきます。

<div class="formula">L_o(x, ω_o) = ∫ f_r(ω_i, ω_o) · L_i(x, ω_i) · (n·ω_i) dω_i</div>

この式では <strong>入る点も出る点も x</strong> です。SSS を扱うにはこれを拡張します。入る点 x_i と出る点 x_o を別にして、<strong>表面全体で足し合わせます</strong>。

<div class="formula">L_o(x_o, ω_o) = ∫_A ∫_Ω S(x_i, ω_i; x_o, ω_o) · L_i(x_i, ω_i) · (n·ω_i) dω_i dA(x_i)</div>

この S を <strong>BSSRDF</strong>（Bidirectional Scattering-Surface Reflectance Distribution Function、双方向散乱面反射率分布関数）と呼びます。式の意味は「面上のあらゆる点 x_i に入った光が、x_o からどれだけ出てくるか」を全部足し合わせるということです。BRDF は 4 次元の関数ですが、BSSRDF は 8 次元（入る点 2 + 出る点 2 + 入る向き 2 + 出る向き 2）で、そのまま扱うのは現実的ではありません。そこで、単純化が必要になります。

<!-- fig:sss-spread:begin -->

<svg class="fig illust motion" data-fig="sss-spread" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sss-spread" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">光が入った点から、どこまでに何 % が出てくるか</text>
<rect x="70" y="70" width="640" height="260" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="330" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="135.0" x2="710" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="330" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="200.0" x2="710" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="330" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="265.0" x2="710" y2="265.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">出てきた光の割合（累積）</text>
<text x="710" y="368" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">入った点からの距離 (mm)</text>
<text x="176.67" y="348" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<text x="283.33" y="348" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2</text>
<text x="390.0" y="348" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">3</text>
<text x="496.67" y="348" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<text x="603.33" y="348" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">5</text>
<path d="M70.0,330.0 L78.0,306.25 L86.0,271.55 L94.0,253.58 L102.0,242.73 L110.0,233.04 L118.0,224.11 L126.0,215.99 L134.0,208.56 L142.0,201.64 L150.0,195.12 L158.0,188.93 L166.0,183.05 L174.0,177.45 L182.0,172.11 L190.0,167.01 L198.0,162.13 L206.0,157.45 L214.0,152.94 L222.0,148.6 L230.0,144.42 L238.0,140.4 L246.0,136.53 L254.0,132.8 L262.0,129.23 L270.0,125.8 L278.0,122.52 L286.0,119.39 L294.0,116.4 L302.0,113.55 L310.0,110.84 L318.0,108.26 L326.0,105.83 L334.0,103.52 L342.0,101.34 L350.0,99.29 L358.0,97.35 L366.0,95.54 L374.0,93.84 L382.0,92.25 L390.0,90.76 L398.0,89.37 L406.0,88.08 L414.0,86.88 L422.0,85.76 L430.0,84.72 L438.0,83.76 L446.0,82.87 L454.0,82.05 L462.0,81.28 L470.0,80.57 L478.0,79.91 L486.0,79.3 L494.0,78.74 L502.0,78.22 L510.0,77.73 L518.0,77.27 L526.0,76.85 L534.0,76.46 L542.0,76.09 L550.0,75.75 L558.0,75.42 L566.0,75.12 L574.0,74.84 L582.0,74.57 L590.0,74.32 L598.0,74.08 L606.0,73.85 L614.0,73.64 L622.0,73.44 L630.0,73.25 L638.0,73.07 L646.0,72.9 L654.0,72.73 L662.0,72.58 L670.0,72.43 L678.0,72.29 L686.0,72.16 L694.0,72.03 L702.0,71.91 L710.0,71.8" fill="none" stroke="#e5484d" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;1.0000" values="0;0;1;1"/></path>
<text x="699.33" y="94" text-anchor="end" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">赤<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,330.0 L78.0,282.22 L86.0,210.93 L94.0,171.78 L102.0,147.75 L110.0,128.4 L118.0,113.25 L126.0,102.1 L134.0,94.05 L142.0,88.16 L150.0,83.71 L158.0,80.29 L166.0,77.66 L174.0,75.66 L182.0,74.18 L190.0,73.1 L198.0,72.33 L206.0,71.79 L214.0,71.42 L222.0,71.15 L230.0,70.97 L238.0,70.83 L246.0,70.73 L254.0,70.64 L262.0,70.57 L270.0,70.52 L278.0,70.47 L286.0,70.42 L294.0,70.38 L302.0,70.35 L310.0,70.31 L318.0,70.28 L326.0,70.26 L334.0,70.23 L342.0,70.21 L350.0,70.19 L358.0,70.17 L366.0,70.15 L374.0,70.14 L382.0,70.12 L390.0,70.11 L398.0,70.1 L406.0,70.09 L414.0,70.08 L422.0,70.07 L430.0,70.06 L438.0,70.05 L446.0,70.05 L454.0,70.04 L462.0,70.03 L470.0,70.03 L478.0,70.03 L486.0,70.02 L494.0,70.02 L502.0,70.02 L510.0,70.01 L518.0,70.01 L526.0,70.01 L534.0,70.01 L542.0,70.01 L550.0,70.01 L558.0,70.01 L566.0,70.0 L574.0,70.0 L582.0,70.0 L590.0,70.0 L598.0,70.0 L606.0,70.0 L614.0,70.0 L622.0,70.0 L630.0,70.0 L638.0,70.0 L646.0,70.0 L654.0,70.0 L662.0,70.0 L670.0,70.0 L678.0,70.0 L686.0,70.0 L694.0,70.0 L702.0,70.0 L710.0,70.0" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;1.0000" values="0;0;1;1"/></path>
<text x="699.33" y="112" text-anchor="end" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">緑<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,330.0 L78.0,264.94 L86.0,171.77 L94.0,127.99 L102.0,107.13 L110.0,92.53 L118.0,82.56 L126.0,76.61 L134.0,73.49 L142.0,72.03 L150.0,71.38 L158.0,71.08 L166.0,70.91 L174.0,70.79 L182.0,70.69 L190.0,70.6 L198.0,70.51 L206.0,70.43 L214.0,70.36 L222.0,70.3 L230.0,70.25 L238.0,70.2 L246.0,70.16 L254.0,70.13 L262.0,70.1 L270.0,70.08 L278.0,70.06 L286.0,70.05 L294.0,70.04 L302.0,70.03 L310.0,70.02 L318.0,70.02 L326.0,70.01 L334.0,70.01 L342.0,70.01 L350.0,70.0 L358.0,70.0 L366.0,70.0 L374.0,70.0 L382.0,70.0 L390.0,70.0 L398.0,70.0 L406.0,70.0 L414.0,70.0 L422.0,70.0 L430.0,70.0 L438.0,70.0 L446.0,70.0 L454.0,70.0 L462.0,70.0 L470.0,70.0 L478.0,70.0 L486.0,70.0 L494.0,70.0 L502.0,70.0 L510.0,70.0 L518.0,70.0 L526.0,70.0 L534.0,70.0 L542.0,70.0 L550.0,70.0 L558.0,70.0 L566.0,70.0 L574.0,70.0 L582.0,70.0 L590.0,70.0 L598.0,70.0 L606.0,70.0 L614.0,70.0 L622.0,70.0 L630.0,70.0 L638.0,70.0 L646.0,70.0 L654.0,70.0 L662.0,70.0 L670.0,70.0 L678.0,70.0 L686.0,70.0 L694.0,70.0 L702.0,70.0 L710.0,70.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/></path>
<text x="699.33" y="130" text-anchor="end" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">青<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/></text>
<text x="390" y="372" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が当たった点から、肌の内側に広がる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="390" y="372" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">青: 0.5 mm ほどで、ほぼ出きる（狭い）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2797;0.2800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="372" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">緑: 1〜2 mm まで広がる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;0.4797;0.4800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="372" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">赤: 数 mm まで届く。だから、影の縁が赤く染まる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sss-spread:end -->

## 拡散近似

肌のような<strong>散乱が強い物質</strong>では光は内部で何十回も散乱するので、<strong>どの方向から入った光も内部ではほぼ等方（どの向きにも均等）に広がります</strong>。この性質を利用すると BSSRDF が劇的に単純になります。

散乱が強い媒質では光のエネルギーの流れは、熱の拡散と同じ<strong>拡散方程式</strong>で近似できます。熱を板の 1 点に当てると同心円状に広がっていく様子と同じです。拡散近似の下では入る向きと出る向きの依存が単純になり（フレネルの透過だけが残る）、BSSRDF は次の形にまとまります。

<div class="formula">S(x_i, ω_i; x_o, ω_o) = (1/π) · F_t(η, ω_i) · R_d(‖x_i − x_o‖) · F_t(η, ω_o)</div>

F_t はフレネルの透過率（表面を通り抜ける割合）で、R_d(r) が<strong>拡散プロファイル</strong>（diffusion profile）です。r は入る点と出る点の距離です。つまり、<strong>入る点と出る点の距離 r だけが、散らばりの大きさを決めます</strong>。向きの依存は表面でのフレネルの項だけに任せればよいのです。

これにより次の考え方が使えます。ある点 x_o の SSS の光は「周りの点 x_i に入った光」を <strong>距離に応じた重み R_d(r) を掛けて足し合わせたもの</strong>です。これは <strong>画像のぼかし（畳み込み）そのもの</strong>です。ライティングの結果の画像を R_d(r) の形のカーネルでぼかせば、SSS の結果が得られます。画面空間の SSS がぼかしだけで実装できる理由は、ここにあります。

## 双極子モデル

R_d(r) の具体的な形を物質の性質から計算する方法が、Jensen らの<strong>双極子モデル</strong>（dipole model、SIGGRAPH 2001）です。考え方は「物質の内部に光の点光源を置いたときその光がどう広がるか」を境界条件を満たすように 2 つの点光源（双極子）で表すことです。

物質は 2 つの係数で特徴づけられます。<strong>吸収係数 σ_a</strong>（単位長さあたりに光が吸収される割合）と <strong>換算散乱係数 σ_s'</strong>（単位長さあたりに光が散乱される割合、方向の偏りを補正したもの）です。これらは RGB ごとに値が違います。ここから次の量が決まります。

<div class="formula">σ_t' = σ_a + σ_s'　　α' = σ_s' / σ_t'　　σ_tr = √(3 σ_a σ_t')</div>

σ_t' は換算消散係数、α' は換算アルベド（1 に近いほど散乱が強い）、σ_tr は有効消散係数で拡散の減衰の速さを表します。さらに、光源の深さを決めます。

<div class="formula">z_r = 1 / σ_t'　　z_v = z_r + 4AD　　D = 1/(3σ_t')　　A = (1 + F_dr)/(1 − F_dr)</div>

z_r は表面の内側にある実の点光源の深さ z_v は表面の外側にある仮想の（負の）点光源の高さです。A は境界での内部反射を表す係数で、F_dr はフレネルの拡散反射率です。これらから拡散プロファイルは次の式になります。

<div class="formula">R_d(r) = (α'/4π) · [ z_r (σ_tr d_r + 1) e^(−σ_tr d_r) / d_r³ + z_v (σ_tr d_v + 1) e^(−σ_tr d_v) / d_v³ ]　　d_r = √(r² + z_r²)、d_v = √(r² + z_v²)</div>

式は複雑ですが形はシンプルです。r が小さいところで高く r が大きくなるにつれて、<strong>指数関数的に減る</strong>曲線です。ただし、中心付近は 1/d³ 的に鋭く尖り遠くは e^(−σ_tr d) でゆっくり裾を引く、<strong>二つの性質を併せ持ちます</strong>。この「鋭い中心」と「長い裾」が、肌の柔らかさを作ります。

## 色ごとの違い

R_d(r) は RGB で別々の曲線になります。肌ではσ_a が赤で小さく（赤は吸収されにくい）、青で大きいためσ_tr は赤で小さく、青で大きくなります。その結果、<strong>赤の R_d(r) は幅が広く、青は狭く</strong>なります。典型的な値で赤は数 mm、緑は 1 mm 前後、青は 0.5 mm 程度まで広がります。

この色ごとの違いが影の縁の赤みを作ります。同じ点光源の光をぼかしたとき赤が広く、青が狭ければ中心から離れた位置では赤だけが残ります。

!!! note "Jensen の論文について"
    Jensen らの 2001 年の論文は、実測した大理石・肌・牛乳などの散乱係数も載せています。この論文で SSS が実用的な計算になり映画の『ゴラム』（ロード・オブ・ザ・リング）などで使われました。リアルタイムではこの R_d(r) を <strong>ガウスの和</strong>や事前積分の LUT で近似します。

## リアルタイムでの考え方

リアルタイムでは双極子の式を毎フレーム、画素ごとに計算することはできません。そこで、次の流れで実装します。

R_d(r) をあらかじめ（オフラインで）計算しておきます。その曲線を <strong>数個のガウス関数の和</strong>で近似します（[Diffusion Profiles](diffusion-profile.md)）。ガウスはぼかしの計算が速く（分離可能で、段階的に重ねられる）、実装が簡単だからです。あるいは画面空間で 1 回のぼかしにまとめた<strong>カーネル</strong>を使います（[Separable SSS](screen-space-sss.md)）。あるいはさらに単純化して曲率と N·L だけで決まる LUT にします（[Pre-Integrated Skin Shading](pre-integrated.md)）。

## 拡散プロファイルを数値で扱う

### 距離ごとの光の広がり

皮膚に細い光を当てたとき入った点から、距離 `r` だけ離れた場所にどれだけの光が出てくるかを <strong>拡散プロファイル</strong> `R(r)` と呼びます。赤・緑・青で広がり方が違います（赤が、最も遠くまで届く）。

```text
R(r) ≈ Σ w_i · G(r, v_i)      （ガウス関数 G の、重み付きの和で近似する）
```

d'Eon と Luebke（2007）は、皮膚の `R(r)` を <strong>6 つのガウス</strong>の和で、よく近似できることを示しました。ガウスは重ね合わせてもガウスのままなので、画像のぼかしとして実装できます。

```hlsl
// 分散 v のガウス関数（2D）。距離 r での重み。
float Gaussian(float v, float r) {
  return exp(-r * r / (2.0 * v)) / (2.0 * 3.14159265 * v);
}

// 赤・緑・青ごとに、重みと分散を持つ、6 ガウスの拡散プロファイル（d'Eon と Luebke の皮膚の値、単位: mm²）。
float3 DiffusionProfile(float r) {
  return float3(0.233, 0.455, 0.649) * Gaussian(0.0064, r)
       + float3(0.100, 0.336, 0.344) * Gaussian(0.0484, r)
       + float3(0.118, 0.198, 0.000) * Gaussian(0.1870, r)
       + float3(0.113, 0.007, 0.007) * Gaussian(0.5670, r)
       + float3(0.358, 0.004, 0.000) * Gaussian(1.9900, r)
       + float3(0.078, 0.000, 0.000) * Gaussian(7.4100, r);
}
```

分散が大きいガウスほど遠くまで光が届きます。赤の成分だけが大きなガウス（分散 1.99、7.41）に重みを持つので皮膚の「赤み」が、光の当たる場所からにじみ出るように広がります。

### 正規化：エネルギーを保つ

```hlsl
// 重みの合計が 1（各色）になるよう、割る。そうしないと、ぼかしただけで、明るさが変わってしまう。
float3 total = float3(0.233 + 0.100 + 0.118 + 0.113 + 0.358 + 0.078,
                      0.455 + 0.336 + 0.198 + 0.007 + 0.004,
                      0.649 + 0.344 + 0.007);
float3 normalized_weight = weight / total;
```

拡散プロファイルは広がる前後で、光の総量を変えない（吸収は別に扱う）ので、積分が 1 になるよう正規化します。

### リアルタイムでの使い方

ガウスは <strong>水平方向のぼかしと垂直方向のぼかし</strong>に分けられます（分離可能）。6 つのガウスを画面空間のぼかしとして、順に適用し足し合わせるのが d'Eon と Luebke のテクスチャ空間 SSS です。Jimenez ら（2015）は 1 つの分離可能なカーネルで、プロファイル全体を近似し 1 回の水平・垂直のぼかしで済ませました（[Screen-Space SSS](screen-space-sss.md)）。

## よくあるミス

??? failure "SSS をただの半透明（アルファ ブレンド）で表そうとする"
    半透明ブレンドは背後の物を透かすだけで、<strong>内部で光が広がる</strong>現象を表せない。SSS は <strong>拡散反射の光を周りの画素へ広げる</strong>処理。

??? failure "距離 r を画面上の画素の距離で測る"
    r は<strong>物体の表面上の実際の距離</strong>（mm 単位）。画面上の画素の距離はカメラからの距離で変わるので、<strong>深度で補正して</strong>、画素の間隔を実際の長さに直す。

??? failure "RGB を同じカーネルでぼかす"
    <strong>赤・緑・青で広がりが違う</strong>ことが、SSS の見た目の核心。色ごとに別の重みを使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] BSSRDF は<strong>入る点と出る点が違う</strong>。拡散近似なら距離 r の関数 R_d(r) だけ
    - [x] R_d(r) は<strong>中心が尖り裾が長い</strong>。赤が最も広い
    - [x] 双極子モデルは吸収と散乱の係数から R_d(r) を計算する
    - [x] リアルタイムでは<strong>ガウスの和（ぼかし）</strong>か<strong>LUT</strong>で近似する

## 参考

- Jensen, Marschner, Levoy, Hanrahan, "A Practical Model for Subsurface Light Transport"（SIGGRAPH 2001）
- Donner, Jensen, "Light Diffusion in Multi-Layered Translucent Materials"（SIGGRAPH 2005）
- d'Eon, Irving, "A Quantized-Diffusion Model for Rendering Translucent Materials"（SIGGRAPH 2011）

## 関連ページ

- [Skin Overview](index.md)
- [Diffusion Profiles](diffusion-profile.md)
- [Separable SSS](screen-space-sss.md)
- [Pre-Integrated Skin Shading](pre-integrated.md)

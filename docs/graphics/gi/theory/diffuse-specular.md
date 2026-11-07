---
title: Diffuse and Specular
tags:
  - 描画
---

# Diffuse and Specular

つるつるの金属球は周りの景色をくっきり映します。マットな石膏の球は周りの景色を映さずぼんやりと明るいだけです。同じ「周りから来る光」でも面の性質で見え方がまるで違います。間接光を 1 つの手法で全部まかなおうとすると、石膏には細かすぎ金属には粗すぎる情報を扱うことになります。そこで、間接光を拡散と鏡面に分けてそれぞれに向く手法を使います。このページでは拡散がなぜ低周波で、鏡面がなぜ高周波なのかを数字で確かめ 2 つを合成するシェーダーを 1 本にまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。split-sum や SH の式は、記憶に基づく標準的な形で今回は元の論文・発表を読んで確かめていません。余弦ローブのエネルギー配分と GGX の幅は、自分で積分して出した数字です。

!!! tip "ポイント"
    - 拡散の間接光は次数 2 までの球面調和（9 係数）で、余弦ローブのエネルギーの 99.29% を表せます。
    - 鏡面の反射ローブは粗さ 0.1 で半幅 0.74°、0.3 で 6.67°、0.5 で 19.13°、0.7 で 42.42° と粗さとともに急に広がります。
    - 拡散の割合は鏡面で反射した分を引きます。誘電体（F0 = 0.04）は `N·V` が 0.2 で拡散が 0.645 に減ります。
    - 手法の分担は拡散はライトマップ・プローブ・SSGI・DDGI、鏡面は反射プローブ・SSR・レイトレです。

!!! info "このページを読む前に"
    - [GI Theory](index.md)（このセクション全体の地図と読む順番）
    - [Irradiance](irradiance.md)（拡散の放射照度）

## なぜ分けるのか {#why}

BRDF を拡散と鏡面に分けると、間接光の性質が別物だと分かります。

| | 拡散 | 鏡面 |
| --- | --- | --- |
| 反射の広がり | 全方向に均等 | 反射方向のまわりだけ |
| 間接光の見え方 | なめらか（低周波） | 鋭い（高周波） |
| 視点への依存 | なし | あり |
| 必要な情報 | 法線ごとに 1 つの値 | 反射方向の細かい景色 |

## 拡散：低周波であること {#diffuse}

### 式で見る {#diffuse-math}

ランバート面の BRDF は `albedo / π` の定数です。法線 `n` の面が受ける放射照度 `E(n)` は、周りの光 `L(ω)` に法線との余弦 `max(n·ω, 0)` を掛けて、半球で積分したものです。余弦は法線の向きで最大で真横で 0 になるなだらかな山です。この山で周りの光を畳み込むので、光の細かい模様は平均されて消えます。

### どれだけ低周波か {#diffuse-numbers}

余弦ローブ `max(x, 0)`（`x` は `cos θ`）をルジャンドル多項式で展開して、次数 `l` ごとのエネルギーを数えました。全体のエネルギーは `∫ max(x,0)² dx = 1/3` で直接の積分と各次数の和が一致することを確かめています。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="余弦ローブの次数別エネルギー"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">余弦ローブの次数別エネルギー</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><rect x="100" y="131.2" width="46" height="118.8" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="123" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">l=0</text><text x="123" y="125.25" text-anchor="middle" style="font-size:11px;font-weight:700">37.5%</text><rect x="166" y="91.7" width="46" height="158.3" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="189" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">l=1</text><text x="189" y="85.66349999999997" text-anchor="middle" style="font-size:11px;font-weight:700">50.0%</text><rect x="232" y="212.9" width="46" height="37.1" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="255" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">l=2</text><text x="255" y="206.893" text-anchor="middle" style="font-size:11px;font-weight:700">11.7%</text><rect x="298" y="250.0" width="46" height="0.0" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="321" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">l=3</text><text x="321" y="244.0" text-anchor="middle" style="font-size:11px;font-weight:700">0.0%</text><rect x="364" y="248.1" width="46" height="1.9" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="387" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">l=4</text><text x="387" y="242.1475" text-anchor="middle" style="font-size:11px;font-weight:700">0.6%</text><rect x="430" y="250.0" width="46" height="0.0" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="453" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">l=5</text><text x="453" y="244.0" text-anchor="middle" style="font-size:11px;font-weight:700">0.0%</text><rect x="496" y="249.6" width="46" height="0.4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="519" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">l=6</text><text x="519" y="243.62" text-anchor="middle" style="font-size:11px;font-weight:700">0.1%</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="190.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">20</text><text x="62" y="127.33333333333333" text-anchor="end" style="font-size:11px;font-weight:400">40</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">60</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">球面調和の次数 l</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">余弦ローブのエネルギーの割合（%）</text><text x="564" y="84" text-anchor="end" style="font-size:12px;font-weight:700">l ≤ 2 の合計 99.29%</text></svg>

- 次数 0: エネルギー 0.12500（全体の 37.5%）
- 次数 1: 0.16667（50.0%）
- 次数 2: 0.03906（11.7%）
- 次数 3: 0
- 次数 4: 0.00195（0.6%）
- 次数 6: 0.00040（0.1%）

次数 2 までの累積は 99.29%、次数 4 までで 99.88% です。次数 2 までは係数が 1 + 3 + 5 = 9 個なので、**9 個の SH 係数で余弦ローブのほぼ全てを表せます**。奇数の次数（3、5）が 0 になるのは余弦ローブが `x ≥ 0` の半分だけを持つ形だからです。

つまり、拡散の間接光は粗いデータ（プローブ 1 個の SH9、小さな放射照度キューブ、ライトマップ）で足ります。放射照度キューブなら 32²×6 面の RGBA16F が 48 KiB で、SH9 の RGB は 108 バイトです。

## 鏡面：高周波であること {#specular}

### ローブの幅 {#lobe}

鏡面反射の BRDF は反射方向のまわりに山を持ちます。GGX の法線分布 `D(θ) = α² / (π (cos²θ (α² − 1) + 1)²)`（`α = roughness²`）が、最大値の半分になるハーフベクトルの角度は、`cos²θ = (1 − √2 α²) / (1 − α²)` から求まります。反射方向の広がりはハーフベクトルの 2 倍です。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="GGX ローブの幅"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">GGX ローブの幅</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="75.0,250.0 80.0,250.0 85.0,249.9 90.0,249.9 95.0,249.8 100.0,249.7 105.0,249.6 110.0,249.5 115.0,249.4 120.0,249.2 125.0,249.1 130.0,248.9 135.0,248.7 140.0,248.5 145.0,248.2 150.0,248.0 155.0,247.7 160.0,247.5 165.0,247.2 170.0,246.9 175.0,246.6 180.0,246.2 185.0,245.9 190.0,245.5 195.0,245.1 200.0,244.7 205.0,244.3 210.0,243.9 215.0,243.4 220.0,243.0 225.0,242.5 230.0,242.0 235.0,241.5 240.0,240.9 245.0,240.4 250.0,239.8 255.0,239.2 260.0,238.6 265.0,238.0 270.0,237.4 275.0,236.7 280.0,236.0 285.0,235.3 290.0,234.6 295.0,233.9 300.0,233.1 305.0,232.3 310.0,231.5 315.0,230.7 320.0,229.8 325.0,228.9 330.0,228.0 335.0,227.1 340.0,226.1 345.0,225.1 350.0,224.1 355.0,223.0 360.0,221.9 365.0,220.8 370.0,219.6 375.0,218.4 380.0,217.2 385.0,215.9 390.0,214.5 395.0,213.1 400.0,211.7 405.0,210.2 410.0,208.6 415.0,207.0 420.0,205.2 425.0,203.4 430.0,201.5 435.0,199.5 440.0,197.4 445.0,195.2 450.0,192.8 455.0,190.3 460.0,187.6 465.0,184.7 470.0,181.6 475.0,178.2 480.0,174.5 485.0,170.4 490.0,165.9 495.0,160.8 500.0,155.0 505.0,148.3 510.0,140.3 515.0,130.4 520.0,117.5 525.0,98.1 530.0,60.0 535.0,60.0 540.0,60.0 545.0,60.0 550.0,60.0 555.0,60.0 560.0,60.0 565.0,60.0"/><circle cx="120.0" cy="249.2" r="4" fill="#4c8bf5"/><text x="112.0" y="241.2188888888889" text-anchor="end" style="font-size:11px;font-weight:700">0.74°</text><circle cx="220.0" cy="243.0" r="4" fill="#4c8bf5"/><text x="212.0" y="234.95944444444444" text-anchor="end" style="font-size:11px;font-weight:700">6.67°</text><circle cx="320.0" cy="229.8" r="4" fill="#4c8bf5"/><text x="312.0" y="221.8072222222222" text-anchor="end" style="font-size:11px;font-weight:700">19.13°</text><circle cx="420.0" cy="205.2" r="4" fill="#4c8bf5"/><text x="412.0" y="197.22333333333333" text-anchor="end" style="font-size:11px;font-weight:700">42.42°</text><line x1="70" y1="186.66666666666666" x2="570" y2="186.66666666666666" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="74" y="180.66666666666666" text-anchor="start" style="font-size:11px;font-weight:400">拡散と同じ広さに近づく目安</text><text x="70" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.25</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="570" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">45</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">90</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">135</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">180</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">粗さ（roughness）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">反射ローブの半値半幅（度、GGX）</text></svg>

- 粗さ 0.05: ハーフベクトル 0.09°、反射の半幅 0.18°
- 0.10: 0.37°、0.74°
- 0.20: 1.48°、2.95°
- 0.30: 3.33°、6.67°
- 0.50: 9.57°、19.13°
- 0.70: 21.21°、42.42°
- 1.00: `D` が一定で、半分に落ちない（全方向）

粗さ 0.05 は半幅 0.18° のほぼ 1 点です。窓や建物の模様がはっきり映ります。粗さ 0.5 でも半幅 19° と拡散（全半球）よりずっと狭いです。粗さ 0.7 で半幅 42° まで広がると、拡散に近づきます。反射ローブの広がりは粗さの 2 乗の `α` でさらに加速的に変わります。

### 粗さの境目 {#boundary}

粗い鏡面は広いローブで低周波になるので、拡散と同じデータで近似できます。つるつるの鏡面は反射の手法が必要です。境目は粗さ 0.5〜0.6 あたりに置くのが一般的です。この値は経験的な目安でこのページで導いたものではありません。

## 手法の分担 {#roles}

<svg class="fig flow" viewBox="0 0 660 310" role="img" aria-label="間接光の分担"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">間接光の分担</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">間接光の分担</text><rect x="20" y="50" width="300" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="170.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">拡散：低周波・視点に依らない</text><rect x="340" y="50" width="300" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="490.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">鏡面：高周波・視点に依存</text><rect x="20" y="120" width="300" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="170.0" y="140.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ライトマップ・プローブ（SH）</text><rect x="20" y="174" width="300" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="170.0" y="194.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">SSGI・DDGI・ボクセル</text><rect x="20" y="228" width="300" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="170.0" y="248.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">Lumen（拡散と粗い鏡面）</text><rect x="340" y="120" width="300" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="490.0" y="140.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">反射プローブ・平面反射</text><rect x="340" y="174" width="300" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="490.0" y="194.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">SSR</text><rect x="340" y="228" width="300" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="490.0" y="248.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">レイトレ反射</text><text x="330" y="296" text-anchor="middle" style="font-size:12px;font-weight:400">粗さ 0.5〜0.6 あたりで、鏡面を拡散側の手法に任せる境目を置くことが多い（目安）</text></svg>

| 手法 | 拡散 | 鏡面 |
| --- | --- | --- |
| ライトマップ | ○（焼き込み） | ×（反射プローブで別に） |
| プローブ GI（SH） | ○ | ×（SH は鏡面に不向き） |
| SSGI | ○ | △（粗い鏡面） |
| DDGI | ○ | ×（拡散のみ） |
| レイトレーシング | ○ | ○ |
| Lumen | ○ | ○（粗い鏡面まで） |

SH が鏡面に向かない理由は次数 2 までの 9 係数では、粗さ 0.5 の反射ローブ（半幅 19°）も表せないからです。

## 合成するコード {#compose}

ここからコードを数行ずつ見ます。最初は定数と読み取る資源です。

```hlsl
// ---- 間接光の合成：拡散（SH）と鏡面（split-sum）（左手系・Y 上。リニア空間）----

cbuffer IblCB : register(b0) {
  float3 gCameraPos;       // カメラ位置（ワールド）
  float  gEnvMipCount;     // 環境キューブのミップ数。256² なら 9
  float4 gSh[9];           // 放射照度の SH9（rgb。w は未使用）。cos 畳み込み済み、PI で割った後の値
};

TextureCube<float3> gEnvSpecular : register(t0);   // 粗さごとにぼかした環境キューブ（プレフィルタ済み）
Texture2D<float2>   gBrdfLut     : register(t1);   // split-sum の 2 係数（x: スケール、y: バイアス）。横 N·V、縦 粗さ
SamplerState gLinearClamp : register(s0);          // 線形・クランプ
```

`gSh` は放射照度の SH9 で、余弦畳み込み済みのものを渡します。`gEnvSpecular` は粗さごとにぼかした環境キューブ（ミップチェーン）、`gBrdfLut` は split-sum の 2 係数を入れた小さなテクスチャ（32×32 の RG16F で 4 KiB）です。

SH から放射照度を求める関数です。

```hlsl
// 法線 n の方向の放射照度を、SH9 から評価する（係数は cos 畳み込み済みと仮定）。
float3 EvalSh9(float3 n) {
  // 実数球面調和の基底（定数は標準の値）。l = 0, 1, 2 の 9 項。
  float basis[9];
  basis[0] = 0.282095;                                  // Y00
  basis[1] = 0.488603 * n.y;                            // Y1-1
  basis[2] = 0.488603 * n.z;                            // Y10
  basis[3] = 0.488603 * n.x;                            // Y11
  basis[4] = 1.092548 * n.x * n.y;                      // Y2-2
  basis[5] = 1.092548 * n.y * n.z;                      // Y2-1
  basis[6] = 0.315392 * (3.0 * n.z * n.z - 1.0);        // Y20
  basis[7] = 1.092548 * n.x * n.z;                      // Y21
  basis[8] = 0.546274 * (n.x * n.x - n.y * n.y);        // Y22
  float3 sum = 0.0;                                     // 9 項の和
  for (int i = 0; i < 9; ++i) sum += gSh[i].rgb * basis[i];
  return max(sum, 0.0);                                 // 負になる誤差を切る（足した）
}
```

球面調和の基底は `l = 0, 1, 2` の 9 項です。係数は標準の値です（今回は導出や出典で確かめていません）。9 項の係数を掛けて足すだけなので、安い計算です。最後の `max(sum, 0)` は足した処理で展開の誤差で値が負になるのを切ります。

粗さを考えたフレネルです。

```hlsl
// 粗さを考えたフレネル（Lagarde & de Rousiers の形）。粗い面ほど縁の反射を抑える。
float3 FresnelSchlickRoughness(float n_dot_v, float3 f0, float roughness) {
  float3 grazing = max(float3(1.0 - roughness, 1.0 - roughness, 1.0 - roughness), f0);   // 縁での上限
  return f0 + (grazing - f0) * pow(1.0 - saturate(n_dot_v), 5.0);
}
```

粗い面は縁でも反射が 1 まで上がりません。`grazing` は縁での上限を `1 − roughness` にしたものです。シュリック近似の `F0 + (1 − F0)(1 − N·V)⁵` で誘電体（`F0 = 0.04`）の反射を `N·V` ごとに数えると、1.0 で 0.040、0.5 で 0.070、0.2 で 0.355、0.1 で 0.607、0.0 で 1.000 です。正面ではほぼ全部が拡散で縁へ行くほど鏡面に移ります。

合成です。

```hlsl
// 間接光の合成。albedo はリニア、metallic は 0〜1、ao は 0〜1。
float3 IndirectLighting(float3 world_pos, float3 n, float3 albedo, float metallic, float roughness, float ao) {
  float3 v = normalize(gCameraPos - world_pos);          // 視線
  float n_dot_v = saturate(dot(n, v));                   // 法線と視線の cos
  float3 r = reflect(-v, n);                             // 反射ベクトル（鏡面で使う）

  float3 f0 = lerp(float3(0.04, 0.04, 0.04), albedo, metallic);   // 誘電体は 0.04、金属は albedo
  float3 f = FresnelSchlickRoughness(n_dot_v, f0, roughness);     // 鏡面で反射する割合

  // 拡散：法線だけで決まる。albedo を掛ける。反射した割合 f と金属の分は引く。
  float3 irradiance = EvalSh9(n);                        // 低周波なので SH 9 項で十分
  float3 kd = (1.0 - f) * (1.0 - metallic);              // 中に入って散乱する割合
  float3 diffuse = kd * albedo * irradiance;

  // 鏡面：反射方向の環境を、粗さに応じたミップで読み、split-sum の係数を掛ける。
  float mip = roughness * (gEnvMipCount - 1.0);          // 粗いほど深いミップ（ぼけた環境）
  float3 prefiltered = gEnvSpecular.SampleLevel(gLinearClamp, r, mip);
  float2 brdf = gBrdfLut.SampleLevel(gLinearClamp, float2(n_dot_v, roughness), 0);
  float3 specular = prefiltered * (f0 * brdf.x + brdf.y);

  return (diffuse + specular) * ao;                      // 間接光は AO で暗くする
}
```

拡散は `kd × albedo × irradiance` です。`kd = (1 − F) × (1 − metallic)` で鏡面で反射した割合 `F` と金属が拡散を持たない分を引きます（エネルギー保存）。`N·V` が 0.2 では `kd` は 0.645 です。鏡面は反射ベクトルで環境キューブを読み `mip = roughness × (ミップ数 − 1)` でぼけた環境を選び split-sum の 2 係数で `F0 × x + y` を掛けます。環境キューブ 256² のミップ全部は、RGBA16F で 4.00 MiB です。最後に、間接光に AO を掛けます。

## 注意：鏡面にも AO がいる {#ao}

拡散だけでなく鏡面の間接光も遮蔽される場所で暗くします。ただし、鏡面は視線の向きで遮蔽が変わるので、拡散と同じ AO をそのまま掛けると不自然です（[Application Mistakes](../../ao/artifacts/application-mistakes.md)）。このコードは簡単のために同じ AO を掛けていますが、スペキュラ遮蔽を使うほうが適しています。

## よくあるミス {#mistakes}

??? failure "鏡面の反射を GI の手法で出そうとして、ぼやける"
    原因は鏡面の間接光を拡散向けのプローブ（SH）で出そうとしていることです。SH9 では粗さ 0.5 の反射ローブ（半幅 19°）も表せません。鏡面は反射の手法（反射プローブ、SSR、レイトレ）で扱います。

??? failure "金属に拡散が残って、ぼんやり明るい"
    原因は `(1 − metallic)` を掛けていないことです。金属は光を吸収して拡散を持たないので、`kd` を 0 にします。

??? failure "拡散と鏡面の合計が、入ってくる光より明るい"
    原因は `kd` から `F` を引いていないことです。鏡面で反射した分は拡散に回りません。

??? failure "縁だけ不自然に白く光る"
    原因は粗い面に粗さを考えないフレネルを使っていることです。粗さを考えた形（`grazing = max(1 − roughness, F0)`）にします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 拡散は低周波。余弦ローブは次数 2（9 係数）で 99.29%
    - [x] 鏡面は高周波。GGX の反射ローブの半幅は粗さ 0.1 で 0.74°、0.5 で 19.13°
    - [x] 合成は `(1 − F)(1 − metallic) × 拡散 + 鏡面`。鏡面は split-sum
    - [x] 手法は分担する。拡散はプローブ・SSGI・DDGI、鏡面は反射プローブ・SSR・レイトレ

## C++ で数えたもの {#numbers}

```cpp
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;       // 円周率
const double kDeg = 180.0 / kPi;           // ラジアン -> 度

// ルジャンドル多項式 P_l(x)（l = 0〜6 を漸化式で）。
double Legendre(int l, double x) {
  double p0 = 1.0, p1 = x;                                  // P_0, P_1
  if (l == 0) return p0;
  for (int k = 2; k <= l; ++k) {                            // (k) P_k = (2k-1) x P_{k-1} - (k-1) P_{k-2}
    const double p2 = ((2 * k - 1) * x * p1 - (k - 1) * p0) / k;
    p0 = p1;
    p1 = p2;
  }
  return p1;
}

// 余弦ローブ f(x) = max(x, 0)（x = cos 角）の、ルジャンドル展開の係数 c_l = (2l+1)/2 * ∫ f P_l dx。
double CosineCoefficient(int l) {
  const int n = 200000;                                     // x を 0〜1 で刻む（f は x < 0 で 0）
  const double dx = 1.0 / n;
  double sum = 0.0;
  for (int i = 0; i < n; ++i) {
    const double x = (i + 0.5) * dx;                        // 区間の中点
    sum += x * Legendre(l, x) * dx;                         // f(x) = x
  }
  return (2 * l + 1) * 0.5 * sum;
}

// GGX の法線分布が最大の半分になるハーフベクトルの角度（度）。alpha = roughness^2。
//   D(theta) = alpha^2 / (pi (cos^2 (alpha^2 - 1) + 1)^2)、D(0) = 1 / (pi alpha^2)。
//   D(theta) = D(0) / 2  =>  cos^2 theta = (1 - sqrt(2) alpha^2) / (1 - alpha^2)。
double GgxHalfWidthDeg(double roughness) {
  const double a = roughness * roughness;                   // alpha
  const double a2 = a * a;                                  // alpha^2
  const double c2 = (1.0 - std::sqrt(2.0) * a2) / (1.0 - a2);
  if (c2 <= 0.0 || c2 >= 1.0) return 90.0;                  // 半分に届かない（非常に粗い）か、1 = 角度 0
  return std::acos(std::sqrt(c2)) * kDeg;
}

int main() {
  // 1. 余弦ローブ（拡散の放射照度の畳み込み）を球面調和で表したときのエネルギー。
  //    c_l の 2 乗 * 2/(2l+1) が、各次数 l のエネルギー（全体 = ∫ f^2 dx）。
  std::printf("-- cosine lobe: Legendre coefficients c_l and energy share\n");
  double total = 0.0, e[7];
  for (int l = 0; l <= 6; ++l) {
    const double c = CosineCoefficient(l);
    e[l] = c * c * 2.0 / (2 * l + 1);
    total += e[l];
    std::printf("l=%d: c_l = %+.5f, energy = %.5f\n", l, c, e[l]);
  }
  double cum = 0.0;
  for (int l = 0; l <= 4; ++l) {
    cum += e[l];
    std::printf("energy in l <= %d: %.2f%%\n", l, cum / total * 100.0);
  }
  std::printf("(direct integral of f^2: %.5f)\n", 1.0 / 3.0);   // ∫_0^1 x^2 dx = 1/3

  // 2. GGX の反射ローブの幅（半値半幅）。反射方向のまわりの広がりは、ハーフベクトルの 2 倍。
  std::printf("-- GGX lobe width by roughness\n");
  for (double r : {0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0}) {
    const double half = GgxHalfWidthDeg(r);
    std::printf("roughness %.2f: alpha = %.4f, half-max half-vector angle = %6.2f deg, reflection lobe half width = %6.2f deg\n",
                r, r * r, half, 2.0 * half);
  }

  // 3. フレネル（シュリック）。F0 = 0.04（誘電体）と、粗さを考えない簡略形。
  std::printf("-- Fresnel Schlick (F0 = 0.04) and the diffuse share kd = 1 - F\n");
  for (double c : {1.0, 0.5, 0.2, 0.1, 0.0}) {
    const double f = 0.04 + 0.96 * std::pow(1.0 - c, 5.0);
    std::printf("n.v = %.1f: F = %.3f, kd = %.3f\n", c, f, 1.0 - f);
  }

  // 4. データ量。環境キューブ 256^2 x 6 面、RGBA16F、ミップ全部。BRDF LUT は 32^2 RG16F。SH9 は RGB 各 9 係数 float。
  std::printf("-- data size\n");
  double texels = 0.0;
  for (int s = 256; s >= 1; s /= 2) texels += 6.0 * s * s;           // 各ミップの面積の合計
  std::printf("environment cube 256^2: %d mips, %.0f texels = %.2f MiB (RGBA16F)\n", 9, texels, texels * 8.0 / 1048576.0);
  std::printf("BRDF LUT 32x32 RG16F: %.1f KiB\n", 32.0 * 32.0 * 4.0 / 1024.0);
  std::printf("SH9 RGB float32: %d bytes\n", 9 * 3 * 4);
  std::printf("irradiance cube 32^2 x 6 RGBA16F: %.1f KiB\n", 6.0 * 32 * 32 * 8.0 / 1024.0);
}
```

```text title="実行結果"
-- cosine lobe: Legendre coefficients c_l and energy share
l=0: c_l = +0.25000, energy = 0.12500
l=1: c_l = +0.50000, energy = 0.16667
l=2: c_l = +0.31250, energy = 0.03906
l=3: c_l = -0.00000, energy = 0.00000
l=4: c_l = -0.09375, energy = 0.00195
l=5: c_l = -0.00000, energy = 0.00000
l=6: c_l = +0.05078, energy = 0.00040
energy in l <= 0: 37.53%
energy in l <= 1: 87.57%
energy in l <= 2: 99.29%
energy in l <= 3: 99.29%
energy in l <= 4: 99.88%
(direct integral of f^2: 0.33333)
-- GGX lobe width by roughness
roughness 0.05: alpha = 0.0025, half-max half-vector angle =   0.09 deg, reflection lobe half width =   0.18 deg
roughness 0.10: alpha = 0.0100, half-max half-vector angle =   0.37 deg, reflection lobe half width =   0.74 deg
roughness 0.20: alpha = 0.0400, half-max half-vector angle =   1.48 deg, reflection lobe half width =   2.95 deg
roughness 0.30: alpha = 0.0900, half-max half-vector angle =   3.33 deg, reflection lobe half width =   6.67 deg
roughness 0.50: alpha = 0.2500, half-max half-vector angle =   9.57 deg, reflection lobe half width =  19.13 deg
roughness 0.70: alpha = 0.4900, half-max half-vector angle =  21.21 deg, reflection lobe half width =  42.42 deg
roughness 1.00: alpha = 1.0000, half-max half-vector angle =  90.00 deg, reflection lobe half width = 180.00 deg
-- Fresnel Schlick (F0 = 0.04) and the diffuse share kd = 1 - F
n.v = 1.0: F = 0.040, kd = 0.960
n.v = 0.5: F = 0.070, kd = 0.930
n.v = 0.2: F = 0.355, kd = 0.645
n.v = 0.1: F = 0.607, kd = 0.393
n.v = 0.0: F = 1.000, kd = 0.000
-- data size
environment cube 256^2: 9 mips, 524286 texels = 4.00 MiB (RGBA16F)
BRDF LUT 32x32 RG16F: 4.0 KiB
SH9 RGB float32: 108 bytes
irradiance cube 32^2 x 6 RGBA16F: 48.0 KiB
```

## 参考資料 {#references}

このページの積分と数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。コードの式（SH の基底の定数、split-sum、粗さを考えたフレネル）は記憶に基づく標準の形で、これらの資料で確かめていません。

- Brian Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014
- Ravi Ramamoorthi, Pat Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ {#related}

- [GI Theory](index.md)
- [Irradiance](irradiance.md)
- [Reflections](../../reflections/index.md)
- [Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)

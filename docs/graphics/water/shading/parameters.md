---
title: Water Color Parameters
tags:
  - 描画
---

# Water Color Parameters

水の見た目は吸収係数、深い水の色、屈折、粗さといったパラメーターで決まりますが、それぞれが何をしていてどの値がどんな絵になるのかは、触ってみるまで分かりにくいものです。しかもアーティストが直感で扱える「透明度の距離」とシェーダーが使う「色ごとの吸収係数」の間には変換が要ります。この変換と深さによる色の変化を間違えずに実装するのが、このページの目的です。吸収係数と透過率、透明度の距離からの変換、屈折した経路の長さ深い水の色の目安、プリセットの補間、天候による変化を HLSL と C++ の数字で説明します。旧版の表にあった数字のうち式と合わない列は、計算し直して直しました。

!!! tip "ポイント"
    - 水の色は色ごとの吸収 `T = exp(−a d)` で決まる。赤は浅いうちに減り青は深くまで残る。きれいな水（赤 0.45 /m）でも 5 m で赤は 10.5 % 残る。5 % に落ちるのは 6.7 m、1 % は 10.2 m。
    - 透明度の距離 D から吸収係数を作る式は `a = −ln(ε) / D`（ε = 5 % なら 3.0 / D）。D をどの色で測るかで値が変わる。RGB の平均で測るか緑で測るかを決める。
    - 屈折した視線は水中で鉛直に近づく。深さ 1 m を真上から見れば 1.00 m、60° の角度から見れば 1.32 m、85° なら 1.51 m 進む。
    - 深い水の色の目安は `b_b / (a + b_b)`。吸収の弱い青ほど大きくなる。外洋では赤:緑:青が約 0.08 : 0.47 : 1.00 になる。
    - 吸収係数は水の性質なので、時間帯や天候では変えない。変えるのは入ってくる光と水面の粗さ。

!!! info "このページを読む前に"
    - [Water Shading](index.md)（このセクション全体の地図と読む順番）

## 読んだ資料とこのページの範囲 {#sources}

このページは特定の論文を読んで書いたものではありません。Pope と Fry の純水の吸収の測定（1997）、Jerlov の海水の分類（1976）、Gordon らの水中の光学の関係式（1975）、Tessendorf の海のシミュレーション（2001）は、読んでいません。そのため、旧版の「実在の水の吸収係数」とプリセットの表の数字には、このページとして出典がありません。**プリセットの数字は見た目の出発点として扱ってください。**

このページの式はビア・ランバートの吸収 `T = exp(−a d)` とスネルの法則（屈折率 1.33）という、一般的な式です。「深い水の色」の `b_b / (a + b_b)` は色の比の目安として使う簡易式で、Gordon らの式の係数は確認していません。数字は C++ で出し HLSL は `fxc`（`ps_5_0`）でコンパイルして確かめました。

## パラメーターの整理 {#overview}

水のマテリアルには次のパラメーターがあります。

- **吸収係数 `a`（RGB、1/m）。** 色ごとの吸収の強さです。値を大きくすると浅いうちに色が消えます。赤を大きく青を小さくすると深くなるほど青くなります。
- **後方散乱 `b_b`（1/m）。** 水自体が返す光の量です。深い水の色（底が見えないときの色）を決めます。
- **透明度の距離。** 底が見える深さの目安です。吸収係数の入力に使えます。
- **屈折の強さ。** 画面のコピーをずらす量です。
- **粗さ。** ハイライトと反射のぼけを決めます。風や雨で変わります。
- **泡の色と量。** 波頭と岸の泡です。

水のマテリアルには 2 つの流儀があります。物理ベースは吸収係数と後方散乱、屈折率を直接指定します。現実の水を再現でき値の意味が明確ですが、アーティストが直感で扱いにくいです。アーティスト向けは浅い所の色、深い所の色、「透明度の距離」を指定します。直感的ですが現実からずれても気づきにくいです。おすすめは内部を物理ベースにして、入力をアーティスト向けにする組み合わせです。アーティストが「この深さで底が見えなくなる」と指定すると、システムが吸収係数に変換します。

## 透明度の距離から吸収係数を作る {#visibility}

透過率が `ε`（たとえば 5 %）になる距離を `D` とすると、`exp(−a D) = ε` から `a = −ln(ε) / D` です。ε = 0.05 なら `a = 3.0 / D` になります。色ごとの吸収にするには比 `color_ratio` を掛けます。平均が `a` になるように比を正規化します。

```hlsl
// 水の色のパラメーターを、シェーダーでどう使うか。
//   ① 透明度の距離 → 吸収係数  ② 屈折した光の経路の長さ  ③ 吸収（ビア・ランバート）と深い水の色  ④ プリセットの補間  ⑤ 空の光の変化
// 式は Beer-Lambert の吸収 T = exp(-a·d) と、スネルの法則。深い水の色 = 後方散乱の割合は、説明のための簡易式。
// 座標は左手系・Y-up。「足した」と書いた式や値は、このページが説明のために決めたもの。

struct WaterMaterial {
  float3 absorption;       // 吸収係数 a（RGB、1/m）
  float backscatter;       // 後方散乱 b_b（1/m）。水自体が返す光の量
  float visibility_m;      // 透明度の距離 [m]（absorption を自動で決めるときの入力）
  float roughness;
  float refraction_strength;
  float reflection_scale;
  float normal_strength;
  float foam_amount;
};

// ================= ① 透明度の距離 → 吸収係数 =================

// 「透過率が eps（例: 5 %）になる距離が D」から、平均の吸収係数 a = -ln(eps) / D。
// color_ratio で色ごとに振り分ける（赤が強く、青が弱い）。RGB の平均が a になるよう、比を正規化する。
float3 AbsorptionFromVisibility(float visibility_m, float3 color_ratio, float eps) {
  float a_mean = -log(eps) / max(visibility_m, 1e-3);          // eps = 0.05 なら 3.0 / D
  float3 ratio = color_ratio / max((color_ratio.x + color_ratio.y + color_ratio.z) / 3.0, 1e-4);   // 平均が 1 になる比
  return a_mean * ratio;
}
```

`AbsorptionFromVisibility` は RGB の平均が `a_mean` になるように比を正規化します（比の平均が 1 になる）。たとえば比が `(2.1, 0.5, 0.14)` なら平均 0.913 で割って、`(2.30, 0.55, 0.15)` になり `D = 20 m` なら `a_mean = 0.15` なので、`a = (0.345, 0.082, 0.023)` です。**どの色の D かを決めておかないと同じ「透明度 20 m」が、色ごとに違う値になります。**

旧版のプリセットの表にあった「透明度」の列は、式 `D = 3.0 / a_mean` と合っていませんでした。C++ で計算し直しました。

```text title="プリセットの透明度の確認"
[2] preset table check: visibility D from a_mean = (ar+ag+ab)/3 via D = 3.0 / a_mean, and D from green only
name       a_mean   D(mean)   D(green)   table D
tropical   0.143      20.9      50.0       30
open sea   0.183      16.4      42.9       20
lake       0.383       7.8      12.0        8
river      0.617       4.9       6.7        3
swamp      1.300       2.3       3.0        1
pool       0.103      29.0      75.0        0
```

南国の海は平均で 20.9 m、緑だけで 50.0 m です。旧版は 30 m でした。外洋は平均で 16.4 m、緑で 42.9 m（旧版 20 m）。湖は 7.8 m と 12.0 m（旧版 8 m）。川は 4.9 m と 6.7 m（旧版 3 m）、沼は 2.3 m と 3.0 m（旧版 1 m）、プールは 29.0 m と 75.0 m でした。**緑で測るか平均で測るかで、2 倍以上違います。** このページの数字では平均に合わせます。

## 深さによる色の変化 {#depth}

吸収は色ごとに違うので深くなるほど色が変わります。外洋のプリセット（`a = (0.45, 0.07, 0.03)`）で深さごとの透過率を計算しました。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="外洋: 深さごとに残る光の割合"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">外洋: 深さごとに残る光の割合</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="129.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="60.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="195.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">10</text><text x="330.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">20</text><text x="465.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">30</text><text x="600.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">40</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">深さ(m)</text><polyline points="60.0,40.0 66.8,74.3 73.5,101.6 80.2,123.4 87.0,140.9 93.8,154.8 100.5,165.9 107.2,174.8 114.0,181.9 120.8,187.6 127.5,192.1 134.2,195.7 141.0,198.6 147.8,200.9 154.5,202.7 161.2,204.2 168.0,205.4 174.8,206.3 181.5,207.0 188.2,207.6 195.0,208.1 201.8,208.5 208.5,208.8 215.2,209.0 222.0,209.2 228.8,209.4 235.5,209.5 242.2,209.6 249.0,209.7 255.8,209.8 262.5,209.8 269.2,209.8 276.0,209.9 282.8,209.9 289.5,209.9 296.2,209.9 303.0,209.9 309.8,210.0 316.5,210.0 323.2,210.0 330.0,210.0 336.8,210.0 343.5,210.0 350.2,210.0 357.0,210.0 363.8,210.0 370.5,210.0 377.2,210.0 384.0,210.0 390.8,210.0 397.5,210.0 404.2,210.0 411.0,210.0 417.8,210.0 424.5,210.0 431.2,210.0 438.0,210.0 444.8,210.0 451.5,210.0 458.2,210.0 465.0,210.0 471.8,210.0 478.5,210.0 485.2,210.0 492.0,210.0 498.8,210.0 505.5,210.0 512.2,210.0 519.0,210.0 525.8,210.0 532.5,210.0 539.2,210.0 546.0,210.0 552.8,210.0 559.5,210.0 566.2,210.0 573.0,210.0 579.8,210.0 586.5,210.0 593.2,210.0 600.0,210.0" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">赤</text><polyline points="60.0,40.0 66.8,45.8 73.5,51.5 80.2,56.9 87.0,62.2 93.8,67.3 100.5,72.2 107.2,76.9 114.0,81.5 120.8,85.9 127.5,90.2 134.2,94.3 141.0,98.3 147.8,102.1 154.5,105.9 161.2,109.4 168.0,112.9 174.8,116.2 181.5,119.5 188.2,122.6 195.0,125.6 201.8,128.5 208.5,131.3 215.2,134.0 222.0,136.6 228.8,139.1 235.5,141.6 242.2,143.9 249.0,146.2 255.8,148.4 262.5,150.5 269.2,152.6 276.0,154.5 282.8,156.4 289.5,158.3 296.2,160.1 303.0,161.8 309.8,163.4 316.5,165.0 323.2,166.6 330.0,168.1 336.8,169.5 343.5,170.9 350.2,172.3 357.0,173.6 363.8,174.8 370.5,176.0 377.2,177.2 384.0,178.3 390.8,179.4 397.5,180.5 404.2,181.5 411.0,182.5 417.8,183.4 424.5,184.3 431.2,185.2 438.0,186.1 444.8,186.9 451.5,187.7 458.2,188.4 465.0,189.2 471.8,189.9 478.5,190.6 485.2,191.3 492.0,191.9 498.8,192.5 505.5,193.1 512.2,193.7 519.0,194.3 525.8,194.8 532.5,195.3 539.2,195.8 546.0,196.3 552.8,196.8 559.5,197.2 566.2,197.7 573.0,198.1 579.8,198.5 586.5,198.9 593.2,199.3 600.0,199.7" fill="none" stroke="#4c8bf5" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">緑</text><polyline points="60.0,40.0 66.8,42.5 73.5,45.0 80.2,47.5 87.0,49.9 93.8,52.3 100.5,54.6 107.2,56.9 114.0,59.2 120.8,61.5 127.5,63.7 134.2,65.9 141.0,68.0 147.8,70.1 154.5,72.2 161.2,74.3 168.0,76.3 174.8,78.3 181.5,80.2 188.2,82.2 195.0,84.1 201.8,85.9 208.5,87.8 215.2,89.6 222.0,91.4 228.8,93.2 235.5,94.9 242.2,96.6 249.0,98.3 255.8,100.0 262.5,101.6 269.2,103.2 276.0,104.8 282.8,106.4 289.5,107.9 296.2,109.4 303.0,110.9 309.8,112.4 316.5,113.9 323.2,115.3 330.0,116.7 336.8,118.1 343.5,119.5 350.2,120.8 357.0,122.1 363.8,123.4 370.5,124.7 377.2,126.0 384.0,127.3 390.8,128.5 397.5,129.7 404.2,130.9 411.0,132.1 417.8,133.2 424.5,134.4 431.2,135.5 438.0,136.6 444.8,137.7 451.5,138.8 458.2,139.8 465.0,140.9 471.8,141.9 478.5,142.9 485.2,143.9 492.0,144.9 498.8,145.9 505.5,146.8 512.2,147.8 519.0,148.7 525.8,149.6 532.5,150.5 539.2,151.4 546.0,152.3 552.8,153.1 559.5,154.0 566.2,154.8 573.0,155.6 579.8,156.4 586.5,157.2 593.2,158.0 600.0,158.8" fill="none" stroke="#e5aa28" stroke-width="2.4"/><line x1="470" y1="80" x2="496" y2="80" stroke="#e5aa28" stroke-width="2.4"/><text x="502" y="84" text-anchor="start" font-size="11" fill="currentColor">青</text></svg>

深さ 1 m で赤は 63.8 %、緑は 93.2 %、青は 97.0 % です。2 m で 40.7 %、86.9 %、94.2 %。5 m で 10.5 %、70.5 %、86.1 %。10 m では赤が 1.1 % に落ち緑 49.7 %、青 74.1 % です。20 m では赤は 0.01 % で、緑 24.7 %、青 54.9 % が残ります。40 m で緑は 6.1 %、青は 30.1 % です。

旧版は「水深 5 m でほぼ赤が消える」と書いていましたが、5 m でも赤は 10.5 % 残ります。5 % に落ちるのは 6.7 m、1 % は 10.2 m です。緑が 5 % になるのは 42.9 m、青は 100 m です。**浅いうちは赤が弱るだけで、本格的に青緑になるのは数 m 以降**だと考えてください。

吸収のあとの色は底（または水中の物）の色に透過率を掛け水自体が返す色（深い水の色）を足したものです。

```hlsl
// ================= ③ 吸収と、深い水の色 =================

// 経路の長さ path_m を進んだあとの色。
//   底（または水中の物）の色は T = exp(-a·path) で弱まる。
//   水自体が返す色（deep_color）は、その分だけ増える（1 - T で重みづけ）。
float3 WaterColorAtDepth(float3 bottom_color, float path_m, WaterMaterial m, float3 incident_light) {
  float3 a = m.absorption;
  float3 t = exp(-a * path_m);                                   // 色ごとの透過率
  // 深い水の色: 入射光 × 後方散乱の割合 b_b / (a + b_b)（色ごと）。簡易式で、係数は足していない。
  float3 deep = incident_light * (m.backscatter / (a + m.backscatter));
  return bottom_color * t * incident_light + deep * (1.0 - t);
}
```

`t = exp(−a × path)` が色ごとの透過率です。`bottom_color × t` は底の色が弱まった分、`deep × (1 − t)` は水自体が返す色です。深くなるほど `t` が 0 に近づき底の色から深い水の色へ移ります。`incident_light` は水に入ってくる光（太陽と空）で、底の色にも深い水の色にも掛かります。

## 深い水の色の目安 {#deep}

底が見えないほど深い水の色は水自体が返す光で決まります。ここでは、色ごとの `b_b / (a + b_b)` を目安にします（簡易式）。吸収が弱い色ほど返る割合が大きくなります。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="深い水の色の目安(最大を 1 に正規化。赤・緑・青)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">深い水の色の目安(最大を 1 に正規化。赤・緑・青)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">0.55</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">1.1</text><rect x="68.0" y="180.5" width="21.7" height="9.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="78.83333333333333" y="176.45454545454544" text-anchor="middle" font-size="10" fill="currentColor">0.07</text><rect x="92.7" y="138.2" width="21.7" height="51.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="103.5" y="134.1818181818182" text-anchor="middle" font-size="10" fill="currentColor">0.38</text><rect x="117.3" y="53.6" width="21.7" height="136.4" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="128.16666666666669" y="49.636363636363654" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="105.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">南国</text><rect x="158.0" y="179.1" width="21.7" height="10.9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="168.83333333333334" y="175.0909090909091" text-anchor="middle" font-size="10" fill="currentColor">0.08</text><rect x="182.7" y="125.9" width="21.7" height="64.1" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="193.5" y="121.90909090909092" text-anchor="middle" font-size="10" fill="currentColor">0.47</text><rect x="207.3" y="53.6" width="21.7" height="136.4" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="218.16666666666669" y="49.636363636363654" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="195.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">外洋</text><rect x="248.0" y="149.1" width="21.7" height="40.9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="258.8333333333333" y="145.0909090909091" text-anchor="middle" font-size="10" fill="currentColor">0.3</text><rect x="272.7" y="79.5" width="21.7" height="110.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="283.5" y="75.54545454545455" text-anchor="middle" font-size="10" fill="currentColor">0.81</text><rect x="297.3" y="53.6" width="21.7" height="136.4" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="308.16666666666663" y="49.636363636363654" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="285.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">湖</text><rect x="338.0" y="132.7" width="21.7" height="57.3" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="348.8333333333333" y="128.72727272727275" text-anchor="middle" font-size="10" fill="currentColor">0.42</text><rect x="362.7" y="67.3" width="21.7" height="122.7" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="373.5" y="63.27272727272728" text-anchor="middle" font-size="10" fill="currentColor">0.9</text><rect x="387.3" y="53.6" width="21.7" height="136.4" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="398.16666666666663" y="49.636363636363654" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="375.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">川</text><rect x="428.0" y="127.3" width="21.7" height="62.7" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="438.8333333333333" y="123.27272727272728" text-anchor="middle" font-size="10" fill="currentColor">0.46</text><rect x="452.7" y="67.3" width="21.7" height="122.7" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="463.5" y="63.27272727272728" text-anchor="middle" font-size="10" fill="currentColor">0.9</text><rect x="477.3" y="53.6" width="21.7" height="136.4" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="488.16666666666663" y="49.636363636363654" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="465.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">沼</text><rect x="518.0" y="177.7" width="21.7" height="12.3" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="528.8333333333334" y="173.72727272727272" text-anchor="middle" font-size="10" fill="currentColor">0.09</text><rect x="542.7" y="119.1" width="21.7" height="70.9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="553.5" y="115.0909090909091" text-anchor="middle" font-size="10" fill="currentColor">0.52</text><rect x="567.3" y="53.6" width="21.7" height="136.4" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="578.1666666666667" y="49.636363636363654" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="555.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">プール</text><rect x="450" y="34" width="12" height="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="466" y="43" text-anchor="start" font-size="11" fill="currentColor">赤</text><rect x="450" y="50" width="12" height="10" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="466" y="59" text-anchor="start" font-size="11" fill="currentColor">緑</text><rect x="450" y="66" width="12" height="10" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="466" y="75" text-anchor="start" font-size="11" fill="currentColor">青</text></svg>

最大値を 1 に正規化した RGB は、南国の海 `(0.07, 0.38, 1.00)`、外洋 `(0.08, 0.47, 1.00)`、湖 `(0.30, 0.81, 1.00)`、川 `(0.42, 0.90, 1.00)`、沼 `(0.46, 0.90, 1.00)`、プール `(0.09, 0.52, 1.00)` です。**どのプリセットでも青が最大で、赤は小さく緑がその間**です。海は青、濁った水は緑がかって見える傾向と合います。この式の係数は物理的な反射率ではなく、色の比の目安です。実際の明るさは入射光と水面の反射・透過の式（[Specular](specular.md)）で決まります。

## 屈折した経路の長さ {#refraction}

水面で屈折した視線は水中で鉛直に近づきます。同じ深さでも斜めに見るほど水中を長く進みます。

```hlsl
// ================= ② 屈折した光の経路の長さ =================

// 水中の深さ depth_m を、視線が水面で屈折したあとに通る道のりに直す。
// スネルの法則 n1 sinθ1 = n2 sinθ2（空気 1.0、水 1.33）。θ2 は水中での鉛直からの角。
float RefractedPathLength(float depth_m, float3 view_dir_to_eye, float3 normal) {
  float cos_i = saturate(dot(normal, view_dir_to_eye));          // 空気側の入射角の余弦
  float sin_i = sqrt(max(1.0 - cos_i * cos_i, 0.0));
  float sin_t = sin_i / 1.33;                                    // 水中の角の正弦
  float cos_t = sqrt(max(1.0 - sin_t * sin_t, 0.0));
  return depth_m / max(cos_t, 0.05);                             // 浅い角度でも発散しないよう下限を置く（足した値）
}
```

スネルの法則 `sin θ_i = 1.33 sin θ_t` から水中の角 `θ_t` を求め道のりを `depth / cos θ_t` にします。C++ で深さ 1 m の道のりを数えました。鉛直（0°）で 1.000 m、30° で 1.079 m、60° で 1.318 m、75° で 1.455 m、85° で 1.509 m です。`θ_t` の最大は `asin(1/1.33) = 48.8°` で `1/cos(48.8°) = 1.52` を超えません。そのため、斜めに見ても道のりの伸びは最大約 1.5 倍で済み発散しません。HLSL の `max(cos_t, 0.05)` は安全のための下限です（足した値）。

## 水の種類のプリセット {#presets}

場所ごとにパラメーターのセットを持つと海、湖、川、沼、プールを 1 つの水シェーダーで作り分けられます。旧版の値をそのまま出発点として並べます。出典は確認していません。

- **南国の海。** `a = (0.35, 0.06, 0.02)`、`b_b = 0.004`。鮮やかな青緑で浅瀬は白い砂が透けます。
- **外洋。** `a = (0.45, 0.07, 0.03)`、`b_b = 0.005`。深い青で波が大きいです。
- **湖。** `a = (0.70, 0.25, 0.20)`、`b_b = 0.015`。緑がかった静かな水面です。
- **川。** `a = (1.0, 0.45, 0.4)`、`b_b = 0.03`。茶から緑で流れがあります。
- **沼。** `a = (2.0, 1.0, 0.9)`、`b_b = 0.05`。暗い緑茶色で底が透けません。
- **プール。** `a = (0.25, 0.04, 0.02)`、`b_b = 0.002`。底のタイルが見えます。

ゲームの明るさや露出に合わせて、調整してください。プリセットは構造体で持ちます。

```cpp
// プリセットを構造体で持つ。
struct WaterMaterial {
  float3 absorption;          // 1/m
  float backscatter;          // 1/m
  float visibility_m;         // 透明度（参考値。absorption を自動で決めるときに使う）
  float roughness;
  float refraction_strength;
  float reflection_scale;
  float normal_strength;
  float foam_amount;
};

constexpr WaterMaterial kOcean = {{0.45f, 0.07f, 0.03f}, 0.005f, 16.4f, 0.15f, 0.03f, 1.0f, 1.0f, 0.6f};
constexpr WaterMaterial kLake  = {{0.70f, 0.25f, 0.20f}, 0.015f, 7.8f, 0.05f, 0.02f, 1.0f, 0.6f, 0.1f};
```

湖から川のように水の種類がつながっている所は、境でパラメーターを補間します。補間の仕方は 3 つあります。水域ごとに別のメッシュにして、境をはっきり分ける方法。頂点カラーにプリセットの重みを持たせる方法。濁りをテクスチャに描いて読む方法で、岸の近くだけ緑にするといった表現に向きます。

```hlsl
// ================= ④ プリセットの補間 =================

// 2 つの水の種類（湖と川など）を、重み w（0〜1）で混ぜる。吸収は対数でなく線形で混ぜる（足した選択）。
WaterMaterial BlendWater(WaterMaterial a, WaterMaterial b, float w) {
  WaterMaterial r;
  r.absorption = lerp(a.absorption, b.absorption, w);
  r.backscatter = lerp(a.backscatter, b.backscatter, w);
  r.visibility_m = lerp(a.visibility_m, b.visibility_m, w);
  r.roughness = lerp(a.roughness, b.roughness, w);
  r.refraction_strength = lerp(a.refraction_strength, b.refraction_strength, w);
  r.reflection_scale = lerp(a.reflection_scale, b.reflection_scale, w);
  r.normal_strength = lerp(a.normal_strength, b.normal_strength, w);
  r.foam_amount = lerp(a.foam_amount, b.foam_amount, w);
  return r;
}

Texture2D<float> g_turbidity_map : register(t0);   // 濁りの重み（0 = 澄んだ水、1 = 濁った水）。岸の近くを濁らせるなど
SamplerState g_linear_clamp : register(s0);

cbuffer WaterCB : register(b0) {
  WaterMaterial g_clear;      // 澄んだ水（例: 湖）
  WaterMaterial g_murky;      // 濁った水（例: 川）
  float3 g_sun_color;         // 太陽の色 × 強さ
  float g_cloud_cover;        // 0 = 晴れ、1 = 厚い雲
  float3 g_sky_color;         // 空の拡散光
  float g_rain;               // 0 = 降っていない、1 = 強い雨
};

// ================= ⑤ 空の光の変化 =================

// 水に入る光。晴れなら太陽が効き、曇りなら空の光だけになる。吸収係数は水の性質なので変えない。
float3 IncidentLight(float sun_visibility) {
  float sun_weight = (1.0 - g_cloud_cover) * sun_visibility;
  return g_sun_color * sun_weight + g_sky_color;
}

float4 WaterPS(float4 pos : SV_Position, float3 world : TEXCOORD0, float3 normal : NORMAL, float2 uv : TEXCOORD1,
               float water_depth : TEXCOORD2, float3 view_to_eye : TEXCOORD3, float3 bottom_color : TEXCOORD4) : SV_Target {
  float w = g_turbidity_map.Sample(g_linear_clamp, uv);
  WaterMaterial m = BlendWater(g_clear, g_murky, w);
  m.roughness = saturate(m.roughness + g_rain * 0.15);           // 雨で水面が荒れる（0.15 は足した値）
  float path = RefractedPathLength(water_depth, view_to_eye, normalize(normal));
  float3 c = WaterColorAtDepth(bottom_color, path, m, IncidentLight(1.0));
  return float4(c, 1.0);
}
```

`BlendWater` は 2 つのプリセットを重みで混ぜます。吸収係数は線形に混ぜています（対数で混ぜる選択もあります。ここでは簡単さを選びました）。`WaterPS` は濁りのテクスチャから重みを読み粗さを雨で上げ屈折した経路の長さで色を求めます。

## 天候と時間帯 {#weather}

水の見た目は空の光で変わります。曇りでは太陽の反射が消えて水は暗くグレーに寄ります。夕方は反射がオレンジになります。夜は空の光がほぼなく水はほぼ黒で、月や街灯の反射だけが見えます。雨では粗さが増して反射がにじみます。

吸収係数は水そのものの性質なので、時間帯では変えません。変えるのは水に入る光（`IncidentLight`）と粗さです（[Scattering Color (SSS-Like)](scattering.md)）。HLSL の最後に曇りで太陽の寄与を減らす関数と雨で粗さを上げる行があります。

## 数字を出した C++ {#experiment}

```cpp
// 水のパラメーターの数字を確かめる。旧版の表・説明の整合性と、色が深さでどう変わるか。
//   [1] 吸収係数と透過率（旧版の「水深 5 m でほぼ赤が消える」は成り立つか）
//   [2] プリセットの透明度の列は、式 a = 3.0 / D と合っているか
//   [3] 深さごとの透過率と、色の変化（海のプリセット）
//   [4] 深い水の色の目安 b_b / (a + b_b)
//   [5] 屈折した経路の長さ（斜めに見るほど長い）
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

constexpr double kPi = 3.14159265358979323846;

struct Preset { const char* name; std::array<double, 3> a; double bb; double visibility; };

int main() {
  // ---- [1] ----
  std::printf("[1] transmittance exp(-a d), clear water a_red = 0.45 /m\n");
  for (double d : {1.0, 2.0, 5.0, 10.0}) std::printf("d = %4.1f m  red remains %.1f %%\n", d, 100 * std::exp(-0.45 * d));
  std::printf("depth where red falls to 5 %% : %.1f m, to 1 %% : %.1f m\n", 3.0 / 0.45, std::log(100.0) / 0.45);

  // ---- [2] ----
  std::printf("\n[2] preset table check: visibility D from a_mean = (ar+ag+ab)/3 via D = 3.0 / a_mean, and D from green only\n");
  const Preset presets[] = {
      {"tropical", {0.35, 0.06, 0.02}, 0.004, 30}, {"open sea", {0.45, 0.07, 0.03}, 0.005, 20}, {"lake", {0.70, 0.25, 0.20}, 0.015, 8},
      {"river", {1.0, 0.45, 0.4}, 0.03, 3},          {"swamp", {2.0, 1.0, 0.9}, 0.05, 1},       {"pool", {0.25, 0.04, 0.02}, 0.002, 0}};
  std::printf("name       a_mean   D(mean)   D(green)   table D\n");
  for (const auto& p : presets) {
    double am = (p.a[0] + p.a[1] + p.a[2]) / 3;
    std::printf("%-9s  %.3f    %6.1f    %6.1f     %4.0f\n", p.name, am, 3.0 / am, 3.0 / p.a[1], p.visibility);
  }

  // ---- [3] ----
  std::printf("\n[3] open sea: remaining light per channel and the ratio R:G:B (normalized to B)\n");
  std::printf("depth[m]   R       G       B       R/B     G/B\n");
  for (double d : {0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0}) {
    double r = std::exp(-0.45 * d), g = std::exp(-0.07 * d), b = std::exp(-0.03 * d);
    std::printf("%6.1f    %.4f  %.4f  %.4f  %.4f  %.4f\n", d, r, g, b, r / b, g / b);
  }
  std::printf("depth where each channel falls to 5%%: R %.1f m, G %.1f m, B %.1f m\n", 3.0 / 0.45, 3.0 / 0.07, 3.0 / 0.03);

  // ---- [4] ----
  std::printf("\n[4] deep water tint b_b / (a + b_b) per channel (not a physical reflectance; normalized so the max = 1)\n");
  std::printf("name       R        G        B        (R, G, B normalized)\n");
  for (const auto& p : presets) {
    double r = p.bb / (p.a[0] + p.bb), g = p.bb / (p.a[1] + p.bb), b = p.bb / (p.a[2] + p.bb);
    double mx = std::max({r, g, b});
    std::printf("%-9s  %.4f   %.4f   %.4f   (%.2f, %.2f, %.2f)\n", p.name, r, g, b, r / mx, g / mx, b / mx);
  }

  // ---- [5] ----
  std::printf("\n[5] refracted path length for depth 1 m (n = 1.33): path = depth / cos(theta_t)\n");
  std::printf("view angle from vertical[deg]  theta_t[deg]  path[m]\n");
  for (double deg : {0.0, 30.0, 60.0, 75.0, 85.0}) {
    double si = std::sin(deg * kPi / 180), st = si / 1.33;
    double ct = std::sqrt(1 - st * st);
    std::printf("%6.0f                        %6.1f        %.3f\n", deg, std::asin(st) * 180 / kPi, 1.0 / ct);
  }
  return 0;
}
```

```text title="実行結果"
[1] transmittance exp(-a d), clear water a_red = 0.45 /m
d =  1.0 m  red remains 63.8 %
d =  2.0 m  red remains 40.7 %
d =  5.0 m  red remains 10.5 %
d = 10.0 m  red remains 1.1 %
depth where red falls to 5 % : 6.7 m, to 1 % : 10.2 m
```

```text title="実行結果（続き）"
[2] preset table check: visibility D from a_mean = (ar+ag+ab)/3 via D = 3.0 / a_mean, and D from green only
name       a_mean   D(mean)   D(green)   table D
tropical   0.143      20.9      50.0       30
open sea   0.183      16.4      42.9       20
lake       0.383       7.8      12.0        8
river      0.617       4.9       6.7        3
swamp      1.300       2.3       3.0        1
pool       0.103      29.0      75.0        0
```

```text title="実行結果（続き）"
[3] open sea: remaining light per channel and the ratio R:G:B (normalized to B)
depth[m]   R       G       B       R/B     G/B
   0.5    0.7985  0.9656  0.9851  0.8106  0.9802
   1.0    0.6376  0.9324  0.9704  0.6570  0.9608
   2.0    0.4066  0.8694  0.9418  0.4317  0.9231
   5.0    0.1054  0.7047  0.8607  0.1225  0.8187
  10.0    0.0111  0.4966  0.7408  0.0150  0.6703
  20.0    0.0001  0.2466  0.5488  0.0002  0.4493
  40.0    0.0000  0.0608  0.3012  0.0000  0.2019
depth where each channel falls to 5%: R 6.7 m, G 42.9 m, B 100.0 m
```

```text title="実行結果（続き）"
[4] deep water tint b_b / (a + b_b) per channel (not a physical reflectance; normalized so the max = 1)
name       R        G        B        (R, G, B normalized)
tropical   0.0113   0.0625   0.1667   (0.07, 0.38, 1.00)
open sea   0.0110   0.0667   0.1429   (0.08, 0.47, 1.00)
lake       0.0210   0.0566   0.0698   (0.30, 0.81, 1.00)
river      0.0291   0.0625   0.0698   (0.42, 0.90, 1.00)
swamp      0.0244   0.0476   0.0526   (0.46, 0.90, 1.00)
pool       0.0079   0.0476   0.0909   (0.09, 0.52, 1.00)
```

```text title="実行結果（続き）"
[5] refracted path length for depth 1 m (n = 1.33): path = depth / cos(theta_t)
view angle from vertical[deg]  theta_t[deg]  path[m]
     0                           0.0        1.000
    30                          22.1        1.079
    60                          40.6        1.318
    75                          46.6        1.455
    85                          48.5        1.509
```

## よくあるミス {#mistakes}

??? failure "海も湖も同じパラメーターで、変化が出ない"
    環境ごとにプリセットを用意する。吸収係数と後方散乱を変える。

??? failure "透明度の距離を入れても、色が思ったより濃い（薄い）"
    D をどの色で測るかが違う。平均で測るか緑で測るかを決めて、変換を合わせる。

??? failure "斜めに見ると、水が急に濃くなる"
    屈折した経路の長さを使わず鉛直の深さで計算している。または、`cos θ_t` に下限がなく発散している。

??? failure "夜や曇りで、水が昼と同じ色のまま"
    入射光を変えていない。吸収係数を変えるのではなく水に入る光を変える。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 水の色は色ごとの吸収 `exp(−a d)` と深い水の色で決まる。
    - [x] 透明度の距離から `a = −ln(ε) / D`。どの色で測るかを決める。
    - [x] 斜めに見ると、屈折した道のりが伸びる（最大約 1.5 倍）。
    - [x] 吸収は水の性質。天候や時間帯では入射光と粗さを変える。

## 参考 {#references}

- Robin M. Pope, Edward S. Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics 36(33), 1997. 読んでいない。純水の吸収係数の測定値の出典として挙げる。
- Nils G. Jerlov, "Marine Optics", Elsevier, 1976. 読んでいない。
- Howard R. Gordon, Otis B. Brown, Michael M. Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics 14(2), 1975. 読んでいない。
- Jerry Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes. 読んでいない。
- プリセットの数字は旧版のもので、出典は確認していない。見た目の出発点として扱う。

## 関連ページ {#related}

- [Water Shading](index.md)
- [Color by Water Depth](depth-color.md)
- [Specular](specular.md)
- [Scattering Color (SSS-Like)](scattering.md)

---
title: Analytic Sky Models
tags:
  - 描画
---

# Analytic Sky Models

空の色をグラデーションの画像で描くと時刻ごとに画像が要ります。大気の散乱を毎フレーム積分すれば正確ですが、重くなります。その中間に観測やシミュレーションの結果を少数のパラメータの式に当てはめた解析的なモデルがあります。

<strong>Preetham（1999）や Hošek–Wilkie（2012）は、太陽の高さと大気の濁りを入れると、空の各方向の色が式 1 つで返るモデルです</strong>。積分も LUT も要らないので、1 画素あたり数十命令で済みます。このページでは Perez の式、Preetham の係数と使い方（計算して確かめた結果つき）、Hošek–Wilkie との違い長所と短所、使いどころを説明します。

!!! tip "ポイント"
    - 太陽の高さと濁り（turbidity）から、空の輝度と色が決まります。
    - Preetham は軽くて簡単ですが、太陽が低い時間帯は不正確です。Hošek–Wilkie は朝夕と地面の反射も扱えて、精度が高いです。
    - 1 画素ごとに式を評価するだけです。事前計算は要りません。
    - 空の見た目だけで、遠景の霞や光の筋は別に計算します。
    - 宇宙や高高度の視点には使えません。地上から見た空に限られます。

!!! info "このページを読む前に"
    - [Sky Models](index.md)（このセクション全体の地図と読む順番）

## 解析的なモデルとは {#overview}

解析的な空のモデルは観測やシミュレーションの結果に数式を当てはめたものです。大気の散乱を直接は計算しません。そのため、軽い代わりに地上から見た空にしか使えません。宇宙から見た地球や遠景の霞（空気遠近法）は扱えません。それらは大気散乱の方式の担当です（[Atmospheric Scattering](../scattering/index.md)）。

- Perez の式（1993）は空の輝度の分布を 5 つの係数で表す古典的な式で、後続のモデルの土台です。
- Preetham（1999）は Perez の式の係数を濁りの関数として決めたモデルです。簡単で広く使われました。昼の空（太陽が地平線より上）が対象です。
- Hošek–Wilkie（2012）は、Preetham より精度が高く、太陽が低いとき（朝夕）もうまく動きます。スペクトル全体で当てはめています。

## Perez の式 {#perez}

空のある方向の輝度を天頂の輝度に対する割合として表します。

<div class="formula">F(θ, γ) = (1 + A·e^(B / cos θ)) · (1 + C·e^(D·γ) + E·cos²γ)</div>

記号は次のとおりです。`θ` は視線の天頂角（真上から何度か）、`γ` は視線と太陽のなす角、`A` から `E` は係数です。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="天頂角 θ と、視線と太陽のなす角 γ の定義"><defs><marker id="skA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Perez の式の 2 つの角度</text>
<line x1="60" y1="230" x2="680" y2="230" stroke="currentColor" stroke-width="2"/><text x="680" y="250" text-anchor="end" style="font-size:12px">地平線</text>
<line x1="300" y1="230" x2="300" y2="40" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="308" y="50" style="font-size:12px">天頂（真上）</text>
<line x1="300" y1="230" x2="430" y2="82" stroke="#4c8bf5" stroke-width="3" marker-end="url(#skA)"/><text x="440" y="80" style="font-size:12px;font-weight:600;fill:#4c8bf5">視線</text>
<line x1="300" y1="230" x2="545" y2="150" stroke="#e5aa28" stroke-width="3" marker-end="url(#skA)"/><text x="552" y="148" style="font-size:12px;font-weight:600;fill:#b7791f">太陽の向き</text>
<path d="M300,190 A40,40 0 0 1 326,196" fill="none" stroke="currentColor" stroke-width="1.5"/><text x="330" y="186" style="font-size:13px;font-weight:600">θ</text>
<path d="M392,134 A60,60 0 0 1 400,176" fill="none" stroke="currentColor" stroke-width="1.5"/><text x="408" y="168" style="font-size:13px;font-weight:600">γ</text>
<text x="360" y="262" text-anchor="middle" style="font-size:12px">θ: 地平線に近いほど大きい（霞で明るい）。γ: 太陽に近いほど小さい（太陽の周りが明るい）</text></svg>

- 前半の `(1 + A·e^(B / cos θ))` は地平線に近づくほど明るく（霞む）なる項です。`A`、`B` が地平線の明るさを決めます。
- 後半の `(1 + C·e^(D·γ) + E·cos²γ)` は太陽の周りが明るくなる項（`C`、`D`）と太陽と反対側のわずかな明るさ（`E`）です。

`cos θ` が 0 に近い（地平線）と `B / cos θ` が大きな値になって、`exp` が暴走します。下限（`max(…, 0.01)`）を設けます。

## Preetham の使い方 {#preetham}

Preetham は空の色を CIE xyY 色空間で表します。輝度 `Y` と色度 `x`、`y` の 3 つのチャンネルについて、それぞれ Perez の式を計算します。各係数は濁り `T`（turbidity）の 1 次式で決まります。

```text
Y: A = 0.1787T − 1.4630,  B = −0.3554T + 0.4275,  C = −0.0227T + 5.3251,
   D = 0.1206T − 2.5771,  E = −0.0670T + 0.3703
x: A = −0.0193T − 0.2592, B = −0.0665T + 0.0008,  C = −0.0004T + 0.2125,
   D = −0.0641T − 0.8989, E = −0.0033T + 0.0452
y: A = −0.0167T − 0.2608, B = −0.0950T + 0.0092,  C = −0.0079T + 0.2102,
   D = −0.0441T − 1.6537, E = −0.0109T + 0.0529
```

天頂の値は太陽の天頂角 `θs` と濁り `T` から決まります。輝度は `χ = (4/9 − T/120)(π − 2θs)` として `Yz = (4.0453T − 4.9710)·tan χ − 0.2155T + 2.4192`（単位は kcd/m²）です。天頂の色度 `xz`、`yz` は `θs` の 3 次式と `T` の 2 次式の組み合わせです。最終的な値は天頂の値 × `F(θ, γ) / F(0, θs)` です。

!!! warning "この係数表は、論文で確かめていません"
    上の係数は記憶から書いた表です。Preetham らの論文（1999）は、このページでは読んでいません。実際に使う前に論文の表と突き合わせてください。ここでは、計算した結果が空として妥当（青い天頂、白っぽい地平線、太陽の周りが明るい）かどうかだけを確かめました。

次の HLSL はこの式をそのまま書いたものです。

```hlsl
struct PerezCoeffs { float A, B, C, D, E; };

// Perez の式。天頂に対する割合を返す
float Perez(PerezCoeffs c, float cos_theta, float gamma) {
  float cos_gamma = cos(gamma);
  // cos_theta が 0 に近い（地平線）と exp が暴走するので、下限を設ける（足した処理）
  return (1.0 + c.A * exp(c.B / max(cos_theta, 0.01)))
       * (1.0 + c.C * exp(c.D * gamma) + c.E * cos_gamma * cos_gamma);
}

// 濁り T からの係数（輝度 Y と色度 x, y）
PerezCoeffs CoeffsY(float T) { PerezCoeffs c; c.A = 0.1787*T - 1.4630; c.B = -0.3554*T + 0.4275; c.C = -0.0227*T + 5.3251; c.D = 0.1206*T - 2.5771; c.E = -0.0670*T + 0.3703; return c; }
PerezCoeffs CoeffsX(float T) { PerezCoeffs c; c.A = -0.0193*T - 0.2592; c.B = -0.0665*T + 0.0008; c.C = -0.0004*T + 0.2125; c.D = -0.0641*T - 0.8989; c.E = -0.0033*T + 0.0452; return c; }
PerezCoeffs CoeffsSmallY(float T) { PerezCoeffs c; c.A = -0.0167*T - 0.2608; c.B = -0.0950*T + 0.0092; c.C = -0.0079*T + 0.2102; c.D = -0.0441*T - 1.6537; c.E = -0.0109*T + 0.0529; return c; }

// 天頂の輝度（kcd/m²）と色度。ts は太陽の天頂角（ラジアン）
float3 ZenithYxy(float T, float ts) {
  float chi = (4.0 / 9.0 - T / 120.0) * (3.14159265 - 2.0 * ts);
  float Yz = (4.0453 * T - 4.9710) * tan(chi) - 0.2155 * T + 2.4192;
  float t2 = ts * ts, t3 = t2 * ts, T2 = T * T;
  float xz = T2 * (0.00166*t3 - 0.00375*t2 + 0.00209*ts) + T * (-0.02903*t3 + 0.06377*t2 - 0.03202*ts + 0.00394)
           + (0.11693*t3 - 0.21196*t2 + 0.06052*ts + 0.25886);
  float yz = T2 * (0.00275*t3 - 0.00610*t2 + 0.00317*ts) + T * (-0.04214*t3 + 0.08970*t2 - 0.04153*ts + 0.00516)
           + (0.15346*t3 - 0.26756*t2 + 0.06669*ts + 0.26688);
  return float3(Yz, xz, yz);
}
```

最後に、方向から RGB を求めます。

```hlsl
float3 XyYToRgb(float x, float y, float Y) {
  float X = x / y * Y;
  float Z = (1.0 - x - y) / y * Y;
  // XYZ → 線形 sRGB
  return float3( 3.2406 * X - 1.5372 * Y - 0.4986 * Z,
                -0.9689 * X + 1.8758 * Y + 0.0415 * Z,
                 0.0557 * X - 0.2040 * Y + 1.0570 * Z);
}

cbuffer SkyConstants : register(b0) {
  float3 g_sun_dir;          // 太陽へ向かう単位ベクトル（y が上）
  float g_turbidity;         // 濁り。2（澄んだ）〜 10（霞んだ）
  float g_exposure;          // 露出。例: 0.12（輝度が kcd/m² なので、小さく掛ける）
  float3 _pad;
};

float4 SkyPreethamPS(float4 pos : SV_Position, float3 view_dir : TEXCOORD0) : SV_Target {
  float3 v = normalize(view_dir);
  float cos_theta = max(v.y, 0.0);                                  // 地平線の下は、地平線と同じ扱い
  float cos_gamma = clamp(dot(v, g_sun_dir), -1.0, 1.0);
  float gamma = acos(cos_gamma);
  float ts = acos(clamp(g_sun_dir.y, -1.0, 1.0));                   // 太陽の天頂角

  float3 zenith = ZenithYxy(g_turbidity, ts);                       // (Yz, xz, yz)
  float Y = zenith.x * Perez(CoeffsY(g_turbidity), cos_theta, gamma) / Perez(CoeffsY(g_turbidity), 1.0, ts);
  float x = zenith.y * Perez(CoeffsX(g_turbidity), cos_theta, gamma) / Perez(CoeffsX(g_turbidity), 1.0, ts);
  float y = zenith.z * Perez(CoeffsSmallY(g_turbidity), cos_theta, gamma) / Perez(CoeffsSmallY(g_turbidity), 1.0, ts);

  float3 rgb = XyYToRgb(x, y, Y) * g_exposure;
  return float4(max(rgb, 0.0), 1.0);                                // HDR のまま返して、後でトーンマップする
}
```

天頂の輝度は kcd/m² の単位で、そのままでは大きすぎるので露出（`g_exposure`）で調整します。

計算して確かめました。太陽の高さ 45° で濁り `T = 2` のとき天頂の輝度は 4.47 kcd/m²、色度は `(0.241, 0.244)` で RGB（線形、未露出）は約 `(2.7, 4.5, 9.3)` と青が強い空になりました。天頂角 60° で太陽の反対側は輝度が 5.6、地平線近くは 14.3 で RGB が `(12.4, 14.4, 19.5)` と白っぽくなって、太陽の近く（5°）は 17.8 で `(14, 18, 28)` と最も明るくなりました。`T = 6` では天頂が 14.9 kcd/m² で `(10.4, 15.3, 24.2)` と `T = 2` より明るく白っぽくなり、地平線近くは `(9.7, 8.6, 7.9)` と赤みがかった黄色寄りになりました。濁りが大きいと空が霞んで白く、地平線が黄みがかるという期待どおりの傾向です。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="濁り 2 と 6 の空の色。太陽の高さ 45 度。濁りが大きいと白っぽく、地平線は黄みがかる"><text x="14" y="22" class="fig-title">濁り T の違い（太陽高度 45°。Preetham の式から計算した色）</text>
<rect x="150" y="50" width="120" height="70" rx="8" fill="#91aed7" stroke="#94a3b8"/><rect x="280" y="50" width="120" height="70" rx="8" fill="#92bde2" stroke="#94a3b8"/><rect x="410" y="50" width="120" height="70" rx="8" fill="#e5ebf5" stroke="#94a3b8"/><rect x="540" y="50" width="120" height="70" rx="8" fill="#eaf2fb" stroke="#94a3b8"/><rect x="150" y="140" width="120" height="70" rx="8" fill="#ddedf9" stroke="#94a3b8"/><rect x="280" y="140" width="120" height="70" rx="8" fill="#bbd1df" stroke="#94a3b8"/><rect x="410" y="140" width="120" height="70" rx="8" fill="#d9d3ce" stroke="#94a3b8"/><rect x="540" y="140" width="120" height="70" rx="8" fill="#fefefe" stroke="#94a3b8"/><text x="210" y="40" text-anchor="middle" style="font-size:12px;font-weight:600">天頂</text><text x="340" y="40" text-anchor="middle" style="font-size:12px;font-weight:600">天頂角 60°</text><text x="470" y="40" text-anchor="middle" style="font-size:12px;font-weight:600">地平線近く</text><text x="600" y="40" text-anchor="middle" style="font-size:12px;font-weight:600">太陽の近く</text>
<text x="140" y="92" text-anchor="end" style="font-size:12px;font-weight:600">T = 2（澄んだ）</text><text x="140" y="182" text-anchor="end" style="font-size:12px;font-weight:600">T = 6（霞んだ）</text>
<text x="360" y="236" text-anchor="middle" style="font-size:12px">T が大きいと、天頂が白っぽくなり、地平線が黄みがかる。トーンマップ後の見た目の目安</text></svg>


濁り（turbidity）は 2（澄んだ）から 10（霞んだ）の範囲を使います。大きいほど空が白っぽく霞んで見えます。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で、`SkyPreethamPS` をコンパイルしてエラーが出ないことを確かめました。Python で同じ式を実装して、4 つの方向と 2 つの濁りで色を計算した結果が、空として妥当であることを確かめました。係数表は論文で確かめていません。GPU での描画は確認していません。

## Hošek–Wilkie {#hosek}

Hošek と Wilkie（2012）のモデルは、Preetham の改良版です。太陽が低いときの精度が高く地面の反射率（アルベド）も考慮します。係数テーブル（9 つのパラメータ × 色（スペクトル）× 濁り × アルベド × 太陽の高さ）を公開データとして持ちます。式の形は Preetham に似ていますが、データが大きいことが違いです。このページでは論文を読んでいないので、係数と式の詳細は解説しません。

違いをまとめます。Preetham は精度が太陽の低い時間帯で劣ります。パラメータは濁りだけでデータは数式の係数だけなので少なく、軽量・手軽な用途に向きます。Hošek–Wilkie は精度が高く、パラメータは濁りと地面のアルベドです。係数テーブルが必要で品質を重視する用途に向きます。

## 長所と短所 {#pros-cons}

長所は実行時のコストが小さい（数十命令）ことです。事前計算も LUT も要りません。パラメータが少なく（太陽の高さ濁り）、調整が簡単です。昼のリアルな空が得られます。

短所は太陽が低い時間帯（朝夕）や地平線の下（薄明）で、精度が落ちることです（Preetham。Hošek–Wilkie で改善します）。カメラが地上に固定で高い山、飛行機、宇宙では使えません。空気遠近法（遠景の霞）を別の方法で与える必要があって、空の色と整合させます。濁り以外の大気のパラメータを自由に変えられません。

## 使いどころ {#usage}

- 昼間の地上で時間帯があまり動かないなら適しています。
- 時間帯が動く（朝夕、夜）なら Hošek–Wilkie か Hillaire の方式を使います（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)）。
- 宇宙や高高度は使えません。大気散乱の方式を使います。
- 環境光（IBL）の元に使う場合は、空をキューブマップに描いてライティングの元にします（[Using the Sky for Lighting](sky-lighting.md)）。

## よくあるミス {#mistakes}

??? failure "日没近くで、空の色が不自然"
    原因は Preetham が、太陽が低い時間帯に不正確なことです。Hošek–Wilkie など精度の高いモデルを使います。

??? failure "地平線の近くで、輝度が発散して白飛びする"
    原因は `cos θ` が 0 に近くなって、`exp(B / cos θ)` が暴走することです。`max(cos θ, 0.01)` で下限を設けます。地平線の下は地平線と同じ扱いにします。

??? failure "輝度が大きすぎて、真っ白になる"
    原因は単位が kcd/m² のまま使っていることです。露出で小さく掛けてトーンマップします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 太陽の高さと濁りから、空の輝度と色が式で求まります。軽い式です。
    - [x] Preetham は手軽で、Hošek–Wilkie は朝夕に強いです。
    - [x] 地上から見た空だけで、遠景の霞や宇宙には使えません。
    - [x] 地平線で `exp` が暴走するので、下限を設けます。

## 参考 {#references}

このページは次の資料を読まずに書きました。Preetham の係数表は記憶から書いたもので、論文では確かめていません。結果の妥当性は Python で計算して確かめています。

- Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight", SIGGRAPH 1999
- Hošek, Wilkie, "An Analytic Model for Full Spectral Sky-Dome Radiance", ACM Transactions on Graphics (SIGGRAPH 2012)
- Perez, Seals, Michalsky, "All-Weather Model for Sky Luminance Distribution — Preliminary Configuration and Validation", Solar Energy, Vol. 50, No. 3, 1993
- Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017

## 関連ページ

- [Sky Models](index.md)
- [Atmospheric Scattering](../scattering/index.md)

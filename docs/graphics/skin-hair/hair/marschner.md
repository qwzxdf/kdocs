---
title: Marschner Model
tags:
  - 描画
---

# Marschner Model

[Kajiya-Kay](kajiya-kay.md) は軽い式ですが、髪の光り方を**物理に基づいて**説明するものではありません。Marschner らの "Light Scattering from Human Hair Fibers"（SIGGRAPH 2003）は、実際の髪の毛を測定し、**光が髪の 1 本の内部をどう通るか**を解析して、反射を **3 つの成分**（R・TT・TRT）に分けました。現代のゲームのヘア シェーダーの多くは、この論文の簡略版です。このページでは、3 つの成分の意味、式の構造、ゲーム向けの近似（Karis の方法）を説明します。

!!! tip "ポイント"
    - 髪 1 本を<strong>透明な円柱</strong>とみなし、光の経路を 3 つに分ける。
    - **R**：表面で**反射**（白いハイライト）。**TT**：内部を**通り抜ける**（透け）。**TRT**：内部で**反射して**出る（色付きの 2 本目のハイライト）。
    - 各成分は<strong>縦方向（長手）M</strong>と<strong>横方向（周り）N</strong>の**積**で表す。
    - 縦方向は**ガウス**、横方向は成分ごとの専用の形。**キューティクルの傾き α**が、成分ごとにハイライトをずらす。
    - **色**は、内部を通る距離に応じた**吸収**。TT は 1 回、TRT は 2 回通る。

## 髪の中の光の経路

髪を、屈折率 1.55 の透明な円柱とみなします（実際の髪は、メラニンで色づいた半透明の円柱です）。光が円柱に当たると、3 つの主要な経路に分かれます。

1. <strong>R</strong>（Reflection）：円柱の**表面で反射**します。キューティクルの表面からの反射なので、**色がつかず**（光源の色のまま）、白いハイライトになります。
2. <strong>TT</strong>（Transmission-Transmission）：円柱の**内部に入り**（屈折）、**反対側から出ます**（屈折）。内部を 1 回通るので、髪の色が 1 回ぶん付きます。光源が髪の後ろにあるときに、**髪が透けて**明るく見える成分です。
3. <strong>TRT</strong>（Transmission-Reflection-Transmission）：内部に入り、**反対側の内面で反射して**、また内部を通り、入った側から出ます。内部を 2 回通るので、色が 2 回ぶん付き、**濃く色づいた**光になります。これが 2 本目のハイライトです。

これらの経路が、**円柱の周りのどの角度で起きるか**によって、光の出る方向が違います。R は鏡のように、入射と反対側の方向に出ます。TT は、入った方向と同じ側（前方）へ、ほぼまっすぐ通り抜けます。TRT は、入射方向に戻るように出ます（後方）。

## 縦方向と横方向

Marschner のモデルは、髪の反射を、**髪の軸に沿った角度**（縦方向、longitudinal）と、**軸の周りの角度**（横方向、azimuthal）の 2 つに**分けて**、積で表します。

<div class="formula">S(ω_i, ω_o) = Σ_p M_p(θ_i, θ_o) · N_p(φ) / cos²θ_d　　p ∈ {R, TT, TRT}</div>

θ_i と θ_o は、入射と出射の方向が、髪の軸に垂直な面となす角（縦方向の角度）。φ は、軸の周りの、入射と出射の方位角の差（横方向の角度）です。θ_d は、θ_i と θ_o の差の半分です。

### 縦方向 M_p：ガウス

縦方向の関数 M_p は、**ガウス分布**で表します。

<div class="formula">M_p(θ_h) = g(β_p; θ_h − α_p)　　θ_h = (θ_i + θ_o)/2　　g(β; x) = exp(−x²/2β²) / (β√(2π))</div>

θ_h は入射と出射の平均の角度です。α_p は、成分 p のハイライトの**ずれ**（シフト）、β_p はその**幅**です。この α_p が、**キューティクルの傾き**に由来します。髪の表面のうろこ状のキューティクルが、わずかに傾いているため、反射の中心が、鏡面の位置からずれるのです。論文の結論は、3 つの成分でずれと幅の関係が決まっていることです。R のずれを α とすると、TT のずれは −α/2、TRT のずれは −3α/2 です。幅は、R を β とすると、TT は β/2、TRT は 2β です。つまり、**TT は鋭く、TRT は広い**。そして、**R・TT・TRT のハイライトは、それぞれ髪の軸に沿って少しずつ位置がずれる**のです。これが、2 本のハイライトが分かれて見える理由です。

### 横方向 N_p：成分ごとの形

横方向の関数 N_p は、成分ごとに形が違います。論文では、円柱の幾何学（屈折の角度の計算）から求められ、複雑です。

R は、円柱の表面での反射なので、比較的単純です。横方向の依存は、およそ `cos(φ/2)` に比例します。つまり、光が円柱の正面から当たり、真後ろへ反射する方向が最も強くなります。

TT は、円柱を通り抜けて、前方へ出る成分です。横方向では、φ が 180°（前方）の近くで強い、狭いピークを持ちます。

TRT は、内部で反射して戻ってくる成分で、横方向の分布が、**複雑な形**を持ちます。**コースティクス**（光が集まる線）を作り、分布に鋭いピークが現れます。

## ゲーム向けの近似（Karis）

論文の式を、そのまま実装するのは重いので、ゲームでは簡略化します。Karis（Epic Games）の "Physically Based Hair Shading in Unreal"（SIGGRAPH 2016）は、Unreal Engine で使われる近似です。

縦方向は、ガウスを使います。

```hlsl
float Hair_G(float beta, float theta) {
  return exp(-0.5 * theta * theta / (beta * beta)) / (sqrt(2.0 * 3.14159265) * beta);
}
```

横方向は、次の近似式を使います。φ の cos を `cos_phi` とします。

```hlsl
float Hair_N_R(float cos_phi_half) { return 0.25 * cos_phi_half; }
float Hair_N_TT(float cos_phi) { return exp(-3.65 * cos_phi - 3.98); }
float Hair_N_TRT(float cos_phi) { return exp(17.0 * cos_phi - 16.78); }
```

R は `cos(φ/2)/4`、TT は `cos φ` が −1（前方）で最大になる指数関数、TRT は `cos φ` が 1（入射方向に戻る）に近いところで鋭いピークを持つ指数関数です。数値の定数（3.65、3.98、17、16.78）は、論文のモデルに合わせたフィッティング値です。

色は、**内部を通る回数**で決めます。

* R：色なし（光源の色のまま）。フレネルを掛けます。
* TT：髪の色を 1 回掛ける（内部を 1 回通る）。
* TRT：髪の色を 2 回掛ける（内部を 2 回通る）。つまり、髪の色の 2 乗です。

髪の色は、メラニンの量で決まる吸収を表すので、色の 2 乗が TRT の色になる、というのは、「通る距離が 2 倍だと、減衰が 2 乗になる」という Beer-Lambert の法則そのものです。

```hlsl
float3 HairMarschner(float3 t, float3 l, float3 v, float3 base_color, float roughness, float shift) {
  float sin_theta_i = dot(t, l);
  float sin_theta_o = dot(t, v);
  float theta_i = asin(sin_theta_i);
  float theta_o = asin(sin_theta_o);
  float theta_h = (theta_i + theta_o) * 0.5;
  float theta_d = (theta_i - theta_o) * 0.5;

  float3 l_perp = l - sin_theta_i * t;
  float3 v_perp = v - sin_theta_o * t;
  float cos_phi = dot(normalize(l_perp), normalize(v_perp));
  float cos_phi_half = sqrt(0.5 + 0.5 * cos_phi);

  float beta = roughness * roughness;
  float alpha = shift;

  float m_r = Hair_G(beta * 0.5, theta_h - alpha);
  float m_tt = Hair_G(beta * 0.25, theta_h + alpha * 0.5);
  float m_trt = Hair_G(beta * 1.0, theta_h + alpha * 1.5);

  float3 r = m_r * Hair_N_R(cos_phi_half) * float3(1, 1, 1);
  float3 tt = m_tt * Hair_N_TT(cos_phi) * base_color;
  float3 trt = m_trt * Hair_N_TRT(cos_phi) * base_color * base_color;

  float cos_theta_d = cos(theta_d);
  return (r + tt + trt) / (cos_theta_d * cos_theta_d);
}
```

このコードは、考え方を示す簡略版です。実際には、フレネルや、エネルギー保存の補正、粗さ（β）から幅への変換などの詳細が加わります。

## 多重散乱：Dual Scattering

Marschner のモデルは、**1 本の髪**への光の散乱を扱います。実際の頭髪は、何万本もの髪が重なり、光が髪から髪へ何度も散乱します。特に**金髪や白髪のような明るい髪**では、髪の内部の吸収が少ないので、多重散乱が重要で、髪全体が柔らかく発光して見えます。

多重散乱は、Zinke らの **Dual Scattering**（"Dual Scattering Approximation for Fast Multiple Scattering in Hair"、SIGGRAPH 2008）で近似されます。考え方は、多重散乱を**2 つの成分**に分けることです。**グローバル多重散乱**は、光が髪の層を通り抜けるときの、前方への散乱で、髪の厚みが増すほど、光が柔らかく広がります。**ローカル多重散乱**は、注目している点のすぐ近くの髪どうしの散乱で、反射を拡散的にします。結果は、各点で、光源からその点までの髪の本数（深さ）から、解析的な式で計算できます。ゲームでは、これを簡略化して、**髪全体に柔らかい拡散光を足す**項として使います。

## Kajiya-Kay との違い

Marschner の方式の利点は、物理的な意味があることです。R・TT・TRT の 3 成分があるので、逆光での**透け**（TT）と、**2 本目の色付きハイライト**（TRT）が、自然に出ます。髪の色（メラニン）と粗さの 2 つのパラメータで、黒髪から金髪まで、一貫した見た目を作れます。エネルギー保存も、補正すれば満たせます。

短所は、計算が重いことです。ピクセルごとに、複数の三角関数と指数関数を計算します。カードに対する、ピクセル数の多いキャラクターでも、Kajiya-Kay よりは重くなります。また、パラメータが物理量なので、アーティストにとっては、見た目の調整が直感的でないことがあります。そのため、多くのゲームは、Kajiya-Kay を基本に、必要に応じて Marschner の考え方（透けの項）を足す、という折衷を取ります。

## よくあるミス

??? failure "TT の項を入れず、逆光でも髪が真っ暗になる"
    **TT（透過）**の項を足す。**光源が髪の後ろ**にあるとき、髪が明るく透ける。

??? failure "TRT のハイライトが、白くなる"
    TRT は**髪の色の 2 乗**を掛けて、**色付き**にする。

??? failure "接線の向きが逆で、ハイライトの位置が上下で入れ替わる"
    α のずれは、**接線の向き**（根元から毛先か）に依存する。**符号を確認**する。

??? failure "粗さを上げても、ハイライトの幅が変わらない"
    β は粗さから決まる。**R・TT・TRT で幅の比（1 : 1/2 : 2）を保つ**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 髪の反射を<strong>R（反射）・TT（透過）・TRT（内部反射）</strong>の 3 成分に分ける
    - [x] 各成分 ＝ <strong>縦方向 M（ガウス）× 横方向 N</strong>。**キューティクルの傾き α でハイライトがずれる**
    - [x] 色は<strong>内部を通る回数</strong>。TT は髪の色、TRT は**髪の色の 2 乗**
    - [x] ゲームでは **Karis の近似**。**金髪には多重散乱（Dual Scattering）**

## 参考

- Marschner, Jensen, Cammarano, Worley, Hanrahan, "Light Scattering from Human Hair Fibers"（SIGGRAPH 2003）
- d'Eon, Francois, Hill, Dias, Burke, Cani, "An Energy-Conserving Hair Reflectance Model"（Eurographics Symposium on Rendering 2011）
- Zinke, Yuksel, Weber, Keyser, "Dual Scattering Approximation for Fast Multiple Scattering in Hair"（SIGGRAPH 2008）
- Karis, "Physically Based Hair Shading in Unreal"（SIGGRAPH 2016 Physically Based Shading in Theory and Practice）

## 関連ページ

- [Hair Overview](index.md)
- [Kajiya-Kay](kajiya-kay.md)
- [Hair Shadows](shadows.md)
- [PBR](../../../3d/pbr.md)

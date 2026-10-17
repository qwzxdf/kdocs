---
title: 大気散乱
tags:
  - 描画
---

# 大気散乱

**空の青さ・夕焼けの赤さ・遠景の霞**は**光が大気の中で「散らされる」ことで生じます**。**物理に基づいた空**を作るには、**視線に沿って大気を積分し、その途中で散る光を足し合わせます**。計算は重いので**あらかじめ表（LUT）に計算しておく**のが**現代の定番**です。このページでは、**レイリー散乱とミー散乱・透過率・単散乱の積分・位相関数・Bruneton の事前計算・Hillaire 2020 の 4 つの LUT**を説明します。

!!! tip "ポイント"
    - 大気の散乱は<strong>2 種類</strong>：<strong>レイリー散乱</strong>（<strong>空気分子。波長の 4 乗に反比例 → 青が強く散る</strong>）と、<strong>ミー散乱</strong>（<strong>エアロゾル。波長にほぼ依らず、前方に強く散る</strong>）。
    - 光は大気を通る間に<strong>減る（透過率 T = e^(−τ)）</strong>。<strong>τ は光学的厚さ</strong>。
    - 空の色 ＝ <strong>視線に沿った積分</strong>：<strong>各点で太陽光が届き（透過）、視線方向へ散る（位相関数）</strong>。
    - <strong>大気は球殻</strong>（地球の半径 6360 km、厚さ 約 100 km）で、<strong>密度は高さで指数的に減る</strong>。
    - <strong>事前計算した LUT</strong>（Bruneton：3D、Hillaire：小さな 2D/3D）で、<strong>実行時は表引き</strong>。
    - Hillaire 2020 は <strong>Transmittance・Multi-Scattering・Sky-View・Aerial Perspective の 4 つの LUT</strong>。<strong>動的な時刻変化に強い</strong>。

## なぜ空は青いか

**太陽光は白色**（全波長を含む）ですが**大気の分子に当たると短い波長（青）ほど強く散らされます**。

<div class="formula">レイリー散乱の強さ ∝ 1 / λ⁴</div>

| 波長 | 色 | 相対的な散乱の強さ |
| --- | --- | --- |
| **700 nm** | **赤** | **1.0** |
| **550 nm** | **緑** | **約 2.6** |
| **450 nm** | **青** | **約 5.9** |

**青い光が全方向に散って空が青く見えます**。**夕方は太陽の光が大気を長く通り、青が散り尽くして赤だけが残る**ので、**太陽が赤く、空が赤く染まります**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="夕焼けの理由">
<text x="20" y="24" class="fig-title">昼と夕方：光が通る大気の長さが違う</text>
<path d="M60,220 A320,320 0 0 1 720,220" fill="none" stroke="#4c8bf5" stroke-opacity="0.5" stroke-width="22"/>
<line x1="60" y1="220" x2="720" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<circle cx="390" cy="220" r="5" fill="#e5484d"/>
<text x="400" y="240" style="font-size:12px">観測者</text>
<line x1="390" y1="60" x2="390" y2="215" stroke="#e5aa28" stroke-width="3"/>
<text x="398" y="110" style="font-size:12px">昼：大気を短く通る → 白い</text>
<line x1="80" y1="190" x2="385" y2="218" stroke="#e5484d" stroke-width="3"/>
<text x="110" y="180" style="font-size:12px">夕方：大気を長く通る → 赤い</text>
</svg>

## 大気のモデル

**地球の大気は球殻**です。**密度は高さに対して指数的に減ります**。

<div class="formula">ρ(h) = exp( −h / H )　（H：スケール ハイト）</div>

| 成分 | スケール ハイト H | 特徴 |
| --- | --- | --- |
| <strong>レイリー（空気分子）</strong> | **約 8 km** | **青く散る。後ろにも前にも均等に** |
| <strong>ミー（エアロゾル）</strong> | **約 1.2 km** | <strong>ほぼ白く散る。前方に強い（太陽の周りのにじみ）</strong> |
| **オゾン** | **高さ 25 km 付近に層** | **散らさず、吸収する**（**朝夕の空の青みの基**） |

**地球の半径は 6360 km、大気の上端は 6460 km**（高さ 100 km）です。

| 係数 | 意味 |
| --- | --- |
| **散乱係数 σs** | **単位長さあたり、散らされる割合**（RGB で違う） |
| **吸収係数 σa** | **単位長さあたり、吸われる割合** |
| **消散係数 σt = σs + σa** | **減る割合の合計** |

<strong>レイリー散乱係数（海面）</strong> は、**RGB で (5.8, 13.5, 33.1) × 10⁻⁶ /m** 程度（**青が大きい**）、**ミー散乱は (3.9, 3.9, 3.9) × 10⁻⁶ /m** 程度です。

## 透過率

**光が距離 d を進むと、強さは指数的に減ります**（Beer–Lambert の法則）。

<div class="formula">T(a → b) = exp( −∫ σt(s) ds )　（光学的厚さ τ = ∫ σt ds）</div>

```hlsl
float3 Transmittance(float3 start, float3 end, int steps) {
  float3 delta = (end - start) / steps;
  float step_length = length(delta);
  float3 optical_depth = 0;
  for (int i = 0; i < steps; ++i) {
    float3 p = start + delta * (i + 0.5);
    float h = length(p) - kPlanetRadius;
    float3 extinction = kRayleighScattering * exp(-h / kRayleighScaleHeight)
                      + kMieExtinction * exp(-h / kMieScaleHeight)
                      + kOzoneAbsorption * OzoneDensity(h);
    optical_depth += extinction * step_length;
  }
  return exp(-optical_depth);
}
```

| 点 | 説明 |
| --- | --- |
| **中点法** | **各区間の中点で密度を取る** |
| **色ごとに別の値** | **RGB の消散係数が違う → 青が先に減る** |
| **球の外・内** | <strong>地面にぶつかる向きは、光が届かない（T = 0 扱い）</strong> |

## 単散乱の積分

**視線に沿った各点で、「太陽光が届く量」×「視線方向へ散る割合」を足し合わせる**のが**空の色**です。

<div class="formula">L = ∫ T(カメラ → p) · σs(p) · P(θ) · T(p → 太陽) · E_sun ds</div>

| 項 | 意味 |
| --- | --- |
| <strong>T(カメラ → p)</strong> | **点 p から、カメラまで届く間の減衰** |
| <strong>σs(p)</strong> | **点 p の散乱係数**（高さで決まる） |
| <strong>P(θ)</strong> | **位相関数**：**太陽の向きから視線の向きへ、どれだけ散るか** |
| <strong>T(p → 太陽)</strong> | **太陽から点 p まで届く間の減衰** |
| **E_sun** | **大気の外での太陽の強さ** |

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="単散乱">
<text x="20" y="24" class="fig-title">単散乱：視線の上の各点で、太陽光が届いて、視線方向へ散る</text>
<path d="M60,230 A320,320 0 0 1 720,230" fill="none" stroke="#4c8bf5" stroke-opacity="0.35" stroke-width="30"/>
<circle cx="200" cy="225" r="6" fill="#e5484d"/><text x="150" y="248" style="font-size:12px">カメラ</text>
<line x1="200" y1="225" x2="500" y2="90" stroke="currentColor" stroke-width="2"/>
<circle cx="330" cy="166" r="4" fill="#2ea043"/><circle cx="400" cy="135" r="4" fill="#2ea043"/><circle cx="460" cy="108" r="4" fill="#2ea043"/>
<line x1="330" y1="40" x2="330" y2="166" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<line x1="400" y1="40" x2="400" y2="135" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<line x1="460" y1="40" x2="460" y2="108" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<text x="540" y="60" style="font-size:12px;fill:#e5aa28">太陽光（平行）</text>
<text x="520" y="100" style="font-size:12px">視線を刻んで、各点の寄与を足す</text>
</svg>

```hlsl
float3 SingleScattering(float3 ray_origin, float3 ray_dir, float ray_length, float3 sun_dir, int steps) {
  float step_length = ray_length / steps;
  float3 rayleigh_sum = 0;
  float3 mie_sum = 0;
  float3 optical_depth_view = 0;

  float cos_theta = dot(ray_dir, sun_dir);
  float phase_r = RayleighPhase(cos_theta);
  float phase_m = HenyeyGreenstein(cos_theta, kMieG);

  for (int i = 0; i < steps; ++i) {
    float3 p = ray_origin + ray_dir * (i + 0.5) * step_length;
    float h = length(p) - kPlanetRadius;
    float density_r = exp(-h / kRayleighScaleHeight);
    float density_m = exp(-h / kMieScaleHeight);

    optical_depth_view += (kRayleighScattering * density_r + kMieExtinction * density_m) * step_length;

    float3 optical_depth_sun = SunOpticalDepth(p, sun_dir);
    float3 attenuation = exp(-(optical_depth_view + optical_depth_sun));

    rayleigh_sum += attenuation * density_r * step_length;
    mie_sum += attenuation * density_m * step_length;
  }
  return sun_intensity * (kRayleighScattering * phase_r * rayleigh_sum
                        + kMieScattering * phase_m * mie_sum);
}
```

| 点 | 説明 |
| --- | --- |
| **`SunOpticalDepth`** | **点 p から太陽方向へ、大気の外まで進んだ光学的厚さ**（**内側のループ**。**地面で遮られる向きは 0**） |
| **二重ループ** | **視線 16 ステップ × 太陽 8 ステップ**で **128 回の密度計算**。**リアルタイムには重い** |
| **レイリーとミーを別々に足す** | **位相関数が違うため** |

## 位相関数

<strong>位相関数 P(θ)</strong> は、**散乱の方向分布**です。**θ は元の光の進行方向と散乱後の方向のなす角**です。

### レイリー

<div class="formula">P_R(θ) = (3 / 16π) · (1 + cos²θ)</div>

**前後に対称**で**横方向へ少し弱い**形です。

### ミー（Henyey-Greenstein）

<div class="formula">P_HG(θ) = (1 / 4π) · (1 − g²) / (1 + g² − 2g·cosθ)^(3/2)</div>

| g | 意味 |
| --- | --- |
| **0** | <strong>等方（全方向に均等）</strong> |
| **0.76 付近** | **大気のミー散乱：前方に強く散る**（**太陽の周りが明るくにじむ**） |
| **負** | **後方へ散る** |

```hlsl
float RayleighPhase(float cos_theta) {
  return 3.0 / (16.0 * 3.14159265) * (1.0 + cos_theta * cos_theta);
}

float HenyeyGreenstein(float cos_theta, float g) {
  float g2 = g * g;
  float denom = 1.0 + g2 - 2.0 * g * cos_theta;
  return (1.0 - g2) / (4.0 * 3.14159265 * pow(denom, 1.5));
}
```

**雲や霧の散乱**（[雲](clouds.md)・[ボリューメトリック フォグ](volumetric-fog.md)）も、**同じ位相関数**を使います。

## 多重散乱

**単散乱だけだと夕方や影の側の空が暗くなりすぎます**。**実際には一度散った光が何度も散ります**（**多重散乱**）。**地球の大気では、昼間の空の明るさの 1〜2 割は多重散乱**で、**夕暮れの空の明るさは多重散乱で決まります**。

| 近似 | 内容 |
| --- | --- |
| **ambient の底上げ** | **単散乱に一定の環境光を足す**（手軽・粗い） |
| **Bruneton の多重散乱** | **散乱次数ごとに事前計算を繰り返す**（正確・重い） |
| **Hillaire の近似** | **多重散乱を等方・無限級数の閉じた式で近似**し、**小さな 2D LUT にまとめる**（軽い） |

## Bruneton の事前計算

<strong>Bruneton & Neyret（2008）</strong>は、**単散乱・多重散乱をすべて 4D のテーブルに事前計算**し、**実行時は表引き**で空を描きます。

| 項目 | 内容 |
| --- | --- |
| **4 つの次元** | **観測者の高さ・視線の天頂角・太陽の天頂角・視線と太陽の方位角差** |
| **3D テクスチャに詰める** | **4D を 3D テクスチャに展開**（**方位角を横に並べる**） |
| **利点** | **実行時は数回のサンプルだけ**。**多重散乱込みで正確** |
| **欠点** | **事前計算が重い**。**時刻や大気の組成を変えると、計算し直し**（**太陽の位置は表の次元にあるので動かせる**が、**大気の密度は固定**） |
| **用途** | **地上〜宇宙まで**、**大気の組成が固定**のゲーム |

## Hillaire 2020：4 つの LUT

<strong>Hillaire（2020, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"）</strong>は、**軽い LUT を毎フレーム更新する**方式です。**大気の組成（霧の濃さ・時間帯）を動的に変えられる**のが**強み**で、**Unreal Engine の SkyAtmosphere**などに**使われています**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="Hillaire の 4 つの LUT">
<text x="20" y="24" class="fig-title">Hillaire 2020：4 つの LUT</text>
<rect x="30" y="60" width="160" height="70" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/>
<text x="110" y="88" text-anchor="middle" style="font-size:13px">透過率 LUT</text><text x="110" y="108" text-anchor="middle" style="font-size:11px">256×64（2D）</text>
<rect x="210" y="60" width="160" height="70" rx="6" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043"/>
<text x="290" y="88" text-anchor="middle" style="font-size:13px">多重散乱 LUT</text><text x="290" y="108" text-anchor="middle" style="font-size:11px">32×32（2D）</text>
<rect x="390" y="60" width="160" height="70" rx="6" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28"/>
<text x="470" y="88" text-anchor="middle" style="font-size:13px">スカイビュー LUT</text><text x="470" y="108" text-anchor="middle" style="font-size:11px">192×108（2D）</text>
<rect x="570" y="60" width="180" height="70" rx="6" fill="#e5484d" fill-opacity="0.2" stroke="#e5484d"/>
<text x="660" y="88" text-anchor="middle" style="font-size:13px">空気遠近法 LUT</text><text x="660" y="108" text-anchor="middle" style="font-size:11px">32×32×32（3D）</text>
<text x="110" y="160" text-anchor="middle" style="font-size:11px">高さ × 太陽角 →</text><text x="110" y="176" text-anchor="middle" style="font-size:11px">太陽までの透過率</text>
<text x="290" y="160" text-anchor="middle" style="font-size:11px">高さ × 太陽角 →</text><text x="290" y="176" text-anchor="middle" style="font-size:11px">多重散乱の寄与</text>
<text x="470" y="160" text-anchor="middle" style="font-size:11px">視線の向き →</text><text x="470" y="176" text-anchor="middle" style="font-size:11px">空の色（全天）</text>
<text x="660" y="160" text-anchor="middle" style="font-size:11px">カメラ前方の froxel →</text><text x="660" y="176" text-anchor="middle" style="font-size:11px">散乱光と透過率</text>
<text x="390" y="230" text-anchor="middle" style="font-size:13px">毎フレーム、順に更新：透過率 → 多重散乱 → スカイビュー → 空気遠近法</text>
</svg>

| LUT | 内容 |
| --- | --- |
| **透過率 LUT** | <strong>(高さ, 太陽の天頂角) → 大気の外までの透過率</strong>（**ほぼ固定。大気の組成が変わると更新**） |
| **多重散乱 LUT** | <strong>(高さ, 太陽の天頂角) → 多重散乱の寄与</strong>（**近似**） |
| **スカイビュー LUT** | **カメラ位置での全方向の空の色**（**緯度経度で圧縮**。**地平線付近を細かく取る**） |
| **空気遠近法 LUT** | **カメラ前方の froxel**（**視錐台の 3D 格子**）**ごとの散乱光と透過率**。**物体への霞に使う**（[距離フォグ](aerial-fog.md)） |

### スカイビュー LUT の工夫

**空の色は地平線付近で急に変わります**。**天頂角をそのまま格子にすると、地平線の解像度が足りません**。**非線形な割り当て**で**地平線付近を細かく取ります**。

```hlsl
float SkyViewV(float view_zenith_cos, float horizon_cos) {
  float v;
  if (view_zenith_cos > horizon_cos) {
    float t = (view_zenith_cos - horizon_cos) / (1.0 - horizon_cos);
    v = 0.5 + 0.5 * sqrt(t);
  } else {
    float t = (horizon_cos - view_zenith_cos) / (horizon_cos + 1.0);
    v = 0.5 - 0.5 * sqrt(t);
  }
  return v;
}
```

**平方根で割り当てる**ことで、**地平線の周り（v = 0.5）が細かく**なります。

### 実行時の流れ

| 手順 | 内容 |
| --- | --- |
| **① LUT 更新** | **透過率・多重散乱・スカイビュー・空気遠近法**を**コンピュートで更新** |
| **② 空を描く** | **ピクセルの視線から、スカイビュー LUT を引く**（1 回の表引き） |
| **③ 太陽の円盤** | **透過率 LUT で減衰させて足す** |
| **④ 物体にかける** | **空気遠近法 LUT で、物体の色を霞ませる**（[距離フォグ](aerial-fog.md)） |

**LUT は小さい**ので<strong>毎フレーム更新しても軽く（0.1〜0.3 ms 程度）</strong>、**時刻・天気・大気の濃さを動的に変えられます**。

## 地面と宇宙

| 状況 | 扱い |
| --- | --- |
| **地面の反射** | **地面のアルベドで地平線付近が明るくなる**。**地面からの散乱を足す** |
| **宇宙から見た地球** | **視点が大気の外のとき、大気の入口まで進めてから積分**（**惑星表面の光る縁**） |
| **日食・月食** | **太陽の円盤が欠けるとき、直射光を減らす** |
| **影の中の空気** | **山の影で空気中の光の筋が途切れる**（[光の筋](god-rays.md)） |

## よくあるミス

??? failure "空が白っぽく、青くならない"
    **レイリー係数が、RGB で同じ**になっている。**青を大きく（5.8, 13.5, 33.1）にする**。

??? failure "夕方に空が真っ黒になる"
    **多重散乱が無い**。**環境光を足すか、多重散乱 LUT を使う**。

??? failure "地面の下にも空が見える／地平線がぼやける"
    **地面（惑星）との交差を判定**し、**スカイビュー LUT の地平線付近を細かく取る**。

??? failure "LUT の境界で、色が段になる"
    **LUT のサンプルを半テクセルずらして補間**する（**UV を `(u * (N − 1) + 0.5) / N`** に直す）。

??? failure "単位が混ざって、太陽が暗い／明るすぎる"
    **距離をメートルか、キロメートルに統一**する。**係数の単位（/m または /km）を合わせる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の青 ＝ <strong>レイリー散乱（1/λ⁴）</strong>。<strong>夕焼けの赤 ＝ 青が散り尽くす</strong>
    - [x] <strong>ミー散乱</strong>は<strong>白く・前方に強い</strong>（<strong>Henyey-Greenstein, g ≈ 0.76</strong>）
    - [x] 空の色 ＝ <strong>視線に沿った積分</strong>：<strong>透過率 × 散乱係数 × 位相関数 × 太陽側の透過率</strong>
    - [x] <strong>多重散乱</strong>がないと<strong>夕方が暗すぎる</strong>
    - [x] <strong>実用は LUT</strong>：<strong>Bruneton（4D 事前計算）</strong>か<strong>Hillaire 2020（4 つの軽い LUT）</strong>

## 参考

- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Nishita et al., "Display of The Earth Taking into Account Atmospheric Scattering"（SIGGRAPH 1993）
- O'Neil, "Accurate Atmospheric Scattering"（GPU Gems 2）

## 関連ページ

- [空と大気](index.md)
- [空のモデル](sky-models.md)
- [距離フォグ](aerial-fog.md)
- [ボリューメトリック フォグ](volumetric-fog.md)
- [雲](clouds.md)

---
title: Hemisphere SSAO
tags:
  - 描画
---

# Hemisphere SSAO

<strong>半球 SSAO</strong>（Normal-oriented Hemisphere SSAO）は、[Crytek SSAO](ssao-crytek.md)の球を法線の側の半球に変えた方式です。これだけで平らな面が灰色になる問題が消え、見た目が大きく改善します。現在、「SSAO」と言えば、この方式を指すことが多く、チュートリアルや多くのゲームで使われる、標準的な SSAO です。このページでは、原理・サンプルの作り方・コード・調整を順に説明します。

!!! tip "ポイント"
    - 入力は<strong>深度（位置）と法線</strong>。法線は G-Buffer から、または深度から復元する。
    - サンプルは<strong>法線の側の半球</strong>（接空間で z ≥ 0）に置く。平らな面では遮蔽 0（明るい）になる。
    - 画素ごとにランダムな軸でサンプルを回転（TBN をランダム ベクトルから作る）。タンジェントは不要。
    - 判定は Crytek と同じ（投影して深度を比べる）。バイアス・範囲チェックが重要。
    - 後処理はぼかし（ランダム パターンと同じ周期のボックス ぼかしが定番）。
    - コサイン重み付きにするなら、サンプルを法線に寄せる（分布を工夫する）。

!!! info "このページを読む前に"
    - [Ambient Occlusion (AO)](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## Crytek 方式からの変更点

| 項目 | Crytek 方式 | 半球 SSAO |
| --- | --- | --- |
| サンプルの領域 | 球 | 法線側の半球 |
| 入力 | 深度のみ | 深度 ＋ 法線 |
| 平らな面 | 約 50% が遮られ、灰色 | <strong>遮蔽なし（明るい）</strong> |
| ランダム化 | サンプル ベクトルを鏡映 | 接空間（TBN）をランダムに回す |
| コスト | 同程度 | わずかに増える（法線の読み込み） |


1 つ目は、サンプルを置く領域を球から、法線側の半球に変えたことです。これで、平らな面では約 50 % が遮られて灰色になる問題がなくなり、遮蔽がない面は明るいままになります。2 つ目は、入力に法線が加わったことです。深度のみだった入力が、深度と法線になり、法線を読む分のコストがわずかに増えます。3 つ目は、ランダム化の方法です。Crytek 方式はサンプル ベクトルを鏡映していましたが、半球 SSAO は接空間（TBN）をランダムに回します。サンプルの半球が、常に法線を向いたまま回転するわけです。4 つ目のコストは、同程度です。

1 つ目は、サンプルを置く領域を球から、法線側の半球に変えたことです。これで、平らな面では約 50 % が遮られて灰色になる問題がなくなり、遮蔽がない面は明るいままになります。2 つ目は、入力に法線が加わったことです。深度のみだった入力が、深度と法線になり、法線を読む分のコストがわずかに増えます。3 つ目は、ランダム化の方法です。Crytek 方式はサンプル ベクトルを鏡映していましたが、半球 SSAO は接空間（TBN）をランダムに回します。サンプルの半球が、常に法線を向いたまま回転するわけです。4 つ目のコストは、同程度です。

!!! info "ここで使われる「積分」を、やさしく言うと"
    Hemisphere SSAO の積分も、Crytek SSAO と同じ、ランダムな点を撒いて、遮られた割合を数える（モンテカルロ法）です。違いは、点を撒く場所が、法線の向きの半球だけ、という点です。

    - 面の下側に、点を撒かないので、平らな面が、灰色にならない。
    - 点は、面の近くに、多く（`scale` で、近くに寄せる）。近い遮蔽物ほど、AO に効くため。
    - 点の数は 16 前後。足りない分は、ノイズとぼかしで、ごまかす。

    数式を使わない、くわしい説明は [Integrals and Elevation Angles in Plain Words](theory/integral-intuition.md) です。

## 半球のサンプルを作る

<strong>接空間</strong>（法線を z 軸とした座標系）で、z が 0 以上のベクトルを作ります。これが半球です。

```cpp
std::vector<Vector3> MakeHemisphereKernel(int n, std::mt19937& rng) {
  std::uniform_real_distribution<float> unit(-1.0f, 1.0f);
  std::uniform_real_distribution<float> zero_one(0.0f, 1.0f);
  std::vector<Vector3> kernel;
  for (int i = 0; i < n; ++i) {
    Vector3 v(unit(rng), unit(rng), zero_one(rng));
    v.Normalize();
    v *= zero_one(rng);
    float t = static_cast<float>(i) / static_cast<float>(n);
    float scale = std::lerp(0.1f, 1.0f, t * t);
    kernel.push_back(v * scale);
  }
  return kernel;
}
```

このコードの工夫は 4 つあります。`z` を 0〜1 の範囲にすることで、正の側だけ、つまり半球になります。`v *= zero_one(rng)` で長さをランダムにして、中心からの距離を一様にばらつかせます。`scale = lerp(0.1, 1.0, t²)` で、原点に近いサンプルを多くします。近くの遮蔽ほど強く効かせたいためです。サンプル数は 8〜16 が実用的で、64 は多すぎます（学習用の値です）。

### サンプルの分布と、コサイン重み

[理論](theory/index.md)の AO はコサイン重み付きの積分でした。法線に近い方向のサンプルが、より重要です。上の分布は一様な半球なので、法線方向に特別に寄せてはいません（コサイン重みを無視した近似です）。コサイン重みを正しく扱うなら、コサイン分布のサンプルを使います。

一様な半球は、半球上で方向を一様に選びます。この分布は、横方向（水平寄り）の遮蔽に必要以上に敏感になります。コサイン分布は、`x = √u1 cos(2πu2)`、`y = √u1 sin(2πu2)`、`z = √(1 − u1)` で作り、法線付近の方向を多く選びます。このとき、モンテカルロの V の割合が、そのまま AO になります（[理論](theory/index.md)のとおり、重みが分布に吸収されるためです）。

```cpp
Vector3 CosineSample(float u1, float u2) {
  float r = std::sqrt(u1);
  float phi = 2.0f * std::numbers::pi_v<float> * u2;
  return Vector3(r * std::cos(phi), r * std::sin(phi), std::sqrt(1.0f - u1));
}
```

## TBN をランダムに作る

<strong>サンプルをビュー空間に持ってくる</strong>ために、法線を z 軸とした座標系（TBN）が必要です。普通はメッシュの接線を使いますが、SSAO ではランダム ベクトルから作ります。画素ごとに軸まわりに回す効果も同時に得られます。

<div class="formula">tangent = normalize( random − normal · dot(random, normal) )、　bitangent = cross(normal, tangent)</div>

グラム・シュミットの直交化です。ランダム ベクトルから、法線方向の成分を引くと、法線に垂直なベクトル（タンジェント）が得られます。

```hlsl
float3 random_vec = normalize(float3(noise_tex.Sample(wrap_sampler, uv * noise_scale).xy, 0.0));
float3 tangent = normalize(random_vec - normal * dot(random_vec, normal));
float3 bitangent = cross(normal, tangent);
float3x3 tbn = float3x3(tangent, bitangent, normal);
```

ノイズ テクスチャは 4×4 の `float2`（z は 0）で、ラップ（繰り返し）設定にして画面全体に貼ります。`noise_scale` は `screen_size / 4` で、4 画素ごとにパターンが繰り返されます。接線は、ランダム ベクトルから法線方向の成分を引いて作る（グラム・シュミット）ので、メッシュに接線データがなくても、法線だけで TBN が組めます。`cross(normal, tangent)` の向きは、このサイトの座標系（左手系）の規約のままです（外積の向きは[ベクトル](../../gamemath/vectors.md)を参照）。

<!-- fig:ssao-samples:begin -->

<svg class="fig illust motion" data-fig="ssao-samples" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ssao-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">SSAO: 周りの深度を調べて、「どれくらい囲まれているか」を数える</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面(横から見た図)で、ピクセル 1 つぶんの調べ方 → 全ピクセルに広げる</text>
<rect x="30" y="90" width="490" height="274" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="80" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 断面と、深度バッファ(各列の見える高さ)</text>
<rect x="120.0" y="294.8" width="20.0" height="35.2" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="140.0" y="294.8" width="20.0" height="35.2" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="260.0" y="242.0" width="20.0" height="88.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="280.0" y="132.0" width="20.0" height="198.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="300.0" y="132.0" width="20.0" height="198.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="320.0" y="132.0" width="20.0" height="198.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<line x1="40.0" y1="330.0" x2="520.0" y2="330.0" stroke="#94a3b8" stroke-width="2"/>
<text x="30" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">深度バッファ(明るい = カメラに近い)</text>
<rect x="40.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="60.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="80.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="100.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="120.0" y="398" width="19.0" height="26" fill="#626262" stroke="#94a3b8" stroke-width="1"/>
<rect x="140.0" y="398" width="19.0" height="26" fill="#626262" stroke="#94a3b8" stroke-width="1"/>
<rect x="160.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="180.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="200.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="220.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="240.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="260.0" y="398" width="19.0" height="26" fill="#959595" stroke="#94a3b8" stroke-width="1"/>
<rect x="280.0" y="398" width="19.0" height="26" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
<rect x="300.0" y="398" width="19.0" height="26" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
<rect x="320.0" y="398" width="19.0" height="26" fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
<rect x="340.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="360.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="380.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="400.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="420.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="440.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="460.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="480.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="500.0" y="398" width="19.0" height="26" fill="#404040" stroke="#94a3b8" stroke-width="1"/>
<rect x="40.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="60.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="80.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="100.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="120.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="140.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="160.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="180.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="200.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.2883;0.2886;0.2886;0.3198;0.3200;1.0000" values="0;0;1;1;0;1;1;0;0"/></rect>
<rect x="220.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2255;0.2257;0.2569;0.2571;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="240.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2255;0.2257;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="260.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;0.0998;0.1000;0.1312;0.1314;0.1626;0.1629;0.1629;0.1941;0.1943;1.0000" values="0;0;1;1;0;0;1;1;0;1;1;0;0"/></rect>
<rect x="280.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0998;0.1000;0.1312;0.1314;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="300.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="320.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="340.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="360.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="380.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="400.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="420.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="440.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="460.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="480.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<rect x="500.0" y="396" width="19.0" height="30" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"/>
<circle cx="250.0" cy="330.0" r="8" fill="#1f2937"/>
<text x="250.0" y="356.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">調べるピクセル</text>
<path d="M180.0,330.0 A70.0,154.0 0 0 1 320.0,330.0" fill="none" stroke="#93c5fd" stroke-width="2.5" stroke-dasharray="6 5"/>
<text x="180.0" y="350.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#2563eb">半径</text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="274.03" y2="319.48" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="274.03" cy="319.48" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<text x="274.03" y="308.48" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">1</text>
</g>
<line x1="274.03" y1="319.48" x2="274.03" y2="242.0" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;0.0998;0.1000;1.0000" values="0;0;1;1;0;0"/></line>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0998;0.1000;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="293.75" y2="265.68" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="293.75" cy="265.68" r="7" fill="#9ca3af" stroke="#ffffff" stroke-width="2"/>
<text x="293.75" y="254.68" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">2</text>
</g>
<line x1="293.75" y1="265.68" x2="293.75" y2="132.0" stroke="#9ca3af" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0998;0.1000;0.1312;0.1314;1.0000" values="0;0;1;1;0;0"/></line>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1312;0.1314;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="269.58" y2="265.54" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="269.58" cy="265.54" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<text x="269.58" y="254.54000000000002" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">3</text>
</g>
<line x1="269.58" y1="265.54" x2="269.58" y2="242.0" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1312;0.1314;0.1626;0.1629;1.0000" values="0;0;1;1;0;0"/></line>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1629;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="262.36" y2="193.28" stroke="#2ea043" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="262.36" cy="193.28" r="7" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="262.36" y="182.28" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">4</text>
</g>
<line x1="262.36" y1="193.28" x2="262.36" y2="242.0" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1629;0.1941;0.1943;1.0000" values="0;0;1;1;0;0"/></line>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="241.03" y2="230.78" stroke="#2ea043" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="241.03" cy="230.78" r="7" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="241.03" y="219.78" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">5</text>
</g>
<line x1="241.03" y1="230.78" x2="241.03" y2="330.0" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2255;0.2257;1.0000" values="0;0;1;1;0;0"/></line>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2255;0.2257;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="234.11" y2="277.68" stroke="#2ea043" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="234.11" cy="277.68" r="7" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="234.11" y="266.68" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">6</text>
</g>
<line x1="234.11" y1="277.68" x2="234.11" y2="330.0" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2255;0.2257;0.2569;0.2571;1.0000" values="0;0;1;1;0;0"/></line>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="202.84" y2="260.67" stroke="#2ea043" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="202.84" cy="260.67" r="7" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="202.84" y="249.67000000000002" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">7</text>
</g>
<line x1="202.84" y1="260.67" x2="202.84" y2="330.0" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.2883;0.2886;1.0000" values="0;0;1;1;0;0"/></line>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2883;0.2886;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="211.41" y2="313.11" stroke="#2ea043" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="211.41" cy="313.11" r="7" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="211.41" y="302.11" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">8</text>
</g>
<line x1="211.41" y1="313.11" x2="211.41" y2="330.0" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2883;0.2886;0.3198;0.3200;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="48" cy="114" r="6" fill="#2ea043"/>
<text x="58" y="118" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">空き</text>
<circle cx="96.8" cy="114" r="6" fill="#e5484d"/>
<text x="106.8" y="118" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">遮蔽</text>
<circle cx="145.6" cy="114" r="6" fill="#9ca3af"/>
<text x="155.6" y="118" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">無視(遠すぎ)</text>
<rect x="550" y="90" width="380" height="274" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="550" y="80" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② サンプルごとの判定</text>
<text x="566" y="114" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">サンプル点の深度 と バッファの深度を比べる</text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;1.0000" values="0;0;1;1"/><circle cx="578" cy="137" r="8" fill="#e5484d"/>
<text x="578" y="141" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">1</text>
<text x="596" y="142" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 0.24  /  バッファ 2.00</text>
<text x="905" y="142" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d">遮蔽</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0998;0.1000;1.0000" values="0;0;1;1"/><circle cx="578" cy="163" r="8" fill="#9ca3af"/>
<text x="578" y="167" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">2</text>
<text x="596" y="168" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 1.46  /  バッファ 4.50</text>
<text x="905" y="168" text-anchor="end" style="font-size:14px;font-weight:700;fill:#9ca3af">無視</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1312;0.1314;1.0000" values="0;0;1;1"/><circle cx="578" cy="189" r="8" fill="#e5484d"/>
<text x="578" y="193" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">3</text>
<text x="596" y="194" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 1.47  /  バッファ 2.00</text>
<text x="905" y="194" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d">遮蔽</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1629;1.0000" values="0;0;1;1"/><circle cx="578" cy="215" r="8" fill="#2ea043"/>
<text x="578" y="219" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">4</text>
<text x="596" y="220" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 3.11  /  バッファ 2.00</text>
<text x="905" y="220" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043">空き</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;1.0000" values="0;0;1;1"/><circle cx="578" cy="241" r="8" fill="#2ea043"/>
<text x="578" y="245" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">5</text>
<text x="596" y="246" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 2.25  /  バッファ 0.00</text>
<text x="905" y="246" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043">空き</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2255;0.2257;1.0000" values="0;0;1;1"/><circle cx="578" cy="267" r="8" fill="#2ea043"/>
<text x="578" y="271" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">6</text>
<text x="596" y="272" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 1.19  /  バッファ 0.00</text>
<text x="905" y="272" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043">空き</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;1.0000" values="0;0;1;1"/><circle cx="578" cy="293" r="8" fill="#2ea043"/>
<text x="578" y="297" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">7</text>
<text x="596" y="298" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 1.58  /  バッファ 0.00</text>
<text x="905" y="298" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043">空き</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2883;0.2886;1.0000" values="0;0;1;1"/><circle cx="578" cy="319" r="8" fill="#2ea043"/>
<text x="578" y="323" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">8</text>
<text x="596" y="324" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">点の高さ 0.38  /  バッファ 0.00</text>
<text x="905" y="324" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043">空き</text>
</g>
<text x="566" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">深度の読み込み:</text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="1">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;1.0000" values="1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;0.0998;0.1000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0998;0.1000;0.1312;0.1314;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">3<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1312;0.1314;0.1626;0.1629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">4<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1629;0.1941;0.1943;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">5<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2255;0.2257;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">6<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2255;0.2257;0.2569;0.2571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">7<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.2883;0.2886;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="354" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">8<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2883;0.2886;1.0000" values="0;0;1;1"/></text>
<text x="910" y="352" text-anchor="end" style="font-size:17px;font-weight:700;fill:#7c3aed" opacity="0">AO = 1 − 2/8 = 0.750<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;1.0000" values="0;0;1;1"/></text>
<text x="30" y="456" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">③ 全部の列で同じことを繰り返す → AO の帯</text>
<rect x="40.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3657" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3771" values="#e5e7eb;#ffffff"/></rect>
<rect x="80.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3886" values="#e5e7eb;#ffffff"/></rect>
<rect x="100.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4000" values="#e5e7eb;#e4e4e4"/></rect>
<rect x="120.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4114" values="#e5e7eb;#ffffff"/></rect>
<rect x="140.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#e5e7eb;#ffffff"/></rect>
<rect x="160.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4343" values="#e5e7eb;#e4e4e4"/></rect>
<rect x="180.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4457" values="#e5e7eb;#e4e4e4"/></rect>
<rect x="200.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4571" values="#e5e7eb;#ffffff"/></rect>
<rect x="220.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4686" values="#e5e7eb;#e4e4e4"/></rect>
<rect x="240.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="260.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4914" values="#e5e7eb;#aeaeae"/></rect>
<rect x="280.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5029" values="#e5e7eb;#ffffff"/></rect>
<rect x="300.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5143" values="#e5e7eb;#ffffff"/></rect>
<rect x="320.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5257" values="#e5e7eb;#ffffff"/></rect>
<rect x="340.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5371" values="#e5e7eb;#ffffff"/></rect>
<rect x="360.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5486" values="#e5e7eb;#ffffff"/></rect>
<rect x="380.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5600" values="#e5e7eb;#ffffff"/></rect>
<rect x="400.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5714" values="#e5e7eb;#ffffff"/></rect>
<rect x="420.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5829" values="#e5e7eb;#ffffff"/></rect>
<rect x="440.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5943" values="#e5e7eb;#ffffff"/></rect>
<rect x="460.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6057" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6171" values="#e5e7eb;#ffffff"/></rect>
<rect x="500.0" y="468.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6286" values="#e5e7eb;#ffffff"/></rect>
<rect x="40.0" y="468" width="480.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="40.0" y="462" width="20.0" height="32.0" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="x" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3769;0.3771;0.3883;0.3886;0.3998;0.4000;0.4112;0.4114;0.4226;0.4229;0.4341;0.4343;0.4455;0.4457;0.4569;0.4571;0.4683;0.4686;0.4798;0.4800;0.4912;0.4914;0.5026;0.5029;0.5141;0.5143;0.5255;0.5257;0.5369;0.5371;0.5483;0.5486;0.5598;0.5600;0.5712;0.5714;0.5826;0.5829;0.5941;0.5943;0.6055;0.6057;0.6169;0.6171;0.6283;0.6286;1.0000" values="40;40;60;60;80;80;100;100;120;120;140;140;160;160;180;180;200;200;220;220;240;240;260;260;280;280;300;300;320;320;340;340;360;360;380;380;400;400;420;420;440;440;460;460;480;480;500;500"/><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3655;0.3657;0.6398;0.6400;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="560" y="478" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">深度の読み込み(合計):</text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3655;0.3657;1.0000" values="1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3655;0.3657;0.3769;0.3771;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3769;0.3771;0.3883;0.3886;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">24<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3883;0.3886;0.3998;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">32<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;0.4112;0.4114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">40<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4112;0.4114;0.4226;0.4229;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">48<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4226;0.4229;0.4341;0.4343;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">56<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4341;0.4343;0.4455;0.4457;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">64<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4455;0.4457;0.4569;0.4571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">72<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4569;0.4571;0.4683;0.4686;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">80<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4683;0.4686;0.4798;0.4800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">88<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4798;0.4800;0.4912;0.4914;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">96<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4912;0.4914;0.5026;0.5029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">104<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5026;0.5029;0.5141;0.5143;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">112<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5141;0.5143;0.5255;0.5257;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">120<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5255;0.5257;0.5369;0.5371;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">128<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5369;0.5371;0.5483;0.5486;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">136<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5483;0.5486;0.5598;0.5600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">144<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5598;0.5600;0.5712;0.5714;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">152<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5712;0.5714;0.5826;0.5829;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">160<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5826;0.5829;0.5941;0.5943;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">168<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5941;0.5943;0.6055;0.6057;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">176<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6055;0.6057;0.6169;0.6171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">184<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6169;0.6171;0.6283;0.6286;1.0000" values="0;0;1;1;0;0"/></text>
<text x="750" y="480" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">192<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6283;0.6286;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6569;0.6571;1.0000" values="0;0;1;1"/><rect x="550" y="384" width="380" height="70" rx="12" fill="#f5f3ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="566" y="408" text-anchor="start" style="font-size:15px;font-weight:700;fill:#4c1d95">24 列 × 8 サンプル = 192 回の深度読み込み</text>
<text x="566" y="432" text-anchor="start" style="font-size:14px;font-weight:700;fill:#4c1d95">壁際の床 0.75 / 離れた床 1.00 / 壁の上 1.00</text>
</g>
<text x="30" y="520" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">調べたいピクセルの周りの、半円の中に、サンプル点を撒く<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;1.0000" values="1;1;0;0"/></text>
<text x="30" y="520" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">各サンプル点の位置の深度を読んで、「点がかべの中にあるか」を調べる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0683;0.0686;0.3198;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="520" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">数えた結果で、このピクセルの AO が決まる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;0.3655;0.3657;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="520" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ処理を、すべてのピクセルに繰り返す(暗い = 囲まれている)<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3655;0.3657;0.6398;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="520" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">壁際の床だけが暗く、壁の上や離れた床は明るい → 隅が自然に暗くなる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6398;0.6400;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ssao-samples:end -->

## 判定

接空間のサンプルを、<strong>TBN でビュー空間へ</strong>変換し、p にずらしてから、画面に投影します。

<div class="formula">s_i = p + (TBN · k_i) · R</div>

```hlsl
float HemisphereSSAO(float2 uv) {
  float z = LinearizeDepth(depth_tex.Sample(point_sampler, uv).r);
  float3 p = ViewPosition(uv, z);
  float3 n = normalize(mul(normal_tex.Sample(point_sampler, uv).xyz * 2.0 - 1.0, (float3x3)view));

  float3 random_vec = normalize(float3(noise_tex.Sample(wrap_sampler, uv * noise_scale).xy, 0.0));
  float3 tangent = normalize(random_vec - n * dot(random_vec, n));
  float3 bitangent = cross(n, tangent);
  float3x3 tbn = float3x3(tangent, bitangent, n);

  float occlusion = 0.0;
  for (int i = 0; i < kKernelSize; ++i) {
    float3 s = p + mul(kernel[i].xyz, tbn) * radius;

    float4 clip = mul(float4(s, 1.0), projection);
    float2 suv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
    float scene_z = LinearizeDepth(depth_tex.SampleLevel(point_sampler, suv, 0).r);

    float range_check = smoothstep(0.0, 1.0, radius / abs(z - scene_z));
    occlusion += (scene_z <= s.z - bias ? 1.0 : 0.0) * range_check;
  }
  return pow(saturate(1.0 - occlusion / kKernelSize), power);
}
```

コードの読みどころを順に説明します。G-Buffer の法線がワールド空間なら、位置と同じ空間にするため、ビュー行列でビュー空間へ変換します。`mul(kernel, tbn)` は行ベクトル規約で、サンプル `k` を TBN の行（T, B, N）の線形結合にする操作です。`scene_z <= s.z − bias` は、面がサンプル点より手前にあれば遮られている、という判定です。`range_check` は `smoothstep(0, 1, R / |z − scene_z|)` で、深度差が R 以内なら 1、離れるほど 0 に近づきます。`smoothstep` を使うのは、硬い境界を避けるためです。最後の `power` は、`pow(ao, power)` でコントラストを調整します。

<!-- fig:ao-range-check:begin -->

<svg class="fig illust motion" data-fig="ao-range-check" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ao-range-check" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">範囲チェック:遠く離れた物は、遮蔽に数えない（ハローを防ぐ）</text>
<rect x="60" y="250" width="300" height="18" fill="#d6c7a1"/>
<rect x="190" y="140" width="70" height="110" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<text x="225" y="130" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">手前の物</text>
<rect x="66" y="140" width="14" height="110" fill="#94a3b8"/>
<text x="60" y="82" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">カメラの視線(左→右)。着色点 P は奥の壁の上。</text>
<rect x="420" y="100" width="320" height="210" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="580" y="92" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">結果:P のまわりの暗さ</text>
<rect x="455" y="140" width="50" height="140" fill="#b8794b"/>
<rect x="505" y="140" width="215" height="140" fill="#cbd5e1"/>
<text x="480" y="158" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">手前</text>
<text x="640" y="158" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">奥の壁</text>
<rect x="505" y="140" width="60" height="140" fill="#000000" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1481;0.2222;0.4815;0.5556;1.0000" values="0;0;0.55;0.55;0;0"/></rect>
<text x="440" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">範囲チェックなし<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;1.0000" values="1;1;0;0"/></text>
<text x="440" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">手前の「そば」が暗い（ハロー）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="440" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">あり:奥の壁に影が落ちない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000;1.0000" values="0;0;1;1;0"/></text>
<line x1="100" y1="250" x2="100" y2="250" stroke="#e5484d" stroke-width="0"/>
<circle cx="200" cy="215" r="7" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000;1.0000" values="0;0;1;1;0"/></circle>
<line x1="100" y1="240" x2="200" y2="215" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000;1.0000" values="0;0;1;1;0"/></line>
<circle cx="225" cy="190" r="7" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1034;0.1037;1.0000;1.0000" values="0;0;1;1;0"/></circle>
<line x1="100" y1="240" x2="225" y2="190" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1034;0.1037;1.0000;1.0000" values="0;0;1;1;0"/></line>
<circle cx="210" cy="165" r="7" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1330;0.1333;1.0000;1.0000" values="0;0;1;1;0"/></circle>
<line x1="100" y1="240" x2="210" y2="165" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1330;0.1333;1.0000;1.0000" values="0;0;1;1;0"/></line>
<text x="60" y="300" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">P のまわりのサンプルが、手前の物に当たる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;1.0000" values="1;1;0;0"/></text>
<text x="60" y="300" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">深度が P よりずっと近い → 遮蔽と数える（誤り）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="300" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">深度差 &gt; 半径 なら数えない（範囲チェック）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="326" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">rangeCheck = smoothstep(0, 1, 半径 / |深度差|)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ao-range-check:end -->

### 範囲チェックの意味

遮られる物体が、p のすぐ近くにあれば、AO は暗くなるべきです。しかし、手前に遠く離れた物体（たとえば p が壁の近くで、その手前 10 m に別の柱）があるとサンプルがその柱の裏に入り、p が暗くなってしまいます。

深度差が R 以下なら、範囲チェックは 1 で、近い物による遮蔽としてそのまま効かせます。R より大きければ、R / 差 の値（1 より小さい）になり、遠い物による遮蔽として弱めます。差が大きいほど、効きはどんどん小さくなります。

## バイアスの決め方

バイアスは、小さすぎても大きすぎてもいけません。小さすぎる（0 に近い）と、浮動小数点の誤差と深度の量子化により、平らな面に縞や斑点（自己遮蔽）が出ます。大きすぎると、接地の暗さが消えてしまい、浅いくぼみが見えなくなります。目安は半径の 1〜5 % で、ビュー空間の単位（メートル）で指定します。

<strong>距離に応じて</strong>バイアスを増やす（遠いほど深度の精度が落ちる）と、安定します。

## ぼかし

結果には、<strong>4×4 周期のノイズ</strong>が残っています。4×4 のボックス ぼかしで、周期のパターンを消すのが定番です。

```hlsl
float Blur(float2 uv) {
  float sum = 0.0;
  [unroll] for (int x = -2; x < 2; ++x) {
    [unroll] for (int y = -2; y < 2; ++y) {
      sum += ao_tex.Sample(point_sampler, uv + float2(x, y) * texel_size).r;
    }
  }
  return sum / 16.0;
}
```

ただし、単純なぼかしは、物体の境界で暗さがにじむので、深度と法線を考慮したバイラテラル ブラーを使うと、品質が上がります（[フィルタ](filtering/index.md)）。

## DirectX 11 で組む

ここまでの HLSL を、1 回の描画パスとして、動かすための、ホスト側の、準備です（共通の部品は、[D3D11 Pass Recipes](../../directx/dx11/pass-recipes.md) を参照）。

### 入力と出力

```cpp
// 出力: AO（1 チャンネル）。フル解像度でも、半分でもよい。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R8_UNORM;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &ao_texture);
device->CreateRenderTargetView(ao_texture.Get(), nullptr, &ao_rtv);
device->CreateShaderResourceView(ao_texture.Get(), nullptr, &ao_srv);
```

AO は、0〜1 の 1 チャンネルなので、`R8_UNORM` で足ります。ぼかしの、2 パスのために、同じ大きさの、もう 1 枚（`ao_blur_texture`）を、作ります。

### ノイズ テクスチャとカーネル

```cpp
// ノイズ: 4×4 の、ランダムな回転（xy の方向）。繰り返して、画面に敷く（WRAP）。
struct Noise { int8_t x, y, z, w; };
Noise noise[16];
for (auto& n : noise) {
  float angle = RandomFloat() * 6.2831853f;
  n = {int8_t(std::cos(angle) * 127), int8_t(std::sin(angle) * 127), 0, 0};
}
D3D11_TEXTURE2D_DESC nd = {};
nd.Width = nd.Height = 4;
nd.MipLevels = nd.ArraySize = 1;
nd.Format = DXGI_FORMAT_R8G8B8A8_SNORM;                         // 符号つき。−1〜1 で読める
nd.SampleDesc.Count = 1;
nd.Usage = D3D11_USAGE_IMMUTABLE;
nd.BindFlags = D3D11_BIND_SHADER_RESOURCE;
D3D11_SUBRESOURCE_DATA init = {noise, 4 * sizeof(Noise), 0};
device->CreateTexture2D(&nd, &init, &noise_texture);
device->CreateShaderResourceView(noise_texture.Get(), nullptr, &noise_srv);
```

ノイズは、4×4 の、小さなテクスチャを、画面いっぱいに、繰り返し（`WRAP` サンプラー）、画素ごとに、違う回転を、与えます。ぼかしで、この 4×4 の模様を、消します。サンプラーは、ノイズ用に、`POINT` と `WRAP`、深度用に、`POINT` と `CLAMP` の、2 つを、用意します。

```cpp
// カーネル: 半球のサンプル（64 個の float4）を、定数バッファに入れる。起動時に、1 度だけ作る。
struct SsaoConstants {
  DirectX::XMFLOAT4 kernel[64];                                 // xyz: 半球内のオフセット
  DirectX::XMFLOAT4X4 projection;
  DirectX::XMFLOAT2 noise_scale;                                // (画面幅 / 4, 画面高さ / 4): ノイズを、画面に敷く倍率
  float radius;
  float bias;
};
```

`noise_scale` は、`uv` に掛けて、ノイズの座標にする倍率です。画面が、1920×1080 なら、(480, 270) で、ノイズが、480×270 回、繰り返されます。

### パスの流れ

```cpp
// ① AO を描く（深度 SRV と、法線 SRV を、読む。DSV は、束ねない）。
context->OMSetRenderTargets(1, ao_rtv.GetAddressOf(), nullptr);
context->PSSetShaderResources(0, 1, depth_srv.GetAddressOf());      // t0: 深度
context->PSSetShaderResources(1, 1, normal_srv.GetAddressOf());     // t1: 法線
context->PSSetShaderResources(2, 1, noise_srv.GetAddressOf());      // t2: ノイズ
DrawFullscreenTriangle();

// ② ぼかし（水平 → 垂直）。入力と出力を、別のテクスチャにする。
context->OMSetRenderTargets(1, ao_blur_rtv.GetAddressOf(), nullptr);
context->PSSetShaderResources(0, 1, ao_srv.GetAddressOf());
DrawFullscreenTriangle();     // 水平
// （もう 1 回、ao_blur → ao へ、垂直）
```

深度の DSV を、束ねたままにすると、深度を、SRV で、読めません（[D3D11 Pass Recipes](../../directx/dx11/pass-recipes.md) の、束縛の衝突）。AO の、結果は、ライティングの、パスで、環境光に、掛けます（[Usage and Misconceptions of AO](theory/usage-misconceptions.md)）。

## パラメータ

| パラメータ | 意味 | 目安 |
| --- | --- | --- |
| <strong>radius（R）</strong> | 影響半径（ビュー空間） | 0.3〜1.0 m（シーンの大きさで） |
| bias | 自己遮蔽を防ぐ | 0.01〜0.05 m |
| kernel size | サンプル数 | 8〜16 |
| power | コントラスト | 1.0〜2.0 |
| noise size | ノイズ テクスチャの一辺 | 4（ぼかしの周期と合わせる） |
| 解像度 | AO を計算する解像度 | フル or 半分（半分なら、アップサンプルが必要。[縮小バッファの効果](../../rendering/low-res-effects.md)） |

## 法線を深度から復元する

<strong>G-Buffer に法線がない</strong>（フォワード レンダリングなど）場合は深度から法線を復元します。

### 画面上の微分で作る

```hlsl
float3 n = normalize(cross(ddx(p), ddy(p)));
```

隣の画素との位置の差（`ddx`・`ddy`）の外積が法線です（左手系・D3D の画面でカメラ向きが正になります）。荒い（面ごとのフラット）法線で深度の段差の所で乱れます。

### 近傍の画素を選ぶ

上下・左右の深度の差が小さい側を選んで、位置の差から作ります。段差を跨がないので輪郭の近くで安定します。

法線の取り方は 3 通りあります。`ddx` / `ddy` は簡単ですが、2×2 のブロックの中でしか差が取れないので荒くなります。隣の画素の位置から作る方法は、深度の差が小さい側を選ぶと、境界で乱れにくくなります。G-Buffer の法線を使う方法は最も正確で、法線マップを反映した法線かジオメトリの法線かを選べます。AO には、ジオメトリの法線が向いています。

## この方式の弱点

| 弱点 | 説明 |
| --- | --- |
| ハロー | 手前の物体の縁で背景が暗く光る輪。範囲チェックで軽減 |
| コサイン重みが雑 | 一様な半球のサンプルは、水平方向の遮蔽を過大評価する |
| サンプル数に依存 | 少ないとノイズ、多いと重い。半径が大きいとサンプルが画面で広がり、キャッシュが効かない |
| 画面外・薄い物体 | [AO Theory](theory/index.md)のスクリーン空間の限界 |
| ライトに依存しない | 直接光の影は表せない |

## 次の方式へ

| 弱点 | 解決する方式 |
| --- | --- |
| 式が経験的 | [Alchemy AO](alchemy-ao.md)（導出された式） |
| 半径が大きいと遅い | [SAO](sao.md)（深度のミップ） |
| ノイズが多い | [HBAO](hbao.md)（方向ごとの地平線で少ないサンプルで安定） |
| コサイン重み | [GTAO](gtao.md) |

## よくあるミス

??? failure "法線をワールド空間のまま使う"
    位置と<strong>同じ空間</strong>（ビュー空間）に変換してから使います。

??? failure "ノイズ テクスチャを、補間（リニア）で読む"
    ポイント サンプリング ＋ ラップにします。

??? failure "ノイズの周期とぼかしの周期が、合っていない"
    4×4 のノイズなら、4×4 のぼかしです。

??? failure "AO を、直接光にも掛けて、全体が暗い"
    間接光（環境光）だけに掛けます（[理論](theory/index.md)）。

??? failure "法線マップ込みの法線を使い、凹凸が AO に出る"
    AO にはジオメトリの法線を使います（法線マップの凹凸が暗い斑点になる）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半球 SSAO ＝ 法線の側の半球にサンプルを置く SSAO。平らな面が灰色にならない
    - [x] TBN を、ランダム ベクトルから作る（グラム・シュミット）。接線は不要
    - [x] 判定は投影して深度を比べる。バイアスと範囲チェックが肝
    - [x] ぼかしは、ノイズと同じ周期。境界をにじませないならバイラテラル
    - [x] 法線は G-Buffer から。無ければ深度から復元

## 参考

- de Vries, "SSAO", LearnOpenGL（半球カーネル・ノイズ・バイアス・範囲チェックの、実装解説）
- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Filion, McNaughton, "StarCraft II: Effects & Techniques", SIGGRAPH 2008, Advances in Real-Time Rendering in 3D Graphics and Games（深度バッファによる、SSAO）
- Kajalin, "Screen Space Ambient Occlusion", ShaderX7, 2009
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）

## 関連ページ

- [Ambient Occlusion (AO)](index.md)
- [Crytek SSAO](ssao-crytek.md)
- [Alchemy AO](alchemy-ao.md)
- [AO Filtering](filtering/index.md)
- [AO Artifacts](artifacts/index.md)
- [法線とライティング](../../3d/lighting-normals.md)

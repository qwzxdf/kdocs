---
title: 半球 SSAO
tags:
  - 描画
---

# 半球 SSAO

**半球 SSAO**（Normal-oriented Hemisphere SSAO）は、[Crytek SSAO](ssao-crytek.md)の**球を法線の側の半球に変えた**方式です。これだけで**平らな面が灰色になる問題が消え**、見た目が大きく改善します。現在、<strong>「SSAO」と言えば、この方式</strong>を指すことが多く、チュートリアルや多くのゲームで使われる、**標準的な SSAO** です。このページでは、**原理・サンプルの作り方・コード・調整**を順に説明します。

!!! tip "ポイント"
    - 入力は<strong>深度（位置）と法線</strong>。法線は G-Buffer から、または深度から復元する。
    - サンプルは<strong>法線の側の半球</strong>（接空間で z ≥ 0）に置く。<strong>平らな面では遮蔽 0（明るい）</strong>になる。
    - <strong>画素ごとにランダムな軸でサンプルを回転</strong>（TBN をランダム ベクトルから作る）。<strong>タンジェントは不要</strong>。
    - 判定は <strong>Crytek と同じ</strong>（投影して深度を比べる）。<strong>バイアス・範囲チェック</strong>が重要。
    - 後処理は<strong>ぼかし</strong>（ランダム パターンと同じ周期のボックス ぼかしが定番）。
    - <strong>コサイン重み付き</strong>にするなら、<strong>サンプルを法線に寄せる</strong>（分布を工夫する）。

## Crytek 方式からの変更点

| 項目 | Crytek 方式 | 半球 SSAO |
| --- | --- | --- |
| **サンプルの領域** | 球 | **法線側の半球** |
| **入力** | 深度のみ | **深度 ＋ 法線** |
| **平らな面** | 約 50% が遮られ、灰色 | <strong>遮蔽なし（明るい）</strong> |
| **ランダム化** | サンプル ベクトルを鏡映 | **接空間（TBN）をランダムに回す** |
| **コスト** | 同程度 | わずかに増える（法線の読み込み） |

## 半球のサンプルを作る

**接空間**（法線を z 軸とした座標系）で、**z が 0 以上**のベクトルを作ります。これが**半球**です。

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

| 点 | 説明 |
| --- | --- |
| **`z` を 0〜1** | **正の側だけ**にすることで、半球になる |
| **長さをランダムに** | `v *= zero_one(rng)` で、**中心からの距離が一様**にばらつく |
| **`scale = lerp(0.1, 1.0, t²)`** | **原点に近いサンプルを多く**する。近い遮蔽ほど効かせたいため |
| **サンプル数** | 8〜16 が実用。64 は多すぎ（学習用） |

### サンプルの分布と、コサイン重み

[理論](theory/index.md)の AO は**コサイン重み付き**の積分でした。**法線に近い方向のサンプルが、より重要**です。上の分布は**一様な半球**なので、法線方向に特別に寄せてはいません（**コサイン重みを無視**した近似です）。コサイン重みを正しく扱うなら、**コサイン分布**のサンプルを使います。

| 分布 | 方向の取り方 | 結果 |
| --- | --- | --- |
| **一様な半球** | 半球上で一様 | 横方向の遮蔽が必要以上に効く（水平寄りの遮蔽に敏感） |
| **コサイン分布** | `x = √u1 cos(2πu2)`、`y = √u1 sin(2πu2)`、`z = √(1 − u1)` | **法線付近が多い**。モンテカルロの `V` の割合が、そのまま AO（理論のとおり） |

```cpp
Vector3 CosineSample(float u1, float u2) {
  float r = std::sqrt(u1);
  float phi = 2.0f * std::numbers::pi_v<float> * u2;
  return Vector3(r * std::cos(phi), r * std::sin(phi), std::sqrt(1.0f - u1));
}
```

## TBN をランダムに作る

**サンプルをビュー空間に持ってくる**ために、**法線を z 軸**とした座標系（TBN）が必要です。普通はメッシュの**接線**を使いますが、SSAO では**ランダム ベクトル**から作ります。**画素ごとに軸まわりに回す**効果も同時に得られます。

<div class="formula">tangent = normalize( random − normal · dot(random, normal) )、　bitangent = cross(normal, tangent)</div>

**グラム・シュミットの直交化**です。ランダム ベクトルから、**法線方向の成分を引く**と、**法線に垂直なベクトル**（タンジェント）が得られます。

```hlsl
float3 random_vec = normalize(float3(noise_tex.Sample(wrap_sampler, uv * noise_scale).xy, 0.0));
float3 tangent = normalize(random_vec - normal * dot(random_vec, normal));
float3 bitangent = cross(normal, tangent);
float3x3 tbn = float3x3(tangent, bitangent, normal);
```

| 点 | 説明 |
| --- | --- |
| **ノイズ テクスチャ** | 4×4 の `float2`（z は 0）。<strong>ラップ（繰り返し）</strong>で、画面全体に貼る |
| **`noise_scale`** | `screen_size / 4`。**4 画素ごとにパターンが繰り返す** |
| **`cross(normal, tangent)`** | **左手系**でも、`TBN` の向きを保つため、このサイトの規約のまま（外積の向きは [ベクトル](../../gamemath/vectors.md) を参照） |
| **メッシュの接線が不要** | 法線だけあればよい |

<!-- fig:ssao-samples:begin -->

<svg class="fig illust motion" data-fig="ssao-samples" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ssao-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">SSAO:点の周りの半球にサンプルを撒いて、物の中に入った割合で暗くする</text>
<polygon points="40,270 470,270 470,150 740,150 740,340 40,340" fill="#cbd5e1" stroke="#1f2937" stroke-width="3"/>
<path d="M367,270 A85,85 0 0 1 537,270" fill="#bfdbfe" fill-opacity="0.35" stroke="#2563eb" stroke-width="1.5" stroke-dasharray="4 3"/>
<circle cx="452" cy="270" r="6" fill="#1f2937"/>
<text x="448" y="296" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">A</text>
<circle cx="500.79" cy="224.77" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></circle>
<circle cx="479.5" cy="206.47" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1214;0.1217;1.0000" values="0;0;1;1"/></circle>
<circle cx="437.17" cy="234.42" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;1.0000" values="0;0;1;1"/></circle>
<circle cx="530.84" cy="266.74" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="0;0;1;1"/></circle>
<circle cx="486.46" cy="233.46" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;1.0000" values="0;0;1;1"/></circle>
<circle cx="388.98" cy="269.14" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000" values="0;0;1;1"/></circle>
<circle cx="396.86" cy="238.88" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;1.0000" values="0;0;1;1"/></circle>
<circle cx="433.04" cy="229.39" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;1.0000" values="0;0;1;1"/></circle>
<circle cx="419.07" cy="196.99" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;1.0000" values="0;0;1;1"/></circle>
<circle cx="446.54" cy="195.13" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></circle>
<circle cx="432.29" cy="237.01" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="0;0;1;1"/></circle>
<circle cx="402.21" cy="222.72" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/></circle>
<circle cx="472.87" cy="241.04" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;1.0000" values="0;0;1;1"/></circle>
<circle cx="394.41" cy="244.11" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;1.0000" values="0;0;1;1"/></circle>
<circle cx="400.91" cy="207.78" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000" values="0;0;1;1"/></circle>
<circle cx="400.84" cy="205.79" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000" values="0;0;1;1"/></circle>
<path d="M85,270 A85,85 0 0 1 255,270" fill="#bfdbfe" fill-opacity="0.35" stroke="#2563eb" stroke-width="1.5" stroke-dasharray="4 3"/>
<circle cx="170" cy="270" r="6" fill="#1f2937"/>
<text x="166" y="296" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">B</text>
<circle cx="218.79" cy="224.77" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1040;0.1043;1.0000" values="0;0;1;1"/></circle>
<circle cx="197.5" cy="206.47" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1388;0.1391;1.0000" values="0;0;1;1"/></circle>
<circle cx="155.17" cy="234.42" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></circle>
<circle cx="248.84" cy="266.74" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2083;0.2087;1.0000" values="0;0;1;1"/></circle>
<circle cx="204.46" cy="233.46" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;1.0000" values="0;0;1;1"/></circle>
<circle cx="106.98" cy="269.14" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/></circle>
<circle cx="114.86" cy="238.88" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000" values="0;0;1;1"/></circle>
<circle cx="151.04" cy="229.39" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3475;0.3478;1.0000" values="0;0;1;1"/></circle>
<circle cx="137.07" cy="196.99" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000" values="0;0;1;1"/></circle>
<circle cx="164.54" cy="195.13" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4170;0.4174;1.0000" values="0;0;1;1"/></circle>
<circle cx="150.29" cy="237.01" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/></circle>
<circle cx="120.21" cy="222.72" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000" values="0;0;1;1"/></circle>
<circle cx="190.87" cy="241.04" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></circle>
<circle cx="112.41" cy="244.11" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;1.0000" values="0;0;1;1"/></circle>
<circle cx="118.91" cy="207.78" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5910;0.5913;1.0000" values="0;0;1;1"/></circle>
<circle cx="118.84" cy="205.79" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6257;0.6261;1.0000" values="0;0;1;1"/></circle>
<text x="362" y="62" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">点 A</text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:1 / 1<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1214;0.1217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:2 / 2<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1214;0.1217;0.1562;0.1565;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:2 / 3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;0.1910;0.1913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:3 / 4<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.2257;0.2261;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 5<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;0.2605;0.2609;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 6<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;0.2953;0.2957;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 7<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;0.3301;0.3304;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;0.3649;0.3652;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 9<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 10<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4344;0.4348;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 11<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:4 / 12<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;0.5040;0.5043;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:5 / 13<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;0.5388;0.5391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:5 / 14<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;0.5736;0.5739;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:5 / 15<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;0.6083;0.6087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="362" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:5 / 16<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000;1.0000" values="0;0;1;1;0"/></text>
<rect x="362" y="104" width="0" height="16" fill="#afafaf" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6518;0.6522;1.0000" values="0;0;1;1"/><animate attributeName="width" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6522;0.7043;1.0000" values="0;0;140;140"/></rect>
<text x="362" y="142" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="362" y="144" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.69（暗くなる）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6866;0.6870;1.0000" values="0;0;1;1"/></text>
<text x="80" y="62" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">点 B</text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 1<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1040;0.1043;0.1388;0.1391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 2<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1388;0.1391;0.1736;0.1739;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;0.2083;0.2087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 4<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2083;0.2087;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 5<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 6<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.3127;0.3130;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 7<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;0.3475;0.3478;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 8<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3475;0.3478;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 9<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;0.4170;0.4174;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 10<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4170;0.4174;0.4518;0.4522;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 11<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;0.4866;0.4870;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 12<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 13<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;0.5562;0.5565;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 14<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;0.5910;0.5913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 15<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5910;0.5913;0.6257;0.6261;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">物の中:0 / 16<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6257;0.6261;1.0000;1.0000" values="0;0;1;1;0"/></text>
<rect x="80" y="104" width="0" height="16" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="0;0;1;1"/><animate attributeName="width" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6696;0.7217;1.0000" values="0;0;140;140"/></rect>
<text x="80" y="142" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="80" y="144" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">明るさ 1.00（ほぼそのまま明るい）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7040;0.7043;1.0000" values="0;0;1;1"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">赤 = 物の中に入ったサンプル、緑 = 空いている。壁の近く（A）ほど赤が多く、暗くなる。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:ssao-samples:end -->

## 判定

接空間のサンプルを、**TBN でビュー空間へ**変換し、**p にずらして**から、画面に投影します。

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

| 点 | 説明 |
| --- | --- |
| **法線をビュー空間へ** | G-Buffer の法線がワールド空間なら、`view` で変換する |
| **`mul(kernel, tbn)`** | 行ベクトル規約：`k` を TBN の行（T, B, N）の線形結合に |
| **`scene_z <= s.z − bias`** | 面がサンプル点より**手前**なら、遮られている |
| **`range_check`** | `smoothstep(0, 1, R / |z − scene_z|)`。**深度差が R 以内なら 1**、**離れるほど 0 へ**。硬い境界を避けるため、`smoothstep` を使う |
| **`power`** | `pow(ao, power)` で、コントラストを調整 |

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

遮られる物体が、**p のすぐ近く**にあれば、AO は暗くなるべきです。しかし、**手前に遠く離れた物体**（たとえば p が壁の近くで、その手前 10 m に別の柱）があると**サンプルがその柱の裏に入り**、**p が暗く**なってしまいます。

| 深度差 \|z − scene_z\| | 範囲チェック | 意味 |
| --- | --- | --- |
| **R 以下** | 1 | 近い物による遮蔽。**効かせる** |
| **R より大きい** | R / 差（小さくなる） | 遠い物による遮蔽。**弱める** |

## バイアスの決め方

| 値 | 症状 |
| --- | --- |
| <strong>小さすぎる（0 に近い）</strong> | **平らな面に縞や斑点**（自己遮蔽）。浮動小数点の誤差・深度の量子化 |
| **大きすぎる** | **接地の暗さが消える**。浅いくぼみが見えない |
| **目安** | 半径の 1〜5%。**ビュー空間の単位**（メートル）で指定 |

**距離に応じて**バイアスを増やす（遠いほど深度の精度が落ちる）と、安定します。

## ぼかし

結果には、**4×4 周期のノイズ**が残っています。**4×4 のボックス ぼかし**で、周期のパターンを消すのが定番です。

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

ただし、**単純なぼかし**は、物体の境界で**暗さがにじむ**ので、**深度と法線を考慮したバイラテラル ブラー**を使うと、品質が上がります（[フィルタ](filtering/index.md)）。

## パラメータ

| パラメータ | 意味 | 目安 |
| --- | --- | --- |
| <strong>radius（R）</strong> | 影響半径（ビュー空間） | 0.3〜1.0 m（シーンの大きさで） |
| **bias** | 自己遮蔽を防ぐ | 0.01〜0.05 m |
| **kernel size** | サンプル数 | 8〜16 |
| **power** | コントラスト | 1.0〜2.0 |
| **noise size** | ノイズ テクスチャの一辺 | 4（ぼかしの周期と合わせる） |
| **解像度** | AO を計算する解像度 | フル or 半分（半分なら、アップサンプルが必要。[低解像度のエフェクト](../../rendering/low-res-effects.md)） |

## 法線を深度から復元する

**G-Buffer に法線がない**（フォワード レンダリングなど）場合は**深度から法線を復元**します。

### 画面上の微分で作る

```hlsl
float3 n = normalize(cross(ddx(p), ddy(p)));
```

**隣の画素との位置の差**（`ddx`・`ddy`）の外積が法線です（左手系・D3D の画面でカメラ向きが正になります）。**荒い（面ごとのフラット）法線**で**深度の段差の所で乱れます**。

### 近傍の画素を選ぶ

**上下・左右**の**深度の差が小さい側**を選んで、位置の差から作ります。段差を跨がないので**輪郭の近くで安定**します。

| 方法 | 特徴 |
| --- | --- |
| **`ddx` / `ddy`** | 簡単。**2×2 のブロック内**でしか差が取れず、荒い |
| **隣の画素の位置から** | **深度の差が小さい側**を選ぶと、境界で乱れにくい |
| **G-Buffer の法線** | 最も正確（**法線マップを反映**した法線か、**ジオメトリの法線**かは選べる。AO には**ジオメトリの法線**が向く） |

## この方式の弱点

| 弱点 | 説明 |
| --- | --- |
| **ハロー** | 手前の物体の縁で背景が暗く光る輪。範囲チェックで軽減 |
| **コサイン重みが雑** | 一様な半球のサンプルは、**水平方向の遮蔽を過大評価**する |
| **サンプル数に依存** | 少ないとノイズ、多いと重い。**半径が大きいとサンプルが画面で広がり、キャッシュが効かない** |
| **画面外・薄い物体** | [理論](theory/index.md)のスクリーン空間の限界 |
| **ライトに依存しない** | 直接光の影は表せない |

## 次の方式へ

| 弱点 | 解決する方式 |
| --- | --- |
| **式が経験的** | [Alchemy AO](alchemy-ao.md)（導出された式） |
| **半径が大きいと遅い** | [SAO](sao.md)（深度のミップ） |
| **ノイズが多い** | [HBAO](hbao.md)（方向ごとの地平線で少ないサンプルで安定） |
| **コサイン重み** | [GTAO](gtao.md) |

## よくあるミス

??? failure "法線をワールド空間のまま使う"
    位置と**同じ空間**（ビュー空間）に変換してから使います。

??? failure "ノイズ テクスチャを、補間（リニア）で読む"
    ポイント サンプリング ＋ ラップにします。

??? failure "ノイズの周期とぼかしの周期が、合っていない"
    4×4 のノイズなら、4×4 のぼかしです。

??? failure "AO を、直接光にも掛けて、全体が暗い"
    間接光（環境光）だけに掛けます（[理論](theory/index.md)）。

??? failure "法線マップ込みの法線を使い、凹凸が AO に出る"
    AO には**ジオメトリの法線**を使います（法線マップの凹凸が暗い斑点になる）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半球 SSAO ＝ <strong>法線の側の半球にサンプルを置く</strong> SSAO。<strong>平らな面が灰色にならない</strong>
    - [x] <strong>TBN を、ランダム ベクトルから作る</strong>（グラム・シュミット）。接線は不要
    - [x] 判定は<strong>投影して深度を比べる</strong>。<strong>バイアス</strong>と<strong>範囲チェック</strong>が肝
    - [x] <strong>ぼかしは、ノイズと同じ周期</strong>。境界をにじませないなら<strong>バイラテラル</strong>
    - [x] 法線は G-Buffer から。無ければ<strong>深度から復元</strong>

## 参考

- LearnOpenGL, "SSAO"（半球カーネル・ノイズ・バイアス・範囲チェックの実装解説）
- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）

## 関連ページ

- [環境光遮蔽（AO）](index.md)
- [Crytek SSAO](ssao-crytek.md)
- [Alchemy AO](alchemy-ao.md)
- [フィルタ](filtering/index.md)
- [アーティファクト](artifacts/index.md)
- [法線とライティング](../../3d/lighting-normals.md)

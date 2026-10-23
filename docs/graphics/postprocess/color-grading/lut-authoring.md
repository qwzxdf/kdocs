---
title: Authoring LUTs
tags:
  - 描画
---

# Authoring LUTs

<strong>3D LUT は、「どうやって中身を作るか」</strong>が次の問題です。ゲームの中で調整パラメータから LUT をコンピュート シェーダーで生成する方法と、外部の映像ツール（Photoshop・DaVinci Resolve）で作った LUT を読み込む方法の2 つがあります。さらに場所や時間帯ごとに LUT を切り替え・補間して、雰囲気を変えるのが実用的です。このページでは、コンピュートでの生成・外部ツールとのやり取り・ゾーンごとの LUT と補間・更新のタイミングを説明します。

!!! tip "ポイント"
    - <strong>ゲーム内で生成</strong>：<strong>パラメータ → コンピュート シェーダーで、全格子点に調整を適用して LUT を作る</strong>。パラメータが変わったときだけ再生成。
    - 外部ツールで作る：基準の LUT（無加工）に、ツールでルックを焼き、保存して読み込む。
    - 基準の LUT（アイデンティティ LUT）＝ 変換しない LUT。これに調整をかけて保存すると、LUT になる。
    - ゾーンごとの LUT：場所・時間帯で LUT を切り替え、境で補間する。
    - 2 つの LUT を混ぜる：1 回の表引きで両方読み、`lerp`。
    - 再生成は毎フレーム不要。パラメータの変化時のみ。

!!! info "このページを読む前に"
    - [Color Grading](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ゲーム内で生成（コンピュート）

<strong>3D の各格子点（r, g, b）</strong>について、その色に調整（露出・ホワイト バランス・LGG・彩度・トーンマップ）を順に適用し、結果を LUT に書きます。

```hlsl
RWTexture3D<float4> out_lut : register(u0);

cbuffer GradingParams : register(b0) {
  float exposure;
  float temperature;
  float tint;
  float3 lift;
  float3 gamma;
  float3 gain;
  float contrast;
  float saturation;
  float lut_size;
};
```

LUT を、書き込む、3D テクスチャと、調整パラメータです。リフト・ガンマ・ゲイン、コントラスト、彩度、色温度などを、定数バッファに、まとめます。

```hlsl
float3 LogToLinear(float3 log_c) {
  const float kMinLog = -10.0;
  const float kMaxLog = 6.5;
  return exp2(log_c * (kMaxLog - kMinLog) + kMinLog);
}
```

LUT の、座標（0〜1）を、対数の値から、線形の光に、戻します。LUT は、対数空間で、並べると、暗部にも、十分な、精度を、割けます。範囲は、`2^−10` から `2^6.5` です。

```hlsl
[numthreads(8, 8, 8)]
void GenerateLut(uint3 id : SV_DispatchThreadID) {
  float3 uvw = (float3(id) + 0.5) / lut_size;
  float3 color = LogToLinear(uvw);
```

1 画素が、LUT の、1 つの格子点を、受け持ちます。格子点の、中心（+0.5）を、座標にして、線形の色に、戻します。

```hlsl
  color *= exposure;
  color = WhiteBalance(color, temperature, tint);
  color = LiftGammaGain(color, lift, gamma, gain);
  color = ApplyContrast(color, contrast, 0.18);
  color = ApplySaturation(color, saturation);
  color = Tonemap(color);
  out_lut[id] = float4(color, 1.0);
}
```

| 点 | 説明 |
| --- | --- |
| `numthreads(8, 8, 8)` | 32³ なら、4×4×4 グループで生成 |
| `uvw = (id + 0.5) / size` | 各セルの中心の座標（半テクセル） |
| `LogToLinear` | 対数エンコードされた入力を、リニアに戻す（適用時の `LinearToLog` の逆） |
| 調整を順に適用 | 露出 → ホワイト バランス → LGG → コントラスト → 彩度 → トーンマップ |
| コスト | 32³ ＝ 32,768 回の計算のみ。1920×1080 の画面の 1.6 % 程度で軽い |

### いつ再生成するか

いつ再生成するかです。パラメータが変わったときは、調整ボリュームの補間中は毎フレーム再生成します。変わらないときは再生成せず、LUT をテクスチャとして保持します。ステージ読み込み時に、初期の LUT を作ります。

コンピュートの 1 回あたりが軽いので、毎フレーム再生成しても問題ない場合も多いです。

## 外部ツールで作る

<strong>映像のプロ用ツールで実際の画面を見ながら、ルックを調整し、LUT に書き出す</strong>方法です。

| 手順 | 内容 |
| --- | --- |
| ① 基準の LUT を用意 | 変換しない LUT（アイデンティティ LUT） を 画像（.png）または .cube で出力 |
| ② ツールで調整 | スクリーンショットに基準の LUT を重ねて、調整レイヤーで加工（Photoshop）。または、Resolve でグレーディング |
| ③ LUT を書き出す | 加工後の基準 LUT 画像を保存（.png）または .cube |
| ④ ゲームに読み込む | 3D テクスチャとして使う |

### 基準の LUT（アイデンティティ LUT）

入力色をそのまま出力する LUT です。各格子点の値がその座標の色と同じです。

```cpp
std::vector<uint16_t> BuildIdentityLut(int size) {
  std::vector<uint16_t> data(size * size * size * 4);
  for (int b = 0; b < size; ++b) {
    for (int g = 0; g < size; ++g) {
      for (int r = 0; r < size; ++r) {
        int index = ((b * size + g) * size + r) * 4;
        data[index + 0] = FloatToHalf(r / (size - 1.0f));
        data[index + 1] = FloatToHalf(g / (size - 1.0f));
        data[index + 2] = FloatToHalf(b / (size - 1.0f));
        data[index + 3] = FloatToHalf(1.0f);
      }
    }
  }
  return data;
}
```

ツールで基準の LUT 画像を加工して保存すれば、加工した内容が LUT に焼かれます。

### 外部ツール使用時の注意

| 注意 | 内容 |
| --- | --- |
| 色空間（sRGB かリニアか）をそろえる | ツールの色空間とゲームの入力の空間が合わないと、色がずれる |
| トーンマップを含めるか | LUT がトーンマップ後の LDR 用か、HDR 用か |
| ビット深度 | 8 ビット画像だとバンディング。16 ビット・.cube が望ましい |
| 解像度 | 32³ が一般的（ツールの出力も、32 か 33） |

## ゾーンごと・時間帯ごとの LUT

<strong>場所（洞窟・森・砂漠）や時間帯（朝・昼・夕・夜）</strong>ごとに別の LUT を用意し、状態に応じて切り替え・補間します。

```hlsl
Texture3D<float3> lut_a : register(t4);
Texture3D<float3> lut_b : register(t5);

float3 ApplyBlendedLut(float3 color, float blend) {
  float3 uvw = saturate(color) * ((kLutSize - 1.0) / kLutSize) + 0.5 / kLutSize;
  float3 a = lut_a.SampleLevel(linear_clamp, uvw, 0);
  float3 b = lut_b.SampleLevel(linear_clamp, uvw, 0);
  return lerp(a, b, blend);
}
```

ゾーン切り替えのコードの要点です。2 つの LUT を読んで `lerp` します。サンプルは 2 回ですが、それでも安いです。`blend` は 0 なら A、1 なら B で、時間で滑らかに変えます。補間の対象は、LUT の出力（色）を混ぜるか、パラメータを補間して LUT を再生成するかです。

補間の方式は 2 つです。LUT どうしを `lerp` する方法は、完成した LUT を混ぜるので、簡単で速いです。パラメータを補間して再生成する方法は、露出や LGG などを補間して LUT を作り直すので、非線形な調整も正しく補間できます。

### 時間帯の遷移

時刻に応じて、朝・昼・夕・夜の 4 つの LUT の間を補間します。太陽の高さなどから重みを決め、隣り合う 2 つを混ぜるのが自然です（[Sky Models](../../atmosphere/sky-models/index.md)）。

<!-- fig:lut-blend-zones:begin -->

<svg class="fig illust motion" data-fig="lut-blend-zones" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lut-blend-zones" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">場所ごとの色補正: 2 つの LUT を、プレイヤーの位置で、なめらかに混ぜる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">洞窟(青く暗い補正)から、野外(暖かく明るい補正)へ歩く。中間の灰色のパレットの見え方を、位置ごとに計算する</text>
<rect x="30" y="96" width="900" height="90" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 通路(左 = 洞窟、右 = 野外)。黄色の帯 = 混ぜる区間</text>
<rect x="298.0" y="114" width="340.0" height="60" fill="#fde68a" opacity="0.5"/>
<rect x="60" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="77" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="94" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="111" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="128" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="145" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="162" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="179" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="196" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="213" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="230" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="247" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="264" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="281" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="298" y="150" width="16.5" height="18" fill="#334155"/>
<rect x="315" y="150" width="16.5" height="18" fill="#364354"/>
<rect x="332" y="150" width="16.5" height="18" fill="#3c4653"/>
<rect x="349" y="150" width="16.5" height="18" fill="#434b51"/>
<rect x="366" y="150" width="16.5" height="18" fill="#4d514f"/>
<rect x="383" y="150" width="16.5" height="18" fill="#58584c"/>
<rect x="400" y="150" width="16.5" height="18" fill="#656049"/>
<rect x="417" y="150" width="16.5" height="18" fill="#726945"/>
<rect x="434" y="150" width="16.5" height="18" fill="#817242"/>
<rect x="451" y="150" width="16.5" height="18" fill="#907b3e"/>
<rect x="468" y="150" width="16.5" height="18" fill="#9e853b"/>
<rect x="485" y="150" width="16.5" height="18" fill="#ad8e37"/>
<rect x="502" y="150" width="16.5" height="18" fill="#bc9734"/>
<rect x="519" y="150" width="16.5" height="18" fill="#c9a030"/>
<rect x="536" y="150" width="16.5" height="18" fill="#d6a82d"/>
<rect x="553" y="150" width="16.5" height="18" fill="#e1af2a"/>
<rect x="570" y="150" width="16.5" height="18" fill="#ebb528"/>
<rect x="587" y="150" width="16.5" height="18" fill="#f2ba26"/>
<rect x="604" y="150" width="16.5" height="18" fill="#f8bd25"/>
<rect x="621" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="638" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="655" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="672" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="689" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="706" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="723" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="740" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="757" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="774" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="791" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="808" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="825" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="842" y="150" width="16.5" height="18" fill="#fbbf24"/>
<rect x="859" y="150" width="16.5" height="18" fill="#fbbf24"/>
<circle cx="128" cy="130" r="9" fill="#1f2937"><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1556;0.2178;0.3067;0.3689;0.4578;0.5200;0.6089;0.6711;1.0000" values="128;128;298;298;468;468;638;638;808;808"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2176;0.2178;1.0000" values="1;1;0;0"/><rect x="60" y="216" width="108" height="90" fill="#99a8be" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="180" y="216" width="108" height="90" fill="#bd858b" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="300" y="216" width="108" height="90" fill="#79b797" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="420" y="216" width="108" height="90" fill="#79a0ec" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="330" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">位置 4: 洞窟の LUT の割合 1.00 / 野外の LUT の割合 0.00</text>
<text x="60" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">灰色の見え方(R, G, B): 0.33, 0.40, 0.53</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2043;0.2044;0.3554;0.3556;1.0000" values="0;0;1;1;0;0"/><rect x="60" y="216" width="108" height="90" fill="#99a8be" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="180" y="216" width="108" height="90" fill="#bd858b" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="300" y="216" width="108" height="90" fill="#79b797" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="420" y="216" width="108" height="90" fill="#79a0ec" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="330" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">位置 14: 洞窟の LUT の割合 1.00 / 野外の LUT の割合 0.00</text>
<text x="60" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">灰色の見え方(R, G, B): 0.33, 0.40, 0.53</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3554;0.3556;0.5065;0.5067;1.0000" values="0;0;1;1;0;0"/><rect x="60" y="216" width="108" height="90" fill="#b1b2b6" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="180" y="216" width="108" height="90" fill="#dc8d85" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="300" y="216" width="108" height="90" fill="#8dc290" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="420" y="216" width="108" height="90" fill="#8daae1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="330" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">位置 24: 洞窟の LUT の割合 0.50 / 野外の LUT の割合 0.50</text>
<text x="60" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">灰色の見え方(R, G, B): 0.45, 0.46, 0.47</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5065;0.5067;0.6576;0.6578;1.0000" values="0;0;1;1;0;0"/><rect x="60" y="216" width="108" height="90" fill="#c6bcad" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="180" y="216" width="108" height="90" fill="#f6957e" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="300" y="216" width="108" height="90" fill="#9dcc89" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="420" y="216" width="108" height="90" fill="#9db3d6" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="330" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">位置 34: 洞窟の LUT の割合 0.00 / 野外の LUT の割合 1.00</text>
<text x="60" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">灰色の見え方(R, G, B): 0.57, 0.51, 0.42</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6576;0.6578;1.0000" values="0;0;1;1"/><rect x="60" y="216" width="108" height="90" fill="#c6bcad" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="180" y="216" width="108" height="90" fill="#f6957e" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="300" y="216" width="108" height="90" fill="#9dcc89" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="420" y="216" width="108" height="90" fill="#9db3d6" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="330" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">位置 44: 洞窟の LUT の割合 0.00 / 野外の LUT の割合 1.00</text>
<text x="60" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">灰色の見え方(R, G, B): 0.57, 0.51, 0.42</text>
</g>
<text x="60" y="205" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">色見本(灰・赤・緑・青)</text>
<text x="560" y="250" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">灰色の R − B(暖かさ):</text>
<text x="560" y="290" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="1">0</text>
<text x="560" y="290" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">-20<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2047;0.2049;1.0000" values="1;1;0;0"/></text>
<text x="560" y="290" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">-20<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2047;0.2049;0.3558;0.3560;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="290" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">-3<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3558;0.3560;0.5069;0.5071;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="290" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5069;0.5071;0.6580;0.6582;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="290" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6580;0.6582;1.0000" values="0;0;1;1"/></text>
<text x="630" y="290" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(×0.01。マイナス = 青い、プラス = 暖かい)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7998;0.8000;1.0000" values="0;0;1;1"/><rect x="40" y="400" width="880" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="424" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">1 歩ごとの色の変化は、最大 0.019(なめらか)。一気に切り替えると、一度に 0.25 変わる(ちらつき)</text>
<text x="56" y="448" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">2 つの LUT を混ぜる重みを、位置から計算する(smoothstep)。LUT 自体を混ぜるか、結果を混ぜる</text>
<text x="56" y="470" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">場所ごとに LUT を持つと、同じゲームでも、場面の雰囲気を作り分けられる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">洞窟と野外で、別の色補正をしたい<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">歩きながら、2 つの LUT の重みを、少しずつ入れ替える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8220;0.8222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">境目で、色が急に変わらない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8220;0.8222;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:lut-blend-zones:end -->

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| コンピュートで生成し、ボリュームでパラメータ補間 | ゾーンの境で滑らか |
| 外部ツールの LUT は 16 ビット・.cube | バンディングを避ける |
| <strong>LUT を連結（合成）</strong> | 複数の LUT を、1 つに焼く（エフェクト用の LUT を重ねる） |
| ダメージ・状態の演出は LUT のブレンド | 体力が低い時に色あせた LUT へ |
| 更新は変化時のみ | 毎フレーム再生成しない |
| デバッグ用に、LUT を画像に出す | LUT の中身を確認できるように |

## よくあるミス

??? failure "外部ツールで作った LUT を使ったら、色がずれる"
    <strong>色空間（sRGB かリニアか）・LUT の入力の定義</strong>をそろえる。

??? failure "8 ビット画像の LUT で、グラデーションにバンディング"
    16 ビット・.cube・FP16 の LUTにする。出力にディザリング。

??? failure "LUT の補間が、ゾーンの境で急に切り替わる"
    `blend` を時間・距離で滑らかに補間する。

??? failure "毎フレーム 64³ の LUT を生成して、無駄が出る"
    パラメータが変わった時だけ再生成する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] LUT は<strong>ゲーム内でコンピュート生成</strong>、または外部ツールで作って読み込む
    - [x] 基準（アイデンティティ）LUT に調整をかけて保存 ＝ LUT になる
    - [x] 色空間・ビット深度・エンコードをそろえる
    - [x] ゾーン・時間帯ごとに LUT を切り替え、`lerp` で補間
    - [x] 再生成は、パラメータが変わった時だけ

## 参考

- Hable, "Uncharted 2: HDR Lighting"（GDC 2010）
- Adobe, "Cube LUT Specification"
- Blackmagic Design, "DaVinci Resolve: LUT Export"

## 関連ページ

- [Color Grading](index.md)
- [3D LUT](lut-3d.md)
- [White Balance](white-balance.md)
- [Sky Models](../../atmosphere/sky-models/index.md)

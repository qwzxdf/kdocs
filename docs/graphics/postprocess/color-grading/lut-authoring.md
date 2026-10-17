---
title: LUT の作り方
tags:
  - 描画
---

# LUT の作り方

<strong>3D LUT は、「どうやって中身を作るか」</strong>が**次の問題**です。**ゲームの中で調整パラメータから LUT をコンピュート シェーダーで生成する**方法と、**外部の映像ツール（Photoshop・DaVinci Resolve）で作った LUT を読み込む**方法の**2 つ**があります。さらに**場所や時間帯ごとに LUT を切り替え・補間**して、**雰囲気を変える**のが**実用的**です。このページでは、**コンピュートでの生成・外部ツールとのやり取り・ゾーンごとの LUT と補間・更新のタイミング**を説明します。

!!! tip "ポイント"
    - <strong>ゲーム内で生成</strong>：<strong>パラメータ → コンピュート シェーダーで、全格子点に調整を適用して LUT を作る</strong>。<strong>パラメータが変わったときだけ再生成</strong>。
    - <strong>外部ツールで作る</strong>：<strong>基準の LUT（無加工）に、ツールでルックを焼き、保存して読み込む</strong>。
    - <strong>基準の LUT（アイデンティティ LUT）</strong>＝ <strong>変換しない LUT</strong>。<strong>これに調整をかけて保存すると、LUT になる</strong>。
    - <strong>ゾーンごとの LUT</strong>：<strong>場所・時間帯で LUT を切り替え、境で補間</strong>する。
    - <strong>2 つの LUT を混ぜる</strong>：<strong>1 回の表引きで両方読み、`lerp`</strong>。
    - <strong>再生成は毎フレーム不要</strong>。<strong>パラメータの変化時のみ</strong>。

## ゲーム内で生成（コンピュート）

<strong>3D の各格子点（r, g, b）</strong>について、**その色に調整（露出・ホワイト バランス・LGG・彩度・トーンマップ）を順に適用**し、**結果を LUT に書きます**。

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

float3 LogToLinear(float3 log_c) {
  const float kMinLog = -10.0;
  const float kMaxLog = 6.5;
  return exp2(log_c * (kMaxLog - kMinLog) + kMinLog);
}

[numthreads(8, 8, 8)]
void GenerateLut(uint3 id : SV_DispatchThreadID) {
  float3 uvw = (float3(id) + 0.5) / lut_size;
  float3 color = LogToLinear(uvw);

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
| **`numthreads(8, 8, 8)`** | **32³ なら、4×4×4 グループ**で**生成** |
| **`uvw = (id + 0.5) / size`** | **各セルの中心の座標**（**半テクセル**） |
| **`LogToLinear`** | **対数エンコードされた入力を、リニアに戻す**（**適用時の `LinearToLog` の逆**） |
| **調整を順に適用** | **露出 → ホワイト バランス → LGG → コントラスト → 彩度 → トーンマップ** |
| **コスト** | **32³ ＝ 32,768 回の計算のみ**。**1920×1080 の画面の 1.6 % 程度**で**非常に軽い** |

### いつ再生成するか

| タイミング | 内容 |
| --- | --- |
| **パラメータが変わった時** | **調整ボリュームの補間中は、毎フレーム** |
| **変わらない時** | **再生成しない**（**LUT はテクスチャとして保持**） |
| **ステージ読み込み時** | **初期の LUT を作る** |

**コンピュートの 1 回あたりが非常に軽い**ので、**毎フレーム再生成**しても**問題ない**場合も多いです。

## 外部ツールで作る

**映像のプロ用ツールで実際の画面を見ながら、ルックを調整し、LUT に書き出す**方法です。

| 手順 | 内容 |
| --- | --- |
| **① 基準の LUT を用意** | <strong>変換しない LUT（アイデンティティ LUT）</strong> を <strong>画像（.png）</strong>または **.cube** で出力 |
| **② ツールで調整** | **スクリーンショットに基準の LUT を重ねて、調整レイヤーで加工**（Photoshop）。**または、Resolve でグレーディング** |
| **③ LUT を書き出す** | **加工後の基準 LUT 画像を保存**（**.png**）または **.cube** |
| **④ ゲームに読み込む** | **3D テクスチャとして使う** |

### 基準の LUT（アイデンティティ LUT）

**入力色をそのまま出力する LUT** です。**各格子点の値がその座標の色と同じ**です。

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

**ツールで基準の LUT 画像を加工して保存**すれば、**加工した内容が LUT に焼かれます**。

### 外部ツール使用時の注意

| 注意 | 内容 |
| --- | --- |
| **色空間（sRGB かリニアか）をそろえる** | **ツールの色空間とゲームの入力の空間が合わないと、色がずれる** |
| **トーンマップを含めるか** | **LUT がトーンマップ後の LDR 用か、HDR 用か** |
| **ビット深度** | **8 ビット画像だとバンディング**。**16 ビット・.cube** が望ましい |
| **解像度** | **32³ が一般的**（**ツールの出力も、32 か 33**） |

## ゾーンごと・時間帯ごとの LUT

<strong>場所（洞窟・森・砂漠）や時間帯（朝・昼・夕・夜）</strong>ごとに**別の LUT** を**用意**し、**状態に応じて切り替え・補間**します。

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

| 点 | 説明 |
| --- | --- |
| **2 つの LUT を読んで `lerp`** | **サンプルは 2 回**（**それでも安い**） |
| **`blend`** | **0 なら A、1 なら B**（**時間で滑らかに変える**） |
| **補間の対象** | **LUT の出力（色）を混ぜる**。**またはパラメータを補間して LUT を再生成** |

| 方式 | 内容 | 長所 |
| --- | --- | --- |
| **LUT どうしを `lerp`** | **完成した LUT を混ぜる** | **簡単・速い** |
| **パラメータを補間して再生成** | **露出・LGG などを補間し、LUT を作り直す** | **非線形な調整も正しく補間** |

### 時間帯の遷移

**時刻に応じて、朝・昼・夕・夜の 4 つの LUT の間を補間**します。**太陽の高さ**などから**重みを決め**、**隣り合う 2 つを混ぜる**のが**自然**です（[空のモデル](../../atmosphere/sky-models/index.md)）。

<!-- fig:lut-blend-zones:begin -->

<svg class="fig illust motion" data-fig="lut-blend-zones" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lut-blend-zones" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">時間帯の LUT 遷移:隣り合う 2 つを、重みで混ぜる</text>
<rect x="50" y="90" width="520" height="200" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="180.0" y1="90" x2="180.0" y2="290" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="140.0" x2="570" y2="140.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="310.0" y1="90" x2="310.0" y2="290" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="570" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="440.0" y1="90" x2="440.0" y2="290" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="240.0" x2="570" y2="240.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="50" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">重み（縦）と時刻（横）</text>
<path d="M50.0,290.0 L60.83,273.33 L71.67,256.67 L82.5,240.0 L93.33,223.33 L104.17,206.67 L115.0,190.0 L125.83,173.33 L136.67,156.67 L147.5,140.0 L158.33,123.33 L169.17,106.67 L180.0,90.0 L190.83,106.67 L201.67,123.33 L212.5,140.0 L223.33,156.67 L234.17,173.33 L245.0,190.0 L255.83,206.67 L266.67,223.33 L277.5,240.0 L288.33,256.67 L299.17,273.33 L310.0,290.0 L320.83,290.0 L331.67,290.0 L342.5,290.0 L353.33,290.0 L364.17,290.0 L375.0,290.0 L385.83,290.0 L396.67,290.0 L407.5,290.0 L418.33,290.0 L429.17,290.0 L440.0,290.0 L450.83,290.0 L461.67,290.0 L472.5,290.0 L483.33,290.0 L494.17,290.0 L505.0,290.0 L515.83,290.0 L526.67,290.0 L537.5,290.0 L548.33,290.0 L559.17,290.0 L570.0,290.0" fill="none" stroke="#f4b183" stroke-width="4" opacity="1"/>
<text x="180.0" y="82" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#f4b183">朝</text>
<path d="M50.0,290.0 L60.83,290.0 L71.67,290.0 L82.5,290.0 L93.33,290.0 L104.17,290.0 L115.0,290.0 L125.83,290.0 L136.67,290.0 L147.5,290.0 L158.33,290.0 L169.17,290.0 L180.0,290.0 L190.83,273.33 L201.67,256.67 L212.5,240.0 L223.33,223.33 L234.17,206.67 L245.0,190.0 L255.83,173.33 L266.67,156.67 L277.5,140.0 L288.33,123.33 L299.17,106.67 L310.0,90.0 L320.83,106.67 L331.67,123.33 L342.5,140.0 L353.33,156.67 L364.17,173.33 L375.0,190.0 L385.83,206.67 L396.67,223.33 L407.5,240.0 L418.33,256.67 L429.17,273.33 L440.0,290.0 L450.83,290.0 L461.67,290.0 L472.5,290.0 L483.33,290.0 L494.17,290.0 L505.0,290.0 L515.83,290.0 L526.67,290.0 L537.5,290.0 L548.33,290.0 L559.17,290.0 L570.0,290.0" fill="none" stroke="#7ec8f2" stroke-width="4" opacity="1"/>
<text x="310.0" y="82" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#7ec8f2">昼</text>
<path d="M50.0,290.0 L60.83,290.0 L71.67,290.0 L82.5,290.0 L93.33,290.0 L104.17,290.0 L115.0,290.0 L125.83,290.0 L136.67,290.0 L147.5,290.0 L158.33,290.0 L169.17,290.0 L180.0,290.0 L190.83,290.0 L201.67,290.0 L212.5,290.0 L223.33,290.0 L234.17,290.0 L245.0,290.0 L255.83,290.0 L266.67,290.0 L277.5,290.0 L288.33,290.0 L299.17,290.0 L310.0,290.0 L320.83,273.33 L331.67,256.67 L342.5,240.0 L353.33,223.33 L364.17,206.67 L375.0,190.0 L385.83,173.33 L396.67,156.67 L407.5,140.0 L418.33,123.33 L429.17,106.67 L440.0,90.0 L450.83,106.67 L461.67,123.33 L472.5,140.0 L483.33,156.67 L494.17,173.33 L505.0,190.0 L515.83,206.67 L526.67,223.33 L537.5,240.0 L548.33,256.67 L559.17,273.33 L570.0,290.0" fill="none" stroke="#ff7f50" stroke-width="4" opacity="1"/>
<text x="440.0" y="82" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ff7f50">夕</text>
<path d="M50.0,90.0 L60.83,106.67 L71.67,123.33 L82.5,140.0 L93.33,156.67 L104.17,173.33 L115.0,190.0 L125.83,206.67 L136.67,223.33 L147.5,240.0 L158.33,256.67 L169.17,273.33 L180.0,290.0 L190.83,290.0 L201.67,290.0 L212.5,290.0 L223.33,290.0 L234.17,290.0 L245.0,290.0 L255.83,290.0 L266.67,290.0 L277.5,290.0 L288.33,290.0 L299.17,290.0 L310.0,290.0 L320.83,290.0 L331.67,290.0 L342.5,290.0 L353.33,290.0 L364.17,290.0 L375.0,290.0 L385.83,290.0 L396.67,290.0 L407.5,290.0 L418.33,290.0 L429.17,290.0 L440.0,290.0 L450.83,273.33 L461.67,256.67 L472.5,240.0 L483.33,223.33 L494.17,206.67 L505.0,190.0 L515.83,173.33 L526.67,156.67 L537.5,140.0 L548.33,123.33 L559.17,106.67 L570.0,90.0" fill="none" stroke="#1d2b64" stroke-width="4" opacity="1"/>
<text x="552.67" y="82" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1d2b64">夜</text>
<text x="50.0" y="308" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0 時</text>
<text x="180.0" y="308" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">6 時</text>
<text x="310.0" y="308" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">12 時</text>
<text x="440.0" y="308" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">18 時</text>
<text x="570.0" y="308" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">24 時</text>
<line x1="50.0" y1="90" x2="50.0" y2="290" stroke="#1f2937" stroke-width="2.5"><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0807;0.1021;0.1235;0.1449;0.1663;0.1877;0.2091;0.2305;0.2519;0.2733;0.2947;0.3160;0.3374;0.3588;0.3802;0.4016;0.4230;0.4444;0.4658;0.4872;0.5086;0.5300;0.5514;0.5728;0.5942;0.6156;0.6370;0.6584;0.6798;0.7012;0.7226;0.7440;0.7654;0.7868;0.8082;0.8296;1.0000" values="50;50;64.44;78.89;93.33;107.78;122.22;136.67;151.11;165.56;180;194.44;208.89;223.33;237.78;252.22;266.67;281.11;295.56;310;324.44;338.89;353.33;367.78;382.22;396.67;411.11;425.56;440;454.44;468.89;483.33;497.78;512.22;526.67;541.11;555.56;570;570"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0807;0.1021;0.1235;0.1449;0.1663;0.1877;0.2091;0.2305;0.2519;0.2733;0.2947;0.3160;0.3374;0.3588;0.3802;0.4016;0.4230;0.4444;0.4658;0.4872;0.5086;0.5300;0.5514;0.5728;0.5942;0.6156;0.6370;0.6584;0.6798;0.7012;0.7226;0.7440;0.7654;0.7868;0.8082;0.8296;1.0000" values="50;50;64.44;78.89;93.33;107.78;122.22;136.67;151.11;165.56;180;194.44;208.89;223.33;237.78;252.22;266.67;281.11;295.56;310;324.44;338.89;353.33;367.78;382.22;396.67;411.11;425.56;440;454.44;468.89;483.33;497.78;512.22;526.67;541.11;555.56;570;570"/></line>
<rect x="610" y="110" width="130" height="90" fill="#1d2b64" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0807;0.1021;0.1235;0.1449;0.1663;0.1877;0.2091;0.2305;0.2519;0.2733;0.2947;0.3160;0.3374;0.3588;0.3802;0.4016;0.4230;0.4444;0.4658;0.4872;0.5086;0.5300;0.5514;0.5728;0.5942;0.6156;0.6370;0.6584;0.6798;0.7012;0.7226;0.7440;0.7654;0.7868;0.8082;0.8296;1.0000" values="#1d2b64;#1d2b64;#353a67;#4d496b;#65586e;#7d6772;#947575;#ac8479;#c4937c;#dca280;#f4b183;#e7b48f;#dab69c;#cdb9a8;#c0bbb4;#b2bec1;#a5c0cd;#98c3d9;#8bc5e6;#7ec8f2;#8cc0e0;#9bb8ce;#a9b0bc;#b7a8aa;#c69f98;#d49786;#e28f74;#f18762;#ff7f50;#e67652;#cd6c54;#b46357;#9b5a59;#81505b;#68475d;#4f3e60;#363462;#1d2b64;#1d2b64"/></rect>
<text x="675" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">混ぜた色</text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">00 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0804;0.0807;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">00 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0804;0.0807;0.1018;0.1021;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">01 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1018;0.1021;0.1232;0.1235;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">02 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1232;0.1235;0.1446;0.1449;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">02 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1446;0.1449;0.1660;0.1663;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">03 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1660;0.1663;0.1874;0.1877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">04 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1874;0.1877;0.2088;0.2091;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">04 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2088;0.2091;0.2302;0.2305;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">05 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2302;0.2305;0.2516;0.2519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">06 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2516;0.2519;0.2730;0.2733;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">06 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2730;0.2733;0.2944;0.2947;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">07 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2944;0.2947;0.3158;0.3160;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">08 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3158;0.3160;0.3372;0.3374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">08 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3372;0.3374;0.3586;0.3588;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">09 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3586;0.3588;0.3800;0.3802;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">10 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3800;0.3802;0.4013;0.4016;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">10 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4013;0.4016;0.4227;0.4230;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">11 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4227;0.4230;0.4441;0.4444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">12 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;0.4655;0.4658;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">12 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4655;0.4658;0.4869;0.4872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">13 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4869;0.4872;0.5083;0.5086;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">14 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5083;0.5086;0.5297;0.5300;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">14 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5297;0.5300;0.5511;0.5514;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">15 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5511;0.5514;0.5725;0.5728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">16 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5725;0.5728;0.5939;0.5942;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">16 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5939;0.5942;0.6153;0.6156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">17 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6153;0.6156;0.6367;0.6370;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">18 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6367;0.6370;0.6581;0.6584;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">18 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6581;0.6584;0.6795;0.6798;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">19 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6795;0.6798;0.7009;0.7012;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">20 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7009;0.7012;0.7223;0.7226;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">20 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7223;0.7226;0.7437;0.7440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">21 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7437;0.7440;0.7651;0.7654;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">22 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7651;0.7654;0.7865;0.7868;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">22 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7865;0.7868;0.8079;0.8082;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">23 時<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8079;0.8082;0.8293;0.8296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夜 100%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0804;0.0807;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 11% / 夜 89%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0804;0.0807;0.1018;0.1021;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 22% / 夜 78%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1018;0.1021;0.1232;0.1235;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 33% / 夜 67%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1232;0.1235;0.1446;0.1449;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 44% / 夜 56%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1446;0.1449;0.1660;0.1663;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 56% / 夜 44%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1660;0.1663;0.1874;0.1877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 67% / 夜 33%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1874;0.1877;0.2088;0.2091;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 78% / 夜 22%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2088;0.2091;0.2302;0.2305;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 89% / 夜 11%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2302;0.2305;0.2516;0.2519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 100%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2516;0.2519;0.2730;0.2733;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 89% / 昼 11%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2730;0.2733;0.2944;0.2947;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 78% / 昼 22%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2944;0.2947;0.3158;0.3160;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 67% / 昼 33%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3158;0.3160;0.3372;0.3374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 56% / 昼 44%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3372;0.3374;0.3586;0.3588;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 44% / 昼 56%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3586;0.3588;0.3800;0.3802;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 33% / 昼 67%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3800;0.3802;0.4013;0.4016;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 22% / 昼 78%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4013;0.4016;0.4227;0.4230;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">朝 11% / 昼 89%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4227;0.4230;0.4441;0.4444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 100%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;0.4655;0.4658;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 89% / 夕 11%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4655;0.4658;0.4869;0.4872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 78% / 夕 22%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4869;0.4872;0.5083;0.5086;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 67% / 夕 33%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5083;0.5086;0.5297;0.5300;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 56% / 夕 44%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5297;0.5300;0.5511;0.5514;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 44% / 夕 56%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5511;0.5514;0.5725;0.5728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 33% / 夕 67%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5725;0.5728;0.5939;0.5942;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 22% / 夕 78%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5939;0.5942;0.6153;0.6156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">昼 11% / 夕 89%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6153;0.6156;0.6367;0.6370;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 100%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6367;0.6370;0.6581;0.6584;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 89% / 夜 11%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6581;0.6584;0.6795;0.6798;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 78% / 夜 22%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6795;0.6798;0.7009;0.7012;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 67% / 夜 33%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7009;0.7012;0.7223;0.7226;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 56% / 夜 44%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7223;0.7226;0.7437;0.7440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 44% / 夜 56%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7437;0.7440;0.7651;0.7654;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 33% / 夜 67%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7651;0.7654;0.7865;0.7868;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 22% / 夜 78%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7865;0.7868;0.8079;0.8082;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="270" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">夕 11% / 夜 89%<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8079;0.8082;0.8293;0.8296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="350" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">各時刻で、隣り合う 2 つの LUT の重みの合計が 1。太陽の高さなどから重みを決める。</text>
</svg>

<!-- fig:lut-blend-zones:end -->

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **コンピュートで生成し、ボリュームでパラメータ補間** | **ゾーンの境で滑らか** |
| **外部ツールの LUT は 16 ビット・.cube** | **バンディングを避ける** |
| <strong>LUT を連結（合成）</strong> | **複数の LUT を、1 つに焼く**（**エフェクト用の LUT を重ねる**） |
| **ダメージ・状態の演出は LUT のブレンド** | **体力が低い時に色あせた LUT へ** |
| **更新は変化時のみ** | **毎フレーム再生成しない** |
| **デバッグ用に、LUT を画像に出す** | **LUT の中身を確認できるように** |

## よくあるミス

??? failure "外部ツールで作った LUT を使ったら、色がずれる"
    **色空間（sRGB かリニアか）・LUT の入力の定義**を**そろえる**。

??? failure "8 ビット画像の LUT で、グラデーションにバンディング"
    **16 ビット・.cube・FP16 の LUT**にする。**出力にディザリング**。

??? failure "LUT の補間が、ゾーンの境で急に切り替わる"
    **`blend` を時間・距離で滑らかに補間**する。

??? failure "毎フレーム 64³ の LUT を生成して、無駄が出る"
    **パラメータが変わった時だけ**再生成する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] LUT は<strong>ゲーム内でコンピュート生成</strong>、または<strong>外部ツールで作って読み込む</strong>
    - [x] <strong>基準（アイデンティティ）LUT に調整をかけて保存</strong> ＝ <strong>LUT になる</strong>
    - [x] <strong>色空間・ビット深度・エンコードをそろえる</strong>
    - [x] <strong>ゾーン・時間帯ごとに LUT を切り替え、`lerp` で補間</strong>
    - [x] <strong>再生成は、パラメータが変わった時だけ</strong>

## 参考

- Hable, "Uncharted 2: HDR Lighting"（GDC 2010）
- Adobe, "Cube LUT Specification"
- Blackmagic Design, "DaVinci Resolve: LUT Export"

## 関連ページ

- [カラー グレーディング](index.md)
- [3D LUT](lut-3d.md)
- [ホワイト バランス](white-balance.md)
- [空のモデル](../../atmosphere/sky-models/index.md)

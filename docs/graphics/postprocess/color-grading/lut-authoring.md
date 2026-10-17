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

**時刻に応じて、朝・昼・夕・夜の 4 つの LUT の間を補間**します。**太陽の高さ**などから**重みを決め**、**隣り合う 2 つを混ぜる**のが**自然**です（[空のモデル](../../atmosphere/sky-models.md)）。

<!-- fig:lut-blend-zones:begin -->
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
- [空のモデル](../../atmosphere/sky-models.md)

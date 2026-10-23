---
title: TAA・アップスケーラ・VRS
tags:
  - 最適化
  - 3Dゲーム
---

# TAA・アップスケーラ・VRS

ピクセル処理が重いとき、最も直接的な解決策は**ピクセルの数を減らす**ことです。しかし、単に解像度を下げると画面がぼやけます。TAA（時間的アンチエイリアシング）・アップスケーラ・VRSは見た目の品質をなるべく保ちながら、実際に計算するピクセルを減らす手法です。このページでは、それぞれの仕組みと注意点を説明します。

!!! tip "ポイント"
    - 目的は<strong>ピクセルシェーダーの計算量を減らす</strong>こと。
    - <strong>TAA</strong>は過去のフレームを混ぜて、ギザギザとノイズを減らす。
    - アップスケーラ（DLSS・FSR・TAAU）は、低解像度で描いて、時間情報も使って高解像度にする。
    - VRSは画面の場所ごとにシェーディングの細かさを変える（DX12 Ultimate）。
    - 動きベクトルの精度が品質を決める。ゴースト（残像）に注意。
    - 動的解像度と組み合わせて、フレーム時間を一定に保つ。

## TAA（時間的アンチエイリアシング）

### 仕組み

MSAA は、1 フレームの中でサンプルを増やします。TAA は**複数のフレームにまたがってサンプルを集めます**。

| 手順 | 内容 |
| --- | --- |
| ① ジッター | 毎フレーム、投影行列をサブピクセル単位でずらす（Halton 列など） |
| ② 描画 | 通常どおり描く。フレームごとに少しずつ違う位置をサンプルする |
| ③ 履歴の再投影 | 動きベクトルで前フレームの同じ点を探す |
| ④ 混ぜる | 現在の色と履歴を混ぜる（履歴を 90% など） |
| ⑤ 履歴の検証 | 履歴が古い・不正なら、混ぜる量を減らす（クランプ） |

### 何が改善するのか

| 改善 | 説明 |
| --- | --- |
| エッジの滑らかさ | 数フレーム分のサンプルが混ざるので、MSAA より品質が高い |
| Deferred と相性が良い | MSAA は G-Buffer が重くなるが、TAA は後処理で済む |
| ノイズの平均化 | AO・SSR・影のサンプル数を減らしても、時間で平均されて滑らかになる |
| 鏡面のちらつき | 細かいハイライトが安定する |

### 注意点

| 問題 | 対策 |
| --- | --- |
| ゴースト（残像） | 速く動く物の履歴を捨てる。速度と深度の差で検出する |
| ぼやけ | 混ぜすぎない。シャープ処理を後で足す |
| 動きベクトル | スキニング・頂点アニメ・パーティクルの動きも正しく出力する |
| 透明物 | 深度がないので履歴が不正になりやすい。TAA の後に描く |
| 画面外から入る部分 | 履歴がないので混ぜる量を減らす |

## アップスケーラ

**低い解像度で描いて、高い解像度に拡大**します。単純な拡大と違い、TAA と同じく過去のフレームの情報を使うので、細部をある程度復元できます。

| 方式 | 仕組み |
| --- | --- |
| TAAU | TAA の延長。低解像度のジッター付きサンプルを、高解像度に蓄積する |
| FSR（AMD） | 空間・時間情報を使うアルゴリズム。ほぼ全ての GPU で動く |
| DLSS（NVIDIA） | ニューラルネットワークで復元する。専用ハードウェア（Tensor コア）を使う |
| XeSS（Intel） | 同様の機械学習ベース |

| 設定 | 内部解像度（出力 4K の場合） | 負荷の目安 |
| --- | --- | --- |
| 品質 | 約 67%（2560×1440） | 約 45% |
| バランス | 約 58% | 約 34% |
| パフォーマンス | 50%（1920×1080） | 25% |

内部解像度に比例して、ピクセルシェーダーとレンダーターゲットの帯域が減ります。ただし、UI は出力解像度で描きます。

## 動的解像度

負荷に応じて、**描画解像度をフレームごとに変える**方法です。

| 点 | 説明 |
| --- | --- |
| 目的 | フレーム時間を一定に保つ（重い場面で少し解像度を下げる） |
| 制御 | 直近の GPU 時間から、次のフレームの解像度を決める |
| UI | 出力解像度のまま（ぼやけさせない） |
| ポストプロセス | 低解像度で描いた結果を、最後に拡大する |

## VRS（可変レート シェーディング）

画面の全ピクセルで同じ細かさでシェーダーを実行するのは、無駄なことがあります。**VRS**は場所ごとにシェーディングのレートを変えます（例：2×2 ピクセルを 1 回の計算で）。

| 方式 | 説明 |
| --- | --- |
| ドロー コールごと | 物体単位でレートを指定（遠景・暗い物体） |
| 画像ベース | 画面上のタイルごとにレートを書いた画像を渡す |
| 向く場所 | 暗い領域・動きが速い領域・周辺視野（VR のフォービエイテッド） |
| 対応 | DX12 Ultimate（Tier 1 / 2）。DX11 では使えない |

エッジやハイライトのある場所は、細かいレートのまま残し、平坦な場所だけを粗くするのがコツです。

<!-- fig:halton-jitter:begin -->

<svg class="fig illust motion" data-fig="halton-jitter" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-halton-jitter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">TAA のジッター: フレームごとに、1 画素の中の別の位置で描く(Halton 2,3)</text>
<rect x="240" y="90" width="300" height="300" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<line x1="390.0" y1="90" x2="390.0" y2="390" stroke="#e2e8f0" stroke-width="1"/>
<line x1="240" y1="240.0" x2="540" y2="240.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="240" y="80" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">1 画素の内側（正方形）。点 = そのフレームのサンプル位置</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><circle cx="390.0" cy="290.0" r="9" fill="#2563eb" opacity="0.9"/>
<text x="390.0" y="294.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/><circle cx="315.0" cy="190.0" r="9" fill="#2ea043" opacity="0.9"/>
<text x="315.0" y="194.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2516;0.2519;1.0000" values="0;0;1;1"/><circle cx="465.0" cy="356.66666666666663" r="9" fill="#e5aa28" opacity="0.9"/>
<text x="465.0" y="360.66666666666663" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">3</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3404;0.3407;1.0000" values="0;0;1;1"/><circle cx="277.5" cy="256.6666666666667" r="9" fill="#e5484d" opacity="0.9"/>
<text x="277.5" y="260.6666666666667" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/><circle cx="427.5" cy="156.66666666666669" r="9" fill="#7c3aed" opacity="0.9"/>
<text x="427.5" y="160.66666666666669" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000" values="0;0;1;1"/><circle cx="352.5" cy="323.33333333333337" r="9" fill="#2563eb" opacity="0.9"/>
<text x="352.5" y="327.33333333333337" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">6</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6071;0.6074;1.0000" values="0;0;1;1"/><circle cx="502.5" cy="223.33333333333331" r="9" fill="#2ea043" opacity="0.9"/>
<text x="502.5" y="227.33333333333331" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">7</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6960;0.6963;1.0000" values="0;0;1;1"/><circle cx="258.75" cy="123.33333333333334" r="9" fill="#e5aa28" opacity="0.9"/>
<text x="258.75" y="127.33333333333334" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">8</text>
</g>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">毎フレーム、カメラをほんの少し(1 画素以内)ずらす<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1〜4 フレーム目: 離れた位置を順に使う<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3701;0.3704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8 フレームで、画素の中をまんべんなく巡る。これを平均して高精細にする<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:halton-jitter:end -->

## TAA の解決パスを、実装する

履歴を混ぜるパスを、シェーダーで見ます。要点は、<strong>履歴を、そのまま混ぜず、「今の周りの色の範囲」に、収めてから、混ぜる</strong>ことです。これでゴーストを、抑えます（[TAA](../graphics/postprocess/antialiasing/taa.md)）。

```hlsl
Texture2D<float3> g_current : register(t0);       // 今フレームの色（ジッター付き）
Texture2D<float3> g_history : register(t1);       // 前フレームの結果
Texture2D<float2> g_velocity : register(t2);      // 動きベクトル（UV 単位）
SamplerState g_linear_clamp : register(s0);

float3 RgbToYCoCg(float3 c) {                      // 色空間を変えると、クランプが、色味を保ちやすい
  return float3(0.25 * c.r + 0.5 * c.g + 0.25 * c.b, 0.5 * c.r - 0.5 * c.b, -0.25 * c.r + 0.5 * c.g - 0.25 * c.b);
}
float3 YCoCgToRgb(float3 c) {
  return float3(c.x + c.y - c.z, c.x + c.z, c.x - c.y - c.z);
}

float4 PSResolve(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  const int2 p = int2(pos.xy);

  // ① 今のピクセルと、周りの 3×3 の色から、「今フレームで、ありうる色の範囲」（平均と分散）を求める。
  float3 current = RgbToYCoCg(g_current.Load(int3(p, 0)));
  float3 m1 = 0, m2 = 0;
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      float3 c = RgbToYCoCg(g_current.Load(int3(p + int2(x, y), 0)));
      m1 += c;
      m2 += c * c;
    }
  }
  float3 mean = m1 / 9.0;
  float3 sigma = sqrt(max(m2 / 9.0 - mean * mean, 0.0));
  float3 box_min = mean - 1.25 * sigma;               // 分散クリッピング（Salvi）。1.0〜1.5 が目安
  float3 box_max = mean + 1.25 * sigma;

  // ② 動きベクトルで、前フレームの同じ点を探して、履歴の色を読む。
  float2 velocity = g_velocity.Load(int3(p, 0));
  float3 history = RgbToYCoCg(g_history.SampleLevel(g_linear_clamp, uv - velocity, 0));

  // ③ 履歴を、範囲の中に、収める（範囲の外の履歴は、古い・間違った色なので、引き戻す）。
  history = clamp(history, box_min, box_max);

  // ④ 混ぜる。動きが大きいほど、履歴を、信用しない。
  float motion = length(velocity * float2(1920.0, 1080.0));     // 画素単位の、動きの大きさ
  float history_weight = lerp(0.95, 0.7, saturate(motion / 8.0));
  float3 result = lerp(current, history, history_weight);
  return float4(YCoCgToRgb(result), 1.0);
}
```

数行ずつ見ると、①で「今、ありうる色の範囲」を作り、②で履歴を読み、③で、その範囲に収め、④で、混ぜています。③のクランプが、ゴースト対策の、要です。動いた物の、後ろに、古い色が残っても、範囲の外なので、引き戻されます。範囲を、広げる（`1.25` を大きく）と、ゴーストが増え、狭めると、ちらつきが増えます。

## ジッターの、入れ方

```cpp
// Halton 数列（底 2 と 3）で、サブピクセルのずらしを作る。8 フレームで、1 周。
float Halton(int index, int base) {
  float result = 0.0f;
  float f = 1.0f;
  while (index > 0) {
    f /= base;
    result += f * (index % base);
    index /= base;
  }
  return result;
}

DirectX::XMFLOAT2 JitterOffset(int frame, int width, int height) {
  const int i = (frame % 8) + 1;
  // -0.5〜0.5 ピクセルを、NDC（-1〜1）の単位に直す（1 ピクセル = 2/width）。
  return {(Halton(i, 2) - 0.5f) * 2.0f / width, (Halton(i, 3) - 0.5f) * 2.0f / height};
}
// 射影行列の _31, _32 に、ずらしを入れる（符号の理由は、TAA のページ）。速度の計算では、ジッターを、引いて使う。
```

## 動的解像度の、制御

GPU 時間を測って、次のフレームの、解像度を決めます。

```cpp
// 目標の GPU 時間（たとえば 60 FPS なら 14 ms）に、近づけるよう、解像度の倍率を、少しずつ、動かす。
class DynamicResolution {
 public:
  float Update(float gpu_ms) {
    const float target_ms = 14.0f;
    const float error = (target_ms - gpu_ms) / target_ms;     // 速すぎれば正、遅すぎれば負
    scale_ += error * 0.1f;                                    // 少しずつ動かす（急に変えると、ちらつく）
    scale_ = std::clamp(scale_, 0.6f, 1.0f);                   // 60%〜100%
    return scale_;
  }

 private:
  float scale_ = 1.0f;
};
// 使い方: 解像度 = 出力解像度 × scale。ピクセル数は scale² に比例して減るので、scale 0.7 でも、約半分。
```

ピクセル数は、<strong>倍率の 2 乗</strong>で減ります（0.7 倍なら 0.49 倍）。そのため、少しの倍率の変化で、GPU 時間が、大きく変わります。UI は、出力解像度のまま描き、3D の結果だけを、拡大して重ねます。

## アップスケーラに、渡すもの

DLSS・FSR・XeSS などは、TAA と同じ入力を、必要とします。

| 入力 | 内容 |
| --- | --- |
| 低解像度の色 | ジッター付きで描いた、HDR の色（トーン マッピング前） |
| 深度 | 低解像度の深度（逆 Z が多い） |
| 動きベクトル | 低解像度、または出力解像度。ジッターを、含まない |
| ジッターの値 | そのフレームで、入れたずらし（ピクセル単位） |
| 露出 | 露出の値（明るさの変化を、正しく扱うため） |
| リセット フラグ | カットシーンの切り替えなど、履歴が使えないとき |

動きベクトルが、不正確（スキニングや、パーティクルが、出ていない）と、アップスケーラの結果にも、ゴーストが出ます。<strong>エンジン側で、正しい入力を、そろえることが、品質の、ほとんど全て</strong>です。

## よくあるミス

??? failure "動きベクトルを出さずに TAA を入れて、ゴーストが出る"
    動く物・スキニングの動きベクトルを、必ず出力します。

??? failure "TAA を入れて、全体がぼやける"
    混ぜる量とシャープ処理を調整します。

??? failure "UI まで低解像度で描いて、文字がぼやける"
    UI は出力解像度で描きます。

??? failure "透明物を TAA の前に描いて、ゴーストが出る"
    TAA の後に描く、または専用のマスクを使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>TAA</strong> は、過去のフレームを混ぜて品質を上げる。動きベクトルが肝
    - [x] アップスケーラは、低解像度で描いて高解像度へ。負荷は内部解像度に比例
    - [x] 動的解像度で、フレーム時間を一定に
    - [x] VRS は、場所ごとにシェーディングを粗く（DX12 Ultimate）
    - [x] UI とポストの順序に注意

## 関連ページ

- [描画最適化](index.md)
- [低解像度のエフェクト](low-res-effects.md)
- [フレーム時間の設計](../optimize/frame-budget.md)
- [ポストプロセス](postprocess.md)
- [Anti-Aliasing](../graphics/postprocess/antialiasing/index.md)

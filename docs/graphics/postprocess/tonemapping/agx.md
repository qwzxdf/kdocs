---
title: AgX and Others
tags:
  - 描画
---

# AgX and Others

<strong>フィルミックや ACES は、明るく鮮やかな色が白や別の色へ偏る</strong>欠点があります。近年はこの「色相の破綻」を抑える、新しいトーンマップが増えました。このページでは、AgX・Tony McMapface・Khronos PBR Neutral の考え方・特徴・使い分けを説明します。

!!! tip "ポイント"
    - 新しい方式の狙い ＝ <strong>明るい彩度の高い色でも、色相が変わらず、自然に白へ向かう</strong>。
    - <strong>AgX</strong>：中立寄りのフィルミック。広い色域を扱い、Blender の標準。パラメータが少なく、使いやすい。
    - Tony McMapface：3D LUT ベース。ブルームとの相性が良い。
    - Khronos PBR Neutral：商品の色をできるだけ忠実に（E コマース向け）。
    - 選ぶ基準：色の再現（忠実）か、映画的な絵（フィルム）か。
    - どれも露出の後・ガンマの前。

!!! info "このページを読む前に"
    - [Tone Mapping and Exposure](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 何が改善されたか

<strong>ACES や Hable では</strong>、R・G・B に別々に曲線を掛けるため、明るい色の比率が崩れます（青い光が紫に赤が黄色に）。新しい方式は色空間を工夫したり、LUT で調整したりして、これを緩和します。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="色の偏りの比較">
<text x="20" y="26" class="fig-title">同じ青い強い光を、トーンマップすると</text>
<g font-size="13">
<text x="40" y="62" style="font-weight:700">入力（HDR）</text>
<rect x="40" y="72" width="190" height="40" fill="#2563eb"/><text x="40" y="132" style="font-size:12px">明るさを上げていく →</text>
<text x="280" y="62" style="font-weight:700">ACES 近似</text>
<defs><linearGradient id="ag-aces" x1="0" x2="1"><stop offset="0" stop-color="#1d4ed8"/><stop offset="0.6" stop-color="#8b5cf6"/><stop offset="1" stop-color="#f5e9ff"/></linearGradient>
<linearGradient id="ag-agx" x1="0" x2="1"><stop offset="0" stop-color="#1d4ed8"/><stop offset="0.6" stop-color="#5b8def"/><stop offset="1" stop-color="#eef5ff"/></linearGradient></defs>
<rect x="280" y="72" width="190" height="40" fill="url(#ag-aces)"/><text x="280" y="132" style="font-size:12px">紫がかって白へ</text>
<text x="520" y="62" style="font-weight:700">AgX など</text>
<rect x="520" y="72" width="190" height="40" fill="url(#ag-agx)"/><text x="520" y="132" style="font-size:12px">青のまま白へ</text>
</g>
<text x="40" y="180" style="font-size:13px">色相を保つ方式は、強い光（ネオン・魔法・炎）の色が、意図どおりに見える。</text>
<text x="40" y="204" style="font-size:13px">一方、フィルムのような「ハイライトの色飛び」は弱くなる（好みで選ぶ）。</text>
</svg>

## AgX

<strong>AgX</strong> は、Troy Sobotka が設計した、フィルム風でありつつ色相が安定するトーンマップです。Blender 4.0 から標準になりました。

| 特徴 | 内容 |
| --- | --- |
| 広い色域で扱う | 作業を広い色空間で行い、最後に出力へ |
| 対数空間で曲線を掛ける | 露出の幅（ダイナミック レンジ）を、対数で受けて、S 字で圧縮 |
| 色相を保ちつつ、白へ滑らかに | ハイライトの色飛びが穏やか |
| ルック（見た目）を選べる | Punchy（強め）・Golden など、後段でルックを調整 |

実装の流れ（概略）です。

```hlsl
float3 AgXTonemap(float3 color) {
  color = mul(kAgXInputMatrix, color);
  color = max(color, 1e-10);
  color = clamp(log2(color), kMinEV, kMaxEV);
  color = (color - kMinEV) / (kMaxEV - kMinEV);
  color = AgXContrastCurve(color);
  color = ApplyLook(color);
  color = mul(kAgXOutputMatrix, color);
  return pow(max(color, 0.0), 2.2);
}
```

| 段階 | 内容 |
| --- | --- |
| 入力行列 | 作業用の広い色空間へ |
| 対数にする | `log2` で、EV 単位の範囲にして、最小・最大 EV で正規化（だいたい −12.5〜+4 EV） |
| コントラスト曲線 | S 字（6 次の多項式など） |
| ルック | 彩度・コントラストの好みの調整 |
| 出力行列とガンマ | sRGB へ戻す |

行列と多項式の係数は、公開されている実装（Blender の OCIO 設定・各種 HLSL 移植）をそのまま使うのが確実です。自分で一から作る必要はありません。

## Tony McMapface

<strong>Tomasz Stachowiak</strong> による、3D LUT ベースのトーンマップです。あらかじめ作った 48×48×48 の LUT を、表引きするだけで使えます。

| 特徴 | 内容 |
| --- | --- |
| 計算が軽い | LUT の 1 回の参照だけ（シェーダーが単純） |
| 色相が破綻しにくい | ブルームの白い光や鮮やかなエフェクトが自然 |
| ブルームとの相性 | ブルームのにじみが色付きの光として自然に出る |
| LUT を差し替えられる | 自分の画作りの LUT に置き換えれば、別のルックにもなる |

```hlsl
Texture3D<float3> tony_lut : register(t5);

float3 TonyMcMapface(float3 color) {
  float3 encoded = color / (color + 1.0);
  float3 uvw = encoded * (47.0 / 48.0) + 0.5 / 48.0;
  return tony_lut.SampleLevel(linear_clamp, uvw, 0);
}
```

コードの要点です。`x / (x + 1)` で入力を 0〜1 にして、LUT の入力範囲に収めます（LUT 側の前提です）。半テクセルのずらし（`* (47/48) + 0.5/48`）で、3D LUT の端で補間が正しくなります。`linear_clamp` で、LUT の外に出ないよう端で止めます。

## Khronos PBR Neutral

<strong>Khronos が、E コマース（商品の 3D 表示）向けに作った</strong>、「色を変えない」トーンマップです。

Khronos PBR Neutral の特徴です。暗部から中間は曲線を掛けず、ほぼ素通しなので、商品の色が正確です。明部だけ、ある閾値（約 0.8）を超えた部分を滑らかに圧縮します。圧縮するときに、白へ向かう量を調整して色相を保ちます。

映画的な絵ではなく、「見たままの色」が大切な場面（商品・建築・カスタマイズ画面）に向きます。ゲームでも色の正確さが大事な UI の 3D 表示に使えます。

## 使い分け

| 方式 | 絵の性格 | 色相 | コスト | 向く場面 |
| --- | --- | --- | --- | --- |
| ACES 近似 | 強いコントラスト・映画的 | 偏る | 軽い | 映画風・標準 |
| AgX | 中立寄りのフィルミック | 安定 | 中 | 色を壊したくない本格的な画作り |
| Tony McMapface | 自然・ブルームと好相性 | 安定 | <strong>軽い（LUT）</strong> | エフェクトが多い |
| PBR Neutral | ほぼ素通し・忠実 | ほぼ保つ | 軽い | 商品・色の正確さ |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| ルックはトーンマップの後に分ける | AgX の「ルック」や、グレーディングを別の LUT に分ける（[Color Grading](../color-grading/index.md)） |
| 設定で切り替えられるようにする | ACES / AgX / Neutral をスイッチで（ユーザーの好み・ステージごと） |
| HDR ディスプレイ用を別に用意 | SDR の曲線をそのまま HDR に使わない（[Gamma and HDR Output](gamma-srgb.md)） |
| エフェクトの色を確認 | 選んだ曲線を通した見た目で、火・魔法の色を決める |

## よくあるミス

??? failure "AgX の行列や係数を、自分で書き写して、一部間違える"
    <strong>公開されている実装をそのまま使う</strong>。テスト画像（グレースケールと彩度のグラデーション）で、確認する。

??? failure "Tony McMapface の LUT の端で、色がずれる"
    半テクセルのずらしを入れ、`linear_clamp` を使う。

??? failure "PBR Neutral を、映画的な絵に使って、地味になる"
    用途に合った曲線を選ぶ。映画的なら、ACES・AgX。

??? failure "曲線を切り替えたら、全体の明るさが変わって、露出がずれる"
    各曲線の中間灰の出力が違う。切り替えたら、露出補正で合わせる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 新しい方式の狙い ＝ <strong>明るい彩度の高い色でも、色相が破綻しない</strong>
    - [x] AgX ＝ 中立寄りのフィルミック。公開実装をそのまま使う
    - [x] Tony McMapface ＝ 3D LUT。軽く、ブルームと好相性
    - [x] PBR Neutral ＝ 色の忠実さ重視（商品向け）
    - [x] 曲線を替えたら、露出も見直す

## 参考

- Sobotka, "AgX"（GitHub: sobotka/AgX）
- Stachowiak, "Tony McMapface"（GitHub: h3r2tic/tony-mc-mapface）
- Khronos, "PBR Neutral Tone Mapper"（KhronosGroup/ToneMapping）
- Blender Foundation, "Color Management: AgX"

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [ACES](aces.md)
- [Preserving Hue](hue-preservation.md)
- [Bloom](../bloom/index.md)

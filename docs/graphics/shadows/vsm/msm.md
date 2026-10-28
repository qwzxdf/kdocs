---
title: MSM
tags:
  - 描画
---

# MSM

<strong>MSM（モーメント シャドウ マップ）</strong>は、深度の 1 次・2 次だけでなく、3 次・4 次のモーメントも保存することで、VSM の光漏れをさらに抑える方式です。深度の分布をより正確に表現できるので、光漏れがほぼ見えない影が得られます。計算が複雑ですがストレージは 4 チャンネルでEVSM と同程度です。このページでは考え方・保存する値・使いどころを説明します。

!!! tip "ポイント"
    - MSM ＝ 深度の 4 つのモーメント（d, d², d³, d⁴）を保存する。
    - 高次のモーメントで、分布を正確に表せ光漏れが少ない。
    - 4 チャンネル。EVSM と同程度のメモリ。
    - 比較の計算は少し複雑（方程式を解く）。

!!! info "このページを読む前に"
    - [VSM, ESM and MSM](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## MSM（モーメント シャドウ マップ）
<strong>MSM</strong>（Moment Shadow Maps、Peters & Klein 2015）は、4 つのモーメント（z, z², z³, z⁴）を保存し、ハンバーガーのモーメント問題を解いて、より正確な可視性の上限を求めます。

| 項目 | 内容 |
| --- | --- |
| 保存 | 4 つのモーメント（4 チャンネル。16 ビットでも変換すれば足りるように工夫） |
| 利点 | 光漏れが小さい。VSM・ESM より安定 |
| 欠点 | 計算が複雑（4 モーメントから、可視性を求める計算が重い） |

## 考え方：モーメントを 4 つ持つ

<strong>MSM</strong>（Moment Shadow Mapping、Peters と Klein、2015）は 深度のモーメントを 4 つ（`z`、`z²`、`z³`、`z⁴`）保存します。VSM は 2 つ（`z`、`z²`、つまり平均と分散）でした。モーメントが多いほど深度の分布を詳細に表せます。

| 手法 | 保存するモーメント | 表せる分布 |
| --- | --- | --- |
| VSM | `z`、`z²`（2 つ） | 平均と分散だけ。1 つの山のような分布 |
| MSM（4 モーメント） | `z`、`z²`、`z³`、`z⁴` | 2 つの遮蔽物（2 層）を区別できる |

光漏れは 複数の遮蔽物が重なるとき（シャドウ マップの 1 画素に 2 つの深度が混ざる）に起きます。VSM は 2 つの深度を 1 つの平均と分散に潰してしまい両者の間の隙間に光漏れが出ます。MSM は 2 つの深度を区別できるので、光漏れが少ないです。

## 影の判定

保存した 4 つのモーメントから、<strong>「画素の深度 `t` より手前に遮蔽物がある確率」の下限</strong>（影の 最も厳しい見積もり）を数値的に計算します。VSM のチェビシェフの不等式の一般化にあたります。

```hlsl
// 4 モーメントから、影の判定（Hamburger 4MSM。論文の、方法）。概略。
float ComputeMsmShadowIntensity(float4 moments, float depth, float depth_bias, float moment_bias) {
  // ① モーメントにわずかな、バイアスを混ぜて、数値的に安定させる
  float4 b = lerp(moments, float4(0.5, 0.5, 0.5, 0.5), moment_bias);
```

最初に 4 つのモーメントを 0.5 側へわずかに寄せます。値がちょうど 0 や 1 に張り付くと次の連立方程式が特異（解けない）になるのでそれを避ける、安定化です。

```hlsl
  // ② 3×3 の、連立方程式（コレスキー分解）を解いて、2 つの、遮蔽する深度（z2、z3）を推定する
  float3 z;
  z[0] = depth - depth_bias;
  float L32D22 = mad(-b[0], b[1], b[2]);
  float D22 = mad(-b[0], b[0], b[1]);
  float squared_depth_variance = mad(-b[1], b[1], b[3]);
  float D33D22 = dot(float2(squared_depth_variance, -L32D22), float2(D22, L32D22));
  float inv_D22 = 1.0 / D22;
  float L32 = L32D22 * inv_D22;
  float3 c = float3(1.0, z[0], z[0] * z[0]);
  c[1] -= b.x;
  c[2] -= b.y + L32 * c[1];
  c[1] *= inv_D22;
  c[2] *= D22 / D33D22;
  c[1] -= L32 * c[2];
  c[0] -= dot(c.yz, b.xy);
```

2 つの遮蔽する深度を推定します。画素の深度 `z[0]` を含めた 3 つの深度のモーメントが観測値と一致するような、深度の組を求める連立方程式をコレスキー分解で解いています。式の細部は Hamburger の論文に従った、数値計算でここでは「モーメントから、2 つの深度を逆算している」ととらえれば十分です。

```hlsl
  float p = c[1] / c[2];
  float q = c[0] / c[2];
  float D = (p * p * 0.25) - q;
  float r = sqrt(D);
  z[1] = -p * 0.5 - r;
  z[2] = -p * 0.5 + r;
```

連立方程式の解を 2 次方程式の解の公式で取り出し 2 つの深度 `z[1]`、`z[2]` を得ます。これが「この画素の上に遮蔽物があるとすればどの深度か」の推定です。

```hlsl
  // ③ 得られた 2 つの深度（z[1]、z[2]）と、画素の深度 z[0] の、順序から、影の強さを決める
  float4 switch_val = (z[2] < z[0]) ? float4(z[1], z[0], 1.0, 1.0)
                    : ((z[1] < z[0]) ? float4(z[0], z[1], 0.0, 1.0) : float4(0.0, 0.0, 0.0, 0.0));
  float quotient = (switch_val[0] * z[2] - b[0] * (switch_val[0] + z[2]) + b[1])
                 / ((z[2] - switch_val[1]) * (z[0] - z[1]));
  float shadow_intensity = switch_val[2] + switch_val[3] * quotient;
  return saturate(shadow_intensity);        // 1 = 完全に影、0 = 光が当たる
}
```

上のコードは 論文のアルゴリズムの骨格です。数値的に安定させるためにバイアスやコレスキー分解の細かい手順が必要です。実際の実装では論文の公開コードを参照してそのまま移植する方法が確実です。

## 保存と書き出し

4 つのモーメントを <strong>最適な形式</strong>に 変換して保存します（論文は、量子化によって 16 ビット × 4 に収める変換も提案）。

```hlsl
// シャドウ パス: 深度の 4 つのモーメントを書き出す（R32G32B32A32_FLOAT、または、R16G16B16A16_UNORM + 最適化変換）。
float4 main(float4 pos : SV_Position) : SV_Target {
  float z = pos.z;
  float z2 = z * z;
  return float4(z, z2, z2 * z, z2 * z2);
}
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 光漏れが少ない（EVSM よりさらに少ない場面が多い） |
| 長所 | ぼかしミップ、異方性フィルタが使える |
| 長所 | 指数を使わないので、浮動小数点のあふれの問題がない |
| 短所 | 4 チャンネル（メモリが通常の 4 倍。16 ビットに量子化すれば 2 倍） |
| 短所 | 判定の計算が重い（連立方程式を解く） |
| 短所 | 数値的な不安定さ（バイアスの調整が必要。浮動小数点の精度に敏感） |
| 短所 | 実装が複雑（論文のコードを参考にしないと難しい） |

## VSM 系の手法の比較

| 手法 | チャンネル | 光漏れ | 判定のコスト | 実装 |
| --- | --- | --- | --- | --- |
| VSM | 2 | 大きい | 小 | 簡単 |
| ESM | 1 | 影が薄れる | 小 | 簡単 |
| EVSM | 4（32 ビット） | 小さい | 中 | 中 |
| MSM | 4 | 最も小さい | 大 | 複雑 |

## よくあるミス

??? failure "モーメントを 16 ビットで保存して、精度が足りない"
    <strong>専用の最適化ベクトル変換</strong>を使い 16 ビット整数で保存する実装（Peters 方式）を参照。

## これだけ覚える

!!! abstract "まとめ"
    - [x] MSM ＝ 4 つのモーメントで、光漏れを抑える
    - [x] 高品質だが、計算は複雑

## 参考

- Peters, Klein, "Moment Shadow Mapping", Symposium on Interactive 3D Graphics and Games 2015
- Donnelly, Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games 2006
- Lauritzen, McGuire, "Layered Variance Shadow Maps", Graphics Interface 2008（光漏れの軽減）
- Peters, Klein, "Moment Shadow Mapping" の公開コードと、補足資料（論文の Web ページ）

## 関連ページ

- [VSM, ESM and MSM](index.md)
- [EVSM](evsm.md)
- [Comparison with PCF](comparison.md)

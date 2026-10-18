---
title: MSM
tags:
  - 描画
---

# MSM

<strong>MSM（モーメント シャドウ マップ）</strong>は、<strong>深度の 1 次・2 次だけでなく、3 次・4 次のモーメントも保存</strong>することで、VSM の光漏れを、さらに抑える方式です。深度の分布を、より正確に表現できるので、光漏れがほぼ見えない影が得られます。計算が複雑ですが、ストレージは 4 チャンネルでEVSM と同程度です。このページでは、考え方・保存する値・使いどころを説明します。

!!! tip "ポイント"
    - MSM ＝ 深度の 4 つのモーメント（d, d², d³, d⁴）を保存。
    - 高次のモーメントで、分布を正確に表せ、光漏れが少ない。
    - 4 チャンネル。EVSM と同程度のメモリ。
    - 比較の計算は、少し複雑（方程式を解く）。

## MSM（モーメント シャドウ マップ）
<strong>MSM</strong>（Moment Shadow Maps、Peters & Klein 2015）は、<strong>4 つのモーメント</strong>（z, z², z³, z⁴）を保存し、ハンバーガーのモーメント問題を解いて、より正確な、可視性の上限を求めます。

| 項目 | 内容 |
| --- | --- |
| 保存 | 4 つのモーメント（4 チャンネル。16 ビットでも変換すれば足りるように工夫） |
| 利点 | 光漏れが非常に小さい。VSM・ESM より、安定 |
| 欠点 | 計算が複雑（4 モーメントから、可視性を求める計算が重い） |

## 考え方：モーメントを、4 つ、持つ

<strong>MSM</strong>（Moment Shadow Mapping、Peters と Klein、2015）は、<strong>深度の、モーメント</strong>を、4 つ（`z`、`z²`、`z³`、`z⁴`）保存します。VSM は、2 つ（`z`、`z²`、つまり、平均と分散）でした。モーメントが、多いほど、深度の分布を、詳細に、表せます。

| 手法 | 保存するモーメント | 表せる、分布 |
| --- | --- | --- |
| VSM | `z`、`z²`（2 つ） | 平均と、分散だけ。1 つの、山のような分布 |
| MSM（4 モーメント） | `z`、`z²`、`z³`、`z⁴` | 2 つの、遮蔽物（2 層）を、区別できる |

<strong>光漏れ</strong>は、<strong>複数の遮蔽物が、重なる</strong>とき（シャドウ マップの、1 画素に、2 つの、深度が、混ざる）に、起きます。VSM は、2 つの深度を、1 つの、平均と分散に、潰してしまい、両者の間の、隙間に、光漏れが、出ます。MSM は、2 つの、深度を、区別できるので、光漏れが、少ないです。

## 影の、判定

保存した、4 つの、モーメントから、<strong>「画素の深度 `t` より、手前に、遮蔽物が、ある確率」の、下限</strong>（影の、<strong>最も、厳しい</strong>見積もり）を、数値的に、計算します。VSM の、チェビシェフの不等式の、一般化に、あたります。

```hlsl
// 4 モーメントから、影の判定（Hamburger 4MSM。論文の、方法）。概略。
float ComputeMsmShadowIntensity(float4 moments, float depth, float depth_bias, float moment_bias) {
  // ① モーメントに、わずかな、バイアスを、混ぜて、数値的に、安定させる
  float4 b = lerp(moments, float4(0.5, 0.5, 0.5, 0.5), moment_bias);

  // ② 3×3 の、連立方程式（コレスキー分解）を、解いて、2 つの、遮蔽する深度（z2、z3）を、推定する
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
  float p = c[1] / c[2];
  float q = c[0] / c[2];
  float D = (p * p * 0.25) - q;
  float r = sqrt(D);
  z[1] = -p * 0.5 - r;
  z[2] = -p * 0.5 + r;

  // ③ 得られた 2 つの深度（z[1]、z[2]）と、画素の深度 z[0] の、順序から、影の強さを、決める
  float4 switch_val = (z[2] < z[0]) ? float4(z[1], z[0], 1.0, 1.0)
                    : ((z[1] < z[0]) ? float4(z[0], z[1], 0.0, 1.0) : float4(0.0, 0.0, 0.0, 0.0));
  float quotient = (switch_val[0] * z[2] - b[0] * (switch_val[0] + z[2]) + b[1])
                 / ((z[2] - switch_val[1]) * (z[0] - z[1]));
  float shadow_intensity = switch_val[2] + switch_val[3] * quotient;
  return saturate(shadow_intensity);        // 1 = 完全に影、0 = 光が当たる
}
```

上のコードは、<strong>論文の、アルゴリズムの、骨格</strong>です。<strong>数値的に、安定させる</strong>ために、バイアスや、コレスキー分解の、細かい手順が、必要です。実際の実装では、論文の、公開コードを、参照して、そのまま、移植する方法が、確実です。

## 保存と、書き出し

4 つの、モーメントを、<strong>最適な、形式</strong>に、<strong>変換</strong>して、保存します（論文は、量子化によって、16 ビット × 4 に、収める、変換も、提案）。

```hlsl
// シャドウ パス: 深度の 4 つのモーメントを、書き出す（R32G32B32A32_FLOAT、または、R16G16B16A16_UNORM + 最適化変換）。
float4 main(float4 pos : SV_Position) : SV_Target {
  float z = pos.z;
  float z2 = z * z;
  return float4(z, z2, z2 * z, z2 * z2);
}
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 光漏れが、少ない（EVSM より、さらに、少ない場面が、多い） |
| 長所 | ぼかし、ミップ、異方性フィルタが、使える |
| 長所 | 指数を、使わないので、浮動小数点の、あふれの問題が、ない |
| 短所 | 4 チャンネル（メモリが、通常の 4 倍。16 ビットに、量子化すれば、2 倍） |
| 短所 | 判定の、計算が、重い（連立方程式を、解く） |
| 短所 | 数値的な、不安定さ（バイアスの、調整が、必要。浮動小数点の、精度に、敏感） |
| 短所 | 実装が、複雑（論文の、コードを、参考にしないと、難しい） |

## VSM 系の、手法の、比較

| 手法 | チャンネル | 光漏れ | 判定の、コスト | 実装 |
| --- | --- | --- | --- | --- |
| VSM | 2 | 大きい | 小 | 簡単 |
| ESM | 1 | 影が、薄れる | 小 | 簡単 |
| EVSM | 4（32 ビット） | 小さい | 中 | 中 |
| MSM | 4 | 最も小さい | 大 | 複雑 |

## よくあるミス

??? failure "モーメントを 16 ビットで保存して、精度が足りない"
    <strong>専用の最適化ベクトル変換</strong>を使い、<strong>16 ビット整数で保存</strong>する実装（Peters 方式）を参照。

## これだけ覚える

!!! abstract "まとめ"
    - [x] MSM ＝ 4 つのモーメントで、光漏れを抑える
    - [x] 高品質だが、計算は複雑

## 参考

- Peters, Klein, "Moment Shadow Mapping", Symposium on Interactive 3D Graphics and Games 2015
- Donnelly, Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games 2006
- Lauritzen, McGuire, "Layered Variance Shadow Maps", Graphics Interface 2008（光漏れの、軽減）
- Peters, Klein, "Moment Shadow Mapping" の公開コードと、補足資料（論文の Web ページ）

## 関連ページ

- [VSM, ESM and MSM](index.md)
- [EVSM](evsm.md)
- [Comparison with PCF](comparison.md)

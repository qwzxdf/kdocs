---
title: カメラのブラー
tags:
  - 描画
---

# カメラのブラー

**カメラが動いたり回ったりすると、静止している背景全体が、流れるように見えます**。**カメラ モーション ブラー**は、**この背景の流れ**を**表現**する**ブラー**で、**コストが安く、スピード感への効果が大きい**ため、**最初に実装すべき**部分です。**必要なのは画素ごとの深度と前フレームのカメラ行列だけ**で、**動く物体の速度バッファを作らなくても実現**できます。このページでは、**深度から速度を再構成する方法・並進と回転の違い・注意点（動く物体・遠景）・より良いやり方**を説明します。

!!! tip "ポイント"
    - カメラ ブラー ＝ <strong>カメラの動きによる、静止した物の見かけの動き</strong>を<strong>ぼかしにする</strong>。
    - <strong>深度（ワールド位置を再構成）</strong>＋<strong>前フレームのカメラ行列</strong>で、<strong>各画素の速度が分かる</strong>。
    - <strong>回転</strong>は<strong>画面全体が同じ向きに流れる</strong>。<strong>並進</strong>は<strong>近い物ほど速く流れる（視差）</strong>。
    - <strong>動く物体には、カメラ速度は不正確</strong>（<strong>物体ブラー</strong>で上書き）。
    - <strong>遠景（深度が最奥）</strong>は<strong>回転の影響だけ</strong>。
    - <strong>ゲーム内のカット切り替え</strong>では<strong>速度を 0 に</strong>する。

## 並進と回転

**カメラの動きは、2 種類**あります。

| 動き | 画面での見え方 |
| --- | --- |
| <strong>回転（見回す）</strong> | **画面全体が同じ向きにほぼ同じ速さで流れる**（**距離に依らない**） |
| <strong>並進（歩く・走る・走行）</strong> | **近い物ほど速く、遠い物ほど遅く流れる**（**視差**）。**進行方向の中心から外へ放射状に広がる** |

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="カメラの動きと速度">
<text x="20" y="26" class="fig-title">回転は一様に流れ、前進は中心から放射状に流れる</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">回転（右を向く）</text>
<rect x="0" y="0" width="300" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<g stroke="#e5484d" stroke-width="2.5" marker-end="url(#cb-arrow)"><line x1="260" y1="30" x2="200" y2="30"/><line x1="260" y1="70" x2="200" y2="70"/><line x1="260" y1="110" x2="200" y2="110"/><line x1="140" y1="30" x2="80" y2="30"/><line x1="140" y1="70" x2="80" y2="70"/><line x1="140" y1="110" x2="80" y2="110"/></g>
<defs><marker id="cb-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#e5484d"/></marker></defs>
<text x="0" y="164" style="font-size:12px">どこも同じ向き・同じ大きさ</text>
</g>
<g transform="translate(420,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">並進（前に進む）</text>
<rect x="0" y="0" width="300" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="150" cy="70" r="4" fill="#2563eb"/>
<g stroke="#e5484d" stroke-width="2.5" marker-end="url(#cb-arrow)"><line x1="160" y1="65" x2="185" y2="52"/><line x1="140" y1="65" x2="115" y2="52"/><line x1="160" y1="75" x2="185" y2="88"/><line x1="140" y1="75" x2="115" y2="88"/><line x1="200" y1="50" x2="262" y2="14"/><line x1="100" y1="50" x2="38" y2="14"/><line x1="200" y1="90" x2="262" y2="126"/><line x1="100" y1="90" x2="38" y2="126"/></g>
<text x="0" y="164" style="font-size:12px">中心は動かず、外へ行くほど速い（近い物ほど速い）</text>
</g>
</svg>

## 深度から速度を作る

**画素の深度から、その点のワールド位置を再構成し**、**前フレームのカメラでその点がどこに見えていたか**を**計算**します。

```hlsl
float2 CameraVelocity(float2 uv, float depth) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  float4 clip = float4(ndc, depth, 1.0);
  float4 world = mul(clip, inverse_view_projection);
  world /= world.w;
  float4 previous_clip = mul(world, previous_view_projection);
  float2 previous_ndc = previous_clip.xy / previous_clip.w;
  float2 previous_uv = float2(previous_ndc.x * 0.5 + 0.5, 0.5 - previous_ndc.y * 0.5);
  return uv - previous_uv;
}
```

| 点 | 説明 |
| --- | --- |
| **`inverse_view_projection`** | **今フレームの逆行列**。**深度 → ワールド位置** |
| **`previous_view_projection`** | **前フレームのカメラ**。**ワールド位置 → 前の画面位置** |
| **`uv − previous_uv`** | **今 − 前**（<strong>[速度バッファ](velocity-buffer.md)と同じ定義</strong>） |
| **ジッター** | **両方の行列から、ジッターを除く** |

## 特徴と注意

| 項目 | 内容 |
| --- | --- |
| **安い** | **フルスクリーンで深度を 1 回読み、行列を 2 回掛けるだけ**。**物体の速度書き込み不要** |
| **動く物体は不正確** | **物体はカメラ以外にも自分で動く**。**物体の速度で上書き** |
| **遠景** | **深度が最奥（スカイ）は、回転の影響だけ**になる（**並進は無視**） |
| **カメラが速く回る** | **ブラーが強くなりすぎる**ので、**最大長で制限** |
| **ジャンプ・カット** | **カメラが瞬間移動したフレームは、前フレームの行列を今に置き換え、速度 0** |

## 速度の合成

**最終的な速度**は、**動く物体は速度バッファ、それ以外はカメラ速度**を**使います**。

```hlsl
float2 FinalVelocity(float2 uv, float depth) {
  float2 object_velocity = velocity_buffer.SampleLevel(point_clamp, uv, 0).xy;
  bool has_object_velocity = any(object_velocity != 0.0) || stencil_flag;
  return has_object_velocity ? object_velocity : CameraVelocity(uv, depth);
}
```

**ステンシル・専用ビットで、「速度を書いた画素」を区別**する**と**、<strong>「速度ぴったり 0 の動く物体」と「書かれていない画素」を、取り違えません</strong>。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **カメラ ブラーだけをまず実装** | **安く、効果が大きい** |
| **速度の最大長を制限** | **急回転でも画面が崩れない**（**画面高さの 3〜5 %**） |
| **カットで即リセット** | **前フレームの行列を今に** |
| **プレイヤーの武器・手を除外** | **カメラに固定された物は、カメラ ブラーを掛けない**（**ステンシル／マスク**） |
| **遠景は強さを弱める** | **空の流れが強すぎるのを防ぐ** |
| **シャッター角で強さを調整** | [強さと TAA](strength-taa.md) |

## よくあるミス

??? failure "カメラに固定された武器まで、ブラーがかかる"
    **ビューモデルは、カメラと同じ動きなので、速度 0**。**マスクして除外**。

??? failure "カメラが瞬間移動したフレームで、画面全体が大きくぶれる"
    **カットや瞬間移動では、前フレームの行列を今の行列にして、速度を 0**。

??? failure "ブラーが強すぎて、酔う"
    **最大長・強さを抑える**。**オプションで切れる**ようにする。

??? failure "静止した物の速度が、ジッターでふるえる"
    **行列からジッターを除いて**速度を計算。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カメラ ブラー ＝ <strong>カメラの動きによる、静止物の見かけの動き</strong>を<strong>ぼかす</strong>
    - [x] <strong>深度 ＋ 前フレームのカメラ行列</strong>で<strong>速度を再構成</strong>
    - [x] <strong>回転は一様、並進は近い物ほど速い</strong>
    - [x] <strong>動く物体は、物体の速度で上書き</strong>
    - [x] <strong>カットで速度 0</strong>、<strong>最大長で制限</strong>

## 参考

- Rosado, "Motion Blur as a Post-Processing Effect"（GPU Gems 3）
- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）

## 関連ページ

- [モーション ブラー](index.md)
- [速度バッファ](velocity-buffer.md)
- [オブジェクトのブラー](object-blur.md)
- [ぼかしの実装](blur-pass.md)

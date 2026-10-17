---
title: コンタクト シャドウ
tags:
  - 描画
---

# コンタクト シャドウ

シャドウ マップは、**解像度に限りがあり**、**バイアスで少し浮かせる**ので**物体が地面に接する付近の細かい影**が**欠けたり、浮いて見えたり**します（ピーター パンニング）。**コンタクト シャドウ**（Contact Shadows）は、<strong>画面空間（深度バッファ）</strong>で、**画素から光の方向へ短いレイを進め**、**手前にある物に当たるか**を調べる方式です。**接触部の細かい影**を**シャドウ マップを補って**、**安く**描きます。

!!! tip "ポイント"
    - <strong>画素から、光の方向へ深度バッファの上で短いレイ</strong>を進める。
    - <strong>レイの深度が深度バッファより奥に入ったら、遮蔽された</strong>。
    - <strong>距離は短い</strong>（数十 cm〜1 m）。<strong>シャドウ マップの接触部の欠けを補う</strong>のが目的。
    - 欠点：<strong>見えている面しか、知らない</strong>（画面外・裏側は遮蔽物にならない）。<strong>厚み</strong>の仮定。
    - <strong>画素ごとにジッター</strong>して、<strong>サンプル数を減らし</strong>、ノイズを<strong>時間蓄積</strong>で消す。
    - <strong>[SSR](../reflections/ssr-basics.md)・[SSAO](../ao/ssao-hemisphere.md) と同じ「画面空間」の方式</strong>で<strong>同じ限界</strong>を持つ。

## なぜ接触部で影が欠けるのか

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="接触部の影の欠け">
<text x="20" y="24" class="fig-title">シャドウ マップは、接触部で影が浮く・欠ける（ピーター パンニング）</text>
<line x1="60" y1="200" x2="720" y2="200" stroke="currentColor" stroke-width="4"/>
<rect x="150" y="150" width="70" height="50" fill="rgba(150,150,150,0.8)" stroke="currentColor" stroke-width="2"/><text x="140" y="140" style="font-size:12px">物体（地面に接している）</text>
<rect x="220" y="196" width="140" height="8" fill="#111" opacity="0.85"/><rect x="220" y="196" width="22" height="8" fill="#e5484d" opacity="0.5"/>
<text x="250" y="226" style="font-size:12px;fill:#e5484d;font-weight:700">接触部の影が欠ける</text>
<text x="420" y="70" style="font-size:13px">原因：</text><text x="420" y="94" style="font-size:12px">・バイアスで深度を浮かせる → 近い所は影が出ない</text><text x="420" y="114" style="font-size:12px">・シャドウ マップの 1 テクセルが、物の大きさに比べて粗い</text>
<text x="420" y="152" style="font-size:13px">解決：</text><text x="420" y="176" style="font-size:12px">画面の深度で、短い距離を調べる → 接触部だけ、細かく影を補う</text>
</svg>

## 原理：画面空間のレイマーチ

**画素のビュー空間位置** `P` から、**光の方向** `L` へ**短いレイ**を**少しずつ進め**ます。**各ステップの位置を画面に投影**し、**その画素の深度**と比べます。**レイが深度バッファの面より奥に入った**ら、**面の裏側に潜った＝遮蔽**されたと判断します。

| 手順 | 内容 |
| --- | --- |
| **① レイの端点** | `P` と、`P + L · max_distance`（ビュー空間） |
| **② 画面に投影** | 両端をスクリーン座標へ（[SSR](../reflections/ssr-basics.md)と同じ） |
| **③ ステップごとに比べる** | 各サンプルで**レイの深度 ＞ 深度バッファ** ならば、遮蔽 |
| **④ 厚みを考慮** | **深度の差が大きすぎる**場合は、**遠くの面の手前を通っただけ**として、無視 |

```hlsl
float ContactShadow(float3 view_pos, float3 light_dir_view, float2 pixel, float jitter) {
  float3 ray_end = view_pos + light_dir_view * kContactDistance;
  float2 uv0 = ProjectToUV(view_pos);
  float2 uv1 = ProjectToUV(ray_end);
  float z0 = view_pos.z;
  float z1 = ray_end.z;

  float shadow = 1.0;
  [loop] for (int i = 1; i <= kContactSteps; ++i) {
    float t = (i - 1.0 + jitter) / kContactSteps;
    float2 uv = lerp(uv0, uv1, t);
    float ray_z = 1.0 / lerp(1.0 / z0, 1.0 / z1, t);
    float scene_z = LinearDepth(depth_tex.SampleLevel(point_sampler, uv, 0).r);
    float diff = ray_z - scene_z;
    if (diff > kBias && diff < kThickness) {
      shadow = 0.0;
      break;
    }
  }
  return shadow;
}
```

| 点 | 説明 |
| --- | --- |
| **`1/z` で補間** | **透視投影では、1/z が画面上で線形**（[SSR](../reflections/ssr-basics.md)） |
| **`jitter`** | **画素ごとのステップ位置のずらし**（IGN）。**ステップ数を少なく**しても、**縞がノイズに変わる** |
| **`kBias`** | **自己遮蔽（面自身）を避ける**、小さな許容値 |
| **`kThickness`** | **厚み**。**これ以上、遮蔽物の奥にある**ものは、**遮蔽物ではない**として扱う |
| **`kContactDistance`** | **短い距離**（0.1〜1 m 程度） |

## 厚みの問題

**深度バッファは、「一番手前の面」の深度しか持たない**ので、**その面の厚み**（裏側までの奥行き）が、**分かりません**。

| 厚みの設定 | 結果 |
| --- | --- |
| **薄すぎる** | <strong>細い物（柵・草）</strong>を、**すり抜ける**ことがある |
| **厚すぎる** | **遠くの面の手前を通っただけ**でも、**遮蔽扱い**（**誤った影**） |
| **適度** | シーンに合わせて調整（**距離で変える**・**物のスケール**） |

**完全な解決はなく**、**パラメータの調整**で**妥当な見た目**に寄せます。

## シャドウ マップとの合成

**コンタクト シャドウ**は、**単独ではなく、シャドウ マップを補う**ために使います。

| 合成 | 内容 |
| --- | --- |
| <strong>最小値（暗い方）</strong> | `shadow = min(shadow_map, contact)` が、一般的 |
| **距離でフェード** | **コンタクト シャドウは、近くだけ**。**距離でフェードアウト** |
| **シャドウ マップのバイアスを、大きく** | **コンタクト シャドウが、接触部を担当**するので**シャドウ マップのバイアスを**、**安全側**（アクネを避ける方）に**振れる** |

## コストと工夫

| 項目 | 内容 |
| --- | --- |
| **ステップ数** | **8〜16**。**多いほど、細部を捉える** |
| **レイの距離** | **短い**ほど安い |
| **ジッター ＋ 時間蓄積** | **少ないステップ**＋**ノイズ**を**TAA**で消す |
| **画面中心・近景に限定** | **遠くはコンタクト シャドウを省略** |
| **ライト ごとに計算** | **主ライト（太陽）だけ**に適用することが多い |
| **コンピュート シェーダー** | **グループ共有メモリ**に**深度を読み込み**、**キャッシュ効率**を上げる実装もある |

## 画面空間の限界

| 限界 | 内容 |
| --- | --- |
| **画面外の遮蔽物** | **深度バッファにない**ので、**遮蔽物として使えない** |
| **見えない面の裏側** | **厚みを知らない** |
| **視点依存** | **カメラが動くと**、**影が変わって見える**ことがある |
| **画面端** | **サンプルが画面外に出る**と**情報がない** |

**そのため、あくまで補助**で**シャドウ マップの代わりには、できません**。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **接触部の細かい影**が出る | **画面にある物だけ**が遮蔽物 |
| **安い**（短いレイ） | **厚みの扱いが難しい** |
| **シャドウ マップのバイアスの問題を補える** | **画面外・裏側は不可** |
| **細い物（草・髪・ディテール）にもある程度、効く** | **ノイズ**が出る（ジッターのとき） |

## よくあるミス

??? failure "自己遮蔽で、面全体が暗くなる"
    **小さなバイアス**を入れる、**レイの開始位置を法線方向に少しずらす**。

??? failure "遠くの面の手前を通っただけで、影になる"
    **厚み**（`kThickness`）を、設定します。

??? failure "非線形の深度のまま比べて、距離でおかしくなる"
    **線形な深度**（ビュー空間の z）で、比べます。

??? failure "全画面・長い距離で計算して、重い"
    **近景だけ・短い距離**にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンタクト シャドウ ＝ <strong>画素から光の方向へ、深度バッファ上で短いレイを進め</strong>、<strong>遮蔽</strong>を調べる
    - [x] <strong>シャドウ マップの、接触部の欠け・ピーター パンニングを補う</strong>
    - [x] <strong>厚み</strong>の仮定が必要（<strong>薄すぎ → すり抜け、厚すぎ → 誤った影</strong>）
    - [x] <strong>画面にある物しか見えない</strong>（<strong>補助</strong>として使う）
    - [x] <strong>ジッター ＋ 時間蓄積</strong>で、<strong>ステップ数を減らす</strong>

## 参考

- Sousa, "Secrets of CryEngine 3 Graphics Technology"（2011、画面空間の影）
- Bend Studio, "Screen Space Shadows"（GDC 2023 など）

## 関連ページ

- [影](index.md)
- [バイアス](bias/index.md)
- [SSR（画面空間の反射）](../reflections/ssr-basics.md)
- [SSAO](../ao/ssao-hemisphere.md)

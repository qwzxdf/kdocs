---
title: ギャザー方式
tags:
  - 描画
---

# ギャザー方式

<strong>ギャザー（Gather）</strong>は、<strong>「各画素が自分の周りの画素を集めて平均する」</strong>方式の DOF です。**出力の画素ごとに、CoC の半径の円の中のサンプルを読み**、**加重平均**します。**実装が簡単で、GPU に向いていて速い**ので、**現代のゲームの標準**です。このページでは、**基本の考え方・サンプルの配置（ヴォーゲル螺旋）・「他の画素の CoC」を考慮した重み・ちらつきの対策・半解像度・コスト**を説明します。

!!! tip "ポイント"
    - ギャザー ＝ <strong>各出力画素が、周りの画素を CoC の半径で集めて平均する</strong>。
    - サンプルは<strong>円盤状に散らす</strong>（<strong>ヴォーゲル螺旋・ポアソン円盤</strong>）。<strong>16〜64 サンプル</strong>が目安。
    - <strong>重要</strong>：<strong>集める相手の CoC も見る</strong>。<strong>相手のボケが自分に届かないなら、混ぜない</strong>（<strong>ピント内の物にぼけた背景がにじむ</strong>のを防ぐ）。
    - <strong>半解像度</strong>で行い、<strong>フル解像度に合成</strong>すると<strong>コストが 1/4</strong>。
    - <strong>ノイズ的なサンプルの回転</strong>＋<strong>ぼかし</strong>で、<strong>サンプル数が少なくても滑らか</strong>。
    - <strong>前景は別処理</strong>（[前景と背景](near-far.md)）。

## 基本の考え方

**出力画素 P の CoC が R 画素なら、P を中心に半径 R の円内の画素を、集めて平均**します。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="ギャザー">
<text x="20" y="26" class="fig-title">ギャザー：出力画素が、周りを集める</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="220" height="180" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="110" cy="90" r="64" fill="#2563eb" fill-opacity="0.12" stroke="#2563eb" stroke-width="2" stroke-dasharray="5 4"/>
<circle cx="110" cy="90" r="7" fill="#e5484d"/><text x="122" y="86" style="font-size:12px">P（出力）</text>
<g fill="#2563eb"><circle cx="70" cy="60" r="4"/><circle cx="150" cy="62" r="4"/><circle cx="90" cy="130" r="4"/><circle cx="140" cy="120" r="4"/><circle cx="60" cy="100" r="4"/><circle cx="160" cy="95" r="4"/><circle cx="110" cy="45" r="4"/><circle cx="105" cy="140" r="4"/></g>
<text x="0" y="200" style="font-size:12px">P の CoC の円の中のサンプルを集める</text>
</g>
<g font-size="13"><text x="320" y="86" style="font-weight:700">手順</text>
<text x="320" y="112">① P の CoC（半径 R）を読む</text>
<text x="320" y="136">② 半径 R の円盤状に N 個のサンプル</text>
<text x="320" y="160">③ 各サンプルの色を、重み付きで平均</text>
<text x="320" y="196" style="font-weight:700">重み：サンプルの CoC が P まで届くか</text></g>
</svg>

## ヴォーゲル螺旋でサンプルを散らす

**円盤の中に均等に近い配置**で**サンプルを置く**には、<strong>ヴォーゲル螺旋（黄金角）</strong>が**簡単**です。

```hlsl
static const float kGoldenAngle = 2.39996323;

float2 VogelDisk(int index, int count, float phi) {
  float r = sqrt((index + 0.5) / count);
  float theta = index * kGoldenAngle + phi;
  return float2(r * cos(theta), r * sin(theta));
}
```

| 点 | 説明 |
| --- | --- |
| **`sqrt((i+0.5)/N)`** | **円盤の面積が均等になる半径**（**外側ほど数が多い**） |
| **黄金角 2.4 rad** | **サンプルが重ならず、偏らず散る** |
| **`phi`** | **画素ごとにランダムに回す**（**縞をノイズに変える**） |

## ギャザーの実装

```hlsl
Texture2D<float4> color_coc : register(t0);

float4 DofGather(float2 uv, float2 texel, float phi) {
  float4 center = color_coc.SampleLevel(linear_clamp, uv, 0);
  float center_coc = abs(center.a);
  float3 sum = center.rgb;
  float weight_sum = 1.0;

  const int kSamples = 32;
  for (int i = 0; i < kSamples; ++i) {
    float2 offset = VogelDisk(i, kSamples, phi) * center_coc;
    float2 sample_uv = uv + offset * texel;
    float4 s = color_coc.SampleLevel(linear_clamp, sample_uv, 0);
    float sample_coc = abs(s.a);
    float distance_in_pixels = length(offset);
    float w = saturate(sample_coc - distance_in_pixels + 1.0);
    sum += s.rgb * w;
    weight_sum += w;
  }
  return float4(sum / weight_sum, center.a);
}
```

| 点 | 説明 |
| --- | --- |
| **`color_coc`** | **RGB に色、A に符号付き CoC**を**入れた画像** |
| **`offset = Vogel × center_coc`** | **自分の CoC の半径で、サンプル位置を決める** |
| **`w = saturate(sample_coc − 距離 + 1)`** | **サンプルの CoC が、自分までの距離以上なら、重みが大きい**（**その画素のボケが自分に届く**） |
| **中心を 1 つ足す** | **サンプルが 0 でも自分自身は残す** |

### なぜ、サンプルの CoC を見るのか

**自分の CoC だけで円内を平均する**と、**ピントが合った前景の物のすぐ後ろに、ぼけた背景があるとき**、**ピント内の物の輪郭に背景の色がにじんで**しまいます。**サンプル側の CoC を見て、そのサンプルのボケが自分まで届かないなら重みを 0 に**することで、**ピントが合った物の輪郭が保たれます**。

<!-- fig:dof-gather-weight:begin -->
<!-- fig:dof-gather-weight:end -->

## ちらつきとノイズの扱い

**サンプル数が少ない**と**円盤が点の集まりに見えて、ざらつきます**。

| 対策 | 内容 |
| --- | --- |
| <strong>サンプルの回転（ノイズ）</strong> | **画素ごとに `phi` を変え、規則的な縞を細かいノイズに** |
| **ブルー ノイズ** | **ノイズの質が良く、後のぼかしで綺麗に消える** |
| **後処理のぼかし** | **ギャザーの後に、3×3 程度の小さなぼかし** |
| **サンプル数を CoC に応じて変える** | **ボケの小さい画素は、サンプルを減らす**（**半径 1 画素以下は、元のまま**） |
| **TAA で時間的に平均** | **毎フレーム `phi` を変え、TAA で滑らかに** |

## 半解像度で処理する

**ボケは低周波**なので**半解像度で計算して、フル解像度に戻して合成**しても、**見た目はほぼ変わりません**。**コストが 1/4**になります。

| 手順 | 内容 |
| --- | --- |
| **① ダウンサンプル** | **色と CoC を半解像度に**（**CoC は重み付き平均**） |
| **② ギャザー** | **半解像度で** |
| **③ アップサンプルと合成** | **CoC に応じて、元の絵と混ぜる**（**ボケが小さい所は元の絵を残す**） |

## コスト

| 項目 | 目安 |
| --- | --- |
| **サンプル数** | **32 で 1080p・半解像度なら 約 0.3〜0.5 ms** |
| **最大 CoC** | **大きいほどサンプルの間隔が開き、ノイズ・粗さが出る** |
| **帯域** | **色 ＋ CoC の 8 バイト（FP16×4）の読み込み × サンプル数** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **サンプル側の CoC を使った重み** | **ピント内の輪郭を守る**（必須） |
| **ブルー ノイズで回転 ＋ TAA** | **少ないサンプルでも滑らか** |
| **半解像度 ＋ 合成** | **コストを 1/4** |
| **前景と背景を分ける** | **前景のにじみを正しく**（[前景と背景](near-far.md)） |
| **ボケの形に合わせた配置** | **多角形のボケ**（[ボケの形](bokeh-shape.md)） |
| **ブルームと併用** | **明るい点が大きなボケの円盤になる**（[スキャッター方式](scatter.md)の簡易版） |

## よくあるミス

??? failure "ピントが合った物の輪郭に、背景の色がにじむ"
    **サンプル側の CoC を重みに使っていない**。<strong>重みに「サンプルの CoC が自分まで届くか」</strong>を入れる。

??? failure "ボケが縞模様（同心円）になる"
    **サンプルが規則的**。<strong>画素ごとに回転（ノイズ）</strong>を入れる。

??? failure "CoC が大きい所で、サンプルが粗く、ざらざらする"
    **サンプル数を増やす**、**半解像度のぼかしを併用**、**最大 CoC を下げる**。

??? failure "前景がボケても、背景にしか効かず、輪郭がきつい"
    **前景を別に処理**し、**ぼけた前景が奥にも広がる**ようにする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ギャザー ＝ <strong>各画素が、CoC の半径で周りを集めて平均</strong>
    - [x] サンプルは<strong>ヴォーゲル螺旋 ＋ 画素ごとの回転</strong>
    - [x] <strong>サンプル側の CoC を見て重み付け</strong>（<strong>ピント内の輪郭を守る</strong>）
    - [x] <strong>半解像度</strong>で<strong>コスト 1/4</strong>
    - [x] <strong>前景は別処理</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Kleber & Hammon, "Bokeh depth of field"（解説）
- Kraus & Strengert, "Depth-of-Field Rendering by Pyramidal Image Processing"（2007）

## 関連ページ

- [被写界深度（DOF）](index.md)
- [錯乱円（CoC）](coc.md)
- [スキャッター方式](scatter.md)
- [前景と背景](near-far.md)
- [ボケの形](bokeh-shape.md)

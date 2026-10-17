---
title: 前景と背景
tags:
  - 描画
---

# 前景と背景

**DOF の難しさは、「ピントの手前（前景）」と「奥（背景）」で、ぼけ方の理屈が違う**ことです。**背景のボケはピントが合った物の「後ろ」にあるので手前の物を隠さない**ですが、**前景のボケはピントが合った物の「手前」にあるのでその物の上に広がってかぶさります**。**これを分けて処理しないと、ボケた前景の輪郭がきつくなったり、ピント内の物に背景がにじんだり**します。このページでは、**前景と背景の違い・別々に処理する方法・近傍の最大 CoC（タイル）・合成・よくある破綻**を説明します。

!!! tip "ポイント"
    - <strong>背景のボケ</strong>は<strong>ピント内の物にかぶらない</strong>。<strong>前景のボケは奥の物の上に広がる</strong>。
    - <strong>CoC を符号付き</strong>で持ち（<strong>前景は負</strong>）、<strong>前景・背景を別々に処理</strong>する。
    - <strong>前景は「周りの最大 CoC」</strong>を使う（<strong>前景の輪郭の外側にまでボケが広がる</strong>ため）。<strong>タイルで高速化</strong>。
    - <strong>前景のボケは、アルファ（透け具合）つきで最後に合成</strong>する。
    - <strong>背景はピント内の物を貫通しない</strong>ように、<strong>重みを制御</strong>。
    - <strong>半解像度</strong>でも<strong>前景と背景は分けて保存</strong>する。

## 前景と背景の違い

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="前景と背景のボケ">
<text x="20" y="26" class="fig-title">ぼけた前景は奥へ広がる、ぼけた背景は手前の物を隠さない</text>
<g transform="translate(40,56)">
<text x="0" y="-10" style="font-size:13px;font-weight:700">背景がぼける</text>
<rect x="0" y="0" width="300" height="130" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="150" cy="65" r="22" fill="#2563eb"/>
<circle cx="100" cy="40" r="26" fill="#e5484d" fill-opacity="0.45"/>
<circle cx="220" cy="90" r="30" fill="#e5aa28" fill-opacity="0.45"/>
<text x="0" y="152" style="font-size:12px">ピント内（青）は輪郭がくっきり、</text><text x="0" y="170" style="font-size:12px">ボケた背景は後ろに広がる</text>
</g>
<g transform="translate(420,56)">
<text x="0" y="-10" style="font-size:13px;font-weight:700">前景がぼける</text>
<rect x="0" y="0" width="300" height="130" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="150" cy="65" r="22" fill="#2563eb"/>
<circle cx="130" cy="60" r="52" fill="#e5484d" fill-opacity="0.3"/>
<text x="0" y="152" style="font-size:12px">ぼけた前景は、ピント内の物の上に</text><text x="0" y="170" style="font-size:12px">かぶさって広がる（透けて見える）</text>
</g>
</svg>

| 項目 | 背景 | 前景 |
| --- | --- | --- |
| **ボケの広がる向き** | **奥の物の周り** | **手前の物の輪郭の外へ奥にかぶさる** |
| **ピント内の物との関係** | **ピント内の物は、手前にあるので隠れない** | **ピント内の物の上に広がる** |
| **ボケた縁** | **ピント内の物の縁できっぱり切れる** | **縁がやわらかく、透ける** |

## 別々に処理する

**CoC の符号**で**前景と背景に分け**、**別々にぼかし、最後に合成**します。

| 手順 | 内容 |
| --- | --- |
| **① 前景と背景に分ける** | **CoC < 0 を前景、CoC > 0 を背景**（**ピント内（|CoC| が小さい）は、そのまま**） |
| **② 背景をぼかす** | **ピント内の物の色が混ざらないよう、重みを制御** |
| **③ 前景をぼかす** | **近傍の最大 CoC を使い、前景の外にも広げる。アルファ付き** |
| **④ 合成** | **背景 → ピント内 → 前景（アルファで上に）の順** |

```hlsl
float3 CompositeDof(float3 sharp, float4 far_blur, float4 near_blur, float coc) {
  float far_alpha = saturate(coc);
  float3 color = lerp(sharp, far_blur.rgb, far_alpha);
  color = lerp(color, near_blur.rgb, near_blur.a);
  return color;
}
```

| 点 | 説明 |
| --- | --- |
| **`far_alpha = saturate(coc)`** | **背景のボケは、CoC が大きいほど強く混ぜる** |
| **`near_blur.a`** | <strong>前景のぼけた「濃さ」</strong>（**ぼけた輪郭の外側は、薄く透ける**） |
| **最後に前景を重ねる** | **前景は最も手前にある** |

## 背景のぼかし：ピント内の物を貫通させない

**背景をぼかすとき**、**ピント内の物（手前にある）の色を背景のボケに混ぜてはいけません**（**ピント内の物がぼけて見えてしまう**）。

```hlsl
float BackgroundWeight(float sample_coc, float distance_in_pixels) {
  float reach = saturate(sample_coc - distance_in_pixels + 1.0);
  float is_far = saturate(sample_coc);
  return reach * is_far;
}
```

| 点 | 説明 |
| --- | --- |
| **`is_far`** | **サンプルが背景（CoC > 0）なら有効**。**前景・ピント内は、0** |
| **`reach`** | **そのサンプルのボケが自分まで届くか** |

## 前景のぼかし：近傍の最大 CoC

**前景のボケは前景の輪郭の「外側」にまで広がります**。**その位置の画素自体の CoC は 0（ピント内か背景）でも近くに前景の画素があれば、その CoC の分だけボケが届く**ので、**周りの画素の最大 CoC**を**使います**。

<!-- fig:dof-near-field:begin -->
<!-- fig:dof-near-field:end -->

### 近傍の最大 CoC（タイル）

**画面をたとえば 16×16 のタイルに分け**、**各タイルの前景の最大 CoC（最も負に大きい値）を求め**、**それを周りのタイルへ広げます**（**ダイレーション**）。

```hlsl
[numthreads(16, 16, 1)]
void TileMaxCoc(uint3 id : SV_DispatchThreadID, uint3 group_id : SV_GroupID, uint group_index : SV_GroupIndex) {
  float coc = color_coc.Load(int3(id.xy, 0)).a;
  s_min_coc[group_index] = coc;
  GroupMemoryBarrierWithGroupSync();
  for (uint stride = 128; stride > 0; stride >>= 1) {
    if (group_index < stride) s_min_coc[group_index] = min(s_min_coc[group_index], s_min_coc[group_index + stride]);
    GroupMemoryBarrierWithGroupSync();
  }
  if (group_index == 0) tile_max_near[group_id.xy] = s_min_coc[0];
}
```

| 点 | 説明 |
| --- | --- |
| **`min`** | **前景は負の値なので最小値 ＝ 最も大きな前景の CoC** |
| **共有メモリでの縮約** | **グループ内の最小値**を求める |
| **周りのタイルへ広げる** | **隣接 3×3 のタイルの最小値**を、<strong>そのタイルの「近傍の最大 CoC」</strong>に |

**タイルの最大 CoC が 0 のタイル**（**前景がまったくない**）は、**前景のぼかしを丸ごとスキップ**でき、**高速化**になります。

## 合成の順序

| 順序 | 内容 |
| --- | --- |
| **① 背景** | **背景のぼけをピント内の画像に混ぜる** |
| **② ピント内** | **そのまま** |
| **③ 前景** | **ぼけた前景をアルファで上に重ねる** |

**半解像度**で**前景・背景を処理**する場合、**前景と背景を別の画像として保存**し、**最後にフル解像度の画像へ合成**します。

## よくある破綻と対処

| 破綻 | 原因 | 対処 |
| --- | --- | --- |
| **ピント内の物の縁に背景のボケがにじむ** | **背景のぼかしで前景・ピント内を混ぜた** | **サンプルの CoC 符号で除外** |
| **ぼけた前景の輪郭がきつい** | **前景を自分の CoC だけで処理** | **近傍の最大 CoC・アルファ合成** |
| <strong>前景と背景の境にハロ（白い縁）</strong> | **混ざり方の誤り** | **符号付きの重み・別画像で合成** |
| **ピント内の物の背後にぼけた物が突き抜けて見える** | **深度の考慮漏れ** | **背景の重みに深度の順序を反映** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **前景・背景を別バッファに** | **混ざりを防ぐ** |
| **タイルの最大 CoC** | **前景のぼかしを必要な所だけ** |
| **前景はアルファ付きで合成** | **透けるボケ** |
| **ピント内はできるだけ元の絵のまま** | **くっきりを保つ** |
| **背景の「裏側」の補完** | **前景の下に隠れた背景が見えるよう、周囲の色で補う**（高度） |

## よくあるミス

??? failure "前景のボケが、奥にしかかからず、手前の物の輪郭が切れている"
    **近傍の最大 CoC**で**前景の外へも広げる**。

??? failure "ピント内の物の周りに、背景のボケが白く縁取る"
    **背景のぼかしで前景・ピント内のサンプルを除外**。

??? failure "前景も背景も、1 枚でぼかして、境が破綻する"
    **符号で分け、別々にぼかして、合成**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>背景のボケは、ピント内の物を隠さない</strong>。<strong>前景のボケは奥にかぶさる</strong>
    - [x] <strong>CoC を符号付きで持ち、前景・背景を別々に処理</strong>
    - [x] <strong>前景は、近傍の最大 CoC（タイル）</strong>で<strong>外側へ広げる</strong>
    - [x] <strong>背景のぼかしで、ピント内・前景のサンプルを除外</strong>
    - [x] <strong>合成は、背景 → ピント内 → 前景（アルファ）</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）

## 関連ページ

- [被写界深度（DOF）](index.md)
- [錯乱円（CoC）](coc.md)
- [ギャザー方式](gather.md)
- [スキャッター方式](scatter.md)

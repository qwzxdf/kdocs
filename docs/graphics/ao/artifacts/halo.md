---
title: ハロー
tags:
  - 描画
---

# ハロー

**ハロー**は、**物体の輪郭の周りに、明るい（または暗い）縁が出る**現象です。**手前の物体と奥の面で、深度が大きく違う所**で、**サンプルが、手前の物体を遮蔽物と誤認する**と、**奥の面が暗くなる（または、逆に明るくなる）**ためです。このページでは、**ハローの原因・距離による減衰（範囲チェック）・対策**を説明します。

!!! tip "ポイント"
    - **ハロー ＝ 輪郭の周りの、明るい・暗い縁**。
    - **原因 ＝ 大きく離れた物を、遮蔽物として扱う**。
    - **対策 ＝ 範囲チェック**：**サンプルと中心の深度差が、半径より大きければ、遮蔽に数えない**。
    - **滑らかな範囲チェック（`smoothstep`）**で**境を柔らかく**。

## ハロー
### 症状

**手前にある物体の輪郭の周り**（背景側）に、**暗い光の輪**が出ます。人物の頭の周りの壁が**暗く縁取られる**ような見た目です。

### 原因

**手前の物体**（人物）と、**奥の背景**（壁）の**深度差が大きい**境界で、**背景の画素の周りのサンプル**が、**手前の物体の内側**に入ります。**深度バッファでは、人物は面として存在する**ので、**背景の点が人物に遮られている**と判定されます。しかし、実際には**人物は壁から離れて立っている**ので、**壁を暗くする理由はありません**。

<svg class="fig illust" viewBox="0 0 760 260" role="img" aria-label="ハローの原因">
<text x="20" y="24" class="fig-title">深度の差が大きいと、奥の壁が、手前の人物に「遮られている」と誤判定される</text>
<line x1="60" y1="220" x2="700" y2="220" stroke="currentColor" stroke-width="3"/>
<text x="60" y="244" style="font-size:12px">奥の壁（面）</text>
<rect x="320" y="80" width="40" height="140" fill="rgba(76,139,245,0.3)" stroke="currentColor" stroke-width="2" transform="translate(0,-30)"/>
<text x="300" y="42" style="font-size:12px">手前の人物</text>
<circle cx="260" cy="220" r="7" fill="currentColor"/><text x="250" y="206" style="font-size:12px">p</text>
<circle cx="260" cy="220" r="70" fill="none" stroke="currentColor" stroke-dasharray="5 4"/>
<g fill="#e5484d"><circle cx="310" cy="190" r="5"/><circle cx="320" cy="150" r="5"/></g>
<text x="410" y="110" style="font-weight:700">赤いサンプルが「人物の中」に入る</text>
<text x="410" y="134" style="font-size:12px">→ 壁の p が、人物に遮られていると判定される</text>
<text x="410" y="164" style="font-size:12px">実際には、人物は壁から離れているので、遮蔽は起きない</text>
</svg>

### 対策

| 対策 | 内容 |
| --- | --- |
| **範囲チェック** | **p と遮蔽物の深度差が半径 R より大きい**なら、寄与を**弱める**（[半球 SSAO](../ssao-hemisphere.md)） |
| **式に距離の減衰を入れる** | Alchemy・HBAO の距離の弱め |
| **バイラテラル ブラー** | ぼかしで境界をまたがない |
| **厚みのヒューリスティック** | 手前の物体の厚みを「有限」と仮定して、**奥側は遮蔽しない**（GTAO など） |
| **半径を小さく** | 半径が大きいほど、ハローは広がる |
| <strong>（高コスト）二層の深度</strong> | 手前の面の**裏側**の深度も持つ |

## よくあるミス

??? failure "輪郭に、黒いハローが出る"
    **範囲チェック（深度差が半径内のときだけ、遮蔽に数える）**を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **離れた物を遮蔽と誤認するのが原因**
    - [x] **範囲チェックで防ぐ**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [AO のアーティファクト](index.md)
- [自己遮蔽](self-occlusion.md)
- [半球 SSAO](../ssao-hemisphere.md)

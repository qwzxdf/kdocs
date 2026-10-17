---
title: SSR Basics
tags:
  - 描画
---

# SSR Basics

**SSR（スクリーン スペース リフレクション）は、すでに描いた画面の画像（色と深度）だけを使って、反射を作る手法**です。**反射レイを画面の上でたどり、当たった画素の色を持ってくる**という、**とても単純な発想**ですが、**細かい所で、つまずきやすい**です。このセクションでは、**発想・レイの進め方・厚み・色の取得とフェード・コストと粗さ・アーティファクト**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **SSR ＝ 画面の色と深度だけで反射を作る**（追加のシーン描画が不要）。
    - **画面に映っていない物は、反射に映らない**（これが最大の弱点）。
    - **レイを画面上で少しずつ進め、深度と比べて、当たりを探す**。
    - **当たらなかった所は、フォールバック（プローブなど）で埋める**。

## 発想
[Reflections](../index.md)で見たとおり、鏡面反射は「**反射方向 R に何が見えるか**」です。SSR は、**R の方向にレイを飛ばして**、**画面の深度バッファを「簡易なシーン」とみなして**、**レイが当たる所**を探します。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="SSR のレイ進行">
<text x="20" y="24" class="fig-title">反射方向のレイを、画面の深度バッファの上で進める。面の奥に入った所が「当たり」</text>
<polygon points="60,230 300,230 300,150 420,150 420,230 720,230 720,270 60,270" fill="rgba(150,150,150,0.3)" stroke="currentColor" stroke-width="2"/>
<text x="330" y="140" style="font-size:12px">壁（深度バッファに映る面）</text>
<circle cx="150" cy="230" r="7" fill="currentColor"/><text x="130" y="254" style="font-size:12px">p（反射する点）</text>
<line x1="150" y1="230" x2="395" y2="120" stroke="#e5484d" stroke-width="3"/>
<g fill="#e5484d"><circle cx="190" cy="212" r="4"/><circle cx="230" cy="194" r="4"/><circle cx="270" cy="176" r="4"/><circle cx="310" cy="158" r="4"/><circle cx="350" cy="140" r="4"/></g>
<circle cx="372" cy="152" r="7" fill="none" stroke="#2ea043" stroke-width="3"/><text x="380" y="190" style="font-size:12px;fill:#2ea043;font-weight:700">当たり（レイ ＞ 面の深度）</text>
<text x="20" y="288" style="font-size:12px">各ステップで、レイの奥行きと、その画素の深度を比べる。レイが面の奥へ潜ったところが交点</text>
</svg>

## 手順
| 手順 | 内容 |
| --- | --- |
| **① 反射方向を求める** | 法線と視線から `R = reflect(視線, 法線)`（ビュー空間） |
| **② レイを作る** | 始点 P（その画素の位置）、方向 R |
| **③ レイを進める** | 画面空間で、**1 ステップずつ**進む |
| **④ 各ステップで当たり判定** | レイの奥行きとその画素の深度を比べる |
| **⑤ 当たった画素の色を取る** | 反射として使う |
| **⑥ 端・粗さ・向きでフェード** | 信頼できない反射を弱める |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Linear Marching](linear-march.md) | レイを進める・歩幅・当たりの精密化 |
| [厚み](thickness.md) | 「裏側へ抜けた」を当たりにしない工夫 |
| [Color Lookup and Fading](color-fade.md) | 当たりの色・信頼度で反射を弱める |
| [Cost and Roughness](cost-roughness.md) | 解像度・簡易のぼかし |
| [Artifacts and Evaluation](artifacts.md) | SSR の問題点・長所と短所 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **SSR は、画面の中だけの反射**
    - [x] **レイを深度と比べて、当たりを探す**
    - [x] **外れた所は、フォールバックで補う**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflections](../index.md)
- [階層 Z（Hi-Z）](../ssr-hiz.md)
- [Stochastic SSR](../ssr-stochastic.md)
- [フォールバック](../ssr-fallback.md)

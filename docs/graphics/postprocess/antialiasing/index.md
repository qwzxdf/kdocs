---
title: アンチエイリアシング
tags:
  - 描画
---

# アンチエイリアシング

**ピクセルは四角い格子**なので、**斜めの線や細い物の縁が、階段状（ジャギー）に見えます**。これが**エイリアシング**で、<strong>アンチエイリアシング（AA）</strong>は、**これを滑らかにする技術**です。**方式が多く、画質・速さ・弱点がそれぞれ違います**。このセクションでは、**エイリアシングの原因・SSAA/MSAA・FXAA・SMAA・TAA・TAA の課題・比較と選び方**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - エイリアシング ＝ <strong>連続した絵を、画素の格子で標本化するときの、ずれ</strong>（<strong>ジャギー・ちらつき・モアレ</strong>）。
    - <strong>根本の対策</strong>は<strong>1 画素あたりのサンプルを増やす</strong>（<strong>SSAA / MSAA</strong>）。
    - <strong>画像後処理</strong>の方式（<strong>FXAA・SMAA</strong>）は<strong>安いが細部をぼかし、時間的なちらつきは残る</strong>。
    - <strong>TAA</strong>は<strong>フレームごとにサンプル位置をずらして、時間方向に蓄積</strong>。<strong>ほぼ全種類のエイリアシングに効く</strong>が、<strong>ゴーストとぼけ</strong>が出る。
    - <strong>現代の主流は TAA 系</strong>（<strong>TAAU・DLSS・FSR・TSR</strong>）。
    - <strong>方式は組み合わせられる</strong>（<strong>MSAA ＋ 後処理、TAA ＋ シャープ</strong>）。

## エイリアシングの 3 つの種類

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="エイリアシングの種類">
<text x="20" y="26" class="fig-title">エイリアシングは、見え方で 3 種類</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">① ジャギー（縁）</text>
<g fill="#334155"><rect x="0" y="100" width="20" height="20"/><rect x="20" y="80" width="20" height="20"/><rect x="40" y="60" width="20" height="20"/><rect x="60" y="40" width="20" height="20"/><rect x="80" y="20" width="20" height="20"/></g>
<text x="0" y="146" style="font-size:12px">斜めの縁が階段状</text>
</g>
<g transform="translate(300,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">② 細い物の途切れ</text>
<g fill="#334155"><rect x="0" y="40" width="20" height="4"/><rect x="40" y="40" width="20" height="4"/><rect x="80" y="40" width="20" height="4"/><rect x="20" y="70" width="20" height="4"/><rect x="60" y="70" width="20" height="4"/></g>
<text x="0" y="146" style="font-size:12px">電線・フェンスが途切れる</text>
</g>
<g transform="translate(560,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">③ ちらつき・モアレ</text>
<g stroke="#334155" stroke-width="2"><line x1="0" y1="10" x2="140" y2="10"/><line x1="0" y1="26" x2="140" y2="30"/><line x1="0" y1="42" x2="140" y2="52"/><line x1="0" y1="58" x2="140" y2="74"/><line x1="0" y1="74" x2="140" y2="96"/></g>
<text x="0" y="146" style="font-size:12px">縞模様が動くとチラつく</text>
</g>
</svg>

| 種類 | 原因 | 効く方式 |
| --- | --- | --- |
| **ジオメトリの縁のジャギー** | **三角形の縁を画素の中心で判定するから** | **MSAA・FXAA・SMAA・TAA** |
| **シェーダー内のエイリアシング** | **スペキュラ・法線マップなど、1 画素内で急変する値** | **TAA・SSAA**（MSAA は効かない） |
| **時間的なちらつき** | **動くとき、サンプルの位置が変わり、出たり消えたりする** | **TAA** |

## 動きで見る：TAA のジッター

<!-- fig:taa-jitter:begin -->
<!-- fig:taa-jitter:end -->

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [MSAA](msaa.md) | SSAA との違い・サンプル パターン・リゾルブ・弱点 |
| [FXAA](fxaa.md) | 輝度から縁を見つけてぼかす・1 パスの後処理 |
| [SMAA](smaa.md) | 縁検出・パターン判定・重みの計算・ブレンド |
| [TAA](taa.md) | ジッター・再投影・履歴のクランプ・合成 |
| [TAA の課題](taa-challenges.md) | ゴースト・ぼけ・ちらつき・アップスケール |
| [比較と選び方](comparison.md) | 方式の比較表・組み合わせ・目的別の選び方 |

## 関連ページ

- [ポストプロセス](../index.md)
- [モーション ブラー](../motion-blur/index.md)
- [TAA とアップスケール（最適化）](../../../rendering/taa-upscaling.md)
- [ラスタライズ](../../../3d/render-flow/rasterize.md)

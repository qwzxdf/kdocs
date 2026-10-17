---
title: 描画のしくみ
tags:
  - 最適化
  - 3Dゲーム
---

# 描画のしくみ

ゲームの 1 フレームは、**CPU が「何を描くか」の命令を作り、GPU がそれを実際に描く**という、2 人のやり取りで成り立っています。どちらかが遅いとフレーム全体が遅くなります。たとえば、CPU が 5 ms で命令を作っても、GPU が描くのに 20 ms かかるなら、フレームは 20 ms です。このページでは、最適化の前提になる、描画の流れと用語を説明します。

!!! tip "ポイント"
    - フレーム時間は<strong>CPU と GPU の遅いほう</strong>で決まる。
    - 流れは<strong>命令の作成 → 頂点 → ラスタライズ → ピクセル → 書き込み</strong>。
    - まず<strong>どちらが遅いか</strong>を見分ける。詳しくは[何が重いのか](bottlenecks.md)。

## 描画の流れ

<svg class="fig flow" viewBox="0 0 1309 196" role="img" aria-label="CPU が描画命令を作り、GPU が処理する"><defs><marker id="fl12852" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">CPU が描画命令を作り、GPU が処理する</text><line x1="150.0" y1="87.0" x2="150.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="275.0" y1="148.0" x2="333.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><text x="304.0" y="142.0" text-anchor="middle" style="font-size:12px">送る</text><line x1="494.0" y1="148.0" x2="552.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="802.0" y1="148.0" x2="860.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="1096.0" y1="148.0" x2="1154.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><rect x="79.5" y="44.0" width="141" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="150.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">CPU ゲームの更新</text><circle cx="81.5" cy="46.0" r="10" fill="#4c8bf5"/><text x="81.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="28.0" y="128.0" width="244" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="150.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">描画命令を作る （ドローコール）</text><circle cx="30.0" cy="130.0" r="10" fill="#2ea043"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="336.0" y="128.0" width="155" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="413.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">GPU 頂点シェーダー</text><circle cx="338.0" cy="130.0" r="10" fill="#e5a828"/><text x="338.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="555.0" y="128.0" width="244" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="677.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ラスタライズ （ピクセルに分解）</text><circle cx="557.0" cy="130.0" r="10" fill="#e5484d"/><text x="557.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="863.0" y="128.0" width="230" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="978.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ピクセルシェーダー （色付け）</text><circle cx="865.0" cy="130.0" r="10" fill="#9664e6"/><text x="865.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="1157.0" y="128.0" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="1219.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">画面に書き込む</text><circle cx="1159.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="1159.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">6</text></svg>

| 用語 | 意味 |
| --- | --- |
| **ドロー コール** | 「この形をこの設定で描いて」という、GPU への 1 回の描画命令 |
| **頂点シェーダー** | 頂点（三角形の角）の位置を計算するプログラム |
| **ピクセル シェーダー** | 画面の 1 点（ピクセル）の色を計算するプログラム |
| **オーバードロー** | 同じピクセルに何度も描くこと（手前に隠れて見えないものまで描く） |
| **フィルレート** | 1 秒に描けるピクセル数。GPU の限界の 1 つ |
| **メモリ帯域** | GPU がテクスチャなどを読み書きできる速さ |

## CPU と GPU、どちらが遅いか

| 症状 | 原因の候補 | 確かめ方 |
| --- | --- | --- |
| **解像度を下げると速くなる** | **GPU 側**（ピクセルが多い。フィルレート、シェーダーが重い） | 解像度を半分にして、フレーム時間を比べる |
| **解像度を下げても変わらない** | **CPU 側**（ドロー コール、ゲームの更新） | 同上 |
| **オブジェクトの数を減らすと、速くなる** | CPU 側（ドロー コール）か、GPU 側（頂点数） | |
| **GPU プロファイラーで、GPU が 100% 近い** | GPU 側 | RenderDoc、PIX、NVIDIA Nsight |
| **CPU プロファイラーで、描画の関数が上位** | CPU 側 | Visual Studio のプロファイラー |

## 関連ページ

- [描画の流れ（入門）：図で最初から追う](../3d/render-flow/index.md)
- [描画最適化](index.md)
- [何が重いのか](bottlenecks.md)
- [計測（プロファイリング）](../optimize/measure.md)
- [フレーム時間の設計](../optimize/frame-budget.md)


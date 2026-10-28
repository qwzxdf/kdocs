---
title: 描画の流れ（入門）
tags:
  - 3Dゲーム
  - 描画
---

# 描画の流れ（入門）

**3D のモデルがどうやって画面の色のついた点（ピクセル）になるのか**を最初から最後まで順番に追うシリーズです。ゲームの画面は 1 秒に 60 回、このしくみを通って作られています。どこで何が起きているかが分かると、シェーダー・最適化・不具合の原因探しが全部やりやすくなります。数式は最小限にして、図を中心に説明します。

## 全体像：工場の流れ作業

**描画は工場のライン**に似ています。材料（頂点）が流れてきて、工程ごとに加工され、最後に製品（ピクセルの色）になって、画面に並べられます。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="描画パイプラインの全体像">
<text x="20" y="24" class="fig-title">描画パイプライン：頂点がピクセルの色になるまで</text>
<defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<rect x="20" y="60" width="110" height="80" rx="8" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/>
<text x="75" y="92" text-anchor="middle" style="font-size:13px;font-weight:700">① 入力</text>
<text x="75" y="112" text-anchor="middle" style="font-size:11px">頂点・インデックス</text>
<text x="75" y="128" text-anchor="middle" style="font-size:11px">の束</text>
<rect x="160" y="60" width="110" height="80" rx="8" fill="#e5aa28" fill-opacity="0.25" stroke="#e5aa28" stroke-width="2"/>
<text x="215" y="92" text-anchor="middle" style="font-size:13px;font-weight:700">② 頂点</text>
<text x="215" y="112" text-anchor="middle" style="font-size:11px">シェーダー</text>
<text x="215" y="128" text-anchor="middle" style="font-size:11px">（位置を変換）</text>
<rect x="300" y="60" width="110" height="80" rx="8" fill="#8a8a8a" fill-opacity="0.2" stroke="#8a8a8a" stroke-width="2"/>
<text x="355" y="92" text-anchor="middle" style="font-size:13px;font-weight:700">③ 三角形</text>
<text x="355" y="112" text-anchor="middle" style="font-size:11px">の組み立て</text>
<text x="355" y="128" text-anchor="middle" style="font-size:11px">クリップ</text>
<rect x="440" y="60" width="110" height="80" rx="8" fill="#e5484d" fill-opacity="0.2" stroke="#e5484d" stroke-width="2"/>
<text x="495" y="92" text-anchor="middle" style="font-size:13px;font-weight:700">④ ラスタ</text>
<text x="495" y="112" text-anchor="middle" style="font-size:11px">ライズ</text>
<text x="495" y="128" text-anchor="middle" style="font-size:11px">（ピクセル化）</text>
<rect x="580" y="60" width="110" height="80" rx="8" fill="#9664e6" fill-opacity="0.22" stroke="#9664e6" stroke-width="2"/>
<text x="635" y="92" text-anchor="middle" style="font-size:13px;font-weight:700">⑤ ピクセル</text>
<text x="635" y="112" text-anchor="middle" style="font-size:11px">シェーダー</text>
<text x="635" y="128" text-anchor="middle" style="font-size:11px">（色を決める）</text>
<rect x="580" y="180" width="110" height="80" rx="8" fill="#2ea043" fill-opacity="0.22" stroke="#2ea043" stroke-width="2"/>
<text x="635" y="212" text-anchor="middle" style="font-size:13px;font-weight:700">⑥ 出力</text>
<text x="635" y="232" text-anchor="middle" style="font-size:11px">深度テスト</text>
<text x="635" y="248" text-anchor="middle" style="font-size:11px">ブレンド</text>
<rect x="300" y="180" width="110" height="80" rx="8" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/>
<text x="355" y="212" text-anchor="middle" style="font-size:13px;font-weight:700">⑦ 画面</text>
<text x="355" y="232" text-anchor="middle" style="font-size:11px">Present</text>
<line x1="130" y1="100" x2="158" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="270" y1="100" x2="298" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="410" y1="100" x2="438" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="550" y1="100" x2="578" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="635" y1="140" x2="635" y2="178" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="580" y1="220" x2="412" y2="220" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<text x="20" y="168" style="font-size:12px;fill:#e5aa28">黄・紫 ＝ 自分でシェーダーを書く</text>
<text x="20" y="188" style="font-size:12px;fill:#e5484d">赤・灰・緑 ＝ GPU が自動でやる（設定だけする）</text>
</svg>

| 番号 | 工程 | 誰がやる | 何をする | ページ |
| --- | --- | --- | --- | --- |
| ① | 入力 | CPU が準備 | 頂点の束と描き方の設定を GPU に渡す | [CPU から GPU へ](cpu-to-gpu.md) |
| ② | 頂点シェーダー | 自分で書く | 頂点の位置を画面に向けて変換する | [頂点の工程](vertex-stage.md) |
| ③ | 組み立て・クリップ | GPU | 頂点を三角形にまとめ、画面の外を切り落とす | [クリップと画面への写し](clip-viewport.md) |
| ④ | ラスタライズ | GPU | 三角形が覆うピクセルを見つける | [ラスタライズ](rasterize.md) |
| ⑤ | ピクセル シェーダー | 自分で書く | ピクセルごとに色を計算する | [ピクセルの色](pixel-shader.md) |
| ⑥ | 出力 | GPU（設定する） | 隠れていないか調べ、画面に混ぜ書きする | [深度・ブレンド](output-merger.md) |
| ⑦ | 表示 | GPU／OS | 完成した絵を画面に出す | [画面に出す](present.md) |

## 1 つの三角形で追ってみる

**最小の例**で流れを実感します。画面に色のついた三角形を 1 つ描く場合です。

<svg class="fig illust" viewBox="0 0 780 360" role="img" aria-label="1 つの三角形の旅"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">三角形 1 つの旅：3 つの頂点 → 覆うピクセルの色</text>
<g transform="translate(20,50)">
<text x="0" y="0" style="font-size:12px;font-weight:700">① 入力：3 頂点</text>
<polygon points="20,100 130,70 70,20" fill="none" stroke="#4c8bf5" stroke-width="2"/>
<circle cx="20" cy="100" r="5" fill="#e5484d"/><circle cx="130" cy="70" r="5" fill="#2ea043"/><circle cx="70" cy="20" r="5" fill="#4c8bf5"/>
<text x="0" y="130" style="font-size:11px">ローカル座標の</text><text x="0" y="146" style="font-size:11px">3 つの点（と色）</text>
</g>
<g transform="translate(200,50)">
<text x="0" y="0" style="font-size:12px;font-weight:700">② 変換後</text>
<rect x="0" y="12" width="140" height="100" fill="none" stroke="currentColor" stroke-opacity="0.5" stroke-dasharray="4 3"/>
<polygon points="20,98 120,78 62,28" fill="none" stroke="#4c8bf5" stroke-width="2"/>
<text x="0" y="130" style="font-size:11px">カメラから見た</text><text x="0" y="146" style="font-size:11px">画面の中の位置</text>
</g>
<g transform="translate(400,50)">
<text x="0" y="0" style="font-size:12px;font-weight:700">③④ ピクセル化</text>
<g stroke="currentColor" stroke-opacity="0.25" fill="none"><rect x="0" y="12" width="140" height="100"/></g>
<g fill="#4c8bf5" fill-opacity="0.6">
<rect x="50" y="32" width="10" height="10"/><rect x="45" y="42" width="20" height="10"/><rect x="40" y="52" width="30" height="10"/><rect x="35" y="62" width="50" height="10"/><rect x="25" y="72" width="80" height="10"/><rect x="20" y="82" width="100" height="10"/>
</g>
<text x="0" y="130" style="font-size:11px">覆うピクセルを</text><text x="0" y="146" style="font-size:11px">全部見つける</text>
</g>
<g transform="translate(580,50)">
<text x="0" y="0" style="font-size:12px;font-weight:700">⑤⑥ 色付け</text>
<defs><linearGradient id="rfg" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#e5484d"/><stop offset="0.5" stop-color="#2ea043"/><stop offset="1" stop-color="#4c8bf5"/></linearGradient></defs>
<polygon points="20,92 120,92 62,32" fill="url(#rfg)" opacity="0.85"/>
<text x="0" y="130" style="font-size:11px">ピクセルごとに</text><text x="0" y="146" style="font-size:11px">色を計算して書く</text>
</g>
<line x1="170" y1="110" x2="198" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="350" y1="110" x2="398" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<line x1="540" y1="110" x2="578" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#rfa)"/>
<text x="20" y="270" style="font-size:13px">・頂点シェーダーは<tspan font-weight="700">3 回</tspan>（頂点の数だけ）呼ばれる</text>
<text x="20" y="294" style="font-size:13px">・ピクセル シェーダーは<tspan font-weight="700">三角形が覆うピクセルの数だけ</tspan>呼ばれる（画面が広いほど増える）</text>
<text x="20" y="318" style="font-size:13px">・頂点ごとの色（赤・緑・青）は、ピクセルの位置に応じて<tspan font-weight="700">自動でなめらかに混ぜられる</tspan></text>
</svg>

ポイントは呼ばれる回数の違いです。頂点シェーダーは頂点の数、ピクセル シェーダーは覆うピクセルの数だけ呼ばれます。画面が大きいほど、ピクセル側が圧倒的に多くなります。最適化で「ピクセル シェーダーを軽くする」ことが重視される理由です。

## このシリーズの読み方

| 目的 | 読む順 |
| --- | --- |
| **とにかく全体を知りたい** | このページ → [1 フレームの中身](frame-passes.md) |
| 順番に理解したい | 上の表の順（①〜⑦） |
| シェーダーを書きたい | [頂点の工程](vertex-stage.md) → [ピクセルの色](pixel-shader.md) |
| 重い原因を探したい | [ラスタライズ](rasterize.md) → [深度・ブレンド](output-merger.md) → [描画最適化](../../rendering/index.md) |

## 用語

| 用語 | 意味 |
| --- | --- |
| <strong>頂点（Vertex）</strong> | 三角形の角の点。位置・色・法線・UV などを持つ |
| プリミティブ | 描画の最小単位の形。ふつうは三角形 |
| シェーダー | GPU で動く小さなプログラム |
| パイプライン | 工程の連なり（流れ作業） |
| ピクセル（フラグメント） | 画面の 1 点。ここでは画面の点とそこに書く候補の色をまとめて呼ぶ |
| ドロー コール | 「これを描いて」という 1 回の命令 |
| フレーム | 1 枚の絵。60 FPS なら 1 秒に 60 枚 |

## 関連ページ

- [3D ゲーム](../index.md)
- [モデルの基本](../model-basics.md)
- [座標変換（MVP）](../transforms-mvp.md)
- [描画のしくみ（最適化の入口）](../../rendering/pipeline.md)
- [シェーダー](../../graphics/index.md)

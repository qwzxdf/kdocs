---
title: Dual Filter
tags:
  - 描画
---

# Dual Filter

<strong>Dual Filter（Kawase の Dual Filtering）</strong>は、**縮小とぼかしを同時に行い、拡大とぼかしも同時に行う**方式です。**ガウスぼかしを別パスで行う必要がなくなり**、**ブルームのコストを大きく下げられます**。**モバイルのように帯域が厳しい環境**でも**定番**です。このページでは、**考え方・ダウンサンプル用とアップサンプル用のカーネル・実装・実質のぼかしの広がり・ガウスとの比較・注意点**を説明します。

!!! tip "ポイント"
    - Dual Filter ＝ <strong>縮小のときに周りも平均し（ぼかし）、拡大のときも周りを足す（ぼかし）</strong>。<strong>ぼかしだけの専用パスが要らない</strong>。
    - <strong>ダウンサンプル</strong>は<strong>5 タップ</strong>（中心 + 4 つの斜め）、<strong>アップサンプル</strong>は<strong>8 タップ</strong>（辺と斜め）。
    - 各タップは<strong>バイリニア</strong>で読むので、<strong>実質より多くの画素</strong>が混ざる。
    - <strong>広さは段数に比例して指数的に増える</strong>。
    - <strong>ガウスよりやや四角い形</strong>になるが、<strong>多段にすると見分けにくい</strong>。
    - <strong>オフセット（広がり）</strong>を<strong>パラメータ</strong>にして、<strong>ぼかしの強さを調整</strong>できる。

## 考え方

**従来**は、「縮小」と「ぼかし」を**別々のパス**で行いました。**Dual Filter は、縮小するときの「サンプルの取り方」自体をぼかしの形に**します。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="Dual Filter のカーネル">
<text x="20" y="26" class="fig-title">Dual Filter のカーネル（ダウン：5 タップ、アップ：8 タップ）</text>
<g transform="translate(60,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">ダウンサンプル（5 タップ）</text>
<rect x="0" y="0" width="200" height="150" fill="none" stroke="#94a3b8"/>
<g stroke="#e2e8f0"><line x1="50" y1="0" x2="50" y2="150"/><line x1="100" y1="0" x2="100" y2="150"/><line x1="150" y1="0" x2="150" y2="150"/><line x1="0" y1="37" x2="200" y2="37"/><line x1="0" y1="75" x2="200" y2="75"/><line x1="0" y1="112" x2="200" y2="112"/></g>
<circle cx="100" cy="75" r="9" fill="#2563eb"/><text x="116" y="70" style="font-size:12px">×4</text>
<circle cx="50" cy="37" r="7" fill="#e5484d"/><circle cx="150" cy="37" r="7" fill="#e5484d"/><circle cx="50" cy="112" r="7" fill="#e5484d"/><circle cx="150" cy="112" r="7" fill="#e5484d"/>
<text x="0" y="176" style="font-size:12px">中心 ×4 + 斜め 4 点 ×1（合計 ÷8）</text>
</g>
<g transform="translate(420,60)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">アップサンプル（8 タップ）</text>
<rect x="0" y="0" width="200" height="150" fill="none" stroke="#94a3b8"/>
<g stroke="#e2e8f0"><line x1="50" y1="0" x2="50" y2="150"/><line x1="100" y1="0" x2="100" y2="150"/><line x1="150" y1="0" x2="150" y2="150"/><line x1="0" y1="37" x2="200" y2="37"/><line x1="0" y1="75" x2="200" y2="75"/><line x1="0" y1="112" x2="200" y2="112"/></g>
<circle cx="100" cy="20" r="7" fill="#2563eb"/><circle cx="100" cy="130" r="7" fill="#2563eb"/><circle cx="25" cy="75" r="7" fill="#2563eb"/><circle cx="175" cy="75" r="7" fill="#2563eb"/>
<circle cx="63" cy="37" r="7" fill="#e5484d"/><circle cx="137" cy="37" r="7" fill="#e5484d"/><circle cx="63" cy="112" r="7" fill="#e5484d"/><circle cx="137" cy="112" r="7" fill="#e5484d"/>
<text x="0" y="176" style="font-size:12px">辺の 4 点 ×1、斜め 4 点 ×2（合計 ÷12）</text>
</g>
</svg>

## ダウンサンプル（5 タップ）

<strong>中心（重み 4）と、斜めの 4 点（重み 1）</strong>を**バイリニアで読み、合計を 8 で割ります**。

```hlsl
float3 DualDown(Texture2D src, SamplerState linear_clamp, float2 uv, float2 half_pixel, float offset) {
  float3 sum = src.SampleLevel(linear_clamp, uv, 0).rgb * 4.0;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2(-1, -1) * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2( 1, -1) * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2(-1,  1) * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + half_pixel * float2( 1,  1) * offset, 0).rgb;
  return sum / 8.0;
}
```

| 点 | 説明 |
| --- | --- |
| **`half_pixel`** | **ソース（縮小前）の 1 画素の半分**の UV 幅（`0.5 / ソース幅`） |
| **`offset`** | **広がりのパラメータ**（**1.0 で標準、大きくすると広くぼける**） |
| **中心×4** | **出力 1 画素に対応する 2×2 の中央** |

## アップサンプル（8 タップ）

<strong>辺の 4 点（重み 1）と、斜めの 4 点（重み 2）</strong>を**バイリニアで読み、合計を 12 で割ります**。

```hlsl
float3 DualUp(Texture2D src, SamplerState linear_clamp, float2 uv, float2 half_pixel, float offset) {
  float3 sum = 0;
  sum += src.SampleLevel(linear_clamp, uv + float2(-1, 0) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(-1, 1) * half_pixel * offset, 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + float2(0, 1) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(1, 1) * half_pixel * offset, 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + float2(1, 0) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(1, -1) * half_pixel * offset, 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + float2(0, -1) * half_pixel * 2.0 * offset, 0).rgb;
  sum += src.SampleLevel(linear_clamp, uv + float2(-1, -1) * half_pixel * offset, 0).rgb * 2.0;
  return sum / 12.0;
}
```

**拡大側の `half_pixel`** は、**ソース（小さい画像）の半画素**です。

## 全体の手順

| 手順 | 内容 |
| --- | --- |
| **① ダウン × N 段** | **各段、5 タップで半分に縮小**。**各段の結果を保存** |
| **② アップ × N 段** | **最小の段から、8 タップで拡大**。**1 つ上の段に加算ブレンドで足す** |
| **③ 最後に元へ足す** | **最上段の結果を強さを掛けて、元の絵に足す**（[合成と強さ](composite.md)） |

<strong>全部で各段 1 パス × 2（ダウン・アップ）</strong>。**ガウスのように横・縦の 2 パスを各段で行う必要がありません**。

<!-- fig:dual-filter-passes:begin -->
<!-- fig:dual-filter-passes:end -->

## 実質の広がり

**バイリニアで読むので、1 タップが 2×2 画素を混ぜます**。**ダウンサンプルは、ソースの 約 6×6 画素**を**混ぜている**ことになります。**これを数段重ねる**と**十分に広く滑らか**です。

| 段数 | 実質の半径（元の画素） |
| --- | --- |
| **3** | **約 12〜16** |
| **5** | **約 50〜64** |
| **7** | **約 200〜250** |

**`offset` を大きくする**と、**段数を増やさずに広がりを増やせます**。**ただし大きすぎるとサンプルがまばらになり、格子状の模様**が**出ます**。

## ガウスとの比較

| 項目 | ガウス（分離・ミップ） | Dual Filter |
| --- | --- | --- |
| <strong>パス数（N 段）</strong> | **ダウン N ＋ ぼかし 2N ＋ アップ N** | **ダウン N ＋ アップ N** |
| **タップ数** | **多い** | **少ない**（5 / 8） |
| **形** | **滑らかな円形** | **やや四角い**（多段でほぼ円） |
| **帯域** | **大きい** | **小さい** |
| **向く場面** | <strong>品質重視（PC・コンソール）</strong> | <strong>帯域重視（モバイル・VR）</strong> |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **最初の段に 13 タップを使う** | **ちらつき対策**（[ダウンサンプル](downsample.md)・[Karis](karis-average.md)） |
| **段ごとに `offset` を変える** | **広がりを調整**（**奥の段ほど大きく**） |
| **アップを加算ブレンドで書く** | **足し算のパスを省く** |
| **半精度フォーマット** | **R11G11B10_FLOAT で帯域を減らす** |
| **動的な段数** | **画面サイズ・品質設定で段数を変える** |

## よくあるミス

??? failure "`half_pixel` の基準が、ダウン（ソース側）とアップ（小さい画像側）で混同される"
    **どちらも「読む側のテクスチャ」の半画素**。**読むテクスチャごとに計算**する。

??? failure "`offset` を大きくしすぎて、格子状の模様が出る"
    **段数を増やして広げる**。**`offset` は 1〜2 程度**。

??? failure "最上段で足す強さが強すぎて、全体がぼんやりする"
    **強さを下げる**（[合成と強さ](composite.md)）。

??? failure "四角いにじみが目立つ"
    **段数が少ない**。**4 段以上、またはガウスと併用**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Dual Filter ＝ <strong>縮小・拡大のサンプルの取り方自体をぼかしにする</strong>
    - [x] <strong>ダウン 5 タップ、アップ 8 タップ</strong>。<strong>バイリニアで読む</strong>
    - [x] <strong>パス数が少なく、帯域が小さい</strong>（<strong>モバイル向き</strong>）
    - [x] <strong>`offset`</strong> で<strong>広がりを調整</strong>。<strong>大きすぎると格子模様</strong>
    - [x] <strong>やや四角い形</strong>だが、<strong>多段でほぼ円</strong>

## 参考

- Marius Bjørge, "Bandwidth-Efficient Rendering"（SIGGRAPH 2015, ARM）
- Masaki Kawase, "Frame Buffer Postprocessing Effects in DOUBLE-S.T.E.A.L"（GDC 2003）

## 関連ページ

- [ブルーム](index.md)
- [ダウンサンプルとミップ チェーン](downsample.md)
- [ガウスぼかし](gaussian.md)
- [合成と強さ](composite.md)

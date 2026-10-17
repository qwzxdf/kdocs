---
title: しきい値
tags:
  - 描画
---

# しきい値

**ブルームの最初の工程**は、<strong>「どこを光らせるか」を決める</strong>ことです。**画面のうち、一定より明るい部分だけを取り出す**のが**しきい値（スレッショルド）方式**です。**暗い物がにじんで画面全体がぼんやりする**のを**防げます**。このページでは、**単純なしきい値・ソフト ニー（滑らかな立ち上がり）・しきい値なしの方式・HDR だからできること・より良いやり方**を説明します。

!!! tip "ポイント"
    - しきい値 ＝ <strong>一定の明るさ以上だけを取り出す</strong>。<strong>それ以下は 0（黒）</strong>。
    - 単純な切り捨て（ハード）は<strong>境で「ぱっ」と出入り</strong>し、<strong>ちらつく</strong>。<strong>ソフト ニー</strong>で<strong>滑らかに立ち上げる</strong>。
    - <strong>HDR だから</strong>、<strong>「1 を超えた部分」を光らせる</strong>という<strong>物理的な基準</strong>が使える。
    - <strong>取り出す量は「超過分」</strong>（<strong>元の値 − しきい値</strong>）にすると<strong>自然</strong>。
    - <strong>しきい値なし</strong>の方式は<strong>ぱっと出ない</strong>が、<strong>全体が柔らかく</strong>なる。
    - <strong>しきい値は、露出の後</strong>（<strong>露出済みの明るさ</strong>で判断）。

## 明るい所だけ取り出す

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="しきい値の曲線">
<text x="20" y="26" class="fig-title">入力の明るさ → 取り出す量</text>
<line x1="80" y1="200" x2="720" y2="200" stroke="currentColor" stroke-opacity="0.5"/><line x1="80" y1="50" x2="80" y2="200" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" stroke-dasharray="6 4" points="80,200 400,200 400,120 720,50"/>
<polyline fill="none" stroke="#2563eb" stroke-width="4" points="80,200 340,200 370,198 400,190 430,170 470,140 560,100 720,50"/>
<line x1="400" y1="200" x2="400" y2="212" stroke="currentColor"/><text x="400" y="226" text-anchor="middle" style="font-size:12px">しきい値</text>
<text x="500" y="76" style="font-size:12px;fill:#e5484d">ハード：境で急に立ち上がる（ちらつく）</text>
<text x="500" y="98" style="font-size:12px;fill:#2563eb">ソフト ニー：滑らかに立ち上がる</text>
<text x="40" y="130" style="font-size:12px">出力</text>
</svg>

| 方式 | 内容 | 見た目 |
| --- | --- | --- |
| **ハード** | **しきい値未満は 0、以上はそのまま** | **境がくっきり。動くと「ぱっ」と光る** |
| **ソフト ニー** | **しきい値の周りを滑らかな曲線でつなぐ** | **自然に光り始める** |

## ハードなしきい値

```hlsl
float3 ThresholdHard(float3 color, float threshold) {
  float brightness = max(color.r, max(color.g, color.b));
  float contribution = max(brightness - threshold, 0.0) / max(brightness, 1e-4);
  return color * contribution;
}
```

| 点 | 説明 |
| --- | --- |
| **`brightness`** | **明るさの目安**（**最大成分**または**輝度**） |
| **`brightness − threshold`** | **しきい値を超えた分**（**超過分**）だけを光らせる |
| **`/ brightness`** | **色の比率を保つ**ために**割る**（**色相が変わらない**） |

## ソフト ニー

**しきい値の周り**で**滑らかに立ち上げる**方法です（**Unity・Unreal などの標準**）。

```hlsl
float3 ThresholdSoft(float3 color, float threshold, float knee) {
  float brightness = max(color.r, max(color.g, color.b));
  float soft = clamp(brightness - threshold + knee, 0.0, 2.0 * knee);
  soft = soft * soft / (4.0 * knee + 1e-4);
  float contribution = max(soft, brightness - threshold) / max(brightness, 1e-4);
  return color * contribution;
}
```

| パラメータ | 内容 |
| --- | --- |
| **`threshold`** | **光り始める明るさ**（**例：1.0**） |
| **`knee`** | **立ち上がりの滑らかさの幅**（**0〜1。0 でハード**） |

**`knee` を大きくする**と、**しきい値より少し暗い所から、じわっと光り**始め、**動いてもちらつきません**。

## HDR だからできること

**LDR（0〜1）の時代**は、<strong>「0.8 以上」のような、見た目の明るさでしきい値</strong>を決めていました。<strong>HDR では、「1.0 を超えた」＝「ディスプレイで表現できる以上に明るい」</strong>という**物理的な意味**を**持たせられます**。

| 基準 | 意味 |
| --- | --- |
| <strong>しきい値 1.0（露出後）</strong> | **白を超えた光だけ光る**（**直接見える光源・反射のハイライト**） |
| **しきい値 0.5** | **中間より明るい所も光る**（**柔らかい光る絵**） |

**露出を掛けた後の値で比べる**ことが**大切**です（**露出が変わると光る範囲も変わる**）。

## しきい値なし

**しきい値を使わず、全画素をぼかして、少しだけ足す**方式です（**エネルギー保存型**）。

| 長所 | 短所 |
| --- | --- |
| <strong>「ぱっ」と出ない</strong> | **暗い所もにじむので全体が柔らかい・霞む** |
| **パラメータが少ない** | **光る部分を細かく制御できない** |
| **物理的に自然**（**レンズは全部の光を広げる**） | **強さを小さくしないと眠くなる** |

**現代のゲームでは、しきい値なしに少ない強さ（0.04〜0.1 程度）で足す**方式が**増えて**います。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **ソフト ニーを使う** | **ちらつきを防ぐ**（**`knee` は 0.5 程度**） |
| **色の比率を保つ** | **`/ brightness`** で**色相を保つ** |
| **露出後の値で判定** | **露出を変えても見た目が一貫** |
| **しきい値なし ＋ 弱く足す** | **自然でパラメータが少ない**（**ただし眠くなる**） |
| **ミップの最初の段で一緒に** | **しきい値を最初のダウンサンプルと同時に**行い、**パスを減らす** |
| **エミッシブ・光源だけ光らせる** | **マスクで光らせたい物だけ**にする（**ゲームごとの演出**） |

## よくあるミス

??? failure "動くと、光がぱっと点いたり消えたりする"
    **ハードなしきい値**。**ソフト ニー**にする。

??? failure "露出を変えると、光る範囲が変わりすぎる"
    **しきい値の基準を露出後の値**にそろえる。

??? failure "光る色が、白っぽく変わる"
    <strong>色の比率を保つ（`/ brightness`）</strong>。

??? failure "しきい値なしにしたら、全体が霞んで眠い"
    **足す強さを下げる**（**0.05 前後**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] しきい値 ＝ <strong>明るい所だけを取り出す</strong>。<strong>超過分</strong>を光らせる
    - [x] <strong>ハードは、ちらつく</strong>。<strong>ソフト ニー</strong>で<strong>滑らかに</strong>
    - [x] <strong>HDR なら「1.0 を超えた」</strong>を基準にできる。<strong>露出後の値</strong>で判断
    - [x] <strong>色の比率を保つ</strong>（<strong>`/ brightness`</strong>）
    - [x] <strong>しきい値なし ＋ 弱く足す</strong>も<strong>定番</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Unity, "Post-processing: Bloom"（ソフト ニーの実装）
- Epic Games, "Unreal Engine: Bloom"

## 関連ページ

- [ブルーム](index.md)
- [ダウンサンプルとミップ チェーン](downsample.md)
- [合成と強さ](composite.md)
- [露出](../tonemapping/exposure.md)

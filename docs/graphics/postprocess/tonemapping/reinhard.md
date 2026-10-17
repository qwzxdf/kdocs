---
title: Reinhard
tags:
  - 描画
---

# Reinhard

**Reinhard** は、**もっとも簡単なトーンマップ**です。**式は `x / (1 + x)` だけ**で**どれだけ明るい値も、1 を超えずに 0〜1 に収まります**。**実装が 1 行**で済むので**最初の一歩**に向きますが、**中間調まで圧縮されて、絵が眠くなりやすい**ので、**見た目の目標が決まったら、フィルミックなどに替えます**。このページでは、<strong>式の性質・白点付きの拡張・チャンネルごとと輝度ベース・改良（より良いやり方）</strong>を説明します。

!!! tip "ポイント"
    - 式 ＝ <strong>`c = x / (1 + x)`</strong>。<strong>どれだけ明るくても 1 に漸近</strong>（飽和しない）。
    - <strong>x = 1 で 0.5</strong>。<strong>中間調が持ち上がり、コントラストが低い</strong>。
    - <strong>拡張版</strong>は<strong>白点 L_w</strong>を決め、<strong>そこでちょうど 1</strong>。<strong>簡単で見た目が良くなる</strong>。
    - <strong>輝度にだけ掛ける</strong>と<strong>色相を保てる</strong>が、<strong>鮮やかな明部が飽和しすぎる</strong>ことがある。
    - <strong>より良いやり方</strong>：<strong>白点付き ＋ 輝度ベースで色を保つ ＋ 軽いコントラストの調整</strong>。

## 式と形

<div class="formula">c = x / (1 + x)</div>

```hlsl
float3 Reinhard(float3 x) {
  return x / (1.0 + x);
}
```

| 入力 x | 出力 c |
| --- | --- |
| **0** | **0** |
| **0.5** | **0.33** |
| **1** | **0.50** |
| **2** | **0.67** |
| **8** | **0.89** |
| **100** | **0.99** |

**x が大きくなるほど増え方が緩やか**になり、**1 に近づきます**。**どんな明るさでも 1 を超えない**ので、**明部が真っ白に潰れる（クランプ）ことはありません**。

<!-- fig:tonemap-reinhard:begin -->
<!-- fig:tonemap-reinhard:end -->

### 性質

| 性質 | 内容 |
| --- | --- |
| **単調増加** | **入力が増えれば、出力も必ず増える**（階調が逆転しない） |
| **飽和しない** | **∞ でも 1 に漸近する**（**真っ白に張り付かない**） |
| **低コントラスト** | **x=1 で 0.5 に持ち上がり、暗部も中間も圧縮される** → **全体が白っぽく、眠い** |
| **白に届かない** | **x がとても大きくても、1 に届かず、「純白」が出ない** |

## 白点付き Reinhard

**白点 `L_w`**（**この入力値でちょうど 1 になる**）を決める**拡張**です。

<div class="formula">c = x · (1 + x / L_w²) / (1 + x)</div>

```hlsl
float3 ReinhardExtended(float3 x, float white_point) {
  float3 numerator = x * (1.0 + x / (white_point * white_point));
  return numerator / (1.0 + x);
}
```

| `white_point` | 見た目 |
| --- | --- |
| <strong>小さい（例：2）</strong> | **早く白に届く**。**明るく、コントラストが強い** |
| <strong>大きい（例：8）</strong> | **ゆっくり白に近づく**。**ハイライトに余裕が残る** |
| **∞** | **元の Reinhard と同じ** |

**白点を使うと、「真っ白」が出せる**ので**太陽や強い光がちゃんと白く飛びます**。

## チャンネルごと・輝度ベース

**R・G・B に別々に掛ける**と**彩度の高い明るい色の色相がずれます**。**輝度にだけ掛けて、色の比率を保つ**方法もあります。

```hlsl
float Luminance(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

float3 ReinhardLuminance(float3 color, float white_point) {
  float l_old = Luminance(color);
  float l_new = l_old * (1.0 + l_old / (white_point * white_point)) / (1.0 + l_old);
  return color * (l_new / max(l_old, 1e-4));
}
```

| 方式 | 見た目 | 欠点 |
| --- | --- | --- |
| **チャンネルごと** | **明るい色が白へ向かう**（**フィルムのよう**） | **色相がずれる**（**オレンジ → 黄**） |
| **輝度ベース** | **色相が保たれる** | **彩度が高い明部が飽和して色が濃すぎる**ことがある |

詳しくは[色相の保ち方](hue-preservation.md)で比べます。

## より良いやり方

**Reinhard をそのまま使う**と**眠い絵**になりがちです。**次の工夫で簡単なまま見栄えを上げられます**。

| 工夫 | 内容 |
| --- | --- |
| **白点を設定する** | **`L_w` を 4〜8 程度**にして、**ハイライトに余裕を持たせつつ、白を出す** |
| **暗部を少し締める** | **トーンマップ後に軽く S 字のコントラスト（`pow(c, 1.1)` など）を掛ける** |
| **輝度ベースで色を保つ** | **鮮やかな色が白に飛びすぎるのを防ぐ**（ただし、飽和に注意） |
| **ブレンド** | **チャンネルごと 50 % ＋ 輝度ベース 50 %**（**ハイブリッド**） |
| **早めに卒業する** | <strong>画作りが固まったら、[フィルミック](filmic-hable.md)・[ACES](aces.md)・[AgX](agx.md)</strong> へ |

## 使いどころ

| 場面 | 向き・不向き |
| --- | --- |
| **プロトタイプ・デバッグ表示** | **向く**（1 行で済む） |
| **UI・2D 寄りの絵** | **向く**（コントラストを強く出さない） |
| **映画のような画作りの本番** | **不向き**（眠い） |

## よくあるミス

??? failure "Reinhard を掛けたら、全体が白っぽく眠い"
    **曲線の性質**。**白点を設定し、軽くコントラストを足す**、または**別の曲線**へ。

??? failure "白点を 1 にして、明るい所が飽和しすぎる"
    **`white_point` は 1 より十分大きく**（4〜8）。**1 だとほぼクランプ**と同じ。

??? failure "輝度ベースで、鮮やかな光が派手すぎる"
    **チャンネルごととブレンド**する。または**彩度を軽く落とす**。

??? failure "ガンマ変換の後に Reinhard を掛けて、暗部が潰れる"
    **トーンマップはリニアで**。**sRGB は最後**（[ガンマと HDR 出力](gamma-srgb.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Reinhard ＝ <strong>`x / (1 + x)`</strong>。<strong>1 行でどんな明るさも 0〜1 に収まる</strong>
    - [x] <strong>中間調が持ち上がって低コントラスト</strong>。<strong>眠い絵になりやすい</strong>
    - [x] <strong>白点付き</strong>で<strong>ちゃんと白を出す</strong>（<strong>4〜8</strong> が目安）
    - [x] <strong>輝度ベース</strong>で<strong>色相を保つ</strong>。ただし<strong>飽和に注意</strong>
    - [x] <strong>本番の画作りは、フィルミック・ACES・AgX へ</strong>

## 参考

- Reinhard et al., "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）
- Reinhard, Stark, Shirley, Ferwerda, "Photographic Tone Reproduction for Images"（同）

## 関連ページ

- [トーンマッピングと露出](index.md)
- [露出](exposure.md)
- [フィルミック（Hable）](filmic-hable.md)
- [色相の保ち方](hue-preservation.md)

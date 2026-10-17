---
title: ダウンサンプルとミップ チェーン
tags:
  - 描画
---

# ダウンサンプルとミップ チェーン

**広くて自然なにじみ**を、**1 回の巨大なぼかし**で作るのは**重すぎます**（**ぼかしの半径が大きいほど、タップ数が増える**）。そこで**画像を半分・1/4・1/8…と縮小しながらぼかし**、**小さい画像で広いぼかしを安く得て、最後に拡大して足し合わせる**のが**ブルームの標準**です。この**縮小の連なり**が**ミップ チェーン**です。このページでは、**なぜ縮小するのか・縮小の方法（ボックス・13 タップ）・段数の決め方・拡大して足す方法・画質の工夫**を説明します。

!!! tip "ポイント"
    - <strong>小さい画像で同じぼかしをかける</strong>と、<strong>元の画像では何倍も広いぼかし</strong>になる。<strong>しかも画素数が少なく、安い</strong>。
    - 縮小は<strong>半分ずつ（1/2・1/4・1/8…）</strong>で、<strong>5〜8 段</strong>が目安。
    - <strong>縮小のときにきちんとフィルタする</strong>（<strong>間引くとちらつく</strong>）。<strong>13 タップ</strong>が定番。
    - <strong>拡大は「テント」フィルタ</strong>で<strong>滑らかに</strong>、<strong>各段を足し合わせる</strong>。
    - <strong>各段の重み</strong>を決めると<strong>PSF の形</strong>（<strong>すそ野の長さ</strong>）を<strong>調整</strong>できる。
    - <strong>画面サイズの端数</strong>に注意（<strong>奇数サイズで半分にすると、ずれる</strong>）。

## なぜ縮小するのか

**ぼかしの半径 R（ピクセル）を直接かけると、1 ピクセルあたり約 2R+1 回のタップ**が**要ります**（**分離可能ガウスでも**）。**画像を半分に縮小すれば、同じ半径 R のぼかしが、元の画像では 2R 相当の広さ**になります。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="ミップ チェーンの考え方">
<text x="20" y="26" class="fig-title">縮小 → ぼかし → 拡大：小さい画像のぼかしは、広い範囲に効く</text>
<g font-size="12">
<rect x="30" y="60" width="160" height="120" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="110" cy="120" r="6" fill="#f59e0b"/><text x="110" y="198" text-anchor="middle">元の画像（1/1）</text>
<rect x="230" y="75" width="110" height="90" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="285" cy="120" r="5" fill="#f59e0b" opacity="0.8"/><text x="285" y="198" text-anchor="middle">1/2</text>
<rect x="380" y="90" width="70" height="60" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="415" cy="120" r="5" fill="#f59e0b" opacity="0.6"/><text x="415" y="198" text-anchor="middle">1/4</text>
<rect x="490" y="100" width="44" height="40" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="512" cy="120" r="5" fill="#f59e0b" opacity="0.5"/><text x="512" y="198" text-anchor="middle">1/8</text>
<rect x="574" y="108" width="28" height="24" fill="#fff7d1" stroke="#94a3b8" stroke-width="2"/><circle cx="588" cy="120" r="4" fill="#f59e0b" opacity="0.4"/><text x="588" y="198" text-anchor="middle">1/16</text>
</g>
<text x="640" y="110" style="font-size:13px">段が深いほど、</text><text x="640" y="132" style="font-size:13px">画素が少なく、</text><text x="640" y="154" style="font-size:13px">広いぼかしが安い</text>
<text x="30" y="236" style="font-size:12px">コスト：各段は前の 1/4 の画素数 → 全段を足しても、元の画像 1 枚の約 1/3 増し</text>
</svg>

| 方法 | 1 画素あたりのコスト | 広さ |
| --- | --- | --- |
| **元の解像度で半径 64 のガウス** | <strong>約 130 タップ（分離でも 2 パス）</strong> | **半径 64** |
| **ミップ 6 段で各段 小さなぼかし** | **各段 数タップ、画素数は急減** | **半径 64 以上** |

## ダウンサンプルの方法

**縮小のとき、ただ間引く（点サンプル）と、小さな明るい点が画素の位置次第で「出たり消えたり」して、ちらつきます**。**周りを平均して縮小**する必要があります。

### バイリニア 1 回（2×2 の平均）

```hlsl
float3 DownsampleBilinear(Texture2D src, SamplerState linear_clamp, float2 uv) {
  return src.SampleLevel(linear_clamp, uv, 0).rgb;
}
```

**GPU のバイリニア補間が、4 画素の平均**を**1 タップで**与えます。**速いですがちらつきを完全には防げません**。

### 13 タップ（Call of Duty: Advanced Warfare 方式）

**中心と周囲 13 点を、重み付きで平均**する方式です。**小さな明るい点のちらつきを、ほぼ消せる**ため、**定番**です。

```hlsl
float3 Downsample13(Texture2D src, SamplerState linear_clamp, float2 uv, float2 texel) {
  float3 a = src.SampleLevel(linear_clamp, uv + texel * float2(-2, -2), 0).rgb;
  float3 b = src.SampleLevel(linear_clamp, uv + texel * float2( 0, -2), 0).rgb;
  float3 c = src.SampleLevel(linear_clamp, uv + texel * float2( 2, -2), 0).rgb;
  float3 d = src.SampleLevel(linear_clamp, uv + texel * float2(-2,  0), 0).rgb;
  float3 e = src.SampleLevel(linear_clamp, uv, 0).rgb;
  float3 f = src.SampleLevel(linear_clamp, uv + texel * float2( 2,  0), 0).rgb;
  float3 g = src.SampleLevel(linear_clamp, uv + texel * float2(-2,  2), 0).rgb;
  float3 h = src.SampleLevel(linear_clamp, uv + texel * float2( 0,  2), 0).rgb;
  float3 i = src.SampleLevel(linear_clamp, uv + texel * float2( 2,  2), 0).rgb;
  float3 j = src.SampleLevel(linear_clamp, uv + texel * float2(-1, -1), 0).rgb;
  float3 k = src.SampleLevel(linear_clamp, uv + texel * float2( 1, -1), 0).rgb;
  float3 l = src.SampleLevel(linear_clamp, uv + texel * float2(-1,  1), 0).rgb;
  float3 m = src.SampleLevel(linear_clamp, uv + texel * float2( 1,  1), 0).rgb;

  float3 center = (j + k + l + m) * 0.25;
  float3 box_a = (a + b + d + e) * 0.25;
  float3 box_b = (b + c + e + f) * 0.25;
  float3 box_c = (d + e + g + h) * 0.25;
  float3 box_d = (e + f + h + i) * 0.25;
  return center * 0.5 + (box_a + box_b + box_c + box_d) * 0.125;
}
```

| 点 | 説明 |
| --- | --- |
| **`texel`** | **ソース画像の 1 画素の UV 幅**（`1 / ソース幅`） |
| **重みの構成** | **中央の 2×2 に 0.5、周囲の 4 つの 2×2 ボックスに 0.125 ずつ**（**合計 1**） |
| **バイリニアと併用** | **各タップがバイリニアで 4 画素ずつを混ぜる**ので、**実質 36 画素を平均** |
| **最初の段だけ使う** | **2 段目以降は、軽い 4 タップ**でも足りる |

<!-- fig:bloom-mip-chain:begin -->
<!-- fig:bloom-mip-chain:end -->

## 段数の決め方

| 項目 | 内容 |
| --- | --- |
| **段数** | **5〜8 段**（**最小の段が 画面の 1/32〜1/128**） |
| **広さ** | **段が深いほど、画面の広い範囲に光が回る**（<strong>大きな「もや」</strong>） |
| **解像度に依らない見た目** | **段数を画面の大きさから決める**（**4K でも、1080p でも同じ見た目**） |
| **最初の段** | **画面の 1/2 で始める**（**フル解像度で始めると重い**） |

**画面の端数**に注意します。**奇数の幅を半分にすると、1 画素ずつずれ**、**光が少し動いて見えます**。**切り上げ（`(w + 1) / 2`）で作り、サンプルの位置も合わせる**と**安定**します。

## アップサンプルして足し合わせる

**小さい方から、順に拡大して、1 段上に足していきます**。

<div class="formula">段 i の結果 = ぼかした段 i + アップサンプル( 段 i+1 の結果 )</div>

```hlsl
float3 UpsampleTent(Texture2D src, SamplerState linear_clamp, float2 uv, float2 texel) {
  float3 sum = 0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2(-1, -1), 0).rgb * 1.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 0, -1), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 1, -1), 0).rgb * 1.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2(-1,  0), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv, 0).rgb * 4.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 1,  0), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2(-1,  1), 0).rgb * 1.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 0,  1), 0).rgb * 2.0;
  sum += src.SampleLevel(linear_clamp, uv + texel * float2( 1,  1), 0).rgb * 1.0;
  return sum / 16.0;
}
```

| 点 | 説明 |
| --- | --- |
| <strong>テント フィルタ（3×3）</strong> | **中心 4、辺 2、角 1 の重み**。**滑らかに拡大**できる |
| **加算ブレンドで書く** | **1 段上の画像にブレンド（加算）で書き込む**と**足し算のパスが不要** |
| **バイリニアの拡大では、ブロック状が出る** | **テントで滑らかにする** |

## 各段の重みで PSF を調整する

**各段を足すときの重み**を**変える**と、**にじみの形**（**すそ野の長さ**）を**調整**できます。

| 重みの付け方 | 見た目 |
| --- | --- |
| **均等** | **標準的なにじみ** |
| **小さい段（広い）を弱く** | **すそ野が短く、くっきり** |
| **大きい段（広い）を強く** | **広い「もや」が目立つ。眩しい・夢のような** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **13 タップで最初の段を縮小** | **ちらつきを抑える** |
| **2 段目以降は軽い縮小** | **4 タップのバイリニアで十分** |
| **アップサンプル時に加算ブレンド** | **パス数と帯域を減らす** |
| <strong>半精度（R11G11B10）</strong> | **メモリと帯域を減らす**（HDR でもブルームは精度が低くてよい） |
| **解像度を画面の高さで決める** | **段数が画面サイズで変わっても、見た目をそろえる** |
| **Dual Filter を使う** | **縮小とぼかしを兼ねて、さらに安く**（[Dual Filter](dual-filter.md)） |

## よくあるミス

??? failure "縮小を点サンプルにして、小さな明るい点がちらつく"
    **バイリニア（最低）、できれば 13 タップ**で縮小。<strong>さらに[ファイアフライ対策](karis-average.md)</strong>。

??? failure "段数を固定して、4K ではにじみが狭く見える"
    **画面の高さから、段数・最小サイズを決める**。

??? failure "奇数サイズで縮小して、光が 1 画素ずつ動く"
    **切り上げのサイズで作り、UV を合わせる**。

??? failure "アップサンプルをバイリニアだけにして、四角いブロックが見える"
    <strong>テント フィルタ（3×3）</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>縮小しながらぼかす</strong>と、<strong>広いぼかしが安い</strong>（<strong>ミップ チェーン</strong>）
    - [x] <strong>縮小は、きちんとフィルタ</strong>（<strong>13 タップ</strong>）。<strong>間引くとちらつく</strong>
    - [x] <strong>5〜8 段</strong>。<strong>画面の高さから決める</strong>
    - [x] <strong>拡大はテント</strong>、<strong>加算ブレンドで足し合わせる</strong>
    - [x] <strong>各段の重み</strong>で<strong>すそ野の長さ</strong>を調整

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Mittring, "A Bit More Deferred - CryEngine 3"（GDC 2009）
- Williams, "Pyramidal Parametrics"（SIGGRAPH 1983）

## 関連ページ

- [ブルーム](index.md)
- [しきい値](threshold.md)
- [ガウスぼかし](gaussian.md)
- [Dual Filter](dual-filter.md)
- [ファイアフライ（Karis）](karis-average.md)

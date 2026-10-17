---
title: ブルーム
tags:
  - 描画
---

# ブルーム

**非常に明るい光**（太陽・ランプ・光る面）は、**カメラのレンズや目の中で散乱**して、**輪郭の外ににじんで見えます**。これが**ブルーム**（Bloom、グロー）です。<strong>ゲームでは画面全体で「明るい部分を抽出 → ぼかす → 元の画像に足す」</strong>ことで再現します。**光の強さを画面の白の限界を超えて伝える**効果で、**HDR レンダリングの代表的な見せ場**です。

!!! tip "ポイント"
    - ブルーム ＝ <strong>明るい部分を、ぼかして、足す</strong>。<strong>光が「輝いて」見える</strong>。
    - <strong>HDR（リニア）</strong>で行う。<strong>トーンマップの前</strong>に足す（またはトーンマップ後に調整）。
    - <strong>広くぼかす</strong>には、<strong>ダウンサンプルのチェーン</strong>（ミップ）を使う。<strong>1 回の巨大ガウス</strong>は<strong>高価</strong>。
    - <strong>Dual Filter（Kawase）</strong>は<strong>安く、きれい</strong>。<strong>COD: AW の方式（13 タップ ＋ テント）</strong>が<strong>現代の標準</strong>。
    - <strong>しきい値</strong>方式より、<strong>しきい値なし（全体を少しずつ足す）</strong>が<strong>物理的でちらつかない</strong>。
    - <strong>ファイアフライ（極端に明るい 1 画素）</strong>は<strong>Karis Average</strong>で抑える。

## 原理

**点光源をレンズで撮る**と<strong>光は理想的な 1 点に集まらず、わずかに広がります（点広がり関数、PSF）</strong>。**明るい光ほど、広がった「すそ野」が、見えるようになる**のがブルームです。

<div class="formula">出力 = 元の画像 + 強さ × (元の画像 ⊛ PSF)</div>

| 要素 | 内容 |
| --- | --- |
| <strong>⊛（畳み込み）</strong> | **画像を、PSF（ぼかしのカーネル）でぼかす** |
| **PSF** | **中心が強く、すそ野が長い**形（**ガウスの重ね合わせ・べき乗則**に近い） |
| **足す** | **加算**（光の合成） |

**1 回の大きなぼかし**でなく、**幅の異なる複数のぼかしを足し合わせる**と、**自然なすそ野**になります。

<!-- fig:bloom-stages:begin -->

<svg class="fig illust motion" data-fig="bloom-stages" viewBox="0 0 780 340" role="img"><rect x="0" y="0" width="780" height="340" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bloom-stages" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<filter id="bl-a" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="3"/>
</filter>
<filter id="bl-b" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="7"/>
</filter>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ブルーム:明るい所だけ抜き出し → ぼかして → 元に足す</text>
<g opacity="1"><text x="20" y="62" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">① 元の絵</text>
<rect x="20" y="76" width="155" height="120" fill="#0f172a" stroke="#94a3b8" stroke-width="2"/>
<rect x="34" y="142" width="56" height="46" fill="#475569"/>
<rect x="108" y="156" width="52" height="32" fill="#64748b"/>
<circle cx="56" cy="114" r="11" fill="#fff7d1"/>
<circle cx="120" cy="150" r="8" fill="#fff7d1"/>
<circle cx="84" cy="172" r="6" fill="#fff7d1"/>
</g>
<line x1="179" y1="136.0" x2="209" y2="136.0" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-bloom-stages)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1388;0.1391;1.0000" values="0;0;1;1"/></line>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;1.0000" values="0;0;1;1"/><text x="215" y="62" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">② 明るい所だけ</text>
<rect x="215" y="76" width="155" height="120" fill="#0f172a" stroke="#94a3b8" stroke-width="2"/>
<circle cx="251" cy="114" r="11" fill="#fff7d1"/>
<circle cx="315" cy="150" r="8" fill="#fff7d1"/>
<circle cx="279" cy="172" r="6" fill="#fff7d1"/>
</g>
<line x1="374" y1="136.0" x2="404" y2="136.0" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-bloom-stages)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000" values="0;0;1;1"/></line>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/><text x="410" y="62" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">③ ぼかす</text>
<rect x="410" y="76" width="155" height="120" fill="#0f172a" stroke="#94a3b8" stroke-width="2"/>
<g filter="url(#bl-a)"><circle cx="446" cy="114" r="11" fill="#fff7d1"/>
<circle cx="510" cy="150" r="8" fill="#fff7d1"/>
<circle cx="474" cy="172" r="6" fill="#fff7d1"/>
</g>
<g filter="url(#bl-b)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4174;0.5565;1.0000" values="0;0;1;1"/><circle cx="446" cy="114" r="11" fill="#fff7d1"/>
<circle cx="510" cy="150" r="8" fill="#fff7d1"/>
<circle cx="474" cy="172" r="6" fill="#fff7d1"/>
</g>
</g>
<line x1="569" y1="136.0" x2="599" y2="136.0" stroke="#1f2937" stroke-width="2.5" marker-end="url(#arr-bloom-stages)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000" values="0;0;1;1"/></line>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000" values="0;0;1;1"/><text x="605" y="62" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">④ 元に足す</text>
<rect x="605" y="76" width="155" height="120" fill="#0f172a" stroke="#94a3b8" stroke-width="2"/>
<rect x="619" y="142" width="56" height="46" fill="#475569"/>
<rect x="693" y="156" width="52" height="32" fill="#64748b"/>
<g filter="url(#bl-b)" opacity="0.95"><circle cx="641" cy="114" r="16.5" fill="#ffe27a"/>
<circle cx="705" cy="150" r="12.0" fill="#ffe27a"/>
<circle cx="669" cy="172" r="9.0" fill="#ffe27a"/>
</g>
<circle cx="641" cy="114" r="11" fill="#ffffff"/>
<circle cx="705" cy="150" r="8" fill="#ffffff"/>
<circle cx="669" cy="172" r="6" fill="#ffffff"/>
</g>
<text x="20" y="236" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">まず、ふつうに描いた絵（明るい光の周りは、にじんでいない）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;1.0000" values="1;1;0;0"/></text>
<text x="20" y="236" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 閾値より明るいピクセルだけを残す（あとは黒）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="236" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 縮小しながらぼかして、光のにじみを作る（ぼかしが強くなる）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.6257;0.6261;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="236" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ ぼかした光を元の絵に足す → 明るい物が光って見える<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6257;0.6261;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="20" y="272" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">ぼかしは、縮小 → ぼかし → 拡大を重ねると、広くて安いにじみになる。</text>
<text x="20" y="296" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">足す前に閾値で選ぶので、暗い所は光らない。</text>
</svg>

<!-- fig:bloom-stages:end -->

## 実装の流れ

| 手順 | 内容 |
| --- | --- |
| <strong>① （しきい値）</strong> | **明るい部分だけを取り出す**（オプション） |
| **② ダウンサンプル** | **半分・1/4・1/8…と縮小**して、**ミップ チェーン**を作る |
| **③ アップサンプル** | **小さい方から、順に拡大して、足し合わせる** |
| **④ 合成** | **元の HDR 画像に強さを掛けて加算** |

### しきい値方式

**一定の輝度以上**だけを**抽出**する、**古典的な方式**です。

```hlsl
float3 ExtractBright(float3 color, float threshold, float knee) {
  float brightness = max(color.r, max(color.g, color.b));
  float soft = clamp(brightness - threshold + knee, 0.0, 2.0 * knee);
  soft = soft * soft / (4.0 * knee + 1e-5);
  float contribution = max(soft, brightness - threshold) / max(brightness, 1e-5);
  return color * contribution;
}
```

| 点 | 説明 |
| --- | --- |
| **`threshold`** | **この明るさ以上がにじむ**（例：1.0） |
| **`knee`** | **しきい値付近の滑らかな立ち上がり**（**突然、にじみ始めない**） |
| **欠点** | **しきい値の近くでにじむ・にじまないが切り替わり**、**物体の動きでちらつく**ことがある |

### しきい値なし

**しきい値を使わず、画像全体をぼかして、小さな係数で足す**方式です。<strong>物理的（レンズの散乱は、明るさに関係なく起こる）</strong>で、**ちらつかず**、**最近の標準**です。**HDR で明るい物ほど、足される量が多くなる**ので、**自然に明るい部分がにじみます**。

| 方式 | 利点 | 欠点 |
| --- | --- | --- |
| **しきい値あり** | **にじむ範囲を制御しやすい** | **ちらつく・不自然な境界** |
| **しきい値なし** | **物理的・安定** | **全体がわずかにぼんやりする**（強さを小さく） |

## ダウンサンプルとアップサンプル

**広い範囲のぼかしを、1 つの巨大なガウシアン**で行うと、**コストが半径に比例**して**重い**です。**縮小して小さな画像でぼかす**と、**同じ見た目の範囲がはるかに安く**得られます。

### ミップ チェーン

**元の画像を、1/2・1/4・1/8…と縮小**し、**各段で軽いぼかし**を掛けます。**小さな画像ほど、元の画像での広い範囲**に**対応**します。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="ブルームのミップ チェーン">
<text x="20" y="24" class="fig-title">縮小しながらぼかし、小さい方から拡大して足し合わせる</text>
<g stroke="currentColor" stroke-width="2" fill="rgba(76,139,245,0.15)"><rect x="30" y="50" width="120" height="80"/><rect x="170" y="70" width="80" height="54"/><rect x="270" y="86" width="54" height="36"/><rect x="344" y="98" width="36" height="24"/><rect x="400" y="106" width="24" height="16"/></g>
<g style="font-size:11px"><text x="62" y="146">1/1（元）</text><text x="190" y="146">1/2</text><text x="282" y="146">1/4</text><text x="350" y="146">1/8</text><text x="402" y="146">1/16</text></g>
<g stroke="currentColor" stroke-width="2" fill="none"><line x1="150" y1="90" x2="170" y2="90"/><line x1="250" y1="100" x2="270" y2="100"/><line x1="324" y1="108" x2="344" y2="108"/><line x1="380" y1="114" x2="400" y2="114"/></g>
<text x="440" y="90" style="font-size:12px">ダウンサンプル（縮小 ＋ ぼかし）：下へ</text><text x="440" y="112" style="font-size:12px">アップサンプル（拡大 ＋ 加算）：上へ戻る</text>
<text x="30" y="190" style="font-size:12px">各段が、異なる幅のぼかし → 足し合わせると、すそ野の長い自然なブルームになる</text>
</svg>

### Dual Filter（Kawase）

**ダウンサンプルとアップサンプルの、専用フィルタ**で**少ないタップ数で滑らか**です。

| 段階 | 内容 |
| --- | --- |
| **ダウンサンプル** | <strong>中心の 1 点（重み 4）＋ 四隅（重み 1 ずつ）</strong>を**ダイアゴナルにサンプル**（5 タップ） |
| **アップサンプル** | **周囲 8 点**を**サンプル**して**足す**（テント状） |

### 13 タップ ダウンサンプル（Call of Duty: Advanced Warfare）

**現代の標準的**な方式です。**2×2 のボックスを 5 つ（中央 1 つと 4 隅）重ね**て、**13 タップ**で**ダウンサンプル**します。**エイリアシング（ちらつき）が少ない**のが**特徴**です。

```hlsl
float3 DownsampleBox13(Texture2D<float4> source, SamplerState linear_sampler, float2 uv,
                       float2 texel_size) {
  float3 a = source.SampleLevel(linear_sampler, uv + texel_size * float2(-2, -2), 0).rgb;
  float3 b = source.SampleLevel(linear_sampler, uv + texel_size * float2(0, -2), 0).rgb;
  float3 c = source.SampleLevel(linear_sampler, uv + texel_size * float2(2, -2), 0).rgb;
  float3 d = source.SampleLevel(linear_sampler, uv + texel_size * float2(-2, 0), 0).rgb;
  float3 e = source.SampleLevel(linear_sampler, uv, 0).rgb;
  float3 f = source.SampleLevel(linear_sampler, uv + texel_size * float2(2, 0), 0).rgb;
  float3 g = source.SampleLevel(linear_sampler, uv + texel_size * float2(-2, 2), 0).rgb;
  float3 h = source.SampleLevel(linear_sampler, uv + texel_size * float2(0, 2), 0).rgb;
  float3 i = source.SampleLevel(linear_sampler, uv + texel_size * float2(2, 2), 0).rgb;
  float3 j = source.SampleLevel(linear_sampler, uv + texel_size * float2(-1, -1), 0).rgb;
  float3 k = source.SampleLevel(linear_sampler, uv + texel_size * float2(1, -1), 0).rgb;
  float3 l = source.SampleLevel(linear_sampler, uv + texel_size * float2(-1, 1), 0).rgb;
  float3 m = source.SampleLevel(linear_sampler, uv + texel_size * float2(1, 1), 0).rgb;

  float3 center = (j + k + l + m) * 0.25 * 0.5;
  float3 top_left = (a + b + d + e) * 0.25 * 0.125;
  float3 top_right = (b + c + e + f) * 0.25 * 0.125;
  float3 bottom_left = (d + e + g + h) * 0.25 * 0.125;
  float3 bottom_right = (e + f + h + i) * 0.25 * 0.125;
  return center + top_left + top_right + bottom_left + bottom_right;
}
```

| 点 | 説明 |
| --- | --- |
| **`texel_size`** | **ソース（縮小前）の 1 テクセル分の uv** |
| **13 タップ** | **中央のボックス（j,k,l,m）の重み 0.5**・**4 つの角のボックス**（それぞれ 0.125） |
| **効果** | **縮小時のちらつき（明るい 1 画素のフレームごとの出入り）を抑える** |

### アップサンプル（テント）

**9 タップのテント フィルタ**で、**拡大**しながら、**1 段上の画像に足します**。

```hlsl
float3 UpsampleTent(Texture2D<float4> source, SamplerState linear_sampler, float2 uv,
                    float2 texel_size, float radius) {
  float4 d = texel_size.xyxy * float4(1, 1, -1, 0) * radius;
  float3 sum = source.SampleLevel(linear_sampler, uv - d.xy, 0).rgb;
  sum += source.SampleLevel(linear_sampler, uv - d.wy, 0).rgb * 2.0;
  sum += source.SampleLevel(linear_sampler, uv - d.zy, 0).rgb;
  sum += source.SampleLevel(linear_sampler, uv + d.zw, 0).rgb * 2.0;
  sum += source.SampleLevel(linear_sampler, uv, 0).rgb * 4.0;
  sum += source.SampleLevel(linear_sampler, uv + d.xw, 0).rgb * 2.0;
  sum += source.SampleLevel(linear_sampler, uv + d.zy, 0).rgb;
  sum += source.SampleLevel(linear_sampler, uv + d.wy, 0).rgb * 2.0;
  sum += source.SampleLevel(linear_sampler, uv + d.xy, 0).rgb;
  return sum * (1.0 / 16.0);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>重み（1,2,1 / 2,4,2 / 1,2,1）</strong> | <strong>3×3 のテント（バイリニアの 2 回分）</strong>。**合計 16** |
| **`radius`** | **にじみの広がり**（**1 が標準**。**大きいと粗いが広い**） |
| **加算** | **アップサンプルの結果を、1 段上のダウンサンプル画像に足し**、**次へ**進む |

## ファイアフライ（Karis Average）

**極端に明るい 1 画素**（太陽の反射・スペキュラの点）があると**縮小のたびに周りへ広がり**、<strong>フレームごとに強くちらつく（ファイアフライ）</strong>ことがあります。**最初のダウンサンプルで、輝度で重み付け平均**する**Karis Average** が、**対策**です。

```hlsl
float3 KarisAverage(float3 color) {
  float luma = Luminance(color);
  return color / (1.0 + luma);
}

float3 DownsampleFirst(Texture2D<float4> source, SamplerState linear_sampler, float2 uv,
                       float2 texel_size) {
  float3 a = source.SampleLevel(linear_sampler, uv + texel_size * float2(-1, -1), 0).rgb;
  float3 b = source.SampleLevel(linear_sampler, uv + texel_size * float2(1, -1), 0).rgb;
  float3 c = source.SampleLevel(linear_sampler, uv + texel_size * float2(-1, 1), 0).rgb;
  float3 d = source.SampleLevel(linear_sampler, uv + texel_size * float2(1, 1), 0).rgb;

  float wa = 1.0 / (1.0 + Luminance(a));
  float wb = 1.0 / (1.0 + Luminance(b));
  float wc = 1.0 / (1.0 + Luminance(c));
  float wd = 1.0 / (1.0 + Luminance(d));
  return (a * wa + b * wb + c * wc + d * wd) / (wa + wb + wc + wd);
}
```

| 点 | 説明 |
| --- | --- |
| **重み `1 / (1 + 輝度)`** | **明るい画素の重みを下げる**。**1 画素が極端に明るくても、平均への寄与が限られる** |
| **最初の段だけ** | **最初のダウンサンプルで適用**すれば**十分**（以降はすでに抑えられている） |

## 合成と強さ

```hlsl
float3 hdr = scene_color.Sample(linear_sampler, uv).rgb;
float3 bloom = bloom_texture.Sample(linear_sampler, uv).rgb;
float3 result = lerp(hdr, bloom, bloom_intensity);
```

| 式 | 内容 |
| --- | --- |
| **`hdr + bloom * intensity`** | **単純な加算<strong>。</strong>明るさが増える** |
| **`lerp(hdr, bloom, k)`**（COD 方式） | **元の画像を少し減らして、ブルームと混ぜる**。**全体の明るさを保つ**（エネルギー保存的）。**k は 0.05〜0.15 程度** |

**強すぎる**と**画面全体が霞んで眠い**見た目になります。**控えめ**が**基本**です。

## レンズ ダートとの組み合わせ

**レンズの汚れ・傷**（**ダート マスク**）の**テクスチャ**を**ブルームに掛ける**と**明るい光の周りに汚れの模様が浮かぶ**、**映画的な見た目**になります。

```hlsl
float3 dirt = dirt_texture.Sample(linear_sampler, uv).rgb;
float3 bloom_with_dirt = bloom * (1.0 + dirt * dirt_intensity);
```

## コスト

| 項目 | 内容 |
| --- | --- |
| **ダウンサンプル数** | **5〜8 段**（1/2 から 1/128 程度） |
| **各段のコスト** | **解像度が 1/4 ずつ**減るので、**全体で最初の段の約 1.33 倍**で済む |
| **帯域** | **フル解像度の読み書きは、最初の段だけ** |
| **最適化** | **ダウンサンプルの最初を、半解像度**から・**コンピュートで複数ミップを 1 回の起動で**・**ブルームを、FP16 / R11G11B10** |

## よくあるミス

??? failure "ブルームを、トーンマップの後（LDR）で掛けて、明るさの強弱が付かず、白がにじむだけ"
    **HDR（リニア）で**、**トーンマップの前**に足す。

??? failure "しきい値が急で、明るさの境界でちらつく"
    **ソフト ニー**・**しきい値なし**にする。

??? failure "明るい 1 画素が、ちらついて画面全体がきらめく（ファイアフライ）"
    **最初のダウンサンプルで Karis Average**。

??? failure "ブルームを強くしすぎて、画面が霞む"
    **強さを抑え**、**`lerp` で元画像と混ぜる**。

??? failure "縮小で、単純な 2×2 ボックスを使って、ちらつき・ジャギー"
    <strong>13 タップ（または Dual Filter）</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ブルーム ＝ <strong>明るい光のにじみ</strong>。<strong>画像をぼかして、元に足す</strong>。<strong>HDR・トーンマップの前</strong>
    - [x] 広くぼかすには<strong>ダウンサンプルのチェーン</strong>。<strong>13 タップ（COD）・Dual Filter</strong>が<strong>安く・きれい</strong>
    - [x] <strong>アップサンプルはテント</strong>で<strong>足し合わせる</strong>。<strong>各段が異なる幅</strong>のぼかし
    - [x] <strong>しきい値なし</strong>が<strong>物理的で、ちらつかない</strong>。<strong>ファイアフライは Karis Average</strong>
    - [x] <strong>強さは控えめ</strong>に。<strong>`lerp(元, ブルーム, k)`</strong> で<strong>明るさを保つ</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Kawase, "Frame Buffer Postprocessing Effects in DOUBLE-S.T.E.A.L"（GDC 2003、Dual Filter の元）
- Karis, "High Quality Bloom"（Unreal Engine ブログ）

## 関連ページ

- [ポストプロセス](index.md)
- [トーンマッピングと露出](tonemapping.md)
- [レンズ効果](lens-effects.md)
- [低解像度エフェクト](../../rendering/low-res-effects.md)

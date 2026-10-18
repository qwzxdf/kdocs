---
title: DDGI
tags:
  - 描画
---

# DDGI

[ライト プローブ](probes/index.md)は、**ベイク**すると**固定**で**ライトが動くと追従できません**。**DDGI**（Dynamic Diffuse Global Illumination）は、**3D 格子に並べたプローブを、毎フレーム、少数のレイトレースで更新**し、**動くライト・動く物体**にも**追従する**動的 GI です。**プローブに放射照度だけでなく「距離（可視性）」も保存**して、**壁越しの光漏れ**を**抑える**のが、特徴です。<strong>NVIDIA（Majercik ら、2019）</strong>が提案し、**RTXGI** として製品化されました。

!!! tip "ポイント"
    - <strong>3D 格子</strong>にプローブを置き、<strong>毎フレーム、各プローブから数十〜百数十本のレイ</strong>を飛ばす。
    - <strong>結果をプローブごとの小さな八面体マップ</strong>（<strong>放射照度</strong>と<strong>距離</strong>）に<strong>時間的に混ぜて</strong>蓄積。
    - <strong>多バウンス</strong>：<strong>ヒット点で前フレームのプローブ</strong>を読む（<strong>無料</strong>）。
    - <strong>可視性</strong>：<strong>距離と距離²</strong>を保存し、<strong>チェビシェフ</strong>の考え方で<strong>壁越しのプローブの重みを下げる</strong>。
    - <strong>静的 ＋ 動的</strong>の<strong>両方に対応</strong>。<strong>低周波の拡散 GI</strong>が対象。
    - 必要：<strong>レイトレース（DXR）</strong>。<strong>コストは画素数でなく、プローブ数に比例</strong>。

<!-- fig:ddgi-probe-rays:begin -->

<svg class="fig illust motion" data-fig="ddgi-probe-rays" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ddgi-probe-rays" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">DDGI:プローブからレイを飛ばし、結果を少しずつ混ぜ込む</text>
<rect x="40" y="80" width="420" height="250" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="40" y="80" width="420" height="12" fill="#94a3b8"/>
<rect x="40" y="318" width="420" height="12" fill="#94a3b8"/>
<rect x="448" y="80" width="12" height="250" fill="#e5484d"/>
<rect x="40" y="80" width="12" height="250" fill="#2ea043"/>
<rect x="230" y="260" width="70" height="58" fill="#cbd5e1" stroke="#64748b" stroke-width="1.5"/>
<circle cx="250" cy="190" r="10" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<text x="264" y="178" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">プローブ</text>
<line x1="250" y1="190" x2="448" y2="150" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="448" cy="150" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="250" y1="190" x2="448" y2="230" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1172;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="448" cy="230" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1172;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="250" y1="190" x2="52" y2="140" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="52" cy="140" r="6" fill="#2ea043" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="250" y1="190" x2="52" y2="240" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2135;0.2138;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="52" cy="240" r="6" fill="#2ea043" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2135;0.2138;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="250" y1="190" x2="330" y2="92" stroke="#94a3b8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2618;0.2621;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330" cy="92" r="6" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2618;0.2621;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="250" y1="190" x2="160" y2="92" stroke="#94a3b8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3101;0.3103;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="160" cy="92" r="6" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3101;0.3103;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="250" y1="190" x2="265" y2="260" stroke="#cbd5e1" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3583;0.3586;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="265" cy="260" r="6" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3583;0.3586;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="250" y1="190" x2="215" y2="318" stroke="#94a3b8" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4066;0.4069;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="215" cy="318" r="6" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4066;0.4069;0.5583;0.5586;1.0000" values="0;0;1;1;0;0"/></circle>
<rect x="520" y="100" width="220" height="170" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="575.0" y1="100" x2="575.0" y2="270" stroke="#e2e8f0" stroke-width="1"/>
<line x1="520" y1="142.5" x2="740" y2="142.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="630.0" y1="100" x2="630.0" y2="270" stroke="#e2e8f0" stroke-width="1"/>
<line x1="520" y1="185.0" x2="740" y2="185.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="685.0" y1="100" x2="685.0" y2="270" stroke="#e2e8f0" stroke-width="1"/>
<line x1="520" y1="227.5" x2="740" y2="227.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="740" y="290" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">フレーム</text>
<text x="520" y="92" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">プローブの値</text>
<line x1="520" y1="134.0" x2="740" y2="134.0" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 3"/>
<text x="740" y="128.0" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">今のフレームの結果</text>
<path d="M520.0,236.0 L538.33,215.6 L556.67,199.28 L575.0,186.22 L593.33,175.78 L611.67,167.42 L630.0,160.74 L648.33,155.39 L666.67,151.11 L685.0,147.69 L703.33,144.95 L721.67,142.76 L740.0,141.01" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;1.0000" values="0;0;1;1"/></path>
<circle cx="520.0" cy="236.0" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4966;0.5276;0.5586;0.5897;0.6207;0.6517;0.6828;0.7138;0.7448;0.7759;0.8069;0.8379;0.8690;1.0000" values="520;520;538.33;556.67;575;593.33;611.67;630;648.33;666.67;685;703.33;721.67;740;740"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4966;0.5276;0.5586;0.5897;0.6207;0.6517;0.6828;0.7138;0.7448;0.7759;0.8069;0.8379;0.8690;1.0000" values="236;236;215.6;199.28;186.22;175.78;167.42;160.74;155.39;151.11;147.69;144.95;142.76;141.01;141.01"/></circle>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">プローブから、ランダムな方向へ<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">レイが当たった所の色（明るさ・色）を集める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.4963;0.4966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">集めた結果を、前フレームの値と混ぜる（ヒステリシス）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="370" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">赤い壁・緑の壁の色が、プローブに入る。毎フレーム少しずつ混ぜるので、ちらつかず、光の変化にも追従する。</text>
</svg>

<!-- fig:ddgi-probe-rays:end -->

## Overall Flow {#全体の流れ}

| 手順 | 内容 |
| --- | --- |
| **① レイの発射** | <strong>各プローブから、N 本（例：64〜256）</strong>のレイを**球面上のランダム方向**に飛ばす |
| **② ヒットの評価** | **レイが当たった点**の<strong>アルベド・法線・直接光（影付き）</strong>を**評価**。**ヒット点での間接光**は、<strong>プローブ自身（前フレーム）</strong>から読む |
| **③ プローブの更新** | <strong>ヒットの結果（放射輝度・距離）</strong>を、**プローブの八面体マップに、時間的に混ぜる** |
| **④ 画面のシェーディング** | **各画素**が**周囲 8 個のプローブ**を、**補間**して**間接拡散光**を得る（**可視性の重み付き**） |


最初に、<strong>各プローブから N 本（例：64〜256）のレイ</strong>を、球面上のランダムな方向へ飛ばします。次に、レイが当たった点のアルベド・法線・直接光（影付き）を評価します。ヒット点での間接光は、<strong>プローブ自身（前フレームの値）</strong>から読みます。これが再帰を避ける仕組みです。3 つ目に、ヒットの結果（放射輝度と距離）を、プローブの八面体マップに時間的に混ぜて更新します。最後に、画面の各画素が、周囲 8 個のプローブを（可視性の重み付きで）補間して、間接拡散光を得ます。

最初に、<strong>各プローブから N 本（例：64〜256）のレイ</strong>を、球面上のランダムな方向へ飛ばします。次に、レイが当たった点のアルベド・法線・直接光（影付き）を評価します。ヒット点での間接光は、<strong>プローブ自身（前フレームの値）</strong>から読みます。これが再帰を避ける仕組みです。3 つ目に、ヒットの結果（放射輝度と距離）を、プローブの八面体マップに時間的に混ぜて更新します。最後に、画面の各画素が、周囲 8 個のプローブを（可視性の重み付きで）補間して、間接拡散光を得ます。

## Probe Data {#プローブのデータ}

**各プローブ**は、**2 枚の小さなテクスチャ**（**八面体マッピング**で**球全体を正方形に展開**）を持ちます。

各プローブは、2 種類のテクスチャを持ちます。1 つは<strong>放射照度</strong>（Irradiance）で、例として 6×6 テクセル（枠を含めて 8×8）の八面体マップに、各方向の余弦畳み込み済みの入射光（RGB）を保存します。もう 1 つは<strong>距離</strong>（Distance）で、14×14 テクセル（枠を含めて 16×16）に、各方向のヒットまでの平均距離と、距離の 2 乗の平均（RG）を保存します。距離は、可視性の計算に使います。

**全プローブ**を、**1 枚の大きなアトラス**（**テクスチャ配列**）に**並べ**ます。

### Octahedral Mapping {#八面体マッピング}

**球面上の方向**を**八面体に投影し、正方形に展開**する**マッピング**です。**方向 ↔ 2D 座標**の**変換が、安く**、**面積の歪みが小さい**ので、**球の保存**に**適しています**。

```hlsl
float2 OctEncode(float3 n) {
  n /= (abs(n.x) + abs(n.y) + abs(n.z));
  float2 p = n.xy;
  if (n.z < 0.0) {
    p = (1.0 - abs(p.yx)) * float2(n.x >= 0.0 ? 1.0 : -1.0, n.y >= 0.0 ? 1.0 : -1.0);
  }
  return p * 0.5 + 0.5;
}
```

**SH**（9 係数）と違い、**八面体マップは**、**方向分解能を上げやすく**、**距離**（可視性）のように、**SH で表しにくいデータ**も**保存**できます。

## Updating Probes (Temporal Accumulation) {#プローブの更新時間蓄積}

**1 フレームに飛ばすレイ数は少ない**ので、**結果はノイズが多い**です。**前フレームの値と指数移動平均で混ぜる**ことで、**滑らか**にします。

<div class="formula">new = lerp(old, sample, 1 − hysteresis)　（hysteresis ≒ 0.97）</div>

更新の混ぜ方は、<strong>hysteresis</strong>（履歴の重み）で調整します。大きいほど滑らかですが、変化にゆっくり追従します。小さいほど速く追従しますが、ノイズが残ります。ライトが急に変わったときは、追従が遅れるため、チャンネルごとに変化を検出して、重みを一時的に下げる工夫を入れます。

### Optimizing Updates {#更新の最適化}

| 工夫 | 内容 |
| --- | --- |
| **全プローブを毎フレーム更新しない** | **画面に近い・見えるプローブ**を**優先**。**遠いものは数フレームに 1 回** |
| **レイ数を調整** | **重要なプローブは多く** |
| **プローブの無効化** | **幾何の中・何も見えない**プローブを、**スリープ**（**更新しない**） |
| <strong>スクロール（カスケード）</strong> | **カメラの周りだけ**に**プローブ格子**を置き、**移動に伴って、リサイクル** |

## Visibility (Suppressing Light Leaks) {#可視性ライト-リークの抑制}

**ライト プローブの最大の問題は、壁越しの漏れ**でした。**DDGI はプローブごとに「各方向のヒットまでの距離」を保存**することで**画素から見て、そのプローブが壁の向こうにあるか**を、**判定**します。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="DDGI の可視性">
<text x="20" y="24" class="fig-title">画素からプローブ方向のヒット距離が、画素までの距離より短ければ、間に壁がある</text>
<rect x="340" y="40" width="20" height="190" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="326" y="34" style="font-size:12px">壁</text>
<circle cx="520" cy="140" r="8" fill="currentColor"/><text x="500" y="168" style="font-size:12px">画素</text>
<circle cx="180" cy="140" r="8" fill="rgba(229,170,40,0.9)" stroke="currentColor" stroke-width="2"/><text x="120" y="168" style="font-size:12px">プローブ（壁の向こう）</text>
<line x1="180" y1="140" x2="340" y2="140" stroke="currentColor" stroke-width="2"/><line x1="340" y1="140" x2="520" y2="140" stroke="currentColor" stroke-dasharray="4 3"/>
<text x="200" y="124" style="font-size:12px">保存された距離（壁まで）</text><text x="400" y="124" style="font-size:12px">画素までの距離</text>
<text x="40" y="222" style="font-size:12px">保存された距離 ＜ 画素までの距離 → 壁に遮られている → このプローブの重みを下げる</text>
</svg>

**画素 → プローブの方向**で、**プローブの距離マップを引き**、**平均距離 μ と距離²の平均**から**分散**を求め、**チェビシェフの不等式**で**可視性の確率**を**見積もります**（[VSM](../shadows/vsm/index.md)と同じ考え方）。

```hlsl
float Visibility(float2 moments, float dist) {
  if (dist <= moments.x) return 1.0;
  float variance = max(moments.y - moments.x * moments.x, 1e-5);
  float d = dist - moments.x;
  return variance / (variance + d * d);
}
```

コードの変数の意味です。`moments.x` は、その方向のヒットまでの平均距離です。`moments.y` は距離の 2 乗の平均です。この 2 つの統計量から、チェビシェフの不等式を使って、「プローブが画素から見える確率」を推定し、戻り値とします。この値を補間の重みに掛けると、壁越しのプローブの重みが自動的に下がります。

**加えて**、**法線方向への位置のバイアス**・**プローブが画素の裏にある場合の重みの低減**（**ウェイト**に、**`max(0, dot(...))`**）を併用します。

## Pixel Shading {#画素のシェーディング}

**画素のワールド位置**から、**周囲の 8 個のプローブ**（**3D 格子のセル**の角）を求め、**トライリニアの重み**に**可視性・方向の重み**を**掛けて**、**放射照度を補間**します。

画素のシェーディングで、8 個のプローブに掛ける重みは、3 種類を掛け合わせます。**トライリニア**は、位置による基本の重みです。**方向（バックフェース）**は、画素から見てプローブが法線の裏側にあれば、重みを下げます。**可視性（チェビシェフ）**は、壁越しのプローブの重みを下げます。

**重みの合計で正規化**して、**間接拡散光**を得ます。

## Benefits and Limits {#利点と限界}

| 利点 | 限界 |
| --- | --- |
| **動く光・動く物に追従** | **DXR（レイトレース）が必要** |
| **ライト リークが少ない**（可視性） | **低周波のみ**（細かい間接影は出ない）。**AO を併用** |
| **画素数に依存しない**（プローブ数に比例） | **追従に遅れがある**（時間蓄積） |
| **事前ベイク不要**・**エディタでの待ち時間が、ない** | **薄い壁・小さな隙間**で**まだ漏れる**ことがある |
| **静的・動的の区別なく扱える** | <strong>プローブの配置（格子の間隔）</strong>で品質が決まる |
| **画面外も反映** | **メモリ**（プローブ数 × 2 テクスチャ） |


限界は、DXR（ハードウェア レイトレース）が必要なこと、低周波のみで細かい間接影は出ない（AO を併用）こと、時間蓄積による追従の遅れがあること、薄い壁や小さな隙間でまだ漏れることがあること、プローブの配置（格子の間隔）で品質が決まること、そしてメモリ（プローブ数 × 2 テクスチャ）です。

限界は、DXR（ハードウェア レイトレース）が必要なこと、低周波のみで細かい間接影は出ない（AO を併用）こと、時間蓄積による追従の遅れがあること、薄い壁や小さな隙間でまだ漏れることがあること、プローブの配置（格子の間隔）で品質が決まること、そしてメモリ（プローブ数 × 2 テクスチャ）です。

## Comparison with Light Probes {#ライト-プローブとの比較}

| 項目 | ベイク済みライト プローブ | DDGI |
| --- | --- | --- |
| **更新** | なし（固定） | **毎フレーム** |
| **動くライト** | ✕ | **○** |
| **ライト リーク対策** | 配置・手動 | <strong>可視性（自動）</strong> |
| **コスト** | 極小 | **レイトレース ＋ 更新** |
| **必要な HW** | 不要 | **DXR** |

## Common Mistakes {#よくあるミス}

??? failure "hysteresis が大きすぎて、ライトの変化に追従しない"
    **変化を検出**し、**一時的に重みを下げる**。

??? failure "壁越しに光が漏れる"
    **距離（可視性）の重み付け**・**法線バイアス**・**プローブ間隔を狭める**。

??? failure "全プローブを毎フレーム更新して重い"
    **優先度・スリープ・遠いプローブの低頻度化**。

??? failure "八面体マップの枠（ボーダー）を処理せず、補間で継ぎ目が出る"
    **枠（ボーダー）にコピー**して、**バイリニア補間**が**正しく**働くようにする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] DDGI ＝ <strong>3D 格子のプローブを、毎フレームの少数のレイトレースで更新</strong>する<strong>動的 GI</strong>
    - [x] <strong>放射照度と距離</strong>を、<strong>プローブごとの八面体マップ</strong>に保存。<strong>時間的に混ぜて</strong>蓄積
    - [x] <strong>距離（平均・2 乗平均）</strong>から<strong>チェビシェフ</strong>で<strong>可視性</strong>を求め、<strong>ライト リーク</strong>を抑える
    - [x] <strong>動く光・物に追従</strong>。<strong>低周波のみ</strong>、<strong>DXR が必要</strong>
    - [x] <strong>更新の優先度・スリープ</strong>で<strong>コストを抑える</strong>

## References {#参考}

- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）
- Majercik et al., "Scaling Probe-Based Real-Time Dynamic Global Illumination for Production"（JCGT 2021）
- NVIDIA, "RTXGI"（SDK ドキュメント）

## Related Pages {#関連ページ}

- [Global Illumination (GI)](index.md)
- [ライト プローブ](probes/index.md)
- [Ray-Traced GI](rt-gi/index.md)
- [VSM（チェビシェフ）](../shadows/vsm/index.md)
- [RT 反射](../reflections/rt-reflections/index.md)

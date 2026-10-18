---
title: DDGI
tags:
  - 描画
---

# DDGI

[ライト プローブ](probes/index.md)は <strong>ベイク</strong>すると<strong>固定</strong>でライトが動くと追従できません。DDGI（Dynamic Diffuse Global Illumination）は、3D 格子に並べたプローブを、毎フレーム、少数のレイトレースで更新し動くライト・動く物体にも追従する動的 GI です。プローブに放射照度だけでなく「距離（可視性）」も保存して、壁越しの光漏れを抑えるのが特徴です。<strong>NVIDIA（Majercik ら、2019）</strong>が提案し RTXGI として製品化されました。

!!! tip "ポイント"
    - <strong>3D 格子</strong>にプローブを置き、<strong>毎フレーム、各プローブから数十〜百数十本のレイ</strong>を飛ばす。
    - <strong>結果をプローブごとの小さな八面体マップ</strong>（<strong>放射照度</strong>と<strong>距離</strong>）に<strong>時間的に混ぜて</strong>蓄積。
    - <strong>多バウンス</strong>：<strong>ヒット点で前フレームのプローブ</strong>を読む（<strong>無料</strong>）。
    - <strong>可視性</strong>：<strong>距離と距離²</strong>を保存し、<strong>チェビシェフ</strong>の考え方で<strong>壁越しのプローブの重みを下げる</strong>。
    - <strong>静的 ＋ 動的</strong>の<strong>両方に対応</strong>。<strong>低周波の拡散 GI</strong>が対象。
    - 必要：<strong>レイトレース（DXR）</strong>。<strong>コストは画素数でなくプローブ数に比例</strong>。

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

## 全体の流れ

| 手順 | 内容 |
| --- | --- |
| ① レイの発射 | <strong>各プローブから、N 本（例：64〜256）</strong>のレイを球面上のランダム方向に飛ばす |
| ② ヒットの評価 | レイが当たった点の<strong>アルベド・法線・直接光（影付き）</strong>を評価。ヒット点での間接光は <strong>プローブ自身（前フレーム）</strong>から読む |
| ③ プローブの更新 | <strong>ヒットの結果（放射輝度・距離）</strong>を、プローブの八面体マップに時間的に混ぜる |
| ④ 画面のシェーディング | 各画素が周囲 8 個のプローブを、補間して間接拡散光を得る（可視性の重み付き） |


最初に <strong>各プローブから N 本（例：64〜256）のレイ</strong>を、球面上のランダムな方向へ飛ばします。次に、レイが当たった点のアルベド・法線・直接光（影付き）を評価します。ヒット点での間接光は <strong>プローブ自身（前フレームの値）</strong>から読みます。これが再帰を避ける仕組みです。3 つ目にヒットの結果（放射輝度と距離）を、プローブの八面体マップに時間的に混ぜて更新します。最後に、画面の各画素が周囲 8 個のプローブを（可視性の重み付きで）補間して、間接拡散光を得ます。

最初に <strong>各プローブから N 本（例：64〜256）のレイ</strong>を、球面上のランダムな方向へ飛ばします。次に、レイが当たった点のアルベド・法線・直接光（影付き）を評価します。ヒット点での間接光は <strong>プローブ自身（前フレームの値）</strong>から読みます。これが再帰を避ける仕組みです。3 つ目にヒットの結果（放射輝度と距離）を、プローブの八面体マップに時間的に混ぜて更新します。最後に、画面の各画素が周囲 8 個のプローブを（可視性の重み付きで）補間して、間接拡散光を得ます。

## プローブのデータ

<strong>各プローブ</strong>は <strong>2 枚の小さなテクスチャ</strong>（八面体マッピングで球全体を正方形に展開）を持ちます。

各プローブは 2 種類のテクスチャを持ちます。1 つは<strong>放射照度</strong>（Irradiance）で、例として 6×6 テクセル（枠を含めて 8×8）の八面体マップに、各方向の余弦畳み込み済みの入射光（RGB）を保存します。もう 1 つは<strong>距離</strong>（Distance）で、14×14 テクセル（枠を含めて 16×16）に、各方向のヒットまでの平均距離と、距離の 2 乗の平均（RG）を保存します。距離は可視性の計算に使います。

<strong>全プローブ</strong>を <strong>1 枚の大きなアトラス</strong>（テクスチャ配列）に並べます。

### 八面体マッピング

<strong>球面上の方向</strong>を<strong>八面体に投影し、正方形に展開</strong>するマッピングです。方向 ↔ 2D 座標の変換が安く、面積の歪みが小さいので球の保存に適しています。

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

<strong>SH</strong>（9 係数）と違い <strong>八面体マップは</strong>、方向分解能を上げやすく距離（可視性）のように、SH で表しにくいデータも保存できます。

## プローブの更新（時間蓄積）

<strong>1 フレームに飛ばすレイ数は少ない</strong>ので、<strong>結果はノイズが多い</strong>です。前フレームの値と指数移動平均で混ぜることで、滑らかにします。

<div class="formula">new = lerp(old, sample, 1 − hysteresis)　（hysteresis ≒ 0.97）</div>

更新の混ぜ方は <strong>hysteresis</strong>（履歴の重み）で調整します。大きいほど滑らかですが変化にゆっくり追従します。小さいほど速く追従しますがノイズが残ります。ライトが急に変わったときは追従が遅れるため、チャンネルごとに変化を検出して、重みを一時的に下げる工夫を入れます。

### 更新の最適化

| 工夫 | 内容 |
| --- | --- |
| 全プローブを毎フレーム更新しない | 画面に近い・見えるプローブを優先。遠いものは数フレームに 1 回 |
| レイ数を調整 | 重要なプローブは多く |
| プローブの無効化 | 幾何の中・何も見えないプローブを、スリープ（更新しない） |
| <strong>スクロール（カスケード）</strong> | カメラの周りだけにプローブ格子を置き、移動に伴ってリサイクル |

## 可視性（ライト リークの抑制）

<strong>ライト プローブの最大の問題は、壁越しの漏れ</strong>でした。<strong>DDGI はプローブごとに「各方向のヒットまでの距離」を保存</strong>することで画素から見て、そのプローブが壁の向こうにあるかを、判定します。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="DDGI の可視性">
<text x="20" y="24" class="fig-title">画素からプローブ方向のヒット距離が、画素までの距離より短ければ、間に壁がある</text>
<rect x="340" y="40" width="20" height="190" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="326" y="34" style="font-size:12px">壁</text>
<circle cx="520" cy="140" r="8" fill="currentColor"/><text x="500" y="168" style="font-size:12px">画素</text>
<circle cx="180" cy="140" r="8" fill="rgba(229,170,40,0.9)" stroke="currentColor" stroke-width="2"/><text x="120" y="168" style="font-size:12px">プローブ（壁の向こう）</text>
<line x1="180" y1="140" x2="340" y2="140" stroke="currentColor" stroke-width="2"/><line x1="340" y1="140" x2="520" y2="140" stroke="currentColor" stroke-dasharray="4 3"/>
<text x="200" y="124" style="font-size:12px">保存された距離（壁まで）</text><text x="400" y="124" style="font-size:12px">画素までの距離</text>
<text x="40" y="222" style="font-size:12px">保存された距離 ＜ 画素までの距離 → 壁に遮られている → このプローブの重みを下げる</text>
</svg>

<strong>画素 → プローブの方向</strong>で、<strong>プローブの距離マップを引き</strong>、平均距離 μ と距離²の平均から分散を求め、チェビシェフの不等式で可視性の確率を見積もります（[VSM](../shadows/vsm/index.md)と同じ考え方）。

```hlsl
float Visibility(float2 moments, float dist) {
  if (dist <= moments.x) return 1.0;
  float variance = max(moments.y - moments.x * moments.x, 1e-5);
  float d = dist - moments.x;
  return variance / (variance + d * d);
}
```

コードの変数の意味です。`moments.x` はその方向のヒットまでの平均距離です。`moments.y` は距離の 2 乗の平均です。この 2 つの統計量からチェビシェフの不等式を使って、「プローブが画素から見える確率」を推定し、戻り値とします。この値を補間の重みに掛けると、壁越しのプローブの重みが自動的に下がります。

<strong>加えて</strong>、<strong>法線方向への位置のバイアス</strong>・プローブが画素の裏にある場合の重みの低減（ウェイトに、`max(0, dot(...))`）を併用します。

## 画素のシェーディング

<strong>画素のワールド位置</strong>から <strong>周囲の 8 個のプローブ</strong>（3D 格子のセルの角）を求め、トライリニアの重みに可視性・方向の重みを掛けて、放射照度を補間します。

画素のシェーディングで 8 個のプローブに掛ける重みは、3 種類を掛け合わせます。<strong>トライリニア</strong>は位置による基本の重みです。<strong>方向（バックフェース）</strong>は、画素から見てプローブが法線の裏側にあれば、重みを下げます。可視性（チェビシェフ）は壁越しのプローブの重みを下げます。

<strong>重みの合計で正規化</strong>して <strong>間接拡散光</strong>を得ます。

## 利点と限界

| 利点 | 限界 |
| --- | --- |
| 動く光・動く物に追従 | DXR（レイトレース）が必要 |
| ライト リークが少ない（可視性） | 低周波のみ（細かい間接影は出ない）。AO を併用 |
| 画素数に依存しない（プローブ数に比例） | 追従に遅れがある（時間蓄積） |
| 事前ベイク不要・エディタでの待ち時間が、ない | 薄い壁・小さな隙間でまだ漏れることがある |
| 静的・動的の区別なく扱える | <strong>プローブの配置（格子の間隔）</strong>で品質が決まる |
| 画面外も反映 | メモリ（プローブ数 × 2 テクスチャ） |


限界は DXR（ハードウェア レイトレース）が必要なこと、低周波のみで細かい間接影は出ない（AO を併用）こと、時間蓄積による追従の遅れがあること、薄い壁や小さな隙間でまだ漏れることがあること、プローブの配置（格子の間隔）で品質が決まること、そしてメモリ（プローブ数 × 2 テクスチャ）です。

限界は DXR（ハードウェア レイトレース）が必要なこと、低周波のみで細かい間接影は出ない（AO を併用）こと、時間蓄積による追従の遅れがあること、薄い壁や小さな隙間でまだ漏れることがあること、プローブの配置（格子の間隔）で品質が決まること、そしてメモリ（プローブ数 × 2 テクスチャ）です。

## ライト プローブとの比較

| 項目 | ベイク済みライト プローブ | DDGI |
| --- | --- | --- |
| 更新 | なし（固定） | 毎フレーム |
| 動くライト | ✕ | ○ |
| ライト リーク対策 | 配置・手動 | <strong>可視性（自動）</strong> |
| コスト | 極小 | レイトレース ＋ 更新 |
| 必要な HW | 不要 | DXR |

## DDGI とは

<strong>DDGI</strong>（Dynamic Diffuse Global Illumination、Majercik ら 2019）は、<strong>プローブ GI</strong>（[Probe GI](probes/index.md)）の値を、毎フレーム、レイトレーシングで更新する方式です。プローブを空間に置く考え方は、ライト プローブと同じですが、ベイクではなく実行時に各プローブからレイを、飛ばして周りの光を集め直します。動的なライト、動く物、扉の開閉がすべて反映されます。

## 全体の流れ

```text
毎フレーム:
  ① 各プローブから、N 本（例 128 本）のレイを、飛ばす（レイトレーシング）
  ② レイが、当たった面の、色（ライティング済み）と、距離を、集める
  ③ 集めた値を、プローブの、放射照度マップ（8×8 の、八面体マップ）に、混ぜ込む（前の値と、ブレンド）
  ④ 物体の描画で、周りのプローブを、補間して、間接光を得る（[Interpolation Methods](probes/interpolation.md)）
```

## 八面体マップで保存する

DDGI は各プローブの <strong>放射照度</strong>を、<strong>SH ではなく</strong>、八面体マップ（球面を 1 枚の、正方形に展開した小さなテクスチャ）に、保存します。SH より方向の解像度が高く光の変化をより細かく、持てます。

| | SH L2 | 八面体マップ（8×8） |
| --- | --- | --- |
| 1 プローブのデータ | 9 係数 × RGB（27 個の数） | 64 画素 × RGB（192 個の数） |
| 方向の表現 | ごくなめらか（低周波） | やや、細かい（8×8 の方向） |
| リンギング | 出る（負の値） | 出ない |
| 補間 | 係数を足す | テクスチャとして、ハードウェアの補間（双線形） |

### 八面体マッピング：球面 ↔ 正方形

<strong>方向ベクトル</strong>（単位ベクトル）を、<strong>2D の座標</strong>（0〜1）に、変換します。

```hlsl
// 単位ベクトル（方向）→ 八面体マップの uv（0〜1）。
float2 OctEncode(float3 n) {
  n /= (abs(n.x) + abs(n.y) + abs(n.z));                                // 八面体の、表面に、投影（L1 ノルムで、正規化）
  float2 p = n.xy;
  if (n.z < 0.0) {                                                      // 下半球は、折り返して、四隅に、広げる
    p = (1.0 - abs(p.yx)) * (p.xy >= 0.0 ? 1.0 : -1.0);
  }
  return p * 0.5 + 0.5;
}

// 逆変換: uv → 方向。
float3 OctDecode(float2 uv) {
  float2 f = uv * 2.0 - 1.0;
  float3 n = float3(f.x, f.y, 1.0 - abs(f.x) - abs(f.y));
  if (n.z < 0.0) {
    n.xy = (1.0 - abs(n.yx)) * (n.xy >= 0.0 ? 1.0 : -1.0);
  }
  return normalize(n);
}
```

<strong>八面体</strong>（8 枚の三角形でできた、立体）の表面に方向を <strong>投影</strong>し、上半分はそのまま下半分は四隅へ、折り返して正方形に広げます。球面の全方向が歪みが少なく 1 枚の、正方形に収まります。

## プローブからレイを飛ばす

<strong>各プローブ</strong>が <strong>球面上の N 本</strong>（128〜256 本）のレイを飛ばし、当たった面のライティングを集めます。

```hlsl
// DXR の、レイ生成シェーダー: 各プローブについて、N 本のレイを、飛ばす。
[shader("raygeneration")]
void ProbeRayGen() {
  uint ray_index = DispatchRaysIndex().x;                               // このプローブの、何本目のレイか
  uint probe_index = DispatchRaysIndex().y;
  float3 probe_pos = g_probe_positions[probe_index];

  // 球面上に、均等に、散らす（毎フレーム、全体を、ランダムに回転させて、方向の偏りを、時間で、平均する）。
  float3 dir = mul(SphericalFibonacci(ray_index, kRaysPerProbe), g_random_rotation);

  RayDesc ray = { probe_pos, 0.0, dir, 1e27 };
  Payload payload = { float3(0, 0, 0), 0.0 };
  TraceRay(g_scene, RAY_FLAG_NONE, 0xFF, 0, 1, 0, ray, payload);

  g_ray_radiance[uint2(ray_index, probe_index)] = payload.radiance;      // 当たった面の、ライティング済みの色
  g_ray_distance[uint2(ray_index, probe_index)] = payload.hit_distance;  // 当たった距離（可視性の、計算用）
}
```

<strong>球面フィボナッチ</strong>で <strong>方向を均等に、散らし</strong>、フレームごとに全体を回転させます。フレームをまたいで平均すると、球面全体が均等にカバーされます。ヒット シェーダー（当たった面での、ライティング）は当たった面の、直接光 + 前のフレームのプローブの、間接光を計算します（多重反射が、フレームごとに積み重なります）。

## 結果をプローブに混ぜる

<strong>今フレームのレイの結果</strong>を、<strong>プローブの八面体マップ</strong>に、書き込みます。前のフレームの値とブレンド（指数移動平均）して、ノイズを減らします。

```hlsl
// 計算シェーダー: プローブの、八面体マップの、各画素について、その方向に近い、レイの結果を、重みつきで集める。
[numthreads(8, 8, 1)]
void UpdateProbeIrradianceCS(uint3 id : SV_DispatchThreadID, uint probe_index : SV_GroupID) {
  float3 texel_dir = OctDecode((id.xy + 0.5) / 8.0);                     // この画素が、表す、方向
  float3 sum = 0.0;
  float weight_sum = 0.0;
  for (uint r = 0; r < kRaysPerProbe; ++r) {
    float3 ray_dir = RayDirection(r);
    float w = max(0.0, dot(texel_dir, ray_dir));                         // 方向が、近いレイほど、重い（余弦重み）
    sum += g_ray_radiance[uint2(r, probe_index)] * w;
    weight_sum += w;
  }
  float3 result = sum / max(weight_sum, 1e-4);

  // 前のフレームと、混ぜる（hysteresis）。値が、大きく変わったら、履歴を、弱める（光の変化に、追従）。
  float3 history = g_probe_irradiance[uint3(id.xy, probe_index)].rgb;
  float change = max3(abs(result - history)) / max(max3(history), 1e-3);
  float alpha = lerp(0.97, 0.7, saturate(change * 4.0));                 // 変化が大きいほど、今フレームを、強く
  g_probe_irradiance[uint3(id.xy, probe_index)] = float4(lerp(result, history, alpha), 1.0);
}
```

<strong>八面体マップの各画素</strong>は <strong>1 つの、方向</strong>を表します。その方向に近いレイ（余弦重み）の結果を集め、前のフレームと混ぜます。混ぜる割合（`alpha` = 履歴の強さ）を値の、変化の大きさに応じて変える（Majercik ら）と光が、急に変わる（扉が開く）とき素早く追従し静かなときは、なめらかです。

## 可視性（光漏れ対策）

<strong>プローブは壁の向こう</strong>の光を、<strong>拾う</strong>ことがあります。DDGI は各プローブが各方向の、「壁までの距離」（の平均と 2 乗の平均）を別の、八面体マップに保存し補間のとき、物の位置が壁の手前にあるかを、チェビシェフの不等式で判定して、光漏れを抑えます（[Interpolation Methods](probes/interpolation.md)）。

```hlsl
// 距離マップ: 各方向の、壁までの、距離の、平均と、2 乗の平均（VSM と、同じ考え方）。
float distance = g_ray_distance[uint2(r, probe_index)];
float2 moments = float2(distance, distance * distance);                  // 1 サンプルあたりの、(距離, 距離²)
// 放射照度と、同じ要領で、八面体マップに、混ぜる（余弦重みを、鋭くして、方向の、解像度を、保つ）。
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 完全に動的（光、物、扉、壊れる壁）。ベイク不要 |
| 長所 | 世界全体の間接光（画面の外の光も、使える。SSGI の弱点がない） |
| 長所 | 多重反射が自然に、積み重なる（フレームごとに前のフレームの、プローブを使うので） |
| 長所 | コストが画面解像度に、依存しない（プローブの数とレイの数で、決まる） |
| 短所 | GPU レイトレーシング（DXR）が、必要 |
| 短所 | 低周波（プローブ間隔の、解像度）。細かい接触の影は出ない（AO、コンタクト シャドウで補う） |
| 短所 | 光の変化に遅れる（履歴との、ブレンド）。急な変化で少し遅れて見える |
| 短所 | プローブの配置（[Probe Placement](probes/placement.md)）が品質を、左右する |
| 短所 | 拡散のみ（鏡面は、別の手法） |

## コスト

| 項目 | 目安 |
| --- | --- |
| プローブ数 | 数千〜数万個 |
| 1 プローブのレイ数 | 128〜256 本 |
| 1 フレームのレイ総数 | プローブ数 × レイ数 = 数十万〜数百万本 |
| 更新のコスト | 約 0.5〜2 ms（GPU、世代による） |
| メモリ | 放射照度マップ（8×8 × RGBA16）+ 距離マップ（16×16 × RG16）で、プローブ 1 つあたり 約 1.5 KB |

<strong>カメラの近くのプローブだけ</strong>を、毎フレーム更新し <strong>遠くは数フレームに、1 回</strong>にする（更新の間引き）と、コストを抑えられます。後続の研究（Majercik ら、2021、DDGI Resampling）は、少ないレイでも品質を保つための、リサンプリングを提案しています。

## DirectX 11 では動かない部分

<strong>DXR（DirectX Raytracing）は、DirectX 12 の機能です。DirectX 11 にはありません。</strong>このページの `TraceRay`・`RayQuery` を使うコードは、D3D12 のレンダラーで動かします。D3D11 だけで同じ効果を狙うときは、次のように置き換えます。

| やりたいこと | D3D11 での代用 |
| --- | --- |
| レイと三角形の交差 | 距離場（SDF）・ボクセル、またはスクリーン空間のレイマーチ（[Linear Marching](../reflections/ssr-basics/linear-march.md)） |
| 影 | シャドウ マップ（[Shadow Map Basics](../shadows/shadow-map-basics/index.md)） |
| 間接光 | ライトマップ・プローブ・SSGI・ボクセル GI（[Global Illumination (GI)](../gi/index.md)） |

D3D12 側の初期化（加速構造・ステート オブジェクト・シェーダー テーブル・`DispatchRays`）は、[DXR Host Setup](../../directx/dx12/dxr-host.md) に、まとめています。

## よくあるミス

??? failure "hysteresis が大きすぎて、ライトの変化に追従しない"
    <strong>変化を検出</strong>し <strong>一時的に重みを下げる</strong>。

??? failure "壁越しに光が漏れる"
    <strong>距離（可視性）の重み付け</strong>・<strong>法線バイアス</strong>・プローブ間隔を狭める。

??? failure "全プローブを毎フレーム更新して重い"
    <strong>優先度・スリープ・遠いプローブの低頻度化</strong>。

??? failure "八面体マップの枠（ボーダー）を処理せず、補間で継ぎ目が出る"
    <strong>枠（ボーダー）にコピー</strong>して、<strong>バイリニア補間</strong>が正しく働くようにする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DDGI ＝ <strong>3D 格子のプローブを、毎フレームの少数のレイトレースで更新</strong>する<strong>動的 GI</strong>
    - [x] <strong>放射照度と距離</strong>を、<strong>プローブごとの八面体マップ</strong>に保存。<strong>時間的に混ぜて</strong>蓄積
    - [x] <strong>距離（平均・2 乗平均）</strong>から<strong>チェビシェフ</strong>で<strong>可視性</strong>を求め、<strong>ライト リーク</strong>を抑える
    - [x] <strong>動く光・物に追従</strong>。<strong>低周波のみ</strong>、<strong>DXR が必要</strong>
    - [x] <strong>更新の優先度・スリープ</strong>で<strong>コストを抑える</strong>

## 参考

- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019（DDGI）
- Majercik, Müller, Keller, Cline, McGuire, "Dynamic Diffuse Global Illumination Resampling", SIGGRAPH 2021 Talks
- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明の章）

## 関連ページ

- [Global Illumination (GI)](index.md)
- [Probe GI](probes/index.md)
- [Ray-Traced GI](rt-gi/index.md)
- [VSM, ESM and MSM](../shadows/vsm/index.md)
- [Ray-Traced Reflections](../reflections/rt-reflections/index.md)

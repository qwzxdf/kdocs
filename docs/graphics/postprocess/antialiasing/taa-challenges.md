---
title: TAA Challenges
tags:
  - 描画
---

# TAA Challenges

<strong>TAA は強力</strong>ですが、「過去のフレームを使う」という性質から、独特の失敗があります。ゴースト（残像）・全体のぼけ・細い物のちらつき・半透明やパーティクルの扱い・カットでの破綻などでどれも、TAA の品質を決める調整ポイントです。このページでは、それぞれの原因と対策、履歴クランプの改良（YCoCg・分散クリップ）・シャープ化・アップスケールとの統合を説明します。

!!! tip "ポイント"
    - TAA の失敗は<strong>「履歴が現在の内容と合わない」</strong>ことから起きる。
    - <strong>ゴースト</strong>：近傍クランプ・分散クリップ・速度の精度で抑える。
    - ぼけ：履歴の読み出し（バイリニアの繰り返し）が原因。バイキュービック・シャープ化で対処する。
    - 細い物のちらつき：1 画素より細い線がサンプルのずれで出入り。ジッターの調整・シャープ・描画側の工夫。
    - 半透明・パーティクル：速度や深度が無いので別扱い（TAA の後に描く、など）。
    - カット・露出の急変では履歴をリセット。

!!! info "このページを読む前に"
    - [Anti-Aliasing](index.md)（このセクション全体の地図と、読む順番）

## 問題と対策の一覧

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| <strong>ゴースト（残像）</strong> | 履歴が現在の内容と合わない（物の後ろから、背景が現れる） | 近傍クランプ・分散クリップ・速度の精度 |
| 全体のぼけ | バイリニアな履歴の読み出しを毎フレーム繰り返す | バイキュービック・シャープ化 |
| 細い物のちらつき | 1 画素以下の線がサンプルのずれで出入り | ジッターの調整・描画側で太くする |
| 半透明・パーティクル | 速度・深度が無い | TAA の後に描く・別の AA |
| 動きの速い物 | 速度バッファの精度不足 | 高精度の速度・近い深度の速度 |
| カメラのカット | 履歴が無効 | 履歴をリセット |
| 露出の急変 | 履歴と現在の明るさが違う | 露出の補正・リセット |

<!-- fig:taa-ghosting:begin -->

<svg class="fig illust motion" data-fig="taa-ghosting" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-taa-ghosting" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">TAA のゴースト: 混ぜる割合 α が小さいほど、滑らかだが、残像が長く残る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">明るい物が消えた画素。履歴の色が新しい色へ何フレームで置き換わるか。α を 0.5 → 0.2 → 0.1 → 0.05 で比べる</text>
<rect x="30" y="96" width="900" height="230" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 画素に残っている、消えた物の色(1 = 完全に残っている)</text>
<path d="M70.0,130.0 L90.5,215.0 L111.0,257.5 L131.5,278.75 L152.0,289.38 L172.5,294.69 L193.0,297.34 L213.5,298.67 L234.0,299.34 L254.5,299.67 L275.0,299.83 L295.5,299.92 L316.0,299.96 L336.5,299.98 L357.0,299.99 L377.5,299.99 L398.0,300.0 L418.5,300.0 L439.0,300.0 L459.5,300.0 L480.0,300.0 L500.5,300.0 L521.0,300.0 L541.5,300.0 L562.0,300.0 L582.5,300.0 L603.0,300.0 L623.5,300.0 L644.0,300.0 L664.5,300.0 L685.0,300.0 L705.5,300.0 L726.0,300.0 L746.5,300.0 L767.0,300.0 L787.5,300.0 L808.0,300.0 L828.5,300.0 L849.0,300.0 L869.5,300.0 L890.0,300.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<text x="886.0" y="293.9999999998454" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">α = 0.5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,130.0 L90.5,164.0 L111.0,191.2 L131.5,212.96 L152.0,230.37 L172.5,244.29 L193.0,255.44 L213.5,264.35 L234.0,271.48 L254.5,277.18 L275.0,281.75 L295.5,285.4 L316.0,288.32 L336.5,290.65 L357.0,292.52 L377.5,294.02 L398.0,295.21 L418.5,296.17 L439.0,296.94 L459.5,297.55 L480.0,298.04 L500.5,298.43 L521.0,298.75 L541.5,299.0 L562.0,299.2 L582.5,299.36 L603.0,299.49 L623.5,299.59 L644.0,299.67 L664.5,299.74 L685.0,299.79 L705.5,299.83 L726.0,299.87 L746.5,299.89 L767.0,299.91 L787.5,299.93 L808.0,299.94 L828.5,299.96 L849.0,299.96 L869.5,299.97 L890.0,299.98" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2265;0.2267;1.0000" values="0;0;1;1"/></path>
<text x="886.0" y="293.97740312407166" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">α = 0.2<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2265;0.2267;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,130.0 L90.5,147.0 L111.0,162.3 L131.5,176.07 L152.0,188.46 L172.5,199.62 L193.0,209.66 L213.5,218.69 L234.0,226.82 L254.5,234.14 L275.0,240.72 L295.5,246.65 L316.0,251.99 L336.5,256.79 L357.0,261.11 L377.5,265.0 L398.0,268.5 L418.5,271.65 L439.0,274.48 L459.5,277.04 L480.0,279.33 L500.5,281.4 L521.0,283.26 L541.5,284.93 L562.0,286.44 L582.5,287.8 L603.0,289.02 L623.5,290.11 L644.0,291.1 L664.5,291.99 L685.0,292.79 L705.5,293.51 L726.0,294.16 L746.5,294.75 L767.0,295.27 L787.5,295.74 L808.0,296.17 L828.5,296.55 L849.0,296.9 L869.5,297.21 L890.0,297.49" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3865;0.3867;1.0000" values="0;0;1;1"/></path>
<text x="886.0" y="291.4872498999561" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">α = 0.1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3865;0.3867;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,130.0 L90.5,138.5 L111.0,146.58 L131.5,154.25 L152.0,161.53 L172.5,168.46 L193.0,175.03 L213.5,181.28 L234.0,187.22 L254.5,192.86 L275.0,198.21 L295.5,203.3 L316.0,208.14 L336.5,212.73 L357.0,217.1 L377.5,221.24 L398.0,225.18 L418.5,228.92 L439.0,232.47 L459.5,235.85 L480.0,239.06 L500.5,242.1 L521.0,245.0 L541.5,247.75 L562.0,250.36 L582.5,252.84 L603.0,255.2 L623.5,257.44 L644.0,259.57 L664.5,261.59 L685.0,263.51 L705.5,265.34 L726.0,267.07 L746.5,268.72 L767.0,270.28 L787.5,271.77 L808.0,273.18 L828.5,274.52 L849.0,275.79 L869.5,277.0 L890.0,278.15" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5465;0.5467;1.0000" values="0;0;1;1"/></path>
<text x="886.0" y="272.15293338393246" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb" opacity="0">α = 0.05<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5465;0.5467;1.0000" values="0;0;1;1"/></text>
<line x1="70.0" y1="291.5" x2="890.0" y2="291.5" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="76.0" y="287.5" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">見えなくなる(5%)</text>
<rect x="30" y="346" width="900" height="130" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="336" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 何フレームで、見えなくなるか(60 fps なら、× 0.0167 秒)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="0;0;1;1"/><text x="50" y="394" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">α = 0.5</text>
<rect x="140" y="380" width="70.0" height="16" fill="#e5484d" opacity="0.85"/>
<text x="218.0" y="393" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">5 フレーム(0.08 秒)/ 半分まで 2 フレーム</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2709;0.2711;1.0000" values="0;0;1;1"/><text x="50" y="416" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">α = 0.2</text>
<rect x="140" y="402" width="196.0" height="16" fill="#e5aa28" opacity="0.85"/>
<text x="344.0" y="415" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">14 フレーム(0.23 秒)/ 半分まで 4 フレーム</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4309;0.4311;1.0000" values="0;0;1;1"/><text x="50" y="438" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">α = 0.1</text>
<rect x="140" y="424" width="406.0" height="16" fill="#2ea043" opacity="0.85"/>
<text x="554.0" y="437" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">29 フレーム(0.48 秒)/ 半分まで 7 フレーム</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5909;0.5911;1.0000" values="0;0;1;1"/><text x="50" y="460" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">α = 0.05</text>
<rect x="140" y="446" width="560.0" height="16" fill="#2563eb" opacity="0.85"/>
<text x="708.0" y="459" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">40 フレーム(0.67 秒)/ 半分まで 14 フレーム</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><rect x="620" y="490" width="310" height="36" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="636" y="514" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1e3a8a">小さい α は滑らか、でも、残像が長い</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">物が消えたあとも、履歴の色が少しずつ薄れながら、残る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">α が小さいほど、薄れるのが遅い<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ゴーストを抑えるには、α を速度に応じて上げる、履歴を押し込める、などを併用する<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:taa-ghosting:end -->

## ゴースト

<strong>ゴースト</strong>は、TAA の最も目立つ失敗です。物が動いたとき、その跡に前の絵が薄く残ります。

### 原因

画素 P に前フレームでは物 A が映っていて、今フレームでは背景 B が映る（物 A が動いて、背景が現れた）とします。履歴（A の色）をそのまま混ぜると、B の画素に A の色が残ります。

### 対策：近傍クランプの改良

| 方式 | 内容 | 特徴 |
| --- | --- | --- |
| 最小・最大クランプ | 周囲 3×3 の最小〜最大の範囲に押し込む | 基本・簡単。範囲が広すぎることがある |
| YCoCg でクランプ | 色を YCoCg に変換して、クランプ | 輝度と色度が分かれ、より自然 |
| 分散クリップ | 周囲の平均と標準偏差から範囲を決め、履歴を範囲の境界へ | 範囲が狭く、ゴーストに強い |
| 速度による履歴の拒否 | 速度が大きい画素は、履歴を減らす | 動く物のゴーストを抑える |
| 深度による拒否 | 前フレームの深度と大きく違えば、履歴を拒否 | 遮蔽が解除された所に強い |

```hlsl
float3 RGBToYCoCg(float3 c) {
  return float3(0.25 * c.r + 0.5 * c.g + 0.25 * c.b, 0.5 * c.r - 0.5 * c.b, -0.25 * c.r + 0.5 * c.g - 0.25 * c.b);
}

float3 ClipAabb(float3 aabb_min, float3 aabb_max, float3 history, float3 center) {
  float3 clip_center = 0.5 * (aabb_max + aabb_min);
  float3 clip_extent = 0.5 * (aabb_max - aabb_min) + 1e-5;
  float3 v = history - clip_center;
  float3 v_unit = v / clip_extent;
  float3 abs_unit = abs(v_unit);
  float max_unit = max(abs_unit.x, max(abs_unit.y, abs_unit.z));
  return max_unit > 1.0 ? clip_center + v / max_unit : history;
}
```

コードの要点です。`ClipAabb` は、履歴を範囲の「中心」へ向かって境界までクリップし、単純な `clamp` より色が自然になります。分散クリップでは、`aabb_min/max` を `平均 ± γ × 標準偏差`（γ ≒ 1.0〜1.25）で作ります。

## ぼけ

<strong>履歴をバイリニアで読む</strong>と画素の中間を読むたびに、少しぼけます。これを毎フレーム繰り返すと、画像全体がぼやけます。

履歴をバイリニアで読むと、画素の中間を読むたびに少しぼけます。これを毎フレーム繰り返すと、画像全体がぼやけます。対策は、バイキュービック（Catmull-Rom）で履歴を読む（9 タップを 5 タップに削る最適化があります）、TAA の後に軽いシャープ フィルタ（アンシャープ マスクや CAS）を掛ける、ブレンド率を調整する（現在の比率を上げるとぼけは減りますが、ちらつきが増えます）、の 3 つです。

```hlsl
float3 Sharpen(float3 center, float3 blurred, float strength) {
  return center + (center - blurred) * strength;
}
```

## 細い物のちらつき

<strong>電線・フェンス・遠くの細い線は、1 画素より細い</strong>ため、サンプルの位置次第で出たり消えたりします。TAA が平均して、ある程度は抑えますが完全には消えません。

| 対策 | 内容 |
| --- | --- |
| ジッターの列を調整 | Halton の周期を伸ばす（8 → 16） |
| 描画側で細い物を太くする | 距離に応じて、最小の太さを保つ（ジオメトリ） |
| コンサバティブ ラスタライズ | 細い物を確実に画素に当てる |
| シャープ化を弱める | シャープはちらつきを強調する |

## 半透明・パーティクル

<strong>半透明やパーティクルには、深度・速度が書かれない</strong>ことが多く、TAA の再投影がうまく働きません。

半透明やパーティクルには、深度や速度が書かれないことが多く、TAA の再投影がうまく働きません。対応は 3 通りです。TAA の後に描き、AA 済みの画像の上に重ねる方法（自身は AA されません）。半透明も速度と深度を書いて TAA に参加させる方法（複雑です）。ディザリングで半透明を表現し、ノイズ的な透け具合を TAA で平均して滑らかにする方法です。

## カットとリセット

<strong>カメラの瞬間移動・カット・場面転換では履歴が完全に無効</strong>です。

カメラの瞬間移動・カット・場面転換では、履歴が完全に無効になります。カットでは履歴を捨てます（ブレンド率 1.0）。露出の急変では、履歴と現在で露出を揃えるか、リセットします。解像度を変えたときは、履歴を作り直します。

## アップスケールとの統合

<strong>TAA の発展形</strong>が低解像度で描き、時間的に蓄積しながら、高解像度に拡大する TAAU・TSR・FSR 2・DLSS です。ジッターと履歴により、元の画素数より多くの情報を取り出します。

TAA の発展形として、低解像度で描き、時間的に蓄積しながら、高解像度に拡大する方式があります。ジッターと履歴によって、元の画素数より多くの情報を取り出します。TAAU・TSR はエンジン内蔵の時間的アップスケール、FSR 2/3 は AMD のオープンな実装、DLSS は NVIDIA のニューラル ネットワークによる実装です。

詳しい運用は[TAA とアップスケール（最適化）](../../../rendering/taa-upscaling.md)を参照してください。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| YCoCg ＋ 分散クリップ | ゴーストを大きく減らす |
| バイキュービックで履歴を読む＋シャープ | ぼけを抑える |
| 速度の精度を確保 | R16G16、動く物体の速度を正しく（[Velocity Buffer](../motion-blur/velocity-buffer.md)） |
| 深度・速度の不一致で履歴を拒否 | 遮蔽解除に強い |
| 半透明は TAA の後 | シンプルで安全 |
| 履歴のリセットを用意 | カット・露出急変・解像度変更 |

## よくあるミス

??? failure "動く物体の後ろに、長く残像が尾を引く"
    <strong>クランプが弱い</strong>。分散クリップ・速度による拒否を入れる。

??? failure "TAA を入れたら、全体がぼやけた"
    バイリニアの履歴が原因。バイキュービック ＋ シャープ化。

??? failure "パーティクルが TAA で二重に見える"
    パーティクルは、TAA の後に描く。

??? failure "カット直後に前のシーンが一瞬残る"
    履歴をリセットする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] TAA の失敗は<strong>「履歴が現在と合わない」</strong>ことから起きる
    - [x] ゴーストはクランプ（YCoCg・分散クリップ）・速度/深度の拒否で抑える
    - [x] ぼけはバイキュービックの履歴読み出し ＋ シャープ化
    - [x] 半透明・パーティクルは TAA の後が基本
    - [x] カット・露出の急変で履歴をリセット

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Salvi, "An Excursion in Temporal Supersampling"（GDC 2016）
- Pedersen, "Temporal Reprojection Anti-Aliasing in INSIDE"（GDC 2016）

## 関連ページ

- [Anti-Aliasing](index.md)
- [TAA](taa.md)
- [Comparison and Choosing](comparison.md)
- [TAA・アップスケーラ・VRS](../../../rendering/taa-upscaling.md)

---
title: TAA Challenges
tags:
  - 描画
---

# TAA Challenges

**TAA は強力**ですが、<strong>「過去のフレームを使う」</strong>という**性質**から、**独特の失敗**があります。**ゴースト（残像）・全体のぼけ・細い物のちらつき・半透明やパーティクルの扱い・カットでの破綻**などで**どれも、TAA の品質を決める調整ポイント**です。このページでは、**それぞれの原因と対策**、**履歴クランプの改良（YCoCg・分散クリップ）・シャープ化・アップスケールとの統合**を説明します。

!!! tip "ポイント"
    - TAA の失敗は<strong>「履歴が現在の内容と合わない」</strong>ことから起きる。
    - <strong>ゴースト</strong>：<strong>近傍クランプ・分散クリップ・速度の精度</strong>で抑える。
    - <strong>ぼけ</strong>：<strong>履歴の読み出し（バイリニアの繰り返し）</strong>が原因。<strong>バイキュービック・シャープ化</strong>で対処。
    - <strong>細い物のちらつき</strong>：<strong>1 画素より細い線</strong>が<strong>サンプルのずれで出入り</strong>。<strong>ジッターの調整・シャープ・描画側の工夫</strong>。
    - <strong>半透明・パーティクル</strong>：<strong>速度や深度が無い</strong>ので<strong>別扱い</strong>（TAA の後に描く、など）。
    - <strong>カット・露出の急変</strong>では<strong>履歴をリセット</strong>。

## 問題と対策の一覧

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| <strong>ゴースト（残像）</strong> | **履歴が現在の内容と合わない**（**物の後ろから、背景が現れる**） | **近傍クランプ・分散クリップ・速度の精度** |
| **全体のぼけ** | **バイリニアな履歴の読み出しを、毎フレーム繰り返す** | **バイキュービック・シャープ化** |
| **細い物のちらつき** | **1 画素以下の線がサンプルのずれで出入り** | **ジッターの調整・描画側で太くする** |
| **半透明・パーティクル** | **速度・深度が無い** | **TAA の後に描く・別の AA** |
| **動きの速い物** | **速度バッファの精度不足** | **高精度の速度・近い深度の速度** |
| **カメラのカット** | **履歴が無効** | **履歴をリセット** |
| **露出の急変** | **履歴と現在の明るさが違う** | **露出の補正・リセット** |

<!-- fig:taa-ghosting:begin -->

<svg class="fig illust motion" data-fig="taa-ghosting" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-taa-ghosting" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ゴースト:動く物体の後ろに、古い履歴が尾を引く</text>
<text x="40" y="94" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">履歴の拒否なし</text>
<rect x="40" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="64" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="88" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="112" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="136" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="160" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="184" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="208" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="232" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="256" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="280" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="304" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="328" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="352" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="40" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1348;0.4130;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="64" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1344;0.1348;0.1826;0.4609;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="88" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1823;0.1826;0.2304;0.5087;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="112" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2301;0.2304;0.2783;0.5565;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="136" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.3261;0.6043;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="160" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3257;0.3261;0.3739;0.6522;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="184" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3736;0.3739;0.4217;0.7000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="208" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4214;0.4217;0.4696;0.7478;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="232" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;0.5174;0.7957;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="256" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5170;0.5174;0.5652;0.8435;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="280" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5649;0.5652;0.6130;0.8913;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="304" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6127;0.6130;0.6609;0.9391;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="328" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6605;0.6609;0.7087;0.9870;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="352" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7083;0.7087;0.7565;1.0000" values="0;0;1;1;0"/></rect>
<text x="420" y="94" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">拒否あり（クランプ・速度）</text>
<rect x="420" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="444" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="468" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="492" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="516" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="540" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="564" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="588" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="612" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="636" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="660" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="684" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="708" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="732" y="120" width="23" height="48" fill="#f1f5f9"/>
<rect x="420" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1344;0.1348;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="444" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1344;0.1348;0.1823;0.1826;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="468" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1823;0.1826;0.2301;0.2304;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="492" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2301;0.2304;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="516" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.3257;0.3261;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="540" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3257;0.3261;0.3736;0.3739;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="564" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3736;0.3739;0.4214;0.4217;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="588" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4214;0.4217;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="612" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;0.5170;0.5174;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="636" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5170;0.5174;0.5649;0.5652;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="660" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5649;0.5652;0.6127;0.6130;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="684" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6127;0.6130;0.6605;0.6609;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="708" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6605;0.6609;0.7083;0.7087;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="732" y="120" width="23" height="48" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7083;0.7087;0.7562;0.7565;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="40" y="230" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">物体が右へ動く(1 マス / フレーム)<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="270" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">左:通ったマスに、薄い影が残る（履歴を捨てない）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="1;1;0;0"/></text>
<text x="40" y="270" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">→ 長い尾が見える（ゴースト）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="270" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">右:履歴が合わなければ捨てる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="1;1;0;0"/></text>
<text x="420" y="270" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">→ 尾が出ない<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="330" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">対策:近傍クランプ・速度による再投影・深度や法線での拒否。</text>
</svg>

<!-- fig:taa-ghosting:end -->

## ゴースト

**ゴースト**は、**TAA の最も目立つ失敗**です。**物が動いたとき、その跡に前の絵が薄く残ります**。

### 原因

**画素 P に前フレームでは物 A が映っていて、今フレームでは背景 B が映る**（**物 A が動いて、背景が現れた**）とします。**履歴（A の色）をそのまま混ぜると、B の画素に A の色が残ります**。

### 対策：近傍クランプの改良

| 方式 | 内容 | 特徴 |
| --- | --- | --- |
| **最小・最大クランプ** | **周囲 3×3 の最小〜最大の範囲に押し込む** | **基本・簡単。範囲が広すぎることがある** |
| **YCoCg でクランプ** | **色を YCoCg に変換して、クランプ** | **輝度と色度が分かれ、より自然** |
| **分散クリップ** | **周囲の平均と標準偏差から範囲を決め、履歴を範囲の境界へ** | **範囲が狭く、ゴーストに強い** |
| **速度による履歴の拒否** | **速度が大きい画素は、履歴を減らす** | **動く物のゴーストを抑える** |
| **深度による拒否** | **前フレームの深度と大きく違えば、履歴を拒否** | **遮蔽が解除された所に強い** |

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

コードの要点です。`ClipAabb` は、履歴を範囲の「中心」へ向かって境界までクリップし、単純な `clamp` より色が自然になります。分散クリップでは、`aabb_min/max` を、`平均 ± γ × 標準偏差`（γ ≒ 1.0〜1.25）で作ります。

## ぼけ

**履歴をバイリニアで読む**と**画素の中間を読むたびに、少しぼけます**。**これを毎フレーム繰り返す**と、**画像全体がぼやけます**。

履歴をバイリニアで読むと、画素の中間を読むたびに少しぼけます。これを毎フレーム繰り返すと、画像全体がぼやけます。対策は、バイキュービック（Catmull-Rom）で履歴を読む（9 タップを 5 タップに削る最適化があります）、TAA の後に軽いシャープ フィルタ（アンシャープ マスクや CAS）を掛ける、ブレンド率を調整する（現在の比率を上げるとぼけは減りますが、ちらつきが増えます）、の 3 つです。

```hlsl
float3 Sharpen(float3 center, float3 blurred, float strength) {
  return center + (center - blurred) * strength;
}
```

## 細い物のちらつき

**電線・フェンス・遠くの細い線は、1 画素より細い**ため、**サンプルの位置次第で出たり消えたり**します。**TAA が平均して、ある程度は抑えますが完全には消えません**。

| 対策 | 内容 |
| --- | --- |
| **ジッターの列を調整** | <strong>Halton の周期を伸ばす（8 → 16）</strong> |
| **描画側で細い物を太くする** | <strong>距離に応じて、最小の太さを保つ（ジオメトリ）</strong> |
| **コンサバティブ ラスタライズ** | **細い物を確実に画素に当てる** |
| **シャープ化を弱める** | **シャープはちらつきを強調する** |

## 半透明・パーティクル

**半透明やパーティクルには、深度・速度が書かれない**ことが**多く**、**TAA の再投影がうまく働きません**。

半透明やパーティクルには、深度や速度が書かれないことが多く、TAA の再投影がうまく働きません。対応は 3 通りです。TAA の後に描き、AA 済みの画像の上に重ねる方法（自身は AA されません）。半透明も速度と深度を書いて TAA に参加させる方法（複雑です）。ディザリングで半透明を表現し、ノイズ的な透け具合を TAA で平均して滑らかにする方法です。

## カットとリセット

**カメラの瞬間移動・カット・場面転換では履歴が完全に無効**です。

カメラの瞬間移動・カット・場面転換では、履歴が完全に無効になります。カットでは履歴を捨てます（ブレンド率 1.0）。露出の急変では、履歴と現在で露出を揃えるか、リセットします。解像度を変えたときは、履歴を作り直します。

## アップスケールとの統合

**TAA の発展形**が**低解像度で描き、時間的に蓄積しながら、高解像度に拡大する TAAU・TSR・FSR 2・DLSS** です。**ジッターと履歴により、元の画素数より多くの情報を取り出します**。

TAA の発展形として、低解像度で描き、時間的に蓄積しながら、高解像度に拡大する方式があります。ジッターと履歴によって、元の画素数より多くの情報を取り出します。TAAU・TSR はエンジン内蔵の時間的アップスケール、FSR 2/3 は AMD のオープンな実装、DLSS は NVIDIA のニューラル ネットワークによる実装です。

詳しい運用は[TAA とアップスケール（最適化）](../../../rendering/taa-upscaling.md)を参照してください。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **YCoCg ＋ 分散クリップ** | **ゴーストを大きく減らす** |
| **バイキュービックで履歴を読む＋シャープ** | **ぼけを抑える** |
| **速度の精度を確保** | **R16G16、動く物体の速度を正しく**（[速度バッファ](../motion-blur/velocity-buffer.md)） |
| **深度・速度の不一致で履歴を拒否** | **遮蔽解除に強い** |
| **半透明は TAA の後** | **シンプルで安全** |
| **履歴のリセットを用意** | **カット・露出急変・解像度変更** |

## よくあるミス

??? failure "動く物体の後ろに、長く残像が尾を引く"
    **クランプが弱い**。**分散クリップ・速度による拒否**を入れる。

??? failure "TAA を入れたら、全体がぼやけた"
    **バイリニアの履歴が原因**。**バイキュービック ＋ シャープ化**。

??? failure "パーティクルが、TAA で二重に見える"
    **パーティクルは、TAA の後に描く**。

??? failure "カット直後に、前のシーンが一瞬残る"
    **履歴をリセット**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] TAA の失敗は<strong>「履歴が現在と合わない」</strong>ことから起きる
    - [x] <strong>ゴースト</strong>は<strong>クランプ（YCoCg・分散クリップ）・速度/深度の拒否</strong>で抑える
    - [x] <strong>ぼけ</strong>は<strong>バイキュービックの履歴読み出し ＋ シャープ化</strong>
    - [x] <strong>半透明・パーティクルは TAA の後</strong>が<strong>基本</strong>
    - [x] <strong>カット・露出の急変で履歴をリセット</strong>

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Salvi, "An Excursion in Temporal Supersampling"（GDC 2016）
- Pedersen, "Temporal Reprojection Anti-Aliasing in INSIDE"（GDC 2016）

## 関連ページ

- [Anti-Aliasing](index.md)
- [TAA](taa.md)
- [Comparison and Choosing](comparison.md)
- [TAA とアップスケール（最適化）](../../../rendering/taa-upscaling.md)

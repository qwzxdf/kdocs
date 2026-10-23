---
title: Tuning the Look
tags:
  - 描画
---

# Tuning the Look

<strong>光の筋は強すぎるとわざとらしく見えます</strong>。強さ・色・ノイズを調整して、自然にします。このページでは見た目の調整を説明します。

!!! tip "ポイント"
    - 強さは控えめに。
    - 色は太陽の色に合わせる。
    - ノイズで筋にむらを付ける。
    - 天気（晴れ・霧）で、強さを変える。

!!! info "このページを読む前に"
    - [God Rays](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 見た目の調整
| パラメータ | 影響 |
| --- | --- |
| 霧の密度 | 濃いほど光の筋が強い |
| 位相関数の g | 大きいほど、太陽の方向でだけ見える |
| 光の強さ | HDR で強く、ブルームで光らせる |
| 色 | 朝夕は暖色、昼は白、水中は青緑 |
| ノイズ・風 | 揺らぎを足す |
| カメラが太陽側へ向くとき強く | 前方散乱 |

### 自然に見せる考え方

光の筋は目立つ効果なのでやりすぎると「いかにも CG」になります。自然に見せるコツを挙げます。

第 1 に <strong>強さは控えめに</strong>します。実際の光の筋はよほど霧が濃い日か、ほこりの多い室内でないとはっきりは見えません。普段は「あることに気づく程度」の薄さにし、特別な場面（教会のステンドグラス、森の朝、洞窟の天井の穴）でだけ強調します。

第 2 に 天気に連動させます。晴れた乾燥した日は筋がほとんど出ず、湿度の高い朝や雨上がりに強く出る、といった差をつけると場面ごとの雰囲気を作れます。霧の密度のパラメータを天気システムに接続するだけで実現できます。

第 3 に 筋に濃淡の揺らぎを付けます。均一な筋は人工的に見えます。ノイズ テクスチャ（雲の影や風で流れるほこり）を密度に掛けると、筋が自然に揺らぎます。

第 4 に 色を太陽に合わせます。朝夕は低い角度で大気を長く通るので、赤みを帯びた筋になります。昼は白、曇りの日は灰色にします。

<!-- fig:decay-weights:begin -->

<svg class="fig illust motion" data-fig="decay-weights" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-decay-weights" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">放射ぼかしの減衰(decay): 1 に近いほど、遠くの光も効いて、筋が長く伸びる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">光源から 64 画素の線。各画素が、光源の方向へ 32 回読んで、decay^i の重みで足す。光源だけが明るいときの、筋の明るさ</text>
<rect x="30" y="96" width="640" height="260" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 光源からの距離と、筋の明るさ</text>
<path d="M70.0,259.77 L78.89,259.77 L87.78,271.62 L96.67,287.7 L105.56,311.64 L114.44,319.37 L123.33,322.53 L132.22,324.26 L141.11,325.57 L150.0,326.19 L158.89,326.82 L167.78,327.18 L176.67,327.64 L185.56,328.0 L194.44,328.0 L203.33,328.39 L212.22,328.39 L221.11,328.39 L230.0,328.62 L238.89,328.74 L247.78,328.74 L256.67,328.74 L265.56,329.01 L274.44,329.01 L283.33,329.01 L292.22,329.01 L301.11,329.11 L310.0,329.11 L318.89,329.3 L327.78,329.3 L336.67,329.3 L345.56,329.3 L354.44,329.3 L363.33,329.3 L372.22,329.3 L381.11,329.3 L390.0,329.3 L398.89,329.3 L407.78,329.3 L416.67,329.48 L425.56,329.48 L434.44,329.48 L443.33,329.48 L452.22,329.57 L461.11,329.57 L470.0,329.57 L478.89,329.57 L487.78,329.57 L496.67,329.57 L505.56,329.57 L514.44,329.57 L523.33,329.57 L532.22,329.57 L541.11,329.57 L550.0,329.57 L558.89,329.57 L567.78,329.57 L576.67,329.57 L585.56,329.57 L594.44,329.57 L603.33,329.57 L612.22,329.57 L621.11,329.57 L630.0,329.57" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<text x="626.0" y="319.568411794902" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">decay 0.90<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,212.73 L78.89,212.73 L87.78,229.02 L96.67,250.73 L105.56,282.23 L114.44,296.71 L123.33,304.03 L132.22,308.59 L141.11,312.45 L150.0,314.39 L158.89,316.58 L167.78,317.75 L176.67,319.44 L185.56,320.83 L194.44,320.83 L203.33,322.39 L212.22,322.39 L221.11,322.39 L230.0,323.35 L238.89,323.87 L247.78,323.87 L256.67,323.87 L265.56,325.09 L274.44,325.09 L283.33,325.09 L292.22,325.09 L301.11,325.58 L310.0,325.58 L318.89,326.45 L327.78,326.45 L336.67,326.45 L345.56,326.45 L354.44,326.45 L363.33,326.45 L372.22,326.45 L381.11,326.45 L390.0,326.45 L398.89,326.45 L407.78,326.45 L416.67,327.27 L425.56,327.27 L434.44,327.27 L443.33,327.27 L452.22,327.74 L461.11,327.74 L470.0,327.74 L478.89,327.74 L487.78,327.74 L496.67,327.74 L505.56,327.74 L514.44,327.74 L523.33,327.74 L532.22,327.74 L541.11,327.74 L550.0,327.74 L558.89,327.74 L567.78,327.74 L576.67,327.74 L585.56,327.74 L594.44,327.74 L603.33,327.74 L612.22,327.74 L621.11,327.74 L630.0,327.74" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;1.0000" values="0;0;1;1"/></path>
<text x="626.0" y="317.7366985098959" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">decay 0.95<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,179.06 L78.89,179.06 L87.78,197.76 L96.67,222.67 L105.56,258.46 L114.44,277.16 L123.33,287.35 L132.22,294.02 L141.11,299.88 L150.0,302.91 L158.89,306.46 L167.78,308.32 L176.67,311.12 L185.56,313.47 L194.44,313.47 L203.33,316.13 L212.22,316.13 L221.11,316.13 L230.0,317.77 L238.89,318.7 L247.78,318.7 L256.67,318.7 L265.56,320.88 L274.44,320.88 L283.33,320.88 L292.22,320.88 L301.11,321.79 L310.0,321.79 L318.89,323.34 L327.78,323.34 L336.67,323.34 L345.56,323.34 L354.44,323.34 L363.33,323.34 L372.22,323.34 L381.11,323.34 L390.0,323.34 L398.89,323.34 L407.78,323.34 L416.67,324.84 L425.56,324.84 L434.44,324.84 L443.33,324.84 L452.22,325.71 L461.11,325.71 L470.0,325.71 L478.89,325.71 L487.78,325.71 L496.67,325.71 L505.56,325.71 L514.44,325.71 L523.33,325.71 L532.22,325.71 L541.11,325.71 L550.0,325.71 L558.89,325.71 L567.78,325.71 L576.67,325.71 L585.56,325.71 L594.44,325.71 L603.33,325.71 L612.22,325.71 L621.11,325.71 L630.0,325.71" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4398;0.4400;1.0000" values="0;0;1;1"/></path>
<text x="626.0" y="315.713176417319" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">decay 0.97<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4398;0.4400;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,130.0 L78.89,130.0 L87.78,151.6 L96.67,180.51 L105.56,221.67 L114.44,245.9 L123.33,260.09 L132.22,269.76 L141.11,278.64 L150.0,283.33 L158.89,289.07 L167.78,291.99 L176.67,296.55 L185.56,300.49 L194.44,300.49 L203.33,304.99 L212.22,304.99 L221.11,304.99 L230.0,307.79 L238.89,309.43 L247.78,309.43 L256.67,309.43 L265.56,313.28 L274.44,313.28 L283.33,313.28 L292.22,313.28 L301.11,314.91 L310.0,314.91 L318.89,317.65 L327.78,317.65 L336.67,317.65 L345.56,317.65 L354.44,317.65 L363.33,317.65 L372.22,317.65 L381.11,317.65 L390.0,317.65 L398.89,317.65 L407.78,317.65 L416.67,320.37 L425.56,320.37 L434.44,320.37 L443.33,320.37 L452.22,321.98 L461.11,321.98 L470.0,321.98 L478.89,321.98 L487.78,321.98 L496.67,321.98 L505.56,321.98 L514.44,321.98 L523.33,321.98 L532.22,321.98 L541.11,321.98 L550.0,321.98 L558.89,321.98 L567.78,321.98 L576.67,321.98 L585.56,321.98 L594.44,321.98 L603.33,321.98 L612.22,321.98 L621.11,321.98 L630.0,321.98" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6265;0.6267;1.0000" values="0;0;1;1"/></path>
<text x="626.0" y="311.98491089582865" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb" opacity="0">decay 0.99<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6265;0.6267;1.0000" values="0;0;1;1"/></text>
<line x1="70.0" y1="325.35" x2="630.0" y2="325.35" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="76.0" y="321.35" text-anchor="start" style="font-size:10px;font-weight:700;fill:#64748b">見えなくなる(0.02)</text>
<rect x="690" y="96" width="240" height="260" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="690" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">筋が届く距離(画素)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="0;0;1;1"/><text x="706" y="136" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">decay 0.90</text>
<text x="706" y="160" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d">7 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;1.0000" values="0;0;1;1"/><text x="706" y="188" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">decay 0.95</text>
<text x="706" y="212" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5aa28">25 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4754;0.4756;1.0000" values="0;0;1;1"/><text x="706" y="240" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">decay 0.97</text>
<text x="706" y="264" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043">42 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6620;0.6622;1.0000" values="0;0;1;1"/><text x="706" y="292" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">decay 0.99</text>
<text x="706" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb">63 画素</text>
</g>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">筋が届く距離:</text>
<text x="180" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="1;1;0;0"/></text>
<text x="180" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">7<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;0.2887;0.2889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">25<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;0.4754;0.4756;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">42<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4754;0.4756;0.6620;0.6622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">63<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6620;0.6622;1.0000" values="0;0;1;1"/></text>
<text x="230" y="396" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">画素</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7998;0.8000;1.0000" values="0;0;1;1"/><rect x="40" y="430" width="880" height="76" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="454" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">decay 0.90 → 0.99 で、筋が届く距離が 7 → 63 画素</text>
<text x="56" y="478" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">重み decay^i は、遠くを読むほど小さい。1 に近いと、遠くの光源の光も、そのまま混ざって、筋が長い</text>
<text x="56" y="500" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">伸ばしすぎると、画面全体が白っぽくぼける。強さ(weight)と一緒に調整する</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くを読んだ分の重みを、decay の累乗で、弱めていく<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">decay が 1 に近いほど、筋が、遠くまで伸びる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8132;0.8133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">伸ばしすぎず、見た目で決める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8132;0.8133;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:decay-weights:end -->

## 調整のパラメーター

ゴッド レイは <strong>強すぎると画面が白く、もやもや</strong>し 弱すぎると見えません。主要なパラメーターの意味と効き方を、整理します。

| パラメーター | 意味 | 大きくすると | 目安 |
| --- | --- | --- | --- |
| 強さ（intensity） | 光の筋の、明るさ | 明るく画面が白っぽく | 0.1〜1 |
| 密度（density） | 放射状ブラーで、どこまで遠くを読むか | 筋が、長く伸びる | 0.5〜1 |
| 減衰（decay） | 遠くの、サンプルの重み（読むたびに掛ける） | 筋が、遠くまで（1 に近い） | 0.95〜0.99 |
| 重み（weight） | 1 回の、サンプルの寄与 | 全体が明るく | 0.01〜0.1 |
| 位相関数の `g` | 太陽の方向への、偏り | 太陽の近くだけが明るく | 0.6〜0.9 |
| 霧の密度 | 散乱する粒子の、濃さ | 筋がはっきり（濃い霧で、強く） | 場面による |
| サンプル数 | 放射状ブラー / レイマーチの、読み込み回数 | なめらか（ノイズ・縞が、減る） | 32〜64 |

## 見た目を決める 3 つの考え方

### ① 太陽の方向を強調する

光の筋は <strong>太陽の方を見たとき</strong>に 最も、はっきり見えます（前方散乱）。太陽に背を向けたときはほぼ見えません。位相関数（[Phase Functions](../scattering/phase-function.md)）と、視線と太陽の角度で強さを変えます。

```hlsl
// 太陽を、向いているほど、強く。背を向けたら、ほぼ 0。
float facing = saturate(dot(g_camera_forward, g_sun_dir));
float strength = g_intensity * pow(facing, 2.0);
```

### ② 色を太陽に合わせる

光の筋の色は 太陽の色（大気を通った後の、色）です。昼は白〜淡い黄色、朝夕は橙〜赤。空の青を使うと筋が見えません（青い光の筋は、不自然）。

```hlsl
float3 ray_color = SunColorAtGround(g_sun_dir) * g_intensity;       // 大気の透過率を、掛けた、太陽の色
```

### ③ 時間帯で強さを変える

| 時間帯 | 光の筋 |
| --- | --- |
| 正午（太陽が高い） | 弱い（光がほぼ、真上から筋が短い。空気も澄んでいる） |
| 朝・夕（太陽が低い） | 強い（光が斜めに長く通る。霧・もやも多い） |
| 夜 | なし（太陽が地平線の下） |

ゴッド レイが最も美しいのは、朝夕です。太陽の高さに応じて強さを、変えると時間帯の雰囲気がぐっと、増します。

```hlsl
float sun_height = g_sun_dir.y;                                       // 1 = 真上、0 = 地平線
float time_of_day_factor = lerp(1.0, 0.3, saturate(sun_height * 2.0));   // 低いほど、強く
```

## 品質を損なう問題

| 症状 | 原因 | 対策 |
| --- | --- | --- |
| 縞（バンディング） | サンプル数が、少ない | ジッター（ノイズで、開始位置をずらす）+ TAA。サンプル数を増やす |
| 画面全体が白くもやもや | 強さが、強すぎる重み・減衰の設定 | 強さを、下げる。しきい値で明るい部分だけを、光源に |
| 筋が画面の端で途切れる | 放射状ブラーの起点が、画面の外 | 起点が画面の外でも計算し端で、フェード |
| 太陽の周りに四角いアーティファクト | 低解像度の、マスクの補間 | マスクをバイラテラルで、アップサンプル、解像度を上げる |
| 筋がちらつく | TAA の履歴が、不安定 | 履歴のクランプ（[Cloud Temporal Reprojection](../clouds/temporal.md)） |
| 木の葉の隙間がざらざら | アルファ テストの、ジャギー | 光のマスクをぼかしてから、放射状ブラーへ |

## ブルームと組み合わせる

<strong>まぶしい</strong>、光の筋は ブルーム（[Bloom](../../postprocess/bloom/index.md)）と一緒に使うと、映えます。ゴッド レイを足した後にブルームを、かけます。

```text
シーン + ゴッド レイ（加算） → ブルーム → トーン マッピング
```

## 目的に合わせた設定

| 目的 | 設定の方向性 |
| --- | --- |
| 自然な控えめな光の筋 | 強さ 小、霧の密度は場面の霧に合わせる、位相関数 `g` = 0.7 |
| ドラマチックな演出（神殿、洞窟） | 強さ 大、局所的な霧（その場所だけ濃く）、筋の方向を固定 |
| スタイライズ（アニメ調） | くっきりした、筋（ぼかしを弱く）、色を暖色に強め |

## よくあるミス

??? failure "光の筋が強すぎて、画面が白っぽい"
    <strong>強さを下げる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 控えめな強さと、ノイズのむら

## 参考

- Mitchell, "Volumetric Light Scattering as a Post-Process", GPU Gems 3, Chapter 13, 2007（放射状ブラーによる、光の筋）
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [God Rays](index.md)
- [Bloom](../../postprocess/bloom/index.md)

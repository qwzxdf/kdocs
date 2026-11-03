---
title: Upscaler Comparison
tags:
  - 描画
---

# Upscaler Comparison

FSR・DLSS・XeSS は入力もジッターも似ているので、1 つに対応したコードは他の 2 つにも使い回せそうに見えます。ところが、同じ名前のプリセットで倍率が違ったりミップ バイアスの式が違ったり動きベクトルの扱いを決めるフラグの名前が違ったりします。ここでは、それぞれの公式資料を読んで値を横に並べました。数値を決め打ちして使い回すと他の SDK で食い違うので、SDK の関数か式で出すための確認に使ってください。

!!! tip "ポイント"
    - プリセットの名前は同じでも倍率は同じとは限りません。XeSS の Quality は 1.7 倍で、FSR と DLSS の Quality は 1.5 倍です。
    - ミップ バイアスは XeSS が `log2(描画 / 出力)` で、FSR 2 と DLSS はそこからさらに 1.0 を引きます。
    - 位相数の目安は 3 社とも `8 × 倍率²` で、端数の扱いだけが違います。
    - 動きベクトルの向き（現在 → 前）とジッターの範囲（±0.5）は共通です。ジッターを動きベクトルに含めるかだけは、DLSS がフラグで選べます。
    - 呼び出す位置は 3 社ともトーン マッピングの前です。

!!! info "このページを読む前に"
    - [Upscaling](index.md)（共通の考え方と入力）
    - [FSR](fsr.md)、[DLSS](dlss.md)、[XeSS](xess.md)（各社の詳細と読んだ資料の範囲）

## 倍率 {#scale}

表の「FSR 3」の列は、FSR 3 の紹介ページの値です。そのほかの表の「FSR 2」の列は、FSR 2 の README の値で、FSR 3 のアップスケールが同じ入力を求めるかは、読んだ範囲では確かめていません（紹介ページは、組み込みが FSR 2 に似ていると書いています）。

倍率は出力の幅を描画の幅で割った値です。名前が同じでも会社で値が違います。

| プリセット | FSR 3 | DLSS | XeSS（1.3 以降） |
| --- | --- | --- | --- |
| Native AA（DLAA） | 1.0 | 1.0 | 1.0 |
| Ultra Quality Plus | なし | なし | 1.3 |
| Ultra Quality | なし | なし | 1.5 |
| Quality | 1.5 | 1.5 | 1.7 |
| Balanced | 1.7 | 1.724 | 2.0 |
| Performance | 2.0 | 2.0 | 2.3 |
| Ultra Performance | 3.0 | 3.0 | 3.0 |

XeSS は 1.3 より前の版で別の倍率を使っていました（Quality が 1.5、Balanced が 1.7、Performance が 2.0）。古い倍率に戻したいときは `xessForceLegacyScaleFactors` で切り替えます。

この表から設定画面に「Quality」と出したとき同じ画質を期待されると食い違うことがわかります。たとえば 4K 出力で XeSS の Quality は約 2259×1271、FSR の Quality は 2560×1440 で描きます。ゲームの設定に倍率や描画解像度を併記するか GPU ごとに既定のモードを決めるときに、この差を考えます。

## ジッターの位相数 {#phases}

位相数は `8 × 倍率²` が目安です。端数の扱いは資料で少し違います。

| 倍率 | 8 × 倍率² | FSR 2 | DLSS（最小） |
| --- | --- | --- | --- |
| 1.5 | 18.0 | 18 | 18 |
| 1.7（DLSS は 1.724） | 23.1 | 23 | 24 |
| 2.0 | 32.0 | 32 | 32 |
| 3.0 | 72.0 | 72 | 72 |

FSR 2 の README は独自の倍率 n に対して `ceil(8 × n²)` を使うと書いています。DLSS のガイドは倍率ごとの最小値を表で示しています。XeSS のガイドは基準の長さに `(出力の幅 / 描画の幅)²` を掛けるという式で、基準が 8 なら 3.0 倍で 72 になります（8 × 9）。XeSS の資料には倍率ごとの表がありません。

3 社とも SDK の関数か式で出す前提です。FSR 2 には `ffxFsr2GetJitterPhaseCount` があります。

## ミップ バイアス {#mip-bias}

低解像度で描くとテクスチャが粗く見えるので、ミップ レベルを細かい側へずらします。式が会社で違います。

```cpp
// 描画の幅 / 出力の幅 を r とする。r < 1 なので log2(r) は負になる。
float r = static_cast<float>(render_width) / output_width;

// XeSS: log2(r) だけ。倍率 2.0 なら -1。
float xess = std::log2(r);

// FSR 2: log2(r) からさらに 1.0 を引く。倍率 2.0 なら -2。
float fsr2 = std::log2(r) - 1.0f;

// DLSS: ネイティブ描画時のバイアスを足し、log2(r) - 1.0 に ε を加える。
// ε は素材ごとの調整用（既定は 0）。native_bias は、DLSS を使わないときのバイアス。
float dlss = native_bias + std::log2(r) - 1.0f + epsilon;
```

倍率ごとの値は次のとおりです。native_bias と ε は 0 とします。

| 倍率 | XeSS | FSR 2 | DLSS |
| --- | --- | --- | --- |
| 1.5 | −0.585 | −1.585 | −1.585 |
| 2.0 | −1.000 | −2.000 | −2.000 |
| 2.3 | −1.202 | −2.202 | −2.202 |
| 3.0 | −1.585 | −2.585 | −2.585 |

FSR 2 の README に書かれた値（Quality −1.58、Balanced −1.76、Performance −2.0、Ultra Performance −2.58）は、この式の小数第 3 位を切り捨てた値と一致します。XeSS のガイドの例（2.0 倍で −1、2.3 倍で約 −1.202、3.0 倍で約 −1.585）も上の式と一致します。

XeSS だけバイアスが 1.0 浅い理由は、資料には書かれていません。同じ 2.0 倍でも XeSS は −1、他の 2 つは −2 です。他のアップスケーラの式を流用するとテクスチャの鮮明さが変わるので、各 SDK の式を使い分けます。

XeSS と DLSS のガイドは、負のバイアスを強くすると、細部が増える代わりにちらつきやモアレが出ることがあると書いています（FSR 2 の README では、この記述を確かめていません）。DLSS のガイドはちらつく素材ではバイアスを弱めてよいが、`log2(r)` を超えて正の側には寄せないことと書いています。

## 入力と呼び出し {#inputs}

形式やフラグの違いは次のとおりです。各項目の意味は [Upscaling](index.md) にあります。

| 項目 | FSR 2 | DLSS | XeSS-SR |
| --- | --- | --- | --- |
| 動きベクトルの形式 | 浮動小数点 2 つ | RG16 か RG32 の FLOAT | R16G16_FLOAT |
| 既定の解像度 | 描画 | 描画 | 描画 |
| 出力解像度で渡す | フラグで切替 | MVLowRes を 0 | HIGH_RES_MV |
| ジッターを含める | 打ち消しフラグ | MVJittered で選ぶ | 含めない |
| ジッターの範囲 | SDK の関数の値 | −0.5〜+0.5 | −0.5〜+0.5 |
| 深度の反転 | DEPTH_INVERTED | DepthInverted | INVERTED_DEPTH |
| 露出 | 1×1 の R32_FLOAT | 1×1 テクスチャ | 値・テクスチャ・自動 |
| 自動露出 | フラグ | AutoExposure | AUTOEXPOSURE |
| リセット | reset | InReset | historyReset |
| 呼び出す位置 | トーン マッピングの前 | トーン マッピングの前 | トーン マッピングの前 |

動きベクトルの既定の解像度は 3 社とも描画解像度で、そのまま渡せば SDK が内部で広げます（膨張）。出力解像度で渡すときは自分で膨張させます。ジッターを動きベクトルに含めるかは FSR 2 と XeSS が含めない前提で、DLSS だけフラグで含める方も選べます。

露出の渡し方は DLSS の Preset J と K だけがテクスチャを使い、Preset L は常に自動露出です。

FSR 3 の紹介ページは対応 API として DirectX 12 と Vulkan を挙げています。DLSS は DirectX 11・12 と Vulkan 1.1 以降、XeSS は DirectX 12・Vulkan と Arc 以降の Intel GPU に限った DirectX 11 です。

## どれを選ぶか {#choose}

3 つは描画側の準備がほぼ同じなので、選ぶ基準は GPU の対応が中心です。DLSS は RTX の GPU が必要です。XeSS は Intel 以外の GPU でも Shader Model 6.4 に対応すれば動きます。FSR は読んだ資料では DirectX 12 と Vulkan に対応するとだけ書かれています。

画質や速度の比較はこの資料群には書かれていません。ゲームと GPU で結果が変わるので、ここでは断定しません。自分のゲームで同じ場面を同じ描画解像度で比べます。

## これだけ覚える {#summary}

- プリセットの倍率は会社で違う。XeSS の Quality は 1.7 倍
- ミップ バイアスは XeSS が `log2(r)`、FSR 2 と DLSS は `log2(r) - 1.0`
- 位相数は `8 × 倍率²`。端数の扱いだけ違う
- 3 社ともトーン マッピングの前で呼ぶ

## 参考資料 {#references}

- Intel. "Intel XeSS-SR Developer Guide 2.0." [https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html](https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html)
- AMD GPUOpen. "FidelityFX Super Resolution 2 (FSR 2)." [https://github.com/GPUOpen-Effects/FidelityFX-FSR2](https://github.com/GPUOpen-Effects/FidelityFX-FSR2)
- AMD GPUOpen. "FidelityFX Super Resolution 3." [https://gpuopen.com/fidelityfx-super-resolution-3/](https://gpuopen.com/fidelityfx-super-resolution-3/)
- NVIDIA. "NVIDIA DLSS Super Resolution Programming Guide." 2026 年 3 月 31 日付. [https://github.com/NVIDIA/DLSS](https://github.com/NVIDIA/DLSS)
    - 表の値はこれらの資料に書かれた値です。倍率ごとの値（ミップ バイアス、`8 × 倍率²`）は上の式から私が計算しました。コードはコンパイルしていません。
    - FSR 2 の README の後ろ約 2.6 万字と DLSS のガイドの 5 章以降は読んでいません。

## 関連ページ

- [Upscaling](index.md)
- [FSR](fsr.md)
- [DLSS](dlss.md)
- [XeSS](xess.md)

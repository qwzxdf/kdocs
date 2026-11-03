---
title: XeSS
tags:
  - 描画
---

# XeSS

NVIDIA の DLSS は NVIDIA の GPU 専用で、AMD の FSR は分析型です。Intel の XeSS（Xe Super Sampling）は、<strong>ニューラル ネットワークで高画質に拡大しつつ、Intel 以外の GPU でも動く</strong>ように作られています。ここでは Intel が公開している XeSS-SR（Super Resolution）の開発者ガイド 2.0 を読んで、組み込みで間違えやすい所を説明します。

!!! tip "ポイント"
    - 入力は低解像度のカラー、動きベクトル、ジッター、露出です。深度は、動きベクトルが低解像度のときに必要になります。
    - 倍率・ミップ バイアス・ジッター列の長さは、プリセットごとに決め打ちせず、SDK の関数から取ります。
    - ジッターは [-0.5, 0.5] の範囲に収めます。範囲を出るとアーティファクトが出ます。
    - TAA と他のアップスケーラは止めます。XeSS が TAA の代わりをします。
    - トーン マッピングの前に実行します。

!!! info "このページを読む前に"
    - [Upscaling](index.md)（入力と品質モードの全体像）
    - [TAA](../antialiasing/taa.md)（ジッターと履歴の考え方）

## 2 つの実装 {#backends}

開発者ガイドには、実装が 2 つあると書かれています。1 つは Intel Arc と Iris Xe 向けに最適化された実装です。もう 1 つは、HLSL で書かれた他社 GPU 向けの実装で、Shader Model 6.4 に対応する GPU で動きます。ガイドは、後者には DP4a（4 つの 8 ビット整数の積和を 1 命令で行う命令）か同等のハードウェア加速があることを勧めています。

ここから先は、ガイドに書かれていない一般的な知識です。Intel の実装は、Arc の行列演算ユニット（XMX）を使って大きなモデルを動かすと言われています。そのため、同じ品質モードでも、他社 GPU の実装は画質が少し落ち、実行時間も長くなる傾向があります。実測するまでは断定できないので、ゲームの設定画面では、アップスケールの有無と品質モードを選べるようにしておきます。

ゲームのコードは、どちらの実装が選ばれるかを意識しません。SDK が GPU を見て切り替えます。ただし、使える API には差があります。D3D12 は Iris Xe 以降か、DP4a 付きの SM 6.4 対応 GPU で動きます。D3D11 は Arc 以降の Intel GPU だけです。未対応のデバイスでコンテキストを作ると、`XESS_RESULT_ERROR_UNSUPPORTED_DEVICE` が返ります。Vulkan 1.1 では、`shaderStorageReadWithoutFormat`、`VK_EXT_mutable_descriptor_type`、`shaderIntegerDotProduct` が要ります。

DLL の組み合わせにも注意が要ります。D3D11 のコンテキストに `libxess.dll` を使ったり、D3D12 や Vulkan のコンテキストに `libxess_dx11.dll` を使ったりしてはいけません。

## 品質モードと倍率 {#modes}

倍率は、出力の幅を入力の幅で割った値です。XeSS-SR 1.3 以降のプリセットは次のとおりです。

- Native Anti-Aliasing: 1.0 倍。解像度は変えず、アンチエイリアスだけを使う
- Ultra Quality Plus: 1.3 倍
- Ultra Quality: 1.5 倍
- Quality: 1.7 倍
- Balanced: 2.0 倍
- Performance: 2.3 倍
- Ultra Performance: 3.0 倍

1.3 より前の版の倍率に戻したいときは、`xessForceLegacyScaleFactors` を使います。そのときは、Ultra Quality が 1.3 倍、Quality が 1.5 倍、Balanced が 1.7 倍、Performance が 2.0 倍になります。

ガイドの推奨は、Performance と Ultra Performance を 1440p 以上で、そのほかを 1080p 以上で使うことです。既定のプリセットは、1080p 以下なら Balanced、1440p 以上なら Performance が目安です。

倍率は版で変わってきました。だから、ガイドも「プリセットごとの値を決め打ちしない」ことを繰り返し求めています。入力解像度は、次の関数で SDK に聞きます。

```cpp
// 出力解像度とプリセットから、描画すべき入力解像度を SDK が返す。
// 倍率を自分で計算して決め打ちすると、SDK の更新で食い違う。
xess_2d_t input_res = {};
xessGetOptimalInputResolution(context, &output_res, XESS_QUALITY_SETTING_BALANCED,
                              &input_res, &input_res_min, &input_res_max);
```

動的解像度を使うときの範囲は、1.0 倍から各プリセットの最大倍率までです。縦横比は、出力に近い値を保ちます。

## ジッター {#jitter}

時間方式のアップスケーラは、毎フレーム投影行列をサブピクセルだけずらして描き、フレームごとに違う位置をサンプルします。XeSS では、ずらし量を投影行列の 3 行目の 1 列目と 2 列目に足します。

```cpp
// jitter_x, jitter_y は [-0.5, 0.5] の範囲（入力ピクセル単位）。
// 範囲を出ると、アーティファクトが出る。
// 2.0 / 幅 は、ピクセル単位のずらし量を、NDC（幅 2）の単位に直す係数。
proj.m[2][0] += jitter_x * 2.0f / input_width;
proj.m[2][1] -= jitter_y * 2.0f / input_height;  // Y は上下が逆なので引く
```

ずらし量は、Halton 列のような準乱数列から取ります。入力ピクセルの中心に偏った分布は避けます。

列の長さは、倍率が大きいほど長く要ります。ガイドの式は、基準の長さに、入力と出力の幅の比の 2 乗を掛けたものです。基準が 8 サンプルなら、3.0 倍の Ultra Performance では 8 × 9 = 72 サンプルになります。長いほど画質が上がることもあります。式も SDK の関数から取るのが安全です。

SDK に渡す値も、実際に加えた値と同じにします。食い違うと、静止していても画面が揺れます。

## 入力 {#inputs}

### カラー {#color}

線形空間で、浮動小数点か UNORM の形式です。非 UNORM の整数形式は使えません。出力は、入力と同じ色空間と形式になります。HDR の scRGB が推奨です。LDR なら、初期化で `XESS_INIT_FLAG_LDR_INPUT_COLOR` を立てます。バッファは FP16 が勧められています。

### 動きベクトル {#motion-vectors}

形式は `R16G16_FLOAT` で、X が R、Y が G です。既定は入力解像度の動きベクトルで、膨張（dilation）はしていないものを渡します。XeSS が深度を使って膨張とアップサンプルをします。

出力解像度の動きベクトルを渡すなら、`XESS_INIT_FLAG_HIGH_RES_MV` を立てます。そのときは、アプリが膨張を済ませておきます。たとえば、3×3 の近傍で一番手前の面のベクトルを選びます。

どちらでも、ベクトルにカメラのジッターは含めません。単位が NDC なら `XESS_INIT_FLAG_USE_NDC_VELOCITY` を立て、それ以外の単位は `xessSetVelocityScale` で合わせます。単位を間違えると、画面全体が滲みます。

### 深度 {#depth}

低解像度の動きベクトルを使うときに必要です。形式は何でもよく、既定では小さい値を手前と見なします。リバース Z なら `XESS_INIT_FLAG_INVERTED_DEPTH` を立てます。立て忘れると、手前と奥が逆になって、輪郭の周りが崩れます。

### 露出 {#exposure}

露出が合っていないと、ゴーストや明るさのずれが出ます。渡し方は 3 つあります。

- `XESS_INIT_FLAG_ENABLE_AUTOEXPOSURE`: XeSS に任せる。使うと負荷が増える
- 呼び出しごとに値を渡す
- 露出のテクスチャを渡す

入力がすでに露出で掛けてある（pre-exposed）なら、`xessSetExposureMultiplier` で補正します。

### レスポンシブ マスク {#responsive-mask}

粒子のように、履歴に頼らず、すぐ反映したい所を示す任意の入力です。入力解像度で、ジッターなしの R 1 チャンネルを [0, 1] の値で渡します。内部では既定で 0.8 に切り詰められます。変えるには `xessSetMaxResponsiveMaskValue` を使いますが、検証してからにします。

### 履歴のリセット {#history-reset}

カット シーンの切り替えのように、前の画面と無関係になったフレームでは、`historyReset` を立てます。立てないと、前の場面の残像が出ます。

## ミップ バイアス {#mip-bias}

低解像度で描くと、テクスチャが荒れて見えます。ミップ レベルを細かい方へずらして補います。ガイドの推奨値は `log2(入力の幅 / 出力の幅)` です。

2.0 倍なら -1、3.0 倍なら約 -1.585 です。動的解像度で入力解像度が変わるたびに、計算し直します。これより強く負にすると細部が増えることもありますが、帯域のコストが上がり、ちらつきやモアレも出ます。

## 実行の位置と前処理 {#placement}

ガイドは、トーン マッピングの前で実行することを求めています。トーン マッピングの後での実行は、実験的な扱いです。

XeSS の前に、次の処理を入れてはいけません。

- VRS
- チェッカーボード レンダリング
- ディザリング
- 4 分の 1 解像度のエフェクト

XeSS をデノイザーの代わりに使うことも勧められていません。

TAA と、DLSS・FSR のような他のアップスケーラは、無効にします。XeSS が時間方向の処理を担当するので、二重にかかると破綻します。

出力は、出力テクスチャの左上に置かれます（オフセットは設定できます）。アルファは 1.0 に固定されます。

## API の使い方で間違えやすい所 {#api-pitfalls}

D3D12 では、入力に non-pixel-shader-resource、出力に UAV のステートを使います。Vulkan では、入力が `SHADER_READ_ONLY_OPTIMAL`、出力が `GENERAL` です。ステートと同期は、アプリが管理します。

API はスレッド セーフではありません。XeSS-SR を初期化したスレッドから呼びます。

コンテキストを作った後で、`xessIsOptimalDriver` を呼びます。`XESS_RESULT_WARNING_OLD_DRIVER` が返っても、致命的なエラーではなく警告です。ユーザーにドライバーの更新を促す程度に使います。

Vulkan では、機能を `pNext` のチェーンで渡し、`pEnabledFeatures` には設定しません。

## よくあるミス {#mistakes}

??? failure "倍率やミップ バイアスを決め打ちして、SDK の更新で食い違う"
    プリセットの倍率は版で変わりました。決め打ちの値は、新しい SDK でテクスチャのぼやけや、ジッター列の不足を起こします。`xessGetOptimalInputResolution` などの関数から取ります。

??? failure "ジッターが [-0.5, 0.5] を出る"
    入力ピクセルの幅を超えたずらしは、アーティファクトになります。ずらし量の単位がピクセルか NDC かを、渡す側と受ける側でそろえます。

??? failure "動きベクトルにジッターが入っている"
    ジッターを含んだまま渡すと、静止した物体まで動いているように見えて、滲みます。ベクトルの計算では、ジッターなしの行列を使います。

??? failure "リバース Z なのに `XESS_INIT_FLAG_INVERTED_DEPTH` を立てない"
    手前と奥が逆に扱われ、輪郭の周りが崩れます。初期化のフラグを、描画側の深度の向きと合わせます。

??? failure "露出が合わず、ゴーストや明るさのずれが出る"
    自動露出を使う場合は、使う側で値を渡し続けます。pre-exposed の入力は、`xessSetExposureMultiplier` で補正します。

??? failure "TAA を切り忘れる"
    XeSS の前に TAA があると、履歴が二重に混ざってぼやけます。XeSS を使うときは、TAA のパスを外します。

## これだけ覚える {#summary}

- XeSS-SR は、Intel の最適化された実装と、SM 6.4 の他社 GPU 向けの HLSL 実装の 2 つがある
- 倍率・ミップ バイアス・ジッター列の長さは、SDK の関数から取る
- ジッターは [-0.5, 0.5]、動きベクトルにジッターは含めない、リバース Z は初期化のフラグで伝える
- トーン マッピングの前で実行し、TAA と他のアップスケーラは止める

## 参考資料 {#references}

- Intel. "Intel Xe Super Sampling (XeSS-SR) Developer Guide 2.0." Intel Developer Zone. [https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html](https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html)
    - プリセットの倍率、ジッターの式、入力の形式、ミップ バイアス、対応 API、初期化のフラグ、よくある間違いは、このガイドの内容です。
    - 上の「2 つの実装」で XMX に触れた段落は、ガイドに書かれていない一般的な知識です。ジッターのコードはガイドの式どおりです。`xessGetOptimalInputResolution` の呼び出しは、引数の並びまでは確かめていない説明用で、どちらもコンパイルしていません。

## 関連ページ

- [Upscaling](index.md)
- [FSR](fsr.md)
- [DLSS](dlss.md)
- [TAA](../antialiasing/taa.md)

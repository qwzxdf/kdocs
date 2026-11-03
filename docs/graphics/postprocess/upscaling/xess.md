---
title: XeSS
tags:
  - 描画
---

# XeSS

NVIDIA の DLSS は NVIDIA の GPU 専用で、AMD の FSR は分析型です。Intel の XeSS（Xe Super Sampling）は、<strong>ニューラル ネットワークで高画質に拡大しつつ Intel 以外の GPU でも動く</strong>ように作られています。ここでは Intel が公開している XeSS-SR（Super Resolution）の開発者ガイド 2.0 を読んで、組み込みで間違えやすい所を説明します。

!!! tip "ポイント"
    - 入力は低解像度のカラー、動きベクトル、ジッター、露出です。深度は動きベクトルが低解像度のときに必要になります。
    - 倍率・ミップ バイアス・ジッター列の長さは、プリセットごとに決め打ちせず SDK の関数から取ります。
    - ジッターは [-0.5, 0.5] の範囲に収めます。範囲を出るとアーティファクトが出ます。
    - TAA と他のアップスケーラは止めます。XeSS が TAA の代わりをします。
    - トーン マッピングの前に実行します。

!!! info "このページを読む前に"
    - [Upscaling](index.md)（入力と品質モードの全体像）
    - [TAA](../antialiasing/taa.md)（ジッターと履歴の考え方）

## 2 つの実装 {#backends}

開発者ガイドには実装が 2 つあると書かれています。1 つは Intel Arc と Iris Xe 向けに最適化された実装です。もう 1 つは HLSL で書かれた他社 GPU 向けの実装で、Shader Model 6.4 に対応する GPU で動きます。ガイドは後者には DP4a（4 つの 8 ビット整数の積和を 1 命令で行う命令）か同等のハードウェア加速があることを勧めています。

ここから先はガイドに書かれていない一般的な知識です。Intel の実装は Arc の行列演算ユニット（XMX）を使って大きなモデルを動かすと言われています。そのため、同じ品質モードでも他社 GPU の実装は画質が少し落ち実行時間も長くなる傾向があります。実測するまでは断定できないので、ゲームの設定画面ではアップスケールの有無と品質モードを選べるようにしておきます。

ゲームのコードはどちらの実装が選ばれるかを意識しません。SDK が GPU を見て切り替えます。ただし、使える API には差があります。D3D12 は Iris Xe 以降か DP4a 付きの SM 6.4 対応 GPU で動きます。D3D11 は Arc 以降の Intel GPU だけです。未対応のデバイスでコンテキストを作ると、`XESS_RESULT_ERROR_UNSUPPORTED_DEVICE` が返ります。Vulkan 1.1 では `shaderStorageReadWithoutFormat`、`VK_EXT_mutable_descriptor_type`、`shaderIntegerDotProduct` が要ります。

DLL の組み合わせにも注意が要ります。D3D11 のコンテキストに `libxess.dll` を使ったり、D3D12 や Vulkan のコンテキストに `libxess_dx11.dll` を使ったりしてはいけません。

## 品質モードと倍率 {#modes}

倍率は出力の幅を入力の幅で割った値です。XeSS-SR 1.3 以降のプリセットは次のとおりです。

- Native Anti-Aliasing: 1.0 倍。解像度は変えずアンチエイリアスだけを使う
- Ultra Quality Plus: 1.3 倍
- Ultra Quality: 1.5 倍
- Quality: 1.7 倍
- Balanced: 2.0 倍
- Performance: 2.3 倍
- Ultra Performance: 3.0 倍

<svg class="fig flow" viewBox="0 0 760 270" role="img" aria-label="XeSS の倍率と描画解像度"><defs><marker id="mx" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">4K 出力のとき、XeSS-SR のプリセットごとに描く解像度（1.3 以降の倍率）</text><rect x="20" y="40" width="330" height="186" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="185.0" y="244" text-anchor="middle" style="font-size:12px;font-weight:400">出力 3840×2160</text><rect x="20" y="40" width="330.0" height="186.0" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><rect x="20" y="40" width="253.8" height="143.1" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><rect x="20" y="40" width="220.0" height="124.0" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><rect x="20" y="40" width="194.1" height="109.4" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><rect x="20" y="40" width="165.0" height="93.0" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><rect x="20" y="40" width="143.5" height="80.9" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><rect x="20" y="40" width="110.0" height="62.0" fill="none" stroke="#4c8bf5" stroke-width="1.5"/><text x="400" y="56" text-anchor="start" style="font-size:13px;font-weight:400">Native AA：1.0 倍 → 3840×2160</text><text x="400" y="80" text-anchor="start" style="font-size:13px;font-weight:400">Ultra Quality Plus：1.3 倍 → 2954×1662</text><text x="400" y="104" text-anchor="start" style="font-size:13px;font-weight:400">Ultra Quality：1.5 倍 → 2560×1440</text><text x="400" y="128" text-anchor="start" style="font-size:13px;font-weight:400">Quality：1.7 倍 → 2259×1271</text><text x="400" y="152" text-anchor="start" style="font-size:13px;font-weight:400">Balanced：2.0 倍 → 1920×1080</text><text x="400" y="176" text-anchor="start" style="font-size:13px;font-weight:400">Performance：2.3 倍 → 1670×939</text><text x="400" y="200" text-anchor="start" style="font-size:13px;font-weight:400">Ultra Performance：3.0 倍 → 1280×720</text><text x="400" y="234" text-anchor="start" style="font-size:12px;font-weight:400">外側の枠が出力。内側の枠ほど小さく描く</text></svg>

図のとおり倍率 1.3 と 3.0 では、描くピクセル数が約 6 倍違います（1.3² と 3.0² の比）。倍率が大きいほど速くなりますが、少ない情報から細部を作り直す量が増えます。ガイドが Performance と Ultra Performance を 1440p 以上で使うよう勧めるのは、元の解像度が低いと復元の元になる情報が少なすぎるためと考えられます（この理由はガイドに書かれていないので、私の推測です）。

1.3 より前の版の倍率に戻したいときは、`xessForceLegacyScaleFactors` を使います。そのときは、Ultra Quality が 1.3 倍、Quality が 1.5 倍、Balanced が 1.7 倍、Performance が 2.0 倍になります。

ガイドの推奨は Performance と Ultra Performance を 1440p 以上で、そのほかを 1080p 以上で使うことです。既定のプリセットは 1080p 以下なら Balanced、1440p 以上なら Performance が目安です。

倍率は版で変わってきました。だから、ガイドも「プリセットごとの値を決め打ちしない」ことを繰り返し求めています。入力解像度は次の関数で SDK に聞きます。

```cpp
// 出力解像度とプリセットから、描画すべき入力解像度を SDK が返す。
// 倍率を自分で計算して決め打ちすると、SDK の更新で食い違う。
xess_2d_t input_res = {};
xessGetOptimalInputResolution(context, &output_res, XESS_QUALITY_SETTING_BALANCED,
                              &input_res, &input_res_min, &input_res_max);
```

動的解像度を使うときの範囲は 1.0 倍から各プリセットの最大倍率までです。縦横比は出力に近い値を保ちます。

## ジッター {#jitter}

ずらし量の取り方（ハルトン列）、位相数の考え方、コードは [Upscaling](index.md#jitter) にまとめました。ここには XeSS に固有の点だけを書きます。

- ずらし量は、投影行列の 3 行目の 1 列目と 2 列目に足します。ガイドの式は `M[2][0] += Jx * 2.0 / 入力の幅` と `M[2][1] -= Jy * 2.0 / 入力の高さ` です。画素の単位を NDC の単位に直す `2.0 / 幅` と、Y を引く符号が、式に書かれています。
- ずらし量の範囲は [-0.5, 0.5] です。範囲を出るとアーティファクトが出ます。
- 列の長さは、基準の長さに `(入力の幅 / 出力の幅)` の 2 乗の逆数、つまり倍率の 2 乗を掛けます。ガイドは 8 サンプルの基準を 3.0 倍にすると 8 × 9 = 72 になる例を挙げています。倍率ごとの表はありません。
- SDK に渡す値も、実際に加えた値と同じにします。食い違うと、静止していても画面が揺れます。

## 入力 {#inputs}

### カラー {#color}

線形空間で浮動小数点か UNORM の形式です。非 UNORM の整数形式は使えません。出力は入力と同じ色空間と形式になります。HDR の scRGB が推奨です。LDR なら初期化で `XESS_INIT_FLAG_LDR_INPUT_COLOR` を立てます。バッファは FP16 が勧められています。

### 動きベクトル {#motion-vectors}

形式は `R16G16_FLOAT` で X が R、Y が G です。既定は入力解像度の動きベクトルで、膨張（dilation）はしていないものを渡します。XeSS が深度を使って膨張とアップサンプルをします。

出力解像度の動きベクトルを渡すなら `XESS_INIT_FLAG_HIGH_RES_MV` を立てます。そのときは、アプリが膨張を済ませておきます。たとえば、3×3 の近傍で一番手前の面のベクトルを選びます。

どちらでもベクトルにカメラのジッターは含めません。単位が NDC なら `XESS_INIT_FLAG_USE_NDC_VELOCITY` を立て、それ以外の単位は `xessSetVelocityScale` で合わせます。単位を間違えると画面全体が滲みます。

### 深度 {#depth}

低解像度の動きベクトルを使うときに必要です。形式は何でもよく既定では小さい値を手前と見なします。リバース Z なら `XESS_INIT_FLAG_INVERTED_DEPTH` を立てます。立て忘れると手前と奥が逆になって、輪郭の周りが崩れます。

### 露出 {#exposure}

露出が合っていないとゴーストや明るさのずれが出ます。渡し方は 3 つあります。

- `XESS_INIT_FLAG_ENABLE_AUTOEXPOSURE`: XeSS に任せる。使うと負荷が増える
- 呼び出しごとに値を渡す
- 露出のテクスチャを渡す

入力がすでに露出で掛けてある（pre-exposed）なら `xessSetExposureMultiplier` で補正します。

### レスポンシブ マスク {#responsive-mask}

粒子のように履歴に頼らずすぐ反映したい所を示す任意の入力です。入力解像度でジッターなしの R 1 チャンネルを [0, 1] の値で渡します。内部では既定で 0.8 に切り詰められます。変えるには `xessSetMaxResponsiveMaskValue` を使いますが、検証してからにします。

### 履歴のリセット {#history-reset}

カット シーンの切り替えのように前の画面と無関係になったフレームでは、`historyReset` を立てます。立てないと前の場面の残像が出ます。

## 初期化フラグの選び方 {#init-flags}

動きベクトルの解像度、深度の向き色の範囲などはコンテキストを作るときのフラグで SDK に伝えます。描画側の作りに合わせて次のように組み立てます。

```cpp
// 初期化時に渡すフラグを組み立てる例（名前は開発者ガイドのもの）。
// ゲームの描画の作りと食い違うと、画面が崩れる。
uint32_t init_flags = 0;

// 動きベクトルを出力解像度で持っているときだけ立てる。
// 描画解像度のベクトルなら立てない（XeSS が膨張とアップサンプルを行う）。
if (motion_vectors_at_output_resolution) init_flags |= XESS_INIT_FLAG_HIGH_RES_MV;

// 動きベクトルの単位が NDC のときに立てる。ピクセル単位なら立てない。
if (velocity_in_ndc) init_flags |= XESS_INIT_FLAG_USE_NDC_VELOCITY;

// リバース Z（近い面が 1.0、遠い面が 0.0）のときに立てる。
// 忘れると手前と奥が逆に扱われて、輪郭の周りが崩れる。
if (reversed_z) init_flags |= XESS_INIT_FLAG_INVERTED_DEPTH;

// 入力が LDR のときだけ立てる。HDR（scRGB など）なら立てない。
if (input_is_ldr) init_flags |= XESS_INIT_FLAG_LDR_INPUT_COLOR;

// 露出を自分で渡さず、XeSS に任せるときに立てる（処理時間が増える）。
if (use_auto_exposure) init_flags |= XESS_INIT_FLAG_ENABLE_AUTOEXPOSURE;
```

フラグごとの意味はガイドの「初期化フラグ」の節をもとに書きました。このコードはコンパイルしていません。変数名（`motion_vectors_at_output_resolution` など）は説明用で、コンテキストを作る関数の引数の並びは、ガイドで確かめていません。

## ミップ バイアス {#mip-bias}

低解像度で描くとテクスチャが荒れて見えます。ミップ レベルを細かい方へずらして補います。ガイドの推奨値は `log2(入力の幅 / 出力の幅)` です。

2.0 倍なら -1、3.0 倍なら約 -1.585 です。動的解像度で入力解像度が変わるたびに計算し直します。これより強く負にすると細部が増えることもありますが、帯域のコストが上がりちらつきやモアレも出ます。

## 実行の位置と前処理 {#placement}

ガイドはトーン マッピングの前で実行することを求めています。トーン マッピングの後での実行は実験的な扱いです。

XeSS の前に次の処理を入れてはいけません。

- VRS
- チェッカーボード レンダリング
- ディザリング
- 4 分の 1 解像度のエフェクト

XeSS をデノイザーの代わりに使うことも勧められていません。

TAA と DLSS・FSR のような他のアップスケーラは、無効にします。XeSS が時間方向の処理を担当するので、二重にかかると破綻します。

出力は出力テクスチャの左上に置かれます（オフセットは設定できます）。アルファは 1.0 に固定されます。

## API の使い方で間違えやすい所 {#api-pitfalls}

D3D12 では入力に non-pixel-shader-resource、出力に UAV のステートを使います。Vulkan では入力が `SHADER_READ_ONLY_OPTIMAL`、出力が `GENERAL` です。ステートと同期はアプリが管理します。

API はスレッド セーフではありません。XeSS-SR を初期化したスレッドから呼びます。

コンテキストを作った後で `xessIsOptimalDriver` を呼びます。`XESS_RESULT_WARNING_OLD_DRIVER` が返っても致命的なエラーではなく警告です。ユーザーにドライバーの更新を促す程度に使います。

Vulkan では機能を `pNext` のチェーンで渡し、`pEnabledFeatures` には設定しません。

## よくあるミス {#mistakes}

??? failure "倍率やミップ バイアスを決め打ちして、SDK の更新で食い違う"
    プリセットの倍率は版で変わりました。決め打ちの値は新しい SDK でテクスチャのぼやけやジッター列の不足を起こします。`xessGetOptimalInputResolution` などの関数から取ります。

??? failure "ジッターが [-0.5, 0.5] を出る"
    入力ピクセルの幅を超えたずらしは、アーティファクトになります。ずらし量の単位がピクセルか NDC かを渡す側と受ける側でそろえます。

??? failure "動きベクトルにジッターが入っている"
    ジッターを含んだまま渡すと静止した物体まで動いているように見えて、滲みます。ベクトルの計算ではジッターなしの行列を使います。

??? failure "リバース Z なのに `XESS_INIT_FLAG_INVERTED_DEPTH` を立てない"
    手前と奥が逆に扱われ輪郭の周りが崩れます。初期化のフラグを描画側の深度の向きと合わせます。

??? failure "露出が合わずゴーストや明るさのずれが出る"
    自動露出を使う場合は使う側で値を渡し続けます。pre-exposed の入力は `xessSetExposureMultiplier` で補正します。

??? failure "TAA を切り忘れる"
    XeSS の前に TAA があると、履歴が二重に混ざってぼやけます。XeSS を使うときは TAA のパスを外します。

## これだけ覚える {#summary}

- XeSS-SR は Intel の最適化された実装と SM 6.4 の他社 GPU 向けの HLSL 実装の 2 つがある
- 倍率・ミップ バイアス・ジッター列の長さは、SDK の関数から取る
- ジッターは [-0.5, 0.5]、動きベクトルにジッターは含めない、リバース Z は初期化のフラグで伝える
- トーン マッピングの前で実行し、TAA と他のアップスケーラは止める

## 参考資料 {#references}

- Intel. "Intel Xe Super Sampling (XeSS-SR) Developer Guide 2.0." Intel Developer Zone. [https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html](https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html)
    - プリセットの倍率、ジッターの式、入力の形式、ミップ バイアス、対応 API、初期化のフラグ、よくある間違いはこのガイドの内容です。
    - 上の「2 つの実装」で XMX に触れた段落は、ガイドに書かれていない一般的な知識です。ジッターのコードはガイドの式どおりです。`xessGetOptimalInputResolution` の呼び出しは引数の並びまでは確かめていない説明用で、どちらもコンパイルしていません。

## 関連ページ

- [Upscaling](index.md)
- [FSR](fsr.md)
- [DLSS](dlss.md)
- [TAA](../antialiasing/taa.md)

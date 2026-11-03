---
title: FSR
tags:
  - 描画
---

# FSR

アップスケーラを入れたいが特定のメーカーの GPU でしか動かないのは困る、という場面があります。FSR（FidelityFX Super Resolution）は AMD が作った技術で、<strong>特別な GPU が要らずソースが公開されていて、どのメーカーの GPU でも動く</strong>のが特徴です。ここでは AMD の FSR 2 の README と FSR 3 の紹介ページを読んで、組み込みで間違えやすい所を説明します。

!!! tip "ポイント"
    - FSR 1 は空間方式で、動きベクトルが要りません。FSR 2 以降は時間方式で、動きベクトルとジッターが要ります。
    - FSR 2 はニューラル ネットワークを使わず手作りの規則で履歴を使います。
    - FSR 3 のアップスケールは FSR 2 とほぼ同じ組み込みで、フレーム生成を足せます。生成を切ると FSR 2 と同等の動きになります。
    - ジッター列の長さとミップ バイアスは、SDK の関数か式から出します。
    - トーン マッピングは FSR の後で行います。SSAO や SSR のような画面空間の処理は、FSR の前で描画解像度のまま行います。

!!! info "このページを読む前に"
    - [Upscaling](index.md)（入力と品質モードの全体像）
    - [TAA](../antialiasing/taa.md)（ジッターと履歴の考え方）

## 版の違い {#versions}

### FSR 1 {#fsr1}

空間方式です。EASU（Edge Adaptive Spatial Upsampling）がエッジの向きを見ながら拡大し、RCAS（Robust Contrast Adaptive Sharpening）が輪郭を強調します。動きベクトルが要らないので組み込みは楽ですが、1 枚の画像だけが入力なので、元の画像に無い細部は戻りません。低解像度から大きく拡大すると、ぼやけが目立ちます。

### FSR 2 {#fsr2}

時間方式です。毎フレーム、カメラをサブピクセルずらして描き動きベクトルで前のフレームを重ねます。DLSS のようなニューラル ネットワークは使わず深度や色の差から履歴を使うか捨てるかを、決め打ちの規則で決めます。専用のハードウェアが要らないので、どの GPU でも動きます。

### FSR 3 と 3.1 {#fsr3}

FSR 3 は FSR 2 のアップスケールにフレーム生成（Frame Generation）を足したものです。紹介ページによるとフレーム生成を切ると、FSR 2 と同等の動きになります。アップスケールの組み込みは FSR 2 に似ているので、FSR 2 を使っているゲームは FSR 3 のアップスケールに差し替えられます。

フレーム生成には制約があります。紹介ページは入力のフレームレートが 60 fps 以上であることを求めています。60 fps を下回るのは勧められず 30 fps 未満は「絶対に避ける」と書かれています。アップスケールだけを組み込んで画質の悪いまま使うとそのアーティファクトが補間フレームにも引き継がれます。

そのほか UI を補間フレームの上に重ねる方法が必要になります。紹介ページは 3 つの方法を挙げています。UI を別のレンダー ターゲットに描いて重ねる方法、エンジンのコールバックを使う方法、フレームの比較で UI を検出する方法です。VSync を入れると描画の速さは暗黙にモニターの最大リフレッシュ レートの半分に制限されます。フレーム リミッターの使用が勧められています。

3.1 ではアップスケーラとフレーム生成が分かれて、別々に差し替えられるようになりました。紹介ページ時点（3.1.5）のアップスケールは、1 倍から 9 倍までの任意の面積倍率に対応します。動的な解像度の変更も使えます。

### FSR 4 {#fsr4}

紹介ページには FSR 4（今は AMD FSR Upscaling という名前）が FSR 3 の後継と書かれています。新しく組み込むなら AMD FSR SDK v2 を使うことが勧められています。この SDK は FSR 2・3・4 をまとめて扱い必要なときに FSR 3.1.5 に切り替えます。機械学習を使うことや対応する GPU の範囲は、読んだ資料に書かれていないので、このページでは解説しません。

## 品質モード {#modes}

FSR 3 のアップスケールの品質モードは、次のとおりです。倍率は幅（高さ）での倍率で括弧の中は面積での割合です。

- Native AA: 1.0 倍。拡大はせずアンチエイリアスだけを行う。負荷が一番大きく反応マスクなども必要
- Quality: 1.5 倍（67%）。4K 出力なら 2560×1440 で描く
- Balanced: 1.7 倍（59%）。4K 出力なら 2259×1270
- Performance: 2.0 倍（50%）。4K 出力なら 1920×1080
- Ultra Performance: 3.0 倍（33%）。4K 出力なら 1280×720。任意のモード

コストの目安として紹介ページは RX 7900 XTX、4K、Quality でアップスケール 1.0 ms、フレーム生成が最大 1.7 ms と書いています。FidelityFX SDK のサンプルから得た見積もりで、シャープニングと非同期コンピュートを切った状態の値です。自分のゲームの数字ではないので、プロファイラーで測り直します。

## ジッター {#jitter}

FSR 2 の README ではジッターのずらし量は Halton 列（底が 2 と 3）です。SDK の関数 `ffxFsr2GetJitterPhaseCount(renderWidth, displayWidth)` が列の長さを返します。品質モードごとの長さは Quality が 18、Balanced が 23、Performance が 32、Ultra Performance が 72 です。独自の倍率 n を使うときは `ceil(8 * n^2)` で出します。

ずらし量を加えるのは不透明な物体だけではありません。半透明やレイトレースの物体も含めて、描画する全部のパスに加えます。動きベクトルにはジッターを入れません（ジッターを打ち消すフラグを立てた場合を除きます）。

ジッターのベクトルが X も Y も 0 のまま渡されると問題になります。`ffxFsr2GetJitterOffset` を使わないときは 0 の値を渡さないようにします。

## ミップ バイアス {#mip-bias}

README の式は次のとおりです。

```cpp
// 描画解像度が表示解像度より小さいほど、log2 は負になる。
// さらに 1.0 を引くので、テクスチャは通常より細かいミップから読まれる。
float mip_bias = std::log2(render_width / display_width) - 1.0f;
```

倍率ごとの値は Quality が -1.58、Balanced が -1.76、Performance が -2.0、Ultra Performance が -2.58 です。XeSS の推奨が `log2` だけで終わるのに対して、FSR 2 の式は 1.0 を余計に引いています。同じ名前の値でもアップスケーラによって式が違うことに注意します。

## 入力 {#inputs}

FSR 2 の README が挙げる入力は、次のとおりです。

### カラー {#color}

描画解像度で線形色空間です。HDR のときは `FFX_FSR2_ENABLE_HIGH_DYNAMIC_RANGE` を立てます。README は LDR のときの動きは書いていません。

### 深度 {#depth}

描画解像度で浮動小数点が 1 つです。リバース Z（[1..0]）なら `FFX_FSR2_ENABLE_DEPTH_INVERTED` を遠方クリップが無限なら `FFX_FSR2_ENABLE_DEPTH_INFINITE` を立てます。この 2 つを併用して遠方の値を低くしすぎると、深度の分離でアーティファクトが出ます。

### 動きベクトル {#motion-vectors}

描画解像度（フラグを立てれば表示解像度）で、浮動小数点が 2 つです。値の範囲は(-幅, -高さ) から (幅, 高さ) までです。NDC の単位で持つ動きベクトルは `motionVectorScale.x` に描画の幅、`motionVectorScale.y` に描画の高さを設定してピクセル単位に直します。内部の精度は実質 16 ビットなので、それ以上の精度にしても効果はありません。

### 露出 {#exposure}

1×1 の `R32_FLOAT` です。自動露出のフラグを立てるなら省略できます。露出の値はゲームのトーン マッピングで使う露出と合わせます。入力が pre-exposed ならその分を割ってから戻します。README はこの説明だけで、式は書いていません。

### 反応マスク {#reactive-mask}

描画解像度の `R8_UNORM` で省略できます。省略すると内部のクリア済み 1×1 が使われます。アルファ ブレンドの物体のアルファを書き込み最大値は 0.9 前後に抑えることが勧められています。半透明の粒子のように履歴に頼らずすぐに反映させたい所を指定します。

透明度と合成のマスクもあります。README の読んだ範囲には形式と解像度が書かれていないので、ここでは解説しません。

### リセットとフレーム時間 {#reset}

カメラのジャンプ カットの最初のフレームでは、`reset` を true にします。立てないと前の場面の残像が出ます。

`frameTimeDelta` はミリ秒で渡します。60 fps なら約 16.6 です。1.0 を下回るとデバッグ チェッカーが警告します。秒で渡すとこれに引っかかります。

## フレーム内での位置 {#placement}

README のフレームの図ではトーン マッピング、ブルーム、被写界深度、モーション ブラー、フィルム グレイン、色収差、ヴィネットが「Post processing B」で、FSR 2 の後に表示解像度で行われます。SSAO、SSR、デノイザーのような画面空間の処理は FSR 2 の前、描画解像度のままです。

<svg class="fig flow" viewBox="0 0 720 210" role="img" aria-label="FSR 2 の README の順番"><defs><marker id="mq" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">FSR 2 のフレーム内の位置（README の図の順番）</text><rect x="20" y="60" width="150" height="80" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="95" y="83.0" text-anchor="middle" style="font-size:12px;font-weight:600">Post processing A</text><text x="95" y="100.0" text-anchor="middle" style="font-size:12px;font-weight:600">SSR・SSAO</text><text x="95" y="117.0" text-anchor="middle" style="font-size:12px;font-weight:600">デノイザー</text><text x="95" y="162" text-anchor="middle" style="font-size:12px;font-weight:400">描画解像度</text><line x1="170" y1="100" x2="190" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#mq)"/><rect x="190" y="60" width="150" height="80" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="265" y="91.5" text-anchor="middle" style="font-size:12px;font-weight:600">FSR 2</text><text x="265" y="108.5" text-anchor="middle" style="font-size:12px;font-weight:600">アップスケール</text><text x="265" y="162" text-anchor="middle" style="font-size:12px;font-weight:400">描画 → 表示</text><line x1="340" y1="100" x2="360" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#mq)"/><rect x="360" y="60" width="150" height="80" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="435" y="83.0" text-anchor="middle" style="font-size:12px;font-weight:600">Post processing B</text><text x="435" y="100.0" text-anchor="middle" style="font-size:12px;font-weight:600">トーン マッピング</text><text x="435" y="117.0" text-anchor="middle" style="font-size:12px;font-weight:600">ブルーム・DOF など</text><text x="435" y="162" text-anchor="middle" style="font-size:12px;font-weight:400">表示解像度</text><line x1="510" y1="100" x2="530" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#mq)"/><rect x="530" y="60" width="150" height="80" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="605" y="91.5" text-anchor="middle" style="font-size:12px;font-weight:600">RCAS</text><text x="605" y="108.5" text-anchor="middle" style="font-size:12px;font-weight:600">シャープ</text><text x="605" y="162" text-anchor="middle" style="font-size:12px;font-weight:400">表示解像度</text><text x="360" y="190" text-anchor="middle" style="font-size:12px;font-weight:400">README の順番。RCAS は最後の段階で、強さをスライダーで変えられるようにする</text></svg>

シャープニング（RCAS）は最後の段階です。README はスライダーで強さを変えられるようにすることを勧めています。FSR 3 の紹介ページも同じ理由でスライダーを勧めています。RCAS の仕組みや強さの範囲は読んだ範囲に書かれていません。

## 組み込みの流れ {#integrate}

1. FidelityFX SDK を取り込みアップスケーラのコンテキストを作る（描画解像度と表示解像度を渡す）
2. 毎フレーム、投影行列にジッターを加えて全パスを描く
3. 低解像度のカラー、深度、動きベクトル、露出、反応マスクを渡して Dispatch する
4. 出力の高解像度の画像にトーン マッピングと UI を適用する

コンテキストを破棄する前に GPU を止めておきます（`ffxFsr2ContextDestroy`）。動いている最中に壊すと描画中のリソースが消えます。RenderDoc で深度のテクスチャを見ると、UNORM や UINT の形式に float をビットキャストして置いてあるため、見え方がおかしく見えます。

## ディスパッチのパラメーター {#dispatch}

毎フレーム、アップスケールを実行するときに渡す値のうち間違えやすいものだけを抜き出します。フィールド名は README に出てくるものです。

```cpp
// フレーム時間はミリ秒で渡す。60 fps なら約 16.6。
// 秒（約 0.0166）で渡すと 1.0 未満になり、デバッグ チェッカーが警告する。
dispatch.frameTimeDelta = delta_seconds * 1000.0f;

// 動きベクトルが NDC の単位のとき、README は描画の幅と高さを設定する。
// （ピクセルの単位で持っている場合の値は、読んだ範囲に書かれていない。）
dispatch.motionVectorScale.x = static_cast<float>(render_width);
dispatch.motionVectorScale.y = static_cast<float>(render_height);

// カメラのジャンプ カットの最初のフレームだけ true。
// 立てないと、前の場面の残像が出る。毎フレーム true にすると、履歴が使われない。
dispatch.reset = is_first_frame_after_camera_cut;
```

`motionVectorScale` は動きベクトルの値に掛ける倍率です。NDC の動きベクトルを描画解像度のピクセル単位の動きに直す役目です。ピクセル単位のまま渡すときの値は README の読んだ範囲に書かれていないので、組み込むときに README の NDC の計算例と合わせて確認します。このコードはコンパイルしていません。`dispatch` は README のディスパッチ用の構造体を指す説明用の変数です。

## よくあるミス {#mistakes}

??? failure "動く物体の後ろに残像が出る"
    動きベクトルにスキンメッシュや粒子の動きが入っていません。動く物体の分も動きベクトルのバッファに書き込みます。

??? failure "画面全体が揺れる"
    SDK に渡したジッターの量と投影行列に加えた量が違います。`ffxFsr2GetJitterOffset` の値をそのまま両方に使います。

??? failure "動きベクトルにジッターが入っている"
    静止している物体まで動いているように見えて、滲みます。ベクトルはジッターなしの行列で計算します。

??? failure "`frameTimeDelta` を秒で渡す"
    値が 1.0 未満になり時間に依存する処理が狂います。ミリ秒で渡します。

??? failure "トーン マッピングの後に FSR を呼ぶ"
    README の構成は FSR がトーン マッピングの前です。順番を逆にすると HDR の入力の前提が崩れます。

## これだけ覚える {#summary}

- FSR は GPU を選ばずソースが公開されている
- 1 は空間方式、2 以降は時間方式。3 でフレーム生成が付き切れば FSR 2 と同等
- ジッター列の長さは `ceil(8 * n^2)`、ミップ バイアスは `log2(描画 / 表示) - 1`
- 動きベクトルとジッターの扱いが、画質を決める
- トーン マッピングは FSR の後、画面空間の効果は FSR の前

## 参考資料 {#references}

- AMD GPUOpen. "FidelityFX Super Resolution 2 (FSR 2)." GitHub: GPUOpen-Effects/FidelityFX-FSR2. [https://github.com/GPUOpen-Effects/FidelityFX-FSR2](https://github.com/GPUOpen-Effects/FidelityFX-FSR2)
    - ジッター列の長さミップ バイアスの式、入力の形式、フラグ、フレーム内での位置はこの README の内容です。README の後ろ約 2.6 万字は読んでいません。
- AMD GPUOpen. "FidelityFX Super Resolution 3." [https://gpuopen.com/fidelityfx-super-resolution-3/](https://gpuopen.com/fidelityfx-super-resolution-3/)
    - 品質モードの倍率、コストの目安、フレーム生成の条件、FSR 4 の位置づけはこの紹介ページの内容です。
- 説明用のコードは README の式を元にしたもので、コンパイルしていません。FSR 1 の EASU と RCAS の説明は、一般的な知識で上の資料では確かめていません。

## 関連ページ

- [Upscaling](index.md)
- [DLSS](dlss.md)
- [XeSS](xess.md)
- [TAA](../antialiasing/taa.md)

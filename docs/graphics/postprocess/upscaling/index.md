---
title: Upscaling
tags:
  - 描画
---

# Upscaling

4K で描くと 1080p の 4 倍のピクセルを塗ることになります。ピクセルシェーダーが重いゲームでは、ここが一番の負担です。そこで<strong>低い解像度で描いて高い解像度に引き伸ばす</strong>のですが、ただ拡大するとぼやけます。アップスケーラは、ぼやけを抑えながら拡大して、元の画像に近い細部を取り戻す技術です。このページでは、FSR・DLSS・XeSS に共通する考え方と入力を説明します。各社で値が違う所は、[Upscaler Comparison](comparison.md) にまとめました。

!!! tip "ポイント"
    - 種類は 2 つあります。1 枚の画像だけで拡大する空間方式と、過去のフレームも使う時間方式です。今の主流は時間方式です。
    - 時間方式は、毎フレーム少しずつずらして描き（ジッター）、動きベクトルで過去の画像を合わせて、複数フレームのサンプルを集めます。
    - 入力は、低解像度のカラー・深度・動きベクトル・ジッターのずれ・露出です。動きベクトルの精度が画質を決めます。
    - 呼び出す位置は、3 社の資料とも、トーン マッピングの前です。
    - 倍率・ジッターの位相数・ミップ バイアスは、プリセットごとに決め打ちせず、SDK の関数か式から出します。

!!! info "このページを読む前に"
    - [TAA](../antialiasing/taa.md)（過去のフレームを混ぜる仕組みの基礎）
    - [TAA, Upscaling and VRS Cost](../taa-upscaling-cost.md)（コストの面から）

## 空間方式と時間方式 {#types}

空間方式は、1 フレームの画像だけを入力にして、エッジを保ちながら拡大します。組み込みは簡単で動きベクトルも要りませんが、元の画像に無い細部は取り戻せません。FSR 1 がこの方式です。

時間方式は TAA と同じ発想です。毎フレームカメラをサブピクセルだけずらして描くと、フレームごとに少しずつ違う位置をサンプルします。動きベクトルで前のフレームを現在の位置に合わせて重ねれば、複数フレーム分のサンプルが集まり、低解像度の描画でも高解像度に近い情報が得られます。

重ねるときは、前のフレームの情報が今の画面で有効か（隠れていないか・物体が変わっていないか）を判断します。この判断を手作りの規則で行うのが FSR 2 以降です。ニューラル ネットワークで行うのが DLSS と XeSS です。

## ジッター {#jitter}

低解像度で描くと、1 画素が出力の複数画素分の広さになります。同じ位置をサンプルし続けても、それ以上の細かさは得られません。そこで、フレームごとにサンプル位置を少しずらします。ずらし量は、1 画素の中を偏りなく埋める必要があるので、ハルトン列（底 2 と 3）のような準乱数列から取ります。DLSS のガイドは、学習データにもハルトン列を使っていると書いています。

<svg class="fig flow" viewBox="0 0 680 270" role="img" aria-label="1 つの入力画素の中に、ハルトン列のジッターが埋める位置"><defs><marker id="mj" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">描画の 1 画素（四角）を、ハルトン列（底 2 と 3）の点が埋めていく</text><rect x="40" y="50" width="170" height="170" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><line x1="125.0" y1="50" x2="125.0" y2="220" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="40" y1="135.0" x2="210" y2="135.0" stroke="#94a3b8" stroke-dasharray="4 4"/><circle cx="125.0" cy="106.7" r="4" fill="#4c8bf5"/><circle cx="82.5" cy="163.3" r="4" fill="#4c8bf5"/><circle cx="167.5" cy="68.9" r="4" fill="#4c8bf5"/><circle cx="61.2" cy="125.6" r="4" fill="#4c8bf5"/><circle cx="146.2" cy="182.2" r="4" fill="#4c8bf5"/><circle cx="103.8" cy="87.8" r="4" fill="#4c8bf5"/><circle cx="188.8" cy="144.4" r="4" fill="#4c8bf5"/><circle cx="50.6" cy="201.1" r="4" fill="#4c8bf5"/><text x="125.0" y="40" text-anchor="middle" style="font-size:13px;font-weight:700">位相 8 個</text><text x="125.0" y="242" text-anchor="middle" style="font-size:12px;font-weight:400">出力画素 4 つに、各 2 個ほど</text><rect x="280" y="50" width="170" height="170" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><line x1="365.0" y1="50" x2="365.0" y2="220" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="280" y1="135.0" x2="450" y2="135.0" stroke="#94a3b8" stroke-dasharray="4 4"/><circle cx="365.0" cy="106.7" r="4" fill="#4c8bf5"/><circle cx="322.5" cy="163.3" r="4" fill="#4c8bf5"/><circle cx="407.5" cy="68.9" r="4" fill="#4c8bf5"/><circle cx="301.2" cy="125.6" r="4" fill="#4c8bf5"/><circle cx="386.2" cy="182.2" r="4" fill="#4c8bf5"/><circle cx="343.8" cy="87.8" r="4" fill="#4c8bf5"/><circle cx="428.8" cy="144.4" r="4" fill="#4c8bf5"/><circle cx="290.6" cy="201.1" r="4" fill="#4c8bf5"/><circle cx="375.6" cy="56.3" r="4" fill="#4c8bf5"/><circle cx="333.1" cy="113.0" r="4" fill="#4c8bf5"/><circle cx="418.1" cy="169.6" r="4" fill="#4c8bf5"/><circle cx="311.9" cy="75.2" r="4" fill="#4c8bf5"/><circle cx="396.9" cy="131.9" r="4" fill="#4c8bf5"/><circle cx="354.4" cy="188.5" r="4" fill="#4c8bf5"/><circle cx="439.4" cy="94.1" r="4" fill="#4c8bf5"/><circle cx="285.3" cy="150.7" r="4" fill="#4c8bf5"/><circle cx="370.3" cy="207.4" r="4" fill="#4c8bf5"/><circle cx="327.8" cy="62.6" r="4" fill="#4c8bf5"/><circle cx="412.8" cy="119.3" r="4" fill="#4c8bf5"/><circle cx="306.6" cy="175.9" r="4" fill="#4c8bf5"/><circle cx="391.6" cy="81.5" r="4" fill="#4c8bf5"/><circle cx="349.1" cy="138.1" r="4" fill="#4c8bf5"/><circle cx="434.1" cy="194.8" r="4" fill="#4c8bf5"/><circle cx="295.9" cy="100.4" r="4" fill="#4c8bf5"/><circle cx="380.9" cy="157.0" r="4" fill="#4c8bf5"/><circle cx="338.4" cy="213.7" r="4" fill="#4c8bf5"/><circle cx="423.4" cy="52.1" r="4" fill="#4c8bf5"/><circle cx="317.2" cy="108.8" r="4" fill="#4c8bf5"/><circle cx="402.2" cy="165.4" r="4" fill="#4c8bf5"/><circle cx="359.7" cy="71.0" r="4" fill="#4c8bf5"/><circle cx="444.7" cy="127.7" r="4" fill="#4c8bf5"/><circle cx="282.7" cy="184.3" r="4" fill="#4c8bf5"/><text x="365.0" y="40" text-anchor="middle" style="font-size:13px;font-weight:700">位相 32 個（描画の 2 倍の解像度で出力）</text><text x="365.0" y="242" text-anchor="middle" style="font-size:12px;font-weight:400">出力画素 4 つに、各 8 個ほど</text><text x="500" y="150" text-anchor="start" style="font-size:12px;font-weight:400">点 ＝ 1 フレームが</text><text x="500" y="168" text-anchor="start" style="font-size:12px;font-weight:400">サンプルする位置</text><text x="500" y="200" text-anchor="start" style="font-size:12px;font-weight:400">破線 ＝ 出力画素の境目</text></svg>

何個の位置（位相）を用意するかは、倍率で決まります。倍率が s なら、描画の 1 画素は出力の s² 画素分の面積です。TAA で使う 8 位相を基準にして、同じ密度で埋めるには、次の式になります。

```text
位相数 = 8 × s²
```

倍率 2.0 なら 8 × 4 = 32、3.0 なら 8 × 9 = 72 です。倍率 1.5 なら 18 になります。1.7 は 23.12 で、FSR 2 の README は 23、DLSS のガイドは 1.724 倍に対して 24 と書いていて、端数の扱いは資料で異なります。位相数が足りないと、静止した場面でも画が解像しきれず、細い線がちらつきます。

### ジッターを加える {#jitter-code}

ずらし量は、投影行列に加えます。次のコードは、ハルトン列から位置を作り、XeSS の開発者ガイドの式で行列に足す例です。

```cpp
// ハルトン列の index 番目（index は 1 以上）を [0, 1) で返す。
// 底 base の数で index を桁ごとに分け、桁を小数点の右側に並べ直した値になる。
float Halton(int index, int base) {
  float f = 1.0f;       // 今の桁の重み。桁が進むたびに 1/base 倍になる
  float result = 0.0f;
  while (index > 0) {
    f /= base;
    result += f * (index % base);  // 今の桁の数字に重みを掛けて足す
    index /= base;                 // 次の桁へ
  }
  return result;
}
```

`Halton` は、`index` を `base` 進数で書いて、桁の並びを小数点の右へ折り返した値を返します。たとえば底 2 で `index = 3`（2 進数で 11）なら 0.75 です。`index` が 0 だと常に 0 になり、点が偏るので、1 から数えます。

```cpp
// 倍率 scale で、描画が input_width × input_height のとき、
// frame 番目のフレームで加えるジッターを求め、投影行列 proj に足す。
void ApplyJitter(Matrix& proj, int frame, float scale, int input_width, int input_height) {
  // 位相数。実際には SDK の関数（FSR 2 の ffxFsr2GetJitterPhaseCount など）から取る
  int phase_count = static_cast<int>(std::ceil(8.0f * scale * scale));
  int index = frame % phase_count + 1;       // 1 から数える（0 は点が偏る）

  float jitter_x = Halton(index, 2) - 0.5f;  // 入力画素の中での位置。範囲は [-0.5, 0.5)
  float jitter_y = Halton(index, 3) - 0.5f;  // 範囲を出ると、3 社とも破綻の原因になる

  // 画素の単位から NDC（幅 2）の単位へ直す。2.0 / 幅 は XeSS のガイドの式。
  // Y を引くのは、画面の下向きが +Y のため。
  proj.m[2][0] += jitter_x * 2.0f / input_width;
  proj.m[2][1] -= jitter_y * 2.0f / input_height;

  // アップスケーラには、加えた jitter_x と jitter_y を、画素の単位でそのまま渡す。
  // 渡す値と加えた値が食い違うと、静止していても画面が揺れる。
}
```

`proj.m[2][0]` と `[2][1]` に足すのは、遠近の除算の前に、画面の XY をずらすためです。カメラ空間で一度ずらすので、ワールド空間でずらして投影し直すのとは違います。DLSS のガイドも、投影行列の同じ要素に足すと書いています。ただし、DLSS と FSR 2 のガイドには、画素から NDC への換算式が書かれていません。XeSS の式をそのまま当てはめてよいかは、資料で確かめていません。実際に組み込むときは、各 SDK のサンプルを見て確認します。

このコードはコンパイルしていません。`Matrix` は、行ベクトル・左手系の 4×4 行列を想定した仮の型です。

## 入力 {#inputs}

どのアップスケーラも、必要な入力は似ています。

### カラー {#color}

低解像度で描いたシーンの色です。ポストプロセスの前で、HDR のまま渡します。LDR にしてから渡すと、明るい部分の情報が失われて、あとで HDR に戻せません。形式や色空間の条件は各社で少し違います（LDR 入力に対応する SDK もありますが、条件がつきます）。

### 深度 {#depth}

低解像度の深度です。動きベクトルを低解像度で渡すときは、アップスケーラが深度を使って動きベクトルを広げます。リバース Z の向きは、初期化のフラグで伝えます。向きを間違えると、手前と奥が逆に扱われて、輪郭の周りが崩れます。

### 動きベクトル {#motion-vectors}

各画素が前のフレームからどれだけ動いたかです。画質への影響が一番大きい入力です。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="動きベクトルの向き"><defs><marker id="mm" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">動きベクトルは、現在の画素から「前のフレームでの位置」へ向ける</text><line x1="60" y1="150" x2="660" y2="150" stroke="#94a3b8" stroke-width="2"/><line x1="60" y1="144" x2="60" y2="156" stroke="#94a3b8"/><line x1="120" y1="144" x2="120" y2="156" stroke="#94a3b8"/><line x1="180" y1="144" x2="180" y2="156" stroke="#94a3b8"/><line x1="240" y1="144" x2="240" y2="156" stroke="#94a3b8"/><line x1="300" y1="144" x2="300" y2="156" stroke="#94a3b8"/><line x1="360" y1="144" x2="360" y2="156" stroke="#94a3b8"/><line x1="420" y1="144" x2="420" y2="156" stroke="#94a3b8"/><line x1="480" y1="144" x2="480" y2="156" stroke="#94a3b8"/><line x1="540" y1="144" x2="540" y2="156" stroke="#94a3b8"/><line x1="600" y1="144" x2="600" y2="156" stroke="#94a3b8"/><line x1="660" y1="144" x2="660" y2="156" stroke="#94a3b8"/><rect x="180" y="100" width="60" height="40" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="210" y="94" text-anchor="middle" style="font-size:12px;font-weight:400">前フレームの位置</text><rect x="480" y="100" width="60" height="40" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="510" y="94" text-anchor="middle" style="font-size:12px;font-weight:400">現在の位置</text><line x1="480" y1="190" x2="242" y2="190" stroke="currentColor" stroke-width="2" marker-end="url(#mm)"/><text x="360" y="214" text-anchor="middle" style="font-size:13px;font-weight:700">動きベクトル ＝ 前の位置 − 現在の位置（左向き）</text><text x="360" y="236" text-anchor="middle" style="font-size:12px;font-weight:400">右へ 300 ピクセル動いた物体なら、X 成分は −300</text></svg>

向きは、現在の画素から前のフレームの位置へです。1080p で物体が画面の左端から右端へ動いたなら、右端の画素の X 成分は −1080 になります。動く物体・スキンアニメーション・粒子・水面・植物・空まで含めて、すべての画素に正しい値が要ります。抜けた所は、残像（ゴースト）やにじみになります。

動きベクトルに、ジッターは含めません。含めるなら、そのことをフラグで SDK に伝えます。形式は、浮動小数点の 2 チャンネルです。整数にすると、画素より細かい動きが失われます。

### ジッターの値 {#jitter-value}

そのフレームで加えたずらし量です。上の「ジッターを加える」のとおり、加えた値と渡す値を一致させます。

### 露出 {#exposure}

明るさの基準です。アップスケーラは履歴を混ぜるので、フレームごとに露出が変わると、混ぜる色の明るさがずれます。露出が合っていないと、ゴースト・ぼやけ・明るさのずれが出ます。渡し方は、1×1 のテクスチャ・値・自動露出のフラグなど、各社で違います。

## 呼び出す位置 {#placement}

FSR 2・DLSS・XeSS のガイドは、どれもトーン マッピングの前に呼ぶ構成です。

<svg class="fig flow" viewBox="0 0 720 180" role="img" aria-label="アップスケーラを呼ぶ位置"><defs><marker id="mf" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">アップスケーラは、トーン マッピングの前に呼ぶ（3 社のガイドに共通）</text><rect x="20" y="70" width="120" height="64" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="80" y="102.0" text-anchor="middle" style="font-size:13px;font-weight:600">G バッファ・光</text><text x="80" y="156" text-anchor="middle" style="font-size:12px;font-weight:400">描画解像度</text><line x1="140" y1="102" x2="160" y2="102" stroke="currentColor" stroke-width="2" marker-end="url(#mf)"/><rect x="160" y="70" width="120" height="64" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="220" y="93.5" text-anchor="middle" style="font-size:13px;font-weight:600">SSAO・SSR</text><text x="220" y="110.5" text-anchor="middle" style="font-size:13px;font-weight:600">デノイザー</text><text x="220" y="156" text-anchor="middle" style="font-size:12px;font-weight:400">描画解像度</text><line x1="280" y1="102" x2="300" y2="102" stroke="currentColor" stroke-width="2" marker-end="url(#mf)"/><rect x="300" y="70" width="120" height="64" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="360" y="102.0" text-anchor="middle" style="font-size:13px;font-weight:600">アップスケーラ</text><text x="360" y="156" text-anchor="middle" style="font-size:12px;font-weight:400">描画 → 出力</text><line x1="420" y1="102" x2="440" y2="102" stroke="currentColor" stroke-width="2" marker-end="url(#mf)"/><rect x="440" y="70" width="120" height="64" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="500" y="93.5" text-anchor="middle" style="font-size:13px;font-weight:600">トーン マッピング</text><text x="500" y="110.5" text-anchor="middle" style="font-size:13px;font-weight:600">ブルーム・DOF</text><text x="500" y="156" text-anchor="middle" style="font-size:12px;font-weight:400">出力解像度</text><line x1="560" y1="102" x2="580" y2="102" stroke="currentColor" stroke-width="2" marker-end="url(#mf)"/><rect x="580" y="70" width="120" height="64" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="640" y="102.0" text-anchor="middle" style="font-size:13px;font-weight:600">UI</text><text x="640" y="156" text-anchor="middle" style="font-size:12px;font-weight:400">出力解像度</text><text x="360" y="50" text-anchor="middle" style="font-size:12px;font-weight:400">入力：カラー・深度・動きベクトル・ジッター・露出</text></svg>

FSR 2 の README の図では、SSAO や SSR のような画面空間の処理は、描画解像度のままアップスケールの前に行います。トーン マッピング・ブルーム・被写界深度は、拡大後の出力解像度で行います。UI は、最後に出力解像度で描きます。DLSS のガイドは、できるだけポストプロセスの先頭に置くほど画質が上がると書いています。そのため、その後ろのエフェクトは、描画解像度を前提にしていないか確かめます。

TAA を持つエンジンでは、TAA のパスだけをアップスケーラに差し替えます。TAA を切ると、ジッターや深度の描き方が変わるエンジンがあります。TAA が有効なときに動いていたほかの処理は、そのまま動かします。

## 品質モード {#modes}

描く解像度を、出力の何分の一にするかを決めます。倍率 s は、縦横それぞれの比です。ピクセル数は s² 分の 1 になります。

4K（3840×2160）に出力するときは、倍率 1.5 なら 2560×1440、2.0 なら 1920×1080、3.0 なら 1280×720 で描きます。2.0 倍はピクセル数が 4 分の 1、3.0 倍は 9 分の 1 です。

名前と倍率の対応は、各社で違います。たとえば XeSS の Quality は 1.7 倍ですが、DLSS と FSR の Quality は 1.5 倍です。同じ名前で同じ負荷とは限らないので、ゲームの設定には、倍率を表示するほうが親切です。一覧は [Upscaler Comparison](comparison.md#scale) にあります。

## 3 つの選び方 {#choose}

- [FSR](fsr.md): AMD。FSR 3 のアップスケールは、DirectX 12 と Vulkan に対応します
- [DLSS](dlss.md): NVIDIA。RTX の GPU が必要です
- [XeSS](xess.md): Intel。Arc 向けの最適化された実装と、Shader Model 6.4 の他社 GPU 向けの実装があります

複数をゲームに入れるなら、入力（カラー・深度・動きベクトル・露出・ジッター）は共通なので、描画側の準備を 1 回にして、後ろで切り替えられます。NVIDIA の Streamline のような抽象化レイヤーもあります（このページでは、読んだ資料には書かれていないので、詳しくは説明しません）。

## よくあるミス {#mistakes}

??? failure "動く物体の後ろに残像が出る"
    動きベクトルが、動く物体の分（スキンメッシュ・粒子・植物）で抜けています。すべての描画パスで、動きベクトルのバッファに書き込みます。各社のデバッグ表示で、ベクトルの欠けを確かめます。

??? failure "画面全体が揺れる"
    SDK に渡したジッターと、投影行列に加えた量が違います。単位（画素か NDC か）と符号を、渡す側と受ける側でそろえます。

??? failure "静止した場面でも、細い線がぼやける・ちらつく"
    位相数が足りません。倍率が大きいほど長い列が要ります。SDK の関数から位相数を取ります。

??? failure "カット シーンの後に、前の場面が残る"
    場面が切り替わるフレームで、履歴のリセットを立てていません。各 SDK に、リセットのフラグがあります。

## これだけ覚える {#summary}

- 低解像度で描いて拡大する。時間方式は、ジッターと動きベクトルで過去のフレームのサンプルを集める
- ジッターは [-0.5, 0.5] の範囲で、位相数は 8 × 倍率² が目安。加えた値と渡す値を一致させる
- 動きベクトルの質が画質を決める。向きは「現在 → 前」で、ジッターは含めない
- アップスケールはトーン マッピングの前、UI は後

## 参考資料 {#references}

- Intel. "Intel XeSS-SR Developer Guide 2.0." [https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html](https://www.intel.com/content/www/us/en/developer/articles/technical/xess-sr-developer-guide.html)
- AMD GPUOpen. "FidelityFX Super Resolution 2 (FSR 2)." [https://github.com/GPUOpen-Effects/FidelityFX-FSR2](https://github.com/GPUOpen-Effects/FidelityFX-FSR2)
- NVIDIA. "NVIDIA DLSS Super Resolution Programming Guide." 2026 年 3 月 31 日付. [https://github.com/NVIDIA/DLSS](https://github.com/NVIDIA/DLSS)
    - 倍率・位相数・動きベクトルの向き・呼び出す位置は、この 3 つの資料を読んだ内容です。読んだ範囲は、各社のページの参考資料の節にあります。
    - ハルトン列の説明と、ジッターのコードは、一般的な知識と XeSS の式を組み合わせた説明用で、コンパイルしていません。

## 関連ページ {#related}

- [Upscaler Comparison](comparison.md)
- [FSR](fsr.md)
- [DLSS](dlss.md)
- [XeSS](xess.md)
- [TAA](../antialiasing/taa.md)
- [TAA, Upscaling and VRS Cost](../taa-upscaling-cost.md)

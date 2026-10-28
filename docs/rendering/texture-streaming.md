---
title: テクスチャとストリーミング
tags:
  - 最適化
  - 3Dゲーム
---

# テクスチャとストリーミング

テクスチャは、VRAM の容量と帯域幅を最も多く使うデータです。1 枚の 4096×4096・RGBA8 は約 64 MB（ミップを含めて約 85 MB）あり、これを数百枚置けば VRAM はすぐにあふれます。このページでは、テクスチャの**圧縮・ミップ・ストリーミング**で、VRAM と帯域幅を節約する方法を説明します。

!!! tip "ポイント"
    - テクスチャは<strong>VRAM と帯域幅</strong>の最大の消費者。
    - <strong>圧縮フォーマット（BC）</strong>で、サイズが 1/4〜1/8 になり、帯域も同じ割合で減る。
    - ミップマップは、遠くでキャッシュに乗りやすくする（メモリは約 1.33 倍）。
    - ストリーミングは、画面で必要なミップだけをメモリに置く。
    - 仮想テクスチャは、巨大なテクスチャをタイル単位で扱う。
    - 読み込みが間に合わないとぼやけた画像が見える。

!!! info "このページを読む前に"
    - [描画最適化](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [何が重いのか（ボトルネック）](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## サイズの感覚

| 条件 | サイズ |
| --- | --- |
| 1024×1024 RGBA8（無圧縮） | 4 MB（ミップ込みで約 5.3 MB） |
| 2048×2048 RGBA8 | 16 MB（約 21 MB） |
| 4096×4096 RGBA8 | 64 MB（約 85 MB） |
| 4096×4096 BC7 | 16 MB（約 21 MB） |
| 4096×4096 BC1 | 8 MB（約 10.7 MB） |

PBR の材質 1 つが、アルベド・法線・粗さ・金属・AO の 5 枚を持つと、4K で 5 枚 × 85 MB で約 400 MB になります（無圧縮の場合）。

## 圧縮フォーマット

GPU が**圧縮したまま読める**フォーマットを使います。読み込む量が減るのでメモリと帯域の両方が節約できます。

| 形式 | 圧縮率 | 用途 |
| --- | --- | --- |
| BC1 | 1/8 | 不透明なカラー（アルファなし／1 ビット） |
| BC3 | 1/4 | アルファ付きカラー |
| BC4 | 1/8 | 1 チャンネル（高さ・粗さなど） |
| BC5 | 1/4 | 2 チャンネル（法線の XY） |
| BC6H | 1/4 | HDR |
| BC7 | 1/4 | 高品質なカラー（アルファ付き）。圧縮は遅い |

| 点 | 説明 |
| --- | --- |
| ビルド時に圧縮 | 実行時に圧縮すると遅い。ツールで事前に作る（[ベイク](../optimize/baking.md)） |
| チャンネルの詰め込み | 粗さ・金属・AO を 1 枚の R・G・B に入れて、読み込み回数も減らす |
| 法線は BC5 | XY だけ保存して、Z はシェーダーで計算する |
| 品質の確認 | 圧縮によるブロックノイズを実機で確認する |

## ミップマップ

遠くの面は画面上の 1 ピクセルが元の画像の多くのテクセルに対応します。ミップがないと**離れた場所を読むためキャッシュに乗らず、ちらつきも出ます**。

| 点 | 説明 |
| --- | --- |
| 選ばれるミップ | GPU が UV の微分から自動で選ぶ |
| キャッシュ効率 | 小さなミップは小さく、キャッシュに乗りやすい |
| メモリ | 全ミップで元の約 1.33 倍 |
| 異方性フィルタリング | 斜めに見える面のぼやけを減らす。倍率が高いほど読み込みが増える |

## テクスチャ ストリーミング

全テクスチャの全ミップを常駐させる必要はありません。**画面上で必要な大きさのミップだけ**を VRAM に置きます。

<svg class="fig illust" viewBox="0 0 800 230" role="img" aria-label="ミップ ストリーミング">
<defs><marker id="ts1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">近づくと、大きなミップを追加で読み込む</text>
<rect x="30" y="50" width="60" height="60" fill="rgba(46,160,67,0.4)" stroke="currentColor" stroke-width="2"/><text x="60" y="84" text-anchor="middle" style="font-size:12px">256</text>
<rect x="100" y="70" width="40" height="40" fill="rgba(46,160,67,0.4)" stroke="currentColor" stroke-width="2"/><text x="120" y="94" text-anchor="middle" style="font-size:11px">128</text>
<text x="30" y="140" style="font-size:12px">遠いとき：小さなミップだけ（VRAM 小）</text>
<line x1="330" y1="80" x2="400" y2="80" stroke="currentColor" stroke-width="3" marker-end="url(#ts1)"/><text x="340" y="70" style="font-size:12px">近づく</text>
<rect x="430" y="40" width="130" height="130" fill="rgba(229,170,40,0.4)" stroke="currentColor" stroke-width="2"/><text x="495" y="110" text-anchor="middle" style="font-size:12px">2048</text>
<rect x="570" y="80" width="60" height="60" fill="rgba(76,139,245,0.4)" stroke="currentColor" stroke-width="2"/><text x="600" y="114" text-anchor="middle" style="font-size:12px">1024</text>
<text x="430" y="196" style="font-size:12px">近いとき：大きなミップを読み込んで追加（ディスクから）</text>
</svg>

| 点 | 説明 |
| --- | --- |
| 必要なミップの決定 | 物体の画面での大きさ・距離から計算。GPU のフィードバックを使う方式もある |
| 常駐の予算 | VRAM の予算内で重要なものから高いミップを置く |
| 先読み | カメラの移動方向を予測して、事前に読み込む |
| 最低限のミップ | 小さなミップは常駐させ、読み込みが間に合わない時の代わりにする |
| 非同期読み込み | ディスク読み込みは別スレッドで。待たせない |

## 仮想テクスチャ

地形や大きな世界のテクスチャは、1 枚で数 GB になります。**タイル（ページ）単位**で必要な部分だけを VRAM に置く方式が仮想テクスチャです。

| 点 | 説明 |
| --- | --- |
| ページテーブル | どのタイルが VRAM のどこにあるか |
| フィードバック | 画面で実際に使われたタイルを GPU から集める |
| 利点 | 巨大なテクスチャを扱える。VRAM の使用が一定 |
| 代償 | 実装が複雑。フィルタリングの境界処理が必要 |

<!-- fig:mip-memory:begin -->

<svg class="fig illust motion" data-fig="mip-memory" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-mip-memory" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ミップを使うと、小さく表示される時、小さな絵だけ読める(全体は +33%)</text>
<text x="238" y="114" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">ミップ 0（1024×1024）</text>
<rect x="250" y="90" width="400.0" height="34" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></rect>
<text x="660.0" y="113" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">4.00 MB<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></text>
<text x="238" y="162" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">ミップ 1（512×512）</text>
<rect x="250" y="138" width="100.0" height="34" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1610;0.1613;1.0000" values="0;0;1;1"/></rect>
<text x="360.0" y="161" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">1.00 MB<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1610;0.1613;1.0000" values="0;0;1;1"/></text>
<text x="238" y="210" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">ミップ 2（256×256）</text>
<rect x="250" y="186" width="25.0" height="34" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;1.0000" values="0;0;1;1"/></rect>
<text x="285.0" y="209" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">0.25 MB<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;1.0000" values="0;0;1;1"/></text>
<text x="238" y="258" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">ミップ 3（128×128）</text>
<rect x="250" y="234" width="6.25" height="34" fill="#7c3aed" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3546;0.3548;1.0000" values="0;0;1;1"/></rect>
<text x="266.25" y="257" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">64 KB<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3546;0.3548;1.0000" values="0;0;1;1"/></text>
<text x="238" y="306" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">ミップ 4（64×64）</text>
<rect x="250" y="282" width="3.0" height="34" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></rect>
<text x="263.0" y="305" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">16 KB<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="238" y="354" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">ミップ 5（32×32）</text>
<rect x="250" y="330" width="3.0" height="34" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5481;0.5484;1.0000" values="0;0;1;1"/></rect>
<text x="263.0" y="353" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">4 KB<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5481;0.5484;1.0000" values="0;0;1;1"/></text>
<text x="390" y="400" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1024×1024 の画像（1 画素 4 バイト）<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="400" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ミップ 0: 4 MB<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.1933;0.1935;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="400" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 段下がるごとに、縦横が半分 → 容量は 1/4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1933;0.1935;0.6126;0.6129;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="400" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">全部足しても約 5.33 MB（元の 4/3 倍）。遠い物は、小さい層だけ読めばよい<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6126;0.6129;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:mip-memory:end -->

## 圧縮後の、大きさを計算する

BC 圧縮は、4×4 ピクセルの<strong>ブロック</strong>ごとに、決まったバイト数で保存します。大きさは、計算で出せます。

| 形式 | 1 ブロック（4×4 = 16 ピクセル）のバイト数 | 1 ピクセルあたり |
| --- | --- | --- |
| BC1、BC4 | 8 バイト | 4 ビット（0.5 バイト） |
| BC3、BC5、BC6H、BC7 | 16 バイト | 8 ビット（1 バイト） |
| RGBA8（無圧縮） | — | 32 ビット（4 バイト） |

```cpp
// 圧縮テクスチャの、1 つのミップの大きさ（バイト）。幅・高さは、4 ピクセル単位に切り上げる。
size_t BlockCompressedSize(uint32_t width, uint32_t height, size_t bytes_per_block) {
  const size_t blocks_x = std::max<size_t>(1, (width + 3) / 4);
  const size_t blocks_y = std::max<size_t>(1, (height + 3) / 4);
  return blocks_x * blocks_y * bytes_per_block;
}

// 全ミップの合計（1×1 まで）。ミップを足すと、元の約 1.33 倍。
size_t TotalMipSize(uint32_t width, uint32_t height, size_t bytes_per_block) {
  size_t total = 0;
  for (;;) {
    total += BlockCompressedSize(width, height, bytes_per_block);
    if (width == 1 && height == 1) break;
    width = std::max(1u, width / 2);
    height = std::max(1u, height / 2);
  }
  return total;
}
// 例: 4096×4096 の BC7（16 バイト/ブロック）→ 約 21 MB。RGBA8 の無圧縮（約 85 MB）の 1/4。
```

## 必要なミップを決める

ストリーミングの核心は、「<strong>この物体にどのミップが必要か</strong>」を決めることです。画面上で、1 ピクセルがテクスチャの、何テクセルに当たるかで決まります。

```cpp
// 物体の、画面上の大きさから、必要なミップを求める。
// texture_size: テクスチャの 1 辺（テクセル）。uv_density: 物体の 1 メートルあたりの UV の長さ。
float RequiredMip(float texture_size, float uv_density, float distance, float screen_height_px, float fov_y) {
  // 距離 distance での、1 ピクセルが覆う、ワールドの長さ。
  const float meters_per_pixel = 2.0f * distance * std::tan(fov_y * 0.5f) / screen_height_px;
  // 1 ピクセルがテクスチャの何テクセルに当たるか。
  const float texels_per_pixel = meters_per_pixel * uv_density * texture_size;
  return std::max(0.0f, std::log2(texels_per_pixel));        // 1 テクセル/ピクセルなら、ミップ 0。2 倍で、ミップ 1。
}
```

たとえば、1080p、縦の視野 60°、距離 10 m では、1 ピクセルが約 0.011 m です。1 m に 1 周する、4096 のテクスチャなら、1 ピクセル ≒ 45 テクセルで、ミップは `log2(45) ≈ 5.5`、つまり、ミップ 5（128×128）以下で足りることになります。

## 予算内で、ミップを割り当てる

必要なミップが決まったら、VRAM の予算内で、<strong>見た目への効きが大きい物から</strong>、高いミップを割り当てます。

```cpp
struct StreamedTexture {
  float required_mip;          // 今、画面で必要なミップ（小さいほど細かい）
  int resident_mip;            // 今、VRAM に置いてあるミップ
  int lowest_mip;              // 常駐させる、最も粗いミップ（読み込みが、間に合わない時の代わり）
  size_t SizeAtMip(int mip) const;   // そのミップ以下を全部置くときの、大きさ
};

// 毎フレーム（または、数フレームに 1 回）: 予算に収まるよう、各テクスチャの、目標のミップを決める。
void UpdateStreaming(std::vector<StreamedTexture>& textures, size_t budget_bytes) {
  // ① まず、全テクスチャを最低限のミップ（小さい）にする。
  size_t used = 0;
  for (auto& t : textures) {
    t.target_mip = t.lowest_mip;
    used += t.SizeAtMip(t.target_mip);
  }
  // ② 必要なミップに近づける。画面で大きい（required_mip が小さい）物から、1 段ずつ、細かくする。
  bool changed = true;
  while (changed) {
    changed = false;
    for (auto& t : SortedByPriority(textures)) {            // 優先: 画面で、大きく映る物から
      const int wanted = static_cast<int>(std::floor(t.required_mip));
      if (t.target_mip <= wanted) continue;                 // すでに、必要な細かさ
      const size_t extra = t.SizeAtMip(t.target_mip - 1) - t.SizeAtMip(t.target_mip);
      if (used + extra > budget_bytes) continue;            // 予算オーバーなら、細かくしない
      --t.target_mip;
      used += extra;
      changed = true;
    }
  }
  // ③ target_mip と resident_mip を比べて、足りない分は、非同期に読み込み、余った分は、解放する。
}
```

予算内で、足りなければ、遠くや、小さい物の、ミップを下げます。画面に大きく映る物は、細かいミップが確保されます。読み込みは、別スレッドで、ディスクから行い、完了したら、`resident_mip` を更新します。

## ストリーミングの、実装上の、注意

| 注意 | 内容 |
| --- | --- |
| ポップイン | 読み込みが間に合わず、ぼやけた画像から、急に細かい画像に切り替わる。ミップ バイアスを徐々に変えて、なじませる |
| ヒステリシス | 境目で、上げ下げを繰り返すと、読み込みが、止まらない。下げるのは、少し遅らせる |
| 最低ミップの常駐 | 小さいミップ（たとえば 64×64 以下）は、常に VRAM に置いて、読み込みが間に合わないときの、保険にする |
| ミップ チェーンの、ファイル配置 | 小さいミップをファイルの先頭に置くと、先に読める。細かいミップだけを後から、追加で読める |
| 先読み | カメラの移動方向や、場面の切り替えを予測して、事前に、読み込む |

D3D12 には、ミップ単位で、メモリを確保・解放できる、<strong>予約リソース</strong>（Reserved Resource、タイルド リソース）の機能があり、GPU が、一部のミップだけをメモリに持てます。仮想テクスチャの土台でもあります（[Texture Upload](../directx/dx12/texture-upload.md)）。

## よくあるミス

??? failure "全テクスチャを無圧縮・全ミップで常駐させる"
    VRAM があふれます。圧縮とストリーミングを使います。

??? failure "実行時にテクスチャを圧縮する"
    遅い処理です。ビルド時に圧縮します。

??? failure "必要以上に大きなテクスチャを使う"
    画面で映る大きさに見合ったサイズにします。小物に 4K は不要です。

??? failure "読み込みが間に合わず、ぼやけた状態が長く続く"
    先読みと常駐させる最低ミップを見直します。

??? failure "法線マップを BC1 で圧縮して、模様が出る"
    法線は BC5 にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] テクスチャは<strong>VRAM と帯域</strong>の最大の消費者
    - [x] BC 圧縮で 1/4〜1/8。ビルド時に圧縮する
    - [x] ミップでキャッシュ効率が上がり、ちらつきも減る
    - [x] ストリーミングは、必要なミップだけを常駐させる
    - [x] 巨大なものは仮想テクスチャ（タイル単位）

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [メモリ帯域幅](bandwidth.md)
- [メッシュとテクスチャ](../3d/mesh-textures.md)
- [PBR](../3d/pbr.md)
- [ベイク](../optimize/baking.md)

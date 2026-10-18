---
title: ロード時間・起動時間
tags:
  - 最適化
---

# ロード時間・起動時間

ゲームは**起動してから遊べるまで**と、**ステージの切り替え**でデータを読み込む時間がかかります。フレームの速さ（FPS）の最適化とは別に**待たせない**ための最適化が必要です。ロード時間はプレイヤーの印象に直接かかわります。ロードが長いとそれだけで「重いゲーム」と思われます。ロードが遅い原因は、**ファイルを読む時間**だけでなく、**読んだデータを解析する時間**（JSON を読む、画像をデコードする）、**メモリを確保する時間**、**GPU にデータを送る時間**など、いくつもあります。このページはそれぞれの原因と対策をまとめます。

!!! tip "ポイント"
    - まず<strong>ロードの内訳を測る</strong>。ファイルの読み込み、解析、確保、GPU への転送のうち、どこが遅いか。
    - <strong>JSON などのテキストは、ビルド時にバイナリに変換</strong>して、実行時はバイナリを読む。
    - <strong>ファイルを減らす</strong>（1 つにまとめる）、<strong>圧縮</strong>する。小さなファイルを大量に読むのが一番遅い。
    - <strong>別スレッドで読み込み</strong>（非同期）、読み込み中も画面を止めない。
    - 必要なものだけ<strong>先に・遅延して</strong>読む。最初のステージに要らないものは、あとで。

## ロードの内訳

<svg class="fig flow" viewBox="0 0 991 112" role="img" aria-label="ロードの流れ"><defs><marker id="fl87013" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ロードの流れ</text><line x1="256.0" y1="64.0" x2="314.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl87013)"/><line x1="503.0" y1="64.0" x2="561.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl87013)"/><line x1="663.0" y1="64.0" x2="721.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl87013)"/><line x1="826.0" y1="64.0" x2="884.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl87013)"/><rect x="28.0" y="44.0" width="225" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="140.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ファイルを開く・読む （I/O）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="317.0" y="44.0" width="183" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="408.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">解析・デコード （CPU）</text><circle cx="319.0" cy="46.0" r="10" fill="#2ea043"/><text x="319.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="564.0" y="44.0" width="96" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="612.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">メモリ確保</text><circle cx="566.0" cy="46.0" r="10" fill="#e5a828"/><text x="566.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="724.0" y="44.0" width="99" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="773.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">GPU へ転送</text><circle cx="726.0" cy="46.0" r="10" fill="#e5484d"/><text x="726.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="887.0" y="44.0" width="76" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="925.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">初期化</text><circle cx="889.0" cy="46.0" r="10" fill="#9664e6"/><text x="889.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text></svg>

| 段階 | 遅い原因 | 対策 |
| --- | --- | --- |
| <strong>ファイルの読み込み（I/O）</strong> | 小さなファイルが大量。HDD のシーク。圧縮なしの巨大ファイル | ファイルをまとめる（パック）。圧縮。SSD |
| **解析・変換** | JSON / XML のパース、画像（PNG）のデコード、モデルの変換 | **バイナリ化**。GPU 向けのフォーマット（BC 圧縮）に事前変換 |
| **メモリ確保** | 要素ごとに `new`。`vector` の再確保 | 先にまとめて確保。アリーナ（[メモリ確保](allocation.md)） |
| **GPU への転送** | テクスチャ・バッファの作成と転送 | 非同期の転送、圧縮テクスチャ |
| **初期化** | シーンの構築、シェーダーのコンパイル、物理の準備 | 事前に済ませる（シェーダーは事前コンパイル）、遅延初期化 |

## 1. まず測る

```cpp
// ロードの各段階を測る（ScopedTimer は「計測」のページ）
void LoadStage(const std::string& path) {
  std::vector<std::byte> bytes;
  { ScopedTimer t("read file");  bytes = ReadFile(path); }
  StageData data;
  { ScopedTimer t("parse");      data = Parse(bytes); }
  { ScopedTimer t("create gpu"); CreateGpuResources(data); }
  { ScopedTimer t("init");       InitStage(data); }
}
```

どの段階が一番長いかで、対策が変わります。**ファイルの読み込みが 5%、JSON のパースが 70%** なら、バイナリ化が一番効きます（[計測](measure.md)）。

## 2. テキストをバイナリにする

JSON や YAML は、人が読める形式ですが**パース（文字を読んで構造を作る）が重い**です。開発中は読みやすさを優先し、**製品版ではビルド時にバイナリへ変換**して、実行時はバイナリを読みます。

<svg class="fig flow" viewBox="0 0 769 196" role="img" aria-label="開発中は人が編集する形式、製品版はバイナリ"><defs><marker id="fl40736" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">開発中は人が編集する形式、製品版はバイナリ</text><line x1="199.9" y1="87.0" x2="317.1" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl40736)"/><text x="258.5" y="100.0" text-anchor="middle" style="font-size:12px">ビルド時に</text><line x1="458.0" y1="125.0" x2="573.5" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl40736)"/><text x="515.8" y="100.0" text-anchor="middle" style="font-size:12px">実行時は、これを読むだけ</text><rect x="28.0" y="44.0" width="202" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="129.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">stage1.json （人が編集）</text><rect x="294.0" y="128.0" width="188" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="388.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">変換ツール （ビルド時）</text><rect x="546.0" y="44.0" width="195" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="643.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">stage1.bin （バイナリ）</text></svg>

| 形式 | 読み込みの速さ | 備考 |
| --- | --- | --- |
| JSON（[nlohmann/json](../libs/serialization/nlohmann-json.md)） | 遅い | 数 MB なら問題ない |
| JSON（[simdjson](../libs/serialization/simdjson.md)） | 速い（数 GB/s） | 読み込み専用 |
| バイナリ（[cereal](../libs/serialization/cereal.md)、[zpp_bits](../libs/serialization/zpp-bits.md)） | 速い | 作り直しが必要 |
| **ゼロコピー**（[cista](../libs/serialization/cista.md)） | **ほぼ一瞬** | メモリマップと組み合わせる。巨大データ向け |

詳しくは [シリアライズ](../engine/serialization/index.md) を見てください。

## 3. ファイルをまとめる・圧縮する

### 小さなファイルを大量に読まない

**ファイルを 1 つ開くコスト**（ファイル システムの処理、ウイルス対策ソフトの検査、HDD のシーク）は、**ファイルの大きさにかかわらず**かかります。1,000 個の小さなファイルより、1 つの大きなファイルのほうが、ずっと速く読めます。

| 方法 | 説明 |
| --- | --- |
| <strong>パック ファイル（アーカイブ）</strong> | たくさんのアセットを、1 つのファイルにまとめる。目次（名前 → ファイル内の位置）で引く |
| **読む順番に並べる** | ステージで使うものを近くに並べて、連続して読める |
| **メモリマップ** | ファイルをメモリのように見せる。必要な部分だけが読まれる |

### 圧縮

| 圧縮 | 特徴 |
| --- | --- |
| **LZ4** | 展開が**非常に速い**。ロード向けの定番。圧縮率は低め |
| <strong>Zstandard（zstd）</strong> | 圧縮率と速さのバランスがよい。vcpkg: `zstd` |
| **zlib / deflate** | 広く使われる。やや遅い |
| **GPU テクスチャ圧縮**（BC フォーマット） | **圧縮したまま GPU に送る**（展開不要）。メモリも減る |

SSD なら、読み込みより展開のほうが遅いことがあります。**測って**決めます。

## 4. 非同期ロード（待たせない）

<strong>読み込みを別スレッドで行い、ゲームの更新・描画は止めません。</strong>

```cpp
// ステージを、別のスレッドで読み込む
std::future<StageData> loading =
    std::async(std::launch::async, [path] { return LoadStageData(path); });

// 読み込み中は、ローディング画面を表示して、ゲームの更新を続ける
void UpdateLoading() {
  UpdateLoadingScreen();                                        // くるくる回るアイコン
  if (loading.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
    StageData data = loading.get();
    StartStage(std::move(data));                                // 完成したデータだけ、メインで使う
  }
}
```

| 設計のポイント | 説明 |
| --- | --- |
| **ロード スレッドは、データを作るだけ** | ゲームの状態は、触らない（[並行処理の設計](../design/practice/concurrency-design.md)） |
| **完成してから、メインに渡す** | `future`、または完成キュー |
| **GPU のリソース作成** | API によって、スレッドの制限がある（DirectX 11 は、デバイスは複数スレッドから作れる。コンテキストは 1 スレッド） |
| **進み具合を、atomic で伝える** | ロード画面の進捗バー |
| **キャンセルできるように** | `std::stop_token`（`std::jthread`） |

## 5. 先読みと遅延読み込み

| 方法 | 説明 |
| --- | --- |
| <strong>先読み（プリロード）</strong> | 次のステージ・次の部屋のデータを遊んでいる間に裏で読み込んでおく |
| **遅延読み込み** | 最初の画面に要らないものは、遊び始めてから読み込む |
| **ストリーミング** | 広い世界を近づいたエリアだけ、順に読み込む。遠くは解放する |
| **LOD の段階読み込み** | まず低解像度のテクスチャで表示を始めて、あとで高解像度に差し替える |
| **キャッシュ** | 一度読んだものを残して、再読み込みを避ける（[リソース管理](../engine/resource.md)） |

## 6. 起動時間を縮める

| 原因 | 対策 |
| --- | --- |
| **起動時に全アセットを読む** | 最初に必要なものだけ。タイトル画面を先に出し、裏で読む |
| **シェーダーのコンパイル** | **事前コンパイル**（ビルド時に `.cso` を作る）。実行時コンパイルは、起動が遅く、カクつく原因 |
| **初期化順序の依存・重い初期化** | 並列に初期化できるものは、並列に。遅延初期化できるものは、遅らせる |
| **静的変数の初期化**（グローバル オブジェクト） | `main` の前に実行される。重い処理を入れない |
| **大きな DLL の読み込み** | 必要なものだけ。遅延ロード（`/DELAYLOAD`） |
| **ウイルス対策ソフトの検査** | 小さなファイルを減らす。制御はできない |
| **ログ出力・デバッグの処理** | 製品版では無効に |

### シェーダーの事前コンパイル

シェーダーは**実行時にコンパイルすると、数百ミリ秒〜数秒**かかります。ゲームでは**ビルド時に事前コンパイル**（HLSL → `.cso`）して、実行時は読み込むだけにします。Visual Studio では、`.hlsl` ファイルのプロパティ → HLSL コンパイラで、ビルドに組み込めます。

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| ステージの切り替えが遅い | 内訳を測る → バイナリ化、パック、非同期、先読み |
| 起動が遅い | タイトル画面を先に出す。シェーダーを事前コンパイル。重い初期化を遅延 |
| 大きなオープン ワールド | ストリーミング（近いエリアだけ読む）、LOD、圧縮 |
| 2D ゲーム | スプライトのアトラス化（1 枚の画像）、パック |
| セーブデータの読み込み | バイナリ形式（[cereal](../libs/serialization/cereal.md)）。サイズが小さければ、JSON でも十分 |
| ホット リロード（開発中） | 開発中は読み込みを速くするより、**変更をすぐ反映**できるほうを優先 |

<!-- fig:load-gantt:begin -->

<svg class="fig illust motion" data-fig="load-gantt" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-load-gantt" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ロード時間: 順番に待つと 10 秒、並べて進めると 5 秒</text>
<text x="40" y="85" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">順番に実行（1 本のスレッド）</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/><rect x="70" y="105" width="183" height="38" fill="#2563eb" opacity="0.9"/>
<text x="163.0" y="130" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">テクスチャ 3s</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1517;1.0000" values="0;0;1;1"/><rect x="256" y="105" width="121" height="38" fill="#2ea043" opacity="0.9"/>
<text x="318.0" y="130" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">メッシュ 2s</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2342;0.2345;1.0000" values="0;0;1;1"/><rect x="380" y="105" width="121" height="38" fill="#7c3aed" opacity="0.9"/>
<text x="442.0" y="130" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">デコード 2s</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3170;0.3172;1.0000" values="0;0;1;1"/><rect x="504" y="105" width="183" height="38" fill="#e5aa28" opacity="0.9"/>
<text x="597.0" y="130" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">シェーダー 3s</text>
</g>
<text x="40" y="205" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">並べて実行（3 本のスレッド）</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4480;0.4483;1.0000" values="0;0;1;1"/><rect x="70" y="225" width="183" height="38" fill="#2563eb" opacity="0.9"/>
<text x="163.0" y="250" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">テクスチャ 3s</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4756;0.4759;1.0000" values="0;0;1;1"/><rect x="70" y="269" width="121" height="38" fill="#2ea043" opacity="0.9"/>
<text x="132.0" y="294" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">メッシュ 2s</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5032;0.5034;1.0000" values="0;0;1;1"/><rect x="70" y="313" width="183" height="38" fill="#e5aa28" opacity="0.9"/>
<text x="163.0" y="338" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">シェーダー 3s</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5308;0.5310;1.0000" values="0;0;1;1"/><rect x="256" y="269" width="121" height="38" fill="#7c3aed" opacity="0.9"/>
<text x="318.0" y="294" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">デコード 2s</text>
</g>
<text x="690" y="160" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">10 秒<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3790;0.3793;1.0000" values="0;0;1;1"/></text>
<text x="380" y="360" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">5 秒<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;1.0000" values="0;0;1;1"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">デコードは、テクスチャとメッシュが終わってから始める(依存関係)。シェーダーは独立</text>
</svg>

<!-- fig:load-gantt:end -->

## よくあるミス

??? failure "ロードの内訳を測らずに、圧縮ツールを入れる"
    ボトルネックが、JSON のパースやシェーダーのコンパイルにあれば、圧縮しても速くなりません。内訳を見ます。

??? failure "ロード スレッドで、ゲームの状態を触る"
    ゲームのスレッドと同時に、同じデータを書き換えて、データ競争になります。ロード スレッドは、データを作るだけです。

??? failure "SSD でしか測らない"
    プレイヤーが HDD かもしれません。ファイルの数・順番の影響は、HDD で大きく出ます。

??? failure "実行時にシェーダーをコンパイルして、初回だけカクつく"
    新しいマテリアルが出るたびに、ゲームが止まります。事前コンパイルして、読み込み時に準備します（パイプライン状態の事前作成）。

??? failure "ローディング画面が、進まない・固まる"
    読み込みをメイン スレッドで行うと、画面の更新も止まります。非同期にして、画面は動かし続けます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロードの<strong>内訳を測る</strong>（I/O、解析、確保、GPU 転送、初期化）
    - [x] テキストはビルド時に<strong>バイナリ化</strong>。ファイルは<strong>1 つにまとめて</strong>圧縮（LZ4、zstd）
    - [x] ロードは<strong>別スレッドで非同期</strong>に。画面は止めない
    - [x] <strong>先読み・遅延・ストリーミング</strong>で待たせない。起動はタイトル画面を先に
    - [x] シェーダーは<strong>事前コンパイル</strong>

## 関連ページ

- [最適化の進め方](index.md)
- [計測（プロファイリング）](measure.md)
- [シリアライズ](../engine/serialization/index.md)
- [リソース管理](../engine/resource.md)
- [並行処理の設計](../design/practice/concurrency-design.md)
- [simdjson（高速な JSON）](../libs/serialization/simdjson.md)
- [メッシュとテクスチャ（DDS・独自形式）](../3d/mesh-textures.md)

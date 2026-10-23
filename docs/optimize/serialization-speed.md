---
title: シリアライズでロードを速くする
tags:
  - 最適化
---

# シリアライズでロードを速くする

**アセット（ステージ・キャラクター・設定）のロードが遅い**原因の多くは、ファイルの読み込みそのものより、テキスト（JSON・XML）を解析して、メモリ上のデータに作り直す処理です。データの保存形式（シリアライズ）を、バイナリに替えるだけで、ロード時間が何倍も短くなることがあります。このページはロードが遅い理由、形式ごとの速さの目安、選び方をまとめます。シリアライズの仕組み・各ライブラリの使い方は、既存のページに詳しく書いてあるのでそちらへ飛べるようにします。

!!! tip "ポイント"
    - ロードの時間は、<strong>読み込み（I/O）＋ 解析（パース）＋ メモリ確保・変換</strong>。<strong>JSON は解析と確保が重い</strong>。
    - バイナリ形式は、解析がほぼなく、速い。さらに速いのが「ゼロコピー」（読んだメモリをそのまま使う）。
    - 開発中は JSON（読みやすい・直せる）、製品版はバイナリ（ビルド時に変換）が定番（[ベイク](baking.md)）。
    - 速さの順の目安：ゼロコピー（cista・mmap）> 構造体のバイナリ（zpp_bits・struct_pack）> 汎用バイナリ（cereal）> 高速 JSON（simdjson）> 普通の JSON。
    - 測ってから決める。ロードが本当に解析で遅いかを確かめる（[計測](measure.md)）。

## ロードが遅い理由

```text
ファイルを開く・読む（I/O） → 解析・デコード（CPU） → メモリ確保・オブジェクトの作成 → GPU へ転送 → 初期化
```

| 段階 | 遅い原因 |
| --- | --- |
| **I/O** | ディスクの速さ・ファイルが小さく大量（ファイルを開くコスト）・圧縮なしで大きい |
| 解析（パース） | テキストを 1 文字ずつ読んで、意味を解釈する（JSON・XML・YAML）。バイナリなら、ほぼ不要 |
| メモリ確保・作成 | 要素ごとに `new`（`std::string`・`std::vector`・`std::map`）。細かい確保が大量に起きる（[メモリ確保](allocation.md)） |
| 変換 | 文字列の数字を数値に変換する、キーを探す（辞書） |
| GPU への転送 | 頂点・テクスチャを、GPU に送る |

解析とメモリ確保が、CPU 側の主なコストで、これは形式を変えれば、減らせます。

## 形式ごとの違い

| 形式 | 読みやすさ | 速さ | 解析 | 確保 | 向く用途 |
| --- | --- | --- | --- | --- | --- |
| **JSON**（nlohmann/json） | ◎ 人が読める・直せる | △ | あり（重い） | 多い | 設定・開発中のデータ |
| JSON（simdjson） | ◎ | ◎ とても速い解析 | あり（高速） | 少なめ | 大きな JSON を速く読みたい（読み込み専用） |
| YAML（rapidyaml） | ◎ | ○ | あり | 少なめ | 人が書く設定 |
| バイナリ（汎用）（cereal） | × | ○ | 軽い | 要素ごと | セーブデータ・STL 型をそのまま |
| バイナリ（高速）（zpp_bits・struct_pack） | × | ◎ | ほぼなし | 少ない | 構造体を速く保存・読み込み |
| ゼロコピー（cista・mmap） | × | ◎◎ 最速 | なし | なし | 大きなアセット（読んだら、すぐ使える） |

!!! note "速さは、データの形と環境で変わる"
    上の表は目安です。自分のデータで測って比べます。

### 速さの違いの理由

| 形式 | 何が起きるか |
| --- | --- |
| JSON | 文字を 1 つずつ読み、`{` `"` `:` を解釈して、木を作る。数値は文字列から変換。文字列は確保・コピー |
| 汎用バイナリ（cereal） | 決まった順に値を読み出す。`vector` や `string` は、確保して作り直す |
| 高速バイナリ（zpp_bits） | 構造体の中身をほぼ `memcpy`。`vector` の確保は、必要 |
| ゼロコピー（cista・mmap） | ファイルをメモリに読む（またはマップ）して、そのメモリをそのまま構造体として使う。作り直しもコピーもない |

ゼロコピーはポインタの代わりにオフセット（自分からの距離）を使って、どこに読み込まれても使えるようにします（[cista](../libs/serialization/cista.md)、[ポインタをインデックスに](data-layout.md)）。

## 速くするための選び方

| 状況 | 選ぶもの |
| --- | --- |
| **設定ファイル・小さなデータ**（ロードの時間が問題でない） | JSON（nlohmann/json）。読みやすさを優先 |
| 大きな JSON を速く読みたい（既存の JSON を変えられない） | simdjson（[simdjson](../libs/serialization/simdjson.md)） |
| セーブデータ | cereal・zpp_bits（バージョン管理に注意）（[cereal](../libs/serialization/cereal.md)、[zpp_bits](../libs/serialization/zpp-bits.md)） |
| 構造体をできるだけ速く保存・読み込み | zpp_bits・struct_pack（[struct_pack](../libs/serialization/struct-pack.md)） |
| 巨大なアセット（ステージ・ナビメッシュ・コリジョン） | ゼロコピー（[cista](../libs/serialization/cista.md)）。ビルド時にバイナリへ変換 |
| 人が編集するデータ（敵のパラメータ） | 開発中は JSON・YAML、製品版はビルド時にバイナリへ変換 |

### 「開発中は JSON、製品版はバイナリ」

編集しやすさとロードの速さを両立する定番の方法です。

<svg class="fig flow" viewBox="0 0 979 112" role="img" aria-label="開発中は人が編集できる JSON、製品版は、ビルド時に変換したバイナリを読む"><defs><marker id="fl70378" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">開発中は人が編集できる JSON、製品版は、ビルド時に変換したバイナリを読む</text><line x1="233.0" y1="64.0" x2="291.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl70378)"/><text x="262.0" y="58.0" text-anchor="middle" style="font-size:12px">ビルド時</text><line x1="485.0" y1="64.0" x2="543.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl70378)"/><text x="514.0" y="58.0" text-anchor="middle" style="font-size:12px">出力</text><line x1="744.0" y1="64.0" x2="802.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl70378)"/><text x="773.0" y="58.0" text-anchor="middle" style="font-size:12px">読むだけ</text><rect x="28.0" y="44.0" width="202" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="129.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">stage1.json （人が編集）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="294.0" y="44.0" width="188" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="388.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">変換ツール （ビルド時）</text><circle cx="296.0" cy="46.0" r="10" fill="#2ea043"/><text x="296.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="546.0" y="44.0" width="195" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="643.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">stage1.bin （バイナリ）</text><circle cx="548.0" cy="46.0" r="10" fill="#2ea043"/><text x="548.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="805.0" y="44.0" width="146" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="878.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム （製品版）</text><circle cx="807.0" cy="46.0" r="10" fill="#e5a828"/><text x="807.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| 手順 | 内容 |
| --- | --- |
| 開発中 | JSON を人が編集。ゲームは、JSON を直接読む（またはホットリロード） |
| ビルド時 | 変換ツールが、JSON を読み、バイナリに変換（[ベイク](baking.md)） |
| 製品版 | バイナリを読むだけ。JSON の解析なし |

同じデータ構造（構造体）を、JSON とバイナリの両方で、読み書きできるようにしておくと、切り替えが簡単です（[シリアライズ](../engine/serialization/index.md)）。

## 速くする、そのほかの工夫

シリアライズの形式を替える以外にも、**ロードを速く**する方法があります（詳しくは、[ロード時間・起動時間](loading.md)）。

| 工夫 | 説明 |
| --- | --- |
| 非同期ロード | ロードを別スレッドで行い、画面を止めない |
| ファイルをまとめる（パッケージ） | 小さなファイルを、1 つにまとめる（ファイルを開く回数を減らす） |
| 圧縮 | ファイルを小さく（I/O が減る）。展開の速い形式（LZ4・zstd）を選ぶ |
| `mmap`（メモリ マップ） | ファイルをメモリのように扱う。読み込みのコピーがない（Windows は `CreateFileMapping`） |
| ストリーミング | 必要になる直前に必要な部分だけを読む |
| ロード中に使う、メモリの確保を減らす | アリーナ（[リニアアロケータ](allocators/linear.md)）で、まとめて確保 |
| GPU 用データは、そのまま転送できる形に | 頂点・テクスチャを変換せず、バッファへ（DDS など） |

### メモリ確保を減らす

要素ごとに `new` する、`std::vector<std::string>` のような構造は、ロード時に大量の確保が起きます。ロード専用のリニアアロケータにまとめて確保し、ロード後にまとめて捨てると確保が数回になります（[リニアアロケータ](allocators/linear.md)、[STL との接続](allocators/stl-adapter.md)）。

## 注意点

| 注意 | 説明 |
| --- | --- |
| **形式の変更に気をつける** | 構造体のメンバを足す・順序を変えると古いファイルが読めなくなる（バージョン番号を付ける）（[シリアライズ](../engine/serialization/index.md)） |
| エンディアン・パディング | 別の環境で書いたバイナリは、読めないことがある |
| ゼロコピーの制約 | ポインタを使えない（オフセットを使う）、構造体のレイアウトが固定される |
| セキュリティ | 信頼できないファイル（ユーザーが作ったデータ・ネットワーク）を、検証せずに読むと危険。サイズや範囲を確認 |
| デバッグしにくい | バイナリは人が読めない。ダンプ ツール（バイナリ → テキスト）を用意する |

## 測る

**シリアライズが本当にロードのボトルネックか**を、先に確かめます。

| 方法 | 説明 |
| --- | --- |
| ロードの各段階をタイマーで測る | 読み込み・解析・確保・GPU 転送のそれぞれの時間（[計測](measure.md)） |
| プロファイラー | 解析の関数（JSON のパーサー）が、上位に出るか（[プロファイラー](../vs/profiler.md)） |
| 形式を替えて、比べる | 同じデータを、JSON・バイナリで読み込み時間を比較 |
| Release で測る | Debug は、数倍遅い |
| キャッシュの影響 | 2 回目以降は、OS のファイルキャッシュで速い。初回（コールド）を、測る |

## よくあるミス

??? failure "ロードが遅いと思って、シリアライズを替えたが、本当は I/O（ディスク）が遅かった"
    **測ってから**。段階ごとに時間を測ります。

??? failure "製品版でも、JSON を解析している"
    ビルド時にバイナリへ変換します（[ベイク](baking.md)）。

??? failure "バイナリの形式を変えて、古いセーブデータが読めなくなる"
    バージョン番号を付け、古い形式を読める（または変換できる）ようにします。

??? failure "ゼロコピーで、ポインタを保存した"
    アドレスは読み込むたびに変わるので、無効です。オフセット・インデックスにします。

??? failure "巨大な `std::vector<std::string>` を、1 つずつ読み込んで確保が大量になる"
    ロード専用のアリーナを使うか、文字列を、1 つの塊にまとめた形式にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロードが遅い主因は<strong>テキストの解析と、細かいメモリ確保</strong>
    - [x] バイナリ形式で、解析をほぼなくせる。ゼロコピー（cista・mmap）が最速
    - [x] 開発中は JSON、製品版はビルド時にバイナリへ変換（ベイク）
    - [x] 選び方：設定 ＝ JSON、高速 JSON ＝ simdjson、構造体 ＝ zpp_bits・struct_pack、巨大アセット ＝ cista
    - [x] 形式は、バージョン番号付き。測ってから決める

## 関連ページ

- [最適化の進め方](index.md)
- [ベイク（事前計算）](baking.md)
- [ロード時間・起動時間](loading.md)
- [シリアライズ（ゲームエンジン）](../engine/serialization/index.md)
- [nlohmann/json](../libs/serialization/nlohmann-json.md)
- [simdjson](../libs/serialization/simdjson.md)
- [cereal](../libs/serialization/cereal.md)
- [zpp_bits](../libs/serialization/zpp-bits.md)
- [struct_pack](../libs/serialization/struct-pack.md)
- [cista](../libs/serialization/cista.md)
- [rapidyaml](../libs/serialization/rapidyaml.md)

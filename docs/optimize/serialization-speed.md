---
title: シリアライズでロードを速くする
tags:
  - 最適化
---

# シリアライズでロードを速くする

**アセット（ステージ・キャラクター・設定）のロードが遅い**原因の多くは、**ファイルの読み込みそのもの**より、**テキスト（JSON・XML）を解析して、メモリ上のデータに作り直す処理**です。**データの保存形式（シリアライズ）を、バイナリに替える**だけで、**ロード時間が、何倍も短く**なることがあります。このページは、**ロードが遅い理由**、**形式ごとの速さの目安**、**選び方**を、まとめます。**シリアライズの仕組み・各ライブラリの使い方**は、**既存のページ**に、詳しく書いてあるので、**そちらへ飛べる**ようにします。

!!! tip "ポイント"
    - ロードの時間は、<strong>読み込み（I/O）＋ 解析（パース）＋ メモリ確保・変換</strong>。<strong>JSON は、解析と確保が、重い</strong>。
    - <strong>バイナリ形式</strong>は、<strong>解析がほぼなく、速い</strong>。<strong>さらに速いのが「ゼロコピー」</strong>（読んだメモリを、そのまま使う）。
    - <strong>開発中は JSON（読みやすい・直せる）</strong>、<strong>製品版はバイナリ</strong>（<strong>ビルド時に変換</strong>）が定番（[ベイク](baking.md)）。
    - <strong>速さの順</strong>の目安：<strong>ゼロコピー（cista・mmap）> 構造体のバイナリ（zpp_bits・struct_pack）> 汎用バイナリ（cereal）> 高速 JSON（simdjson）> 普通の JSON</strong>。
    - <strong>測ってから</strong>決める。<strong>ロードが、本当に解析で遅いか</strong>を、確かめる（[計測](measure.md)）。

## ロードが遅い理由

```text
ファイルを開く・読む（I/O） → 解析・デコード（CPU） → メモリ確保・オブジェクトの作成 → GPU へ転送 → 初期化
```

| 段階 | 遅い原因 |
| --- | --- |
| **I/O** | **ディスクの速さ**・**ファイルが、小さく大量**（ファイルを開くコスト）・**圧縮なしで大きい** |
| <strong>解析（パース）</strong> | **テキストを 1 文字ずつ読んで、意味を解釈**する（**JSON・XML・YAML**）。**バイナリなら、ほぼ不要** |
| **メモリ確保・作成** | **要素ごとに `new`**（`std::string`・`std::vector`・`std::map`）。**細かい確保が、大量に起きる**（[メモリ確保](allocation.md)） |
| **変換** | **文字列の数字を、数値に**変換する、**キーを探す**（辞書） |
| **GPU への転送** | **頂点・テクスチャ**を、GPU に送る |

**解析と、メモリ確保**が、**CPU 側の主なコスト**で、**これは、形式を変えれば、減らせます**。

## 形式ごとの違い

| 形式 | 読みやすさ | 速さ | 解析 | 確保 | 向く用途 |
| --- | --- | --- | --- | --- | --- |
| **JSON**（nlohmann/json） | **◎ 人が読める・直せる** | △ | <strong>あり（重い）</strong> | **多い** | **設定・開発中のデータ** |
| <strong>JSON（simdjson）</strong> | ◎ | **◎ とても速い解析** | <strong>あり（高速）</strong> | 少なめ | **大きな JSON を、速く読みたい**（読み込み専用） |
| **YAML**（rapidyaml） | ◎ | ○ | あり | 少なめ | 人が書く設定 |
| <strong>バイナリ（汎用）</strong>（cereal） | × | ○ | **軽い** | 要素ごと | **セーブデータ**・STL 型をそのまま |
| <strong>バイナリ（高速）</strong>（zpp_bits・struct_pack） | × | **◎** | **ほぼなし** | 少ない | **構造体を、速く保存・読み込み** |
| **ゼロコピー**（cista・mmap） | × | **◎◎ 最速** | **なし** | **なし** | **大きなアセット**（読んだら、すぐ使える） |

!!! note "速さは、データの形と、環境で変わる"
    **上の表は、目安**です。**自分のデータで、測って**比べます。

### 速さの違いの理由

| 形式 | 何が起きるか |
| --- | --- |
| **JSON** | **文字を 1 つずつ読み、`{` `"` `:` を解釈**して、**木を作る**。**数値は、文字列から変換**。**文字列は、確保・コピー** |
| **汎用バイナリ**（cereal） | **決まった順に、値を読み出す**。**`vector` や `string` は、確保して作り直す** |
| **高速バイナリ**（zpp_bits） | **構造体の中身を、ほぼ `memcpy`**。**`vector` の確保は、必要** |
| **ゼロコピー**（cista・mmap） | <strong>ファイルを、メモリに読む（またはマップ）</strong>して、**そのメモリを、そのまま構造体として使う**。**作り直しも、コピーもない** |

**ゼロコピー**は、<strong>ポインタの代わりに、オフセット（自分からの距離）</strong>を使って、**どこに読み込まれても、使える**ようにします（[cista](../libs/serialization/cista.md)、[ポインタをインデックスに](data-layout.md)）。

## 速くするための、選び方

| 状況 | 選ぶもの |
| --- | --- |
| **設定ファイル・小さなデータ**（ロードの時間が、問題でない） | <strong>JSON（nlohmann/json）</strong>。**読みやすさを優先** |
| **大きな JSON を、速く読みたい**（既存の JSON を、変えられない） | **simdjson**（[simdjson](../libs/serialization/simdjson.md)） |
| **セーブデータ** | **cereal**・**zpp_bits**（バージョン管理に注意）（[cereal](../libs/serialization/cereal.md)、[zpp_bits](../libs/serialization/zpp-bits.md)） |
| **構造体を、できるだけ速く保存・読み込み** | **zpp_bits・struct_pack**（[struct_pack](../libs/serialization/struct-pack.md)） |
| <strong>巨大なアセット（ステージ・ナビメッシュ・コリジョン）</strong> | **ゼロコピー**（[cista](../libs/serialization/cista.md)）。**ビルド時に、バイナリへ変換** |
| <strong>人が編集するデータ（敵のパラメータ）</strong> | **開発中は JSON・YAML、製品版は、ビルド時に、バイナリへ変換** |

### 「開発中は JSON、製品版はバイナリ」

**編集しやすさ**と、**ロードの速さ**を、**両立する定番の方法**です。

<svg class="fig flow" viewBox="0 0 979 112" role="img" aria-label="開発中は人が編集できる JSON、製品版は、ビルド時に変換したバイナリを読む"><defs><marker id="fl70378" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">開発中は人が編集できる JSON、製品版は、ビルド時に変換したバイナリを読む</text><line x1="233.0" y1="64.0" x2="291.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl70378)"/><text x="262.0" y="58.0" text-anchor="middle" style="font-size:12px">ビルド時</text><line x1="485.0" y1="64.0" x2="543.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl70378)"/><text x="514.0" y="58.0" text-anchor="middle" style="font-size:12px">出力</text><line x1="744.0" y1="64.0" x2="802.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl70378)"/><text x="773.0" y="58.0" text-anchor="middle" style="font-size:12px">読むだけ</text><rect x="28.0" y="44.0" width="202" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="129.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">stage1.json （人が編集）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="294.0" y="44.0" width="188" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="388.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">変換ツール （ビルド時）</text><circle cx="296.0" cy="46.0" r="10" fill="#2ea043"/><text x="296.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="546.0" y="44.0" width="195" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="643.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">stage1.bin （バイナリ）</text><circle cx="548.0" cy="46.0" r="10" fill="#2ea043"/><text x="548.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="805.0" y="44.0" width="146" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="878.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム （製品版）</text><circle cx="807.0" cy="46.0" r="10" fill="#e5a828"/><text x="807.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| 手順 | 内容 |
| --- | --- |
| **開発中** | **JSON を、人が編集**。**ゲームは、JSON を直接読む**（またはホットリロード） |
| **ビルド時** | **変換ツール**が、**JSON を読み、バイナリに変換**（[ベイク](baking.md)） |
| **製品版** | **バイナリを、読むだけ**。**JSON の解析なし** |

<strong>同じデータ構造（構造体）</strong>を、**JSON とバイナリの両方で、読み書き**できるようにしておくと、**切り替えが、簡単**です（[シリアライズ](../engine/serialization/index.md)）。

## 速くする、そのほかの工夫

シリアライズの形式を替える以外にも、**ロードを速く**する方法があります（詳しくは、[ロード時間・起動時間](loading.md)）。

| 工夫 | 説明 |
| --- | --- |
| **非同期ロード** | **ロードを、別スレッドで**行い、**画面を止めない** |
| <strong>ファイルを、まとめる（パッケージ）</strong> | **小さなファイルを、1 つにまとめる**（ファイルを開く回数を減らす） |
| **圧縮** | **ファイルを、小さく**（I/O が減る）。**展開の速い形式**（LZ4・zstd）を選ぶ |
| <strong>`mmap`（メモリ マップ）</strong> | **ファイルを、メモリのように扱う**。**読み込みのコピーが、ない**（Windows は `CreateFileMapping`） |
| **ストリーミング** | **必要になる直前に、必要な部分だけ**を読む |
| **ロード中に使う、メモリの確保を減らす** | **アリーナ**（[リニアアロケータ](allocators/linear.md)）で、**まとめて確保** |
| **GPU 用データは、そのまま転送できる形**に | **頂点・テクスチャ**を、**変換せず**、バッファへ（DDS など） |

### メモリ確保を減らす

**要素ごとに `new`** する、**`std::vector<std::string>`** のような構造は、**ロード時に、大量の確保**が起きます。**ロード専用の、リニアアロケータ**に、まとめて確保し、**ロード後に、まとめて捨てる**と、**確保が、数回に**なります（[リニアアロケータ](allocators/linear.md)、[STL との接続](allocators/stl-adapter.md)）。

## 注意点

| 注意 | 説明 |
| --- | --- |
| **形式の変更に、気をつける** | **構造体のメンバを足す・順序を変える**と、**古いファイルが、読めなくなる**（**バージョン番号**を付ける）（[シリアライズ](../engine/serialization/index.md)） |
| **エンディアン・パディング** | **別の環境で書いたバイナリは、読めない**ことがある |
| **ゼロコピーの、制約** | **ポインタを使えない**（オフセットを使う）、**構造体のレイアウトが固定**される |
| **セキュリティ** | **信頼できないファイル**（ユーザーが作ったデータ・ネットワーク）を、**検証せずに**読むと、**危険**。**サイズや範囲を確認** |
| **デバッグしにくい** | **バイナリは、人が読めない**。**ダンプ ツール**（バイナリ → テキスト）を用意する |

## 測る

**シリアライズが、本当にロードのボトルネックか**を、**先に確かめます**。

| 方法 | 説明 |
| --- | --- |
| **ロードの各段階を、タイマーで測る** | **読み込み・解析・確保・GPU 転送**の、それぞれの時間（[計測](measure.md)） |
| **プロファイラー** | **解析の関数（JSON のパーサー）が、上位に出るか**（[プロファイラー](../vs/profiler.md)） |
| **形式を替えて、比べる** | **同じデータを、JSON・バイナリで**、読み込み時間を比較 |
| **Release で測る** | **Debug は、数倍遅い** |
| **キャッシュの影響** | **2 回目以降は、OS のファイルキャッシュで速い**。**初回（コールド）を、測る** |

## よくあるミス

??? failure "ロードが遅いと思って、シリアライズを替えたが、本当は I/O（ディスク）が遅かった"
    **測ってから**。**段階ごとに、時間を測ります**。

??? failure "製品版でも、JSON を解析している"
    **ビルド時に、バイナリへ変換**します（[ベイク](baking.md)）。

??? failure "バイナリの形式を変えて、古いセーブデータが、読めなくなる"
    **バージョン番号**を付け、**古い形式を読める**（または、変換できる）ようにします。

??? failure "ゼロコピーで、ポインタを保存した"
    **アドレスは、読み込むたびに変わる**ので、**無効**です。**オフセット・インデックス**にします。

??? failure "巨大な `std::vector<std::string>` を、1 つずつ読み込んで、確保が大量になる"
    **ロード専用のアリーナ**を使うか、**文字列を、1 つの塊にまとめた形式**にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ロードが遅い主因は<strong>テキストの解析と、細かいメモリ確保</strong>
    - [x] <strong>バイナリ形式</strong>で、解析をほぼなくせる。<strong>ゼロコピー（cista・mmap）が最速</strong>
    - [x] <strong>開発中は JSON、製品版は、ビルド時に、バイナリへ変換</strong>（<strong>ベイク</strong>）
    - [x] 選び方：<strong>設定 ＝ JSON</strong>、<strong>高速 JSON ＝ simdjson</strong>、<strong>構造体 ＝ zpp_bits・struct_pack</strong>、<strong>巨大アセット ＝ cista</strong>
    - [x] <strong>形式は、バージョン番号付き</strong>。<strong>測ってから</strong>決める

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

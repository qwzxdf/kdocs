---
title: ビルド時間の最適化
tags:
  - 最適化
---

# ビルド時間の最適化

ビルドが遅いと**コードを直して、動かして、確かめる**サイクルが遅くなり、開発の速さが落ちます。プログラムの実行速度とは別に、ビルド時間も最適化の対象です。C++ はヘッダを何度も読み直すので、特に遅くなりがちです。このページはなぜ遅いか、測り方、効く順に対策（include の整理、プリコンパイル済みヘッダー、並列ビルド、unity ビルド、キャッシュ、モジュール）をまとめます。

!!! tip "ポイント"
    - 遅い原因の大半は、<strong>ヘッダの読み直し</strong>。<strong>同じヘッダを何百回も解析</strong>している。
    - まず測る（どのファイル・どのヘッダが重いか）。勘で直さない。
    - 効果が大きい順：並列ビルド（/MP）→ include を減らす（前方宣言）→ プリコンパイル済みヘッダー → ヘッダ内のテンプレートを減らす → キャッシュ・モジュール。
    - ヘッダに重い物（`<windows.h>` 全部、`<regex>`、`<iostream>`）を入れない。
    - Debug のビルドを、速くする（日々の開発で一番使う）。Release の LTCG は、遅くてよい（CI で）。

## なぜ遅いのか

<svg class="fig flow" viewBox="0 0 417 280" role="img" aria-label="同じヘッダを、すべての .cpp が読み直す"><defs><marker id="fl51929" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">同じヘッダを、すべての .cpp が読み直す</text><line x1="107.0" y1="80.2" x2="220.3" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl51929)"/><text x="163.7" y="96.6" text-anchor="middle" style="font-size:12px">#include</text><line x1="107.0" y1="148.0" x2="165.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl51929)"/><text x="136.0" y="142.0" text-anchor="middle" style="font-size:12px">#include</text><line x1="107.0" y1="215.8" x2="220.3" y2="171.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl51929)"/><text x="163.7" y="187.4" text-anchor="middle" style="font-size:12px">#include</text><rect x="28.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">A.cpp</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="168.0" y="128.0" width="221" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="278.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">big.h （100回、解析・展開）</text><circle cx="170.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="170.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="28.0" y="128.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="66.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">B.cpp</text><circle cx="30.0" cy="130.0" r="10" fill="#2ea043"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="28.0" y="212.0" width="76" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="66.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">C.cpp</text><circle cx="30.0" cy="214.0" r="10" fill="#e5a828"/><text x="30.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| 原因 | 説明 |
| --- | --- |
| **ヘッダの多重読み込み** | 各 `.cpp` がヘッダを自分で読み込む。1 個のヘッダが全 `.cpp` ぶん解析される |
| ヘッダの連鎖 | `a.h` → `b.h` → `c.h` ... と、芋づる式に増える |
| 重い標準ヘッダ | `<regex>`、`<iostream>`、`<algorithm>`、`<ranges>`、`<format>` は、読み込みが重い |
| テンプレートの展開 | 同じテンプレートを`.cpp` ごとにインスタンス化する |
| インライン関数・巨大な `constexpr` | ヘッダに書くと全員が解析する |
| リンク時コード生成（LTCG） | リリースの最適化。リンクが非常に遅くなる |
| ディスク・ウイルス対策 | ファイルを大量に読むので、遅い環境ではさらに遅い |

## 測る

「何が遅いか」を、数字で見ます。

| 方法 | 説明 |
| --- | --- |
| **ビルドの総時間** | Visual Studio の出力に、経過時間が出る。まず、これを記録 |
| `/Bt+`（コンパイラの時間表示） | `.cpp` ごとのフロントエンド・バックエンドの時間 |
| `/d1reportTime` | どのヘッダが何秒かかったか（include の時間） |
| C++ Build Insights（`vcperf`） | ビルド全体の流れをタイムラインで見る。Windows Performance Analyzer で開く |
| Ninja の `.ninja_log` | `ninja -d stats`、`ninjatracing` で、遅いファイルを探す |
| ClangBuildAnalyzer | Clang 向け。ヘッダの重さを集計する |

### プロパティでの設定

プロジェクトのプロパティ → C/C++ → コマンド ライン → 追加のオプションに、`/d1reportTime` や `/Bt+` を書き、ビルドの出力ウィンドウで結果を見ます。測ったら、外します（出力が増えるため）。

## 1. 並列ビルド

| 設定 | 説明 |
| --- | --- |
| **`/MP`**（複数プロセッサによるコンパイル） | 1 つのプロジェクト内の `.cpp` を、複数のコアで同時にコンパイル。プロパティ → C/C++ → 全般 → 複数プロセッサによるコンパイル |
| プロジェクトの並列ビルド数 | ツール → オプション → プロジェクトおよびソリューション → ビルドして実行 → 最大並列プロジェクトビルド数 |
| Ninja | CMake + Ninja は、自動で全コアを使う（[Ninja](../vs/ninja.md)） |

!!! warning "/MP は、ビルドの再現性に注意"
    `/MP` はコンパイラのプロセスを多数起動します。メモリが足りないとかえって遅くなります。コア数とメモリに合わせて、`/MP4` のように数を指定できます。`/Gm`（最小リビルド）とは併用できません（最近のバージョンでは、既定でオフ）。

## 2. include を減らす

**最も本質的な対策**です。ヘッダが他のヘッダを読み込まないようにします。

### 前方宣言

```cpp
#include "enemy.h"

class Player {
  Enemy* target_;
};
```

↓

```cpp
class Enemy;

class Player {
  Enemy* target_;
};
```

ポインタ・参照だけ使うなら、`#include` せず、前方宣言で済みます。`.cpp` に`#include` を移すことで、ヘッダを読む範囲が狭くなります（[ヘッダとソースの分け方](../design/foundations/header-source.md)）。

### PImpl

クラスの中身を`.cpp` に隠すことで、ヘッダを軽くできます（[PImpl](../design/patterns/pimpl.md)）。実行時のコスト（ポインタ経由・ヒープ確保）がかかるので変更が多く、よく include されるクラスに限ります。

### 重い標準ヘッダを、ヘッダに書かない

| ヘッダ | 対策 |
| --- | --- |
| `<windows.h>` | `WIN32_LEAN_AND_MEAN`、`NOMINMAX` を定義（[プリプロセッサマクロ](../vs/preprocessor.md)）。ヘッダでなく、`.cpp` で |
| `<iostream>` | `<iosfwd>` で前方宣言。`.cpp` で `#include <iostream>` |
| `<regex>` | 重い。`.cpp` の中だけ。使わないのがよい |
| `<algorithm>` `<ranges>` | 必要な `.cpp` だけ |
| `<format>` `<print>` | 重め。ヘッダの中で使わない |
| `<nlohmann/json.hpp>` | 非常に重い。一部の `.cpp` に閉じ込める |

### include のチェック

| 方法 | 説明 |
| --- | --- |
| `/showIncludes` | どのファイルが何を include しているかを表示 |
| [Include What You Use（IWYU）](#iwyu) | 足りない・不要な include を、提案するツール |
| Visual Studio の「インクルード ファイルの整理」 | 一部の機能（新しいバージョン） |
| include のグラフ | 依存を可視化して、中心にある重いヘッダを見つける |

### Include What You Use（IWYU） {#iwyu}

Include What You Use（インクルード・ワット・ユー・ユース、IWYU）は、「使っているもののヘッダを自分で include する」というルールとそれを守るためのツールの名前です。

| 考え方 | 説明 |
| --- | --- |
| 使うものは直接 include | `std::vector` を使う `.cpp` は、`#include <vector>` を、自分で書く（ほかのヘッダがたまたま include していても、頼らない） |
| 使わないものは、include しない | 不要な include は、消す（読む量が減って、ビルドが速くなる） |
| 間接的な include に、頼らない | `a.h` が `b.h` を include しているからと、`a.h` だけで `b.h` の中身を使うのは、脆い（`a.h` が整理されると、突然ビルドエラー） |

```cpp
#include "enemy.h"

std::vector<int> ids;
```

`enemy.h` がたまたま `<vector>` を include していると、動きます。`enemy.h` から `<vector>` が消えた日に、ビルドが壊れます。IWYU の守り方は`#include <vector>` を、自分で書くことです。

#### ツール include-what-you-use

Clang をベースにした、解析ツールです。ソースを解析して、「足すべき include」「消すべき include」を、提案します。

```text
main.cpp should add these lines:
#include <vector>

main.cpp should remove these lines:
- #include "unused.h"  // lines 3-3

The full include-list for main.cpp:
#include <vector>
#include "enemy.h"
```

| 項目 | 説明 |
| --- | --- |
| 提案の 3 つ | 足す行（add）、消す行（remove）、あるべき、include の全体（full include-list） |
| CMake から使う | `set(CMAKE_CXX_INCLUDE_WHAT_YOU_USE include-what-you-use)` で、ビルドのたびに提案を出力 |
| 一括で解析 | `iwyu_tool.py -p <build>`（`compile_commands.json` を使って、全ファイルを解析） |
| 提案を自動で反映 | `fix_includes.py`（提案をソースに適用） |
| 除外・保持の指示 | `// IWYU pragma: keep`（消さない）、`// IWYU pragma: export`（この include を、再公開） |
| マッピングファイル | 「この型はこのヘッダ」という対応を自分で教える（標準ライブラリの内部ヘッダ対策） |

!!! warning "Windows・MSVC では、導入が少し面倒"
    IWYU は Clang 系のツールで、LLVM のバージョンに合わせてビルドする必要があります。MSVC の標準ライブラリのヘッダでは、提案が不正確になることがあります。提案は鵜呑みにせず、人が確認します。

#### Visual Studio・エディタの機能

| 機能 | 説明 |
| --- | --- |
| Visual Studio の「未使用の `#include`」の検出・削除 | 新しい Visual Studio（2022 の後期の版）で、使っていない include を、グレー表示・整理する機能がある（バージョンで機能が違う） |
| clangd の「Unused include」診断 | VS Code などで、clangd を使うと、使われていない include が、警告される（`Include Cleaner`） |

まずはこれらのエディタの支援で使っていない include を消すだけでも、効果があります。

#### 前方宣言との関係

IWYU は、「ヘッダに重い include を増やす」ためのルールではありません。

| 場面 | 方針 |
| --- | --- |
| `.cpp` の中 | 使うものはすべて include（IWYU どおり） |
| ヘッダの中（ポインタ・参照だけ使う） | include せず、前方宣言（`class Enemy;`）。重いヘッダを持ち込まない |
| ヘッダの中（値のメンバ・継承） | 完全な定義が必要なので、include する |

ヘッダは最小限の include（前方宣言を活用）、`.cpp` は、IWYU（使うものを全部 include）、が、バランスの良い方針です（[ヘッダとソースの分け方](../design/foundations/header-source.md)）。

## 3. プリコンパイル済みヘッダー（PCH）

<strong>変更されない重いヘッダ（標準ライブラリ、外部ライブラリ）</strong>を、一度だけ解析して、結果を保存し、各 `.cpp` で再利用します。

```cpp
#pragma once

#include <algorithm>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>
```

| 手順 | 設定 |
| --- | --- |
| 1. `pch.h` を作る | 変更しないヘッダ（標準・外部ライブラリ）だけを入れる |
| 2. `pch.cpp` を作る | `#include "pch.h"` だけを書く |
| 3. プロパティを設定 | プロジェクト → C/C++ → プリコンパイル済みヘッダー → 使用（/Yu）、`pch.h`。`pch.cpp` だけ作成（/Yc） |
| 4. 各 `.cpp` の先頭に | `#include "pch.h"`（最初の行） |

| 注意 | 説明 |
| --- | --- |
| 自分のヘッダを入れない | 頻繁に変わるヘッダを入れると、変更のたびに全体を再ビルドする |
| `.cpp` の最初の行 | `#include "pch.h"` が、他の `#include` より前でないと、`/Yu` でエラー（または無視） |
| 全部入れすぎない | 使わないヘッダまで入れると、PCH のサイズが増えて、遅くなる |
| 強制インクルード（`/FI`） | 全 `.cpp` に自動で `pch.h` を入れる方法。書き忘れを防げる |
| CMake | `target_precompile_headers(app PRIVATE pch.h)` |

## 4. unity ビルド（Jumbo ビルド）

**複数の `.cpp` を、1 つの `.cpp` にまとめて**コンパイルします。ヘッダの読み込みが、1 回になるので速くなります。

```cmake
set_target_properties(app PROPERTIES UNITY_BUILD ON UNITY_BUILD_BATCH_SIZE 16)
```

| 長所 | 短所 |
| --- | --- |
| ヘッダの解析がまとめて 1 回。大幅に速くなることがある | 名前の衝突（無名名前空間、`static` がまとめられた `.cpp` 同士で衝突） |
| リンクも速い（オブジェクトが減る） | 1 つ変えるとまとめた全部を再コンパイル（増分ビルドに不利） |
| | `using namespace` や マクロが、ほかの `.cpp` に漏れる |

CI・リリースビルドで使い、日々の開発では、使わないのが無難です。

## 5. テンプレートの再インスタンス化を減らす

**同じテンプレートの展開を、`.cpp` ごとにやり直さない**ようにします。

```cpp
extern template class std::vector<Enemy>;
```

```cpp
template class std::vector<Enemy>;
```

| 書き方 | 意味 |
| --- | --- |
| `extern template` | 「この展開は他の `.cpp` にある。ここでは展開しない」 |
| 明示的インスタンス化（`template class ...;`） | 「この `.cpp` で展開する」（1 か所だけ） |

自作のテンプレートで使う型が決まっているとき（例：`Vector<float>`、`Vector<int>` だけ）に、ヘッダには宣言、`.cpp` に実装と明示的インスタンス化を書くと、ヘッダが軽くなります。

## 6. 増分ビルドを守る

**変更した部分だけを再ビルド**する仕組みを壊さないようにします。

| 失敗 | 説明 |
| --- | --- |
| よく変わるヘッダを多くが include | 1 つ直すと全部再ビルド。`config.h` や、`common.h` がよくある犯人 |
| PCH に頻繁に変わるヘッダを入れる | 同上 |
| 自動生成ファイルの毎回の更新 | 中身が変わらなくてもタイムスタンプが変わると、再ビルド。内容が同じなら、書き換えない |
| `__DATE__` / `__TIME__` マクロ | 毎回違うので毎回再ビルド |
| ビルドのたびにファイルを触る | タイムスタンプが更新される |

## 7. リンクを速くする

| 方法 | 説明 |
| --- | --- |
| <strong>増分リンク（`/INCREMENTAL`）</strong> | Debug で有効（既定）。変更だけをリンクし直す |
| `/DEBUG:FASTLINK` | デバッグ情報の作成を速く（互換性・機能に制約あり） |
| LTCG（`/GL`、`/LTCG`） | Release の最適化。非常に遅い。CI・最終ビルドだけ |
| 静的ライブラリの数を減らす | 小さなライブラリを大量にリンクすると、遅い |
| ライブラリを DLL にする | 変更時の再リンクが速くなる（実行時のコストと配布に注意） |
| 新しいリンカー・`lld` | 一部のプロジェクトで速くなる |

## 8. キャッシュ

同じソース・同じオプションなら、前回の結果を使う仕組みです。

| ツール | 説明 |
| --- | --- |
| ccache | GCC / Clang で、よく使う。MSVC は制約がある |
| sccache | MSVC にも対応。チーム・CI でキャッシュを共有できる |
| CI のキャッシュ | ビルド成果物を、CI 上で保存・再利用 |

クリーンビルドが何度も行われる（CI）環境で特に効果があります。

## 9. モジュール

C++20 のモジュールは、ヘッダを一度だけコンパイルして、結果を再利用する仕組みです。

```cpp
import std;

int main() {
  std::println("Hello");
}
```

| 項目 | 説明 |
| --- | --- |
| `import std;`（C++23） | 標準ライブラリ全体を、1 行で。MSVC（Visual Studio 2026）で使える |
| 効果 | ヘッダを読むより、速いことが多い |
| 現状の課題 | ツール・IDE・ビルドシステムの対応がまだ発展中。外部ライブラリは、対応していないことが多い |
| 設定 | プロジェクトのプロパティ → C/C++ → 言語 → C++ 標準ライブラリ モジュールのビルド（新しいバージョン） |

学習・小さなプロジェクトでは、試してみる価値があります。大きなプロジェクトは、ツールの成熟を見て、判断します。

## 優先順位

| 順番 | 対策 | 難しさ | 効果 |
| --- | --- | --- | --- |
| 1 | `/MP`・Ninja（並列化） | 簡単 | 大 |
| 2 | `<windows.h>` の軽量化マクロ | 簡単 | 中 |
| 3 | include を減らす（前方宣言） | 中 | 大 |
| 4 | PCH | 簡単〜中 | 大 |
| 5 | 重いヘッダの閉じ込め | 中 | 中〜大 |
| 6 | unity ビルド（CI） | 簡単 | 大（増分には不利） |
| 7 | キャッシュ（sccache） | 中 | 大（CI） |
| 8 | モジュール | 難しい | 将来性 |

## よくあるミス

??? failure "ヘッダが、他のヘッダを不必要に include している"
    前方宣言で済む所は、`.cpp` に移します。

??? failure "PCH に、頻繁に変わる自分のヘッダを入れる"
    変更のたびに全体が再ビルドされます。変わらないものだけを入れます。

??? failure "`/MP` をつけたら、メモリ不足で遅くなる"
    `/MP` の数をコア数・メモリに合わせて制限します。

??? failure "Debug も、LTCG・全最適化でビルドしている"
    日々の開発は速くビルドできる設定にします。LTCG は Release だけ。

??? failure "測らずに、ビルドの設定をいじる"
    `/d1reportTime`、Build Insights で、何が遅いかを先に調べます。

??? failure "`__DATE__` / `__TIME__` を、全体で使っていて、毎回再ビルドになる"
    1 つの `.cpp` に閉じ込めるか、ビルド情報を別ファイルにします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 遅い原因はヘッダの読み直し。まず測る（`/d1reportTime`、Build Insights）
    - [x] 並列化（`/MP`、Ninja）が、最も手軽で効く
    - [x] 前方宣言・PImplで include を減らす。重いヘッダをヘッダに書かない
    - [x] PCH には変更しないヘッダだけ。unity ビルドは CI で
    - [x] よく変わるヘッダ・`__DATE__` が増分ビルドを壊す。Debug を速く、LTCG は Release だけ

## 関連ページ

- [最適化の進め方](index.md)
- [コンパイラの最適化](compiler.md)
- [ヘッダとソースの分け方](../design/foundations/header-source.md)
- [PImpl](../design/patterns/pimpl.md)
- [ビルドと CMake の構成](../design/practice/build-cmake.md)
- [Ninja](../vs/ninja.md)
- [プリプロセッサマクロ（Visual Studio）](../vs/preprocessor.md)

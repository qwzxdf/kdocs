# kdocs TODO

docs の外（リポジトリ直下）に置いているので、サイトにはビルドされない。2026-10-28 に、全体を調べ直して書き直した。

## 1. 全体レビュー（2026-10-28 時点）

2356 ページの統計を取り、今回の作業で書いたページ（約 700 ページ）を読み返した結果。実際の日本語記事との並べ読みや、Compiler Explorer での実行はしていない。

### 1-1. 規模と濃さ

本文の長さ（コードと表を除く）の中央値と、1300 字未満の薄いページの数。

| 場所 | ページ数 | 中央値 | 薄いページ |
| --- | --- | --- | --- |
| STL `support` | 412 | 1449 字 | 126 |
| STL `numeric` | 285 | 1609 字 | 31 |
| STL `io` | 283 | 980 字 | 236 |
| STL `utilities` | 222 | 1173 字 | 138 |
| STL `algorithms` | 140 | 1546 字 | 56 |
| STL `memory` | 80 | 1145 字 | 62 |
| STL `concurrency` | 72 | 1148 字 | 43 |
| STL `containers` | 63 | 1416 字 | 26 |
| `graphics` | 290 | 12487 字 | 1 |
| `3d`・`gamemath` | 39 | 12000〜15000 字 | 0 |
| `rendering`・`optimize` | 62 | 5400〜5800 字 | 0 |
| `directx`・`libs`・`csharp`・`vs`・`design`・`engine` ほか | 約 340 | 2900〜5200 字 | 7 |

- STL は 1560 ページで、サイト全体の約 3 分の 2。そのうち約 720 ページが 1300 字未満で、ここが一番の弱点。`io` と `utilities` が、まだ手つかず
- `numeric` は一通り書き直した。`support` も、type_traits・concepts・exceptions・比較・ranges・エラーコードを書き直した
- 書き直したページの本文は 1200〜2500 字。`gcd.md` の濃さには届くが、`vector.md`（約 15000 字）や `graphics` の水準には遠い

### 1-2. 今回の作業の品質で、気になる所

- **同じ型の文章が並ぶ。** 同じ種類のページ（`cctype`、`ratio` の接頭辞、`cstdint`、`type_traits` の `is_xxx`、`functional` の演算子）は、生成スクリプトで、同じ構成の文章を作った。1 ページずつ読むと自然だが、続けて読むと、言い回しが同じで、人が書いた感じが薄い。特に「ゲームでの使いどころ」が、型どおりのページがある
- **実行結果は手計算。** この環境にコンパイラが無く、Compiler Explorer も使っていない。値は、既知の値と照らして確かめたが、実機の出力と 1 文字違う可能性が残る。C++23・C++26 の機能（`bind_back`、`from_range`、飽和演算など）の対応バージョンも、実機では確かめていない
- **「このページを読む前に」を機械的に入れた。** 約 690 ページに、フォルダーごとの対応表で前提ページを入れた。リンク先は実在するが、そのページに本当に必要な前提かは、1 ページずつ見ていない（例: `graphics` の全ページに、MVP 変換と GPU パイプラインを入れた）
- **「非常に」を地の文から削った。** 201 か所。「影が非常に、長く」→「影が、長く」のように、読点だけ残った所がある
- **検査スクリプトが無い。** CLAUDE.md が push 前に要求する `.handoff/scripts/check_anchors.py` と `check_docs.py` が、このチェックアウトに無く、一度も実行できていない。`mkdocs build --strict` だけで push している
- **ビルドが遅い。** 全体のビルドに 6〜60 分かかる（機械の状況で変わる）。ページを足すたびの確認が重い
- `k-cpperr/`（VS 拡張）を、誤って自分のコミットに含めた。その後、本人のコミットも載っているので、扱いは問題ないはずだが、確認はしていない

### 1-3. 文体の違和感・わかりにくさ（サイト全体）

- 「このページでは〜／このページは〜」を含むページが 427 ページ（436 か所）。多くは導入の最後の「このページは〜をまとめます」で、先頭にあるのは数ページだけ。一括の書き換えは見送った
- 「必要があります」256 か所（213 ページ）、「つまり」66 か所（58 ページ）、「効率的」12 か所、「具体的には」6 か所
- 読点: 「に、」が 1827 か所、「が、」が 1828 か所、「を、」が 96 か所。**読点を整える `tools/fix_commas.py` が既にある**（`--survey` で密度の一覧、`--apply 6.0` で直す）。まだ全体には適用していない
- 太字の多いページ 29 ページ（STL で 7 か所以上）。`stl/containers/vector.md` が 41 か所、`stl/utilities/hash.md` が 37 か所、`stl/index.md` が 34 か所。`tools/fix_bold.py` がある
- 実行結果が続かないコード: `int main` があるのに、直後に「実行結果」が無いコード ブロックが 47 か所
- `TODO` の下書きが残るページ: `design/foundations/naming.md`、`design/practice/coding-style.md`、`libs/index.md`

### 1-4. 良い点（維持する）

- `graphics`・`3d`・`gamemath` は、どのページも濃く、動く図もある。構成が一定
- `csharp/04-player.md`、`stl/containers/vector.md`、`graphics/terrain/lod/cdlod.md` の流れ（動機 → 例 → 構造、コード → すぐ解説）は、そのまま読み物として通る
- 新しく足した `vs/git.md`、`engine/ai/` などは、導入が動機から入っていて、見本のページに近い

## 2. 直す優先順位

1. **検査スクリプトを復活させる**（`.handoff/scripts/` の 2 本。無いなら、`tools/` に作り直す）。以降の作業の安全網になる
2. **生成ページを読み直す**: 特に `cctype`、`cwctype`、`cstdint` の fast / least、`ratio`、`cmath` の特殊関数、`type_traits` の `is_xxx`。同じ文章の所を、ページごとの具体的な話に差し替える
3. **STL の残りを濃くする**（`io` → `utilities` → `memory` → `concurrency` → `containers` → `algorithms` → `support` の残り）。約 720 ページ
4. **Compiler Explorer で、書き直したページのサンプルを実行して照合する**（ユーザーの指示があったときだけ。CLAUDE.md のルール）
5. 読点（`tools/fix_commas.py`）と太字（`tools/fix_bold.py`）の一括整理。まず見本の 1 ページで試して、OK をもらってから広げる
6. 「必要があります」「つまり」「効率的」などの整理（文脈ごとに、手で）

### STL の残り（薄い順の目安）

- `io`（283 ページ中 236）: `filesystem`、`cstdio`、`cwchar`、`locale`、`regex`、`ctime`、ストリームの操作子
- `utilities`（222 ページ中 138）: `chrono`（86）、`random`（39）、`tuple`・`pair`・`optional` まわり
- `memory`（80 ページ中 62）: `cstring`、`new_delete`、`pmr`、スマート ポインターの周辺
- `concurrency`（72 ページ中 43）、`containers`（63 ページ中 26）、`algorithms`（140 ページ中 56。`views` と数値アルゴリズム）
- `support` の残り: iterator のコンセプト（約 35）、iterator の細かい型、`coroutine`（8）、`functional` の検索器・`function_ref`・placeholders、`invoke_result` 系、`stacktrace`・`contract_violation`・`text_encoding`・`*_order_fallback`
- `numeric` の残り: `cfloat`、`climits`、`complex`、`cstdint`、`numbers`、`ratio` の概要ページ（`cmath/atan2.md`、`lerp.md`、`sqrt.md` を含む）

## 3. 追加したいページ（残り）

優先度は ★ の数（★★★ が高い）。新規ページを足したときは `ratings.yml` と `autolinks.yml` も更新する。

### 3-1. 手順のページを濃くする

- [ ] ★★★ DX11 / DX12 のガイド（`dx11/guide.md`、`dx12/guide.md`）は、今は**手順の道しるべ**。各段階の完全なコード（ウィンドウ → デバイス → 三角形 → 回る立方体）を、1 段階 1 ページで書く
- [ ] ★★ Vulkan 対応表（`directx/vulkan-mapping.md`）に、同期（フェンス / セマフォ）の流れの図を足す
- [ ] ★★ RenderDoc / PIX（`vs/renderdoc-pix.md`）に、画面の写真と、実際の手順の画像を足す

### 3-2. 描画

- [ ] ★★ VBAO（出典を確かめてから。名前だけが先に出ていて、定義がはっきりしない）
- [ ] ★★ アップスケーラ（`graphics/postprocess/upscaling/`）に、ジッターと動きベクトルの動く図
- [ ] ★ Lumen / Nanite（`graphics/gi/lumen.md`）に、Surface Cache と仮想化ジオメトリの図

### 3-3. ゲームの分野

- [ ] ★★ 入力・サウンド・AI・ネットワーク（`engine/` に追加済み）を、1 つの小さなゲームで通して使う実践ページにする
- [ ] ★★ ビヘイビア ツリー（`engine/ai/behavior-tree.md`）に、動く図（Selector と Sequence の評価の流れ）
- [ ] ★ `libs/sol2.md`・`libs/pybind11.md` に、導入手順の画面（vcpkg の `vcpkg.json` を置いた状態）
- [ ] ★ Wwise・OpenAL の個別ページ（FMOD は 27 ページに出る）

### 3-4. 開発の道具

- [ ] ★★ `vs/team.md` と `vs/github-actions.md` に、実際の PR の画面と、ワークフローの結果の画面
- [ ] ★ Conan の個別ページ（`vs/package-managers.md` の比較から先）

### 3-5. 初心者向けの導線

- [ ] ★★★ 用語集（`glossary.yml`）は 9 語を足したところ。主要な用語（Git・CI・RAII・SIMD・シェーダーなど）を、ページごとに拾って足す
- [ ] ★★ 学習ロードマップ（`roadmap.md`）に、「作りたいもの別」の完全な読書リスト（2D ゲーム、3D ゲーム、ツール）
- [ ] ★★ よくある質問（`faq.md`）に、「どちらを使う？」を 20 件まで増やす

## 4. 完了したこと（履歴）

### 2026-10-28 までの作業

- 追加: `vs/` に Git の基礎・SourceTree と GitHub Desktop・Git LFS・チーム開発・GitHub Actions・clang-tidy・単体テスト・RenderDoc と PIX・GPU デバッグ・Tracy・パッケージ管理・エラーメッセージの読み方。学習ロードマップ、よくある質問
- 追加: 描画の XeGTAO・ASSAO と CACAO・MSSAO、アップスケーラ（FSR・DLSS・XeSS）、Lumen と Nanite、ReSTIR
- 追加: `engine/` の入力・サウンド・ゲーム AI（ビヘイビア ツリー、経路探索）・ネットワーク、`libs/` の sol2・pybind11、`directx/` の DX11・DX12 ガイド、Vulkan 対応表、Slang と WebGPU
- 「このページを読む前に」を、抜けていた約 690 ページに追加
- 地の文の「非常に」を 152 ページから削除
- STL を `gcd.md` の濃さに書き直し: `numeric` のほぼ全部（cmath、bit、cctype、cwctype、cstdint、cstdlib、ratio、cfenv、cuchar、complex、拡張浮動小数点型）、`support` の type_traits・concepts・exceptions・比較（cmp・ordering・three_way）・ranges・エラーコード・型情報・iterator と functional の主要ページ
- 太字の削減（2026-10-23。STL 以外の約 510 ページ）

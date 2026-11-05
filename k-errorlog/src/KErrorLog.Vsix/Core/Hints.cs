using System;
using System.Collections.Generic;

namespace KErrorLog
{
    public sealed class Hint
    {
        public string Title;
        public string Text;
        public Hint(string title, string text) { Title = title; Text = text; }
    }

    /// <summary>エラー コードごとの、日本語の見出しと対処のヒント。</summary>
    public static class Hints
    {
        private static readonly Dictionary<string, Hint> Table = new Dictionary<string, Hint>(StringComparer.OrdinalIgnoreCase)
        {
            // ---- 名前・宣言 ----
            ["C2065"] = new Hint("宣言されていない名前", "綴り、宣言の場所(スコープ)、#include の不足、名前空間(std:: など)を確かめます。"),
            ["C3861"] = new Hint("その名前の関数が見つからない", "#include の不足と、名前空間(std:: など)、宣言より前で使っていないかを確かめます。"),
            ["C2039"] = new Hint("クラス(名前空間)にそのメンバーがない", "メンバー名の綴りと、そのクラスの宣言、#include を確かめます。std:: のものは、対応するヘッダーが要ります。"),
            ["C2061"] = new Hint("識別子が不正", "型名の綴りと、その型の #include を確かめます。循環 include のときもこのエラーが出ます。"),
            ["C2027"] = new Hint("未定義の型を使っている", "前方宣言だけで、定義(#include)がありません。メンバーを使う側のファイルで、定義のあるヘッダーを include します。"),
            ["C2079"] = new Hint("未定義のクラスのオブジェクトは作れない", "前方宣言だけでは、値としては持てません。定義を include するか、ポインターにします。"),
            ["C2504"] = new Hint("基底クラスが未定義", "基底クラスのヘッダーを include します。循環 include も疑います。"),
            ["C2371"] = new Hint("同じ名前を別の型で再定義している", "同じ名前の定義が 2 か所にあります。include ガード(#pragma once)と、名前の衝突を確かめます。"),
            ["C2011"] = new Hint("型が二重に定義されている", "ヘッダーに #pragma once(または include ガード)がありません。"),
            ["C2086"] = new Hint("変数が二重に定義されている", "同じ名前の変数を、同じスコープで 2 回宣言しています。"),
            ["C2084"] = new Hint("関数が二重に定義されている", "同じ関数の本体を 2 回書いています。ヘッダーの include ガードも確かめます。"),
            ["C2955"] = new Hint("テンプレート引数リストが必要", "クラス テンプレートは、<型> を付けて使います(C++17 では、コンストラクターから推論できる場合もあります)。"),

            // ---- 構文 ----
            ["C2143"] = new Hint("構文エラー", "多くは、エラーの行より前の行で、「;」「)」「}」が足りません。エラーの 1 つ前の文を見ます。"),
            ["C2146"] = new Hint("構文エラー(識別子の手前に記号がない)", "直前の行の「;」の抜けか、型名が未宣言のことが多いです。"),
            ["C2059"] = new Hint("構文エラー", "示されたトークンの手前で文が崩れています。直前の行の閉じ忘れを疑います。"),
            ["C2447"] = new Hint("関数の本体の「{」がない", "関数の定義の途中に、おかしな記述があります。引数リストの手前を確かめます。"),
            ["C1004"] = new Hint("予期しないファイル終端", "どこかの「{」や「/*」「#if」が閉じていません。"),
            ["C1075"] = new Hint("対応する括弧がない", "示された括弧に対応する閉じ括弧が見つかりません。"),
            ["C2001"] = new Hint("文字列定数が改行している", "文字列の終わりの「\"」が抜けています。"),

            // ---- 型・引数 ----
            ["C2664"] = new Hint("引数を変換できない", "N 番目の引数の型が、関数の宣言と合っていません。const・参照・ポインターの違いと、ほかの型への暗黙の変換がない点を見ます。"),
            ["C2665"] = new Hint("どのオーバーロードにも合わない", "渡した引数の個数と型を、候補の宣言と見比べます。"),
            ["C2660"] = new Hint("引数の個数が合わない", "その関数は、渡した個数の引数を受け取りません。"),
            ["C2661"] = new Hint("その個数の引数を受け取るオーバーロードがない", "引数の数を数え直します。"),
            ["C2440"] = new Hint("その型へ変換できない", "明示的な変換が要るか、型そのものが違っています。const を外す変換や、ポインターと整数の混在が多いです。"),
            ["C2445"] = new Hint("変換できない(const)", "const のオブジェクトから非 const へは変換できません。"),
            ["C2512"] = new Hint("既定コンストラクターがない", "引数なしでは作れません。引数を渡すか、既定コンストラクターを足します。メンバーや基底クラスの初期化リストも確かめます。"),
            ["C2280"] = new Hint("削除された関数を呼んでいる", "コピーできない型(unique_ptr、mutex など)をコピーしています。std::move を使うか、参照で渡します。"),
            ["C2662"] = new Hint("const のオブジェクトから非 const の関数は呼べない", "その関数に const を付けるか、オブジェクトを非 const にします。"),
            ["C2679"] = new Hint("対応する演算子がない(右辺の型)", "右辺の型に対する演算子(代入や << など)が、その型にありません。"),
            ["C2676"] = new Hint("その二項演算子が定義されていない", "その型に、演算子のオーバーロードを定義するか、別の書き方にします。"),
            ["C2678"] = new Hint("その二項演算子が定義されていない", "その型に、演算子のオーバーロードを定義するか、別の書き方にします。"),
            ["C2675"] = new Hint("その単項演算子が定義されていない", "++ や -- などの演算子が、その型にありません。"),
            ["C2362"] = new Hint("goto がオブジェクトの初期化を飛び越している", "初期化のあるオブジェクトの宣言を、case や goto が飛び越しています。波括弧で囲みます。"),
            ["C2360"] = new Hint("case が初期化を飛び越している", "case の中の変数宣言は、波括弧で囲みます。"),
            ["C2535"] = new Hint("同じメンバー関数が二重に定義されている", "宣言と定義のシグネチャが同じ関数を、2 回定義しています。"),
            ["C2511"] = new Hint("宣言にないオーバーロード", "クラスの宣言にない引数の組み合わせで、メンバー関数を定義しています。宣言と定義の引数・const をそろえます。"),
            ["C2509"] = new Hint("宣言にないメンバー関数", "クラスの宣言にないメンバー関数を定義しています。"),
            ["C2338"] = new Hint("static_assert に失敗した", "メッセージに、満たされなかった条件が書かれています。テンプレートの引数の型を確かめます。"),
            ["C7500"] = new Hint("concept の条件を満たしていない", "メッセージの制約のうち、満たしていないものを確かめます。"),
            ["C7602"] = new Hint("concept の条件を満たしていない", "メッセージの制約のうち、満たしていないものを確かめます。"),
            ["C2672"] = new Hint("テンプレート引数に合う関数がない", "渡した型に対して、テンプレートのどの候補も使えません。候補ごとの理由(下)を読みます。"),
            ["C2784"] = new Hint("テンプレート引数を推論できない", "引数の型から T を決められません。型を明示するか、渡す型をそろえます。"),
            ["C2782"] = new Hint("テンプレート引数が複数の型に決まる", "同じ T に、別の型が当たっています。型をそろえるか、明示的に指定します。"),
            ["C2783"] = new Hint("テンプレート引数を推論できない", "引数から決められないテンプレート引数があります。明示的に指定します。"),
            ["C2893"] = new Hint("関数テンプレートを特殊化できない", "渡した型では、テンプレートの本体が成り立ちません。候補ごとの理由(下)を読みます。"),
            ["C2976"] = new Hint("テンプレート引数が足りない", "クラス テンプレートの引数の個数を確かめます。"),
            ["C2988"] = new Hint("テンプレートの宣言が不正", "テンプレートとして使えない場所で、テンプレートを宣言しています。"),

            // ---- ファイル・プリプロセッサ ----
            ["C1083"] = new Hint("ファイルを開けない(include)", "ヘッダーの名前・パスと、追加のインクルード ディレクトリ(C/C++ > 全般)を確かめます。vcpkg のライブラリなら、導入されているかも確かめます。"),
            ["C1189"] = new Hint("#error が実行された", "メッセージが、そのまま理由です。条件(#if)の前提となる設定を確かめます。"),
            ["C1010"] = new Hint("プリコンパイル済みヘッダーを使うのに、先頭で include していない", "各 .cpp の先頭で、pch.h(stdafx.h)を include します。使わないなら、そのファイルの設定を「使用しない」にします。"),
            ["C1853"] = new Hint("プリコンパイル済みヘッダーが古い", "ソリューションのリビルドで直ります。"),
            ["C1090"] = new Hint("PDB の API の呼び出しに失敗", "並列ビルドや、ウイルス対策ソフトとの競合が多いです。リビルドと、/FS の追加を試します。"),
            ["C4996"] = new Hint("非推奨の関数", "関数が非推奨です。代わりの関数があります。意図があって使うなら、_CRT_SECURE_NO_WARNINGS を定義します。"),
            ["C4244"] = new Hint("型の変換で、値が欠ける", "大きな型から小さな型へ代入しています。static_cast で意図を示します。"),
            ["C4267"] = new Hint("size_t から小さな型への変換", "size_t は 64 ビットです。int に入れるときは static_cast を使います。"),
            ["C4018"] = new Hint("符号付きと符号なしの比較", "負の値が大きな値になります。型をそろえます。"),
            ["C4100"] = new Hint("使っていない引数", "使わない引数は、名前を消すか [[maybe_unused]] を付けます。"),
            ["C4189"] = new Hint("使っていないローカル変数", "初期化したあと、使っていません。"),
            ["C4005"] = new Hint("マクロの再定義", "同じ名前のマクロが 2 か所で違う値で定義されています。windows.h の前後と、プロジェクトのプリプロセッサ定義を確かめます。"),
            ["C4819"] = new Hint("文字コードを表せない文字がある", "ソースを UTF-8 (BOM 付き)で保存するか、/utf-8 を付けます。"),
            ["C4651"] = new Hint("コンパイル オプションの不一致", "プリコンパイル済みヘッダーと、そのファイルの定義(/D)がそろっていません。"),
            ["C4838"] = new Hint("縮小変換", "波括弧の初期化で、値が欠ける型変換をしています。"),

            // ---- リンカー ----
            ["LNK2019"] = new Hint("未解決の外部シンボル", "関数やデータの宣言はあるのに、定義がリンクされていません。"),
            ["LNK2001"] = new Hint("未解決の外部シンボル", "関数やデータの宣言はあるのに、定義がリンクされていません。"),
            ["LNK1120"] = new Hint("未解決の外部参照の件数", "リンカーが数えた件数です。個々の原因は、上の LNK2019 / LNK2001 を見ます。"),
            ["LNK2005"] = new Hint("同じシンボルが二重に定義されている", "ヘッダーに関数の本体を書いて(inline なし)、複数の .cpp から include している場合が多いです。"),
            ["LNK1169"] = new Hint("二重定義のシンボルがある", "上の LNK2005 の一覧が原因です。"),
            ["LNK2038"] = new Hint("設定の不一致を検出した", "ランタイム ライブラリ(/MT と /MD)や、Debug と Release のライブラリが混ざっています。"),
            ["LNK1104"] = new Hint("ファイルを開けない", ".lib のパス(追加のライブラリ ディレクトリ)と、ファイル名の綴りを確かめます。exe を開いたままのときもこのエラーが出ます。"),
            ["LNK1181"] = new Hint("入力ファイルを開けない", "追加の依存ファイルに書いた .lib の名前と、ライブラリ ディレクトリを確かめます。"),
            ["LNK1112"] = new Hint("モジュールのマシン種別が違う", "x86 と x64 が混ざっています。プラットフォームと、リンクする .lib のビット数をそろえます。"),
            ["LNK1168"] = new Hint("出力ファイルを書き込めない", "その exe / dll が実行中か、デバッグ中です。終了させてからビルドします。"),
            ["LNK1561"] = new Hint("エントリ ポイントが定義されていない", "main(または WinMain)がありません。サブシステムの設定と、プロジェクトの種類(exe / dll / lib)を確かめます。"),
            ["LNK1123"] = new Hint("COFF への変換に失敗", "中間ファイルが壊れています。リビルドします。"),
            ["LNK1136"] = new Hint("ファイルが無効または壊れている", "出力ファイルを削除して、リビルドします。"),
            ["LNK2022"] = new Hint("メタデータの操作に失敗", "C++/CLI の型が、ビルドごとに食い違っています。"),
            ["LNK4098"] = new Hint("既定のライブラリが競合している", "/NODEFAULTLIB に、競合しているライブラリを指定します。ランタイム ライブラリが混ざっている場合が多いです。"),
            ["LNK4204"] = new Hint("デバッグ情報(.pdb)がない", "ライブラリを作ったときの PDB が見つかりません。警告のままでも動きます。"),

            // ---- 追加: コンパイラのエラー ----
            ["C2668"] = new Hint("どのオーバーロードか決められない(あいまい)", "候補のうち、2 つ以上が同じくらい合っています。引数に static_cast を付けて型を明示するか、オーバーロードを整理します。"),
            ["C2593"] = new Hint("演算子がどれか決められない(あいまい)", "暗黙の変換が 2 通りあります。片方の型に明示的にそろえます。"),
            ["C2594"] = new Hint("変換がどれか決められない(あいまい)", "変換の候補が複数あります。明示的にキャストします。"),
            ["C2397"] = new Hint("縮小変換(波括弧の初期化)", "波括弧の初期化では、値が欠ける変換が禁止です。static_cast で型をそろえます。"),
            ["C2398"] = new Hint("縮小変換(波括弧の初期化)", "波括弧の初期化では、値が欠ける変換が禁止です。static_cast で型をそろえます。"),
            ["C2653"] = new Hint("クラスまたは名前空間の名前ではない", "名前の綴りと、そのヘッダーの #include を確かめます。std:: なら、対応する標準ヘッダーが要ります。"),
            ["C2882"] = new Hint("名前空間の名前が使えない場所", "名前空間名は、「using namespace」か「名前::」の形でだけ使えます。"),
            ["C2144"] = new Hint("構文エラー(型のあとに ')' がない)", "キャストや sizeof の括弧の対応を確かめます。"),
            ["C2182"] = new Hint("void 型は使えない", "void の変数や引数は作れません。ポインターにするか、型を決めます。"),
            ["C2228"] = new Hint("「.」の左がクラスではない", "ポインターなら「->」を使います。型が思った型かも確かめます。"),
            ["C2231"] = new Hint("「.」の左がポインター", "ポインターには「->」を使います。"),
            ["C2233"] = new Hint("クラスではない型にメンバー アクセス", "ポインターか、型が違っています。"),
            ["C2274"] = new Hint("型のキャストの構文が違う", "new や sizeof の書き方を確かめます。"),
            ["C2300"] = new Hint("クラスに演算子がない", "その型には、該当の演算子が定義されていません。"),
            ["C2327"] = new Hint("外側のクラスの非 static メンバーは使えない", "入れ子のクラスからは、外側の非 static メンバーを直接使えません。インスタンスを渡します。"),
            ["C2337"] = new Hint("属性が見つからない", "属性の綴りを確かめます。"),
            ["C2491"] = new Hint("dllimport の関数は定義できない", "DLL を作るプロジェクトで、API マクロが dllimport になっています。DLL 側では dllexport になるよう、マクロの定義を確かめます。"),
            ["C2429"] = new Hint("その機能は、いまの言語標準では使えない", "プロジェクトの C++ 言語標準 (C/C++ > 言語 > C++ 言語標準) を上げます。"),
            ["C2760"] = new Hint("構文エラー(予期しないトークン)", "示されたトークンの手前を見ます。"),
            ["C2766"] = new Hint("明示的な特殊化が重複している", "同じテンプレートの特殊化を、2 回宣言しています。"),
            ["C2797"] = new Hint("メンバーの初期化子リストが不正", "メンバーの宣言順と、初期化の形を確かめます。"),
            ["C2800"] = new Hint("演算子を適用できない", "そのオペランドの型に対して、演算子がありません。"),
            ["C2913"] = new Hint("typename または template が要る", "従属名(T::value_type など)の前に typename を付けます。"),
            ["C2953"] = new Hint("クラス テンプレートが二重に定義されている", "ヘッダーの include ガードを確かめます。"),
            ["C2974"] = new Hint("テンプレート引数が不正", "型を渡す場所に、型でないものを渡しています。"),
            ["C3083"] = new Hint("「::」の左が名前空間・クラスではない", "名前の綴りと、スコープを確かめます。"),
            ["C3205"] = new Hint("引数の型が不正", "テンプレートの引数に、使えない型があります。"),
            ["C3245"] = new Hint("名前を再宣言している", "同じ名前が、別の意味で宣言されています。"),
            ["C3312"] = new Hint("範囲 for のための begin / end がない", "範囲 for で回したい型に、begin() / end() がありません。"),
            ["C3615"] = new Hint("constexpr 関数で定数式にならない", "constexpr 関数の中で、定数式にできない処理をしています。"),
            ["C3646"] = new Hint("未知の指定子", "型名が未宣言のことが多いです。#include と、循環 include を確かめます。"),
            ["C3688"] = new Hint("リテラルの接尾辞が不正", "文字列リテラルの隣に、識別子が付いています。マクロの前後に空白を入れます。"),
            ["C3779"] = new Hint("auto の戻り値が決められない", "関数の定義を、呼ぶ側より前に書くか、戻り値の型を明示します。"),
            ["C4251"] = new Hint("DLL のクラスが、dll-interface でない型を持つ", "DLL からエクスポートするクラスのメンバーに、STL などの型があります。DLL と利用側のランタイムが同じなら、警告は無視できます(C4251 を抑制)。"),
            ["C4275"] = new Hint("エクスポートするクラスの基底が dll-interface でない", "基底クラスもエクスポートするか、警告を抑制します。"),
            ["C4091"] = new Hint("typedef の中で宣言が無視された", "古い Windows SDK のヘッダーで出ます。SDK を更新するか、警告を抑制します。"),
            ["C4101"] = new Hint("使っていないローカル変数", "宣言した変数を、使っていません。"),
            ["C4146"] = new Hint("符号なしの数に単項マイナス", "符号なし型の負数は、大きな値になります。"),
            ["C4172"] = new Hint("ローカル変数のアドレスを返している", "関数を出ると消える変数への参照・ポインターを返しています。値で返すか、呼び出し側が持つ領域を使います。"),
            ["C4305"] = new Hint("型の切り詰め(double から float)", "float のリテラルには 1.0f のように f を付けます。"),
            ["C4309"] = new Hint("定数が型に収まらない", "代入する値が、その型の範囲を超えています。"),
            ["C4311"] = new Hint("ポインターを小さな整数に切り詰め", "x64 では、ポインターは 64 ビットです。uintptr_t を使います。"),
            ["C4312"] = new Hint("整数からより大きなポインターへ変換", "uintptr_t を経由して変換します。"),
            ["C4390"] = new Hint("空の制御文", "if や for のあとの「;」を確かめます。"),
            ["C4458"] = new Hint("メンバーを隠す宣言", "引数やローカル変数の名前が、クラスのメンバーと同じです。"),
            ["C4477"] = new Hint("書式文字列と引数の型が合わない", "printf の %d や %s と、渡した引数の型を合わせます。"),
            ["C4505"] = new Hint("使っていない static 関数", "どこからも呼ばれていません。"),
            ["C4530"] = new Hint("例外処理が有効でないのに、例外を使っている", "C/C++ > コード生成 > C++ 例外を有効にする を「はい (/EHsc)」にします。"),
            ["C4551"] = new Hint("関数の呼び出しに () がない", "関数名だけでは、呼び出しになりません。"),
            ["C4574"] = new Hint("マクロの定義が 0 か 1 でない", "#if で使うマクロの値を確かめます。"),
            ["C4668"] = new Hint("未定義のマクロを #if で使っている", "マクロが定義されていません。0 と見なされます。"),
            ["C4700"] = new Hint("初期化していない変数を使っている", "値を入れる前に、読んでいます。"),
            ["C4701"] = new Hint("初期化していないかもしれない変数", "すべての経路で値を入れているか確かめます。"),
            ["C4702"] = new Hint("到達できないコード", "return や throw のあとに、コードがあります。"),
            ["C4715"] = new Hint("値を返さない経路がある", "すべての経路で return しているか確かめます。戻り値を使うと未定義の動作です。"),
            ["C4716"] = new Hint("値を返していない", "戻り値のある関数に、return がありません。"),
            ["C4834"] = new Hint("[[nodiscard]] の戻り値を捨てている", "戻り値を使うか、意図があるなら (void) でキャストします。"),
            ["C5045"] = new Hint("Spectre 対策を入れられる箇所がある", "/Qspectre を付けたときの情報です。通常は無視できます。"),
            ["C5105"] = new Hint("マクロの展開が未定義の動作", "windows.h の古いヘッダーで出ます。/Zc:preprocessor を外すか、SDK を更新します。"),
            ["C5030"] = new Hint("属性が認識されない", "コンパイラが知らない属性を無視しました。綴りか、言語標準を確かめます。"),

            // ---- HLSL (fxc / dxc) ----
            ["X3000"] = new Hint("HLSL: 構文エラー", "直前の行の「;」「)」「}」の抜けが多いです。"),
            ["X3004"] = new Hint("HLSL: 宣言されていない識別子", "綴りと、変数のスコープ、#include を確かめます。"),
            ["X3013"] = new Hint("HLSL: 引数に合う関数がない", "渡した引数の型・個数を確かめます。候補は下に出ます。"),
            ["X3014"] = new Hint("HLSL: 引数の数が違う", "関数の引数の個数を確かめます。"),
            ["X3017"] = new Hint("HLSL: 暗黙の型変換ができない", "float3 と float4 のような、次元の違いが多いです。.xyz などで切り出します。"),
            ["X3018"] = new Hint("HLSL: 添字が不正", "スカラーに [] を使っているなど、型を確かめます。"),
            ["X3020"] = new Hint("HLSL: 型が合わない", "比較や代入の左右の型をそろえます。"),
            ["X3025"] = new Hint("HLSL: グローバル変数は暗黙の const", "シェーダー内でグローバルを書き換えられません。static を付けるか、ローカルにします。"),
            ["X3039"] = new Hint("HLSL: 出力の型が不正", "出力セマンティクスを確かめます。"),
            ["X3059"] = new Hint("HLSL: 定数バッファの記述が不正", "cbuffer の宣言と、レジスタの指定を確かめます。"),
            ["X3078"] = new Hint("HLSL: ループ変数が二重に宣言されている", "同じ名前のループ変数を、同じスコープで 2 回宣言しています。"),
            ["X3081"] = new Hint("HLSL: どの関数か決められない(あいまい)", "引数の型を明示的にそろえます。"),
            ["X3082"] = new Hint("HLSL: 整数のリテラルが大きすぎる", "float のリテラルなら小数点を付けます。"),
            ["X3500"] = new Hint("HLSL: テクスチャ・サンプラーの組み合わせが不正", "Sample に使う型を確かめます。"),
            ["X3501"] = new Hint("HLSL: エントリ ポイントが見つからない", "エントリ ポイントの名前(/E)が、関数の名前と合っているか確かめます。"),
            ["X3502"] = new Hint("HLSL: 出力セマンティクスが書かれていない", "戻り値の型・構造体の各メンバーに、セマンティクス(SV_Position など)が要ります。"),
            ["X3506"] = new Hint("HLSL: 出力が初期化されていない", "戻り値の構造体のメンバーを、すべて初期化します。"),
            ["X3507"] = new Hint("HLSL: 出力が初期化されていない", "戻り値のすべての成分を設定します。"),
            ["X3512"] = new Hint("HLSL: サンプラー引数の使い方が不正", "SamplerState の使い方を確かめます。"),
            ["X3550"] = new Hint("HLSL: 配列の添字が定数でない", "配列は定数の添字で使います。[unroll] を付けると、ループのカウンターで引ける場合があります。"),
            ["X4000"] = new Hint("HLSL: 初期化していない変数を使っている", "すべての経路で値を入れているか確かめます。"),
            ["X3206"] = new Hint("HLSL: オーバーロードが決められない", "引数の型を明示的にキャストします。"),
            ["X4717"] = new Hint("HLSL: 機能が使えない(シェーダー モデル)", "シェーダー モデル (/T) を上げるか、別の書き方にします。"),

            // ---- NuGet / MSBuild ----
            ["NU1101"] = new Hint("NuGet: パッケージが見つからない", "パッケージ名と、パッケージ ソース(nuget.org)を確かめます。"),
            ["NU1102"] = new Hint("NuGet: 指定の版がない", "存在する版を指定します。"),
            ["NU1605"] = new Hint("NuGet: 版のダウングレード", "依存関係の版を、そろえます。"),
            ["MSB3644"] = new Hint("参照アセンブリが見つからない", "対象の .NET Framework の Developer Pack を入れます。"),
            ["MSB4019"] = new Hint("インポートするプロジェクトが見つからない", "Visual Studio のワークロードが足りないか、パスが違います。"),
            ["MSB8003"] = new Hint("ビルド ツールの設定が不正", "プロジェクトのプロパティを確かめます。"),
            ["MSB8028"] = new Hint("中間ディレクトリが重複している", "複数のプロジェクトが、同じ中間ディレクトリを使っています。プロジェクトごとに分けます。"),
            ["MSB1009"] = new Hint("プロジェクト ファイルがない", "コマンドで指定したパスを確かめます。"),

            // ---- MSBuild ----
            ["MSB8020"] = new Hint("プラットフォーム ツールセットがない", "プロジェクトが指定している、ビルド ツールのバージョンが入っていません。Visual Studio Installer で追加するか、プロジェクトの設定を変えます。"),
            ["MSB8036"] = new Hint("Windows SDK が見つからない", "プロジェクトが指定している SDK のバージョンが入っていません。ソリューションのターゲットを変更します。"),
            ["MSB3073"] = new Hint("カスタム コマンドが失敗した", "ビルド後イベントなどのコマンドが、0 以外で終了しました。その出力を読みます。"),
            ["MSB6006"] = new Hint("ツールが 0 以外で終了した", "cl.exe や link.exe が失敗しています。上のエラーを読みます。"),
            ["MSB4181"] = new Hint("タスクがエラーを出さずに失敗した", "ビルドの中断や、ツールのクラッシュです。もう一度ビルドします。"),

            // ---- コマンド ライン ----
            ["D8016"] = new Hint("コマンド ライン オプションが両立しない", "たとえば /RTC1 と /O2 は、同時に指定できません。構成ごとの設定を確かめます。"),
            ["D8003"] = new Hint("ソース ファイルが見つからない", "ファイルがプロジェクトから外れているか、移動しています。"),
            ["D9002"] = new Hint("不明なオプションを無視した", "コンパイラが知らないオプションがあります。"),
        };

        public static Hint For(string code)
        {
            Hint h;
            if (code != null && Table.TryGetValue(code, out h) && !string.IsNullOrEmpty(h.Title)) return h;
            return null;
        }

        // ---- Windows / DirectX の関数 → 必要な .lib ----

        private static readonly Dictionary<string, string> Win32Exact = new Dictionary<string, string>(StringComparer.Ordinal);
        private static readonly string[][] Win32Prefix;

        static Hints()
        {
            Add("user32.lib",
                "CreateWindow", "CreateWindowEx", "RegisterClass", "RegisterClassEx", "UnregisterClass", "DefWindowProc", "GetMessage", "PeekMessage",
                "DispatchMessage", "TranslateMessage", "ShowWindow", "UpdateWindow", "MessageBox", "SetWindowText", "GetClientRect", "GetWindowRect",
                "AdjustWindowRect", "AdjustWindowRectEx", "LoadCursor", "LoadIcon", "LoadImage", "PostQuitMessage", "SetCursorPos", "GetCursorPos",
                "ClientToScreen", "ScreenToClient", "GetAsyncKeyState", "GetKeyState", "SendMessage", "PostMessage", "SetWindowLongPtr", "GetWindowLongPtr",
                "SetWindowLong", "GetWindowLong", "SetWindowPos", "GetDC", "ReleaseDC", "MapVirtualKey", "GetRawInputData", "RegisterRawInputDevices",
                "ShowCursor", "ClipCursor", "SetCapture", "ReleaseCapture", "GetSystemMetrics", "MonitorFromWindow", "GetMonitorInfo", "EnumDisplayMonitors",
                "SetProcessDPIAware", "GetDpiForWindow", "DestroyWindow", "IsIconic", "IsZoomed", "SetFocus", "SetForegroundWindow", "SetTimer", "KillTimer",
                "MessageBeep", "GetForegroundWindow", "GetCapture", "SetWindowsHookEx", "UnhookWindowsHookEx", "CallNextHookEx", "GetActiveWindow",
                "SystemParametersInfo", "EnumDisplaySettings", "ChangeDisplaySettings", "LoadString", "wsprintf", "CharUpper", "CharLower", "GetFocus");
            Add("gdi32.lib",
                "CreateCompatibleDC", "BitBlt", "StretchBlt", "SelectObject", "DeleteObject", "GetStockObject", "CreateFont", "CreateFontIndirect", "TextOut",
                "SetBkMode", "SetTextColor", "CreateSolidBrush", "GetDeviceCaps", "StretchDIBits", "CreateDIBSection", "SetPixel", "GetObject",
                "CreateCompatibleBitmap", "DeleteDC", "SwapBuffers", "ChoosePixelFormat", "SetPixelFormat", "CreateBitmap", "GetDIBits");
            Add("shell32.lib",
                "ShellExecute", "ShellExecuteEx", "SHGetFolderPath", "SHGetKnownFolderPath", "CommandLineToArgvW", "DragAcceptFiles", "DragQueryFile",
                "DragFinish", "SHFileOperation", "Shell_NotifyIcon", "ExtractIcon", "SHBrowseForFolder", "SHGetFileInfo", "SHGetSpecialFolderPath",
                "SHCreateDirectoryEx", "SHGetPathFromIDList");
            Add("shlwapi.lib",
                "PathFindFileName", "PathCombine", "PathRemoveFileSpec", "PathFileExists", "PathIsRelative", "PathAppend", "PathCanonicalize", "StrStrI",
                "PathFindExtension", "PathRemoveExtension", "PathIsDirectory", "PathStripPath", "PathRelativePathTo", "PathAddBackslash", "PathRenameExtension",
                "SHGetValue", "SHSetValue", "StrToInt", "StrCmpLogicalW");
            Add("ole32.lib",
                "CoInitialize", "CoInitializeEx", "CoUninitialize", "CoCreateInstance", "CoTaskMemFree", "CoTaskMemAlloc", "CreateStreamOnHGlobal",
                "StringFromGUID2", "CLSIDFromString", "CoCreateGuid", "CoGetMalloc", "OleInitialize", "OleUninitialize", "PropVariantClear",
                "CoSetProxyBlanket", "CoInitializeSecurity", "CoCreateInstanceEx", "StringFromCLSID", "IIDFromString");
            Add("oleaut32.lib", "SysAllocString", "SysFreeString", "SysStringLen", "VariantClear", "VariantInit", "SafeArrayCreate", "SysAllocStringLen", "VariantChangeType");
            Add("advapi32.lib",
                "RegOpenKey", "RegOpenKeyEx", "RegCloseKey", "RegQueryValue", "RegQueryValueEx", "RegSetValue", "RegSetValueEx", "RegCreateKey",
                "RegCreateKeyEx", "RegGetValue", "RegEnumKey", "RegEnumKeyEx", "RegEnumValue", "RegDeleteKey", "RegDeleteValue", "GetUserName",
                "OpenProcessToken", "CryptAcquireContext", "CryptGenRandom", "CryptReleaseContext", "LookupPrivilegeValue", "AdjustTokenPrivileges",
                "OpenSCManager", "CreateService", "EventRegister", "EventWrite", "GetTokenInformation", "InitiateSystemShutdown");
            Add("winmm.lib",
                "timeGetTime", "timeBeginPeriod", "timeEndPeriod", "timeGetDevCaps", "PlaySound", "waveOutOpen", "waveOutWrite", "waveOutClose", "joyGetPos",
                "joyGetPosEx", "joyGetDevCaps", "joyGetNumDevs", "midiOutOpen", "mciSendString", "mmioOpen");
            Add("ws2_32.lib",
                "WSAStartup", "WSACleanup", "WSAGetLastError", "WSASocket", "WSAIoctl", "WSARecv", "WSASend", "WSAPoll", "socket", "bind", "listen", "accept",
                "connect", "send", "recv", "sendto", "recvfrom", "closesocket", "getaddrinfo", "freeaddrinfo", "select", "htons", "htonl", "ntohs", "ntohl",
                "ioctlsocket", "setsockopt", "getsockopt", "inet_pton", "inet_ntop", "gethostname", "shutdown", "getsockname", "getpeername");
            Add("d3d11.lib", "D3D11CreateDevice", "D3D11CreateDeviceAndSwapChain");
            Add("d3d12.lib", "D3D12CreateDevice", "D3D12GetDebugInterface", "D3D12SerializeRootSignature", "D3D12SerializeVersionedRootSignature",
                "D3D12CreateRootSignatureDeserializer", "D3D12EnableExperimentalFeatures", "D3D12CreateVersionedRootSignatureDeserializer");
            Add("dxgi.lib", "CreateDXGIFactory", "CreateDXGIFactory1", "CreateDXGIFactory2", "DXGIGetDebugInterface1", "DXGIDeclareAdapterRemovalSupport");
            Add("d3dcompiler.lib", "D3DCompile", "D3DCompile2", "D3DCompileFromFile", "D3DReflect", "D3DCreateBlob", "D3DReadFileToBlob", "D3DWriteBlobToFile",
                "D3DDisassemble", "D3DPreprocess", "D3DGetBlobPart", "D3DStripShader", "D3DGetInputSignatureBlob");
            Add("dxguid.lib", "DXGI_DEBUG_ALL", "DXGI_DEBUG_DX", "DXGI_DEBUG_DXGI", "DXGI_DEBUG_APP");
            Add("xinput.lib", "XInputGetState", "XInputSetState", "XInputEnable", "XInputGetCapabilities", "XInputGetBatteryInformation");
            Add("dinput8.lib", "DirectInput8Create");
            Add("dwmapi.lib", "DwmSetWindowAttribute", "DwmGetWindowAttribute", "DwmExtendFrameIntoClientArea", "DwmFlush", "DwmIsCompositionEnabled", "DwmEnableBlurBehindWindow");
            Add("comctl32.lib", "InitCommonControls", "InitCommonControlsEx", "DefSubclassProc", "SetWindowSubclass", "RemoveWindowSubclass", "TaskDialog", "TaskDialogIndirect");
            Add("comdlg32.lib", "GetOpenFileName", "GetSaveFileName", "ChooseColor", "ChooseFont", "PrintDlg");
            Add("version.lib", "GetFileVersionInfo", "GetFileVersionInfoSize", "VerQueryValue");
            Add("dbghelp.lib", "SymInitialize", "SymCleanup", "SymFromAddr", "MiniDumpWriteDump", "StackWalk64", "SymGetLineFromAddr64", "SymSetOptions",
                "SymLoadModule64", "SymGetModuleBase64", "SymFunctionTableAccess64", "ImageNtHeader", "UnDecorateSymbolName");
            Add("crypt32.lib", "CryptProtectData", "CryptUnprotectData", "CertOpenStore", "CertOpenSystemStore", "CertFindCertificateInStore", "CryptStringToBinary", "CryptBinaryToString");
            Add("bcrypt.lib", "BCryptGenRandom", "BCryptOpenAlgorithmProvider", "BCryptCloseAlgorithmProvider", "BCryptHash", "BCryptCreateHash", "BCryptHashData", "BCryptFinishHash");
            Add("iphlpapi.lib", "GetAdaptersInfo", "GetAdaptersAddresses", "GetIpAddrTable", "GetBestInterface", "IcmpSendEcho", "IcmpCreateFile");
            Add("winhttp.lib", "WinHttpOpen", "WinHttpConnect", "WinHttpOpenRequest", "WinHttpSendRequest", "WinHttpReceiveResponse", "WinHttpReadData", "WinHttpCloseHandle");
            Add("wininet.lib", "InternetOpen", "InternetConnect", "InternetOpenUrl", "InternetReadFile", "InternetCloseHandle", "HttpOpenRequest", "HttpSendRequest");
            Add("setupapi.lib", "SetupDiGetClassDevs", "SetupDiEnumDeviceInterfaces", "SetupDiGetDeviceInterfaceDetail", "SetupDiDestroyDeviceInfoList", "SetupDiEnumDeviceInfo");
            Add("d2d1.lib", "D2D1CreateFactory", "D2D1MakeRotateMatrix", "D2D1CreateDevice", "D2D1CreateDeviceContext", "D2D1MakeSkewMatrix", "D2D1InvertMatrix");
            Add("dwrite.lib", "DWriteCreateFactory");
            Add("xaudio2.lib", "XAudio2Create");
            Add("opengl32.lib", "wglCreateContext", "wglMakeCurrent", "wglDeleteContext", "wglGetProcAddress", "wglGetCurrentContext", "wglGetCurrentDC", "wglSwapBuffers");
            Add("glu32.lib", "gluPerspective", "gluLookAt", "gluOrtho2D", "gluErrorString");
            Add("mfplat.lib", "MFStartup", "MFShutdown", "MFCreateMediaType", "MFCreateAttributes", "MFCreateMemoryBuffer", "MFCreateSample");
            Add("mfreadwrite.lib", "MFCreateSourceReaderFromURL", "MFCreateSourceReaderFromMediaSource", "MFCreateSinkWriterFromURL");
            Add("mf.lib", "MFCreateMediaSession", "MFCreateTopology", "MFCreateSourceResolver");
            Add("mfuuid.lib", "MR_VIDEO_RENDER_SERVICE", "MF_MT_MAJOR_TYPE", "MFMediaType_Audio", "MFMediaType_Video");
            Add("uuid.lib", "FOLDERID_RoamingAppData", "FOLDERID_LocalAppData", "FOLDERID_Documents", "FOLDERID_Desktop");
            Add("psapi.lib", "EnumProcesses", "EnumProcessModules", "GetModuleFileNameEx", "GetModuleInformation", "GetProcessMemoryInfo", "GetModuleBaseName");
            Add("userenv.lib", "GetUserProfileDirectory", "CreateEnvironmentBlock");
            Add("wtsapi32.lib", "WTSRegisterSessionNotification", "WTSUnRegisterSessionNotification", "WTSEnumerateSessions");
            Add("rpcrt4.lib", "UuidCreate", "UuidToString", "RpcStringFree", "UuidFromString");
            Add("netapi32.lib", "NetUserGetInfo", "NetApiBufferFree", "NetWkstaGetInfo");
            Add("pdh.lib", "PdhOpenQuery", "PdhAddCounter", "PdhCollectQueryData", "PdhGetFormattedCounterValue");

            Win32Prefix = new[]
            {
                new[] { "D3D12", "d3d12.lib" }, new[] { "D3D11", "d3d11.lib" }, new[] { "D3DCompile", "d3dcompiler.lib" }, new[] { "D3DX", "d3dx9.lib" },
                new[] { "Dwm", "dwmapi.lib" }, new[] { "XInput", "xinput.lib" }, new[] { "WSA", "ws2_32.lib" }, new[] { "WinHttp", "winhttp.lib" },
                new[] { "SetupDi", "setupapi.lib" }, new[] { "wgl", "opengl32.lib" }, new[] { "glu", "glu32.lib" }, new[] { "gl", "opengl32.lib" },
                new[] { "SH", "shell32.lib" }, new[] { "Shell", "shell32.lib" }, new[] { "Path", "shlwapi.lib" }, new[] { "BCrypt", "bcrypt.lib" },
                new[] { "Crypt", "advapi32.lib" }, new[] { "MF", "mfplat.lib" }, new[] { "time", "winmm.lib" }, new[] { "IID_", "dxguid.lib" },
                new[] { "CLSID_", "uuid.lib" }
            };
        }

        private static void Add(string lib, params string[] names)
        {
            foreach (string n in names) Win32Exact[n] = lib;
        }

        /// <summary>
        /// Windows / DirectX の関数やデータなら、必要な .lib の名前を返す。違えば null。
        /// 「__imp_」が付く名前(dllimport)と、IID_ / CLSID_ の GUID だけを対象にする。
        /// </summary>
        public static string Win32Lib(string mangled)
        {
            if (string.IsNullOrEmpty(mangled)) return null;
            bool imp = mangled.StartsWith("__imp_", StringComparison.Ordinal);
            string n = imp ? mangled.Substring(6) : mangled;
            n = n.TrimStart('_');
            int at = n.LastIndexOf('@');
            if (at > 0 && at + 1 < n.Length && char.IsDigit(n[at + 1])) n = n.Substring(0, at);   // x86: _Name@16

            if (!imp)
            {
                if (n.StartsWith("IID_", StringComparison.Ordinal)) return "dxguid.lib";
                if (n.StartsWith("DXGI_DEBUG", StringComparison.Ordinal)) return "dxguid.lib";
                return null;
            }

            string lib;
            if (Win32Exact.TryGetValue(n, out lib)) return lib;
            if (n.Length > 1 && (n.EndsWith("A", StringComparison.Ordinal) || n.EndsWith("W", StringComparison.Ordinal))
                && Win32Exact.TryGetValue(n.Substring(0, n.Length - 1), out lib)) return lib;
            if (n.Length > 2 && (n.EndsWith("ExA", StringComparison.Ordinal) || n.EndsWith("ExW", StringComparison.Ordinal))
                && Win32Exact.TryGetValue(n.Substring(0, n.Length - 3), out lib)) return lib;

            foreach (string[] p in Win32Prefix)
            {
                if (!n.StartsWith(p[0], StringComparison.Ordinal) || n.Length <= p[0].Length) continue;
                // 小文字の接頭辞(gl, time)は、そのあとが大文字のときだけ(glClear、timeGetTime)
                char next = n[p[0].Length];
                if (char.IsLower(p[0][0]) && !char.IsUpper(next)) continue;
                return p[1];
            }
            return null;
        }

        // ---- LNK2038 の値の読み方 ----

        public static string DescribeMismatch(string key, string value)
        {
            switch (key)
            {
                case "RuntimeLibrary":
                    switch (value)
                    {
                        case "MT_StaticRelease": return "/MT (静的リンク・Release)";
                        case "MTd_StaticDebug": return "/MTd (静的リンク・Debug)";
                        case "MD_DynamicRelease": return "/MD (DLL・Release)";
                        case "MDd_DynamicDebug": return "/MDd (DLL・Debug)";
                    }
                    break;
                case "_ITERATOR_DEBUG_LEVEL":
                    switch (value)
                    {
                        case "0": return "0 (反復子のデバッグなし。Release)";
                        case "1": return "1 (反復子のデバッグ(検査つき))";
                        case "2": return "2 (反復子のデバッグあり。Debug)";
                    }
                    break;
                case "annotate_string":
                case "annotate_vector":
                    return value == "0" ? "0 (ASan の注釈なし)" : value + " (ASan の注釈あり)";
            }
            return value;
        }
    }
}

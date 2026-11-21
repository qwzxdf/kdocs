using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;

namespace KCppAssist
{
    /// <summary>画面に出す言語。設定の「表示する言語」。</summary>
    public enum UiLanguage { Japanese, English, ChineseSimplified, Korean }

    /// <summary>
    /// 画面の文字の翻訳。日本語の原文をそのまま鍵にして、英語・中国語(簡体字)・韓国語を引く。
    /// 表にない文字は、英語の表にあれば英語、なければ日本語のまま出す(訳していない所が空にならないように)。
    /// 文の途中に名前が入るものは、F の「{0}」で書く(語順が言語ごとに違うため、文字列をつないで作らない)。
    /// </summary>
    internal static class L
    {
        /// <summary>いまの言語。設定を読んだとき・変えたときに、パッケージが入れる。</summary>
        public static volatile UiLanguage Current = UiLanguage.Japanese;

        public static string T(string ja)
        {
            if (string.IsNullOrEmpty(ja) || Current == UiLanguage.Japanese) return ja;
            string[] row;
            if (!Table.TryGetValue(ja, out row) && !LangDescriptions.Rows.TryGetValue(ja, out row) && !LangMessages.Rows.TryGetValue(ja, out row) && !LangMore.Rows.TryGetValue(ja, out row)) return ja;
            int i = Current == UiLanguage.English ? 0 : Current == UiLanguage.ChineseSimplified ? 1 : 2;
            if (i < row.Length && !string.IsNullOrEmpty(row[i])) return row[i];
            return string.IsNullOrEmpty(row[0]) ? ja : row[0];
        }

        public static string F(string jaFormat, params object[] args)
        {
            try { return string.Format(T(jaFormat), args); }
            catch (FormatException) { return string.Format(jaFormat, args); }
        }

        // 文字コードの表などで、決まった言い回しを組み合わせた文を訳すための部品(長いものから順に置き換える)
        private static readonly string[] PhraseKeys =
        {
            "読めない (バイナリか、どの文字コードでもない)", "Shift-JIS にない文字があるので変換しない: ", "大きすぎるので飛ばす (8 MB 超)",
            "未保存なので飛ばす", "UTF-8 (BOM なし)", "UTF-8 (BOM 付き)", "変換しました", "ASCII のみ", "読めない: ", "失敗: ",
            "バイナリ?", "そのまま", "改行 ", "混在", "なし", "、",
        };

        /// <summary>決まった言い回しを組み合わせた文(「UTF-8 (BOM なし) → UTF-8 (BOM 付き)、改行 LF → CRLF」など)を、言い回しごとに訳す。</summary>
        public static string Phrases(string s)
        {
            if (string.IsNullOrEmpty(s) || Current == UiLanguage.Japanese) return s;
            string whole = T(s);
            if (whole != s) return whole;
            foreach (string k in PhraseKeys) if (s.Contains(k)) s = s.Replace(k, T(k));
            return s;
        }

        /// <summary>PC(Windows)の表示言語から決める。日本語・中国語・韓国語以外は英語。</summary>
        public static UiLanguage FromCulture(CultureInfo c)
        {
            string n = c == null ? "" : c.Name.ToLowerInvariant();
            if (n.StartsWith("ja")) return UiLanguage.Japanese;
            if (n.StartsWith("zh")) return UiLanguage.ChineseSimplified;
            if (n.StartsWith("ko")) return UiLanguage.Korean;
            return UiLanguage.English;
        }

        // 日本語 → { 英語, 中国語(簡体字), 韓国語 }
        private static readonly Dictionary<string, string[]> Table = new Dictionary<string, string[]>(StringComparer.Ordinal)
        {
            // ---- メニュー ----
            ["K-Cpp: 使い方..."] = new[] { "K-Cpp: How to use...", "K-Cpp: 使用说明...", "K-Cpp: 사용법..." },
            ["K-Cpp: #include を整理（プロジェクト全体）"] = new[] { "K-Cpp: Organize #include (whole project)", "K-Cpp: 整理 #include（整个项目）", "K-Cpp: #include 정리 (프로젝트 전체)" },
            ["K-Cpp: 使っていない #include を消す（プロジェクト全体）"] = new[] { "K-Cpp: Remove unused #include (whole project)", "K-Cpp: 删除未使用的 #include（整个项目）", "K-Cpp: 사용하지 않는 #include 삭제 (프로젝트 전체)" },
            ["K-Cpp: このファイルの #include を整理"] = new[] { "K-Cpp: Organize #include in this file", "K-Cpp: 整理此文件的 #include", "K-Cpp: 이 파일의 #include 정리" },
            ["K-Cpp: #include を前方宣言にする (Forward / Alt+F)"] = new[] { "K-Cpp: Replace #include with forward declaration (Forward / Alt+F)", "K-Cpp: 将 #include 改为前向声明 (Forward / Alt+F)", "K-Cpp: #include를 전방 선언으로 바꾸기 (Forward / Alt+F)" },
            ["K-Cpp: メンバーからコンストラクターを作る (Constructor / Alt+C)"] = new[] { "K-Cpp: Generate constructor from members (Constructor / Alt+C)", "K-Cpp: 根据成员生成构造函数 (Constructor / Alt+C)", "K-Cpp: 멤버로 생성자 만들기 (Constructor / Alt+C)" },
            ["K-Cpp: 基底クラスの仮想関数を override する (Override / Alt+O)"] = new[] { "K-Cpp: Override base class virtual functions (Override / Alt+O)", "K-Cpp: 重写基类虚函数 (Override / Alt+O)", "K-Cpp: 기본 클래스의 가상 함수 override (Override / Alt+O)" },
            ["K-Cpp: 呼び出しから関数を作る (Usage / Alt+U)"] = new[] { "K-Cpp: Generate function from call (Usage / Alt+U)", "K-Cpp: 根据调用生成函数 (Usage / Alt+U)", "K-Cpp: 호출로 함수 만들기 (Usage / Alt+U)" },
            ["K-Cpp: ファイルの文字コードをそろえる..."] = new[] { "K-Cpp: Unify file encodings...", "K-Cpp: 统一文件编码...", "K-Cpp: 파일 인코딩 통일..." },
            ["K-Cpp: この位置の書き換え・生成の一覧... (eXplore / Alt+X)"] = new[] { "K-Cpp: Refactorings and generators here... (eXplore / Alt+X)", "K-Cpp: 此处可用的重写与生成... (eXplore / Alt+X)", "K-Cpp: 이 위치의 리팩터링·생성 목록... (eXplore / Alt+X)" },
            ["ローカル変数に型を付ける (Qualify type / Alt+Q)"] = new[] { "Add type to local variable (Qualify type / Alt+Q)", "为局部变量添加类型 (Qualify type / Alt+Q)", "지역 변수에 형식 붙이기 (Qualify type / Alt+Q)" },
            ["メンバー変数として宣言する (Write member / Alt+W)"] = new[] { "Declare as member variable (Write member / Alt+W)", "声明为成员变量 (Write member / Alt+W)", "멤버 변수로 선언 (Write member / Alt+W)" },
            ["Getter・Setter を作る (Getter / Alt+G)"] = new[] { "Generate Getter / Setter (Getter / Alt+G)", "生成 Getter / Setter (Getter / Alt+G)", "Getter·Setter 만들기 (Getter / Alt+G)" },
            ["#include を足す (Include / Alt+I)"] = new[] { "Add #include (Include / Alt+I)", "添加 #include (Include / Alt+I)", "#include 추가 (Include / Alt+I)" },
            ["宣言と定義の引数を合わせる (Sync / Alt+S)"] = new[] { "Sync declaration and definition parameters (Sync / Alt+S)", "同步声明与定义的参数 (Sync / Alt+S)", "선언과 정의의 매개변수 맞추기 (Sync / Alt+S)" },
            ["宣言・定義の相手を作る (Resolve / Alt+R)"] = new[] { "Create matching declaration / definition (Resolve / Alt+R)", "生成对应的声明 / 定义 (Resolve / Alt+R)", "짝이 되는 선언·정의 만들기 (Resolve / Alt+R)" },
            ["関数を ヘッダー ⇄ cpp に移す (Move / Alt+M)"] = new[] { "Move function between header ⇄ cpp (Move / Alt+M)", "在头文件 ⇄ cpp 之间移动函数 (Move / Alt+M)", "함수를 헤더 ⇄ cpp로 옮기기 (Move / Alt+M)" },
            ["ファイル名をまとめて変える (Name / Alt+N)"] = new[] { "Rename files together (Name / Alt+N)", "一起重命名文件 (Name / Alt+N)", "파일 이름 함께 바꾸기 (Name / Alt+N)" },
            ["K-ErrorLog (エラーログ)を開く"] = new[] { "Open K-ErrorLog (error log)", "打开 K-ErrorLog（错误日志）", "K-ErrorLog (오류 로그) 열기" },
            ["K-Cpp: 設定..."] = new[] { "K-Cpp: Settings...", "K-Cpp: 设置...", "K-Cpp: 설정..." },

            // ---- 電球(Quick Fix)・Alt+X の一覧 ----
            ["宣言から cpp に定義を作る"] = new[] { "Create definition in cpp from declaration", "根据声明在 cpp 中生成定义", "선언으로 cpp에 정의 만들기" },
            ["cpp の定義の引数を、この宣言に合わせる"] = new[] { "Match cpp definition parameters to this declaration", "使 cpp 定义的参数与此声明一致", "cpp 정의의 매개변수를 이 선언에 맞추기" },
            ["定義からヘッダーに宣言を作る"] = new[] { "Create declaration in header from definition", "根据定义在头文件中生成声明", "정의로 헤더에 선언 만들기" },
            ["ヘッダーの宣言の引数を、この定義に合わせる"] = new[] { "Match header declaration parameters to this definition", "使头文件声明的参数与此定义一致", "헤더 선언의 매개변수를 이 정의에 맞추기" },
            ["#include を前方宣言にして、cpp に #include を移す"] = new[] { "Replace #include with forward declaration and move #include to cpp", "将 #include 改为前向声明，并把 #include 移到 cpp", "#include를 전방 선언으로 바꾸고 #include를 cpp로 옮기기" },
            ["関数の本体を cpp に移す"] = new[] { "Move function body to cpp", "将函数体移到 cpp", "함수 본문을 cpp로 옮기기" },
            ["関数の本体をヘッダーに移す"] = new[] { "Move function body to header", "将函数体移到头文件", "함수 본문을 헤더로 옮기기" },
            ["基底クラスの仮想関数を override する"] = new[] { "Override base class virtual functions", "重写基类虚函数", "기본 클래스의 가상 함수 override" },
            ["メンバーからコンストラクターを作る"] = new[] { "Generate constructor from members", "根据成员生成构造函数", "멤버로 생성자 만들기" },
            ["ローカル変数として型を付ける ({0})"] = new[] { "Add type as local variable ({0})", "作为局部变量添加类型 ({0})", "지역 변수로 형식 붙이기 ({0})" },
            ["メンバー変数としてヘッダーに宣言する ({0})"] = new[] { "Declare in header as member variable ({0})", "作为成员变量在头文件中声明 ({0})", "멤버 변수로 헤더에 선언 ({0})" },
            ["Getter・Setter を作る"] = new[] { "Generate Getter / Setter", "生成 Getter / Setter", "Getter·Setter 만들기" },
            ["Getter を作る"] = new[] { "Generate Getter", "生成 Getter", "Getter 만들기" },
            ["Setter を作る"] = new[] { "Generate Setter", "生成 Setter", "Setter 만들기" },
            ["{0} を前方宣言にする (#include を cpp に移す)"] = new[] { "Forward-declare {0} (move #include to cpp)", "将 {0} 改为前向声明（把 #include 移到 cpp）", "{0}을(를) 전방 선언으로 (#include를 cpp로 옮김)" },
            ["#include を足す ({0})"] = new[] { "Add #include ({0})", "添加 #include ({0})", "#include 추가 ({0})" },
            ["このファイルの #include を整理する"] = new[] { "Organize #include in this file", "整理此文件的 #include", "이 파일의 #include 정리" },
            ["このファイルの使っていない #include を消す"] = new[] { "Remove unused #include in this file", "删除此文件中未使用的 #include", "이 파일에서 사용하지 않는 #include 삭제" },
            ["NULL を nullptr にする (この行)"] = new[] { "Replace NULL with nullptr (this line)", "将 NULL 改为 nullptr（此行）", "NULL을 nullptr로 (이 줄)" },
            ["NULL を nullptr にする (ファイル全体)"] = new[] { "Replace NULL with nullptr (whole file)", "将 NULL 改为 nullptr（整个文件）", "NULL을 nullptr로 (파일 전체)" },
            ["typedef を using にする"] = new[] { "Convert typedef to using", "将 typedef 改为 using", "typedef를 using으로" },
            ["C のキャストを static_cast にする"] = new[] { "Convert C-style cast to static_cast", "将 C 风格转换改为 static_cast", "C 캐스트를 static_cast로" },
            ["添字の for を範囲 for にする"] = new[] { "Convert index for to range-based for", "将下标 for 改为范围 for", "인덱스 for를 범위 for로" },
            ["if を反転する (then と else を入れ替える)"] = new[] { "Invert if (swap then and else)", "反转 if（交换 then 与 else）", "if 반전 (then과 else 교체)" },
            ["if を早期 return / continue にして入れ子を浅くする"] = new[] { "Use early return / continue to reduce nesting", "改为提前 return / continue 以减少嵌套", "조기 return / continue로 중첩 줄이기" },
            ["型を auto にする"] = new[] { "Use auto for the type", "将类型改为 auto", "형식을 auto로" },
            ["この変数をデバッグ出力する (OutputDebugString)"] = new[] { "Debug-print this variable (OutputDebugString)", "调试输出此变量 (OutputDebugString)", "이 변수를 디버그 출력 (OutputDebugString)" },
            ["デバッグ出力の行 (// KDBG) をすべて消す"] = new[] { "Remove all debug-print lines (// KDBG)", "删除所有调试输出行 (// KDBG)", "디버그 출력 줄 (// KDBG) 모두 삭제" },
            ["enum の ToString / FromString を作る"] = new[] { "Generate ToString / FromString for enum", "为 enum 生成 ToString / FromString", "enum의 ToString / FromString 만들기" },
            ["初期化子リストを、メンバーの宣言の順に並べ替える"] = new[] { "Reorder initializer list to member declaration order", "按成员声明顺序重排初始化列表", "초기화 목록을 멤버 선언 순서로 정렬" },
            ["コンストラクター・デストラクターを作る (= default)"] = new[] { "Generate constructor / destructor (= default)", "生成构造函数 / 析构函数 (= default)", "생성자·소멸자 만들기 (= default)" },
            ["コンストラクター・デストラクターを作る (.h に {} で書く)"] = new[] { "Generate constructor / destructor ({} in .h)", "生成构造函数 / 析构函数（在 .h 中写 {}）", "생성자·소멸자 만들기 (.h에 {}로)" },
            ["コンストラクター・デストラクターを作る (.h に宣言、.cpp に定義)"] = new[] { "Generate constructor / destructor (declare in .h, define in .cpp)", "生成构造函数 / 析构函数（.h 声明，.cpp 定义）", "생성자·소멸자 만들기 (.h에 선언, .cpp에 정의)" },
            ["コピー・ムーブを禁止する (= delete)"] = new[] { "Disable copy and move (= delete)", "禁止复制与移动 (= delete)", "복사·이동 금지 (= delete)" },
            ["コピー禁止・ムーブ可にする (= delete / = default)"] = new[] { "Disable copy, allow move (= delete / = default)", "禁止复制、允许移动 (= delete / = default)", "복사 금지·이동 허용 (= delete / = default)" },
            ["コピー・ムーブ・デストラクターを = default で書く"] = new[] { "Write copy / move / destructor as = default", "将复制 / 移动 / 析构写为 = default", "복사·이동·소멸자를 = default로 작성" },
            ["== と <=> を = default で作る"] = new[] { "Generate == and <=> as = default", "以 = default 生成 == 与 <=>", "== 와 <=> 를 = default로 만들기" },
            ["std::format で書けるようにする (std::formatter)"] = new[] { "Make formattable with std::format (std::formatter)", "使其可用于 std::format (std::formatter)", "std::format으로 출력 가능하게 (std::formatter)" },
            ["std::unordered_map のキーにできるようにする (std::hash)"] = new[] { "Make usable as std::unordered_map key (std::hash)", "使其可作为 std::unordered_map 的键 (std::hash)", "std::unordered_map의 키로 쓸 수 있게 (std::hash)" },
            ["JSON に読み書きできるようにする (nlohmann)"] = new[] { "Make JSON serializable (nlohmann)", "使其可读写 JSON (nlohmann)", "JSON 읽기·쓰기 가능하게 (nlohmann)" },
            ["cereal で保存できるようにする (serialize)"] = new[] { "Make serializable with cereal (serialize)", "使其可用 cereal 保存 (serialize)", "cereal로 저장 가능하게 (serialize)" },
            ["頂点構造体から入力レイアウトを作る (D3D)"] = new[] { "Generate input layout from vertex struct (D3D)", "根据顶点结构生成输入布局 (D3D)", "정점 구조체로 입력 레이아웃 만들기 (D3D)" },
            ["定数バッファの並びを HLSL に合わせる (パディング)"] = new[] { "Align constant buffer layout to HLSL (padding)", "使常量缓冲区布局与 HLSL 一致（填充）", "상수 버퍼 배치를 HLSL에 맞추기 (패딩)" },
            ["{0}.cpp を作る"] = new[] { "Create {0}.cpp", "创建 {0}.cpp", "{0}.cpp 만들기" },
            ["デバッガーの表示 (Natvis) を作る"] = new[] { "Generate debugger display (Natvis)", "生成调试器显示 (Natvis)", "디버거 표시 (Natvis) 만들기" },
            ["定義のない関数を、cpp にまとめて作る"] = new[] { "Create all missing definitions in cpp", "在 cpp 中一并生成缺少的定义", "정의가 없는 함수를 cpp에 한꺼번에 만들기" },
            ["クラスを {0}.h / .cpp に移す"] = new[] { "Move class to {0}.h / .cpp", "将类移到 {0}.h / .cpp", "클래스를 {0}.h / .cpp로 옮기기" },
            ["pimpl にする (実装を cpp の Impl に移す)"] = new[] { "Convert to pimpl (move implementation to Impl in cpp)", "改为 pimpl（把实现移到 cpp 的 Impl）", "pimpl로 바꾸기 (구현을 cpp의 Impl로 옮김)" },

            // ---- ダイアログ ----
            ["ほかのファイルにも反映しますか?"] = new[] { "Apply the change to other files too?", "也要应用到其他文件吗？", "다른 파일에도 반영할까요?" },
            ["次から確認しない"] = new[] { "Don't ask again", "下次不再询问", "다음부터 묻지 않기" },
            ["反映する"] = new[] { "Apply", "应用", "반영" },
            ["全部に反映する"] = new[] { "Apply to all", "全部应用", "모두 반영" },
            ["何もしない"] = new[] { "Do nothing", "不做任何事", "아무것도 안 함" },
            ["実行する"] = new[] { "Run", "执行", "실행" },
            ["やめる"] = new[] { "Cancel", "取消", "취소" },
            ["選ぶ"] = new[] { "Select", "选择", "선택" },
            ["選んでください"] = new[] { "Choose one", "请选择", "선택하세요" },
            ["名前を入力"] = new[] { "Enter a name", "输入名称", "이름 입력" },
            ["ヘッダーの名前が変わりました"] = new[] { "Header was renamed", "头文件已重命名", "헤더 이름이 바뀌었습니다" },
            ["cpp の名前が変わりました"] = new[] { "cpp file was renamed", "cpp 文件已重命名", "cpp 이름이 바뀌었습니다" },
            ["ファイルを別のフォルダーに移しました"] = new[] { "File was moved to another folder", "文件已移到其他文件夹", "파일을 다른 폴더로 옮겼습니다" },
            ["ファイルの名前と場所が変わりました"] = new[] { "File was renamed and moved", "文件的名称和位置已更改", "파일 이름과 위치가 바뀌었습니다" },
            ["クラス名が変わりました"] = new[] { "Class was renamed", "类已重命名", "클래스 이름이 바뀌었습니다" },
            ["フォルダーの名前が変わりました"] = new[] { "Folder was renamed", "文件夹已重命名", "폴더 이름이 바뀌었습니다" },
            ["フォルダーを移しました"] = new[] { "Folder was moved", "文件夹已移动", "폴더를 옮겼습니다" },
            ["{0} 個のファイルを移しました"] = new[] { "{0} files were moved", "已移动 {0} 个文件", "파일 {0}개를 옮겼습니다" },
            ["{0} 個のファイルの名前が変わりました"] = new[] { "{0} files were renamed", "{0} 个文件已重命名", "파일 {0}개의 이름이 바뀌었습니다" },
            ["相手の cpp の名前・#include・CMake も直す"] = new[] { "Also rename the paired cpp and update #include / CMake", "同时重命名对应的 cpp，并更新 #include / CMake", "짝 cpp 이름·#include·CMake도 고치기" },
            ["相手のヘッダーの名前・#include・CMake も直す"] = new[] { "Also rename the paired header and update #include / CMake", "同时重命名对应的头文件，并更新 #include / CMake", "짝 헤더 이름·#include·CMake도 고치기" },
            ["#include・CMake も直す"] = new[] { "Also update #include / CMake", "同时更新 #include / CMake", "#include·CMake도 고치기" },
            ["CMake のファイル名も直す"] = new[] { "Also update the file name in CMake", "同时更新 CMake 中的文件名", "CMake의 파일 이름도 고치기" },
            ["クラス名も、新しいファイル名に合わせて直す"] = new[] { "Also rename the class to match the new file name", "同时按新文件名重命名类", "클래스 이름도 새 파일 이름에 맞추기" },
            ["クラス名も直す(いまはファイル名と一致していません)"] = new[] { "Also rename the class (it does not match the file name now)", "同时重命名类（目前与文件名不一致）", "클래스 이름도 고치기 (지금은 파일 이름과 다름)" },
            ["  (コード全体の同じ名前の単語が変わります)"] = new[] { "  (every whole-word match in the code changes)", "  （代码中所有同名单词都会更改）", "  (코드 전체의 같은 이름 단어가 바뀝니다)" },
            ["全部の #include・CMake を、新しいパスに直す"] = new[] { "Update all #include / CMake to the new paths", "将所有 #include / CMake 更新为新路径", "모든 #include·CMake를 새 경로로 고치기" },
            ["相手のファイル {0} 個の名前も直す"] = new[] { "Also rename {0} paired files", "同时重命名 {0} 个对应文件", "짝 파일 {0}개의 이름도 고치기" },
            ["中のファイルを #include している所と、CMake のパスを直す"] = new[] { "Update #include of files inside and CMake paths", "更新包含其中文件的 #include 和 CMake 路径", "안의 파일을 #include하는 곳과 CMake 경로 고치기" },
            ["ファイル名・相手のファイル・#include・CMake も直す"] = new[] { "Also rename the file and its pair, and update #include / CMake", "同时重命名文件及对应文件，并更新 #include / CMake", "파일 이름·짝 파일·#include·CMake도 고치기" },
            ["ファイル名も直す (いまのファイル名 {0} は、クラス名と違っています)"] = new[] { "Also rename the file (the current file name {0} differs from the class name)", "同时重命名文件（当前文件名 {0} 与类名不同）", "파일 이름도 고치기 (지금 파일 이름 {0}은(는) 클래스 이름과 다름)" },
            ["#include を整理する"] = new[] { "Organize #include", "整理 #include", "#include 정리" },
            ["使っていない #include を消す"] = new[] { "Remove unused #include", "删除未使用的 #include", "사용하지 않는 #include 삭제" },
            ["並べ替える"] = new[] { "Reorder", "重新排序", "정렬" },
            ["消す"] = new[] { "Remove", "删除", "삭제" },
            ["文字コードをそろえる"] = new[] { "Unify encodings", "统一编码", "인코딩 통일" },
            ["そろえる"] = new[] { "Unify", "统一", "통일" },
            ["縮小変換を全部直す"] = new[] { "Fix all narrowing conversions", "修复所有收窄转换", "축소 변환 모두 고치기" },
            ["直す"] = new[] { "Fix", "修复", "고치기" },

            ["  (パスも)"] = new[] { "  (path too)", "  （包括路径）", "  (경로도)" },
            ["CMakeLists.txt の {0} → {1}"] = new[] { "{0} → {1} in CMakeLists.txt", "CMakeLists.txt 中的 {0} → {1}", "CMakeLists.txt의 {0} → {1}" },
            ["\n… ほか {0} 個"] = new[] { "\n… and {0} more", "\n… 另外 {0} 个", "\n… 외 {0}개" },
            ["ヘッダー {0} 個、cpp {1} 個\n例: #include \"{2}\" → #include \"{3}\""] = new[] { "{0} headers, {1} cpp files\ne.g. #include \"{2}\" → #include \"{3}\"", "头文件 {0} 个、cpp {1} 个\n例: #include \"{2}\" → #include \"{3}\"", "헤더 {0}개, cpp {1}개\n예: #include \"{2}\" → #include \"{3}\"" },

            // ---- 設定の分類 ----
            ["Getter・Setter"] = new[] { "Getter / Setter", "Getter / Setter", "Getter·Setter" },
            ["引数の同期"] = new[] { "Parameter sync", "参数同步", "매개변수 동기화" },
            ["名前の変更"] = new[] { "Rename", "重命名", "이름 바꾸기" },
            ["ファイル名の同期"] = new[] { "File name sync", "文件名同步", "파일 이름 동기화" },
            ["呼び出しのチェック"] = new[] { "Call checks", "调用检查", "호출 검사" },
            ["キー"] = new[] { "Keys", "快捷键", "키" },
            ["全般"] = new[] { "General", "常规", "일반" },
            ["エラーログ"] = new[] { "Error log", "错误日志", "오류 로그" },
            ["エラーログ (窓の初期値)"] = new[] { "Error log (window defaults)", "错误日志（窗口默认值）", "오류 로그 (창 기본값)" },
            ["include 整理"] = new[] { "Include cleanup", "include 整理", "include 정리" },
            ["書き換えと生成"] = new[] { "Refactoring and generation", "重写与生成", "리팩터링과 생성" },
            ["新規ファイル"] = new[] { "New files", "新文件", "새 파일" },
            ["言語"] = new[] { "Language", "语言", "언어" },

            // ---- 設定の項目名 ----
            ["表示する言語"] = new[] { "Display language", "显示语言", "표시 언어" },
            ["Getter と Setter の間に空行を入れる"] = new[] { "Insert a blank line between Getter and Setter", "在 Getter 与 Setter 之间插入空行", "Getter와 Setter 사이에 빈 줄 넣기" },
            ["#include を足すしかた"] = new[] { "How to add #include", "添加 #include 的方式", "#include 추가 방식" },
            ["自動で足す前の待ち時間 (ミリ秒)"] = new[] { "Delay before adding automatically (ms)", "自动添加前的等待时间（毫秒）", "자동 추가 전 대기 시간 (밀리초)" },
            ["自動で足さない名前"] = new[] { "Names not added automatically", "不自动添加的名称", "자동으로 추가하지 않는 이름" },
            ["ヘッダーを探さないフォルダー"] = new[] { "Folders not searched for headers", "不搜索头文件的文件夹", "헤더를 찾지 않는 폴더" },
            ["宣言と定義の引数を合わせるしかた"] = new[] { "How to sync declaration and definition parameters", "同步声明与定义参数的方式", "선언과 정의의 매개변수 맞추는 방식" },
            ["自動で合わせるまでの待ち(ミリ秒)"] = new[] { "Delay before syncing automatically (ms)", "自动同步前的等待（毫秒）", "자동으로 맞추기 전 대기 (밀리초)" },
            ["書き換えた場所を小さなウィンドウで見せる"] = new[] { "Show changed places in a small window", "在小窗口中显示修改的位置", "고친 곳을 작은 창으로 보여 주기" },
            ["宣言の名前を変えたら、使っている場所も変える"] = new[] { "Rename usages when a declaration is renamed", "重命名声明时同时更改使用处", "선언 이름을 바꾸면 사용하는 곳도 바꾸기" },
            ["型が分からない obj.name も変える"] = new[] { "Also rename obj.name whose type is unknown", "也更改类型未知的 obj.name", "형식을 모르는 obj.name도 바꾸기" },
            ["一緒に変わる場所を枠で囲む"] = new[] { "Outline places that change together", "为一起更改的位置加框", "함께 바뀌는 곳을 테두리로 표시" },
            ["引数の並べ替え・削除を、呼び出しにも写す"] = new[] { "Apply parameter reorder / removal to calls", "将参数的重排 / 删除同步到调用处", "매개변수 정렬·삭제를 호출에도 반영" },
            ["ヘッダー・cpp の名前を変えたときのしかた"] = new[] { "When a header / cpp is renamed", "重命名头文件 / cpp 时的方式", "헤더·cpp 이름을 바꿀 때의 방식" },
            ["相手のファイルも同じ名前にする"] = new[] { "Rename the paired file too", "对应文件也使用相同名称", "짝 파일도 같은 이름으로" },
            ["CMake の書き方も直す"] = new[] { "Update CMake too", "同时更新 CMake", "CMake도 고치기" },
            ["引数の個数をビルド前にチェックする"] = new[] { "Check argument counts before building", "在构建前检查参数个数", "빌드 전에 인수 개수 검사" },
            ["波線の色"] = new[] { "Squiggle color", "波浪线颜色", "물결선 색" },
            ["入力が止まってから調べるまでの待ち(ミリ秒)"] = new[] { "Delay after typing stops (ms)", "停止输入后到检查的等待（毫秒）", "입력이 멈춘 뒤 검사까지 대기 (밀리초)" },
            ["make_unique / make_shared を調べる"] = new[] { "Check make_unique / make_shared", "检查 make_unique / make_shared", "make_unique / make_shared 검사" },
            ["new T(…) を調べる"] = new[] { "Check new T(…)", "检查 new T(…)", "new T(…) 검사" },
            ["調べないクラス"] = new[] { "Classes not checked", "不检查的类", "검사하지 않는 클래스" },
            ["ファイル名をまとめて変える (Name)"] = new[] { "Rename files together (Name)", "一起重命名文件 (Name)", "파일 이름 함께 바꾸기 (Name)" },
            ["ステータスバーに知らせる"] = new[] { "Show messages in the status bar", "在状态栏中提示", "상태 표시줄에 알리기" },
            ["ログを残す"] = new[] { "Write a log", "记录日志", "로그 남기기" },
            ["標準・Windows・DirectX の表を使う"] = new[] { "Use the standard / Windows / DirectX table", "使用标准 / Windows / DirectX 表", "표준·Windows·DirectX 표 사용" },
            ["ソリューションのヘッダーの索引を使う"] = new[] { "Use the solution header index", "使用解决方案的头文件索引", "솔루션 헤더 색인 사용" },
            ["自分で決める対応 (名前=ヘッダー)"] = new[] { "Custom mappings (name=header)", "自定义对应 (名称=头文件)", "직접 정하는 대응 (이름=헤더)" },
            [".h でも、ソリューションの型を自動で足す"] = new[] { "Add solution types automatically in .h too", "在 .h 中也自动添加解决方案的类型", ".h에서도 솔루션 형식을 자동 추가" },
            ["自動で足した #include を戻すまでの秒数"] = new[] { "Seconds before reverting an auto-added #include", "撤销自动添加的 #include 的秒数", "자동 추가한 #include를 되돌리기까지 초" },
            ["#include も新しい名前に直す"] = new[] { "Update #include to the new name", "将 #include 也改为新名称", "#include도 새 이름으로 고치기" },
            ["ファイルの名前変更を、フォルダーの監視でも見つける"] = new[] { "Also detect renames by watching folders", "也通过监视文件夹检测重命名", "폴더 감시로도 이름 변경 찾기" },
            ["多数の名前変更を、自動では直さない件数"] = new[] { "Rename count treated as a bulk operation", "视为批量操作而不自动修复的重命名数", "자동으로 고치지 않는 대량 이름 변경 수" },
            ["直す前に確認する"] = new[] { "Confirm before fixing", "修复前确认", "고치기 전에 확인" },
            ["先頭に「まず一番上から」の案内を出す"] = new[] { "Show \"start from the top\" guidance first", "在开头显示“先从最上面开始”的提示", "맨 앞에 \"맨 위부터\" 안내 표시" },
            ["連鎖の可能性を示す"] = new[] { "Show possible cascades", "显示连锁错误的可能性", "연쇄 가능성 표시" },
            ["直し方の例を出す"] = new[] { "Show fix examples", "显示修复示例", "고치는 예 표시" },
            ["一度に出すエラーの数の上限"] = new[] { "Maximum errors shown at once", "一次显示的错误数上限", "한 번에 표시할 오류 수 상한" },
            ["エラーログを使う"] = new[] { "Use the error log", "使用错误日志", "오류 로그 사용" },
            ["エラーがあるとき、窓を自動で前に出す"] = new[] { "Bring the window to front on errors", "有错误时自动将窗口置前", "오류가 있으면 창을 자동으로 앞으로" },
            ["原因を探す (.lib とソースの検索)"] = new[] { "Find causes (search .lib and sources)", "查找原因（搜索 .lib 与源文件）", "원인 찾기 (.lib와 소스 검색)" },
            ["探す時間の上限 (秒)"] = new[] { "Search time limit (s)", "搜索时间上限（秒）", "검색 시간 상한 (초)" },
            ["読む .lib の数の上限"] = new[] { "Maximum .lib files to read", "读取 .lib 数量上限", "읽을 .lib 수 상한" },
            ["型名を短くする"] = new[] { "Shorten type names", "缩短类型名", "형식 이름 줄이기" },
            ["日本語のヒントを出す"] = new[] { "Show hints", "显示提示", "힌트 표시" },
            ["警告も表示"] = new[] { "Show warnings too", "也显示警告", "경고도 표시" },
            ["経路を全部表示"] = new[] { "Show the full path", "显示完整路径", "경로 전체 표시" },
            ["原文を併記"] = new[] { "Show the original message too", "同时显示原文", "원문 함께 표시" },
            ["原文"] = new[] { "Original message", "原文", "원문" },
            ["ローカル変数に型を付ける (Qualify type)"] = new[] { "Add type to local variable (Qualify type)", "为局部变量添加类型 (Qualify type)", "지역 변수에 형식 붙이기 (Qualify type)" },
            ["メンバー変数として宣言する (Write member)"] = new[] { "Declare as member variable (Write member)", "声明为成员变量 (Write member)", "멤버 변수로 선언 (Write member)" },
            ["Getter・Setter を作る (Getter)"] = new[] { "Generate Getter / Setter (Getter)", "生成 Getter / Setter (Getter)", "Getter·Setter 만들기 (Getter)" },
            ["#include を足す (Include)"] = new[] { "Add #include (Include)", "添加 #include (Include)", "#include 추가 (Include)" },
            ["宣言と定義の引数を合わせる (Sync)"] = new[] { "Sync declaration and definition parameters (Sync)", "同步声明与定义的参数 (Sync)", "선언과 정의의 매개변수 맞추기 (Sync)" },
            ["宣言・定義の相手を作る (Resolve)"] = new[] { "Create matching declaration / definition (Resolve)", "生成对应的声明 / 定义 (Resolve)", "짝이 되는 선언·정의 만들기 (Resolve)" },
            ["関数をヘッダー ⇄ cpp に移す (Move)"] = new[] { "Move function between header ⇄ cpp (Move)", "在头文件 ⇄ cpp 之间移动函数 (Move)", "함수를 헤더 ⇄ cpp로 옮기기 (Move)" },
            ["#include を前方宣言にする (Forward)"] = new[] { "Replace #include with forward declaration (Forward)", "将 #include 改为前向声明 (Forward)", "#include를 전방 선언으로 바꾸기 (Forward)" },
            ["メンバーからコンストラクターを作る (Constructor)"] = new[] { "Generate constructor from members (Constructor)", "根据成员生成构造函数 (Constructor)", "멤버로 생성자 만들기 (Constructor)" },
            ["基底クラスの仮想関数を override する (Override)"] = new[] { "Override base class virtual functions (Override)", "重写基类虚函数 (Override)", "기본 클래스의 가상 함수 override (Override)" },
            ["呼び出しから関数を作る (Usage)"] = new[] { "Generate function from call (Usage)", "根据调用生成函数 (Usage)", "호출로 함수 만들기 (Usage)" },
            ["この位置の書き換え・生成の一覧 (eXplore)"] = new[] { "Refactorings and generators here (eXplore)", "此处可用的重写与生成 (eXplore)", "이 위치의 리팩터링·생성 목록 (eXplore)" },
            ["使っていない #include を、ヘッダーからも消す"] = new[] { "Remove unused #include from headers too", "也从头文件中删除未使用的 #include", "헤더에서도 사용하지 않는 #include 삭제" },
            ["電球(Quick Fix)に出す"] = new[] { "Show in the light bulb (Quick Fix)", "在灯泡 (Quick Fix) 中显示", "전구 (Quick Fix)에 표시" },
            ["JSON (nlohmann) の項目を出す"] = new[] { "Show the JSON (nlohmann) item", "显示 JSON (nlohmann) 项", "JSON (nlohmann) 항목 표시" },
            ["cereal の項目を出す"] = new[] { "Show the cereal item", "显示 cereal 项", "cereal 항목 표시" },
            ["Natvis の項目を出す"] = new[] { "Show the Natvis item", "显示 Natvis 项", "Natvis 항목 표시" },
            ["switch を打ったら、case と default を自動で入れる"] = new[] { "Insert case and default after typing switch", "输入 switch 后自动插入 case 与 default", "switch를 입력하면 case와 default 자동 삽입" },
            ["新しい空のファイルに、ひな形を書く"] = new[] { "Write a template into new empty files", "在新的空文件中写入模板", "새 빈 파일에 템플릿 쓰기" },
            ["ヘッダーに class を書く"] = new[] { "Write a class in the header", "在头文件中写 class", "헤더에 class 쓰기" },
            ["class にコンストラクター・デストラクターを = default で書く"] = new[] { "Write constructor / destructor as = default in the class", "在 class 中以 = default 写构造 / 析构函数", "class에 생성자·소멸자를 = default로 쓰기" },
            ["クラス名の決めかた"] = new[] { "Class naming", "类名的决定方式", "클래스 이름 정하는 방식" },
            ["namespace の決めかた"] = new[] { "Namespace selection", "namespace 的决定方式", "namespace 정하는 방식" },
            ["固定の namespace"] = new[] { "Fixed namespace", "固定的 namespace", "고정 namespace" },
            ["字下げ"] = new[] { "Indentation", "缩进", "들여쓰기" },
            ["namespace の中を字下げする"] = new[] { "Indent inside namespace", "缩进 namespace 内部", "namespace 안을 들여쓰기" },
            ["インクルード ガード"] = new[] { "Include guard", "包含保护", "인클루드 가드" },
            ["namespace を閉じる行にコメントを付ける"] = new[] { "Comment the closing line of namespace", "在 namespace 结束行加注释", "namespace 닫는 줄에 주석 달기" },
            ["強制インクルードにある pch の #include を書かない"] = new[] { "Omit #include of a force-included pch", "不写强制包含中已有的 pch 的 #include", "강제 포함된 pch의 #include 쓰지 않기" },
        };
    }

    /// <summary>設定の画面の分類名を、いまの言語で出す(VS は、最初に読んだときの値を覚えるので、言語を変えたら VS を開き直す)。</summary>
    internal sealed class LocCategoryAttribute : CategoryAttribute
    {
        public LocCategoryAttribute(string ja) : base(ja) { }
        protected override string GetLocalizedString(string value) { return L.T(value); }
    }

    internal sealed class LocDisplayNameAttribute : DisplayNameAttribute
    {
        public LocDisplayNameAttribute(string ja) : base(ja) { }
        public override string DisplayName { get { return L.T(DisplayNameValue); } }
    }

    internal sealed class LocDescriptionAttribute : DescriptionAttribute
    {
        public LocDescriptionAttribute(string ja) : base(ja) { }
        public override string Description { get { return L.T(DescriptionValue); } }
    }
}

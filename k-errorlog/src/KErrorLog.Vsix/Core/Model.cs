using System;
using System.Collections.Generic;

namespace KErrorLog
{
    public enum Sev { Error, Warning, Note }

    /// <summary>主エラーに続く補足行の種類。</summary>
    public enum FrameKind
    {
        Trace,      // テンプレートのインスタンス化の経路 (see reference to ... being compiled)
        Decl,       // 宣言の場所 (see declaration of ...)
        Candidate,  // オーバーロードの候補 (could be / or)
        Reason      // 候補が落ちた理由などの、そのほかの補足
    }

    public enum DiagKind { Generic, Unresolved, MultiDefined, Mismatch }

    /// <summary>主エラーに続く補足の 1 行(note など)。</summary>
    public sealed class Frame
    {
        public string File = "";
        public int Line;
        public int Col;
        public Sev Sev = Sev.Note;
        public string Code = "";
        public string Message = "";
        public FrameKind Kind = FrameKind.Reason;
        /// <summary>この行のあとに続く、インデントされた行("with" や "[ _Ty=int ]" など)。</summary>
        public List<string> Details = new List<string>();

        public bool HasLocation { get { return File.Length > 0 && Line > 0; } }

        public string Location
        {
            get
            {
                if (!HasLocation) return File;
                return Col > 0 ? File + "(" + Line + "," + Col + ")" : File + "(" + Line + ")";
            }
        }
    }

    /// <summary>LNK2019 / LNK2001 の 1 行から取り出した、未解決のシンボルと、それを参照している関数。</summary>
    public sealed class UnresolvedRef
    {
        public string SymbolDem = "";
        public string SymbolMangled = "";
        public string FromObj = "";
        public string FuncDem = "";
        public string FuncMangled = "";
        /// <summary>lld / GNU ld のように、1 つのシンボルに参照元が複数ぶら下がる形式での、2 つ目以降の参照元(obj, 関数)。</summary>
        public List<KeyValuePair<string, string>> More = new List<KeyValuePair<string, string>>();
    }

    /// <summary>LNK2005 / LNK1169 の、二重定義。</summary>
    public sealed class MultiDefRef
    {
        public string SymbolDem = "";
        public string SymbolMangled = "";
        public string InObj = "";
        public string OtherObj = "";
    }

    /// <summary>LNK2038 の、設定の不一致 (RuntimeLibrary, _ITERATOR_DEBUG_LEVEL など)。</summary>
    public sealed class MismatchRef
    {
        public string Key = "";
        public string ValueHere = "";
        public string ValueOther = "";
        public string InObj = "";
        public string OtherObj = "";
    }

    /// <summary>ビルド出力にある 1 件のエラーまたは警告。</summary>
    public sealed class Diag
    {
        public int ProjectNo;
        public string Project = "";
        public Sev Sev = Sev.Error;
        public string Code = "";
        public string File = "";
        public int Line;
        public int Col;
        public string Message = "";
        public List<string> Details = new List<string>();
        public List<Frame> Frames = new List<Frame>();
        public List<string> Raw = new List<string>();

        public DiagKind Kind = DiagKind.Generic;
        public UnresolvedRef Unresolved;
        public MultiDefRef MultiDef;
        public MismatchRef Mismatch;

        /// <summary>「ファイルを開けない」系のエラーで、足りないファイル名(include の相対パス、.lib の名前)。</summary>
        public string MissingName = "";
        /// <summary>そのファイルが、ソリューションの下で見つかった場所(検索のあとで入る)。</summary>
        public List<string> Found = new List<string>();

        public bool HasLocation { get { return File.Length > 0 && Line > 0; } }

        public string Location
        {
            get
            {
                if (!HasLocation) return File;
                return Col > 0 ? File + "(" + Line + "," + Col + ")" : File + "(" + Line + ")";
            }
        }

        /// <summary>個々のエラーではなく、件数の集計だけを言うリンカーの行。</summary>
        public bool IsSummary { get { return Code == "LNK1120" || Code == "LNK1169"; } }

        public bool IsLinker { get { return Kind == DiagKind.Unresolved || Code.StartsWith("LNK", StringComparison.OrdinalIgnoreCase); } }
    }

    public enum RawKind { Normal, ProjectHeader, Error, Warning, Note, Summary }

    /// <summary>原文表示用の 1 行。</summary>
    public sealed class RawLine
    {
        public string Text = "";
        public RawKind Kind = RawKind.Normal;
        /// <summary>診断行なら、その場所と中身(色分けとリンクに使う)。</summary>
        public Frame Parsed;
        public bool Linker;
    }

    /// <summary>1 回のビルドの出力を解析した結果。</summary>
    public sealed class BuildReport
    {
        public List<Diag> Diags = new List<Diag>();
        public List<RawLine> RawLines = new List<RawLine>();
        public Dictionary<int, string> Projects = new Dictionary<int, string>();
        public string Config = "";
        public string Summary = "";
        /// <summary>LNK1120 が言う「未解決 N 件」。0 なら出ていない。</summary>
        public int LinkerUnresolvedTotal;
        public string RawText = "";

        /// <summary>エラーの数。LNK1120 / LNK1169 は、ほかのエラーの件数を言うだけの行なので、数えない。</summary>
        public int ErrorCount { get { return Diags.FindAll(d => d.Sev == Sev.Error && !d.IsSummary).Count; } }
        public int WarningCount { get { return Diags.FindAll(d => d.Sev == Sev.Warning).Count; } }
    }
}

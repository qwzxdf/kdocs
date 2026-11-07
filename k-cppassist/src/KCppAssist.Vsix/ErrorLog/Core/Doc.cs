using System;
using System.Collections.Generic;
using System.Text;

namespace KCppAssist.ErrorLog
{
    /// <summary>文字の役割。実際の色は Theme が、テーマ(ダーク / ライト)に合わせて決める。</summary>
    public enum Role
    {
        Normal, Dim, Error, Warning, Note, Code, Link, Scope, Func, Type, Keyword, Number, Punct, Heading, Good, Hint
    }

    /// <summary>同じ書式の文字の並び。リンクにもなる。</summary>
    public sealed class Run
    {
        public string Text = "";
        public Role Role = Role.Normal;
        public bool Bold;
        public bool Italic;
        /// <summary>リンクのとき、開くファイルと行。</summary>
        public string File;
        public int Line;
        public int Col;
        /// <summary>リンクのとき、ソリューション内を検索する語(File が空のとき)。</summary>
        public string Search;
        /// <summary>リンクのとき、ブラウザーで開く URL(https:// だけ)。</summary>
        public string Url;
        /// <summary>1 以上なら、押すとその番号の詳細を開閉する印(▸ / ▾)。</summary>
        public int Toggle;
        /// <summary>リンクのとき、窓の中でジャンプする先の名前(DocLine.Anchor)。</summary>
        public string Jump;
        /// <summary>空でなければ、押すと File の Line 行の右辺を static_cast&lt;Fix&gt;(...) で包む修正のリンク。</summary>
        public string Fix;
        /// <summary>修正のとき、ビルドの時点の行の中身(行が変わっていないかの確認用)。</summary>
        public string FixLine;

        public bool IsLink { get { return !string.IsNullOrEmpty(File) || !string.IsNullOrEmpty(Search) || !string.IsNullOrEmpty(Url) || Toggle > 0 || !string.IsNullOrEmpty(Jump); } }
    }

    public sealed class DocLine
    {
        public List<Run> Runs = new List<Run>();
        /// <summary>左の余白(段数)。</summary>
        public int Indent;
        /// <summary>この行の上に、横線を引く。</summary>
        public bool RuleAbove;
        /// <summary>左に、縦の帯(原因ごとの区切り)を付けるときの色。</summary>
        public Role? Bar;
        /// <summary>行の前の空き(段落の区切り)。</summary>
        public bool SpaceBefore;
        /// <summary>0 でなければ、この番号の詳細の行。開いているときだけ見せる。</summary>
        public int DetailGroup;
        /// <summary>ジャンプ先の名前(目次のリンクが指す)。</summary>
        public string Anchor;

        public string PlainText()
        {
            var sb = new StringBuilder();
            sb.Append(' ', Indent * 2);
            foreach (Run r in Runs) sb.Append(r.Text);
            return sb.ToString();
        }
    }

    public sealed class Doc
    {
        public List<DocLine> Lines = new List<DocLine>();
        private int _groups;
        private int _detail;
        private int _detailLines;

        /// <summary>新しい詳細の番号を返す(1 から)。</summary>
        public int NewGroup() { return ++_groups; }
        /// <summary>これ以降に足す行を、group の詳細にする。</summary>
        public void BeginDetail(int group) { _detail = group; _detailLines = 0; }
        /// <summary>詳細の終わり。詳細の行が 1 本もなければ false。</summary>
        public bool EndDetail() { _detail = 0; return _detailLines > 0; }
        internal int CurrentDetail { get { return _detail; } }
        internal void CountDetail() { _detailLines++; }

        public string ToPlainText()
        {
            var sb = new StringBuilder();
            foreach (DocLine l in Lines)
            {
                if (l.RuleAbove) sb.AppendLine(new string('-', 40));
                if (l.SpaceBefore) sb.AppendLine();
                sb.AppendLine(l.PlainText());
            }
            return sb.ToString();
        }
    }

    /// <summary>1 行を組み立てる小さな道具。</summary>
    public sealed class LineBuilder
    {
        private readonly Doc _doc;
        private readonly DocLine _line = new DocLine();

        public LineBuilder(Doc doc, int indent = 0)
        {
            _doc = doc;
            _line.Indent = indent;
        }

        public LineBuilder Anchor(string name) { _line.Anchor = name; return this; }

        /// <summary>行頭の ▸ 印。押すと group の詳細を開閉する。詳細がなければ、Renderer が空白に直す。</summary>
        public LineBuilder ToggleMark(int group)
        {
            _line.Runs.Add(new Run { Text = "▸ ", Role = Role.Dim, Toggle = group });
            return this;
        }

        public LineBuilder FixLink(string text, string file, int line, int col, string type, string lineText)
        {
            _line.Runs.Add(new Run { Text = text, Role = Role.Good, Bold = true, File = file, Line = line, Col = col, Fix = type, FixLine = lineText });
            return this;
        }

        public LineBuilder JumpLink(string text, string anchor)
        {
            _line.Runs.Add(new Run { Text = text, Role = Role.Link, Jump = anchor });
            return this;
        }

        public LineBuilder Bar(Role r) { _line.Bar = r; return this; }
        public LineBuilder Rule() { _line.RuleAbove = true; return this; }
        public LineBuilder Space() { _line.SpaceBefore = true; return this; }

        public LineBuilder Add(string text, Role role = Role.Normal, bool bold = false, bool italic = false)
        {
            if (string.IsNullOrEmpty(text)) return this;
            _line.Runs.Add(new Run { Text = text, Role = role, Bold = bold, Italic = italic });
            return this;
        }

        public LineBuilder Link(string text, string file, int line, int col, bool bold = false)
        {
            _line.Runs.Add(new Run { Text = text, Role = Role.Link, Bold = bold, File = file, Line = line, Col = col });
            return this;
        }

        public LineBuilder SearchLink(string text, string search)
        {
            _line.Runs.Add(new Run { Text = text, Role = Role.Link, Search = search });
            return this;
        }

        public LineBuilder UrlLink(string text, string url)
        {
            _line.Runs.Add(new Run { Text = text, Role = Role.Link, Url = url });
            return this;
        }

        /// <summary>C++ の型・シグネチャを、役割ごとの色で追加する。</summary>
        public LineBuilder Code(string pretty, bool boldFunc = true)
        {
            foreach (Run r in CodeColor.Tokenize(pretty, boldFunc)) _line.Runs.Add(r);
            return this;
        }

        /// <summary>メッセージを追加する。'...' の中の C++ らしい部分は、短くして色を付ける。</summary>
        public LineBuilder Message(string msg, Role baseRole = Role.Normal)
        {
            foreach (Run r in MessageFormat.Format(msg, baseRole)) _line.Runs.Add(r);
            return this;
        }

        public DocLine Done()
        {
            if (_doc.CurrentDetail > 0) { _line.DetailGroup = _doc.CurrentDetail; _doc.CountDetail(); }
            _doc.Lines.Add(_line);
            return _line;
        }
    }
}

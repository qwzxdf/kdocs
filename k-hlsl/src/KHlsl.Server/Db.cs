using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;

namespace KHlsl.Server
{
    /// <summary>組み込みの言語データ(hlsl.json)。組み込み関数・型・セマンティクスなど。</summary>
    internal sealed class Db
    {
        public sealed class Func { public string n; public List<string> s; public string d; public string m; }
        public sealed class TypeInfo { public string n; public string d; public string m; public List<string> g; public bool scalar; }
        public sealed class Sem { public string n; public string d; }
        public sealed class Attr { public string n; public string syntax; public string d; public string m; }
        public sealed class Const { public string g; public string n; public string d; }
        public sealed class Directive { public string n; public string syntax; public string d; }
        public sealed class Macro { public string n; public string d; }
        public sealed class Keyword { public string n; public string d; public string k; }
        public sealed class Special { public string n; public string d; public string m; }

        public List<Func> intrinsics;
        public Dictionary<string, List<Func>> methods;
        public List<TypeInfo> types;
        public List<Sem> semantics;
        public List<Attr> attributes;
        public List<Const> constants;
        public List<Directive> directives;
        public List<Macro> macros;
        public List<Keyword> keywords;
        public List<Special> special;

        [JsonIgnore] public Dictionary<string, Func> IntrinsicByName;
        [JsonIgnore] public Dictionary<string, TypeInfo> TypeByName;
        [JsonIgnore] public Dictionary<string, Sem> SemByName;
        [JsonIgnore] public Dictionary<string, Attr> AttrByName;
        [JsonIgnore] public Dictionary<string, Const> ConstByName;
        [JsonIgnore] public Dictionary<string, Macro> MacroByName;
        [JsonIgnore] public Dictionary<string, Keyword> KeywordByName;
        [JsonIgnore] public Dictionary<string, Special> SpecialByName;

        public static Db Load()
        {
            using (var s = typeof(Db).Assembly.GetManifestResourceStream("hlsl.json"))
            using (var r = new StreamReader(s, System.Text.Encoding.UTF8))
            {
                var db = JsonConvert.DeserializeObject<Db>(r.ReadToEnd());
                db.Index();
                return db;
            }
        }

        private void Index()
        {
            IntrinsicByName = intrinsics.GroupBy(x => x.n).ToDictionary(g => g.Key, g => g.First());
            TypeByName = types.GroupBy(x => x.n).ToDictionary(g => g.Key, g => g.First());
            SemByName = semantics.GroupBy(x => x.n.ToLowerInvariant()).ToDictionary(g => g.Key, g => g.First());
            AttrByName = attributes.GroupBy(x => x.n).ToDictionary(g => g.Key, g => g.First());
            ConstByName = constants.GroupBy(x => x.n).ToDictionary(g => g.Key, g => g.First());
            MacroByName = macros.GroupBy(x => x.n).ToDictionary(g => g.Key, g => g.First());
            KeywordByName = keywords.GroupBy(x => x.n).ToDictionary(g => g.Key, g => g.First());
            SpecialByName = special.GroupBy(x => x.n).ToDictionary(g => g.Key, g => g.First());
        }

        /// <summary>型名から、使えるメソッドを集める(重複は先勝ち)。</summary>
        public List<Func> MethodsOf(string typeName)
        {
            var result = new List<Func>();
            TypeInfo t;
            if (!TypeByName.TryGetValue(typeName, out t)) return result;
            var seen = new HashSet<string>();
            foreach (var g in t.g)
            {
                List<Func> list;
                if (!methods.TryGetValue(g, out list)) continue;
                foreach (var m in list)
                    if (seen.Add(m.n)) result.Add(m);
            }
            return result;
        }

        public IEnumerable<Func> AllMethods()
        {
            var seen = new HashSet<string>();
            foreach (var kv in methods)
                foreach (var m in kv.Value)
                    if (seen.Add(m.n)) yield return m;
        }

        public Func FindMethodAnywhere(string name)
        {
            foreach (var kv in methods)
                foreach (var m in kv.Value)
                    if (m.n == name) return m;
            return null;
        }
    }
}

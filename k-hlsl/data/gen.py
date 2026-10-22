# -*- coding: utf-8 -*-
"""K-HLSL のデータ生成。hlsl.json(言語サーバー用)と TextMate 文法を作る。"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d_intrinsics as I
import d_lang as L

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rows(raw):
    for line in raw.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        yield [p.strip() for p in line.split(' | ')]


def sigs(s):
    return [x.strip() for x in s.split(';;')]


# ---- 組み込み関数 ----
intr = []
for r in list(rows(I.RAW)) + list(rows(I.RAW_DX)):
    name, sg, doc, sm = r[0], r[1], r[2], r[3]
    if name == 'dx::HitObject':
        continue
    intr.append({'n': name, 's': sigs(sg), 'd': doc, 'm': sm})

# ---- メソッド(群ごとに同名の重複を統合) ----
groups = {}
for r in rows(L.METHODS):
    g, name, sg, doc, sm = r
    e = groups.setdefault(g, {}).setdefault(name, {'n': name, 's': [], 'd': doc, 'm': sm})
    e['s'] += sigs(sg)
hit = {}
for r in rows(L.HITOBJECT_METHODS):
    full, sg, doc, sm = r
    short = full.split('::')[-1]
    hit[short] = {'n': short, 's': sigs(sg), 'd': doc, 'm': sm}
groups['hitobject'] = hit
methods = {g: list(v.values()) for g, v in groups.items()}

# ---- 型 ----
types = []
for r in rows(L.RESOURCE_TYPES):
    name, doc, sm = r[0], r[1], r[2]
    grp = r[3].split(',') if len(r) > 3 and r[3] else []
    types.append({'n': name, 'd': doc, 'm': sm, 'g': grp})
for r in rows(L.DX_TYPES):
    types.append({'n': r[0], 'd': r[1], 'm': r[2], 'g': ['hitobject']})
types.append({'n': 'RayDesc', 'd': 'レイを表す構造体(Origin, TMin, Direction, TMax)。', 'm': '6.3', 'g': []})
types.append({'n': 'BuiltInTriangleIntersectionAttributes', 'd': '三角形の交差属性(barycentrics)。', 'm': '6.3', 'g': []})
for n in L.SCALAR_TYPES:
    types.append({'n': n, 'd': L.SCALAR_DOCS.get(n, ''), 'm': '1.0', 'g': [], 'scalar': True})

sem = [{'n': r[0], 'd': r[1]} for r in rows(L.SEMANTICS)]
attrs = []
for line in L.ATTRIBUTES.strip().split('\n'):
    p = [x.strip() for x in line.split(' | ')]
    attrs.append({'n': p[0], 'syntax': ' | '.join(p[1:-2]), 'd': p[-2], 'm': p[-1]})
consts = [{'g': r[0], 'n': r[1], 'd': r[2]} for r in rows(L.CONSTANTS)]
dirs = [{'n': r[0], 'syntax': r[1], 'd': r[2]} for r in rows(L.DIRECTIVES)]
macros = [{'n': r[0], 'd': r[1]} for r in rows(L.MACROS)]
kw = []
for k in L.KEYWORDS_CONTROL:
    kw.append({'n': k, 'd': L.KEYWORD_DOCS.get(k, ''), 'k': 'control'})
for k in L.KEYWORDS_STORAGE:
    kw.append({'n': k, 'd': L.KEYWORD_DOCS.get(k, ''), 'k': 'storage'})
for k in L.KEYWORDS_DECL:
    kw.append({'n': k, 'd': L.KEYWORD_DOCS.get(k, ''), 'k': 'decl'})
special = [{'n': k, 'd': v, 'm': '6.6'} for k, v in L.SPECIAL_OBJECTS.items()]

db = dict(intrinsics=intr, methods=methods, types=types, semantics=sem, attributes=attrs,
          constants=consts, directives=dirs, macros=macros, keywords=kw, special=special)
os.makedirs(os.path.join(ROOT, 'src', 'KHlsl.Server'), exist_ok=True)
with open(os.path.join(ROOT, 'src', 'KHlsl.Server', 'hlsl.json'), 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=1)


# ---- TextMate 文法 ----
def alt(names):
    names = sorted(set(names), key=lambda x: (-len(x), x))
    return '|'.join(re.escape(n) for n in names)


intr_names = [i['n'] for i in intr if '::' not in i['n']]
type_names = [t['n'] for t in types if not t.get('scalar') and '::' not in t['n']]
method_names = sorted({m['n'] for v in methods.values() for m in v})
sem_names = [s['n'] for s in sem if s['n'].startswith('SV_')]
legacy_sem = [s['n'] for s in sem if not s['n'].startswith('SV_')]
attr_names = [a['n'] for a in attrs if not a['n'].startswith('vk::')]
const_names = [c['n'] for c in consts if c['g'] != 'lang']
macro_names = [m['n'] for m in macros]
scalar_alt = alt(['bool', 'int', 'uint', 'dword', 'half', 'float', 'double', 'min16float', 'min10float',
                  'min16int', 'min12int', 'min16uint', 'int16_t', 'uint16_t', 'float16_t', 'int32_t',
                  'uint32_t', 'float32_t', 'int64_t', 'uint64_t', 'float64_t'])
decl_words = ('struct', 'class', 'interface', 'cbuffer', 'tbuffer', 'namespace', 'typedef', 'enum')

CAP = {"1": {"name": "punctuation.separator.colon.khlsl"}}
G = {
    "name": "K-HLSL", "scopeName": "source.khlsl",
    "fileTypes": ["hlsl", "hlsli", "fx", "fxh", "vsh", "psh", "gsh", "hsh", "dsh", "csh", "msh", "ash",
                  "usf", "ush", "compute", "cginc"],
    "patterns": [{"include": "#all"}],
    "repository": {
        "all": {"patterns": [{"include": "#" + n} for n in (
            "comments", "preprocessor", "strings", "attributes", "semantics", "numbers", "declarations",
            "keywords", "types", "constants", "special", "methods", "functions", "namespaces", "operators")]},
        "comments": {"patterns": [
            {"name": "comment.block.documentation.khlsl", "begin": "/\\*\\*(?!/)", "end": "\\*/"},
            {"name": "comment.block.khlsl", "begin": "/\\*", "end": "\\*/"},
            {"name": "comment.line.double-slash.khlsl", "match": "//.*$"}]},
        "preprocessor": {"patterns": [
            {"match": "^\\s*(#)\\s*(include)\\s+(<[^>\\n]*>|\"[^\"\\n]*\")",
             "captures": {"1": {"name": "keyword.control.directive.khlsl"},
                          "2": {"name": "keyword.control.directive.include.khlsl"},
                          "3": {"name": "string.quoted.other.lt-gt.include.khlsl"}}},
            {"match": "^\\s*(#)\\s*(define|undef)\\s+([A-Za-z_]\\w*)",
             "captures": {"1": {"name": "keyword.control.directive.khlsl"},
                          "2": {"name": "keyword.control.directive.define.khlsl"},
                          "3": {"name": "entity.name.function.preprocessor.khlsl"}}},
            {"match": "^\\s*(#)\\s*(pragma)\\b(?:\\s+(\\w+))?",
             "captures": {"1": {"name": "keyword.control.directive.khlsl"},
                          "2": {"name": "keyword.control.directive.pragma.khlsl"},
                          "3": {"name": "entity.other.attribute-name.pragma.khlsl"}}},
            {"match": "^\\s*(#)\\s*(ifdef|ifndef|if|elif|else|endif|error|warning|line)\\b",
             "captures": {"1": {"name": "keyword.control.directive.khlsl"},
                          "2": {"name": "keyword.control.directive.conditional.khlsl"}}},
            {"match": "\\bdefined\\b", "name": "keyword.control.directive.defined.khlsl"},
            {"match": "\\b(?:" + alt(macro_names) + ")\\b", "name": "support.constant.predefined-macro.khlsl"}]},
        "strings": {"patterns": [
            {"name": "string.quoted.double.khlsl", "begin": "\"", "end": "\"",
             "patterns": [{"match": "\\\\.", "name": "constant.character.escape.khlsl"}]},
            {"name": "string.quoted.single.khlsl", "begin": "'", "end": "'",
             "patterns": [{"match": "\\\\.", "name": "constant.character.escape.khlsl"}]}]},
        "numbers": {"patterns": [
            {"match": "\\b0[xX][0-9a-fA-F]+[uUlL]{0,3}\\b", "name": "constant.numeric.hex.khlsl"},
            {"match": "\\b0[bB][01]+[uUlL]{0,3}\\b", "name": "constant.numeric.binary.khlsl"},
            {"match": "(?<![\\w.])(?:\\d+\\.\\d*|\\.\\d+|\\d+)(?:[eE][+-]?\\d+)?(?:[fFhHlL]|[uU][lL]{0,2})?(?![\\w.])",
             "name": "constant.numeric.decimal.khlsl"}]},
        "attributes": {"patterns": [
            {"match": "(\\[\\[)\\s*(vk::\\w+)",
             "captures": {"1": {"name": "punctuation.definition.attribute.khlsl"},
                          "2": {"name": "entity.other.attribute-name.khlsl"}}},
            {"match": "(?<=\\[)\\s*(" + alt(attr_names) + ")\\b",
             "captures": {"1": {"name": "entity.other.attribute-name.khlsl"}}}]},
        "semantics": {"patterns": [
            {"match": "(?i)(:)\\s*(SV_(?:" + alt([s[3:] for s in sem_names]) + ")\\d*)\\b",
             "captures": {**CAP, "2": {"name": "support.constant.semantic.khlsl"}}},
            {"match": "(?i)(:)\\s*(" + alt(legacy_sem) + ")\\d*\\b(?=\\s*(?:[,;)=:{]|$))",
             "captures": {**CAP, "2": {"name": "support.constant.semantic.khlsl"}}},
            {"match": "(:)\\s*(register|packoffset)\\b",
             "captures": {**CAP, "2": {"name": "storage.modifier.khlsl"}}},
            {"match": "(:)\\s*(read|write)\\s*(?=\\()",
             "captures": {**CAP, "2": {"name": "storage.modifier.paq.khlsl"}}},
            {"match": "\\b(anyhit|closesthit|miss|caller)\\b(?=\\s*[,)])",
             "name": "support.constant.payload-stage.khlsl"}]},
        "declarations": {"patterns": [
            {"match": "\\b(struct|class|interface|enum(?:\\s+class)?|cbuffer|tbuffer|namespace|technique\\d*|pass)\\s+([A-Za-z_]\\w*)",
             "captures": {"1": {"name": "storage.type.struct.khlsl"}, "2": {"name": "entity.name.type.khlsl"}}},
            {"match": "\\btypedef\\b", "name": "storage.type.typedef.khlsl"}]},
        "keywords": {"patterns": [
            {"match": "\\b(?:" + alt(L.KEYWORDS_CONTROL) + ")\\b", "name": "keyword.control.khlsl"},
            {"match": "\\b(?:" + alt(L.KEYWORDS_STORAGE) + ")\\b", "name": "storage.modifier.khlsl"},
            {"match": "\\b(?:" + alt([k for k in L.KEYWORDS_DECL if k not in decl_words]) + ")\\b",
             "name": "keyword.other.khlsl"}]},
        "types": {"patterns": [
            {"match": "\\b(?:" + scalar_alt + ")(?:[1-4](?:x[1-4])?)?\\b", "name": "storage.type.primitive.khlsl"},
            {"match": "\\b(?:vector|matrix|void|string|sampler(?:1D|2D|3D|CUBE|_state)?|texture|Texture)\\b",
             "name": "storage.type.primitive.khlsl"},
            {"match": "\\b(?:" + alt(type_names) + ")\\b", "name": "support.type.resource.khlsl"},
            {"match": "\\bdx::HitObject\\b", "name": "support.type.resource.khlsl"}]},
        "constants": {"patterns": [
            {"match": "\\b(?:true|false)\\b", "name": "constant.language.khlsl"},
            {"match": "\\b(?:" + alt(const_names) + ")\\b", "name": "support.constant.enum.khlsl"}]},
        "special": {"patterns": [
            {"match": "\\b(?:ResourceDescriptorHeap|SamplerDescriptorHeap)\\b",
             "name": "support.variable.descriptor-heap.khlsl"},
            {"match": "\\bthis\\b", "name": "variable.language.this.khlsl"}]},
        "methods": {"patterns": [
            {"match": "(dx::)(HitObject)(::)(\\w+)",
             "captures": {"1": {"name": "entity.name.namespace.khlsl"}, "2": {"name": "support.type.resource.khlsl"},
                          "3": {"name": "punctuation.accessor.khlsl"}, "4": {"name": "support.function.method.khlsl"}}},
            {"match": "(\\.)\\s*(" + alt(method_names) + ")\\b(?=\\s*(?:<[^>]*>\\s*)?\\()",
             "captures": {"1": {"name": "punctuation.accessor.khlsl"}, "2": {"name": "support.function.method.khlsl"}}},
            {"match": "(\\.)\\s*(mips|sample)\\b(?=\\s*\\[)",
             "captures": {"1": {"name": "punctuation.accessor.khlsl"}, "2": {"name": "support.variable.property.khlsl"}}}]},
        "functions": {"patterns": [
            {"match": "\\bdx::MaybeReorderThread\\b", "name": "support.function.intrinsic.khlsl"},
            {"match": "\\b(?:" + alt(intr_names) + ")\\b(?=\\s*(?:<[^>]*>\\s*)?\\()",
             "name": "support.function.intrinsic.khlsl"},
            {"match": "\\b[A-Za-z_]\\w*(?=\\s*\\()", "name": "entity.name.function.khlsl"}]},
        "namespaces": {"patterns": [
            {"match": "\\b([A-Za-z_]\\w*)\\s*(::)",
             "captures": {"1": {"name": "entity.name.namespace.khlsl"}, "2": {"name": "punctuation.accessor.khlsl"}}}]},
        "operators": {"patterns": [
            {"match": "\\+\\+|--|&&|\\|\\||<<=?|>>=?|[-+*/%&|^<>=!]=|[-+*/%&|^~!<>?]",
             "name": "keyword.operator.khlsl"}]},
    },
}
gdir = os.path.join(ROOT, 'src', 'KHlsl.Vsix', 'Grammars')
os.makedirs(gdir, exist_ok=True)
with open(os.path.join(gdir, 'KHlsl.json'), 'w', encoding='utf-8') as f:
    json.dump(G, f, ensure_ascii=False, indent=1)
print('intrinsics', len(intr), 'methods', sum(len(v) for v in methods.values()), 'types', len(types),
      'semantics', len(sem), 'attributes', len(attrs), 'constants', len(consts))

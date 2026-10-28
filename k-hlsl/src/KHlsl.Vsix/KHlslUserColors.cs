using System.ComponentModel.Composition;
using System.Windows.Media;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Utilities;

namespace KHlsl.Vsix
{
    /// <summary>設定ページで色を決めた項目だけが、元の分類に重ねる分類。自動生成(tools/gen_colors の内容)。</summary>
    internal static class KHlslUserDefinitions
    {
        [Export] [Name("khlsl.user.comment")] internal static ClassificationTypeDefinition Comment;
        [Export] [Name("khlsl.user.string")] internal static ClassificationTypeDefinition String;
        [Export] [Name("khlsl.user.number")] internal static ClassificationTypeDefinition Number;
        [Export] [Name("khlsl.user.operator")] internal static ClassificationTypeDefinition Operator;
        [Export] [Name("khlsl.user.keyword")] internal static ClassificationTypeDefinition Keyword;
        [Export] [Name("khlsl.user.type")] internal static ClassificationTypeDefinition Type;
        [Export] [Name("khlsl.user.namespace")] internal static ClassificationTypeDefinition Namespace;
        [Export] [Name("khlsl.user.label")] internal static ClassificationTypeDefinition Label;
        [Export] [Name("khlsl.user.function")] internal static ClassificationTypeDefinition Function;
        [Export] [Name("khlsl.user.memberfunc")] internal static ClassificationTypeDefinition MemberFunc;
        [Export] [Name("khlsl.user.param")] internal static ClassificationTypeDefinition Param;
        [Export] [Name("khlsl.user.local")] internal static ClassificationTypeDefinition Local;
        [Export] [Name("khlsl.user.member")] internal static ClassificationTypeDefinition Member;
        [Export] [Name("khlsl.user.global")] internal static ClassificationTypeDefinition Global;
        [Export] [Name("khlsl.user.macro")] internal static ClassificationTypeDefinition Macro;
        [Export] [Name("khlsl.user.enumerator")] internal static ClassificationTypeDefinition Enumerator;
        [Export] [Name("khlsl.user.semantic")] internal static ClassificationTypeDefinition Semantic;
        [Export] [Name("khlsl.user.attribute")] internal static ClassificationTypeDefinition Attribute;
        [Export] [Name("khlsl.user.identifier")] internal static ClassificationTypeDefinition Identifier;
    }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.comment")]
    [Name("khlsl.user.comment.format")] [Order(After = Priority.High)]
    internal sealed class UserCommentFormat : ClassificationFormatDefinition { public UserCommentFormat() { DisplayName = "K-HLSL コメント(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.string")]
    [Name("khlsl.user.string.format")] [Order(After = Priority.High)]
    internal sealed class UserStringFormat : ClassificationFormatDefinition { public UserStringFormat() { DisplayName = "K-HLSL 文字列(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.number")]
    [Name("khlsl.user.number.format")] [Order(After = Priority.High)]
    internal sealed class UserNumberFormat : ClassificationFormatDefinition { public UserNumberFormat() { DisplayName = "K-HLSL 数値(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.operator")]
    [Name("khlsl.user.operator.format")] [Order(After = Priority.High)]
    internal sealed class UserOperatorFormat : ClassificationFormatDefinition { public UserOperatorFormat() { DisplayName = "K-HLSL 演算子(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.keyword")]
    [Name("khlsl.user.keyword.format")] [Order(After = Priority.High)]
    internal sealed class UserKeywordFormat : ClassificationFormatDefinition { public UserKeywordFormat() { DisplayName = "K-HLSL キーワード(float struct など)(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.type")]
    [Name("khlsl.user.type.format")] [Order(After = Priority.High)]
    internal sealed class UserTypeFormat : ClassificationFormatDefinition { public UserTypeFormat() { DisplayName = "K-HLSL 型(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.namespace")]
    [Name("khlsl.user.namespace.format")] [Order(After = Priority.High)]
    internal sealed class UserNamespaceFormat : ClassificationFormatDefinition { public UserNamespaceFormat() { DisplayName = "K-HLSL 名前空間(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.label")]
    [Name("khlsl.user.label.format")] [Order(After = Priority.High)]
    internal sealed class UserLabelFormat : ClassificationFormatDefinition { public UserLabelFormat() { DisplayName = "K-HLSL ラベル(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.function")]
    [Name("khlsl.user.function.format")] [Order(After = Priority.High)]
    internal sealed class UserFunctionFormat : ClassificationFormatDefinition { public UserFunctionFormat() { DisplayName = "K-HLSL 関数(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.memberfunc")]
    [Name("khlsl.user.memberfunc.format")] [Order(After = Priority.High)]
    internal sealed class UserMemberFuncFormat : ClassificationFormatDefinition { public UserMemberFuncFormat() { DisplayName = "K-HLSL メンバー関数(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.param")]
    [Name("khlsl.user.param.format")] [Order(After = Priority.High)]
    internal sealed class UserParamFormat : ClassificationFormatDefinition { public UserParamFormat() { DisplayName = "K-HLSL 引数(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.local")]
    [Name("khlsl.user.local.format")] [Order(After = Priority.High)]
    internal sealed class UserLocalFormat : ClassificationFormatDefinition { public UserLocalFormat() { DisplayName = "K-HLSL ローカル変数(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.member")]
    [Name("khlsl.user.member.format")] [Order(After = Priority.High)]
    internal sealed class UserMemberFormat : ClassificationFormatDefinition { public UserMemberFormat() { DisplayName = "K-HLSL メンバー変数(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.global")]
    [Name("khlsl.user.global.format")] [Order(After = Priority.High)]
    internal sealed class UserGlobalFormat : ClassificationFormatDefinition { public UserGlobalFormat() { DisplayName = "K-HLSL グローバル変数(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.macro")]
    [Name("khlsl.user.macro.format")] [Order(After = Priority.High)]
    internal sealed class UserMacroFormat : ClassificationFormatDefinition { public UserMacroFormat() { DisplayName = "K-HLSL マクロ(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.enumerator")]
    [Name("khlsl.user.enumerator.format")] [Order(After = Priority.High)]
    internal sealed class UserEnumeratorFormat : ClassificationFormatDefinition { public UserEnumeratorFormat() { DisplayName = "K-HLSL 列挙子(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.semantic")]
    [Name("khlsl.user.semantic.format")] [Order(After = Priority.High)]
    internal sealed class UserSemanticFormat : ClassificationFormatDefinition { public UserSemanticFormat() { DisplayName = "K-HLSL セマンティクス(SV_Position など)(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.attribute")]
    [Name("khlsl.user.attribute.format")] [Order(After = Priority.High)]
    internal sealed class UserAttributeFormat : ClassificationFormatDefinition { public UserAttributeFormat() { DisplayName = "K-HLSL 属性([numthreads] など)(設定ページ)"; } }

    [Export(typeof(EditorFormatDefinition))] [ClassificationType(ClassificationTypeNames = "khlsl.user.identifier")]
    [Name("khlsl.user.identifier.format")] [Order(After = Priority.High)]
    internal sealed class UserIdentifierFormat : ClassificationFormatDefinition { public UserIdentifierFormat() { DisplayName = "K-HLSL その他の識別子(設定ページ)"; } }

}

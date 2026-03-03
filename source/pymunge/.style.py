from pymunge.swbf.formatters.style import Style, OdfStyle, CfgStyle


style = {
    'indentSpace': 2,
    'keepEmptyLines': 1,
    'trailingCommentSpace': 2,
    'whitespace': Style.Whitespace.UseSpaces,

    'cfg': {
        'comment': CfgStyle.Comment.UseForwardSlash,
    },

    'odf': {
        'alignment': OdfStyle.Alignment.AlignOnEqualPerSection,
        'comment': OdfStyle.Comment.UseForwardSlash,
        'commentAlignment': OdfStyle.CommentAlignment.AlignTrailingCommentsPerSection,
        'separateSubsections': True
    }
}
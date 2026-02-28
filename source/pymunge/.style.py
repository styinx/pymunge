from pymunge.swbf.formatters.style import Style, OdfStyle
style = {
    'whitespace': Style.Whitespace.UseSpaces,

    'odf': {
        'alignment': OdfStyle.Alignment.AlignOnEqualPerSection,
        'comment': OdfStyle.Comment.UseForwardSlash,
        'separateSubsections': True
    }
}
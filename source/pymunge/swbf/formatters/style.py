class Style:
    class Alignment:
        AlignOnEqual = 'AlignOnEqual'
        AlignOnValue = 'AlignOnValue'

    class CommentAlignment:
        AlignTrailingComments = 'AlignTrailingComments'

    class Whitespace:
        UseSpaces = 'UseSpaces'
        UseTabs = 'UseTabs'

    ALIGNMENT = Alignment.AlignOnEqual


class CfgStyle:
    class Comment:
        UseForwardSlash = 'UseForwardSlash'
        UseDoubleDash = 'UseDoubleDash'

    COMMENT = Comment.UseForwardSlash


class OdfStyle:
    class Alignment(Style.Alignment):
        AlignOnEqual = 'AlignOnEqual'
        AlignOnValue = 'AlignOnValue'
        AlignOnEqualPerBlock = 'AlignOnEqualPerBlock'
        AlignOnValuePerBlock = 'AlignOnValuePerBlock'
        AlignOnEqualPerSection = 'AlignOnEqualPerSection'
        AlignOnValuePerSection = 'AlignOnValuePerSection'

    class Comment:
        UseForwardSlash = 'UseForwardSlash'
        UseBackSlash = 'UseBackSlash'

    class CommentAlignment(Style.CommentAlignment):
        AlignTrailingComments = 'AlignTrailingComments'
        AlignTrailingCommentsPerBlock = 'AlignTrailingCommentsPerBlock'
        AlignTrailingCommentsPerSection = 'AlignTrailingCommentsPerSection'

    SeparateSubsections: bool = True
    
    ALIGNMENT  = Alignment.AlignOnEqualPerSection
    COMMENT = Comment.UseForwardSlash
    COMMENT_ALIGNMENT = CommentAlignment.AlignTrailingCommentsPerBlock

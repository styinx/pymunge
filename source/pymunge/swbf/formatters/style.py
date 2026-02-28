class Style:
    class Alignment:
        AlignOnEqual = 'AlignOnEqual'
        AlignOnValue = 'AlignOnValue'
        StripEmpty = 'StripEmpty'

    class CommentAlignment:
        AlignTrailingComments = 'AlignTrailingComments'

    class Whitespace:
        UseSpaces = 'UseSpaces'
        UseTabs = 'UseTabs'

    ALIGNMENT = Alignment.AlignOnEqual


class OdfStyle:
    class Alignment(Style.Alignment):
        AlignOnEqualPerBlock = 'AlignOnEqualPerBlock'
        AlignOnValuePerBlock = 'AlignOnValuePerBlock'
        AlignOnEqualPerSection = 'AlignOnEqualPerSection'
        AlignOnValuePerSection = 'AlignOnValuePerSection'

    class Comment:
        UseForwardSlash = 'UseForwardSlash'
        UseBackSlash = 'UseBackSlash'

    class CommentAlignment(Style.CommentAlignment):
        AlignTrailingCommentsPerBlock = 'AlignTrailingCommentsPerBlock'
        AlignTrailingCommentsPerSections = 'AlignTrailingCommentsPerSections'

    SeparateSubsections: bool = True
    
    ALIGNMENT  = Alignment.AlignOnEqualPerSection
    COMMENT = Comment.UseForwardSlash
    COMMENT_ALIGNMENT = CommentAlignment.AlignTrailingCommentsPerBlock

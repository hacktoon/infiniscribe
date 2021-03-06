
class Node:
    def __init__(self):
        self.text = ""
        self.index = (0, 0)

    def __bool__(self):
        return True

    def __str__(self):
        first, last = self.index
        return self.text[first:last]

    def __repr__(self):
        template = "{}('{}')"
        id = self.id.upper()
        return template.format(id, self)

    def eval(self):
        return


class ContainerNode(Node):
    def __init__(self):
        super().__init__()
        self._subnodes = []

    def __len__(self):
        return len(self._subnodes)

    def __iter__(self):
        for node in self._subnodes:
            yield node

    def __getitem__(self, index):
        return self._subnodes[index]

    def add(self, *nodes):
        for node in nodes:
            self._subnodes.append(node)


# ABSTRACT STRUCTS =================================================

class KeyStructNode(ContainerNode):
    def __init__(self):
        super().__init__()
        self.key = Node()


# ROOT STRUCT =========================================================

class RootNode(ContainerNode):
    id = "root"


# OBJECT STRUCTS ======================================================

class ObjectNode(KeyStructNode):
    id = "object"

    def eval(self):
        return str(self)


# QUERY STRUCTS =================================================

class QueryNode(KeyStructNode):
    id = "query"


# STRUCT KEYS =================================================

class AnonymKeyNode(Node):
    id = "anonym-key"


class DefaultFormatKeyNode(Node):
    id = "default-format-key"


class DefaultDocKeyNode(Node):
    id = "default-doc-key"


# RELATION ========================================================

class RelationNode(Node):
    id = "relation"

    def __init__(self):
        super().__init__()
        self.path = PathNode()
        self.sign = None
        self.value = None


class EqualNode(RelationNode):
    id = "equal"


class DifferentNode(RelationNode):
    id = "different"


class GreaterThanNode(RelationNode):
    id = "greater_than"


class GreaterThanEqualNode(RelationNode):
    id = "greater_than_equal"


class LessThanNode(RelationNode):
    id = "less_than"


class LessThanEqualNode(RelationNode):
    id = "less_than_equal"


class InNode(RelationNode):
    id = "in"


class NotInNode(RelationNode):
    id = "not_in"


# REFERENCE ========================================================

class ReferenceNode(ContainerNode):
    id = "reference"


class SubReferenceNode(Node):
    id = "sub-reference"


# LIST ========================================================

class ListNode(ContainerNode):
    id = "list"


# KEYWORD ========================================================

class KeywordNode(Node):
    id = "keyword"

    def __init__(self):
        super().__init__()
        self.value = ""


class NameKeywordNode(KeywordNode):
    id = "name-keyword"


class ConceptKeywordNode(NameKeywordNode):
    id = "concept-keyword"


class TagKeywordNode(KeywordNode):
    id = "tag-keyword"


class LogKeywordNode(KeywordNode):
    id = "log-keyword"


class AliasKeywordNode(KeywordNode):
    id = "alias-keyword"


class CacheKeywordNode(KeywordNode):
    id = "cache-keyword"


class FormatKeywordNode(KeywordNode):
    id = "format-keyword"


class DocKeywordNode(KeywordNode):
    id = "doc-keyword"


# RANGE ========================================================

class RangeNode(Node):
    id = "range"

    def __init__(self):
        super().__init__()
        self.start = None
        self.end = None


# LITERAL ========================================================

class LiteralNode(Node):
    id = "literal"

    def __init__(self):
        super().__init__()
        self.value = None

    def eval(self, _):
        return self.value


class IntNode(LiteralNode):
    id = "int"


class FloatNode(LiteralNode):
    id = "float"


class BooleanNode(LiteralNode):
    id = "boolean"


class StringNode(LiteralNode):
    id = "string"


class TemplateStringNode(LiteralNode):
    id = "template-string"


# PATH ========================================================

class PathNode(ContainerNode):
    id = "path"


class ChildPathNode(Node):
    id = "child-path"


class MetaPathNode(Node):
    id = "meta-path"


# WILDCARD ========================================================

class WildcardNode(Node):
    id = "wildcard"

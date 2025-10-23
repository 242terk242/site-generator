class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children if children is not None else []
        self.props = props if props is not None else {}

    def props_to_html(self):
        if not self.props:
            return ""
        pairs = [f'{k}="{v}"' for k, v in self.props.items()]
        return " " + " ".join(pairs)

    def to_html(self):
        raise NotImplementedError("to_html must be implemented by subclasses")


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        # no children allowed; tag and value required (tag may be None)
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if self.tag is None:
            return str(self.value)
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
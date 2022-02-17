from io import StringIO

from django.utils.encoding import force_str
from django.utils.xmlutils import SimplerXMLGenerator
from rest_framework_xml.renderers import XMLRenderer


class NexusRenderer(XMLRenderer):
    item_tag_name = "outcode"
    root_tag_name = "outcodes"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ""

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, data.get("root_attrs", {}))

        self._to_xml(xml, data["items"])

        xml.endElement(self.root_tag_name)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement(self.item_tag_name, item["attrs"])
                self._to_xml(xml, item["content"])
                xml.endElement(self.item_tag_name)

        elif isinstance(data, dict):
            for key, value in data:
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(force_str(data))


class OutcodeRenderer(NexusRenderer):
    root_tag_name = "outcode"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ""

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()

        xml.addQuickElement(self.root_tag_name, data["content"], data["attr"])

        xml.endDocument()
        return stream.getvalue()

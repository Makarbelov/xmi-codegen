"""Разбор XMI-файла (класс XmiParser из ЛР№2).

Из файла извлекаются UML-классы: имя, атрибуты, операции (с параметрами).
Результат - обычный список словарей, который дальше получает CodeGenerator.
"""
import xml.etree.ElementTree as ET
from typing import Any

from app.exceptions import XmiParseError

# Соответствие примитивных типов UML и Python
PRIMITIVES = {
    "String": "str",
    "Integer": "int",
    "int": "int",
    "UnlimitedNatural": "int",
    "Boolean": "bool",
    "Real": "float",
    "Double": "float",
    "Float": "float",
}


def _local(tag: str) -> str:
    """'{namespace}Class' -> 'Class'."""
    return tag.rsplit("}", 1)[-1]


def _xmi_attr(el: ET.Element, name: str) -> str | None:
    """Атрибут с пространством имён xmi (xmi:type, xmi:id)."""
    for key, value in el.attrib.items():
        if "}" in key and _local(key) == name:
            return value
    return None


def _python_type(name: str) -> str:
    return PRIMITIVES.get(name, name)


class XmiParser:
    def parse(self, xmi_path: str) -> list[dict[str, Any]]:
        """Читает XMI-файл и возвращает список классов."""
        try:
            root = ET.parse(xmi_path).getroot()
        except (ET.ParseError, OSError) as exc:
            raise XmiParseError(f"Не удалось прочитать XMI-файл: {exc}") from exc

        names = {
            xmi_id: el.get("name", "")
            for el in root.iter()
            if (xmi_id := _xmi_attr(el, "id")) is not None
        }

        classes: list[dict[str, Any]] = []
        for el in root.iter():
            kind = _xmi_attr(el, "type") or ""
            if _local(el.tag) == "packagedElement" and kind.endswith("Class") and el.get("name"):
                classes.append(self._read_class(el, names))

        if not classes:
            raise XmiParseError("В XMI-файле не найдено ни одного UML-класса")
        return classes

    def _type_of(self, el: ET.Element, names: dict[str, str]) -> str:
        ref = el.get("type")
        if ref:
            return _python_type(names.get(ref, ref))
        for child in el:
            if _local(child.tag) == "type":
                href = child.get("href", "")
                if "#" in href:
                    return _python_type(href.rsplit("#", 1)[1])
                idref = child.get("idref") or _xmi_attr(child, "idref")
                if idref:
                    return _python_type(names.get(idref, idref))
        return "object"

    def _read_class(self, el: ET.Element, names: dict[str, str]) -> dict[str, Any]:
        attributes: list[dict[str, str]] = []
        methods: list[dict[str, Any]] = []
        for child in el:
            tag = _local(child.tag)
            if tag == "ownedAttribute" and child.get("name"):
                attributes.append({"name": child.get("name", ""), "type": self._type_of(child, names)})
            elif tag == "ownedOperation" and child.get("name"):
                params: list[dict[str, str]] = []
                return_type = "None"
                for param in child:
                    if _local(param.tag) != "ownedParameter":
                        continue
                    if param.get("direction") == "return":
                        return_type = self._type_of(param, names)
                    else:
                        params.append({"name": param.get("name", "arg"), "type": self._type_of(param, names)})
                methods.append({"name": child.get("name", ""), "params": params, "return_type": return_type})
        return {"name": el.get("name", ""), "attributes": attributes, "methods": methods}

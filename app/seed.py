"""Готовый набор шаблонов и профилей, который создаётся при первом запуске."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Profile, Template

_METHOD = """\
{% for m in cls.methods %}

{{ indent }}def {{ m.name }}(self{% for p in m.params %}, {{ p.name }}: {{ p.type }}{% endfor %}) -> {{ m.return_type }}:
{{ indent }}{{ indent }}raise NotImplementedError
{% endfor %}
"""

SIMPLE = """\
{% for cls in classes %}
class {{ cls.name }}:
{{ indent }}def __init__(self{% for a in cls.attributes %}, {{ a.name }}: {{ a.type }}{% endfor %}) -> None:
{% for a in cls.attributes %}
{{ indent }}{{ indent }}self.{{ a.name }} = {{ a.name }}
{% else %}
{{ indent }}{{ indent }}pass
{% endfor %}
""" + _METHOD + """

{% endfor %}
"""

DATACLASS = """\
from dataclasses import dataclass


{% for cls in classes %}
@dataclass
class {{ cls.name }}:
{% for a in cls.attributes %}
{{ indent }}{{ a.name }}: {{ a.type }}
{% endfor %}
""" + _METHOD + """
{% if not cls.attributes and not cls.methods %}
{{ indent }}pass
{% endif %}


{% endfor %}
"""

PROPERTIES = """\
{% for cls in classes %}
class {{ cls.name }}:
{{ indent }}def __init__(self{% for a in cls.attributes %}, {{ a.name }}: {{ a.type }}{% endfor %}) -> None:
{% for a in cls.attributes %}
{{ indent }}{{ indent }}self._{{ a.name }} = {{ a.name }}
{% else %}
{{ indent }}{{ indent }}pass
{% endfor %}
{% for a in cls.attributes %}

{{ indent }}@property
{{ indent }}def {{ a.name }}(self) -> {{ a.type }}:
{{ indent }}{{ indent }}return self._{{ a.name }}

{{ indent }}@{{ a.name }}.setter
{{ indent }}def {{ a.name }}(self, value: {{ a.type }}) -> None:
{{ indent }}{{ indent }}self._{{ a.name }} = value
{% endfor %}
""" + _METHOD + """

{% endfor %}
"""


def seed_defaults(db: Session) -> None:
    """Добавляет профили и шаблоны, если таблица профилей пуста."""
    if db.execute(select(func.count(Profile.id))).scalar_one() > 0:
        return
    pep8 = Profile(name="Python (PEP 8)", language="python", indent=4, naming="snake_case")
    pep8.templates = [
        Template(name="Простой класс", content=SIMPLE),
        Template(name="Dataclass", content=DATACLASS),
        Template(name="Класс с геттерами и сеттерами", content=PROPERTIES),
    ]
    compact = Profile(name="Python (компактный)", language="python", indent=2, naming="camel_case")
    compact.templates = [Template(name="Простой класс (компактный)", content=SIMPLE)]
    db.add_all([pep8, compact])
    db.commit()

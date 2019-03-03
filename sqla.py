import warnings

import inflect
from sqlalchemy import (
    create_engine,
    exc as sa_exc
)
from sqlalchemy.ext.automap import automap_base, generate_relationship
from sqlalchemy.orm import configure_mappers, interfaces, Session

Base = automap_base()

engine = create_engine("postgresql://brett:@localhost/tropes")

_pluralizer = inflect.engine()


# noinspection PyUnusedLocal
def pluralize_collection(base, local_cls, referred_cls, constraint):
    return _pluralizer.plural(referred_cls.__name__).lower()


def _gen_relationship(base, direction, return_fn, attrname, local_cls, referred_cls, **kw):
    if direction not in (interfaces.MANYTOONE,):
        kw['lazy'] = 'dynamic'
    return generate_relationship(base, direction, return_fn, attrname, local_cls, referred_cls, **kw)


with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=sa_exc.SAWarning)
    Base.prepare(engine, reflect=True, name_for_collection_relationship=pluralize_collection,
                 generate_relationship=_gen_relationship)

configure_mappers()

session = Session(engine, autoflush=False)

classes = Base.classes

Media = classes.get('media')
Troperows = classes.get('troperows')
#mat view?

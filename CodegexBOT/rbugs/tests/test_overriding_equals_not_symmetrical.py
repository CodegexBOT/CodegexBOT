import pytest

from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse

params = [
    (False, 'EQ_COMPARING_CLASS_NAMES', '',
     '''if (auth.getClass().getName().equals(
                        "complication.auth.DefaultAthenticationHandler")) {''', 1, 2),
    (False, 'EQ_COMPARING_CLASS_NAMES', '',
     '''if (x.getClass().getName().equals(y.getClass().getName() )) {''', 1, 1),
    (False, 'EQ_COMPARING_CLASS_NAMES', '',
     '''if (Objects.equals( "complication.auth.DefaultAthenticationHandler",
                            auth.getClass().getName())){''', 1, 2),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=['EqualsClassNameDetector'])
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.filter_bugs('low')) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0

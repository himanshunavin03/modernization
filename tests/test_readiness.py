import pytest
from polaris_modernization.readiness import readiness


@pytest.mark.parametrize(("pipeline", "kwargs", "expected"), [
    ("SUCCESS", {}, "READY"),
    ("SUCCESS", {"explained_limitations": 1}, "READY_WITH_EXPLAINED_LIMITATIONS"),
    ("SUCCESS", {"analyzer_defects": 1}, "NOT_READY"),
    ("SUCCESS", {"unknowns": 1}, "NOT_READY"),
    ("SUCCESS", {"integrity_valid": False}, "NOT_READY"),
    ("FAILED", {}, "NOT_READY"),
])
def test_pipeline_execution_does_not_imply_knowledge_graph_readiness(pipeline, kwargs, expected):
    assert readiness(pipeline, **kwargs) == expected

from __future__ import annotations

import json
import unittest

from hgrid_skill.tools.workflow_builder import build_workflow_spec


class WorkflowBuilderTests(unittest.TestCase):
    def test_builds_source_assembly_sink_chain(self) -> None:
        spec = build_workflow_spec(
            name="CSV to Parquet",
            source_config={
                "type": "HfsSource",
                "path": "/data/input.csv",
                "format": "csv",
            },
            assemblies=[
                {"type": "Filter", "condition": "amount > 0"},
                {"type": "Transform", "fields": ["id", "amount"]},
            ],
            sink_config={
                "type": "ParquetSink",
                "path": "/data/output",
            },
            engine="Spark 2.x Dataset",
        )

        self.assertEqual(spec["schema"], "hgrid247.workflow.draft.v1")
        self.assertEqual(spec["status"], "draft_spec")
        self.assertEqual(
            [node["role"] for node in spec["nodes"]],
            ["source", "assembly", "assembly", "sink"],
        )
        self.assertEqual(
            spec["edges"],
            [
                {"from": "source_1", "to": "assembly_1"},
                {"from": "assembly_1", "to": "assembly_2"},
                {"from": "assembly_2", "to": "sink_1"},
            ],
        )
        self.assertEqual(spec["warnings"], [])

    def test_warns_for_unknown_components(self) -> None:
        spec = build_workflow_spec(
            name="Custom flow",
            source_config={"type": "UnknownSource"},
            assemblies=[{"type": "CustomAssembly"}],
            sink_config={"type": "UnknownSink"},
            engine="UnknownEngine",
        )

        warning_text = json.dumps(spec["warnings"])
        self.assertIn("UnknownEngine", warning_text)
        self.assertIn("UnknownSource", warning_text)
        self.assertIn("CustomAssembly", warning_text)
        self.assertIn("UnknownSink", warning_text)

    def test_requires_non_empty_source_and_sink(self) -> None:
        with self.assertRaises(ValueError):
            build_workflow_spec(
                name="Invalid",
                source_config={},
                assemblies=[],
                sink_config={"type": "HfsSink"},
            )


if __name__ == "__main__":
    unittest.main()

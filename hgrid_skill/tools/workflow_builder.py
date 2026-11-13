"""Workflow builder tools for HGrid247 agent mode."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_core.tools import tool


DEFAULT_OUTPUT_DIR = Path("generated_workflows")

SUPPORTED_ENGINES = {
    "MapReduce",
    "Spark 1.6 RDD",
    "Spark 2.x RDD",
    "Spark 2.x Dataset",
    "Beam 2.29.0 Batch",
    "Beam 2.29.0 Streaming",
    "Flink 1.12.x Batch",
    "Flink 1.12.x Streaming",
    "Tez 0.9.1",
    "PySpark",
}

COMMON_SOURCES = {
    "HfsSource",
    "XmlSource",
    "ParquetSource",
    "AvroSource",
    "HtmlSource",
    "RowDelimiterSource",
    "ORCSource",
    "HiveSource",
    "RdbmsSource",
    "JDBCSource",
    "MongoDBSource",
    "KafkaSource",
    "SocketSource",
    "WebCrawler",
    "DataFeeder",
}

COMMON_ASSEMBLIES = {
    "Pipe",
    "Transform",
    "Transform2",
    "GroupBy",
    "Aggregator",
    "GroupAndAggregate",
    "Combiner",
    "CoGroup",
    "ReferenceJoin",
    "Merge",
    "Filter",
    "Filter2",
    "ExpressionFilter",
    "Buffer",
    "BufferTrans",
    "UdfOperation",
    "UdfPythonOperation",
    "DuplicateCheck",
    "BloomFilter",
    "TopN",
    "GlobalTopN",
    "Profiling",
    "PipeSplitter",
    "Debug",
    "EventTime",
}

COMMON_SINKS = {
    "HfsSink",
    "XmlSink",
    "ParquetSink",
    "AvroSink",
    "ORCSink",
    "RowDelimiterSink",
    "RdbmsSink",
    "HiveSink",
    "HBaseSink",
    "MongoDBSink",
    "ElasticSearchSink",
    "SolrSink",
    "KafkaSink",
    "MQTTSink",
    "StdOutSink",
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return slug or "workflow"


def _node_type(config: dict[str, Any], fallback: str) -> str:
    for key in ("type", "operator", "component", "name"):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _clean_config(config: dict[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in config.items() if value not in (None, "")}


def build_workflow_spec(
    name: str,
    source_config: dict[str, Any],
    assemblies: list[dict[str, Any]],
    sink_config: dict[str, Any],
    engine: str = "Spark 2.x Dataset",
    description: str = "",
) -> dict[str, Any]:
    """Build a portable HGrid247 workflow draft specification."""
    if not name.strip():
        raise ValueError("Workflow name is required.")
    if not isinstance(source_config, dict) or not source_config:
        raise ValueError("source_config must be a non-empty object.")
    if not isinstance(assemblies, list):
        raise ValueError("assemblies must be a list.")
    if not isinstance(sink_config, dict) or not sink_config:
        raise ValueError("sink_config must be a non-empty object.")

    source_type = _node_type(source_config, "Source")
    sink_type = _node_type(sink_config, "Sink")

    nodes: list[dict[str, Any]] = [
        {
            "id": "source_1",
            "role": "source",
            "type": source_type,
            "config": _clean_config(source_config),
        }
    ]

    for index, assembly in enumerate(assemblies, 1):
        if not isinstance(assembly, dict) or not assembly:
            raise ValueError(f"Assembly at position {index} must be a non-empty object.")

        assembly_type = _node_type(assembly, f"Assembly{index}")
        nodes.append(
            {
                "id": f"assembly_{index}",
                "role": "assembly",
                "type": assembly_type,
                "config": _clean_config(assembly),
            }
        )

    nodes.append(
        {
            "id": "sink_1",
            "role": "sink",
            "type": sink_type,
            "config": _clean_config(sink_config),
        }
    )

    edges = [
        {"from": nodes[index]["id"], "to": nodes[index + 1]["id"]}
        for index in range(len(nodes) - 1)
    ]

    warnings: list[str] = []
    if engine not in SUPPORTED_ENGINES:
        warnings.append(f"Engine '{engine}' is not in the common supported engine list.")
    if source_type not in COMMON_SOURCES:
        warnings.append(f"Source '{source_type}' is not in the common source list.")
    if sink_type not in COMMON_SINKS:
        warnings.append(f"Sink '{sink_type}' is not in the common sink list.")

    for node in nodes:
        if node["role"] == "assembly" and node["type"] not in COMMON_ASSEMBLIES:
            warnings.append(f"Assembly '{node['type']}' is not in the common assembly list.")

    return {
        "schema": "hgrid247.workflow.draft.v1",
        "status": "draft_spec",
        "name": name.strip(),
        "description": description.strip(),
        "engine": engine,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "edges": edges,
        "warnings": warnings,
        "notes": [
            "This is a portable workflow draft for the AI assistant.",
            "Convert to native HGrid .csd only after confirming the official HGrid workflow schema.",
        ],
    }


@tool
def list_workflow_components() -> str:
    """List common HGrid247 workflow component names for workflow planning."""
    payload = {
        "engines": sorted(SUPPORTED_ENGINES),
        "sources": sorted(COMMON_SOURCES),
        "assemblies": sorted(COMMON_ASSEMBLIES),
        "sinks": sorted(COMMON_SINKS),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


@tool
def create_workflow(
    name: str,
    source_config: dict[str, Any],
    assemblies: list[dict[str, Any]],
    sink_config: dict[str, Any],
    engine: str = "Spark 2.x Dataset",
    description: str = "",
) -> str:
    """
    Create a draft HGrid247 workflow specification as JSON.

    Use this after collecting enough user requirements for Source, Assembly,
    Sink, and target engine. The output is not a native .csd file yet.
    """
    spec = build_workflow_spec(
        name=name,
        source_config=source_config,
        assemblies=assemblies,
        sink_config=sink_config,
        engine=engine,
        description=description,
    )

    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DEFAULT_OUTPUT_DIR / f"{_slugify(spec['name'])}.workflow.json"
    output_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")

    response = {
        "message": "Draft workflow spec created.",
        "path": str(output_path),
        "workflow": spec,
    }
    return json.dumps(response, indent=2, ensure_ascii=False)

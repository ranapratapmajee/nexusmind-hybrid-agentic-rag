import os
import sys
import uuid

# Ensure project root is in path
sys.path.append(os.path.abspath("."))

from src.core.orchestrator import Orchestrator


def test_single_query():
    print("\n🧪 TEST 1: Single Query Pipeline")

    orch = Orchestrator()
    session_id = str(uuid.uuid4())

    query = "What is machine learning in simple terms?"

    result = orch.run(query, session_id)

    assert "response" in result
    assert result["response"] is not None

    print("✔ Response:", result["response"])
    print("✔ Latency:", result["latency_ms"], "ms")


def test_rag_query():
    print("\n🧪 TEST 2: RAG Flow")

    orch = Orchestrator()
    session_id = str(uuid.uuid4())

    query = "Explain retrieval augmented generation"

    result = orch.run(query, session_id)

    assert "rag" in result
    print("✔ RAG Context:", result.get("rag"))


def test_tool_execution():
    print("\n🧪 TEST 3: Tool Execution")

    orch = Orchestrator()
    session_id = str(uuid.uuid4())

    query = "calculate 45 * 12"

    result = orch.run(query, session_id)

    assert "tool" in result
    print("✔ Tool Output:", result.get("tool"))


def test_memory_persistence():
    print("\n🧪 TEST 4: Memory Persistence")

    orch = Orchestrator()
    session_id = str(uuid.uuid4())

    orch.run("Hello, my name is Rana", session_id)
    orch.run("What is my name?", session_id)

    result = orch.run("Recall my name", session_id)

    print("✔ Memory Response:", result["response"])


def test_full_pipeline():
    print("\n🧪 TEST 5: Full Hybrid Pipeline")

    orch = Orchestrator()
    session_id = str(uuid.uuid4())

    query = "Explain AI, then calculate 23 * 7 and summarize RAG systems"

    result = orch.run(query, session_id)

    assert result["planner"] is not None
    assert result["route"] is not None
    assert result["context"] is not None
    assert result["response"] is not None

    print("✔ Planner:", result["planner"])
    print("✔ Route:", result["route"])
    print("✔ Response:", result["response"])
    print("✔ Latency:", result["latency_ms"], "ms")


if __name__ == "__main__":
    test_single_query()
    test_rag_query()
    test_tool_execution()
    test_memory_persistence()
    test_full_pipeline()

    print("\n🎉 ALL TESTS COMPLETED")

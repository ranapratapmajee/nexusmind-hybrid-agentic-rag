import os
import sys
import time
import uuid

# =========================================================
# PATH FIX (PROJECT ROOT)
# =========================================================
sys.path.append(os.path.abspath("."))

from src.core.orchestrator import Orchestrator


# =========================================================
# HELPER
# =========================================================
def new_orchestrator():
    return Orchestrator()


# =========================================================
# 1. SINGLE QUERY PIPELINE
# =========================================================
def test_single_query():
    print("\n🧪 TEST 1: Single Query Pipeline")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    query = "What is machine learning in simple terms?"

    result = orch.run(query, session_id)

    assert "response" in result
    assert result["response"] is not None
    assert "latency_ms" in result

    print("✔ Response:", result["response"])
    print("✔ Latency:", result["latency_ms"], "ms")


# =========================================================
# 2. RAG FLOW
# =========================================================
def test_rag_query():
    print("\n🧪 TEST 2: RAG Flow")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    query = "Explain retrieval augmented generation"

    result = orch.run(query, session_id)

    assert "rag" in result

    print("✔ RAG Context:", result.get("rag"))


# =========================================================
# 3. TOOL EXECUTION
# =========================================================
def test_tool_execution():
    print("\n🧪 TEST 3: Tool Execution")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    query = "calculate 45 * 12"

    result = orch.run(query, session_id)

    assert "tool" in result

    print("✔ Tool Output:", result.get("tool"))


# =========================================================
# 4. MEMORY PERSISTENCE
# =========================================================
def test_memory_persistence():
    print("\n🧪 TEST 4: Memory Persistence")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    orch.run("Hello, my name is Rana", session_id)
    orch.run("What is my name?", session_id)

    result = orch.run("Recall my name", session_id)

    assert result["response"] is not None

    print("✔ Memory Response:", result["response"])


# =========================================================
# 5. FULL PIPELINE TEST
# =========================================================
def test_full_pipeline():
    print("\n🧪 TEST 5: Full Hybrid Pipeline")

    orch = new_orchestrator()
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


# =========================================================
# 6. GOVERNANCE TEST
# =========================================================
def test_governance():
    print("\n🧪 TEST 6: Governance Layer")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    result = orch.run("What is AI?", session_id)

    assert "governance" in result
    assert "budget" in result["governance"]
    assert "latency" in result["governance"]

    print("✔ Governance:", result["governance"])


# =========================================================
# 7. EDGE CASE: EMPTY INPUT
# =========================================================
def test_empty_query():
    print("\n🧪 TEST 7: Empty Query")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    result = orch.run("", session_id)

    assert result is not None

    print("✔ Empty query handled safely")


# =========================================================
# 8. EDGE CASE: LARGE INPUT
# =========================================================
def test_large_input():
    print("\n🧪 TEST 8: Large Input")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    query = "Explain AI " * 300

    result = orch.run(query, session_id)

    assert result is not None

    print("✔ Large input handled safely")


# =========================================================
# 9. ROUTER VALIDATION
# =========================================================
def test_router():
    print("\n🧪 TEST 9: Router Validation")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    result = orch.run("solve 25 * 4", session_id)

    assert "route" in result
    assert "action" in result["route"]

    print("✔ Route:", result["route"])


# =========================================================
# 10. STREAMING TEST
# =========================================================
def test_streaming():
    print("\n🧪 TEST 10: Streaming")

    orch = new_orchestrator()
    session_id = str(uuid.uuid4())

    stream, trace = orch.run_stream("Explain machine learning", session_id)

    chunks = []

    for token in stream:
        chunks.append(token)

        # safety stop
        if len(chunks) > 30:
            break

    assert len(chunks) > 0

    print("✔ Stream chunks:", len(chunks))


# =========================================================
# MAIN EXECUTION (NON-PYTEST MODE)
# =========================================================
if __name__ == "__main__":
    start = time.time()

    test_single_query()
    test_rag_query()
    test_tool_execution()
    test_memory_persistence()
    test_full_pipeline()
    test_governance()
    test_empty_query()
    test_large_input()
    test_router()
    test_streaming()

    print("\n🎉 ALL TESTS COMPLETED")
    print("⏱ Total Time:", round(time.time() - start, 2), "seconds")

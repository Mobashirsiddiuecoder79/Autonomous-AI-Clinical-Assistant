import pytest
from database.connection import init_db
from agent.graph import run_agent_flow

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

def test_agent_graph_execution_fallback():
    session_id = "test-session-123"
    patient_id = 1
    prompt = "Calculate my BMI. Weight 75 kg, height 180 cm."
    
    # Run graph
    res = run_agent_flow(session_id, patient_id, prompt)
    
    assert res is not None
    assert "final_output" in res
    assert "plan" in res
    assert len(res["plan"]) > 0
    assert "Body Mass Index" in res["final_output"] or "automated clinical agent" in res["final_output"]

import pytest
import os
import shutil
from memory.vector_store import VectorMemoryManager

def test_vector_memory_store_retrieve():
    mgr = VectorMemoryManager()
    patient_id = 9999
    
    # Clean previous
    mgr.clear(patient_id)
    
    # Store
    mgr.store_document(patient_id, "Patient has history of asthma and uses Albuterol inhaler.", {"source": "test"})
    
    # Retrieve
    nodes = mgr.search_documents(patient_id, "asthma inhaler")
    assert len(nodes) > 0
    assert "Albuterol" in nodes[0]["text"]
    
    # Clear up
    mgr.clear(patient_id)
    assert not os.path.exists(mgr._get_index_path(patient_id))

# -*- coding: utf-8 -*-
import os
import sys
import json
import traceback
import time

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "agent_diagnose.json")

result = {"steps": []}

def log(step, success=True, data=None, error=None):
    entry = {"step": step, "success": success, "timestamp": time.time()}
    if data:
        entry["data"] = data
    if error:
        entry["error"] = error[:500] if isinstance(error, str) else str(error)[:500]
    result["steps"].append(entry)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

# Test 1: Check if openclaw.llm_service imports
try:
    log("test_1_start_openclaw", True)
    from openclaw.llm_service import LLMService
    log("test_1_openclaw", True)
except Exception as e:
    log("test_1_openclaw", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 2: Check multi_llm_service
try:
    log("test_2_start_multi_llm", True)
    from openclaw.multi_llm_service import generate_with_fallback
    log("test_2_multi_llm", True)
except Exception as e:
    log("test_2_multi_llm", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 3: Check specialists
try:
    log("test_3_start_specialists", True)
    from agents.specialists import ControlCenterSpecialistAgent
    log("test_3_specialists", True)
except Exception as e:
    log("test_3_specialists", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 4: Check agent_registration without auto-init
try:
    log("test_4_start_agent_reg", True)
    from agents.agent_registration import register_all_agents
    log("test_4_agent_reg", True)
except Exception as e:
    log("test_4_agent_reg", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Diagnose complete")

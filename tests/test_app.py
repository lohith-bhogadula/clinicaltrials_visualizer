import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import QueryRequest, build_visualization, matches_filters, plan_query, retryable_status
import asyncio

def study(nct, year, phase, drug="Drug A", sponsor="Acme"):
    return {"protocolSection":{"identificationModule":{"nctId":nct,"briefTitle":"A trial"},"statusModule":{"startDateStruct":{"date":f"{year}-01-02"}},"designModule":{"phases":[phase]},"sponsorCollaboratorsModule":{"leadSponsor":{"name":sponsor}},"armsInterventionsModule":{"interventions":[{"name":drug,"type":"DRUG"}]},"contactsLocationsModule":{"locations":[{"country":"United States"}]}}}

def test_time_series_has_citations():
    out=build_visualization([study("NCT1",2020,"PHASE2"),study("NCT2",2021,"PHASE3")],QueryRequest(query="trials per year"))
    assert out.type == "time_series" and out.data[0]["citations"][0]["nct_id"] == "NCT1"

def test_phase_distribution_and_year_filter():
    req=QueryRequest(query="phases",trial_phase=["PHASE2"],start_year=2020)
    assert matches_filters(study("NCT1",2020,"PHASE2"),req)
    assert not matches_filters(study("NCT2",2019,"PHASE2"),req)
    assert build_visualization([study("NCT1",2020,"PHASE2")],req).type == "bar_chart"

def test_network():
    out=build_visualization([study("NCT1",2020,"PHASE2")],QueryRequest(query="show sponsor drug network"))
    assert out.type == "network_graph" and len(out.data["edges"]) == 1

def test_dashboard_and_health_regression():
    root = Path(__file__).resolve().parents[1]
    page = (root / "static" / "index.html").read_text()
    js = (root / "static" / "app.js").read_text()
    assert 'TrialLens' in page and '/static/app.js' in page
    assert all(token in js for token in ('bar_chart', 'time_series', 'network_graph', 'citations'))

def test_ai_planner_safe_fallback_and_retry_policy(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    plan = asyncio.run(plan_query(QueryRequest(query="Tell me about melanoma research", condition="melanoma")))
    assert plan.source == "heuristic" and plan.intent == "intervention"
    assert retryable_status(429) and retryable_status(503) and not retryable_status(404)

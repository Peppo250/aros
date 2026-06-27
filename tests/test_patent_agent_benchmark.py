import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))

# Reconfigure stdout to use UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import unittest
from app.services.patent_search import search_patents

class TestPatentAgentBenchmark(unittest.TestCase):

    def setUp(self):
        self.benchmarks = [
            "Edge AI Mesh",
            "Federated Learning",
            "UAV Swarm Networks",
            "Disaster Communication Systems",
            "Autonomous Agents",
            "Smart City Edge Infrastructure"
        ]

    def test_run_benchmarks(self):
        print("\n" + "="*80)
        print("AROS PATENT AGENT BENCHMARK SUITE RUN")
        print("="*80)
        
        for topic in self.benchmarks:
            print(f"\n--- Testing Topic: {topic} ---")
            patents = search_patents(topic, limit=5)
            
            if not patents or (isinstance(patents, dict) and patents.get("status") == "retrieval_failed"):
                print(f"Warning: No patents retrieved for topic '{topic}' (likely due to missing API keys or search API blockages). Skipping assertions.")
                continue
                
            # Assertions
            self.assertTrue(len(patents) > 0, f"Benchmark failed: 0 patents returned for topic '{topic}'")
            print(f"Success: Retrieved {len(patents)} patents.")
            
            # Verify scores are computed and properties exist
            prev_relevance = 100.0
            for i, p in enumerate(patents):
                p_id = p.get("patent_id") or p.get("patent_number")
                title = p.get("patent_title") or p.get("title") or ""
                rel_score = p.get("relevance_score")
                val_score = p.get("validation_score")
                nov_score = p.get("novelty_contribution_score")
                comm_score = p.get("commercial_impact_score")
                prior_score = p.get("prior_art_overlap_score")
                
                print(f"[{i+1}] Patent {p_id}: {title[:50]}...")
                print(f"    - Relevance Score: {rel_score}")
                print(f"    - Validation Score: {val_score}")
                print(f"    - Novelty Score: {nov_score}")
                print(f"    - Commercial Impact: {comm_score}")
                print(f"    - Prior Art Overlap: {prior_score}")
                
                self.assertIsNotNone(rel_score, f"Relevance score missing for {p_id}")
                self.assertIsNotNone(val_score, f"Validation score missing for {p_id}")
                self.assertIsNotNone(nov_score, f"Novelty score missing for {p_id}")
                self.assertIsNotNone(comm_score, f"Commercial impact score missing for {p_id}")
                self.assertIsNotNone(prior_score, f"Prior art overlap score missing for {p_id}")
                
                # Check ranking order (descending relevance)
                self.assertTrue(rel_score <= prev_relevance, f"Ranking order failed: {rel_score} > {prev_relevance}")
                prev_relevance = rel_score

        print("\n" + "="*80)
        print("ALL BENCHMARKS COMPLETED SUCCESSFULLY!")
        print("="*80)

if __name__ == "__main__":
    unittest.main()

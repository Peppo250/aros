import os
import re
import time
from sqlalchemy.orm import Session
from neo4j import GraphDatabase

from app.models.paper import Paper
from app.models.github_repo import GithubRepo
from app.models.patent import Patent
from app.models.dataset import Dataset
from app.models.trend import TrendSignal

STOPWORDS = {
    "system",
    "systems",
    "method",
    "methods",
    "model",
    "models",
    "framework",
    "frameworks",
    "network",
    "networks",
    "application",
    "applications",
    "analysis",
    "study",
    "studies",
    "approach",
    "approaches",
    "data",
    "algorithm",
    "algorithms",
    "research",
    "paper",
    "dataset",
    "datasets",
    "using",
    "based",
    "towards",
    "novel",
    "efficient",
    "learning"
}

GRAMMAR_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", 
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", 
    "to", "was", "were", "will", "with", "or", "but", "not", "this", "our"
}

def get_keywords(text: str) -> set[str]:
    if not text:
        return set()
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    keywords = set(words) - GRAMMAR_STOPWORDS - STOPWORDS
    return keywords


class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        if self.uri and self.user and self.password:
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            except Exception as e:
                print(f"Failed to create Neo4j driver: {e}")

    def close(self):
        if self.driver:
            try:
                self.driver.close()
            except Exception as e:
                print(f"Failed to close Neo4j driver: {e}")

    def check_health(self):
        if not self.driver:
            return {"status": "unavailable", "error": "Neo4j driver is not initialized"}
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    def get_summary(self, project_id: str):
        node_counts = {
            "Paper": 0,
            "Repository": 0,
            "Patent": 0,
            "Dataset": 0,
            "Trend": 0
        }
        rel_count = 0

        if not self.driver:
            return {
                "node_counts": node_counts,
                "relationship_count": 0,
                "error": "Neo4j driver is not initialized"
            }

        try:
            with self.driver.session() as session:
                # Count nodes by label
                query_nodes = """
                MATCH (n) WHERE n.project_id = $project_id
                RETURN labels(n)[0] AS label, count(n) AS count
                """
                result_nodes = session.run(query_nodes, project_id=project_id)
                for record in result_nodes:
                    label = record["label"]
                    if label in node_counts:
                        node_counts[label] = record["count"]

                # Count relationships
                query_rels = """
                MATCH (a)-[r:RELATED_TO]->(b) WHERE a.project_id = $project_id
                RETURN count(r) AS count
                """
                result_rels = session.run(query_rels, project_id=project_id)
                record_rel = result_rels.single()
                if record_rel:
                    rel_count = record_rel["count"]
        except Exception as e:
            print(f"Failed to query Neo4j summary: {e}")
            return {
                "node_counts": node_counts,
                "relationship_count": 0,
                "error": f"Neo4j service unavailable: {e}"
            }

        return {
            "node_counts": node_counts,
            "relationship_count": rel_count
        }

    def get_graph_insights(self, project_id: str):
        insights = {
            "node_counts": {
                "Paper": 0,
                "Repository": 0,
                "Patent": 0,
                "Dataset": 0,
                "Trend": 0
            },
            "relationship_count": 0,
            "top_connected": [],
            "statistics": {
                "avg_overlap": 0.0,
                "max_overlap": 0
            },
            "most_connected_paper": None,
            "most_connected_repo": None,
            "most_connected_dataset": None
        }
        if not self.driver:
            return insights

        try:
            with self.driver.session() as session:
                # 1. Summary
                summary = self.get_summary(project_id)
                if "error" not in summary:
                    insights["node_counts"] = summary.get("node_counts", {})
                    insights["relationship_count"] = summary.get("relationship_count", 0)

                # 2. Top connected entities
                q_top = """
                MATCH (n) WHERE n.project_id = $project_id
                OPTIONAL MATCH (n)-[r:RELATED_TO]-()
                RETURN n.title AS title, labels(n)[0] AS type, count(r) AS degree
                ORDER BY degree DESC
                LIMIT 5
                """
                res_top = session.run(q_top, project_id=project_id)
                for record in res_top:
                    insights["top_connected"].append({
                        "title": record["title"] or "Unnamed",
                        "type": record["type"] or "Unknown",
                        "degree": record["degree"]
                    })

                # 3. Statistics (Average overlap, max overlap)
                q_stats = """
                MATCH (a)-[r:RELATED_TO]->(b) WHERE a.project_id = $project_id
                RETURN avg(r.overlap_count) AS avg_overlap, max(r.overlap_count) AS max_overlap
                """
                res_stats = session.run(q_stats, project_id=project_id)
                rec_stats = res_stats.single()
                if rec_stats:
                    insights["statistics"]["avg_overlap"] = rec_stats["avg_overlap"] or 0.0
                    insights["statistics"]["max_overlap"] = rec_stats["max_overlap"] or 0

                # 4. Centrality breakdowns (Paper, Repository, Dataset)
                q_m_paper = """
                MATCH (p:Paper) WHERE p.project_id = $project_id
                OPTIONAL MATCH (p)-[r:RELATED_TO]-()
                WITH p, count(r) AS degree
                ORDER BY degree DESC
                LIMIT 1
                RETURN p.title AS title
                """
                r_paper = session.run(q_m_paper, project_id=project_id).single()
                if r_paper and r_paper["title"]:
                    insights["most_connected_paper"] = r_paper["title"]

                q_m_repo = """
                MATCH (r:Repository) WHERE r.project_id = $project_id
                OPTIONAL MATCH (r)-[rel:RELATED_TO]-()
                WITH r, count(rel) AS degree
                ORDER BY degree DESC
                LIMIT 1
                RETURN r.title AS title
                """
                r_repo = session.run(q_m_repo, project_id=project_id).single()
                if r_repo and r_repo["title"]:
                    insights["most_connected_repo"] = r_repo["title"]

                q_m_dataset = """
                MATCH (d:Dataset) WHERE d.project_id = $project_id
                OPTIONAL MATCH (d)-[rel:RELATED_TO]-()
                WITH d, count(rel) AS degree
                ORDER BY degree DESC
                LIMIT 1
                RETURN d.title AS title
                """
                r_dataset = session.run(q_m_dataset, project_id=project_id).single()
                if r_dataset and r_dataset["title"]:
                    insights["most_connected_dataset"] = r_dataset["title"]

        except Exception as e:
            print(f"Failed to query Neo4j graph insights: {e}")
            insights["error"] = str(e)
        return insights



def build_graph(
    db: Session,
    project_id: str
):
    import time
    start_time = time.time()

    # Retrieve all AROS entities from PostgreSQL for the project
    papers = db.query(Paper).filter(Paper.project_id == project_id).all()
    repos = db.query(GithubRepo).filter(GithubRepo.project_id == project_id).all()
    patents = db.query(Patent).filter(Patent.project_id == project_id).all()
    datasets = db.query(Dataset).filter(Dataset.project_id == project_id).all()
    trends = db.query(TrendSignal).filter(TrendSignal.project_id == project_id).all()

    # Collect nodes details in memory
    # Format: (label, id, name_or_title, topic)
    nodes_list = []
    
    for p in papers:
        nodes_list.append(("Paper", str(p.id), p.title or "", getattr(p, "topic", None)))
    for r in repos:
        nodes_list.append(("Repository", str(r.id), r.repo_name or "", getattr(r, "topic", None)))
    for pat in patents:
        nodes_list.append(("Patent", str(pat.id), pat.title or "", getattr(pat, "topic", None)))
    for d in datasets:
        nodes_list.append(("Dataset", str(d.id), d.name or "", getattr(d, "topic", None)))
    for t in trends:
        nodes_list.append(("Trend", str(t.id), t.title or "", getattr(t, "topic", None)))

    # Connect to Neo4j
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    nodes_processed = 0
    relationships_processed = 0

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        print("Neo4j connected")

        with driver.session() as session:
            # Step 1: Merge nodes
            for label, node_id, name, topic in nodes_list:
                query = f"""
                MERGE (n:{label} {{id: $id}})
                SET n.title = $title,
                    n.name = $title,
                    n.project_id = $project_id,
                    n.topic = $topic
                """
                session.run(
                    query,
                    id=node_id,
                    title=name,
                    project_id=project_id,
                    topic=topic
                )
                nodes_processed += 1
            print("Nodes merged")

            # Step 2: Compute and Merge RELATIONSHIPS (case-insensitive keyword overlap)
            # Nested loop comparing unique pairs (lexicographically sorted IDs to prevent duplicate rels)
            for i in range(len(nodes_list)):
                for j in range(i + 1, len(nodes_list)):
                    label_a, id_a, name_a, _ = nodes_list[i]
                    label_b, id_b, name_b, _ = nodes_list[j]

                    keywords_a = get_keywords(name_a)
                    keywords_b = get_keywords(name_b)

                    overlap = keywords_a & keywords_b

                    # Only create relationship if overlap is at least MIN_OVERLAP = 3
                    if len(overlap) >= 3:
                        # Create directed RELATED_TO relationship in Neo4j
                        rel_query = f"""
                        MATCH (a:{label_a} {{id: $id_a}}), (b:{label_b} {{id: $id_b}})
                        MERGE (a)-[r:RELATED_TO]->(b)
                        SET r.overlap_count = $overlap_count,
                            r.overlap_keywords = $overlap_keywords
                        """
                        session.run(
                            rel_query,
                            id_a=id_a,
                            id_b=id_b,
                            overlap_count=len(overlap),
                            overlap_keywords=sorted(list(overlap))
                        )
                        relationships_processed += 1

                        # Debug log output for created relationships
                        print("RELATED:")
                        print(f"{label_a} -> {label_b}")
                        print("Overlap:")
                        print(sorted(list(overlap)))
            print("Relationships merged")

        driver.close()
    except Exception as e:
        print(f"Neo4j Graph Database execution failed: {e}")
        return {
            "papers": len(papers),
            "repositories": len(repos),
            "patents": len(patents),
            "datasets": len(datasets),
            "trends": len(trends),
            "nodes_processed": 0,
            "relationships_processed": 0,
            "error": f"Neo4j service unavailable: {e}"
        }

    duration = time.time() - start_time
    print("Graph build completed")
    print(f"Graph build duration: {duration:.4f} seconds")

    return {
        "papers": len(papers),
        "repositories": len(repos),
        "patents": len(patents),
        "datasets": len(datasets),
        "trends": len(trends),
        "nodes_processed": nodes_processed,
        "relationships_processed": relationships_processed
    }

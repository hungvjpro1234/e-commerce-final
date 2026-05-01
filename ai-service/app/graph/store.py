from collections.abc import Sequence
from contextlib import AbstractContextManager
from typing import Any

from neo4j import GraphDatabase

from app.config import get_settings


INTERACTION_TYPES = ("VIEW", "CLICK", "ADD_TO_CART", "BUY")


class Neo4jGraphStore(AbstractContextManager["Neo4jGraphStore"]):
    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        settings = get_settings()
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self.driver.close()

    def clear_graph(self) -> None:
        self._run("MATCH (n) DETACH DELETE n")

    def upsert_product(self, product: dict[str, Any]) -> None:
        self._run(
            """
            MERGE (p:Product {id: $id})
            SET p.name = $name,
                p.price = $price,
                p.stock = $stock,
                p.category_id = $category_id,
                p.category_name = $category_name,
                p.detail_type = $detail_type,
                p.detail_json = $detail_json
            """,
            product,
        )

    def upsert_user(self, user_id: int) -> None:
        self._run("MERGE (:User {id: $user_id})", {"user_id": user_id})

    def add_interaction(self, user_id: int, product_id: int, action: str, timestamp: str) -> None:
        relationship_type = action.upper()
        if relationship_type not in INTERACTION_TYPES:
            raise ValueError(f"Unsupported interaction type: {action}")

        self._run(
            f"""
            MATCH (u:User {{id: $user_id}})
            MATCH (p:Product {{id: $product_id}})
            MERGE (u)-[r:{relationship_type}]->(p)
            ON CREATE SET r.count = 1, r.first_timestamp = $timestamp, r.last_timestamp = $timestamp
            ON MATCH SET r.count = coalesce(r.count, 0) + 1, r.last_timestamp = $timestamp
            """,
            {"user_id": user_id, "product_id": product_id, "timestamp": timestamp},
        )

    def add_similarity(self, source_id: int, target_id: int, score: float, reason_summary: str) -> None:
        ordered_source, ordered_target = sorted([source_id, target_id])
        self._run(
            """
            MATCH (source:Product {id: $source_id})
            MATCH (target:Product {id: $target_id})
            MERGE (source)-[r:SIMILAR]->(target)
            SET r.score = $score, r.reason_summary = $reason_summary
            """,
            {
                "source_id": ordered_source,
                "target_id": ordered_target,
                "score": score,
                "reason_summary": reason_summary,
            },
        )

    def get_user_recommendations(self, user_id: int, limit: int) -> list[dict[str, Any]]:
        query = """
        MATCH (u:User {id: $user_id})-[r:VIEW|CLICK|ADD_TO_CART|BUY]->(source:Product)
        MATCH (source)-[s:SIMILAR]-(candidate:Product)
        WHERE candidate.id <> source.id
          AND NOT (u)-[:VIEW|CLICK|ADD_TO_CART|BUY]->(candidate)
        WITH candidate,
             sum(
               (CASE type(r)
                   WHEN 'VIEW' THEN 1.0
                   WHEN 'CLICK' THEN 1.5
                   WHEN 'ADD_TO_CART' THEN 2.5
                   WHEN 'BUY' THEN 3.5
                   ELSE 0.0
                END) * coalesce(s.score, 0.0)
             ) AS score,
             collect(DISTINCT source.name)[0..3] AS source_products,
             collect(DISTINCT s.reason_summary)[0..3] AS similarity_reasons
        RETURN candidate.id AS id,
               candidate.name AS name,
               candidate.price AS price,
               candidate.category_name AS category_name,
               candidate.detail_type AS detail_type,
               round(score, 4) AS score,
               source_products,
               similarity_reasons
        ORDER BY score DESC, candidate.id ASC
        LIMIT $limit
        """
        return self._run_and_collect(query, {"user_id": user_id, "limit": limit})

    def get_user_interacted_product_ids(self, user_id: int) -> list[int]:
        rows = self._run_and_collect(
            """
            MATCH (:User {id: $user_id})-[:VIEW|CLICK|ADD_TO_CART|BUY]->(p:Product)
            RETURN DISTINCT p.id AS id
            ORDER BY id ASC
            """,
            {"user_id": user_id},
        )
        return [int(row["id"]) for row in rows]

    def get_popular_products(self, limit: int, exclude_product_ids: Sequence[int] | None = None) -> list[dict[str, Any]]:
        query = """
        MATCH (:User)-[r:VIEW|CLICK|ADD_TO_CART|BUY]->(p:Product)
        WHERE size($exclude_product_ids) = 0 OR NOT p.id IN $exclude_product_ids
        WITH p, sum(coalesce(r.count, 1)) AS interaction_count
        RETURN p.id AS id,
               p.name AS name,
               p.price AS price,
               p.category_name AS category_name,
               p.detail_type AS detail_type,
               interaction_count
        ORDER BY interaction_count DESC, p.id ASC
        LIMIT $limit
        """
        return self._run_and_collect(
            query,
            {
                "exclude_product_ids": list(exclude_product_ids) if exclude_product_ids else [],
                "limit": limit,
            },
        )

    def get_graph_stats(self) -> dict[str, Any]:
        node_counts = self._run_and_collect(
            """
            CALL () {
              MATCH (u:User) RETURN count(u) AS user_count
            }
            CALL () {
              MATCH (p:Product) RETURN count(p) AS product_count
            }
            RETURN user_count, product_count
            """
        )[0]

        relationship_counts = self._run_and_collect(
            """
            MATCH ()-[r]->()
            RETURN type(r) AS relationship_type, count(r) AS count
            ORDER BY relationship_type ASC
            """
        )
        top_products = self._run_and_collect(
            """
            MATCH (p:Product)
            RETURN p.id AS id, p.name AS name, COUNT { (p)--() } AS degree
            ORDER BY degree DESC, p.id ASC
            LIMIT 10
            """
        )
        top_users = self._run_and_collect(
            """
            MATCH (u:User)
            RETURN u.id AS id, COUNT { (u)--() } AS degree
            ORDER BY degree DESC, u.id ASC
            LIMIT 10
            """
        )
        degree_distribution = self._run_and_collect(
            """
            MATCH (p:Product)
            RETURN p.id AS id, COUNT { (p)--() } AS degree
            ORDER BY id ASC
            """
        )

        return {
            "user_count": int(node_counts["user_count"]),
            "product_count": int(node_counts["product_count"]),
            "relationship_counts": {
                str(row["relationship_type"]): int(row["count"]) for row in relationship_counts
            },
            "top_products": top_products,
            "top_users": top_users,
            "degree_distribution": degree_distribution,
        }

    def get_snapshot_edges(self, limit: int = 30) -> list[dict[str, Any]]:
        return self._run_and_collect(
            """
            MATCH (u:User)-[r:VIEW|CLICK|ADD_TO_CART|BUY]->(p:Product)
            RETURN 'User:' + toString(u.id) AS source,
                   type(r) AS relationship_type,
                   'Product:' + toString(p.id) + ':' + p.name AS target
            ORDER BY u.id ASC, p.id ASC
            LIMIT $limit
            """,
            {"limit": limit},
        )

    def get_cypher_examples(self) -> list[dict[str, str]]:
        return [
            {
                "name": "Count nodes",
                "query": "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count",
            },
            {
                "name": "Top connected products",
                "query": "MATCH (p:Product) RETURN p.name, size((p)--()) AS degree ORDER BY degree DESC LIMIT 5",
            },
            {
                "name": "User recommendation traversal",
                "query": "MATCH (u:User {id: 1})-[r]->(p:Product)-[s:SIMILAR]-(candidate:Product) RETURN candidate.name, s.score",
            },
        ]

    def _run(self, query: str, parameters: dict[str, Any] | None = None) -> None:
        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run(query, parameters or {}).consume())

    def _run_and_collect(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self.driver.session() as session:
            result = session.execute_read(lambda tx: [record.data() for record in tx.run(query, parameters or {})])
        return result

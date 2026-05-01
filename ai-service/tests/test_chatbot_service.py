from app.schemas.chatbot import ChatbotProductSuggestion
from app.services.chatbot import build_chatbot_answer, classify_query_type, rerank_chatbot_products


class FakeRagItem:
    def __init__(self, *, id: int, name: str, price: float, category: str, detail_type: str, score: float, matched_terms: list[str]):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.detail_type = detail_type
        self.score = score
        self.matched_terms = matched_terms


def test_classify_query_type_detects_budget_and_gift():
    assert classify_query_type("toi can laptop gia re") == "budget"
    assert classify_query_type("mua qua tang") == "gift"


def test_rerank_chatbot_products_applies_personalization_boost():
    rag_results = [
        FakeRagItem(id=1, name="Laptop Pro 14", price=1299.0, category="Electronics", detail_type="electronics", score=0.5, matched_terms=["laptop"]),
        FakeRagItem(id=2, name="Clean Architecture", price=34.5, category="Books", detail_type="book", score=0.4, matched_terms=["book"]),
    ]

    ranked = rerank_chatbot_products(rag_results=rag_results, personalized_scores={2: 1.0})

    assert ranked[0]["id"] == 2
    assert "boosted by user recommendation history" in ranked[0]["reason"]


def test_build_chatbot_answer_is_grounded_in_top_product():
    answer = build_chatbot_answer(
        query="goi y sach hoc lap trinh",
        query_type="book",
        products=[
            ChatbotProductSuggestion(
                id=2,
                name="Clean Architecture",
                price=34.5,
                category="Books",
                detail_type="book",
                score=0.6,
                reason="Grounded RAG match.",
            )
        ],
    )

    assert "Clean Architecture" in answer

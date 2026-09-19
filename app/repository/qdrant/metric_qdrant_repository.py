from dataclasses import asdict

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import VectorParams,Distance

from app.conf.app_config import app_config
from app.entities.metric_info import MetricInfo


class MetricQdrantRepository:
    collection_name: str = 'data-agent-metric'

    def __init__(self,client : AsyncQdrantClient):
        self.client = client

    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=app_config.qdrant.embedding_size, distance=Distance.COSINE)
            )

    async def update(self, ids:list[str], embeddings:list[list[float]], payloads:list[MetricInfo]):
        # 构造PointStruct
        points =  [ PointStruct(id = id , vector=embedding,payload=asdict(payload)) for id,embedding,payload in zip(ids,embeddings,payloads)]
        await self.client.upsert(
            collection_name= self.collection_name,
            points=points
        )

    async def search(self, embedding: list[float], score_threshold: float = 0.6, limit: int = 5) -> list[
        MetricInfo]:
        result = await self.client.query_points(collection_name=self.collection_name,
                                                query=embedding,
                                                score_threshold=score_threshold,
                                                limit=limit)
        return [MetricInfo(**point.payload) for point in result.points]

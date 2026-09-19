from dataclasses import asdict

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.conf.app_config import app_config
from app.entities.column_info import ColumnInfo


class ColumnQdrantRepository:
    collection_name: str = 'data-agent-column'

    def __init__(self,client:AsyncQdrantClient):
        self.client = client

    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name = self.collection_name,
                vectors_config = VectorParams(size = app_config.qdrant.embedding_size, distance= Distance.COSINE)
            )

    async def update(self, ids:list[str], embeddings:list[list[float]], payloads:list[ColumnInfo],batch_size:int = 20):
        # 进入一个遍历，去构建PointStruct
        # 如果zip内的数据不等长 -> 短板效应
        # 承接一下这里的PointStruct列表
        points :list =[PointStruct(id = id,vector=embedding,payload=asdict(payload)) for id,embedding,payload in zip(ids,embeddings,payloads)]
        for i in range(0,len(points),batch_size):
            await self.client.upsert(
                collection_name = self.collection_name,
                points = points[i:i+batch_size]
            )

    async def search(self,embedding:list[float],score_threshold:float=0.6,limit:int =5)->list[ColumnInfo]:
        result= await self.client.query_points(collection_name=self.collection_name,
                                               query=embedding,
                                               score_threshold=score_threshold,
                                               limit=limit)
        return [ColumnInfo(**point.payload) for point in result.points]

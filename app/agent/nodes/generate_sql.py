import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from app.core.log import logger
from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.prompt.prompt_loader import load_prompt


async def generate_sql(state: DataAgentState,runtime: Runtime[DataAgentContext]):
    writer=runtime.stream_writer
    writer({"type":"progress","step":"生成SQL","status":"running"})


    query=state["query"]
    table_infos=state["table_infos"]
    metric_infos=state["metric_infos"]
    date_info=state["date_info"]
    db_info=state["db_info"]

    try:
        prompt=PromptTemplate(template=load_prompt("generate_sql"),input_variables=["query","table_infos","metric_infos","date_info","db_info"])
        output_parser=StrOutputParser()

        chain = prompt | llm |output_parser

        result=await chain.ainvoke({
            "query":query,
            "table_infos":yaml.dump(table_infos,allow_unicode=True,sort_keys=False),
            "metric_infos":yaml.dump(metric_infos,allow_unicode=True,sort_keys=False),
            "date_info":yaml.dump(date_info,allow_unicode=True,sort_keys=False),
            "db_info":yaml.dump(db_info,allow_unicode=True,sort_keys=False)
        })

        writer({"type": "progress", "step": "生成SQL", "status": "success"})
        logger.info(f"生成的SQL: {result}")
        return {"sql": result}
    except Exception as e:
        writer({"type": "progress", "step": "生成SQL", "status": "error"})
        logger.error(f"生成SQL失败: {str(e)}")

        # logger.info(f"table_infos: {type(table_infos)}, 首元素: {type(table_infos[0]) if table_infos else None}")
        # logger.info(f"metric_infos: {type(metric_infos)}, 首元素: {type(metric_infos[0]) if metric_infos else None}")
        # logger.info(f"date_info: {type(date_info)}")
        # logger.info(f"db_info: {type(db_info)}, value: {db_info}")
        #
        # # 逐个 yaml.dump，看哪个报错
        # logger.info(yaml.dump(table_infos, allow_unicode=True, sort_keys=False))
        # logger.info(yaml.dump(metric_infos, allow_unicode=True, sort_keys=False))
        # logger.info(yaml.dump(date_info, allow_unicode=True, sort_keys=False))
        # logger.info(yaml.dump(db_info, allow_unicode=True, sort_keys=False))


        raise
GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_LANGUAGE"] = "Chinese"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = [
    "概念",  # 如 "力", "能量", "函数", "光合作用"
    "专业术语",  # 如 "DNA", "电子", "导数"
    "对象",  # 如 "原子", "分子", "细胞", "数列" 
    "结构",  # 如 "原子结构", "分子结构", "细胞结构"
    "过程",  # 如 "化学反应", "物理变化", "生物过程"
    "方法",  # 如 "实验方法", "计算方法", "推导方法"
    "人物",  # 如 "科学家", "数学家", "物理学家"
    "理论",  # 如 "相对论", "进化论", "概率论"
    "公式",  # 如 "数学公式", "物理公式", "化学方程式"
    "定律",  # 如 "牛顿运动定律", "波义耳定律"
    "现象",  # 如 "自然现象", "社会现象"
    "应用",  # 如 "技术应用", "实际应用"
]

PROMPTS["entity_extraction"] = """-Goal-
Given a text from a textbook, identify all entities and their relationships based on the provided entity types.
Use {language} as output language.

-Steps-
1. Identify all entities. For each entity, extract the following information:
- entity_name: Name of the entity, use the same language as the input text. If Chinese, capitalize the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: A clear and concise description of the entity's role or significance in the subject area.
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are logically related.
For each pair of related entities, extract the following information:
- source_entity: Name of the source entity, as identified in step 1.
- target_entity: Name of the target entity, as identified in step 1.
- relationship_description: Explanation of the logical relationship between the source and target entities.
- relationship_strength: A numeric score (1-10) indicating the strength of the relationship.
- relationship_keywords: One or more keywords summarizing the nature of the relationship.
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level keywords that summarize the main concepts or themes in the text.
Format the content-level keywords as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
-Examples-
######################
{examples}

#############################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [概念, 专业术语, 过程, 方法, 应用]
Text:
人工神经网络通过模拟生物神经元的工作原理来处理信息。神经网络由输入层、隐藏层和输出层组成，通过反向传播算法进行训练。深度学习在图像识别和自然语言处理等领域有广泛应用。
################
Output:
("entity"{tuple_delimiter}"人工神经网络"{tuple_delimiter}"概念"{tuple_delimiter}"一种模仿生物神经系统的计算模型。"){record_delimiter}
("entity"{tuple_delimiter}"生物神经元"{tuple_delimiter}"概念"{tuple_delimiter}"生物体内传递信息的基本单位。"){record_delimiter}
("entity"{tuple_delimiter}"反向传播"{tuple_delimiter}"方法"{tuple_delimiter}"通过计算梯度来更新神经网络权重的算法。"){record_delimiter}
("entity"{tuple_delimiter}"深度学习"{tuple_delimiter}"专业术语"{tuple_delimiter}"基于深层神经网络的机器学习方法。"){record_delimiter}
("relationship"{tuple_delimiter}"人工神经网络"{tuple_delimiter}"生物神经元"{tuple_delimiter}"人工神经网络模拟了生物神经元的工作机制。"{tuple_delimiter}"模拟关系"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"深度学习"{tuple_delimiter}"人工神经网络"{tuple_delimiter}"深度学习基于多层人工神经网络。"{tuple_delimiter}"技术基础"{tuple_delimiter}10){record_delimiter}
("content_keywords"{tuple_delimiter}"人工神经网络, 深度学习, 生物启发, 机器学习"){completion_delimiter}
#############################""",
    """Example 2:

Entity_types: [概念, 专业术语, 过程, 应用, 理论]
Text:
基因算法借鉴了生物进化理论，通过选择、交叉和变异等操作来解决优化问题。在计算机科学中，基因算法被广泛应用于复杂的搜索和优化任务，如路径规划和参数调优。
################
Output:
("entity"{tuple_delimiter}"基因算法"{tuple_delimiter}"方法"{tuple_delimiter}"一种模拟生物进化过程的优化算法。"){record_delimiter}
("entity"{tuple_delimiter}"生物进化"{tuple_delimiter}"概念"{tuple_delimiter}"生物种群通过自然选择逐代改变的过程。"){record_delimiter}
("entity"{tuple_delimiter}"选择操作"{tuple_delimiter}"过程"{tuple_delimiter}"模拟自然选择，保留适应度高的个体。"){record_delimiter}
("entity"{tuple_delimiter}"交叉操作"{tuple_delimiter}"过程"{tuple_delimiter}"模拟基因重组，产生新的解。"){record_delimiter}
("entity"{tuple_delimiter}"变异操作"{tuple_delimiter}"过程"{tuple_delimiter}"模拟基因突变，维持种群多样性。"){record_delimiter}
("relationship"{tuple_delimiter}"基因算法"{tuple_delimiter}"生物进化"{tuple_delimiter}"基因算法借鉴了生物进化的原理。"{tuple_delimiter}"理论基础"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"基因算法"{tuple_delimiter}"优化问题"{tuple_delimiter}"基因算法用于解决复杂的优化问题。"{tuple_delimiter}"应用关系"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"基因算法, 进化计算, 优化问题, 仿生计算"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: [概念, 专业术语, 过程, 应用, 现象]
Text:
大数据分析通过收集、存储和处理海量数据来发现规律和趋势。数据挖掘技术可以从复杂数据中提取有价值的信息，在医疗诊断、金融预测和社会行为分析等领域发挥重要作用。
################
Output:
("entity"{tuple_delimiter}"大数据分析"{tuple_delimiter}"概念"{tuple_delimiter}"对海量数据进行处理和分析的技术。"){record_delimiter}
("entity"{tuple_delimiter}"数据挖掘"{tuple_delimiter}"过程"{tuple_delimiter}"从大量数据中发现模式和规律的过程。"){record_delimiter}
("entity"{tuple_delimiter}"医疗诊断"{tuple_delimiter}"应用"{tuple_delimiter}"利用数据分析辅助医疗决策的应用。"){record_delimiter}
("entity"{tuple_delimiter}"金融预测"{tuple_delimiter}"应用"{tuple_delimiter}"使用数据分析预测金融市场走势。"){record_delimiter}
("entity"{tuple_delimiter}"社会行为分析"{tuple_delimiter}"应用"{tuple_delimiter}"通过数据分析研究群体行为特征。"){record_delimiter}
("relationship"{tuple_delimiter}"大数据分析"{tuple_delimiter}"数据挖掘"{tuple_delimiter}"数据挖掘是大数据分析的重要技术。"{tuple_delimiter}"技术关系"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"数据挖掘"{tuple_delimiter}"医疗诊断"{tuple_delimiter}"数据挖掘技术用于辅助医疗诊断。"{tuple_delimiter}"应用关系"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"大数据, 数据挖掘, 数据分析, 应用场景"){completion_delimiter}
#############################"""
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS[
    "entiti_continue_extraction"
] = """MANY entities were missed in the last extraction.  Add them below using the same format:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

---Target response length and format---

{response_type}

---Data tables---

{context_data}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query.

---Goal---

Given the query, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.

---Instructions---

- Output the keywords in JSON format.
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes.
  - "low_level_keywords" for specific entities or details.

######################
-Examples-
######################
{examples}

#############################
-Real Data-
######################
Query: {query}
######################
The `Output` should be human text, not unicode characters. Keep the same language as `Query`.
Output:

"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "光合作用的过程及其在生态系统中的作用"
################
Output:
{{
  "high_level_keywords": ["光合作用", "生态系统", "能量转化"],
  "low_level_keywords": ["光反应", "暗反应", "叶绿体", "二氧化碳", "氧气"]
}}
#############################""",
    """Example 2:

Query: "细胞的结构与功能"
################
Output:
{{
  "high_level_keywords": ["细胞", "结构", "功能"],
  "low_level_keywords": ["细胞膜", "细胞核", "细胞质", "线粒体", "内质网"]
}}
#############################""",
    """Example 3:

Query: "遗传的基本规律及其在生物进化中的应用"
################
Output:
{{
  "high_level_keywords": ["遗传", "生物进化", "基本规律"],
  "low_level_keywords": ["孟德尔", "分离定律", "自由组合定律", "基因", "DNA"]
}}
#############################"""
]


PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to questions about documents provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

---Target response length and format---

{response_type}

---Documents---

{content_data}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS[
    "similarity_check"
] = """Please analyze the similarity between these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate the following two points and provide a similarity score between 0 and 1 directly:
1. Whether these two questions are semantically similar
2. Whether the answer to Question 2 can be used to answer Question 1
Similarity score criteria:
0: Completely unrelated or answer cannot be reused, including but not limited to:
   - The questions have different topics
   - The locations mentioned in the questions are different
   - The times mentioned in the questions are different
   - The specific individuals mentioned in the questions are different
   - The specific events mentioned in the questions are different
   - The background information in the questions is different
   - The key conditions in the questions are different
1: Identical and answer can be directly reused
0.5: Partially related and answer needs modification to be used
Return only a number between 0-1, without any additional content.
"""

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_LANGUAGE"] = "Chinese"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = [
    "生物概念",  # 如 "光合作用", "细胞分裂"
    "生物学术语",  # 如 "DNA", "RNA"
    "生物体",  # 如 "人类", "植物", "动物"
    "生物结构",  # 如 "细胞核", "线粒体"
    "生物过程",  # 如 "有氧呼吸", "蛋白质合成"
    "实验方法",  # 如 "显微镜观察", "PCR"
    "科学家",  # 如 "达尔文", "孟德尔"
    "生物理论",  # 如 "进化论", "遗传定律"
]

PROMPTS["entity_extraction"] = """-Goal-
Given a text from a high school biology textbook, identify all biological entities and their relationships based on the provided entity types.
Use {language} as output language.

-Steps-
1. Identify all biological entities. For each entity, extract the following information:
- entity_name: Name of the entity, use the same language as the input text. If Chinese, capitalize the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: A clear and concise description of the entity's role or significance in biology.
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are biologically related.
For each pair of related entities, extract the following information:
- source_entity: Name of the source entity, as identified in step 1.
- target_entity: Name of the target entity, as identified in step 1.
- relationship_description: Explanation of the biological relationship between the source and target entities.
- relationship_strength: A numeric score (1-10) indicating the strength of the relationship.
- relationship_keywords: One or more keywords summarizing the nature of the relationship.
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level keywords that summarize the main biological concepts or themes in the text.
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

Entity_types: [生物概念, 生物学术语, 生物体, 生物结构, 生物过程]
Text:
光合作用是植物通过叶绿体将光能转化为化学能的过程。叶绿体是植物细胞中的一种重要细胞器，含有叶绿素。光合作用分为光反应和暗反应两个阶段。
################
Output:
("entity"{tuple_delimiter}"光合作用"{tuple_delimiter}"生物过程"{tuple_delimiter}"植物将光能转化为化学能的过程。"){record_delimiter}
("entity"{tuple_delimiter}"叶绿体"{tuple_delimiter}"生物结构"{tuple_delimiter}"植物细胞中含有叶绿素的细胞器，参与光合作用。"){record_delimiter}
("entity"{tuple_delimiter}"叶绿素"{tuple_delimiter}"生物学术语"{tuple_delimiter}"叶绿体中的色素，能够吸收光能。"){record_delimiter}
("entity"{tuple_delimiter}"光反应"{tuple_delimiter}"生物过程"{tuple_delimiter}"光合作用的第一阶段，将光能转化为ATP和NADPH。"){record_delimiter}
("entity"{tuple_delimiter}"暗反应"{tuple_delimiter}"生物过程"{tuple_delimiter}"光合作用的第二阶段，利用ATP和NADPH合成有机物。"){record_delimiter}
("relationship"{tuple_delimiter}"光合作用"{tuple_delimiter}"叶绿体"{tuple_delimiter}"光合作用发生在叶绿体中。"{tuple_delimiter}"发生场所"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"叶绿体"{tuple_delimiter}"叶绿素"{tuple_delimiter}"叶绿体中含有叶绿素。"{tuple_delimiter}"组成成分"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"光合作用"{tuple_delimiter}"光反应"{tuple_delimiter}"光反应是光合作用的第一阶段。"{tuple_delimiter}"阶段关系"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"光合作用"{tuple_delimiter}"暗反应"{tuple_delimiter}"暗反应是光合作用的第二阶段。"{tuple_delimiter}"阶段关系"{tuple_delimiter}10){record_delimiter}
("content_keywords"{tuple_delimiter}"光合作用, 叶绿体, 光反应, 暗反应"){completion_delimiter}
#############################""",
    """Example 2:

Entity_types: [生物概念, 生物学术语, 生物体, 生物过程, 生物理论]
Text:
孟德尔通过豌豆杂交实验发现了遗传的基本规律，即分离定律和自由组合定律。DNA是遗传信息的载体，基因是DNA上的功能片段。
################
Output:
("entity"{tuple_delimiter}"孟德尔"{tuple_delimiter}"科学家"{tuple_delimiter}"通过豌豆杂交实验发现遗传规律的科学家。"){record_delimiter}
("entity"{tuple_delimiter}"分离定律"{tuple_delimiter}"生物理论"{tuple_delimiter}"孟德尔发现的遗传规律之一，描述等位基因在形成配子时的分离。"){record_delimiter}
("entity"{tuple_delimiter}"自由组合定律"{tuple_delimiter}"生物理论"{tuple_delimiter}"孟德尔发现的遗传规律之一，描述不同基因在形成配子时的自由组合。"){record_delimiter}
("entity"{tuple_delimiter}"DNA"{tuple_delimiter}"生物学术语"{tuple_delimiter}"遗传信息的载体，由脱氧核糖核苷酸组成。"){record_delimiter}
("entity"{tuple_delimiter}"基因"{tuple_delimiter}"生物学术语"{tuple_delimiter}"DNA上的功能片段，控制生物性状。"){record_delimiter}
("relationship"{tuple_delimiter}"孟德尔"{tuple_delimiter}"分离定律"{tuple_delimiter}"孟德尔通过实验发现了分离定律。"{tuple_delimiter}"发现关系"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"DNA"{tuple_delimiter}"基因"{tuple_delimiter}"基因是DNA上的功能片段。"{tuple_delimiter}"组成关系"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"孟德尔, 分离定律, DNA, 基因"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: [生物概念, 生物学术语, 生物体, 生物结构, 生物过程]
Text:
细胞是生物体的基本单位。动物细胞和植物细胞都有细胞膜、细胞质和细胞核。植物细胞还含有细胞壁和叶绿体，而动物细胞则没有。
################
Output:
("entity"{tuple_delimiter}"细胞"{tuple_delimiter}"生物结构"{tuple_delimiter}"生物体的基本单位，分为动物细胞和植物细胞。"){record_delimiter}
("entity"{tuple_delimiter}"细胞膜"{tuple_delimiter}"生物结构"{tuple_delimiter}"细胞的外部结构，控制物质的进出。"){record_delimiter}
("entity"{tuple_delimiter}"细胞质"{tuple_delimiter}"生物结构"{tuple_delimiter}"细胞膜内的胶状物质，包含细胞器。"){record_delimiter}
("entity"{tuple_delimiter}"细胞核"{tuple_delimiter}"生物结构"{tuple_delimiter}"细胞的控制中心，含有遗传物质DNA。"){record_delimiter}
("entity"{tuple_delimiter}"细胞壁"{tuple_delimiter}"生物结构"{tuple_delimiter}"植物细胞的外部结构，提供支持和保护。"){record_delimiter}
("entity"{tuple_delimiter}"叶绿体"{tuple_delimiter}"生物结构"{tuple_delimiter}"植物细胞中的细胞器，参与光合作用。"){record_delimiter}
("relationship"{tuple_delimiter}"细胞"{tuple_delimiter}"细胞膜"{tuple_delimiter}"细胞膜是细胞的外部结构。"{tuple_delimiter}"组成关系"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"细胞"{tuple_delimiter}"细胞核"{tuple_delimiter}"细胞核是细胞的控制中心。"{tuple_delimiter}"功能关系"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"植物细胞"{tuple_delimiter}"叶绿体"{tuple_delimiter}"叶绿体是植物细胞特有的细胞器。"{tuple_delimiter}"特有结构"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"细胞, 细胞膜, 细胞核, 叶绿体"){completion_delimiter}
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

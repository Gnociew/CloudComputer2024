# 云计算项目报告

## 一.项目背景

### 1.大语言模型在教育的使用

随着人工智能技术的快速发展，大语言模型在教育领域的应用潜力日益凸显。通过语言模型可以满足学生问答等场景的需求。

### 2.大规模个性化学习的愿景

数据科学与工程学院长期坚持推进大规模个性化学习的愿景。通过水杉在线学习平台、全民数字素养与技能培训基地等平台，通过数据赋能，推进个性化教育。本平台正顺应这一倡议。

## 二.设计思路与系统架构

我们的对该项目的系统架构进行了如下的设计，并在接下来进行实现

![image-20250119145459115](/Users/harry/Library/Application Support/typora-user-images/image-20250119145459115.png)



## 三.技术实现

## 3.Langgraph框架的构建

Langgraph的框架构建如下

![image-20250119145714521](/Users/harry/Library/Application Support/typora-user-images/image-20250119145714521.png)

该项目的聊天服务由Langgraph提供支持，并在其中集成了以下主要功能 

### 工具函数

#### 联网搜索——tavilysearch

联网搜索工具函数我们使用了tavilysearch提供了联网搜索服务

#### KnowledgeRag

这一功能由GraphRag提供api服务，该工具通过向GraphRag的api发送请求以获得问题中对应的知识

#### wq_search

该功能用于通过向wq_search的api发送请求以获得问题相关的错题



### 对话历史持久话存储

我们用supabase为我们的Langgraph的框架提供了每个检查点的存储，这一用户可以根据线程恢复历史对话上下文



### 错题Rag

我们用智谱的embedding模型将错题进行embedding后存储至supabase，并创建了向量化的索引，用supabase提供的向量化搜索来实现相似性的搜索



### 对话

对话的模型我们选择了智谱的API来提供
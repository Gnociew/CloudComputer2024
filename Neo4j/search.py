from neo4j import GraphDatabase
import json

# 替换为你的Neo4j URI、用户名和密码
uri = "bolt://121.43.160.105:7687"
username = "neo4j"
password = "123456"

# 创建一个驱动器实例
driver = GraphDatabase.driver(uri, auth=(username, password))

def get_all_nodes(driver):
    with driver.session() as session:
        # Cypher查询语句，用于获取所有节点
        result = session.run("MATCH (n) RETURN n")
        nodes = []
        for record in result:
            node_data = {
                "labels": list(record["n"].labels),
                "properties": dict(record["n"].items())
            }
            nodes.append(node_data)
        return nodes

def save_to_json(nodes, filename='nodes2.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    try:
        nodes = get_all_nodes(driver)
        save_to_json(nodes)
        print(f"Nodes have been saved to nodes.json")
    finally:
        driver.close()
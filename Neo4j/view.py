import json
from py2neo import *
from django.shortcuts import render
from tqdm import tqdm
graph = Graph('bolt://121.43.160.105:7687', auth=('neo4j', '123456')) # 连接数据库

def search_all():
    # 定义data数组，存放节点信息
    data = []
    # 定义关系数组，存放节点间的关系
    links = []
    # 查询所有节点，并将节点信息取出存放在data数组中
    for n in graph.nodes:
        # 将节点信息转化为json格式，否则中文会不显示
        # print(n)
        nodesStr = json.dumps(graph.nodes[n], ensure_ascii=False)
        # 取出节点的name
        node_name = json.loads(nodesStr)['name']

        # 构造字典，存储单个节点信息
        dict = {
            # 'id':str(n), # 防止重复节点
            'name': node_name,
            'symbolSize': 50,
            'category': '对象'
        }
        # 将单个节点信息存放在data数组中
        data.append(dict)
    # 查询所有关系，并将所有的关系信息存放在links数组中
    rps = graph.relationships
    for r in rps:
        # 取出开始节点的name
        source = str(rps[r].start_node['name'])
        # for i in data: #需要使用ID
        #     if source == i['name']:
        #         source = i['id']
        # 取出结束节点的name
        target = str(rps[r].end_node['name'])
        # for i in data: #需要使用ID
        #     if target == i['name']:
        #         target = i['id']
        # 取出开始节点的结束节点之间的关系
        name = str(type(rps[r]).__name__)
        # 构造字典存储单个关系信息
        dict = {
            'source': source,
            'target': target,
            'name': name
        }
        # 将单个关系信息存放进links数组中
        links.append(dict)
    # 输出所有节点信息
    # for item in data:
    #     print(item)
    # 输出所有关系信息
    # for item in links:
    #     print(item)
    # 将所有的节点信息和关系信息存放在一个字典中
    neo4j_data = {
        'data': data,
        'links': links
    }
    neo4j_data = json.dumps(neo4j_data)
    return neo4j_data

def search_all_category(): 
    data = []# 定义data数组，存放节点信息
    links = []# 定义关系数组，存放节点间的关系
    # 节点分类
    node_DEPLOY = graph.run('MATCH (n:DEPLOY) RETURN n').data()
    node_CATE = graph.run('MATCH (n:CATE) RETURN n').data()
    node_EXPS = graph.run('MATCH (n:EXPS) RETURN n').data()
    node_LOCA = graph.run('MATCH (n:LOCA) RETURN n').data()
    node_MSYS = graph.run('MATCH (n:MSYS) RETURN n').data()
    node_PERF = graph.run('MATCH (n:PERF) RETURN n').data()


    for n in node_DEPLOY:    
        nodesStr = json.dumps(n, ensure_ascii=False)# 将节点信息转化为json格式，否则中文会不显示
        node_name = json.loads(nodesStr)
        node_name = node_name['n']['name']   # 取出节点的name
        # print(node_name)
        dict = {
            # 'id':str(n), # 防止重复节点
            'name': node_name,
            'symbolSize': 50,
            'category': 'DEPLOY'
        }
        data.append(dict) # 将单个节点信息存放在data数组中
    for n in node_CATE:    
        nodesStr = json.dumps(n, ensure_ascii=False)# 将节点信息转化为json格式，否则中文会不显示
        node_name = json.loads(nodesStr)
        node_name = node_name['n']['name']   # 取出节点的name
        # print(node_name)
        dict = {
            # 'id':str(n), # 防止重复节点
            'name': node_name,
            'symbolSize': 50,
            'category': 'CATE'
        }
        data.append(dict) # 将单个节点信息存放在data数组中
    for n in node_EXPS:    
        nodesStr = json.dumps(n, ensure_ascii=False)# 将节点信息转化为json格式，否则中文会不显示
        node_name = json.loads(nodesStr)
        node_name = node_name['n']['name']   # 取出节点的name
        # print(node_name)
        dict = {
            # 'id':str(n), # 防止重复节点
            'name': node_name,
            'symbolSize': 50,
            'category': 'EXPS'
        }
        data.append(dict) # 将单个节点信息存放在data数组中
    for n in node_LOCA:    
        nodesStr = json.dumps(n, ensure_ascii=False)# 将节点信息转化为json格式，否则中文会不显示
        node_name = json.loads(nodesStr)
        node_name = node_name['n']['name']   # 取出节点的name
        # print(node_name)
        dict = {
            # 'id':str(n), # 防止重复节点
            'name': node_name,
            'symbolSize': 50,
            'category': 'LOCA'
        }
        data.append(dict) # 将单个节点信息存放在data数组中
    for n in node_MSYS:    
        nodesStr = json.dumps(n, ensure_ascii=False)# 将节点信息转化为json格式，否则中文会不显示
        node_name = json.loads(nodesStr)
        node_name = node_name['n']['name']   # 取出节点的name
        # print(node_name)
        dict = {
            # 'id':str(n), # 防止重复节点
            'name': node_name,
            'symbolSize': 50,
            'category': 'MSYS'
        }
        data.append(dict) # 将单个节点信息存放在data数组中
    for n in node_PERF:    
        nodesStr = json.dumps(n, ensure_ascii=False)# 将节点信息转化为json格式，否则中文会不显示
        node_name = json.loads(nodesStr)
        node_name = node_name['n']['name']   # 取出节点的name
        # print(node_name)
        dict = {
            # 'id':str(n), # 防止重复节点
            'name': node_name,
            'symbolSize': 50,
            'category': 'PERF'
        }
        data.append(dict) # 将单个节点信息存放在data数组中
    
    # 查询所有关系，并将所有的关系信息存放在links数组中
    rps = graph.relationships
    for r in rps:
        source = str(rps[r].start_node['name']) # 取出开始节点的name
        target = str(rps[r].end_node['name']) 
        name = str(type(rps[r]).__name__)# 取出开始节点的结束节点之间的关系
        # 构造字典存储单个关系信息
        dict = {
            'source': source,
            'target': target,
            'name': name
        }
        links.append(dict)# 将单个关系信息存放进links数组中
    neo4j_data = {
        'data': data,
        'links': links
    }
    neo4j_data = json.dumps(neo4j_data)
    with open('search_neo4j_data.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(neo4j_data), f, ensure_ascii=False, indent=4)
        print("已保存")
    return neo4j_data


def search_one(value):
    # 定义data数组存储节点信息
    data = []
    # 定义links数组存储关系信息
    links = []
    # 查询节点是否存在
    node = graph.run('MATCH(n:person{name:"' + value + '"}) return n').data()
    # 如果节点存在len(node)的值为1不存在的话len(node)的值为0
    if len(node):
        # 如果该节点存在将该节点存入data数组中
        # 构造字典存放节点信息
        dict = {
            'name': value,
            'symbolSize': 50,
            'category': '对象'
        }
        data.append(dict)
        # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
        nodes = graph.run('MATCH(n:person{name:"' + value + '"})<-->(m:person) return m').data()
        # 查询该节点所涉及的所有relationship，无向，步长为1，并返回这些relationship
        reps = graph.run('MATCH(n:person{name:"' + value + '"})<-[rel]->(m:person) return rel').data()
        # 处理节点信息
        for n in nodes:
            # 将节点信息的格式转化为json
            node = json.dumps(n, ensure_ascii=False)
            node = json.loads(node)
            # 取出节点信息中person的name
            name = str(node['m']['name'])
            # 构造字典存放单个节点信息
            dict = {
                'name': name,
                'symbolSize': 50,
                'category': '对象'
            }
            # 将单个节点信息存储进data数组中
            data.append(dict)
        # 处理relationship
        for r in reps:
            source = str(r['rel'].start_node['name'])
            target = str(r['rel'].end_node['name'])
            name = str(type(r['rel']).__name__)
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            links.append(dict)
        # 构造字典存储data和links
        search_neo4j_data = {
            'data': data,
            'links': links
        }
        # 将dict转化为json格式
        search_neo4j_data = json.dumps(search_neo4j_data)
        with open('search_neo4j_data.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(search_neo4j_data), f, ensure_ascii=False, indent=4)
        print("已保存")
        return 1
    else:
        print("查无此节点")
        return 0


def index(request):
    ctx = {}
    if request.method == 'POST':
        # 接收前端传过来的查询值
        node_name = request.POST.get('node')
        # 查询结果
        search_neo4j_data = search_one(node_name)
        # 未查询到该节点
        if search_neo4j_data == 0:
            ctx = {'title': '数据库中暂未添加该实体'}
            neo4j_data = search_all_category()
            return render(request, 'index.html', {'neo4j_data': neo4j_data, 'ctx': ctx})
        # 查询到了该节点
        else:
            neo4j_data = search_all_category()
            return render(request, 'index.html',
                          {'neo4j_data': neo4j_data, 'search_neo4j_data': search_neo4j_data, 'ctx': ctx})

    neo4j_data = search_all_category()
    return render(request, 'index.html', {'neo4j_data': neo4j_data, 'ctx': ctx})

def extract_entity_and_relations(entity_name, visited_nodes=None, visited_relations=None):
    if visited_nodes is None:
        visited_nodes = set()
    if visited_relations is None:
        visited_relations = set()

    # 查询节点是否存在
    node = graph.run('MATCH(n {name:$name}) RETURN n', name=entity_name).data()
    if not node:
        print("查无此节点")
        return {'data': [], 'links': []}

    # 获取节点信息
    node = node[0]['n']
    node_id = id(node)
    if node_id in visited_nodes:
        return {'data': [], 'links': []}

    visited_nodes.add(node_id)

    # 构造字典存放节点信息
    node_dict = {
        'name': node['name'],
        'symbolSize': 50,
        'category': '对象'
    }

    data = [node_dict]
    links = []

    # 查询与该节点有关的节点和关系
    relationships = graph.run(
        'MATCH (n {name:$name})-[r]-(m) RETURN r, m',
        name=entity_name
    ).data()

    for rel in relationships:
        rel_obj = rel['r']
        rel_id = id(rel_obj)
        if rel_id in visited_relations:
            continue

        visited_relations.add(rel_id)

        # 获取结束节点信息
        end_node = rel['m']
        end_node_id = id(end_node)
        if end_node_id not in visited_nodes:
            end_node_dict = {
                'name': end_node['name'],
                'symbolSize': 50,
                'category': '对象'
            }
            data.append(end_node_dict)
            visited_nodes.add(end_node_id)

        # 构造字典存放关系信息
        link_dict = {
            'source': node['name'],
            'target': end_node['name'],
            'name': type(rel_obj).__name__
        }
        links.append(link_dict)

        # 递归调用以获取所有相关节点和关系
        result = extract_entity_and_relations(end_node['name'], visited_nodes, visited_relations)
        data.extend(result['data'])
        links.extend(result['links'])

    return {'data': data, 'links': links}

def search_entity(request):
    ctx = {}
    if request.method == 'POST':
        # 接收前端传过来的查询值
        entity_name = request.POST.get('entity')
        # 查询结果
        search_neo4j_data = extract_entity_and_relations(entity_name)
        # 未查询到该节点
        if not search_neo4j_data['data']:
            ctx = {'title': '数据库中暂未添加该实体'}
            neo4j_data = search_all_category()
            return render(request, 'index.html', {'neo4j_data': neo4j_data, 'ctx': ctx})
        # 查询到了该节点
        else:
            neo4j_data = search_all_category()
            search_neo4j_data_json = json.dumps(search_neo4j_data)
            with open('search_neo4j_data.json', 'w', encoding='utf-8') as f:
                json.dump(json.loads(search_neo4j_data_json), f, ensure_ascii=False, indent=4)
            print("已保存")
            return render(request, 'index.html',
                          {'neo4j_data': neo4j_data, 'search_neo4j_data': search_neo4j_data_json, 'ctx': ctx})

    neo4j_data = search_all_category()
    return render(request, 'index.html', {'neo4j_data': neo4j_data, 'ctx': ctx})

if __name__ == '__main__':
    # neo4j_data = search_all_category()
    # print(neo4j_data)
    # search_one("光合作用")
    # print(graph.schema.node_labels)
    # print(graph.schema.relationship_types)
    schema_node_labels = graph.schema.node_labels
    list_schema_node_labels = list(schema_node_labels)
    with open('schema_node_labels.json', 'w', encoding='utf-8') as f:
        json.dump(list_schema_node_labels, f, ensure_ascii=False, indent=4)
    print("已保存")
    a = extract_entity_and_relations("葡萄糖")
    print(a)


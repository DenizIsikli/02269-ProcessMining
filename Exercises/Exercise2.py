from collections import defaultdict
from datetime import datetime
import xml.etree.ElementTree as ET

def log_as_dictionary(log):
    d = defaultdict(list)
    for line in log.strip().splitlines():
        if not line.strip():
            continue
        task, case, user, ts = line.split(";")
        d[case].append({
            "concept:name": task,
            "case": case,
            "org:resource": user,
            "time:timestamp": datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        })
    for case in d:
        d[case].sort(key=lambda x: x["time:timestamp"])
    return d

def dependency_graph_inline(log):
    df = defaultdict(lambda: defaultdict(int))
    for case, events in log.items():
        for i in range(len(events)-1):
            a1 = events[i]["concept:name"]
            a2 = events[i+1]["concept:name"]
            df[a1][a2] += 1
    return df

def read_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    d = defaultdict(list)
    
    ns = {'xes': 'http://www.xes-standard.org/'}
    if root.tag.endswith('log'):
        ns_prefix = '{http://www.xes-standard.org/}'
    else:
        ns_prefix = ''
    
    for trace in root.findall(f'{ns_prefix}trace'):
        case_id = None
        for child in trace:
            if child.tag.endswith('string') and child.get('key') == 'concept:name':
                case_id = child.get('value')
                break
        
        if not case_id:
            continue
        
        events = []
        for event in trace.findall(f'{ns_prefix}event'):
            e = {}
            for attr in event:
                key = attr.get('key')
                val = attr.get('value')
                
                if val is None:
                    continue
                
                if attr.tag.endswith('date'):
                    try:
                        if 'T' in val:
                            if val.endswith('Z'):
                                val = val[:-1] + '+00:00'
                            dt = datetime.fromisoformat(val)
                            val = dt.replace(tzinfo=None)
                        else:
                            val = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                    except:
                        val = datetime(1970, 1, 1, 1, 0)
                elif attr.tag.endswith('int'):
                    val = int(val)
                elif attr.tag.endswith('float'):
                    val = float(val)
                
                e[key] = val
            
            events.append(e)
        
        events.sort(key=lambda x: x.get('time:timestamp', datetime.min))
        d[case_id].extend(events)
    
    return d

def dependency_graph_file(log):
    df = defaultdict(lambda: defaultdict(int))
    for case, events in log.items():
        for i in range(len(events)-1):
            a1 = events[i]["concept:name"]
            a2 = events[i+1]["concept:name"]
            df[a1][a2] += 1
    return df

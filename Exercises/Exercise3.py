import xml.etree.ElementTree as ET
from itertools import combinations

class PetriNet():
    def __init__(self):
        self.places={}
        self.transitions={}
        self.edges={}
    def add_place(self, name):
        self.places[name]=0
        if name not in self.edges:
            self.edges[name]=set()
        return self
    def add_transition(self, name, id):
        self.transitions[id]=name
        if id not in self.edges:
            self.edges[id]=set()
        return self
    def add_edge(self, source, target):
        if source not in self.edges:
            self.edges[source]=set()
        self.edges[source].add(target)
        return self
    def get_tokens(self, place):
        return self.places.get(place, 0)
    def is_enabled(self, transition):
        for src,tgts in self.edges.items():
            if transition in tgts and src in self.places:
                if self.places[src]==0:
                    return False
        return True
    def add_marking(self, place):
        if place in self.places:
            self.places[place]+=1
        return self
    def fire_transition(self, transition):
        if not self.is_enabled(transition):
            return self
        for src,tgts in self.edges.items():
            if transition in tgts and src in self.places:
                self.places[src]-=1
        for tgt in self.edges[transition]:
            if tgt in self.places:
                self.places[tgt]+=1
        return self
    def transition_name_to_id(self, name):
        for id, n in self.transitions.items():
            if n == name:
                return id
        return None

def read_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    ns = {'xes': 'http://www.xes-standard.org/'}
    if root.tag.endswith('log'):
        ns_prefix = '{http://www.xes-standard.org/}'
    else:
        ns_prefix = ''
    log = []
    for trace_elem in root.findall(f'{ns_prefix}trace'):
        trace = []
        for event_elem in trace_elem.findall(f'{ns_prefix}event'):
            for attr in event_elem.findall(f'{ns_prefix}string'):
                if attr.get('key') == 'concept:name':
                    trace.append(attr.get('value'))
                    break
        if trace:
            log.append(trace)
    return log

def alpha(log):
    activities = set()
    for trace in log:
        activities.update(trace)
    
    start_activities = set()
    end_activities = set()
    for trace in log:
        if trace:
            start_activities.add(trace[0])
            end_activities.add(trace[-1])
    
    direct_succession = set()
    for trace in log:
        for i in range(len(trace) - 1):
            direct_succession.add((trace[i], trace[i+1]))
    
    causality = set()
    for a in activities:
        for b in activities:
            if (a, b) in direct_succession and (b, a) not in direct_succession:
                causality.add((a, b))
    
    parallel = set()
    for a in activities:
        for b in activities:
            if (a, b) in direct_succession and (b, a) in direct_succession:
                parallel.add((a, b))
    
    choice = set()
    for a in activities:
        for b in activities:
            if (a, b) not in direct_succession and (b, a) not in direct_succession:
                choice.add((a, b))
    
    xl = []
    for r in range(1, len(activities) + 1):
        for subset in combinations(activities, r):
            A = set(subset)
            is_valid_A = True
            for a1 in A:
                for a2 in A:
                    if a1 != a2 and (a1, a2) not in choice:
                        is_valid_A = False
                        break
                if not is_valid_A:
                    break
            if not is_valid_A:
                continue
            for s in range(1, len(activities) + 1):
                for subset_b in combinations(activities, s):
                    B = set(subset_b)
                    is_valid_B = True
                    for b1 in B:
                        for b2 in B:
                            if b1 != b2 and (b1, b2) not in choice:
                                is_valid_B = False
                                break
                        if not is_valid_B:
                            break
                    if not is_valid_B:
                        continue
                    is_valid_pair = True
                    for a in A:
                        for b in B:
                            if (a, b) not in causality:
                                is_valid_pair = False
                                break
                        if not is_valid_pair:
                            break
                    if is_valid_pair:
                        xl.append((A, B))
    
    yl = []
    for pair in xl:
        is_maximal = True
        for other in xl:
            if pair != other:
                if pair[0].issubset(other[0]) and pair[1].issubset(other[1]) and (pair[0] != other[0] or pair[1] != other[1]):
                    is_maximal = False
                    break
        if is_maximal:
            yl.append(pair)
    
    pn = PetriNet()
    
    place_counter = 0
    pn.add_place(f"p_start")
    pn.add_marking(f"p_start")
    place_counter += 1
    
    pn.add_place(f"p_end")
    place_counter += 1
    
    transition_counter = 0
    activity_to_id = {}
    for activity in activities:
        pn.add_transition(activity, transition_counter)
        activity_to_id[activity] = transition_counter
        transition_counter += 1
    
    for activity in start_activities:
        pn.add_edge(f"p_start", activity_to_id[activity])
    
    for activity in end_activities:
        pn.add_edge(activity_to_id[activity], f"p_end")
    
    place_map = {}
    for A, B in yl:
        place_name = f"p_{place_counter}"
        place_counter += 1
        pn.add_place(place_name)
        place_map[(frozenset(A), frozenset(B))] = place_name
        for a in A:
            pn.add_edge(activity_to_id[a], place_name)
        for b in B:
            pn.add_edge(place_name, activity_to_id[b])
    
    return pn

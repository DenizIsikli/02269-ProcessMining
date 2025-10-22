from decimal import Decimal, ROUND_HALF_UP
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

def _input_places_of_transition(net: PetriNet, tid):
    """All places that have an edge to the given transition id."""
    ins = []
    for src, tgts in net.edges.items():
        if src in net.places and tid in tgts:
            ins.append(src)
    return ins

def _output_places_of_transition(net: PetriNet, tid):
    """All places that are targets of the given transition id."""
    outs = []
    for tgt in net.edges.get(tid, set()):
        if tgt in net.places:
            outs.append(tgt)
    return outs

def _sink_places(net: PetriNet):
    """Places with no outgoing edges."""
    sinks = set()
    for p in net.places:
        if len(net.edges.get(p, set())) == 0:
            sinks.add(p)
    return sinks

def fitness_token_replay(log, net: PetriNet):
    """
    Exact token-replay fitness (Metric 3-style):
      fitness = 0.5 * ((1 - missing/consumed) + (1 - remaining/produced))
    Rounded HALF_UP to 5 decimals.
    """
    total_missing = total_consumed = total_remaining = total_produced = 0.0
    sinks = _sink_places(net)
    end_place = "p_end"

    for trace in log:
        # reset marking
        for p in net.places:
            net.places[p] = 0
        # initial marking
        if "p_start" in net.places:
            net.places["p_start"] = 1

        missing = consumed = remaining = produced = 0.0

        # account for the start token (consumed/produced once)
        consumed += 1.0
        produced += 1.0

        for ev in trace:
            tid = net.transition_name_to_id(ev)
            if tid is None:
                continue

            ins = _input_places_of_transition(net, tid)
            outs = _output_places_of_transition(net, tid)

            # add missing tokens if not enabled
            for p in ins:
                if net.places[p] <= 0:
                    missing += 1.0
                    net.places[p] += 1

            # consume
            for p in ins:
                net.places[p] -= 1
            consumed += len(ins)

            # produce
            for p in outs:
                net.places[p] += 1
            produced += len(outs)

        # end place accounting
        if end_place in net.places:
            if net.places[end_place] == 0:
                missing += 1.0
            elif net.places[end_place] > 1:
                remaining += net.places[end_place] - 1.0

        # remaining tokens outside sinks and not in end place
        for p, tok in net.places.items():
            if p != end_place and p not in sinks and tok > 0:
                remaining += tok

        total_missing += missing
        total_consumed += consumed
        total_remaining += remaining
        total_produced += produced

    if total_consumed == 0 or total_produced == 0:
        return 0.0

    fitness = 0.5 * ((1 - total_missing / total_consumed) + (1 - total_remaining / total_produced))
    fitness = max(0.0, min(1.0, fitness))
    return float(Decimal(str(fitness)).quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP))

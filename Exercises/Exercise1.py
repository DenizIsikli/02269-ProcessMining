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

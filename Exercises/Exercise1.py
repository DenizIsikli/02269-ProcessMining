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

p = PetriNet()

p.add_place(1)  # add place with id 1
p.add_place(2)
p.add_place(3)
p.add_place(4)
p.add_transition("A", -1)  # add transition "A" with id -1
p.add_transition("B", -2)
p.add_transition("C", -3)
p.add_transition("D", -4)

p.add_edge(1, -1)
p.add_edge(-1, 2)
p.add_edge(2, -2).add_edge(-2, 3)
p.add_edge(2, -3).add_edge(-3, 3)
p.add_edge(3, -4)
p.add_edge(-4, 4)

print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.add_marking(1)  # add one token to place id 1
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-1)  # fire transition A
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-3)  # fire transition C
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-4)  # fire transition D
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.add_marking(2)  # add one token to place id 2
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-2)  # fire transition B
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-4)  # fire transition D
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

# by the end of the execution there should be 2 tokens on the final place
print(p.get_tokens(4))

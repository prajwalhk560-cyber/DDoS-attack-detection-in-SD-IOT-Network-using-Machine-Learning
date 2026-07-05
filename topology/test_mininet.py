#!/usr/bin/python3

try:
    from mininet.topo import Topo
    print("✅ Mininet import successful!")

    class DummyTopo(Topo):
        def build(self):
            h1 = self.addHost('h1')
            s1 = self.addSwitch('s1')
            self.addLink(h1, s1)

    print("✅ Dummy topology created without errors.")

except Exception as e:
    print("❌ Mininet import failed:", e)

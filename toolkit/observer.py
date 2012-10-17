class Publisher():    
    def __init__(self):
        self.subscribers = set()
        
    def subscribe(self, Subscriber):
        self.subscribers.add(Subscriber)
    
    def unsubscriber(self, Subscriber):
        self.subscribers.remove(Subscriber)
    
    def notify(self, data):
        for subscriber in self.subscribers:
            subscriber.notification(data)
            
class Subscriber():
    def __init__(self):
        pass
    def notification(self, data):
        pass
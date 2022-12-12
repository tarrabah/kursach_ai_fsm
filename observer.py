class State_observer:
    def __init__(self, master):
        self.responsible_ids = []
        self.master = master

    def add_id(self, id):
        self.responsible_ids.append(id)

    def do_work(self, message):
        if message.sender_id in self.responsible_ids:
            if message.sender_type == "Mob":
                self.master.new_state(message.sender_id, message.state)



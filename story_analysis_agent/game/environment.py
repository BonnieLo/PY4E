# game/environment.py

class Environment:
    def __init__(self, action_registry):
        """
        初始化環境，接收一個 action registry 來查找要執行的功能。
        """
        self.actions = action_registry

    def execute(self, action_name: str, args: dict):
        """
        執行指定名稱的動作，將參數傳給對應的 function。
        """
        action = self.actions.get_action(action_name)
        return action.execute(**args)

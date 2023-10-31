class UserNotFoundException(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(self.message)
        
class InsufficientBalanceException(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(self.message)
        
class InsufficientAmountException(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(self.message)
        

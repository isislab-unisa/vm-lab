class VmNotSharedError(Exception):
    def __init__(self, vm_name):
        self.message = f"The VM `{vm_name}` is not shared by its owner."
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.message}"
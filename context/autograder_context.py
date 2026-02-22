class AutograderContext:
    def __init__(self):
        self._context_data = {}

    def set(self, key: str, value):
        self._context_data[key] = value
    
    def get(self, key: str, default=None):
        value = self._context_data.get(key, default)
        if value is None:
            raise Warning(f"The key '{key}' is not in AutograderContext")
        
        return value
    
    def get_int(self, key: str) -> int:
        """
        Retrieve an integer value from the context.

        Args:
            key: The key to look up.
        Returns:
            The integer value associated with the key, or 0 if not found.
        """
        return int(self.get(key, 0))
    
    def get_str(self, key: str) -> str:
        """
        Retrieve a string value from the context.

        Args:
            key: The key to look up.
        Returns:
            The string value associated with the key, or an empty string if not found.
        """
        return str(self.get(key, ""))
    
    def get_bool(self, key: str) -> bool:
        """
        Retrieve a boolean value from the context.

        Args:
            key: The key to look up.
        Returns:
            The boolean value associated with the key, or False if not found.
        """
        return bool(self.get(key, False))
    
    def get_float(self, key: str) -> float:
        """
        Retrieve a float value from the context.

        Args:
            key: The key to look up.
        Returns:
            The float value associated with the key, or 0.0 if not found.
        """
        return float(self.get(key, 0.0))
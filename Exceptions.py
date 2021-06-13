class BlockNotFound(Exception):
    def __str__(self):
        return f"block not found"

class FullBlock(Exception):
    def __str__(self):
        return f"block rempli"

class BlockCorrupt(Exception):
    def __str__(self):
        return f"block erone"

class ConnexionError(Exception):
    def __str__(self):
        return f"probleme de connexxion"

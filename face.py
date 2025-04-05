class Rect:
    def __init__(self, x, y, width, height):
        """Constructeur principal avec 4 valeurs."""
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    @classmethod
    def from_xml(cls, element):
        """Deuxième 'constructeur' qui prend un élément XML <rect>."""
        return cls(
            element.get("x", 0),
            element.get("y", 0),
            element.get("width", 0),
            element.get("height", 0),
        )

    def __repr__(self):
        return f"Rect(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    def is_close(self, other, tolerance=0.05):
        """Compare deux Rect avec une tolérance (5% par défaut)."""
        if not isinstance(other, Rect):
            return False  # Comparaison avec un autre type impossible

        return all(
            abs(getattr(self, attr) - getattr(other, attr)) <= tolerance * getattr(self, attr)
            for attr in ["x", "y", "width", "height"]
        )
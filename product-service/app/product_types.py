PRODUCT_TYPE_SCHEMAS = {
    "book": {
        "label": "Book",
        "fields": [
            {"name": "author", "label": "Author", "type": "string", "required": True},
            {"name": "publisher", "label": "Publisher", "type": "string", "required": True},
            {"name": "isbn", "label": "ISBN", "type": "string", "required": True},
        ],
    },
    "electronics": {
        "label": "Electronics",
        "fields": [
            {"name": "brand", "label": "Brand", "type": "string", "required": True},
            {"name": "warranty_months", "label": "Warranty", "type": "number", "required": True},
            {"name": "model", "label": "Model", "type": "string", "required": True},
        ],
    },
    "fashion": {
        "label": "Fashion",
        "fields": [
            {"name": "size", "label": "Size", "type": "string", "required": True},
            {"name": "color", "label": "Color", "type": "string", "required": True},
            {"name": "material", "label": "Material", "type": "string", "required": True},
        ],
    },
    "home-living": {
        "label": "Home & Living",
        "fields": [
            {"name": "material", "label": "Material", "type": "string", "required": True},
            {"name": "dimensions", "label": "Dimensions", "type": "string", "required": True},
            {"name": "room", "label": "Room", "type": "string", "required": True},
        ],
    },
    "beauty": {
        "label": "Beauty",
        "fields": [
            {"name": "brand", "label": "Brand", "type": "string", "required": True},
            {"name": "skin_type", "label": "Skin Type", "type": "string", "required": True},
            {"name": "volume_ml", "label": "Volume", "type": "number", "required": True},
        ],
    },
    "sports": {
        "label": "Sports",
        "fields": [
            {"name": "brand", "label": "Brand", "type": "string", "required": True},
            {"name": "sport", "label": "Sport", "type": "string", "required": True},
            {"name": "level", "label": "Level", "type": "string", "required": True},
        ],
    },
    "toys": {
        "label": "Toys",
        "fields": [
            {"name": "age_range", "label": "Age Range", "type": "string", "required": True},
            {"name": "material", "label": "Material", "type": "string", "required": True},
            {"name": "battery_required", "label": "Battery Required", "type": "boolean", "required": True},
        ],
    },
    "grocery": {
        "label": "Grocery",
        "fields": [
            {"name": "weight_grams", "label": "Weight", "type": "number", "required": True},
            {"name": "expiry_days", "label": "Expiry (days)", "type": "number", "required": True},
            {"name": "organic", "label": "Organic", "type": "boolean", "required": True},
        ],
    },
    "office": {
        "label": "Office",
        "fields": [
            {"name": "brand", "label": "Brand", "type": "string", "required": True},
            {"name": "pack_size", "label": "Pack Size", "type": "number", "required": True},
            {"name": "color", "label": "Color", "type": "string", "required": True},
        ],
    },
    "pet-supplies": {
        "label": "Pet Supplies",
        "fields": [
            {"name": "pet_type", "label": "Pet Type", "type": "string", "required": True},
            {"name": "size", "label": "Size", "type": "string", "required": True},
            {"name": "weight_grams", "label": "Weight", "type": "number", "required": True},
        ],
    },
}


PRODUCT_TYPE_CHOICES = [(product_type, schema["label"]) for product_type, schema in PRODUCT_TYPE_SCHEMAS.items()]


def get_product_type_schema(detail_type):
    return PRODUCT_TYPE_SCHEMAS.get(detail_type)

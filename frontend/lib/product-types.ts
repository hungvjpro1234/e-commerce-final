export type ProductDetailValue = string | number | boolean;

export type ProductTypeField = {
  name: string;
  label: string;
  type: "string" | "number" | "boolean";
  required: boolean;
  adminInput?: "text" | "number" | "checkbox";
  format?: (value: ProductDetailValue) => string;
};

export type ProductTypeConfig = {
  label: string;
  categoryName: string;
  imageQuery: string;
  fields: ProductTypeField[];
};

const booleanLabel = (value: ProductDetailValue) => ((value as boolean) ? "Yes" : "No");

export const PRODUCT_TYPE_CONFIG: Record<string, ProductTypeConfig> = {
  book: {
    label: "Book",
    categoryName: "Books",
    imageQuery: "books",
    fields: [
      { name: "author", label: "Author", type: "string", required: true, adminInput: "text" },
      { name: "publisher", label: "Publisher", type: "string", required: true, adminInput: "text" },
      { name: "isbn", label: "ISBN", type: "string", required: true, adminInput: "text" },
    ],
  },
  electronics: {
    label: "Electronics",
    categoryName: "Electronics",
    imageQuery: "electronics",
    fields: [
      { name: "brand", label: "Brand", type: "string", required: true, adminInput: "text" },
      {
        name: "warranty_months",
        label: "Warranty",
        type: "number",
        required: true,
        adminInput: "number",
        format: (value) => `${value} months`,
      },
      { name: "model", label: "Model", type: "string", required: true, adminInput: "text" },
    ],
  },
  fashion: {
    label: "Fashion",
    categoryName: "Fashion",
    imageQuery: "fashion",
    fields: [
      { name: "size", label: "Size", type: "string", required: true, adminInput: "text" },
      { name: "color", label: "Color", type: "string", required: true, adminInput: "text" },
      { name: "material", label: "Material", type: "string", required: true, adminInput: "text" },
    ],
  },
  "home-living": {
    label: "Home & Living",
    categoryName: "Home & Living",
    imageQuery: "home decor",
    fields: [
      { name: "material", label: "Material", type: "string", required: true, adminInput: "text" },
      { name: "dimensions", label: "Dimensions", type: "string", required: true, adminInput: "text" },
      { name: "room", label: "Room", type: "string", required: true, adminInput: "text" },
    ],
  },
  beauty: {
    label: "Beauty",
    categoryName: "Beauty",
    imageQuery: "beauty product",
    fields: [
      { name: "brand", label: "Brand", type: "string", required: true, adminInput: "text" },
      { name: "skin_type", label: "Skin Type", type: "string", required: true, adminInput: "text" },
      {
        name: "volume_ml",
        label: "Volume",
        type: "number",
        required: true,
        adminInput: "number",
        format: (value) => `${value} ml`,
      },
    ],
  },
  sports: {
    label: "Sports",
    categoryName: "Sports",
    imageQuery: "sports gear",
    fields: [
      { name: "brand", label: "Brand", type: "string", required: true, adminInput: "text" },
      { name: "sport", label: "Sport", type: "string", required: true, adminInput: "text" },
      { name: "level", label: "Level", type: "string", required: true, adminInput: "text" },
    ],
  },
  toys: {
    label: "Toys",
    categoryName: "Toys",
    imageQuery: "toys",
    fields: [
      { name: "age_range", label: "Age Range", type: "string", required: true, adminInput: "text" },
      { name: "material", label: "Material", type: "string", required: true, adminInput: "text" },
      {
        name: "battery_required",
        label: "Battery Required",
        type: "boolean",
        required: true,
        adminInput: "checkbox",
        format: booleanLabel,
      },
    ],
  },
  grocery: {
    label: "Grocery",
    categoryName: "Grocery",
    imageQuery: "grocery",
    fields: [
      {
        name: "weight_grams",
        label: "Weight",
        type: "number",
        required: true,
        adminInput: "number",
        format: (value) => `${value} g`,
      },
      {
        name: "expiry_days",
        label: "Expiry",
        type: "number",
        required: true,
        adminInput: "number",
        format: (value) => `${value} days`,
      },
      { name: "organic", label: "Organic", type: "boolean", required: true, adminInput: "checkbox", format: booleanLabel },
    ],
  },
  office: {
    label: "Office",
    categoryName: "Office",
    imageQuery: "office supplies",
    fields: [
      { name: "brand", label: "Brand", type: "string", required: true, adminInput: "text" },
      { name: "pack_size", label: "Pack Size", type: "number", required: true, adminInput: "number" },
      { name: "color", label: "Color", type: "string", required: true, adminInput: "text" },
    ],
  },
  "pet-supplies": {
    label: "Pet Supplies",
    categoryName: "Pet Supplies",
    imageQuery: "pet supplies",
    fields: [
      { name: "pet_type", label: "Pet Type", type: "string", required: true, adminInput: "text" },
      { name: "size", label: "Size", type: "string", required: true, adminInput: "text" },
      {
        name: "weight_grams",
        label: "Weight",
        type: "number",
        required: true,
        adminInput: "number",
        format: (value) => `${value} g`,
      },
    ],
  },
};

export type ProductDetailType = keyof typeof PRODUCT_TYPE_CONFIG;

export const PRODUCT_TYPE_OPTIONS = Object.entries(PRODUCT_TYPE_CONFIG).map(([value, config]) => ({
  value,
  label: config.label,
}));

export function getDetailDraft(detailType: string, detail?: Record<string, ProductDetailValue>) {
  const config = PRODUCT_TYPE_CONFIG[detailType];
  if (!config) {
    return detail || {};
  }

  return config.fields.reduce<Record<string, ProductDetailValue>>((acc, field) => {
    if (detail && detail[field.name] !== undefined) {
      acc[field.name] = detail[field.name];
      return acc;
    }

    if (field.type === "number") {
      acc[field.name] = 0;
    } else if (field.type === "boolean") {
      acc[field.name] = false;
    } else {
      acc[field.name] = "";
    }
    return acc;
  }, {});
}

export function getProductImageQuery(detailType?: string, categoryName?: string) {
  if (detailType && PRODUCT_TYPE_CONFIG[detailType]) {
    return PRODUCT_TYPE_CONFIG[detailType].imageQuery;
  }

  const normalizedCategory = categoryName?.toLowerCase() || "";
  if (normalizedCategory.includes("book")) return "books";
  if (normalizedCategory.includes("electronic") || normalizedCategory.includes("tech")) return "electronics";
  if (normalizedCategory.includes("fashion") || normalizedCategory.includes("clothes")) return "fashion";
  return "product";
}

export function toDisplayLabel(key: string) {
  return key
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

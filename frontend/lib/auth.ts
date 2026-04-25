export const ROLE_ADMIN = "admin";
export const ROLE_STAFF = "staff";
export const ROLE_CUSTOMER = "customer";

export type AppRole = typeof ROLE_ADMIN | typeof ROLE_STAFF | typeof ROLE_CUSTOMER | string;

export function hasRequiredRole(role: AppRole | null | undefined, allowedRoles: AppRole[]) {
  if (!role) return false;
  return allowedRoles.includes(role);
}

export function getDefaultRouteForRole(role: AppRole | null | undefined) {
  if (role === ROLE_ADMIN) return "/admin";
  if (role === ROLE_STAFF) return "/staff";
  return "/";
}

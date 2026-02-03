/**
 * Branded types for NEXLOOP domain models.
 * Purpose: Prevent accidental mixing of different string-based identifiers.
 */

export type Brand<K, T> = K & { readonly __brand: T };

export type UserId = Brand<string, 'UserId'>;
export type TeamId = Brand<number, 'TeamId'>;
export type RoleId = Brand<number, 'RoleId'>;
export type TaskId = Brand<string, 'TaskId'>;
export type GcsPath = Brand<string, 'GcsPath'>;
export type Email = Brand<string, 'Email'>;

// Type guards/creators
export const asTaskId = (id: string) => id as TaskId;
export const asGcsPath = (path: string) => path as GcsPath;
export const asEmail = (email: string) => email as Email;

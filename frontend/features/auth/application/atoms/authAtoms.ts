import { atom } from "jotai";
import type { User } from "../../domain/model/auth";

export const userAtom = atom<User | null>(null);
export const isAuthenticatedAtom = atom((get) => get(userAtom) !== null);

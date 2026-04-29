"use client";

import { atomWithStorage } from "jotai/utils";

export type ViewMode = "card" | "list";

export const viewModeAtom = atomWithStorage<ViewMode>("ai-vms.view-mode", "card");
